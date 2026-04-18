
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_benchmark_agrupado_individual_shadow

ARQUIVO_XLSX = nome_auditoria_benchmark_agrupado_individual_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_benchmark_agrupado_individual_shadow('csv')
COLUNAS = [
    'data_pagamento', 'qtd_pagamentos_individual', 'valor_total_dia',
    'lote_dominante_individual', 'lote_agrupado', 'mudou_lote_vs_dominante_individual',
    'score_proxy_ponderado_individual', 'score_proxy_agrupado', 'delta_score_proxy_agrupado_vs_individual_ponderado',
    'excesso_liquido_total_individual', 'excesso_liquido_agrupado', 'delta_excesso_liquido_agrupado_vs_individual',
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
    pacote = contexto.benchmark_agrupado_individual_shadow
    resumo = pacote.auditoria['resumo']
    quadro = pacote.quadro_comparativo_datas.copy()

    print('=== BENCHMARK SHADOW: AGRUPADO VS INDIVIDUAL (SCRIPT 2) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'proxy_version',
        'total_pagamentos_individuais',
        'total_datas_agrupadas',
        'datas_com_mudanca_de_lote_dominante',
        'modo_recomendado_shadow',
        'justificativa_modo_recomendado',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- RESUMO INDIVIDUAL ---')
    print(resumo.get('resumo_individual'))
    print('\n--- RESUMO AGRUPADO ---')
    print(resumo.get('resumo_agrupado'))
    print('\n--- AMOSTRA POR DATA ---')
    print(quadro[COLUNAS].head(40).to_string(index=False) if len(quadro) else 'sem dados')

    caminho_xlsx = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    quadro.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        quadro.to_excel(writer, sheet_name='Comparativo_Datas', index=False)
        pacote.quadro_pagamentos_individual.to_excel(writer, sheet_name='Decisao_Individual', index=False)
        pacote.quadro_pagamentos_agrupados.to_excel(writer, sheet_name='Decisao_Agrupado', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
