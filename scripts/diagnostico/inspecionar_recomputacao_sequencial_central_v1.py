"""Inspeciona a recomputação sequencial central v1."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional',
    'lote_sugerido_original', 'lote_final_central', 'status_central', 'deficit_liquido_total',
    'patrimonio_terminal_proxy', 'mudou_vs_decisao_local',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
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
    print(f"fontes_preservadas_por_reserva: {resumo.get('fontes_preservadas_por_reserva', 0)}")
    print(f"primeira_sem_cobertura: {resumo.get('primeira_sem_cobertura_data')} | {resumo.get('primeira_sem_cobertura_pagamento')}")
    print(f"primeira_violacao_protegida: {resumo.get('primeira_violation_protegida_data')} | {resumo.get('primeira_violation_protegida_pagamento')}")
    print(f"primeira_fonte_preservada_por_reserva: {resumo.get('primeira_fonte_preservada_por_reserva_data')} | {resumo.get('primeira_fonte_preservada_por_reserva_pagamento')} | {resumo.get('primeira_fonte_preservada_por_reserva_fonte')}")
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
