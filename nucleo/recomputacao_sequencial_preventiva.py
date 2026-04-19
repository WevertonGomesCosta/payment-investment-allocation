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
    _selecionar_candidato_decisao_local_v1,
)
from nucleo.nucleo_financeiro_minimo import executar_saque_lote


@dataclass(slots=True)
class PacoteRecomputacaoSequencialPreventiva:
    quadro_recomputacao_sequencial: pd.DataFrame
    auditoria: dict[str, Any]


def _rotulo_fonte(candidato: dict[str, Any]) -> str:
    lote_id = str(candidato.get('lote_id') or candidato.get('lote_id_escolhido') or '').strip()
    if lote_id:
        return lote_id
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _ajustar_candidatos_sequenciais(
    candidatos: list[dict[str, Any]],
    *,
    valor_pagamento: float,
    mapa_lotes: dict[str, Any],
    consumo_generico: dict[str, float],
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    tolerancia_monetaria: float,
) -> list[dict[str, Any]]:
    ajustados: list[dict[str, Any]] = []
    for candidato in candidatos:
        cand = deepcopy(candidato)
        tipo = str(cand.get('tipo_fonte_escolhida') or '').strip()
        lote_id = str(cand.get('lote_id') or '').strip()
        if tipo == 'lote_resgatavel' and lote_id:
            lote = mapa_lotes.get(lote_id)
            saldo_bruto_antes = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2) if lote is not None else 0.0
            liquido_disponivel = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2) if lote is not None else 0.0
            cand['saldo_antes_sequencial'] = saldo_bruto_antes
            cand['valor_disponivel'] = liquido_disponivel
            cand['elegivel'] = bool(cand.get('elegivel')) and bool(liquido_disponivel > tolerancia_monetaria)
            cand['pagamento_totalmente_coberto'] = bool(cand.get('elegivel')) and bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
            if not cand['elegivel']:
                cand['motivo_bloqueio'] = str(cand.get('motivo_bloqueio') or 'fonte_esgotada_na_recomputacao_sequencial')
        else:
            fonte_id = str(cand.get('fonte_base_escolhida') or cand.get('fonte_escolhida_id') or '').strip()
            consumido = round(float(consumo_generico.get(fonte_id, 0.0) or 0.0), 2)
            valor_base = round(float(cand.get('valor_disponivel') or 0.0), 2)
            saldo_liquido_antes = round(max(valor_base - consumido, 0.0), 2)
            cand['saldo_antes_sequencial'] = saldo_liquido_antes
            cand['valor_disponivel'] = saldo_liquido_antes
            cand['elegivel'] = bool(cand.get('elegivel')) and bool(saldo_liquido_antes > tolerancia_monetaria)
            cand['pagamento_totalmente_coberto'] = bool(cand.get('elegivel')) and bool(saldo_liquido_antes + tolerancia_monetaria >= valor_pagamento)
            if not cand['elegivel']:
                cand['motivo_bloqueio'] = str(cand.get('motivo_bloqueio') or 'fonte_esgotada_na_recomputacao_sequencial')
        ajustados.append(cand)
    return ajustados


def carregar_recomputacao_sequencial_preventiva(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    decisao_local_v1,
    auditoria_temporal_decisao_local,
    replay_passado,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
    tolerancia_monetaria: float = 0.01,
) -> PacoteRecomputacaoSequencialPreventiva:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
        'fonte_original_id', 'lote_sugerido_original', 'tipo_fonte_original', 'status_temporal_original',
        'fonte_original_ainda_cobre', 'lote_final_sequencial', 'fonte_final_id', 'tipo_fonte_final',
        'criterio_recomputacao', 'score_proxy_sequencial', 'saldo_antes_sequencial', 'bruto_sequencial',
        'imposto_sequencial', 'liquido_sequencial', 'saldo_remanescente_sequencial',
        'pagamento_totalmente_coberto_sequencial', 'mudou_fonte_sequencial', 'troca_preventiva',
        'troca_por_inviabilidade', 'status_sequencial', 'motivo_troca', 'sequencia_na_fonte_final',
        'observacao_recomputacao',
    ]
    if len(pagamentos_alvo) == 0:
        return PacoteRecomputacaoSequencialPreventiva(
            quadro_recomputacao_sequencial=pd.DataFrame(columns=colunas),
            auditoria={
                'validacao': {'ok': False, 'erros': ['recomputacao_sequencial_sem_pagamentos_alvo'], 'avisos': []},
                'resumo': {'total_pagamentos_auditados': 0},
                'amostra_trocas_preventivas': [],
                'amostra_sem_cobertura': [],
            },
        )

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_decisao = {
        str(row.get('pagamento_id') or '').strip(): row
        for row in decisao_local_v1.quadro_decisao_local_v1.to_dict(orient='records')
    } if decisao_local_v1 is not None else {}
    mapa_temporal = {
        str(row.get('pagamento_id') or '').strip(): row
        for row in auditoria_temporal_decisao_local.quadro_auditoria_temporal.to_dict(orient='records')
    } if auditoria_temporal_decisao_local is not None else {}

    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    consumo_generico: dict[str, float] = {}
    contagem_fonte_final: dict[str, int] = {}
    registros: list[dict[str, Any]] = []
    primeira_troca_preventiva = None
    primeira_troca_inviabilidade = None
    primeira_sem_cobertura = None

    pagamentos_alvo = pagamentos_alvo.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        decisao_original = mapa_decisao.get(pagamento_id, {})
        temporal_original = mapa_temporal.get(pagamento_id, {})
        candidatos_base = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        candidatos = _ajustar_candidatos_sequenciais(
            candidatos_base,
            valor_pagamento=valor_pagamento,
            mapa_lotes=mapa_lotes,
            consumo_generico=consumo_generico,
            data_referencia=data_referencia,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            tolerancia_monetaria=tolerancia_monetaria,
        )

        fonte_original_id = str(decisao_original.get('fonte_escolhida_id') or '').strip()
        candidato_original = next((c for c in candidatos if str(c.get('fonte_escolhida_id') or '').strip() == fonte_original_id), None)
        original_ainda_cobre = bool(candidato_original and candidato_original.get('pagamento_totalmente_coberto'))

        escolhido, criterio, observacao_selecao = _selecionar_candidato_decisao_local_v1(
            candidatos,
            valor_pagamento=valor_pagamento,
            proxy_version=proxy_version,
        )
        score_final = escolhido.get('custo_economico_proxy')
        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final = str(escolhido.get('lote_id') or '').strip()
        fonte_final_id = str(escolhido.get('fonte_escolhida_id') or '').strip()
        fonte_final_rotulo = lote_final or _rotulo_fonte(escolhido)

        saldo_antes_sequencial = round(float(escolhido.get('saldo_antes_sequencial') or 0.0), 2)
        bruto_sequencial = 0.0
        imposto_sequencial = 0.0
        liquido_sequencial = 0.0
        saldo_rem_sequencial = saldo_antes_sequencial
        coberto_sequencial = False

        if tipo_final == 'lote_resgatavel' and lote_final:
            lote = mapa_lotes.get(lote_final)
            liquido_disponivel = round(float(escolhido.get('valor_disponivel') or 0.0), 2)
            coberto_sequencial = bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
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
                    saldo_antes_sequencial = round(float(movimento.get('saldo_antes') or 0.0), 2)
                    bruto_sequencial = round(float(movimento.get('bruto') or 0.0), 2)
                    imposto_sequencial = round(float(movimento.get('imposto') or 0.0), 2)
                    liquido_sequencial = round(float(movimento.get('liquido') or 0.0), 2)
                    saldo_rem_sequencial = round(float(movimento.get('saldo_remanescente') or 0.0), 2)
            else:
                saldo_rem_sequencial = saldo_antes_sequencial
        else:
            fonte_id_final_base = str(escolhido.get('fonte_base_escolhida') or escolhido.get('fonte_escolhida_id') or '').strip()
            coberto_sequencial = bool(saldo_antes_sequencial + tolerancia_monetaria >= valor_pagamento)
            liquido_sequencial = round(min(valor_pagamento, saldo_antes_sequencial), 2)
            bruto_sequencial = liquido_sequencial
            imposto_sequencial = 0.0
            saldo_rem_sequencial = round(max(saldo_antes_sequencial - liquido_sequencial, 0.0), 2)
            consumo_generico[fonte_id_final_base] = round(float(consumo_generico.get(fonte_id_final_base, 0.0) or 0.0) + liquido_sequencial, 2)

        contagem_fonte_final[fonte_final_rotulo] = contagem_fonte_final.get(fonte_final_rotulo, 0) + 1
        seq_fonte_final = contagem_fonte_final[fonte_final_rotulo]

        mudou_fonte = bool(fonte_final_id != fonte_original_id)
        troca_preventiva = bool(mudou_fonte and original_ainda_cobre)
        troca_por_inviabilidade = bool(mudou_fonte and not original_ainda_cobre)

        if troca_preventiva and primeira_troca_preventiva is None:
            primeira_troca_preventiva = {
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'valor_pagamento': valor_pagamento,
                'lote_original': str(decisao_original.get('lote_id_escolhido') or ''),
                'lote_final': fonte_final_rotulo,
            }
        if troca_por_inviabilidade and primeira_troca_inviabilidade is None:
            primeira_troca_inviabilidade = {
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'valor_pagamento': valor_pagamento,
                'lote_original': str(decisao_original.get('lote_id_escolhido') or ''),
                'lote_final': fonte_final_rotulo,
            }
        if not coberto_sequencial and primeira_sem_cobertura is None:
            primeira_sem_cobertura = {
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': str(pagamento.get('descricao') or ''),
                'valor_pagamento': valor_pagamento,
                'lote_final': fonte_final_rotulo,
            }

        if not coberto_sequencial:
            status_sequencial = 'recomputado sem cobertura integral'
            motivo_troca = 'insuficiencia_estrutural_pos_recomputacao'
        elif troca_preventiva:
            status_sequencial = 'troca preventiva antes da quebra'
            motivo_troca = 'troca_preventiva_melhora_trajetoria_local'
        elif troca_por_inviabilidade:
            status_sequencial = 'troca por inviabilidade da fonte original'
            motivo_troca = 'fonte_original_inviavel_na_sequencia'
        elif fonte_original_id:
            status_sequencial = 'mantido pela recomputação sequencial'
            motivo_troca = 'fonte_original_permaneceu_melhor_no_estado_atualizado'
        else:
            status_sequencial = 'escolha sequencial sem referência local original'
            motivo_troca = 'sem_fonte_original_materializada'

        observacao = str(observacao_selecao or '')
        if troca_preventiva:
            observacao = (
                'recomputação sequencial preventiva trocou a fonte antes da quebra porque, no estado residual atualizado, '
                'outra alternativa passou a dominar a decisão local. ' + observacao
            )
        elif troca_por_inviabilidade:
            observacao = (
                'recomputação sequencial trocou a fonte porque a sugestão original perdeu cobertura integral no estado residual atualizado. '
                + observacao
            )
        elif not coberto_sequencial:
            observacao = 'recomputação sequencial não encontrou cobertura integral entre as fontes elegíveis remanescentes. ' + observacao
        else:
            observacao = 'recomputação sequencial confirmou a melhor fonte no estado residual atualizado. ' + observacao

        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'fonte_original_id': fonte_original_id,
            'lote_sugerido_original': str(decisao_original.get('lote_id_escolhido') or ''),
            'tipo_fonte_original': str(decisao_original.get('tipo_fonte_escolhida') or ''),
            'status_temporal_original': str(temporal_original.get('status_temporal') or ''),
            'fonte_original_ainda_cobre': original_ainda_cobre,
            'lote_final_sequencial': fonte_final_rotulo,
            'fonte_final_id': fonte_final_id,
            'tipo_fonte_final': tipo_final,
            'criterio_recomputacao': criterio,
            'score_proxy_sequencial': round(float(score_final or 0.0), 4) if score_final is not None else None,
            'saldo_antes_sequencial': saldo_antes_sequencial,
            'bruto_sequencial': bruto_sequencial,
            'imposto_sequencial': imposto_sequencial,
            'liquido_sequencial': liquido_sequencial,
            'saldo_remanescente_sequencial': saldo_rem_sequencial,
            'pagamento_totalmente_coberto_sequencial': coberto_sequencial,
            'mudou_fonte_sequencial': mudou_fonte,
            'troca_preventiva': troca_preventiva,
            'troca_por_inviabilidade': troca_por_inviabilidade,
            'status_sequencial': status_sequencial,
            'motivo_troca': motivo_troca,
            'sequencia_na_fonte_final': seq_fonte_final,
            'observacao_recomputacao': observacao.strip(),
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    amostra_preventiva = []
    sub_prev = quadro[quadro['troca_preventiva'] == True].copy()
    if len(sub_prev):
        for _, item in sub_prev.head(10).iterrows():
            data = item.get('data_pagamento')
            amostra_preventiva.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else str(data or ''),
                'Descrição': item.get('descricao_pagamento') or '',
                'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
                'Lote original': item.get('lote_sugerido_original') or '',
                'Lote sequencial': item.get('lote_final_sequencial') or '',
                'Score sequencial': round(float(item.get('score_proxy_sequencial') or 0.0), 4) if item.get('score_proxy_sequencial') is not None else '',
                'Status sequencial': item.get('status_sequencial') or '',
            })
    amostra_sem = []
    sub_sem = quadro[quadro['pagamento_totalmente_coberto_sequencial'] == False].copy()
    if len(sub_sem):
        for _, item in sub_sem.head(10).iterrows():
            data = item.get('data_pagamento')
            amostra_sem.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else str(data or ''),
                'Descrição': item.get('descricao_pagamento') or '',
                'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
                'Lote sequencial': item.get('lote_final_sequencial') or '',
                'Saldo Antes sequencial': round(float(item.get('saldo_antes_sequencial') or 0.0), 2),
                'Status sequencial': item.get('status_sequencial') or '',
            })

    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_cobertos_sequencialmente': int(quadro['pagamento_totalmente_coberto_sequencial'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_sequencial': int((~quadro['pagamento_totalmente_coberto_sequencial']).sum()) if len(quadro) else 0,
        'mudancas_efetivas_de_fonte': int(quadro['mudou_fonte_sequencial'].sum()) if len(quadro) else 0,
        'trocas_preventivas': int(quadro['troca_preventiva'].sum()) if len(quadro) else 0,
        'trocas_por_inviabilidade': int(quadro['troca_por_inviabilidade'].sum()) if len(quadro) else 0,
        'mantidos_sem_troca': int((~quadro['mudou_fonte_sequencial']).sum()) if len(quadro) else 0,
        'primeira_troca_preventiva_data': primeira_troca_preventiva.get('data_pagamento') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_pagamento': primeira_troca_preventiva.get('descricao_pagamento') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_lote_original': primeira_troca_preventiva.get('lote_original') if primeira_troca_preventiva else None,
        'primeira_troca_preventiva_lote_final': primeira_troca_preventiva.get('lote_final') if primeira_troca_preventiva else None,
        'primeira_troca_inviabilidade_data': primeira_troca_inviabilidade.get('data_pagamento') if primeira_troca_inviabilidade else None,
        'primeira_troca_inviabilidade_pagamento': primeira_troca_inviabilidade.get('descricao_pagamento') if primeira_troca_inviabilidade else None,
        'primeira_troca_inviabilidade_lote_original': primeira_troca_inviabilidade.get('lote_original') if primeira_troca_inviabilidade else None,
        'primeira_troca_inviabilidade_lote_final': primeira_troca_inviabilidade.get('lote_final') if primeira_troca_inviabilidade else None,
        'primeira_sem_cobertura_data': primeira_sem_cobertura.get('data_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_pagamento': primeira_sem_cobertura.get('descricao_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_lote_final': primeira_sem_cobertura.get('lote_final') if primeira_sem_cobertura else None,
    }
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_trocas_preventivas': amostra_preventiva,
        'amostra_sem_cobertura': amostra_sem,
    }
    return PacoteRecomputacaoSequencialPreventiva(quadro_recomputacao_sequencial=quadro, auditoria=auditoria)
