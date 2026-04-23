from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TIPOS_FONTE_SUPORTADOS = (
    'saldo_disponivel',
    'lote_nao_aportado',
    'lote_aportado',
    'combinacao_minima_fontes',
    'sem_fonte_viavel',
)


@dataclass(slots=True)
class FontePagamentoCandidata:
    tipo_fonte: str
    fonte_id: str | None
    valor_coberto: float
    valor_deficit: float
    cobertura_integral: bool
    custo_fiscal_imediato: float
    perda_retorno_terminal_estimada: float
    penalidade_liquidez_futura: float
    penalidade_estrategica_lote: float
    score_terminal_comparativo: tuple[float, float, float, float, float, float, float, float]
    justificativa: str
    status_modelo: str = 'esqueleto_v117'

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _valor_pagamento(pagamento: dict[str, Any] | None) -> float:
    if not pagamento:
        return 0.0
    for chave in ('valor', 'valor_pagamento', 'valor_previsto', 'valor_original'):
        if chave in pagamento and pagamento[chave] is not None:
            return float(pagamento[chave] or 0.0)
    return 0.0


def _score_placeholder(
    *,
    viola_protegida: float,
    deficit: float,
    sem_cobertura: float,
    perda_terminal: float,
    penalidade_estrategica: float,
    penalidade_liquidez: float,
    custo_fiscal: float,
    custo_operacional: float,
) -> tuple[float, float, float, float, float, float, float, float]:
    return (
        float(viola_protegida),
        float(deficit),
        float(sem_cobertura),
        float(perda_terminal),
        float(penalidade_estrategica),
        float(penalidade_liquidez),
        float(custo_fiscal),
        float(custo_operacional),
    )


def alocar_pagamento_terminal_v1(
    pagamento: dict[str, Any] | None,
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    plano_switching_candidato: dict[str, Any] | None = None,
    permitir_combinacao_minima: bool = True,
    limite_fontes_candidatas: int | None = None,
) -> dict[str, Any]:
    """Compara fontes de pagamento pelo vetor terminal mínimo da V117.

    Esta função é um esqueleto executável e deliberadamente conservador. Ela
    formaliza as fontes candidatas, produz score placeholder auditável e escolhe
    provisoriamente a melhor alternativa pelo menor vetor lexicográfico local.
    """

    pagamento = dict(pagamento or {})
    estado = dict(estado_global or {})
    valor = round(_valor_pagamento(pagamento), 2)
    data_pagamento = pagamento.get('data_pagamento') or pagamento.get('data') or estado.get('data_evento_corrente')
    classe = str(pagamento.get('classe_pagamento') or pagamento.get('classe') or 'NAO_CLASSIFICADA')
    saldo_disponivel = float(estado.get('saldo_disponivel_geral') or 0.0)

    candidatos: list[FontePagamentoCandidata] = []

    def adicionar(candidato: FontePagamentoCandidata) -> None:
        if limite_fontes_candidatas is not None and len(candidatos) >= max(limite_fontes_candidatas, 0):
            return
        candidatos.append(candidato)

    valor_coberto_saldo = min(valor, saldo_disponivel)
    deficit_saldo = max(valor - valor_coberto_saldo, 0.0)
    adicionar(FontePagamentoCandidata(
        tipo_fonte='saldo_disponivel',
        fonte_id='saldo_disponivel_geral',
        valor_coberto=valor_coberto_saldo,
        valor_deficit=deficit_saldo,
        cobertura_integral=deficit_saldo <= 0.0,
        custo_fiscal_imediato=0.0,
        perda_retorno_terminal_estimada=0.0,
        penalidade_liquidez_futura=max(valor_coberto_saldo, 0.0),
        penalidade_estrategica_lote=0.0,
        score_terminal_comparativo=_score_placeholder(
            viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit_saldo > 0 else 0.0,
            deficit=deficit_saldo,
            sem_cobertura=1.0 if deficit_saldo > 0 else 0.0,
            perda_terminal=0.0,
            penalidade_estrategica=0.0,
            penalidade_liquidez=max(valor_coberto_saldo, 0.0),
            custo_fiscal=0.0,
            custo_operacional=0.0,
        ),
        justificativa='Fonte contratual mínima da V117 baseada no saldo disponível geral.',
    ))

    recebidos = estado.get('recebidos_nao_aportados_disponiveis') or []
    for indice, item in enumerate(recebidos, start=1):
        bruto = item if isinstance(item, dict) else {'id': getattr(item, 'id', None), 'valor': getattr(item, 'valor', None)}
        valor_fonte = float(bruto.get('valor') or bruto.get('valor_disponivel') or 0.0)
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_nao_aportado',
            fonte_id=str(bruto.get('id') or f'recebido_{indice}'),
            valor_coberto=coberto,
            valor_deficit=deficit,
            cobertura_integral=deficit <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=coberto,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=0.0,
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit > 0 else 0.0,
                deficit=deficit,
                sem_cobertura=1.0 if deficit > 0 else 0.0,
                perda_terminal=coberto,
                penalidade_estrategica=0.0,
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa='Fonte estrutural da V117: recebido/lote não aportado disponível.',
        ))

    lotes = estado.get('lotes_aportados') or []
    for indice, item in enumerate(lotes, start=1):
        bruto = item if isinstance(item, dict) else {
            'id': getattr(item, 'id', None),
            'principal_remanescente': getattr(item, 'principal_remanescente', None),
            'investimento': getattr(item, 'investimento', None),
        }
        valor_fonte = float(bruto.get('valor_liquido_resgatavel') or bruto.get('principal_remanescente') or 0.0)
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_aportado',
            fonte_id=str(bruto.get('id') or f'lote_{indice}'),
            valor_coberto=coberto,
            valor_deficit=deficit,
            cobertura_integral=deficit <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=coberto,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=coberto,
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit > 0 else 0.0,
                deficit=deficit,
                sem_cobertura=1.0 if deficit > 0 else 0.0,
                perda_terminal=coberto,
                penalidade_estrategica=coberto,
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa='Fonte estrutural da V117: resgate de lote aportado elegível.',
        ))

    if permitir_combinacao_minima:
        soma_nao_aportado = sum(float((x if isinstance(x, dict) else {}).get('valor') or 0.0) for x in recebidos)
        valor_combinado = min(valor, saldo_disponivel + soma_nao_aportado)
        deficit_comb = max(valor - valor_combinado, 0.0)
        adicionar(FontePagamentoCandidata(
            tipo_fonte='combinacao_minima_fontes',
            fonte_id='combinacao_minima_controlada',
            valor_coberto=valor_combinado,
            valor_deficit=deficit_comb,
            cobertura_integral=deficit_comb <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=max(valor_combinado - saldo_disponivel, 0.0),
            penalidade_liquidez_futura=min(valor_combinado, saldo_disponivel),
            penalidade_estrategica_lote=0.0,
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit_comb > 0 else 0.0,
                deficit=deficit_comb,
                sem_cobertura=1.0 if deficit_comb > 0 else 0.0,
                perda_terminal=max(valor_combinado - saldo_disponivel, 0.0),
                penalidade_estrategica=0.0,
                penalidade_liquidez=min(valor_combinado, saldo_disponivel),
                custo_fiscal=0.0,
                custo_operacional=1.0,
            ),
            justificativa='Combinação mínima placeholder da V117; não implica política final.',
        ))

    if not candidatos:
        adicionar(FontePagamentoCandidata(
            tipo_fonte='sem_fonte_viavel',
            fonte_id=None,
            valor_coberto=0.0,
            valor_deficit=valor,
            cobertura_integral=False,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=0.0,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=0.0,
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' else 0.0,
                deficit=valor,
                sem_cobertura=1.0,
                perda_terminal=0.0,
                penalidade_estrategica=0.0,
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa='Ausência de fonte viável detectada pelo esqueleto da V117.',
        ))

    melhor = min(candidatos, key=lambda item: item.score_terminal_comparativo)
    return {
        'status': 'esqueleto_v117',
        'implementado': False,
        'pagamento_id': pagamento.get('id') or pagamento.get('pagamento_id') or '',
        'data_pagamento': data_pagamento,
        'classe_pagamento': classe,
        'plano_switching_candidato_informado': bool(plano_switching_candidato),
        'fontes_candidatas': [item.para_dict() for item in candidatos],
        'melhor_acao_pagamento': f'usar_{melhor.tipo_fonte}',
        'fonte_principal_tipo': melhor.tipo_fonte,
        'fonte_principal_id': melhor.fonte_id,
        'fontes_secundarias': [],
        'valor_coberto': melhor.valor_coberto,
        'valor_deficit': melhor.valor_deficit,
        'cobertura_integral': melhor.cobertura_integral,
        'data_resgate_ou_uso': data_pagamento,
        'custo_fiscal_imediato': melhor.custo_fiscal_imediato,
        'perda_retorno_terminal_estimada': melhor.perda_retorno_terminal_estimada,
        'penalidade_liquidez_futura': melhor.penalidade_liquidez_futura,
        'penalidade_estrategica_lote': melhor.penalidade_estrategica_lote,
        'score_terminal_comparativo': melhor.score_terminal_comparativo,
        'justificativa': melhor.justificativa,
        'config_resumido': dict(config or {}),
    }
