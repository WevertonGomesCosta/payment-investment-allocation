from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ALVOS_DUPLICIDADE = {
    "valor_original": ["orig", "valor_original", "valor original"],
    "produto_carteira": ["produto", "carteira"],
    "aplicacao_base_fiscal": ["aplic", "aplicação", "base fiscal"],
    "saldo_sacado_remanescente": ["saldo", "sac", "remanesc"],
}


def _contains_any(text: str, tokens: list[str]) -> bool:
    t = text.lower()
    return any(tok in t for tok in tokens)


def _func_source(src_lines: list[str], node: ast.AST) -> str:
    ini = getattr(node, "lineno", 1) - 1
    fim = getattr(node, "end_lineno", getattr(node, "lineno", 1))
    return "\n".join(src_lines[ini:fim]).lower()


def inventariar_saida_observavel(path: Path) -> dict[str, Any]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()

    funcoes_contexto_replay: list[str] = []
    funcoes_getattr_amplo: list[str] = []
    funcoes_iter_dict: list[str] = []
    funcoes_iter_df_generico: list[str] = []
    funcoes_reconstroem_observavel_com_replay: list[str] = []
    duplicidades: dict[str, list[str]] = {k: [] for k in ALVOS_DUPLICIDADE}

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        nome = node.name
        corpo = _func_source(lines, node)

        if _contains_any(corpo, ["contexto", "replay"]):
            funcoes_contexto_replay.append(nome)

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id == "getattr":
                if len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant) and isinstance(sub.args[1].value, str):
                    arg = sub.args[1].value.lower()
                    if arg in {"__dict__", "dict", "items"} or any(x in arg for x in ["contexto", "replay", "log", "extrato"]):
                        funcoes_getattr_amplo.append(nome)
                else:
                    funcoes_getattr_amplo.append(nome)

            if isinstance(sub, ast.Attribute) and sub.attr == "__dict__":
                funcoes_iter_dict.append(nome)

            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr in {"iterrows", "itertuples", "to_dict"}:
                    funcoes_iter_df_generico.append(nome)

        if _contains_any(corpo, ["replay", "corrig", "reconst", "observ"]):
            funcoes_reconstroem_observavel_com_replay.append(nome)

        for chave, tokens in ALVOS_DUPLICIDADE.items():
            if all(tok in corpo for tok in tokens):
                duplicidades[chave].append(nome)

    uniq = lambda xs: sorted(set(xs))
    return {
        "arquivo_alvo": str(path.relative_to(ROOT)),
        "funcoes_contexto_replay": uniq(funcoes_contexto_replay),
        "funcoes_getattr_amplo": uniq(funcoes_getattr_amplo),
        "funcoes_iter_dict": uniq(funcoes_iter_dict),
        "funcoes_iter_df_generico": uniq(funcoes_iter_df_generico),
        "funcoes_reconstroem_observavel_com_replay": uniq(funcoes_reconstroem_observavel_com_replay),
        "duplicidades_potenciais": {k: uniq(v) for k, v in duplicidades.items()},
    }


def inventariar_shadows_e_v4() -> dict[str, Any]:
    py_files = sorted((ROOT / "nucleo").glob("*.py"))
    shadow_paths = [str(p.relative_to(ROOT)) for p in py_files if "shadow" in p.stem.lower()]

    diag_v4 = sorted((ROOT / "scripts" / "diagnostico").glob("*v4*.py"))
    classificacao = {
        "auditoria": [],
        "equivalencia_runtime": [],
        "normalizacao": [],
        "outros": [],
    }
    for p in diag_v4:
        n = p.stem.lower()
        rel = str(p.relative_to(ROOT))
        if "auditar" in n:
            classificacao["auditoria"].append(rel)
        elif "equivalencia" in n or "runtime" in n:
            classificacao["equivalencia_runtime"].append(rel)
        elif "normalizacao" in n:
            classificacao["normalizacao"].append(rel)
        else:
            classificacao["outros"].append(rel)

    return {
        "caminhos_shadow_ainda_necessarios": shadow_paths,
        "diagnosticos_v4_classificacao": classificacao,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true", help="Mantido para compatibilidade operacional")
    _ = parser.parse_args()

    alvo = ROOT / "nucleo" / "saida_observavel.py"
    if not alvo.exists():
        print("inventario_emitido=False")
        print("erro=arquivo_alvo_inexistente")
        return 1

    inventario = {}
    inventario.update(inventariar_saida_observavel(alvo))
    inventario.update(inventariar_shadows_e_v4())
    inventario["inventario_emitido"] = True

    for k, v in inventario.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False, sort_keys=True)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
