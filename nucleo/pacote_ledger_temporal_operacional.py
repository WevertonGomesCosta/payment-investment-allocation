"""PacoteLedgerTemporalOperacional temporal.

V17-F0-V.4E normaliza o PacoteLedgerTemporal temporal existente para o
contrato operacional mínimo da Etapa 4, sem acionar o ledger legado removido e sem
alterar saída canônica/observável.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


VERSAO_PACOTE_LEDGER_TEMPORAL_OPERACIONAL = "V17-F0-V.4E-temporal"


@dataclass(slots=True)
class PacoteLedgerTemporalOperacional:
    """Contrato operacional temporal do ledger temporal.

    Este pacote é derivado do contrato oficial do ledger temporal e do
    PacoteLedgerTemporal temporal. Não executa decisão econômica nova.
    """

    versao: str
    modo_execucao: str
    data_referencia: Any
    eventos_temporais: list[dict[str, Any]] = field(default_factory=list)
    estado_temporal_por_data: list[dict[str, Any]] = field(default_factory=list)
    saldos_por_lote: list[dict[str, Any]] = field(default_factory=list)
    saldos_disponiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    vencimentos_processados: list[dict[str, Any]] = field(default_factory=list)
    pagamentos_futuros_processados: list[dict[str, Any]] = field(default_factory=list)
    fontes_elegiveis_por_pagamento: list[dict[str, Any]] = field(default_factory=list)
    fontes_elegiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    fifo_candidatos_avaliados: list[dict[str, Any]] = field(default_factory=list)
    alertas_temporais: list[dict[str, Any]] = field(default_factory=list)
    auditoria_ledger_temporal: dict[str, Any] = field(default_factory=dict)
    validacao_ledger_temporal: dict[str, Any] = field(default_factory=dict)
    metadados_origem: dict[str, Any] = field(default_factory=dict)

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_dict(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return dict(valor)
    if isinstance(valor, Mapping):
        return dict(valor.items())
    return {}


def _as_list_dict(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, tuple):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    try:
        if hasattr(valor, "to_dict") and hasattr(valor, "columns"):
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


def _inferir_data_referencia(contexto: Any = None, pacote_temporal: Any = None) -> Any:
    data = getattr(pacote_temporal, "data_referencia", None)
    if data not in (None, ""):
        return data.isoformat() if hasattr(data, "isoformat") else data
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    return data.isoformat() if hasattr(data, "isoformat") else data


def _normalizar_evento_temporal(ev: Mapping[str, Any], idx: int) -> dict[str, Any]:
    tipo_evento = "pagamento_futuro"
    if _txt(ev.get("evento_switching_id")) or _txt(ev.get("lote_pos_switching_materializado")):
        tipo_evento = "switching"
    if _txt(ev.get("tipo_evento")):
        tipo_evento = _txt(ev.get("tipo_evento"))

    return {
        "evento_id": _txt(_primeiro(ev, "evento_id", "evento_switching_id")) or f"evento_temporal_{idx:05d}",
        "data_evento": _primeiro(ev, "data_evento", "data_pagamento", "data", "Data"),
        "tipo_evento": tipo_evento,
        "subtipo_evento": _primeiro(ev, "subtipo_evento", "pacote_do_dia", "pacote_dia"),
        "lote_id": _primeiro(ev, "lote_id", "lote_sugerido_operacional", "lote_fonte_origem", "Lote"),
        "lote_origem": _primeiro(ev, "lote_origem", "lote_fonte_origem", "lote_origem_switching"),
        "lote_destino": _primeiro(ev, "lote_destino", "lote_pos_switching_materializado", "lote_pos_switching"),
        "pagamento_id": _primeiro(ev, "pagamento_id", "despesa_id", "Despesa ID"),
        "valor_evento": _primeiro(ev, "valor_evento", "consumo", "liquido", "valor_pagamento"),
        "valor_bruto": _primeiro(ev, "valor_bruto", "bruto"),
        "valor_liquido": _primeiro(ev, "valor_liquido", "liquido"),
        "imposto": _primeiro(ev, "imposto"),
        "saldo_antes": _primeiro(ev, "saldo_antes"),
        "saldo_depois": _primeiro(ev, "saldo_depois"),
        "status_evento": _primeiro(ev, "status_evento", "status"),
        "motivo_bloqueio": _primeiro(ev, "motivo_bloqueio"),
        "fonte_temporal": _primeiro(ev, "fonte_temporal", "origem_fonte_candidata"),
        "origem_dado": _primeiro(ev, "origem_dado", "origem_mapa_migracao"),
        "evento_legado": dict(ev),
    }


def _normalizar_eventos(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_normalizar_evento_temporal(ev, idx) for idx, ev in enumerate(eventos, start=1)]


def _normalizar_pagamentos(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pagamentos: dict[str, dict[str, Any]] = {}
    for ev in eventos:
        pagamento_id = _txt(_primeiro(ev, "pagamento_id", "despesa_id", "Despesa ID"))
        if not pagamento_id or pagamento_id in pagamentos:
            continue
        pagamentos[pagamento_id] = {
            "pagamento_id": pagamento_id,
            "data_pagamento": _primeiro(ev, "data_pagamento", "data", "Data"),
            "descricao_pagamento": _primeiro(ev, "descricao_pagamento", "conta", "Conta"),
            "valor_pagamento": _primeiro(ev, "valor_pagamento", "fifo_valor_pagamento", "Valor"),
            "status_pagamento_temporal": _primeiro(ev, "status_pagamento_temporal", "status"),
            "cobertura_integral": _primeiro(ev, "cobertura_integral"),
            "lote_sugerido_operacional": _primeiro(ev, "lote_sugerido_operacional"),
            "lote_reserva": _primeiro(ev, "lote_reserva"),
            "necessita_switching": _primeiro(ev, "necessita_switching"),
            "switching_antes_pagamento": _primeiro(ev, "switching_antes_pagamento"),
            "switching_depois_pagamento": _primeiro(ev, "switching_depois_pagamento"),
            "motivo_bloqueio": _primeiro(ev, "motivo_bloqueio"),
            "pacote_dia": _primeiro(ev, "pacote_dia", "pacote_do_dia"),
        }
    return list(pagamentos.values())


def _normalizar_fontes_elegiveis_por_pagamento(
    eventos: list[dict[str, Any]],
    fifo: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    saida: list[dict[str, Any]] = []
    for idx, item in enumerate(fifo or eventos, start=1):
        pagamento_id = _txt(_primeiro(item, "pagamento_id", "despesa_id", "Despesa ID"))
        fonte = _primeiro(item, "fonte_candidata_id", "lote_id", "lote_sugerido_operacional", "Lote")
        if not pagamento_id and not fonte:
            continue
        saida.append({
            "pagamento_id": pagamento_id,
            "data_pagamento": _primeiro(item, "data_pagamento", "data", "Data"),
            "fonte_candidata_id": fonte,
            "tipo_fonte_candidata": _primeiro(item, "tipo_fonte_candidata"),
            "origem_fonte_candidata": _primeiro(item, "origem_fonte_candidata"),
            "saldo_liquido_disponivel": _primeiro(item, "saldo_liquido_disponivel", "saldo_antes", "liquido"),
            "saldo_bruto_disponivel": _primeiro(item, "saldo_bruto_disponivel", "bruto"),
            "carencia_ok": _primeiro(item, "carencia_ok"),
            "vencimento_ok": _primeiro(item, "vencimento_ok"),
            "migracao_ok": _primeiro(item, "migracao_ok"),
            "motivo_descarte_fonte": _primeiro(item, "motivo_descarte_fonte", "motivo_bloqueio"),
            "status_fonte": _primeiro(item, "status_fonte", "status"),
            "ordem_temporal": idx,
        })
    return saida


def _saldos_por_data(saldos_por_lote: list[dict[str, Any]]) -> list[dict[str, Any]]:
    por_data: dict[str, dict[str, Any]] = {}
    for saldo in saldos_por_lote:
        data = _txt(_primeiro(saldo, "data_referencia_temporal", "data_evento", "data")) or "sem_data"
        atual = por_data.setdefault(data, {"data_referencia_temporal": data, "qtd_lotes": 0})
        atual["qtd_lotes"] += 1
    return list(por_data.values())


def _montar_auditoria(
    *,
    retorno_legado: Mapping[str, Any],
    pacote_temporal: Any,
    eventos_temporais: list[dict[str, Any]],
    fifo_candidatos_avaliados: list[dict[str, Any]],
    pagamentos_futuros_processados: list[dict[str, Any]],
    fontes_elegiveis_por_pagamento: list[dict[str, Any]],
    saldos_por_lote: list[dict[str, Any]],
    campos_vazios_auditados: list[str],
) -> dict[str, Any]:
    auditoria_temporal = _as_dict(getattr(pacote_temporal, "auditoria_ledger_temporal", {}))
    auditoria = dict(auditoria_temporal)
    auditoria.update({
        "ok": True,
        "modo_operacional_temporal": True,
        "origem_execucao": "construir_pacote_ledger_temporal_operacional",
        "versao_microetapa": "V17-F0-V.4E",
        "contrato_alvo": "PacoteLedgerTemporalOperacional",
        "qtd_eventos_temporais": len(eventos_temporais),
        "qtd_pagamentos_futuros_processados": len(pagamentos_futuros_processados),
        "qtd_fifo_candidatos_avaliados": len(fifo_candidatos_avaliados),
        "qtd_fontes_elegiveis_por_pagamento": len(fontes_elegiveis_por_pagamento),
        "qtd_saldos_por_lote": len(saldos_por_lote),
        "fonte_primaria_switching_ledger": "switching_canonico",
        "fallback_legado_switching_auditavel": False,
        "usa_contexto_amplo": True,
        "usa_planilha_bruta_como_fonte_primaria": False,
        "usa_planilha_bruta_apenas_fallback": True,
        "usa_switching_canonico_como_fonte_primaria": False,
        "usa_switching_canonico_como_fonte_primaria": True,
        "retorno_dict_legado_usado_como_origem": False,
        "pacote_ledger_temporal_usado_como_origem": True,
        "campos_vazios_auditados": list(campos_vazios_auditados),
        "nao_altera_ledger_efetivo": True,
        "nao_altera_saida_canonica": True,
        "retorno_legado_chaves": sorted(str(k) for k in retorno_legado.keys()),
    })
    return auditoria


def _montar_validacao(
    *,
    eventos_temporais: list[dict[str, Any]],
    fifo_candidatos_avaliados: list[dict[str, Any]],
    campos_vazios_auditados: list[str],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    if not eventos_temporais:
        erros.append("eventos_temporais_ausentes")
    if not fifo_candidatos_avaliados:
        erros.append("fifo_candidatos_avaliados_ausente")
    for campo in campos_vazios_auditados:
        avisos.append(f"campo_temporal_operacional_vazio:{campo}")
    avisos.append("contrato_vazio_oficial_usado_como_origem_ledger_temporal")
    return {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": avisos,
        "evidencias": {
            "qtd_eventos_temporais": len(eventos_temporais),
            "qtd_fifo_candidatos_avaliados": len(fifo_candidatos_avaliados),
            "campos_vazios_auditados": list(campos_vazios_auditados),
        },
    }


def construir_pacote_ledger_temporal_operacional(
    retorno_legado: Mapping[str, Any],
    pacote_temporal: Any,
    *,
    contexto: Any = None,
    modo_execucao: str = "operacional_temporal",
) -> PacoteLedgerTemporalOperacional:
    """Normaliza o ledger temporal atual para o contrato operacional V4B/V4E."""
    retorno = _as_dict(retorno_legado)
    eventos_originais = _as_list_dict(getattr(pacote_temporal, "eventos_temporais", []))
    fifo = _as_list_dict(getattr(pacote_temporal, "fifo_candidatos_avaliados", []))
    saldos_originais = _as_list_dict(getattr(pacote_temporal, "saldos_por_lote", []))

    eventos_temporais = _normalizar_eventos(eventos_originais)
    pagamentos = _normalizar_pagamentos(eventos_originais)
    fontes_por_pagamento = _normalizar_fontes_elegiveis_por_pagamento(eventos_originais, fifo)
    saldos_por_lote = saldos_originais
    saldos_disponiveis_por_data = _saldos_por_data(saldos_por_lote)

    estado_temporal_por_data = _as_list_dict(getattr(pacote_temporal, "estado_temporal_por_data", []))
    vencimentos_processados = _as_list_dict(getattr(pacote_temporal, "vencimentos_processados", []))
    fontes_elegiveis_por_data = _as_list_dict(getattr(pacote_temporal, "fontes_elegiveis_por_data", []))
    alertas_temporais = _as_list_dict(getattr(pacote_temporal, "alertas_temporais", []))

    campos_vazios = []
    for nome, valor in [
        ("estado_temporal_por_data", estado_temporal_por_data),
        ("vencimentos_processados", vencimentos_processados),
        ("fontes_elegiveis_por_data", fontes_elegiveis_por_data),
    ]:
        if not valor:
            campos_vazios.append(nome)

    auditoria = _montar_auditoria(
        retorno_legado=retorno,
        pacote_temporal=pacote_temporal,
        eventos_temporais=eventos_temporais,
        fifo_candidatos_avaliados=fifo,
        pagamentos_futuros_processados=pagamentos,
        fontes_elegiveis_por_pagamento=fontes_por_pagamento,
        saldos_por_lote=saldos_por_lote,
        campos_vazios_auditados=campos_vazios,
    )
    validacao = _montar_validacao(
        eventos_temporais=eventos_temporais,
        fifo_candidatos_avaliados=fifo,
        campos_vazios_auditados=campos_vazios,
    )
    auditoria["ok"] = bool(validacao.get("ok"))

    metadados = {
        "versao_microetapa": "V17-F0-V.4E",
        "modo_operacional_temporal": True,
        "adaptador": "construir_pacote_ledger_temporal_operacional",
        "origem_pacote_temporal": type(pacote_temporal).__name__,
        "origem_retorno_legado": "contrato_vazio_oficial_me521b",
        "nao_altera_ledger_efetivo": True,
        "nao_altera_saida_canonica": True,
    }

    return PacoteLedgerTemporalOperacional(
        versao=VERSAO_PACOTE_LEDGER_TEMPORAL_OPERACIONAL,
        modo_execucao=modo_execucao,
        data_referencia=_inferir_data_referencia(contexto=contexto, pacote_temporal=pacote_temporal),
        eventos_temporais=eventos_temporais,
        estado_temporal_por_data=estado_temporal_por_data,
        saldos_por_lote=saldos_por_lote,
        saldos_disponiveis_por_data=saldos_disponiveis_por_data,
        vencimentos_processados=vencimentos_processados,
        pagamentos_futuros_processados=pagamentos,
        fontes_elegiveis_por_pagamento=fontes_por_pagamento,
        fontes_elegiveis_por_data=fontes_elegiveis_por_data,
        fifo_candidatos_avaliados=fifo,
        alertas_temporais=alertas_temporais,
        auditoria_ledger_temporal=auditoria,
        validacao_ledger_temporal=validacao,
        metadados_origem=metadados,
    )
