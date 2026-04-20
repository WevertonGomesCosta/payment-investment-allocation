from __future__ import annotations

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.caixa_recebidos_auditaveis import auditar_transicao_dominante_proxy_v3_vs_hibrido_shadow
from nucleo.identidade_baseline import (
    caminho_saida_operacional,
    nome_auditoria_fina_transicao_dominante_proxy_v3_vs_hibrido_shadow,
)

ARQUIVO_XLSX = nome_auditoria_fina_transicao_dominante_proxy_v3_vs_hibrido_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_fina_transicao_dominante_proxy_v3_vs_hibrido_shadow('csv')
COLUNAS_CASOS = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_id_escolhido_local_v3', 'lote_principal_hibrido_shadow', 'transicao_lote_principal',
    'delta_score_proxy_v3_principal_benchmark_vs_local', 'delta_excesso_liquido_benchmark_vs_local',
    'bucket_valor_pagamento', 'bucket_horizonte', 'hipotese_fina_local', 'prioridade_fina',
    'ganho_relativo_excesso_pct', 'intensidade_ganho_score',
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
    auditoria = auditar_transicao_dominante_proxy_v3_vs_hibrido_shadow(
        contexto.dados_operacionais,
        contexto.fontes_elegiveis_pagamento,
        contexto.saldo_disponivel_geral,
        contexto.decisao_local_v1,
        contexto.resolver_hibrido_5p_shadow,
        data_referencia=contexto.execucao.data_referencia,
        carteira_canonica=contexto.carteira_canonica,
    )
    resumo = auditoria['auditoria']['resumo']
    casos = auditoria['quadro_transicao_fina'].copy()
    descricoes = auditoria['quadro_resumo_descricoes'].copy()
    buckets = auditoria['quadro_resumo_buckets'].copy()
    temporal = auditoria['quadro_resumo_temporal'].copy()

    print('=== AUDITORIA FINA: TRANSIÇÃO DOMINANTE 3000 B -> 8500 MAR. ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'transicao_auditada',
        'total_casos_transicao',
        'bucket_valor_dominante',
        'bucket_horizonte_dominante',
        'descricao_pagamento_dominante',
        'delta_score_proxy_v3_medio',
        'delta_excesso_liquido_medio',
        'ganho_relativo_excesso_pct_medio',
        'hipotese_fina_dominante',
        'conclusao_fina',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- AMOSTRA DOS CASOS DA TRANSIÇÃO ---')
    amostra = casos[COLUNAS_CASOS].head(42) if len(casos) else casos
    print(amostra.to_string(index=False) if len(amostra) else 'sem casos na transicao dominante')

    caminho_xlsx = caminho_saida_operacional(RAIZ, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    casos.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        casos.to_excel(writer, sheet_name='Transicao_Fina', index=False)
        descricoes.to_excel(writer, sheet_name='Resumo_Descricoes', index=False)
        buckets.to_excel(writer, sheet_name='Resumo_Buckets', index=False)
        temporal.to_excel(writer, sheet_name='Resumo_Temporal', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
