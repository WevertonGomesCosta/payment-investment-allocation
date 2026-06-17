from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from nucleo.situacao_atual_oficial import (
    _coagir_data_observavel,
    _serie_cdi_contexto,
    construir_situacao_atual_oficial as _construir_situacao_atual_oficial_base,
    para_float,
)


VERSAO_ME531_RENDIMENTO_MOTOR_CALIBRADO = "ME-531-RENDIMENTO-MOTOR-CALIBRADO-OBSERVADO-01"

COL_RENDIMENTO_OBSERVADO = "Rend. líq."
COL_RENDIMENTO_CALIBRADO = "Rend. líq. motor"
COL_DIF_CALIBRADA = "Dif. rend."
COL_RENDIMENTO_TEORICO = "Rend. motor teórico"
COL_DIF_TEORICA = "Dif. teórica"

_TITULOS_BLOCOS_VALORES = {
    "Lotes exauridos — valores e patrimônio",
    "Lotes ativos — valores e patrimônio",
}


def _norm_lote(valor: Any) -> str:
    return str(valor or "").strip().lower().replace(".", "")


def _round2(valor: Any) -> float:
    return round(para_float(valor), 2)


def _valor_numerico(valor: Any) -> bool:
    if valor is None or valor == "":
        return False
    try:
        float(valor)
        return True
    except Exception:
        return False


def _diferenca(observado: Any, motor: Any) -> float | str:
    if _valor_numerico(observado) and _valor_numerico(motor):
        return round(float(observado) - float(motor), 2)
    return "n/d"


def _iter_rows(objeto: Any) -> list[dict[str, Any]]:
    if objeto is None:
        return []
    if hasattr(objeto, "to_dict"):
        try:
            return list(objeto.to_dict(orient="records"))
        except Exception:
            pass
    if isinstance(objeto, list):
        return [dict(item) if isinstance(item, dict) else {"valor": item} for item in objeto]
    return []


def _mapa_lotes_por_id(lotes: Any) -> dict[str, Any]:
    mapa: dict[str, Any] = {}
    for lote in list(lotes or []):
        chave = _norm_lote(getattr(lote, "id", ""))
        if chave:
            mapa.setdefault(chave, lote)
    return mapa


def _linhas_replay_passado(contexto: Any) -> list[dict[str, Any]]:
    replay = getattr(contexto, "replay_passado", None)
    linhas = _iter_rows(getattr(replay, "log_passado", None))
    if linhas:
        return linhas
    return _iter_rows(getattr(replay, "log_movimentos_passados", None))


def _somas_replay_por_lote(contexto: Any) -> dict[str, dict[str, float]]:
    """Agrega valores realizados diretamente do replay passado upstream."""

    saida: dict[str, dict[str, float]] = {}
    for linha in _linhas_replay_passado(contexto):
        lote = str(linha.get("Lote") or linha.get("Lotes usados") or "").strip()
        if not lote:
            continue

        chave = _norm_lote(lote)
        slot = saida.setdefault(
            chave,
            {
                "bruto_sacado": 0.0,
                "imposto_pago": 0.0,
                "liquido_sacado": 0.0,
                "qtd_movimentos": 0.0,
            },
        )
        bruto = linha.get("Bruto")
        imposto = linha.get("Imposto")
        liquido = linha.get("Liquido") if "Liquido" in linha else linha.get("Líquido")
        if liquido is None:
            liquido = linha.get("Valor Líquido") or linha.get("Valor Liquido") or linha.get("Valor")

        slot["bruto_sacado"] = round(slot["bruto_sacado"] + abs(para_float(bruto)), 2)
        slot["imposto_pago"] = round(slot["imposto_pago"] + abs(para_float(imposto)), 2)
        slot["liquido_sacado"] = round(slot["liquido_sacado"] + abs(para_float(liquido)), 2)
        slot["qtd_movimentos"] = round(slot["qtd_movimentos"] + 1.0, 2)

    return saida


def _valores_switching_por_origem(
    estado_temporal_inicial: Any | None,
    saida: Any,
) -> dict[str, dict[str, float]]:
    """Agrega valores de switching materializados a partir de fontes upstream."""

    mapa: dict[str, dict[str, float]] = {}

    def _slot(lote: str) -> dict[str, float]:
        return mapa.setdefault(
            _norm_lote(lote),
            {
                "liquido_historico": 0.0,
                "bruto_historico": 0.0,
                "liquido_migrado": 0.0,
                "bruto_migrado": 0.0,
                "qtd_eventos": 0.0,
            },
        )

    auditoria = dict(getattr(saida, "auditoria", {}) or {})
    for item in list(auditoria.get("origens_migradas_por_switching") or []):
        lote = str(item.get("lote_origem") or "").strip()
        if not lote:
            continue

        slot = _slot(lote)
        liq_hist = para_float(item.get("valor_liquido_sacado_historico"))
        bruto_hist = para_float(item.get("valor_bruto_sacado_historico"))
        liq_migrado = para_float(item.get("valor_liquido_migrado_total") or item.get("valor_liquido_migrado"))
        bruto_migrado = (
            para_float(item.get("valor_bruto_migrado_total") or item.get("valor_bruto_migrado"))
            or liq_migrado
        )

        slot["liquido_historico"] = round(max(slot["liquido_historico"], liq_hist), 2)
        slot["bruto_historico"] = round(max(slot["bruto_historico"], bruto_hist), 2)
        slot["liquido_migrado"] = round(max(slot["liquido_migrado"], liq_migrado), 2)
        slot["bruto_migrado"] = round(max(slot["bruto_migrado"], bruto_migrado), 2)
        slot["qtd_eventos"] = round(slot["qtd_eventos"] + 1.0, 2)

    if estado_temporal_inicial is not None:
        for evento in list(getattr(estado_temporal_inicial, "switching_temporal_realizado", []) or []):
            lote = str(evento.get("lote_origem") or "").strip()
            if not lote:
                continue

            slot = _slot(lote)
            liq_migrado = para_float(
                evento.get("valor_liquido_migrado")
                or evento.get("valor_liquido_migrado_total")
                or evento.get("valor_liquido_origem")
                or evento.get("Valor líquido origem")
                or evento.get("Valor Líquido Migrado")
            )
            bruto_migrado = (
                para_float(
                    evento.get("valor_bruto_migrado")
                    or evento.get("valor_bruto_migrado_total")
                    or evento.get("valor_bruto_origem")
                    or evento.get("Valor bruto origem")
                )
                or liq_migrado
            )

            slot["liquido_migrado"] = round(max(slot["liquido_migrado"], liq_migrado), 2)
            slot["bruto_migrado"] = round(max(slot["bruto_migrado"], bruto_migrado), 2)
            slot["qtd_eventos"] = round(slot["qtd_eventos"] + 1.0, 2)

    return mapa


def _valor_liquido_residual_pos_replay(contexto: Any, lote: Any | None) -> float:
    if lote is None:
        return 0.0

    data_referencia = _coagir_data_observavel(getattr(contexto, "data_referencia", None))
    if data_referencia is None:
        return 0.0

    try:
        return _round2(
            lote.valor_liquido_em_data(
                data_referencia,
                contexto.calendario_financeiro,
                tabela_iof=getattr(contexto, "tabela_iof", None),
                faixas_ir=getattr(contexto, "faixas_ir", None),
                serie_cdi=_serie_cdi_contexto(contexto),
                data_base_referencia=data_referencia,
            )
        )
    except Exception:
        try:
            return _round2(
                lote.valor_liquido_hoje(
                    data_referencia,
                    tabela_iof=getattr(contexto, "tabela_iof", None),
                    faixas_ir=getattr(contexto, "faixas_ir", None),
                )
            )
        except Exception:
            return 0.0


def _valor_original_upstream(
    *,
    lote_id: str,
    linha: dict[str, Any],
    lotes_pre_replay: dict[str, Any],
    lotes_pos_replay: dict[str, Any],
) -> float:
    chave = _norm_lote(lote_id)
    lote = lotes_pos_replay.get(chave) or lotes_pre_replay.get(chave)
    valor = para_float(getattr(lote, "valor_inicial", 0.0))
    if valor <= 0.0:
        valor = para_float(linha.get("Orig."))
    return round(valor, 2)


def _rendimento_calibrado_linha(
    *,
    contexto: Any,
    estado_temporal_inicial: Any | None,
    saida: Any,
    linha: dict[str, Any],
    somas_replay: dict[str, dict[str, float]],
    lotes_pre_replay: dict[str, Any],
    lotes_pos_replay: dict[str, Any],
    valores_switching: dict[str, dict[str, float]],
) -> tuple[float | str, str]:
    """Calcula rendimento calibrado sem consultar a tabela renderizada como fonte primária.

    A linha observável é usada apenas como chave operacional/status. Os valores
    financeiros vêm do replay, dos lotes pós-replay e dos eventos/auditorias de
    switching materializados upstream.
    """

    _ = estado_temporal_inicial
    _ = saida

    lote_id = str(linha.get("Lote") or "").strip()
    chave = _norm_lote(lote_id)
    status = str(linha.get("Status ciclo") or "").strip()
    valor_original = _valor_original_upstream(
        lote_id=lote_id,
        linha=linha,
        lotes_pre_replay=lotes_pre_replay,
        lotes_pos_replay=lotes_pos_replay,
    )
    if not chave or valor_original <= 0.0:
        return "n/d", "sem_lote_ou_valor_original_upstream"

    soma = somas_replay.get(chave, {})
    liquido_sacado_replay = para_float(soma.get("liquido_sacado"))

    if status == "migrado_por_switching":
        sw = valores_switching.get(chave, {})
        liquido_historico = para_float(sw.get("liquido_historico"))
        liquido_migrado = para_float(sw.get("liquido_migrado"))
        if liquido_historico <= 0.0:
            liquido_historico = liquido_sacado_replay

        patrimonio_calibrado = round(liquido_historico + liquido_migrado, 2)
        return (
            round(patrimonio_calibrado - valor_original, 2),
            "saida.auditoria/estado_temporal_inicial.switching_materializado",
        )

    lote_pos = lotes_pos_replay.get(chave)
    liquido_residual = 0.0
    if status in {"ativo", "ativo_pos_switching"}:
        liquido_residual = _valor_liquido_residual_pos_replay(contexto, lote_pos)

    patrimonio_calibrado = round(liquido_sacado_replay + liquido_residual, 2)
    if patrimonio_calibrado <= 0.0:
        return "n/d", "sem_ancora_replay_pos_replay"

    return (
        round(patrimonio_calibrado - valor_original, 2),
        "replay_passado.log_passado+lotes_apos_replay",
    )


def _headers_valores_me531(headers: list[str]) -> list[str]:
    base = [
        h
        for h in list(headers or [])
        if h not in {COL_RENDIMENTO_CALIBRADO, COL_DIF_CALIBRADA, COL_RENDIMENTO_TEORICO, COL_DIF_TEORICA}
    ]
    return base + [
        COL_RENDIMENTO_CALIBRADO,
        COL_DIF_CALIBRADA,
        COL_RENDIMENTO_TEORICO,
        COL_DIF_TEORICA,
    ]


def _enriquecer_linhas_valores(
    *,
    contexto: Any,
    estado_temporal_inicial: Any | None,
    saida: Any,
    linhas: list[dict[str, Any]],
    somas_replay: dict[str, dict[str, float]],
    lotes_pre_replay: dict[str, Any],
    lotes_pos_replay: dict[str, Any],
    valores_switching: dict[str, dict[str, float]],
    auditoria: dict[str, Any],
) -> list[dict[str, Any]]:
    saida_linhas: list[dict[str, Any]] = []

    for linha in list(linhas or []):
        nova = dict(linha)
        rendimento_teorico = nova.get(COL_RENDIMENTO_CALIBRADO)
        dif_teorica = nova.get(COL_DIF_CALIBRADA)
        rendimento_observado = nova.get(COL_RENDIMENTO_OBSERVADO)

        rendimento_calibrado, fonte = _rendimento_calibrado_linha(
            contexto=contexto,
            estado_temporal_inicial=estado_temporal_inicial,
            saida=saida,
            linha=nova,
            somas_replay=somas_replay,
            lotes_pre_replay=lotes_pre_replay,
            lotes_pos_replay=lotes_pos_replay,
            valores_switching=valores_switching,
        )
        if not _valor_numerico(rendimento_calibrado):
            rendimento_calibrado = rendimento_teorico
            fonte = f"{fonte}|fallback_motor_teorico"

        dif_calibrada = _diferenca(rendimento_observado, rendimento_calibrado)

        nova[COL_RENDIMENTO_CALIBRADO] = rendimento_calibrado
        nova[COL_DIF_CALIBRADA] = dif_calibrada
        nova[COL_RENDIMENTO_TEORICO] = rendimento_teorico
        nova[COL_DIF_TEORICA] = dif_teorica

        auditoria["qtd_linhas_calibradas"] += int(_valor_numerico(rendimento_calibrado))
        auditoria["qtd_linhas_com_motor_teorico"] += int(_valor_numerico(rendimento_teorico))
        auditoria["qtd_linhas_fallback_teorico"] += int("fallback_motor_teorico" in fonte)
        if _valor_numerico(dif_calibrada) and abs(float(dif_calibrada)) <= 0.20:
            auditoria["qtd_dif_calibrada_dentro_tolerancia_020"] += 1
        elif _valor_numerico(dif_calibrada):
            auditoria["qtd_dif_calibrada_fora_tolerancia_020"] += 1

        if len(auditoria["amostra_fontes_calibracao"]) < 8:
            auditoria["amostra_fontes_calibracao"].append(
                {
                    "lote": nova.get("Lote"),
                    "status_ciclo": nova.get("Status ciclo"),
                    "fonte": fonte,
                    "rendimento_calibrado": rendimento_calibrado,
                    "rendimento_teorico": rendimento_teorico,
                    "dif_calibrada": dif_calibrada,
                    "dif_teorica": dif_teorica,
                }
            )

        saida_linhas.append(nova)

    return saida_linhas


def _enriquecer_blocos_situacao_atual(
    *,
    contexto: Any,
    saida: Any,
    estado_temporal_inicial: Any | None,
    blocos: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    replay = getattr(contexto, "replay_passado", None)
    nucleo = getattr(contexto, "nucleo_financeiro", None)

    somas_replay = _somas_replay_por_lote(contexto)
    lotes_pre_replay = _mapa_lotes_por_id(getattr(nucleo, "lotes_financeiros", []) or [])
    lotes_pos_replay = _mapa_lotes_por_id(getattr(replay, "lotes_apos_replay", []) or [])
    valores_switching = _valores_switching_por_origem(estado_temporal_inicial, saida)

    auditoria = {
        "versao": VERSAO_ME531_RENDIMENTO_MOTOR_CALIBRADO,
        "escopo": "rendimento_motor_situacao_atual",
        "fonte_primaria": "replay_passado.lotes_apos_replay/log_passado + estado_temporal_inicial.switching_temporal_realizado",
        "nao_usa_saida_renderizada_como_fonte_primaria": True,
        "preserva_motor_teorico": True,
        "coluna_motor_calibrado": COL_RENDIMENTO_CALIBRADO,
        "coluna_dif_calibrada": COL_DIF_CALIBRADA,
        "coluna_motor_teorico": COL_RENDIMENTO_TEORICO,
        "coluna_dif_teorica": COL_DIF_TEORICA,
        "qtd_lotes_pre_replay": len(lotes_pre_replay),
        "qtd_lotes_pos_replay": len(lotes_pos_replay),
        "qtd_lotes_com_movimentos_replay": len(somas_replay),
        "qtd_origens_switching_calibraveis": len(valores_switching),
        "qtd_blocos_valores_enriquecidos": 0,
        "qtd_linhas_calibradas": 0,
        "qtd_linhas_com_motor_teorico": 0,
        "qtd_linhas_fallback_teorico": 0,
        "qtd_dif_calibrada_dentro_tolerancia_020": 0,
        "qtd_dif_calibrada_fora_tolerancia_020": 0,
        "amostra_fontes_calibracao": [],
    }

    saida_blocos: list[dict[str, Any]] = []
    for bloco in list(blocos or []):
        novo_bloco = dict(bloco)
        if novo_bloco.get("titulo") in _TITULOS_BLOCOS_VALORES:
            novo_bloco["headers"] = _headers_valores_me531(list(novo_bloco.get("headers") or []))
            novo_bloco["linhas"] = _enriquecer_linhas_valores(
                contexto=contexto,
                estado_temporal_inicial=estado_temporal_inicial,
                saida=saida,
                linhas=list(novo_bloco.get("linhas") or []),
                somas_replay=somas_replay,
                lotes_pre_replay=lotes_pre_replay,
                lotes_pos_replay=lotes_pos_replay,
                valores_switching=valores_switching,
                auditoria=auditoria,
            )
            auditoria["qtd_blocos_valores_enriquecidos"] += 1
        saida_blocos.append(novo_bloco)

    return saida_blocos, auditoria


def construir_situacao_atual_oficial(
    contexto: Any,
    saida: Any,
    estado_temporal_inicial: Any | None = None,
) -> SimpleNamespace:
    """Monta a Situação Atual oficial com rendimento de motor calibrado ME-531.

    O construtor base continua produzindo o motor teórico. Esta camada move esse
    valor para colunas diagnósticas e publica, nas colunas históricas, o motor
    calibrado por observações reais upstream.
    """

    base = _construir_situacao_atual_oficial_base(
        contexto,
        saida,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    blocos, auditoria_me531 = _enriquecer_blocos_situacao_atual(
        contexto=contexto,
        saida=saida,
        estado_temporal_inicial=estado_temporal_inicial,
        blocos=list(getattr(base, "situacao_atual_blocos", []) or []),
    )

    auditoria_base = dict(getattr(base, "auditoria_situacao_atual_oficial", {}) or {})
    auditoria_base["me531_rendimento_motor_calibrado"] = auditoria_me531

    validacao_base = dict(getattr(base, "validacao_situacao_atual_oficial", {}) or {})
    evidencias = dict(validacao_base.get("evidencias", {}) or {})
    evidencias["me531_preserva_motor_teorico"] = True
    evidencias["me531_publica_motor_calibrado_por_ancora_upstream"] = True
    validacao_base["evidencias"] = evidencias

    return SimpleNamespace(
        fechamento_atual=list(getattr(base, "fechamento_atual", []) or []),
        resumo_recebidos=list(getattr(base, "resumo_recebidos", []) or []),
        recebidos_atuais=list(getattr(base, "recebidos_atuais", []) or []),
        situacao_atual_blocos=blocos,
        auditoria_situacao_atual_oficial=auditoria_base,
        validacao_situacao_atual_oficial=validacao_base,
    )
