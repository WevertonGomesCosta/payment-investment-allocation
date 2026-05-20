"""Adaptador shadow para o contrato mínimo PacoteReplayPassado.

V17-F0-V.4D não altera o replay efetivo nem a saída canônica. Este módulo
apenas embrulha o PacoteReplayPassadoControlado atual em um contrato explícito
com aliases estáveis para a Etapa 4.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import pandas as pd


VERSAO_PACOTE_REPLAY_PASSADO_SHADOW = "V17-F0-V.4D-shadow"


@dataclass(slots=True)
class PacoteReplayPassado:
    """Contrato mínimo shadow do replay passado.

    O pacote preserva os objetos já produzidos pelo replay controlado e adiciona
    aliases contratuais, metadados e validação para uso diagnóstico da Etapa 4.
    """

    versao: str
    modo_execucao: str
    data_referencia: Any
    lotes_apos_replay: list[Any] = field(default_factory=list)
    log_movimentos_passados: Any = None
    estado_lotes_passado: Any = None
    audit_trilha_pagamentos_passados: list[dict[str, Any]] = field(default_factory=list)
    auditoria_replay: dict[str, Any] = field(default_factory=dict)
    validacao_replay: dict[str, Any] = field(default_factory=dict)
    metadados_origem: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_dict(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return dict(valor)
    if isinstance(valor, Mapping):
        return dict(valor.items())
    return {}


def _df_copy(valor: Any) -> Any:
    if isinstance(valor, pd.DataFrame):
        return valor.copy()
    return valor


def _records(valor: Any) -> list[dict[str, Any]]:
    if isinstance(valor, pd.DataFrame):
        return list(valor.to_dict(orient="records"))
    if isinstance(valor, list):
        return [dict(x) for x in valor if isinstance(x, dict)]
    return []


def _inferir_data_referencia(contexto: Any = None, data_referencia: Any = None) -> Any:
    if data_referencia is not None:
        return data_referencia.isoformat() if hasattr(data_referencia, "isoformat") else data_referencia
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    return data.isoformat() if hasattr(data, "isoformat") else data


def _montar_auditoria(
    *,
    replay_controlado: Any,
    lotes_apos_replay: list[Any],
    log_movimentos_passados: Any,
    estado_lotes_passado: Any,
    audit_trilha_pagamentos_passados: list[dict[str, Any]],
    auditoria_base: dict[str, Any],
) -> dict[str, Any]:
    qtd_log = int(len(log_movimentos_passados)) if hasattr(log_movimentos_passados, "__len__") else 0
    qtd_estado = int(len(estado_lotes_passado)) if hasattr(estado_lotes_passado, "__len__") else 0
    auditoria = dict(auditoria_base)
    auditoria.update({
        "ok": True,
        "modo_shadow": True,
        "origem_execucao": "construir_pacote_replay_passado_shadow",
        "origem_replay_controlado": type(replay_controlado).__name__,
        "qtd_lotes_apos_replay": len(lotes_apos_replay),
        "qtd_log_movimentos_passados": qtd_log,
        "qtd_estado_lotes_passado": qtd_estado,
        "qtd_audit_trilha_pagamentos_passados": len(audit_trilha_pagamentos_passados),
        "alias_log_passado_para_log_movimentos_passados": True,
        "alias_auditoria_para_auditoria_replay": True,
        "alias_validacao_para_validacao_replay": True,
        "nao_altera_replay_efetivo": True,
        "nao_altera_saida_canonica": True,
    })
    return auditoria


def _montar_validacao(
    *,
    lotes_apos_replay: list[Any],
    log_movimentos_passados: Any,
    estado_lotes_passado: Any,
    validacao_base: dict[str, Any],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []

    if lotes_apos_replay is None:
        erros.append("lotes_apos_replay_ausente")
    if log_movimentos_passados is None:
        avisos.append("log_movimentos_passados_ausente")
    if estado_lotes_passado is None:
        avisos.append("estado_lotes_passado_ausente")

    base_erros = list(validacao_base.get("erros", [])) or list(validacao_base.get("erros_bloqueantes", []))
    base_avisos = list(validacao_base.get("avisos", []))

    return {
        "ok": len(erros) == 0 and bool(validacao_base.get("ok", True)),
        "erros_bloqueantes": erros + base_erros,
        "avisos": avisos + base_avisos,
        "evidencias": {
            "qtd_lotes_apos_replay": len(lotes_apos_replay or []),
            "qtd_log_movimentos_passados": int(len(log_movimentos_passados)) if hasattr(log_movimentos_passados, "__len__") else 0,
            "qtd_estado_lotes_passado": int(len(estado_lotes_passado)) if hasattr(estado_lotes_passado, "__len__") else 0,
        },
    }


def construir_pacote_replay_passado_shadow(
    replay_controlado: Any,
    *,
    contexto: Any = None,
    data_referencia: Any = None,
    modo_execucao: str = "shadow",
) -> PacoteReplayPassado:
    """Constrói PacoteReplayPassado mínimo a partir do replay controlado atual.

    Não executa replay, não altera lotes, não altera a saída canônica e não
    reinterpreta economicamente movimentos passados.
    """
    lotes_apos_replay = list(getattr(replay_controlado, "lotes_apos_replay", []) or [])
    log_movimentos_passados = _df_copy(getattr(replay_controlado, "log_passado", None))
    estado_lotes_passado = _df_copy(getattr(replay_controlado, "estado_lotes_passado", None))
    auditoria_base = _as_dict(getattr(replay_controlado, "auditoria", {}))
    validacao_base = _as_dict(getattr(replay_controlado, "validacao", {}))
    audit_trilha = _records(log_movimentos_passados)

    validacao = _montar_validacao(
        lotes_apos_replay=lotes_apos_replay,
        log_movimentos_passados=log_movimentos_passados,
        estado_lotes_passado=estado_lotes_passado,
        validacao_base=validacao_base,
    )
    auditoria = _montar_auditoria(
        replay_controlado=replay_controlado,
        lotes_apos_replay=lotes_apos_replay,
        log_movimentos_passados=log_movimentos_passados,
        estado_lotes_passado=estado_lotes_passado,
        audit_trilha_pagamentos_passados=audit_trilha,
        auditoria_base=auditoria_base,
    )
    auditoria["ok"] = bool(validacao.get("ok"))

    metadados_origem = {
        "versao_microetapa": "V17-F0-V.4D",
        "modo_shadow": True,
        "adaptador": "construir_pacote_replay_passado_shadow",
        "classe_origem": type(replay_controlado).__name__,
        "campo_origem_lotes": "lotes_apos_replay",
        "campo_origem_log": "log_passado",
        "campo_origem_estado": "estado_lotes_passado",
        "campo_origem_auditoria": "auditoria",
        "campo_origem_validacao": "validacao",
        "nao_altera_replay_efetivo": True,
        "nao_altera_saida_canonica": True,
    }

    return PacoteReplayPassado(
        versao=VERSAO_PACOTE_REPLAY_PASSADO_SHADOW,
        modo_execucao=modo_execucao,
        data_referencia=_inferir_data_referencia(contexto=contexto, data_referencia=data_referencia),
        lotes_apos_replay=lotes_apos_replay,
        log_movimentos_passados=log_movimentos_passados,
        estado_lotes_passado=estado_lotes_passado,
        audit_trilha_pagamentos_passados=audit_trilha,
        auditoria_replay=auditoria,
        validacao_replay=validacao,
        metadados_origem=metadados_origem,
    )
