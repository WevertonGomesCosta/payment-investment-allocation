from __future__ import annotations

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_benchmark_runner_futuro_shadow

ARQUIVO_XLSX = nome_auditoria_benchmark_runner_futuro_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_benchmark_runner_futuro_shadow('csv')
COLUNAS = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_vigente', 'lote_principal_shadow', 'mudou_lote_principal', 'qtd_lotes_usados_shadow',
    'pagamento_totalmente_coberto_vigente', 'pagamento_totalmente_coberto_shadow',
    'delta_excesso_shadow_vs_vigente', 'delta_cobertura_shadow_vs_vigente',
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
    pacote = contexto.benchmark_runner_futuro_shadow
    resumo = pacote.auditoria['resumo']
    quadro = pacote.quadro_comparativo_vigente.copy()

    print('=== BENCHMARK SHADOW: RUNNER DE SIMULAÇÃO FUTURA (SCRIPT 2) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'total_pagamentos',
        'pagamentos_totalmente_cobertos_shadow',
        'pagamentos_totalmente_cobertos_vigente',
        'pagamentos_multifonte_shadow',
        'pagamentos_com_mudanca_lote_principal',
        'recomendacao_shadow',
        'justificativa_recomendacao',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- RESUMO SHADOW ---')
    print(resumo.get('resumo_shadow'))
    print('\n--- AMOSTRA COMPARATIVA ---')
    print(quadro[COLUNAS].head(40).to_string(index=False) if len(quadro) else 'sem dados')

    caminho_xlsx = caminho_saida_operacional(RAIZ, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    quadro.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        quadro.to_excel(writer, sheet_name='Comparativo_Vigente', index=False)
        pacote.quadro_pagamentos_shadow.to_excel(writer, sheet_name='Pagamentos_Shadow', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
