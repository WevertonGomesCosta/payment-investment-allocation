from __future__ import annotations

from typing import Any

import pandas as pd

from estado import EstadoSistema, assert_estado_minimo
from motor_precificacao import (
    calcular_valor_liquido_lote_bruto,
    calcular_data_elegivel_resgate,
    precificar_lote_investido_na_data,
    projetar_saldo_bruto_lote_ate_data,
)
from tipos import ConfigProjeto, FaseTemporal, StatusLote, ValidationIssue, ValidationReport


GASTOS_LOTES_HISTORICOS_COLUMNS = {
    "id_gasto": "string",
    "ordem_lote": "int16",
    "id_lote": "string",
    "data_gasto": "datetime64[ns]",
    "valor_gasto_centavos": "int64",
}

MOVIMENTACOES_HISTORICAS_COLUMNS = [
    "id_movimentacao",
    "tipo_movimentacao",
    "data_movimentacao",
    "id_gasto",
    "id_lote",
    "valor_consumido_centavos",
    "valor_bruto_antes_centavos",
    "valor_bruto_depois_centavos",
    "principal_antes_centavos",
    "principal_depois_centavos",
    "saldo_liquido_referencia_centavos",
    "observacao",
]


TOLERANCIA_CENTAVOS = 2



def inferir_data_corte_modelo(gastos: pd.DataFrame, config: ConfigProjeto) -> pd.Timestamp:
    gastos_historicos = gastos.loc[gastos["flag_pago_historico"], "data_gasto"].dropna()
    if gastos_historicos.empty:
        raise ValueError("Não foi possível inferir data_corte_modelo: nenhum gasto histórico encontrado.")
    return gastos_historicos.max()



def classificar_fase_temporal_gastos(
    gastos: pd.DataFrame,
    data_corte_modelo: pd.Timestamp,
    config: ConfigProjeto,
) -> pd.DataFrame:
    out = gastos.copy()
    out["fase_temporal"] = FaseTemporal.FUTURO.value
    out.loc[out["flag_pago_historico"], "fase_temporal"] = FaseTemporal.HISTORICO.value
    return out



def classificar_lotes_no_tempo(
    lotes: pd.DataFrame,
    data_corte_modelo: pd.Timestamp,
    data_referencia: pd.Timestamp,
) -> pd.DataFrame:
    out = lotes.copy()
    out["flag_historico"] = out["data_entrada_lote"] <= data_corte_modelo
    out["flag_futuro"] = out["data_entrada_lote"] > data_referencia
    return out



def materializar_gastos_lotes_historicos(gastos: pd.DataFrame, config: ConfigProjeto) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in gastos[gastos["flag_pago_historico"]].iterrows():
        lote_1 = str(row["lote_usado_1_raw"]).strip()
        lote_2 = str(row["lote_usado_2_raw"]).strip()
        if lote_1:
            rows.append(
                {
                    "id_gasto": row["id_gasto"],
                    "ordem_lote": 1,
                    "id_lote": lote_1,
                    "data_gasto": row["data_gasto"],
                    "valor_gasto_centavos": row["valor_gasto_centavos"],
                }
            )
        if lote_2:
            rows.append(
                {
                    "id_gasto": row["id_gasto"],
                    "ordem_lote": 2,
                    "id_lote": lote_2,
                    "data_gasto": row["data_gasto"],
                    "valor_gasto_centavos": row["valor_gasto_centavos"],
                }
            )
    return pd.DataFrame(rows, columns=list(GASTOS_LOTES_HISTORICOS_COLUMNS.keys()))



def validar_historico_gastos_vs_lotes(
    gastos_lotes_historicos: pd.DataFrame,
    lotes: pd.DataFrame,
) -> ValidationReport:
    report = ValidationReport(ok=True)
    lotes_existentes = set(lotes["id_lote"].dropna().astype(str))

    for _, row in gastos_lotes_historicos.iterrows():
        lote_id = str(row["id_lote"])
        if lote_id not in lotes_existentes:
            report.add_issue(
                ValidationIssue(
                    severity="ERROR",
                    table_name="gastos_lotes_historicos",
                    row_id=str(row["id_gasto"]),
                    field_name="id_lote",
                    code="LOTE_HISTORICO_INEXISTENTE",
                    message=f"Lote histórico '{lote_id}' não encontrado no inventário.",
                )
            )
    return report



def _buscar_carteira_do_lote(lote: pd.Series, carteiras: pd.DataFrame) -> pd.Series | None:
    carteira_id = str(lote.get("id_carteira_atual", "")).strip()
    if carteira_id == "":
        return None
    match = carteiras.loc[carteiras["id_carteira"] == carteira_id]
    if match.empty:
        return None
    return match.iloc[0]



def _atualizar_lote_ate_data(
    lote: pd.Series,
    data_alvo: pd.Timestamp,
    carteiras: pd.DataFrame,
    config: ConfigProjeto,
) -> pd.Series:
    out = lote.copy()
    data_alvo = pd.Timestamp(data_alvo).normalize()
    data_ultima = pd.Timestamp(out["data_ultima_atualizacao"]).normalize()
    if data_alvo <= data_ultima:
        return out

    if out["status_lote"] == StatusLote.INVESTIDO_ATUAL.value and bool(out["flag_carteira_encontrada"]):
        carteira = _buscar_carteira_do_lote(out, carteiras)
        if carteira is not None:
            out["valor_bruto_remanescente_centavos"] = projetar_saldo_bruto_lote_ate_data(
                valor_bruto_atual_centavos=int(out["valor_bruto_remanescente_centavos"]),
                carteira=carteira,
                data_inicio=data_ultima,
                data_fim=data_alvo,
                config=config,
            )
            out["valor_saldo_centavos"] = int(out["valor_bruto_remanescente_centavos"])

    out["data_ultima_atualizacao"] = data_alvo
    return out



def _consumir_valor_do_lote(
    lote: pd.Series,
    valor_consumo_centavos: int,
) -> tuple[pd.Series, dict[str, int]]:
    out = lote.copy()
    bruto_antes = int(out["valor_bruto_remanescente_centavos"])
    principal_antes = int(out["valor_principal_remanescente_centavos"])
    consumo = min(max(valor_consumo_centavos, 0), bruto_antes)

    if bruto_antes <= 0 or consumo <= 0:
        return out, {
            "consumo_realizado_centavos": 0,
            "valor_bruto_antes_centavos": bruto_antes,
            "valor_bruto_depois_centavos": bruto_antes,
            "principal_antes_centavos": principal_antes,
            "principal_depois_centavos": principal_antes,
        }

    fracao = min(consumo / bruto_antes, 1.0)
    principal_consumido = int(round(principal_antes * fracao))
    principal_depois = max(principal_antes - principal_consumido, 0)
    bruto_depois = max(bruto_antes - consumo, 0)

    if bruto_depois <= TOLERANCIA_CENTAVOS:
        bruto_depois = 0
    if principal_depois <= TOLERANCIA_CENTAVOS:
        principal_depois = 0

    out["valor_bruto_remanescente_centavos"] = bruto_depois
    out["valor_principal_remanescente_centavos"] = min(principal_depois, bruto_depois)
    out["valor_saldo_centavos"] = bruto_depois
    out["valor_consumido_historico_centavos"] = int(out["valor_consumido_historico_centavos"]) + consumo
    out["quantidade_consumos_historicos"] = int(out["quantidade_consumos_historicos"]) + 1
    out["flag_usado_historico"] = True
    out["data_ultimo_consumo_historico"] = out["data_ultima_atualizacao"]

    return out, {
        "consumo_realizado_centavos": consumo,
        "valor_bruto_antes_centavos": bruto_antes,
        "valor_bruto_depois_centavos": bruto_depois,
        "principal_antes_centavos": principal_antes,
        "principal_depois_centavos": int(out["valor_principal_remanescente_centavos"]),
    }



def _definir_status_final_lote(
    lote: pd.Series,
    data_referencia: pd.Timestamp,
) -> str:
    saldo = int(lote["valor_bruto_remanescente_centavos"])
    if saldo <= 0:
        return StatusLote.HISTORICO_EXECUTADO.value if bool(lote["flag_usado_historico"]) else StatusLote.ENCERRADO.value

    if str(lote["classe_bruta_lote"]) == "INVESTIDO":
        return StatusLote.INVESTIDO_ATUAL.value
    if str(lote["classe_bruta_lote"]) == "BLOQUEADO":
        return StatusLote.BLOQUEADO_MODELO.value
    if pd.Timestamp(lote["data_entrada_lote"]).normalize() <= pd.Timestamp(data_referencia).normalize():
        return StatusLote.LIVRE_DISPONIVEL.value
    return StatusLote.LIVRE_FUTURO.value



def reconstruir_saldos_pos_historico(
    lotes: pd.DataFrame,
    gastos_historicos: pd.DataFrame,
    gastos_lotes_historicos: pd.DataFrame,
    carteiras: pd.DataFrame,
    config: ConfigProjeto,
    data_referencia: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = lotes.copy()
    movimentacoes: list[dict[str, Any]] = []

    if gastos_historicos.empty:
        return out, pd.DataFrame(columns=MOVIMENTACOES_HISTORICAS_COLUMNS)

    gastos_hist_sorted = gastos_historicos.sort_values(["data_gasto", "id_gasto"]).reset_index(drop=True)
    lotes_idx = {str(row["id_lote"]): idx for idx, row in out.iterrows()}

    for _, gasto in gastos_hist_sorted.iterrows():
        remaining = int(gasto["valor_gasto_centavos"])
        refs = gastos_lotes_historicos.loc[gastos_lotes_historicos["id_gasto"] == gasto["id_gasto"]].sort_values("ordem_lote")

        for _, ref in refs.iterrows():
            lote_id = str(ref["id_lote"])
            idx = lotes_idx.get(lote_id)
            if idx is None:
                continue

            lote = out.loc[idx].copy()
            lote = _atualizar_lote_ate_data(lote, gasto["data_gasto"], carteiras, config)
            disponivel = int(lote["valor_bruto_remanescente_centavos"])
            consumir = min(remaining, disponivel)
            lote, info = _consumir_valor_do_lote(lote, consumir)
            out.loc[idx, lote.index] = lote.values

            remaining -= int(info["consumo_realizado_centavos"])
            movimentacoes.append(
                {
                    "id_movimentacao": f"MOV_HIST_{len(movimentacoes) + 1:06d}",
                    "tipo_movimentacao": "CONSUMO_HISTORICO",
                    "data_movimentacao": pd.Timestamp(gasto["data_gasto"]).normalize(),
                    "id_gasto": str(gasto["id_gasto"]),
                    "id_lote": lote_id,
                    "valor_consumido_centavos": int(info["consumo_realizado_centavos"]),
                    "valor_bruto_antes_centavos": int(info["valor_bruto_antes_centavos"]),
                    "valor_bruto_depois_centavos": int(info["valor_bruto_depois_centavos"]),
                    "principal_antes_centavos": int(info["principal_antes_centavos"]),
                    "principal_depois_centavos": int(info["principal_depois_centavos"]),
                    "saldo_liquido_referencia_centavos": int(lote["valor_liquido_resgatavel_centavos"]),
                    "observacao": "Reconstrução histórica v1: consumo econômico sequencial do lote usado no gasto já pago.",
                }
            )
            if remaining <= 0:
                break

        if remaining > TOLERANCIA_CENTAVOS:
            message = (
                f"Reconciliação histórica falhou para {gasto['id_gasto']}: "
                f"faltaram {remaining} centavos após consumir os lotes indicados."
            )
            if config.politicas_modelo.falha_reconciliacao_financeira.lower() == "erro":
                raise ValueError(message)
            movimentacoes.append(
                {
                    "id_movimentacao": f"MOV_HIST_{len(movimentacoes) + 1:06d}",
                    "tipo_movimentacao": "RECONCILIACAO_PENDENTE",
                    "data_movimentacao": pd.Timestamp(gasto["data_gasto"]).normalize(),
                    "id_gasto": str(gasto["id_gasto"]),
                    "id_lote": "",
                    "valor_consumido_centavos": 0,
                    "valor_bruto_antes_centavos": 0,
                    "valor_bruto_depois_centavos": 0,
                    "principal_antes_centavos": 0,
                    "principal_depois_centavos": 0,
                    "saldo_liquido_referencia_centavos": 0,
                    "observacao": message,
                }
            )

    # Atualiza lotes restantes até a data de referência e materializa valores econômicos finais.
    for idx, lote in out.iterrows():
        lote = _atualizar_lote_ate_data(lote, data_referencia, carteiras, config)
        carteira = _buscar_carteira_do_lote(lote, carteiras)
        if lote["status_lote"] == StatusLote.INVESTIDO_ATUAL.value and carteira is not None and int(lote["valor_bruto_remanescente_centavos"]) > 0:
            resultado = precificar_lote_investido_na_data(
                lote=lote,
                carteira=carteira,
                data_referencia=data_referencia,
                config=config,
            )
            lote["data_elegivel_resgate"] = calcular_data_elegivel_resgate(pd.Timestamp(lote["data_entrada_lote"]), carteira)
            lote["data_elegivel_switching"] = lote["data_elegivel_resgate"]
            lote["valor_liquido_resgatavel_centavos"] = int(resultado.valor_liquido_centavos)
            lote["valor_economico_centavos"] = int(resultado.valor_bruto_centavos)
        else:
            saldo = int(lote["valor_bruto_remanescente_centavos"])
            lote["valor_liquido_resgatavel_centavos"] = saldo
            lote["valor_economico_centavos"] = saldo
        lote["valor_saldo_centavos"] = int(lote["valor_bruto_remanescente_centavos"])
        lote["status_lote"] = _definir_status_final_lote(lote, data_referencia)
        out.loc[idx, lote.index] = lote.values

    return out, pd.DataFrame(movimentacoes, columns=MOVIMENTACOES_HISTORICAS_COLUMNS)



def construir_estado_inicial_prospectivo(
    gastos: pd.DataFrame,
    lotes: pd.DataFrame,
    carteiras: pd.DataFrame,
    config: ConfigProjeto,
    horizonte_final: pd.Timestamp | None = None,
) -> EstadoSistema:
    data_corte_modelo = inferir_data_corte_modelo(gastos, config)

    if config.execucao.data_referencia_simulacao:
        data_referencia = pd.Timestamp(config.execucao.data_referencia_simulacao).normalize()
    else:
        data_referencia = data_corte_modelo

    if horizonte_final is None:
        horizonte_final = max(
            gastos["data_gasto"].dropna().max(),
            lotes["data_entrada_lote"].dropna().max(),
        )

    gastos_classificados = classificar_fase_temporal_gastos(gastos, data_corte_modelo, config)
    lotes_classificados = classificar_lotes_no_tempo(lotes, data_corte_modelo, data_referencia)

    gastos_lotes_historicos = materializar_gastos_lotes_historicos(gastos_classificados, config)
    report = validar_historico_gastos_vs_lotes(gastos_lotes_historicos, lotes_classificados)
    if not report.ok:
        messages = [issue.message for issue in report.issues if issue.severity == "ERROR"]
        raise ValueError(" ; ".join(messages))

    gastos_historicos = gastos_classificados[gastos_classificados["fase_temporal"] == FaseTemporal.HISTORICO.value].copy()
    gastos_futuros = gastos_classificados[gastos_classificados["fase_temporal"] == FaseTemporal.FUTURO.value].copy()

    lotes_reconstruidos, movimentacoes = reconstruir_saldos_pos_historico(
        lotes=lotes_classificados,
        gastos_historicos=gastos_historicos,
        gastos_lotes_historicos=gastos_lotes_historicos,
        carteiras=carteiras,
        config=config,
        data_referencia=data_referencia,
    )

    lotes_historicos = lotes_reconstruidos[lotes_reconstruidos["flag_historico"]].copy()
    lotes_futuros = lotes_reconstruidos[lotes_reconstruidos["flag_futuro"]].copy()
    lotes_ativos = lotes_reconstruidos[
        (~lotes_reconstruidos["flag_futuro"])
        & (lotes_reconstruidos["valor_saldo_centavos"] > 0)
    ].copy()

    caixa_mask = lotes_ativos["status_lote"] == StatusLote.LIVRE_DISPONIVEL.value
    caixa_livre_centavos = int(lotes_ativos.loc[caixa_mask, "valor_saldo_centavos"].sum())

    estado = EstadoSistema(
        data_referencia=data_referencia,
        data_corte_modelo=data_corte_modelo,
        data_inicio_otimizacao=data_referencia,
        horizonte_final=pd.Timestamp(horizonte_final).normalize(),
        gastos=gastos_classificados,
        lotes=lotes_reconstruidos,
        carteiras=carteiras.copy(),
        gastos_historicos=gastos_historicos,
        gastos_futuros=gastos_futuros,
        lotes_historicos=lotes_historicos,
        lotes_ativos=lotes_ativos,
        lotes_futuros=lotes_futuros,
        movimentacoes=movimentacoes,
        decisoes=pd.DataFrame(),
        eventos=pd.DataFrame(),
        caixa_livre_centavos=caixa_livre_centavos,
        config=config,
        cenario_id="CENARIO_BASE_V1",
    )
    assert_estado_minimo(estado)
    return estado
