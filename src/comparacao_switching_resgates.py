from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from diagnostico_futuro import construir_timeline_fluxo_livre
from estado import EstadoSistema
from motor_resgates import selecionar_resgates_para_deficit
from motor_switching import gerar_candidatos_switching_por_data


COMPARACAO_SWITCHING_RESGATES_COLUMNS = [
    "data",
    "deficit_sem_resgate_centavos",
    "resgates_atuais_total_centavos",
    "qtd_resgates_atual",
    "custo_oportunidade_resgates_centavos",
    "ids_lotes_resgatados",
    "melhor_switching_id_lote_origem",
    "melhor_switching_carteira_origem",
    "melhor_switching_id_carteira_destino",
    "melhor_switching_carteira_destino",
    "melhor_switching_valor_transferido_centavos",
    "melhor_switching_score_vs_resgate_centavos",
    "melhor_switching_melhor_acao",
    "qtd_candidatos_switching",
    "qtd_candidatos_switching_positivos",
    "switching_substitui_totalmente",
    "switching_melhora_parcialmente",
    "classificacao_comparacao",
    "observacao",
]

TOP_CANDIDATOS_COLUMNS = [
    "data",
    "deficit_sem_resgate_centavos",
    "tipo_candidato",
    "ranking_candidato",
    "id_lote_origem",
    "carteira_origem",
    "id_carteira_destino",
    "carteira_destino",
    "valor_liquido_transferido_centavos",
    "score_switching_vs_resgate_centavos",
    "score_ranking_switching_centavos",
    "melhor_acao",
    "suficiente_para_cobrir_sozinho",
]


@dataclass
class ResultadoComparacaoSwitchingResgates:
    resumo: dict[str, Any]
    comparacao_por_data: pd.DataFrame
    top_candidatos_por_data: pd.DataFrame
    resgates_politica_atual: pd.DataFrame



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



def _safe_join_ids(series: pd.Series) -> str:
    vals = [str(v) for v in series.dropna().tolist() if str(v).strip()]
    return ", ".join(vals)



def _json_safe(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value



def _records(df: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    if limit is not None:
        df = df.head(limit).copy()
    out: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        out.append({k: _json_safe(v) for k, v in row.items()})
    return out



def comparar_switching_vs_resgates(estado: EstadoSistema, limitar_destinos_por_lote: int | None = None) -> ResultadoComparacaoSwitchingResgates:
    timeline_livre = construir_timeline_fluxo_livre(estado)
    datas = _datas_evento(estado)
    lotes_diag = estado.lotes.copy()
    caixa = int(estado.caixa_livre_centavos)

    gastos_por_data = (
        estado.gastos_futuros.groupby("data_gasto", dropna=True)["valor_gasto_centavos"].sum().to_dict()
    )
    recebidos_por_data = (
        estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO"]
        .groupby("data_entrada_lote", dropna=True)["valor_saldo_centavos"]
        .sum()
        .to_dict()
    )

    comparacao_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    resgates_rows: list[dict[str, Any]] = []

    for data in datas:
        data = pd.Timestamp(data).normalize()
        recebidos = int(recebidos_por_data.get(data, 0))
        gastos = int(gastos_por_data.get(data, 0))
        caixa_sem_resgate = caixa + recebidos - gastos
        deficit = max(-caixa_sem_resgate, 0)

        if deficit > 0:
            candidatos = gerar_candidatos_switching_por_data(
                estado=estado,
                data_critica=data,
                deficit_centavos=deficit,
                lotes_base=lotes_diag,
                limitar_destinos_por_lote=limitar_destinos_por_lote,
            )
            resultado_resgates = selecionar_resgates_para_deficit(
                estado=estado,
                data_critica=data,
                deficit_centavos=deficit,
                lotes_base=lotes_diag,
            )

            selecoes = resultado_resgates.selecoes.copy()
            lotes_diag = resultado_resgates.lotes_atualizados.copy()
            if not selecoes.empty:
                resgates_rows.extend(selecoes.to_dict(orient="records"))
                caixa = caixa_sem_resgate + int(selecoes["valor_resgatado_centavos"].sum())
            else:
                caixa = caixa_sem_resgate

            positivos = candidatos.loc[
                (candidatos["melhor_acao"] == "SWITCHAR")
                & (candidatos["score_switching_vs_resgate_centavos"] > 0)
            ].copy() if not candidatos.empty else pd.DataFrame(columns=candidatos.columns if not candidatos.empty else [])

            suficientes = positivos.loc[
                positivos["valor_liquido_transferido_centavos"] >= deficit
            ].copy() if not positivos.empty else pd.DataFrame(columns=positivos.columns if not positivos.empty else [])

            melhor_geral = positivos.head(1).copy() if not positivos.empty else pd.DataFrame()
            melhor_suficiente = suficientes.head(1).copy() if not suficientes.empty else pd.DataFrame()

            if not melhor_suficiente.empty:
                melhor = melhor_suficiente.iloc[0]
                substitui_totalmente = True
                melhora_parcialmente = False
                classificacao = "SWITCH_SUBSTITUI_TOTAL"
                observacao = "Há candidato de switching com ganho positivo vs resgate e cobertura integral do déficit do dia."
            elif not melhor_geral.empty:
                melhor = melhor_geral.iloc[0]
                substitui_totalmente = False
                melhora_parcialmente = True
                classificacao = "SWITCH_COMPLEMENTA"
                observacao = "Há candidato de switching melhor que resgate, mas sem cobertura total isolada do déficit do dia."
            else:
                melhor = None
                substitui_totalmente = False
                melhora_parcialmente = False
                classificacao = "RESGATE_MANTIDO"
                observacao = "Não houve candidato de switching com ganho positivo vs resgate nesta data crítica."

            if melhor_geral is not None and not melhor_geral.empty:
                mg = melhor_geral.iloc[0]
                top_rows.append({
                    "data": data,
                    "deficit_sem_resgate_centavos": int(deficit),
                    "tipo_candidato": "melhor_geral",
                    "ranking_candidato": int(mg["ranking_candidato"]),
                    "id_lote_origem": str(mg["id_lote_origem"]),
                    "carteira_origem": str(mg["carteira_origem"]),
                    "id_carteira_destino": str(mg["id_carteira_destino"]),
                    "carteira_destino": str(mg["carteira_destino"]),
                    "valor_liquido_transferido_centavos": int(mg["valor_liquido_transferido_centavos"]),
                    "score_switching_vs_resgate_centavos": int(mg["score_switching_vs_resgate_centavos"]),
                    "score_ranking_switching_centavos": int(mg["score_ranking_switching_centavos"]),
                    "melhor_acao": str(mg["melhor_acao"]),
                    "suficiente_para_cobrir_sozinho": bool(mg["suficiente_para_cobrir_sozinho"]),
                })
            if melhor_suficiente is not None and not melhor_suficiente.empty:
                ms = melhor_suficiente.iloc[0]
                top_rows.append({
                    "data": data,
                    "deficit_sem_resgate_centavos": int(deficit),
                    "tipo_candidato": "melhor_suficiente",
                    "ranking_candidato": int(ms["ranking_candidato"]),
                    "id_lote_origem": str(ms["id_lote_origem"]),
                    "carteira_origem": str(ms["carteira_origem"]),
                    "id_carteira_destino": str(ms["id_carteira_destino"]),
                    "carteira_destino": str(ms["carteira_destino"]),
                    "valor_liquido_transferido_centavos": int(ms["valor_liquido_transferido_centavos"]),
                    "score_switching_vs_resgate_centavos": int(ms["score_switching_vs_resgate_centavos"]),
                    "score_ranking_switching_centavos": int(ms["score_ranking_switching_centavos"]),
                    "melhor_acao": str(ms["melhor_acao"]),
                    "suficiente_para_cobrir_sozinho": bool(ms["suficiente_para_cobrir_sozinho"]),
                })

            comparacao_rows.append({
                "data": data,
                "deficit_sem_resgate_centavos": int(deficit),
                "resgates_atuais_total_centavos": int(selecoes["valor_resgatado_centavos"].sum()) if not selecoes.empty else 0,
                "qtd_resgates_atual": int(len(selecoes)),
                "custo_oportunidade_resgates_centavos": int(selecoes["custo_oportunidade_centavos"].sum()) if not selecoes.empty else 0,
                "ids_lotes_resgatados": _safe_join_ids(selecoes["id_lote"]) if not selecoes.empty else "",
                "melhor_switching_id_lote_origem": "" if melhor is None else str(melhor["id_lote_origem"]),
                "melhor_switching_carteira_origem": "" if melhor is None else str(melhor["carteira_origem"]),
                "melhor_switching_id_carteira_destino": "" if melhor is None else str(melhor["id_carteira_destino"]),
                "melhor_switching_carteira_destino": "" if melhor is None else str(melhor["carteira_destino"]),
                "melhor_switching_valor_transferido_centavos": 0 if melhor is None else int(melhor["valor_liquido_transferido_centavos"]),
                "melhor_switching_score_vs_resgate_centavos": 0 if melhor is None else int(melhor["score_switching_vs_resgate_centavos"]),
                "melhor_switching_melhor_acao": "" if melhor is None else str(melhor["melhor_acao"]),
                "qtd_candidatos_switching": int(len(candidatos)),
                "qtd_candidatos_switching_positivos": int(len(positivos)),
                "switching_substitui_totalmente": bool(substitui_totalmente),
                "switching_melhora_parcialmente": bool(melhora_parcialmente),
                "classificacao_comparacao": classificacao,
                "observacao": observacao,
            })
        else:
            caixa = caixa_sem_resgate

    comparacao_df = pd.DataFrame(comparacao_rows, columns=COMPARACAO_SWITCHING_RESGATES_COLUMNS)
    top_df = pd.DataFrame(top_rows, columns=TOP_CANDIDATOS_COLUMNS)
    resgates_df = pd.DataFrame(resgates_rows)

    timeline_criticas = timeline_livre.loc[timeline_livre["deficit_sem_resgate_centavos"] > 0].copy()
    resumo = {
        "politica_base_resgates": "intertemporal_gulosa_com_preservacao_futura",
        "qtd_datas_criticas": int(len(timeline_criticas)),
        "qtd_datas_com_switch_substitui_total": int((comparacao_df["classificacao_comparacao"] == "SWITCH_SUBSTITUI_TOTAL").sum()) if not comparacao_df.empty else 0,
        "qtd_datas_com_switch_complementa": int((comparacao_df["classificacao_comparacao"] == "SWITCH_COMPLEMENTA").sum()) if not comparacao_df.empty else 0,
        "qtd_datas_sem_ganho_switch": int((comparacao_df["classificacao_comparacao"] == "RESGATE_MANTIDO").sum()) if not comparacao_df.empty else 0,
        "primeira_data_com_substituicao_total": None,
        "primeira_data_com_melhoria_parcial": None,
    }
    if not comparacao_df.empty:
        sub = comparacao_df.loc[comparacao_df["classificacao_comparacao"] == "SWITCH_SUBSTITUI_TOTAL"]
        comp = comparacao_df.loc[comparacao_df["classificacao_comparacao"] == "SWITCH_COMPLEMENTA"]
        if not sub.empty:
            resumo["primeira_data_com_substituicao_total"] = str(pd.Timestamp(sub.iloc[0]["data"]).date())
        if not comp.empty:
            resumo["primeira_data_com_melhoria_parcial"] = str(pd.Timestamp(comp.iloc[0]["data"]).date())

        top_sub = comparacao_df.loc[comparacao_df["switching_substitui_totalmente"]].sort_values(
            ["melhor_switching_score_vs_resgate_centavos", "data"], ascending=[False, True]
        )
        if not top_sub.empty:
            row = top_sub.iloc[0]
            resumo["melhor_substituicao_total"] = {
                "data": str(pd.Timestamp(row["data"]).date()),
                "id_lote_origem": str(row["melhor_switching_id_lote_origem"]),
                "carteira_destino": str(row["melhor_switching_carteira_destino"]),
                "score_vs_resgate_centavos": int(row["melhor_switching_score_vs_resgate_centavos"]),
                "valor_transferido_centavos": int(row["melhor_switching_valor_transferido_centavos"]),
            }
        top_comp = comparacao_df.loc[comparacao_df["switching_melhora_parcialmente"]].sort_values(
            ["melhor_switching_score_vs_resgate_centavos", "data"], ascending=[False, True]
        )
        if not top_comp.empty:
            row = top_comp.iloc[0]
            resumo["melhor_melhoria_parcial"] = {
                "data": str(pd.Timestamp(row["data"]).date()),
                "id_lote_origem": str(row["melhor_switching_id_lote_origem"]),
                "carteira_destino": str(row["melhor_switching_carteira_destino"]),
                "score_vs_resgate_centavos": int(row["melhor_switching_score_vs_resgate_centavos"]),
                "valor_transferido_centavos": int(row["melhor_switching_valor_transferido_centavos"]),
            }

    return ResultadoComparacaoSwitchingResgates(
        resumo=resumo,
        comparacao_por_data=comparacao_df,
        top_candidatos_por_data=top_df,
        resgates_politica_atual=resgates_df,
    )
