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
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos
from nucleo.utilitarios_neutros import _fonte_id, _rotulo_fonte, _safe_float


@dataclass(slots=True)
class PacotePlanejamentoConjuntoLocalBlocoCriticoV1:
    quadro_planejamento_conjunto_local: pd.DataFrame
    quadro_comparativo_politicas: pd.DataFrame
    auditoria: dict[str, Any]


DEFAULT_BLOCO_CRITICO_INICIO = date(2026, 4, 20)
DEFAULT_BLOCO_CRITICO_FIM = date(2026, 5, 20)




def _safe_round(valor: Any, ndigits: int = 2) -> float:
    return round(_safe_float(valor), ndigits)


def _criterio_desempate(candidato: dict[str, Any], valor_pagamento: float) -> tuple[Any, ...]:
    excesso = max(_safe_float(candidato.get('valor_disponivel')) - valor_pagamento, 0.0)
    return (
        round(excesso, 4),
        _prioridade_status_origem(candidato.get('status_origem')),
        _fonte_id(candidato),
    )


def _evento_ancora(quadro_bloco: pd.DataFrame, *, data_alvo: date | None = None) -> dict[str, Any] | None:
    if len(quadro_bloco) == 0:
        return None
    sub = quadro_bloco.copy()
    if data_alvo is not None:
        sub = sub[sub['data'] == data_alvo].copy()
    if len(sub):
        cartao = sub[sub['descricao'].astype(str).str.contains('Cartão Azul', case=False, na=False)].copy()
        if len(cartao):
            sub = cartao
    if len(sub) == 0:
        sub = quadro_bloco.copy()
    sub = sub.sort_values(by=['valor', 'data', 'despesa_id'], ascending=[False, True, True], kind='stable')
    if len(sub) == 0:
        return None
    return sub.iloc[0].to_dict()


def _simular_saque(
    candidato: dict[str, Any],
    *,
    valor_pagamento: float,
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
    liquido_disponivel = _safe_round(candidato.get('valor_disponivel'))
    coberto = bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
    liquido = round(min(valor_pagamento, liquido_disponivel), 2)
    bruto = 0.0
    imposto = 0.0
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
        'tipo_fonte_final': tipo_final,
        'fonte_final_id': fonte_final_id,
        'lote_final_planejamento': lote_final or _rotulo_fonte(candidato),
        'saldo_antes_planejamento': saldo_antes,
        'bruto_planejamento': bruto,
        'imposto_planejamento': imposto,
        'liquido_planejamento': liquido,
        'saldo_remanescente_planejamento': saldo_rem,
        'pagamento_totalmente_coberto_planejamento': coberto,
    }


def _montar_contexto_politicas(
    quadro_reescolha: pd.DataFrame,
    quadro_heuristica: pd.DataFrame,
    evento_ancora: dict[str, Any] | None,
) -> dict[str, Any]:
    contexto: dict[str, Any] = {
        'lote_ancora_v102': '',
        'lote_ancora_v103': '',
        'lote_escola_v103': '',
        'lote_cartao_inicial_v103': '',
        'pagamento_escola_id': '',
        'pagamento_ancora_id': str(evento_ancora.get('despesa_id') or '').strip() if evento_ancora else '',
    }
    if evento_ancora is not None:
        pid_ancora = str(evento_ancora.get('despesa_id') or '').strip()
        if len(quadro_reescolha):
            sub = quadro_reescolha[quadro_reescolha['pagamento_id'].astype(str).eq(pid_ancora)]
            if len(sub):
                contexto['lote_ancora_v102'] = str(sub.iloc[0].get('lote_final_dinamico') or '').strip()
        if len(quadro_heuristica):
            sub = quadro_heuristica[quadro_heuristica['pagamento_id'].astype(str).eq(pid_ancora)]
            if len(sub):
                contexto['lote_ancora_v103'] = str(sub.iloc[0].get('lote_final_heuristica') or '').strip()
    if len(quadro_heuristica):
        sub_escola = quadro_heuristica[quadro_heuristica['descricao_pagamento'].astype(str).eq('Escola')]
        if len(sub_escola):
            contexto['lote_escola_v103'] = str(sub_escola.iloc[0].get('lote_final_heuristica') or '').strip()
            contexto['pagamento_escola_id'] = str(sub_escola.iloc[0].get('pagamento_id') or '').strip()
        sub_cartao_inicial = quadro_heuristica[(quadro_heuristica['descricao_pagamento'].astype(str).eq('Cartão Azul')) & (quadro_heuristica['data_pagamento'] < DEFAULT_BLOCO_CRITICO_FIM)]
        if len(sub_cartao_inicial):
            contexto['lote_cartao_inicial_v103'] = str(sub_cartao_inicial.iloc[0].get('lote_final_heuristica') or '').strip()
    return contexto


def _penalidade_politica(
    politica_id: str,
    candidato: dict[str, Any],
    pagamento: dict[str, Any],
    *,
    contexto: dict[str, Any],
    data_ancora: date,
) -> tuple[float, str]:
    lot = _rotulo_fonte(candidato)
    desc = str(pagamento.get('descricao') or '')
    data_pagamento = pagamento.get('data')
    valor = _safe_float(pagamento.get('valor'))
    pre_anchor = bool(isinstance(data_pagamento, date) and data_pagamento < data_ancora)
    if politica_id == 'reserva_lote_cartao_inicial_pos_cartao_inicial':
        lote_prioritario = contexto.get('lote_cartao_inicial_v103') or ''
        if pre_anchor and lot == lote_prioritario and desc != 'Cartão Azul':
            return 3200.0 + min(valor, 1200.0), 'penalização para preservar o lote principal usado no primeiro Cartão Azul até a âncora de 20/05.'
        if pre_anchor and lot == (contexto.get('lote_ancora_v102') or ''):
            return -120.0, 'bônus leve para usar a válvula de escape observada na V102.'
    if politica_id == 'reserva_lote_ancora_e_escola':
        lote_ancora = contexto.get('lote_ancora_v103') or contexto.get('lote_ancora_v102') or ''
        lote_escola = contexto.get('lote_escola_v103') or ''
        if pre_anchor and lot == lote_ancora and desc != 'Cartão Azul':
            return 4200.0 + min(valor, 1400.0), 'penalização para preservar o lote que melhor cobriu a âncora na baseline vigente.'
        if pre_anchor and lot == lote_escola and desc != 'Escola':
            return 1700.0 + min(valor, 600.0), 'penalização para preservar o lote crítico da Escola antes de 12/05.'
        if pre_anchor and lot == (contexto.get('lote_ancora_v102') or ''):
            return -150.0, 'bônus leve para deslocar pagamentos menores para a fonte menos estratégica observada na V102.'
    if politica_id == 'reserva_dupla_ancora':
        lote_ancora = contexto.get('lote_ancora_v103') or ''
        lote_inicial = contexto.get('lote_cartao_inicial_v103') or ''
        lote_escola = contexto.get('lote_escola_v103') or ''
        if pre_anchor and lot == lote_ancora and desc != 'Cartão Azul':
            return 5200.0 + min(valor, 1600.0), 'penalização forte para preservar o lote da âncora de 20/05.'
        if pre_anchor and lot == lote_inicial and desc != 'Cartão Azul':
            return 2400.0 + min(valor, 800.0), 'penalização moderada para não exaurir cedo o lote do primeiro Cartão Azul.'
        if pre_anchor and lot == lote_escola and desc not in {'Escola', 'Cartão Azul'}:
            return 1800.0 + min(valor, 600.0), 'penalização para manter o lote da Escola disponível até 12/05.'
        if pre_anchor and lot == (contexto.get('lote_ancora_v102') or ''):
            return -180.0, 'bônus leve para usar a alternativa operacional menos estratégica antes da âncora.'
    return 0.0, ''


def _simular_politica_customizada(
    politica_id: str,
    politica_descricao: str,
    pagamentos_bloco: list[dict[str, Any]],
    *,
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, dict[str, Any]],
    mapa_lotes_base: dict[str, Any],
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    contexto_politicas: dict[str, Any],
    data_ancora: date,
    tolerancia_monetaria: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    mapa_lotes = {k: deepcopy(v) for k, v in mapa_lotes_base.items()}
    consumo_generico: dict[str, float] = {}
    registros: list[dict[str, Any]] = []
    primeira_sem_cobertura = None
    primeira_troca_preventiva = None

    for pagamento in pagamentos_bloco:
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
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
        pool = [c for c in elegiveis if bool(c.get('pagamento_totalmente_coberto'))] or elegiveis
        if not pool:
            escolhido = {
                'tipo_fonte_escolhida': '',
                'lote_id': '',
                'fonte_base_escolhida': '',
                'fonte_escolhida_id': '',
                'valor_disponivel': 0.0,
                'saldo_antes_dinamico': 0.0,
                'pagamento_totalmente_coberto': False,
                'custo_economico_proxy': None,
            }
            score_ajustado = None
            observacao_criterio = 'sem candidatos elegíveis após abatimento sequencial no bloco crítico.'
        else:
            melhores = []
            for candidato in pool:
                score_base, detalhes = _score_proxy_economico_por_versao('v3', candidato, valor_pagamento=valor_pagamento)
                penalidade, motivo_penalidade = _penalidade_politica(
                    politica_id,
                    candidato,
                    pagamento,
                    contexto=contexto_politicas,
                    data_ancora=data_ancora,
                )
                score_final = score_base + penalidade
                melhores.append((
                    round(score_final, 6),
                    _criterio_desempate(candidato, valor_pagamento),
                    candidato,
                    round(score_base, 6),
                    round(penalidade, 6),
                    motivo_penalidade,
                    detalhes,
                ))
            melhores.sort(key=lambda item: (item[0], item[1]))
            score_ajustado, _, escolhido, score_base_final, penalidade_final, motivo_penalidade_final, detalhes_final = melhores[0]
            escolhido['custo_economico_proxy'] = score_base_final
            escolhido['proxy_componentes'] = detalhes_final
            observacao_criterio = f'proxy_v3 ajustado pela política {politica_id}; penalidade={penalidade_final:.4f}. {motivo_penalidade_final}'.strip()

        movimento = _simular_saque(
            escolhido,
            valor_pagamento=valor_pagamento,
            mapa_lotes=mapa_lotes,
            consumo_generico=consumo_generico,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        cobertura_integral = bool(movimento['pagamento_totalmente_coberto_planejamento'])
        evento_ancora = bool(pagamento_id == contexto_politicas.get('pagamento_ancora_id'))
        lote_v103 = ''
        lote_v102 = ''
        mudou_vs_v103 = False

        if not cobertura_integral and primeira_sem_cobertura is None:
            primeira_sem_cobertura = {
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'valor_pagamento': valor_pagamento,
                'lote_final': movimento['lote_final_planejamento'],
            }

        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'politica_id': politica_id,
            'politica_descricao': politica_descricao,
            'evento_ancora': evento_ancora,
            'lote_final_planejamento': movimento['lote_final_planejamento'],
            'tipo_fonte_final': movimento['tipo_fonte_final'],
            'fonte_final_id': movimento['fonte_final_id'],
            'score_planejamento': round(score_ajustado, 4) if score_ajustado is not None else None,
            'status_planejamento': 'coberto pelo planejamento local' if cobertura_integral else 'sem cobertura no planejamento local',
            'saldo_antes_planejamento': movimento['saldo_antes_planejamento'],
            'bruto_planejamento': movimento['bruto_planejamento'],
            'imposto_planejamento': movimento['imposto_planejamento'],
            'liquido_planejamento': movimento['liquido_planejamento'],
            'saldo_remanescente_planejamento': movimento['saldo_remanescente_planejamento'],
            'pagamento_totalmente_coberto_planejamento': cobertura_integral,
            'observacao_planejamento': observacao_criterio,
            'mudou_vs_v103': mudou_vs_v103,
        })

    quadro = pd.DataFrame(registros)
    anchor_row = quadro[quadro['evento_ancora'] == True].copy()
    anchor_liq = _safe_round(anchor_row.iloc[0].get('liquido_planejamento')) if len(anchor_row) else 0.0
    anchor_val = _safe_round(anchor_row.iloc[0].get('valor_pagamento')) if len(anchor_row) else 0.0
    anchor_def = round(max(anchor_val - anchor_liq, 0.0), 2)
    total_cobertos = int(quadro['pagamento_totalmente_coberto_planejamento'].sum()) if len(quadro) else 0
    deficit_total = round(sum(max(_safe_float(row.get('valor_pagamento')) - _safe_float(row.get('liquido_planejamento')), 0.0) for row in quadro.to_dict(orient='records')), 2)
    residual_total = round(sum(_safe_float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)) for lote in mapa_lotes.values()), 2)
    resumo = {
        'politica_id': politica_id,
        'politica_descricao': politica_descricao,
        'pagamentos_bloco': int(len(quadro)),
        'pagamentos_cobertos_bloco': total_cobertos,
        'deficit_total_bloco': deficit_total,
        'liquido_coberto_ancora': anchor_liq,
        'deficit_ancora': anchor_def,
        'cobertura_integral_ancora': bool(anchor_liq + tolerancia_monetaria >= anchor_val),
        'residual_total_pos_bloco': residual_total,
        'primeira_sem_cobertura_data': primeira_sem_cobertura.get('data_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_pagamento': primeira_sem_cobertura.get('descricao_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_lote_final': primeira_sem_cobertura.get('lote_final') if primeira_sem_cobertura else None,
        'trocas_preventivas_planejamento': 0,
    }
    return quadro, resumo


def _normalizar_quadro_referencia(
    quadro: pd.DataFrame,
    *,
    politica_id: str,
    politica_descricao: str,
    lote_col: str,
    tipo_col: str,
    score_col: str,
    status_col: str,
    saldo_col: str,
    bruto_col: str,
    imposto_col: str,
    liquido_col: str,
    rem_col: str,
    cobertura_col: str,
    anchor_payment_id: str,
) -> pd.DataFrame:
    linhas = []
    for row in quadro.to_dict(orient='records'):
        linhas.append({
            'pagamento_id': str(row.get('pagamento_id') or '').strip(),
            'data_pagamento': row.get('data_pagamento'),
            'descricao_pagamento': str(row.get('descricao_pagamento') or ''),
            'valor_pagamento': _safe_round(row.get('valor_pagamento')),
            'politica_id': politica_id,
            'politica_descricao': politica_descricao,
            'evento_ancora': bool(str(row.get('pagamento_id') or '').strip() == anchor_payment_id),
            'lote_final_planejamento': str(row.get(lote_col) or '').strip(),
            'tipo_fonte_final': str(row.get(tipo_col) or '').strip(),
            'fonte_final_id': str(row.get('fonte_final_id') or row.get('fonte_base_escolhida') or ''),
            'score_planejamento': round(_safe_float(row.get(score_col)), 4) if row.get(score_col) is not None else None,
            'status_planejamento': str(row.get(status_col) or '').strip(),
            'saldo_antes_planejamento': _safe_round(row.get(saldo_col)),
            'bruto_planejamento': _safe_round(row.get(bruto_col)),
            'imposto_planejamento': _safe_round(row.get(imposto_col)),
            'liquido_planejamento': _safe_round(row.get(liquido_col)),
            'saldo_remanescente_planejamento': _safe_round(row.get(rem_col)),
            'pagamento_totalmente_coberto_planejamento': bool(row.get(cobertura_col)),
            'observacao_planejamento': f'política de referência {politica_id}; decisão reproduzida a partir da baseline anterior.',
            'mudou_vs_v103': False,
        })
    return pd.DataFrame(linhas)


def _resumo_de_quadro(quadro: pd.DataFrame, *, tolerancia_monetaria: float) -> dict[str, Any]:
    if len(quadro) == 0:
        return {
            'pagamentos_bloco': 0,
            'pagamentos_cobertos_bloco': 0,
            'deficit_total_bloco': 0.0,
            'liquido_coberto_ancora': 0.0,
            'deficit_ancora': 0.0,
            'cobertura_integral_ancora': False,
            'residual_total_pos_bloco': 0.0,
            'primeira_sem_cobertura_data': None,
            'primeira_sem_cobertura_pagamento': None,
            'primeira_sem_cobertura_lote_final': None,
            'trocas_preventivas_planejamento': 0,
        }
    anchor = quadro[quadro['evento_ancora'] == True].copy()
    anchor_val = _safe_round(anchor.iloc[0].get('valor_pagamento')) if len(anchor) else 0.0
    anchor_liq = _safe_round(anchor.iloc[0].get('liquido_planejamento')) if len(anchor) else 0.0
    primeira_sem = quadro[quadro['pagamento_totalmente_coberto_planejamento'] == False].copy()
    primeira_sem = primeira_sem.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable') if len(primeira_sem) else primeira_sem
    return {
        'pagamentos_bloco': int(len(quadro)),
        'pagamentos_cobertos_bloco': int(quadro['pagamento_totalmente_coberto_planejamento'].sum()),
        'deficit_total_bloco': round(sum(max(_safe_float(row.get('valor_pagamento')) - _safe_float(row.get('liquido_planejamento')), 0.0) for row in quadro.to_dict(orient='records')), 2),
        'liquido_coberto_ancora': anchor_liq,
        'deficit_ancora': round(max(anchor_val - anchor_liq, 0.0), 2),
        'cobertura_integral_ancora': bool(anchor_liq + tolerancia_monetaria >= anchor_val),
        'residual_total_pos_bloco': round(sum(_safe_float(v) for v in quadro['saldo_remanescente_planejamento'].tolist()), 2),
        'primeira_sem_cobertura_data': primeira_sem.iloc[0].get('data_pagamento') if len(primeira_sem) else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.iloc[0].get('descricao_pagamento') if len(primeira_sem) else None,
        'primeira_sem_cobertura_lote_final': primeira_sem.iloc[0].get('lote_final_planejamento') if len(primeira_sem) else None,
        'trocas_preventivas_planejamento': 0,
    }


def _ordenar_politicas(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -int(bool(item.get('cobertura_integral_ancora'))),
        -_safe_float(item.get('liquido_coberto_ancora')),
        -int(item.get('pagamentos_cobertos_bloco') or 0),
        _safe_float(item.get('deficit_total_bloco')),
        -_safe_float(item.get('residual_total_pos_bloco')),
        str(item.get('politica_id') or ''),
    )


def carregar_planejamento_conjunto_local_bloco_critico_v1(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    replay_passado,
    reescolha_dinamica_pos_quebra,
    heuristica_conjunta_parcial_bloco_critico,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    bloco_critico_inicio: date = DEFAULT_BLOCO_CRITICO_INICIO,
    bloco_critico_fim: date = DEFAULT_BLOCO_CRITICO_FIM,
    tolerancia_monetaria: float = 0.01,
) -> PacotePlanejamentoConjuntoLocalBlocoCriticoV1:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    pagamentos_bloco_df = pagamentos_alvo[(pagamentos_alvo['data'] >= bloco_critico_inicio) & (pagamentos_alvo['data'] <= bloco_critico_fim)].copy()
    pagamentos_bloco_df = pagamentos_bloco_df.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    colunas_planejamento = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'politica_id', 'politica_descricao',
        'evento_ancora', 'lote_final_planejamento', 'tipo_fonte_final', 'fonte_final_id', 'score_planejamento',
        'status_planejamento', 'saldo_antes_planejamento', 'bruto_planejamento', 'imposto_planejamento',
        'liquido_planejamento', 'saldo_remanescente_planejamento', 'pagamento_totalmente_coberto_planejamento',
        'observacao_planejamento', 'mudou_vs_v103',
    ]
    if len(pagamentos_bloco_df) == 0:
        return PacotePlanejamentoConjuntoLocalBlocoCriticoV1(
            quadro_planejamento_conjunto_local=pd.DataFrame(columns=colunas_planejamento),
            quadro_comparativo_politicas=pd.DataFrame(),
            auditoria={'validacao': {'ok': False, 'erros': ['planejamento_conjunto_sem_pagamentos_no_bloco'], 'avisos': []}, 'resumo': {'pagamentos_bloco': 0}},
        )

    evento_ancora = _evento_ancora(pagamentos_bloco_df, data_alvo=bloco_critico_fim)
    pagamento_ancora_id = str(evento_ancora.get('despesa_id') or '').strip() if evento_ancora else ''
    data_ancora = evento_ancora.get('data') if evento_ancora else bloco_critico_fim

    quadro_reescolha_bloco = reescolha_dinamica_pos_quebra.quadro_reescolha_dinamica.copy() if reescolha_dinamica_pos_quebra is not None else pd.DataFrame()
    quadro_reescolha_bloco = quadro_reescolha_bloco[(quadro_reescolha_bloco['data_pagamento'] >= bloco_critico_inicio) & (quadro_reescolha_bloco['data_pagamento'] <= bloco_critico_fim)].copy() if len(quadro_reescolha_bloco) else quadro_reescolha_bloco
    quadro_heuristica_bloco = heuristica_conjunta_parcial_bloco_critico.quadro_heuristica_conjunta_parcial.copy() if heuristica_conjunta_parcial_bloco_critico is not None else pd.DataFrame()
    quadro_heuristica_bloco = quadro_heuristica_bloco[(quadro_heuristica_bloco['data_pagamento'] >= bloco_critico_inicio) & (quadro_heuristica_bloco['data_pagamento'] <= bloco_critico_fim)].copy() if len(quadro_heuristica_bloco) else quadro_heuristica_bloco

    quadro_v102 = _normalizar_quadro_referencia(
        quadro_reescolha_bloco,
        politica_id='v102_referencia',
        politica_descricao='Recomputação sequencial preventiva da V102',
        lote_col='lote_final_dinamico',
        tipo_col='tipo_fonte_final',
        score_col='score_proxy_final',
        status_col='status_pos_reescolha',
        saldo_col='saldo_antes_dinamico',
        bruto_col='bruto_dinamico',
        imposto_col='imposto_dinamico',
        liquido_col='liquido_dinamico',
        rem_col='saldo_remanescente_dinamico',
        cobertura_col='pagamento_totalmente_coberto_dinamico',
        anchor_payment_id=pagamento_ancora_id,
    ) if len(quadro_reescolha_bloco) else pd.DataFrame(columns=colunas_planejamento)
    quadro_v103 = _normalizar_quadro_referencia(
        quadro_heuristica_bloco,
        politica_id='v103_referencia',
        politica_descricao='Heurística conjunta parcial da V103',
        lote_col='lote_final_heuristica',
        tipo_col='tipo_fonte_final',
        score_col='score_proxy_ajustado_heuristica',
        status_col='status_heuristica',
        saldo_col='saldo_antes_heuristica',
        bruto_col='bruto_heuristica',
        imposto_col='imposto_heuristica',
        liquido_col='liquido_heuristica',
        rem_col='saldo_remanescente_heuristica',
        cobertura_col='pagamento_totalmente_coberto_heuristica',
        anchor_payment_id=pagamento_ancora_id,
    ) if len(quadro_heuristica_bloco) else pd.DataFrame(columns=colunas_planejamento)

    contexto_politicas = _montar_contexto_politicas(quadro_reescolha_bloco, quadro_heuristica_bloco, evento_ancora)

    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_lotes_base = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    pagamentos_bloco = pagamentos_bloco_df.to_dict(orient='records')

    custom_specs = [
        ('reserva_lote_cartao_inicial_pos_cartao_inicial', 'Preservar o lote do primeiro Cartão Azul e deslocar pagamentos menores antes de 20/05'),
        ('reserva_lote_ancora_e_escola', 'Preservar o lote da âncora de 20/05 e o lote crítico da Escola dentro do bloco'),
        ('reserva_dupla_ancora', 'Preservar simultaneamente o lote da âncora, o lote do primeiro Cartão Azul e o lote da Escola'),
    ]
    quadros_custom: dict[str, pd.DataFrame] = {}
    resumos_custom: list[dict[str, Any]] = []
    for politica_id, politica_descricao in custom_specs:
        quadro_custom, resumo_custom = _simular_politica_customizada(
            politica_id,
            politica_descricao,
            pagamentos_bloco,
            quadro_saldo=quadro_saldo,
            quadro_fontes=quadro_fontes,
            mapa_produtos_proxy=mapa_produtos_proxy,
            mapa_lotes_base=mapa_lotes_base,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            contexto_politicas=contexto_politicas,
            data_ancora=data_ancora,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        quadros_custom[politica_id] = quadro_custom
        resumos_custom.append(resumo_custom)

    resumos = []
    if len(quadro_v102):
        resumo_v102 = _resumo_de_quadro(quadro_v102, tolerancia_monetaria=tolerancia_monetaria)
        resumo_v102.update({'politica_id': 'v102_referencia', 'politica_descricao': 'Recomputação sequencial preventiva da V102'})
        resumos.append(resumo_v102)
    if len(quadro_v103):
        resumo_v103 = _resumo_de_quadro(quadro_v103, tolerancia_monetaria=tolerancia_monetaria)
        resumo_v103.update({'politica_id': 'v103_referencia', 'politica_descricao': 'Heurística conjunta parcial da V103'})
        resumos.append(resumo_v103)
    resumos.extend(resumos_custom)

    mapa_v103 = {str(row.get('pagamento_id') or '').strip(): row for row in quadro_v103.to_dict(orient='records')} if len(quadro_v103) else {}
    for quadro_custom in quadros_custom.values():
        if len(quadro_custom):
            quadro_custom['mudou_vs_v103'] = False
    for pid, row_v103 in mapa_v103.items():
        lote_v103 = str(row_v103.get('lote_final_planejamento') or '')
        for quadro_custom in quadros_custom.values():
            if len(quadro_custom):
                mask = quadro_custom['pagamento_id'].astype(str).eq(pid)
                if mask.any():
                    quadro_custom.loc[mask, 'mudou_vs_v103'] = quadro_custom.loc[mask, 'lote_final_planejamento'].astype(str) != lote_v103
    if len(quadro_v102) and mapa_v103:
        quadro_v102['mudou_vs_v103'] = quadro_v102['pagamento_id'].astype(str).map(lambda pid: str(quadro_v102.loc[quadro_v102['pagamento_id'].astype(str).eq(pid), 'lote_final_planejamento'].iloc[0]) != str(mapa_v103.get(str(pid), {}).get('lote_final_planejamento') or ''))
    if len(quadro_v103):
        quadro_v103['mudou_vs_v103'] = False

    for resumo in resumos:
        politica_id = str(resumo.get('politica_id') or '')
        quadro_ref = quadros_custom.get(politica_id)
        if politica_id == 'v102_referencia':
            quadro_ref = quadro_v102
        elif politica_id == 'v103_referencia':
            quadro_ref = quadro_v103
        resumo['mudancas_vs_v103'] = int(quadro_ref['mudou_vs_v103'].sum()) if quadro_ref is not None and len(quadro_ref) else 0
        resumo['delta_liquido_ancora_vs_v102'] = round(_safe_float(resumo.get('liquido_coberto_ancora')) - _safe_float(next((r.get('liquido_coberto_ancora') for r in resumos if r.get('politica_id') == 'v102_referencia'), 0.0)), 2)
        resumo['delta_liquido_ancora_vs_v103'] = round(_safe_float(resumo.get('liquido_coberto_ancora')) - _safe_float(next((r.get('liquido_coberto_ancora') for r in resumos if r.get('politica_id') == 'v103_referencia'), 0.0)), 2)

    quadro_comparativo = pd.DataFrame(resumos)
    quadro_comparativo = quadro_comparativo.sort_values(by=['cobertura_integral_ancora', 'liquido_coberto_ancora', 'pagamentos_cobertos_bloco', 'deficit_total_bloco', 'residual_total_pos_bloco', 'politica_id'], ascending=[False, False, False, True, False, True], kind='stable').reset_index(drop=True)

    politica_escolhida = quadro_comparativo.iloc[0].to_dict() if len(quadro_comparativo) else {}
    politica_escolhida_id = str(politica_escolhida.get('politica_id') or '')
    if politica_escolhida_id == 'v102_referencia':
        quadro_escolhido = quadro_v102.copy()
    elif politica_escolhida_id == 'v103_referencia':
        quadro_escolhido = quadro_v103.copy()
    else:
        quadro_escolhido = quadros_custom.get(politica_escolhida_id, pd.DataFrame()).copy()
    if len(quadro_escolhido) == 0:
        quadro_escolhido = pd.DataFrame(columns=colunas_planejamento)

    mapa_v102 = {str(row.get('pagamento_id') or '').strip(): row for row in quadro_v102.to_dict(orient='records')} if len(quadro_v102) else {}
    for pid, row in {str(r.get('pagamento_id') or '').strip(): r for r in quadro_escolhido.to_dict(orient='records')}.items():
        pass
    if len(quadro_escolhido):
        def _obs_extra(row):
            pid = str(row.get('pagamento_id') or '').strip()
            lote_v103 = str(mapa_v103.get(pid, {}).get('lote_final_planejamento') or '') if mapa_v103 else ''
            lote_v102 = str(mapa_v102.get(pid, {}).get('lote_final_planejamento') or '') if mapa_v102 else ''
            return f"v102={lote_v102 or '-'} | v103={lote_v103 or '-'} | escolhida={row.get('lote_final_planejamento') or '-'}"
        quadro_escolhido['observacao_planejamento'] = quadro_escolhido.apply(lambda row: (str(row.get('observacao_planejamento') or '') + ' ' + _obs_extra(row)).strip(), axis=1)

    amostra_comparativo = []
    for _, row in quadro_comparativo.head(6).iterrows():
        amostra_comparativo.append({
            'Política': row.get('politica_id'),
            'Liquidez no Cartão Azul 20/05': _safe_round(row.get('liquido_coberto_ancora')),
            'Déficit do Cartão Azul 20/05': _safe_round(row.get('deficit_ancora')),
            'Pagamentos cobertos no bloco': int(row.get('pagamentos_cobertos_bloco') or 0),
            'Déficit total do bloco': _safe_round(row.get('deficit_total_bloco')),
            'Mudanças vs V103': int(row.get('mudancas_vs_v103') or 0),
        })
    amostra_mudancas = []
    if len(quadro_escolhido):
        sub_m = quadro_escolhido[quadro_escolhido['mudou_vs_v103'] == True].copy().sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable')
        for _, row in sub_m.head(10).iterrows():
            pid = str(row.get('pagamento_id') or '').strip()
            amostra_mudancas.append({
                'Data': row.get('data_pagamento'),
                'Descrição': row.get('descricao_pagamento'),
                'Valor': _safe_round(row.get('valor_pagamento')),
                'Lote V103': str(mapa_v103.get(pid, {}).get('lote_final_planejamento') or ''),
                'Lote planejado': str(row.get('lote_final_planejamento') or ''),
                'Status planejamento': str(row.get('status_planejamento') or ''),
            })

    resumo = {
        'pagamentos_no_bloco_critico': int(len(pagamentos_bloco_df)),
        'politicas_avaliadas': int(len(quadro_comparativo)),
        'politica_escolhida': politica_escolhida.get('politica_id'),
        'descricao_politica_escolhida': politica_escolhida.get('politica_descricao'),
        'evento_ancora_data': evento_ancora.get('data') if evento_ancora else None,
        'evento_ancora_pagamento': evento_ancora.get('descricao') if evento_ancora else None,
        'evento_ancora_valor': _safe_round(evento_ancora.get('valor')) if evento_ancora else None,
        'liquido_coberto_ancora_escolhida': _safe_round(politica_escolhida.get('liquido_coberto_ancora')),
        'deficit_ancora_escolhida': _safe_round(politica_escolhida.get('deficit_ancora')),
        'cobertura_integral_ancora_escolhida': bool(politica_escolhida.get('cobertura_integral_ancora')),
        'pagamentos_cobertos_bloco_escolhida': int(politica_escolhida.get('pagamentos_cobertos_bloco') or 0),
        'deficit_total_bloco_escolhida': _safe_round(politica_escolhida.get('deficit_total_bloco')),
        'delta_liquido_ancora_vs_v102': _safe_round(politica_escolhida.get('delta_liquido_ancora_vs_v102')),
        'delta_liquido_ancora_vs_v103': _safe_round(politica_escolhida.get('delta_liquido_ancora_vs_v103')),
        'mudancas_vs_v103_escolhida': int(politica_escolhida.get('mudancas_vs_v103') or 0),
        'primeira_sem_cobertura_data_escolhida': politica_escolhida.get('primeira_sem_cobertura_data'),
        'primeira_sem_cobertura_pagamento_escolhida': politica_escolhida.get('primeira_sem_cobertura_pagamento'),
        'primeira_sem_cobertura_lote_escolhida': politica_escolhida.get('primeira_sem_cobertura_lote_final'),
        'ganho_material_vs_v103': bool(_safe_float(politica_escolhida.get('liquido_coberto_ancora')) > _safe_float(next((r.get('liquido_coberto_ancora') for r in resumos if r.get('politica_id') == 'v103_referencia'), 0.0)) + tolerancia_monetaria),
    }

    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_comparativo_politicas': amostra_comparativo,
        'amostra_mudancas_vs_v103': amostra_mudancas,
    }
    return PacotePlanejamentoConjuntoLocalBlocoCriticoV1(
        quadro_planejamento_conjunto_local=quadro_escolhido.reindex(columns=colunas_planejamento),
        quadro_comparativo_politicas=quadro_comparativo,
        auditoria=auditoria,
    )
