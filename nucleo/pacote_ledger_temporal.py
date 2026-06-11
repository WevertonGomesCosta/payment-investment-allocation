"""Envelope temporal para o ledger temporal.

V17-F0-V.3.7K cria apenas um adaptador compatível em modo temporal.
Este módulo não aciona o ledger legado removido, não altera a saída canônica e
não remove nenhuma ponte histórica. Ele apenas materializa o contrato oficial
vazio/fornecido do ledger temporal em um envelope explícito.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


VERSAO_PACOTE_LEDGER_TEMPORAL = "V17-F0-V.3.7K-temporal"


@dataclass(slots=True)
class PacoteLedgerTemporal:
    """Pacote contratual mínimo do ledger temporal em modo temporal.

    Os campos seguem o contrato documental V3.7J. Nesta primeira versão, os
    campos que ainda não existem no contrato recebido são preenchidos com listas
    vazias e registrados em auditoria, sem inferência econômica nova.
    """

    versao: str
    modo_operacional_temporal: bool
    data_referencia: Any
    eventos_temporais: list[dict[str, Any]] = field(default_factory=list)
    estado_temporal_por_data: list[dict[str, Any]] = field(default_factory=list)
    saldos_por_lote: list[dict[str, Any]] = field(default_factory=list)
    saldos_disponiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    vencimentos_processados: list[dict[str, Any]] = field(default_factory=list)
    pagamentos_futuros_processados: list[dict[str, Any]] = field(default_factory=list)
    fontes_elegiveis_por_data: list[dict[str, Any]] = field(default_factory=list)
    alertas_temporais: list[dict[str, Any]] = field(default_factory=list)
    fifo_candidatos_avaliados: list[dict[str, Any]] = field(default_factory=list)
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


def _as_list(valor: Any) -> list[Any]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return list(valor)
    if isinstance(valor, tuple):
        return list(valor)
    try:
        # pandas.DataFrame
        if hasattr(valor, "to_dict") and hasattr(valor, "columns"):
            return list(valor.to_dict(orient="records"))
    except Exception:
        pass
    return []


def _as_list_dict(valor: Any) -> list[dict[str, Any]]:
    saida: list[dict[str, Any]] = []
    for item in _as_list(valor):
        if isinstance(item, dict):
            saida.append(dict(item))
        elif isinstance(item, Mapping):
            saida.append(dict(item.items()))
    return saida


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _primeiro_valor(row: Mapping[str, Any], *chaves: str) -> Any:
    for chave in chaves:
        if chave in row and row.get(chave) not in (None, ""):
            return row.get(chave)
    return ""


def _inferir_data_referencia(contexto: Any) -> Any:
    execucao = getattr(contexto, "execucao", None)
    data = getattr(execucao, "data_referencia", None)
    if hasattr(data, "isoformat"):
        return data.isoformat()
    return data


def _extrair_pagamentos_futuros_processados(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pagamentos: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for ev in eventos:
        pagamento_id = _txt(_primeiro_valor(ev, "pagamento_id", "Despesa ID", "despesa_id"))
        if not pagamento_id or pagamento_id in vistos:
            continue
        vistos.add(pagamento_id)
        pagamentos.append({
            "pagamento_id": pagamento_id,
            "data_pagamento": _primeiro_valor(ev, "data_pagamento", "Data", "data_evento"),
            "valor_pagamento": _primeiro_valor(ev, "valor_pagamento", "Valor", "fifo_valor_pagamento"),
            "lote_sugerido_operacional": _primeiro_valor(ev, "lote_sugerido_operacional", "Lote sugerido", "lote_id"),
            "status": _primeiro_valor(ev, "status", "Status recomendação", "Status recomendacao"),
            "motivo_bloqueio": _primeiro_valor(ev, "motivo_bloqueio", "Motivo bloqueio lote"),
            "cobertura_integral": _primeiro_valor(ev, "cobertura_integral", "Cobertura integral"),
            "pacote_dia": _primeiro_valor(ev, "pacote_dia", "pacote", "Pacote do dia"),
            "necessita_switching": _primeiro_valor(ev, "necessita_switching", "Necessita switching"),
            "switching_antes_pagamento": _primeiro_valor(ev, "switching_antes_pagamento", "Switching antes do pagamento"),
            "switching_depois_pagamento": _primeiro_valor(ev, "switching_depois_pagamento", "Switching depois do pagamento"),
        })
    return pagamentos


def _extrair_saldos_por_lote(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    saldos: dict[tuple[str, str], dict[str, Any]] = {}
    for ev in eventos:
        lote_id = _txt(_primeiro_valor(ev, "lote_id", "lote_sugerido_operacional", "Lote sugerido", "Lote"))
        if not lote_id:
            continue
        data_ref = _txt(_primeiro_valor(ev, "data_evento", "data_pagamento", "Data"))
        chave = (lote_id, data_ref)
        saldos[chave] = {
            "lote_id": lote_id,
            "data_referencia_temporal": data_ref,
            "saldo_antes": _primeiro_valor(ev, "saldo_antes", "Saldo Antes", "Saldo temp. ant."),
            "saldo_depois": _primeiro_valor(ev, "saldo_depois", "Saldo Remanescente", "Saldo temp. dep."),
            "saldo_liquido": _primeiro_valor(ev, "saldo_liquido", "liquido", "Líquido", "Liq. pos"),
            "saldo_bruto": _primeiro_valor(ev, "saldo_bruto", "bruto", "Bruto", "Bruto pos"),
            "status_funcional": _primeiro_valor(ev, "status_funcional", "status"),
            "fonte_temporal": _primeiro_valor(ev, "fonte_temporal", "Fonte sw."),
            "migrado_em": _primeiro_valor(ev, "migrado_em", "Data switching"),
            "lote_origem_switching": _primeiro_valor(ev, "lote_origem_switching", "Origem switching"),
            "lote_pos_switching": _primeiro_valor(ev, "lote_pos_switching", "Lote pós-switching", "Fonte pos sw"),
        }
    return list(saldos.values())


def _extrair_alertas_temporais(retorno_legado: Mapping[str, Any]) -> list[dict[str, Any]]:
    alertas: list[dict[str, Any]] = []
    for chave, valor in retorno_legado.items():
        chave_txt = str(chave)
        if "alerta" not in chave_txt and "bloqueio" not in chave_txt:
            continue
        if isinstance(valor, list):
            for idx, item in enumerate(valor, start=1):
                if isinstance(item, dict):
                    alerta = dict(item)
                    alerta.setdefault("alerta_id", f"{chave_txt}_{idx:05d}")
                    alerta.setdefault("origem_alerta", chave_txt)
                    alertas.append(alerta)
    return alertas


def _montar_auditoria(
    *,
    retorno_legado: Mapping[str, Any],
    eventos_temporais: list[dict[str, Any]],
    fifo_candidatos_avaliados: list[dict[str, Any]],
    pagamentos_futuros_processados: list[dict[str, Any]],
    saldos_por_lote: list[dict[str, Any]],
    alertas_temporais: list[dict[str, Any]],
    contexto: Any,
    campos_ausentes: list[str],
) -> dict[str, Any]:
    return {
        "ok": True,
        "modo_operacional_temporal": True,
        "origem_execucao": "construir_pacote_ledger_temporal",
        "origem_retorno_legado": "contrato_vazio_oficial_me521b",
        "qtd_eventos_temporais": len(eventos_temporais),
        "qtd_pagamentos_futuros_processados": len(pagamentos_futuros_processados),
        "qtd_fifo_candidatos_avaliados": len(fifo_candidatos_avaliados),
        "qtd_saldos_por_lote": len(saldos_por_lote),
        "qtd_alertas_temporais": len(alertas_temporais),
        "campos_ausentes_preenchidos_vazios": list(campos_ausentes),
        "usa_contexto_amplo": contexto is not None,
        "usa_planilha_bruta": True,
        "usa_switching_canonico": True,
        "usa_pos_injetado": True,
        "compatibilidade_contrato_ledger_temporal": True,
        "retorno_legado_chaves_total": len(list(retorno_legado.keys())),
        "retorno_legado_chaves": sorted(str(k) for k in retorno_legado.keys()),
    }


def _montar_validacao(
    *,
    retorno_legado: Mapping[str, Any],
    eventos_temporais: list[dict[str, Any]],
    fifo_candidatos_avaliados: list[dict[str, Any]],
    campos_ausentes: list[str],
) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []

    if not isinstance(retorno_legado, Mapping):
        erros.append("retorno_legado_nao_mapeavel")
    if "eventos" not in retorno_legado:
        avisos.append("retorno_legado_sem_chave_eventos")
    if "fifo_candidatos_avaliados" not in retorno_legado:
        avisos.append("retorno_legado_sem_chave_fifo_candidatos_avaliados")
    if not eventos_temporais:
        avisos.append("eventos_temporais_vazio_no_temporal")
    if not fifo_candidatos_avaliados:
        avisos.append("fifo_candidatos_avaliados_vazio_no_temporal")

    avisos.extend(f"campo_minimo_temporal_operacional_vazio:{campo}" for campo in campos_ausentes)
    avisos.append("uso_transitorio_de_contexto_amplo")
    avisos.append("contrato_ledger_temporal_vazio_oficial_sem_planilha_bruta_legada")
    avisos.append("switching_canonico_preservado_sem_ledger_legado")

    return {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": avisos,
        "evidencias": {
            "qtd_eventos_temporais": len(eventos_temporais),
            "qtd_fifo_candidatos_avaliados": len(fifo_candidatos_avaliados),
            "qtd_chaves_retorno_legado": len(list(retorno_legado.keys())) if isinstance(retorno_legado, Mapping) else 0,
        },
    }


def construir_pacote_ledger_temporal(
    quadro_futuro: Any,
    mapa_central: Any,
    contexto: Any,
    *,
    modo_operacional_temporal: bool = True,
    retorno_legado: Mapping[str, Any] | None = None,
) -> PacoteLedgerTemporal:
    """Constrói o envelope temporal do ledger temporal.

    Quando ``retorno_legado`` não é fornecido, usa contrato vazio oficial.
    Quando fornecido, apenas embrulha o retorno já calculado. Em ambos os casos,
    não altera a saída canônica nem aciona o ledger legado.
    """
    if retorno_legado is None:
        retorno_legado = {
            "eventos": [],
            "fifo_candidatos_avaliados": [],
        }

    retorno = _as_dict(retorno_legado)
    eventos_temporais = _as_list_dict(retorno.get("eventos"))
    fifo_candidatos_avaliados = _as_list_dict(retorno.get("fifo_candidatos_avaliados"))
    pagamentos_futuros_processados = _extrair_pagamentos_futuros_processados(eventos_temporais)
    saldos_por_lote = _extrair_saldos_por_lote(eventos_temporais)
    alertas_temporais = _extrair_alertas_temporais(retorno)

    estado_temporal_por_data: list[dict[str, Any]] = []
    saldos_disponiveis_por_data: list[dict[str, Any]] = []
    vencimentos_processados: list[dict[str, Any]] = []
    fontes_elegiveis_por_data: list[dict[str, Any]] = []
    campos_ausentes = [
        "estado_temporal_por_data",
        "saldos_disponiveis_por_data",
        "vencimentos_processados",
        "fontes_elegiveis_por_data",
    ]

    auditoria = _montar_auditoria(
        retorno_legado=retorno,
        eventos_temporais=eventos_temporais,
        fifo_candidatos_avaliados=fifo_candidatos_avaliados,
        pagamentos_futuros_processados=pagamentos_futuros_processados,
        saldos_por_lote=saldos_por_lote,
        alertas_temporais=alertas_temporais,
        contexto=contexto,
        campos_ausentes=campos_ausentes,
    )
    validacao = _montar_validacao(
        retorno_legado=retorno,
        eventos_temporais=eventos_temporais,
        fifo_candidatos_avaliados=fifo_candidatos_avaliados,
        campos_ausentes=campos_ausentes,
    )
    auditoria["ok"] = bool(validacao.get("ok"))

    metadados_origem = {
        "versao_microetapa": "V17-F0-V.3.7K",
        "modo_operacional_temporal": bool(modo_operacional_temporal),
        "adaptador": "construir_pacote_ledger_temporal",
        "origem_contrato_ledger_temporal": "contrato_vazio_oficial_me521b",
        "nao_altera_saida_canonica": True,
        "nao_remove_ponte_legacy": True,
        "retorno_legado_chaves": sorted(str(k) for k in retorno.keys()),
    }

    return PacoteLedgerTemporal(
        versao=VERSAO_PACOTE_LEDGER_TEMPORAL,
        modo_operacional_temporal=bool(modo_operacional_temporal),
        data_referencia=_inferir_data_referencia(contexto),
        eventos_temporais=eventos_temporais,
        estado_temporal_por_data=estado_temporal_por_data,
        saldos_por_lote=saldos_por_lote,
        saldos_disponiveis_por_data=saldos_disponiveis_por_data,
        vencimentos_processados=vencimentos_processados,
        pagamentos_futuros_processados=pagamentos_futuros_processados,
        fontes_elegiveis_por_data=fontes_elegiveis_por_data,
        alertas_temporais=alertas_temporais,
        fifo_candidatos_avaliados=fifo_candidatos_avaliados,
        auditoria_ledger_temporal=auditoria,
        validacao_ledger_temporal=validacao,
        metadados_origem=metadados_origem,
    )
