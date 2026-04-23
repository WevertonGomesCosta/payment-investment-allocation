from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
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
    componentes: list[dict[str, Any]] = field(default_factory=list)
    status_modelo: str = 'integracao_minima_v119'

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _coerce_date(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except Exception:
            return None
    return None


def _valor_pagamento(pagamento: dict[str, Any] | None) -> float:
    if not pagamento:
        return 0.0
    for chave in ('valor', 'valor_pagamento', 'valor_previsto', 'valor_original'):
        if chave in pagamento and pagamento[chave] is not None:
            return round(float(pagamento[chave] or 0.0), 2)
    return 0.0


def _normalizar_proxy_terminal(valor: Any) -> float:
    try:
        numero = float(valor or 0.0)
    except Exception:
        return 0.0
    if numero > 1.0:
        numero = numero / 100.0
    return max(numero, 0.0)


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
        round(float(deficit), 2),
        float(sem_cobertura),
        round(float(perda_terminal), 2),
        round(float(penalidade_estrategica), 2),
        round(float(penalidade_liquidez), 2),
        round(float(custo_fiscal), 2),
        round(float(custo_operacional), 2),
    )


def _horizonte_terminal_dias(estado: dict[str, Any], data_pagamento: date | None) -> int:
    data_fim = _coerce_date(estado.get('data_fim_recorte'))
    if data_pagamento is None or data_fim is None:
        return int(estado.get('dias_horizonte_terminal') or 0)
    return max((data_fim - data_pagamento).days, 0)


def _perda_terminal_por_fonte(valor_usado: float, proxy_terminal: float, dias_horizonte: int) -> float:
    fator_tempo = max(dias_horizonte, 1) / 365.0
    return round(float(valor_usado) * float(proxy_terminal) * fator_tempo, 2)


def _normalizar_fonte(item: Any, *, tipo_padrao: str) -> dict[str, Any]:
    if isinstance(item, dict):
        bruto = dict(item)
    else:
        bruto = {'id': getattr(item, 'id', None)}
    bruto.setdefault('tipo_fonte', tipo_padrao)
    bruto.setdefault('fonte_id', bruto.get('id'))
    return bruto


def alocar_pagamento_terminal_v1(
    pagamento: dict[str, Any] | None,
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    plano_switching_candidato: dict[str, Any] | None = None,
    permitir_combinacao_minima: bool = True,
    limite_fontes_candidatas: int | None = None,
) -> dict[str, Any]:
    """Compara fontes de pagamento pelo vetor terminal mínimo da V119.

    A função continua simples, mas agora já considera:
    - proxy terminal do lote/fonte;
    - horizonte do recorte;
    - combinação mínima de múltiplas fontes;
    - estado alterado por switching previamente executado.
    """

    pagamento = dict(pagamento or {})
    estado = dict(estado_global or {})
    valor = round(_valor_pagamento(pagamento), 2)
    data_pagamento = _coerce_date(pagamento.get('data_pagamento') or pagamento.get('data') or estado.get('data_evento_corrente'))
    classe = str(pagamento.get('classe_pagamento') or pagamento.get('classe') or 'NAO_CLASSIFICADA')
    saldo_disponivel = round(float(estado.get('saldo_disponivel_geral') or 0.0), 2)
    dias_horizonte = _horizonte_terminal_dias(estado, data_pagamento)

    candidatos: list[FontePagamentoCandidata] = []

    def adicionar(candidato: FontePagamentoCandidata) -> None:
        if limite_fontes_candidatas is not None and len(candidatos) >= max(limite_fontes_candidatas, 0):
            return
        candidatos.append(candidato)

    valor_coberto_saldo = min(valor, saldo_disponivel)
    deficit_saldo = max(valor - valor_coberto_saldo, 0.0)
    perda_saldo = _perda_terminal_por_fonte(valor_coberto_saldo, 0.0, dias_horizonte)
    adicionar(FontePagamentoCandidata(
        tipo_fonte='saldo_disponivel',
        fonte_id='saldo_disponivel_geral',
        valor_coberto=valor_coberto_saldo,
        valor_deficit=deficit_saldo,
        cobertura_integral=deficit_saldo <= 0.0,
        custo_fiscal_imediato=0.0,
        perda_retorno_terminal_estimada=perda_saldo,
        penalidade_liquidez_futura=valor_coberto_saldo,
        penalidade_estrategica_lote=0.0,
        score_terminal_comparativo=_score_placeholder(
            viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit_saldo > 0 else 0.0,
            deficit=deficit_saldo,
            sem_cobertura=1.0 if deficit_saldo > 0 else 0.0,
            perda_terminal=perda_saldo,
            penalidade_estrategica=0.0,
            penalidade_liquidez=valor_coberto_saldo,
            custo_fiscal=0.0,
            custo_operacional=0.0,
        ),
        justificativa='Fonte contratual mínima baseada no saldo disponível geral.',
        componentes=[{'tipo_fonte': 'saldo_disponivel', 'fonte_id': 'saldo_disponivel_geral', 'valor_utilizado': valor_coberto_saldo}],
    ))

    recebidos = estado.get('recebidos_nao_aportados_disponiveis') or []
    candidatos_combo: list[dict[str, Any]] = []
    if saldo_disponivel > 0:
        candidatos_combo.append({'tipo_fonte': 'saldo_disponivel', 'fonte_id': 'saldo_disponivel_geral', 'valor_disponivel': saldo_disponivel, 'proxy_terminal': 0.0})

    for indice, item in enumerate(recebidos, start=1):
        bruto = _normalizar_fonte(item, tipo_padrao='lote_nao_aportado')
        valor_fonte = round(float(bruto.get('valor') or bruto.get('valor_disponivel') or 0.0), 2)
        proxy_terminal = _normalizar_proxy_terminal(bruto.get('proxy_terminal_atual') or estado.get('proxy_terminal_nao_aportado_padrao'))
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        perda = _perda_terminal_por_fonte(coberto, proxy_terminal, dias_horizonte)
        candidatos_combo.append({'tipo_fonte': 'lote_nao_aportado', 'fonte_id': str(bruto.get('fonte_id') or bruto.get('id') or f'recebido_{indice}'), 'valor_disponivel': valor_fonte, 'proxy_terminal': proxy_terminal})
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_nao_aportado',
            fonte_id=str(bruto.get('fonte_id') or bruto.get('id') or f'recebido_{indice}'),
            valor_coberto=coberto,
            valor_deficit=deficit,
            cobertura_integral=deficit <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=perda,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=round(coberto * proxy_terminal, 2),
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit > 0 else 0.0,
                deficit=deficit,
                sem_cobertura=1.0 if deficit > 0 else 0.0,
                perda_terminal=perda,
                penalidade_estrategica=round(coberto * proxy_terminal, 2),
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa='Fonte estrutural: recebido/lote não aportado disponível.',
            componentes=[{'tipo_fonte': 'lote_nao_aportado', 'fonte_id': str(bruto.get('fonte_id') or bruto.get('id') or f'recebido_{indice}'), 'valor_utilizado': coberto}],
        ))

    lotes = estado.get('lotes_aportados') or []
    for indice, item in enumerate(lotes, start=1):
        bruto = _normalizar_fonte(item, tipo_padrao='lote_aportado')
        valor_fonte = round(float(bruto.get('valor_liquido_resgatavel') or bruto.get('principal_remanescente') or 0.0), 2)
        if valor_fonte <= 0.0:
            continue
        proxy_terminal = _normalizar_proxy_terminal(bruto.get('proxy_terminal_atual'))
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        perda = _perda_terminal_por_fonte(coberto, proxy_terminal, dias_horizonte)
        fonte_id = str(bruto.get('fonte_id') or bruto.get('id') or f'lote_{indice}')
        candidatos_combo.append({'tipo_fonte': 'lote_aportado', 'fonte_id': fonte_id, 'valor_disponivel': valor_fonte, 'proxy_terminal': proxy_terminal})
        justificativa = 'Resgate de lote aportado elegível no estado atual.'
        if plano_switching_candidato:
            justificativa += ' Estado avaliado com plano de switching já informado/executado até a data do pagamento.'
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_aportado',
            fonte_id=fonte_id,
            valor_coberto=coberto,
            valor_deficit=deficit,
            cobertura_integral=deficit <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=perda,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=round(coberto * proxy_terminal, 2),
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit > 0 else 0.0,
                deficit=deficit,
                sem_cobertura=1.0 if deficit > 0 else 0.0,
                perda_terminal=perda,
                penalidade_estrategica=round(coberto * proxy_terminal, 2),
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa=justificativa,
            componentes=[{'tipo_fonte': 'lote_aportado', 'fonte_id': fonte_id, 'valor_utilizado': coberto}],
        ))

    if permitir_combinacao_minima and valor > 0.0 and candidatos_combo:
        ranking_combo = sorted(
            [x for x in candidatos_combo if float(x.get('valor_disponivel') or 0.0) > 0.0],
            key=lambda item: (
                _normalizar_proxy_terminal(item.get('proxy_terminal')),
                -float(item.get('valor_disponivel') or 0.0),
                str(item.get('fonte_id') or ''),
            ),
        )
        restante = valor
        componentes: list[dict[str, Any]] = []
        perda_total = 0.0
        penalidade_estrategica_total = 0.0
        penalidade_liquidez_total = 0.0
        for item in ranking_combo:
            if restante <= 0.0:
                break
            valor_disponivel = round(float(item.get('valor_disponivel') or 0.0), 2)
            if valor_disponivel <= 0.0:
                continue
            usado = min(restante, valor_disponivel)
            proxy_terminal = _normalizar_proxy_terminal(item.get('proxy_terminal'))
            componentes.append({
                'tipo_fonte': str(item.get('tipo_fonte') or ''),
                'fonte_id': str(item.get('fonte_id') or ''),
                'valor_utilizado': round(usado, 2),
            })
            perda_total += _perda_terminal_por_fonte(usado, proxy_terminal, dias_horizonte)
            if item.get('tipo_fonte') == 'saldo_disponivel':
                penalidade_liquidez_total += usado
            else:
                penalidade_estrategica_total += usado * proxy_terminal
            restante = round(restante - usado, 2)
        valor_coberto = round(valor - max(restante, 0.0), 2)
        deficit_comb = max(valor - valor_coberto, 0.0)
        adicionar(FontePagamentoCandidata(
            tipo_fonte='combinacao_minima_fontes',
            fonte_id='combinacao_minima_controlada',
            valor_coberto=valor_coberto,
            valor_deficit=deficit_comb,
            cobertura_integral=deficit_comb <= 0.0,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=round(perda_total, 2),
            penalidade_liquidez_futura=round(penalidade_liquidez_total, 2),
            penalidade_estrategica_lote=round(penalidade_estrategica_total, 2),
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=1.0 if classe == 'PROTEGIDA' and deficit_comb > 0 else 0.0,
                deficit=deficit_comb,
                sem_cobertura=1.0 if deficit_comb > 0 else 0.0,
                perda_terminal=round(perda_total, 2),
                penalidade_estrategica=round(penalidade_estrategica_total, 2),
                penalidade_liquidez=round(penalidade_liquidez_total, 2),
                custo_fiscal=0.0,
                custo_operacional=max(len(componentes) - 1, 0),
            ),
            justificativa='Combinação mínima funcional do recorte curto, priorizando menor proxy terminal por real usado.',
            componentes=componentes,
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
            justificativa='Ausência de fonte viável no estado corrente.',
        ))

    melhor = min(candidatos, key=lambda item: item.score_terminal_comparativo)
    return {
        'status': 'integracao_minima_v119',
        'implementado': True,
        'pagamento_id': pagamento.get('id') or pagamento.get('pagamento_id') or pagamento.get('despesa_id') or '',
        'data_pagamento': data_pagamento.isoformat() if data_pagamento else None,
        'classe_pagamento': classe,
        'plano_switching_candidato_informado': bool(plano_switching_candidato),
        'fontes_candidatas': [item.para_dict() for item in candidatos],
        'melhor_acao_pagamento': f'usar_{melhor.tipo_fonte}',
        'fonte_principal_tipo': melhor.tipo_fonte,
        'fonte_principal_id': melhor.fonte_id,
        'fontes_secundarias': melhor.componentes[1:] if len(melhor.componentes) > 1 else [],
        'valor_coberto': melhor.valor_coberto,
        'valor_deficit': melhor.valor_deficit,
        'cobertura_integral': melhor.cobertura_integral,
        'data_resgate_ou_uso': data_pagamento.isoformat() if data_pagamento else None,
        'custo_fiscal_imediato': melhor.custo_fiscal_imediato,
        'perda_retorno_terminal_estimada': melhor.perda_retorno_terminal_estimada,
        'penalidade_liquidez_futura': melhor.penalidade_liquidez_futura,
        'penalidade_estrategica_lote': melhor.penalidade_estrategica_lote,
        'score_terminal_comparativo': melhor.score_terminal_comparativo,
        'justificativa': melhor.justificativa,
        'componentes_escolhidos': melhor.componentes,
        'config_resumido': dict(config or {}),
    }
