"""PacoteEstadoTemporal shadow.

V17-F0-V.4F materializa um estado temporal explícito a partir do
PacoteReplayPassado shadow e do PacoteLedgerTemporalOperacional shadow, sem
alterar replay, ledger efetivo, saída canônica ou saída observável.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

import pandas as pd


VERSAO_PACOTE_ESTADO_TEMPORAL_SHADOW = "V17-F0-V.4F-shadow"


@dataclass(slots=True)
class PacoteEstadoTemporal:
    """Contrato shadow do estado temporal da Etapa 4."""

    versao: str
    modo_execucao: str
    data_referencia: Any
    estado_lotes_por_data: list[dict[str, Any]] = field(default_factory=list)
    estado_lotes_final: list[dict[str, Any]] = field(default_factory=list)
    saldos_por_lote: list[dict[str, Any]] = field(default_factory=list)
    saldos_disponiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    fontes_disponiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    vencimentos_por_data: list[dict[str, Any]] = field(default_factory=list)
    migracoes_por_data: list[dict[str, Any]] = field(default_factory=list)
    auditoria_estado_temporal: dict[str, Any] = field(default_factory=dict)
    validacao_estado_temporal: dict[str, Any] = field(default_factory=dict)
    metadados_origem: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_list_dict(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, tuple):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    try:
        if isinstance(valor, pd.DataFrame):
            return list(valor.to_dict(orient="records"))
    except Exception:
        return []
    return []


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _primeiro(row: Mapping[str, Any], *chaves: str) -> Any:
    for chave in chaves:
        if chave in row and row.get(chave) not in (None, ""):
            return row.get(chave)
    return ""


def _inferir_data_referencia(
    *,
    pacote_replay_passado: Any = None,
    pacote_ledger_operacional: Any = None,
    contexto: Any = None,
) -> Any:
    for origem in (pacote_ledger_operacional, pacote_replay_passado):
        data = getattr(origem, "data_referencia", None)
        if data not in (None, ""):
            return data.isoformat() if hasattr(data, "isoformat") else data
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    return data.isoformat() if hasattr(data, "isoformat") else data


def _registro_replay_para_estado(row: Mapping[str, Any], data_referencia: Any) -> dict[str, Any]:
    lote_id = _primeiro(row, "lote_id", "Lote ID", "Lote", "lote")
    saldo_bruto = _primeiro(row, "saldo_bruto_pos_replay", "Saldo Após Replay", "Saldo Apos Replay", "saldo_apos_replay")
    return {
        "data_referencia_temporal": data_referencia,
        "lote_id": lote_id,
        "status_temporal": "pos_replay",
        "saldo_bruto": saldo_bruto,
        "saldo_liquido": _primeiro(row, "saldo_liquido_pos_replay", "Saldo Líquido", "Saldo Liquido") or saldo_bruto,
        "principal_remanescente": _primeiro(row, "principal_remanescente", "Principal Remanescente"),
        "fator_acumulado": _primeiro(row, "fator_acumulado", "Fator Acumulado"),
        "disponivel_para_pagamento": _primeiro(row, "disponivel_para_pagamento") or "n/d_shadow",
        "disponivel_para_switching": _primeiro(row, "disponivel_para_switching") or "n/d_shadow",
        "carencia_ate": _primeiro(row, "carencia_ate", "Carência Até", "Carencia Ate"),
        "vencido": _primeiro(row, "vencido") or "n/d_shadow",
        "data_vencimento": _primeiro(row, "data_vencimento", "Data Vencimento"),
        "migrado": _primeiro(row, "migrado") or "n/d_shadow",
        "migrado_em": _primeiro(row, "migrado_em"),
        "lote_pos_switching": _primeiro(row, "lote_pos_switching"),
        "origem_estado": "replay_passado.estado_lotes_passado",
        "registro_origem": dict(row),
    }


def _registro_saldo_para_estado(row: Mapping[str, Any]) -> dict[str, Any]:
    lote_id = _primeiro(row, "lote_id", "Lote")
    return {
        "data_referencia_temporal": _primeiro(row, "data_referencia_temporal", "data_evento", "data"),
        "lote_id": lote_id,
        "status_temporal": _primeiro(row, "status_temporal", "status_funcional", "status") or "ledger_temporal",
        "saldo_bruto": _primeiro(row, "saldo_bruto", "bruto"),
        "saldo_liquido": _primeiro(row, "saldo_liquido", "liquido"),
        "principal_remanescente": _primeiro(row, "principal_remanescente"),
        "fator_acumulado": _primeiro(row, "fator_acumulado"),
        "disponivel_para_pagamento": _primeiro(row, "disponivel_para_pagamento") or "n/d_shadow",
        "disponivel_para_switching": _primeiro(row, "disponivel_para_switching") or "n/d_shadow",
        "carencia_ate": _primeiro(row, "carencia_ate"),
        "vencido": _primeiro(row, "vencido") or "n/d_shadow",
        "data_vencimento": _primeiro(row, "data_vencimento"),
        "migrado": bool(_txt(_primeiro(row, "lote_pos_switching", "lote_origem_switching"))),
        "migrado_em": _primeiro(row, "migrado_em"),
        "lote_pos_switching": _primeiro(row, "lote_pos_switching"),
        "origem_estado": "pacote_ledger_temporal_operacional.saldos_por_lote",
        "registro_origem": dict(row),
    }


def _montar_estado_lotes_por_data(
    *,
    pacote_replay_passado: Any,
    pacote_ledger_operacional: Any,
    data_referencia: Any,
) -> list[dict[str, Any]]:
    estado: list[dict[str, Any]] = []
    for row in _as_list_dict(getattr(pacote_replay_passado, "estado_lotes_passado", None)):
        if _txt(_primeiro(row, "lote_id", "Lote ID", "Lote", "lote")):
            estado.append(_registro_replay_para_estado(row, data_referencia))
    for row in _as_list_dict(getattr(pacote_ledger_operacional, "saldos_por_lote", [])):
        if _txt(_primeiro(row, "lote_id", "Lote")):
            estado.append(_registro_saldo_para_estado(row))
    return estado


def _montar_estado_final(estado_lotes_por_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    por_lote: dict[str, dict[str, Any]] = {}
    for row in estado_lotes_por_data:
        lote_id = _txt(row.get("lote_id"))
        if not lote_id:
            continue
        por_lote[lote_id] = {
            "lote_id": lote_id,
            "status_final": row.get("status_temporal"),
            "saldo_bruto_final": row.get("saldo_bruto"),
            "saldo_liquido_final": row.get("saldo_liquido"),
            "patrimonio_liquido_final": row.get("saldo_liquido") or row.get("saldo_bruto"),
            "principal_remanescente": row.get("principal_remanescente"),
            "data_referencia_temporal": row.get("data_referencia_temporal"),
            "migrado": row.get("migrado"),
            "lote_pos_switching": row.get("lote_pos_switching"),
            "origem_estado_final": row.get("origem_estado"),
        }
    return list(por_lote.values())


def _fontes_por_data(fontes_por_pagamento: list[dict[str, Any]]) -> list[dict[str, Any]]:
    por_data: dict[str, dict[str, Any]] = {}
    for fonte in fontes_por_pagamento:
        data = _txt(_primeiro(fonte, "data_pagamento", "data")) or "sem_data"
        atual = por_data.setdefault(data, {"data_referencia_temporal": data, "qtd_fontes": 0, "pagamentos": set()})
        atual["qtd_fontes"] += 1
        pid = _txt(_primeiro(fonte, "pagamento_id"))
        if pid:
            atual["pagamentos"].add(pid)
    saida: list[dict[str, Any]] = []
    for data, row in por_data.items():
        pagamentos = sorted(row.pop("pagamentos"))
        row["qtd_pagamentos"] = len(pagamentos)
        row["pagamentos"] = pagamentos
        saida.append(row)
    return saida


def _migracoes_por_data(eventos_temporais: list[dict[str, Any]]) -> list[dict[str, Any]]:
    migracoes: list[dict[str, Any]] = []
    for ev in eventos_temporais:
        tipo = _txt(ev.get("tipo_evento"))
        lote_destino = _txt(ev.get("lote_destino"))
        evento_switching = _txt(ev.get("evento_id")) if "switching" in _txt(ev.get("evento_id")).lower() else ""
        if tipo != "switching" and not lote_destino and not evento_switching:
            continue
        migracoes.append({
            "data_referencia_temporal": _primeiro(ev, "data_evento"),
            "lote_origem": _primeiro(ev, "lote_origem"),
            "lote_destino": _primeiro(ev, "lote_destino"),
            "evento_id": _primeiro(ev, "evento_id"),
            "status_evento": _primeiro(ev, "status_evento"),
            "origem_estado": "pacote_ledger_temporal_operacional.eventos_temporais",
        })
    return migracoes


def _vencimentos_por_data(pacote_ledger_operacional: Any) -> list[dict[str, Any]]:
    vencimentos = _as_list_dict(getattr(pacote_ledger_operacional, "vencimentos_processados", []))
    saida: list[dict[str, Any]] = []
    for idx, row in enumerate(vencimentos, start=1):
        saida.append({
            "vencimento_id": _primeiro(row, "vencimento_id") or f"vencimento_{idx:05d}",
            "data_referencia_temporal": _primeiro(row, "data_vencimento", "data", "data_evento"),
            "lote_id": _primeiro(row, "lote_id", "Lote"),
            "status_vencimento": _primeiro(row, "status_vencimento", "status"),
            "origem_estado": "pacote_ledger_temporal_operacional.vencimentos_processados",
            "registro_origem": dict(row),
        })
    return saida


def _montar_auditoria(
    *,
    estado_lotes_por_data: list[dict[str, Any]],
    estado_lotes_final: list[dict[str, Any]],
    saldos_por_lote: list[dict[str, Any]],
    saldos_disponiveis_por_data: list[dict[str, Any]],
    fontes_disponiveis_por_data: list[dict[str, Any]],
    vencimentos_por_data: list[dict[str, Any]],
    migracoes_por_data: list[dict[str, Any]],
    campos_vazios_auditados: list[str],
) -> dict[str, Any]:
    return {
        "ok": True,
        "modo_shadow": True,
        "origem_execucao": "construir_pacote_estado_temporal_shadow",
        "versao_microetapa": "V17-F0-V.4F",
        "contrato_alvo": "PacoteEstadoTemporal",
        "qtd_estado_lotes_por_data": len(estado_lotes_por_data),
        "qtd_estado_lotes_final": len(estado_lotes_final),
        "qtd_saldos_por_lote": len(saldos_por_lote),
        "qtd_saldos_disponiveis_por_data": len(saldos_disponiveis_por_data),
        "qtd_fontes_disponiveis_por_data": len(fontes_disponiveis_por_data),
        "qtd_vencimentos_por_data": len(vencimentos_por_data),
        "qtd_migracoes_por_data": len(migracoes_por_data),
        "campos_vazios_auditados": list(campos_vazios_auditados),
        "usa_pacote_replay_passado_shadow": True,
        "usa_pacote_ledger_temporal_operacional_shadow": True,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "nao_altera_saida_canonica": True,
    }


def _montar_validacao(
    *,
    estado_lotes_por_data: list[dict[str, Any]],
    estado_lotes_final: list[dict[str, Any]],
    saldos_por_lote: list[dict[str, Any]],
    fontes_disponiveis_por_data: list[dict[str, Any]],
    campos_vazios_auditados: list[str],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    if not estado_lotes_por_data:
        erros.append("estado_lotes_por_data_ausente")
    if not estado_lotes_final:
        erros.append("estado_lotes_final_ausente")
    if not saldos_por_lote:
        avisos.append("saldos_por_lote_vazio")
    if not fontes_disponiveis_por_data:
        avisos.append("fontes_disponiveis_por_data_vazio")
    for campo in campos_vazios_auditados:
        avisos.append(f"campo_estado_temporal_shadow_vazio:{campo}")
    return {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": avisos,
        "evidencias": {
            "qtd_estado_lotes_por_data": len(estado_lotes_por_data),
            "qtd_estado_lotes_final": len(estado_lotes_final),
            "qtd_saldos_por_lote": len(saldos_por_lote),
            "qtd_fontes_disponiveis_por_data": len(fontes_disponiveis_por_data),
            "campos_vazios_auditados": list(campos_vazios_auditados),
        },
    }


def construir_pacote_estado_temporal_shadow(
    pacote_replay_passado: Any,
    pacote_ledger_operacional: Any,
    *,
    contexto: Any = None,
    modo_execucao: str = "shadow",
) -> PacoteEstadoTemporal:
    """Constrói PacoteEstadoTemporal shadow a partir dos pacotes V4D e V4E."""
    data_referencia = _inferir_data_referencia(
        pacote_replay_passado=pacote_replay_passado,
        pacote_ledger_operacional=pacote_ledger_operacional,
        contexto=contexto,
    )
    estado_lotes_por_data = _montar_estado_lotes_por_data(
        pacote_replay_passado=pacote_replay_passado,
        pacote_ledger_operacional=pacote_ledger_operacional,
        data_referencia=data_referencia,
    )
    estado_lotes_final = _montar_estado_final(estado_lotes_por_data)
    saldos_por_lote = _as_list_dict(getattr(pacote_ledger_operacional, "saldos_por_lote", []))
    saldos_disponiveis_por_data = _as_list_dict(getattr(pacote_ledger_operacional, "saldos_disponiveis_por_data", []))
    fontes_disponiveis_por_data = _fontes_por_data(
        _as_list_dict(getattr(pacote_ledger_operacional, "fontes_elegiveis_por_pagamento", []))
    )
    vencimentos_por_data = _vencimentos_por_data(pacote_ledger_operacional)
    migracoes_por_data = _migracoes_por_data(
        _as_list_dict(getattr(pacote_ledger_operacional, "eventos_temporais", []))
    )

    campos_vazios = []
    for nome, valor in [
        ("vencimentos_por_data", vencimentos_por_data),
        ("migracoes_por_data", migracoes_por_data),
    ]:
        if not valor:
            campos_vazios.append(nome)

    auditoria = _montar_auditoria(
        estado_lotes_por_data=estado_lotes_por_data,
        estado_lotes_final=estado_lotes_final,
        saldos_por_lote=saldos_por_lote,
        saldos_disponiveis_por_data=saldos_disponiveis_por_data,
        fontes_disponiveis_por_data=fontes_disponiveis_por_data,
        vencimentos_por_data=vencimentos_por_data,
        migracoes_por_data=migracoes_por_data,
        campos_vazios_auditados=campos_vazios,
    )
    validacao = _montar_validacao(
        estado_lotes_por_data=estado_lotes_por_data,
        estado_lotes_final=estado_lotes_final,
        saldos_por_lote=saldos_por_lote,
        fontes_disponiveis_por_data=fontes_disponiveis_por_data,
        campos_vazios_auditados=campos_vazios,
    )
    auditoria["ok"] = bool(validacao.get("ok"))

    metadados = {
        "versao_microetapa": "V17-F0-V.4F",
        "modo_shadow": True,
        "adaptador": "construir_pacote_estado_temporal_shadow",
        "origem_replay": type(pacote_replay_passado).__name__,
        "origem_ledger": type(pacote_ledger_operacional).__name__,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "nao_altera_saida_canonica": True,
    }

    return PacoteEstadoTemporal(
        versao=VERSAO_PACOTE_ESTADO_TEMPORAL_SHADOW,
        modo_execucao=modo_execucao,
        data_referencia=data_referencia,
        estado_lotes_por_data=estado_lotes_por_data,
        estado_lotes_final=estado_lotes_final,
        saldos_por_lote=saldos_por_lote,
        saldos_disponiveis_por_data=saldos_disponiveis_por_data,
        fontes_disponiveis_por_data=fontes_disponiveis_por_data,
        vencimentos_por_data=vencimentos_por_data,
        migracoes_por_data=migracoes_por_data,
        auditoria_estado_temporal=auditoria,
        validacao_estado_temporal=validacao,
        metadados_origem=metadados,
    )
