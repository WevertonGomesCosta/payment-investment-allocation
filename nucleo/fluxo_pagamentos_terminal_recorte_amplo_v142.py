from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, escolher_melhor_cenario_promovivel
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_v138 import _cap_fontes_por_destino, _gerar_cenarios_integral_parametrizados, _melhores_por_fonte_destino
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _ativar_recebidos_futuros_no_dia,
    _calcular_metrica,
    _coerce_date,
    _consumir_componentes,
    _patrimonio_terminal_proxy,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)


TIPOS_PRIORITARIOS = (
    'lote_aportado',
    'lote_nao_aportado',
    'combinacao_minima_fontes',
    'cenario_switching_elegivel',
)


from nucleo.utilitarios_neutros import _safe_float
@dataclass(slots=True)
class ResultadoPagamentoFluxoV142:
    data_pagamento: str
    pagamento_id: str
    descricao: str
    classe_pagamento: str
    valor_pagamento: float
    fonte_principal_tipo: str
    fonte_principal_id: str | None
    melhor_acao_pagamento: str
    cobertura_integral: bool
    valor_coberto: float
    valor_deficit: float
    custo_fiscal_imediato: float
    perda_retorno_terminal_estimada: float
    penalidade_liquidez_futura: float
    penalidade_estrategica_lote: float
    classe_cenario_switching: str | None
    rotulo_cenario_switching: str | None
    promovivel_switching: bool
    switching_aplicado_no_fluxo: bool
    score_auxiliar_script1: tuple[float, float, float] | list[float]
    mudou_decisao_local_h1h3: bool = False
    fonte_local_sem_h1h3_tipo: str | None = None
    fonte_local_sem_h1h3_id: str | None = None
    melhor_acao_local_sem_h1h3: str | None = None
    delta_perda_terminal_local_h1h3: float = 0.0
    delta_custo_fiscal_local_h1h3: float = 0.0
    delta_penalidade_liquidez_local_h1h3: float = 0.0
    transicao_local_h1h3: str | None = None

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResumoFluxoV142:
    data_inicio: str
    data_fim: str
    quantidade_pagamentos: int
    quantidade_dias_com_pagamento: int
    contagem_fontes: dict[str, int]
    pagamentos_com_switching_elegivel_promovivel: int
    pagamentos_que_escolheram_switching: int
    pagamentos_cobertos_integralmente: int
    deficit_total: float
    patrimonio_liquido_terminal_proxy: float
    perda_patrimonio_liquido_terminal: float
    custo_fiscal_imediato_total: float
    custo_operacional_total: float

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)



def _config_sem_h1h3(config: dict[str, Any]) -> dict[str, Any]:
    novo = deepcopy(dict(config or {}))
    novo['desabilitar_modelos_script1_fase1'] = True
    return novo



def _carregar_estado_recorte_amplo(contexto: Any, *, data_inicio: date | None = None, data_fim: date | None = None, limite_pagamentos: int = 45) -> tuple[dict[str, Any], date, int]:
    data_inicio = data_inicio or contexto.execucao.data_referencia
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=data_inicio)
    if limite_pagamentos > 0:
        pagamentos = pagamentos.head(limite_pagamentos).copy()
    data_fim = data_fim or (max(pagamentos['data']) if len(pagamentos) else data_inicio)
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=max(limite_pagamentos, 1),
    )
    return estado, data_fim, len(estado.get('pagamentos_futuros') or [])



def _comparar_com_baseline(sim: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    metrica = sim.get('metrica_central') or {}
    base = baseline.get('metrica_central') or {}
    vetor = vetor_lexicografico_central(metrica)
    vetor_base = vetor_lexicografico_central(base)
    return {
        'vetor_lexicografico': vetor,
        'vetor_baseline': vetor_base,
        'continua_vencedor_central': vetor < vetor_base,
        'delta_perda_terminal_vs_baseline': round(_safe_float(metrica.get('perda_patrimonio_liquido_terminal')) - _safe_float(base.get('perda_patrimonio_liquido_terminal')), 2),
        'delta_deficit_vs_baseline': round(_safe_float(metrica.get('deficit_liquido_total')) - _safe_float(base.get('deficit_liquido_total')), 2),
        'delta_violacoes_protegida_vs_baseline': round(_safe_float(metrica.get('violacoes_protegida')) - _safe_float(base.get('violacoes_protegida')), 2),
        'delta_patrimonio_proxy_vs_baseline': round(_safe_float(sim.get('patrimonio_liquido_terminal_proxy')) - _safe_float(baseline.get('patrimonio_liquido_terminal_proxy')), 2),
    }



def _melhor_plano_switching_promovivel_para_estado(estado: dict[str, Any], config: dict[str, Any], *, data_atual: date, data_fim: date) -> dict[str, Any] | None:
    estado_local = deepcopy(estado)
    estado_local['data_evento_corrente'] = data_atual
    horizonte = {'data_inicio': data_atual.isoformat(), 'data_fim': data_fim.isoformat()}
    baseline = simular_cenario_eventos_v1(deepcopy(estado_local), [], config, horizonte=horizonte)
    plano = planejar_switching_temporal_v1(
        estado_global=estado_local,
        config=config,
        horizonte_planejamento=horizonte,
        filtros_eventos=None,
        limite_candidatos_por_data=8,
    )
    acoes = [
        deepcopy(item)
        for item in (plano.get('acoes_candidatas') or [])
        if str(item.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'} and item.get('elegivel')
    ]
    acoes = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), 3)
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



def _transicao_tipo(origem: str | None, destino: str | None) -> str:
    return f"{origem or 'NA'} -> {destino or 'NA'}"



def _rodar_fluxo(
    *,
    raiz_repositorio: Path,
    limite_pagamentos: int,
    config_override: dict[str, Any] | None = None,
    comparar_local_h1h3: bool = False,
) -> dict[str, Any]:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=raiz_repositorio,
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
    config = deepcopy(config_override if config_override is not None else contexto.pacote_config.conteudo)
    estado, data_fim_recorte, quantidade_pagamentos = _carregar_estado_recorte_amplo(
        contexto,
        data_inicio=contexto.execucao.data_referencia,
        data_fim=None,
        limite_pagamentos=limite_pagamentos,
    )
    data_inicio = _coerce_date(estado.get('data_referencia')) or contexto.execucao.data_referencia
    pagamentos = sorted(
        [deepcopy(dict(item)) for item in estado.get('pagamentos_futuros', [])],
        key=lambda item: (
            _coerce_date(item.get('data')) or date.max,
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )
    pagamentos_por_dia: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pagamento in pagamentos:
        pagamentos_por_dia[(_coerce_date(pagamento.get('data')) or data_inicio).isoformat()].append(pagamento)

    estado_corrente = deepcopy(estado)
    historico_fluxo: list[dict[str, Any]] = []
    resultados_pagamento: list[dict[str, Any]] = []
    contagem_fontes: Counter[str] = Counter()
    pagamentos_com_switching_promovivel = 0
    pagamentos_que_escolheram_switching = 0
    eventos_switching_aplicados: list[dict[str, Any]] = []
    comparacoes_locais: list[dict[str, Any]] = []

    config_sem_h1h3 = _config_sem_h1h3(config)

    dia = data_inicio
    while dia <= data_fim_recorte:
        estado_corrente['data_evento_corrente'] = dia
        _ativar_recebidos_futuros_no_dia(estado_corrente, dia, historico_fluxo)
        pagamentos_dia = pagamentos_por_dia.get(dia.isoformat(), [])
        for pagamento in pagamentos_dia:
            plano_switching = _melhor_plano_switching_promovivel_para_estado(
                estado_corrente,
                config,
                data_atual=dia,
                data_fim=data_fim_recorte,
            )
            if plano_switching is not None:
                pagamentos_com_switching_promovivel += 1

            estado_para_alocar = deepcopy(estado_corrente)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_alocar,
                config=config,
                plano_switching_candidato=plano_switching,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )

            comparacao_local = {}
            if comparar_local_h1h3:
                alocacao_sem_h1h3 = alocar_pagamento_terminal_v1(
                    pagamento=pagamento,
                    estado_global=deepcopy(estado_corrente),
                    config=config_sem_h1h3,
                    plano_switching_candidato=plano_switching,
                    permitir_combinacao_minima=True,
                    limite_fontes_candidatas=None,
                )
                comparacao_local = {
                    'mudou_decisao_local_h1h3': (
                        str(alocacao.get('fonte_principal_tipo') or '') != str(alocacao_sem_h1h3.get('fonte_principal_tipo') or '')
                        or str(alocacao.get('fonte_principal_id') or '') != str(alocacao_sem_h1h3.get('fonte_principal_id') or '')
                    ),
                    'fonte_local_sem_h1h3_tipo': alocacao_sem_h1h3.get('fonte_principal_tipo'),
                    'fonte_local_sem_h1h3_id': alocacao_sem_h1h3.get('fonte_principal_id'),
                    'melhor_acao_local_sem_h1h3': alocacao_sem_h1h3.get('melhor_acao_pagamento'),
                    'delta_perda_terminal_local_h1h3': round(_safe_float(alocacao.get('perda_retorno_terminal_estimada')) - _safe_float(alocacao_sem_h1h3.get('perda_retorno_terminal_estimada')), 2),
                    'delta_custo_fiscal_local_h1h3': round(_safe_float(alocacao.get('custo_fiscal_imediato')) - _safe_float(alocacao_sem_h1h3.get('custo_fiscal_imediato')), 2),
                    'delta_penalidade_liquidez_local_h1h3': round(_safe_float(alocacao.get('penalidade_liquidez_futura')) - _safe_float(alocacao_sem_h1h3.get('penalidade_liquidez_futura')), 2),
                    'transicao_local_h1h3': _transicao_tipo(alocacao_sem_h1h3.get('fonte_principal_tipo'), alocacao.get('fonte_principal_tipo')),
                }
                comparacoes_locais.append({
                    'data_pagamento': dia.isoformat(),
                    'pagamento_id': str(alocacao.get('pagamento_id') or pagamento.get('pagamento_id') or ''),
                    'descricao': str(pagamento.get('descricao') or ''),
                    **comparacao_local,
                })

            tipo_fonte = str(alocacao.get('fonte_principal_tipo') or 'sem_fonte_viavel')
            classe_sw = None if plano_switching is None else str(plano_switching.get('classe_comparador_hibrido') or '')
            rotulo_sw = None if plano_switching is None else str(plano_switching.get('rotulo') or '')
            switching_aplicado = False
            if tipo_fonte == 'cenario_switching_elegivel' and plano_switching is not None:
                eventos = [deepcopy(dict(x)) for x in (plano_switching.get('eventos') or [])]
                _aplicar_switching_eventos(estado_corrente, eventos, dia, historico_fluxo)
                eventos_switching_aplicados.extend(eventos)
                switching_aplicado = True
                pagamentos_que_escolheram_switching += 1

            _consumir_componentes(estado_corrente, alocacao.get('componentes_escolhidos') or [])
            contagem_fontes[tipo_fonte] += 1
            resultados_pagamento.append(ResultadoPagamentoFluxoV142(
                data_pagamento=dia.isoformat(),
                pagamento_id=str(alocacao.get('pagamento_id') or pagamento.get('pagamento_id') or ''),
                descricao=str(alocacao.get('descricao_pagamento') or pagamento.get('descricao') or ''),
                classe_pagamento=str(alocacao.get('classe_pagamento') or pagamento.get('classe_pagamento') or ''),
                valor_pagamento=round(_safe_float(alocacao.get('valor_pagamento') or pagamento.get('valor')), 2),
                fonte_principal_tipo=tipo_fonte,
                fonte_principal_id=(None if alocacao.get('fonte_principal_id') in (None, '') else str(alocacao.get('fonte_principal_id'))),
                melhor_acao_pagamento=str(alocacao.get('melhor_acao_pagamento') or ''),
                cobertura_integral=bool(alocacao.get('cobertura_integral')),
                valor_coberto=round(_safe_float(alocacao.get('valor_coberto')), 2),
                valor_deficit=round(_safe_float(alocacao.get('valor_deficit')), 2),
                custo_fiscal_imediato=round(_safe_float(alocacao.get('custo_fiscal_imediato')), 2),
                perda_retorno_terminal_estimada=round(_safe_float(alocacao.get('perda_retorno_terminal_estimada')), 2),
                penalidade_liquidez_futura=round(_safe_float(alocacao.get('penalidade_liquidez_futura')), 2),
                penalidade_estrategica_lote=round(_safe_float(alocacao.get('penalidade_estrategica_lote')), 2),
                classe_cenario_switching=classe_sw,
                rotulo_cenario_switching=rotulo_sw,
                promovivel_switching=bool(plano_switching is not None and plano_switching.get('promovivel_hibrido')),
                switching_aplicado_no_fluxo=switching_aplicado,
                score_auxiliar_script1=alocacao.get('score_auxiliar_script1') or (0.0, 0.0, 0.0),
                mudou_decisao_local_h1h3=bool(comparacao_local.get('mudou_decisao_local_h1h3', False)),
                fonte_local_sem_h1h3_tipo=comparacao_local.get('fonte_local_sem_h1h3_tipo'),
                fonte_local_sem_h1h3_id=comparacao_local.get('fonte_local_sem_h1h3_id'),
                melhor_acao_local_sem_h1h3=comparacao_local.get('melhor_acao_local_sem_h1h3'),
                delta_perda_terminal_local_h1h3=_safe_float(comparacao_local.get('delta_perda_terminal_local_h1h3')),
                delta_custo_fiscal_local_h1h3=_safe_float(comparacao_local.get('delta_custo_fiscal_local_h1h3')),
                delta_penalidade_liquidez_local_h1h3=_safe_float(comparacao_local.get('delta_penalidade_liquidez_local_h1h3')),
                transicao_local_h1h3=comparacao_local.get('transicao_local_h1h3'),
            ).para_dict())
            historico_fluxo.append({
                'tipo_evento': 'pagamento_terminal_recorte_amplo_v142',
                'data_evento': dia.isoformat(),
                'pagamento_id': pagamento.get('pagamento_id'),
                'fonte_principal_tipo': tipo_fonte,
                'fonte_principal_id': alocacao.get('fonte_principal_id'),
                'switching_aplicado': switching_aplicado,
                'rotulo_cenario_switching': rotulo_sw,
            })
        dia += timedelta(days=1)

    estado_corrente['data_evento_corrente'] = data_fim_recorte
    metrica = _calcular_metrica(
        [deepcopy(item) for item in resultados_pagamento],
        ganho_switching=0.0,
        perda_liquidez_switching=0.0,
        custo_fiscal_switching=0.0,
        eventos_executados=eventos_switching_aplicados,
    )
    patrimonio = _patrimonio_terminal_proxy(estado_corrente, metrica, 0.0)
    resumo = ResumoFluxoV142(
        data_inicio=data_inicio.isoformat(),
        data_fim=data_fim_recorte.isoformat(),
        quantidade_pagamentos=quantidade_pagamentos,
        quantidade_dias_com_pagamento=len({str(item['data_pagamento']) for item in resultados_pagamento}),
        contagem_fontes=dict(sorted(contagem_fontes.items())),
        pagamentos_com_switching_elegivel_promovivel=pagamentos_com_switching_promovivel,
        pagamentos_que_escolheram_switching=pagamentos_que_escolheram_switching,
        pagamentos_cobertos_integralmente=sum(1 for item in resultados_pagamento if item.get('cobertura_integral')),
        deficit_total=round(sum(_safe_float(item.get('valor_deficit')) for item in resultados_pagamento), 2),
        patrimonio_liquido_terminal_proxy=round(patrimonio, 2),
        perda_patrimonio_liquido_terminal=round(_safe_float(metrica.get('perda_patrimonio_liquido_terminal')), 2),
        custo_fiscal_imediato_total=round(_safe_float(metrica.get('custo_fiscal_imediato')), 2),
        custo_operacional_total=round(_safe_float(metrica.get('custo_operacional')), 2),
    ).para_dict()

    return {
        'status': 'ok',
        'versao': 'V142',
        'resumo': resumo,
        'resultados_pagamento': resultados_pagamento,
        'historico_fluxo': historico_fluxo,
        'comparacoes_locais_h1h3': comparacoes_locais,
        'metrica_central': metrica,
        'estado_final_estimado': deepcopy(estado_corrente),
        'metadados_recorte': deepcopy(estado.get('metadados_recorte') or {}),
    }



def _resumir_comparacoes_locais(resultados_fase1_ativa: list[dict[str, Any]]) -> dict[str, Any]:
    alterados = [item for item in resultados_fase1_ativa if item.get('mudou_decisao_local_h1h3')]
    transicoes = Counter(item.get('transicao_local_h1h3') or 'NA -> NA' for item in alterados)
    foco_transicoes = {
        k: v for k, v in transicoes.items()
        if any(tipo in k for tipo in TIPOS_PRIORITARIOS)
    }
    return {
        'pagamentos_com_mudanca_local_h1h3': len(alterados),
        'transicoes_locais_h1h3': dict(sorted(transicoes.items())),
        'transicoes_locais_h1h3_foco': dict(sorted(foco_transicoes.items())),
        'top_casos_alterados': alterados[:15],
    }



def _comparar_fluxos(resultados_ativos: list[dict[str, Any]], resultados_neutros: list[dict[str, Any]], resumo_ativo: dict[str, Any], resumo_neutro: dict[str, Any], metrica_ativa: dict[str, Any], metrica_neutra: dict[str, Any]) -> dict[str, Any]:
    neutro_por_pagamento = {str(item.get('pagamento_id') or ''): item for item in resultados_neutros}
    alterados = []
    transicoes = Counter()
    for ativo in resultados_ativos:
        pgto = str(ativo.get('pagamento_id') or '')
        neutro = neutro_por_pagamento.get(pgto)
        if not neutro:
            continue
        mudou = (
            str(ativo.get('fonte_principal_tipo') or '') != str(neutro.get('fonte_principal_tipo') or '')
            or str(ativo.get('fonte_principal_id') or '') != str(neutro.get('fonte_principal_id') or '')
        )
        if not mudou:
            continue
        trans = _transicao_tipo(neutro.get('fonte_principal_tipo'), ativo.get('fonte_principal_tipo'))
        transicoes[trans] += 1
        alterados.append({
            'data_pagamento': ativo.get('data_pagamento'),
            'pagamento_id': pgto,
            'descricao': ativo.get('descricao'),
            'classe_pagamento': ativo.get('classe_pagamento'),
            'valor_pagamento': ativo.get('valor_pagamento'),
            'fonte_sem_h1h3_tipo': neutro.get('fonte_principal_tipo'),
            'fonte_sem_h1h3_id': neutro.get('fonte_principal_id'),
            'fonte_com_h1h3_tipo': ativo.get('fonte_principal_tipo'),
            'fonte_com_h1h3_id': ativo.get('fonte_principal_id'),
            'transicao_fluxo_h1h3': trans,
        })

    return {
        'pagamentos_com_tipo_ou_fonte_alterados_no_fluxo': len(alterados),
        'transicoes_fluxo_h1h3': dict(sorted(transicoes.items())),
        'delta_patrimonio_liquido_terminal_proxy': round(_safe_float(resumo_ativo.get('patrimonio_liquido_terminal_proxy')) - _safe_float(resumo_neutro.get('patrimonio_liquido_terminal_proxy')), 2),
        'delta_perda_patrimonio_liquido_terminal': round(_safe_float(metrica_ativa.get('perda_patrimonio_liquido_terminal')) - _safe_float(metrica_neutra.get('perda_patrimonio_liquido_terminal')), 2),
        'delta_custo_fiscal_imediato_total': round(_safe_float(metrica_ativa.get('custo_fiscal_imediato')) - _safe_float(metrica_neutra.get('custo_fiscal_imediato')), 2),
        'delta_custo_operacional_total': round(_safe_float(metrica_ativa.get('custo_operacional')) - _safe_float(metrica_neutra.get('custo_operacional')), 2),
        'delta_pagamentos_que_escolheram_switching': int(_safe_float(resumo_ativo.get('pagamentos_que_escolheram_switching')) - _safe_float(resumo_neutro.get('pagamentos_que_escolheram_switching'))),
        'casos_alterados_no_fluxo': alterados[:20],
    }



def rodar_fluxo_pagamentos_terminal_recorte_amplo_v142(*, raiz_repositorio: Path, limite_pagamentos: int = 45) -> dict[str, Any]:
    base = Path(raiz_repositorio)
    fluxo_h1h3 = _rodar_fluxo(
        raiz_repositorio=base,
        limite_pagamentos=limite_pagamentos,
        config_override=None,
        comparar_local_h1h3=False,
    )
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
    fluxo_neutro = _rodar_fluxo(
        raiz_repositorio=base,
        limite_pagamentos=limite_pagamentos,
        config_override=_config_sem_h1h3(contexto.pacote_config.conteudo),
        comparar_local_h1h3=False,
    )
    comparacao_local = {
        'pagamentos_com_mudanca_local_h1h3': 0,
        'transicoes_locais_h1h3': {},
        'transicoes_locais_h1h3_foco': {},
        'top_casos_alterados': [],
        'observacao': 'Comparação local no mesmo estado foi desativada nesta rodada para priorizar a comparação de fluxo completo em recorte real maior com custo computacional controlado.',
    }
    comparacao_fluxos = _comparar_fluxos(
        fluxo_h1h3.get('resultados_pagamento') or [],
        fluxo_neutro.get('resultados_pagamento') or [],
        fluxo_h1h3.get('resumo') or {},
        fluxo_neutro.get('resumo') or {},
        fluxo_h1h3.get('metrica_central') or {},
        fluxo_neutro.get('metrica_central') or {},
    )
    return {
        'status': 'ok',
        'versao': 'V142',
        'limite_pagamentos': int(limite_pagamentos),
        'fluxo_h1h3_ativo': fluxo_h1h3,
        'fluxo_h1h3_neutro': fluxo_neutro,
        'comparacao_local_mesmo_estado': comparacao_local,
        'comparacao_fluxo_completo': comparacao_fluxos,
    }
