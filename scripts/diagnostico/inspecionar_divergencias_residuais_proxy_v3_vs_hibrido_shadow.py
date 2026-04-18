from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.caixa_recebidos_auditaveis import auditar_divergencias_residuais_proxy_v3_vs_hibrido_shadow
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_residual_proxy_v3_vs_hibrido_shadow

ARQUIVO_XLSX = nome_auditoria_residual_proxy_v3_vs_hibrido_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_residual_proxy_v3_vs_hibrido_shadow('csv')
COLUNAS_DIVERGENCIAS = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_id_escolhido_local_v3', 'lote_principal_hibrido_shadow', 'transicao_lote_principal',
    'benchmark_multifonte_shadow', 'qtd_lotes_usados_hibrido_shadow',
    'delta_score_proxy_v3_principal_benchmark_vs_local', 'classificacao_score_proxy_v3_principal',
    'delta_excesso_liquido_benchmark_vs_local', 'classificacao_excesso_liquido',
    'classificacao_residual', 'bucket_valor_pagamento', 'bucket_horizonte', 'grau_delta_score_proxy_v3',
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
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    auditoria = auditar_divergencias_residuais_proxy_v3_vs_hibrido_shadow(
        contexto.dados_operacionais,
        contexto.fontes_elegiveis_pagamento,
        contexto.saldo_disponivel_geral,
        contexto.decisao_local_v1,
        contexto.resolver_hibrido_5p_shadow,
        data_referencia=contexto.execucao.data_referencia,
        carteira_canonica=contexto.carteira_canonica,
    )
    resumo = auditoria['auditoria']['resumo']
    divergencias = auditoria['quadro_divergencias_residuais'].copy()
    padroes_transicao = auditoria['quadro_padroes_transicao'].copy()
    padroes_buckets = auditoria['quadro_padroes_buckets'].copy()
    reaproveitaveis = auditoria['quadro_reaproveitaveis'].copy()
    estruturais = auditoria['quadro_estruturais'].copy()

    print('=== AUDITORIA RESIDUAL: DIVERGÊNCIAS MATERIAIS PROXY V3 VS BENCHMARK HÍBRIDO ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'total_pagamentos',
        'total_divergencias_materiais',
        'pct_divergencias_materiais',
        'casos_potencial_reaproveitamento_proxy_v3',
        'casos_divergencia_estrutural_benchmark',
        'casos_multifonte_shadow',
        'classificacao_residual',
        'transicao_lote_principal',
        'conclusao_residual',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- AMOSTRA DAS DIVERGÊNCIAS RESIDUAIS ---')
    amostra = divergencias[COLUNAS_DIVERGENCIAS].head(40)
    print(amostra.to_string(index=False) if len(amostra) else 'sem divergências residuais materiais')

    caminho_xlsx = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    divergencias.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        divergencias.to_excel(writer, sheet_name='Divergencias_Residuais', index=False)
        padroes_transicao.to_excel(writer, sheet_name='Padroes_Transicao', index=False)
        padroes_buckets.to_excel(writer, sheet_name='Padroes_Buckets', index=False)
        reaproveitaveis.to_excel(writer, sheet_name='Casos_Reaproveitaveis', index=False)
        estruturais.to_excel(writer, sheet_name='Casos_Estruturais', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
