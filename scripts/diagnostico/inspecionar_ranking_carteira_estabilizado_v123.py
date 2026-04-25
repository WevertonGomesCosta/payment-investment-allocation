from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.saida_canonica import construir_saida_canonica


def main() -> dict[str, object]:
    """Wrapper diagnóstico read-only.

    V204: este script não cria XLSX/CSV/JSON próprios. A leitura do ranking
    operacional passa pela camada canônica para evitar divergência entre console,
    planilha oficial e diagnósticos.
    """
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)
    linhas = list(getattr(saida, 'ranking_amostra', []) or [])

    print('ranking carteira estabilizado - leitura canonica V204')
    print('origem: nucleo.saida_canonica.construir_saida_canonica')
    print(f'linhas_amostra={len(linhas)}')
    if linhas:
        df = pd.DataFrame(linhas)
        colunas = [c for c in ['Rank', 'Nome', 'Bucket', 'Score Final', 'Score Final Prazo'] if c in df.columns]
        if not colunas:
            colunas = list(df.columns)[:8]
        print(df[colunas].head(10).to_string(index=False))
    return {'origem': 'saida_canonica_v204', 'linhas_amostra': len(linhas)}


if __name__ == '__main__':
    main()
