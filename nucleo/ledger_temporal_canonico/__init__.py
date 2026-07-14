from __future__ import annotations

import importlib.util
import sys
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


def construir_ledger_temporal_canonico(resultado: Any, parametros: Any | None = None) -> Any:
    ledger = _legacy.construir_ledger_temporal_canonico(resultado, parametros)
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
        }
    )
    if ledger.auditoria is not None:
        ledger.auditoria.resumo.update(
            {
                "motor_funcional": bool(ledger.metadados.get("motor_funcional")),
                "pacotes_normativos_completos": bool(ledger.metadados.get("pacotes_normativos_completos")),
                "argmax_comprovado": bool(ledger.metadados.get("argmax_comprovado")),
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
