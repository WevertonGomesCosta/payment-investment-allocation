from __future__ import annotations
import hashlib, sys
from pathlib import Path
import pandas as pd
RAIZ=Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0,str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
DADOS=RAIZ/'dados/dados_financeiros.xlsx'; CACHE=RAIZ/'dados/cache_bcb.json'
CSV=RAIZ/'saidas/diagnostico/auditar_consumo_lotes_pos_switching_v17_f0_q5b.csv'

def h(p):
 x=hashlib.sha256(); x.update(Path(p).read_bytes()); return x.hexdigest()

def main():
 h0,hc0=h(DADOS),h(CACHE)
 ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_resolver_hibrido_5p_shadow=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
 s=construir_saida_canonica_com_switching_v17_c7(ctx,versao=VERSAO_BASELINE)
 ex=[x for x in s.extrato_passado if str(x.get('Lote') or '').strip().lower() in {'lote 190 mai','lote 3120 mai'}]
 ativos=[x for x in s.lotes_ativos if str(x.get('Lote') or '').strip().lower() in {'lote 190 mai','lote 3120 mai'}]
 exaur=[x for x in s.lotes_exauridos if str(x.get('Lote') or '').strip().lower() in {'lote 190 mai','lote 3120 mai'}]
 r={'qtd_lotes_pos_normalizados':len(getattr(ctx.dados_operacionais,'lotes_pos_switching_normalizados',pd.DataFrame())),
    'qtd_pagamentos_passados_pos_detectados':len(ex),
    'qtd_pagamentos_passados_pos_com_saldo_antes_preenchido':sum(1 for x in ex if x.get('Saldo Antes') is not None and str(x.get('Saldo Antes')).strip()!=''),
    'qtd_pagamentos_passados_pos_com_saldo_remanescente_preenchido':sum(1 for x in ex if x.get('Saldo Remanescente') is not None and str(x.get('Saldo Remanescente')).strip()!=''),
    'qtd_lotes_pos_exauridos_apos_consumo':len(exaur),
    'qtd_lotes_pos_ativos_com_saldo_abatido':sum(1 for x in ativos if float(x.get('Saldo rem') or 0)<float(x.get('Valor original') or 0)),
    'status_geral_q5b':'consumo_pos_switching_integrado' if len(ex)==2 and len(exaur)>=1 else 'integracao_parcial'}
 for lote in ['lote 190 mai','lote 3120 mai']:
  lin=next((x for x in ex if str(x.get('Lote') or '').strip().lower()==lote),{})
  r[f'{lote}_saldo_antes']=lin.get('Saldo Antes','')
  r[f'{lote}_saldo_remanescente']=lin.get('Saldo Remanescente','')
 h1,hc1=h(DADOS),h(CACHE)
 r['dados_financeiros_modificado_apos_execucao']='sim' if h0!=h1 else 'nao'
 r['cache_bcb_modificado_apos_execucao']='sim' if hc0!=hc1 else 'nao'
 CSV.parent.mkdir(parents=True,exist_ok=True); pd.DataFrame([r]).to_csv(CSV,index=False)
 for k,v in r.items(): print(f'{k}={v}')
 print(f'csv={CSV}')
if __name__=='__main__': main()
