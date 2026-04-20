from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.caixa_recebidos_auditaveis import (
    _construir_candidatos_decisao_local_v1,
    _construir_mapa_produtos_proxy,
    _janela_excesso_por_proxy,
    _pagamentos_alvo_f1_4,
    _prioridade_status_origem,
    _score_proxy_economico_por_versao,
    _selecionar_candidato_decisao_local_v1,
)
from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos


@dataclass(slots=True)
class PacoteHeuristicaConjuntaParcialBlocoCritico:
    quadro_heuristica_conjunta_parcial: pd.DataFrame
    auditoria: dict[str, Any]


DEFAULT_BLOCO_CRITICO_INICIO = date(2026, 4, 20)
DEFAULT_BLOCO_CRITICO_FIM = date(2026, 5, 20)


def _rotulo_fonte(candidato: dict[str, Any]) -> str:
    lote_id = str(candidato.get('lote_id') or candidato.get('lote_id_escolhido') or '').strip()
    if lote_id:
        return lote_id
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _fonte_id(candidato: dict[str, Any]) -> str:
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _esta_no_bloco_critico(data_pagamento: Any, *, inicio: date, fim: date) -> bool:
    return bool(isinstance(data_pagamento, date) and inicio <= data_pagamento <= fim)


def _construir_plano_reservas_restantes(
    pagamentos_restantes: list[dict[str, Any]],
    *,
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, dict[str, Any]],
    mapa_lotes: dict[str, Any],
    consumo_generico: dict[str, float],
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    proxy_version: str,
    tolerancia_monetaria: float,
    valor_minimo_estrategico: float = 800.0,
) -> tuple[dict[str, float], list[dict[str, Any]], list[dict[str, Any]]]:
    entradas: list[dict[str, Any]] = []
    capacidades: dict[str, float] = {}

    for pagamento in pagamentos_restantes:
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
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
        cobrem = []
        parciais = []
        for candidato in candidatos:
            if not bool(candidato.get('elegivel')) or not bool(candidato.get('pagamento_totalmente_coberto')):
                continue
            score, _ = _score_proxy_economico_por_versao(proxy_version, candidato, valor_pagamento=valor_pagamento)
            fonte_id = _fonte_id(candidato)
            valor_disp = round(float(candidato.get('valor_disponivel') or 0.0), 2)
            capacidades[fonte_id] = max(capacidades.get(fonte_id, 0.0), valor_disp)
            if bool(candidato.get('elegivel')) and valor_disp > tolerancia_monetaria:
                parciais.append({
                    'fonte_id': fonte_id,
                    'rotulo': _rotulo_fonte(candidato),
                    'valor_disponivel': valor_disp,
                    'score': score,
                })
            cobrem.append({
                'fonte_id': fonte_id,
                'rotulo': _rotulo_fonte(candidato),
                'valor_disponivel': valor_disp,
                'score': score,
            })
        if valor_pagamento >= valor_minimo_estrategico or len(cobrem) <= 2:
            entradas.append({
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'pagamento_id': str(pagamento.get('despesa_id') or '').strip(),
                'valor_pagamento': valor_pagamento,
                'cobrem': cobrem,
                'parciais': parciais,
            })

    capacidades_trabalho = {k: round(v, 2) for k, v in capacidades.items()}
    reserva_por_fonte: dict[str, float] = {}
    alocacoes: list[dict[str, Any]] = []
    nao_alocados: list[dict[str, Any]] = []

    entradas_ordenadas = sorted(
        entradas,
        key=lambda item: (
            len(item.get('cobrem') or []) if item.get('cobrem') else 9999,
            -float(item.get('valor_pagamento') or 0.0),
            item.get('data_pagamento'),
            item.get('pagamento_id'),
        ),
    )

    for entrada in entradas_ordenadas:
        valor = round(float(entrada.get('valor_pagamento') or 0.0), 2)
        cobrem = entrada.get('cobrem') or []
        viaveis = [
            c for c in cobrem
            if round(float(capacidades_trabalho.get(c['fonte_id'], 0.0) or 0.0), 2) + tolerancia_monetaria >= valor
        ]
        if not viaveis:
            parciais = [
                c for c in (entrada.get('parciais') or [])
                if round(float(capacidades_trabalho.get(c['fonte_id'], 0.0) or 0.0), 2) > tolerancia_monetaria
            ]
            if not parciais:
                nao_alocados.append({
                    'Data': entrada.get('data_pagamento'),
                    'Descrição': entrada.get('descricao_pagamento'),
                    'Valor': valor,
                    'Coberturas monofonte restantes': len(cobrem),
                })
                continue
            escolhido = max(
                parciais,
                key=lambda c: (round(float(capacidades_trabalho.get(c['fonte_id'], 0.0) or 0.0), 4), -round(float(c.get('score') or 0.0), 6), c['fonte_id']),
            )
            reserva_consumida = round(float(capacidades_trabalho.get(escolhido['fonte_id'], 0.0) or 0.0), 2)
            capacidades_trabalho[escolhido['fonte_id']] = 0.0
            reserva_por_fonte[escolhido['fonte_id']] = round(reserva_por_fonte.get(escolhido['fonte_id'], 0.0) + reserva_consumida, 2)
            if len(alocacoes) < 12:
                alocacoes.append({
                    'Data': entrada.get('data_pagamento'),
                    'Descrição': entrada.get('descricao_pagamento'),
                    'Valor': valor,
                    'Fonte reservada': escolhido['rotulo'] + ' (reserva parcial)',
                    'Saldo residual planejado': capacidades_trabalho.get(escolhido['fonte_id'], 0.0),
                    'Coberturas monofonte': len(cobrem),
                })
            continue
        escolhido = min(
            viaveis,
            key=lambda c: (
                round(float(capacidades_trabalho.get(c['fonte_id'], 0.0) or 0.0) - valor, 4),
                round(float(c.get('score') or 0.0), 6),
                c['fonte_id'],
            ),
        )
        capacidades_trabalho[escolhido['fonte_id']] = round(capacidades_trabalho.get(escolhido['fonte_id'], 0.0) - valor, 2)
        reserva_por_fonte[escolhido['fonte_id']] = round(reserva_por_fonte.get(escolhido['fonte_id'], 0.0) + valor, 2)
        if len(alocacoes) < 12:
            alocacoes.append({
                'Data': entrada.get('data_pagamento'),
                'Descrição': entrada.get('descricao_pagamento'),
                'Valor': valor,
                'Fonte reservada': escolhido['rotulo'],
                'Saldo residual planejado': capacidades_trabalho.get(escolhido['fonte_id'], 0.0),
                'Coberturas monofonte': len(cobrem),
            })
    return reserva_por_fonte, alocacoes, nao_alocados


def _selecionar_candidato_com_preservacao(
    candidatos: list[dict[str, Any]],
    *,
    valor_pagamento: float,
    proxy_version: str,
    reserva_por_fonte: dict[str, float],
) -> tuple[dict[str, Any], str, str, float, float, float]:
    elegiveis = [c for c in candidatos if c.get('elegivel')]
    if not elegiveis:
        escolhido, criterio, observacao = _selecionar_candidato_decisao_local_v1(candidatos, valor_pagamento=valor_pagamento, proxy_version=proxy_version)
        return escolhido, criterio, observacao, 0.0, 0.0, round(float(escolhido.get('custo_economico_proxy') or 0.0), 4) if escolhido else 0.0

    elegiveis_cobertura_total = [c for c in elegiveis if c.get('pagamento_totalmente_coberto')]
    janela_excesso = _janela_excesso_por_proxy(proxy_version, valor_pagamento)
    if elegiveis_cobertura_total:
        min_excesso = min(max(float(c.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0) for c in elegiveis_cobertura_total)
        pool = [
            c for c in elegiveis_cobertura_total
            if max(float(c.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0) <= min_excesso + janela_excesso
        ]
        criterio = f'heuristica_conjunta_parcial_bloco_critico__proxy_{proxy_version}_com_preservacao'
    else:
        pool = list(elegiveis)
        criterio = f'heuristica_conjunta_parcial_bloco_critico__proxy_{proxy_version}_sem_cobertura_integral'

    melhor = None
    escolhido = None
    melhor_obs = ''
    melhor_penalidade = 0.0
    melhor_reserva = 0.0
    melhor_ajustado = 0.0
    menor_valor_pool = min(float(c.get('valor_disponivel') or 0.0) for c in pool) if pool else 0.0

    for candidato in pool:
        score_base, detalhes = _score_proxy_economico_por_versao(proxy_version, candidato, valor_pagamento=valor_pagamento)
        candidato['custo_economico_proxy'] = score_base
        candidato['proxy_componentes'] = detalhes
        fonte_id = _fonte_id(candidato)
        reserva = round(float(reserva_por_fonte.get(fonte_id, 0.0) or 0.0), 2)
        consumo_liquido = round(min(valor_pagamento, float(candidato.get('valor_disponivel') or 0.0)), 2)
        saldo_pos = round(max(float(candidato.get('valor_disponivel') or 0.0) - consumo_liquido, 0.0), 2)
        shortfall_reserva = round(max(reserva - saldo_pos, 0.0), 2)
        penalidade_preservacao = round(shortfall_reserva / 10.0, 4)
        excesso_porte = max(float(candidato.get('valor_disponivel') or 0.0) - menor_valor_pool, 0.0)
        if valor_pagamento <= 500.0:
            penalidade_porte = round(excesso_porte / 20.0, 4)
        elif valor_pagamento <= 800.0:
            penalidade_porte = round(excesso_porte / 40.0, 4)
        elif valor_pagamento <= 1500.0:
            penalidade_porte = round(excesso_porte / 80.0, 4)
        else:
            penalidade_porte = 0.0
        score_ajustado = round(score_base + penalidade_preservacao + penalidade_porte, 4)
        excesso = max(float(candidato.get('valor_disponivel') or 0.0) - valor_pagamento, 0.0)
        chave = (
            score_ajustado,
            penalidade_preservacao,
            excesso,
            _prioridade_status_origem(candidato.get('origem_status', 'ausente')),
            fonte_id,
        )
        if melhor is None or chave < melhor:
            melhor = chave
            escolhido = candidato
            melhor_penalidade = penalidade_preservacao
            melhor_reserva = reserva
            melhor_ajustado = score_ajustado
            melhor_obs = (
                f'preservação estratégica aplicada; reserva estimada da fonte={reserva:.2f}; '
                f'saldo pós-uso={saldo_pos:.2f}; shortfall_reserva={shortfall_reserva:.2f}; '
                f'penalidade_preservacao={penalidade_preservacao:.4f}; penalidade_porte={penalidade_porte:.4f}; '
                f'score_base={score_base:.4f}; score_ajustado={score_ajustado:.4f}.'
            )

    assert escolhido is not None
    return escolhido, criterio, melhor_obs, melhor_penalidade, melhor_reserva, melhor_ajustado


def carregar_heuristica_conjunta_parcial_bloco_critico(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    decisao_local_v1,
    replay_passado,
    auditoria_temporal_decisao_local,
    reescolha_dinamica_pos_quebra,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
    bloco_critico_inicio: date = DEFAULT_BLOCO_CRITICO_INICIO,
    bloco_critico_fim: date = DEFAULT_BLOCO_CRITICO_FIM,
    tolerancia_monetaria: float = 0.01,
) -> PacoteHeuristicaConjuntaParcialBlocoCritico:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'esta_no_bloco_critico',
        'lote_sugerido_original', 'lote_final_heuristica', 'tipo_fonte_final', 'mudou_fonte_heuristica',
        'troca_preventiva_heuristica', 'troca_por_inviabilidade_heuristica', 'criterio_heuristica',
        'score_proxy_original', 'score_proxy_heuristica', 'score_proxy_ajustado_heuristica',
        'penalidade_preservacao_estrategica', 'reserva_planejada_fonte', 'status_heuristica',
        'saldo_antes_heuristica', 'bruto_heuristica', 'imposto_heuristica', 'liquido_heuristica',
        'saldo_remanescente_heuristica', 'pagamento_totalmente_coberto_heuristica', 'observacao_heuristica',
    ]
    if len(pagamentos_alvo) == 0:
        return PacoteHeuristicaConjuntaParcialBlocoCritico(
            quadro_heuristica_conjunta_parcial=pd.DataFrame(columns=colunas),
            auditoria={'validacao': {'ok': False, 'erros': ['heuristica_conjunta_sem_pagamentos_alvo'], 'avisos': []}, 'resumo': {'total_pagamentos_auditados': 0}},
        )

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_decisao = {
        str(row.get('pagamento_id') or '').strip(): row
        for row in (decisao_local_v1.quadro_decisao_local_v1.to_dict(orient='records') if decisao_local_v1 is not None else [])
    }
    resumo_temporal = (auditoria_temporal_decisao_local.auditoria or {}).get('resumo', {}) if auditoria_temporal_decisao_local is not None else {}
    resumo_reescolha = (reescolha_dinamica_pos_quebra.auditoria or {}).get('resumo', {}) if reescolha_dinamica_pos_quebra is not None else {}

    pagamentos_ordenados = pagamentos_alvo.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True).to_dict(orient='records')
    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    consumo_generico: dict[str, float] = {}
    registros: list[dict[str, Any]] = []
    primeira_troca_preventiva = None
    primeira_sem_cobertura = None
    amostra_trocas_preventivas: list[dict[str, Any]] = []
    amostra_sem_cobertura: list[dict[str, Any]] = []
    amostra_planejamento_reservas: list[dict[str, Any]] = []

    for idx, pagamento in enumerate(pagamentos_ordenados):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        data_pagamento = pagamento.get('data')
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        decisao_original = mapa_decisao.get(pagamento_id, {})

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

        esta_no_bloco = _esta_no_bloco_critico(data_pagamento, inicio=bloco_critico_inicio, fim=bloco_critico_fim)
        reserva_por_fonte: dict[str, float] = {}
        planejamento_reservas: list[dict[str, Any]] = []

        if esta_no_bloco:
            pagamentos_restantes_bloco = [
                item for item in pagamentos_ordenados[idx + 1:]
                if _esta_no_bloco_critico(item.get('data'), inicio=bloco_critico_inicio, fim=bloco_critico_fim)
            ]
            reserva_por_fonte, planejamento_reservas, _ = _construir_plano_reservas_restantes(
                pagamentos_restantes_bloco,
                quadro_saldo=quadro_saldo,
                quadro_fontes=quadro_fontes,
                mapa_produtos_proxy=mapa_produtos_proxy,
                mapa_lotes=mapa_lotes,
                consumo_generico=consumo_generico,
                data_referencia=data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                proxy_version=proxy_version,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            if planejamento_reservas and len(amostra_planejamento_reservas) < 12:
                amostra_planejamento_reservas.extend(planejamento_reservas[: max(0, 12 - len(amostra_planejamento_reservas))])
            escolhido, criterio, observacao_base, penalidade_preservacao, reserva_planejada, score_ajustado = _selecionar_candidato_com_preservacao(
                candidatos,
                valor_pagamento=valor_pagamento,
                proxy_version=proxy_version,
                reserva_por_fonte=reserva_por_fonte,
            )
        else:
            escolhido, criterio, observacao_base = _selecionar_candidato_decisao_local_v1(candidatos, valor_pagamento=valor_pagamento, proxy_version=proxy_version)
            penalidade_preservacao = 0.0
            reserva_planejada = 0.0
            score_ajustado = round(float(escolhido.get('custo_economico_proxy') or 0.0), 4) if escolhido else 0.0

        fonte_original_id = str(decisao_original.get('fonte_base_escolhida') or decisao_original.get('fonte_escolhida_id') or '').strip()
        fonte_final_id = _fonte_id(escolhido)
        lote_original = str(decisao_original.get('lote_id_escolhido') or '')
        lote_final = str(escolhido.get('lote_id') or '').strip() or _rotulo_fonte(escolhido)
        candidato_original = next((c for c in candidatos if _fonte_id(c) == fonte_original_id), None)
        original_ainda_cobre = bool(candidato_original and candidato_original.get('pagamento_totalmente_coberto'))
        mudou_fonte = bool(fonte_final_id != fonte_original_id)
        troca_preventiva = bool(esta_no_bloco and original_ainda_cobre and mudou_fonte)
        troca_por_inviabilidade = bool((not original_ainda_cobre) and mudou_fonte)

        saldo_antes = round(float(escolhido.get('saldo_antes_dinamico') or 0.0), 2)
        bruto = 0.0
        imposto = 0.0
        liquido = 0.0
        saldo_rem = saldo_antes
        coberto = False
        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final_exec = str(escolhido.get('lote_id') or '').strip()
        if tipo_final == 'lote_resgatavel' and lote_final_exec:
            lote = mapa_lotes.get(lote_final_exec)
            liquido_disponivel = round(float(escolhido.get('valor_disponivel') or 0.0), 2)
            coberto = bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
            liquido_alvo = round(min(valor_pagamento, liquido_disponivel), 2)
            if lote is not None and liquido_alvo > tolerancia_monetaria:
                movimento = executar_saque_lote(
                    lote,
                    liquido_alvo,
                    data_referencia,
                    tabela_iof=tabela_iof,
                    faixas_ir=faixas_ir,
                    tolerancia_monetaria=tolerancia_monetaria,
                )
                if movimento is not None:
                    saldo_antes = round(float(movimento.get('saldo_antes') or 0.0), 2)
                    bruto = round(float(movimento.get('bruto') or 0.0), 2)
                    imposto = round(float(movimento.get('imposto') or 0.0), 2)
                    liquido = round(float(movimento.get('liquido') or 0.0), 2)
                    saldo_rem = round(float(movimento.get('saldo_remanescente') or 0.0), 2)
            else:
                saldo_rem = saldo_antes
        else:
            fonte_generic = _fonte_id(escolhido)
            coberto = bool(saldo_antes + tolerancia_monetaria >= valor_pagamento)
            liquido = round(min(valor_pagamento, saldo_antes), 2)
            bruto = liquido
            imposto = 0.0
            saldo_rem = round(max(saldo_antes - liquido, 0.0), 2)
            consumo_generico[fonte_generic] = round(float(consumo_generico.get(fonte_generic, 0.0) or 0.0) + liquido, 2)

        if coberto:
            if troca_preventiva:
                status = 'troca preventiva por preservação estratégica'
                if primeira_troca_preventiva is None:
                    primeira_troca_preventiva = {
                        'data_pagamento': data_pagamento,
                        'descricao_pagamento': str(pagamento.get('descricao') or ''),
                        'valor_pagamento': valor_pagamento,
                        'lote_original': lote_original,
                        'lote_final': lote_final,
                    }
                if len(amostra_trocas_preventivas) < 10:
                    amostra_trocas_preventivas.append({
                        'Data': data_pagamento,
                        'Descrição': str(pagamento.get('descricao') or ''),
                        'Valor': valor_pagamento,
                        'Lote original': lote_original,
                        'Lote heurístico': lote_final,
                        'Reserva planejada': reserva_planejada,
                        'Penalidade preservação': penalidade_preservacao,
                    })
            elif troca_por_inviabilidade:
                status = 'troca por inviabilidade na sequência'
            elif mudou_fonte:
                status = 'troca heurística com cobertura integral'
            else:
                status = 'mantido pela heurística'
        else:
            status = 'sem cobertura pela heurística parcial'
            if primeira_sem_cobertura is None:
                primeira_sem_cobertura = {
                    'data_pagamento': data_pagamento,
                    'descricao_pagamento': str(pagamento.get('descricao') or ''),
                    'valor_pagamento': valor_pagamento,
                    'lote_final': lote_final,
                }
            if len(amostra_sem_cobertura) < 10:
                amostra_sem_cobertura.append({
                    'Data': data_pagamento,
                    'Descrição': str(pagamento.get('descricao') or ''),
                    'Valor': valor_pagamento,
                    'Lote heurístico': lote_final,
                    'Saldo Antes heurístico': saldo_antes,
                    'Status heurística': status,
                })

        observacao = observacao_base.strip()
        if esta_no_bloco:
            observacao = (
                f'bloco crítico ativo; {observacao} '
                f'fonte_original_ainda_cobre={"sim" if original_ainda_cobre else "não"}; '
                f'reserva_planejada_fonte={reserva_planejada:.2f}; '
                f'penalidade_preservacao={penalidade_preservacao:.4f}.'
            )
        else:
            observacao = 'fora do bloco crítico; decisão segue recomputação sequencial local sem solver global. ' + observacao

        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': data_pagamento,
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'esta_no_bloco_critico': esta_no_bloco,
            'lote_sugerido_original': lote_original,
            'lote_final_heuristica': lote_final,
            'tipo_fonte_final': tipo_final,
            'mudou_fonte_heuristica': mudou_fonte,
            'troca_preventiva_heuristica': troca_preventiva,
            'troca_por_inviabilidade_heuristica': troca_por_inviabilidade,
            'criterio_heuristica': criterio,
            'score_proxy_original': round(float(decisao_original.get('custo_economico_proxy') or 0.0), 4) if decisao_original else None,
            'score_proxy_heuristica': round(float(escolhido.get('custo_economico_proxy') or 0.0), 4) if escolhido.get('custo_economico_proxy') is not None else None,
            'score_proxy_ajustado_heuristica': score_ajustado,
            'penalidade_preservacao_estrategica': penalidade_preservacao,
            'reserva_planejada_fonte': round(float(reserva_planejada or 0.0), 2),
            'status_heuristica': status,
            'saldo_antes_heuristica': saldo_antes,
            'bruto_heuristica': bruto,
            'imposto_heuristica': imposto,
            'liquido_heuristica': liquido,
            'saldo_remanescente_heuristica': saldo_rem,
            'pagamento_totalmente_coberto_heuristica': coberto,
            'observacao_heuristica': observacao,
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_no_bloco_critico': int(quadro['esta_no_bloco_critico'].sum()) if len(quadro) else 0,
        'pagamentos_cobertos_heuristica': int(quadro['pagamento_totalmente_coberto_heuristica'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_heuristica': int((~quadro['pagamento_totalmente_coberto_heuristica']).sum()) if len(quadro) else 0,
        'pagamentos_cobertos_no_bloco_critico': int((quadro['esta_no_bloco_critico'] & quadro['pagamento_totalmente_coberto_heuristica']).sum()) if len(quadro) else 0,
        'mudancas_efetivas_de_fonte': int(quadro['mudou_fonte_heuristica'].sum()) if len(quadro) else 0,
        'trocas_preventivas_heuristica': int(quadro['troca_preventiva_heuristica'].sum()) if len(quadro) else 0,
        'trocas_por_inviabilidade_heuristica': int(quadro['troca_por_inviabilidade_heuristica'].sum()) if len(quadro) else 0,
        'primeira_troca_preventiva_data': primeira_troca_preventiva.get('data_pagamento') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_pagamento': primeira_troca_preventiva.get('descricao_pagamento') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_lote_original': primeira_troca_preventiva.get('lote_original') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_lote_final': primeira_troca_preventiva.get('lote_final') if primeira_troca_preventiva else None,
        'primeira_sem_cobertura_data': primeira_sem_cobertura.get('data_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_pagamento': primeira_sem_cobertura.get('descricao_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_lote_final': primeira_sem_cobertura.get('lote_final') if primeira_sem_cobertura else None,
        'primeira_quebra_global_temporal_data': resumo_temporal.get('primeira_quebra_global_data'),
        'primeira_sem_cobertura_reescolha_data': resumo_reescolha.get('primeira_sem_cobertura_data'),
    }

    atraso_vs_temporal = None
    if resumo.get('primeira_sem_cobertura_data') and resumo.get('primeira_quebra_global_temporal_data'):
        atraso_vs_temporal = (resumo['primeira_sem_cobertura_data'] - resumo['primeira_quebra_global_temporal_data']).days
        resumo['atraso_dias_vs_primeira_quebra_temporal'] = atraso_vs_temporal
    atraso_vs_reescolha = None
    if resumo.get('primeira_sem_cobertura_data') and resumo.get('primeira_sem_cobertura_reescolha_data'):
        atraso_vs_reescolha = (resumo['primeira_sem_cobertura_data'] - resumo['primeira_sem_cobertura_reescolha_data']).days
        resumo['atraso_dias_vs_primeira_sem_cobertura_reescolha'] = atraso_vs_reescolha
    resumo['quebra_estrutural_adiada_vs_temporal'] = bool((atraso_vs_temporal or 0) > 0)
    resumo['quebra_estrutural_adiada_vs_reescolha'] = bool((atraso_vs_reescolha or 0) > 0)

    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_trocas_preventivas': amostra_trocas_preventivas,
        'amostra_sem_cobertura': amostra_sem_cobertura,
        'amostra_planejamento_reservas': amostra_planejamento_reservas,
    }
    return PacoteHeuristicaConjuntaParcialBlocoCritico(quadro_heuristica_conjunta_parcial=quadro, auditoria=auditoria)
