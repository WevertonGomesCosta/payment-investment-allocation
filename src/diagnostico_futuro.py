from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from estado import EstadoSistema
from motor_resgates import (
    CANDIDATOS_RESGATE_COLUMNS,
    SELECOES_RESGATE_COLUMNS,
    selecionar_resgates_para_deficit,
    gerar_candidatos_resgate_por_data,
)


TIMELINE_DIAGNOSTICO_COLUMNS = [
    "data",
    "caixa_antes_centavos",
    "recebidos_livres_centavos",
    "gastos_futuros_centavos",
    "caixa_depois_sem_resgate_centavos",
    "deficit_sem_resgate_centavos",
    "resgates_realizados_centavos",
    "custo_oportunidade_resgates_centavos",
    "caixa_depois_com_resgate_centavos",
    "saldo_investido_liquido_pos_dia_centavos",
    "observacao",
]

RESGATES_DIAGNOSTICO_COLUMNS = SELECOES_RESGATE_COLUMNS


@dataclass
class DiagnosticoPagamentosFuturos:
    resumo: dict[str, Any]
    timeline: pd.DataFrame
    resgates: pd.DataFrame
    candidatos_primeira_data_critica: pd.DataFrame



def _datas_evento(estado: EstadoSistema) -> list[pd.Timestamp]:
    datas_gastos = set(pd.to_datetime(estado.gastos_futuros["data_gasto"], errors="coerce").dropna().dt.normalize())
    datas_lotes = set(
        pd.to_datetime(
            estado.lotes_futuros.loc[
                estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO",
                "data_entrada_lote",
            ],
            errors="coerce",
        ).dropna().dt.normalize()
    )
    return sorted(datas_gastos.union(datas_lotes))



def construir_timeline_fluxo_livre(estado: EstadoSistema) -> pd.DataFrame:
    datas = _datas_evento(estado)
    caixa = int(estado.caixa_livre_centavos)
    rows: list[dict[str, Any]] = []

    gastos_por_data = (
        estado.gastos_futuros.groupby("data_gasto", dropna=True)["valor_gasto_centavos"].sum().to_dict()
    )
    recebidos_por_data = (
        estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO"]
        .groupby("data_entrada_lote", dropna=True)["valor_saldo_centavos"]
        .sum()
        .to_dict()
    )

    for data in datas:
        data = pd.Timestamp(data).normalize()
        caixa_antes = caixa
        recebidos = int(recebidos_por_data.get(data, 0))
        gastos = int(gastos_por_data.get(data, 0))
        caixa_depois = caixa + recebidos - gastos
        deficit = max(-caixa_depois, 0)
        rows.append(
            {
                "data": data,
                "caixa_antes_centavos": caixa_antes,
                "recebidos_livres_centavos": recebidos,
                "gastos_futuros_centavos": gastos,
                "caixa_depois_sem_resgate_centavos": caixa_depois,
                "deficit_sem_resgate_centavos": deficit,
            }
        )
        caixa = caixa_depois

    return pd.DataFrame(rows)



def obter_datas_criticas_sem_resgate(
    estado: EstadoSistema,
    max_datas: int | None = None,
) -> pd.DataFrame:
    """Retorna datas críticas considerando apenas caixa livre e recebidos futuros livres."""
    timeline = construir_timeline_fluxo_livre(estado)
    if timeline.empty:
        return timeline
    criticas = timeline.loc[timeline["deficit_sem_resgate_centavos"] > 0].copy()
    criticas = criticas.sort_values(["data", "deficit_sem_resgate_centavos"], ascending=[True, False]).reset_index(drop=True)
    if max_datas is not None:
        criticas = criticas.head(max_datas).copy()
    return criticas


def _saldo_investido_liquido(lotes: pd.DataFrame) -> int:
    mask = lotes["status_lote"] == "INVESTIDO_ATUAL"
    return int(lotes.loc[mask, "valor_liquido_resgatavel_centavos"].sum())



def diagnosticar_pagamentos_futuros(estado: EstadoSistema) -> DiagnosticoPagamentosFuturos:
    timeline_livre = construir_timeline_fluxo_livre(estado)
    lotes_diag = estado.lotes.copy()
    datas = _datas_evento(estado)
    caixa = int(estado.caixa_livre_centavos)
    timeline_rows: list[dict[str, Any]] = []
    resgates_rows: list[dict[str, Any]] = []

    gastos_por_data = (
        estado.gastos_futuros.groupby("data_gasto", dropna=True)["valor_gasto_centavos"].sum().to_dict()
    )
    recebidos_por_data = (
        estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO"]
        .groupby("data_entrada_lote", dropna=True)["valor_saldo_centavos"]
        .sum()
        .to_dict()
    )

    primeira_data_critica = None
    if not timeline_livre.empty:
        crit = timeline_livre.loc[timeline_livre["deficit_sem_resgate_centavos"] > 0]
        if not crit.empty:
            primeira_data_critica = pd.Timestamp(crit.iloc[0]["data"]).normalize()

    for data in datas:
        data = pd.Timestamp(data).normalize()
        caixa_antes = caixa
        recebidos = int(recebidos_por_data.get(data, 0))
        gastos = int(gastos_por_data.get(data, 0))
        caixa_sem_resgate = caixa + recebidos - gastos
        deficit = max(-caixa_sem_resgate, 0)
        resgates_dia = 0
        custo_oportunidade_dia = 0
        observacao = "Cobertura integral sem resgate."

        caixa = caixa_sem_resgate
        if deficit > 0:
            resultado = selecionar_resgates_para_deficit(
                estado=estado,
                data_critica=data,
                deficit_centavos=deficit,
                lotes_base=lotes_diag,
            )
            lotes_diag = resultado.lotes_atualizados.copy()
            if not resultado.selecoes.empty:
                for row in resultado.selecoes.to_dict(orient="records"):
                    resgates_rows.append(row)
                    resgates_dia += int(row["valor_resgatado_centavos"])
                    custo_oportunidade_dia += int(row["custo_oportunidade_centavos"])
                caixa += int(resultado.selecoes["valor_resgatado_centavos"].sum())

            if resultado.cobertura_total:
                observacao = "Déficit coberto por política intertemporal de resgates candidatos."
            else:
                observacao = "Déficit permaneceu após política intertemporal: cobertura insuficiente."

        timeline_rows.append(
            {
                "data": data,
                "caixa_antes_centavos": caixa_antes,
                "recebidos_livres_centavos": recebidos,
                "gastos_futuros_centavos": gastos,
                "caixa_depois_sem_resgate_centavos": caixa_sem_resgate,
                "deficit_sem_resgate_centavos": max(-caixa_sem_resgate, 0),
                "resgates_realizados_centavos": resgates_dia,
                "custo_oportunidade_resgates_centavos": custo_oportunidade_dia,
                "caixa_depois_com_resgate_centavos": caixa,
                "saldo_investido_liquido_pos_dia_centavos": _saldo_investido_liquido(lotes_diag),
                "observacao": observacao,
            }
        )

    timeline = pd.DataFrame(timeline_rows, columns=TIMELINE_DIAGNOSTICO_COLUMNS)
    resgates = pd.DataFrame(resgates_rows, columns=RESGATES_DIAGNOSTICO_COLUMNS)

    if primeira_data_critica is not None:
        candidatos_primeira = gerar_candidatos_resgate_por_data(
            estado=estado,
            data_critica=primeira_data_critica,
            valor_necessario_centavos=int(
                timeline_livre.loc[timeline_livre["data"] == primeira_data_critica, "deficit_sem_resgate_centavos"].iloc[0]
            ),
            lotes_base=estado.lotes.copy(),
        )
    else:
        candidatos_primeira = pd.DataFrame(columns=CANDIDATOS_RESGATE_COLUMNS)

    total_gastos_futuros = int(estado.gastos_futuros["valor_gasto_centavos"].sum())
    total_recebidos_futuros = int(
        estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO", "valor_saldo_centavos"].sum()
    )
    saldo_final_sem_resgate = int(estado.caixa_livre_centavos + total_recebidos_futuros - total_gastos_futuros)
    pior_deficit_sem_resgate = int(max(0, -timeline_livre["caixa_depois_sem_resgate_centavos"].min())) if not timeline_livre.empty else 0
    saldo_final_com_resgate = int(timeline["caixa_depois_com_resgate_centavos"].iloc[-1]) if not timeline.empty else int(estado.caixa_livre_centavos)
    lotes_remanescentes_liquidos = int(_saldo_investido_liquido(lotes_diag))
    custo_oportunidade_total = int(resgates["custo_oportunidade_centavos"].sum()) if not resgates.empty else 0

    resumo = {
        "politica_resgate": "intertemporal_gulosa_com_preservacao_futura",
        "data_corte_modelo": str(estado.data_corte_modelo.date()),
        "data_referencia": str(estado.data_referencia.date()),
        "horizonte_final": str(estado.horizonte_final.date()),
        "caixa_livre_inicial_centavos": int(estado.caixa_livre_centavos),
        "total_gastos_futuros_centavos": total_gastos_futuros,
        "total_recebidos_futuros_livres_centavos": total_recebidos_futuros,
        "saldo_final_sem_resgates_centavos": saldo_final_sem_resgate,
        "pior_deficit_sem_resgate_centavos": pior_deficit_sem_resgate,
        "primeira_data_critica_sem_resgate": str(primeira_data_critica.date()) if primeira_data_critica is not None else None,
        "qtd_datas_criticas_sem_resgate": int((timeline_livre["deficit_sem_resgate_centavos"] > 0).sum()) if not timeline_livre.empty else 0,
        "total_resgates_diagnostico_centavos": int(resgates["valor_resgatado_centavos"].sum()) if not resgates.empty else 0,
        "total_custo_oportunidade_resgates_centavos": custo_oportunidade_total,
        "qtd_datas_com_resgate": int((timeline["resgates_realizados_centavos"] > 0).sum()) if not timeline.empty else 0,
        "qtd_eventos_resgate": int(len(resgates)),
        "saldo_final_com_resgates_centavos": saldo_final_com_resgate,
        "lotes_investidos_liquidos_remanescentes_centavos": lotes_remanescentes_liquidos,
        "cobertura_total_viavel": bool(saldo_final_com_resgate >= 0),
    }

    return DiagnosticoPagamentosFuturos(
        resumo=resumo,
        timeline=timeline,
        resgates=resgates,
        candidatos_primeira_data_critica=candidatos_primeira,
    )
