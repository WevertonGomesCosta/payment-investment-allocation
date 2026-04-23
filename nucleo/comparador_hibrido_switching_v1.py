from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ToleranciasComparadorHibrido:
    tolerancia_perda_terminal: float = 1.0
    tolerancia_patrimonio_proxy: float = 1.0
    tolerancia_deficit: float = 1.0
    tolerancia_violacoes_protegida: float = 0.5


PRIORIDADE_CLASSE = {
    'vencedor_terminal': 0,
    'vencedor_hibrido_aceitavel': 1,
    'vencedor_operacional': 2,
    'dominado_pelo_baseline': 9,
}


def _safe_float(value: Any) -> float:
    try:
        if value in (None, ''):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def classificar_cenario_diario(
    resultado: dict[str, Any],
    tolerancias: ToleranciasComparadorHibrido | None = None,
) -> dict[str, Any]:
    t = tolerancias or ToleranciasComparadorHibrido()
    delta_perda = _safe_float(resultado.get('delta_perda_terminal_vs_baseline'))
    delta_patrimonio = _safe_float(resultado.get('delta_patrimonio_proxy_vs_baseline'))
    delta_deficit = _safe_float(resultado.get('delta_deficit_vs_baseline'))
    delta_protegida = _safe_float(resultado.get('delta_violacoes_protegida_vs_baseline'))
    continua_vencedor_central = bool(resultado.get('continua_vencedor_central'))

    melhora_terminal_material = (
        delta_perda <= -t.tolerancia_perda_terminal
        and delta_patrimonio >= t.tolerancia_patrimonio_proxy
    )
    piora_terminal_material = (
        delta_perda >= t.tolerancia_perda_terminal
        or delta_patrimonio <= -t.tolerancia_patrimonio_proxy
    )
    melhora_operacional_material = (
        delta_deficit <= -t.tolerancia_deficit
        or delta_protegida <= -t.tolerancia_violacoes_protegida
    )
    piora_operacional_material = (
        delta_deficit >= t.tolerancia_deficit
        or delta_protegida >= t.tolerancia_violacoes_protegida
    )

    if continua_vencedor_central and piora_terminal_material:
        classe = 'vencedor_operacional'
        promovivel = False
        motivo = 'vence na métrica central atual, mas piora patrimônio terminal frente ao baseline'
    elif melhora_terminal_material and not piora_operacional_material:
        classe = 'vencedor_terminal'
        promovivel = True
        motivo = 'melhora patrimônio terminal sem piora operacional material frente ao baseline'
    elif continua_vencedor_central and not piora_terminal_material:
        classe = 'vencedor_hibrido_aceitavel'
        promovivel = True
        motivo = 'vence na métrica central e não piora materialmente o patrimônio terminal'
    else:
        classe = 'dominado_pelo_baseline'
        promovivel = False
        motivo = 'não oferece combinação suficiente de ganho operacional e preservação terminal'

    return {
        'classe_comparador_hibrido': classe,
        'promovivel_hibrido': promovivel,
        'bloqueado_promocao_automatica': not promovivel,
        'motivo_comparador_hibrido': motivo,
        'melhora_terminal_material': melhora_terminal_material,
        'piora_terminal_material': piora_terminal_material,
        'melhora_operacional_material': melhora_operacional_material,
        'piora_operacional_material': piora_operacional_material,
        'prioridade_classe_hibrida': PRIORIDADE_CLASSE[classe],
    }


def chave_promocao_hibrida(resultado: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(resultado.get('prioridade_classe_hibrida', PRIORIDADE_CLASSE['dominado_pelo_baseline'])),
        _safe_float(resultado.get('delta_perda_terminal_vs_baseline')),
        _safe_float(resultado.get('delta_deficit_vs_baseline')),
        -_safe_float(resultado.get('delta_patrimonio_proxy_vs_baseline')),
        tuple(resultado.get('vetor_lexicografico') or []),
        str(resultado.get('rotulo') or ''),
    )


def escolher_melhor_cenario_promovivel(resultados: Iterable[dict[str, Any]]) -> dict[str, Any] | None:
    candidatos = [item for item in resultados if bool(item.get('promovivel_hibrido'))]
    if not candidatos:
        return None
    return sorted(candidatos, key=chave_promocao_hibrida)[0]
