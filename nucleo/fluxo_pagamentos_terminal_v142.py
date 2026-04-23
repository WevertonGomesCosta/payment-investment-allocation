from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_v138 import (
    ResultadoPagamentoRecorteV138,
    _carregar_estado_recorte,
    _coerce_date,
    _safe_float,
    _melhor_plano_switching_promovivel_para_estado,
)
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _ativar_recebidos_futuros_no_dia,
    _consumir_componentes,
)


@dataclass(slots=True)
class ResumoComparativoFluxoV142:
    data_inicio: str
    data_fim: str
    limite_pagamentos: int
    pagamentos_avaliados: int
    dias_com_pagamento: int
    contagem_fontes_sem_h1_h3: dict[str, int]
    contagem_fontes_com_h1_h3: dict[str, int]
    pagamentos_com_mudanca_fonte: int
    pagamentos_com_mudanca_tipo: int
    pagamentos_com_switching_promovivel_disponivel: int
    pagamentos_com_switching_escolhido_sem_h1_h3: int
    pagamentos_com_switching_escolhido_com_h1_h3: int
    deficit_total_sem_h1_h3: float
    deficit_total_com_h1_h3: float

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def _default_data_fim(contexto: Any, data_inicio: date, limite_pagamentos: int) -> date:
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=data_inicio)
    if limite_pagamentos > 0:
        pagamentos = pagamentos.head(limite_pagamentos).copy()
    if len(pagamentos) == 0:
        return data_inicio
    data_max = max(pagamentos['data'])
    return data_max if isinstance(data_max, date) else data_inicio + timedelta(days=90)


def _executar_fluxo_pagamentos_terminal(
    *,
    contexto: Any,
    config: dict[str, Any],
    data_inicio: date,
    data_fim: date,
    limite_pagamentos: int,
    rotulo_execucao: str,
) -> dict[str, Any]:
    estado, data_fim_recorte, quantidade_pagamentos = _carregar_estado_recorte(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    pagamentos = sorted(
        [deepcopy(dict(item)) for item in estado.get('pagamentos_futuros', [])],
        key=lambda item: (
            _coerce_date(item.get('data')) or date.max,
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )
    pagamentos_por_dia: dict[str, list[dict[str, Any]]] = {}
    for pagamento in pagamentos:
        pagamentos_por_dia.setdefault((_coerce_date(pagamento.get('data')) or data_inicio).isoformat(), []).append(pagamento)

    estado_corrente = deepcopy(estado)
    historico_fluxo: list[dict[str, Any]] = []
    resultados_pagamento: list[dict[str, Any]] = []
    contagem_fontes: Counter[str] = Counter()
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
            switching_aplicado = False
            classe_sw = None if plano_switching is None else str(plano_switching.get('classe_comparador_hibrido') or '')
            rotulo_sw = None if plano_switching is None else str(plano_switching.get('rotulo') or '')
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
                'tipo_evento': 'pagamento_terminal_v142',
                'rotulo_execucao': rotulo_execucao,
                'data_evento': dia.isoformat(),
                'pagamento_id': pagamento.get('pagamento_id'),
                'fonte_principal_tipo': tipo_fonte,
                'fonte_principal_id': alocacao.get('fonte_principal_id'),
                'switching_aplicado': switching_aplicado,
                'rotulo_cenario_switching': rotulo_sw,
            })
        dia += timedelta(days=1)

    return {
        'status': 'ok',
        'rotulo_execucao': rotulo_execucao,
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim_recorte.isoformat(),
        'limite_pagamentos': limite_pagamentos,
        'quantidade_pagamentos': quantidade_pagamentos,
        'quantidade_dias_com_pagamento': len({str(item['data_pagamento']) for item in resultados_pagamento}),
        'contagem_fontes': dict(sorted(contagem_fontes.items())),
        'pagamentos_com_switching_elegivel_promovivel': pagamentos_com_switching_promovivel,
        'pagamentos_que_escolheram_switching': pagamentos_que_escolheram_switching,
        'pagamentos_cobertos_integralmente': sum(1 for item in resultados_pagamento if item.get('cobertura_integral')),
        'deficit_total': round(sum(_safe_float(item.get('valor_deficit')) for item in resultados_pagamento), 2),
        'resultados_pagamento': resultados_pagamento,
        'historico_fluxo': historico_fluxo,
        'metadados_recorte': deepcopy(estado.get('metadados_recorte') or {}),
    }


def _comparar_resultados(sem_h: dict[str, Any], com_h: dict[str, Any]) -> dict[str, Any]:
    antes = {f"{item['data_pagamento']}::{item['pagamento_id']}": item for item in sem_h.get('resultados_pagamento', [])}
    depois = {f"{item['data_pagamento']}::{item['pagamento_id']}": item for item in com_h.get('resultados_pagamento', [])}
    mudancas: list[dict[str, Any]] = []
    for chave in sorted(set(antes) | set(depois)):
        a = antes.get(chave)
        b = depois.get(chave)
        if a is None or b is None:
            continue
        mudou_tipo = a.get('fonte_principal_tipo') != b.get('fonte_principal_tipo')
        mudou_id = a.get('fonte_principal_id') != b.get('fonte_principal_id')
        mudou_switching = bool(a.get('switching_aplicado_no_fluxo')) != bool(b.get('switching_aplicado_no_fluxo'))
        if mudou_tipo or mudou_id or mudou_switching:
            mudancas.append({
                'chave_pagamento': chave,
                'data_pagamento': a.get('data_pagamento'),
                'pagamento_id': a.get('pagamento_id'),
                'descricao': a.get('descricao'),
                'antes_fonte_tipo': a.get('fonte_principal_tipo'),
                'depois_fonte_tipo': b.get('fonte_principal_tipo'),
                'antes_fonte_id': a.get('fonte_principal_id'),
                'depois_fonte_id': b.get('fonte_principal_id'),
                'antes_switching': bool(a.get('switching_aplicado_no_fluxo')),
                'depois_switching': bool(b.get('switching_aplicado_no_fluxo')),
                'antes_perda_terminal': a.get('perda_retorno_terminal_estimada'),
                'depois_perda_terminal': b.get('perda_retorno_terminal_estimada'),
                'antes_custo_fiscal': a.get('custo_fiscal_imediato'),
                'depois_custo_fiscal': b.get('custo_fiscal_imediato'),
            })
    resumo = ResumoComparativoFluxoV142(
        data_inicio=str(com_h.get('data_inicio')),
        data_fim=str(com_h.get('data_fim')),
        limite_pagamentos=int(com_h.get('limite_pagamentos') or 0),
        pagamentos_avaliados=int(com_h.get('quantidade_pagamentos') or 0),
        dias_com_pagamento=int(com_h.get('quantidade_dias_com_pagamento') or 0),
        contagem_fontes_sem_h1_h3=dict(sorted((sem_h.get('contagem_fontes') or {}).items())),
        contagem_fontes_com_h1_h3=dict(sorted((com_h.get('contagem_fontes') or {}).items())),
        pagamentos_com_mudanca_fonte=len(mudancas),
        pagamentos_com_mudanca_tipo=sum(1 for item in mudancas if item['antes_fonte_tipo'] != item['depois_fonte_tipo']),
        pagamentos_com_switching_promovivel_disponivel=max(int(sem_h.get('pagamentos_com_switching_elegivel_promovivel') or 0), int(com_h.get('pagamentos_com_switching_elegivel_promovivel') or 0)),
        pagamentos_com_switching_escolhido_sem_h1_h3=int(sem_h.get('pagamentos_que_escolheram_switching') or 0),
        pagamentos_com_switching_escolhido_com_h1_h3=int(com_h.get('pagamentos_que_escolheram_switching') or 0),
        deficit_total_sem_h1_h3=round(_safe_float(sem_h.get('deficit_total')), 2),
        deficit_total_com_h1_h3=round(_safe_float(com_h.get('deficit_total')), 2),
    ).para_dict()
    return {'resumo': resumo, 'mudancas_pagamento': mudancas}


def comparar_fluxo_pagamentos_terminal_fase1_v142(
    *,
    raiz_repositorio: Path,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 18,
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
    data_inicio = data_inicio or contexto.execucao.data_referencia
    data_fim = data_fim or _default_data_fim(contexto, data_inicio, limite_pagamentos)
    config_base = deepcopy(contexto.pacote_config.conteudo)
    config_sem = deepcopy(config_base)
    config_sem['desabilitar_modelos_script1_fase1'] = True
    config_com = deepcopy(config_base)
    config_com['desabilitar_modelos_script1_fase1'] = False

    resultado_sem = _executar_fluxo_pagamentos_terminal(
        contexto=contexto,
        config=config_sem,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
        rotulo_execucao='sem_h1_h3',
    )
    resultado_com = _executar_fluxo_pagamentos_terminal(
        contexto=contexto,
        config=config_com,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
        rotulo_execucao='com_h1_h3',
    )
    comparativo = _comparar_resultados(resultado_sem, resultado_com)
    return {
        'status': 'ok',
        'versao': 'V142',
        'resultado_sem_h1_h3': resultado_sem,
        'resultado_com_h1_h3': resultado_com,
        **comparativo,
    }
