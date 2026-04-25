from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, escolher_melhor_cenario_promovivel
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _ativar_recebidos_futuros_no_dia,
    _coerce_date,
    _consumir_componentes,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)


from nucleo.utilitarios_neutros import _safe_float
@dataclass(slots=True)
class ResultadoPagamentoRecorteV138:
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

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ResumoFluxoPagamentosRecorteV138:
    data_inicio: str
    data_fim: str
    quantidade_pagamentos: int
    quantidade_dias_com_pagamento: int
    contagem_fontes: dict[str, int]
    pagamentos_com_switching_elegivel_promovivel: int
    pagamentos_que_escolheram_switching: int
    pagamentos_cobertos_integralmente: int
    deficit_total: float

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


MAX_FONTES_POR_DESTINO = 3


def _carregar_estado_recorte(contexto: Any, *, data_inicio: date | None = None, data_fim: date | None = None, limite_pagamentos: int = 15) -> tuple[dict[str, Any], date, int]:
    data_inicio = data_inicio or contexto.execucao.data_referencia
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=data_inicio)
    if limite_pagamentos > 0:
        pagamentos = pagamentos.head(limite_pagamentos).copy()
    data_fim = data_fim or (min(max(pagamentos['data']), data_inicio + timedelta(days=30)) if len(pagamentos) else data_inicio)
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


def _ticket_ok(valor_total: float, acao: dict[str, Any], *, individual: bool) -> bool:
    minimo = _safe_float(acao.get('aplicacao_minima_destino'))
    maximo = _safe_float(acao.get('aplicacao_maxima_destino'))
    somente_combo = bool(acao.get('somente_combo_destino') or False)
    if individual:
        if not bool(acao.get('atende_ticket_individual', True)):
            return False
        if somente_combo:
            return False
    else:
        if minimo > 0.0 and valor_total + 1e-9 < minimo:
            return False
        if maximo > 0.0 and valor_total - 1e-9 > maximo:
            return False
    return True


def _cap_fontes_por_destino(acoes: list[dict[str, Any]], max_fontes: int = MAX_FONTES_POR_DESTINO) -> list[dict[str, Any]]:
    por_destino: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for acao in acoes:
        destino = str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')
        por_destino[destino].append(deepcopy(acao))
    saida: list[dict[str, Any]] = []
    for grupo in por_destino.values():
        grupo = sorted(grupo, key=lambda a: _safe_float(a.get('ganho_terminal_economico_minimo_estimado')), reverse=True)
        saida.extend(grupo[:max_fontes])
    return saida


def _melhores_por_fonte_destino(acoes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    melhores: dict[tuple[str, str], dict[str, Any]] = {}
    for acao in acoes:
        if str(acao.get('tipo_acao') or '') not in {'switching_simples', 'aporte_nao_aportado'}:
            continue
        if not acao.get('elegivel'):
            continue
        fonte = str(acao.get('lote_origem_id') or '')
        destino = str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')
        if not fonte or not destino:
            continue
        chave = (fonte, destino)
        atual = melhores.get(chave)
        score = _safe_float(acao.get('ganho_terminal_economico_minimo_estimado'))
        if atual is None or score > _safe_float(atual.get('ganho_terminal_economico_minimo_estimado')):
            melhores[chave] = deepcopy(acao)
    return list(melhores.values())


def _gerar_cenarios_integral_parametrizados(acoes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cenarios: list[dict[str, Any]] = []
    for acao in acoes:
        valor_total = round(_safe_float(acao.get('valor_migrado_estimado') or acao.get('valor_liquido_resgatavel')), 2)
        if not _ticket_ok(valor_total, acao, individual=True):
            continue
        evento = deepcopy(acao)
        evento['fracao_lote'] = 1.0
        cenarios.append({
            'familia': 'individual_integral_parametrizado',
            'rotulo': f"{acao.get('lote_origem_id')} -> {acao.get('produto_destino')}",
            'produto_destino': acao.get('produto_destino'),
            'eventos': [evento],
            'valor_total_alocado': valor_total,
        })
    por_destino: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for acao in acoes:
        por_destino[str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')].append(deepcopy(acao))
    for grupo in por_destino.values():
        grupo = sorted(grupo, key=lambda a: _safe_float(a.get('ganho_terminal_economico_minimo_estimado')), reverse=True)
        if len(grupo) < 2:
            continue
        for tamanho in range(2, len(grupo) + 1):
            for combo in combinations(grupo, tamanho):
                fontes = [str(acao.get('lote_origem_id') or '') for acao in combo]
                if len(set(fontes)) < len(fontes):
                    continue
                valor_total = round(sum(_safe_float(acao.get('valor_migrado_estimado') or acao.get('valor_liquido_resgatavel')) for acao in combo), 2)
                if not _ticket_ok(valor_total, combo[0], individual=False):
                    continue
                eventos = []
                for acao in combo:
                    evento = deepcopy(acao)
                    evento['fracao_lote'] = 1.0
                    eventos.append(evento)
                cenarios.append({
                    'familia': 'agrupado_integral_parametrizado',
                    'rotulo': f"{' + '.join(fontes)} -> {combo[0].get('produto_destino')}",
                    'produto_destino': combo[0].get('produto_destino'),
                    'eventos': eventos,
                    'valor_total_alocado': valor_total,
                })
    return cenarios


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
        limite_candidatos_por_data=24,
    )
    acoes = [
        deepcopy(item)
        for item in (plano.get('acoes_candidatas') or [])
        if str(item.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'} and item.get('elegivel')
    ]
    acoes = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), MAX_FONTES_POR_DESTINO)
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


def rodar_fluxo_pagamentos_terminal_recorte_curto_v138(
    *,
    raiz_repositorio: Path,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
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
    config = contexto.pacote_config.conteudo
    estado, data_fim_recorte, quantidade_pagamentos = _carregar_estado_recorte(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
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
    contagem_fontes: dict[str, int] = defaultdict(int)
    pagamentos_com_switching_promovivel = 0
    pagamentos_que_escolheram_switching = 0

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
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=deepcopy(estado_corrente),
                config=config,
                plano_switching_candidato=plano_switching,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            tipo_fonte = str(alocacao.get('fonte_principal_tipo') or 'sem_fonte_viavel')
            classe_sw = None if plano_switching is None else str(plano_switching.get('classe_comparador_hibrido') or '')
            rotulo_sw = None if plano_switching is None else str(plano_switching.get('rotulo') or '')
            switching_aplicado = False
            if tipo_fonte == 'cenario_switching_elegivel' and plano_switching is not None:
                _aplicar_switching_eventos(estado_corrente, plano_switching.get('eventos') or [], dia, historico_fluxo)
                switching_aplicado = True
                pagamentos_que_escolheram_switching += 1
            _consumir_componentes(estado_corrente, alocacao.get('componentes_escolhidos') or [])
            contagem_fontes[tipo_fonte] += 1
            resultados_pagamento.append(ResultadoPagamentoRecorteV138(
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
            ).para_dict())
            historico_fluxo.append({
                'tipo_evento': 'pagamento_terminal_v138',
                'data_evento': dia.isoformat(),
                'pagamento_id': pagamento.get('pagamento_id'),
                'fonte_principal_tipo': tipo_fonte,
                'fonte_principal_id': alocacao.get('fonte_principal_id'),
                'switching_aplicado': switching_aplicado,
                'rotulo_cenario_switching': rotulo_sw,
            })
        dia += timedelta(days=1)

    resumo = ResumoFluxoPagamentosRecorteV138(
        data_inicio=data_inicio.isoformat(),
        data_fim=data_fim_recorte.isoformat(),
        quantidade_pagamentos=quantidade_pagamentos,
        quantidade_dias_com_pagamento=len({str(item['data_pagamento']) for item in resultados_pagamento}),
        contagem_fontes=dict(sorted(contagem_fontes.items())),
        pagamentos_com_switching_elegivel_promovivel=pagamentos_com_switching_promovivel,
        pagamentos_que_escolheram_switching=pagamentos_que_escolheram_switching,
        pagamentos_cobertos_integralmente=sum(1 for item in resultados_pagamento if item.get('cobertura_integral')),
        deficit_total=round(sum(_safe_float(item.get('valor_deficit')) for item in resultados_pagamento), 2),
    ).para_dict()

    return {
        'status': 'ok',
        'versao': 'V138',
        'resumo': resumo,
        'resultados_pagamento': resultados_pagamento,
        'historico_fluxo': historico_fluxo,
        'metadados_recorte': deepcopy(estado.get('metadados_recorte') or {}),
    }
