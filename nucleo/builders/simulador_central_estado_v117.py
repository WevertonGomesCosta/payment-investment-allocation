from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.calendario_financeiro import proximo_dia_util_bancario_em_ou_apos
from nucleo.recomputacao_sequencial_central_v1 import _perfil_pagamento_operacional
from nucleo.simulador_central_eventos_v1 import (
    _destinos_switch_elegiveis,
    _destinos_switch_elegiveis as _produtos_destino_elegiveis,
    _mapa_produtos_proxy,
    _proxy_fallback_lote,
    _top_destino_switch,
)


def construir_estado_global_recorte_curto_v117(
    contexto: Any,
    *,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
) -> dict[str, Any]:
    """Constrói o snapshot inicial do recorte curto do simulador central."""

    data_inicio = data_inicio or contexto.execucao.data_referencia
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=data_inicio)
    if limite_pagamentos > 0:
        pagamentos = pagamentos.head(limite_pagamentos).copy()
    if len(pagamentos) == 0:
        data_fim = data_fim or data_inicio
    else:
        data_limite_padrao = data_inicio + timedelta(days=30)
        data_fim = data_fim or min(max(pagamentos['data']), data_limite_padrao)
        pagamentos = pagamentos.loc[pagamentos['data'] <= data_fim].copy().reset_index(drop=True)

    mapa_produtos = _mapa_produtos_proxy(contexto)
    mapa_produtos_carteira = (getattr(getattr(contexto, 'carteira_canonica', None), 'mapa_produtos', None) or {}).get('by_key') or {}
    lotes: list[dict[str, Any]] = []
    for lote in contexto.replay_passado.lotes_apos_replay:
        if getattr(lote, 'esgotado', False):
            continue
        valor_liquido = round(float(lote.valor_liquido_em_data(
            data_inicio,
            contexto.calendario_financeiro,
            tabela_iof=contexto.tabela_iof,
            faixas_ir=contexto.faixas_ir,
            serie_cdi=contexto.cache_cdi.serie_cdi,
            data_base_referencia=contexto.execucao.data_referencia,
        ) or 0.0), 2)
        if valor_liquido <= 0.0:
            continue
        produto_key = str(getattr(lote, 'produto_key', '') or '').strip()
        produto = mapa_produtos.get(produto_key, {})
        produto_carteira = mapa_produtos_carteira.get(produto_key, {})
        data_aplicacao_lote = getattr(lote, 'data_aplicacao', None)
        prazo_dias_atual = int(produto_carteira.get('prazo_dias') or produto.get('prazo_dias') or 0)
        regime_liquidez_atual = str(produto_carteira.get('regime_liquidez') or produto.get('regime_liquidez') or '')
        data_vencimento = None
        if data_aplicacao_lote is not None and prazo_dias_atual > 0:
            data_vencimento_bruta = data_aplicacao_lote + timedelta(days=prazo_dias_atual)
            try:
                data_vencimento = proximo_dia_util_bancario_em_ou_apos(data_vencimento_bruta, contexto.calendario_financeiro)
            except Exception:
                data_vencimento = data_vencimento_bruta
        lotes.append({
            'id': str(lote.id),
            'investimento': str(lote.investimento),
            'produto_key': str(getattr(lote, 'produto_key', '') or ''),
            'prazo_dias_atual': prazo_dias_atual,
            'regime_liquidez_atual': regime_liquidez_atual,
            'data_vencimento': data_vencimento,
            'valor_inicial': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'principal_remanescente': round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2),
            'valor_liquido_resgatavel': valor_liquido,
            'carencia_ate': getattr(lote, 'carencia_ate', None),
            'data_aplicacao': getattr(lote, 'data_aplicacao', None),
            'data_recebimento': getattr(lote, 'data_recebimento', None),
            'taxa_base_cdi': float(getattr(lote, 'taxa_base_cdi', 0.0) or 0.0),
            'taxa_bonus_cdi': float(getattr(lote, 'taxa_bonus_cdi', 0.0) or 0.0),
            'proxy_terminal_atual': produto.get('proxy_terminal') if produto else _proxy_fallback_lote(lote, contexto),
            'proxy_score_atual': produto.get('score_final', 0.0),
            'retorno_anual_proxy_atual': float(produto.get('retorno_anual_proxy') or 0.0),
            'liquidez_dias_atual': int(produto.get('liquidez_dias') or 0),
            'carencia_dias_atual': int(produto.get('carencia_dias') or 0),
            'valor_terminal_estimado': valor_liquido,
            'produto_destino_key': None,
            'custo_fiscal_acumulado': 0.0,
        })

    recebidos_disponiveis: list[dict[str, Any]] = []
    recebidos_futuros: list[dict[str, Any]] = []
    inventario = contexto.dados_operacionais.inventario_canonico.copy()
    if len(inventario):
        mask = inventario['nao_aportado_disponivel'].fillna(False)
        for _, row in inventario.loc[mask].iterrows():
            valor_original = round(float(row.get('valor_original') or 0.0), 2)
            recebidos_disponiveis.append({
                'id': str(row.get('lote_id') or ''),
                'valor_disponivel': valor_original,
                'valor_recebido_original_v216': valor_original,
                'valor_pago_com_recebido_v216': 0.0,
                'valor_aportado_planejado_v216': 0.0,
                'saldo_caixa_remanescente_v216': valor_original,
                'proxy_terminal_atual': 0.0,
                'data_recebimento': row.get('data_recebimento'),
            })
        mask_fut = inventario.get('recebido_futuro_nao_disponivel', False)
        if hasattr(mask_fut, 'fillna'):
            mask_fut = mask_fut.fillna(False)
        for _, row in inventario.loc[mask_fut].iterrows():
            valor_original = round(float(row.get('valor_original') or 0.0), 2)
            recebidos_futuros.append({
                'id': str(row.get('lote_id') or ''),
                'valor_disponivel': valor_original,
                'valor_recebido_original_v216': valor_original,
                'valor_pago_com_recebido_v216': 0.0,
                'valor_aportado_planejado_v216': 0.0,
                'saldo_caixa_remanescente_v216': valor_original,
                'proxy_terminal_atual': 0.0,
                'data_recebimento': row.get('data_recebimento'),
            })

    pagamentos_norm: list[dict[str, Any]] = []
    for _, row in pagamentos.iterrows():
        perfil = _perfil_pagamento_operacional(str(row.get('descricao') or ''))
        pagamentos_norm.append({
            'pagamento_id': str(row.get('despesa_id') or ''),
            'despesa_id': str(row.get('despesa_id') or ''),
            'data': row.get('data'),
            'descricao': str(row.get('descricao') or ''),
            'valor': round(float(row.get('valor') or 0.0), 2),
            'classe_pagamento': perfil['classe'],
            'subclasse_pagamento': perfil['subclasse'],
            'prioridade_classe': perfil['prioridade_classe'],
            'prioridade_intraclasse': perfil['prioridade_intraclasse'],
        })

    return {
        'data_referencia': data_inicio,
        'data_evento_corrente': data_inicio,
        'data_fim_recorte': data_fim,
        'saldo_disponivel_geral': 0.0,
        'recebidos_nao_aportados_disponiveis': recebidos_disponiveis,
        'recebidos_nao_aportados_futuros': recebidos_futuros,
        'lotes_aportados': lotes,
        'pagamentos_futuros': pagamentos_norm,
        'produto_destino_padrao': _top_destino_switch(contexto),
        'produtos_destino_elegiveis': _destinos_switch_elegiveis(contexto, limite=12),
        'cdi_anual_modelo': float(getattr(contexto.calendario_financeiro, 'cdi_anual_modelo', 0.0) or 0.0),
        'metadados_recorte': {
            'limite_pagamentos': limite_pagamentos,
            'quantidade_pagamentos': len(pagamentos_norm),
            'quantidade_lotes': len(lotes),
            'quantidade_recebidos_nao_aportados': len(recebidos_disponiveis),
            'quantidade_recebidos_nao_aportados_futuros': len(recebidos_futuros),
            'aportes_planejados_v216_integracao': 'estado_inicial_preparado_com_campos_de_invariante',
        },
    }
