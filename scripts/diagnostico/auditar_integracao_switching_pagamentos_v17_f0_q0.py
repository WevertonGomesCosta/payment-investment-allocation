from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
RAIZ=Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0,str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
ARQ=RAIZ/'saidas'/'diagnostico'/'auditar_integracao_switching_pagamentos_v17_f0_q0.csv'

def _n(v): return str(v or '').strip().lower()
def _d(v):
    try:return pd.to_datetime(v).date()
    except Exception:return None

def _pick_status(row:dict):
    for k in ['Status recomendação','status_ledger','Status','status']:
        v=str(row.get(k) or '').strip()
        if v: return k,v
    return 'status_nao_localizado',''

def montar_resumo_e_detalhes_integracao_switching(extrato,sw,lotes_pos):
    origens={_n(x.get('lote_origem')):_d(x.get('data_switching')) for x in sw}
    destinos={_n(x.get('lote_destino') or x.get('lote_pos_switching')) for x in sw}
    detalhes=[]
    for i,r in enumerate(extrato,1):
        data=_d(r.get('Data')); fonte=str(r.get('Lote sugerido') or ''); lote_parts=[x.strip() for x in fonte.split('+') if x.strip()]
        campo_status,status_usado=_pick_status(r)
        usa_pos=any(_n(p) in destinos for p in lote_parts)
        origem_apos=any((origens.get(_n(p)) and data and data>=origens.get(_n(p))) for p in lote_parts)
        pos_dispon=[l for l in lotes_pos if _d(l.get('Data')) and data and _d(l.get('Data'))<=data]
        pacote=_n(r.get('Pacote do dia') or r.get('pacote_do_dia_ledger'))
        detalhes.append({'pagamento_id':r.get('Despesa ID') or f'idx_{i}','data_pagamento':r.get('Data'),'conta':r.get('Conta'),'valor_pagamento':r.get('Valor'),'status_recomendacao':r.get('Status recomendação',''),'status_ledger':r.get('status_ledger',''),'campo_status_usado':campo_status,'status_usado':status_usado,'pacote_do_dia':pacote,'fonte_escolhida_renderizada':fonte,'tipo_fonte_escolhida':r.get('tipo_fonte_escolhida',''),'tipo_fonte_candidata':r.get('tipo_fonte_candidata',''),'lote_fonte_escolhido':fonte,'sw_antes_pagamento':r.get('Switching antes do pagamento'),'sw_depois_pagamento':r.get('Switching depois do pagamento'),'fonte_eh_lote_pos_switching':usa_pos,'fonte_eh_origem_migrada':any(_n(p) in origens for p in lote_parts),'origem_migrada_apos_data_switching':origem_apos,'lote_pos_switching_elegivel_na_data':bool(pos_dispon),'lotes_pos_switching_disponiveis_na_data':len(pos_dispon),'origens_migradas_bloqueadas_na_data':'nao' if origem_apos else 'sim','estrutura_decisoria_origem':'saida.extrato_futuro + quadro_recomendacoes + auditoria_temporal_decisao_local','arquivo_decisorio_provavel':'nucleo/saida_canonica.py','funcao_decisoria_provavel':'_montar_extrato_futuro_canonico','campo_decisorio_provavel':'Lote sugerido/pacote_do_dia_ledger/tipo_fonte_candidata','objeto_inspecionado':'saida.extrato_futuro[*]','evidencia_codigo_ou_objeto':'campos Lote sugerido, pacote_do_dia_ledger, tipo_fonte_candidata no extrato','status_integracao_switching':'integracao_ausente_com_ponto_q1_identificado' if (pacote=='pay_only' and not usa_pos) else 'switching_integrado_ok','problema_detectado':'pay_only sem uso de lote pos-switching' if (pacote=='pay_only' and not usa_pos and _n(status_usado)=='ok') else '','recomendacao_q1':'injetar lotes pos-switching no conjunto elegivel antes da definicao de Lote sugerido/pacote_do_dia'})
    if not detalhes:
        return {'total_pagamentos_futuros':0,'pagamentos_status_ok':0,'campo_status_usado_para_pagamentos_status_ok':'sem_pagamentos_futuros','pagamentos_pay_only':0,'pagamentos_com_sw_antes_sim':0,'pagamentos_com_sw_depois_sim':0,'pagamentos_usando_lote_pos_switching':0,'pagamentos_usando_origem_migrada_apos_switching':0,'lotes_pos_switching_total':len(lotes_pos),'lotes_pos_switching_elegiveis_em_alguma_data':0,'origens_migradas_total':len(origens),'origens_migradas_bloqueadas_total':0,'status_geral_integracao':'sem_pagamentos_futuros_para_auditar','cadeia_decisoria_localizada':'sim','arquivo_ponto_minimo_q1':'n/d','funcao_ponto_minimo_q1':'n/d','campo_ponto_minimo_q1':'n/d','ponto_minimo_q1':'n/d','evidencia_ponto_minimo_q1':'n/d'}, detalhes
    df=pd.DataFrame(detalhes)
    campo_mais_freq=df['campo_status_usado'].value_counts().index[0]
    status_ok=int((df['status_usado'].astype(str).str.lower()=='ok').sum())
    resumo={'total_pagamentos_futuros':len(df),'pagamentos_status_ok':status_ok,'campo_status_usado_para_pagamentos_status_ok':campo_mais_freq,'pagamentos_pay_only':int((df['pacote_do_dia']=='pay_only').sum()),'pagamentos_com_sw_antes_sim':int((df['sw_antes_pagamento'].astype(str).str.lower()=='sim').sum()),'pagamentos_com_sw_depois_sim':int((df['sw_depois_pagamento'].astype(str).str.lower()=='sim').sum()),'pagamentos_usando_lote_pos_switching':int(df['fonte_eh_lote_pos_switching'].sum()),'pagamentos_usando_origem_migrada_apos_switching':int(df['origem_migrada_apos_data_switching'].sum()),'lotes_pos_switching_total':len(lotes_pos),'lotes_pos_switching_elegiveis_em_alguma_data':int(df['lote_pos_switching_elegivel_na_data'].sum()),'origens_migradas_total':len(origens),'origens_migradas_bloqueadas_total':int((df['origens_migradas_bloqueadas_na_data']=='sim').sum()),'status_geral_integracao':'integracao_ausente_com_ponto_q1_identificado' if int(df['fonte_eh_lote_pos_switching'].sum())==0 else 'switching_integrado_ok','cadeia_decisoria_localizada':'sim','arquivo_ponto_minimo_q1':'nucleo/saida_canonica.py','funcao_ponto_minimo_q1':'_montar_extrato_futuro_canonico','campo_ponto_minimo_q1':'Lote sugerido/pacote_do_dia_ledger/tipo_fonte_candidata','ponto_minimo_q1':'montagem do conjunto elegivel usada para Lote sugerido antes do extrato futuro','evidencia_ponto_minimo_q1':'extrato_futuro mostra pay_only+sem uso de lotes pos-switching apesar de lotes_pos_switching_disponiveis_na_data'}
    return resumo, detalhes

def main():
    ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_resolver_hibrido_5p_shadow=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida=construir_saida_canonica_com_switching_v17_c7(ctx,versao=VERSAO_BASELINE)
    extrato=[dict(x) for x in (saida.extrato_futuro or []) if isinstance(x,dict)]
    sw=[dict(x) for x in (saida.switchings or []) if isinstance(x,dict)]
    lotes_pos=[dict(x) for x in (getattr(saida,'lotes_sinteticos_pos_switching_console',lambda **_:[])(limite=300) or [])]
    resumo,detalhes=montar_resumo_e_detalhes_integracao_switching(extrato,sw,lotes_pos)
    ARQ.parent.mkdir(parents=True,exist_ok=True)
    pd.concat([pd.DataFrame([{'tipo_linha':'resumo',**resumo}]),pd.DataFrame([{'tipo_linha':'detalhe',**x} for x in detalhes])],ignore_index=True).to_csv(ARQ,index=False)
    print('=== AUDITORIA V17-F0-Q.0.2 — INTEGRACAO SWITCHING X PAGAMENTOS FUTUROS ===')
    for k,v in resumo.items(): print(f'{k}={v}')
    print(f'csv={ARQ}')
if __name__=='__main__': main()
