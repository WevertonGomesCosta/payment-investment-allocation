from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import _safe_float
from nucleo.motor_diario import (
    DecisaoDiaV143,
    PacoteDiaResumoV143,
    ResumoMotorV143,
    _avaliar_continuacao_neutra,
    _carregar_estado_janela,
    _chave_pacote,
    _chave_pacote_tau,
    _combinar_metricas,
    _executar_pacote_dia,
    _ordenar_pagamentos,
    _remover_pagamentos_ate_dia,
    _selecionar_vencedor_pacote,
    _cenarios_switching_diario_v143,
    _melhor_plano_switching_diario_v143,
)
from nucleo.simulador_central_eventos_v1 import (
    _ativar_recebidos_futuros_no_dia,
    _calcular_metrica,
    _coerce_date,
    _normalizar_lote_pos_vencimento_no_dia,
    _patrimonio_terminal_proxy,
)

__all__ = [
    'PacoteDiaResumoV143',
    'DecisaoDiaV143',
    'ResumoMotorV143',
    '_ordenar_pagamentos',
    '_combinar_metricas',
    '_remover_pagamentos_ate_dia',
    '_avaliar_continuacao_neutra',
    '_cenarios_switching_diario_v143',
    '_melhor_plano_switching_diario_v143',
    '_executar_pacote_dia',
    '_chave_pacote',
    '_chave_pacote_tau',
    '_selecionar_vencedor_pacote',
    '_carregar_estado_janela',
    'rodar_motor_diario_conjunto_experimental_v143',
]


def rodar_motor_diario_conjunto_experimental_v143(
    *,
    raiz_repositorio: Path,
    data_inicio: date,
    data_fim: date,
    limite_candidatos_por_data: int = 24,
    cap_fontes_destino: int = 5,
    tau_custo_operacional: float | None = None,
) -> dict[str, object]:
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
    pagamentos_por_dia: dict[str, list[dict[str, object]]] = defaultdict(list)
    for pagamento in pagamentos_iniciais:
        pagamentos_por_dia[(_coerce_date(pagamento.get('data')) or data_inicio).isoformat()].append(deepcopy(dict(pagamento)))

    decisoes: list[dict[str, object]] = []
    historico_execucao: list[dict[str, object]] = []
    contagem_fontes: dict[str, int] = defaultdict(int)
    resultados_pagamento_executados: list[dict[str, object]] = []

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

        candidatos: list[dict[str, object]] = []
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

        vencedor = _selecionar_vencedor_pacote(candidatos, tau_custo_operacional)
        estado_corrente = deepcopy(vencedor.get('estado_pos_dia') or estado_corrente)
        _remover_pagamentos_ate_dia(estado_corrente, dia)
        for pagamento in vencedor.get('resultados_pagamento') or []:
            resultados_pagamento_executados.append(deepcopy(pagamento))
            contagem_fontes[str(pagamento.get('fonte_principal_tipo') or 'sem_fonte')] += 1

        if tau_custo_operacional is None:
            justificativa = (
                f"Vencedor por vetor total estimado {tuple(vencedor.get('vetor_total_estimado') or ())} "
                f"e patrimônio terminal proxy estimado R$ {float(vencedor.get('patrimonio_terminal_proxy_estimado') or 0.0):.2f}."
            )
        else:
            justificativa = (
                f"Vencedor por chave tau={tau_custo_operacional:.2f}, vetor base {tuple(vencedor.get('vetor_total_estimado') or ())} "
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
        'versao': 'V153',
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
        'parametro_tau_custo_operacional': tau_custo_operacional,
        'observacao_metodologica': (
            'Motor diário conjunto experimental: a escolha do pacote do dia usa continuação neutra até o fim da janela '
            'sem novo switching proativo após o dia avaliado. A comparação é útil para auditar precedência diária, '
            'mas não substitui ainda um resolvedor global exato de múltiplos dias.'
        ),
    }
