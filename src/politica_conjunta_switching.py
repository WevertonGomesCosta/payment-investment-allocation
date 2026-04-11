from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import pandas as pd

from estado import EstadoSistema
from diagnostico_futuro import _datas_evento, diagnosticar_pagamentos_futuros
from motor_resgates import atualizar_lotes_investidos_ate_data, selecionar_resgates_para_deficit
from motor_switching import gerar_candidatos_switching_por_data, obter_carteira_por_id


POLITICA_TIMELINE_COLUMNS = [
    "data",
    "caixa_antes_centavos",
    "recebidos_livres_centavos",
    "gastos_futuros_centavos",
    "deficit_sem_acao_centavos",
    "estrategia_escolhida",
    "switching_realizado",
    "id_lote_origem_switching",
    "id_carteira_destino_switching",
    "carteira_destino_switching",
    "valor_switching_centavos",
    "resgates_realizados_centavos",
    "qtd_eventos_resgate",
    "caixa_depois_centavos",
    "saldo_investido_liquido_pos_dia_centavos",
    "ganho_vs_base_centavos",
    "observacao",
]

SWITCH_EVENTS_COLUMNS = [
    "data_switching",
    "id_lote_origem",
    "id_lote_destino",
    "id_carteira_origem",
    "id_carteira_destino",
    "carteira_destino",
    "valor_switching_centavos",
    "tipo_switching",
    "ganho_vs_base_centavos",
    "riqueza_terminal_base_centavos",
    "riqueza_terminal_switch_centavos",
    "delta_eventos_resgate_futuros",
    "delta_custo_oportunidade_futuro_centavos",
    "motivo",
]


@dataclass
class ResultadoPoliticaConjuntaSwitching:
    resumo: dict[str, Any]
    timeline: pd.DataFrame
    switchings: pd.DataFrame
    resgates: pd.DataFrame
    comparacao_base: dict[str, Any]



def _maps_fluxo(estado: EstadoSistema) -> tuple[dict[pd.Timestamp, int], dict[pd.Timestamp, int]]:
    gastos_por_data = (
        estado.gastos_futuros.groupby("data_gasto", dropna=True)["valor_gasto_centavos"].sum().to_dict()
    )
    recebidos_por_data = (
        estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO"]
        .groupby("data_entrada_lote", dropna=True)["valor_saldo_centavos"]
        .sum()
        .to_dict()
    )
    return gastos_por_data, recebidos_por_data



def _saldo_investido_liquido(lotes: pd.DataFrame) -> int:
    mask = lotes["status_lote"] == "INVESTIDO_ATUAL"
    return int(lotes.loc[mask, "valor_liquido_resgatavel_centavos"].sum()) if mask.any() else 0



def _simular_futuro_com_resgates(
    estado: EstadoSistema,
    lotes_inicio: pd.DataFrame,
    caixa_inicial_centavos: int,
    data_inicio_exclusiva: pd.Timestamp,
) -> dict[str, Any]:
    gastos_por_data, recebidos_por_data = _maps_fluxo(estado)
    datas = [pd.Timestamp(d).normalize() for d in _datas_evento(estado) if pd.Timestamp(d).normalize() > pd.Timestamp(data_inicio_exclusiva).normalize()]
    lotes = lotes_inicio.copy()
    caixa = int(caixa_inicial_centavos)
    total_resgates = 0
    total_custo = 0
    eventos_resgate = 0

    for data in datas:
        caixa += int(recebidos_por_data.get(data, 0))
        caixa -= int(gastos_por_data.get(data, 0))
        deficit = max(-caixa, 0)
        if deficit > 0:
            resultado = selecionar_resgates_para_deficit(
                estado=estado,
                data_critica=data,
                deficit_centavos=deficit,
                lotes_base=lotes,
            )
            lotes = resultado.lotes_atualizados.copy()
            if not resultado.selecoes.empty:
                valor = int(resultado.selecoes["valor_resgatado_centavos"].sum())
                caixa += valor
                total_resgates += valor
                total_custo += int(resultado.selecoes["custo_oportunidade_centavos"].sum())
                eventos_resgate += int(len(resultado.selecoes))
            if not resultado.cobertura_total:
                return {
                    "viavel": False,
                    "caixa_final_centavos": int(caixa),
                    "saldo_investido_liquido_final_centavos": _saldo_investido_liquido(lotes),
                    "total_resgates_centavos": int(total_resgates),
                    "total_custo_oportunidade_centavos": int(total_custo),
                    "eventos_resgate": int(eventos_resgate),
                    "lotes_finais": lotes,
                }

    return {
        "viavel": caixa >= 0,
        "caixa_final_centavos": int(caixa),
        "saldo_investido_liquido_final_centavos": _saldo_investido_liquido(lotes),
        "total_resgates_centavos": int(total_resgates),
        "total_custo_oportunidade_centavos": int(total_custo),
        "eventos_resgate": int(eventos_resgate),
        "lotes_finais": lotes,
    }



def _criar_lote_destino_switching(
    lote_origem: pd.Series,
    carteira_destino: pd.Series,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    suffix: str,
    colunas_base: list[str],
) -> pd.Series:
    data_switching = pd.Timestamp(data_switching).normalize()
    carencia = int(carteira_destino.get("carencia_dias", 0))
    data_elegivel = data_switching + pd.Timedelta(days=carencia)
    row = {col: pd.NA for col in colunas_base}
    row.update(
        {
            "id_lote": f"SW_{str(lote_origem.get('id_lote',''))}_{str(carteira_destino.get('id_carteira',''))}_{suffix}",
            "data_entrada_lote": data_switching,
            "valor_original_centavos": int(valor_transferido_centavos),
            "valor_saldo_centavos": int(valor_transferido_centavos),
            "valor_principal_remanescente_centavos": int(valor_transferido_centavos),
            "valor_bruto_remanescente_centavos": int(valor_transferido_centavos),
            "valor_consumido_historico_centavos": 0,
            "quantidade_consumos_historicos": 0,
            "data_ultima_atualizacao": data_switching,
            "data_ultimo_consumo_historico": pd.NaT,
            "flag_usado_historico": False,
            "investimento_raw": str(carteira_destino.get("nome_carteira", "")),
            "classe_bruta_lote": "INVESTIDO",
            "status_lote": "INVESTIDO_ATUAL",
            "carteira_atual": str(carteira_destino.get("nome_carteira", "")),
            "id_carteira_atual": str(carteira_destino.get("id_carteira", "")),
            "flag_carteira_encontrada": True,
            "flag_historico": False,
            "flag_futuro": False,
            "flag_pode_pagar": False,
            "flag_pode_aportar": False,
            "flag_pode_switchar": True,
            "data_elegivel_resgate": data_elegivel,
            "data_elegivel_switching": data_elegivel,
            "valor_economico_centavos": int(valor_transferido_centavos),
            "valor_liquido_resgatavel_centavos": int(valor_transferido_centavos),
            "ultimo_ir_estimado_centavos": 0,
            "ultimo_iof_estimado_centavos": 0,
            "ultimo_custo_estimado_centavos": 0,
        }
    )
    return pd.Series(row)



def aplicar_switching_candidato(
    estado: EstadoSistema,
    lotes_base: pd.DataFrame,
    candidato: pd.Series,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    data = pd.Timestamp(candidato["data_switching"]).normalize()
    lotes = atualizar_lotes_investidos_ate_data(lotes_base.copy(), data, estado)

    id_lote = str(candidato["id_lote_origem"])
    idx_matches = lotes.index[lotes["id_lote"].astype(str) == id_lote].tolist()
    if not idx_matches:
        raise ValueError(f"Lote de origem não encontrado para switching: {id_lote}")
    idx = idx_matches[0]
    lote_origem = lotes.loc[idx].copy()

    valor_transferido = min(
        int(candidato["valor_liquido_transferido_centavos"]),
        int(lote_origem.get("valor_liquido_resgatavel_centavos", 0)),
    )
    if valor_transferido <= 0:
        raise ValueError("Valor de switching inválido ou nulo.")

    liquido_antes = int(lote_origem["valor_liquido_resgatavel_centavos"])
    bruto_antes = int(lote_origem["valor_bruto_remanescente_centavos"])
    principal_antes = int(lote_origem["valor_principal_remanescente_centavos"])

    fracao = min(valor_transferido / liquido_antes, 1.0)
    bruto_depois = max(int(round(bruto_antes * (1.0 - fracao))), 0)
    principal_depois = max(int(round(principal_antes * (1.0 - fracao))), 0)
    liquido_depois = max(liquido_antes - valor_transferido, 0)

    lotes.at[idx, "valor_bruto_remanescente_centavos"] = bruto_depois
    lotes.at[idx, "valor_saldo_centavos"] = bruto_depois
    lotes.at[idx, "valor_economico_centavos"] = bruto_depois
    lotes.at[idx, "valor_principal_remanescente_centavos"] = min(principal_depois, bruto_depois)
    lotes.at[idx, "valor_liquido_resgatavel_centavos"] = liquido_depois
    lotes.at[idx, "data_ultima_atualizacao"] = data
    if bruto_depois <= 0:
        lotes.at[idx, "status_lote"] = "ENCERRADO"

    carteira_destino = obter_carteira_por_id(estado.carteiras, str(candidato["id_carteira_destino"]))
    if carteira_destino is None:
        raise ValueError("Carteira de destino não encontrada para switching.")
    lote_destino = _criar_lote_destino_switching(
        lote_origem=lote_origem,
        carteira_destino=carteira_destino,
        data_switching=data,
        valor_transferido_centavos=valor_transferido,
        suffix=f"{data.strftime('%Y%m%d')}_{idx}",
        colunas_base=list(lotes.columns),
    )
    lotes = pd.concat([lotes, pd.DataFrame([lote_destino])], ignore_index=True)

    evento = {
        "data_switching": data,
        "id_lote_origem": id_lote,
        "id_lote_destino": str(lote_destino["id_lote"]),
        "id_carteira_origem": str(candidato["id_carteira_origem"]),
        "id_carteira_destino": str(candidato["id_carteira_destino"]),
        "carteira_destino": str(candidato["carteira_destino"]),
        "valor_switching_centavos": int(valor_transferido),
        "tipo_switching": str(candidato["tipo_switching"]),
    }
    return lotes, evento



def avaliar_melhor_estrategia_no_dia(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    deficit_centavos: int,
    lotes_dia: pd.DataFrame,
    caixa_sem_acao_centavos: int,
    top_k_switch: int = 1,
) -> dict[str, Any]:
    """Escolhe entre política base de resgates e switching prévio + resgates no mesmo dia.

    Nesta versão endurecida, a comparação deixa de ser apenas local ao dia crítico.
    Depois de cobrir o déficit do dia, cada estratégia é reavaliada no restante do
    horizonte usando a política atual de resgates. O switching só é aceito quando
    melhora a riqueza terminal do horizonte remanescente ou, em empate econômico,
    simplifica a trajetória futura.
    """
    base = selecionar_resgates_para_deficit(
        estado=estado,
        data_critica=data_critica,
        deficit_centavos=deficit_centavos,
        lotes_base=lotes_dia,
    )
    if not base.cobertura_total:
        return {
            "estrategia": "SEM_COBERTURA",
            "ganho_vs_base_centavos": 0,
            "lotes_resultantes": base.lotes_atualizados.copy(),
            "caixa_depois_centavos": int(caixa_sem_acao_centavos + (base.selecoes["valor_resgatado_centavos"].sum() if not base.selecoes.empty else 0)),
            "resgates": base.selecoes.copy(),
            "switch_event": None,
            "observacao": "Nem a política base conseguiu cobrir o déficit no dia.",
            "riqueza_terminal_centavos": None,
            "riqueza_terminal_base_centavos": None,
        }

    caixa_base_depois = int(caixa_sem_acao_centavos + (base.selecoes["valor_resgatado_centavos"].sum() if not base.selecoes.empty else 0))
    saldo_base_pos_dia = _saldo_investido_liquido(base.lotes_atualizados)
    futuro_base = _simular_futuro_com_resgates(
        estado=estado,
        lotes_inicio=base.lotes_atualizados,
        caixa_inicial_centavos=caixa_base_depois,
        data_inicio_exclusiva=data_critica,
    )
    riqueza_base_terminal = int(futuro_base["caixa_final_centavos"] + futuro_base["saldo_investido_liquido_final_centavos"])

    melhor = {
        "estrategia": "RESGATE_BASE",
        "ganho_vs_base_centavos": 0,
        "lotes_resultantes": base.lotes_atualizados.copy(),
        "caixa_depois_centavos": caixa_base_depois,
        "resgates": base.selecoes.copy(),
        "switch_event": None,
        "saldo_pos_dia_centavos": saldo_base_pos_dia,
        "observacao": "A política base de resgates permaneceu dominante na avaliação intertemporal do horizonte remanescente.",
        "riqueza_terminal_centavos": riqueza_base_terminal,
        "riqueza_terminal_base_centavos": riqueza_base_terminal,
    }

    ids_origem_prioritarios = set(base.selecoes["id_lote"].astype(str)) if not base.selecoes.empty else set()
    lotes_origem = lotes_dia.loc[lotes_dia["id_lote"].astype(str).isin(ids_origem_prioritarios)].copy()
    if lotes_origem.empty:
        lotes_origem = lotes_dia.copy()

    candidatos = gerar_candidatos_switching_por_data(
        estado=estado,
        data_critica=data_critica,
        deficit_centavos=deficit_centavos,
        lotes_base=lotes_origem,
        limitar_destinos_por_lote=max(top_k_switch, 1),
    )
    if candidatos.empty:
        return melhor

    candidatos = candidatos.loc[
        (candidatos["melhor_acao"] == "SWITCHAR") & (candidatos["score_switching_vs_resgate_centavos"] > 0)
    ].copy()
    if candidatos.empty:
        return melhor

    candidatos = candidatos.sort_values(
        ["score_switching_vs_resgate_centavos", "score_ranking_switching_centavos", "ranking_candidato"],
        ascending=[False, False, True],
    ).head(top_k_switch)

    melhor_ganho = 0
    for _, cand in candidatos.iterrows():
        try:
            lotes_pos_switch, switch_event = aplicar_switching_candidato(estado, lotes_dia, cand)
        except Exception:
            continue

        resg_pos_switch = selecionar_resgates_para_deficit(
            estado=estado,
            data_critica=data_critica,
            deficit_centavos=deficit_centavos,
            lotes_base=lotes_pos_switch,
        )
        if not resg_pos_switch.cobertura_total:
            continue

        caixa_dia = int(caixa_sem_acao_centavos + (resg_pos_switch.selecoes["valor_resgatado_centavos"].sum() if not resg_pos_switch.selecoes.empty else 0))
        saldo_switch_pos_dia = _saldo_investido_liquido(resg_pos_switch.lotes_atualizados)
        futuro_switch = _simular_futuro_com_resgates(
            estado=estado,
            lotes_inicio=resg_pos_switch.lotes_atualizados,
            caixa_inicial_centavos=caixa_dia,
            data_inicio_exclusiva=data_critica,
        )
        if not futuro_switch["viavel"]:
            continue

        riqueza_switch_terminal = int(futuro_switch["caixa_final_centavos"] + futuro_switch["saldo_investido_liquido_final_centavos"])
        ganho_intertemporal = int(riqueza_switch_terminal - riqueza_base_terminal)
        delta_eventos_futuros = int(futuro_base["eventos_resgate"] - futuro_switch["eventos_resgate"])
        delta_custo_futuro = int(futuro_base["total_custo_oportunidade_centavos"] - futuro_switch["total_custo_oportunidade_centavos"])

        aceitar = False
        if ganho_intertemporal > melhor_ganho:
            aceitar = True
        elif ganho_intertemporal == melhor_ganho and ganho_intertemporal > 0:
            evento_switch_total = int(len(resg_pos_switch.selecoes)) + int(futuro_switch["eventos_resgate"])
            evento_base_total = int(len(base.selecoes)) + int(futuro_base["eventos_resgate"])
            aceitar = evento_switch_total < evento_base_total

        if aceitar:
            melhor_ganho = ganho_intertemporal
            melhor = {
                "estrategia": "SWITCH_E_RESGATE",
                "ganho_vs_base_centavos": int(ganho_intertemporal),
                "lotes_resultantes": resg_pos_switch.lotes_atualizados.copy(),
                "caixa_depois_centavos": caixa_dia,
                "resgates": resg_pos_switch.selecoes.copy(),
                "switch_event": {
                    **switch_event,
                    "ganho_vs_base_centavos": int(ganho_intertemporal),
                    "motivo": "Switching aplicado antes dos resgates do dia melhorou a riqueza terminal do horizonte remanescente após reavaliar as datas futuras críticas.",
                    "riqueza_terminal_base_centavos": int(riqueza_base_terminal),
                    "riqueza_terminal_switch_centavos": int(riqueza_switch_terminal),
                    "delta_eventos_resgate_futuros": int(delta_eventos_futuros),
                    "delta_custo_oportunidade_futuro_centavos": int(delta_custo_futuro),
                },
                "saldo_pos_dia_centavos": saldo_switch_pos_dia,
                "observacao": "Switching integrado à política do dia crítico por melhorar a riqueza terminal do restante do horizonte, e não apenas o saldo remanescente do próprio dia.",
                "riqueza_terminal_centavos": riqueza_switch_terminal,
                "riqueza_terminal_base_centavos": riqueza_base_terminal,
            }

    return melhor




@dataclass
class ResultadoSensibilidadeTopKSwitching:
    resumo: dict[str, Any]
    sensibilidade: pd.DataFrame
    melhor_timeline: pd.DataFrame
    melhor_switchings: pd.DataFrame
    melhor_resgates: pd.DataFrame


def diagnosticar_sensibilidade_top_k_switching(
    estado: EstadoSistema,
    top_ks: tuple[int, ...] = (1, 2, 3),
) -> ResultadoSensibilidadeTopKSwitching:
    ks_validos = tuple(sorted({int(k) for k in top_ks if int(k) >= 1}))
    if not ks_validos:
        ks_validos = (1,)

    linhas: list[dict[str, Any]] = []
    resultados: dict[int, ResultadoPoliticaConjuntaSwitching] = {}
    base_tempo = None
    base_ganho = None
    base_riqueza = None

    for k in ks_validos:
        t0 = perf_counter()
        resultado = diagnosticar_politica_conjunta_switching(estado, top_k_switch_por_data=k)
        tempo = perf_counter() - t0
        resultados[int(k)] = resultado

        riqueza = int(resultado.resumo["riqueza_final_politica_conjunta_centavos"])
        ganho = int(resultado.resumo["ganho_total_vs_politica_base_centavos"])
        if base_tempo is None:
            base_tempo = tempo
            base_ganho = ganho
            base_riqueza = riqueza
        ganho_marginal = int(ganho - base_ganho)
        riqueza_marginal = int(riqueza - base_riqueza)
        tempo_extra = float(tempo - base_tempo)
        eficiencia = None if tempo_extra <= 0 or ganho_marginal == 0 else float(ganho_marginal / tempo_extra)

        linhas.append({
            "top_k_switch_por_data": int(k),
            "tempo_execucao_segundos": float(round(tempo, 6)),
            "riqueza_final_centavos": int(riqueza),
            "ganho_vs_politica_base_centavos": int(ganho),
            "qtd_switchings": int(resultado.resumo["qtd_eventos_switching"]),
            "qtd_datas_com_switching": int(resultado.resumo["qtd_datas_com_switching_escolhido"]),
            "qtd_resgates": int(resultado.resumo["qtd_eventos_resgate"]),
            "cobertura_total_viavel": bool(resultado.resumo["cobertura_total_viavel"]),
            "ganho_marginal_vs_k1_centavos": int(ganho_marginal),
            "riqueza_marginal_vs_k1_centavos": int(riqueza_marginal),
            "tempo_extra_vs_k1_segundos": float(round(tempo_extra, 6)),
            "eficiencia_marginal_centavos_por_segundo": None if eficiencia is None else float(round(eficiencia, 6)),
        })

    sens = pd.DataFrame(linhas).sort_values("top_k_switch_por_data").reset_index(drop=True)
    melhor_riqueza = int(sens["riqueza_final_centavos"].max())
    candidatos = sens.loc[sens["riqueza_final_centavos"] == melhor_riqueza].copy()
    recomendado = int(candidatos.sort_values(["tempo_execucao_segundos", "top_k_switch_por_data"], ascending=[True, True]).iloc[0]["top_k_switch_por_data"])
    resultado_recomendado = resultados[recomendado]
    resumo = {
        "politica_sensibilidade": "top_k_switch_por_data",
        "ks_testados": [int(k) for k in ks_validos],
        "top_k_recomendado": int(recomendado),
        "criterio_recomendacao": "maior riqueza final; em empate, menor tempo de execução",
        "melhor_riqueza_final_centavos": int(melhor_riqueza),
        "ganho_recomendado_vs_politica_base_centavos": int(sens.loc[sens["top_k_switch_por_data"] == recomendado, "ganho_vs_politica_base_centavos"].iloc[0]),
        "tempo_execucao_recomendado_segundos": float(sens.loc[sens["top_k_switch_por_data"] == recomendado, "tempo_execucao_segundos"].iloc[0]),
        "ganho_marginal_recomendado_vs_k1_centavos": int(sens.loc[sens["top_k_switch_por_data"] == recomendado, "ganho_marginal_vs_k1_centavos"].iloc[0]),
        "tempo_extra_recomendado_vs_k1_segundos": float(sens.loc[sens["top_k_switch_por_data"] == recomendado, "tempo_extra_vs_k1_segundos"].iloc[0]),
    }
    return ResultadoSensibilidadeTopKSwitching(
        resumo=resumo,
        sensibilidade=sens,
        melhor_timeline=resultado_recomendado.timeline,
        melhor_switchings=resultado_recomendado.switchings,
        melhor_resgates=resultado_recomendado.resgates,
    )

def diagnosticar_politica_conjunta_switching(
    estado: EstadoSistema,
    top_k_switch_por_data: int = 1,
) -> ResultadoPoliticaConjuntaSwitching:
    base_diag = diagnosticar_pagamentos_futuros(estado)
    gastos_por_data, recebidos_por_data = _maps_fluxo(estado)
    datas = [pd.Timestamp(d).normalize() for d in _datas_evento(estado)]

    lotes_diag = estado.lotes.copy()
    caixa = int(estado.caixa_livre_centavos)
    timeline_rows: list[dict[str, Any]] = []
    resgates_rows: list[dict[str, Any]] = []
    switch_rows: list[dict[str, Any]] = []

    for data in datas:
        caixa_antes = int(caixa)
        recebidos = int(recebidos_por_data.get(data, 0))
        gastos = int(gastos_por_data.get(data, 0))
        caixa_sem_acao = caixa + recebidos - gastos
        deficit = max(-caixa_sem_acao, 0)

        estrategia = "SEM_ACAO"
        observacao = "Cobertura integral sem necessidade de ação."
        ganho = 0
        valor_switch = 0
        id_lote_switch = ""
        id_carteira_dest = ""
        carteira_dest = ""
        qtd_eventos_resgate = 0
        resgates_total = 0
        switch_realizado = False

        if deficit > 0:
            lotes_dia = atualizar_lotes_investidos_ate_data(lotes_diag, data, estado)
            escolha = avaliar_melhor_estrategia_no_dia(
                estado=estado,
                data_critica=data,
                deficit_centavos=deficit,
                lotes_dia=lotes_dia,
                caixa_sem_acao_centavos=caixa_sem_acao,
                top_k_switch=top_k_switch_por_data,
            )
            estrategia = str(escolha["estrategia"])
            observacao = str(escolha["observacao"])
            ganho = int(escolha["ganho_vs_base_centavos"])
            lotes_diag = escolha["lotes_resultantes"].copy()
            caixa = int(escolha["caixa_depois_centavos"])
            if not escolha["resgates"].empty:
                qtd_eventos_resgate = int(len(escolha["resgates"]))
                resgates_total = int(escolha["resgates"]["valor_resgatado_centavos"].sum())
                resgates_rows.extend(escolha["resgates"].to_dict(orient="records"))
            if escolha["switch_event"] is not None:
                switch_realizado = True
                valor_switch = int(escolha["switch_event"]["valor_switching_centavos"])
                id_lote_switch = str(escolha["switch_event"]["id_lote_origem"])
                id_carteira_dest = str(escolha["switch_event"]["id_carteira_destino"])
                carteira_dest = str(escolha["switch_event"]["carteira_destino"])
                switch_rows.append(escolha["switch_event"])
        else:
            caixa = int(caixa_sem_acao)

        timeline_rows.append(
            {
                "data": data,
                "caixa_antes_centavos": int(caixa_antes),
                "recebidos_livres_centavos": int(recebidos),
                "gastos_futuros_centavos": int(gastos),
                "deficit_sem_acao_centavos": int(deficit),
                "estrategia_escolhida": estrategia,
                "switching_realizado": bool(switch_realizado),
                "id_lote_origem_switching": id_lote_switch,
                "id_carteira_destino_switching": id_carteira_dest,
                "carteira_destino_switching": carteira_dest,
                "valor_switching_centavos": int(valor_switch),
                "resgates_realizados_centavos": int(resgates_total),
                "qtd_eventos_resgate": int(qtd_eventos_resgate),
                "caixa_depois_centavos": int(caixa),
                "saldo_investido_liquido_pos_dia_centavos": _saldo_investido_liquido(lotes_diag),
                "ganho_vs_base_centavos": int(ganho),
                "observacao": observacao,
            }
        )

    timeline = pd.DataFrame(timeline_rows, columns=POLITICA_TIMELINE_COLUMNS)
    switch_df = pd.DataFrame(switch_rows, columns=SWITCH_EVENTS_COLUMNS)
    resgates_df = pd.DataFrame(resgates_rows)

    riqueza_final = int((timeline.iloc[-1]["caixa_depois_centavos"] if not timeline.empty else estado.caixa_livre_centavos) + _saldo_investido_liquido(lotes_diag))
    riqueza_final_base = int(base_diag.resumo["saldo_final_com_resgates_centavos"] + base_diag.resumo["lotes_investidos_liquidos_remanescentes_centavos"])

    resumo = {
        "politica": "intertemporal_com_switching_previo_e_reavaliacao_do_horizonte",
        "top_k_switch_por_data": int(top_k_switch_por_data),
        "data_corte_modelo": str(estado.data_corte_modelo.date()),
        "data_referencia": str(estado.data_referencia.date()),
        "horizonte_final": str(estado.horizonte_final.date()),
        "qtd_datas_com_deficit": int((timeline["deficit_sem_acao_centavos"] > 0).sum()) if not timeline.empty else 0,
        "qtd_datas_com_switching_escolhido": int(timeline["switching_realizado"].sum()) if not timeline.empty else 0,
        "qtd_eventos_switching": int(len(switch_df)),
        "qtd_eventos_resgate": int(len(resgates_df)),
        "saldo_final_caixa_centavos": int(timeline.iloc[-1]["caixa_depois_centavos"]) if not timeline.empty else int(estado.caixa_livre_centavos),
        "saldo_final_investido_liquido_centavos": _saldo_investido_liquido(lotes_diag),
        "riqueza_final_politica_conjunta_centavos": int(riqueza_final),
        "riqueza_final_politica_base_centavos": int(riqueza_final_base),
        "ganho_total_vs_politica_base_centavos": int(riqueza_final - riqueza_final_base),
        "cobertura_total_viavel": bool((timeline.iloc[-1]["caixa_depois_centavos"] if not timeline.empty else estado.caixa_livre_centavos) >= 0),
    }

    comparacao_base = {
        "politica_base": base_diag.resumo.get("politica_resgate"),
        "riqueza_final_base_centavos": int(riqueza_final_base),
        "qtd_datas_com_resgate_base": int(base_diag.resumo.get("qtd_datas_com_resgate", 0)),
        "qtd_eventos_resgate_base": int(base_diag.resumo.get("qtd_eventos_resgate", 0)),
    }

    return ResultadoPoliticaConjuntaSwitching(
        resumo=resumo,
        timeline=timeline,
        switchings=switch_df,
        resgates=resgates_df,
        comparacao_base=comparacao_base,
    )
