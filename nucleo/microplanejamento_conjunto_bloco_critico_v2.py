from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.caixa_recebidos_auditaveis import (
    _construir_candidatos_decisao_local_v1,
    _construir_mapa_produtos_proxy,
    _pagamentos_alvo_f1_4,
    _prioridade_status_origem,
    _score_proxy_economico_por_versao,
)
from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.planejamento_conjunto_local_bloco_critico_v1 import _evento_ancora, _normalizar_quadro_referencia
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos
from nucleo.utilitarios_neutros import _fonte_id, _rotulo_fonte, _safe_float


@dataclass(slots=True)
class PacoteMicroplanejamentoConjuntoBlocoCriticoV2:
    quadro_microplanejamento_conjunto: pd.DataFrame
    quadro_comparativo_politicas: pd.DataFrame
    auditoria: dict[str, Any]


DEFAULT_BLOCO_CRITICO_INICIO = date(2026, 4, 20)
DEFAULT_BLOCO_CRITICO_FIM = date(2026, 5, 20)


COLUNAS_QUADRO = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'politica_id', 'politica_descricao',
    'evento_ancora', 'bloco_critico', 'lote_final_microplanejamento', 'fontes_usadas_microplanejamento', 'multifonte_microplanejamento',
    'tipo_fonte_final', 'score_microplanejamento', 'status_microplanejamento', 'criterio_microplanejamento',
    'reserva_explicita_microplanejamento', 'saldo_antes_microplanejamento', 'bruto_microplanejamento', 'imposto_microplanejamento',
    'liquido_microplanejamento', 'saldo_remanescente_microplanejamento', 'pagamento_totalmente_coberto_microplanejamento',
    'mudou_vs_v104', 'observacao_microplanejamento',
]


def _safe_round(valor: Any, ndigits: int = 2) -> float:
    return round(_safe_float(valor), ndigits)




def _criterio_desempate(candidato: dict[str, Any], valor_pagamento: float) -> tuple[Any, ...]:
    excesso = max(_safe_float(candidato.get('valor_disponivel')) - valor_pagamento, 0.0)
    return (
        round(excesso, 4),
        _prioridade_status_origem(candidato.get('status_origem')),
        _fonte_id(candidato),
    )


def _resumo_movimentos(movimentos: list[dict[str, Any]], valor_pagamento: float, tolerancia_monetaria: float) -> dict[str, Any]:
    fontes = [m.get('rotulo_fonte') or '' for m in movimentos]
    saldo_antes = round(sum(_safe_float(m.get('saldo_antes')) for m in movimentos), 2)
    bruto = round(sum(_safe_float(m.get('bruto')) for m in movimentos), 2)
    imposto = round(sum(_safe_float(m.get('imposto')) for m in movimentos), 2)
    liquido = round(sum(_safe_float(m.get('liquido')) for m in movimentos), 2)
    saldo_rem = round(sum(_safe_float(m.get('saldo_remanescente')) for m in movimentos), 2)
    return {
        'lote_final_microplanejamento': ' + '.join([f for f in fontes if f]) if fontes else '',
        'fontes_usadas_microplanejamento': ' | '.join([f for f in fontes if f]) if fontes else '',
        'multifonte_microplanejamento': len([f for f in fontes if f]) > 1,
        'saldo_antes_microplanejamento': saldo_antes,
        'bruto_microplanejamento': bruto,
        'imposto_microplanejamento': imposto,
        'liquido_microplanejamento': liquido,
        'saldo_remanescente_microplanejamento': saldo_rem,
        'pagamento_totalmente_coberto_microplanejamento': bool(liquido + tolerancia_monetaria >= valor_pagamento),
    }


def _aplicar_movimento_candidato(
    candidato: dict[str, Any],
    *,
    valor_liquido: float,
    mapa_lotes: dict[str, Any],
    consumo_generico: dict[str, float],
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    tolerancia_monetaria: float,
) -> dict[str, Any]:
    tipo_final = str(candidato.get('tipo_fonte_escolhida') or '').strip()
    lote_final = str(candidato.get('lote_id') or '').strip()
    fonte_final_id = _fonte_id(candidato)
    saldo_antes = _safe_round(candidato.get('saldo_antes_dinamico'))
    bruto = 0.0
    imposto = 0.0
    liquido = round(min(valor_liquido, _safe_float(candidato.get('valor_disponivel'))), 2)
    saldo_rem = saldo_antes

    if tipo_final == 'lote_resgatavel' and lote_final:
        lote = mapa_lotes.get(lote_final)
        if lote is not None and liquido > tolerancia_monetaria:
            movimento = executar_saque_lote(
                lote,
                liquido,
                data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            if movimento is not None:
                saldo_antes = _safe_round(movimento.get('saldo_antes'))
                bruto = _safe_round(movimento.get('bruto'))
                imposto = _safe_round(movimento.get('imposto'))
                liquido = _safe_round(movimento.get('liquido'))
                saldo_rem = _safe_round(movimento.get('saldo_remanescente'))
    else:
        consumo_generico[fonte_final_id] = round(_safe_float(consumo_generico.get(fonte_final_id)) + liquido, 2)
        bruto = liquido
        imposto = 0.0
        saldo_rem = round(max(saldo_antes - liquido, 0.0), 2)

    return {
        'rotulo_fonte': lote_final or _rotulo_fonte(candidato),
        'tipo_fonte_final': tipo_final,
        'fonte_final_id': fonte_final_id,
        'saldo_antes': saldo_antes,
        'bruto': bruto,
        'imposto': imposto,
        'liquido': liquido,
        'saldo_remanescente': saldo_rem,
    }


def _construir_contexto_reservas(quadro_v104: pd.DataFrame, quadro_v103: pd.DataFrame, evento_ancora: dict[str, Any] | None) -> dict[str, Any]:
    contexto: dict[str, Any] = {
        'pagamento_ancora_id': str(evento_ancora.get('despesa_id') or '').strip() if evento_ancora else '',
        'lotes_reserva': [],
        'lote_ancora_v104': '',
        'lote_ancora_v103': '',
        'lote_escola_v103': '',
        'lote_cartao_inicial_v103': '',
    }
    if len(quadro_v104) and evento_ancora is not None:
        pid = str(evento_ancora.get('despesa_id') or '').strip()
        sub = quadro_v104[quadro_v104['pagamento_id'].astype(str).eq(pid)]
        if len(sub):
            contexto['lote_ancora_v104'] = str(sub.iloc[0].get('lote_final_planejamento') or '').strip()
    if len(quadro_v103) and evento_ancora is not None:
        pid = str(evento_ancora.get('despesa_id') or '').strip()
        sub = quadro_v103[quadro_v103['pagamento_id'].astype(str).eq(pid)]
        if len(sub):
            contexto['lote_ancora_v103'] = str(sub.iloc[0].get('lote_final_heuristica') or '').strip()
        sub_escola = quadro_v103[quadro_v103['descricao_pagamento'].astype(str).eq('Escola')]
        if len(sub_escola):
            contexto['lote_escola_v103'] = str(sub_escola.iloc[0].get('lote_final_heuristica') or '').strip()
        sub_cartao_inicial = quadro_v103[(quadro_v103['descricao_pagamento'].astype(str).eq('Cartão Azul')) & (quadro_v103['data_pagamento'] < DEFAULT_BLOCO_CRITICO_FIM)]
        if len(sub_cartao_inicial):
            contexto['lote_cartao_inicial_v103'] = str(sub_cartao_inicial.iloc[0].get('lote_final_heuristica') or '').strip()
    reservas = []
    for chave in ['lote_ancora_v104', 'lote_ancora_v103', 'lote_escola_v103', 'lote_cartao_inicial_v103']:
        valor = str(contexto.get(chave) or '').strip()
        if valor and valor not in reservas:
            reservas.append(valor)
    contexto['lotes_reserva'] = reservas
    return contexto


def _score_ajustado_politica(
    politica_id: str,
    candidato: dict[str, Any],
    pagamento: dict[str, Any],
    *,
    contexto_reservas: dict[str, Any],
    data_ancora: date,
) -> tuple[float, float, str]:
    valor_pagamento = _safe_float(pagamento.get('valor'))
    score_base, _ = _score_proxy_economico_por_versao('v3', candidato, valor_pagamento=valor_pagamento)
    lot = _rotulo_fonte(candidato)
    desc = str(pagamento.get('descricao') or '')
    data_pagamento = pagamento.get('data')
    pre_anchor = bool(isinstance(data_pagamento, date) and data_pagamento < data_ancora)
    anchor = bool(str(pagamento.get('despesa_id') or '').strip() == contexto_reservas.get('pagamento_ancora_id'))
    reservas = set(contexto_reservas.get('lotes_reserva') or [])
    penalty = 0.0
    motivo = ''
    if politika := politica_id:
        pass
    if politica_id == 'ancora_first_soft':
        if pre_anchor and lot in reservas and desc != 'Cartão Azul':
            penalty += 2600.0 + min(valor_pagamento, 1200.0)
            motivo = 'penalização suave para preservar lotes de reserva até 20/05.'
    elif politica_id == 'ancora_first_hard':
        if pre_anchor and lot in reservas and desc not in {'Cartão Azul', 'Escola'}:
            penalty += 5200.0 + min(valor_pagamento, 1800.0)
            motivo = 'penalização forte para bloquear consumo prévio dos lotes de reserva.'
    elif politica_id == 'ancora_multifonte_soft':
        if pre_anchor and lot in reservas and desc != 'Cartão Azul':
            penalty += 1800.0 + min(valor_pagamento, 900.0)
            motivo = 'penalização moderada para preservar reserva e permitir multifonte na âncora.'
        if anchor and lot in reservas:
            penalty -= 250.0
            motivo = 'bônus na âncora para liberar a reserva preservada.'
    elif politica_id == 'ancora_multifonte_hardreserve':
        if pre_anchor and lot in reservas and desc not in {'Cartão Azul', 'Escola'}:
            penalty += 6000.0 + min(valor_pagamento, 2200.0)
            motivo = 'penalização máxima para preservação explícita dos lotes reservados até a âncora.'
        if anchor and lot in reservas:
            penalty -= 350.0
            motivo = 'bônus forte na âncora para acionar multifonte com as reservas explícitas.'
    elif politica_id == 'ancora_first_sacrificio_local':
        if pre_anchor and lot in reservas and desc not in {'Cartão Azul', 'Escola'}:
            penalty += (8000.0 + 500.0) + min(valor_pagamento, 3000.0)
            motivo = 'penalização extrema para priorizar a âncora mesmo com sacrifício local.'
        if anchor and lot in reservas:
            penalty -= 500.0
            motivo = 'bônus extremo na âncora para liberar uso de reservas preservadas.'
    return round(score_base + penalty, 6), round(penalty, 6), motivo


def _ordenar_candidatos_para_politica(
    politica_id: str,
    candidatos: list[dict[str, Any]],
    pagamento: dict[str, Any],
    *,
    contexto_reservas: dict[str, Any],
    data_ancora: date,
) -> list[dict[str, Any]]:
    avaliados = []
    for candidato in candidatos:
        score_final, penalidade, motivo = _score_ajustado_politica(
            politica_id,
            candidato,
            pagamento,
            contexto_reservas=contexto_reservas,
            data_ancora=data_ancora,
        )
        cand = deepcopy(candidato)
        cand['score_microplanejamento'] = score_final
        cand['penalidade_microplanejamento'] = penalidade
        cand['motivo_penalidade_microplanejamento'] = motivo
        avaliados.append((score_final, _criterio_desempate(candidato, _safe_float(pagamento.get('valor'))), cand))
    avaliados.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in avaliados]


def _reservas_explicitas_ativas(politica_id: str, pagamento: dict[str, Any], contexto_reservas: dict[str, Any], data_ancora: date) -> bool:
    data_pagamento = pagamento.get('data')
    pre_anchor = bool(isinstance(data_pagamento, date) and data_pagamento < data_ancora)
    desc = str(pagamento.get('descricao') or '')
    if not pre_anchor:
        return False
    if politica_id in {'ancora_first_hard', 'ancora_multifonte_hardreserve', 'ancora_first_sacrificio_local'} and desc not in {'Cartão Azul', 'Escola'}:
        return True
    return False


def _selecionar_pool_politica(
    politica_id: str,
    candidatos_ordenados: list[dict[str, Any]],
    pagamento: dict[str, Any],
    *,
    contexto_reservas: dict[str, Any],
    data_ancora: date,
) -> list[dict[str, Any]]:
    reservas = set(contexto_reservas.get('lotes_reserva') or [])
    anchor = bool(str(pagamento.get('despesa_id') or '').strip() == contexto_reservas.get('pagamento_ancora_id'))
    desc = str(pagamento.get('descricao') or '')
    if anchor:
        return candidatos_ordenados
    if _reservas_explicitas_ativas(politica_id, pagamento, contexto_reservas, data_ancora):
        nao_reserva = [c for c in candidatos_ordenados if _rotulo_fonte(c) not in reservas]
        if nao_reserva:
            return nao_reserva
    if politica_id == 'ancora_first_soft':
        cobridores_nao_reserva = [c for c in candidatos_ordenados if _rotulo_fonte(c) not in reservas and bool(c.get('pagamento_totalmente_coberto'))]
        if cobridores_nao_reserva:
            return cobridores_nao_reserva + [c for c in candidatos_ordenados if _rotulo_fonte(c) in reservas]
    if politica_id == 'ancora_multifonte_soft' and desc not in {'Cartão Azul', 'Escola'}:
        nao_reserva = [c for c in candidatos_ordenados if _rotulo_fonte(c) not in reservas]
        if nao_reserva:
            return nao_reserva + [c for c in candidatos_ordenados if _rotulo_fonte(c) in reservas]
    return candidatos_ordenados


def _permitir_multifonte(politica_id: str, pagamento: dict[str, Any], contexto_reservas: dict[str, Any]) -> bool:
    anchor = bool(str(pagamento.get('despesa_id') or '').strip() == contexto_reservas.get('pagamento_ancora_id'))
    if anchor and politica_id in {'ancora_multifonte_soft', 'ancora_multifonte_hardreserve', 'ancora_first_sacrificio_local'}:
        return True
    if politica_id == 'ancora_first_sacrificio_local':
        return True
    return False


def _simular_pagamento_politica(
    politica_id: str,
    pagamento: dict[str, Any],
    *,
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, dict[str, Any]],
    mapa_lotes: dict[str, Any],
    consumo_generico: dict[str, float],
    contexto_reservas: dict[str, Any],
    data_referencia: date,
    data_ancora: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    tolerancia_monetaria: float,
) -> dict[str, Any]:
    valor_pagamento = _safe_round(pagamento.get('valor'))
    candidatos_base = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
    candidatos = _ajustar_candidatos_dinamicos(
        candidatos_base,
        valor_pagamento=valor_pagamento,
        mapa_lotes=mapa_lotes,
        consumo_generico=consumo_generico,
        data_referencia=data_referencia,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
        tolerancia_monetaria=tolerancia_monetaria,
    )
    elegiveis = [c for c in candidatos if bool(c.get('elegivel'))]
    ordenados = _ordenar_candidatos_para_politica(politica_id, elegiveis, pagamento, contexto_reservas=contexto_reservas, data_ancora=data_ancora)
    pool = _selecionar_pool_politica(politica_id, ordenados, pagamento, contexto_reservas=contexto_reservas, data_ancora=data_ancora)
    permitir_multifonte = _permitir_multifonte(politica_id, pagamento, contexto_reservas)
    anchor = bool(str(pagamento.get('despesa_id') or '').strip() == contexto_reservas.get('pagamento_ancora_id'))

    movimentos: list[dict[str, Any]] = []
    criterio = 'sem candidatos elegíveis'
    score = None
    observacao = ''

    cobridores = [c for c in pool if bool(c.get('pagamento_totalmente_coberto'))]
    if cobridores:
        escolhido = cobridores[0]
        movimento = _aplicar_movimento_candidato(
            escolhido,
            valor_liquido=valor_pagamento,
            mapa_lotes=mapa_lotes,
            consumo_generico=consumo_generico,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        movimentos.append(movimento)
        criterio = 'monofonte reordenado por política'
        score = escolhido.get('score_microplanejamento')
        observacao = str(escolhido.get('motivo_penalidade_microplanejamento') or '').strip()
    elif permitir_multifonte and pool:
        restante = valor_pagamento
        usados = []
        for candidato in pool:
            disponivel = _safe_round(candidato.get('valor_disponivel'))
            if disponivel <= tolerancia_monetaria or restante <= tolerancia_monetaria:
                continue
            alvo = min(restante, disponivel)
            movimento = _aplicar_movimento_candidato(
                candidato,
                valor_liquido=alvo,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            movimentos.append(movimento)
            usados.append(candidato)
            restante = round(restante - _safe_float(movimento.get('liquido')), 2)
            if restante <= tolerancia_monetaria:
                break
        criterio = 'multifonte embutido na política' if anchor else 'multifonte local embutido na política'
        score = round(sum(_safe_float(c.get('score_microplanejamento')) for c in usados), 4) if usados else None
        observacao = 'combinação greedy de fontes ordenadas pelo score ajustado da política.'
    elif pool:
        escolhido = pool[0]
        movimento = _aplicar_movimento_candidato(
            escolhido,
            valor_liquido=min(valor_pagamento, _safe_round(escolhido.get('valor_disponivel'))),
            mapa_lotes=mapa_lotes,
            consumo_generico=consumo_generico,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        movimentos.append(movimento)
        criterio = 'uso parcial da melhor fonte residual'
        score = escolhido.get('score_microplanejamento')
        observacao = 'a política preservou reservas explícitas e aceitou cobertura parcial neste evento.'

    resumo_mov = _resumo_movimentos(movimentos, valor_pagamento, tolerancia_monetaria)
    status = 'sem candidatos elegíveis'
    if movimentos:
        if resumo_mov['pagamento_totalmente_coberto_microplanejamento']:
            status = 'coberto pelo microplanejamento'
        elif resumo_mov['liquido_microplanejamento'] > 0:
            status = 'cobertura parcial no microplanejamento'
        else:
            status = 'sem cobertura no microplanejamento'
    return {
        'score_microplanejamento': round(_safe_float(score), 4) if score is not None else None,
        'criterio_microplanejamento': criterio,
        'reserva_explicita_microplanejamento': 'sim' if _reservas_explicitas_ativas(politica_id, pagamento, contexto_reservas, data_ancora) else '',
        'tipo_fonte_final': 'multifonte' if resumo_mov['multifonte_microplanejamento'] else (movimentos[0].get('tipo_fonte_final') if movimentos else ''),
        'status_microplanejamento': status,
        'observacao_microplanejamento': observacao,
        **resumo_mov,
    }


def _resumo_quadro(quadro: pd.DataFrame, anchor_payment_id: str, tolerancia_monetaria: float) -> dict[str, Any]:
    anchor = quadro[quadro['pagamento_id'].astype(str).eq(anchor_payment_id)].copy() if anchor_payment_id else pd.DataFrame()
    liquido_anchor = _safe_round(anchor.iloc[0].get('liquido_microplanejamento')) if len(anchor) else 0.0
    valor_anchor = _safe_round(anchor.iloc[0].get('valor_pagamento')) if len(anchor) else 0.0
    primeira_sem = quadro[quadro['pagamento_totalmente_coberto_microplanejamento'] == False].copy()
    primeira_sem = primeira_sem.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable') if len(primeira_sem) else primeira_sem
    return {
        'pagamentos_bloco': int(len(quadro)),
        'pagamentos_cobertos_bloco': int(quadro['pagamento_totalmente_coberto_microplanejamento'].sum()) if len(quadro) else 0,
        'deficit_total_bloco': round(sum(max(_safe_float(r.get('valor_pagamento')) - _safe_float(r.get('liquido_microplanejamento')), 0.0) for r in quadro.to_dict(orient='records')), 2),
        'liquido_coberto_ancora': liquido_anchor,
        'deficit_ancora': round(max(valor_anchor - liquido_anchor, 0.0), 2),
        'cobertura_integral_ancora': bool(liquido_anchor + tolerancia_monetaria >= valor_anchor),
        'primeira_sem_cobertura_data': primeira_sem.iloc[0].get('data_pagamento') if len(primeira_sem) else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.iloc[0].get('descricao_pagamento') if len(primeira_sem) else None,
        'primeira_sem_cobertura_lote_final': primeira_sem.iloc[0].get('lote_final_microplanejamento') if len(primeira_sem) else None,
        'uso_multifonte': int(quadro['multifonte_microplanejamento'].sum()) if len(quadro) else 0,
        'reservas_acionadas': int((quadro['reserva_explicita_microplanejamento'].astype(str) == 'sim').sum()) if len(quadro) else 0,
    }


def _ordenar_politicas(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -int(bool(item.get('cobertura_integral_ancora'))),
        -_safe_float(item.get('liquido_coberto_ancora')),
        -int(item.get('pagamentos_cobertos_bloco') or 0),
        _safe_float(item.get('deficit_total_bloco')),
        -int(item.get('uso_multifonte') or 0),
        str(item.get('politica_id') or ''),
    )


def carregar_microplanejamento_conjunto_bloco_critico_v2(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    replay_passado,
    heuristica_conjunta_parcial_bloco_critico,
    planejamento_conjunto_local_bloco_critico_v1,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    bloco_critico_inicio: date = DEFAULT_BLOCO_CRITICO_INICIO,
    bloco_critico_fim: date = DEFAULT_BLOCO_CRITICO_FIM,
    tolerancia_monetaria: float = 0.01,
) -> PacoteMicroplanejamentoConjuntoBlocoCriticoV2:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    pagamentos_bloco_df = pagamentos_alvo[(pagamentos_alvo['data'] >= bloco_critico_inicio) & (pagamentos_alvo['data'] <= bloco_critico_fim)].copy()
    pagamentos_bloco_df = pagamentos_bloco_df.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    if len(pagamentos_bloco_df) == 0:
        return PacoteMicroplanejamentoConjuntoBlocoCriticoV2(
            quadro_microplanejamento_conjunto=pd.DataFrame(columns=COLUNAS_QUADRO),
            quadro_comparativo_politicas=pd.DataFrame(),
            auditoria={'validacao': {'ok': False, 'erros': ['microplanejamento_sem_pagamentos_no_bloco'], 'avisos': []}, 'resumo': {'pagamentos_no_bloco_critico': 0}},
        )

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    evento_ancora = _evento_ancora(pagamentos_bloco_df, data_alvo=bloco_critico_fim)
    pagamento_ancora_id = str(evento_ancora.get('despesa_id') or '').strip() if evento_ancora else ''
    data_ancora = evento_ancora.get('data') if evento_ancora else bloco_critico_fim

    quadro_v103 = heuristica_conjunta_parcial_bloco_critico.quadro_heuristica_conjunta_parcial.copy() if heuristica_conjunta_parcial_bloco_critico is not None else pd.DataFrame()
    quadro_v103 = quadro_v103[(quadro_v103['data_pagamento'] >= bloco_critico_inicio) & (quadro_v103['data_pagamento'] <= bloco_critico_fim)].copy() if len(quadro_v103) else quadro_v103
    quadro_v104_ref = planejamento_conjunto_local_bloco_critico_v1.quadro_planejamento_conjunto_local.copy() if planejamento_conjunto_local_bloco_critico_v1 is not None else pd.DataFrame()
    comparativo_v104_ref = planejamento_conjunto_local_bloco_critico_v1.quadro_comparativo_politicas.copy() if planejamento_conjunto_local_bloco_critico_v1 is not None else pd.DataFrame()

    quadro_v104 = quadro_v104_ref[(quadro_v104_ref['data_pagamento'] >= bloco_critico_inicio) & (quadro_v104_ref['data_pagamento'] <= bloco_critico_fim)].copy() if len(quadro_v104_ref) else quadro_v104_ref
    quadro_v104 = quadro_v104.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable') if len(quadro_v104) else quadro_v104
    quadro_ref = _normalizar_quadro_referencia(
        quadro_v104,
        politica_id='v104_referencia',
        politica_descricao='Planejamento conjunto local do bloco crítico da V104',
        lote_col='lote_final_planejamento',
        tipo_col='tipo_fonte_final',
        score_col='score_planejamento',
        status_col='status_planejamento',
        saldo_col='saldo_antes_planejamento',
        bruto_col='bruto_planejamento',
        imposto_col='imposto_planejamento',
        liquido_col='liquido_planejamento',
        rem_col='saldo_remanescente_planejamento',
        cobertura_col='pagamento_totalmente_coberto_planejamento',
        anchor_payment_id=pagamento_ancora_id,
    ) if len(quadro_v104) else pd.DataFrame(columns=[
        'pagamento_id','data_pagamento','descricao_pagamento','valor_pagamento','politica_id','politica_descricao','evento_ancora','lote_final_planejamento','tipo_fonte_final','fonte_final_id','score_planejamento','status_planejamento','saldo_antes_planejamento','bruto_planejamento','imposto_planejamento','liquido_planejamento','saldo_remanescente_planejamento','pagamento_totalmente_coberto_planejamento','observacao_planejamento','mudou_vs_v103'
    ])
    contexto_reservas = _construir_contexto_reservas(quadro_v104, quadro_v103, evento_ancora)

    registros_por_politica: dict[str, pd.DataFrame] = {'v104_referencia': quadro_ref.copy()}
    comparativos: list[dict[str, Any]] = []

    ref_resumo = {
        'politica_id': 'v104_referencia',
        'politica_descricao': 'Planejamento conjunto local do bloco crítico da V104',
        **_resumo_quadro(pd.DataFrame([{ 
            'pagamento_id': r.get('pagamento_id'),
            'data_pagamento': r.get('data_pagamento'),
            'descricao_pagamento': r.get('descricao_pagamento'),
            'valor_pagamento': r.get('valor_pagamento'),
            'liquido_microplanejamento': r.get('liquido_planejamento'),
            'pagamento_totalmente_coberto_microplanejamento': r.get('pagamento_totalmente_coberto_planejamento'),
            'lote_final_microplanejamento': r.get('lote_final_planejamento'),
            'multifonte_microplanejamento': '+' in str(r.get('lote_final_planejamento') or ''),
            'reserva_explicita_microplanejamento': '',
        } for r in quadro_ref.to_dict(orient='records')]), pagamento_ancora_id, tolerancia_monetaria),
    }
    comparativos.append(ref_resumo)

    politicas = [
        ('ancora_first_soft', 'Reserva suave explícita para a âncora com monofonte preferencial e multifonte na âncora.'),
        ('ancora_first_hard', 'Reserva forte dos lotes estratégicos antes de 20/05 e liberação na âncora.'),
        ('ancora_multifonte_soft', 'Reserva moderada e multifonte embutido quando necessário, priorizando a âncora.'),
        ('ancora_multifonte_hardreserve', 'Reserva forte com multifonte embutido explícito na âncora e nos resgates críticos.'),
        ('ancora_first_sacrificio_local', 'Política âncora-first agressiva, aceitando sacrifício local para preservar liquidez até 20/05.'),
    ]

    for politica_id, politica_desc in politicas:
        mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
        consumo_generico: dict[str, float] = {}
        linhas = []
        for pagamento in pagamentos_bloco_df.to_dict(orient='records'):
            sim = _simular_pagamento_politica(
                politica_id,
                pagamento,
                quadro_saldo=quadro_saldo,
                quadro_fontes=quadro_fontes,
                mapa_produtos_proxy=mapa_produtos_proxy,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                contexto_reservas=contexto_reservas,
                data_referencia=data_referencia,
                data_ancora=data_ancora,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            pid = str(pagamento.get('despesa_id') or '').strip()
            ref_row = next((r for r in quadro_ref.to_dict(orient='records') if str(r.get('pagamento_id') or '').strip() == pid), {})
            linhas.append({
                'pagamento_id': pid,
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'valor_pagamento': _safe_round(pagamento.get('valor')),
                'politica_id': politica_id,
                'politica_descricao': politica_desc,
                'evento_ancora': bool(pid == pagamento_ancora_id),
                'bloco_critico': 'sim',
                'mudou_vs_v104': bool(str(sim.get('lote_final_microplanejamento') or '') != str(ref_row.get('lote_final_planejamento') or '')),
                **sim,
            })
        quadro_pol = pd.DataFrame(linhas, columns=COLUNAS_QUADRO).sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
        registros_por_politica[politica_id] = quadro_pol
        comparativos.append({
            'politica_id': politica_id,
            'politica_descricao': politica_desc,
            **_resumo_quadro(quadro_pol, pagamento_ancora_id, tolerancia_monetaria),
        })

    comparativos.sort(key=_ordenar_politicas)
    escolhido = comparativos[0] if comparativos else ref_resumo
    politica_escolhida = str(escolhido.get('politica_id') or 'v104_referencia')
    quadro_escolhido = registros_por_politica.get(politica_escolhida, quadro_ref.copy())

    resumo = {
        'pagamentos_no_bloco_critico': int(len(pagamentos_bloco_df)),
        'politicas_avaliadas': int(len(comparativos)),
        'politica_escolhida': politica_escolhida,
        'descricao_politica_escolhida': escolhido.get('politica_descricao') or '',
        'evento_ancora_pagamento': str(evento_ancora.get('descricao') or '') if evento_ancora else '',
        'evento_ancora_data': evento_ancora.get('data') if evento_ancora else None,
        'evento_ancora_valor': _safe_round(evento_ancora.get('valor')) if evento_ancora else 0.0,
        'liquido_coberto_ancora_escolhida': _safe_round(escolhido.get('liquido_coberto_ancora')),
        'deficit_ancora_escolhida': _safe_round(escolhido.get('deficit_ancora')),
        'cobertura_integral_ancora_escolhida': bool(escolhido.get('cobertura_integral_ancora')),
        'pagamentos_cobertos_bloco_escolhida': int(escolhido.get('pagamentos_cobertos_bloco') or 0),
        'deficit_total_bloco_escolhida': _safe_round(escolhido.get('deficit_total_bloco')),
        'delta_liquido_ancora_vs_v104': _safe_round(_safe_float(escolhido.get('liquido_coberto_ancora')) - _safe_float(ref_resumo.get('liquido_coberto_ancora'))),
        'delta_pagamentos_cobertos_vs_v104': int(escolhido.get('pagamentos_cobertos_bloco') or 0) - int(ref_resumo.get('pagamentos_cobertos_bloco') or 0),
        'uso_multifonte_escolhida': int(escolhido.get('uso_multifonte') or 0),
        'reservas_acionadas_escolhida': int(escolhido.get('reservas_acionadas') or 0),
        'primeira_sem_cobertura_data_escolhida': escolhido.get('primeira_sem_cobertura_data'),
        'primeira_sem_cobertura_pagamento_escolhida': escolhido.get('primeira_sem_cobertura_pagamento') or '',
        'primeira_sem_cobertura_lote_escolhida': escolhido.get('primeira_sem_cobertura_lote_final') or '',
        'ganho_material_vs_v104': bool(_safe_float(escolhido.get('liquido_coberto_ancora')) > _safe_float(ref_resumo.get('liquido_coberto_ancora')) + tolerancia_monetaria),
        'lotes_reserva_explicitos': list(contexto_reservas.get('lotes_reserva') or []),
    }

    amostra_comp = []
    for item in comparativos[:10]:
        amostra_comp.append({
            'Política': item.get('politica_id') or '',
            'Liquidez no Cartão Azul 20/05': _safe_round(item.get('liquido_coberto_ancora')),
            'Déficit do Cartão Azul 20/05': _safe_round(item.get('deficit_ancora')),
            'Pagamentos cobertos no bloco': int(item.get('pagamentos_cobertos_bloco') or 0),
            'Uso multifonte': int(item.get('uso_multifonte') or 0),
            'Reservas acionadas': int(item.get('reservas_acionadas') or 0),
        })

    mapa_ref = {str(r.get('pagamento_id') or '').strip(): r for r in quadro_ref.to_dict(orient='records')}
    amostra_mudancas = []
    for _, row in quadro_escolhido.iterrows():
        ref_row = mapa_ref.get(str(row.get('pagamento_id') or '').strip(), {})
        if bool(row.get('mudou_vs_v104')):
            data = row.get('data_pagamento')
            amostra_mudancas.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else str(data or ''),
                'Descrição': row.get('descricao_pagamento') or '',
                'Valor': _safe_round(row.get('valor_pagamento')),
                'Lote V104': ref_row.get('lote_final_planejamento') or '',
                'Lote v2': row.get('lote_final_microplanejamento') or '',
                'Status v2': row.get('status_microplanejamento') or '',
            })
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_comparativo_politicas': amostra_comp,
        'amostra_mudancas_vs_v104': amostra_mudancas[:10],
    }
    quadro_comparativo = pd.DataFrame(comparativos)
    return PacoteMicroplanejamentoConjuntoBlocoCriticoV2(
        quadro_microplanejamento_conjunto=quadro_escolhido,
        quadro_comparativo_politicas=quadro_comparativo,
        auditoria=auditoria,
    )
