from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta

from nucleo.calendario_financeiro import proximo_dia_util_bancario_em_ou_apos
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import avaliar_cenarios_conjuntos_v1
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.recomputacao_sequencial_central_v1 import _perfil_pagamento_operacional
from nucleo.utilitarios_neutros import _aliquota_ir_estimada, _coerce_date, _normalizar_proxy_terminal
from nucleo.aportes_futuros_planejados import materializar_aportes_planejados_v216



def _destinos_switch_elegiveis(contexto: Any, limite: int = 12) -> list[dict[str, Any]]:
    ranking = getattr(contexto, 'ranking_carteira', None)
    quadro = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    if quadro is not None and len(quadro) > 0:
        destinos: list[dict[str, Any]] = []
        for posicao, (_, row) in enumerate(quadro.iterrows(), start=1):
            destinos.append({
                'rank_destino': int(row.get('rank_destino') or posicao),
                'produto_key': row.get('produto_key'),
                'nome': row.get('nome'),
                'score_final': float(row.get('score_final') or 0.0),
                'proxy_terminal_destino': _normalizar_proxy_terminal(row.get('proxy_terminal_destino') or row.get('score_final')),
                'retorno_anual_proxy': float(row.get('retorno_anual_proxy') or 0.0),
                'liquidez_dias': int(row.get('liquidez_dias') or 0),
                'carencia_dias': int(row.get('carencia_dias') or 0),
                'aplicacao_minima': float(row.get('aplicacao_minima') or 0.0),
                'aplicacao_maxima': float(row.get('aplicacao_maxima') or 0.0),
                'somente_combo': bool(row.get('somente_combo') or False),
                'tipo_produto': str(row.get('tipo_produto') or ''),
                'produto_base': str(row.get('produto_base') or ''),
                'produto_bonus': str(row.get('produto_bonus') or ''),
                'ratio_base': float(row.get('ratio_base') or 0.0),
                'ratio_bonus': float(row.get('ratio_bonus') or 0.0),
                'taxa_base_cdi': float(row.get('taxa_base_cdi') or 0.0),
                'taxa_bonus_cdi': float(row.get('taxa_bonus_cdi') or 0.0),
                'bucket_saof': row.get('Bucket_SAOF'),
                'score_final_prazo': float(row.get('SAOF_Final_Prazo') or row.get('score_final') or 0.0),
            })
            if len(destinos) >= max(int(limite or 0), 1):
                break
        return destinos

    triagem = contexto.triagem_motor.quadro_candidatos.copy()
    if len(triagem) == 0:
        return []
    if 'elegivel_switch_in' in triagem.columns:
        triagem = triagem.loc[triagem['elegivel_switch_in'].fillna(False)].copy()
    if len(triagem) == 0:
        return []
    cols_ordem = [col for col in ('score_final', 'retorno_anual_proxy') if col in triagem.columns]
    triagem = triagem.sort_values(cols_ordem, ascending=[False] * len(cols_ordem), kind='stable')
    destinos: list[dict[str, Any]] = []
    for posicao, (_, row) in enumerate(triagem.iterrows(), start=1):
        destinos.append({
            'rank_destino': posicao,
            'produto_key': row.get('produto_key'),
            'nome': row.get('nome'),
            'score_final': float(row.get('score_final') or 0.0),
            'proxy_terminal_destino': _normalizar_proxy_terminal(row.get('score_final')),
            'retorno_anual_proxy': float(row.get('retorno_anual_proxy') or 0.0),
            'liquidez_dias': int(row.get('liquidez_dias') or 0),
            'carencia_dias': int(row.get('carencia_dias') or 0),
            'taxa_base_cdi': float(row.get('taxa_base_cdi') or 0.0),
            'taxa_bonus_cdi': float(row.get('taxa_bonus_cdi') or 0.0),
        })
        if len(destinos) >= max(int(limite or 0), 1):
            break
    return destinos


def _top_destino_switch(contexto: Any) -> dict[str, Any]:
    destinos = _destinos_switch_elegiveis(contexto, limite=1)
    return destinos[0] if destinos else {}


def _mapa_produtos_proxy(contexto: Any) -> dict[str, dict[str, float]]:
    ranking = getattr(contexto, 'ranking_carteira', None)
    quadro = getattr(ranking, 'quadro_destinos_switch', None) if ranking is not None else None
    mapa: dict[str, dict[str, float]] = {}
    if quadro is not None and len(quadro) > 0 and 'produto_key' in quadro.columns:
        for _, row in quadro.iterrows():
            produto_key = str(row.get('produto_key') or '').strip()
            if not produto_key:
                continue
            mapa[produto_key] = {
                'score_final': float(row.get('score_final') or 0.0),
                'proxy_terminal': _normalizar_proxy_terminal(row.get('proxy_terminal_destino') or row.get('score_final')),
                'retorno_anual_proxy': float(row.get('retorno_anual_proxy') or 0.0),
                'nome': str(row.get('nome') or ''),
                'liquidez_dias': int(row.get('liquidez_dias') or 0),
                'carencia_dias': int(row.get('carencia_dias') or 0),
                'taxa_base_cdi': float(row.get('taxa_base_cdi') or 0.0),
                'taxa_bonus_cdi': float(row.get('taxa_bonus_cdi') or 0.0),
            }
    triagem = contexto.triagem_motor.quadro_candidatos.copy()
    if len(triagem) == 0 or 'produto_key' not in triagem.columns:
        return mapa
    for _, row in triagem.iterrows():
        produto_key = str(row.get('produto_key') or '').strip()
        if not produto_key or produto_key in mapa:
            continue
        mapa[produto_key] = {
            'score_final': float(row.get('score_final') or 0.0),
            'proxy_terminal': _normalizar_proxy_terminal(row.get('score_final')),
            'retorno_anual_proxy': float(row.get('retorno_anual_proxy') or 0.0),
            'nome': str(row.get('nome') or ''),
            'liquidez_dias': int(row.get('liquidez_dias') or 0),
            'carencia_dias': int(row.get('carencia_dias') or 0),
            'aplicacao_minima': float(row.get('aplicacao_minima') or 0.0),
            'aplicacao_maxima': float(row.get('aplicacao_maxima') or 0.0),
            'somente_combo': bool(row.get('somente_combo') or False),
            'tipo_produto': str(row.get('tipo_produto') or ''),
            'produto_base': str(row.get('produto_base') or ''),
            'produto_bonus': str(row.get('produto_bonus') or ''),
            'ratio_base': float(row.get('ratio_base') or 0.0),
            'ratio_bonus': float(row.get('ratio_bonus') or 0.0),
            'taxa_base_cdi': float(row.get('taxa_base_cdi') or 0.0),
            'taxa_bonus_cdi': float(row.get('taxa_bonus_cdi') or 0.0),
        }
    return mapa


def _proxy_fallback_lote(lote: Any, contexto: Any) -> float:
    taxa_ref = max(float(getattr(lote, 'taxa_bonus_cdi', 0.0) or 0.0), float(getattr(lote, 'taxa_base_cdi', 0.0) or 0.0))
    cdi = float(getattr(contexto.calendario_financeiro, 'cdi_anual_modelo', 0.0) or 0.0)
    return max(min(taxa_ref * cdi, 0.95), 0.05)



def _estimar_imposto_resgate(valor_liquido: float, principal: float, aliquota_ir: float) -> float:
    ganho_liquido = max(float(valor_liquido or 0.0) - float(principal or 0.0), 0.0)
    if ganho_liquido <= 0.0 or aliquota_ir <= 0.0 or aliquota_ir >= 1.0:
        return 0.0
    ganho_bruto = ganho_liquido / max(1.0 - aliquota_ir, 1e-9)
    imposto = ganho_bruto * aliquota_ir
    return round(max(imposto, 0.0), 2)


def _projetar_valor_terminal(valor_base: float, retorno_anual: float, dias: int) -> float:
    valor_base = float(valor_base or 0.0)
    retorno_anual = max(float(retorno_anual or 0.0), 0.0)
    dias = max(int(dias or 0), 0)
    if valor_base <= 0.0 or dias <= 0:
        return round(valor_base, 2)
    fator = (1.0 + retorno_anual / 100.0) ** (dias / 365.0)
    return round(valor_base * fator, 2)


def _valor_terminal_estimado_lote(lote: dict[str, Any], data_final: date | None, data_base: date | None) -> float:
    valor_liquido = float(lote.get('valor_liquido_resgatavel') or 0.0)
    retorno = float(lote.get('retorno_anual_proxy_atual') or 0.0)
    valor_terminal_registrado = float(lote.get('valor_terminal_estimado') or 0.0)
    data_final_registrada = _coerce_date(lote.get('data_final_valor_terminal_estimado'))
    valor_base_registrado = float(lote.get('valor_liquido_base_terminal_estimado') or 0.0)
    origem_switching = bool(lote.get('origem_switching_evento'))
    if origem_switching and valor_terminal_registrado > 0.0 and data_final is not None and data_final_registrada == data_final:
        if valor_base_registrado > 0.0:
            proporcao = max(min(valor_liquido / valor_base_registrado, 1.0), 0.0)
            valor_ajustado = round(valor_terminal_registrado * proporcao, 2)
        else:
            valor_ajustado = round(valor_terminal_registrado, 2)
        return round(max(valor_liquido, valor_ajustado), 2)
    if data_final is None or data_base is None:
        return round(valor_liquido, 2)
    dias = max((data_final - data_base).days, 0)
    return _projetar_valor_terminal(valor_liquido, retorno, dias)


def construir_estado_global_recorte_curto_v117(
    contexto: Any,
    *,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
) -> dict[str, Any]:
    from nucleo.builders.simulador_central_estado_v117 import (
        construir_estado_global_recorte_curto_v117 as _builder_impl,
    )

    return _builder_impl(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )


def _politica_pos_vencimento(config: dict[str, Any] | None) -> dict[str, Any]:
    politicas = dict((config or {}).get('politicas') or {})
    return dict(politicas.get('pos_vencimento') or {})


def _normalizar_lote_pos_vencimento_no_dia(
    estado: dict[str, Any],
    data_atual: date,
    config: dict[str, Any] | None,
    historico: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    politica = _politica_pos_vencimento(config)
    if str(politica.get('acao') or '') != 'disponivel_para_resgate':
        return []
    if str(politica.get('rendimento') or '') != 'parar':
        return []

    convertidos: list[dict[str, Any]] = []
    lotes_remanescentes: list[dict[str, Any]] = []
    disponiveis = estado.setdefault('recebidos_nao_aportados_disponiveis', [])
    ids_disponiveis = {str(item.get('id') or item.get('fonte_id') or '') for item in disponiveis}
    for lote in list(estado.get('lotes_aportados') or []):
        data_vencimento = _coerce_date(lote.get('data_vencimento'))
        prazo_dias = int(lote.get('prazo_dias_atual') or 0)
        liquidez_dias = int(lote.get('liquidez_dias_atual') or 0)
        regime_liquidez = str(lote.get('regime_liquidez_atual') or '')
        lote_id = str(lote.get('id') or '')
        vencido = (
            data_vencimento is not None
            and prazo_dias > 0
            and data_vencimento <= data_atual
            and (regime_liquidez == 'vencimento' or liquidez_dias <= 0)
        )
        if not vencido:
            lotes_remanescentes.append(lote)
            continue

        valor_liquido = round(float(lote.get('valor_liquido_resgatavel') or 0.0), 2)
        if valor_liquido > 0.0 and lote_id not in ids_disponiveis:
            recebido = {
                'id': lote_id,
                'valor_disponivel': valor_liquido,
                'proxy_terminal_atual': 0.0,
                'data_recebimento': data_atual,
                'origem_pos_vencimento': True,
                'produto_origem': str(lote.get('investimento') or ''),
                'data_vencimento_origem': data_vencimento,
            }
            disponiveis.append(recebido)
            ids_disponiveis.add(lote_id)
            convertidos.append(recebido)
            if historico is not None:
                historico.append({
                    'tipo_evento': 'normalizacao_pos_vencimento',
                    'data_evento': data_atual.isoformat(),
                    'lote_id': lote_id,
                    'produto_origem': str(lote.get('investimento') or ''),
                    'valor_disponivel': valor_liquido,
                    'data_vencimento': data_vencimento.isoformat() if data_vencimento else None,
                })

    estado['lotes_aportados'] = lotes_remanescentes
    return convertidos


def _ativar_recebidos_futuros_no_dia(estado: dict[str, Any], data_atual: date, historico: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    ativados: list[dict[str, Any]] = []
    futuros = list(estado.get('recebidos_nao_aportados_futuros') or [])
    remanescentes: list[dict[str, Any]] = []
    disponiveis = estado.setdefault('recebidos_nao_aportados_disponiveis', [])
    ids_disponiveis = {str(item.get('id') or item.get('fonte_id') or '') for item in disponiveis}
    for recebido in futuros:
        data_recebimento = _coerce_date(recebido.get('data_recebimento'))
        recebido_id = str(recebido.get('id') or recebido.get('fonte_id') or '')
        if data_recebimento is not None and data_recebimento <= data_atual:
            if recebido_id not in ids_disponiveis:
                novo = deepcopy(recebido)
                novo['ativado_em'] = data_atual
                valor_original = round(float(novo.get('valor_recebido_original_v216') or novo.get('valor_original') or novo.get('valor_disponivel') or novo.get('valor') or 0.0), 2)
                novo['valor_recebido_original_v216'] = valor_original
                novo.setdefault('valor_pago_com_recebido_v216', 0.0)
                novo.setdefault('valor_aportado_planejado_v216', 0.0)
                novo.setdefault('saldo_caixa_remanescente_v216', round(float(novo.get('valor_disponivel') or novo.get('valor') or valor_original or 0.0), 2))
                disponiveis.append(novo)
                ids_disponiveis.add(recebido_id)
                ativados.append(novo)
                if historico is not None:
                    historico.append({
                        'tipo_evento': 'ativacao_nao_aportado_futuro',
                        'data_evento': data_atual.isoformat(),
                        'lote_id': recebido_id,
                        'valor_disponivel': round(float(novo.get('valor_disponivel') or novo.get('valor') or 0.0), 2),
                        'data_recebimento': data_recebimento.isoformat(),
                    })
            continue
        remanescentes.append(recebido)
    estado['recebidos_nao_aportados_futuros'] = remanescentes
    return ativados


def _preparar_evento_executavel_no_dia(estado: dict[str, Any], evento: dict[str, Any], data_atual: date) -> dict[str, Any] | None:
    data_acao = _coerce_date(evento.get('data_acao'))
    if not evento.get('elegivel') or data_acao is None or data_acao != data_atual:
        return None
    tipo_acao = str(evento.get('tipo_acao') or '')
    if tipo_acao not in {'switching_simples', 'aporte_nao_aportado'}:
        return None
    lote_id = str(evento.get('lote_origem_id') or '')
    if tipo_acao == 'aporte_nao_aportado':
        recebido = None
        for item in list(estado.get('recebidos_nao_aportados_disponiveis', [])):
            if str(item.get('id') or item.get('fonte_id') or '') == lote_id:
                recebido = item
                break
        if recebido is None:
            return None
        return {'tipo_acao': tipo_acao, 'lote_id': lote_id, 'recebido': recebido, 'lote': None, 'evento': evento}
    lote = None
    for item in list(estado.get('lotes_aportados', [])):
        if str(item.get('id') or '') == lote_id:
            lote = item
            break
    if lote is None:
        return None
    return {'tipo_acao': tipo_acao, 'lote_id': lote_id, 'recebido': None, 'lote': lote, 'evento': evento}


def _registrar_historico_evento(historico: list[dict[str, Any]], payload: dict[str, Any]) -> None:
    historico.append(payload)


def _registrar_execucao_evento(executados: list[dict[str, Any]], evento: dict[str, Any], payload: dict[str, Any]) -> None:
    executados.append({**evento, **payload})


def _acumular_resultados_execucao(ganho_total: float, perda_liquidez: float, custo_fiscal_total: float, ganho_evento: float, perda_evento: float, custo_fiscal: float) -> tuple[float, float, float]:
    return (
        ganho_total + ganho_evento,
        perda_liquidez + perda_evento,
        custo_fiscal_total + custo_fiscal,
    )


def _registrar_pos_execucao_evento_switching(
    historico: list[dict[str, Any]],
    executados: list[dict[str, Any]],
    evento: dict[str, Any],
    *,
    tipo_evento: str,
    data_atual: date,
    lote_id: str,
    produto_origem: str,
    produto_destino: str,
    fracao_lote: float,
    valor_liquido_origem: float,
    valor_migrado: float,
    custo_fiscal: float,
    liquidez_destino: int,
    carencia_destino: int,
    valor_terminal_estimado: float,
    ganho_evento: float,
    ganho_total: float,
    perda_liquidez: float,
    custo_fiscal_total: float,
    perda_evento: float,
) -> tuple[float, float, float]:
    _registrar_historico_evento(historico, {
        'tipo_evento': tipo_evento,
        'data_evento': data_atual.isoformat(),
        'lote_id': lote_id,
        'produto_origem': produto_origem,
        'produto_destino': produto_destino,
        'fracao_lote': fracao_lote,
        'valor_liquido_origem': valor_liquido_origem,
        'valor_migrado': valor_migrado,
        'custo_fiscal_realizado': custo_fiscal,
        'liquidez_dias_destino': liquidez_destino,
        'carencia_dias_destino': carencia_destino,
        'valor_terminal_estimado': valor_terminal_estimado,
        'ganho_terminal_proxy_estimado': ganho_evento,
    })
    _registrar_execucao_evento(executados, evento, {
        'fracao_lote': fracao_lote,
        'custo_fiscal_realizado': custo_fiscal,
        'valor_migrado_realizado': valor_migrado,
        'valor_terminal_estimado': valor_terminal_estimado,
    })
    return _acumular_resultados_execucao(
        ganho_total,
        perda_liquidez,
        custo_fiscal_total,
        ganho_evento,
        perda_evento,
        custo_fiscal,
    )


def _construir_campos_comuns_destino_evento_switching(
    lote_base: dict[str, Any],
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_destino: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
    custo_fiscal_incremental: float,
    *,
    origem_tipo_evento: str,
) -> dict[str, Any]:
    return {
        'investimento': str(evento.get('produto_destino') or lote_base.get('investimento') or ''),
        'produto_key': str(evento.get('produto_destino_key') or lote_base.get('produto_key') or ''),
        'produto_destino_key': str(evento.get('produto_destino_key') or lote_base.get('produto_destino_key') or ''),
        'valor_liquido_resgatavel': valor_destino,
        'principal_remanescente': valor_destino,
        'proxy_terminal_atual': float(evento.get('proxy_terminal_destino') or lote_base.get('proxy_terminal_atual') or 0.0),
        'retorno_anual_proxy_atual': retorno_destino,
        'liquidez_dias_atual': liquidez_destino,
        'carencia_dias_atual': carencia_destino,
        'liquidez_ate': data_atual + timedelta(days=liquidez_destino) if liquidez_destino > 0 else None,
        'carencia_ate': data_atual + timedelta(days=carencia_destino) if carencia_destino > 0 else None,
        'data_aplicacao': data_atual,
        'custo_fiscal_acumulado': round(float(lote_base.get('custo_fiscal_acumulado') or 0.0) + custo_fiscal_incremental, 2),
        'valor_terminal_estimado': valor_terminal_estimado,
        'data_base_valor_terminal_estimado': data_base_terminal,
        'data_final_valor_terminal_estimado': data_final,
        'valor_liquido_base_terminal_estimado': valor_destino,
        'origem_switching_evento': True,
        'origem_tipo_evento': origem_tipo_evento,
    }


def _construir_payload_mutacao_switching_integral(
    lote: dict[str, Any],
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_migrado: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
    custo_fiscal: float,
) -> dict[str, Any]:
    return _construir_campos_comuns_destino_evento_switching(
        lote,
        evento,
        data_atual,
        data_final,
        data_base_terminal,
        valor_migrado,
        valor_terminal_estimado,
        retorno_destino,
        liquidez_destino,
        carencia_destino,
        custo_fiscal,
        origem_tipo_evento='switching_integral',
    )




def _construir_lote_destino_aporte_nao_aportado(
    lote_id: str,
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_disponivel: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
) -> dict[str, Any]:
    return {
        'id': f"{lote_id}_ap_{data_atual.isoformat()}",
        'investimento': str(evento.get('produto_destino') or ''),
        'produto_key': str(evento.get('produto_destino_key') or ''),
        'produto_destino_key': str(evento.get('produto_destino_key') or ''),
        'valor_inicial': valor_disponivel,
        'valor_liquido_resgatavel': valor_disponivel,
        'principal_remanescente': valor_disponivel,
        'proxy_terminal_atual': float(evento.get('proxy_terminal_destino') or 0.0),
        'retorno_anual_proxy_atual': retorno_destino,
        'liquidez_dias_atual': liquidez_destino,
        'carencia_dias_atual': carencia_destino,
        'carencia_ate': data_atual + timedelta(days=carencia_destino) if carencia_destino > 0 else None,
        'data_aplicacao': data_atual,
        'data_recebimento': data_atual,
        'taxa_base_cdi': 0.0,
        'taxa_bonus_cdi': 0.0,
        'valor_terminal_estimado': valor_terminal_estimado,
        'data_base_valor_terminal_estimado': data_base_terminal,
        'data_final_valor_terminal_estimado': data_final,
        'valor_liquido_base_terminal_estimado': valor_disponivel,
        'origem_switching_evento': True,
        'origem_tipo_evento': 'aporte_nao_aportado',
        'custo_fiscal_acumulado': 0.0,
    }



def _aplicar_aporte_nao_aportado_no_estado(
    estado: dict[str, Any],
    recebido: dict[str, Any],
    lote_id: str,
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_disponivel: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
) -> None:
    recebido['valor_disponivel'] = 0.0
    novo_lote = _construir_lote_destino_aporte_nao_aportado(
        lote_id,
        evento,
        data_atual,
        data_final,
        data_base_terminal,
        valor_disponivel,
        valor_terminal_estimado,
        retorno_destino,
        liquidez_destino,
        carencia_destino,
    )
    estado.setdefault('lotes_aportados', []).append(novo_lote)


def _aplicar_switching_integral_no_lote(
    lote: dict[str, Any],
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_migrado: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
    custo_fiscal: float,
) -> None:
    payload_mutacao = _construir_payload_mutacao_switching_integral(
        lote,
        evento,
        data_atual,
        data_final,
        data_base_terminal,
        valor_migrado,
        valor_terminal_estimado,
        retorno_destino,
        liquidez_destino,
        carencia_destino,
        custo_fiscal,
    )
    lote.update(payload_mutacao)




def _construir_payload_mutacao_origem_switching_parcial(
    lote: dict[str, Any],
    data_final: date | None,
    data_base_terminal: date,
    valor_liquido_total: float,
    valor_liquido_origem: float,
    principal_total: float,
    principal: float,
) -> dict[str, Any]:
    valor_residual = round(max(valor_liquido_total - valor_liquido_origem, 0.0), 2)
    principal_residual = round(max(principal_total - principal, 0.0), 2)
    lote_residual = deepcopy(lote)
    lote_residual['valor_liquido_resgatavel'] = valor_residual
    lote_residual['principal_remanescente'] = principal_residual
    return {
        'valor_liquido_resgatavel': valor_residual,
        'principal_remanescente': principal_residual,
        'valor_terminal_estimado': _valor_terminal_estimado_lote(lote_residual, data_final, data_base_terminal),
    }


def _aplicar_mutacao_origem_switching_parcial(
    lote: dict[str, Any],
    data_final: date | None,
    data_base_terminal: date,
    valor_liquido_total: float,
    valor_liquido_origem: float,
    principal_total: float,
    principal: float,
) -> None:
    lote.update(_construir_payload_mutacao_origem_switching_parcial(
        lote,
        data_final,
        data_base_terminal,
        valor_liquido_total,
        valor_liquido_origem,
        principal_total,
        principal,
    ))

def _aplicar_switching_parcial_no_lote(
    estado: dict[str, Any],
    lote: dict[str, Any],
    lote_id: str,
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    valor_liquido_total: float,
    valor_liquido_origem: float,
    principal_total: float,
    principal: float,
    valor_migrado: float,
    valor_terminal_estimado: float,
    retorno_destino: float,
    liquidez_destino: int,
    carencia_destino: int,
    custo_fiscal: float,
) -> None:
    _aplicar_mutacao_origem_switching_parcial(
        lote,
        data_final,
        data_base_terminal,
        valor_liquido_total,
        valor_liquido_origem,
        principal_total,
        principal,
    )
    novo_lote = deepcopy(lote)
    novo_lote['id'] = f"{lote_id}_sw_{data_atual.isoformat()}_{int(float(evento.get('fracao_lote') or 1.0) * 100)}"
    novo_lote['valor_inicial'] = valor_migrado
    novo_lote.update(_construir_campos_comuns_destino_evento_switching(
        lote,
        evento,
        data_atual,
        data_final,
        data_base_terminal,
        valor_migrado,
        valor_terminal_estimado,
        retorno_destino,
        liquidez_destino,
        carencia_destino,
        custo_fiscal,
        origem_tipo_evento='switching_parcial',
    ))
    estado.setdefault('lotes_aportados', []).append(novo_lote)



def _aplicar_efeito_evento_switching(
    estado: dict[str, Any],
    evento_preparado: dict[str, Any],
    evento: dict[str, Any],
    data_atual: date,
    data_final: date | None,
    data_base_terminal: date,
    *,
    fracao_lote: float = 1.0,
    valor_disponivel: float = 0.0,
    valor_liquido_total: float = 0.0,
    valor_liquido_origem: float = 0.0,
    principal_total: float = 0.0,
    principal: float = 0.0,
    valor_migrado: float = 0.0,
    valor_terminal_estimado: float = 0.0,
    retorno_destino: float = 0.0,
    liquidez_destino: int = 0,
    carencia_destino: int = 0,
    custo_fiscal: float = 0.0,
) -> None:
    tipo_acao = str(evento_preparado.get('tipo_acao') or '')
    lote_id = str(evento_preparado.get('lote_id') or '')

    if tipo_acao == 'aporte_nao_aportado':
        recebido = evento_preparado.get('recebido')
        if recebido is None or valor_disponivel <= 0.0:
            return
        _aplicar_aporte_nao_aportado_no_estado(
            estado,
            recebido,
            lote_id,
            evento,
            data_atual,
            data_final,
            data_base_terminal,
            valor_disponivel,
            valor_terminal_estimado,
            retorno_destino,
            liquidez_destino,
            carencia_destino,
        )
        return

    lote = evento_preparado.get('lote')
    if lote is None:
        return
    if fracao_lote >= 0.999999:
        _aplicar_switching_integral_no_lote(
            lote,
            evento,
            data_atual,
            data_final,
            data_base_terminal,
            valor_migrado,
            valor_terminal_estimado,
            retorno_destino,
            liquidez_destino,
            carencia_destino,
            custo_fiscal,
        )
        return
    _aplicar_switching_parcial_no_lote(
        estado,
        lote,
        lote_id,
        evento,
        data_atual,
        data_final,
        data_base_terminal,
        valor_liquido_total,
        valor_liquido_origem,
        principal_total,
        principal,
        valor_migrado,
        valor_terminal_estimado,
        retorno_destino,
        liquidez_destino,
        carencia_destino,
        custo_fiscal,
    )


def _aplicar_switching_eventos(estado: dict[str, Any], eventos: list[dict[str, Any]], data_atual: date, historico: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float, float, float]:
    executados: list[dict[str, Any]] = []
    ganho_total = 0.0
    perda_liquidez = 0.0
    custo_fiscal_total = 0.0
    data_final = _coerce_date(estado.get('data_fim_recorte'))
    for evento in eventos:
        evento_preparado = _preparar_evento_executavel_no_dia(estado, evento, data_atual)
        if evento_preparado is None:
            continue
        tipo_acao = str(evento_preparado.get('tipo_acao') or '')
        lote_id = str(evento_preparado.get('lote_id') or '')
        if tipo_acao == 'aporte_nao_aportado':
            recebido = evento_preparado.get('recebido')
            if recebido is None:
                continue
            valor_disponivel = round(float(recebido.get('valor_disponivel') or recebido.get('valor') or 0.0), 2)
            if valor_disponivel <= 0.0:
                continue
            produto_destino = str(evento.get('produto_destino') or '')
            retorno_destino = float(evento.get('retorno_anual_destino') or 0.0)
            liquidez_destino = int(evento.get('liquidez_dias_destino') or 0)
            carencia_destino = int(evento.get('carencia_dias_destino') or 0)
            data_base_terminal = max(data_atual, _coerce_date(estado.get('data_evento_corrente')) or data_atual)
            valor_terminal_estimado = _valor_terminal_estimado_lote(
                {'valor_liquido_resgatavel': valor_disponivel, 'retorno_anual_proxy_atual': retorno_destino},
                data_final,
                data_base_terminal,
            )
            _aplicar_efeito_evento_switching(
                estado,
                evento_preparado,
                evento,
                data_atual,
                data_final,
                data_base_terminal,
                valor_disponivel=valor_disponivel,
                valor_terminal_estimado=valor_terminal_estimado,
                retorno_destino=retorno_destino,
                liquidez_destino=liquidez_destino,
                carencia_destino=carencia_destino,
            )
            ganho_evento = round(float(evento.get('ganho_terminal_proxy_estimado') or 0.0), 2)
            perda_evento = round(float(evento.get('perda_liquidez_estimada') or 0.0), 2)
            ganho_total, perda_liquidez, custo_fiscal_total = _registrar_pos_execucao_evento_switching(
                historico,
                executados,
                evento,
                tipo_evento='aporte_nao_aportado',
                data_atual=data_atual,
                lote_id=lote_id,
                produto_origem='NAO_APORTADO_DISPONIVEL',
                produto_destino=produto_destino,
                fracao_lote=1.0,
                valor_liquido_origem=valor_disponivel,
                valor_migrado=valor_disponivel,
                custo_fiscal=0.0,
                liquidez_destino=liquidez_destino,
                carencia_destino=carencia_destino,
                valor_terminal_estimado=valor_terminal_estimado,
                ganho_evento=ganho_evento,
                ganho_total=ganho_total,
                perda_liquidez=perda_liquidez,
                custo_fiscal_total=custo_fiscal_total,
                perda_evento=perda_evento,
            )
            continue
        lote = evento_preparado.get('lote')
        if lote is None:
            continue
        valor_liquido_total = round(float(lote.get('valor_liquido_resgatavel') or 0.0), 2)
        principal_total = round(float(lote.get('principal_remanescente') or 0.0), 2)
        if valor_liquido_total <= 0.0:
            continue
        fracao_lote = float(evento.get('fracao_lote') or 1.0)
        fracao_lote = min(max(fracao_lote, 0.0), 1.0)
        if fracao_lote <= 0.0:
            continue
        valor_liquido_origem = round(valor_liquido_total * fracao_lote, 2)
        principal = round(principal_total * fracao_lote, 2)
        aliquota = _aliquota_ir_estimada(_coerce_date(lote.get('data_aplicacao')), data_atual)
        custo_fiscal_estimado = float(evento.get('custo_fiscal_estimado') or 0.0)
        if fracao_lote < 0.999999:
            custo_fiscal = round(_estimar_imposto_resgate(valor_liquido_origem, principal, aliquota), 2)
        else:
            custo_fiscal = round(custo_fiscal_estimado or _estimar_imposto_resgate(valor_liquido_origem, principal, aliquota), 2)
        valor_migrado_estimado = float(evento.get('valor_migrado_estimado') or 0.0)
        if fracao_lote < 0.999999:
            valor_migrado = round(max(valor_liquido_origem - custo_fiscal, 0.0), 2)
        else:
            valor_migrado = round(max(valor_migrado_estimado, valor_liquido_origem - custo_fiscal), 2)
        produto_origem = str(lote.get('investimento') or evento.get('produto_origem') or '')
        produto_destino = str(evento.get('produto_destino') or lote.get('investimento') or '')
        retorno_destino = float(evento.get('retorno_anual_destino') or lote.get('retorno_anual_proxy_atual') or 0.0)
        liquidez_destino = int(evento.get('liquidez_dias_destino') or 0)
        carencia_destino = int(evento.get('carencia_dias_destino') or 0)
        data_base_terminal = max(data_atual, _coerce_date(estado.get('data_evento_corrente')) or data_atual)
        valor_terminal_estimado = _valor_terminal_estimado_lote(
            {'valor_liquido_resgatavel': valor_migrado, 'retorno_anual_proxy_atual': retorno_destino},
            data_final,
            data_base_terminal,
        )
        ganho_evento = round(float(evento.get('ganho_terminal_proxy_estimado') or 0.0) * fracao_lote, 2)
        perda_evento = round(float(evento.get('perda_liquidez_estimada') or 0.0) * fracao_lote, 2)
        _aplicar_efeito_evento_switching(
            estado,
            evento_preparado,
            evento,
            data_atual,
            data_final,
            data_base_terminal,
            fracao_lote=fracao_lote,
            valor_liquido_total=valor_liquido_total,
            valor_liquido_origem=valor_liquido_origem,
            principal_total=principal_total,
            principal=principal,
            valor_migrado=valor_migrado,
            valor_terminal_estimado=valor_terminal_estimado,
            retorno_destino=retorno_destino,
            liquidez_destino=liquidez_destino,
            carencia_destino=carencia_destino,
            custo_fiscal=custo_fiscal,
        )
        ganho_total, perda_liquidez, custo_fiscal_total = _registrar_pos_execucao_evento_switching(
            historico,
            executados,
            evento,
            tipo_evento='switching',
            data_atual=data_atual,
            lote_id=lote_id,
            produto_origem=produto_origem,
            produto_destino=produto_destino,
            fracao_lote=fracao_lote,
            valor_liquido_origem=valor_liquido_origem,
            valor_migrado=valor_migrado,
            custo_fiscal=custo_fiscal,
            liquidez_destino=liquidez_destino,
            carencia_destino=carencia_destino,
            valor_terminal_estimado=valor_terminal_estimado,
            ganho_evento=ganho_evento,
            ganho_total=ganho_total,
            perda_liquidez=perda_liquidez,
            custo_fiscal_total=custo_fiscal_total,
            perda_evento=perda_evento,
        )
    return executados, round(ganho_total, 2), round(perda_liquidez, 2), round(custo_fiscal_total, 2)


def _consumir_componentes(estado: dict[str, Any], componentes: list[dict[str, Any]]) -> None:
    for item in componentes:
        valor = round(float(item.get('valor_utilizado') or 0.0), 2)
        if valor <= 0.0:
            continue
        tipo = str(item.get('tipo_fonte') or '')
        fonte_id = str(item.get('fonte_id') or '')
        if tipo == 'saldo_disponivel':
            estado['saldo_disponivel_geral'] = round(max(float(estado.get('saldo_disponivel_geral') or 0.0) - valor, 0.0), 2)
            continue
        if tipo == 'lote_nao_aportado':
            for recebido in estado.get('recebidos_nao_aportados_disponiveis', []):
                if str(recebido.get('id') or recebido.get('fonte_id') or '') != fonte_id:
                    continue
                chave = 'valor_disponivel' if 'valor_disponivel' in recebido else 'valor'
                recebido[chave] = round(max(float(recebido.get(chave) or 0.0) - valor, 0.0), 2)
                recebido['valor_pago_com_recebido_v216'] = round(float(recebido.get('valor_pago_com_recebido_v216') or 0.0) + valor, 2)
                recebido['saldo_caixa_remanescente_v216'] = round(float(recebido.get(chave) or 0.0), 2)
                break
            continue
        if tipo == 'lote_aportado':
            for lote in estado.get('lotes_aportados', []):
                if str(lote.get('id') or lote.get('fonte_id') or '') != fonte_id:
                    continue
                lote['valor_liquido_resgatavel'] = round(max(float(lote.get('valor_liquido_resgatavel') or 0.0) - valor, 0.0), 2)
                lote['principal_remanescente'] = round(max(float(lote.get('principal_remanescente') or 0.0) - valor, 0.0), 2)
                break


def _calcular_metrica(resultados_pagamento: list[dict[str, Any]], *, ganho_switching: float, perda_liquidez_switching: float, custo_fiscal_switching: float, eventos_executados: list[dict[str, Any]]) -> dict[str, Any]:
    violacoes_protegida = 0
    deficit_total = 0.0
    pagamentos_sem_cobertura = 0
    perda_terminal = 0.0
    destruicao_estrategica = 0.0
    deterioracao_liquidez = 0.0
    custo_fiscal = float(custo_fiscal_switching or 0.0)
    custo_operacional = float(len(eventos_executados))

    for row in resultados_pagamento:
        deficit = float(row.get('valor_deficit') or 0.0)
        if deficit > 0.0:
            pagamentos_sem_cobertura += 1
        if str(row.get('classe_pagamento') or '') == 'PROTEGIDA' and deficit > 0.0:
            violacoes_protegida += 1
        deficit_total += deficit
        perda_terminal += float(row.get('perda_retorno_terminal_estimada') or 0.0)
        destruicao_estrategica += float(row.get('penalidade_estrategica_lote') or 0.0)
        deterioracao_liquidez += float(row.get('penalidade_liquidez_futura') or 0.0)
        custo_fiscal += float(row.get('custo_fiscal_imediato') or 0.0)
        if str(row.get('fonte_principal_tipo') or '') == 'combinacao_minima_fontes':
            custo_operacional += 1.0

    perda_terminal = max(perda_terminal - ganho_switching, 0.0)
    deterioracao_liquidez += perda_liquidez_switching
    return {
        'violacoes_protegida': float(violacoes_protegida),
        'deficit_liquido_total': round(deficit_total, 2),
        'pagamentos_sem_cobertura_integral': float(pagamentos_sem_cobertura),
        'perda_patrimonio_liquido_terminal': round(perda_terminal, 2),
        'destruicao_estrategica_lotes': round(destruicao_estrategica, 2),
        'deterioracao_liquidez_futura': round(deterioracao_liquidez, 2),
        'custo_fiscal_imediato': round(custo_fiscal, 2),
        'custo_operacional': round(custo_operacional, 2),
    }


def _patrimonio_terminal_proxy(estado: dict[str, Any], metrica: dict[str, Any], ganho_switching: float) -> float:
    saldo = float(estado.get('saldo_disponivel_geral') or 0.0)
    recebidos = sum(float(x.get('valor_disponivel') or x.get('valor') or 0.0) for x in estado.get('recebidos_nao_aportados_disponiveis', []))
    data_final = _coerce_date(estado.get('data_fim_recorte'))
    data_corrente = _coerce_date(estado.get('data_evento_corrente')) or _coerce_date(estado.get('data_referencia'))
    lotes = sum(_valor_terminal_estimado_lote(x, data_final, data_corrente) for x in estado.get('lotes_aportados', []))
    base = saldo + recebidos + lotes + float(ganho_switching or 0.0)
    perda = float(metrica.get('perda_patrimonio_liquido_terminal') or 0.0)
    return round(base - perda, 2)


def simular_cenario_eventos_v1(
    estado_inicial: dict[str, Any] | None,
    eventos_candidatos: list[dict[str, Any]] | None,
    config: dict[str, Any] | None,
    horizonte: Any = None,
) -> dict[str, Any]:
    """Executa a integração temporal multidestino da V121.

    O simulador ainda não substitui o motor econômico final, mas agora integra:
    - switching temporal autônomo por data;
    - alocação terminal de fontes por pagamento;
    - vetor central auditável por cenário no recorte curto.
    """

    estado = deepcopy(dict(estado_inicial or {}))
    eventos = [deepcopy(dict(item)) for item in (eventos_candidatos or [])]
    pagamentos = sorted(
        [deepcopy(dict(item)) for item in estado.get('pagamentos_futuros', [])],
        key=lambda item: (
            _coerce_date(item.get('data')) or date.max,
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )

    historico: list[dict[str, Any]] = []
    resultados_pagamento: list[dict[str, Any]] = []
    pagamentos_cobertos: list[str] = []
    pagamentos_sem_cobertura: list[str] = []
    eventos_executados: list[dict[str, Any]] = []
    ganho_switching_total = 0.0
    perda_liquidez_switching_total = 0.0
    custo_fiscal_switching_total = 0.0

    datas_eventos = {
        _coerce_date(item.get('data_acao'))
        for item in eventos if _coerce_date(item.get('data_acao')) is not None
    }
    datas_pagamentos = {_coerce_date(item.get('data')) for item in pagamentos if _coerce_date(item.get('data')) is not None}
    datas_recebidos_futuros = {
        _coerce_date(item.get('data_recebimento'))
        for item in (estado.get('recebidos_nao_aportados_futuros') or [])
        if _coerce_date(item.get('data_recebimento')) is not None
    }
    agenda = sorted([d for d in (datas_eventos | datas_pagamentos | datas_recebidos_futuros) if d is not None])

    for data_atual in agenda:
        estado['data_evento_corrente'] = data_atual
        _normalizar_lote_pos_vencimento_no_dia(estado, data_atual, config, historico)
        _ativar_recebidos_futuros_no_dia(estado, data_atual, historico)
        novos_eventos, ganho_switch, perda_liq, custo_fiscal_switch = _aplicar_switching_eventos(estado, eventos, data_atual, historico)
        eventos_executados.extend(novos_eventos)
        ganho_switching_total += ganho_switch
        perda_liquidez_switching_total += perda_liq
        custo_fiscal_switching_total += custo_fiscal_switch

        pagamentos_data = [item for item in pagamentos if _coerce_date(item.get('data')) == data_atual]
        for pagamento in pagamentos_data:
            estado_para_pagamento = deepcopy(estado)
            estado_para_pagamento['dias_horizonte_terminal'] = max(((_coerce_date(estado.get('data_fim_recorte')) or data_atual) - data_atual).days, 0)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_pagamento,
                config=config,
                plano_switching_candidato={'eventos_executados': eventos_executados} if eventos_executados else None,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            resultados_pagamento.append(alocacao)
            historico.append({
                'tipo_evento': 'pagamento',
                'data_evento': data_atual.isoformat(),
                'pagamento_id': alocacao.get('pagamento_id'),
                'fonte_principal_tipo': alocacao.get('fonte_principal_tipo'),
                'fonte_principal_id': alocacao.get('fonte_principal_id'),
                'valor_coberto': alocacao.get('valor_coberto'),
                'valor_deficit': alocacao.get('valor_deficit'),
            })
            _consumir_componentes(estado, alocacao.get('componentes_escolhidos') or [])
            if alocacao.get('cobertura_integral'):
                pagamentos_cobertos.append(str(alocacao.get('pagamento_id') or ''))
            else:
                pagamentos_sem_cobertura.append(str(alocacao.get('pagamento_id') or ''))

        materializar_aportes_planejados_v216(estado, data_atual, config, historico)

    metrica = _calcular_metrica(
        resultados_pagamento,
        ganho_switching=ganho_switching_total,
        perda_liquidez_switching=perda_liquidez_switching_total,
        custo_fiscal_switching=custo_fiscal_switching_total,
        eventos_executados=eventos_executados,
    )
    patrimonio_proxy = _patrimonio_terminal_proxy(estado, metrica, ganho_switching_total)

    return {
        'status': 'integracao_integral_multidestino_v216',
        'implementado': True,
        'horizonte': horizonte,
        'estado_inicial_normalizado': deepcopy(dict(estado_inicial or {})),
        'estado_final_estimado': deepcopy(estado),
        'eventos_recebidos': eventos,
        'eventos_executados': eventos_executados,
        'historico_eventos': historico,
        'auditoria_aportes_planejados_v216': deepcopy(estado.get('auditoria_aportes_planejados_v216') or []),
        'resultados_pagamento': resultados_pagamento,
        'pagamentos_cobertos': pagamentos_cobertos,
        'pagamentos_sem_cobertura': pagamentos_sem_cobertura,
        'ganho_switching_total': round(ganho_switching_total, 2),
        'perda_liquidez_switching_total': round(perda_liquidez_switching_total, 2),
        'custo_fiscal_switching_total': round(custo_fiscal_switching_total, 2),
        'patrimonio_liquido_terminal_proxy': patrimonio_proxy,
        'metrica_central': metrica,
        'config_resumido': dict(config or {}),
        'observacao': 'Integração temporal multidestino V216: recebidos futuros ativados podem virar caixa/reserva/aporte planejado após pagamentos do dia, com invariante, bloqueio de dupla contagem, auditoria de liquidez/carência e comparação com/sem aporte.',
    }


def rodar_integracao_funcional_minima_v117(
    *,
    raiz_repositorio: Path,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
) -> dict[str, Any]:
    """Wrapper de compatibilidade para o runner extraído do simulador central."""

    from nucleo.runners.simulador_central_runner_v117 import (
        rodar_integracao_funcional_minima_v117 as _runner_extraido_v117,
    )

    return _runner_extraido_v117(
        raiz_repositorio=raiz_repositorio,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
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
