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
from nucleo.nucleo_financeiro_minimo import executar_saque_lote
from nucleo.reescolha_dinamica_pos_quebra import _ajustar_candidatos_dinamicos
from nucleo.utilitarios_neutros import limpar_texto


@dataclass(slots=True)
class PacoteRecomputacaoSequencialCentralV1:
    quadro_recomputacao_sequencial_central: pd.DataFrame
    auditoria: dict[str, Any]


def _rotulo_fonte(candidato: dict[str, Any]) -> str:
    lote_id = str(candidato.get('lote_id') or candidato.get('lote_id_escolhido') or '').strip()
    if lote_id:
        return lote_id
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _classe_pagamento_operacional(descricao: str) -> str:
    texto = limpar_texto(descricao).lower()
    protegida = ['cemig', 'condom', 'aluguel', 'tratamento', 'escola', 'internet']
    semiprotegida = ['cartão', 'cartao', 'claro']
    if any(k in texto for k in protegida):
        return 'PROTEGIDA'
    if any(k in texto for k in semiprotegida):
        return 'SEMIPROTEGIDA'
    return 'FLEXIVEL'


def _simular_movimento_candidato(
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
    tipo = str(candidato.get('tipo_fonte_escolhida') or '').strip()
    lote_id = str(candidato.get('lote_id') or '').strip()
    saldo_antes = round(float(candidato.get('saldo_antes_dinamico') or candidato.get('valor_disponivel') or 0.0), 2)
    bruto = 0.0
    imposto = 0.0
    liquido = 0.0
    saldo_rem = saldo_antes
    patrimonio_delta = 0.0
    if tipo == 'lote_resgatavel' and lote_id:
        lote_atual = mapa_lotes.get(lote_id)
        lote_sim = deepcopy(lote_atual) if lote_atual is not None else None
        liquido_disponivel_antes = round(float(candidato.get('valor_disponivel') or 0.0), 2)
        if lote_sim is not None and liquido_disponivel_antes > tolerancia_monetaria:
            liquido_alvo = round(min(valor_pagamento, liquido_disponivel_antes), 2)
            movimento = executar_saque_lote(
                lote_sim,
                liquido_alvo,
                data_referencia,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                tolerancia_monetaria=tolerancia_monetaria,
            )
            if movimento is not None:
                bruto = round(float(movimento.get('bruto') or 0.0), 2)
                imposto = round(float(movimento.get('imposto') or 0.0), 2)
                liquido = round(float(movimento.get('liquido') or 0.0), 2)
                saldo_rem = round(float(movimento.get('saldo_remanescente') or 0.0), 2)
                liquido_disponivel_depois = round(float(lote_sim.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
                patrimonio_delta = round(liquido_disponivel_antes - liquido_disponivel_depois, 2)
        return {
            'tipo_fonte_final': tipo,
            'lote_final_central': lote_id,
            'fonte_final_id': str(candidato.get('fonte_escolhida_id') or ''),
            'saldo_antes_central': saldo_antes,
            'bruto_central': bruto,
            'imposto_central': imposto,
            'liquido_central': liquido,
            'saldo_remanescente_central': saldo_rem,
            'pagamento_totalmente_coberto_central': bool(liquido + tolerancia_monetaria >= valor_pagamento),
            'mapa_lotes_pos': lote_sim,
            'consumo_generico_pos': None,
            'patrimonio_delta': patrimonio_delta,
        }

    fonte_id = str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()
    liquido = round(min(valor_pagamento, saldo_antes), 2)
    bruto = liquido
    imposto = 0.0
    saldo_rem = round(max(saldo_antes - liquido, 0.0), 2)
    patrimonio_delta = round(liquido, 2)
    return {
        'tipo_fonte_final': tipo,
        'lote_final_central': _rotulo_fonte(candidato),
        'fonte_final_id': str(candidato.get('fonte_escolhida_id') or ''),
        'saldo_antes_central': saldo_antes,
        'bruto_central': bruto,
        'imposto_central': imposto,
        'liquido_central': liquido,
        'saldo_remanescente_central': saldo_rem,
        'pagamento_totalmente_coberto_central': bool(liquido + tolerancia_monetaria >= valor_pagamento),
        'mapa_lotes_pos': None,
        'consumo_generico_pos': {fonte_id: round(float(consumo_generico.get(fonte_id, 0.0) or 0.0) + liquido, 2)},
        'patrimonio_delta': patrimonio_delta,
    }


def _patrimonio_terminal_proxy(
    candidatos_ajustados: list[dict[str, Any]],
    *,
    candidato_escolhido: dict[str, Any],
    movimento_simulado: dict[str, Any],
    data_referencia: date,
    mapa_lotes: dict[str, Any],
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> float:
    total = 0.0
    vistos: set[str] = set()
    lote_sim_pos = movimento_simulado.get('mapa_lotes_pos')
    consumo_pos = movimento_simulado.get('consumo_generico_pos') or {}
    fonte_escolhida = str(candidato_escolhido.get('fonte_escolhida_id') or '')
    for candidato in candidatos_ajustados:
        fonte_id = str(candidato.get('fonte_escolhida_id') or '')
        if not fonte_id or fonte_id in vistos:
            continue
        vistos.add(fonte_id)
        tipo = str(candidato.get('tipo_fonte_escolhida') or '').strip()
        lote_id = str(candidato.get('lote_id') or '').strip()
        if tipo == 'lote_resgatavel' and lote_id:
            if fonte_id == fonte_escolhida and lote_sim_pos is not None:
                valor = round(float(lote_sim_pos.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
            else:
                lote = mapa_lotes.get(lote_id)
                valor = round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2) if lote is not None else 0.0
        else:
            valor = round(float(candidato.get('saldo_antes_dinamico') or candidato.get('valor_disponivel') or 0.0), 2)
            if fonte_id in consumo_pos:
                valor = max(round(valor - float(consumo_pos.get(fonte_id, 0.0) or 0.0), 2), 0.0)
            elif fonte_id == fonte_escolhida:
                valor = round(float(movimento_simulado.get('saldo_remanescente_central') or 0.0), 2)
        total += max(valor, 0.0)
    return round(total, 2)


def _comparador_central(
    *,
    classe_pagamento: str,
    valor_pagamento: float,
    candidato: dict[str, Any],
    candidatos_ajustados: list[dict[str, Any]],
    movimento_simulado: dict[str, Any],
    data_referencia: date,
    mapa_lotes: dict[str, Any],
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    proxy_version: str,
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    score_proxy, detalhes = _score_proxy_economico_por_versao(proxy_version, candidato, valor_pagamento=valor_pagamento)
    deficit = round(max(valor_pagamento - float(movimento_simulado.get('liquido_central') or 0.0), 0.0), 2)
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
    comparador = (
        violacao_protegida,
        round(severidade_protegida, 2),
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
        'violacao_protegida': violacao_protegida,
        'severidade_protegida': round(severidade_protegida, 2),
        'deficit_liquido_total': round(deficit, 2),
        'pagamento_sem_cobertura_integral': uncovered,
        'patrimonio_terminal_proxy': patrimonio,
        'penalidade_estrategica_central': penalidade_estrategica,
        'penalidade_fragmentacao_central': penalidade_fragmentacao,
        'score_proxy_central': round(float(score_proxy or 0.0), 4),
        'detalhes_proxy_componentes': detalhes,
    }
    return comparador, diagnostico


def carregar_recomputacao_sequencial_central_v1(
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
) -> PacoteRecomputacaoSequencialCentralV1:
    pagamentos_alvo = _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional',
        'lote_sugerido_original', 'lote_final_central', 'fonte_final_id', 'tipo_fonte_final', 'mudou_vs_decisao_local',
        'criterio_central', 'status_central', 'score_proxy_central', 'violacao_protegida', 'severidade_protegida',
        'deficit_liquido_total', 'pagamento_sem_cobertura_integral', 'patrimonio_terminal_proxy',
        'penalidade_estrategica_central', 'penalidade_fragmentacao_central', 'saldo_antes_central', 'bruto_central',
        'imposto_central', 'liquido_central', 'saldo_remanescente_central', 'pagamento_totalmente_coberto_central',
        'observacao_central',
    ]
    if len(pagamentos_alvo) == 0:
        return PacoteRecomputacaoSequencialCentralV1(
            quadro_recomputacao_sequencial_central=pd.DataFrame(columns=colunas),
            auditoria={
                'validacao': {'ok': False, 'erros': ['recomputacao_sequencial_central_sem_pagamentos_alvo'], 'avisos': []},
                'resumo': {'total_pagamentos_auditados': 0},
                'amostra_mudancas': [],
                'amostra_sem_cobertura': [],
            },
        )

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_saldo = saldo_disponivel_geral.quadro_saldo_disponivel.copy()
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    mapa_lotes = {str(l.id): deepcopy(l) for l in getattr(replay_passado, 'lotes_apos_replay', [])}
    consumo_generico: dict[str, float] = {}
    mapa_decisao = {
        str(row.get('pagamento_id') or '').strip(): row
        for row in decisao_local_v1.quadro_decisao_local_v1.to_dict(orient='records')
    } if decisao_local_v1 is not None else {}

    registros: list[dict[str, Any]] = []
    primeira_sem = None
    primeira_protegida = None

    pagamentos_alvo = pagamentos_alvo.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        classe_pagamento = _classe_pagamento_operacional(str(pagamento.get('descricao') or ''))
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

        escolhido = None
        melhor_cmp = None
        melhor_diag: dict[str, Any] = {}
        melhor_mov: dict[str, Any] = {}
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
            cmp_tuple, diag = _comparador_central(
                classe_pagamento=classe_pagamento,
                valor_pagamento=valor_pagamento,
                candidato=candidato,
                candidatos_ajustados=candidatos,
                movimento_simulado=movimento,
                data_referencia=data_referencia,
                mapa_lotes=mapa_lotes,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                proxy_version=proxy_version,
            )
            if melhor_cmp is None or cmp_tuple < melhor_cmp:
                melhor_cmp = cmp_tuple
                escolhido = candidato
                melhor_diag = diag
                melhor_mov = movimento

        assert escolhido is not None
        tipo_final = str(escolhido.get('tipo_fonte_escolhida') or '').strip()
        lote_final = str(escolhido.get('lote_id') or '').strip()
        fonte_final_id = str(escolhido.get('fonte_escolhida_id') or '')
        if tipo_final == 'lote_resgatavel' and lote_final and melhor_mov.get('mapa_lotes_pos') is not None:
            mapa_lotes[lote_final] = melhor_mov['mapa_lotes_pos']
        elif melhor_mov.get('consumo_generico_pos'):
            for fonte_id, consumido in melhor_mov['consumo_generico_pos'].items():
                consumo_generico[fonte_id] = round(float(consumido or 0.0), 2)

        coberto = bool(melhor_mov.get('pagamento_totalmente_coberto_central'))
        if melhor_diag.get('violacao_protegida') and primeira_protegida is None:
            primeira_protegida = {
                'Data': pagamento.get('data'),
                'Descrição': str(pagamento.get('descricao') or ''),
                'Valor': valor_pagamento,
                'Lote central': lote_final or _rotulo_fonte(escolhido),
            }
        if not coberto and primeira_sem is None:
            primeira_sem = {
                'Data': pagamento.get('data'),
                'Descrição': str(pagamento.get('descricao') or ''),
                'Valor': valor_pagamento,
                'Lote central': lote_final or _rotulo_fonte(escolhido),
            }

        decisao_original = mapa_decisao.get(pagamento_id, {})
        mudou = bool(str(decisao_original.get('fonte_escolhida_id') or '').strip() != fonte_final_id)
        if melhor_diag.get('violacao_protegida'):
            status = 'violacao de pagamento protegida'
        elif coberto:
            status = 'coberto pela recomputacao central'
        elif float(melhor_mov.get('liquido_central') or 0.0) > 0:
            status = 'cobertura parcial na recomputacao central'
        else:
            status = 'sem cobertura na recomputacao central'

        observacao = (
            f"comparador central => protegida={melhor_diag.get('violacao_protegida')}, deficit={melhor_diag.get('deficit_liquido_total'):.2f}, "
            f"sem_integral={melhor_diag.get('pagamento_sem_cobertura_integral')}, patrimonio_proxy={melhor_diag.get('patrimonio_terminal_proxy'):.2f}, "
            f"pen_estrat={melhor_diag.get('penalidade_estrategica_central'):.4f}, pen_frag={melhor_diag.get('penalidade_fragmentacao_central'):.4f}."
        )
        registros.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': str(pagamento.get('descricao') or ''),
            'valor_pagamento': valor_pagamento,
            'classe_pagamento_operacional': classe_pagamento,
            'lote_sugerido_original': str(decisao_original.get('lote_id_escolhido') or ''),
            'lote_final_central': lote_final or _rotulo_fonte(escolhido),
            'fonte_final_id': fonte_final_id,
            'tipo_fonte_final': tipo_final,
            'mudou_vs_decisao_local': mudou,
            'criterio_central': 'metrica_canonica_minima_central',
            'status_central': status,
            'score_proxy_central': melhor_diag.get('score_proxy_central'),
            'violacao_protegida': melhor_diag.get('violacao_protegida'),
            'severidade_protegida': melhor_diag.get('severidade_protegida'),
            'deficit_liquido_total': melhor_diag.get('deficit_liquido_total'),
            'pagamento_sem_cobertura_integral': melhor_diag.get('pagamento_sem_cobertura_integral'),
            'patrimonio_terminal_proxy': melhor_diag.get('patrimonio_terminal_proxy'),
            'penalidade_estrategica_central': melhor_diag.get('penalidade_estrategica_central'),
            'penalidade_fragmentacao_central': melhor_diag.get('penalidade_fragmentacao_central'),
            'saldo_antes_central': melhor_mov.get('saldo_antes_central'),
            'bruto_central': melhor_mov.get('bruto_central'),
            'imposto_central': melhor_mov.get('imposto_central'),
            'liquido_central': melhor_mov.get('liquido_central'),
            'saldo_remanescente_central': melhor_mov.get('saldo_remanescente_central'),
            'pagamento_totalmente_coberto_central': coberto,
            'observacao_central': observacao,
        })

    quadro = pd.DataFrame(registros, columns=colunas).sort_values(by=['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    resumo = {
        'total_pagamentos_auditados': int(len(quadro)),
        'pagamentos_cobertos_integral_central': int(quadro['pagamento_totalmente_coberto_central'].sum()) if len(quadro) else 0,
        'pagamentos_sem_cobertura_integral': int(quadro['pagamento_sem_cobertura_integral'].sum()) if len(quadro) else 0,
        'violacoes_pagamentos_protegida': int(quadro['violacao_protegida'].sum()) if len(quadro) else 0,
        'deficit_liquido_total_central': round(float(quadro['deficit_liquido_total'].sum()), 2) if len(quadro) else 0.0,
        'mudancas_vs_decisao_local': int(quadro['mudou_vs_decisao_local'].sum()) if len(quadro) else 0,
        'patrimonio_terminal_proxy_final': round(float(quadro.iloc[-1].get('patrimonio_terminal_proxy') or 0.0), 2) if len(quadro) else 0.0,
        'primeira_sem_cobertura_data': primeira_sem.get('Data') if primeira_sem else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.get('Descrição') if primeira_sem else None,
        'primeira_violation_protegida_data': primeira_protegida.get('Data') if primeira_protegida else None,
        'primeira_violation_protegida_pagamento': primeira_protegida.get('Descrição') if primeira_protegida else None,
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
        })
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_mudancas': amostra_mudancas,
        'amostra_sem_cobertura': amostra_sem_cobertura,
    }
    return PacoteRecomputacaoSequencialCentralV1(quadro_recomputacao_sequencial_central=quadro, auditoria=auditoria)
