"""PacoteAuditoriaTemporal temporal.

V17-F0-V.4G centraliza auditorias temporais já existentes em um pacote único,
sem alterar replay efetivo, ledger efetivo, estado temporal efetivo, saída
canônica ou saída observável.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


VERSAO_PACOTE_AUDITORIA_TEMPORAL = "V17-F0-V.4G-temporal"


@dataclass(slots=True)
class PacoteAuditoriaTemporal:
    """Contrato temporal de auditoria temporal da Etapa 4."""

    versao: str
    modo_execucao: str
    data_referencia: Any
    auditoria_replay: dict[str, Any] = field(default_factory=dict)
    auditoria_ledger: dict[str, Any] = field(default_factory=dict)
    auditoria_estado_temporal: dict[str, Any] = field(default_factory=dict)
    auditoria_fontes_elegiveis: dict[str, Any] = field(default_factory=dict)
    auditoria_switching_temporal: dict[str, Any] = field(default_factory=dict)
    auditoria_invariantes: dict[str, Any] = field(default_factory=dict)
    auditoria_residuos_legados: dict[str, Any] = field(default_factory=dict)
    validacao_temporal_global: dict[str, Any] = field(default_factory=dict)
    metadados_origem: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_dict(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return dict(valor)
    if isinstance(valor, Mapping):
        return dict(valor.items())
    return {}


def _as_list(valor: Any) -> list[Any]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return list(valor)
    if isinstance(valor, tuple):
        return list(valor)
    return []


def _inferir_data_referencia(
    *,
    pacote_replay_passado: Any = None,
    pacote_ledger_operacional: Any = None,
    pacote_estado_temporal: Any = None,
    contexto: Any = None,
) -> Any:
    for origem in (pacote_estado_temporal, pacote_ledger_operacional, pacote_replay_passado):
        data = getattr(origem, "data_referencia", None)
        if data not in (None, ""):
            return data.isoformat() if hasattr(data, "isoformat") else data
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    return data.isoformat() if hasattr(data, "isoformat") else data


def _validacao_ok(pacote: Any, campo: str) -> bool:
    validacao = _as_dict(getattr(pacote, campo, {}))
    return bool(validacao.get("ok", False))


def _auditoria_fontes(pacote_ledger_operacional: Any, pacote_estado_temporal: Any) -> dict[str, Any]:
    fontes_por_pagamento = _as_list(getattr(pacote_ledger_operacional, "fontes_elegiveis_por_pagamento", []))
    fontes_por_data = _as_list(getattr(pacote_estado_temporal, "fontes_disponiveis_por_data", []))
    fifo = _as_list(getattr(pacote_ledger_operacional, "fifo_candidatos_avaliados", []))
    return {
        "ok": len(fontes_por_pagamento) > 0 and len(fontes_por_data) > 0,
        "qtd_fontes_elegiveis_por_pagamento": len(fontes_por_pagamento),
        "qtd_fontes_disponiveis_por_data": len(fontes_por_data),
        "qtd_fifo_candidatos_avaliados": len(fifo),
        "fontes_por_pagamento_materializadas": len(fontes_por_pagamento) > 0,
        "fontes_por_data_materializadas": len(fontes_por_data) > 0,
    }


def _auditoria_switching(pacote_ledger_operacional: Any, pacote_estado_temporal: Any) -> dict[str, Any]:
    auditoria_ledger = _as_dict(getattr(pacote_ledger_operacional, "auditoria_ledger_temporal", {}))
    migracoes = _as_list(getattr(pacote_estado_temporal, "migracoes_por_data", []))
    return {
        "ok": auditoria_ledger.get("fonte_primaria_switching_ledger") == "switching_canonico",
        "fonte_primaria_switching_ledger": auditoria_ledger.get("fonte_primaria_switching_ledger"),
        "fallback_legado_switching_auditavel": auditoria_ledger.get("fallback_legado_switching_auditavel"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_ledger.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_planilha_bruta_apenas_fallback": auditoria_ledger.get("usa_planilha_bruta_apenas_fallback"),
        "usa_switching_canonico_como_fonte_primaria": auditoria_ledger.get("usa_switching_canonico_como_fonte_primaria"),
        "qtd_migracoes_por_data": len(migracoes),
        "migracoes_por_data_materializadas": len(migracoes) > 0,
    }


def _auditoria_invariantes(
    *,
    pacote_replay_passado: Any,
    pacote_ledger_operacional: Any,
    pacote_estado_temporal: Any,
) -> dict[str, Any]:
    validacao_replay_ok = _validacao_ok(pacote_replay_passado, "validacao_replay")
    validacao_ledger_ok = _validacao_ok(pacote_ledger_operacional, "validacao_ledger_temporal")
    validacao_estado_ok = _validacao_ok(pacote_estado_temporal, "validacao_estado_temporal")
    auditoria_ledger = _as_dict(getattr(pacote_ledger_operacional, "auditoria_ledger_temporal", {}))
    estado_final = _as_list(getattr(pacote_estado_temporal, "estado_lotes_final", []))
    estado_por_data = _as_list(getattr(pacote_estado_temporal, "estado_lotes_por_data", []))

    return {
        "ok": all([
            validacao_replay_ok,
            validacao_ledger_ok,
            validacao_estado_ok,
            auditoria_ledger.get("fonte_primaria_switching_ledger") == "switching_canonico",
            auditoria_ledger.get("usa_planilha_bruta_como_fonte_primaria") is False,
            len(estado_por_data) > 0,
            len(estado_final) > 0,
        ]),
        "validacao_replay_ok": validacao_replay_ok,
        "validacao_ledger_ok": validacao_ledger_ok,
        "validacao_estado_ok": validacao_estado_ok,
        "estado_lotes_por_data_materializado": len(estado_por_data) > 0,
        "estado_lotes_final_materializado": len(estado_final) > 0,
        "switching_canonico_usado_como_fonte_primaria": auditoria_ledger.get("fonte_primaria_switching_ledger") == "switching_canonico",
        "fallback_switching_bruto_nao_usado_como_fonte_primaria": auditoria_ledger.get("usa_planilha_bruta_como_fonte_primaria") is False,
        "saida_canonica_nao_recalculada_pelo_pacote_temporal": True,
    }


def _auditoria_residuos(pacote_ledger_operacional: Any, pacote_estado_temporal: Any) -> dict[str, Any]:
    auditoria_ledger = _as_dict(getattr(pacote_ledger_operacional, "auditoria_ledger_temporal", {}))
    auditoria_estado = _as_dict(getattr(pacote_estado_temporal, "auditoria_estado_temporal", {}))
    campos_vazios = []
    campos_vazios.extend(_as_list(auditoria_ledger.get("campos_vazios_auditados")))
    campos_vazios.extend(_as_list(auditoria_estado.get("campos_vazios_auditados")))
    return {
        "ok": True,
        "usa_contexto_amplo": auditoria_ledger.get("usa_contexto_amplo"),
        "usa_pacote_planilha": "n/d_temporal",
        "usa_quadros_brutos": "n/d_temporal",
        "usa_planilha_bruta_como_fonte_primaria": auditoria_ledger.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_planilha_bruta_apenas_fallback": auditoria_ledger.get("usa_planilha_bruta_apenas_fallback"),
        "usa_retorno_ledger_dict_legado": auditoria_ledger.get("retorno_dict_legado_usado_como_origem", False),
        "saida_chama_ledger_diretamente": False,
        "campos_vazios_auditados": campos_vazios,
    }


def _montar_validacao_global(
    *,
    auditoria_replay: dict[str, Any],
    auditoria_ledger: dict[str, Any],
    auditoria_estado: dict[str, Any],
    auditoria_fontes: dict[str, Any],
    auditoria_switching: dict[str, Any],
    auditoria_invariantes: dict[str, Any],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []

    if not auditoria_replay:
        erros.append("auditoria_replay_ausente")
    if not auditoria_ledger:
        erros.append("auditoria_ledger_ausente")
    if not auditoria_estado:
        erros.append("auditoria_estado_temporal_ausente")
    if not auditoria_fontes.get("ok"):
        erros.append("auditoria_fontes_elegiveis_incompleta")
    if not auditoria_switching.get("ok"):
        erros.append("auditoria_switching_temporal_incompleta")
    if not auditoria_invariantes.get("ok"):
        erros.append("auditoria_invariantes_incompleta")

    if auditoria_switching.get("migracoes_por_data_materializadas") is False:
        avisos.append("migracoes_por_data_vazio_auditado")
    if auditoria_replay.get("modo_operacional_temporal") is True:
        avisos.append("auditoria_replay_origem_temporal_operacional")
    if auditoria_ledger.get("retorno_dict_legado_usado_como_origem") is True:
        avisos.append("contrato_vazio_oficial_usado_como_origem_ledger_temporal")

    return {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": avisos,
        "evidencias": {
            "auditoria_replay_presente": bool(auditoria_replay),
            "auditoria_ledger_presente": bool(auditoria_ledger),
            "auditoria_estado_temporal_presente": bool(auditoria_estado),
            "auditoria_fontes_ok": auditoria_fontes.get("ok"),
            "auditoria_switching_ok": auditoria_switching.get("ok"),
            "auditoria_invariantes_ok": auditoria_invariantes.get("ok"),
        },
    }


def construir_pacote_auditoria_temporal(
    pacote_replay_passado: Any,
    pacote_ledger_operacional: Any,
    pacote_estado_temporal: Any,
    *,
    contexto: Any = None,
    modo_execucao: str = "operacional_temporal",
) -> PacoteAuditoriaTemporal:
    """Centraliza auditorias temporais dos pacotes temporal da Etapa 4."""
    data_referencia = _inferir_data_referencia(
        pacote_replay_passado=pacote_replay_passado,
        pacote_ledger_operacional=pacote_ledger_operacional,
        pacote_estado_temporal=pacote_estado_temporal,
        contexto=contexto,
    )

    auditoria_replay = _as_dict(getattr(pacote_replay_passado, "auditoria_replay", {}))
    auditoria_ledger = _as_dict(getattr(pacote_ledger_operacional, "auditoria_ledger_temporal", {}))
    auditoria_estado = _as_dict(getattr(pacote_estado_temporal, "auditoria_estado_temporal", {}))
    auditoria_fontes = _auditoria_fontes(pacote_ledger_operacional, pacote_estado_temporal)
    auditoria_switching = _auditoria_switching(pacote_ledger_operacional, pacote_estado_temporal)
    auditoria_invariantes = _auditoria_invariantes(
        pacote_replay_passado=pacote_replay_passado,
        pacote_ledger_operacional=pacote_ledger_operacional,
        pacote_estado_temporal=pacote_estado_temporal,
    )
    auditoria_residuos = _auditoria_residuos(pacote_ledger_operacional, pacote_estado_temporal)
    validacao = _montar_validacao_global(
        auditoria_replay=auditoria_replay,
        auditoria_ledger=auditoria_ledger,
        auditoria_estado=auditoria_estado,
        auditoria_fontes=auditoria_fontes,
        auditoria_switching=auditoria_switching,
        auditoria_invariantes=auditoria_invariantes,
    )

    metadados = {
        "versao_microetapa": "V17-F0-V.4G",
        "modo_operacional_temporal": True,
        "adaptador": "construir_pacote_auditoria_temporal",
        "origem_replay": type(pacote_replay_passado).__name__,
        "origem_ledger": type(pacote_ledger_operacional).__name__,
        "origem_estado": type(pacote_estado_temporal).__name__,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "nao_altera_estado_temporal_efetivo": True,
        "nao_altera_saida_canonica": True,
    }

    return PacoteAuditoriaTemporal(
        versao=VERSAO_PACOTE_AUDITORIA_TEMPORAL,
        modo_execucao=modo_execucao,
        data_referencia=data_referencia,
        auditoria_replay=auditoria_replay,
        auditoria_ledger=auditoria_ledger,
        auditoria_estado_temporal=auditoria_estado,
        auditoria_fontes_elegiveis=auditoria_fontes,
        auditoria_switching_temporal=auditoria_switching,
        auditoria_invariantes=auditoria_invariantes,
        auditoria_residuos_legados=auditoria_residuos,
        validacao_temporal_global=validacao,
        metadados_origem=metadados,
    )
