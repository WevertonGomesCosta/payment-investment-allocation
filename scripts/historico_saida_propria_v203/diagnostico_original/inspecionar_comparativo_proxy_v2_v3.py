"""Audita comparativamente a decisão local v1 com proxy econômico v2 vs v3."""

from __future__ import annotations

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.caixa_recebidos_auditaveis import auditar_comparativo_proxy_v2_v3

from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_comparativa_proxy_v2_v3

ARQUIVO_XLSX = nome_auditoria_comparativa_proxy_v2_v3('xlsx')
ARQUIVO_CSV = nome_auditoria_comparativa_proxy_v2_v3('csv')
COLUNAS_EXIBICAO = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_id_escolhido_v2', 'lote_id_escolhido_v3', 'criterio_decisao_v2', 'criterio_decisao_v3',
    'custo_economico_proxy_v2', 'custo_economico_proxy_v3', 'delta_score_comum_v3',
    'mudou_fonte', 'mudou_lote', 'mudou_criterio', 'classificacao_delta_score_comum_v3',
]


def _quadro_resumo(resumo: dict[str, object]) -> pd.DataFrame:
    registros = []
    for chave, valor in resumo.items():
        if isinstance(valor, dict):
            for subchave, subvalor in valor.items():
                registros.append({'grupo': chave, 'item': str(subchave), 'valor': subvalor})
        else:
            registros.append({'grupo': 'geral', 'item': chave, 'valor': valor})
    return pd.DataFrame(registros)


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    auditoria = auditar_comparativo_proxy_v2_v3(
        contexto.dados_operacionais,
        contexto.fontes_elegiveis_pagamento,
        contexto.saldo_disponivel_geral,
        data_referencia=contexto.execucao.data_referencia,
        carteira_canonica=contexto.carteira_canonica,
    )
    resumo = auditoria['auditoria']['resumo']
    quadro_comparativo = auditoria['quadro_comparativo'].copy()
    quadro_mudancas = auditoria['quadro_mudancas'].copy()

    print('=== AUDITORIA COMPARATIVA PROXY V2 VS V3 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos: {resumo.get('total_pagamentos')}")
    print(f"pagamentos_com_fonte_alterada: {resumo.get('pagamentos_com_fonte_alterada')}")
    print(f"pagamentos_com_lote_alterado: {resumo.get('pagamentos_com_lote_alterado')}")
    print(f"pagamentos_com_criterio_alterado: {resumo.get('pagamentos_com_criterio_alterado')}")
    print(f"delta_score_comum_v2_total: {resumo.get('delta_score_comum_v2_total')}")
    print(f"delta_score_comum_v2_medio: {resumo.get('delta_score_comum_v2_medio')}")
    print(f"classificacao_delta_score_comum_v2: {resumo.get('classificacao_delta_score_comum_v2', {})}")
    print(f"delta_score_comum_v3_total: {resumo.get('delta_score_comum_v3_total')}")
    print(f"delta_score_comum_v3_medio: {resumo.get('delta_score_comum_v3_medio')}")
    print(f"classificacao_delta_score_comum_v3: {resumo.get('classificacao_delta_score_comum_v3', {})}")
    print(f"lote_id_escolhido_v2: {resumo.get('lote_id_escolhido_v2', {})}")
    print(f"lote_id_escolhido_v3: {resumo.get('lote_id_escolhido_v3', {})}")
    print(f"pagamentos_totalmente_cobertos_v2: {resumo.get('pagamentos_totalmente_cobertos_v2')}")
    print(f"pagamentos_totalmente_cobertos_v3: {resumo.get('pagamentos_totalmente_cobertos_v3')}")
    print('\n--- AMOSTRA DAS MUDANÇAS MATERIAIS ---')
    quadro_mudancas_materiais = quadro_comparativo.loc[quadro_comparativo['mudou_fonte'] | quadro_comparativo['mudou_lote']].copy()
    amostra = quadro_mudancas_materiais[COLUNAS_EXIBICAO].head(40) if len(quadro_mudancas_materiais) else quadro_comparativo[COLUNAS_EXIBICAO].head(20)
    if len(quadro_mudancas_materiais):
        print(amostra.to_string(index=False))
    else:
        print('não houve mudança material de fonte/lote; as diferenças ficaram apenas no critério auditável.')


    caminho_xlsx = caminho_saida_operacional(RAIZ, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    quadro_comparativo.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        quadro_comparativo.to_excel(writer, sheet_name='Comparativo', index=False)
        quadro_mudancas.to_excel(writer, sheet_name='Mudancas', index=False)
        auditoria['pacote_v2'].quadro_decisao_local_v1.to_excel(writer, sheet_name='Decisao_v2', index=False)
        auditoria['pacote_v3'].quadro_decisao_local_v1.to_excel(writer, sheet_name='Decisao_v3', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
