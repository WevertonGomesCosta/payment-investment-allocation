from __future__ import annotations

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.caixa_recebidos_auditaveis import auditar_comparativo_proxy_v3_vs_hibrido_shadow
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_comparativa_proxy_v3_vs_hibrido_shadow

ARQUIVO_XLSX = nome_auditoria_comparativa_proxy_v3_vs_hibrido_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_comparativa_proxy_v3_vs_hibrido_shadow('csv')
COLUNAS_EXIBICAO = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_id_escolhido_local_v3', 'lote_principal_hibrido_shadow', 'mudou_lote_principal',
    'benchmark_multifonte_shadow', 'qtd_lotes_usados_hibrido_shadow',
    'score_proxy_v3_local_comum', 'score_proxy_v3_lote_principal_benchmark',
    'delta_score_proxy_v3_principal_benchmark_vs_local', 'classificacao_score_proxy_v3_principal',
    'excesso_liquido_local_v3', 'excesso_liquido_benchmark_shadow', 'delta_excesso_liquido_benchmark_vs_local',
    'classificacao_excesso_liquido', 'divergencia_material',
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
    auditoria = auditar_comparativo_proxy_v3_vs_hibrido_shadow(
        contexto.dados_operacionais,
        contexto.fontes_elegiveis_pagamento,
        contexto.saldo_disponivel_geral,
        contexto.decisao_local_v1,
        contexto.resolver_hibrido_5p_shadow,
        data_referencia=contexto.execucao.data_referencia,
        carteira_canonica=contexto.carteira_canonica,
    )
    resumo = auditoria['auditoria']['resumo']
    quadro = auditoria['quadro_comparativo'].copy()
    divergencias = auditoria['quadro_divergencias'].copy()

    print('=== AUDITORIA COMPARATIVA: PROXY V3 VS BENCHMARK SHADOW resolver_hibrido_5p ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'total_pagamentos',
        'pagamentos_totalmente_cobertos_local_v3',
        'pagamentos_totalmente_cobertos_benchmark_shadow',
        'pagamentos_com_lote_principal_alterado',
        'pagamentos_multifonte_shadow',
        'pagamentos_com_divergencia_material',
        'delta_score_proxy_v3_principal_total',
        'delta_score_proxy_v3_principal_medio',
        'classificacao_score_proxy_v3_principal',
        'delta_excesso_liquido_total',
        'delta_excesso_liquido_medio',
        'classificacao_excesso_liquido',
        'lote_id_escolhido_local_v3',
        'lote_principal_hibrido_shadow',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- AMOSTRA DAS DIVERGÊNCIAS MATERIAIS ---')
    amostra = divergencias[COLUNAS_EXIBICAO].head(40) if len(divergencias) else quadro[COLUNAS_EXIBICAO].head(20)
    print(amostra.to_string(index=False) if len(amostra) else 'sem divergências materiais')

    caminho_xlsx = caminho_saida_operacional(RAIZ, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    quadro.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        quadro.to_excel(writer, sheet_name='Comparativo', index=False)
        divergencias.to_excel(writer, sheet_name='Divergencias', index=False)
        auditoria['pacote_local_v3'].quadro_decisao_local_v1.to_excel(writer, sheet_name='Decisao_Local_V3', index=False)
        auditoria['pacote_benchmark_shadow'].quadro_pagamentos_benchmark.to_excel(writer, sheet_name='Benchmark_Shadow', index=False)
        auditoria['pacote_benchmark_shadow'].quadro_alocacoes_shadow.to_excel(writer, sheet_name='Alocacoes_Shadow', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
