#!/usr/bin/env python3
"""Validação funcional mínima da rota principal (Codex-ready V227)."""

from __future__ import annotations

import json
import py_compile
from dataclasses import dataclass
from importlib.util import spec_from_file_location
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CheckResult:
    nome: str
    ok: bool
    detalhe: str


def _check_exists(path_rel: str) -> CheckResult:
    path = ROOT / path_rel
    ok = path.exists()
    detalhe = f"{path_rel} {'encontrado' if ok else 'nao_encontrado'}"
    return CheckResult(nome=f"existencia:{path_rel}", ok=ok, detalhe=detalhe)


def _check_config_json() -> CheckResult:
    path_rel = "dados/config_atualizado.json"
    path = ROOT / path_rel
    if not path.exists():
        return CheckResult(nome="config_json_legivel", ok=False, detalhe=f"{path_rel} nao_encontrado")
    try:
        conteudo = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return CheckResult(nome="config_json_legivel", ok=False, detalhe=f"falha_leitura_json: {exc}")

    tipo = type(conteudo).__name__
    return CheckResult(nome="config_json_legivel", ok=True, detalhe=f"json_ok_tipo:{tipo}")


def _check_main_compilavel() -> CheckResult:
    path_rel = "aplicacao/principal.py"
    path = ROOT / path_rel
    if not path.exists():
        return CheckResult(nome="principal_compilavel", ok=False, detalhe=f"{path_rel} nao_encontrado")

    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        return CheckResult(nome="principal_compilavel", ok=False, detalhe=f"falha_compilacao: {exc}")

    return CheckResult(nome="principal_compilavel", ok=True, detalhe="compilacao_ok")


def _check_main_importavel() -> CheckResult:
    path = ROOT / "aplicacao/principal.py"
    spec = spec_from_file_location("aplicacao.principal", path)
    ok = spec is not None and spec.loader is not None
    detalhe = "spec_loader_ok" if ok else "spec_loader_indisponivel"
    return CheckResult(nome="principal_importavel", ok=ok, detalhe=detalhe)


def main() -> int:
    checks: list[Callable[[], CheckResult]] = [
        lambda: _check_exists("aplicacao/principal.py"),
        lambda: _check_exists("requirements.txt"),
        lambda: _check_exists("dados/config_atualizado.json"),
        lambda: _check_exists("dados/dados_financeiros.xlsx"),
        _check_config_json,
        _check_main_compilavel,
        _check_main_importavel,
    ]

    resultados = [fn() for fn in checks]

    for r in resultados:
        status = "OK" if r.ok else "ERRO"
        print(f"[{status}] {r.nome} :: {r.detalhe}")

    total_ok = sum(1 for r in resultados if r.ok)
    total = len(resultados)
    print(f"RESUMO: {total_ok}/{total} verificacoes OK")

    return 0 if total_ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
