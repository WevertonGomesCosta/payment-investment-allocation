"""Agregador temporal de pacotes temporais para a saída canônica.

V17-F0-V.4I cria um construtor único que monta, de forma coordenada, os
pacotes temporais temporal da Etapa 4. O módulo não altera replay efetivo,
ledger efetivo, estado temporal efetivo, saída canônica ou saída observável.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import pandas as pd

from nucleo.pacote_auditoria_temporal import PacoteAuditoriaTemporal, construir_pacote_auditoria_temporal
from nucleo.pacote_estado_temporal import PacoteEstadoTemporal, construir_pacote_estado_temporal
from nucleo.pacote_ledger_temporal import construir_pacote_ledger_temporal
from nucleo.pacote_ledger_temporal_operacional import (
    PacoteLedgerTemporalOperacional,
    construir_pacote_ledger_temporal_operacional,
)
from nucleo.pacote_replay_passado import PacoteReplayPassado, construir_pacote_replay_passado
from nucleo.saida_canonica import _mapa_pagamentos_central, _quadro_futuro_preferencial



def _retorno_ledger_temporal_vazio_oficial(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Contrato vazio oficial para o ledger temporal.

    ME-521B: mantém o contrato consumido pelos pacotes temporais sem acionar
    o ledger removido na ME-521D, validado por baseline e paridade oficiais.
    """
    return {
        "eventos": [],
        "fifo_candidatos_avaliados": [],
    }

VERSAO_PACOTES_TEMPORAIS_AGREGADOS = "V17-F0-V.4I-temporal"


@dataclass(slots=True)
class PacotesTemporaisAgregadosSaida:
    """Envelope temporal dos pacotes temporais necessários à saída canônica."""

    versao: str
    modo_execucao: str
    data_referencia: Any
    pacote_replay_passado: PacoteReplayPassado
    pacote_ledger_temporal_operacional: PacoteLedgerTemporalOperacional
    pacote_estado_temporal: PacoteEstadoTemporal
    pacote_auditoria_temporal: PacoteAuditoriaTemporal
    auditoria_agregador_temporal: dict[str, Any] = field(default_factory=dict)
    validacao_agregador_temporal: dict[str, Any] = field(default_factory=dict)
    metadados_origem: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_dict(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return dict(valor)
    if isinstance(valor, Mapping):
        return dict(valor.items())
    return {}


def _qtd(valor: Any) -> int:
    try:
        if valor is None:
            return 0
        if isinstance(valor, pd.DataFrame):
            return int(len(valor))
        if hasattr(valor, "__len__"):
            return int(len(valor))
    except Exception:
        return 0
    return 0


def _inferir_data_referencia(*, contexto: Any = None, pacote_auditoria: Any = None, pacote_estado: Any = None) -> Any:
    for origem in (pacote_auditoria, pacote_estado):
        data = getattr(origem, "data_referencia", None)
        if data not in (None, ""):
            return data.isoformat() if hasattr(data, "isoformat") else data
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    return data.isoformat() if hasattr(data, "isoformat") else data


def _validacao_ok(pacote: Any, campo: str) -> bool:
    validacao = _as_dict(getattr(pacote, campo, {}))
    return bool(validacao.get("ok", False))


def _montar_auditoria_agregador(
    *,
    pacote_replay: PacoteReplayPassado,
    pacote_ledger_operacional: PacoteLedgerTemporalOperacional,
    pacote_estado: PacoteEstadoTemporal,
    pacote_auditoria: PacoteAuditoriaTemporal,
    contrato_ledger: Mapping[str, Any],
    quadro_futuro: Any,
    mapa_central: Mapping[str, Any],
) -> dict[str, Any]:
    auditoria_ledger = _as_dict(getattr(pacote_ledger_operacional, "auditoria_ledger_temporal", {}))
    auditoria_estado = _as_dict(getattr(pacote_estado, "auditoria_estado_temporal", {}))
    auditoria_temporal = _as_dict(getattr(pacote_auditoria, "auditoria_residuos_temporais", {}))

    return {
        "ok": True,
        "modo_operacional_temporal": True,
        "origem_execucao": "construir_pacotes_temporais_agregados_saida",
        "versao_microetapa": "V17-F0-V.4I",
        "contrato_alvo": "PacotesTemporaisAgregadosSaida",
        "qtd_quadro_futuro": _qtd(quadro_futuro),
        "qtd_mapa_central": len(dict(mapa_central or {})),
        "qtd_eventos_contrato_ledger": _qtd(contrato_ledger.get("eventos", [])),
        "qtd_fifo_contrato_ledger": _qtd(contrato_ledger.get("fifo_candidatos_avaliados", [])),
        "qtd_lotes_replay": _qtd(getattr(pacote_replay, "lotes_apos_replay", [])),
        "qtd_log_movimentos_passados": _qtd(getattr(pacote_replay, "log_movimentos_passados", [])),
        "qtd_eventos_ledger_operacional": _qtd(getattr(pacote_ledger_operacional, "eventos_temporais", [])),
        "qtd_fifo_ledger_operacional": _qtd(getattr(pacote_ledger_operacional, "fifo_candidatos_avaliados", [])),
        "qtd_estado_lotes_por_data": _qtd(getattr(pacote_estado, "estado_lotes_por_data", [])),
        "qtd_estado_lotes_final": _qtd(getattr(pacote_estado, "estado_lotes_final", [])),
        "auditoria_temporal_global_ok": bool(getattr(pacote_auditoria, "validacao_temporal_global", {}).get("ok")),
        "fonte_primaria_switching_ledger": auditoria_ledger.get("fonte_primaria_switching_ledger"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_ledger.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_contrato_ledger_dict": auditoria_temporal.get("usa_contrato_ledger_dict"),
        "saida_chama_ledger_diretamente_fluxo_atual": auditoria_temporal.get("saida_chama_ledger_diretamente"),
        "campos_vazios_ledger_auditados": auditoria_ledger.get("campos_vazios_auditados"),
        "campos_vazios_estado_auditados": auditoria_estado.get("campos_vazios_auditados"),
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "nao_altera_estado_temporal_efetivo": True,
        "nao_altera_saida_canonica": True,
    }


def _montar_validacao_agregador(
    *,
    pacote_replay: PacoteReplayPassado,
    pacote_ledger_operacional: PacoteLedgerTemporalOperacional,
    pacote_estado: PacoteEstadoTemporal,
    pacote_auditoria: PacoteAuditoriaTemporal,
    auditoria_agregador: Mapping[str, Any],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []

    if not _validacao_ok(pacote_replay, "validacao_replay"):
        erros.append("validacao_replay_nao_ok")
    if not _validacao_ok(pacote_ledger_operacional, "validacao_ledger_temporal"):
        erros.append("validacao_ledger_temporal_nao_ok")
    if not _validacao_ok(pacote_estado, "validacao_estado_temporal"):
        erros.append("validacao_estado_temporal_nao_ok")
    if not bool(getattr(pacote_auditoria, "validacao_temporal_global", {}).get("ok")):
        erros.append("validacao_temporal_global_nao_ok")

    if int(auditoria_agregador.get("qtd_eventos_contrato_ledger") or 0) != int(auditoria_agregador.get("qtd_eventos_ledger_operacional") or 0):
        erros.append("qtd_eventos_ledger_operacional_diverge_contrato_ledger")
    if int(auditoria_agregador.get("qtd_fifo_contrato_ledger") or 0) != int(auditoria_agregador.get("qtd_fifo_ledger_operacional") or 0):
        erros.append("qtd_fifo_ledger_operacional_diverge_contrato_ledger")
    if int(auditoria_agregador.get("qtd_estado_lotes_por_data") or 0) <= 0:
        erros.append("estado_lotes_por_data_nao_materializado")
    if int(auditoria_agregador.get("qtd_estado_lotes_final") or 0) <= 0:
        erros.append("estado_lotes_final_nao_materializado")
    if auditoria_agregador.get("fonte_primaria_switching_ledger") != "switching_canonico":
        erros.append("switching_canonico_nao_e_fonte_primaria_ledger")
    if auditoria_agregador.get("usa_planilha_bruta_como_fonte_primaria") is not False:
        erros.append("planilha_bruta_usada_como_fonte_primaria")

    if auditoria_agregador.get("usa_contrato_ledger_dict") is True:
        avisos.append("contrato_vazio_oficial_usado_como_origem_temporal")
    if auditoria_agregador.get("saida_chama_ledger_diretamente_fluxo_atual"):
        avisos.append("saida_nao_chama_ledger_removido_fluxo_atual")

    return {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": avisos,
        "evidencias": {
            "qtd_eventos_contrato_ledger": auditoria_agregador.get("qtd_eventos_contrato_ledger"),
            "qtd_eventos_ledger_operacional": auditoria_agregador.get("qtd_eventos_ledger_operacional"),
            "qtd_fifo_contrato_ledger": auditoria_agregador.get("qtd_fifo_contrato_ledger"),
            "qtd_fifo_ledger_operacional": auditoria_agregador.get("qtd_fifo_ledger_operacional"),
            "qtd_estado_lotes_por_data": auditoria_agregador.get("qtd_estado_lotes_por_data"),
            "qtd_estado_lotes_final": auditoria_agregador.get("qtd_estado_lotes_final"),
            "fonte_primaria_switching_ledger": auditoria_agregador.get("fonte_primaria_switching_ledger"),
        },
    }


def construir_pacotes_temporais_agregados_saida(
    contexto: Any,
    *,
    modo_execucao: str = "operacional_temporal",
) -> PacotesTemporaisAgregadosSaida:
    """Constrói os quatro pacotes temporais temporal da Etapa 4 em cadeia única.

    A função não altera o contexto e não substitui nenhuma chamada da saída
    canônica. Ela apenas centraliza a construção V4D→V4G para futuras auditorias
    de equivalência.
    """
    pacote_replay = construir_pacote_replay_passado(
        getattr(contexto, "replay_passado", None),
        contexto=contexto,
    )

    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    contrato_ledger = _retorno_ledger_temporal_vazio_oficial(quadro_futuro, mapa_central, contexto) or {}

    pacote_ledger_temporal = construir_pacote_ledger_temporal(
        quadro_futuro,
        mapa_central,
        contexto,
        contrato_ledger=contrato_ledger,
    )
    pacote_ledger_operacional = construir_pacote_ledger_temporal_operacional(
        contrato_ledger,
        pacote_ledger_temporal,
        contexto=contexto,
    )
    pacote_estado = construir_pacote_estado_temporal(
        pacote_replay,
        pacote_ledger_operacional,
        contexto=contexto,
    )
    pacote_auditoria = construir_pacote_auditoria_temporal(
        pacote_replay,
        pacote_ledger_operacional,
        pacote_estado,
        contexto=contexto,
    )

    auditoria = _montar_auditoria_agregador(
        pacote_replay=pacote_replay,
        pacote_ledger_operacional=pacote_ledger_operacional,
        pacote_estado=pacote_estado,
        pacote_auditoria=pacote_auditoria,
        contrato_ledger=contrato_ledger,
        quadro_futuro=quadro_futuro,
        mapa_central=mapa_central,
    )
    validacao = _montar_validacao_agregador(
        pacote_replay=pacote_replay,
        pacote_ledger_operacional=pacote_ledger_operacional,
        pacote_estado=pacote_estado,
        pacote_auditoria=pacote_auditoria,
        auditoria_agregador=auditoria,
    )
    auditoria["ok"] = bool(validacao.get("ok"))

    metadados = {
        "versao_microetapa": "V17-F0-V.4I",
        "modo_operacional_temporal": True,
        "adaptador": "construir_pacotes_temporais_agregados_saida",
        "ordem_construcao": [
            "PacoteReplayPassado",
            "PacoteLedgerTemporalOperacional",
            "PacoteEstadoTemporal",
            "PacoteAuditoriaTemporal",
        ],
        "nao_altera_contexto": True,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "nao_altera_estado_temporal_efetivo": True,
        "nao_altera_saida_canonica": True,
    }

    return PacotesTemporaisAgregadosSaida(
        versao=VERSAO_PACOTES_TEMPORAIS_AGREGADOS,
        modo_execucao=modo_execucao,
        data_referencia=_inferir_data_referencia(
            contexto=contexto,
            pacote_auditoria=pacote_auditoria,
            pacote_estado=pacote_estado,
        ),
        pacote_replay_passado=pacote_replay,
        pacote_ledger_temporal_operacional=pacote_ledger_operacional,
        pacote_estado_temporal=pacote_estado,
        pacote_auditoria_temporal=pacote_auditoria,
        auditoria_agregador_temporal=auditoria,
        validacao_agregador_temporal=validacao,
        metadados_origem=metadados,
    )
