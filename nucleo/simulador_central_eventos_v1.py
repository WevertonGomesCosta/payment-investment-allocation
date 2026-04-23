from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import avaliar_cenarios_conjuntos_v1
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.recomputacao_sequencial_central_v1 import _perfil_pagamento_operacional


def _coerce_date(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except Exception:
            return None
    return None


def _normalizar_proxy_terminal(valor: Any) -> float:
    try:
        numero = float(valor or 0.0)
    except Exception:
        return 0.0
    if numero > 1.0:
        numero = numero / 100.0
    return max(numero, 0.0)


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
            'taxa_base_cdi': float(row.get('taxa_base_cdi') or 0.0),
            'taxa_bonus_cdi': float(row.get('taxa_bonus_cdi') or 0.0),
        }
    return mapa


def _proxy_fallback_lote(lote: Any, contexto: Any) -> float:
    taxa_ref = max(float(getattr(lote, 'taxa_bonus_cdi', 0.0) or 0.0), float(getattr(lote, 'taxa_base_cdi', 0.0) or 0.0))
    cdi = float(getattr(contexto.calendario_financeiro, 'cdi_anual_modelo', 0.0) or 0.0)
    return max(min(taxa_ref * cdi, 0.95), 0.05)


def _aliquota_ir_estimada(data_aplicacao: date | None, data_acao: date | None) -> float:
    if data_aplicacao is None or data_acao is None:
        return 0.15
    dias = max((data_acao - data_aplicacao).days, 0)
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


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
        produto = mapa_produtos.get(str(getattr(lote, 'produto_key', '') or '').strip(), {})
        lotes.append({
            'id': str(lote.id),
            'investimento': str(lote.investimento),
            'produto_key': str(getattr(lote, 'produto_key', '') or ''),
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
    inventario = contexto.dados_operacionais.inventario_canonico.copy()
    if len(inventario):
        mask = inventario['nao_aportado_disponivel'].fillna(False)
        for _, row in inventario.loc[mask].iterrows():
            recebidos_disponiveis.append({
                'id': str(row.get('lote_id') or ''),
                'valor_disponivel': round(float(row.get('valor_original') or 0.0), 2),
                'proxy_terminal_atual': 0.0,
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
        },
    }


def _aplicar_switching_eventos(estado: dict[str, Any], eventos: list[dict[str, Any]], data_atual: date, historico: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float, float, float]:
    executados: list[dict[str, Any]] = []
    ganho_total = 0.0
    perda_liquidez = 0.0
    custo_fiscal_total = 0.0
    data_final = _coerce_date(estado.get('data_fim_recorte'))
    for evento in eventos:
        data_acao = _coerce_date(evento.get('data_acao'))
        if not evento.get('elegivel') or data_acao is None or data_acao != data_atual:
            continue
        if evento.get('tipo_acao') != 'switching_simples':
            continue
        lote_id = str(evento.get('lote_origem_id') or '')
        for lote in estado.get('lotes_aportados', []):
            if str(lote.get('id') or '') != lote_id:
                continue
            valor_liquido_origem = round(float(lote.get('valor_liquido_resgatavel') or 0.0), 2)
            principal = round(float(lote.get('principal_remanescente') or 0.0), 2)
            aliquota = _aliquota_ir_estimada(_coerce_date(lote.get('data_aplicacao')), data_atual)
            custo_fiscal = round(float(evento.get('custo_fiscal_estimado') or _estimar_imposto_resgate(valor_liquido_origem, principal, aliquota)), 2)
            valor_migrado = round(max(float(evento.get('valor_migrado_estimado') or 0.0), valor_liquido_origem - custo_fiscal), 2)
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
            lote['investimento'] = produto_destino
            lote['produto_key'] = str(evento.get('produto_destino_key') or lote.get('produto_key') or '')
            lote['produto_destino_key'] = str(evento.get('produto_destino_key') or lote.get('produto_destino_key') or '')
            lote['valor_liquido_resgatavel'] = valor_migrado
            lote['principal_remanescente'] = valor_migrado
            lote['proxy_terminal_atual'] = float(evento.get('proxy_terminal_destino') or lote.get('proxy_terminal_atual') or 0.0)
            lote['retorno_anual_proxy_atual'] = retorno_destino
            lote['liquidez_dias_atual'] = liquidez_destino
            lote['carencia_dias_atual'] = carencia_destino
            lote['carencia_ate'] = data_atual + timedelta(days=carencia_destino) if carencia_destino > 0 else None
            lote['data_aplicacao'] = data_atual
            lote['custo_fiscal_acumulado'] = round(float(lote.get('custo_fiscal_acumulado') or 0.0) + custo_fiscal, 2)
            lote['valor_terminal_estimado'] = valor_terminal_estimado
            historico.append({
                'tipo_evento': 'switching',
                'data_evento': data_atual.isoformat(),
                'lote_id': lote_id,
                'produto_origem': produto_origem,
                'produto_destino': produto_destino,
                'valor_liquido_origem': valor_liquido_origem,
                'valor_migrado': valor_migrado,
                'custo_fiscal_realizado': custo_fiscal,
                'liquidez_dias_destino': liquidez_destino,
                'carencia_dias_destino': carencia_destino,
                'valor_terminal_estimado': valor_terminal_estimado,
                'ganho_terminal_proxy_estimado': float(evento.get('ganho_terminal_proxy_estimado') or 0.0),
            })
            executados.append({**evento, 'custo_fiscal_realizado': custo_fiscal, 'valor_migrado_realizado': valor_migrado, 'valor_terminal_estimado': valor_terminal_estimado})
            ganho_total += float(evento.get('ganho_terminal_proxy_estimado') or 0.0)
            perda_liquidez += float(evento.get('perda_liquidez_estimada') or 0.0)
            custo_fiscal_total += custo_fiscal
            break
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
    agenda = sorted([d for d in (datas_eventos | datas_pagamentos) if d is not None])

    for data_atual in agenda:
        estado['data_evento_corrente'] = data_atual
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

    metrica = _calcular_metrica(
        resultados_pagamento,
        ganho_switching=ganho_switching_total,
        perda_liquidez_switching=perda_liquidez_switching_total,
        custo_fiscal_switching=custo_fiscal_switching_total,
        eventos_executados=eventos_executados,
    )
    patrimonio_proxy = _patrimonio_terminal_proxy(estado, metrica, ganho_switching_total)

    return {
        'status': 'integracao_multidestino_v121',
        'implementado': True,
        'horizonte': horizonte,
        'estado_inicial_normalizado': deepcopy(dict(estado_inicial or {})),
        'estado_final_estimado': deepcopy(estado),
        'eventos_recebidos': eventos,
        'eventos_executados': eventos_executados,
        'historico_eventos': historico,
        'resultados_pagamento': resultados_pagamento,
        'pagamentos_cobertos': pagamentos_cobertos,
        'pagamentos_sem_cobertura': pagamentos_sem_cobertura,
        'ganho_switching_total': round(ganho_switching_total, 2),
        'perda_liquidez_switching_total': round(perda_liquidez_switching_total, 2),
        'custo_fiscal_switching_total': round(custo_fiscal_switching_total, 2),
        'patrimonio_liquido_terminal_proxy': patrimonio_proxy,
        'metrica_central': metrica,
        'config_resumido': dict(config or {}),
        'observacao': 'Integração temporal multidestino: planejador ranqueado por ganho terminal econômico mínimo real estimado com múltiplos destinos elegíveis por lote antes do simulador central.',
    }


def rodar_integracao_funcional_minima_v117(
    *,
    raiz_repositorio: Path,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite_pagamentos: int = 15,
) -> dict[str, Any]:
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
        'status': 'integracao_multidestino_v121',
        'implementado': True,
        'contexto_data_referencia': contexto.execucao.data_referencia.isoformat(),
        'horizonte': horizonte,
        'estado_global_recorte': estado,
        'plano_switching_temporal': plano,
        'simulacoes': simulacoes,
        'avaliacao_cenarios': avaliacao,
    }
