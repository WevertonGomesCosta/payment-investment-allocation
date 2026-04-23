from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, escolher_melhor_cenario_promovivel
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import (
    _cap_fontes_por_destino,
    _comparar_com_baseline,
    _gerar_cenarios_integral_parametrizados,
    _melhores_por_fonte_destino,
    _safe_float,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _ativar_recebidos_futuros_no_dia,
    _normalizar_lote_pos_vencimento_no_dia,
    _calcular_metrica,
    _coerce_date,
    _consumir_componentes,
    _patrimonio_terminal_proxy,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)


@dataclass(slots=True)
class PacoteDiaResumoV143:
    data: str
    tipo_pacote: str
    possui_pagamentos_no_dia: bool
    pagamentos_dia: int
    pagamentos_ids: list[str]
    switching_considerado: bool
    switching_executado: bool
    rotulo_switching: str | None
    classe_switching: str | None
    eventos_switching: int
    metrica_dia: dict[str, float]
    metrica_total_estimada: dict[str, float]
    vetor_total_estimado: tuple[float, float, float, float, float, float, float, float]
    patrimonio_terminal_proxy_estimado: float
    resultados_pagamento: list[dict[str, Any]]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DecisaoDiaV143:
    data: str
    tipo_dia: str
    quantidade_pagamentos: int
    pagamentos_ids: list[str]
    descricao_pagamentos: list[str]
    pacote_vencedor: str
    justificativa_vencedor: str
    patrimonio_terminal_proxy_estimado_vencedor: float
    vetor_total_estimado_vencedor: tuple[float, float, float, float, float, float, float, float]
    candidatos: list[dict[str, Any]]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResumoMotorV143:
    data_inicio: str
    data_fim: str
    dias_no_horizonte: int
    dias_com_pagamento: int
    pagamentos_no_horizonte: int
    decisoes_switch_then_pay: int
    decisoes_pay_only: int
    decisoes_switch_only: int
    decisoes_no_action: int
    patrimonio_liquido_terminal_proxy_final: float
    metrica_central_final: dict[str, float]
    contagem_fontes_pagamento: dict[str, int]

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ordenar_pagamentos(pagamentos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [deepcopy(dict(x)) for x in pagamentos],
        key=lambda item: (
            _coerce_date(item.get('data')) or date.max,
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )


def _combinar_metricas(m1: dict[str, Any] | None, m2: dict[str, Any] | None) -> dict[str, float]:
    a = dict(m1 or {})
    b = dict(m2 or {})
    return {
        'violacoes_protegida': round(_safe_float(a.get('violacoes_protegida')) + _safe_float(b.get('violacoes_protegida')), 2),
        'deficit_liquido_total': round(_safe_float(a.get('deficit_liquido_total')) + _safe_float(b.get('deficit_liquido_total')), 2),
        'pagamentos_sem_cobertura_integral': round(_safe_float(a.get('pagamentos_sem_cobertura_integral')) + _safe_float(b.get('pagamentos_sem_cobertura_integral')), 2),
        'perda_patrimonio_liquido_terminal': round(_safe_float(a.get('perda_patrimonio_liquido_terminal')) + _safe_float(b.get('perda_patrimonio_liquido_terminal')), 2),
        'destruicao_estrategica_lotes': round(_safe_float(a.get('destruicao_estrategica_lotes')) + _safe_float(b.get('destruicao_estrategica_lotes')), 2),
        'deterioracao_liquidez_futura': round(_safe_float(a.get('deterioracao_liquidez_futura')) + _safe_float(b.get('deterioracao_liquidez_futura')), 2),
        'custo_fiscal_imediato': round(_safe_float(a.get('custo_fiscal_imediato')) + _safe_float(b.get('custo_fiscal_imediato')), 2),
        'custo_operacional': round(_safe_float(a.get('custo_operacional')) + _safe_float(b.get('custo_operacional')), 2),
    }


def _remover_pagamentos_ate_dia(estado: dict[str, Any], dia: date) -> None:
    estado['pagamentos_futuros'] = [
        deepcopy(dict(item))
        for item in (estado.get('pagamentos_futuros') or [])
        if (_coerce_date(item.get('data')) or date.max) > dia
    ]


def _avaliar_continuacao_neutra(
    *,
    estado_pos_dia: dict[str, Any],
    dia_atual: date,
    data_fim: date,
    config: dict[str, Any],
) -> tuple[dict[str, float], float]:
    if dia_atual >= data_fim:
        metrica = {
            'violacoes_protegida': 0.0,
            'deficit_liquido_total': 0.0,
            'pagamentos_sem_cobertura_integral': 0.0,
            'perda_patrimonio_liquido_terminal': 0.0,
            'destruicao_estrategica_lotes': 0.0,
            'deterioracao_liquidez_futura': 0.0,
            'custo_fiscal_imediato': 0.0,
            'custo_operacional': 0.0,
        }
        patrimonio = _patrimonio_terminal_proxy(estado_pos_dia, metrica, 0.0)
        return metrica, round(patrimonio, 2)

    estado_futuro = deepcopy(estado_pos_dia)
    _remover_pagamentos_ate_dia(estado_futuro, dia_atual)
    proximo_dia = dia_atual + timedelta(days=1)
    if not (estado_futuro.get('pagamentos_futuros') or []):
        estado_futuro['data_evento_corrente'] = dia_atual
        metrica = {
            'violacoes_protegida': 0.0,
            'deficit_liquido_total': 0.0,
            'pagamentos_sem_cobertura_integral': 0.0,
            'perda_patrimonio_liquido_terminal': 0.0,
            'destruicao_estrategica_lotes': 0.0,
            'deterioracao_liquidez_futura': 0.0,
            'custo_fiscal_imediato': 0.0,
            'custo_operacional': 0.0,
        }
        patrimonio = _patrimonio_terminal_proxy(estado_futuro, metrica, 0.0)
        return metrica, round(patrimonio, 2)

    horizonte = {'data_inicio': proximo_dia.isoformat(), 'data_fim': data_fim.isoformat()}
    sim = simular_cenario_eventos_v1(deepcopy(estado_futuro), [], config, horizonte=horizonte)
    return dict(sim.get('metrica_central') or {}), round(_safe_float(sim.get('patrimonio_liquido_terminal_proxy')), 2)


def _melhor_plano_switching_diario_v143(
    *,
    estado: dict[str, Any],
    config: dict[str, Any],
    data_atual: date,
    data_fim: date,
    limite_candidatos_por_data: int = 24,
    cap_fontes_destino: int = 5,
) -> dict[str, Any] | None:
    estado_local = deepcopy(estado)
    estado_local['data_evento_corrente'] = data_atual
    _normalizar_lote_pos_vencimento_no_dia(estado_local, data_atual, config, None)
    horizonte = {'data_inicio': data_atual.isoformat(), 'data_fim': data_fim.isoformat()}
    baseline = simular_cenario_eventos_v1(deepcopy(estado_local), [], config, horizonte=horizonte)
    plano = planejar_switching_temporal_v1(
        estado_global=estado_local,
        config=config,
        horizonte_planejamento=horizonte,
        filtros_eventos=None,
        limite_candidatos_por_data=limite_candidatos_por_data,
    )
    acoes = [
        deepcopy(item)
        for item in (plano.get('acoes_candidatas') or [])
        if str(item.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'} and item.get('elegivel')
    ]
    acoes = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), cap_fontes_destino)
    cenarios = _gerar_cenarios_integral_parametrizados(acoes)
    resultados: list[dict[str, Any]] = []
    for cenario in cenarios:
        sim = simular_cenario_eventos_v1(deepcopy(estado_local), cenario.get('eventos') or [], config, horizonte=horizonte)
        comparacao = _comparar_com_baseline(sim, baseline)
        classif = classificar_cenario_diario(comparacao)
        estado_pos = deepcopy(estado_local)
        _aplicar_switching_eventos(estado_pos, cenario.get('eventos') or [], data_atual, [])
        resultados.append({
            **cenario,
            **comparacao,
            **classif,
            'estado_pos_switching': estado_pos,
            'custo_fiscal_switching_total': sim.get('custo_fiscal_switching_total'),
            'perda_liquidez_switching_total': sim.get('perda_liquidez_switching_total'),
            'patrimonio_liquido_terminal_proxy': sim.get('patrimonio_liquido_terminal_proxy'),
            'metrica_central': sim.get('metrica_central'),
        })
    return escolher_melhor_cenario_promovivel(resultados)


def _executar_pacote_dia(
    *,
    estado_inicial: dict[str, Any],
    dia: date,
    pagamentos_dia: list[dict[str, Any]],
    config: dict[str, Any],
    data_fim: date,
    tipo_pacote: str,
    plano_switching: dict[str, Any] | None,
) -> dict[str, Any]:
    estado = deepcopy(estado_inicial)
    historico_local: list[dict[str, Any]] = []
    _normalizar_lote_pos_vencimento_no_dia(estado, dia, config, historico_local)
    eventos_executados: list[dict[str, Any]] = []
    ganho_switching = 0.0
    perda_liquidez_switching = 0.0
    custo_fiscal_switching = 0.0
    rotulo_switching = None
    classe_switching = None
    switching_executado = False

    if tipo_pacote in {'switch_only', 'switch_then_pay'} and plano_switching is not None:
        eventos = [deepcopy(dict(x)) for x in (plano_switching.get('eventos') or [])]
        novos_eventos, ganho_switching, perda_liquidez_switching, custo_fiscal_switching = _aplicar_switching_eventos(estado, eventos, dia, historico_local)
        eventos_executados.extend(novos_eventos)
        switching_executado = len(novos_eventos) > 0
        rotulo_switching = str(plano_switching.get('rotulo') or '') or None
        classe_switching = str(plano_switching.get('classe_comparador_hibrido') or '') or None

    resultados_pagamento: list[dict[str, Any]] = []
    pagamentos_ids = [str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia]
    if tipo_pacote in {'pay_only', 'switch_then_pay'}:
        for pagamento in _ordenar_pagamentos(pagamentos_dia):
            estado_para_pagamento = deepcopy(estado)
            estado_para_pagamento['dias_horizonte_terminal'] = max(((_coerce_date(estado.get('data_fim_recorte')) or dia) - dia).days, 0)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_pagamento,
                config=config,
                plano_switching_candidato=None,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            resultados_pagamento.append(alocacao)
            _consumir_componentes(estado, alocacao.get('componentes_escolhidos') or [])

    metrica_dia = _calcular_metrica(
        resultados_pagamento,
        ganho_switching=ganho_switching,
        perda_liquidez_switching=perda_liquidez_switching,
        custo_fiscal_switching=custo_fiscal_switching,
        eventos_executados=eventos_executados,
    )
    estado['data_evento_corrente'] = dia
    _remover_pagamentos_ate_dia(estado, dia)
    metrica_futura, patrimonio_futuro = _avaliar_continuacao_neutra(
        estado_pos_dia=estado,
        dia_atual=dia,
        data_fim=data_fim,
        config=config,
    )
    metrica_total = _combinar_metricas(metrica_dia, metrica_futura)
    patrimonio_total = round(patrimonio_futuro - _safe_float(metrica_dia.get('perda_patrimonio_liquido_terminal')), 2)
    return {
        'tipo_pacote': tipo_pacote,
        'estado_pos_dia': estado,
        'eventos_switching': eventos_executados,
        'switching_executado': switching_executado,
        'rotulo_switching': rotulo_switching,
        'classe_switching': classe_switching,
        'resultados_pagamento': resultados_pagamento,
        'metrica_dia': metrica_dia,
        'metrica_total_estimada': metrica_total,
        'vetor_total_estimado': vetor_lexicografico_central(metrica_total),
        'patrimonio_terminal_proxy_estimado': patrimonio_total,
        'pagamentos_ids': pagamentos_ids,
    }


def _chave_pacote(resultado: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(resultado.get('vetor_total_estimado') or ()) + (-_safe_float(resultado.get('patrimonio_terminal_proxy_estimado')),)


def _carregar_estado_janela(
    *,
    contexto: Any,
    data_inicio: date,
    data_fim: date,
    limite_pagamentos: int = 200,
) -> dict[str, Any]:
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    pagamentos = [
        deepcopy(dict(x))
        for x in (estado.get('pagamentos_futuros') or [])
        if data_inicio <= (_coerce_date(x.get('data')) or date.max) <= data_fim
    ]
    recebidos_futuros = [
        deepcopy(dict(x))
        for x in (estado.get('recebidos_nao_aportados_futuros') or [])
        if data_inicio <= (_coerce_date(x.get('data_recebimento')) or date.max) <= data_fim
    ]
    estado['pagamentos_futuros'] = _ordenar_pagamentos(pagamentos)
    estado['recebidos_nao_aportados_futuros'] = recebidos_futuros
    estado['data_referencia'] = data_inicio
    estado['data_evento_corrente'] = data_inicio
    estado['data_fim_recorte'] = data_fim
    return estado


def rodar_motor_diario_conjunto_experimental_v143(
    *,
    raiz_repositorio: Path,
    data_inicio: date,
    data_fim: date,
    limite_candidatos_por_data: int = 24,
    cap_fontes_destino: int = 5,
) -> dict[str, Any]:
    base = Path(raiz_repositorio)
    contexto = carregar_contexto_baseline(
        raiz_repositorio=base,
        instalar_automaticamente=False,
        incluir_switching_shadow=False,
        incluir_triagem=True,
        incluir_replay=True,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    config = deepcopy(contexto.pacote_config.conteudo)
    estado_corrente = _carregar_estado_janela(contexto=contexto, data_inicio=data_inicio, data_fim=data_fim)
    pagamentos_iniciais = list(estado_corrente.get('pagamentos_futuros') or [])
    pagamentos_por_dia: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pagamento in pagamentos_iniciais:
        pagamentos_por_dia[(_coerce_date(pagamento.get('data')) or data_inicio).isoformat()].append(deepcopy(dict(pagamento)))

    decisoes: list[dict[str, Any]] = []
    historico_execucao: list[dict[str, Any]] = []
    contagem_fontes: dict[str, int] = defaultdict(int)
    resultados_pagamento_executados: list[dict[str, Any]] = []

    dia = data_inicio
    while dia <= data_fim:
        estado_corrente['data_evento_corrente'] = dia
        _normalizar_lote_pos_vencimento_no_dia(estado_corrente, dia, config, historico_execucao)
        _ativar_recebidos_futuros_no_dia(estado_corrente, dia, historico_execucao)
        pagamentos_dia = _ordenar_pagamentos(pagamentos_por_dia.get(dia.isoformat(), []))
        plano_switching = _melhor_plano_switching_diario_v143(
            estado=estado_corrente,
            config=config,
            data_atual=dia,
            data_fim=data_fim,
            limite_candidatos_por_data=limite_candidatos_por_data,
            cap_fontes_destino=cap_fontes_destino,
        )

        candidatos: list[dict[str, Any]] = []
        if pagamentos_dia:
            candidatos.append(_executar_pacote_dia(
                estado_inicial=estado_corrente,
                dia=dia,
                pagamentos_dia=pagamentos_dia,
                config=config,
                data_fim=data_fim,
                tipo_pacote='pay_only',
                plano_switching=None,
            ))
            if plano_switching is not None:
                candidatos.append(_executar_pacote_dia(
                    estado_inicial=estado_corrente,
                    dia=dia,
                    pagamentos_dia=pagamentos_dia,
                    config=config,
                    data_fim=data_fim,
                    tipo_pacote='switch_then_pay',
                    plano_switching=plano_switching,
                ))
            tipo_dia = 'dia_com_pagamento'
        else:
            candidatos.append(_executar_pacote_dia(
                estado_inicial=estado_corrente,
                dia=dia,
                pagamentos_dia=[],
                config=config,
                data_fim=data_fim,
                tipo_pacote='no_action',
                plano_switching=None,
            ))
            if plano_switching is not None:
                candidatos.append(_executar_pacote_dia(
                    estado_inicial=estado_corrente,
                    dia=dia,
                    pagamentos_dia=[],
                    config=config,
                    data_fim=data_fim,
                    tipo_pacote='switch_only',
                    plano_switching=plano_switching,
                ))
            tipo_dia = 'dia_sem_pagamento'

        vencedor = min(candidatos, key=_chave_pacote)
        estado_corrente = deepcopy(vencedor.get('estado_pos_dia') or estado_corrente)
        _remover_pagamentos_ate_dia(estado_corrente, dia)
        for pagamento in vencedor.get('resultados_pagamento') or []:
            resultados_pagamento_executados.append(deepcopy(pagamento))
            contagem_fontes[str(pagamento.get('fonte_principal_tipo') or 'sem_fonte')] += 1

        justificativa = (
            f"Vencedor por vetor total estimado {tuple(vencedor.get('vetor_total_estimado') or ())} "
            f"e patrimônio terminal proxy estimado R$ {float(vencedor.get('patrimonio_terminal_proxy_estimado') or 0.0):.2f}."
        )
        decisoes.append(DecisaoDiaV143(
            data=dia.isoformat(),
            tipo_dia=tipo_dia,
            quantidade_pagamentos=len(pagamentos_dia),
            pagamentos_ids=[str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia],
            descricao_pagamentos=[str(x.get('descricao') or '') for x in pagamentos_dia],
            pacote_vencedor=str(vencedor.get('tipo_pacote') or ''),
            justificativa_vencedor=justificativa,
            patrimonio_terminal_proxy_estimado_vencedor=round(_safe_float(vencedor.get('patrimonio_terminal_proxy_estimado')), 2),
            vetor_total_estimado_vencedor=tuple(vencedor.get('vetor_total_estimado') or ()),
            candidatos=[PacoteDiaResumoV143(
                data=dia.isoformat(),
                tipo_pacote=str(c.get('tipo_pacote') or ''),
                possui_pagamentos_no_dia=bool(pagamentos_dia),
                pagamentos_dia=len(pagamentos_dia),
                pagamentos_ids=[str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia],
                switching_considerado=bool(c.get('tipo_pacote') in {'switch_only', 'switch_then_pay'}),
                switching_executado=bool(c.get('switching_executado')),
                rotulo_switching=c.get('rotulo_switching'),
                classe_switching=c.get('classe_switching'),
                eventos_switching=len(c.get('eventos_switching') or []),
                metrica_dia=dict(c.get('metrica_dia') or {}),
                metrica_total_estimada=dict(c.get('metrica_total_estimada') or {}),
                vetor_total_estimado=tuple(c.get('vetor_total_estimado') or ()),
                patrimonio_terminal_proxy_estimado=round(_safe_float(c.get('patrimonio_terminal_proxy_estimado')), 2),
                resultados_pagamento=[deepcopy(dict(x)) for x in (c.get('resultados_pagamento') or [])],
            ).para_dict() for c in candidatos],
        ).para_dict())
        historico_execucao.append({
            'data': dia.isoformat(),
            'tipo_dia': tipo_dia,
            'pacote_vencedor': vencedor.get('tipo_pacote'),
            'switching_executado': bool(vencedor.get('switching_executado')),
            'rotulo_switching': vencedor.get('rotulo_switching'),
            'pagamentos_ids': [str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia],
        })
        dia += timedelta(days=1)

    estado_corrente['data_evento_corrente'] = data_fim
    metrica_final = _calcular_metrica(
        resultados_pagamento_executados,
        ganho_switching=0.0,
        perda_liquidez_switching=0.0,
        custo_fiscal_switching=0.0,
        eventos_executados=[],
    )
    patrimonio_final = _patrimonio_terminal_proxy(estado_corrente, metrica_final, 0.0)
    resumo = ResumoMotorV143(
        data_inicio=data_inicio.isoformat(),
        data_fim=data_fim.isoformat(),
        dias_no_horizonte=(data_fim - data_inicio).days + 1,
        dias_com_pagamento=sum(1 for item in decisoes if item.get('quantidade_pagamentos')),
        pagamentos_no_horizonte=len(pagamentos_iniciais),
        decisoes_switch_then_pay=sum(1 for item in decisoes if item.get('pacote_vencedor') == 'switch_then_pay'),
        decisoes_pay_only=sum(1 for item in decisoes if item.get('pacote_vencedor') == 'pay_only'),
        decisoes_switch_only=sum(1 for item in decisoes if item.get('pacote_vencedor') == 'switch_only'),
        decisoes_no_action=sum(1 for item in decisoes if item.get('pacote_vencedor') == 'no_action'),
        patrimonio_liquido_terminal_proxy_final=round(patrimonio_final, 2),
        metrica_central_final=metrica_final,
        contagem_fontes_pagamento=dict(sorted(contagem_fontes.items())),
    ).para_dict()
    return {
        'status': 'ok',
        'versao': 'V146',
        'janela': {'data_inicio': data_inicio.isoformat(), 'data_fim': data_fim.isoformat()},
        'limites_busca_switching': {
            'limite_candidatos_por_data': int(limite_candidatos_por_data),
            'cap_fontes_destino': int(cap_fontes_destino),
        },
        'resumo': resumo,
        'decisoes_diarias': decisoes,
        'historico_execucao': historico_execucao,
        'estado_final_estimado': deepcopy(estado_corrente),
        'resultados_pagamento_executados': resultados_pagamento_executados,
        'observacao_metodologica': (
            'Motor diário conjunto experimental: a escolha do pacote do dia usa continuação neutra até o fim da janela '\
            'sem novo switching proativo após o dia avaliado. A comparação é útil para auditar precedência diária, '\
            'mas não substitui ainda um resolvedor global exato de múltiplos dias.'
        ),
    }
