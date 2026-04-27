"""Auditoria final pré-baseline da V223."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from nucleo.identidade_baseline import VERSAO_BASELINE, caminho_saida_diagnostico

COLUNAS_ALERTAS = ["tipo_alerta", "classe_alerta", "pagamento_id", "lote_planejado_id", "detalhe", "valor"]

def _csv(nome: str) -> Path:
    return caminho_saida_diagnostico(RAIZ, nome)

def _ler_csv(nome: str) -> tuple[pd.DataFrame, str]:
    caminho = _csv(nome)
    if not caminho.exists():
        return pd.DataFrame(), "AUSENTE"
    try:
        return pd.read_csv(caminho), "OK"
    except pd.errors.EmptyDataError:
        return pd.DataFrame(), "VAZIO_SEM_CABECALHO"
    except Exception as exc:
        return pd.DataFrame(), f"ERRO:{exc}"

def _salvar(nome: str, df: pd.DataFrame) -> None:
    destino = _csv(nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"CSV: {destino.relative_to(RAIZ).as_posix()}")

def main() -> int:
    versao = VERSAO_BASELINE.lower()
    checks: list[dict[str, Any]] = []

    def add(item: str, status: str, evidencia: str, gravidade: str = "informativa") -> None:
        checks.append({"item": item, "status": status, "gravidade": gravidade, "evidencia": evidencia})

    scripts = [
        "scripts/diagnostico/auditar_impacto_contas_futuras_v223.py",
        "scripts/diagnostico/auditar_gate_economico_aportes_v223.py",
        "scripts/diagnostico/auditar_impacto_contas_futuras_v217.py",
        "scripts/diagnostico/auditar_gate_economico_aportes_v220.py",
    ]
    for rel in scripts:
        add(f"script_presente::{rel}", "OK" if (RAIZ / rel).exists() else "FALHA", rel, "alta")

    alertas_impacto_nome = f"impacto_contas_futuras_{versao}_alertas_real.csv"
    alertas_impacto, st_alertas_impacto = _ler_csv(alertas_impacto_nome)
    if st_alertas_impacto == "OK":
        falta = [c for c in COLUNAS_ALERTAS if c not in alertas_impacto.columns]
        add("impacto_alertas_com_cabecalho", "OK" if not falta else "FALHA", f"linhas={len(alertas_impacto)}; faltantes={falta}", "alta")
    elif st_alertas_impacto == "AUSENTE":
        add("impacto_alertas_com_cabecalho", "NAO_EXECUTADO", f"{alertas_impacto_nome} ausente; rode auditar_impacto_contas_futuras_v223.py --real", "media")
    else:
        add("impacto_alertas_com_cabecalho", "FALHA", st_alertas_impacto, "alta")

    decisao_nome = f"gate_economico_aportes_{versao}_decisao_final_real.csv"
    decisao, st_decisao = _ler_csv(decisao_nome)
    if st_decisao == "OK" and len(decisao):
        row = decisao.iloc[0].to_dict()
        add("gate_decisao_final_presente", "OK", f"cenario={row.get('cenario_final_v220')}; status={row.get('status_gate_economico_v220')}", "critica")
        add("gate_status_auditado", "OK" if str(row.get("status_gate_economico_v220")) else "FALHA", str(row.get("status_gate_economico_v220")), "critica")
    elif st_decisao == "AUSENTE":
        add("gate_decisao_final_presente", "NAO_EXECUTADO", f"{decisao_nome} ausente; rode auditar_gate_economico_aportes_v223.py --real", "media")
    else:
        add("gate_decisao_final_presente", "FALHA", st_decisao, "critica")

    matriz = pd.DataFrame(checks)
    _salvar(f"auditoria_final_pre_baseline_{versao}.csv", matriz)

    falhas = int((matriz["status"] == "FALHA").sum())
    nao_exec = int((matriz["status"] == "NAO_EXECUTADO").sum())
    atencoes = int(matriz["status"].astype(str).str.startswith("ATENCAO").sum())

    print("=== AUDITORIA FINAL PRE-BASELINE V223 ===")
    print(f"versao: {VERSAO_BASELINE}")
    print(f"checks: {len(matriz)}")
    print(f"falhas: {falhas}")
    print(f"nao_executado: {nao_exec}")
    print(f"atencoes: {atencoes}")
    print("status: " + ("auditoria_final_v223_pronta_para_execucao_real" if falhas == 0 else "revisar_v223"))
    return 0 if falhas == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
