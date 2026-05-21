from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import construir_amostras_pagamentos_operacionais, construir_linhas_lotes_consolidados


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--sem-csv', action='store_true'); parser.parse_args()
    ctx = carregar_contexto_baseline(raiz_repositorio=ROOT, instalar_automaticamente=False, incluir_benchmark_agrupado_individual_shadow=False)
    saida = construir_saida_canonica(ctx)
    pacotes = construir_pacotes_temporais_agregados_saida_shadow(ctx)
    ativos = construir_linhas_lotes_consolidados(ctx, saida, tipo='ativos')
    exauridos = construir_linhas_lotes_consolidados(ctx, saida, tipo='exauridos')
    am = construir_amostras_pagamentos_operacionais(saida, limite=1000, contexto=ctx)
    realizados = list((am.get('realizados') or {}).get('linhas') or [])

    p = construir_pacote_saida_observavel_temporal(ctx, saida, pacotes_temporais=pacotes,
        lotes_ativos_observaveis=ativos, lotes_exauridos_observaveis=exauridos, pagamentos_realizados_observaveis=realizados)
    a, v = p.auditoria_saida_observavel_temporal, p.validacao_saida_observavel_temporal
    out = {
      'pacote_saida_observavel_temporal_criado': True,
      'usa_pacotes_temporais_agregados': a.get('usa_pacotes_temporais_agregados', False),
      'usa_saida_apenas_como_snapshot_observavel': a.get('usa_saida_apenas_como_snapshot_observavel', False),
      'nao_importa_saida_observavel': a.get('nao_importa_saida_observavel', False),
      'nao_altera_saida_canonica': a.get('nao_altera_saida_canonica', False),
      'nao_altera_saida_observavel': a.get('nao_altera_saida_observavel', False),
      'nao_altera_replay_efetivo': a.get('nao_altera_replay_efetivo', False),
      'nao_altera_ledger_efetivo': a.get('nao_altera_ledger_efetivo', False),
      'origem_lotes_ativos_exauridos': a.get('origem_lotes_ativos_exauridos'),
      'lote_3120_mai_presente_ativos': a.get('lote_3120_mai_presente_ativos_snapshot', False),
      'lote_3120_mai_presente_exauridos': a.get('lote_3120_mai_presente_exauridos_snapshot', False),
      'lote_3120_mai_saldo_final': a.get('lote_3120_mai_saldo_final', 0.0),

      "pagamentos_replay_sem_colisao": a.get("pagamentos_replay_sem_colisao", False),
      "qtd_colisoes_chave_pagamento": a.get("qtd_colisoes_chave_pagamento", 0),
      "qtd_pagamentos_replay_linhas": a.get("qtd_pagamentos_replay_linhas", 0),
      "qtd_pagamentos_replay_chaves_unicas": a.get("qtd_pagamentos_replay_chaves_unicas", 0),
      "valor_sacado_lote_3120_mai": a.get("valor_sacado_lote_3120_mai", 0.0),
      'sem_duplicidade_ativos_exauridos': 'lotes_duplicados_ativos_exauridos' not in v.get('erros_bloqueantes', []),
      'mapas_substitutivos_criados': all([len(p.saldos_finais_replay_por_lote)>0,len(p.pagamentos_replay_por_chave)>0]),
      'pacote_pronto_para_migracao_v4v': bool(a.get('prepara_migracao_v4v', False)),
      'helpers_legados_ainda_existentes': True,
      'etapa5_pode_abrir_agora': False,
      'proxima_etapa_recomendada': 'V17-F0-V.4V',
      'validacao_v4u_ok': bool(v.get('ok', False)),
      'qtd_saldos_finais_replay_por_lote': len(p.saldos_finais_replay_por_lote),
      'qtd_pagamentos_replay_por_chave': len(p.pagamentos_replay_por_chave),
      'qtd_aplicacoes_por_lote': len(p.aplicacoes_por_lote),
      'qtd_produtos_por_lote': len(p.produtos_por_lote),
      'qtd_valores_originais_por_lote': len(p.valores_originais_por_lote),
      'qtd_valores_sacados_por_lote': len(p.valores_sacados_por_lote),
      'qtd_lotes_ativos_observaveis': len(p.lotes_ativos_observaveis),
      'qtd_lotes_exauridos_observaveis': len(p.lotes_exauridos_observaveis),
      'qtd_pagamentos_realizados_observaveis': len(p.pagamentos_realizados_observaveis),
    }
    for k,v in out.items(): print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
