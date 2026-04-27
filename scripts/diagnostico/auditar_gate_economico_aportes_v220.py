"""Gate econômico obrigatório dos aportes planejados — V220/V222.

A V222 corrige o fluxo efetivo de leitura dos CSVs de impacto. O script agora
usa um resolver único para aceitar arquivos com prefixo da versão corrente
(V222), V221, V220 ou o fallback histórico V217.

Fluxo esperado:
    python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
    python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from nucleo.aportes_futuros_planejados import avaliar_gate_economico_aportes_planejados_v220
from nucleo.identidade_baseline import VERSAO_BASELINE, caminho_saida_diagnostico

COL_ALERTAS = ["tipo_alerta", "classe_alerta", "pagamento_id", "lote_planejado_id", "detalhe", "valor"]
COL_DECISAO = [
    "cenario_final_v220",
    "gate_economico_aprovado_v220",
    "status_gate_economico_v220",
    "acao_operacional_v220",
    "motivo",
    "delta_patrimonio_terminal_proxy",
    "delta_perda_terminal_total",
    "delta_penalidade_estrategica_total",
    "delta_deficit_total",
]


def sf(v: Any) -> float:
    try:
        if v is None or pd.isna(v):
            return 0.0
    except Exception:
        if v is None:
            return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def salvar(nome: str, df: pd.DataFrame | list[dict[str, Any]], cols: list[str] | None = None) -> None:
    destino = caminho_saida_diagnostico(RAIZ, nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    else:
        df = df.copy()
    if cols:
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df = df[cols]
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"CSV: {destino.relative_to(RAIZ).as_posix()}")


def _resolver_csv_impacto(nome_base: str) -> Path:
    """Resolve CSVs de impacto compatíveis com V222/V221/V220/V217."""
    candidatos = [
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_{VERSAO_BASELINE.lower()}_{nome_base}_real.csv"),
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_v223_{nome_base}_real.csv"),
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_v222_{nome_base}_real.csv"),
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_v221_{nome_base}_real.csv"),
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_v220_{nome_base}_real.csv"),
        caminho_saida_diagnostico(RAIZ, f"impacto_contas_futuras_v217_{nome_base}_real.csv"),
    ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    candidatos_txt = "\n".join(f"- {c.relative_to(RAIZ).as_posix()}" for c in candidatos)
    raise SystemExit(
        "CSV de impacto ausente. Rode primeiro:\n"
        "python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real\n\n"
        f"Candidatos esperados:\n{candidatos_txt}"
    )


def _resolver_csv_impacto_opcional(nome_base: str) -> Path | None:
    try:
        return _resolver_csv_impacto(nome_base)
    except SystemExit:
        return None


def _carregar_csvs_impacto() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    resumo_path = _resolver_csv_impacto("resumo")
    comp_path = _resolver_csv_impacto_opcional("comparativo_pagamentos")
    lotes_path = _resolver_csv_impacto_opcional("lotes_planejados")

    resumo = pd.read_csv(resumo_path)
    comp = pd.read_csv(comp_path) if comp_path is not None and comp_path.exists() else pd.DataFrame()
    lotes = pd.read_csv(lotes_path) if lotes_path is not None and lotes_path.exists() else pd.DataFrame()
    return resumo, comp, lotes, resumo_path.name


def _obter_delta(resumo: pd.DataFrame) -> dict[str, float]:
    if "cenario" not in resumo.columns:
        raise SystemExit("CSV de resumo não contém coluna obrigatória: cenario")

    delta_rows = resumo[resumo["cenario"].astype(str).eq("delta_com_menos_sem")]
    if len(delta_rows):
        r = delta_rows.iloc[0]
        return {
            "patrimonio_terminal_proxy": sf(r.get("patrimonio_terminal_proxy")),
            "perda_terminal_total": sf(r.get("perda_terminal_total")),
            "penalidade_estrategica_total": sf(r.get("penalidade_estrategica_total")),
            "deficit_total": sf(r.get("deficit_total")),
        }

    sem_rows = resumo[resumo["cenario"].astype(str).str.contains("sem_aporte", case=False, na=False)]
    com_rows = resumo[resumo["cenario"].astype(str).str.contains("com_aporte", case=False, na=False)]
    if not len(sem_rows) or not len(com_rows):
        raise SystemExit("Não foi possível identificar cenários sem_aporte/com_aporte no resumo.")

    sem = sem_rows.iloc[0]
    com = com_rows.iloc[0]
    return {
        "patrimonio_terminal_proxy": round(sf(com.get("patrimonio_terminal_proxy")) - sf(sem.get("patrimonio_terminal_proxy")), 2),
        "perda_terminal_total": round(sf(com.get("perda_terminal_total")) - sf(sem.get("perda_terminal_total")), 2),
        "penalidade_estrategica_total": round(sf(com.get("penalidade_estrategica_total")) - sf(sem.get("penalidade_estrategica_total")), 2),
        "deficit_total": round(sf(com.get("deficit_total")) - sf(sem.get("deficit_total")), 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true")
    args = ap.parse_args()
    if not args.real:
        raise SystemExit("Use --real")

    resumo, comp, lotes, arquivo_resumo_usado = _carregar_csvs_impacto()
    delta = _obter_delta(resumo)

    gate = avaliar_gate_economico_aportes_planejados_v220(
        delta_patrimonio_terminal_proxy=delta["patrimonio_terminal_proxy"],
        delta_perda_terminal_total=delta["perda_terminal_total"],
        delta_penalidade_estrategica_total=delta["penalidade_estrategica_total"],
        delta_deficit_total=delta["deficit_total"],
    )
    aprovado = bool(gate["gate_economico_aprovado_v220"])

    lotes = lotes.copy()
    if len(lotes):
        lotes["status_gate_economico_v220"] = gate["status_gate_economico_v220"]
        lotes["classificacao_economica_v220"] = gate["status_gate_economico_v220"]
        lotes["motivo_gate_economico_v220"] = gate.get("falhas_gate_economico_v220") or "gate_economico_aprovado"
        for k in [
            "delta_patrimonio_terminal_proxy",
            "delta_perda_terminal_total",
            "delta_penalidade_estrategica_total",
            "delta_deficit_total",
        ]:
            lotes[k] = gate[k]

    alertas = []
    if not aprovado:
        alertas.append(
            {
                "tipo_alerta": "gate_economico_bloqueou_aportes_planejados",
                "classe_alerta": "bloqueio_economico_v220",
                "pagamento_id": "",
                "lote_planejado_id": "",
                "detalhe": gate.get("falhas_gate_economico_v220"),
                "valor": gate.get("delta_patrimonio_terminal_proxy"),
            }
        )

    decisao = [
        {
            "cenario_final_v220": "com_aportes_planejados" if aprovado else "sem_aportes_planejados",
            "gate_economico_aprovado_v220": aprovado,
            "status_gate_economico_v220": gate["status_gate_economico_v220"],
            "acao_operacional_v220": "usar_aportes_planejados" if aprovado else "bloquear_aportes_planejados_e_usar_sem_aporte",
            "motivo": gate.get("falhas_gate_economico_v220") or "gate_economico_aprovado",
            "delta_patrimonio_terminal_proxy": gate["delta_patrimonio_terminal_proxy"],
            "delta_perda_terminal_total": gate["delta_perda_terminal_total"],
            "delta_penalidade_estrategica_total": gate["delta_penalidade_estrategica_total"],
            "delta_deficit_total": gate["delta_deficit_total"],
        }
    ]

    salvar(f"gate_economico_aportes_{VERSAO_BASELINE.lower()}_resumo_real.csv", resumo)
    salvar(f"gate_economico_aportes_{VERSAO_BASELINE.lower()}_comparativo_pagamentos_real.csv", comp)
    salvar(f"gate_economico_aportes_{VERSAO_BASELINE.lower()}_lotes_real.csv", lotes)
    salvar(f"gate_economico_aportes_{VERSAO_BASELINE.lower()}_alertas_real.csv", alertas, COL_ALERTAS)
    salvar(f"gate_economico_aportes_{VERSAO_BASELINE.lower()}_decisao_final_real.csv", decisao, COL_DECISAO)

    print("=== GATE ECONOMICO APORTES PLANEJADOS V220/V222/V223 ===")
    print(f"versao: {VERSAO_BASELINE}")
    print(f"arquivo_resumo_usado: {arquivo_resumo_usado}")
    print(f"delta_patrimonio_terminal_proxy: {gate['delta_patrimonio_terminal_proxy']}")
    print(f"delta_perda_terminal_total: {gate['delta_perda_terminal_total']}")
    print(f"delta_penalidade_estrategica_total: {gate['delta_penalidade_estrategica_total']}")
    print(f"delta_deficit_total: {gate['delta_deficit_total']}")
    print(f"status_gate_economico_v220: {gate['status_gate_economico_v220']}")
    print(f"cenario_final_v220: {'com_aportes_planejados' if aprovado else 'sem_aportes_planejados'}")
    print(f"alertas: {len(alertas)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
