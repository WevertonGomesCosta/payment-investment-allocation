from __future__ import annotations

from typing import Any


ORDEM_METRICA_CANONICA = (
    'violacoes_protegida',
    'deficit_liquido_total',
    'pagamentos_sem_cobertura_integral',
    'perda_patrimonio_liquido_terminal',
    'destruicao_estrategica_lotes',
    'deterioracao_liquidez_futura',
    'custo_fiscal_imediato',
    'custo_operacional',
)


def vetor_lexicografico_central(metrica: dict[str, Any] | None) -> tuple[float, float, float, float, float, float, float, float]:
    dados = dict(metrica or {})
    return tuple(float(dados.get(chave) or 0.0) for chave in ORDEM_METRICA_CANONICA)


def avaliar_cenarios_conjuntos_v1(
    cenarios: list[dict[str, Any]] | None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Avalia cenários por um vetor lexicográfico mínimo e auditável.

    A função é um esqueleto executável da V117: aceita cenários já materializados,
    normaliza a métrica central e produz um ranking determinístico sem afirmar
    completude econômica do processo.
    """

    ranking: list[dict[str, Any]] = []
    for indice, bruto in enumerate(cenarios or [], start=1):
        cenario = dict(bruto)
        metrica = cenario.get('metrica_central') or {}
        vetor = vetor_lexicografico_central(metrica)
        ranking.append({
            'cenario_id': cenario.get('cenario_id') or f'cenario_{indice}',
            'descricao': cenario.get('descricao') or '',
            'vetor_lexicografico': vetor,
            'metrica_central': metrica,
            'status_cenario': cenario.get('status') or 'informado',
        })

    ranking.sort(key=lambda item: item['vetor_lexicografico'])
    melhor = ranking[0] if ranking else None
    return {
        'status': 'esqueleto_v117',
        'implementado': False,
        'ordem_metrica_canonica': ORDEM_METRICA_CANONICA,
        'quantidade_cenarios': len(ranking),
        'melhor_cenario': melhor,
        'ranking_cenarios': ranking,
        'config_resumido': dict(config or {}),
    }
