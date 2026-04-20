"""Inspeciona a auditoria temporal da decisão local v1."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'lote_id_escolhido', 'sequencia_na_fonte',
    'status_local', 'status_temporal', 'saldo_antes_local', 'saldo_antes_temporal', 'saldo_remanescente_temporal',
    'primeira_quebra_na_fonte', 'requer_reescolha_dinamica',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.auditoria_temporal_decisao_local
    quadro = pacote.quadro_auditoria_temporal
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== AUDITORIA TEMPORAL DA DECISÃO LOCAL V1 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_auditados: {resumo.get('total_pagamentos_auditados', 0)}")
    print(f"integrais_na_decisao_local: {resumo.get('pagamentos_integral_local', 0)}")
    print(f"integrais_na_sequencia: {resumo.get('pagamentos_integral_temporal', 0)}")
    print(f"quebras_temporais: {resumo.get('pagamentos_com_quebra_temporal', 0)}")
    print(f"pagamentos_apos_quebra_fonte: {resumo.get('pagamentos_apos_quebra_fonte', 0)}")
    print(f"fontes_com_quebra_temporal: {resumo.get('fontes_com_quebra_temporal', 0)}")
    print(f"primeira_quebra_global: {resumo.get('primeira_quebra_global_data')} | {resumo.get('primeira_quebra_global_pagamento')} | {resumo.get('primeira_quebra_global_lote')}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1
    print('\n--- AMOSTRA DAS PRIMEIRAS QUEBRAS ---')
    amostra = auditoria.get('amostra_primeiras_quebras', [])
    if amostra:
        for item in amostra[:10]:
            print(item)
    print('\n--- QUADRO TEMPORAL (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
