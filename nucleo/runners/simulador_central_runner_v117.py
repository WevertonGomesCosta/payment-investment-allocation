from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from nucleo.avaliador_cenarios_conjuntos_v1 import avaliar_cenarios_conjuntos_v1
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _coerce_date,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)


def rodar_integracao_funcional_minima_v117(
    *,
    raiz_repositorio: Path,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
) -> dict[str, Any]:
    """Executa o runner funcional mínimo do simulador central."""

    contexto = carregar_contexto_baseline(raiz_repositorio=raiz_repositorio, instalar_automaticamente=False)
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    config = contexto.pacote_config.conteudo
    horizonte = {
        'data_inicio': (data_inicio or contexto.execucao.data_referencia).isoformat(),
        'data_fim': (_coerce_date(estado.get('data_fim_recorte')) or (data_inicio or contexto.execucao.data_referencia)).isoformat(),
    }
    plano = planejar_switching_temporal_v1(
        estado_global=estado,
        config=config,
        horizonte_planejamento=horizonte,
        filtros_eventos=None,
        limite_candidatos_por_data=20,
    )
    acoes = [x for x in plano.get('acoes_candidatas', []) if x.get('tipo_acao') == 'switching_simples' and x.get('elegivel')]
    cenarios_brutos = [
        {
            'cenario_id': 'baseline_sem_switching',
            'descricao': 'Recorte curto sem switching temporal.',
            'eventos': [],
        }
    ]
    for idx, acao in enumerate(acoes[:2], start=1):
        cenarios_brutos.append({
            'cenario_id': f'switching_temporal_top{idx}',
            'descricao': f"Recorte curto com {acao.get('lote_origem_id')} -> {acao.get('produto_destino')} em {acao.get('data_acao')}",
            'eventos': [acao],
        })

    cenarios_avaliados: list[dict[str, Any]] = []
    simulacoes: dict[str, Any] = {}
    for cenario in cenarios_brutos:
        simulacao = simular_cenario_eventos_v1(
            estado_inicial=estado,
            eventos_candidatos=cenario['eventos'],
            config=config,
            horizonte=horizonte,
        )
        simulacoes[cenario['cenario_id']] = simulacao
        cenarios_avaliados.append({
            'cenario_id': cenario['cenario_id'],
            'descricao': cenario['descricao'],
            'status': simulacao.get('status'),
            'metrica_central': simulacao.get('metrica_central') or {},
            'patrimonio_liquido_terminal_proxy': simulacao.get('patrimonio_liquido_terminal_proxy'),
            'ganho_switching_total': simulacao.get('ganho_switching_total'),
        })

    avaliacao = avaliar_cenarios_conjuntos_v1(cenarios_avaliados, config=config)
    return {
        'status': 'integracao_integral_multidestino_v127',
        'implementado': True,
        'contexto_data_referencia': contexto.execucao.data_referencia.isoformat(),
        'horizonte': horizonte,
        'estado_global_recorte': estado,
        'plano_switching_temporal': plano,
        'simulacoes': simulacoes,
        'avaliacao_cenarios': avaliacao,
    }
