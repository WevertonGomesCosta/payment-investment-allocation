from __future__ import annotations

import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ALVOS = [ROOT / "scripts" / "diagnostico", ROOT / "nucleo", ROOT / "aplicacao"]
TERMOS_LEGADOS = ["shadow", "legado", "fallback", "replay_passado", "log_passado", "alias_shadow", "validacao_legada", "caminho legado"]
SENTINELAS = ["3120", "8500"]
GATES = {"validacao_v4w_ok", "etapa4_saneada", "etapa4_fechamento_saneado_ok", "etapa5_pode_abrir"}


def inferir_etapa(path: Path, texto: str) -> str:
    s = f"{path.as_posix()}\n{texto}".lower()
    if "etapa1" in s or "v32a" in s or "v36" in s:
        return "ETAPA1"
    if "etapa2" in s or "v35" in s or "entrada_resolvida" in s:
        return "ETAPA2"
    if "etapa3" in s or "v37" in s or "ledger" in s:
        return "ETAPA3"
    if "etapa4" in s or any(x in s for x in ["v4u", "v4v", "v4w", "v4x", "v4y"]):
        return "ETAPA4"
    return "INDETERMINADO"


def inferir_tipo(path: Path) -> str:
    n = path.name.lower()
    if n.startswith("auditar_"):
        return "auditor"
    if "pacote" in n:
        return "pacote"
    if "principal" in n:
        return "runtime"
    if "log" in n or n.endswith(".md"):
        return "log"
    if any(x in n for x in ["legacy", "legado", "historico"]):
        return "histórico"
    return "auxiliar"


def _target_name(t: ast.AST) -> str | None:
    if isinstance(t, ast.Name):
        return t.id
    if isinstance(t, ast.Subscript):
        sl = t.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            return sl.value
    return None


def analisar(path: Path) -> dict[str, Any]:
    texto = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(texto)
    funs, classes, args_map, calls, imports_i, reads, writes = [], [], {}, set(), set(), set(), set()
    has_main = False
    gate_hardcoded = False
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            funs.append(n.name)
            args_map[n.name] = [a.arg for a in n.args.args]
        if isinstance(n, ast.ClassDef):
            classes.append(n.name)
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                calls.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                calls.add(n.func.attr)
        if isinstance(n, ast.ImportFrom) and n.module:
            if n.module.startswith(("nucleo", "aplicacao", "scripts")):
                imports_i.add(n.module)
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.startswith(("nucleo", "aplicacao", "scripts")):
                    imports_i.add(a.name)
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            v = n.value
            if any(x in v for x in [".csv", ".xlsx", ".json", ".md", ".py"]):
                if any(y in v.lower() for y in ["saida", "output", "write", "gera", "export"]):
                    writes.add(v)
                else:
                    reads.add(v)
        if isinstance(n, ast.If):
            if "__name__" in ast.dump(n.test):
                has_main = True
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            value = n.value
            if value is not None:
                for t in targets:
                    nm = _target_name(t)
                    if nm in GATES:
                        dump = ast.dump(value, include_attributes=False)
                        if any(s in dump for s in SENTINELAS + ["lote_3120", "lote_8500"]):
                            gate_hardcoded = True

    legados = [t for t in TERMOS_LEGADOS if t in texto.lower()]
    sent = [s for s in SENTINELAS if s in texto]
    etapa = inferir_etapa(path, texto)
    tipo = inferir_tipo(path)
    return {
        "caminho": str(path.relative_to(ROOT)),
        "etapa": etapa,
        "tipo": tipo,
        "funcoes": funs,
        "classes": classes,
        "args_funcoes": args_map,
        "chamadas_internas": sorted(calls),
        "imports_internos": sorted(imports_i),
        "arquivos_lidos": sorted(reads),
        "arquivos_escritos": sorted(writes),
        "possui_main_cli": has_main,
        "consome_etapa_anterior": "indeterminado",
        "expoe_para_posterior": "indeterminado",
        "termos_legados": legados,
        "sentinelas": sent,
        "flags_hardcoded_gate": gate_hardcoded,
    }


def classificar(reg: dict[str, Any], consumidos: set[str]) -> str:
    if reg["flags_hardcoded_gate"]:
        return "NECESSITA_DECISAO"
    if reg["caminho"] not in consumidos and reg["tipo"] == "auditor":
        return "DIAGNOSTICO_HISTORICO"
    if reg["termos_legados"] and reg["tipo"] in {"auditor", "auxiliar"}:
        return "ATIVO_COMPATIBILIDADE"
    if reg["tipo"] in {"runtime", "pacote"}:
        return "ATIVO_CANONICO"
    if reg["tipo"] == "auditor":
        return "ATIVO_CANONICO"
    return "NECESSITA_DECISAO"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-csv", action="store_true")
    args = ap.parse_args()

    arquivos = []
    for base in ALVOS:
        arquivos.extend(sorted(base.rglob("*.py")))

    regs = [analisar(p) for p in arquivos]
    importers = {r["caminho"] for r in regs}
    consumidos = set()
    by_path = {r["caminho"]: r for r in regs}
    for r in regs:
        txt = (ROOT / r["caminho"]).read_text(encoding="utf-8", errors="replace")
        for p2 in importers:
            if p2 == r["caminho"]:
                continue
            if Path(p2).name.replace('.py', '') in txt:
                consumidos.add(p2)

    for r in regs:
        r["consumido_por_outro"] = r["caminho"] in consumidos
        r["classificacao"] = classificar(r, consumidos)

    resumo = {
        "qtd_scripts_por_etapa": {e: sum(1 for r in regs if r["etapa"] == e) for e in {r["etapa"] for r in regs}},
        "qtd_scripts_ativos_canonicos": sum(1 for r in regs if r["classificacao"] == "ATIVO_CANONICO"),
        "qtd_scripts_com_shadow_ou_legado": sum(1 for r in regs if r["termos_legados"]),
        "qtd_scripts_com_fallback": sum(1 for r in regs if "fallback" in " ".join(r["termos_legados"])),
        "qtd_scripts_com_sentinelas": sum(1 for r in regs if r["sentinelas"]),
        "qtd_scripts_nao_consumidos": sum(1 for r in regs if not r["consumido_por_outro"]),
        "qtd_scripts_ativos_que_deveriam_ir_para_historico": sum(1 for r in regs if r["classificacao"] == "DIAGNOSTICO_HISTORICO"),
    }
    resumo["qtd_residuos_a_arquivar"] = sum(1 for r in regs if r["classificacao"] == "DIAGNOSTICO_HISTORICO")
    resumo["qtd_residuos_a_remover"] = sum(1 for r in regs if r["classificacao"] == "RESIDUO_A_REMOVER")
    resumo["cadeia_etapas_1_4_estrita"] = "indeterminado"

    out = {"resumo": resumo, "itens": regs}
    print(json.dumps(out, ensure_ascii=False, indent=2))

    if not args.sem_csv:
        csv_path = ROOT / "saidas" / "diagnostico" / "inventario_contratual_etapas_1_4.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["caminho", "etapa", "tipo", "classificacao", "consumido_por_outro", "termos_legados", "sentinelas", "flags_hardcoded_gate"])
            for r in regs:
                w.writerow([r["caminho"], r["etapa"], r["tipo"], r["classificacao"], r["consumido_por_outro"], ";".join(r["termos_legados"]), ";".join(r["sentinelas"]), r["flags_hardcoded_gate"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
