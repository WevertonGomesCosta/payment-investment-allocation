from __future__ import annotations
import pandas as pd
from pathlib import Path

RECORTE_INI=None
RECORTE_FIM=None
PACOTES=['no_action','switch_only','pay_only','switch_then_pay','pay_then_switch']

def contar_fontes_lote_sugerido(valor) -> int:
    txt=str(valor or '').strip()
    if txt.lower() in {'','n/d','nd','nan','none','-'}:
        return 0
    partes=[p.strip() for p in txt.split('+') if p.strip()]
    return len(partes) if partes else 0

def norm(v)->str:
    return str(v or '').strip().lower()

oficiais=sorted(Path('saidas/oficial').glob('*.xlsx'), key=lambda x: x.stat().st_mtime, reverse=True)
if not oficiais:
    raise SystemExit('ERRO: nenhum xlsx encontrado em saidas/oficial; execute python aplicacao/principal.py antes.')
p=oficiais[0]
mtime_utc=pd.Timestamp.utcfromtimestamp(p.stat().st_mtime).isoformat()+'Z'

xf=pd.ExcelFile(p)
ext=pd.read_excel(p,sheet_name='Extrato Futuro')
aud=pd.read_excel(p,sheet_name='Auditoria Fontes') if 'Auditoria Fontes' in xf.sheet_names else pd.DataFrame()

ext['Data']=pd.to_datetime(ext['Data'],errors='coerce').dt.date
ext=ext[ext['Data'].notna()].copy()
if len(ext)==0:
    raise SystemExit('ERRO: Extrato Futuro vazio ou sem datas válidas no xlsx oficial.')
ext['_pacote_norm']=ext.get('Pacote do dia',pd.Series('',index=ext.index)).fillna('').astype(str).str.strip().str.lower()
ext['_status_norm']=ext.get('Status recomendação',pd.Series('',index=ext.index)).fillna('').astype(str).str.strip().str.lower()
ext['_cob_norm']=ext.get('Cobertura integral',pd.Series('',index=ext.index)).fillna('').astype(str).str.strip().str.lower()
if len(aud):
    aud['Data']=pd.to_datetime(aud['Data'],errors='coerce').dt.date

ini_data=min(ext['Data']); fim_data=max(ext['Data'])
if RECORTE_INI is not None:
    ini_data=max(ini_data, pd.to_datetime(RECORTE_INI).date())
if RECORTE_FIM is not None:
    fim_data=min(fim_data, pd.to_datetime(RECORTE_FIM).date())
if ini_data>fim_data:
    raise SystemExit('ERRO: recorte inválido após aplicar RECORTE_INI/RECORTE_FIM.')
dias=[d.date() for d in pd.date_range(ini_data,fim_data,freq='D')]

carteira=pd.read_excel(p,sheet_name='Carteira') if 'Carteira' in xf.sheet_names else pd.DataFrame()
destinos_ranking_elegiveis_runtime=0
if len(carteira):
    if 'Rank' in carteira.columns:
        destinos_ranking_elegiveis_runtime=int(pd.to_numeric(carteira['Rank'],errors='coerce').notna().sum())
    elif 'Produto' in carteira.columns:
        destinos_ranking_elegiveis_runtime=int(carteira['Produto'].fillna('').astype(str).str.strip().ne('').sum())
rows=[]
for d in dias:
    dia=ext[ext['Data']==d].copy()
    ad=aud[aud['Data']==d].copy() if len(aud) else pd.DataFrame()
    has_pay=len(dia)>0

    materializadas = dia[(dia['_status_norm']=='ok') & (dia['_cob_norm'].isin(['sim','true','1']))]
    packs_mat=sorted(set(materializadas['_pacote_norm'].tolist()))
    switch_only_materializado = 'switch_only' in packs_mat
    if not has_pay:
        vencedor='switch_only' if switch_only_materializado else 'no_action'
    elif len(packs_mat)==1:
        vencedor=packs_mat[0]
    elif len(packs_mat)>1:
        vencedor='misto'
    else:
        vencedor='indeterminado_por_saida'

    cand_sw = bool((ad.get('evento_switching_id',pd.Series([],dtype=str)).fillna('').astype(str).str.strip()!='').any() or (ad.get('origem_fonte_candidata',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('switch',case=False,na=False)).any())
    receb_disp = int((ad.get('tipo_fonte_candidata',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('recebido|caixa_pre_aplicacao',case=False,regex=True)).sum()) if len(ad) else 'n/d'
    lotes_ini = int(ad.get('fonte_candidata_id',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('lote',case=False,na=False).sum()) if len(ad) else 'n/d'
    fontes_ini = int(ad.get('fonte_candidata_id',pd.Series([],dtype=str)).fillna('').astype(str).str.strip().ne('').sum()) if len(ad) else 'n/d'
    total_val=float(pd.to_numeric(dia.get('Valor',pd.Series([],dtype=float)),errors='coerce').fillna(0).sum())

    if has_pay:
        fontes_por_pagamento = dia.get('Lote sugerido', pd.Series([],dtype=object)).apply(contar_fontes_lote_sugerido)
        qtd_fontes = int(fontes_por_pagamento.sum())
        qtd_pagamentos_multifonte = int((fontes_por_pagamento > 1).sum())
    else:
        qtd_fontes=0; qtd_pagamentos_multifonte=0

    for pacote in PACOTES:
        dia_pacote=dia[dia['_pacote_norm'].eq(pacote)]
        aval = len(dia_pacote)>0
        status_ok = bool((dia_pacote['_status_norm']=='ok').any()) if aval else False
        cob_ok = bool((dia_pacote['_cob_norm'].isin(['sim','true','1'])).any()) if aval else False

        motivo_na='n/d'
        if not aval:
            if has_pay and pacote in ('no_action','switch_only'):
                motivo_na='nao_aplicavel_por_haver_pagamento_no_dia'
            elif (not has_pay) and pacote in ('pay_only','switch_then_pay','pay_then_switch'):
                motivo_na='sem_pagamento_no_dia'
            elif pacote in ('switch_only','switch_then_pay','pay_then_switch') and not (cand_sw or switch_only_materializado):
                motivo_na='sem_candidato_ou_bloqueado_sem_distincao'
            else:
                motivo_na='ausente_no_motor'

        # factibilidade conceitual independe de evidência runtime (aval)
        if not has_pay:
            if pacote == 'no_action':
                factivel = True
            elif pacote == 'switch_only':
                factivel = bool(cand_sw or switch_only_materializado)
            else:
                factivel = False
        else:
            if pacote in ('no_action','switch_only'):
                factivel = False
            elif pacote == 'pay_only':
                factivel = True
            else:
                factivel = bool(cand_sw)

        if not has_pay and pacote=='no_action' and vencedor=='no_action' and not switch_only_materializado:
            promov=True
        elif not has_pay and pacote=='switch_only' and vencedor=='switch_only':
            promov=bool(aval and status_ok and cob_ok)
        elif vencedor in ('misto','indeterminado_por_saida'):
            promov=False
        else:
            promov = bool(aval and pacote==vencedor and status_ok and cob_ok)

        status='ok' if status_ok else 'n/d'
        motivo_ledger='n/d' if status_ok else (motivo_na if not aval else 'nao_materializado')
        obs='inferido_por_saida_operacional_nao_por_solver_canonico'
        if not has_pay and pacote=='no_action' and vencedor=='no_action' and not switch_only_materializado:
            obs += ';vencedor_conceitual_sem_evento_runtime'
        if not has_pay and pacote=='switch_only' and not (cand_sw or switch_only_materializado):
            obs += ';limite_inferencia_sem_candidato_ou_gate'
        if vencedor=='misto':
            obs += ';pacotes_materializados_multiplos'

        rows.append({
            'data':d.isoformat(),'pagamentos_do_dia':int(len(dia)),'valor_total_pagamentos_dia':round(total_val,2),
            'recebidos_disponiveis_no_dia':receb_disp,'lotes_ativos_inicio_dia':lotes_ini,
            'lotes_vencidos_normalizados_no_dia':'n/d','fontes_disponiveis_inicio_dia':fontes_ini,
            'destinos_ranking_elegiveis':destinos_ranking_elegiveis_runtime,'pacote':pacote,
            'pacote_foi_avaliado':aval,'pacote_foi_factivel':factivel,
            'pacote_foi_promovido':promov,'pacote_vencedor_do_dia':vencedor,
            'motivo_nao_avaliado':motivo_na,'motivo_infactibilidade':'n/d' if aval else motivo_na,'motivo_descarte':'n/d' if promov else (motivo_na if not aval else 'nao_materializado'),
            'valor_objetivo_ou_proxy_terminal':'n/d','delta_vs_no_action':'n/d','delta_vs_pay_only':'n/d',
            'exige_switching':pacote in ('switch_only','switch_then_pay','pay_then_switch'),
            'aplica_switching_antes_pagamento':pacote=='switch_then_pay','aplica_switching_depois_pagamento':pacote=='pay_then_switch',
            'usa_multifonte':qtd_pagamentos_multifonte>0,'qtd_fontes_pagamento':qtd_fontes,'qtd_pagamentos_multifonte':qtd_pagamentos_multifonte,
            'status_ledger_resultante':status,'motivo_ledger_resultante':motivo_ledger,'observacao_auditoria':obs
        })

out=pd.DataFrame(rows)
out_path=Path('saidas/diagnostico/auditoria_comparacao_pacotes_diarios.csv')
out_path.parent.mkdir(parents=True,exist_ok=True)
out.to_csv(out_path,index=False)

print(f'xlsx_escolhido={p}')
print(f'xlsx_mtime_utc={mtime_utc}')
print(f'janela_auditada_inicio={ini_data}')
print(f'janela_auditada_fim={fim_data}')
print(f'total_dias_janela={len(dias)}')
print(f'total_linhas_csv={len(out)}')
print(f'total_pacotes_conceituais_esperados={len(dias)*len(PACOTES)}')
print(f'total_pacotes_efetivamente_avaliados={int(out["pacote_foi_avaliado"].sum())}')
print(f'pacotes_ausentes_por_tipo={out[out["pacote_foi_avaliado"]==False]["pacote"].value_counts().to_dict()}')
print(f'total_datas_com_pagamento={int((out.groupby("data")["pagamentos_do_dia"].max()>0).sum())}')
print(f'total_datas_sem_pagamento={int((out.groupby("data")["pagamentos_do_dia"].max()==0).sum())}')
print(f'destinos_ranking_elegiveis_runtime={destinos_ranking_elegiveis_runtime}')
print('primeira_quebra_2026_06_10=')
print(out[out['data'].eq('2026-06-10')][['data','pacote','pacote_foi_avaliado','pacote_vencedor_do_dia','status_ledger_resultante','motivo_nao_avaliado']].to_string(index=False))
print(f'csv={out_path}')
