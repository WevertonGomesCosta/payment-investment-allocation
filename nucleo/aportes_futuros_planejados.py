from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from typing import Any

from nucleo.utilitarios_neutros import _coerce_date, _normalizar_proxy_terminal


STATUS_PROMOVIVEL_V216 = "PROMOVIDO_CONTROLADO_V216"
STATUS_BLOQUEADO_DUPLA_CONTAGEM_V216 = "BLOQUEADO_DUPLA_CONTAGEM_V216"
STATUS_BLOQUEADO_RESERVA_V216 = "BLOQUEADO_RESERVA_CAIXA_V216"
STATUS_BLOQUEADO_PRODUTO_V216 = "BLOQUEADO_PRODUTO_DESTINO_V216"
STATUS_BLOQUEADO_INVARIANTE_V216 = "BLOQUEADO_INVARIANTE_V216"
STATUS_BLOQUEADO_GANHO_V216 = "BLOQUEADO_COMPARACAO_SEM_APORTE_V216"
STATUS_PROMOVIVEL_ECONOMICO_V220 = "PROMOVIVEL_ECONOMICO_V220"
STATUS_BLOQUEADO_GATE_ECONOMICO_V220 = "BLOQUEADO_GATE_ECONOMICO_V220"


def _safe_float(valor: Any, padrao: float = 0.0) -> float:
    if valor is None:
        return padrao
    try:
        if hasattr(valor, "isna") and valor.isna():
            return padrao
    except Exception:
        pass
    if isinstance(valor, str):
        bruto = valor.replace("R$", "").replace(" ", "").strip()
        if "," in bruto and "." in bruto:
            bruto = bruto.replace(".", "").replace(",", ".")
        elif "," in bruto:
            bruto = bruto.replace(",", ".")
        try:
            return float(bruto)
        except Exception:
            return padrao
    try:
        return float(valor)
    except Exception:
        return padrao


def _config_aportes_v216(config: dict[str, Any] | None) -> dict[str, Any]:
    bruto = {}
    for chave in ("aportes_futuros_v216", "aportes_planejados_v216", "aportes_futuros"):
        valor = (config or {}).get(chave)
        if isinstance(valor, dict):
            bruto.update(valor)
    return {
        "habilitado": bool(bruto.get("habilitado", True)),
        "reserva_dias": int(bruto.get("reserva_dias", 7) or 7),
        "liquidez_max_dias": int(bruto.get("liquidez_max_dias", 7) or 7),
        "carencia_max_dias": int(bruto.get("carencia_max_dias", 7) or 7),
        "tolerancia_monetaria": round(_safe_float(bruto.get("tolerancia_monetaria", 0.01), 0.01), 2),
        "exigir_ganho_positivo": bool(bruto.get("exigir_ganho_positivo", True)),
        "permitir_produto_combo": bool(bruto.get("permitir_produto_combo", False)),
    }


def _data_iso(valor: Any) -> str | None:
    data = _coerce_date(valor)
    return data.isoformat() if data is not None else None


def _id_recebido(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("fonte_id") or item.get("recebido_id") or "").strip()


def _valor_atual_recebido(item: dict[str, Any]) -> float:
    return round(_safe_float(item.get("valor_disponivel", item.get("valor"))), 2)


def _valor_original_recebido(item: dict[str, Any]) -> float:
    atual = _valor_atual_recebido(item)
    return round(_safe_float(
        item.get("valor_recebido_original_v216")
        or item.get("valor_original")
        or item.get("valor_liquido")
        or (atual + _safe_float(item.get("valor_pago_com_recebido_v216")) + _safe_float(item.get("valor_aportado_planejado_v216")))
        or atual
    ), 2)


def _pagamentos_futuros_janela(estado: dict[str, Any], data_atual: date, dias: int) -> list[dict[str, Any]]:
    limite = data_atual + timedelta(days=max(int(dias or 0), 0))
    saida: list[dict[str, Any]] = []
    for pagamento in estado.get("pagamentos_futuros") or []:
        data_pagamento = _coerce_date(pagamento.get("data"))
        if data_pagamento is None:
            continue
        # Pagamentos do próprio dia já foram processados antes desta etapa. A reserva cobre o futuro estrito.
        if data_atual < data_pagamento <= limite:
            saida.append(dict(pagamento))
    return saida


def _demanda_pagamentos_futuros(estado: dict[str, Any], data_atual: date, dias: int) -> float:
    return round(sum(_safe_float(p.get("valor")) for p in _pagamentos_futuros_janela(estado, data_atual, dias)), 2)


def _capacidade_caixa_outras_fontes(estado: dict[str, Any], recebido_id: str) -> float:
    saldo = _safe_float(estado.get("saldo_disponivel_geral"))
    outros_recebidos = 0.0
    for item in estado.get("recebidos_nao_aportados_disponiveis") or []:
        if _id_recebido(item) == recebido_id:
            continue
        outros_recebidos += _valor_atual_recebido(item)
    return round(saldo + outros_recebidos, 2)


def _ids_recebidos_ja_aportados(estado: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for lote in estado.get("lotes_aportados") or []:
        if bool(lote.get("origem_aporte_planejado_v216")):
            recebido_id = str(lote.get("recebido_id_origem") or "").strip()
            if recebido_id:
                ids.add(recebido_id)
    return ids


def _selecionar_produto_destino_v216(
    estado: dict[str, Any],
    valor_aporte: float,
    politica: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    motivos_rejeicao: list[str] = []
    candidatos = list(estado.get("produtos_destino_elegiveis") or [])
    if not candidatos:
        produto_padrao = dict(estado.get("produto_destino_padrao") or {})
        candidatos = [produto_padrao] if produto_padrao else []
    elegiveis: list[dict[str, Any]] = []
    for produto in candidatos:
        prod = dict(produto or {})
        produto_key = str(prod.get("produto_key") or "").strip()
        if not produto_key:
            motivos_rejeicao.append("produto_sem_key")
            continue
        aplicacao_minima = _safe_float(prod.get("aplicacao_minima"))
        aplicacao_maxima = _safe_float(prod.get("aplicacao_maxima"))
        liquidez_dias = int(_safe_float(prod.get("liquidez_dias"), 0.0))
        carencia_dias = int(_safe_float(prod.get("carencia_dias"), 0.0))
        somente_combo = bool(prod.get("somente_combo") or False)
        if somente_combo and not politica["permitir_produto_combo"]:
            motivos_rejeicao.append(f"{produto_key}:somente_combo")
            continue
        if valor_aporte + politica["tolerancia_monetaria"] < aplicacao_minima:
            motivos_rejeicao.append(f"{produto_key}:aplicacao_minima")
            continue
        if aplicacao_maxima > 0 and valor_aporte - politica["tolerancia_monetaria"] > aplicacao_maxima:
            motivos_rejeicao.append(f"{produto_key}:aplicacao_maxima")
            continue
        if liquidez_dias > politica["liquidez_max_dias"]:
            motivos_rejeicao.append(f"{produto_key}:liquidez_{liquidez_dias}d")
            continue
        if carencia_dias > politica["carencia_max_dias"]:
            motivos_rejeicao.append(f"{produto_key}:carencia_{carencia_dias}d")
            continue
        prod["_score_destino_v216"] = (
            _safe_float(prod.get("score_final")),
            _safe_float(prod.get("retorno_anual_proxy")),
            -float(liquidez_dias),
            -float(carencia_dias),
        )
        elegiveis.append(prod)
    if not elegiveis:
        return None, motivos_rejeicao
    elegiveis.sort(key=lambda x: x["_score_destino_v216"], reverse=True)
    return elegiveis[0], motivos_rejeicao


def _valor_terminal_estimado(valor: float, retorno_anual: float, data_atual: date, data_final: date | None) -> float:
    if data_final is None or data_final <= data_atual:
        return round(valor, 2)
    dias = max((data_final - data_atual).days, 0)
    retorno = max(float(retorno_anual or 0.0), 0.0)
    return round(float(valor) * ((1.0 + retorno) ** (dias / 365.0)), 2)


def _validar_invariante_v216(
    *,
    valor_recebido: float,
    valor_pago_com_recebido: float,
    valor_aportado: float,
    saldo_caixa_remanescente: float,
    tolerancia: float,
) -> tuple[bool, float]:
    diff = round(valor_recebido - (valor_pago_com_recebido + valor_aportado + saldo_caixa_remanescente), 2)
    return abs(diff) <= tolerancia, diff


def _construir_lote_planejado_v216(
    *,
    recebido: dict[str, Any],
    recebido_id: str,
    produto: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    valor_aporte: float,
    valor_terminal_com_aporte: float,
) -> dict[str, Any]:
    liquidez_dias = int(_safe_float(produto.get("liquidez_dias"), 0.0))
    carencia_dias = int(_safe_float(produto.get("carencia_dias"), 0.0))
    data_bloqueio_ate = data_atual + timedelta(days=max(liquidez_dias, carencia_dias))
    produto_key = str(produto.get("produto_key") or "")
    return {
        "id": f"{recebido_id}_ap_planejado_v216_{data_atual.isoformat()}",
        "investimento": str(produto.get("nome") or produto.get("produto_nome") or produto_key),
        "produto_key": produto_key,
        "produto_destino_key": produto_key,
        "valor_inicial": round(valor_aporte, 2),
        "valor_liquido_resgatavel": round(valor_aporte, 2),
        "principal_remanescente": round(valor_aporte, 2),
        "proxy_terminal_atual": _normalizar_proxy_terminal(produto.get("proxy_terminal_destino") or produto.get("proxy_terminal") or produto.get("score_final")),
        "retorno_anual_proxy_atual": _safe_float(produto.get("retorno_anual_proxy")),
        "liquidez_dias_atual": liquidez_dias,
        "carencia_dias_atual": carencia_dias,
        "liquidez_ate": data_bloqueio_ate if liquidez_dias > 0 else None,
        "carencia_ate": data_bloqueio_ate if carencia_dias > 0 else None,
        "data_aplicacao": data_atual,
        "data_recebimento": _coerce_date(recebido.get("data_recebimento")) or data_atual,
        "taxa_base_cdi": _safe_float(produto.get("taxa_base_cdi")),
        "taxa_bonus_cdi": _safe_float(produto.get("taxa_bonus_cdi")),
        "valor_terminal_estimado": round(valor_terminal_com_aporte, 2),
        "data_base_valor_terminal_estimado": data_atual,
        "data_final_valor_terminal_estimado": data_final,
        "valor_liquido_base_terminal_estimado": round(valor_aporte, 2),
        "origem_aporte_planejado_v216": True,
        "recebido_id_origem": recebido_id,
        "status_integracao_v216": STATUS_PROMOVIVEL_V216,
        "custo_fiscal_acumulado": 0.0,
    }


def _registrar_auditoria(estado: dict[str, Any], historico: list[dict[str, Any]] | None, payload: dict[str, Any]) -> None:
    estado.setdefault("auditoria_aportes_planejados_v216", []).append(payload)
    if historico is not None:
        historico.append({
            "tipo_evento": "aporte_planejado_v216",
            "data_evento": payload.get("data_evento"),
            "recebido_id": payload.get("recebido_id"),
            "status": payload.get("status_integracao_v216"),
            "valor_recebido": payload.get("valor_recebido"),
            "valor_pago_com_recebido": payload.get("valor_pago_com_recebido"),
            "valor_aportado": payload.get("valor_aportado"),
            "saldo_caixa_remanescente": payload.get("saldo_caixa_remanescente"),
            "produto_destino_key": payload.get("produto_destino_key"),
            "ganho_liquido_estimado": payload.get("ganho_liquido_estimado"),
            "invariante_v216_valida": payload.get("invariante_v216_valida"),
        })


def materializar_aportes_planejados_v216(
    estado: dict[str, Any],
    data_atual: date,
    config: dict[str, Any] | None = None,
    historico: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Materializa aportes planejados pós-pagamentos do dia.

    Invariante central: valor_recebido = valor_pago_com_recebido + valor_aportado + saldo_caixa_remanescente.

    A função implementa a transição controlada:
    recebido_futuro -> caixa/reserva -> aporte_planejado -> lote_aportado planejado.

    A materialização ocorre apenas após os pagamentos do próprio dia terem sido processados,
    preservando a precedência intradiária. O mesmo recebido não pode ser contado como caixa
    integral e como lote planejado simultaneamente: o valor aportado é debitado do recebido
    e o lote recebe `recebido_id_origem`.
    """
    politica = _config_aportes_v216(config)
    if not politica["habilitado"]:
        return []

    promovidos: list[dict[str, Any]] = []
    ja_aportados = _ids_recebidos_ja_aportados(estado)
    data_final = _coerce_date(estado.get("data_fim_recorte"))

    for recebido in list(estado.get("recebidos_nao_aportados_disponiveis") or []):
        recebido_id = _id_recebido(recebido)
        if not recebido_id:
            continue
        if recebido_id in ja_aportados or bool(recebido.get("aporte_planejado_materializado_v216")):
            payload = {
                "data_evento": data_atual.isoformat(),
                "recebido_id": recebido_id,
                "status_integracao_v216": STATUS_BLOQUEADO_DUPLA_CONTAGEM_V216,
                "motivo": "recebido_ja_materializado_como_lote_planejado",
            }
            _registrar_auditoria(estado, historico, payload)
            continue

        data_recebimento = _coerce_date(recebido.get("data_recebimento"))
        if data_recebimento is not None and data_recebimento > data_atual:
            continue

        valor_atual = _valor_atual_recebido(recebido)
        if valor_atual <= politica["tolerancia_monetaria"]:
            continue

        valor_recebido = _valor_original_recebido(recebido)
        valor_pago = round(_safe_float(recebido.get("valor_pago_com_recebido_v216")), 2)
        demanda_7d_total = _demanda_pagamentos_futuros(estado, data_atual, politica["reserva_dias"])
        capacidade_outras = _capacidade_caixa_outras_fontes(estado, recebido_id)
        reserva_dependente = round(max(demanda_7d_total - capacidade_outras, 0.0), 2)
        reserva_caixa = round(min(valor_atual, reserva_dependente), 2)
        valor_aporte = round(max(valor_atual - reserva_caixa, 0.0), 2)

        produto, motivos_produto = _selecionar_produto_destino_v216(estado, valor_aporte, politica)
        status = STATUS_PROMOVIVEL_V216
        motivo = "promovido_com_trava_reversao_v216"
        if valor_aporte <= politica["tolerancia_monetaria"]:
            status = STATUS_BLOQUEADO_RESERVA_V216
            motivo = "sem_excedente_pos_reserva_caixa"
        elif produto is None:
            status = STATUS_BLOQUEADO_PRODUTO_V216
            motivo = "sem_produto_destino_elegivel:" + "|".join(motivos_produto[:6])

        retorno = _safe_float((produto or {}).get("retorno_anual_proxy"))
        valor_terminal_sem_aporte = round(valor_aporte, 2)
        valor_terminal_com_aporte = _valor_terminal_estimado(valor_aporte, retorno, data_atual, data_final)
        ganho = round(valor_terminal_com_aporte - valor_terminal_sem_aporte, 2)
        if status == STATUS_PROMOVIVEL_V216 and politica["exigir_ganho_positivo"] and ganho <= politica["tolerancia_monetaria"]:
            status = STATUS_BLOQUEADO_GANHO_V216
            motivo = "ganho_liquido_estimado_nao_positivo_vs_sem_aporte"

        saldo_caixa_remanescente = round(valor_recebido - valor_pago - (valor_aporte if status == STATUS_PROMOVIVEL_V216 else 0.0), 2)
        inv_ok, diff = _validar_invariante_v216(
            valor_recebido=valor_recebido,
            valor_pago_com_recebido=valor_pago,
            valor_aportado=(valor_aporte if status == STATUS_PROMOVIVEL_V216 else 0.0),
            saldo_caixa_remanescente=saldo_caixa_remanescente,
            tolerancia=politica["tolerancia_monetaria"],
        )
        if status == STATUS_PROMOVIVEL_V216 and not inv_ok:
            status = STATUS_BLOQUEADO_INVARIANTE_V216
            motivo = "invariante_v216_invalida"

        payload = {
            "data_evento": data_atual.isoformat(),
            "recebido_id": recebido_id,
            "data_recebimento": _data_iso(recebido.get("data_recebimento")),
            "valor_recebido": round(valor_recebido, 2),
            "valor_pago_com_recebido": round(valor_pago, 2),
            "reserva_caixa_7d": round(reserva_caixa, 2),
            "valor_aportado": round(valor_aporte if status == STATUS_PROMOVIVEL_V216 else 0.0, 2),
            "saldo_caixa_remanescente": round(saldo_caixa_remanescente, 2),
            "diferenca_invariante": round(diff, 2),
            "invariante_v216_valida": bool(inv_ok),
            "produto_destino_key": str((produto or {}).get("produto_key") or ""),
            "produto_destino_nome": str((produto or {}).get("nome") or (produto or {}).get("produto_nome") or ""),
            "liquidez_dias_destino": int(_safe_float((produto or {}).get("liquidez_dias"))),
            "carencia_dias_destino": int(_safe_float((produto or {}).get("carencia_dias"))),
            "valor_terminal_sem_aporte": valor_terminal_sem_aporte,
            "valor_terminal_com_aporte": valor_terminal_com_aporte,
            "ganho_liquido_estimado": ganho,
            "status_integracao_v216": status,
            "motivo": motivo,
        }

        if status != STATUS_PROMOVIVEL_V216:
            _registrar_auditoria(estado, historico, payload)
            continue

        lote = _construir_lote_planejado_v216(
            recebido=recebido,
            recebido_id=recebido_id,
            produto=produto or {},
            data_atual=data_atual,
            data_final=data_final,
            valor_aporte=valor_aporte,
            valor_terminal_com_aporte=valor_terminal_com_aporte,
        )
        estado.setdefault("lotes_aportados", []).append(lote)
        recebido["valor_disponivel"] = round(max(valor_atual - valor_aporte, 0.0), 2)
        recebido["valor_aportado_planejado_v216"] = round(_safe_float(recebido.get("valor_aportado_planejado_v216")) + valor_aporte, 2)
        recebido["saldo_caixa_remanescente_v216"] = round(recebido["valor_disponivel"], 2)
        recebido["aporte_planejado_materializado_v216"] = True
        recebido["lote_planejado_id_v216"] = lote["id"]
        payload["lote_planejado_id"] = lote["id"]
        _registrar_auditoria(estado, historico, payload)
        promovidos.append(lote)

    return promovidos


def avaliar_gate_economico_aportes_planejados_v220(
    *,
    delta_patrimonio_terminal_proxy: float,
    delta_perda_terminal_total: float,
    delta_penalidade_estrategica_total: float,
    delta_deficit_total: float,
    tolerancia: float = 0.01,
) -> dict[str, Any]:
    """Gate econômico obrigatório da V220 para aportes planejados."""
    tol = max(_safe_float(tolerancia, 0.01), 0.0)
    falhas: list[str] = []
    if _safe_float(delta_patrimonio_terminal_proxy) < -tol:
        falhas.append("reduz_patrimonio_terminal_proxy")
    if _safe_float(delta_perda_terminal_total) > tol:
        falhas.append("aumenta_perda_terminal_total")
    if _safe_float(delta_penalidade_estrategica_total) > tol:
        falhas.append("aumenta_penalidade_estrategica_total")
    if _safe_float(delta_deficit_total) > tol:
        falhas.append("aumenta_deficit_total")
    status = STATUS_PROMOVIVEL_ECONOMICO_V220 if not falhas else STATUS_BLOQUEADO_GATE_ECONOMICO_V220
    return {
        "status_gate_economico_v220": status,
        "gate_economico_aprovado_v220": not falhas,
        "falhas_gate_economico_v220": " | ".join(falhas),
        "delta_patrimonio_terminal_proxy": round(_safe_float(delta_patrimonio_terminal_proxy), 2),
        "delta_perda_terminal_total": round(_safe_float(delta_perda_terminal_total), 2),
        "delta_penalidade_estrategica_total": round(_safe_float(delta_penalidade_estrategica_total), 2),
        "delta_deficit_total": round(_safe_float(delta_deficit_total), 2),
    }
