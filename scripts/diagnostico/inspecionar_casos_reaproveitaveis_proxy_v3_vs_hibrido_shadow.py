from __future__ import annotations

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.caixa_recebidos_auditaveis import auditar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_cirurgica_reaproveitaveis_proxy_v3_vs_hibrido_shadow

ARQUIVO_XLSX = nome_auditoria_cirurgica_reaproveitaveis_proxy_v3_vs_hibrido_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_cirurgica_reaproveitaveis_proxy_v3_vs_hibrido_shadow('csv')
COLUNAS_CASOS = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_id_escolhido_local_v3', 'lote_principal_hibrido_shadow', 'transicao_lote_principal',
    'delta_score_proxy_v3_principal_benchmark_vs_local', 'delta_excesso_liquido_benchmark_vs_local',
    'grau_delta_score_proxy_v3', 'bucket_valor_pagamento', 'bucket_horizonte',
    'padrao_cirurgico', 'prioridade_cirurgica', 'potencial_patch_proxy_v3',
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
    auditoria = auditar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow(
        contexto.dados_operacionais,
        contexto.fontes_elegiveis_pagamento,
        contexto.saldo_disponivel_geral,
        contexto.decisao_local_v1,
        contexto.resolver_hibrido_5p_shadow,
        data_referencia=contexto.execucao.data_referencia,
        carteira_canonica=contexto.carteira_canonica,
    )
    resumo = auditoria['auditoria']['resumo']
    casos = auditoria['quadro_casos_cirurgicos'].copy()
    transicoes = auditoria['quadro_resumo_transicoes'].copy()
    buckets = auditoria['quadro_resumo_buckets'].copy()
    dominante = auditoria['quadro_transicao_dominante'].copy()

    print('=== AUDITORIA CIRÚRGICA: 42 CASOS REAPROVEITÁVEIS ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'total_casos_cirurgicos',
        'transicao_dominante',
        'qtd_transicao_dominante',
        'pct_transicao_dominante',
        'bucket_valor_dominante',
        'bucket_horizonte_dominante',
        'prioridade_cirurgica',
        'padrao_cirurgico',
        'conclusao_cirurgica',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- AMOSTRA DOS CASOS CIRÚRGICOS ---')
    amostra = casos[COLUNAS_CASOS].head(42) if len(casos) else casos
    print(amostra.to_string(index=False) if len(amostra) else 'sem casos reaproveitaveis')

    caminho_xlsx = caminho_saida_operacional(RAIZ, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    casos.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        casos.to_excel(writer, sheet_name='Casos_Cirurgicos', index=False)
        transicoes.to_excel(writer, sheet_name='Resumo_Transicoes', index=False)
        buckets.to_excel(writer, sheet_name='Resumo_Buckets', index=False)
        dominante.to_excel(writer, sheet_name='Transicao_Dominante', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
