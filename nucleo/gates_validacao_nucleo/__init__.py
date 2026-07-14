from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


_LEGACY_NAME = "nucleo._gates_validacao_nucleo_legacy"
_LEGACY_PATH = Path(__file__).resolve().parents[1] / "gates_validacao_nucleo.py"


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


def _adicionar_bloqueio_motor(gate: Any, codigo: str, mensagem: str, ledger: Any, observado: Any, esperado: Any) -> None:
    evidencia = _legacy._nova_evidencia(
        gate.gate_id,
        getattr(ledger, "data_referencia", None),
        "motor_temporal_conjunto",
        None,
        codigo,
        observado,
        esperado,
        None,
        "bloqueio",
        mensagem,
        {"origem_formal": "LedgerTemporalCanonico", "metadados_ledger": dict(getattr(ledger, "metadados", {}) or {})},
    )
    _legacy._adicionar_bloqueio(
        gate,
        codigo,
        mensagem,
        getattr(ledger, "data_referencia", None),
        "motor_temporal_conjunto",
        None,
        evidencia,
    )


def _gate_motor_funcional(ledger: Any) -> Any:
    gate = _legacy._novo_gate("gate_motor_funcional", "Motor temporal funcional e objetivo terminal")
    metadados = dict(getattr(ledger, "metadados", {}) or {})
    evidencias = dict(metadados.get("evidencias_economicas_por_data", {}) or {})

    requisitos = {
        "motor_funcional": metadados.get("motor_funcional") is True,
        "pacotes_normativos_completos": metadados.get("pacotes_normativos_completos") is True,
        "argmax_comprovado": metadados.get("argmax_comprovado") is True,
        "comparacao_mesmo_estado": metadados.get("comparacao_mesmo_estado") is True,
        "obrigacoes_integralmente_cobertas": metadados.get("obrigacoes_integralmente_cobertas") is True,
        "aderencia_terminal": metadados.get("aderencia_terminal") is True,
        "resultado_terminal_materializado": isinstance(metadados.get("resultado_terminal"), (int, float)),
        "evidencias_por_data": bool(evidencias),
    }
    mensagens = {
        "motor_funcional": "Ledger não declara uso do motor temporal funcional.",
        "pacotes_normativos_completos": "Nem todas as datas avaliaram exatamente os pacotes normativos permitidos.",
        "argmax_comprovado": "A escolha do pacote vencedor não está comprovada como argmax do patrimônio terminal.",
        "comparacao_mesmo_estado": "Pacotes não estão comprovadamente comparados a partir do mesmo estado inicial.",
        "obrigacoes_integralmente_cobertas": "Há obrigação obrigatória sem cobertura integral na trajetória vencedora.",
        "aderencia_terminal": "A trajetória vencedora não demonstra aderência ao objetivo econômico terminal.",
        "resultado_terminal_materializado": "Resultado terminal não foi materializado numericamente no ledger.",
        "evidencias_por_data": "Ledger não contém matriz econômica por data/pacote.",
    }
    for codigo, ok in requisitos.items():
        if not ok:
            _adicionar_bloqueio_motor(gate, codigo, mensagens[codigo], ledger, metadados.get(codigo), True)

    for data_txt, evidencia in sorted(evidencias.items()):
        permitidos = set(evidencia.get("pacotes_permitidos", []) or [])
        avaliados = set(evidencia.get("pacotes_avaliados", []) or [])
        if permitidos != avaliados:
            _adicionar_bloqueio_motor(
                gate,
                f"pacotes_divergentes:{data_txt}",
                f"Pacotes avaliados divergem dos permitidos em {data_txt}.",
                ledger,
                sorted(avaliados),
                sorted(permitidos),
            )
        if evidencia.get("argmax_comprovado") is not True:
            _adicionar_bloqueio_motor(
                gate,
                f"argmax_ausente:{data_txt}",
                f"Argmax não comprovado em {data_txt}.",
                ledger,
                evidencia.get("argmax_comprovado"),
                True,
            )
        if evidencia.get("pacote_vencedor") not in permitidos:
            _adicionar_bloqueio_motor(
                gate,
                f"vencedor_fora_contrato:{data_txt}",
                f"Pacote vencedor não pertence ao conjunto permitido em {data_txt}.",
                ledger,
                evidencia.get("pacote_vencedor"),
                sorted(permitidos),
            )

    gate.resumo.update(
        {
            "qtd_datas_auditadas": len(evidencias),
            "funcao_objetivo": metadados.get("funcao_objetivo"),
            "resultado_terminal": metadados.get("resultado_terminal"),
            "requisitos": requisitos,
        }
    )
    return _legacy._finalizar_gate(gate, len(evidencias))


def validar_gates_nucleo(ledger: Any, parametros: Any | None = None) -> Any:
    resultado = _legacy.validar_gates_nucleo(ledger, parametros)
    gate_motor = _gate_motor_funcional(ledger)
    resultado.gates.append(gate_motor)
    resultado.bloqueios.extend(gate_motor.bloqueios)
    resultado.avisos.extend(gate_motor.avisos)
    resultado.evidencias.extend(gate_motor.evidencias)
    resultado.ok = not resultado.bloqueios
    resultado.pronto_para_etapa8 = bool(
        resultado.ok
        and getattr(ledger, "auditoria", None) is not None
        and ledger.auditoria.ok
        and getattr(ledger, "pronto_para_etapa_posterior", False)
    )
    resumo = resultado.resumo
    resumo.qtd_gates = len(resultado.gates)
    resumo.qtd_gates_executados = sum(1 for gate in resultado.gates if gate.executado)
    resumo.qtd_gates_aprovados = sum(1 for gate in resultado.gates if gate.aprovado)
    resumo.qtd_gates_reprovados = sum(1 for gate in resultado.gates if not gate.aprovado and not gate.nao_aplicavel)
    resumo.qtd_gates_nao_aplicaveis = sum(1 for gate in resultado.gates if gate.nao_aplicavel)
    resumo.qtd_bloqueios = len(resultado.bloqueios)
    resumo.qtd_avisos = len(resultado.avisos)
    resumo.pronto_para_etapa8 = resultado.pronto_para_etapa8
    resultado.metadados.update(
        {
            "gate_motor_funcional_obrigatorio": True,
            "evidencia_terminal_obrigatoria": True,
            "motor_funcional_aprovado": gate_motor.aprovado,
        }
    )
    return resultado


__all__ = sorted(set(getattr(_legacy, "__all__", [])) | {"validar_gates_nucleo"})
