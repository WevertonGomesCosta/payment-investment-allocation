"""Compatibilidade temporária para o antigo wrapper configurável.

A lógica configurável de nomes de arquivo e abas foi incorporada em
`scripts.operacional.gerar_planilha_operacional`. Este módulo permanece apenas
para chamadas antigas e delega diretamente ao gerador base.
"""
from __future__ import annotations

from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from scripts.operacional.gerar_planilha_operacional import main as gerar_planilha_operacional


def main() -> Path:
    return gerar_planilha_operacional()


if __name__ == '__main__':
    print(main())
