from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

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


def rodar_validacao_diaria_operacional_v175(
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
    pagamentos_por_dia: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pagamento in pagamentos_iniciais:
        pagamentos_por_dia[(_coerce_date(pagamento.get('data')) or data_inicio).isoformat()].append(deepcopy(dict(pagamento)))

    dia = data_inicio
    decisoes_diarias: list[dict[str, Any]] = []
    pagamentos_executados: list[dict[str, Any]] = []
    inconsistencias_temporais: list[dict[str, Any]] = []
    contagem_familias = Counter()

    while dia <= data_fim:
        estado_corrente['data_evento_corrente'] = dia
        _normalizar_lote_pos_vencimento_no_dia(estado_corrente, dia, config, None)
        _ativar_recebidos_futuros_no_dia(estado_corrente, dia, None)
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
            if x.get('elegivel') and str(x.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'}
        ]
        for c in cenarios:
            contagem_familias[str(c.get('familia') or '')] += 1

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
            melhor_plano = None
            promoviveis = [c for c in cenarios if bool(c.get('promovivel'))]
            if promoviveis:
                promoviveis = sorted(promoviveis, key=lambda x: (tuple(x.get('vetor_lexicografico') or ()), -float(x.get('delta_patrimonio_proxy_vs_baseline') or 0.0)))
                melhor_plano = promoviveis[0]
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
            promoviveis = [c for c in cenarios if bool(c.get('promovivel'))]
            melhor_plano = None
            if promoviveis:
                promoviveis = sorted(promoviveis, key=lambda x: (tuple(x.get('vetor_lexicografico') or ()), -float(x.get('delta_patrimonio_proxy_vs_baseline') or 0.0)))
                melhor_plano = promoviveis[0]
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
        estado_corrente = deepcopy(vencedor.get('estado_pos_dia') or estado_corrente)
        _remover_pagamentos_ate_dia(estado_corrente, dia)

        pagamentos_resumo = []
        for pagamento in vencedor.get('resultados_pagamento') or []:
            item = deepcopy(dict(pagamento))
            pagamentos_executados.append(item)
            pagamentos_resumo.append({
                'pagamento_id': str(item.get('pagamento_id') or item.get('despesa_id') or ''),
                'descricao': str(item.get('descricao') or ''),
                'valor': round(float(item.get('valor_pagamento') or item.get('valor') or 0.0), 2),
                'fonte_principal_tipo': str(item.get('fonte_principal_tipo') or ''),
                'fonte_principal_id': str(item.get('fonte_principal_id') or ''),
                'cobertura_integral': bool(item.get('cobertura_integral')),
                'switching_aplicado_no_fluxo': bool(item.get('switching_aplicado_no_fluxo')),
                'rotulo_cenario_switching': str(item.get('rotulo_cenario_switching') or ''),
            })

        decisoes_diarias.append({
            'data': dia.isoformat(),
            'quantidade_pagamentos': len(pagamentos_dia),
            'quantidade_acoes_candidatas_switching': len(acoes_candidatas),
            'quantidade_cenarios_switching': len(cenarios),
            'familias_cenarios_switching': dict(Counter(str(c.get('familia') or '') for c in cenarios)),
            'quantidade_cenarios_promoviveis': sum(1 for c in cenarios if bool(c.get('promovivel'))),
            'pacote_vencedor': str(vencedor.get('tipo_pacote') or ''),
            'switching_executado': bool(vencedor.get('switching_executado')),
            'rotulo_switching': str(vencedor.get('rotulo_switching') or ''),
            'classe_switching': str(vencedor.get('classe_switching') or ''),
            'pagamentos': pagamentos_resumo,
        })
        dia += timedelta(days=1)

    resumo = {
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dias_no_horizonte': (data_fim - data_inicio).days + 1,
        'dias_com_pagamento': sum(1 for d in decisoes_diarias if int(d.get('quantidade_pagamentos') or 0) > 0),
        'dias_sem_pagamento': sum(1 for d in decisoes_diarias if int(d.get('quantidade_pagamentos') or 0) == 0),
        'dias_com_acoes_candidatas_switching': sum(1 for d in decisoes_diarias if int(d.get('quantidade_acoes_candidatas_switching') or 0) > 0),
        'dias_com_cenarios_promoviveis': sum(1 for d in decisoes_diarias if int(d.get('quantidade_cenarios_promoviveis') or 0) > 0),
        'dias_com_switching_executado': sum(1 for d in decisoes_diarias if bool(d.get('switching_executado'))),
        'pagamentos_no_horizonte': len(pagamentos_executados),
        'pagamentos_com_switching_no_fluxo': sum(1 for p in pagamentos_executados if bool(p.get('switching_aplicado_no_fluxo'))),
        'inconsistencias_temporais_no_estado': len(inconsistencias_temporais),
        'familias_cenarios_switching_avaliadas': dict(contagem_familias),
    }
    return {
        'status': 'ok',
        'versao': 'V175',
        'resumo': resumo,
        'decisoes_diarias': decisoes_diarias,
        'pagamentos_executados': pagamentos_executados,
        'inconsistencias_temporais': inconsistencias_temporais,
    }
