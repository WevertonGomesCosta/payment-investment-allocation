from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


_LEGACY_NAME = "nucleo._ledger_temporal_canonico_legacy"
_LEGACY_PATH = Path(__file__).resolve().parents[1] / "ledger_temporal_canonico.py"


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


def _numero(valor: Any) -> float | None:
    if valor is None or isinstance(valor, bool):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if numero == numero else None


def _agregar_numericos(itens: list[Any], campo: str) -> float | str | None:
    valores = [getattr(item, campo, None) for item in itens]
    numeros = [_numero(valor) for valor in valores]
    if all(numero is not None for numero in numeros):
        return round(sum(float(numero) for numero in numeros if numero is not None), 10)
    categorias = {str(valor).strip() for valor in valores if str(valor).strip()}
    if categorias == {"nao_aplicavel"}:
        return "nao_aplicavel"
    if "nao_materializado" in categorias:
        return "nao_materializado"
    return None


def _agregar_movimentos(movimentos: list[Any], *, campo_valor: str) -> list[Any]:
    grupos: dict[tuple[Any, Any, Any], list[Any]] = {}
    ordem: list[tuple[Any, Any, Any]] = []
    for movimento in movimentos:
        chave = (
            getattr(movimento, "fonte_id", None),
            getattr(movimento, "data", None),
            getattr(movimento, "pacote_id", None),
        )
        if chave not in grupos:
            grupos[chave] = []
            ordem.append(chave)
        grupos[chave].append(movimento)

    consolidados: list[Any] = []
    for chave in ordem:
        itens = grupos[chave]
        if len(itens) == 1:
            consolidados.append(itens[0])
            continue

        consolidado = deepcopy(itens[0])
        valores = [_numero(getattr(item, campo_valor, None)) for item in itens]
        total = round(sum(float(valor or 0.0) for valor in valores), 10)
        antes = [
            valor
            for item in itens
            for valor in (_numero(getattr(item, "valor_disponivel_antes_referencial", None)),)
            if valor is not None
        ]
        depois = [
            valor
            for item in itens
            for valor in (_numero(getattr(item, "valor_disponivel_depois_referencial", None)),)
            if valor is not None
        ]
        saldos_antes = [
            valor
            for item in itens
            for valor in (_numero(getattr(item, "saldo_antes_fonte", None)),)
            if valor is not None
        ]
        saldos_depois = [
            valor
            for item in itens
            for valor in (_numero(getattr(item, "saldo_remanescente_fonte", None)),)
            if valor is not None
        ]
        obrigacoes_ids = sorted(
            {
                str(getattr(item, "obrigacao_id"))
                for item in itens
                if getattr(item, "obrigacao_id", None) not in (None, "")
            }
        )

        setattr(consolidado, campo_valor, total)
        consolidado.valor_disponivel_antes_referencial = max(antes) if antes else None
        consolidado.valor_disponivel_depois_referencial = min(depois) if depois else None
        consolidado.obrigacao_id = None
        consolidado.saldo_antes_fonte = max(saldos_antes) if saldos_antes else consolidado.valor_disponivel_antes_referencial
        consolidado.saldo_remanescente_fonte = min(saldos_depois) if saldos_depois else consolidado.valor_disponivel_depois_referencial
        consolidado.valor_liquido_resgate = total
        consolidado.valor_bruto_resgate = _agregar_numericos(itens, "valor_bruto_resgate")
        consolidado.imposto_resgate = _agregar_numericos(itens, "imposto_resgate")
        consolidado.status_saldo_antes_fonte = "materializado" if consolidado.saldo_antes_fonte is not None else "nao_materializado"
        consolidado.status_valor_liquido_resgate = "materializado"
        consolidado.status_saldo_remanescente_fonte = "materializado" if consolidado.saldo_remanescente_fonte is not None else "nao_materializado"
        consolidado.metadados = dict(getattr(consolidado, "metadados", {}) or {})
        consolidado.metadados.update(
            {
                "movimento_agregado_por_fonte_data_pacote": True,
                "qtd_movimentos_originais": len(itens),
                "obrigacoes_ids": obrigacoes_ids,
                "regra_agregacao": "soma_consumo_max_saldo_antes_min_saldo_depois",
            }
        )
        referencias = []
        for item in itens:
            ref = getattr(item, "referencia_original", {}) or {}
            referencias.append(asdict(ref) if is_dataclass(ref) else deepcopy(ref))
        consolidado.referencia_original = dict(getattr(consolidado, "referencia_original", {}) or {})
        consolidado.referencia_original["movimentos_originais_agregados"] = referencias
        consolidados.append(consolidado)
    return consolidados


def _materializar_movimentos_switching(ledger: Any) -> None:
    existentes = {
        (
            getattr(item, "fonte_id", None),
            getattr(item, "data", None),
            getattr(item, "pacote_id", None),
            getattr(item, "tipo", None),
        )
        for item in list(ledger.fontes_utilizadas or [])
    }
    novos = []
    for switching in list(ledger.switchings_escolhidos or []):
        fonte_id = getattr(switching, "lote_origem_id", None)
        data_switching = getattr(switching, "data", None)
        pacote_id = getattr(switching, "pacote_id", None)
        valor = _numero(getattr(switching, "valor_liquido_migrado_referencial", None))
        chave = (fonte_id, data_switching, pacote_id, "migracao_switching_referencial")
        if not fonte_id or data_switching is None or valor is None or valor <= 0 or chave in existentes:
            continue
        referencia_switching = dict(getattr(switching, "referencia_original", {}) or {})
        movimento = _legacy.LancamentoFonteLedger(
            data=data_switching,
            tipo="migracao_switching_referencial",
            fonte_id=str(fonte_id),
            pacote_id=pacote_id,
            obrigacao_id=None,
            valor_referencial=round(valor, 10),
            valor_disponivel_antes_referencial=round(valor, 10),
            valor_disponivel_depois_referencial=0.0,
            tipo_fonte="origem_switching_integral",
            origem_fonte="switchings_escolhidos_temporalmente",
            status="migrado_integralmente_por_switching_no_pacote_vencedor",
            referencia_original=referencia_switching,
            metadados={
                "origem": "switchings_escolhidos_temporalmente",
                "switching_id": getattr(switching, "switching_id", None),
                "lote_destino_id": getattr(switching, "lote_destino_id", None),
                "movimento_complementar_ao_pagamento": True,
                "conservacao_valor_switching": True,
            },
            fonte_id_tecnico=str(fonte_id),
            lote_id_operacional=str(fonte_id),
            saldo_antes_fonte=round(valor, 10),
            valor_bruto_resgate="nao_aplicavel",
            imposto_resgate="nao_aplicavel",
            valor_liquido_resgate=round(valor, 10),
            saldo_remanescente_fonte=0.0,
            status_saldo_antes_fonte="materializado",
            status_valor_bruto_resgate="nao_aplicavel",
            status_imposto_resgate="nao_aplicavel",
            status_valor_liquido_resgate="materializado",
            status_saldo_remanescente_fonte="materializado",
        )
        novos.append(movimento)
        existentes.add(chave)
    ledger.fontes_utilizadas.extend(novos)
    ledger.metadados["qtd_movimentos_switching_materializados"] = len(novos)


def _reconstruir_lancamentos_por_data(ledger: Any) -> None:
    ledger.lancamentos_por_data = {}
    colecoes = (
        ledger.eventos,
        ledger.obrigacoes_cobertas,
        ledger.obrigacoes_bloqueadas,
        ledger.fontes_utilizadas,
        ledger.fontes_reservadas,
        ledger.switchings_escolhidos,
        ledger.bloqueios,
    )
    for colecao in colecoes:
        for item in list(colecao or []):
            data_item = getattr(item, "data", None) or ledger.data_referencia
            if data_item is None:
                continue
            registro = asdict(item) if is_dataclass(item) else deepcopy(item)
            ledger.lancamentos_por_data.setdefault(data_item, []).append(registro)


def construir_ledger_temporal_canonico(resultado: Any, parametros: Any | None = None) -> Any:
    ledger = _legacy.construir_ledger_temporal_canonico(resultado, parametros)
    ledger.fontes_utilizadas = _agregar_movimentos(
        list(ledger.fontes_utilizadas or []),
        campo_valor="valor_referencial",
    )
    ledger.fontes_reservadas = _agregar_movimentos(
        list(ledger.fontes_reservadas or []),
        campo_valor="valor_reservado_referencial",
    )
    _materializar_movimentos_switching(ledger)
    _reconstruir_lancamentos_por_data(ledger)

    metadados_resultado = dict(getattr(resultado, "metadados", {}) or {})
    campos_promovidos = (
        "motor_funcional",
        "funcao_objetivo",
        "pacotes_normativos",
        "pacotes_normativos_completos",
        "argmax_comprovado",
        "comparacao_mesmo_estado",
        "obrigacoes_integralmente_cobertas",
        "horizonte_terminal",
        "evidencias_economicas_por_data",
        "resultado_terminal",
        "aderencia_terminal",
        "ganho_terminal",
    )
    for campo in campos_promovidos:
        if campo in metadados_resultado:
            ledger.metadados[campo] = metadados_resultado[campo]
    ledger.metadados.update(
        {
            "decisao_derivada_exclusivamente_etapa5": True,
            "etapa6_sem_reotimizacao_confirmada": True,
            "evidencia_terminal_obrigatoria": True,
            "movimentos_fontes_agregados_por_pacote": True,
        }
    )
    if ledger.auditoria is not None:
        bloqueios_preexistentes = [
            bloqueio
            for bloqueio in list(ledger.auditoria.bloqueios or [])
            if bloqueio not in {
                "motor_funcional_nao_declarado",
                "pacotes_normativos_incompletos",
                "argmax_nao_comprovado",
            }
        ]
        ledger.auditoria.bloqueios = bloqueios_preexistentes
        ledger.auditoria.resumo.update(
            {
                "motor_funcional": bool(ledger.metadados.get("motor_funcional")),
                "pacotes_normativos_completos": bool(ledger.metadados.get("pacotes_normativos_completos")),
                "argmax_comprovado": bool(ledger.metadados.get("argmax_comprovado")),
                "qtd_fontes_utilizadas_pos_agregacao": len(ledger.fontes_utilizadas),
                "qtd_fontes_reservadas_pos_agregacao": len(ledger.fontes_reservadas),
                "qtd_movimentos_switching_materializados": ledger.metadados.get("qtd_movimentos_switching_materializados", 0),
            }
        )
        if not ledger.metadados.get("motor_funcional"):
            ledger.auditoria.bloqueios.append("motor_funcional_nao_declarado")
        if not ledger.metadados.get("pacotes_normativos_completos"):
            ledger.auditoria.bloqueios.append("pacotes_normativos_incompletos")
        if not ledger.metadados.get("argmax_comprovado"):
            ledger.auditoria.bloqueios.append("argmax_nao_comprovado")
        ledger.auditoria.ok = not ledger.auditoria.bloqueios
    ledger.pronto_para_etapa_posterior = bool(
        ledger.pronto_para_etapa_posterior
        and ledger.auditoria is not None
        and ledger.auditoria.ok
        and ledger.metadados.get("aderencia_terminal") is True
    )
    return ledger


__all__ = sorted(set(getattr(_legacy, "__all__", [])) | {"construir_ledger_temporal_canonico"})
