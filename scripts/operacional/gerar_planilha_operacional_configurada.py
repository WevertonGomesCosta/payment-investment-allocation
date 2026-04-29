"""Compatibilidade temporária para o antigo wrapper configurável.

A lógica configurável de nomes de arquivo e abas foi incorporada em
`scripts.operacional.gerar_planilha_operacional`. Este módulo permanece apenas
para chamadas antigas e delega diretamente ao gerador base.
"""
from __future__ import annotations

from pathlib import Path

from scripts.operacional.gerar_planilha_operacional import main as gerar_planilha_operacional


def main() -> Path:
    return gerar_planilha_operacional()


if __name__ == '__main__':
    print(main())
