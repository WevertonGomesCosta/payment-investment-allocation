from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.utilitarios_neutros import _rotulo_fonte


@dataclass(slots=True)
class PacoteAuditoriaTemporalDecisaoLocal:
    quadro_auditoria_temporal: pd.DataFrame
    auditoria: dict[str, Any]


def _fonte_temporal_id(linha: dict[str, Any]) -> str:
    return str(linha.get('fonte_base_escolhida') or linha.get('fonte_escolhida_id') or 'sem_fonte').strip()



def carregar_auditoria_temporal_decisao_local(
    decisao_local_v1,
    replay_passado,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    tolerancia_monetaria: float = 0.01,
) -> PacoteAuditoriaTemporalDecisaoLocal:
    quadro_local = decisao_local_v1.quadro_decisao_local_v1.copy() if decisao_local_v1 is not None else pd.DataFrame()
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'tipo_fonte_escolhida',
        'fonte_base_escolhida', 'fonte_escolhida_id', 'lote_id_escolhido', 'sequencia_global', 'sequencia_na_fonte',
        'saldo_antes_local', 'status_local', 'saldo_antes_temporal', 'bruto_temporal', 'imposto_temporal',
        'liquido_temporal', 'saldo_remanescente_temporal', 'pagamento_totalmente_coberto_temporal',
        'status_temporal', 'primeira_quebra_global', 'primeira_quebra_na_fonte', 'requer_reescolha_dinamica',
        'observacao_temporal',
    ]
    if len(quadro_local) == 0:
        return PacoteAuditoriaTemporalDecisaoLocal(
            quadro_auditoria_temporal=pd.DataFrame(columns=colunas),
            auditoria={
                'validacao': {'ok': False, 'erros': ['auditoria_temporal_sem_decisao_local'], 'avisos': []},
                'resumo': {'total_pagamentos_auditados': 0},
                'amostra_primeiras_quebras': [],
                'resumo_fontes_com_quebra': [],
            },
        )

    quadro_local = quadro_local.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    estados_genericos: dict[str, dict[str, Any]] = {}
    contagem_fontes: dict[str, int] = {}
    primeira_quebra_por_fonte: dict[str, dict[str, Any]] = {}
    primeira_quebra_global: dict[str, Any] | None = None
    linhas: list[dict[str, Any]] = []

    for idx, row in enumerate(quadro_local.to_dict(orient='records'), start=1):
        pagamento_id = str(row.get('pagamento_id') or '').strip()
        valor_pagamento = round(float(row.get('valor_pagamento') or 0.0), 2)
        tipo_fonte = str(row.get('tipo_fonte_escolhida') or '').strip()
        fonte_id = _fonte_temporal_id(row)
        lote_id = str(row.get('lote_id_escolhido') or '').strip()
        contagem_fontes[fonte_id] = contagem_fontes.get(fonte_id, 0) + 1
        seq_fonte = contagem_fontes[fonte_id]
        local_coberto = bool(row.get('pagamento_totalmente_coberto'))
        status_local = 'integral na decisão local' if local_coberto else 'parcial/ausente na decisão local'

        saldo_antes_temporal = 0.0
        bruto_temporal = 0.0
        imposto_temporal = 0.0
        liquido_temporal = 0.0
        saldo_rem_temporal = 0.0
        temporal_coberto = False
        observacao_temporal = ''

        if tipo_fonte == 'lote_resgatavel' and lote_id:
            lote = mapa_lotes.get(lote_id)
            if lote is None:
                observacao_temporal = 'lote sugerido não foi encontrado na base pós-replay para auditoria temporal.'
            else:
                saldo_antes_temporal = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
                liquido_disponivel = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
                temporal_coberto = bool(liquido_disponivel + tolerancia_monetaria >= valor_pagamento)
                liquido_alvo = min(valor_pagamento, liquido_disponivel)
                if liquido_alvo > tolerancia_monetaria:
                    movimento = executar_saque_lote(
                        lote,
                        liquido_alvo,
                        data_referencia,
                        tabela_iof=tabela_iof,
                        faixas_ir=faixas_ir,
                        tolerancia_monetaria=tolerancia_monetaria,
                    )
                    if movimento is not None:
                        bruto_temporal = round(float(movimento.get('bruto') or 0.0), 2)
                        imposto_temporal = round(float(movimento.get('imposto') or 0.0), 2)
                        liquido_temporal = round(float(movimento.get('liquido') or 0.0), 2)
                        saldo_rem_temporal = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
                else:
                    saldo_rem_temporal = saldo_antes_temporal
                if temporal_coberto:
                    observacao_temporal = 'sugestão local permanece viável quando o lote é abatido cumulativamente na fotografia da data de referência.'
                else:
                    observacao_temporal = (
                        f'saldo líquido disponível na sequência ({liquido_disponivel:.2f}) ficou abaixo do pagamento alvo '
                        f'({valor_pagamento:.2f}); a sugestão local exige reescolha dinâmica a partir deste ponto.'
                    )
        else:
            estado = estados_genericos.setdefault(
                fonte_id,
                {'saldo_remanescente_liquido': round(float(row.get('valor_disponivel_escolhido') or 0.0), 2)},
            )
            saldo_antes_temporal = round(float(estado.get('saldo_remanescente_liquido') or 0.0), 2)
            temporal_coberto = bool(saldo_antes_temporal + tolerancia_monetaria >= valor_pagamento)
            liquido_temporal = round(min(valor_pagamento, saldo_antes_temporal), 2)
            bruto_temporal = liquido_temporal
            imposto_temporal = 0.0
            saldo_rem_temporal = round(max(saldo_antes_temporal - liquido_temporal, 0.0), 2)
            estado['saldo_remanescente_liquido'] = saldo_rem_temporal
            if temporal_coberto:
                observacao_temporal = 'fonte não-lote permanece viável sob abatimento cumulativo simples do saldo líquido observável.'
            else:
                observacao_temporal = (
                    f'saldo líquido observável na sequência ({saldo_antes_temporal:.2f}) ficou abaixo do pagamento alvo '
                    f'({valor_pagamento:.2f}); a sugestão local exige reescolha dinâmica a partir deste ponto.'
                )

        primeira_quebra_fonte = False
        primeira_quebra_global_flag = False
        if local_coberto and not temporal_coberto:
            if fonte_id not in primeira_quebra_por_fonte:
                primeira_quebra_fonte = True
                primeira_quebra_por_fonte[fonte_id] = {
                    'fonte_temporal_id': fonte_id,
                    'fonte_rotulo': _rotulo_fonte(row),
                    'tipo_fonte': tipo_fonte,
                    'data_pagamento': row.get('data_pagamento'),
                    'pagamento_id': pagamento_id,
                    'descricao_pagamento': row.get('descricao_pagamento'),
                    'valor_pagamento': valor_pagamento,
                    'sequencia_na_fonte': seq_fonte,
                    'saldo_antes_temporal': saldo_antes_temporal,
                }
            if primeira_quebra_global is None:
                primeira_quebra_global_flag = True
                primeira_quebra_global = {
                    'fonte_temporal_id': fonte_id,
                    'fonte_rotulo': _rotulo_fonte(row),
                    'tipo_fonte': tipo_fonte,
                    'data_pagamento': row.get('data_pagamento'),
                    'pagamento_id': pagamento_id,
                    'descricao_pagamento': row.get('descricao_pagamento'),
                    'valor_pagamento': valor_pagamento,
                    'sequencia_na_fonte': seq_fonte,
                    'saldo_antes_temporal': saldo_antes_temporal,
                }

        if not local_coberto:
            status_temporal = 'já parcial na decisão local'
        elif temporal_coberto:
            status_temporal = 'coerente na sequência'
        elif primeira_quebra_fonte:
            status_temporal = 'primeira quebra temporal da fonte'
        else:
            status_temporal = 'após quebra temporal da fonte'

        linhas.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': row.get('data_pagamento'),
            'descricao_pagamento': row.get('descricao_pagamento'),
            'valor_pagamento': valor_pagamento,
            'tipo_fonte_escolhida': tipo_fonte,
            'fonte_base_escolhida': fonte_id,
            'fonte_escolhida_id': row.get('fonte_escolhida_id'),
            'lote_id_escolhido': lote_id,
            'sequencia_global': idx,
            'sequencia_na_fonte': seq_fonte,
            'saldo_antes_local': round(float(row.get('valor_disponivel_escolhido') or 0.0), 2),
            'status_local': status_local,
            'saldo_antes_temporal': saldo_antes_temporal,
            'bruto_temporal': bruto_temporal,
            'imposto_temporal': imposto_temporal,
            'liquido_temporal': liquido_temporal,
            'saldo_remanescente_temporal': saldo_rem_temporal,
            'pagamento_totalmente_coberto_temporal': temporal_coberto,
            'status_temporal': status_temporal,
            'primeira_quebra_global': primeira_quebra_global_flag,
            'primeira_quebra_na_fonte': primeira_quebra_fonte,
            'requer_reescolha_dinamica': bool(local_coberto and not temporal_coberto),
            'observacao_temporal': observacao_temporal,
        })

    quadro = pd.DataFrame(linhas)
    amostra_primeiras_quebras = []
    if len(quadro):
        sub_q = quadro[quadro['primeira_quebra_na_fonte'] == True].copy()
        if len(sub_q):
            for _, item in sub_q.sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').iterrows():
                amostra_primeiras_quebras.append({
                    'Data': item.get('data_pagamento'),
                    'Descrição': item.get('descricao_pagamento'),
                    'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
                    'Lote sugerido': _rotulo_fonte(item),
                    'Seq. fonte': int(item.get('sequencia_na_fonte') or 0),
                    'Saldo Antes temporal': round(float(item.get('saldo_antes_temporal') or 0.0), 2),
                    'Status temporal': item.get('status_temporal'),
                })

    resumo_fontes_com_quebra = []
    for fonte_id, item in sorted(primeira_quebra_por_fonte.items(), key=lambda kv: (kv[1].get('data_pagamento'), kv[1].get('pagamento_id'))):
        resumo_fontes_com_quebra.append({
            'Fonte': item.get('fonte_rotulo') or fonte_id,
            'Tipo': item.get('tipo_fonte') or '',
            'Primeira quebra': item.get('data_pagamento'),
            'Pagamento': item.get('descricao_pagamento') or '',
            'Valor': round(float(item.get('valor_pagamento') or 0.0), 2),
            'Seq. fonte': int(item.get('sequencia_na_fonte') or 0),
        })

    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_integral_local': int(quadro['status_local'].eq('integral na decisão local').sum()) if len(quadro) else 0,
        'pagamentos_integral_temporal': int(quadro['pagamento_totalmente_coberto_temporal'].fillna(False).sum()) if len(quadro) else 0,
        'pagamentos_com_quebra_temporal': int(quadro['requer_reescolha_dinamica'].fillna(False).sum()) if len(quadro) else 0,
        'pagamentos_apos_quebra_fonte': int(quadro['status_temporal'].eq('após quebra temporal da fonte').sum()) if len(quadro) else 0,
        'fontes_auditadas': int(quadro['fonte_base_escolhida'].astype(str).nunique()) if len(quadro) else 0,
        'fontes_com_quebra_temporal': int(len(primeira_quebra_por_fonte)),
        'primeira_quebra_global_data': primeira_quebra_global.get('data_pagamento') if primeira_quebra_global else None,
        'primeira_quebra_global_pagamento': primeira_quebra_global.get('descricao_pagamento') if primeira_quebra_global else None,
        'primeira_quebra_global_lote': primeira_quebra_global.get('fonte_rotulo') if primeira_quebra_global else None,
        'primeira_quebra_global_valor': round(float(primeira_quebra_global.get('valor_pagamento') or 0.0), 2) if primeira_quebra_global else None,
        'primeira_quebra_global_seq_fonte': int(primeira_quebra_global.get('sequencia_na_fonte') or 0) if primeira_quebra_global else None,
    }

    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_primeiras_quebras': amostra_primeiras_quebras,
        'resumo_fontes_com_quebra': resumo_fontes_com_quebra,
    }
    return PacoteAuditoriaTemporalDecisaoLocal(quadro_auditoria_temporal=quadro, auditoria=auditoria)
