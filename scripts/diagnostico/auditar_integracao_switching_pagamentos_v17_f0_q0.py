from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
import pandas as pd
RAIZ=Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0,str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2
ARQ=RAIZ/'saidas'/'diagnostico'/'auditar_integracao_switching_pagamentos_v17_f0_q0.csv'

def _n(v): return str(v or '').strip().lower()
def _d(v):
    try: return pd.to_datetime(v).date()
    except Exception: return None

def main():
    ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_resolver_hibrido_5p_shadow=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida=construir_saida_canonica_com_switching_v17_c7(ctx,versao=VERSAO_BASELINE)
    sw=[dict(x) for x in (saida.switchings or []) if isinstance(x,dict)]
    ev=materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(ctx)
    extrato=[dict(x) for x in (saida.extrato_futuro or []) if isinstance(x,dict)]
    lotes_pos=[dict(x) for x in (getattr(saida,'lotes_sinteticos_pos_switching_console',lambda **_:[]) (limite=300) or [])]
    origens={_n(x.get('lote_origem')):_d(x.get('data_switching')) for x in sw}
    lotes_dest={_n(x.get('lote_destino') or x.get('lote_pos_switching')) for x in sw}
    rows=[]
    for i,r in enumerate(extrato,1):
        data=_d(r.get('Data')); lote=_n(r.get('Lote sugerido')); pacote=_n(r.get('Pacote do dia')) or _n(r.get('pacote_do_dia_ledger'))
        pid=str(r.get('Despesa ID') or f'idx_{i}')
        fonte=str(r.get('Lote sugerido') or '')
        multi=' + ' in fonte
        usa_pos=lote in lotes_dest if lote else any(_n(p) in lotes_dest for p in fonte.split('+'))
        usa_origem=any(_n(p.strip()) in origens for p in fonte.split('+'))
        origem_apos=False
        for p in [x.strip() for x in fonte.split('+') if x.strip()]:
            dsw=origens.get(_n(p))
            if dsw and data and data>=dsw: origem_apos=True
        pos_dispon=[l for l in lotes_pos if _d(l.get('Data')) and data and _d(l.get('Data'))<=data]
        rows.append({
            'pagamento_id':pid,'data_pagamento':r.get('Data'),'conta':r.get('Conta'),'valor_pagamento':r.get('Valor'),'pacote_do_dia':pacote,
            'fonte_escolhida_renderizada':fonte,'tipo_fonte_escolhida':r.get('tipo_fonte_candidata') or r.get('tipo_fonte_escolhida'),'lote_fonte_escolhido':fonte,
            'sw_antes_pagamento':r.get('Switching antes do pagamento'),'sw_depois_pagamento':r.get('Switching depois do pagamento'),
            'fonte_eh_lote_pos_switching':usa_pos,'fonte_eh_origem_migrada':usa_origem,'origem_migrada_apos_data_switching':origem_apos,
            'lote_pos_switching_elegivel_na_data':bool(pos_dispon),'lotes_pos_switching_disponiveis_na_data':len(pos_dispon),
            'origens_migradas_bloqueadas_na_data':('sim' if not origem_apos else 'nao'),'estrutura_decisoria_origem':'saida.extrato_futuro + auditoria_temporal_decisao_local + quadro_recomendacoes',
            'funcao_decisoria_provavel':'nucleo.saida_canonica._montar_extrato_futuro_canonico / motor_recomendacao_pagamentos_switching_v1','campo_decisorio_provavel':'Lote sugerido / tipo_fonte_candidata / pacote_do_dia_ledger',
            'evidencia_codigo_ou_objeto':'extrato_futuro[*].Lote sugerido, pacote_do_dia_ledger, status_ledger',
            'status_integracao_switching':('switching_integrado_ok' if usa_pos else ('integracao_ausente_com_ponto_q1_identificado' if pacote=='pay_only' else 'pagamento_ignora_switching')),
            'problema_detectado':('pagamento continua pay_only sem usar lote pos-switching' if (pacote=='pay_only' and not usa_pos and r.get('Status recomendação')=='ok') else ''),
            'recomendacao_q1':'integrar eventos materializados ao conjunto elegivel da decisao local antes de definir Lote sugerido/pacote_do_dia',
        })
    df=pd.DataFrame(rows)
    resumo={
      'total_pagamentos_futuros':len(df),'pagamentos_status_ok':int((df['problema_detectado']!='').sum()+ (df['problema_detectado']=='').sum()),
      'pagamentos_pay_only':int((df['pacote_do_dia']=='pay_only').sum()),'pagamentos_com_sw_antes_sim':int((df['sw_antes_pagamento'].astype(str).str.lower()=='sim').sum()),
      'pagamentos_com_sw_depois_sim':int((df['sw_depois_pagamento'].astype(str).str.lower()=='sim').sum()),'pagamentos_usando_lote_pos_switching':int(df['fonte_eh_lote_pos_switching'].sum()),
      'pagamentos_usando_origem_migrada_apos_switching':int(df['origem_migrada_apos_data_switching'].sum()),'lotes_pos_switching_total':len(lotes_pos),
      'lotes_pos_switching_elegiveis_em_alguma_data':int((df['lote_pos_switching_elegivel_na_data']).sum()),'origens_migradas_total':len(origens),
      'origens_migradas_bloqueadas_total':int((df['origens_migradas_bloqueadas_na_data']=='sim').sum()),
      'status_geral_integracao':'integracao_ausente_com_ponto_q1_identificado' if int(df['fonte_eh_lote_pos_switching'].sum())==0 else 'switching_integrado_ok',
      'ponto_minimo_q1':'nucleo.saida_canonica: montagem de fontes elegíveis para Lote sugerido/pacote_do_dia_ledger (antes do extrato futuro)'
    }
    ARQ.parent.mkdir(parents=True,exist_ok=True)
    pd.concat([pd.DataFrame([{'tipo_linha':'resumo',**resumo}]),pd.DataFrame([{'tipo_linha':'detalhe',**r} for r in rows])],ignore_index=True).to_csv(ARQ,index=False)
    print('=== AUDITORIA V17-F0-Q.0 — INTEGRACAO SWITCHING X PAGAMENTOS FUTUROS ===')
    for k,v in resumo.items(): print(f'{k}={v}')
    print('cadeia_decisoria_localizada=nucleo.saida_canonica -> extrato_futuro (Lote sugerido/pacote_do_dia_ledger) com apoio de estruturas do motor e auditoria temporal')
    print(f'switchings_materializados={len(sw)} eventos_ledger={len(ev)} lotes_pos_switching={len(lotes_pos)}')
    print(f'csv={ARQ}')

if __name__=='__main__': main()
