"""Governança de scripts diagnósticos e legados — V203.

Este módulo não altera o motor econômico. Ele centraliza avisos/bloqueios de
execução para scripts que produziam saídas próprias antes da camada canônica.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Any

MARCADOR_GOVERNANCA_V203 = "BLOQUEADO_POR_GOVERNANCA_V203"


def bloquear_script_legado(caminho: str | Path, *, motivo: str, alternativa: str | None = None) -> int:
    """Bloqueia execução de script legado com saída própria.

    Retorna código 2 para sinalizar bloqueio intencional de governança, não erro do motor.
    """
    nome = Path(caminho).as_posix()
    print("=== SCRIPT LEGADO BLOQUEADO PELA GOVERNANCA V203 ===")
    print(f"marcador: {MARCADOR_GOVERNANCA_V203}")
    print(f"script: {nome}")
    print(f"motivo: {motivo}")
    if alternativa:
        print(f"alternativa canônica: {alternativa}")
    print("autoridade operacional: nenhuma")
    print("use a camada nucleo.saida_canonica ou scripts/operacional/gerar_planilha_operacional.py")
    return 2


def imprimir_tabela_dicts(titulo: str, linhas: Iterable[Mapping[str, Any]], colunas: list[str], limite: int = 15) -> None:
    """Imprime tabela simples para wrappers diagnósticos canônicos."""
    linhas_lista = list(linhas)[:limite]
    print(f"\n=== {titulo} ===")
    if not linhas_lista:
        print("(sem linhas)")
        return
    larguras = {col: max(len(col), *(len(str(item.get(col, ""))) for item in linhas_lista)) for col in colunas}
    print(" | ".join(col.ljust(larguras[col]) for col in colunas))
    print("-+-".join("-" * larguras[col] for col in colunas))
    for item in linhas_lista:
        print(" | ".join(str(item.get(col, "")).ljust(larguras[col]) for col in colunas))
