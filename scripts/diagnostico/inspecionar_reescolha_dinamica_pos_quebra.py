"""Inspeciona a reescolha dinâmica pós-quebra sobre a auditoria temporal da decisão local."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'lote_sugerido_original',
    'reescolha_acionada', 'mudou_fonte', 'lote_final_dinamico', 'status_pos_reescolha',
    'saldo_antes_dinamico', 'liquido_dinamico', 'saldo_remanescente_dinamico', 'pagamento_totalmente_coberto_dinamico',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.reescolha_dinamica_pos_quebra
    quadro = pacote.quadro_reescolha_dinamica
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== REESCOLHA DINÂMICA PÓS-QUEBRA ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_auditados: {resumo.get('total_pagamentos_auditados', 0)}")
    print(f"pagamentos_mantidos_sem_reescolha: {resumo.get('pagamentos_mantidos_sem_reescolha', 0)}")
    print(f"pagamentos_com_reescolha_acionada: {resumo.get('pagamentos_com_reescolha_acionada', 0)}")
    print(f"mudancas_efetivas_de_fonte: {resumo.get('mudancas_efetivas_de_fonte', 0)}")
    print(f"pagamentos_cobertos_pos_reescolha: {resumo.get('pagamentos_cobertos_pos_reescolha', 0)}")
    print(f"pagamentos_sem_cobertura_pos_reescolha: {resumo.get('pagamentos_sem_cobertura_pos_reescolha', 0)}")
    print(f"primeira_reescolha: {resumo.get('primeira_reescolha_data')} | {resumo.get('primeira_reescolha_pagamento')} | {resumo.get('primeira_reescolha_lote_original')} -> {resumo.get('primeira_reescolha_lote_final')}")
    print(f"primeira_sem_cobertura_pos_reescolha: {resumo.get('primeira_sem_cobertura_data')} | {resumo.get('primeira_sem_cobertura_pagamento')} | {resumo.get('primeira_sem_cobertura_lote_final')}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1

    print('\n--- AMOSTRA DE REESCOLHAS ---')
    for item in (auditoria.get('amostra_reescolhas') or [])[:10]:
        print(item)

    print('\n--- QUADRO DINÂMICO (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
