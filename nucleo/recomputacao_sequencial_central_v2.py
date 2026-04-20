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
    _score_proxy_economico_por_versao,
)
from nucleo.recomputacao_sequencial_central_v1 import (
    _coerce_date,
    _perfil_pagamento_operacional,
    _patrimonio_terminal_proxy,
    _peso_horizonte_protegida,
    _peso_subclasse_protegida,
    _rotulo_fonte,
    _simular_movimento_candidato,
)
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos


@dataclass(slots=True)
class PacoteRecomputacaoSequencialCentralV2:
    quadro_recomputacao_sequencial_central: pd.DataFrame
    auditoria: dict[str, Any]


def _reserva_critica_por_fonte(
    *,
    candidato: dict[str, Any],
    pagamentos_futuros: list[dict[str, Any]],
    data_pagamento_atual: date,
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, Any],
    mapa_lotes: dict[str, Any],
    consumo_generico: dict[str, float],
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    tolerancia_monetaria: float,
) -> dict[str, Any]:
    fonte_id = str(candidato.get('fonte_escolhida_id') or '').strip()
    referencia_fonte = _rotulo_fonte(candidato)
    saldo_fonte = round(float(candidato.get('saldo_antes_dinamico') or candidato.get('valor_disponivel') or 0.0), 2)
    if not referencia_fonte or saldo_fonte <= tolerancia_monetaria:
        return {
            'demanda_marginal_protegida_fonte_7d': 0.0,
            'demanda_marginal_protegida_fonte_14d': 0.0,
            'demanda_marginal_protegida_fonte_21d': 0.0,
            'reserva_critica_total_fonte': 0.0,
            'orcamento_livre_apos_reserva_fonte': saldo_fonte,
            'fonte_critica_para_protegida_futura': False,
            'pagamentos_protegidos_dependentes_fonte': 0,
            'fonte_critica_referencias': '',
        }

    bruto_7 = 0.0
    bruto_14 = 0.0
    bruto_21 = 0.0
    ponderada_total = 0.0
    dependentes = 0
    refs: list[str] = []

    for pagamento in pagamentos_futuros:
        if str(pagamento.get('classe_pagamento_operacional') or '') != 'PROTEGIDA':
            continue
        data_pagamento = _coerce_date(pagamento.get('data'))
        if data_pagamento is None:
            continue
        dias = (data_pagamento - data_pagamento_atual).days
        if dias < 0 or dias > 21:
            continue

        futuros_base = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        futuros = _ajustar_candidatos_dinamicos(
            futuros_base,
            valor_pagamento=round(float(pagamento.get('valor') or 0.0), 2),
            mapa_lotes=mapa_lotes,
            consumo_generico=consumo_generico,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )
        if not futuros:
            continue
        saldo_alvo = 0.0
        melhor_outra_capacidade = 0.0
        for futuro in futuros:
            saldo_item = round(float(futuro.get('saldo_antes_dinamico') or futuro.get('valor_disponivel') or 0.0), 2)
            if saldo_item <= tolerancia_monetaria:
                continue
            if _rotulo_fonte(futuro) == referencia_fonte:
                saldo_alvo = max(saldo_alvo, saldo_item)
            else:
                melhor_outra_capacidade = max(melhor_outra_capacidade, saldo_item)
        if saldo_alvo <= tolerancia_monetaria:
            continue
        valor_futuro = round(float(pagamento.get('valor') or 0.0), 2)
        demanda_marginal = round(max(min(saldo_alvo, valor_futuro - melhor_outra_capacidade), 0.0), 2)
        if demanda_marginal <= tolerancia_monetaria:
            continue
        dependentes += 1
        subclasse = str(pagamento.get('subclasse_pagamento_operacional') or '')
        peso = _peso_subclasse_protegida(subclasse) * _peso_horizonte_protegida(dias)
        ponderada_total += demanda_marginal * peso
        if dias <= 7:
            bruto_7 += demanda_marginal
        if dias <= 14:
            bruto_14 += demanda_marginal
        if dias <= 21:
            bruto_21 += demanda_marginal
        if len(refs) < 3:
            refs.append(f"{pagamento.get('descricao') or ''} ({data_pagamento.strftime('%d/%m')})")

    demanda_7 = round(min(saldo_fonte, bruto_7), 2)
    demanda_14 = round(min(saldo_fonte, bruto_14), 2)
    demanda_21 = round(min(saldo_fonte, bruto_21), 2)
    reserva_total = round(min(saldo_fonte, ponderada_total), 2)
    livre = round(max(saldo_fonte - reserva_total, 0.0), 2)
    return {
        'demanda_marginal_protegida_fonte_7d': demanda_7,
        'demanda_marginal_protegida_fonte_14d': demanda_14,
        'demanda_marginal_protegida_fonte_21d': demanda_21,
        'reserva_critica_total_fonte': reserva_total,
        'orcamento_livre_apos_reserva_fonte': livre,
        'fonte_critica_para_protegida_futura': bool(reserva_total > 0.0),
        'pagamentos_protegidos_dependentes_fonte': dependentes,
        'fonte_critica_referencias': '; '.join(refs),
    }


def _comparador_central_v2(
    *,
    classe_pagamento: str,
    subclasse_pagamento: str,
    valor_pagamento: float,
    candidato: dict[str, Any],
    candidatos_ajustados: list[dict[str, Any]],
    movimento_simulado: dict[str, Any],
    data_referencia: date,
    mapa_lotes: dict[str, Any],
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    proxy_version: str,
    reserva_fonte: dict[str, Any],
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    score_proxy, detalhes = _score_proxy_economico_por_versao(proxy_version, candidato, valor_pagamento=valor_pagamento)
    liquido = round(float(movimento_simulado.get('liquido_central') or 0.0), 2)
    deficit = round(max(valor_pagamento - liquido, 0.0), 2)
    uncovered = 1 if deficit > 0.01 else 0
    violacao_protegida = 1 if classe_pagamento == 'PROTEGIDA' and uncovered else 0
    severidade_protegida = deficit if classe_pagamento == 'PROTEGIDA' else 0.0
    patrimonio = _patrimonio_terminal_proxy(
        candidatos_ajustados,
        candidato_escolhido=candidato,
        movimento_simulado=movimento_simulado,
        data_referencia=data_referencia,
        mapa_lotes=mapa_lotes,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
    )
    penalidade_estrategica = round(
        float(detalhes.get('penalidade_papel_estrategico') or 0.0)
        + float(detalhes.get('penalidade_destruicao_estrategica') or 0.0),
        4,
    )
    penalidade_fragmentacao = round(
        float(detalhes.get('penalidade_fragmentacao_residual') or 0.0)
        + float(detalhes.get('penalidade_fotografia') or 0.0)
        + float(detalhes.get('penalidade_horizonte_curto') or 0.0),
        4,
    )
    consumo_efetivo = round(float(movimento_simulado.get('patrimonio_delta') or liquido), 2)
    orcamento_livre = round(float(reserva_fonte.get('orcamento_livre_apos_reserva_fonte') or 0.0), 2)
    excesso_sobre_reserva = round(max(consumo_efetivo - orcamento_livre, 0.0), 2)
    multiplicador = {
        'PROTEGIDA': 0.55,
        'SEMIPROTEGIDA': 1.05,
        'FLEXIVEL': 1.55,
    }.get(classe_pagamento, 1.0)
    penalidade_reserva = round(excesso_sobre_reserva * multiplicador, 4)

    if classe_pagamento == 'PROTEGIDA':
        comparador = (
            violacao_protegida,
            round(severidade_protegida, 2),
            round(deficit, 2),
            uncovered,
            round(penalidade_reserva, 4),
            -patrimonio,
            penalidade_estrategica,
            penalidade_fragmentacao,
            round(float(score_proxy or 0.0), 4),
            str(candidato.get('fonte_escolhida_id') or ''),
        )
    else:
        comparador = (
            violacao_protegida,
            round(penalidade_reserva, 4),
            round(deficit, 2),
            uncovered,
            -patrimonio,
            penalidade_estrategica,
            penalidade_fragmentacao,
            round(float(score_proxy or 0.0), 4),
            str(candidato.get('fonte_escolhida_id') or ''),
        )
    diagnostico = {
        'classe_pagamento_operacional': classe_pagamento,
        'subclasse_pagamento_operacional': subclasse_pagamento,
        'violacao_protegida': violacao_protegida,
        'severidade_protegida': round(severidade_protegida, 2),
        'deficit_liquido_total': round(deficit, 2),
        'pagamento_sem_cobertura_integral': uncovered,
        'patrimonio_terminal_proxy': patrimonio,
        'penalidade_estrategica_central': penalidade_estrategica,
        'penalidade_fragmentacao_central': penalidade_fragmentacao,
        'penalidade_reserva_critica_fonte': penalidade_reserva,
        'excesso_sobre_reserva_critica': excesso_sobre_reserva,
        'reserva_critica_total_fonte': round(float(reserva_fonte.get('reserva_critica_total_fonte') or 0.0), 2),
        'orcamento_livre_apos_reserva_fonte': round(float(reserva_fonte.get('orcamento_livre_apos_reserva_fonte') or 0.0), 2),
        'demanda_marginal_protegida_fonte_7d': round(float(reserva_fonte.get('demanda_marginal_protegida_fonte_7d') or 0.0), 2),
        'demanda_marginal_protegida_fonte_14d': round(float(reserva_fonte.get('demanda_marginal_protegida_fonte_14d') or 0.0), 2),
        'demanda_marginal_protegida_fonte_21d': round(float(reserva_fonte.get('demanda_marginal_protegida_fonte_21d') or 0.0), 2),
        'fonte_critica_para_protegida_futura': bool(reserva_fonte.get('fonte_critica_para_protegida_futura')),
        'pagamentos_protegidos_dependentes_fonte': int(reserva_fonte.get('pagamentos_protegidos_dependentes_fonte') or 0),
        'fonte_critica_referencias': str(reserva_fonte.get('fonte_critica_referencias') or ''),
        'score_proxy_central': round(float(score_proxy or 0.0), 4),
        'detalhes_proxy_componentes': detalhes,
    }
    return comparador, diagnostico


def carregar_recomputacao_sequencial_central_v2(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    decisao_local_v1,
    replay_passado,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
    tolerancia_monetaria: float = 0.01,
) -> PacoteRecomputacaoSequencialCentralV2:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional',
        'subclasse_pagamento_operacional', 'prioridade_intraclasse_operacional', 'lote_sugerido_original',
        'lote_final_central', 'fonte_final_id', 'tipo_fonte_final', 'mudou_vs_decisao_local', 'criterio_central',
        'status_central', 'score_proxy_central', 'violacao_protegida', 'severidade_protegida',
        'deficit_liquido_total', 'pagamento_sem_cobertura_integral', 'patrimonio_terminal_proxy',
        'penalidade_estrategica_central', 'penalidade_fragmentacao_central', 'penalidade_reserva_critica_fonte',
        'excesso_sobre_reserva_critica', 'demanda_marginal_protegida_fonte_7d', 'demanda_marginal_protegida_fonte_14d',
        'demanda_marginal_protegida_fonte_21d', 'reserva_critica_total_fonte', 'orcamento_livre_apos_reserva_fonte',
        'fonte_critica_para_protegida_futura', 'pagamentos_protegidos_dependentes_fonte', 'fonte_critica_referencias',
        'fallback_sem_fonte_viavel', 'saldo_antes_central', 'bruto_central', 'imposto_central', 'liquido_central',
        'saldo_remanescente_central', 'pagamento_totalmente_coberto_central', 'observacao_central',
    ]
    if len(pagamentos_alvo) == 0:
        return PacoteRecomputacaoSequencialCentralV2(pd.DataFrame(columns=colunas), {'validacao': {'ok': False, 'erros': ['recomputacao_sequencial_central_v2_sem_pagamentos_alvo'], 'avisos': []}, 'resumo': {'total_pagamentos_auditados': 0}, 'amostra_mudancas': [], 'amostra_sem_cobertura': []})

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    consumo_generico: dict[str, float] = {}
    mapa_decisao = {
        str(row.get('pagamento_id') or '').strip(): row
        for row in decisao_local_v1.quadro_decisao_local_v1.to_dict(orient='records')
    } if decisao_local_v1 is not None else {}

    pagamentos_alvo = pagamentos_alvo.copy()
    perfis = pagamentos_alvo['descricao'].apply(_perfil_pagamento_operacional)
    pagamentos_alvo['classe_pagamento_operacional'] = perfis.apply(lambda x: x['classe'])
    pagamentos_alvo['subclasse_pagamento_operacional'] = perfis.apply(lambda x: x['subclasse'])
    pagamentos_alvo['prioridade_classe_operacional'] = perfis.apply(lambda x: x['prioridade_classe'])
    pagamentos_alvo['prioridade_intraclasse_operacional'] = perfis.apply(lambda x: x['prioridade_intraclasse'])
    pagamentos_alvo = pagamentos_alvo.sort_values(by=['data', 'prioridade_classe_operacional', 'prioridade_intraclasse_operacional', 'despesa_id'], kind='stable').reset_index(drop=True)
    pagamentos_ordenados = pagamentos_alvo.to_dict(orient='records')

    registros: list[dict[str, Any]] = []
    primeira_sem = None
    primeira_protegida = None
    primeiro_sem_fonte_viavel = None

    for indice, pagamento in enumerate(pagamentos_ordenados):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        classe_pagamento = str(pagamento.get('classe_pagamento_operacional') or '')
        subclasse_pagamento = str(pagamento.get('subclasse_pagamento_operacional') or '')
        prioridade_intraclasse = int(pagamento.get('prioridade_intraclasse_operacional') or 99)
        data_pagamento = _coerce_date(pagamento.get('data')) or data_referencia
        pagamentos_futuros = pagamentos_ordenados[indice + 1:]

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
        if not candidatos:
            continue

        avaliacoes: list[dict[str, Any]] = []
        for candidato in candidatos:
            movimento = _simular_movimento_candidato(
                candidato,
                valor_pagamento=valor_pagamento,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            reserva_fonte = _reserva_critica_por_fonte(
                candidato=candidato,
                pagamentos_futuros=pagamentos_futuros,
                data_pagamento_atual=data_pagamento,
                quadro_saldo=quadro_saldo,
                quadro_fontes=quadro_fontes,
                mapa_produtos_proxy=mapa_produtos_proxy,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            cmp_tuple, diag = _comparador_central_v2(
                classe_pagamento=classe_pagamento,
                subclasse_pagamento=subclasse_pagamento,
                valor_pagamento=valor_pagamento,
                candidato=candidato,
                candidatos_ajustados=candidatos,
                movimento_simulado=movimento,
                data_referencia=data_referencia,
                mapa_lotes=mapa_lotes,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                proxy_version=proxy_version,
                reserva_fonte=reserva_fonte,
            )
            avaliacoes.append({'candidato': candidato, 'movimento': movimento, 'comparador': cmp_tuple, 'diagnostico': diag})

        avaliacoes = sorted(avaliacoes, key=lambda item: item['comparador'])
        melhor = avaliacoes[0]
        escolhido = melhor['candidato']
        melhor_diag = melhor['diagnostico']
        melhor_mov = melhor['movimento']
        max_liquido_potencial = max(round(float(item['movimento'].get('liquido_central') or 0.0), 2) for item in avaliacoes)
        fallback_sem_fonte_viavel = bool(max_liquido_potencial <= tolerancia_monetaria)

        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final = str(escolhido.get('lote_id') or '').strip()
        fonte_final_id = str(escolhido.get('fonte_escolhida_id') or '')
        if not fallback_sem_fonte_viavel:
            if tipo_final == 'lote_resgatavel' and lote_final and melhor_mov.get('mapa_lotes_pos') is not None:
                mapa_lotes[lote_final] = melhor_mov['mapa_lotes_pos']
            elif melhor_mov.get('consumo_generico_pos'):
                for fonte_id_item, consumido in melhor_mov['consumo_generico_pos'].items():
                    consumo_generico[fonte_id_item] = round(float(consumido or 0.0), 2)
        else:
            tipo_final = 'sem_fonte_viavel'
            lote_final = 'sem_fonte_viavel'
            fonte_final_id = ''

        coberto = bool(melhor_mov.get('pagamento_totalmente_coberto_central')) and not fallback_sem_fonte_viavel
        if melhor_diag.get('violacao_protegida') and primeira_protegida is None:
            primeira_protegida = {'Data': pagamento.get('data'), 'Descrição': str(pagamento.get('descricao') or ''), 'Valor': valor_pagamento, 'Lote central': lote_final or _rotulo_fonte(escolhido)}
        if not coberto and primeira_sem is None:
            primeira_sem = {'Data': pagamento.get('data'), 'Descrição': str(pagamento.get('descricao') or ''), 'Valor': valor_pagamento, 'Lote central': lote_final or _rotulo_fonte(escolhido)}
        if fallback_sem_fonte_viavel and primeiro_sem_fonte_viavel is None:
            primeiro_sem_fonte_viavel = {'Data': pagamento.get('data'), 'Descrição': str(pagamento.get('descricao') or ''), 'Valor': valor_pagamento}

        decisao_original = mapa_decisao.get(pagamento_id, {})
        mudou = bool(str(decisao_original.get('fonte_escolhida_id') or '').strip() != fonte_final_id)
        if fallback_sem_fonte_viavel:
            status = 'sem fonte viável na recomputação central'
        elif melhor_diag.get('violacao_protegida'):
            status = 'violacao de pagamento protegida'
        elif coberto:
            status = 'coberto pela recomputacao central'
        elif float(melhor_mov.get('liquido_central') or 0.0) > 0:
            status = 'cobertura parcial na recomputacao central'
        else:
            status = 'sem cobertura na recomputacao central'

        observacao = (
            f"comparador central v2 => protegida={melhor_diag.get('violacao_protegida')}, deficit={melhor_diag.get('deficit_liquido_total'):.2f}, "
            f"sem_integral={melhor_diag.get('pagamento_sem_cobertura_integral')}, patrimonio_proxy={melhor_diag.get('patrimonio_terminal_proxy'):.2f}, "
            f"pen_reserva={melhor_diag.get('penalidade_reserva_critica_fonte'):.4f}, res_total={melhor_diag.get('reserva_critica_total_fonte'):.2f}, "
            f"livre={melhor_diag.get('orcamento_livre_apos_reserva_fonte'):.2f}, d7={melhor_diag.get('demanda_marginal_protegida_fonte_7d'):.2f}, "
            f"d14={melhor_diag.get('demanda_marginal_protegida_fonte_14d'):.2f}, d21={melhor_diag.get('demanda_marginal_protegida_fonte_21d'):.2f}."
        )
        if melhor_diag.get('fonte_critica_referencias'):
            observacao += f" refs: {melhor_diag.get('fonte_critica_referencias')}."
        if fallback_sem_fonte_viavel:
            observacao += ' fallback auditável acionado: sem fonte viável com liquidez positiva no evento.'

        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'classe_pagamento_operacional': classe_pagamento,
            'subclasse_pagamento_operacional': subclasse_pagamento,
            'prioridade_intraclasse_operacional': prioridade_intraclasse,
            'lote_sugerido_original': str(decisao_original.get('lote_id_escolhido') or ''),
            'lote_final_central': lote_final or _rotulo_fonte(escolhido),
            'fonte_final_id': fonte_final_id,
            'tipo_fonte_final': tipo_final,
            'mudou_vs_decisao_local': mudou,
            'criterio_central': 'metrica_canonica_minima_central_v112_reserva_critica_por_fonte',
            'status_central': status,
            'score_proxy_central': melhor_diag.get('score_proxy_central'),
            'violacao_protegida': melhor_diag.get('violacao_protegida'),
            'severidade_protegida': melhor_diag.get('severidade_protegida'),
            'deficit_liquido_total': melhor_diag.get('deficit_liquido_total'),
            'pagamento_sem_cobertura_integral': melhor_diag.get('pagamento_sem_cobertura_integral'),
            'patrimonio_terminal_proxy': melhor_diag.get('patrimonio_terminal_proxy'),
            'penalidade_estrategica_central': melhor_diag.get('penalidade_estrategica_central'),
            'penalidade_fragmentacao_central': melhor_diag.get('penalidade_fragmentacao_central'),
            'penalidade_reserva_critica_fonte': melhor_diag.get('penalidade_reserva_critica_fonte'),
            'excesso_sobre_reserva_critica': melhor_diag.get('excesso_sobre_reserva_critica'),
            'demanda_marginal_protegida_fonte_7d': melhor_diag.get('demanda_marginal_protegida_fonte_7d'),
            'demanda_marginal_protegida_fonte_14d': melhor_diag.get('demanda_marginal_protegida_fonte_14d'),
            'demanda_marginal_protegida_fonte_21d': melhor_diag.get('demanda_marginal_protegida_fonte_21d'),
            'reserva_critica_total_fonte': melhor_diag.get('reserva_critica_total_fonte'),
            'orcamento_livre_apos_reserva_fonte': melhor_diag.get('orcamento_livre_apos_reserva_fonte'),
            'fonte_critica_para_protegida_futura': bool(melhor_diag.get('fonte_critica_para_protegida_futura')),
            'pagamentos_protegidos_dependentes_fonte': melhor_diag.get('pagamentos_protegidos_dependentes_fonte'),
            'fonte_critica_referencias': melhor_diag.get('fonte_critica_referencias'),
            'fallback_sem_fonte_viavel': fallback_sem_fonte_viavel,
            'saldo_antes_central': 0.0 if fallback_sem_fonte_viavel else melhor_mov.get('saldo_antes_central'),
            'bruto_central': 0.0 if fallback_sem_fonte_viavel else melhor_mov.get('bruto_central'),
            'imposto_central': 0.0 if fallback_sem_fonte_viavel else melhor_mov.get('imposto_central'),
            'liquido_central': 0.0 if fallback_sem_fonte_viavel else melhor_mov.get('liquido_central'),
            'saldo_remanescente_central': 0.0 if fallback_sem_fonte_viavel else melhor_mov.get('saldo_remanescente_central'),
            'pagamento_totalmente_coberto_central': coberto,
            'observacao_central': observacao,
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'prioridade_intraclasse_operacional', 'pagamento_id'], kind='stable').reset_index(drop=True)
    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_cobertos_integral_central': int(quadro['pagamento_totalmente_coberto_central'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_integral': int(quadro['pagamento_sem_cobertura_integral'].sum()) if len(quadro) else 0,
        'violacoes_pagamentos_protegida': int(quadro['violacao_protegida'].sum()) if len(quadro) else 0,
        'deficit_liquido_total_central': round(float(quadro['deficit_liquido_total'].sum()), 2) if len(quadro) else 0.0,
        'mudancas_vs_decisao_local': int(quadro['mudou_vs_decisao_local'].sum()) if len(quadro) else 0,
        'patrimonio_terminal_proxy_final': round(float(quadro.iloc[-1].get('patrimonio_terminal_proxy') or 0.0), 2) if len(quadro) else 0.0,
        'fallbacks_sem_fonte_viavel': int(quadro['fallback_sem_fonte_viavel'].sum()) if len(quadro) else 0,
        'fontes_criticas_para_protegida': int(quadro['fonte_critica_para_protegida_futura'].sum()) if len(quadro) else 0,
        'reserva_critica_total_observada': round(float(quadro['reserva_critica_total_fonte'].sum()), 2) if len(quadro) else 0.0,
        'primeira_sem_cobertura_data': primeira_sem.get('Data') if primeira_sem else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.get('Descrição') if primeira_sem else None,
        'primeira_violation_protegida_data': primeira_protegida.get('Data') if primeira_protegida else None,
        'primeira_violation_protegida_pagamento': primeira_protegida.get('Descrição') if primeira_protegida else None,
        'primeiro_fallback_sem_fonte_viavel_data': primeiro_sem_fonte_viavel.get('Data') if primeiro_sem_fonte_viavel else None,
        'primeiro_fallback_sem_fonte_viavel_pagamento': primeiro_sem_fonte_viavel.get('Descrição') if primeiro_sem_fonte_viavel else None,
    }
    amostra_mudancas = []
    for _, row in quadro[quadro['mudou_vs_decisao_local'] == True].head(10).iterrows():
        amostra_mudancas.append({
            'Data': row.get('data_pagamento'),
            'Descrição': row.get('descricao_pagamento') or '',
            'Valor': round(float(row.get('valor_pagamento') or 0.0), 2),
            'Lote local': row.get('lote_sugerido_original') or '',
            'Lote central': row.get('lote_final_central') or '',
            'Classe': row.get('classe_pagamento_operacional') or '',
            'Subclasse': row.get('subclasse_pagamento_operacional') or '',
        })
    amostra_sem_cobertura = []
    for _, row in quadro[quadro['pagamento_totalmente_coberto_central'] == False].head(10).iterrows():
        amostra_sem_cobertura.append({
            'Data': row.get('data_pagamento'),
            'Descrição': row.get('descricao_pagamento') or '',
            'Valor': round(float(row.get('valor_pagamento') or 0.0), 2),
            'Classe': row.get('classe_pagamento_operacional') or '',
            'Lote central': row.get('lote_final_central') or '',
            'Déficit': round(float(row.get('deficit_liquido_total') or 0.0), 2),
            'Fallback': 'sim' if bool(row.get('fallback_sem_fonte_viavel')) else '',
        })
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_mudancas': amostra_mudancas,
        'amostra_sem_cobertura': amostra_sem_cobertura,
    }
    return PacoteRecomputacaoSequencialCentralV2(quadro_recomputacao_sequencial_central=quadro, auditoria=auditoria)
