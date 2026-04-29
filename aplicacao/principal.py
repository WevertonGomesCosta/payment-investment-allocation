"""Ponto de entrada principal com console + geração de saídas."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from aplicacao.console.principal import main as main_console
from scripts.operacional.gerar_planilha_operacional import main as main_planilha


def main() -> None:
    main_console()
    caminho_saida = main_planilha()
    print(f"Saída operacional gerada em: {caminho_saida}")


if __name__ == "__main__":
    main()
