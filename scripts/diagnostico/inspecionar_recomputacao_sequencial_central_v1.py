"""Inspeciona a recomputação sequencial central v1."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional',
    'lote_sugerido_original', 'lote_final_central', 'status_central', 'deficit_liquido_total',
    'patrimonio_terminal_proxy', 'mudou_vs_decisao_local',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.recomputacao_sequencial_central_v1
    quadro = pacote.quadro_recomputacao_sequencial_central
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== RECOMPUTAÇÃO SEQUENCIAL CENTRAL V1 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_auditados: {resumo.get('total_pagamentos_auditados', 0)}")
    print(f"pagamentos_cobertos_integral_central: {resumo.get('pagamentos_cobertos_integral_central', 0)}")
    print(f"pagamentos_sem_cobertura_integral: {resumo.get('pagamentos_sem_cobertura_integral', 0)}")
    print(f"violacoes_pagamentos_protegida: {resumo.get('violacoes_pagamentos_protegida', 0)}")
    print(f"deficit_liquido_total_central: {resumo.get('deficit_liquido_total_central', 0.0)}")
    print(f"mudancas_vs_decisao_local: {resumo.get('mudancas_vs_decisao_local', 0)}")
    print(f"patrimonio_terminal_proxy_final: {resumo.get('patrimonio_terminal_proxy_final', 0.0)}")
    print(f"primeira_sem_cobertura: {resumo.get('primeira_sem_cobertura_data')} | {resumo.get('primeira_sem_cobertura_pagamento')}")
    print(f"primeira_violacao_protegida: {resumo.get('primeira_violation_protegida_data')} | {resumo.get('primeira_violation_protegida_pagamento')}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1

    print('\n--- AMOSTRA DE MUDANÇAS ---')
    for item in (auditoria.get('amostra_mudancas') or [])[:10]:
        print(item)

    print('\n--- QUADRO CENTRAL (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
