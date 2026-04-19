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
class PacoteReescolhaDinamicaPosQuebra:
    quadro_reescolha_dinamica: pd.DataFrame
    auditoria: dict[str, Any]


def _rotulo_fonte(candidato: dict[str, Any]) -> str:
    lote_id = str(candidato.get('lote_id') or candidato.get('lote_id_escolhido') or '').strip()
    if lote_id:
        return lote_id
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _ajustar_candidatos_dinamicos(
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
            cand['saldo_antes_dinamico'] = saldo_bruto_antes
            cand['valor_disponivel'] = liquido_disponivel
            cand['elegivel'] = bool(cand.get('elegivel')) and bool(liquido_disponivel > tolerancia_monetaria)
            cand['pagamento_totalmente_coberto'] = bool(cand.get('elegivel')) and bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
            if not cand['elegivel']:
                cand['motivo_bloqueio'] = str(cand.get('motivo_bloqueio') or 'fonte_esgotada_pos_sequencia')
        else:
            fonte_id = str(cand.get('fonte_base_escolhida') or cand.get('fonte_escolhida_id') or '').strip()
            consumido = round(float(consumo_generico.get(fonte_id, 0.0) or 0.0), 2)
            valor_base = round(float(cand.get('valor_disponivel') or 0.0), 2)
            saldo_liquido_antes = round(max(valor_base - consumido, 0.0), 2)
            cand['saldo_antes_dinamico'] = saldo_liquido_antes
            cand['valor_disponivel'] = saldo_liquido_antes
            cand['elegivel'] = bool(cand.get('elegivel')) and bool(saldo_liquido_antes > tolerancia_monetaria)
            cand['pagamento_totalmente_coberto'] = bool(cand.get('elegivel')) and bool(saldo_liquido_antes + tolerancia_monetaria >= valor_pagamento)
            if not cand['elegivel']:
                cand['motivo_bloqueio'] = str(cand.get('motivo_bloqueio') or 'fonte_esgotada_pos_sequencia')
        ajustados.append(cand)
    return ajustados


def carregar_reescolha_dinamica_pos_quebra(
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
) -> PacoteReescolhaDinamicaPosQuebra:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'lote_sugerido_original', 'status_temporal_original',
        'reescolha_acionada', 'mudou_fonte', 'fonte_final_id', 'lote_final_dinamico', 'tipo_fonte_final', 'criterio_reescolha',
        'score_proxy_final', 'status_pos_reescolha', 'saldo_antes_dinamico', 'bruto_dinamico', 'imposto_dinamico', 'liquido_dinamico',
        'saldo_remanescente_dinamico', 'pagamento_totalmente_coberto_dinamico', 'observacao_reescolha',
    ]
    if len(pagamentos_alvo) == 0:
        return PacoteReescolhaDinamicaPosQuebra(
            quadro_reescolha_dinamica=pd.DataFrame(columns=colunas),
            auditoria={
                'validacao': {'ok': False, 'erros': ['reescolha_dinamica_sem_pagamentos_alvo'], 'avisos': []},
                'resumo': {'total_pagamentos_auditados': 0},
                'amostra_reescolhas': [],
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
    registros: list[dict[str, Any]] = []
    primeira_reescolha = None
    primeira_sem_cobertura = None

    pagamentos_alvo = pagamentos_alvo.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        decisao_original = mapa_decisao.get(pagamento_id, {})
        temporal_original = mapa_temporal.get(pagamento_id, {})
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

        fonte_original_id = str(decisao_original.get('fonte_escolhida_id') or '').strip()
        candidato_original = next((c for c in candidatos if str(c.get('fonte_escolhida_id') or '').strip() == fonte_original_id), None)
        original_ainda_cobre = bool(candidato_original and candidato_original.get('pagamento_totalmente_coberto'))

        if original_ainda_cobre:
            escolhido = candidato_original
            reescolha_acionada = False
            criterio = str(decisao_original.get('criterio_decisao') or '')
            score_final = decisao_original.get('custo_economico_proxy')
            observacao = 'fonte sugerida na decisão local permaneceu viável após a depleção cumulativa observável; não foi necessário reescolher.'
        else:
            escolhido, criterio, observacao_selecao = _selecionar_candidato_decisao_local_v1(
                candidatos,
                valor_pagamento=valor_pagamento,
                proxy_version=proxy_version,
            )
            reescolha_acionada = True
            score_final = escolhido.get('custo_economico_proxy')
            observacao = 'recomputação dinâmica acionada porque a fonte sugerida originalmente deixou de cobrir integralmente o pagamento na sequência. ' + str(observacao_selecao or '')
            if primeira_reescolha is None:
                primeira_reescolha = {
                    'data_pagamento': pagamento.get('data'),
                    'descricao_pagamento': str(pagamento.get('descricao') or ''),
                    'valor_pagamento': valor_pagamento,
                    'lote_original': str(decisao_original.get('lote_id_escolhido') or ''),
                    'lote_final': _rotulo_fonte(escolhido),
                }

        saldo_antes_dinamico = round(float(escolhido.get('saldo_antes_dinamico') or 0.0), 2)
        bruto_dinamico = 0.0
        imposto_dinamico = 0.0
        liquido_dinamico = 0.0
        saldo_rem_dinamico = saldo_antes_dinamico
        coberto_dinamico = False

        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final = str(escolhido.get('lote_id') or '').strip()
        if tipo_final == 'lote_resgatavel' and lote_final:
            lote = mapa_lotes.get(lote_final)
            liquido_disponivel = round(float(escolhido.get('valor_disponivel') or 0.0), 2)
            coberto_dinamico = bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
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
                    saldo_antes_dinamico = round(float(movimento.get('saldo_antes') or 0.0), 2)
                    bruto_dinamico = round(float(movimento.get('bruto') or 0.0), 2)
                    imposto_dinamico = round(float(movimento.get('imposto') or 0.0), 2)
                    liquido_dinamico = round(float(movimento.get('liquido') or 0.0), 2)
                    saldo_rem_dinamico = round(float(movimento.get('saldo_remanescente') or 0.0), 2)
            else:
                saldo_rem_dinamico = saldo_antes_dinamico
        else:
            fonte_id_final = str(escolhido.get('fonte_base_escolhida') or escolhido.get('fonte_escolhida_id') or '').strip()
            coberto_dinamico = bool(saldo_antes_dinamico + tolerancia_monetaria >= valor_pagamento)
            liquido_dinamico = round(min(valor_pagamento, saldo_antes_dinamico), 2)
            bruto_dinamico = liquido_dinamico
            imposto_dinamico = 0.0
            saldo_rem_dinamico = round(max(saldo_antes_dinamico - liquido_dinamico, 0.0), 2)
            consumo_generico[fonte_id_final] = round(float(consumo_generico.get(fonte_id_final, 0.0) or 0.0) + liquido_dinamico, 2)

        mudou_fonte = bool(str(escolhido.get('fonte_escolhida_id') or '').strip() != fonte_original_id)
        if not reescolha_acionada:
            status_pos = 'mantido sem reescolha'
        elif coberto_dinamico:
            status_pos = 'reescolhido com cobertura integral' if mudou_fonte else 'reavaliado sem mudar a fonte e com cobertura integral'
        else:
            status_pos = 'reescolha acionada sem cobertura integral'
            if primeira_sem_cobertura is None:
                primeira_sem_cobertura = {
                    'data_pagamento': pagamento.get('data'),
                    'descricao_pagamento': str(pagamento.get('descricao') or ''),
                    'valor_pagamento': valor_pagamento,
                    'lote_final': _rotulo_fonte(escolhido),
                }

        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'lote_sugerido_original': str(decisao_original.get('lote_id_escolhido') or ''),
            'status_temporal_original': str(temporal_original.get('status_temporal') or ''),
            'reescolha_acionada': reescolha_acionada,
            'mudou_fonte': mudou_fonte,
            'fonte_final_id': str(escolhido.get('fonte_escolhida_id') or ''),
            'lote_final_dinamico': lote_final or _rotulo_fonte(escolhido),
            'tipo_fonte_final': tipo_final,
            'criterio_reescolha': criterio,
            'score_proxy_final': round(float(score_final or 0.0), 4) if score_final is not None else None,
            'status_pos_reescolha': status_pos,
            'saldo_antes_dinamico': saldo_antes_dinamico,
            'bruto_dinamico': bruto_dinamico,
            'imposto_dinamico': imposto_dinamico,
            'liquido_dinamico': liquido_dinamico,
            'saldo_remanescente_dinamico': saldo_rem_dinamico,
            'pagamento_totalmente_coberto_dinamico': coberto_dinamico,
            'observacao_reescolha': observacao.strip(),
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    amostra_reescolhas = []
    sub_re = quadro[quadro['reescolha_acionada'] == True].copy()
    if len(sub_re):
        for _, item in sub_re.head(10).iterrows():
            data = item.get('data_pagamento')
            amostra_reescolhas.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else str(data or ''),
                'Descrição': item.get('descricao_pagamento') or '',
                'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
                'Lote original': item.get('lote_sugerido_original') or '',
                'Lote dinâmico': item.get('lote_final_dinamico') or '',
                'Status pós-reescolha': item.get('status_pos_reescolha') or '',
                'Score final': round(float(item.get('score_proxy_final') or 0.0), 4) if item.get('score_proxy_final') is not None else '',
            })
    amostra_sem = []
    sub_sem = quadro[quadro['pagamento_totalmente_coberto_dinamico'] == False].copy()
    if len(sub_sem):
        for _, item in sub_sem.head(10).iterrows():
            data = item.get('data_pagamento')
            amostra_sem.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else str(data or ''),
                'Descrição': item.get('descricao_pagamento') or '',
                'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
                'Lote dinâmico': item.get('lote_final_dinamico') or '',
                'Saldo Antes dinâmico': round(float(item.get('saldo_antes_dinamico') or 0.0), 2),
                'Status pós-reescolha': item.get('status_pos_reescolha') or '',
            })

    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_mantidos_sem_reescolha': int((~quadro['reescolha_acionada']).sum()) if len(quadro) else 0,
        'pagamentos_com_reescolha_acionada': int(quadro['reescolha_acionada'].sum()) if len(quadro) else 0,
        'mudancas_efetivas_de_fonte': int(quadro['mudou_fonte'].sum()) if len(quadro) else 0,
        'pagamentos_cobertos_pos_reescolha': int(quadro['pagamento_totalmente_coberto_dinamico'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_pos_reescolha': int((~quadro['pagamento_totalmente_coberto_dinamico']).sum()) if len(quadro) else 0,
        'pagamentos_recuperados_pos_reescolha': int(((quadro['reescolha_acionada']) & (quadro['pagamento_totalmente_coberto_dinamico'])).sum()) if len(quadro) else 0,
        'primeira_reescolha_data': primeira_reescolha.get('data_pagamento') if primeira_reescolha else None,
        'primeira_reescolha_pagamento': primeira_reescolha.get('descricao_pagamento') if primeira_reescolha else None,
        'primeira_reescolha_lote_original': primeira_reescolha.get('lote_original') if primeira_reescolha else None,
        'primeira_reescolha_lote_final': primeira_reescolha.get('lote_final') if primeira_reescolha else None,
        'primeira_sem_cobertura_data': primeira_sem_cobertura.get('data_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_pagamento': primeira_sem_cobertura.get('descricao_pagamento') if primeira_sem_cobertura else None,
        'primeira_sem_cobertura_lote_final': primeira_sem_cobertura.get('lote_final') if primeira_sem_cobertura else None,
    }
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_reescolhas': amostra_reescolhas,
        'amostra_sem_cobertura': amostra_sem,
    }
    return PacoteReescolhaDinamicaPosQuebra(quadro_reescolha_dinamica=quadro, auditoria=auditoria)
