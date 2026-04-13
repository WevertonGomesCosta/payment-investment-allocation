from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from estado import EstadoSistema
from motor_precificacao import (
    avaliar_aporte_em_carteira,
    bonus_remanescente_domina_destino,
    calcular_dias_bonus_restantes,
    origem_domina_destino_estruturalmente,
    precificar_lote_investido_na_data,
)
from motor_resgates import aplicar_resgate_liquido_proporcional, atualizar_lotes_investidos_ate_data
from tipos import (
    AvaliacaoSwitching,
    ConfigProjeto,
    ContratoSwitching,
    InvarianteSwitching,
    ResultadoComparacaoSwitching,
    StatusContratoSwitching,
    TipoSwitching,
    ValidationIssue,
    ValidationReport,
)


SWITCHING_INVARIANTES: tuple[InvarianteSwitching, ...] = (
    InvarianteSwitching(
        code="SW_ORIGEM_STATUS_INVESTIDO",
        description="A origem deve estar em INVESTIDO_ATUAL.",
    ),
    InvarianteSwitching(
        code="SW_ORIGEM_SALDO_POSITIVO",
        description="A origem deve ter valor líquido resgatável positivo.",
    ),
    InvarianteSwitching(
        code="SW_ORIGEM_FLAG_SWITCH",
        description="O lote de origem deve permitir switching no modelo.",
    ),
    InvarianteSwitching(
        code="SW_ORIGEM_DATA_ELEGIVEL",
        description="A data crítica deve ser maior ou igual à data de elegibilidade para switching.",
    ),
    InvarianteSwitching(
        code="SW_ORIGEM_DOMINA_DESTINO_ESTRUTURALMENTE",
        description="Se a origem dominar estruturalmente o destino em rendimento comparável, o switching deve ser bloqueado.",
    ),
    InvarianteSwitching(
        code="SW_ORIGEM_BONUS_REMANESCENTE_DOMINANTE",
        description="Se a origem ainda estiver em bônus remanescente dominante frente ao destino, o switching deve ser bloqueado.",
    ),
    InvarianteSwitching(
        code="SW_DESTINO_ATIVO",
        description="A carteira de destino deve estar ativa para nova entrada.",
    ),
    InvarianteSwitching(
        code="SW_DESTINO_DIFERENTE_ORIGEM",
        description="A carteira de destino deve ser diferente da carteira de origem.",
    ),
    InvarianteSwitching(
        code="SW_DESTINO_NAO_COMBO_ONLY",
        description="Produtos Somente_Combo não podem ser destino nesta fase metodológica.",
    ),
    InvarianteSwitching(
        code="SW_DESTINO_TIPO_SUPORTADO",
        description="Combos explícitos e estruturas ainda não suportadas não entram como destino nesta fase.",
    ),
    InvarianteSwitching(
        code="SW_DESTINO_FAIXA_APLICACAO",
        description="O valor transferido deve respeitar mínimo e máximo de aplicação.",
    ),
    InvarianteSwitching(
        code="SW_VALOR_NAO_NEGATIVO",
        description="O valor transferido deve ser estritamente positivo.",
    ),
    InvarianteSwitching(
        code="SW_LINEAGE_IDS_PRESENTES",
        description="Origem, destino e data devem estar materializados para auditoria.",
    ),
)


SWITCHING_CANDIDATE_COLUMNS = [
    "data_switching",
    "deficit_data_critica_centavos",
    "ranking_candidato",
    "id_lote_origem",
    "id_carteira_origem",
    "carteira_origem",
    "id_carteira_destino",
    "carteira_destino",
    "tipo_switching",
    "valor_liquido_origem_centavos",
    "valor_liquido_transferido_centavos",
    "suficiente_para_cobrir_sozinho",
    "status_contrato",
    "valor_terminal_manter_centavos",
    "valor_terminal_resgatar_centavos",
    "valor_terminal_switchar_centavos",
    "ganho_incremental_switching_vs_manter_centavos",
    "custo_oportunidade_resgate_centavos",
    "custo_oportunidade_switching_centavos",
    "score_switching_vs_manter_centavos",
    "score_switching_vs_resgate_centavos",
    "score_ranking_switching_centavos",
    "melhor_acao",
    "motivo_economico",
]


SWITCHING_EVENT_COLUMNS = [
    "data_switching",
    "id_lote_origem",
    "id_lote_destino_previsto",
    "id_carteira_origem",
    "id_carteira_destino",
    "tipo_switching",
    "valor_bruto_origem_centavos",
    "valor_liquido_transferido_centavos",
    "status_contrato",
    "motivo_economico",
]


def listar_invariantes_switching() -> list[dict[str, Any]]:
    return [asdict(inv) for inv in SWITCHING_INVARIANTES]


def _empty_report() -> ValidationReport:
    return ValidationReport(ok=True, issues=[])


def _add_issue(
    report: ValidationReport,
    *,
    row_id: str,
    field_name: str,
    code: str,
    message: str,
    severity: str = "ERROR",
) -> None:
    report.add_issue(
        ValidationIssue(
            severity=severity,
            table_name="switching",
            row_id=row_id,
            field_name=field_name,
            code=code,
            message=message,
        )
    )


def obter_carteira_por_id(carteiras: pd.DataFrame, id_carteira: str) -> pd.Series | None:
    match = carteiras.loc[carteiras["id_carteira"].astype(str) == str(id_carteira)]
    if match.empty:
        return None
    return match.iloc[0]


def obter_carteira_origem_do_lote(lote: pd.Series, estado: EstadoSistema) -> pd.Series | None:
    id_carteira = str(lote.get("id_carteira_atual", ""))
    if not id_carteira:
        return None
    return obter_carteira_por_id(estado.carteiras, id_carteira)



def validar_origem_switching(
    lote: pd.Series,
    carteira_origem: pd.Series | None,
    data_switching: pd.Timestamp,
    config: ConfigProjeto,
) -> ValidationReport:
    report = _empty_report()
    lote_id = str(lote.get("id_lote", ""))
    data_switching = pd.Timestamp(data_switching).normalize()

    if str(lote.get("status_lote", "")) != "INVESTIDO_ATUAL":
        _add_issue(
            report,
            row_id=lote_id,
            field_name="status_lote",
            code="SW_ORIGEM_STATUS_INVESTIDO",
            message="Switching individual exige lote em INVESTIDO_ATUAL.",
        )

    if int(lote.get("valor_liquido_resgatavel_centavos", 0)) <= 0:
        _add_issue(
            report,
            row_id=lote_id,
            field_name="valor_liquido_resgatavel_centavos",
            code="SW_ORIGEM_SALDO_POSITIVO",
            message="Lote sem valor líquido positivo não pode originar switching.",
        )

    if not bool(lote.get("flag_pode_switchar", False)):
        _add_issue(
            report,
            row_id=lote_id,
            field_name="flag_pode_switchar",
            code="SW_ORIGEM_FLAG_SWITCH",
            message="Lote marcado como não elegível para switching.",
        )

    data_elegivel = lote.get("data_elegivel_switching", pd.NaT)
    if pd.isna(data_elegivel) or data_switching < pd.Timestamp(data_elegivel).normalize():
        _add_issue(
            report,
            row_id=lote_id,
            field_name="data_elegivel_switching",
            code="SW_ORIGEM_DATA_ELEGIVEL",
            message="Data crítica anterior à elegibilidade de switching.",
        )

    if carteira_origem is None:
        _add_issue(
            report,
            row_id=lote_id,
            field_name="id_carteira_atual",
            code="SW_LINEAGE_IDS_PRESENTES",
            message="Carteira de origem não encontrada para o lote.",
        )

    return report


def validar_destino_switching(
    carteira_destino: pd.Series | None,
    id_carteira_origem: str,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> ValidationReport:
    report = _empty_report()
    destino_id = "" if carteira_destino is None else str(carteira_destino.get("id_carteira", ""))

    if carteira_destino is None:
        _add_issue(
            report,
            row_id=destino_id,
            field_name="id_carteira_destino",
            code="SW_LINEAGE_IDS_PRESENTES",
            message="Carteira de destino ausente.",
        )
        return report

    if valor_transferido_centavos <= 0:
        _add_issue(
            report,
            row_id=destino_id,
            field_name="valor_liquido_transferido_centavos",
            code="SW_VALOR_NAO_NEGATIVO",
            message="Switching exige valor transferido positivo.",
        )

    if not bool(carteira_destino.get("flag_ativa", False)):
        _add_issue(
            report,
            row_id=destino_id,
            field_name="flag_ativa",
            code="SW_DESTINO_ATIVO",
            message="Carteira de destino inativa para nova entrada.",
        )

    if str(carteira_destino.get("id_carteira", "")) == str(id_carteira_origem):
        _add_issue(
            report,
            row_id=destino_id,
            field_name="id_carteira_destino",
            code="SW_DESTINO_DIFERENTE_ORIGEM",
            message="Destino deve ser diferente da carteira de origem.",
        )

    if bool(carteira_destino.get("flag_somente_combo", False)):
        _add_issue(
            report,
            row_id=destino_id,
            field_name="flag_somente_combo",
            code="SW_DESTINO_NAO_COMBO_ONLY",
            message="Produtos Somente_Combo ficam bloqueados nesta fase.",
        )

    tipo_produto = str(carteira_destino.get("tipo_produto", "")).strip().lower()
    if tipo_produto == "combo":
        _add_issue(
            report,
            row_id=destino_id,
            field_name="tipo_produto",
            code="SW_DESTINO_TIPO_SUPORTADO",
            message="Produtos Combo explícitos ainda não são suportados como destino.",
        )

    aplicacao_minima = int(carteira_destino.get("aplicacao_minima_centavos", 0))
    aplicacao_maxima = int(carteira_destino.get("aplicacao_maxima_centavos", 0))
    if valor_transferido_centavos < aplicacao_minima:
        _add_issue(
            report,
            row_id=destino_id,
            field_name="aplicacao_minima_centavos",
            code="SW_DESTINO_FAIXA_APLICACAO",
            message="Valor abaixo do mínimo exigido pela carteira de destino.",
        )
    if aplicacao_maxima > 0 and valor_transferido_centavos > aplicacao_maxima:
        _add_issue(
            report,
            row_id=destino_id,
            field_name="aplicacao_maxima_centavos",
            code="SW_DESTINO_FAIXA_APLICACAO",
            message="Valor acima do máximo permitido pela carteira de destino.",
        )

    if config.politicas_modelo.produto_inativo_em_novo_aporte.lower() == "erro" and not bool(carteira_destino.get("flag_ativa", False)):
        # explicit policy reinforcement already captured as validation issue above
        pass

    return report


def validar_bloqueio_bonus_remanescente(
    lote: pd.Series,
    carteira_origem: pd.Series | None,
    carteira_destino: pd.Series | None,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> ValidationReport:
    report = _empty_report()
    lote_id = str(lote.get("id_lote", ""))
    if carteira_origem is None or carteira_destino is None:
        return report

    if bonus_remanescente_domina_destino(
        lote=lote,
        carteira_origem=carteira_origem,
        carteira_destino=carteira_destino,
        data_switching=data_switching,
        valor_transferido_centavos=valor_transferido_centavos,
        config=config,
    ):
        dias_restantes = calcular_dias_bonus_restantes(
            data_entrada_produto=pd.Timestamp(lote["data_entrada_lote"]).normalize(),
            data_referencia=pd.Timestamp(data_switching).normalize(),
            carteira=carteira_origem,
        )
        _add_issue(
            report,
            row_id=lote_id,
            field_name="dias_bonus",
            code="SW_ORIGEM_BONUS_REMANESCENTE_DOMINANTE",
            message=(
                "Origem ainda possui bônus remanescente dominante frente ao destino; "
                f"switching bloqueado ({dias_restantes} dias de bônus restantes)."
            ),
        )
    return report


def validar_dominancia_estrutural_origem(
    lote: pd.Series,
    carteira_origem: pd.Series | None,
    carteira_destino: pd.Series | None,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> ValidationReport:
    report = _empty_report()
    lote_id = str(lote.get("id_lote", ""))
    if carteira_origem is None or carteira_destino is None:
        return report

    if origem_domina_destino_estruturalmente(
        lote=lote,
        carteira_origem=carteira_origem,
        carteira_destino=carteira_destino,
        data_switching=data_switching,
        valor_transferido_centavos=valor_transferido_centavos,
        config=config,
    ):
        _add_issue(
            report,
            row_id=lote_id,
            field_name="dominancia_estrutural_origem",
            code="SW_ORIGEM_DOMINA_DESTINO_ESTRUTURALMENTE",
            message="Origem domina estruturalmente o destino em rendimento comparável; manter deve dominar switching.",
        )
    return report


def validar_contrato_switching(
    lote: pd.Series,
    carteira_origem: pd.Series | None,
    carteira_destino: pd.Series | None,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int,
    config: ConfigProjeto,
) -> ValidationReport:
    report = _empty_report()
    report.extend(validar_origem_switching(lote, carteira_origem, data_switching, config).issues)
    report.extend(
        validar_destino_switching(
            carteira_destino=carteira_destino,
            id_carteira_origem=str(lote.get("id_carteira_atual", "")),
            valor_transferido_centavos=valor_transferido_centavos,
            config=config,
        ).issues
    )
    report.extend(
        validar_bloqueio_bonus_remanescente(
            lote=lote,
            carteira_origem=carteira_origem,
            carteira_destino=carteira_destino,
            data_switching=data_switching,
            valor_transferido_centavos=valor_transferido_centavos,
            config=config,
        ).issues
    )

    report.extend(
        validar_dominancia_estrutural_origem(
            lote=lote,
            carteira_origem=carteira_origem,
            carteira_destino=carteira_destino,
            data_switching=data_switching,
            valor_transferido_centavos=valor_transferido_centavos,
            config=config,
        ).issues
    )

    if not str(lote.get("id_lote", "")) or not str(lote.get("id_carteira_atual", "")):
        _add_issue(
            report,
            row_id=str(lote.get("id_lote", "")),
            field_name="lineage",
            code="SW_LINEAGE_IDS_PRESENTES",
            message="Origem precisa ter lote e carteira materializados.",
        )

    return report


def construir_contrato_switching_individual(
    lote: pd.Series,
    carteira_destino: pd.Series,
    data_switching: pd.Timestamp,
    valor_transferido_centavos: int | None = None,
    estado: EstadoSistema | None = None,
) -> ContratoSwitching:
    data_switching = pd.Timestamp(data_switching).normalize()
    valor_liquido_origem = int(lote.get("valor_liquido_resgatavel_centavos", 0))
    valor_bruto_origem = int(lote.get("valor_bruto_remanescente_centavos", lote.get("valor_saldo_centavos", 0)))
    if valor_transferido_centavos is None:
        valor_transferido_centavos = valor_liquido_origem
    valor_transferido_centavos = min(int(valor_transferido_centavos), valor_liquido_origem)
    tipo = TipoSwitching.INDIVIDUAL_TOTAL if valor_transferido_centavos >= valor_liquido_origem else TipoSwitching.INDIVIDUAL_PARCIAL

    carteira_origem = None
    if estado is not None:
        carteira_origem = obter_carteira_origem_do_lote(lote, estado)
    report = validar_contrato_switching(
        lote=lote,
        carteira_origem=carteira_origem,
        carteira_destino=carteira_destino,
        data_switching=data_switching,
        valor_transferido_centavos=valor_transferido_centavos,
        config=estado.config if estado is not None else None,  # type: ignore[arg-type]
    ) if estado is not None else _empty_report()
    status = StatusContratoSwitching.ELEGIVEL if report.ok else StatusContratoSwitching.INVALIDO

    return ContratoSwitching(
        id_lote_origem=str(lote.get("id_lote", "")),
        id_carteira_origem=str(lote.get("id_carteira_atual", "")),
        id_carteira_destino=str(carteira_destino.get("id_carteira", "")),
        data_switching=data_switching,
        tipo_switching=tipo,
        valor_liquido_transferido_centavos=valor_transferido_centavos,
        valor_bruto_origem_centavos=valor_bruto_origem,
        valor_liquido_origem_centavos=valor_liquido_origem,
        status=status,
        motivo_economico="Comparar manter vs resgatar vs switchar preservando liquidez futura.",
        id_lote_destino_previsto=f"SW_{str(lote.get('id_lote', ''))}_{str(carteira_destino.get('id_carteira', ''))}",
    )


def avaliar_contrato_switching(
    contrato: ContratoSwitching,
    lote_origem: pd.Series,
    carteira_origem: pd.Series,
    carteira_destino: pd.Series,
    estado: EstadoSistema,
) -> AvaliacaoSwitching:
    if contrato.status == StatusContratoSwitching.INVALIDO:
        return AvaliacaoSwitching(
            contrato=contrato,
            valor_terminal_manter_centavos=0,
            valor_terminal_resgatar_centavos=0,
            valor_terminal_switchar_centavos=0,
            custo_oportunidade_resgate_centavos=0,
            custo_oportunidade_switching_centavos=0,
            ganho_incremental_switching_vs_manter_centavos=0,
            melhor_acao=ResultadoComparacaoSwitching.INDETERMINADO,
            observacoes=("Contrato inválido para avaliação econômica.",),
        )

    data_switching = contrato.data_switching
    lote_atualizado = atualizar_lotes_investidos_ate_data(
        pd.DataFrame([lote_origem]),
        data_switching,
        estado,
    ).iloc[0].copy()
    lote_precificado = precificar_lote_investido_na_data(
        lote=lote_atualizado,
        carteira=carteira_origem,
        data_referencia=data_switching,
        config=estado.config,
    )

    valor_transferido = min(contrato.valor_liquido_transferido_centavos, lote_precificado.valor_liquido_centavos)
    valor_terminal_manter = precificar_lote_investido_na_data(
        lote=lote_atualizado,
        carteira=carteira_origem,
        data_referencia=estado.horizonte_final,
        config=estado.config,
    ).valor_liquido_centavos

    lote_atualizado["valor_liquido_resgatavel_centavos"] = int(lote_precificado.valor_liquido_centavos)
    lote_atualizado["valor_bruto_remanescente_centavos"] = int(lote_precificado.valor_bruto_centavos)
    lote_atualizado["valor_saldo_centavos"] = int(lote_precificado.valor_bruto_centavos)
    lote_pos_resgate, _ = aplicar_resgate_liquido_proporcional(lote_atualizado, valor_transferido)
    if int(lote_pos_resgate.get("valor_bruto_remanescente_centavos", 0)) > 0 and str(lote_pos_resgate.get("status_lote", "")) == "INVESTIDO_ATUAL":
        valor_terminal_residual_origem = precificar_lote_investido_na_data(
            lote=lote_pos_resgate,
            carteira=carteira_origem,
            data_referencia=estado.horizonte_final,
            config=estado.config,
        ).valor_liquido_centavos
    else:
        valor_terminal_residual_origem = 0

    valor_terminal_resgatar = valor_terminal_residual_origem

    avaliacao_destino = avaliar_aporte_em_carteira(
        valor_inicial_centavos=valor_transferido,
        carteira_destino=carteira_destino,
        data_aporte=data_switching,
        horizonte_final=estado.horizonte_final,
        config=estado.config,
    )
    valor_terminal_switchar = valor_terminal_residual_origem + avaliacao_destino.valor_liquido_projetado_centavos

    custo_resgate = max(int(valor_terminal_manter) - int(valor_terminal_resgatar), 0)
    custo_switch = max(int(valor_terminal_manter) - int(valor_terminal_switchar), 0)
    ganho_switch = int(valor_terminal_switchar) - int(valor_terminal_manter)

    melhor = ResultadoComparacaoSwitching.MANTER
    if valor_terminal_switchar >= valor_terminal_manter and valor_terminal_switchar >= valor_terminal_resgatar:
        melhor = ResultadoComparacaoSwitching.SWITCHAR
    elif valor_terminal_resgatar > valor_terminal_manter and valor_terminal_resgatar >= valor_terminal_switchar:
        melhor = ResultadoComparacaoSwitching.RESGATAR

    observacoes = (
        f"Valor transferido avaliado: {valor_transferido} centavos.",
        "Comparação econômica ainda não incorpora política conjunta nem switching em conjunto.",
    )

    return AvaliacaoSwitching(
        contrato=ContratoSwitching(
            **{**asdict(contrato), "status": StatusContratoSwitching.AVALIADO}
        ),
        valor_terminal_manter_centavos=int(valor_terminal_manter),
        valor_terminal_resgatar_centavos=int(valor_terminal_resgatar),
        valor_terminal_switchar_centavos=int(valor_terminal_switchar),
        custo_oportunidade_resgate_centavos=int(custo_resgate),
        custo_oportunidade_switching_centavos=int(custo_switch),
        ganho_incremental_switching_vs_manter_centavos=int(ganho_switch),
        melhor_acao=melhor,
        observacoes=observacoes,
    )



def listar_lotes_elegiveis_switching(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    lotes_base: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Atualiza os lotes investidos até a data crítica e devolve apenas as origens elegíveis."""
    data_critica = pd.Timestamp(data_critica).normalize()
    lotes_ref = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    lotes_atualizados = atualizar_lotes_investidos_ate_data(lotes_ref, data_critica, estado)
    mask = (
        (lotes_atualizados["status_lote"] == "INVESTIDO_ATUAL")
        & (lotes_atualizados["flag_pode_switchar"].astype(bool))
        & (lotes_atualizados["flag_carteira_encontrada"].astype(bool))
        & (lotes_atualizados["valor_liquido_resgatavel_centavos"] > 0)
        & (pd.to_datetime(lotes_atualizados["data_elegivel_switching"], errors="coerce").dt.normalize() <= data_critica)
    )
    return lotes_atualizados.loc[mask].copy().reset_index(drop=True)


def listar_destinos_elegiveis_switching(
    estado: EstadoSistema,
    lote_origem: pd.Series,
    valor_transferido_centavos: int,
) -> pd.DataFrame:
    """Lista carteiras destino já filtradas pelas regras canônicas de contrato."""
    rows: list[dict[str, Any]] = []
    id_origem = str(lote_origem.get("id_carteira_atual", ""))
    for _, carteira_destino in estado.carteiras.iterrows():
        report = validar_destino_switching(
            carteira_destino=carteira_destino,
            id_carteira_origem=id_origem,
            valor_transferido_centavos=int(valor_transferido_centavos),
            config=estado.config,
        )
        if report.ok:
            rows.append(carteira_destino.to_dict())
    return pd.DataFrame(rows)


def gerar_candidatos_switching_por_data(
    estado: EstadoSistema,
    data_critica: pd.Timestamp,
    deficit_centavos: int | None = None,
    lotes_base: pd.DataFrame | None = None,
    limitar_destinos_por_lote: int | None = None,
) -> pd.DataFrame:
    """Gera candidatos elegíveis de switching individual para uma data crítica."""
    data_critica = pd.Timestamp(data_critica).normalize()
    lotes_elegiveis = listar_lotes_elegiveis_switching(estado, data_critica, lotes_base=lotes_base)
    rows: list[dict[str, Any]] = []

    for _, lote in lotes_elegiveis.iterrows():
        valor_liquido_origem = int(lote.get("valor_liquido_resgatavel_centavos", 0))
        if valor_liquido_origem <= 0:
            continue
        valor_transferido = valor_liquido_origem if not deficit_centavos or int(deficit_centavos) <= 0 else min(valor_liquido_origem, int(deficit_centavos))
        destinos = listar_destinos_elegiveis_switching(estado, lote, valor_transferido)
        if destinos.empty:
            continue
        if limitar_destinos_por_lote is not None:
            destinos = destinos.head(limitar_destinos_por_lote).copy()

        carteira_origem = obter_carteira_origem_do_lote(lote, estado)
        if carteira_origem is None:
            continue

        for _, carteira_destino in destinos.iterrows():
            contrato = construir_contrato_switching_individual(
                lote=lote,
                carteira_destino=carteira_destino,
                data_switching=data_critica,
                valor_transferido_centavos=valor_transferido,
                estado=estado,
            )
            if contrato.status == StatusContratoSwitching.INVALIDO:
                continue
            avaliacao = avaliar_contrato_switching(
                contrato=contrato,
                lote_origem=lote,
                carteira_origem=carteira_origem,
                carteira_destino=carteira_destino,
                estado=estado,
            )
            row = materializar_linha_candidata_switching(avaliacao, carteira_destino, lote)
            row["deficit_data_critica_centavos"] = int(deficit_centavos or 0)
            row["valor_liquido_origem_centavos"] = valor_liquido_origem
            row["suficiente_para_cobrir_sozinho"] = bool(deficit_centavos is not None and valor_transferido >= int(deficit_centavos))
            row["valor_terminal_manter_centavos"] = int(avaliacao.valor_terminal_manter_centavos)
            row["valor_terminal_resgatar_centavos"] = int(avaliacao.valor_terminal_resgatar_centavos)
            row["valor_terminal_switchar_centavos"] = int(avaliacao.valor_terminal_switchar_centavos)
            row["ganho_incremental_switching_vs_manter_centavos"] = int(avaliacao.ganho_incremental_switching_vs_manter_centavos)
            row["custo_oportunidade_resgate_centavos"] = int(avaliacao.custo_oportunidade_resgate_centavos)
            row["custo_oportunidade_switching_centavos"] = int(avaliacao.custo_oportunidade_switching_centavos)
            row["score_ranking_switching_centavos"] = int(avaliacao.ganho_incremental_switching_vs_manter_centavos)
            rows.append(row)

    candidatos = pd.DataFrame(rows)
    if candidatos.empty:
        return pd.DataFrame(columns=SWITCHING_CANDIDATE_COLUMNS)

    prioridade = {"SWITCHAR": 0, "MANTER": 1, "RESGATAR": 2, "INDETERMINADO": 3}
    candidatos["_prioridade_melhor_acao"] = candidatos["melhor_acao"].map(prioridade).fillna(9).astype(int)
    candidatos = candidatos.sort_values(
        [
            "_prioridade_melhor_acao",
            "score_ranking_switching_centavos",
            "custo_oportunidade_switching_centavos",
            "id_lote_origem",
            "id_carteira_destino",
        ],
        ascending=[True, False, True, True, True],
    ).reset_index(drop=True)
    candidatos["ranking_candidato"] = range(1, len(candidatos) + 1)
    candidatos = candidatos.drop(columns=["_prioridade_melhor_acao"])
    return candidatos[SWITCHING_CANDIDATE_COLUMNS]


def gerar_candidatos_switching_datas_criticas(
    estado: EstadoSistema,
    max_datas: int | None = None,
    limitar_destinos_por_lote: int | None = None,
    lotes_base: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Gera candidatos elegíveis para todas as datas críticas sem resgate do estado atual."""
    from diagnostico_futuro import obter_datas_criticas_sem_resgate

    criticas = obter_datas_criticas_sem_resgate(estado, max_datas=max_datas)
    if criticas.empty:
        return pd.DataFrame(columns=SWITCHING_CANDIDATE_COLUMNS)

    blocos: list[pd.DataFrame] = []
    base = estado.lotes.copy() if lotes_base is None else lotes_base.copy()
    for _, row in criticas.iterrows():
        data = pd.Timestamp(row["data"]).normalize()
        deficit = int(row["deficit_sem_resgate_centavos"])
        candidatos = gerar_candidatos_switching_por_data(
            estado=estado,
            data_critica=data,
            deficit_centavos=deficit,
            lotes_base=base,
            limitar_destinos_por_lote=limitar_destinos_por_lote,
        )
        if not candidatos.empty:
            blocos.append(candidatos)
    if not blocos:
        return pd.DataFrame(columns=SWITCHING_CANDIDATE_COLUMNS)
    return pd.concat(blocos, ignore_index=True)

def materializar_linha_candidata_switching(avaliacao: AvaliacaoSwitching, carteira_destino: pd.Series, lote_origem: pd.Series) -> dict[str, Any]:
    return {
        "data_switching": avaliacao.contrato.data_switching,
        "id_lote_origem": avaliacao.contrato.id_lote_origem,
        "id_carteira_origem": avaliacao.contrato.id_carteira_origem,
        "carteira_origem": str(lote_origem.get("carteira_atual", "")),
        "id_carteira_destino": avaliacao.contrato.id_carteira_destino,
        "carteira_destino": str(carteira_destino.get("nome_carteira", "")),
        "tipo_switching": avaliacao.contrato.tipo_switching.value,
        "valor_liquido_transferido_centavos": avaliacao.contrato.valor_liquido_transferido_centavos,
        "status_contrato": avaliacao.contrato.status.value,
        "score_switching_vs_manter_centavos": int(avaliacao.ganho_incremental_switching_vs_manter_centavos),
        "score_switching_vs_resgate_centavos": int(
            avaliacao.valor_terminal_switchar_centavos - avaliacao.valor_terminal_resgatar_centavos
        ),
        "melhor_acao": avaliacao.melhor_acao.value,
        "motivo_economico": avaliacao.contrato.motivo_economico,
    }
