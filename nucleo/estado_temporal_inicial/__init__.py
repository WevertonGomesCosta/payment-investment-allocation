from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from typing import Any


_LEGACY_NAME = "nucleo._estado_temporal_inicial_legacy"
_LEGACY_PATH = Path(__file__).resolve().parents[1] / "estado_temporal_inicial.py"


def _carregar_legado():
    modulo = sys.modules.get(_LEGACY_NAME)
    if modulo is not None:
        return modulo
    spec = importlib.util.spec_from_file_location(_LEGACY_NAME, _LEGACY_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo legado em {_LEGACY_PATH}")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[_LEGACY_NAME] = modulo
    spec.loader.exec_module(modulo)
    return modulo


_legacy = _carregar_legado()
for _nome in getattr(_legacy, "__all__", []):
    globals()[_nome] = getattr(_legacy, _nome)

EstadoTemporalInicial = _legacy.EstadoTemporalInicial
auditar_estado_temporal_inicial = _legacy.auditar_estado_temporal_inicial


def _registros(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    to_dict = getattr(valor, "to_dict", None)
    if callable(to_dict):
        try:
            return [dict(item) for item in to_dict("records")]
        except TypeError:
            pass
    if isinstance(valor, list):
        return [dict(item) for item in valor if isinstance(item, dict)]
    return []


def _texto(*valores: Any) -> str:
    for valor in valores:
        texto = str(valor or "").strip()
        if texto and texto.lower() not in {"nan", "none", "n/d", "nd"}:
            return texto
    return ""


def _numero(*valores: Any, padrao: float = 0.0) -> float:
    for valor in valores:
        if valor in (None, "") or isinstance(valor, bool):
            continue
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            continue
        if numero == numero:
            return numero
    return float(padrao)


def _inteiro(*valores: Any, padrao: int = 0) -> int:
    return int(round(_numero(*valores, padrao=float(padrao))))


def _bool(valor: Any, padrao: bool = False) -> bool:
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return padrao
    texto = str(valor).strip().casefold()
    if texto in {"sim", "s", "true", "1", "yes", "ativo", "elegivel", "elegível"}:
        return True
    if texto in {"nao", "não", "n", "false", "0", "no", "inativo", "inelegivel", "inelegível"}:
        return False
    return padrao


def _normalizar_nome(valor: Any) -> str:
    return " ".join(str(valor or "").strip().casefold().split())


def _data_maxima_estado(estado: EstadoTemporalInicial) -> date:
    datas: list[date] = [estado.data_referencia]
    for colecao, campos in (
        (estado.pagamentos_temporais, ("data", "data_pagamento", "data_vencimento")),
        (estado.recebidos_temporais, ("data_recebimento", "data_disponibilidade", "data")),
        (estado.switching_temporal_realizado, ("data_switching", "data_aplicacao")),
    ):
        for item in colecao or []:
            for campo in campos:
                valor = item.get(campo)
                if isinstance(valor, date):
                    datas.append(valor)
                    break
    return max(datas)


def _destinos_switching(contexto: Any) -> list[dict[str, Any]]:
    ranking = getattr(contexto, "ranking_carteira", None)
    registros = _registros(getattr(ranking, "quadro_destinos_switch", None))
    carteira = _registros(getattr(getattr(contexto, "carteira_canonica", None), "quadro_canonico", None))
    carteira_por_nome = {
        _normalizar_nome(_texto(item.get("nome"), item.get("Nome"))): item
        for item in carteira
        if _texto(item.get("nome"), item.get("Nome"))
    }
    destinos: list[dict[str, Any]] = []
    for posicao, item in enumerate(registros, start=1):
        nome = _texto(item.get("nome"), item.get("Nome"), item.get("Produto"))
        if not nome:
            continue
        produto_meta = carteira_por_nome.get(_normalizar_nome(nome), {})
        retorno = _numero(item.get("retorno_anual_proxy"), item.get("Retorno_Proxy_aa"), padrao=0.0)
        if abs(retorno) > 3.0:
            retorno /= 100.0
        destinos.append(
            {
                "rank_destino": _inteiro(item.get("rank_destino"), item.get("Rank_Consolidado_Prazo_Ativos"), padrao=posicao),
                "produto_key": _texto(item.get("produto_key")),
                "nome": nome,
                "retorno_anual_proxy": retorno,
                "proxy_terminal_destino": _numero(item.get("proxy_terminal_destino"), padrao=0.0),
                "liquidez_dias": max(_inteiro(item.get("liquidez_dias"), item.get("Liquidez_Dias"), padrao=0), 0),
                "carencia_dias": max(_inteiro(item.get("carencia_dias"), item.get("Carência_Dias"), padrao=0), 0),
                "aplicacao_minima": max(_numero(item.get("aplicacao_minima"), item.get("Aplicação_Mínima"), padrao=0.0), 0.0),
                "aplicacao_maxima": max(_numero(item.get("aplicacao_maxima"), item.get("Aplicação_Máxima"), padrao=0.0), 0.0),
                "somente_combo": _bool(item.get("somente_combo"), False),
                "elegivel_switch_in": _bool(item.get("elegivel_switch_in"), True),
                "tipo_produto": _texto(item.get("tipo_produto"), item.get("Tipo")),
                "isento_ir": _bool(item.get("isento_ir"), _bool(produto_meta.get("isento_ir"), False)),
                "regra_iof": _texto(item.get("regra_iof"), produto_meta.get("regra_iof"), "regressiva_30d"),
            }
        )
    destinos.sort(key=lambda item: (item["rank_destino"], -item["retorno_anual_proxy"], item["nome"]))
    return destinos


def _enriquecer_fontes(estado: EstadoTemporalInicial, contexto: Any, destinos: list[dict[str, Any]]) -> None:
    inventario_obj = getattr(getattr(contexto, "dados_operacionais", None), "inventario_canonico", None)
    inventario = _registros(inventario_obj)
    carteira = _registros(getattr(getattr(contexto, "carteira_canonica", None), "quadro_canonico", None))
    carteira_por_nome = {
        _normalizar_nome(_texto(item.get("nome"), item.get("Nome"))): item
        for item in carteira
        if _texto(item.get("nome"), item.get("Nome"))
    }
    inventario_por_lote = {
        _texto(item.get("lote_id"), item.get("Lote (ID)"), item.get("lote")): item
        for item in inventario
        if _texto(item.get("lote_id"), item.get("Lote (ID)"), item.get("lote"))
    }
    destinos_por_nome = {_normalizar_nome(item["nome"]): item for item in destinos}

    for item in estado.inventario_temporal or []:
        lote_id = _texto(item.get("lote_id"))
        origem = inventario_por_lote.get(lote_id, {})
        produto = _texto(
            origem.get("produto"),
            origem.get("investimento"),
            origem.get("carteira"),
            origem.get("nome_produto"),
            origem.get("Produto"),
        )
        ranking = destinos_por_nome.get(_normalizar_nome(produto), {})
        produto_meta = carteira_por_nome.get(_normalizar_nome(produto), {})
        item.update(
            {
                "produto": produto,
                "data_vencimento": origem.get("data_vencimento") or origem.get("vencimento"),
                "carencia_ate": origem.get("carencia_ate") or origem.get("data_fim_carencia"),
                "retorno_anual_proxy": _numero(
                    origem.get("retorno_anual_proxy"),
                    ranking.get("retorno_anual_proxy"),
                    padrao=0.0,
                ),
                "liquidez_dias": max(_inteiro(origem.get("liquidez_dias"), produto_meta.get("liquidez_dias"), padrao=0), 0),
                "isento_ir": _bool(origem.get("isento_ir"), _bool(produto_meta.get("isento_ir"), False)),
                "regra_iof": _texto(origem.get("regra_iof"), produto_meta.get("regra_iof"), "regressiva_30d"),
                "data_base_fiscal": origem.get("data_base_fiscal") or origem.get("data_aplicacao"),
                "elegivel_switch_out": _bool(origem.get("elegivel_switch_out"), True),
            }
        )

    inventario_estado = {
        _texto(item.get("lote_id")): item
        for item in estado.inventario_temporal or []
        if _texto(item.get("lote_id"))
    }
    for fonte in estado.fontes_temporais or []:
        lote_id = _texto(fonte.get("lote_id"), fonte.get("fonte_id"))
        lote = inventario_estado.get(lote_id, {})
        produto = _texto(fonte.get("produto"), fonte.get("investimento"), lote.get("produto"))
        ranking = destinos_por_nome.get(_normalizar_nome(produto), {})
        produto_meta = carteira_por_nome.get(_normalizar_nome(produto), {})
        fonte.update(
            {
                "produto": produto,
                "retorno_anual_proxy": _numero(
                    fonte.get("retorno_anual_proxy"),
                    lote.get("retorno_anual_proxy"),
                    ranking.get("retorno_anual_proxy"),
                    padrao=0.0,
                ),
                "data_vencimento": fonte.get("data_vencimento") or lote.get("data_vencimento"),
                "carencia_ate": fonte.get("carencia_ate") or lote.get("carencia_ate"),
                "liquidez_dias": max(_inteiro(fonte.get("liquidez_dias"), lote.get("liquidez_dias"), produto_meta.get("liquidez_dias"), padrao=0), 0),
                "isento_ir": _bool(fonte.get("isento_ir"), _bool(lote.get("isento_ir"), _bool(produto_meta.get("isento_ir"), False))),
                "regra_iof": _texto(fonte.get("regra_iof"), lote.get("regra_iof"), produto_meta.get("regra_iof"), "regressiva_30d"),
                "data_base_fiscal": fonte.get("data_base_fiscal") or lote.get("data_base_fiscal") or lote.get("data_aplicacao"),
                "elegivel_switch_out": _bool(fonte.get("elegivel_switch_out"), lote.get("elegivel_switch_out", True)),
            }
        )


def construir_estado_temporal_inicial(contexto: Any) -> EstadoTemporalInicial:
    estado = _legacy.construir_estado_temporal_inicial(contexto)
    destinos = _destinos_switching(contexto)
    _enriquecer_fontes(estado, contexto, destinos)
    estado.metadados.update(
        {
            "versao_estado_temporal": "ME-535-MOTOR-FUNCIONAL",
            "destinos_switching": destinos,
            "qtd_destinos_switching": len(destinos),
            "data_horizonte_terminal": _data_maxima_estado(estado),
            "funcao_objetivo_requerida": "patrimonio_liquido_terminal_liquido",
            "parametros_fiscais_materializados": True,
            "pacotes_normativos": [
                "no_action",
                "switch_only",
                "pay_only",
                "switch_then_pay",
                "pay_then_switch",
            ],
        }
    )
    auditoria = dict(estado.auditoria_temporal or {})
    resumo = dict(auditoria.get("resumo", {}) or {})
    resumo.update(
        {
            "qtd_destinos_switching": len(destinos),
            "fontes_enriquecidas_economicamente": len(estado.fontes_temporais or []),
        }
    )
    auditoria["resumo"] = resumo
    estado.auditoria_temporal = auditoria
    return estado


__all__ = sorted(set(getattr(_legacy, "__all__", [])) | {
    "EstadoTemporalInicial",
    "auditar_estado_temporal_inicial",
    "construir_estado_temporal_inicial",
})
