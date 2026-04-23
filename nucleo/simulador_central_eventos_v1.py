from __future__ import annotations

from copy import deepcopy
from typing import Any


def simular_cenario_eventos_v1(
    estado_inicial: dict[str, Any] | None,
    eventos_candidatos: list[dict[str, Any]] | None,
    config: dict[str, Any] | None,
    horizonte: Any = None,
) -> dict[str, Any]:
    """Esqueleto executável do simulador central de eventos da V117.

    Nesta entrega a função não executa transições econômicas reais. Ela apenas
    normaliza a entrada, preserva o estado recebido e devolve uma trilha
    auditável mínima para integração incremental posterior.
    """

    estado = deepcopy(dict(estado_inicial or {}))
    eventos = [deepcopy(dict(item)) for item in (eventos_candidatos or [])]

    return {
        'status': 'esqueleto_v117',
        'implementado': False,
        'horizonte': horizonte,
        'estado_inicial_normalizado': estado,
        'estado_final_estimado': deepcopy(estado),
        'eventos_recebidos': eventos,
        'eventos_executados': [],
        'pagamentos_cobertos': [],
        'pagamentos_sem_cobertura': [],
        'patrimonio_liquido_terminal_proxy': None,
        'metrica_central': None,
        'config_resumido': dict(config or {}),
        'observacao': 'Simulador documental/técnico mínimo da V117. Sem transição econômica real nesta etapa.',
    }
