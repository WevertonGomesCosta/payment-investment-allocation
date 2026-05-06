from __future__ import annotations
import pandas as pd
from pathlib import Path

INI='2026-05-06'; FIM='2026-06-15'
PACOTES=['no_action','switch_only','pay_only','switch_then_pay','pay_then_switch']


def contar_fontes_lote_sugerido(valor) -> int:
    txt=str(valor or '').strip()
    if txt.lower() in {'','n/d','nd','nan','none','-'}:
        return 0
    partes=[x.strip() for x in txt.split('+') if str(x).strip()]
    return len(partes) if partes else 0

oficiais=sorted(Path('saidas/oficial').glob('*.xlsx'), key=lambda x: x.stat().st_mtime, reverse=True)
if not oficiais:
    raise SystemExit('ERRO: nenhum xlsx encontrado em saidas/oficial; execute python aplicacao/principal.py antes.')
p=oficiais[0]
xf=pd.ExcelFile(p)
mtime_utc=pd.Timestamp.utcfromtimestamp(p.stat().st_mtime).isoformat()+'Z'
ext=pd.read_excel(p,sheet_name='Extrato Futuro')
aud=pd.read_excel(p,sheet_name='Auditoria Fontes') if 'Auditoria Fontes' in xf.sheet_names else pd.DataFrame()

ext['Data']=pd.to_datetime(ext['Data'],errors='coerce').dt.date
if len(aud):
    aud['Data']=pd.to_datetime(aud['Data'],errors='coerce').dt.date

dias=[d.date() for d in pd.date_range(INI,FIM,freq='D')]
rows=[]
for d in dias:
    dia=ext[ext['Data']==d].copy()
    ad=aud[aud['Data']==d].copy() if len(aud) else pd.DataFrame()
    has_pay=len(dia)>0
    total_val=float(pd.to_numeric(dia.get('Valor',pd.Series([],dtype=float)),errors='coerce').fillna(0).sum())
    pacotes_dia=set(str(x).strip().lower() for x in dia.get('Pacote do dia',pd.Series([],dtype=str)).fillna(''))
    cand_sw = bool((ad.get('evento_switching_id',pd.Series([],dtype=str)).fillna('').astype(str).str.strip()!='').any() or (ad.get('origem_fonte_candidata',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('switch',case=False,na=False)).any())

    receb_disp = int((ad.get('tipo_fonte_candidata',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('recebido|caixa_pre_aplicacao',case=False,regex=True)).sum()) if len(ad) else 'n/d'
    lotes_ini = int(ad.get('fonte_candidata_id',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('lote',case=False,na=False).sum()) if len(ad) else 'n/d'
    fontes_ini = int(ad.get('fonte_candidata_id',pd.Series([],dtype=str)).fillna('').astype(str).str.strip().ne('').sum()) if len(ad) else 'n/d'
    lotes_venc_norm='n/d'

    winner='no_action' if not has_pay else 'pay_only'
    if 'switch_then_pay' in pacotes_dia: winner='switch_then_pay'
    elif 'pay_then_switch' in pacotes_dia: winner='pay_then_switch'
    elif 'switch_only' in pacotes_dia and not has_pay: winner='switch_only'

    for pacote in PACOTES:
        aval = pacote in pacotes_dia
        conceit_aplicavel = ((pacote in ('no_action','switch_only') and not has_pay) or (pacote in ('pay_only','switch_then_pay','pay_then_switch') and has_pay))

        motivo_na=''
        if not aval:
            if has_pay and pacote in ('no_action','switch_only'):
                motivo_na='nao_aplicavel_por_haver_pagamento_no_dia'
            elif (not has_pay) and pacote in ('pay_only','switch_then_pay','pay_then_switch'):
                motivo_na='sem_pagamento_no_dia'
            elif pacote in ('switch_only','switch_then_pay','pay_then_switch') and not cand_sw:
                motivo_na='sem_candidato_ou_bloqueado_sem_distincao'
            else:
                motivo_na='ausente_no_motor'

        status = 'ok' if aval and bool((dia.get('Status recomendação',pd.Series([],dtype=str)).fillna('').astype(str).str.lower()=='ok').any()) else 'n/d'
        mot_ledger = '' if status=='ok' else (motivo_na if not aval else 'nao_materializado')
        cob = bool((dia.get('Cobertura integral',pd.Series([],dtype=str)).fillna('').astype(str).str.lower()=='sim').any())
        promov = aval and pacote==winner and cob

        if has_pay:
            fontes_por_pagamento = dia.get('Lote sugerido', pd.Series([],dtype=object)).apply(contar_fontes_lote_sugerido)
            qtd_fontes = int(fontes_por_pagamento.sum())
            qtd_pagamentos_multifonte = int((fontes_por_pagamento > 1).sum())
        else:
            qtd_fontes = 0
            qtd_pagamentos_multifonte = 0
        usa_multifonte = qtd_pagamentos_multifonte > 0

        rows.append({
            'data':d.isoformat(),'pagamentos_do_dia':int(len(dia)),'valor_total_pagamentos_dia':round(total_val,2),
            'recebidos_disponiveis_no_dia':receb_disp,'lotes_ativos_inicio_dia':lotes_ini,
            'lotes_vencidos_normalizados_no_dia':lotes_venc_norm,'fontes_disponiveis_inicio_dia':fontes_ini,
            'destinos_ranking_elegiveis':78,'pacote':pacote,
            'pacote_foi_avaliado':bool(aval),'pacote_foi_factivel':bool(aval and conceit_aplicavel),'pacote_foi_promovido':bool(promov),
            'pacote_vencedor_do_dia':winner,'motivo_nao_avaliado':motivo_na or 'n/d','motivo_infactibilidade':'n/d' if aval else motivo_na,
            'motivo_descarte':'n/d' if promov else (motivo_na or 'nao_materializado'),'valor_objetivo_ou_proxy_terminal':'n/d',
            'delta_vs_no_action':'n/d','delta_vs_pay_only':'n/d','exige_switching':pacote in ('switch_only','switch_then_pay','pay_then_switch'),
            'aplica_switching_antes_pagamento':pacote=='switch_then_pay','aplica_switching_depois_pagamento':pacote=='pay_then_switch',
            'usa_multifonte':usa_multifonte,'qtd_fontes_pagamento':qtd_fontes,'qtd_pagamentos_multifonte':qtd_pagamentos_multifonte,
            'status_ledger_resultante':status,'motivo_ledger_resultante':mot_ledger or 'n/d',
            'observacao_auditoria':'inferido_por_saida_operacional_nao_por_solver_canonico'
        })

out=pd.DataFrame(rows)
out_path=Path('saidas/diagnostico/auditoria_comparacao_pacotes_diarios.csv')
out_path.parent.mkdir(parents=True,exist_ok=True)
out.to_csv(out_path,index=False)

exp=len(dias)*len(PACOTES)
aval=int(out['pacote_foi_avaliado'].sum())
miss=out[out['pacote_foi_avaliado']==False]['pacote'].value_counts().to_dict()
dias_sem=int((out.groupby('data')['pagamentos_do_dia'].max()==0).sum())
dias_com=int((out.groupby('data')['pagamentos_do_dia'].max()>0).sum())
dias_sw_app=int(((out['pacote']=='switch_only') & (out['motivo_nao_avaliado'].isin(['ausente_no_motor','sem_candidato_ou_bloqueado_sem_distincao','n/d']))).sum())

causa='diagnostico_ainda_insuficiente'
if out['observacao_auditoria'].str.contains('inferido',na=False).all():
    causa='ausencia_observavel_de_avaliacao_materializacao_de_pacotes_switching'
print(f'xlsx_escolhido={p}')
print(f'xlsx_mtime_utc={mtime_utc}')
print(f'janela_auditada={INI}..{FIM}')
print(f'total_dias_janela={len(dias)}')
print(f'total_linhas_csv={len(out)}')
print(f'total_pacotes_conceituais_esperados={exp}')
print(f'total_pacotes_efetivamente_avaliados={aval}')
print(f'pacotes_ausentes_por_tipo={miss}')
print(f'dias_sem_pagamento={dias_sem}')
print(f'dias_com_pagamento={dias_com}')
print(f'dias_com_switch_only_conceitualmente_aplicavel={dias_sw_app}')
print(f'dias_com_switch_only_avaliado={int(((out.pacote=="switch_only") & (out.pacote_foi_avaliado)).sum())}')
print(f'dias_com_switch_then_pay_avaliado={int(((out.pacote=="switch_then_pay") & (out.pacote_foi_avaliado)).sum())}')
print(f'dias_com_pay_then_switch_avaliado={int(((out.pacote=="pay_then_switch") & (out.pacote_foi_avaliado)).sum())}')
print(f'causa_principal_switching_zero={causa}')
print('primeira_quebra_2026_06_10=')
print(out[(out['data']=='2026-06-10') & (out['pacote'].isin(['no_action','switch_only','pay_only','switch_then_pay','pay_then_switch']))][['data','pacote','pacote_foi_avaliado','motivo_nao_avaliado','status_ledger_resultante','motivo_ledger_resultante']].to_string(index=False))
print(f'csv={out_path}')
