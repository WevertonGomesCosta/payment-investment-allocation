"""Inspeciona o benchmark shadow do resolver_hibrido_5p legado."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_PAG = [
    'pagamento_id',
    'data_pagamento',
    'valor_pagamento',
    'status_benchmark',
    'qtd_lotes_candidatos',
    'qtd_lotes_usados_hibrido',
    'valor_bruto_total_hibrido',
    'valor_liquido_total_hibrido',
    'custo_total_proxy_hibrido',
    'benchmark_totalmente_coberto',
    'lote_principal_hibrido',
    'lote_principal_local_v1',
    'diverge_decisao_local_v1',
]

COLUNAS_ALOC = [
    'pagamento_id',
    'lote_id',
    'produto_nome',
    'saldo_bruto_pagamento',
    'saldo_liquido_pagamento',
    'custo_unitario_hibrido',
    'valor_bruto_alocado_hibrido',
    'valor_liquido_alocado_hibrido',
    'participacao_liquida_pct',
    'escolhido_no_benchmark',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.resolver_hibrido_5p_shadow
    quadro = pacote.quadro_pagamentos_benchmark
    aloc = pacote.quadro_alocacoes_shadow
    auditoria = pacote.auditoria
    validacao = pacote.validacao

    print('=== BENCHMARK SHADOW DO resolver_hibrido_5p ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"parametros_hibrido_shadow: {auditoria.get('parametros_hibrido_shadow', {})}")
    print(f"total_pagamentos_alvo: {auditoria.get('resumo', {}).get('total_pagamentos_alvo')}")
    print(f"pagamentos_totalmente_cobertos: {auditoria.get('resumo', {}).get('pagamentos_totalmente_cobertos')}")
    print(f"pagamentos_multifonte_shadow: {auditoria.get('resumo', {}).get('pagamentos_multifonte_shadow')}")
    print(f"pagamentos_com_divergencia_vs_local_v1: {auditoria.get('resumo', {}).get('pagamentos_com_divergencia_vs_local_v1')}")
    print(f"status_benchmark: {auditoria.get('resumo', {}).get('status_benchmark', {})}")
    print(f"lote_principal_hibrido: {auditoria.get('resumo', {}).get('lote_principal_hibrido', {})}")
    print(f"qtd_linhas_alocacao_shadow: {auditoria.get('resumo', {}).get('qtd_linhas_alocacao_shadow')}")
    print(f"status_validacao: {'OK' if validacao.get('ok') else 'FALHA'}")
    if validacao.get('avisos'):
        print(f"avisos: {validacao['avisos']}")
    if validacao.get('erros'):
        print(f"erros: {validacao['erros']}")
        return 1

    if len(quadro) == 0:
        print('quadro vazio')
        return 1

    print('\n--- PAGAMENTOS BENCHMARK ---')
    print(quadro[COLUNAS_PAG].head(20).to_string(index=False))

    escolhidos = aloc[aloc['escolhido_no_benchmark'].eq(True)].copy() if len(aloc) else aloc
    print('\n--- ALOCAÇÕES SHADOW ESCOLHIDAS ---')
    if len(escolhidos) > 0:
        print(escolhidos[COLUNAS_ALOC].head(30).to_string(index=False))
    else:
        print('sem alocações shadow escolhidas')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
