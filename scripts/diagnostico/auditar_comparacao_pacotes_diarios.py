from __future__ import annotations
import pandas as pd
from pathlib import Path

INI='2026-05-06'; FIM='2026-06-15'
PACOTES=['no_action','switch_only','pay_only','switch_then_pay','pay_then_switch']

p=Path('saidas/oficial/relatorio_operacional_v225.xlsx')
if not p.exists():
    raise SystemExit('ERRO: execute python aplicacao/principal.py antes')
xf=pd.ExcelFile(p)
ext=pd.read_excel(p,sheet_name='Extrato Futuro')
aud=pd.read_excel(p,sheet_name='Auditoria Fontes') if 'Auditoria Fontes' in xf.sheet_names else pd.DataFrame()
sit=pd.read_excel(p,sheet_name='Situação Atual') if 'Situação Atual' in xf.sheet_names else pd.DataFrame()

ext['Data']=pd.to_datetime(ext['Data'],errors='coerce').dt.date
jan=ext[(ext['Data']>=pd.to_datetime(INI).date()) & (ext['Data']<=pd.to_datetime(FIM).date())].copy()
if aud is not None and len(aud):
    aud['Data']=pd.to_datetime(aud['Data'],errors='coerce').dt.date
    aud=aud[(aud['Data']>=pd.to_datetime(INI).date()) & (aud['Data']<=pd.to_datetime(FIM).date())].copy()

rows=[]
for d in sorted(jan['Data'].dropna().unique()):
    dia=jan[jan['Data']==d]
    has_pay=len(dia)>0
    total_val=float(pd.to_numeric(dia['Valor'],errors='coerce').fillna(0).sum())
    pacotes_dia=set(str(x).strip().lower() for x in dia.get('Pacote do dia',pd.Series([],dtype=str)).fillna(''))
    winner='pay_only' if has_pay else 'no_action'
    if 'switch_then_pay' in pacotes_dia: winner='switch_then_pay'
    if 'pay_then_switch' in pacotes_dia: winner='pay_then_switch'
    if 'switch_only' in pacotes_dia and not has_pay: winner='switch_only'
    cand_sw=False
    if len(aud):
        ad=aud[aud['Data']==d]
        cand_sw=bool((ad.get('evento_switching_id',pd.Series([],dtype=str)).fillna('').astype(str).str.strip()!='').any() or (ad.get('origem_fonte_candidata',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('switch',case=False)).any())
    for pacote in PACOTES:
        aval = pacote in pacotes_dia
        fact = aval and bool((dia.get('Status recomendação',pd.Series([],dtype=str)).fillna('').astype(str)!='sem_saldo_temporal_auditavel').any())
        promov = aval and pacote==winner and bool((dia.get('Cobertura integral',pd.Series([],dtype=str)).fillna('').astype(str).str.lower()=='sim').any())
        mna=''
        if not aval:
            if pacote in ('no_action','switch_only') and has_pay: mna='sem_pagamento_no_dia_nao_se_aplica'
            elif pacote in ('pay_only','switch_then_pay','pay_then_switch') and not has_pay: mna='sem_pagamento_no_dia'
            elif 'switch' in pacote and not cand_sw: mna='sem_switching_candidato'
            else: mna='ausente_no_motor'
        st='ok' if fact else ('sem_saldo_temporal_auditavel' if has_pay and pacote.startswith('pay') else 'nao_materializado')
        mot='' if fact else (mna or 'infactivel')
        usa_multifonte=False; qtd_fontes=1
        if has_pay:
            qtd_fontes=int(dia.get('Lote sugerido',pd.Series([],dtype=str)).fillna('').astype(str).str.contains('\+').sum())
            usa_multifonte=qtd_fontes>0
        rows.append({
            'data':d.isoformat(),'pagamentos_do_dia':int(len(dia)),'valor_total_pagamentos_dia':round(total_val,2),
            'recebidos_disponiveis_no_dia':None,'lotes_ativos_inicio_dia':None,'lotes_vencidos_normalizados_no_dia':None,
            'fontes_disponiveis_inicio_dia':None,'destinos_ranking_elegiveis':78,
            'pacote':pacote,'pacote_foi_avaliado':bool(aval),'pacote_foi_factivel':bool(fact),'pacote_foi_promovido':bool(promov),
            'pacote_vencedor_do_dia':winner,'motivo_nao_avaliado':mna,'motivo_infactibilidade':'' if fact else mot,
            'motivo_descarte':'' if promov else mot,'valor_objetivo_ou_proxy_terminal':None,
            'delta_vs_no_action':None,'delta_vs_pay_only':None,
            'exige_switching': pacote in ('switch_only','switch_then_pay','pay_then_switch'),
            'aplica_switching_antes_pagamento': pacote=='switch_then_pay','aplica_switching_depois_pagamento': pacote=='pay_then_switch',
            'usa_multifonte':usa_multifonte,'qtd_fontes_pagamento':qtd_fontes,
            'status_ledger_resultante':st,'motivo_ledger_resultante':mot,
            'observacao_auditoria':'linha conceitual; inferida por Extrato Futuro/Auditoria Fontes'
        })

out=pd.DataFrame(rows)
Path('saidas/diagnostico').mkdir(parents=True,exist_ok=True)
out_path=Path('saidas/diagnostico/auditoria_comparacao_pacotes_diarios.csv')
out.to_csv(out_path,index=False)

# summary
exp=len(out)
aval=int(out['pacote_foi_avaliado'].sum())
miss=out[~out['pacote_foi_avaliado']]['pacote'].value_counts().to_dict()
sw=out[out['pacote'].isin(['switch_only','switch_then_pay','pay_then_switch'])]
causa='ausencia_de_candidatos' if int(sw['pacote_foi_avaliado'].sum())==0 else 'incerto'
if miss.get('switch_only',0)>0: causa='switch_only_nao_avaliado'
if miss.get('switch_then_pay',0)>0 and miss.get('pay_then_switch',0)>0: causa='ausencia_de_integracao_com_pagamento'
print(f'janela_auditada={INI}..{FIM}')
print(f'total_dias={out["data"].nunique()}')
print(f'total_pacotes_conceituais_esperados={exp}')
print(f'total_pacotes_efetivamente_avaliados={aval}')
print(f'pacotes_ausentes_por_tipo={miss}')
print(f'causa_principal_switching_zero={causa}')
crit=out[(out['data']=='2026-06-10') & (out['pacote'].isin(['pay_only','switch_then_pay','pay_then_switch']))]
print('primeira_quebra_2026_06_10=')
print(crit[['data','pacote','pacote_foi_avaliado','motivo_nao_avaliado','motivo_infactibilidade','status_ledger_resultante']].to_string(index=False))
print(f'csv={out_path}')
