"""Inspeciona a recomputação sequencial preventiva sobre a decisao_local_v1."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'lote_sugerido_original',
    'fonte_original_ainda_cobre', 'lote_final_sequencial', 'mudou_fonte_sequencial', 'troca_preventiva',
    'troca_por_inviabilidade', 'status_sequencial', 'saldo_antes_sequencial', 'liquido_sequencial',
    'saldo_remanescente_sequencial', 'pagamento_totalmente_coberto_sequencial',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.recomputacao_sequencial_preventiva
    quadro = pacote.quadro_recomputacao_sequencial
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== RECOMPUTAÇÃO SEQUENCIAL PREVENTIVA ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_auditados: {resumo.get('total_pagamentos_auditados', 0)}")
    print(f"pagamentos_cobertos_sequencialmente: {resumo.get('pagamentos_cobertos_sequencialmente', 0)}")
    print(f"pagamentos_sem_cobertura_sequencial: {resumo.get('pagamentos_sem_cobertura_sequencial', 0)}")
    print(f"mudancas_efetivas_de_fonte: {resumo.get('mudancas_efetivas_de_fonte', 0)}")
    print(f"trocas_preventivas: {resumo.get('trocas_preventivas', 0)}")
    print(f"trocas_por_inviabilidade: {resumo.get('trocas_por_inviabilidade', 0)}")
    print(
        f"primeira_troca_preventiva: {resumo.get('primeira_troca_preventiva_data')} | "
        f"{resumo.get('primeira_troca_preventiva_pagamento')} | "
        f"{resumo.get('primeira_troca_preventiva_lote_original')} -> {resumo.get('primeira_troca_preventiva_lote_final')}"
    )
    print(
        f"primeira_troca_inviabilidade: {resumo.get('primeira_troca_inviabilidade_data')} | "
        f"{resumo.get('primeira_troca_inviabilidade_pagamento')} | "
        f"{resumo.get('primeira_troca_inviabilidade_lote_original')} -> {resumo.get('primeira_troca_inviabilidade_lote_final')}"
    )
    print(
        f"primeira_sem_cobertura: {resumo.get('primeira_sem_cobertura_data')} | "
        f"{resumo.get('primeira_sem_cobertura_pagamento')} | {resumo.get('primeira_sem_cobertura_lote_final')}"
    )
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1

    print('\n--- AMOSTRA DE TROCAS PREVENTIVAS ---')
    for item in (auditoria.get('amostra_trocas_preventivas') or [])[:10]:
        print(item)

    print('\n--- QUADRO SEQUENCIAL (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
