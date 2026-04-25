from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Iterable

from nucleo.pagamentos.modelos_script1.heuristicas_fase1 import (
    avaliar_heuristicas_fase1_por_fonte,
    carregar_parametros_fase1,
)


TIPOS_FONTE_SUPORTADOS = (
    'saldo_disponivel',
    'lote_nao_aportado',
    'lote_aportado',
    'combinacao_minima_fontes',
    'cenario_switching_elegivel',
    'sem_fonte_viavel',
)

from nucleo.utilitarios_neutros import _coerce_date, _safe_float
CLASSES_SWITCHING_PROMOVIVEIS = {'vencedor_terminal', 'vencedor_hibrido_aceitavel'}


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
    status_modelo: str = 'funcional_v141'
    score_auxiliar_script1: tuple[float, float, float] = (0.0, 0.0, 0.0)
    chave_decisao_final: tuple[Any, ...] = field(default_factory=tuple)
    metadados_extras: dict[str, Any] = field(default_factory=dict)

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_str(valor: Any) -> str:
    return '' if valor is None else str(valor)


def _dias_idade_fonte(data_base: date | None, data_origem: date | None) -> int:
    if data_base is None or data_origem is None:
        return 0
    return max((data_base - data_origem).days, 0)


def _montar_chave_decisao_final(candidato: FontePagamentoCandidata) -> tuple[Any, ...]:
    score = tuple(candidato.score_terminal_comparativo)
    aux = tuple(candidato.score_auxiliar_script1 or (0.0, 0.0, 0.0))
    return (
        score[0],
        score[1],
        score[2],
        score[3],
        aux[0],
        aux[1],
        aux[2],
        score[4],
        score[5],
        score[6],
        score[7],
        _safe_str(candidato.tipo_fonte),
        _safe_str(candidato.fonte_id),
    )


def _aplicar_heuristicas_script1(
    candidato: FontePagamentoCandidata,
    *,
    valor_pagamento: float,
    dias_horizonte: int,
    config: dict[str, Any] | None,
) -> FontePagamentoCandidata:
    meta = dict(candidato.metadados_extras or {})
    if bool((config or {}).get('desabilitar_modelos_script1_fase1')):
        meta['heuristicas_script1_fase1'] = {
            'desabilitada': True,
            'justificativa': 'Heurísticas H1-H3 explicitamente desabilitadas para comparação controlada.',
            'score_auxiliar_script1': (0.0, 0.0, 0.0),
        }
        candidato.score_auxiliar_script1 = (0.0, 0.0, 0.0)
        candidato.chave_decisao_final = _montar_chave_decisao_final(candidato)
        candidato.metadados_extras = meta
        return candidato

    params = carregar_parametros_fase1(config)
    heur = avaliar_heuristicas_fase1_por_fonte(
        tipo_fonte=candidato.tipo_fonte,
        valor_pagamento=valor_pagamento,
        valor_coberto=candidato.valor_coberto,
        valor_deficit=candidato.valor_deficit,
        custo_fiscal_imediato=candidato.custo_fiscal_imediato,
        perda_retorno_terminal_estimada=candidato.perda_retorno_terminal_estimada,
        penalidade_liquidez_futura=candidato.penalidade_liquidez_futura,
        penalidade_estrategica_lote=candidato.penalidade_estrategica_lote,
        dias_horizonte=dias_horizonte,
        dias_idade_fonte=int(meta.get('dias_idade_fonte') or 0),
        proxy_terminal_fonte=float(meta.get('proxy_terminal_fonte') or 0.0),
        params=params,
    )
    meta['heuristicas_script1_fase1'] = heur.para_dict()
    candidato.score_auxiliar_script1 = heur.score_auxiliar_script1
    candidato.chave_decisao_final = _montar_chave_decisao_final(candidato)
    candidato.metadados_extras = meta
    return candidato


def _valor_pagamento(pagamento: dict[str, Any] | None) -> float:
    if not pagamento:
        return 0.0
    for chave in ('valor', 'valor_pagamento', 'valor_previsto', 'valor_original'):
        if chave in pagamento and pagamento[chave] is not None:
            return round(_safe_float(pagamento[chave]), 2)
    return 0.0


def _normalizar_proxy_terminal(valor: Any) -> float:
    numero = _safe_float(valor)
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


def _proporcao_utilizada(valor_utilizado: float, valor_total: float) -> float:
    if valor_total <= 0:
        return 0.0
    return max(min(valor_utilizado / valor_total, 1.0), 0.0)


def _estimar_custo_fiscal_lote(bruto: dict[str, Any], valor_utilizado: float, data_pagamento: date | None) -> float:
    valor_total = round(_safe_float(bruto.get('valor_liquido_resgatavel') or bruto.get('valor_disponivel') or bruto.get('principal_remanescente')), 2)
    principal_total = round(_safe_float(bruto.get('principal_remanescente') or bruto.get('valor_inicial')), 2)
    if valor_total <= 0.0 or valor_utilizado <= 0.0:
        return 0.0
    ganho_total = max(valor_total - principal_total, 0.0)
    if ganho_total <= 0.0:
        return 0.0
    data_aplicacao = _coerce_date(bruto.get('data_aplicacao') or bruto.get('data_recebimento'))
    dias = max(((data_pagamento or data_aplicacao or date.today()) - (data_aplicacao or (data_pagamento or date.today()))).days, 0)
    if dias <= 180:
        aliquota = 0.225
    elif dias <= 360:
        aliquota = 0.20
    elif dias <= 720:
        aliquota = 0.175
    else:
        aliquota = 0.15
    ganho_utilizado = ganho_total * _proporcao_utilizada(valor_utilizado, valor_total)
    return round(max(ganho_utilizado * aliquota, 0.0), 2)


def _fonte_disponivel_na_data(bruto: dict[str, Any], data_pagamento: date | None) -> tuple[bool, str]:
    tipo = _safe_str(bruto.get('tipo_fonte'))
    data_recebimento = _coerce_date(bruto.get('data_recebimento'))
    if tipo == 'lote_nao_aportado' and data_recebimento and data_pagamento and data_recebimento > data_pagamento:
        return False, 'recebimento_futuro'
    carencia_ate = _coerce_date(bruto.get('carencia_ate'))
    if tipo == 'lote_aportado' and carencia_ate and data_pagamento and carencia_ate > data_pagamento:
        return False, 'carencia_ativa'
    return True, ''


def _impacto_unitario_combo(item: dict[str, Any]) -> tuple[float, float, float, str]:
    valor_disponivel = max(_safe_float(item.get('valor_disponivel')), 0.0)
    proxy = _normalizar_proxy_terminal(item.get('proxy_terminal'))
    custo_fiscal = max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0)
    custo_rate = custo_fiscal / max(valor_disponivel, 1.0)
    liquidez = _safe_float(item.get('penalidade_liquidez_unitaria'), 0.0)
    return (proxy + custo_rate + liquidez, custo_rate, -valor_disponivel, _safe_str(item.get('fonte_id')))


def _chave_combo_script1(item: dict[str, Any], *, valor_pagamento: float, dias_horizonte: int, config: dict[str, Any] | None) -> tuple[Any, ...]:
    heur = avaliar_heuristicas_fase1_por_fonte(
        tipo_fonte=_safe_str(item.get('tipo_fonte')),
        valor_pagamento=valor_pagamento,
        valor_coberto=min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)),
        valor_deficit=max(valor_pagamento - max(_safe_float(item.get('valor_disponivel')), 0.0), 0.0),
        custo_fiscal_imediato=max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0),
        perda_retorno_terminal_estimada=_perda_terminal_por_fonte(
            min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)),
            _normalizar_proxy_terminal(item.get('proxy_terminal')),
            dias_horizonte,
        ),
        penalidade_liquidez_futura=max(_safe_float(item.get('penalidade_liquidez_unitaria')), 0.0) * min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)),
        penalidade_estrategica_lote=min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)) * _normalizar_proxy_terminal(item.get('proxy_terminal')),
        dias_horizonte=dias_horizonte,
        dias_idade_fonte=int(item.get('dias_idade_fonte') or 0),
        proxy_terminal_fonte=_normalizar_proxy_terminal(item.get('proxy_terminal')),
        params=carregar_parametros_fase1(config),
    )
    return tuple(heur.score_auxiliar_script1) + _impacto_unitario_combo(item)


def _iterar_planos_switching(plano_switching_candidato: Any) -> Iterable[dict[str, Any]]:
    if not plano_switching_candidato:
        return []
    if isinstance(plano_switching_candidato, list):
        return [x for x in plano_switching_candidato if isinstance(x, dict)]
    if isinstance(plano_switching_candidato, dict):
        for chave in ('cenarios_promoviveis', 'planos_switching_promoviveis', 'cenarios_filtrados_hibrido', 'cenarios_switching_elegiveis'):
            valor = plano_switching_candidato.get(chave)
            if isinstance(valor, list):
                return [x for x in valor if isinstance(x, dict)]
        return [plano_switching_candidato]
    return []


def _plano_switching_promovivel(plano: dict[str, Any]) -> bool:
    classe = _safe_str(plano.get('classe_comparador_hibrido'))
    return bool(plano.get('promovivel_hibrido')) or classe in CLASSES_SWITCHING_PROMOVIVEIS


def _estado_pos_switching(plano: dict[str, Any]) -> dict[str, Any] | None:
    for chave in ('estado_pos_switching', 'estado_global_pos_switching', 'estado_alterado', 'estado_simulado_pos_switching'):
        valor = plano.get(chave)
        if isinstance(valor, dict):
            return deepcopy(valor)
    return None


def alocar_pagamento_terminal_v1(
    pagamento: dict[str, Any] | None,
    estado_global: dict[str, Any] | None,
    config: dict[str, Any] | None,
    plano_switching_candidato: dict[str, Any] | list[dict[str, Any]] | None = None,
    permitir_combinacao_minima: bool = True,
    limite_fontes_candidatas: int | None = None,
    *,
    _permitir_cenario_switching: bool = True,
) -> dict[str, Any]:
    """Primeira versão funcional do alocador terminal com Fase 1 do Script 1.

    A V141 compara explicitamente:
    - saldo disponível;
    - lote não aportado disponível na data;
    - lote aportado resgatável na data, com custo fiscal estimado;
    - combinação mínima funcional entre fontes;
    - cenário com switching elegível já filtrado pelo comparador híbrido.
    """

    pagamento = dict(pagamento or {})
    estado = dict(estado_global or {})
    valor = round(_valor_pagamento(pagamento), 2)
    data_pagamento = _coerce_date(pagamento.get('data_pagamento') or pagamento.get('data') or estado.get('data_evento_corrente'))
    classe = _safe_str(pagamento.get('classe_pagamento') or pagamento.get('classe') or 'NAO_CLASSIFICADA')
    saldo_disponivel = round(_safe_float(estado.get('saldo_disponivel_geral')), 2)
    dias_horizonte = _horizonte_terminal_dias(estado, data_pagamento)

    candidatos: list[FontePagamentoCandidata] = []

    def adicionar(candidato: FontePagamentoCandidata) -> None:
        if limite_fontes_candidatas is not None and len(candidatos) >= max(limite_fontes_candidatas, 0):
            return
        candidatos.append(candidato)

    if valor <= 0.0:
        candidato_nulo = FontePagamentoCandidata(
            tipo_fonte='saldo_disponivel',
            fonte_id='saldo_disponivel_geral',
            valor_coberto=0.0,
            valor_deficit=0.0,
            cobertura_integral=True,
            custo_fiscal_imediato=0.0,
            perda_retorno_terminal_estimada=0.0,
            penalidade_liquidez_futura=0.0,
            penalidade_estrategica_lote=0.0,
            score_terminal_comparativo=_score_placeholder(
                viola_protegida=0.0,
                deficit=0.0,
                sem_cobertura=0.0,
                perda_terminal=0.0,
                penalidade_estrategica=0.0,
                penalidade_liquidez=0.0,
                custo_fiscal=0.0,
                custo_operacional=0.0,
            ),
            justificativa='Pagamento nulo ou ausente no recorte.',
            componentes=[],
        )
        adicionar(candidato_nulo)
    else:
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
            justificativa='Fonte contratual baseada no saldo disponível geral do estado corrente.',
            componentes=[{'tipo_fonte': 'saldo_disponivel', 'fonte_id': 'saldo_disponivel_geral', 'valor_utilizado': valor_coberto_saldo}],
            metadados_extras={'proxy_terminal_fonte': 0.0, 'dias_idade_fonte': 0},
        ))

    candidatos_combo: list[dict[str, Any]] = []
    if saldo_disponivel > 0.0:
        candidatos_combo.append({
            'tipo_fonte': 'saldo_disponivel',
            'fonte_id': 'saldo_disponivel_geral',
            'valor_disponivel': saldo_disponivel,
            'proxy_terminal': 0.0,
            'custo_fiscal_total_estimado': 0.0,
            'penalidade_liquidez_unitaria': 0.005,
            'dias_idade_fonte': 0,
        })

    for indice, item in enumerate(estado.get('recebidos_nao_aportados_disponiveis') or [], start=1):
        bruto = _normalizar_fonte(item, tipo_padrao='lote_nao_aportado')
        disponivel, motivo = _fonte_disponivel_na_data(bruto, data_pagamento)
        if not disponivel:
            continue
        valor_fonte = round(_safe_float(bruto.get('valor') or bruto.get('valor_disponivel')), 2)
        if valor_fonte <= 0.0:
            continue
        proxy_terminal = _normalizar_proxy_terminal(bruto.get('proxy_terminal_atual') or estado.get('proxy_terminal_nao_aportado_padrao'))
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        perda = _perda_terminal_por_fonte(coberto, proxy_terminal, dias_horizonte)
        fonte_id = _safe_str(bruto.get('fonte_id') or bruto.get('id') or f'recebido_{indice}')
        candidatos_combo.append({
            'tipo_fonte': 'lote_nao_aportado',
            'fonte_id': fonte_id,
            'valor_disponivel': valor_fonte,
            'proxy_terminal': proxy_terminal,
            'custo_fiscal_total_estimado': 0.0,
            'penalidade_liquidez_unitaria': 0.0,
            'dias_idade_fonte': _dias_idade_fonte(data_pagamento, _coerce_date(bruto.get('data_recebimento'))),
        })
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_nao_aportado',
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
            justificativa='Recebido/lote não aportado já disponível na data do pagamento.',
            componentes=[{'tipo_fonte': 'lote_nao_aportado', 'fonte_id': fonte_id, 'valor_utilizado': coberto}],
            metadados_extras={'motivo_temporal': motivo, 'proxy_terminal_fonte': proxy_terminal, 'dias_idade_fonte': _dias_idade_fonte(data_pagamento, _coerce_date(bruto.get('data_aplicacao') or bruto.get('data_recebimento')))},
        ))

    for indice, item in enumerate(estado.get('lotes_aportados') or [], start=1):
        bruto = _normalizar_fonte(item, tipo_padrao='lote_aportado')
        disponivel, motivo = _fonte_disponivel_na_data(bruto, data_pagamento)
        if not disponivel:
            continue
        valor_fonte = round(_safe_float(bruto.get('valor_liquido_resgatavel') or bruto.get('principal_remanescente')), 2)
        if valor_fonte <= 0.0:
            continue
        proxy_terminal = _normalizar_proxy_terminal(bruto.get('proxy_terminal_atual'))
        coberto = min(valor, valor_fonte)
        deficit = max(valor - coberto, 0.0)
        custo_fiscal = _estimar_custo_fiscal_lote(bruto, coberto, data_pagamento)
        perda = _perda_terminal_por_fonte(coberto, proxy_terminal, dias_horizonte)
        fonte_id = _safe_str(bruto.get('fonte_id') or bruto.get('id') or f'lote_{indice}')
        justificativa = 'Resgate de lote aportado elegível na data do pagamento, com custo fiscal estimado.'
        candidatos_combo.append({
            'tipo_fonte': 'lote_aportado',
            'fonte_id': fonte_id,
            'valor_disponivel': valor_fonte,
            'proxy_terminal': proxy_terminal,
            'custo_fiscal_total_estimado': _estimar_custo_fiscal_lote(bruto, valor_fonte, data_pagamento),
            'penalidade_liquidez_unitaria': 0.0,
            'dias_idade_fonte': _dias_idade_fonte(data_pagamento, _coerce_date(bruto.get('data_aplicacao') or bruto.get('data_recebimento'))),
        })
        adicionar(FontePagamentoCandidata(
            tipo_fonte='lote_aportado',
            fonte_id=fonte_id,
            valor_coberto=coberto,
            valor_deficit=deficit,
            cobertura_integral=deficit <= 0.0,
            custo_fiscal_imediato=custo_fiscal,
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
                custo_fiscal=custo_fiscal,
                custo_operacional=0.0,
            ),
            justificativa=justificativa,
            componentes=[{'tipo_fonte': 'lote_aportado', 'fonte_id': fonte_id, 'valor_utilizado': coberto}],
            metadados_extras={'motivo_temporal': motivo, 'proxy_terminal_fonte': proxy_terminal, 'dias_idade_fonte': _dias_idade_fonte(data_pagamento, _coerce_date(bruto.get('data_aplicacao') or bruto.get('data_recebimento')))},
        ))

    if permitir_combinacao_minima and valor > 0.0 and candidatos_combo:
        ranking_combo = sorted(
            [x for x in candidatos_combo if _safe_float(x.get('valor_disponivel')) > 0.0],
            key=lambda item: _chave_combo_script1(item, valor_pagamento=valor, dias_horizonte=dias_horizonte, config=config),
        )
        restante = valor
        componentes: list[dict[str, Any]] = []
        perda_total = 0.0
        custo_fiscal_total = 0.0
        penalidade_estrategica_total = 0.0
        penalidade_liquidez_total = 0.0
        for item in ranking_combo:
            if restante <= 0.0:
                break
            valor_disponivel = round(_safe_float(item.get('valor_disponivel')), 2)
            if valor_disponivel <= 0.0:
                continue
            usado = min(restante, valor_disponivel)
            proxy_terminal = _normalizar_proxy_terminal(item.get('proxy_terminal'))
            custo_fiscal_total_item = max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0)
            custo_fiscal_item = round(custo_fiscal_total_item * _proporcao_utilizada(usado, valor_disponivel), 2)
            componentes.append({
                'tipo_fonte': _safe_str(item.get('tipo_fonte')),
                'fonte_id': _safe_str(item.get('fonte_id')),
                'valor_utilizado': round(usado, 2),
            })
            perda_total += _perda_terminal_por_fonte(usado, proxy_terminal, dias_horizonte)
            custo_fiscal_total += custo_fiscal_item
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
            custo_fiscal_imediato=round(custo_fiscal_total, 2),
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
                custo_fiscal=round(custo_fiscal_total, 2),
                custo_operacional=max(len(componentes) - 1, 0),
            ),
            justificativa='Combinação mínima funcional entre fontes elegíveis, ordenada por menor impacto terminal unitário.',
            componentes=componentes,
            metadados_extras={
                'proxy_terminal_fonte': round(perda_total / max(valor_coberto, 1.0) * max(365 / max(dias_horizonte, 1), 1), 6) if valor_coberto > 0 else 0.0,
                'dias_idade_fonte': 0,
                'componentes_combinacao': componentes,
            },
        ))

    if _permitir_cenario_switching:
        for plano in _iterar_planos_switching(plano_switching_candidato):
            if not _plano_switching_promovivel(plano):
                continue
            estado_pos = _estado_pos_switching(plano)
            if not isinstance(estado_pos, dict):
                continue
            estado_pos.setdefault('data_evento_corrente', data_pagamento)
            subresultado = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_pos,
                config=config,
                plano_switching_candidato=None,
                permitir_combinacao_minima=permitir_combinacao_minima,
                limite_fontes_candidatas=limite_fontes_candidatas,
                _permitir_cenario_switching=False,
            )
            custo_fiscal_switch = round(_safe_float(plano.get('custo_fiscal_switching_total') or plano.get('custo_fiscal_realizado') or plano.get('custo_fiscal_estimado')), 2)
            perda_liquidez_switch = round(_safe_float(plano.get('perda_liquidez_switching_total') or plano.get('perda_liquidez_estimada')), 2)
            delta_perda_switch = round(_safe_float(plano.get('delta_perda_terminal_vs_baseline') or plano.get('ganho_terminal_economico_minimo_estimado')), 2)
            perda_terminal_total = round(_safe_float(subresultado.get('perda_retorno_terminal_estimada')) + delta_perda_switch, 2)
            penalidade_liquidez_total = round(_safe_float(subresultado.get('penalidade_liquidez_futura')) + perda_liquidez_switch, 2)
            custo_fiscal_total = round(_safe_float(subresultado.get('custo_fiscal_imediato')) + custo_fiscal_switch, 2)
            valor_deficit = round(_safe_float(subresultado.get('valor_deficit')), 2)
            valor_coberto = round(_safe_float(subresultado.get('valor_coberto')), 2)
            componentes = [{
                'tipo_fonte': 'switching_elegivel_previo',
                'fonte_id': _safe_str(plano.get('id_acao') or plano.get('rotulo') or plano.get('cenario_id') or 'switching_elegivel'),
                'valor_utilizado': 0.0,
                'classe_comparador_hibrido': _safe_str(plano.get('classe_comparador_hibrido')),
            }] + list(subresultado.get('componentes_escolhidos') or [])
            adicionar(FontePagamentoCandidata(
                tipo_fonte='cenario_switching_elegivel',
                fonte_id=_safe_str(plano.get('id_acao') or plano.get('rotulo') or plano.get('cenario_id') or 'switching_elegivel'),
                valor_coberto=valor_coberto,
                valor_deficit=valor_deficit,
                cobertura_integral=bool(subresultado.get('cobertura_integral')),
                custo_fiscal_imediato=custo_fiscal_total,
                perda_retorno_terminal_estimada=perda_terminal_total,
                penalidade_liquidez_futura=penalidade_liquidez_total,
                penalidade_estrategica_lote=round(_safe_float(subresultado.get('penalidade_estrategica_lote')), 2),
                score_terminal_comparativo=_score_placeholder(
                    viola_protegida=1.0 if classe == 'PROTEGIDA' and valor_deficit > 0 else 0.0,
                    deficit=valor_deficit,
                    sem_cobertura=1.0 if valor_deficit > 0 else 0.0,
                    perda_terminal=perda_terminal_total,
                    penalidade_estrategica=round(_safe_float(subresultado.get('penalidade_estrategica_lote')), 2),
                    penalidade_liquidez=penalidade_liquidez_total,
                    custo_fiscal=custo_fiscal_total,
                    custo_operacional=1.0,
                ),
                justificativa='Cenário com switching elegível já filtrado pelo comparador híbrido e comparado no estado pós-switching.',
                componentes=componentes,
                metadados_extras={
                    'classe_comparador_hibrido': _safe_str(plano.get('classe_comparador_hibrido')),
                    'promovivel_hibrido': bool(plano.get('promovivel_hibrido')),
                    'justificativa_plano': _safe_str(plano.get('motivo_comparador_hibrido') or plano.get('justificativa')),
                    'fonte_pos_switching_tipo': subresultado.get('fonte_principal_tipo'),
                    'fonte_pos_switching_id': subresultado.get('fonte_principal_id'),
                    'proxy_terminal_fonte': float((subresultado.get('metadados_escolhidos') or {}).get('proxy_terminal_fonte') or 0.0),
                    'dias_idade_fonte': int((subresultado.get('metadados_escolhidos') or {}).get('dias_idade_fonte') or 0),
                },
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
            metadados_extras={'proxy_terminal_fonte': 0.0, 'dias_idade_fonte': 0},
        ))

    candidatos = [
        _aplicar_heuristicas_script1(item, valor_pagamento=valor, dias_horizonte=dias_horizonte, config=config)
        for item in candidatos
    ]
    melhor = min(candidatos, key=lambda item: item.chave_decisao_final or _montar_chave_decisao_final(item))
    resumo_switching = {
        'planos_recebidos': len(list(_iterar_planos_switching(plano_switching_candidato))),
        'candidatos_switching_elegivel': sum(1 for item in candidatos if item.tipo_fonte == 'cenario_switching_elegivel'),
        'melhor_envolve_switching': melhor.tipo_fonte == 'cenario_switching_elegivel',
    }
    return {
        'status': 'funcional_v141',
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
        'score_auxiliar_script1': melhor.score_auxiliar_script1,
        'chave_decisao_final': melhor.chave_decisao_final,
        'justificativa': melhor.justificativa,
        'componentes_escolhidos': melhor.componentes,
        'metadados_escolhidos': melhor.metadados_extras,
        'resumo_comparacao_switching': resumo_switching,
        'config_resumido': dict(config or {}),
        'parametros_script1_fase1': carregar_parametros_fase1(config),
    }
