#!/usr/bin/env python3
"""V17-E1-B — Auditoria de duplicidades de código no núcleo.

Gera artefatos CSV em `saidas/diagnostico/v17_e1_b/` com foco em:
- blocos textuais repetidos entre arquivos de `nucleo/`;
- funções potencialmente redundantes (assinatura lexical aproximada);
- imports comuns (sinal fraco de convergência técnica);
- matriz de priorização para microetapas de consolidação.

Heurístico e não-bloqueante: prioriza falso-positivo controlado para guiar refatoração.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
NUCLEO_DIR = ROOT / "nucleo"
OUT_DIR = ROOT / "saidas" / "diagnostico" / "v17_e1_b"

MIN_BLOCK_LINES = 6
MIN_BLOCK_CHARS = 180
MAX_SNIPPET_CHARS = 220


@dataclass
class FunctionLex:
    arquivo: str
    nome: str
    linha_inicio: int
    linha_fim: int
    assinatura: str
    hash_lexico: str


def norm_path_key(value: str) -> str:
    return str(value or "").replace("\\", "/")


def normalize_code(text: str) -> str:
    text = re.sub(r"#.*", "", text)
    text = re.sub(r"\"\"\"[\s\S]*?\"\"\"", "", text)
    text = re.sub(r"'''[\s\S]*?'''", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def chunk_blocks(lines: list[str], size: int = MIN_BLOCK_LINES) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    if len(lines) < size:
        return blocks
    for i in range(0, len(lines) - size + 1):
        raw = "\n".join(lines[i : i + size]).strip()
        if len(raw) < MIN_BLOCK_CHARS:
            continue
        norm = normalize_code(raw)
        if norm:
            blocks.append((i + 1, norm))
    return blocks


def read_py_files(base: Path) -> list[Path]:
    files = [p for p in base.rglob("*.py") if p.is_file()]
    return sorted(files)


def lexical_signature(node: ast.AST, source: str) -> str:
    seg = (ast.get_source_segment(source, node) or "").strip()
    seg = re.sub(r"\bself\b", "obj", seg)
    seg = re.sub(r"\bcls\b", "obj", seg)
    seg = re.sub(r"\b\d+(\.\d+)?\b", "N", seg)
    seg = re.sub(r"'[^']*'|\"[^\"]*\"", "S", seg)
    seg = re.sub(r"\s+", " ", seg)
    return seg.lower()


def extract_functions(path: Path) -> list[FunctionLex]:
    txt = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(txt)
    except SyntaxError:
        return []

    out: list[FunctionLex] = []
    rel = norm_path_key(path.relative_to(ROOT).as_posix())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = lexical_signature(node, txt)
            if len(sig) < MIN_BLOCK_CHARS:
                continue
            h = hashlib.sha1(sig.encode("utf-8")).hexdigest()[:16]
            out.append(
                FunctionLex(
                    arquivo=rel,
                    nome=node.name,
                    linha_inicio=getattr(node, "lineno", 0),
                    linha_fim=getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                    assinatura=sig[:MAX_SNIPPET_CHARS],
                    hash_lexico=h,
                )
            )
    return out


def extract_imports(path: Path) -> set[str]:
    txt = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(txt)
    except SyntaxError:
        return set()

    imps: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imps.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imps.add(node.module)
    return imps


def write_csv(name: str, rows: list[dict], headers: Iterable[str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(headers))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    if not NUCLEO_DIR.exists():
        raise RuntimeError(f"Diretório ausente: {NUCLEO_DIR}")

    files = read_py_files(NUCLEO_DIR)

    block_index: dict[str, list[tuple[str, int]]] = defaultdict(list)
    imports_map: dict[str, set[str]] = {}
    all_functions: list[FunctionLex] = []

    for p in files:
        rel = norm_path_key(p.relative_to(ROOT).as_posix())
        txt = p.read_text(encoding="utf-8")
        lines = txt.splitlines()

        for line_start, block in chunk_blocks(lines):
            h = hashlib.sha1(block.encode("utf-8")).hexdigest()[:16]
            block_index[h].append((rel, line_start))

        imports_map[rel] = extract_imports(p)
        all_functions.extend(extract_functions(p))

    duplicidades_blocos: list[dict] = []
    for h, ocorrencias in sorted(block_index.items()):
        arquivos = sorted({a for a, _ in ocorrencias})
        if len(arquivos) < 2:
            continue
        duplicidades_blocos.append(
            {
                "hash_bloco": h,
                "qtd_ocorrencias": len(ocorrencias),
                "qtd_arquivos": len(arquivos),
                "arquivos": ";".join(arquivos),
                "linhas_inicio": ";".join(f"{a}:{ln}" for a, ln in ocorrencias[:20]),
                "risco": "alto" if len(arquivos) >= 4 else "medio",
                "acao_recomendada": "extrair_util_compartilhado" if len(arquivos) >= 3 else "avaliar_merge_local",
            }
        )

    funcoes_por_hash: dict[str, list[FunctionLex]] = defaultdict(list)
    for fn in all_functions:
        funcoes_por_hash[fn.hash_lexico].append(fn)

    duplicidades_funcoes: list[dict] = []
    for h, group in sorted(funcoes_por_hash.items()):
        arquivos = sorted({g.arquivo for g in group})
        if len(arquivos) < 2:
            continue
        nomes = sorted({g.nome for g in group})
        duplicidades_funcoes.append(
            {
                "hash_lexico": h,
                "qtd_funcoes": len(group),
                "qtd_arquivos": len(arquivos),
                "arquivos": ";".join(arquivos),
                "funcoes": ";".join(nomes),
                "linhas": ";".join(f"{g.arquivo}:{g.linha_inicio}-{g.linha_fim}" for g in group[:20]),
                "snippet_assinatura": group[0].assinatura,
                "risco": "alto" if len(arquivos) >= 3 else "medio",
                "acao_recomendada": "unificar_api_interna" if len(arquivos) >= 2 else "manter",
            }
        )

    sobreposicao_imports: list[dict] = []
    rels = sorted(imports_map)
    for i in range(len(rels)):
        for j in range(i + 1, len(rels)):
            a, b = rels[i], rels[j]
            ia, ib = imports_map[a], imports_map[b]
            if not ia or not ib:
                continue
            inter = sorted(ia & ib)
            if len(inter) < 8:
                continue
            un = ia | ib
            jaccard = len(inter) / max(len(un), 1)
            sobreposicao_imports.append(
                {
                    "arquivo_a": a,
                    "arquivo_b": b,
                    "imports_comuns_qtd": len(inter),
                    "imports_comuns": ";".join(inter[:30]),
                    "indice_jaccard": f"{jaccard:.4f}",
                    "risco": "medio" if jaccard >= 0.35 else "baixo",
                    "observacao": "Sinal fraco de possível oportunidade de consolidação.",
                }
            )

    riscos: list[dict] = []
    for row in duplicidades_funcoes[:40]:
        riscos.append(
            {
                "prioridade": "P0" if row["risco"] == "alto" else "P1",
                "tipo": "duplicidade_funcao_nucleo",
                "referencia": row["hash_lexico"],
                "arquivos": row["arquivos"],
                "impacto": "Aumento de custo de manutenção e risco de regressão por correções divergentes.",
                "acao": row["acao_recomendada"],
            }
        )
    for row in duplicidades_blocos[:40]:
        riscos.append(
            {
                "prioridade": "P1" if row["risco"] == "alto" else "P2",
                "tipo": "duplicidade_bloco_nucleo",
                "referencia": row["hash_bloco"],
                "arquivos": row["arquivos"],
                "impacto": "Trechos repetidos dificultam evolução consistente.",
                "acao": row["acao_recomendada"],
            }
        )

    resumo = [
        {"metrica": "arquivos_nucleo_auditados", "valor": len(files)},
        {"metrica": "grupos_duplicidade_blocos", "valor": len(duplicidades_blocos)},
        {"metrica": "grupos_duplicidade_funcoes", "valor": len(duplicidades_funcoes)},
        {"metrica": "pares_sobreposicao_imports", "valor": len(sobreposicao_imports)},
        {"metrica": "riscos_p0", "valor": sum(1 for r in riscos if r["prioridade"] == "P0")},
        {"metrica": "riscos_p1", "valor": sum(1 for r in riscos if r["prioridade"] == "P1")},
        {"metrica": "riscos_p2", "valor": sum(1 for r in riscos if r["prioridade"] == "P2")},
        {
            "metrica": "recomendacao_proxima_microetapa",
            "valor": "V17-E1-B: consolidar duplicidades P0/P1 via utilitários internos do núcleo",
        },
    ]

    write_csv(
        "v17_e1_b_duplicidades_blocos.csv",
        duplicidades_blocos,
        [
            "hash_bloco",
            "qtd_ocorrencias",
            "qtd_arquivos",
            "arquivos",
            "linhas_inicio",
            "risco",
            "acao_recomendada",
        ],
    )
    write_csv(
        "v17_e1_b_duplicidades_funcoes.csv",
        duplicidades_funcoes,
        [
            "hash_lexico",
            "qtd_funcoes",
            "qtd_arquivos",
            "arquivos",
            "funcoes",
            "linhas",
            "snippet_assinatura",
            "risco",
            "acao_recomendada",
        ],
    )
    write_csv(
        "v17_e1_b_sobreposicao_imports.csv",
        sobreposicao_imports,
        [
            "arquivo_a",
            "arquivo_b",
            "imports_comuns_qtd",
            "imports_comuns",
            "indice_jaccard",
            "risco",
            "observacao",
        ],
    )
    write_csv(
        "v17_e1_b_riscos_priorizados.csv",
        riscos,
        ["prioridade", "tipo", "referencia", "arquivos", "impacto", "acao"],
    )
    write_csv("v17_e1_b_resumo.csv", resumo, ["metrica", "valor"])


if __name__ == "__main__":
    main()
