from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from estado import EstadoSistema
from motor_precificacao import (
    calcular_valor_liquido_lote_bruto,
    precificar_lote_investido_na_data,
    projetar_saldo_bruto_lote_ate_data,
)


CANDIDATOS_RESGATE_COLUMNS = [
    "data",
    "ranking_candidato",
    "id_lote",
    "id_carteira",
    "carteira",
    "valor_liquido_atual_centavos",
    "valor_bruto_atual_centavos",
    "valor_principal_atual_centavos",
    "valor_resgate_planejado_centavos",
    "valor_terminal_se_mantido_centavos",
    "valor_terminal_apos_resgate_centavos",
    "custo_oportunidade_centavos",
    "custo_oportunidade_por_real_resgatado",
    "custo_complemento_mesmo_dia_centavos",
    "penalidade_preservacao_futura_centavos",
    "penalidade_essencialidade_futura_centavos",
    "cobertura_futura_viavel",
    "saldo_investido_liquido_final_centavos",
    "score_intertemporal_centavos",
    "score_intertemporal_por_real_resgatado",
    "suficiente_para_cobrir_sozinho",
]


SELECOES_RESGATE_COLUMNS = [
    "data",
    "ordem_resgate_no_dia",
    "ranking_candidato",
    "id_lote",
    "id_carteira",
    "carteira",
    "valor_resgatado_centavos",
    "valor_liquido_antes_centavos",
    "valor_liquido_depois_centavos",
    "valor_bruto_antes_centavos",
    "valor_bruto_depois_centavos",
    "principal_antes_centavos",
    "principal_depois_centavos",
    "foi_resgate_total",
    "valor_terminal_se_mantido_centavos",
    "valor_terminal_apos_resgate_centavos",
    "custo_oportunidade_centavos",
    "custo_oportunidade_por_real_resgatado",
    "custo_complemento_mesmo_dia_centavos",
    "penalidade_preservacao_futura_centavos",
    "penalidade_essencialidade_futura_centavos",
    "cobertura_futura_viavel",
    "saldo_investido_liquido_final_centavos",
    "score_intertemporal_centavos",
    "score_intertemporal_por_real_resgatado",
]


LOOKAHEAD_MAX_DATAS = 5
ESSENCIALIDADE_PENALTY_MULTIPLIER = 10


@dataclass
class ResultadoSelecaoResgates:
    selecoes: pd.DataFrame
    candidatos_ordenados: pd.DataFrame
    lotes_atualizados: pd.DataFrame
    deficit_inicial_centavos: int
    deficit_final_centavos: int
    cobertura_total: bool


@dataclass
class AvaliacaoResgateLote:
    lote_atualizado_data: pd.Series
    lote_pos_resgate: pd.Series
    valor_resgate_centavos: int
    valor_terminal_se_mantido_centavos: int
    valor_terminal_apos_resgate_centavos: int
    custo_oportunidade_centavos: int
    custo_oportunidade_por_real_resgatado: float
    info_resgate: dict[str, Any]


@dataclass
class AvaliacaoIntertemporalResgate:
    avaliacao_base: AvaliacaoResgateLote
    custo_complemento_mesmo_dia_centavos: int
    penalidade_preservacao_futura_centavos: int
    penalidade_essencialidade_futura_centavos: int
    cobertura_futura_viavel: bool
    saldo_investido_liquido_final_centavos: int
    score_intertemporal_centavos: int
    score_intertemporal_por_real_resgatado: float



def _carteira_map(estado: EstadoSistema) -> dict[str, pd.Series]:
    cache = getattr(estado, "_cache_carteira_map", None)
    if cache is None:
        cache = {str(row["id_carteira"]): row for _, row in estado.carteiras.iterrows()}
        setattr(estado, "_cache_carteira_map", cache)
    return cache



def _fluxos_futuros_maps(estado: EstadoSistema) -> tuple[dict[pd.Timestamp, int], dict[pd.Timestamp, int]]:
    cache = getattr(estado, "_cache_fluxos_futuros_maps", None)
    if cache is None:
        gastos_por_data = (
            estado.gastos_futuros.groupby("data_gasto", dropna=True)["valor_gasto_centavos"].sum().to_dict()
        )
        recebidos_por_data = (
            estado.lotes_futuros.loc[estado.lotes_futuros["status_lote"] == "LIVRE_FUTURO"]
            .groupby("data_entrada_lote", dropna=True)["valor_saldo_centavos"]
            .sum()
            .to_dict()
        )
        cache = (gastos_por_data, recebidos_por_data)
        setattr(estado, "_cache_fluxos_futuros_maps", cache)
    return cache



def _datas_evento_posteriores(estado: EstadoSistema, data_exclusiva: pd.Timestamp) -> list[pd.Timestamp]:
    data_exclusiva = pd.Timestamp(data_exclusiva).normalize()
    cache = getattr(estado, "_cache_datas_evento_ordenadas", None)
    if cache is None:
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
        cache = sorted(datas_gastos.union(datas_lotes))
        setattr(estado, "_cache_datas_evento_ordenadas", cache)
    return [d for d in cache if d > data_exclusiva]



def _saldo_investido_liquido(lotes: pd.DataFrame) -> int:
    mask = lotes["status_lote"] == "INVESTIDO_ATUAL"
    if mask.sum() == 0:
        return 0
    return int(lotes.loc[mask, "valor_liquido_resgatavel_centavos"].sum())



def _carteira_do_lote(lote: pd.Series, estado: EstadoSistema) -> pd.Series | None:
    return _carteira_map(estado).get(str(lote["id_carteira_atual"]).strip())



def _precificar_liquido_lote_em_data(lote: pd.Series, data_alvo: pd.Timestamp, estado: EstadoSistema) -> int:
    carteira = _carteira_do_lote(lote, estado)
    if carteira is None:
        return 0
    if str(lote["status_lote"]) != "INVESTIDO_ATUAL":
        return 0
    bruto = int(lote.get("valor_bruto_remanescente_centavos", 0))
    if bruto <= 0:
        return 0
    data_alvo = pd.Timestamp(data_alvo).normalize()
    cache = getattr(estado, "_cache_precificar_liquido", None)
    if cache is None:
        cache = {}
        setattr(estado, "_cache_precificar_liquido", cache)
    key = (
        str(lote.get("id_lote", "")),
        str(lote.get("id_carteira_atual", "")),
        data_alvo,
        bruto,
        int(lote.get("valor_principal_remanescente_centavos", 0)),
    )
    if key in cache:
        return int(cache[key])
    resultado = precificar_lote_investido_na_data(
        lote=lote,
        carteira=carteira,
        data_referencia=data_alvo,
        config=estado.config,
    )
    cache[key] = int(resultado.valor_liquido_centavos)
    return int(cache[key])



def _timeline_deficits_futuros_a_partir_de_data(
    estado: EstadoSistema,
    data_exclusiva: pd.Timestamp,
    caixa_inicial_centavos: int = 0,
) -> list[tuple[pd.Timestamp, int]]:
    gastos_por_data, recebidos_por_data = _fluxos_futuros_maps(estado)
    datas = _datas_evento_posteriores(estado, data_exclusiva)
    caixa = int(caixa_inicial_centavos)
    deficits: list[tuple[pd.Timestamp, int]] = []

    for data in datas:
        data = pd.Timestamp(data).normalize()
        caixa += int(recebidos_por_data.get(data, 0))
        caixa -= int(gastos_por_data.get(data, 0))
        deficit = max(-caixa, 0)
        if deficit > 0:
            deficits.append((data, int(deficit)))
    return deficits[:LOOKAHEAD_MAX_DATAS]



def _liquidez_total_pool_por_data(
    lotes_base: pd.DataFrame,
    datas: list[pd.Timestamp],
    estado: EstadoSistema,
) -> dict[pd.Timestamp, int]:
    out: dict[pd.Timestamp, int] = {}
    investidos = lotes_base.loc[lotes_base["status_lote"] == "INVESTIDO_ATUAL"].copy()
    if investidos.empty:
        return {pd.Timestamp(d).normalize(): 0 for d in datas}

    for data in datas:
        data = pd.Timestamp(data).normalize()
        total = 0
        for _, lote in investidos.iterrows():
            total += _precificar_liquido_lote_em_data(lote, data, estado)
        out[data] = int(total)
    return out



def atualizar_lotes_investidos_ate_data(
    lotes: pd.DataFrame,
    data_alvo: pd.Timestamp,
    estado: EstadoSistema,
) -> pd.DataFrame:
    out = lotes.copy()
    carteiras = _carteira_map(estado)
    data_alvo = pd.Timestamp(data_alvo).normalize()

    mask = out["status_lote"] == "INVESTIDO_ATUAL"
    for idx, lote in out.loc[mask].iterrows():
        data_ultima = pd.Timestamp(lote["data_ultima_atualizacao"]).normalize()
        if data_alvo <= data_ultima:
            continue

        carteira_id = str(lote["id_carteira_atual"]).strip()
        carteira = carteiras.get(carteira_id)
        if carteira is None:
            continue

        bruto_atualizado = projetar_saldo_bruto_lote_ate_data(
            valor_bruto_atual_centavos=int(lote["valor_bruto_remanescente_centavos"]),
            carteira=carteira,
            data_inicio=data_ultima,
            data_fim=data_alvo,
            config=estado.config,
        )
        valor_liquido, ir, iof, custo = calcular_valor_liquido_lote_bruto(
            valor_principal_centavos=int(lote["valor_principal_remanescente_centavos"]),
            valor_bruto_centavos=bruto_atualizado,
            data_entrada_original=pd.Timestamp(lote["data_entrada_lote"]).normalize(),
            data_referencia=data_alvo,
            carteira=carteira,
            config=estado.config,
        )
        out.at[idx, "valor_bruto_remanescente_centavos"] = int(bruto_atualizado)
        out.at[idx, "valor_saldo_centavos"] = int(bruto_atualizado)
        out.at[idx, "valor_economico_centavos"] = int(bruto_atualizado)
        out.at[idx, "valor_liquido_resgatavel_centavos"] = int(valor_liquido)
        out.at[idx, "data_ultima_atualizacao"] = data_alvo
        out.at[idx, "ultimo_ir_estimado_centavos"] = int(ir)
        out.at[idx, "ultimo_iof_estimado_centavos"] = int(iof)
        out.at[idx, "ultimo_custo_estimado_centavos"] = int(custo)

    return out


def atualizar_lote_investido_ate_data(
    lote: pd.Series,
    data_alvo: pd.Timestamp,
    estado: EstadoSistema,
) -> pd.Series:
    out = lote.copy()
    if str(out.get("status_lote", "")) != "INVESTIDO_ATUAL":
        return out
    data_alvo = pd.Timestamp(data_alvo).normalize()
    data_ultima = pd.Timestamp(out["data_ultima_atualizacao"]).normalize()
    if data_alvo <= data_ultima:
        return out

    carteira_id = str(out["id_carteira_atual"]).strip()
    carteira = _carteira_map(estado).get(carteira_id)
    if carteira is None:
        return out

    bruto_atualizado = projetar_saldo_bruto_lote_ate_data(
        valor_bruto_atual_centavos=int(out["valor_bruto_remanescente_centavos"]),
        carteira=carteira,
        data_inicio=data_ultima,
        data_fim=data_alvo,
        config=estado.config,
    )
    valor_liquido, ir, iof, custo = calcular_valor_liquido_lote_bruto(
        valor_principal_centavos=int(out["valor_principal_remanescente_centavos"]),
        valor_bruto_centavos=bruto_atualizado,
        data_entrada_original=pd.Timestamp(out["data_entrada_lote"]).normalize(),
        data_referencia=data_alvo,
        carteira=carteira,
        config=estado.config,
    )
    out["valor_bruto_remanescente_centavos"] = int(bruto_atualizado)
    out["valor_saldo_centavos"] = int(bruto_atualizado)
    out["valor_economico_centavos"] = int(bruto_atualizado)
    out["valor_liquido_resgatavel_centavos"] = int(valor_liquido)
    out["data_ultima_atualizacao"] = data_alvo
    out["ultimo_ir_estimado_centavos"] = int(ir)
    out["ultimo_iof_estimado_centavos"] = int(iof)
    out["ultimo_custo_estimado_centavos"] = int(custo)
    return out


def aplicar_resgate_liquido_proporcional(
    lote: pd.Series,
    valor_resgate_centavos: int,
) -> tuple[pd.Series, dict[str, Any]]:
    out = lote.copy()

    liquido_antes = int(out["valor_liquido_resgatavel_centavos"])
    bruto_antes = int(out["valor_bruto_remanescente_centavos"])
    principal_antes = int(out["valor_principal_remanescente_centavos"])

    valor_resgate = min(max(int(valor_resgate_centavos), 0), liquido_antes)
    if liquido_antes <= 0 or valor_resgate <= 0:
        return out, {
            "valor_resgatado_centavos": 0,
            "valor_liquido_antes_centavos": liquido_antes,
            "valor_liquido_depois_centavos": liquido_antes,
            "valor_bruto_antes_centavos": bruto_antes,
            "valor_bruto_depois_centavos": bruto_antes,
            "principal_antes_centavos": principal_antes,
            "principal_depois_centavos": principal_antes,
            "foi_resgate_total": False,
        }

    fracao = min(valor_resgate / liquido_antes, 1.0)
    bruto_depois = max(int(round(bruto_antes * (1.0 - fracao))), 0)
    principal_depois = max(int(round(principal_antes * (1.0 - fracao))), 0)
    liquido_depois = max(liquido_antes - valor_resgate, 0)

    out["valor_bruto_remanescente_centavos"] = bruto_depois
    out["valor_saldo_centavos"] = bruto_depois
    out["valor_economico_centavos"] = bruto_depois
    out["valor_principal_remanescente_centavos"] = min(principal_depois, bruto_depois)
    out["valor_liquido_resgatavel_centavos"] = liquido_depois
    if bruto_depois <= 0:
        out["status_lote"] = "ENCERRADO"

    return out, {
        "valor_resgatado_centavos": valor_resgate,
        "valor_liquido_antes_centavos": liquido_antes,
        "valor_liquido_depois_centavos": liquido_depois,
        "valor_bruto_antes_centavos": bruto_antes,
        "valor_bruto_depois_centavos": bruto_depois,
        "principal_antes_centavos": principal_antes,
        "principal_depois_centavos": int(out["valor_principal_remanescente_centavos"]),
        "foi_resgate_total": bruto_depois <= 0,
    }



def avaliar_candidato_resgate(
    lote: pd.Series,
    data_critica: pd.Timestamp,
    valor_necessario_centavos: int,
    estado: EstadoSistema,
    lote_ja_atualizado: bool = False,
) -> AvaliacaoResgateLote | None:
    if str(lote["status_lote"]) != "INVESTIDO_ATUAL":
        return None

    valor_liquido_atual = int(lote["valor_liquido_resgatavel_centavos"])
    if valor_liquido_atual <= 0:
        return None

    carteira = _carteira_do_lote(lote, estado)
    if carteira is None:
        return None

    lote_atualizado = lote.copy() if lote_ja_atualizado else atualizar_lote_investido_ate_data(lote, data_critica, estado)

    valor_resgate = min(int(valor_necessario_centavos), int(lote_atualizado["valor_liquido_resgatavel_centavos"]))
    if valor_resgate <= 0:
        return None

    resultado_manter = precificar_lote_investido_na_data(
        lote=lote_atualizado,
        carteira=carteira,
        data_referencia=estado.horizonte_final,
        config=estado.config,
    )

    lote_pos_resgate, info = aplicar_resgate_liquido_proporcional(lote_atualizado, valor_resgate)
    if str(lote_pos_resgate["status_lote"]) == "INVESTIDO_ATUAL" and int(lote_pos_resgate["valor_bruto_remanescente_centavos"]) > 0:
        resultado_apos = precificar_lote_investido_na_data(
            lote=lote_pos_resgate,
            carteira=carteira,
            data_referencia=estado.horizonte_final,
            config=estado.config,
        )
        valor_terminal_apos = int(resultado_apos.valor_liquido_centavos)
    else:
        valor_terminal_apos = 0

    valor_terminal_manter = int(resultado_manter.valor_liquido_centavos)
    custo_oportunidade = max(valor_terminal_manter - valor_terminal_apos, 0)
    custo_por_real = custo_oportunidade / valor_resgate if valor_resgate > 0 else float("inf")

    return AvaliacaoResgateLote(
        lote_atualizado_data=lote_atualizado,
        lote_pos_resgate=lote_pos_resgate,
        valor_resgate_centavos=valor_resgate,
        valor_terminal_se_mantido_centavos=valor_terminal_manter,
        valor_terminal_apos_resgate_centavos=valor_terminal_apos,
        custo_oportunidade_centavos=custo_oportunidade,
        custo_oportunidade_por_real_resgatado=custo_por_real,
        info_resgate=info,
    )



def gerar_candidatos_resgate_por_data_local(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    valor_necessario_centavos: int,
    lotes_base: pd.DataFrame | None = None,
) -> pd.DataFrame:
    data_critica = pd.Timestamp(data_critica).normalize()
    lotes_ref = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    lotes_ref = atualizar_lotes_investidos_ate_data(lotes_ref, data_critica, estado)

    rows: list[dict[str, Any]] = []
    for _, lote in lotes_ref.iterrows():
        avaliacao = avaliar_candidato_resgate(
            lote=lote,
            data_critica=data_critica,
            valor_necessario_centavos=valor_necessario_centavos,
            estado=estado,
            lote_ja_atualizado=True,
        )
        if avaliacao is None:
            continue
        rows.append(
            {
                "data": data_critica,
                "ranking_candidato": 0,
                "id_lote": str(lote["id_lote"]),
                "id_carteira": str(lote["id_carteira_atual"]),
                "carteira": str(lote["carteira_atual"]),
                "valor_liquido_atual_centavos": int(avaliacao.info_resgate["valor_liquido_antes_centavos"]),
                "valor_bruto_atual_centavos": int(avaliacao.info_resgate["valor_bruto_antes_centavos"]),
                "valor_principal_atual_centavos": int(avaliacao.info_resgate["principal_antes_centavos"]),
                "valor_resgate_planejado_centavos": int(avaliacao.valor_resgate_centavos),
                "valor_terminal_se_mantido_centavos": int(avaliacao.valor_terminal_se_mantido_centavos),
                "valor_terminal_apos_resgate_centavos": int(avaliacao.valor_terminal_apos_resgate_centavos),
                "custo_oportunidade_centavos": int(avaliacao.custo_oportunidade_centavos),
                "custo_oportunidade_por_real_resgatado": float(avaliacao.custo_oportunidade_por_real_resgatado),
                "custo_complemento_mesmo_dia_centavos": 0,
                "penalidade_preservacao_futura_centavos": 0,
                "penalidade_essencialidade_futura_centavos": 0,
                "cobertura_futura_viavel": True,
                "saldo_investido_liquido_final_centavos": int(avaliacao.valor_terminal_apos_resgate_centavos),
                "score_intertemporal_centavos": int(avaliacao.custo_oportunidade_centavos),
                "score_intertemporal_por_real_resgatado": float(avaliacao.custo_oportunidade_por_real_resgatado),
                "suficiente_para_cobrir_sozinho": bool(int(avaliacao.info_resgate["valor_liquido_antes_centavos"]) >= int(valor_necessario_centavos)),
            }
        )

    candidatos = pd.DataFrame(rows, columns=CANDIDATOS_RESGATE_COLUMNS)
    if candidatos.empty:
        return candidatos

    candidatos = candidatos.sort_values(
        [
            "custo_oportunidade_por_real_resgatado",
            "custo_oportunidade_centavos",
            "suficiente_para_cobrir_sozinho",
            "valor_liquido_atual_centavos",
            "id_lote",
        ],
        ascending=[True, True, False, False, True],
    ).reset_index(drop=True)
    candidatos["ranking_candidato"] = candidatos.index + 1
    return candidatos[CANDIDATOS_RESGATE_COLUMNS]



def selecionar_resgates_para_deficit_local(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    deficit_centavos: int,
    lotes_base: pd.DataFrame | None = None,
) -> ResultadoSelecaoResgates:
    data_critica = pd.Timestamp(data_critica).normalize()
    deficit_restante = max(int(deficit_centavos), 0)
    lotes_trabalho = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    lotes_trabalho = atualizar_lotes_investidos_ate_data(lotes_trabalho, data_critica, estado)

    selecoes_rows: list[dict[str, Any]] = []
    snapshot_candidatos: pd.DataFrame | None = None
    ordem = 0

    while deficit_restante > 0:
        candidatos = gerar_candidatos_resgate_por_data_local(
            estado=estado,
            data_critica=data_critica,
            valor_necessario_centavos=deficit_restante,
            lotes_base=lotes_trabalho,
        )
        if snapshot_candidatos is None:
            snapshot_candidatos = candidatos.copy()
        if candidatos.empty:
            break

        melhor = candidatos.iloc[0]
        idxs = lotes_trabalho.index[lotes_trabalho["id_lote"] == melhor["id_lote"]]
        if len(idxs) == 0:
            break
        idx = idxs[0]
        lote_atual = lotes_trabalho.loc[idx].copy()
        avaliacao = avaliar_candidato_resgate(
            lote=lote_atual,
            data_critica=data_critica,
            valor_necessario_centavos=deficit_restante,
            estado=estado,
            lote_ja_atualizado=True,
        )
        if avaliacao is None or avaliacao.valor_resgate_centavos <= 0:
            break

        ordem += 1
        lotes_trabalho.loc[idx, avaliacao.lote_pos_resgate.index] = avaliacao.lote_pos_resgate.values
        deficit_restante -= int(avaliacao.valor_resgate_centavos)

        selecoes_rows.append(
            {
                "data": data_critica,
                "ordem_resgate_no_dia": ordem,
                "ranking_candidato": int(melhor["ranking_candidato"]),
                "id_lote": str(melhor["id_lote"]),
                "id_carteira": str(melhor["id_carteira"]),
                "carteira": str(melhor["carteira"]),
                "valor_resgatado_centavos": int(avaliacao.valor_resgate_centavos),
                "valor_liquido_antes_centavos": int(avaliacao.info_resgate["valor_liquido_antes_centavos"]),
                "valor_liquido_depois_centavos": int(avaliacao.info_resgate["valor_liquido_depois_centavos"]),
                "valor_bruto_antes_centavos": int(avaliacao.info_resgate["valor_bruto_antes_centavos"]),
                "valor_bruto_depois_centavos": int(avaliacao.info_resgate["valor_bruto_depois_centavos"]),
                "principal_antes_centavos": int(avaliacao.info_resgate["principal_antes_centavos"]),
                "principal_depois_centavos": int(avaliacao.info_resgate["principal_depois_centavos"]),
                "foi_resgate_total": bool(avaliacao.info_resgate["foi_resgate_total"]),
                "valor_terminal_se_mantido_centavos": int(avaliacao.valor_terminal_se_mantido_centavos),
                "valor_terminal_apos_resgate_centavos": int(avaliacao.valor_terminal_apos_resgate_centavos),
                "custo_oportunidade_centavos": int(avaliacao.custo_oportunidade_centavos),
                "custo_oportunidade_por_real_resgatado": float(avaliacao.custo_oportunidade_por_real_resgatado),
                "custo_complemento_mesmo_dia_centavos": 0,
                "penalidade_preservacao_futura_centavos": 0,
                "penalidade_essencialidade_futura_centavos": 0,
                "cobertura_futura_viavel": True,
                "saldo_investido_liquido_final_centavos": 0,
                "score_intertemporal_centavos": int(avaliacao.custo_oportunidade_centavos),
                "score_intertemporal_por_real_resgatado": float(avaliacao.custo_oportunidade_por_real_resgatado),
            }
        )

    selecoes = pd.DataFrame(selecoes_rows, columns=SELECOES_RESGATE_COLUMNS)
    if snapshot_candidatos is None:
        snapshot_candidatos = pd.DataFrame(columns=CANDIDATOS_RESGATE_COLUMNS)

    if not selecoes.empty:
        saldo_final = _saldo_investido_liquido(lotes_trabalho)
        selecoes["saldo_investido_liquido_final_centavos"] = saldo_final

    return ResultadoSelecaoResgates(
        selecoes=selecoes,
        candidatos_ordenados=snapshot_candidatos,
        lotes_atualizados=lotes_trabalho,
        deficit_inicial_centavos=int(deficit_centavos),
        deficit_final_centavos=max(deficit_restante, 0),
        cobertura_total=deficit_restante <= 0,
    )



def avaliar_candidato_resgate_intertemporal(
    lote: pd.Series,
    data_critica: pd.Timestamp,
    valor_necessario_centavos: int,
    estado: EstadoSistema,
    lotes_base: pd.DataFrame,
    deficits_futuros: list[tuple[pd.Timestamp, int]],
    liquidez_pool_futuro: dict[pd.Timestamp, int],
) -> AvaliacaoIntertemporalResgate | None:
    avaliacao_base = avaliar_candidato_resgate(
        lote=lote,
        data_critica=data_critica,
        valor_necessario_centavos=valor_necessario_centavos,
        estado=estado,
    )
    if avaliacao_base is None or avaliacao_base.valor_resgate_centavos <= 0:
        return None

    lotes_pos = lotes_base.copy()
    idxs = lotes_pos.index[lotes_pos["id_lote"] == lote["id_lote"]]
    if len(idxs) == 0:
        return None
    idx = idxs[0]
    lotes_pos.loc[idx, avaliacao_base.lote_pos_resgate.index] = avaliacao_base.lote_pos_resgate.values

    deficit_restante_no_dia = max(int(valor_necessario_centavos) - int(avaliacao_base.valor_resgate_centavos), 0)
    custo_complemento = 0
    if deficit_restante_no_dia > 0:
        complemento = selecionar_resgates_para_deficit_local(
            estado=estado,
            data_critica=data_critica,
            deficit_centavos=deficit_restante_no_dia,
            lotes_base=lotes_pos,
        )
        custo_complemento = int(complemento.selecoes["custo_oportunidade_centavos"].sum()) if not complemento.selecoes.empty else 0

    penalidade_preservacao = 0.0
    penalidade_essencialidade = 0
    cobertura_futura_viavel = True

    for ordem, (data_futura, deficit_futuro) in enumerate(deficits_futuros, start=1):
        if deficit_futuro <= 0:
            continue
        liquidez_pool = max(int(liquidez_pool_futuro.get(pd.Timestamp(data_futura).normalize(), 0)), 1)
        liquidez_lote_mantido = _precificar_liquido_lote_em_data(avaliacao_base.lote_atualizado_data, data_futura, estado)
        liquidez_lote_apos = _precificar_liquido_lote_em_data(avaliacao_base.lote_pos_resgate, data_futura, estado)
        perda_liquidez_futura = max(liquidez_lote_mantido - liquidez_lote_apos, 0)
        if perda_liquidez_futura <= 0:
            continue

        fator_escassez = min(deficit_futuro / liquidez_pool, 1.0)
        peso_urgencia = 1.0 / ordem
        penalidade_preservacao += perda_liquidez_futura * fator_escassez * peso_urgencia

        liquidez_pool_apos = max(liquidez_pool - perda_liquidez_futura, 0)
        if liquidez_pool_apos < deficit_futuro:
            cobertura_futura_viavel = False
            penalidade_essencialidade += int((deficit_futuro - liquidez_pool_apos) * ESSENCIALIDADE_PENALTY_MULTIPLIER)

    penalidade_preservacao_i = int(round(penalidade_preservacao))
    saldo_investido_final = int(avaliacao_base.valor_terminal_apos_resgate_centavos)
    score_intertemporal = int(
        avaliacao_base.custo_oportunidade_centavos
        + custo_complemento
        + penalidade_preservacao_i
        + penalidade_essencialidade
    )
    score_por_real = score_intertemporal / avaliacao_base.valor_resgate_centavos if avaliacao_base.valor_resgate_centavos > 0 else float("inf")

    return AvaliacaoIntertemporalResgate(
        avaliacao_base=avaliacao_base,
        custo_complemento_mesmo_dia_centavos=int(custo_complemento),
        penalidade_preservacao_futura_centavos=int(penalidade_preservacao_i),
        penalidade_essencialidade_futura_centavos=int(penalidade_essencialidade),
        cobertura_futura_viavel=bool(cobertura_futura_viavel),
        saldo_investido_liquido_final_centavos=saldo_investido_final,
        score_intertemporal_centavos=int(score_intertemporal),
        score_intertemporal_por_real_resgatado=float(score_por_real),
    )



def gerar_candidatos_resgate_por_data(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    valor_necessario_centavos: int,
    lotes_base: pd.DataFrame | None = None,
) -> pd.DataFrame:
    data_critica = pd.Timestamp(data_critica).normalize()
    lotes_ref = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    lotes_ref = atualizar_lotes_investidos_ate_data(lotes_ref, data_critica, estado)

    deficits_futuros = _timeline_deficits_futuros_a_partir_de_data(estado, data_critica, caixa_inicial_centavos=0)
    datas_futuras = [d for d, _ in deficits_futuros]
    liquidez_pool_futuro = _liquidez_total_pool_por_data(lotes_ref, datas_futuras, estado)

    rows: list[dict[str, Any]] = []
    for _, lote in lotes_ref.iterrows():
        avaliacao = avaliar_candidato_resgate_intertemporal(
            lote=lote,
            data_critica=data_critica,
            valor_necessario_centavos=valor_necessario_centavos,
            estado=estado,
            lotes_base=lotes_ref,
            deficits_futuros=deficits_futuros,
            liquidez_pool_futuro=liquidez_pool_futuro,
        )
        if avaliacao is None:
            continue

        base = avaliacao.avaliacao_base
        rows.append(
            {
                "data": data_critica,
                "ranking_candidato": 0,
                "id_lote": str(lote["id_lote"]),
                "id_carteira": str(lote["id_carteira_atual"]),
                "carteira": str(lote["carteira_atual"]),
                "valor_liquido_atual_centavos": int(base.info_resgate["valor_liquido_antes_centavos"]),
                "valor_bruto_atual_centavos": int(base.info_resgate["valor_bruto_antes_centavos"]),
                "valor_principal_atual_centavos": int(base.info_resgate["principal_antes_centavos"]),
                "valor_resgate_planejado_centavos": int(base.valor_resgate_centavos),
                "valor_terminal_se_mantido_centavos": int(base.valor_terminal_se_mantido_centavos),
                "valor_terminal_apos_resgate_centavos": int(base.valor_terminal_apos_resgate_centavos),
                "custo_oportunidade_centavos": int(base.custo_oportunidade_centavos),
                "custo_oportunidade_por_real_resgatado": float(base.custo_oportunidade_por_real_resgatado),
                "custo_complemento_mesmo_dia_centavos": int(avaliacao.custo_complemento_mesmo_dia_centavos),
                "penalidade_preservacao_futura_centavos": int(avaliacao.penalidade_preservacao_futura_centavos),
                "penalidade_essencialidade_futura_centavos": int(avaliacao.penalidade_essencialidade_futura_centavos),
                "cobertura_futura_viavel": bool(avaliacao.cobertura_futura_viavel),
                "saldo_investido_liquido_final_centavos": int(avaliacao.saldo_investido_liquido_final_centavos),
                "score_intertemporal_centavos": int(avaliacao.score_intertemporal_centavos),
                "score_intertemporal_por_real_resgatado": float(avaliacao.score_intertemporal_por_real_resgatado),
                "suficiente_para_cobrir_sozinho": bool(int(base.info_resgate["valor_liquido_antes_centavos"]) >= int(valor_necessario_centavos)),
            }
        )

    candidatos = pd.DataFrame(rows, columns=CANDIDATOS_RESGATE_COLUMNS)
    if candidatos.empty:
        return candidatos

    candidatos = candidatos.sort_values(
        [
            "cobertura_futura_viavel",
            "score_intertemporal_por_real_resgatado",
            "score_intertemporal_centavos",
            "custo_oportunidade_por_real_resgatado",
            "custo_oportunidade_centavos",
            "suficiente_para_cobrir_sozinho",
            "saldo_investido_liquido_final_centavos",
            "valor_liquido_atual_centavos",
            "id_lote",
        ],
        ascending=[False, True, True, True, True, False, False, False, True],
    ).reset_index(drop=True)
    candidatos["ranking_candidato"] = candidatos.index + 1
    return candidatos[CANDIDATOS_RESGATE_COLUMNS]



def selecionar_resgates_para_deficit(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    deficit_centavos: int,
    lotes_base: pd.DataFrame | None = None,
) -> ResultadoSelecaoResgates:
    data_critica = pd.Timestamp(data_critica).normalize()
    deficit_restante = max(int(deficit_centavos), 0)
    lotes_trabalho = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    lotes_trabalho = atualizar_lotes_investidos_ate_data(lotes_trabalho, data_critica, estado)

    selecoes_rows: list[dict[str, Any]] = []
    snapshot_candidatos: pd.DataFrame | None = None
    ordem = 0

    while deficit_restante > 0:
        candidatos = gerar_candidatos_resgate_por_data(
            estado=estado,
            data_critica=data_critica,
            valor_necessario_centavos=deficit_restante,
            lotes_base=lotes_trabalho,
        )
        if snapshot_candidatos is None:
            snapshot_candidatos = candidatos.copy()
        if candidatos.empty:
            break

        melhor = candidatos.iloc[0]
        idxs = lotes_trabalho.index[lotes_trabalho["id_lote"] == melhor["id_lote"]]
        if len(idxs) == 0:
            break
        idx = idxs[0]
        lote_atual = lotes_trabalho.loc[idx].copy()
        deficits_futuros = _timeline_deficits_futuros_a_partir_de_data(estado, data_critica, caixa_inicial_centavos=0)
        liquidez_pool_futuro = _liquidez_total_pool_por_data(lotes_trabalho, [d for d, _ in deficits_futuros], estado)
        avaliacao = avaliar_candidato_resgate_intertemporal(
            lote=lote_atual,
            data_critica=data_critica,
            valor_necessario_centavos=deficit_restante,
            estado=estado,
            lotes_base=lotes_trabalho,
            deficits_futuros=deficits_futuros,
            liquidez_pool_futuro=liquidez_pool_futuro,
        )
        if avaliacao is None or avaliacao.avaliacao_base.valor_resgate_centavos <= 0:
            break

        ordem += 1
        lotes_trabalho.loc[idx, avaliacao.avaliacao_base.lote_pos_resgate.index] = avaliacao.avaliacao_base.lote_pos_resgate.values
        deficit_restante -= int(avaliacao.avaliacao_base.valor_resgate_centavos)

        selecoes_rows.append(
            {
                "data": data_critica,
                "ordem_resgate_no_dia": ordem,
                "ranking_candidato": int(melhor["ranking_candidato"]),
                "id_lote": str(melhor["id_lote"]),
                "id_carteira": str(melhor["id_carteira"]),
                "carteira": str(melhor["carteira"]),
                "valor_resgatado_centavos": int(avaliacao.avaliacao_base.valor_resgate_centavos),
                "valor_liquido_antes_centavos": int(avaliacao.avaliacao_base.info_resgate["valor_liquido_antes_centavos"]),
                "valor_liquido_depois_centavos": int(avaliacao.avaliacao_base.info_resgate["valor_liquido_depois_centavos"]),
                "valor_bruto_antes_centavos": int(avaliacao.avaliacao_base.info_resgate["valor_bruto_antes_centavos"]),
                "valor_bruto_depois_centavos": int(avaliacao.avaliacao_base.info_resgate["valor_bruto_depois_centavos"]),
                "principal_antes_centavos": int(avaliacao.avaliacao_base.info_resgate["principal_antes_centavos"]),
                "principal_depois_centavos": int(avaliacao.avaliacao_base.info_resgate["principal_depois_centavos"]),
                "foi_resgate_total": bool(avaliacao.avaliacao_base.info_resgate["foi_resgate_total"]),
                "valor_terminal_se_mantido_centavos": int(avaliacao.avaliacao_base.valor_terminal_se_mantido_centavos),
                "valor_terminal_apos_resgate_centavos": int(avaliacao.avaliacao_base.valor_terminal_apos_resgate_centavos),
                "custo_oportunidade_centavos": int(avaliacao.avaliacao_base.custo_oportunidade_centavos),
                "custo_oportunidade_por_real_resgatado": float(avaliacao.avaliacao_base.custo_oportunidade_por_real_resgatado),
                "custo_complemento_mesmo_dia_centavos": int(avaliacao.custo_complemento_mesmo_dia_centavos),
                "penalidade_preservacao_futura_centavos": int(avaliacao.penalidade_preservacao_futura_centavos),
                "penalidade_essencialidade_futura_centavos": int(avaliacao.penalidade_essencialidade_futura_centavos),
                "cobertura_futura_viavel": bool(avaliacao.cobertura_futura_viavel),
                "saldo_investido_liquido_final_centavos": int(avaliacao.saldo_investido_liquido_final_centavos),
                "score_intertemporal_centavos": int(avaliacao.score_intertemporal_centavos),
                "score_intertemporal_por_real_resgatado": float(avaliacao.score_intertemporal_por_real_resgatado),
            }
        )

    selecoes = pd.DataFrame(selecoes_rows, columns=SELECOES_RESGATE_COLUMNS)
    if snapshot_candidatos is None:
        snapshot_candidatos = pd.DataFrame(columns=CANDIDATOS_RESGATE_COLUMNS)

    return ResultadoSelecaoResgates(
        selecoes=selecoes,
        candidatos_ordenados=snapshot_candidatos,
        lotes_atualizados=lotes_trabalho,
        deficit_inicial_centavos=int(deficit_centavos),
        deficit_final_centavos=max(deficit_restante, 0),
        cobertura_total=deficit_restante <= 0,
    )
