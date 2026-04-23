from __future__ import annotations

import json
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from nucleo.comparador_hibrido_switching_v1 import escolher_melhor_cenario_promovivel
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.motor_diario import (
    _carregar_estado_janela,
    _cenarios_switching_diario_v143,
    _executar_pacote_dia,
    _ordenar_pagamentos,
    _remover_pagamentos_ate_dia,
    _selecionar_vencedor_pacote,
)
from nucleo.simulador_central_eventos_v1 import (
    _ativar_recebidos_futuros_no_dia,
    _coerce_date,
    _normalizar_lote_pos_vencimento_no_dia,
)


def _safe_float(valor: Any) -> float:
    try:
        if valor in (None, ''):
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def _safe_str(valor: Any) -> str:
    if valor in (None, ''):
        return ''
    return str(valor)


def _arred(valor: Any) -> float:
    return round(_safe_float(valor), 2)


def _capturar_inconsistencias_temporais_no_estado(estado: dict[str, Any], dia: date) -> list[dict[str, Any]]:
    inconsistencias: list[dict[str, Any]] = []
    for recebido in list(estado.get('recebidos_nao_aportados_disponiveis') or []):
        data_recebimento = _coerce_date(recebido.get('data_recebimento'))
        if data_recebimento is not None and data_recebimento > dia:
            inconsistencias.append({
                'tipo': 'recebido_disponivel_futuro_no_estado',
                'dia': dia.isoformat(),
                'id': str(recebido.get('id') or recebido.get('fonte_id') or ''),
                'data_recebimento': data_recebimento.isoformat(),
            })
    for lote in list(estado.get('lotes_aportados') or []):
        data_aplicacao = _coerce_date(lote.get('data_aplicacao'))
        if data_aplicacao is not None and data_aplicacao > dia:
            inconsistencias.append({
                'tipo': 'lote_aportado_futuro_no_estado',
                'dia': dia.isoformat(),
                'id': str(lote.get('id') or ''),
                'data_aplicacao': data_aplicacao.isoformat(),
            })
    return inconsistencias


def _resumir_componente_pagamento(item: dict[str, Any], indice: int) -> dict[str, Any]:
    return {
        'ordem': indice,
        'tipo_fonte': _safe_str(item.get('tipo_fonte')),
        'fonte_id': _safe_str(item.get('fonte_id')),
        'valor_utilizado': _arred(item.get('valor_utilizado')),
        'classe_comparador_hibrido': _safe_str(item.get('classe_comparador_hibrido')),
    }


def _resumir_fonte_candidata(item: dict[str, Any], fonte_principal_tipo: str, fonte_principal_id: str) -> dict[str, Any]:
    tipo = _safe_str(item.get('tipo_fonte'))
    fonte_id = _safe_str(item.get('fonte_id'))
    return {
        'selecionada': tipo == fonte_principal_tipo and fonte_id == fonte_principal_id,
        'tipo_fonte': tipo,
        'fonte_id': fonte_id,
        'valor_coberto': _arred(item.get('valor_coberto')),
        'valor_deficit': _arred(item.get('valor_deficit')),
        'cobertura_integral': bool(item.get('cobertura_integral')),
        'custo_fiscal_imediato': _arred(item.get('custo_fiscal_imediato')),
        'perda_retorno_terminal_estimada': _arred(item.get('perda_retorno_terminal_estimada')),
        'penalidade_liquidez_futura': _arred(item.get('penalidade_liquidez_futura')),
        'penalidade_estrategica_lote': _arred(item.get('penalidade_estrategica_lote')),
        'score_terminal_comparativo': list(item.get('score_terminal_comparativo') or []),
        'score_auxiliar_script1': list(item.get('score_auxiliar_script1') or []),
        'justificativa': _safe_str(item.get('justificativa')),
        'proxy_terminal_fonte': _arred((item.get('metadados_extras') or {}).get('proxy_terminal_fonte')),
        'dias_idade_fonte': int((item.get('metadados_extras') or {}).get('dias_idade_fonte') or 0),
        'classe_comparador_hibrido': _safe_str((item.get('metadados_extras') or {}).get('classe_comparador_hibrido')),
        'promovivel_hibrido': bool((item.get('metadados_extras') or {}).get('promovivel_hibrido')),
        'componentes': [
            _resumir_componente_pagamento(comp, indice)
            for indice, comp in enumerate(item.get('componentes') or [], start=1)
        ],
    }


def _resumir_pagamento_vencedor(item: dict[str, Any], *, pagamento_original: dict[str, Any] | None = None, limite_fontes: int = 12) -> dict[str, Any]:
    original = dict(pagamento_original or {})
    fonte_principal_tipo = _safe_str(item.get('fonte_principal_tipo'))
    fonte_principal_id = _safe_str(item.get('fonte_principal_id'))
    valor_pagamento = _safe_float(item.get('valor_pagamento') or item.get('valor') or original.get('valor'))
    if valor_pagamento <= 0.0:
        valor_pagamento = round(_safe_float(item.get('valor_coberto')) + _safe_float(item.get('valor_deficit')), 2)
    fontes_candidatas = [
        _resumir_fonte_candidata(fonte, fonte_principal_tipo, fonte_principal_id)
        for fonte in (item.get('fontes_candidatas') or [])
    ]
    fontes_candidatas = sorted(
        fontes_candidatas,
        key=lambda x: (
            not x.get('selecionada', False),
            not x.get('cobertura_integral', False),
            x.get('valor_deficit', 0.0),
            x.get('perda_retorno_terminal_estimada', 0.0),
            x.get('custo_fiscal_imediato', 0.0),
            x.get('penalidade_liquidez_futura', 0.0),
            x.get('tipo_fonte', ''),
            x.get('fonte_id', ''),
        ),
    )
    return {
        'pagamento_id': _safe_str(item.get('pagamento_id') or original.get('pagamento_id') or original.get('despesa_id') or original.get('id')),
        'data_pagamento': _safe_str(item.get('data_pagamento') or original.get('data')),
        'classe_pagamento': _safe_str(item.get('classe_pagamento') or original.get('classe_pagamento_operacional') or original.get('classe_pagamento') or original.get('classe')),
        'descricao': _safe_str(item.get('descricao') or original.get('descricao') or original.get('descricao_padronizada') or original.get('descricao_original') or original.get('nome')),
        'valor_pagamento': _arred(valor_pagamento),
        'melhor_acao_pagamento': _safe_str(item.get('melhor_acao_pagamento')),
        'fonte_principal_tipo': fonte_principal_tipo,
        'fonte_principal_id': fonte_principal_id,
        'valor_coberto': _arred(item.get('valor_coberto')),
        'valor_deficit': _arred(item.get('valor_deficit')),
        'cobertura_integral': bool(item.get('cobertura_integral')),
        'data_resgate_ou_uso': _safe_str(item.get('data_resgate_ou_uso')),
        'custo_fiscal_imediato': _arred(item.get('custo_fiscal_imediato')),
        'perda_retorno_terminal_estimada': _arred(item.get('perda_retorno_terminal_estimada')),
        'penalidade_liquidez_futura': _arred(item.get('penalidade_liquidez_futura')),
        'penalidade_estrategica_lote': _arred(item.get('penalidade_estrategica_lote')),
        'score_terminal_comparativo': list(item.get('score_terminal_comparativo') or []),
        'score_auxiliar_script1': list(item.get('score_auxiliar_script1') or []),
        'justificativa': _safe_str(item.get('justificativa')),
        'metadados_escolhidos': deepcopy(dict(item.get('metadados_escolhidos') or {})),
        'componentes_reais_pagamento': [
            _resumir_componente_pagamento(comp, indice)
            for indice, comp in enumerate(item.get('componentes_escolhidos') or [], start=1)
        ],
        'fontes_candidatas_ordenadas': fontes_candidatas[:limite_fontes],
        'resumo_comparacao_switching': deepcopy(dict(item.get('resumo_comparacao_switching') or {})),
    }


def _resumir_acao_candidata_switching(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'id_acao': _safe_str(item.get('id_acao')),
        'tipo_acao': _safe_str(item.get('tipo_acao')),
        'data_acao': _safe_str(item.get('data_acao')),
        'lote_origem_id': _safe_str(item.get('lote_origem_id')),
        'produto_origem': _safe_str(item.get('produto_origem')),
        'produto_destino': _safe_str(item.get('produto_destino')),
        'produto_destino_key': _safe_str(item.get('produto_destino_key')),
        'elegivel': bool(item.get('elegivel')),
        'valor_liquido_resgatavel': _arred(item.get('valor_liquido_resgatavel')),
        'valor_migrado_estimado': _arred(item.get('valor_migrado_estimado')),
        'custo_fiscal_estimado': _arred(item.get('custo_fiscal_estimado')),
        'ganho_terminal_economico_minimo_estimado': _arred(item.get('ganho_terminal_economico_minimo_estimado')),
        'patrimonio_terminal_origem_estimado': _arred(item.get('patrimonio_terminal_origem_estimado')),
        'patrimonio_terminal_destino_estimado': _arred(item.get('patrimonio_terminal_destino_estimado')),
        'perda_liquidez_estimada': _arred(item.get('perda_liquidez_estimada')),
        'impacto_pagamentos_futuros_estimado': _arred(item.get('impacto_pagamentos_futuros_estimado')),
        'retorno_anual_destino': _arred(item.get('retorno_anual_destino')),
        'liquidez_dias_destino': int(item.get('liquidez_dias_destino') or 0),
        'carencia_dias_destino': int(item.get('carencia_dias_destino') or 0),
        'fracao_lote': round(_safe_float(item.get('fracao_lote') if item.get('fracao_lote') not in (None, '') else 1.0), 6),
        'rank_destino_sugerido': int(item.get('rank_destino_sugerido') or 0),
        'motivo_bloqueio_ticket_individual': _safe_str(item.get('motivo_bloqueio_ticket_individual')),
        'justificativa': _safe_str(item.get('justificativa')),
    }


def _resumir_evento_switching(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'id_acao': _safe_str(item.get('id_acao')),
        'tipo_acao': _safe_str(item.get('tipo_acao')),
        'lote_origem_id': _safe_str(item.get('lote_origem_id')),
        'produto_origem': _safe_str(item.get('produto_origem')),
        'produto_destino': _safe_str(item.get('produto_destino')),
        'valor_liquido_resgatavel': _arred(item.get('valor_liquido_resgatavel')),
        'valor_migrado_estimado': _arred(item.get('valor_migrado_estimado')),
        'custo_fiscal_estimado': _arred(item.get('custo_fiscal_estimado')),
        'ganho_terminal_economico_minimo_estimado': _arred(item.get('ganho_terminal_economico_minimo_estimado')),
        'liquidez_dias_destino': int(item.get('liquidez_dias_destino') or 0),
        'carencia_dias_destino': int(item.get('carencia_dias_destino') or 0),
        'fracao_lote': round(_safe_float(item.get('fracao_lote') if item.get('fracao_lote') not in (None, '') else 1.0), 6),
    }


def _resumir_cenario_switching(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'familia': _safe_str(item.get('familia')),
        'rotulo': _safe_str(item.get('rotulo')),
        'produto_destino': _safe_str(item.get('produto_destino')),
        'classe_comparador_hibrido': _safe_str(item.get('classe_comparador_hibrido')),
        'promovivel_hibrido': bool(item.get('promovivel_hibrido')),
        'motivo_comparador_hibrido': _safe_str(item.get('motivo_comparador_hibrido')),
        'continua_vencedor_central': bool(item.get('continua_vencedor_central')),
        'delta_perda_terminal_vs_baseline': _arred(item.get('delta_perda_terminal_vs_baseline')),
        'delta_deficit_vs_baseline': _arred(item.get('delta_deficit_vs_baseline')),
        'delta_violacoes_protegida_vs_baseline': _arred(item.get('delta_violacoes_protegida_vs_baseline')),
        'delta_patrimonio_proxy_vs_baseline': _arred(item.get('delta_patrimonio_proxy_vs_baseline')),
        'custo_fiscal_switching_total': _arred(item.get('custo_fiscal_switching_total')),
        'perda_liquidez_switching_total': _arred(item.get('perda_liquidez_switching_total')),
        'patrimonio_liquido_terminal_proxy': _arred(item.get('patrimonio_liquido_terminal_proxy')),
        'vetor_lexicografico': list(item.get('vetor_lexicografico') or []),
        'vetor_baseline': list(item.get('vetor_baseline') or []),
        'eventos': [_resumir_evento_switching(ev) for ev in (item.get('eventos') or [])],
    }


def _resumir_lotes_monitorados(estado: dict[str, Any], config: dict[str, Any], dia: date) -> list[dict[str, Any]]:
    ids_monitorados = list(((config or {}).get('auditoria') or {}).get('lotes_monitorados_liquido') or [])
    if not ids_monitorados:
        return []
    resumo: list[dict[str, Any]] = []
    lotes_aportados = list(estado.get('lotes_aportados') or [])
    recebidos_disp = list(estado.get('recebidos_nao_aportados_disponiveis') or [])
    recebidos_futuros = list(estado.get('recebidos_nao_aportados_futuros') or [])
    for lote_id in ids_monitorados:
        item = next((x for x in lotes_aportados if _safe_str(x.get('id')) == lote_id), None)
        origem = 'lote_aportado'
        if item is None:
            item = next((x for x in recebidos_disp if _safe_str(x.get('id') or x.get('fonte_id')) == lote_id), None)
            origem = 'recebido_disponivel'
        if item is None:
            item = next((x for x in recebidos_futuros if _safe_str(x.get('id') or x.get('fonte_id')) == lote_id), None)
            origem = 'recebido_futuro'
        if item is None:
            resumo.append({'id': lote_id, 'origem_estado': 'ausente_no_estado', 'disponivel_no_dia': False})
            continue
        data_base = _coerce_date(item.get('data_aplicacao') or item.get('data_recebimento'))
        data_venc = _coerce_date(item.get('data_vencimento') or item.get('vencimento') or item.get('data_vencimento_origem'))
        valor_relevante = item.get('valor_liquido_resgatavel')
        if valor_relevante in (None, ''):
            valor_relevante = item.get('valor_disponivel')
        if valor_relevante in (None, ''):
            valor_relevante = item.get('valor')
        resumo.append({
            'id': lote_id,
            'origem_estado': origem,
            'investimento': _safe_str(item.get('investimento') or item.get('produto_origem') or item.get('produto_nome_canonico')),
            'data_base': data_base.isoformat() if data_base is not None else None,
            'data_vencimento': data_venc.isoformat() if data_venc is not None else None,
            'valor_relevante': _arred(valor_relevante),
            'valor_disponivel': _arred(item.get('valor_disponivel')),
            'valor_liquido_resgatavel': _arred(item.get('valor_liquido_resgatavel')),
            'disponivel_no_dia': bool(data_base is None or data_base <= dia),
            'pos_vencimento': bool(data_venc is not None and data_venc <= dia),
            'origem_pos_vencimento': bool(item.get('origem_pos_vencimento')),
            'data_vencimento_origem': _coerce_date(item.get('data_vencimento_origem')).isoformat() if _coerce_date(item.get('data_vencimento_origem')) is not None else None,
        })
    return resumo


def _resumir_normalizacao_pos_vencimento(item: dict[str, Any], dia: date) -> dict[str, Any]:
    data_recebimento = _coerce_date(item.get('data_recebimento'))
    data_vencimento_origem = _coerce_date(item.get('data_vencimento_origem'))
    valor_disponivel = item.get('valor_disponivel')
    if valor_disponivel in (None, ''):
        valor_disponivel = item.get('valor')
    return {
        'id': _safe_str(item.get('id') or item.get('fonte_id')),
        'produto_origem': _safe_str(item.get('produto_origem') or item.get('investimento')),
        'data_recebimento': data_recebimento.isoformat() if data_recebimento is not None else None,
        'data_vencimento_origem': data_vencimento_origem.isoformat() if data_vencimento_origem is not None else None,
        'valor_disponivel': _arred(valor_disponivel),
        'origem_pos_vencimento': bool(item.get('origem_pos_vencimento')),
        'disponivel_no_dia': bool(data_recebimento is None or data_recebimento <= dia),
    }


def rodar_validacao_diaria_operacional_v176(
    *,
    raiz_repositorio: Path,
    data_inicio: date,
    data_fim: date,
    limite_candidatos_por_data: int = 8,
    cap_fontes_destino: int = 3,
    tau_custo_operacional: float | None = None,
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
    mapa_pagamentos: dict[str, dict[str, Any]] = {}
    pagamentos_por_dia: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pagamento in pagamentos_iniciais:
        pagamento_id = _safe_str(pagamento.get('pagamento_id') or pagamento.get('despesa_id') or pagamento.get('id'))
        if pagamento_id:
            mapa_pagamentos[pagamento_id] = deepcopy(dict(pagamento))
        pagamentos_por_dia[(_coerce_date(pagamento.get('data')) or data_inicio).isoformat()].append(deepcopy(dict(pagamento)))

    dia = data_inicio
    decisoes_diarias: list[dict[str, Any]] = []
    pagamentos_executados: list[dict[str, Any]] = []
    inconsistencias_temporais: list[dict[str, Any]] = []
    contagem_familias = Counter()
    contagem_classes_hibridas = Counter()

    while dia <= data_fim:
        estado_corrente['data_evento_corrente'] = dia
        lotes_normalizados_pos_vencimento = _normalizar_lote_pos_vencimento_no_dia(estado_corrente, dia, config, None)
        recebidos_ativados_no_dia = _ativar_recebidos_futuros_no_dia(estado_corrente, dia, None)
        inconsistencias_temporais.extend(_capturar_inconsistencias_temporais_no_estado(estado_corrente, dia))

        pagamentos_dia = _ordenar_pagamentos(pagamentos_por_dia.get(dia.isoformat(), []))
        plano, cenarios = _cenarios_switching_diario_v143(
            estado=estado_corrente,
            config=config,
            data_atual=dia,
            data_fim=data_fim,
            limite_candidatos_por_data=limite_candidatos_por_data,
            cap_fontes_destino=cap_fontes_destino,
        )
        acoes_candidatas = [
            deepcopy(x)
            for x in (plano.get('acoes_candidatas') or [])
            if str(x.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'}
        ]
        for c in cenarios:
            contagem_familias[str(c.get('familia') or '')] += 1
            contagem_classes_hibridas[str(c.get('classe_comparador_hibrido') or '')] += 1

        melhor_plano = escolher_melhor_cenario_promovivel(cenarios)
        candidatos_pacote: list[dict[str, Any]] = []
        if pagamentos_dia:
            candidatos_pacote.append(_executar_pacote_dia(
                estado_inicial=estado_corrente,
                dia=dia,
                pagamentos_dia=pagamentos_dia,
                config=config,
                data_fim=data_fim,
                tipo_pacote='pay_only',
                plano_switching=None,
            ))
            if melhor_plano is not None:
                candidatos_pacote.append(_executar_pacote_dia(
                    estado_inicial=estado_corrente,
                    dia=dia,
                    pagamentos_dia=pagamentos_dia,
                    config=config,
                    data_fim=data_fim,
                    tipo_pacote='switch_then_pay',
                    plano_switching=melhor_plano,
                ))
        else:
            candidatos_pacote.append(_executar_pacote_dia(
                estado_inicial=estado_corrente,
                dia=dia,
                pagamentos_dia=[],
                config=config,
                data_fim=data_fim,
                tipo_pacote='no_action',
                plano_switching=None,
            ))
            if melhor_plano is not None:
                candidatos_pacote.append(_executar_pacote_dia(
                    estado_inicial=estado_corrente,
                    dia=dia,
                    pagamentos_dia=[],
                    config=config,
                    data_fim=data_fim,
                    tipo_pacote='switch_only',
                    plano_switching=melhor_plano,
                ))

        vencedor = _selecionar_vencedor_pacote(candidatos_pacote, tau_custo_operacional)
        gate_execucao_switching_diario = 'selecao_pacote'
        if not pagamentos_dia and melhor_plano is not None and bool(melhor_plano.get('promovivel_hibrido')):
            candidato_switch_only = next((c for c in candidatos_pacote if str(c.get('tipo_pacote') or '') == 'switch_only'), None)
            if candidato_switch_only is not None and not bool(vencedor.get('switching_executado')):
                vencedor = candidato_switch_only
                gate_execucao_switching_diario = 'override_promovivel_sem_pagamento'
        elif bool(vencedor.get('switching_executado')):
            gate_execucao_switching_diario = 'selecao_pacote_com_switching'
        estado_corrente = deepcopy(vencedor.get('estado_pos_dia') or estado_corrente)
        _remover_pagamentos_ate_dia(estado_corrente, dia)

        pagamentos_resumo = []
        for pagamento in vencedor.get('resultados_pagamento') or []:
            bruto = deepcopy(dict(pagamento))
            item = _resumir_pagamento_vencedor(bruto, pagamento_original=mapa_pagamentos.get(_safe_str(bruto.get('pagamento_id'))))
            pagamentos_executados.append(item)
            pagamentos_resumo.append(item)

        cenarios_resumo = sorted(
            [_resumir_cenario_switching(c) for c in cenarios],
            key=lambda x: (
                not x.get('promovivel_hibrido', False),
                x.get('classe_comparador_hibrido', ''),
                -_safe_float(x.get('delta_patrimonio_proxy_vs_baseline')),
                _safe_float(x.get('delta_perda_terminal_vs_baseline')),
                x.get('rotulo', ''),
            ),
        )
        acoes_resumo = sorted(
            [_resumir_acao_candidata_switching(a) for a in acoes_candidatas],
            key=lambda x: (
                not x.get('elegivel', False),
                -_safe_float(x.get('ganho_terminal_economico_minimo_estimado')),
                x.get('lote_origem_id', ''),
                x.get('produto_destino', ''),
            ),
        )

        decisoes_diarias.append({
            'data': dia.isoformat(),
            'resumo_estado': {
                'saldo_disponivel_geral': _arred(estado_corrente.get('saldo_disponivel_geral')),
                'quantidade_lotes_aportados': len(list(estado_corrente.get('lotes_aportados') or [])),
                'quantidade_recebidos_nao_aportados_disponiveis': len(list(estado_corrente.get('recebidos_nao_aportados_disponiveis') or [])),
                'quantidade_recebidos_nao_aportados_futuros': len(list(estado_corrente.get('recebidos_nao_aportados_futuros') or [])),
            },
            'lotes_monitorados': _resumir_lotes_monitorados(estado_corrente, config, dia),
            'lotes_normalizados_pos_vencimento': [
                _resumir_normalizacao_pos_vencimento(item, dia)
                for item in lotes_normalizados_pos_vencimento
            ],
            'recebidos_ativados_no_dia': [
                _resumir_normalizacao_pos_vencimento(item, dia)
                for item in recebidos_ativados_no_dia
            ],
            'quantidade_pagamentos': len(pagamentos_dia),
            'pacote_vencedor': str(vencedor.get('tipo_pacote') or ''),
            'switching_executado': bool(vencedor.get('switching_executado')),
            'rotulo_switching': str(vencedor.get('rotulo_switching') or ''),
            'classe_switching': str(vencedor.get('classe_switching') or ''),
            'gate_execucao_switching_diario': gate_execucao_switching_diario,
            'pagamentos': pagamentos_resumo,
            'switching': {
                'quantidade_acoes_candidatas': len(acoes_resumo),
                'quantidade_cenarios': len(cenarios_resumo),
                'quantidade_cenarios_promoviveis': sum(1 for c in cenarios_resumo if bool(c.get('promovivel_hibrido'))),
                'familias_cenarios_switching': dict(Counter(str(c.get('familia') or '') for c in cenarios)),
                'classes_cenarios_switching': dict(Counter(str(c.get('classe_comparador_hibrido') or '') for c in cenarios)),
                'acoes_candidatas': acoes_resumo,
                'cenarios_classificados': cenarios_resumo,
                'melhor_cenario_promovivel': _resumir_cenario_switching(melhor_plano) if melhor_plano is not None else None,
            },
        })
        dia += timedelta(days=1)

    resumo = {
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dias_no_horizonte': (data_fim - data_inicio).days + 1,
        'dias_com_pagamento': sum(1 for d in decisoes_diarias if int(d.get('quantidade_pagamentos') or 0) > 0),
        'dias_sem_pagamento': sum(1 for d in decisoes_diarias if int(d.get('quantidade_pagamentos') or 0) == 0),
        'dias_com_acoes_candidatas_switching': sum(1 for d in decisoes_diarias if int((d.get('switching') or {}).get('quantidade_acoes_candidatas') or 0) > 0),
        'dias_com_cenarios_promoviveis': sum(1 for d in decisoes_diarias if int((d.get('switching') or {}).get('quantidade_cenarios_promoviveis') or 0) > 0),
        'dias_com_switching_executado': sum(1 for d in decisoes_diarias if bool(d.get('switching_executado'))),
        'dias_com_normalizacao_pos_vencimento': sum(1 for d in decisoes_diarias if len(d.get('lotes_normalizados_pos_vencimento') or []) > 0),
        'pagamentos_no_horizonte': len(pagamentos_executados),
        'pagamentos_com_switching_no_fluxo': sum(1 for p in pagamentos_executados if any(c.get('tipo_fonte') == 'switching_elegivel_previo' for c in (p.get('componentes_reais_pagamento') or []))),
        'inconsistencias_temporais_no_estado': len(inconsistencias_temporais),
        'familias_cenarios_switching_avaliadas': dict(contagem_familias),
        'classes_cenarios_hibridos_avaliados': dict(contagem_classes_hibridas),
    }
    return {
        'status': 'ok',
        'versao': 'V176',
        'resumo': resumo,
        'decisoes_diarias': decisoes_diarias,
        'pagamentos_executados': pagamentos_executados,
        'inconsistencias_temporais': inconsistencias_temporais,
    }


__all__ = ['rodar_validacao_diaria_operacional_v176']
