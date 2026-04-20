from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
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


def _coerce_date(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, pd.Timestamp):
        return valor.date()
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return None


def _rotulo_fonte(candidato: dict[str, Any]) -> str:
    lote_id = str(candidato.get('lote_id') or candidato.get('lote_id_escolhido') or '').strip()
    if lote_id:
        return lote_id
    return str(candidato.get('fonte_base_escolhida') or candidato.get('fonte_escolhida_id') or '').strip()


def _perfil_pagamento_operacional(descricao: str, valor_pagamento: float = 0.0) -> dict[str, Any]:
    texto = limpar_texto(descricao).lower()
    if 'tratamento' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_A_TRATAMENTO',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 0,
        }
    if 'escola' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_A_ESCOLA',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 1,
        }
    if 'aluguel' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_A_ALUGUEL',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 2,
        }
    if 'condom' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_A_CONDOMINIO',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 3,
        }
    if 'internet' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_B_INTERNET',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 4,
        }
    if 'cemig' in texto:
        return {
            'classe': 'PROTEGIDA',
            'subclasse': 'PROTEGIDA_B_CEMIG',
            'prioridade_classe': 0,
            'prioridade_intraclasse': 5,
        }
    if 'cartão' in texto or 'cartao' in texto:
        if float(valor_pagamento or 0.0) >= 1000.0:
            return {
                'classe': 'SEMIPROTEGIDA',
                'subclasse': 'SEMIPROTEGIDA_A_CARTAO_MATERIAL',
                'prioridade_classe': 1,
                'prioridade_intraclasse': 8,
            }
        return {
            'classe': 'SEMIPROTEGIDA',
            'subclasse': 'SEMIPROTEGIDA_B_CARTAO',
            'prioridade_classe': 1,
            'prioridade_intraclasse': 10,
        }
    if 'claro' in texto:
        return {
            'classe': 'SEMIPROTEGIDA',
            'subclasse': 'SEMIPROTEGIDA_C_CLARO',
            'prioridade_classe': 1,
            'prioridade_intraclasse': 11,
        }
    return {
        'classe': 'FLEXIVEL',
        'subclasse': 'FLEXIVEL',
        'prioridade_classe': 2,
        'prioridade_intraclasse': 20,
    }


def _peso_subclasse_protegida(subclasse: str) -> float:
    pesos = {
        'PROTEGIDA_A_TRATAMENTO': 1.00,
        'PROTEGIDA_A_ESCOLA': 1.00,
        'PROTEGIDA_A_ALUGUEL': 0.95,
        'PROTEGIDA_A_CONDOMINIO': 0.95,
        'PROTEGIDA_B_INTERNET': 0.70,
        'PROTEGIDA_B_CEMIG': 0.70,
    }
    return float(pesos.get(subclasse, 0.0))


def _peso_horizonte_protegida(dias: int) -> float:
    if dias <= 0:
        return 1.30
    if dias <= 7:
        return 1.00
    if dias <= 14:
        return 0.75
    if dias <= 21:
        return 0.70
    if dias <= 30:
        return 0.45
    return 0.15


def _demanda_protegida_futura_ponderada(pagamentos_futuros: list[dict[str, Any]], data_pagamento_atual: date) -> dict[str, float]:
    demanda_ponderada = 0.0
    demanda_7d = 0.0
    demanda_14d = 0.0
    demanda_21d = 0.0
    for pagamento in pagamentos_futuros:
        classe = str(pagamento.get('classe_pagamento_operacional') or '')
        if classe != 'PROTEGIDA':
            continue
        data_pagamento = _coerce_date(pagamento.get('data'))
        if data_pagamento is None:
            continue
        dias = (data_pagamento - data_pagamento_atual).days
        valor = round(float(pagamento.get('valor') or 0.0), 2)
        peso = _peso_subclasse_protegida(str(pagamento.get('subclasse_pagamento_operacional') or '')) * _peso_horizonte_protegida(dias)
        demanda_ponderada += valor * peso
        if dias <= 7:
            demanda_7d += valor
        if dias <= 14:
            demanda_14d += valor
        if dias <= 21:
            demanda_21d += valor
    return {
        'demanda_protegida_futura_ponderada': round(demanda_ponderada, 2),
        'demanda_protegida_futura_7d': round(demanda_7d, 2),
        'demanda_protegida_futura_14d': round(demanda_14d, 2),
        'demanda_protegida_futura_21d': round(demanda_21d, 2),
    }




def _cap_penalidade_escassez_protegida_futura(
    classe_pagamento: str,
    subclasse_pagamento: str,
    valor_pagamento: float,
) -> float:
    valor = max(round(float(valor_pagamento or 0.0), 2), 0.0)
    if valor <= 0.0:
        return 0.0
    if classe_pagamento == 'PROTEGIDA':
        return round(min(valor * 0.25, 900.0), 4)
    if subclasse_pagamento == 'SEMIPROTEGIDA_A_CARTAO_MATERIAL':
        return round(min(valor * 0.28, 1400.0), 4)
    if classe_pagamento == 'SEMIPROTEGIDA':
        return round(min(valor * 0.45, 900.0), 4)
    return round(min(valor * 0.75, 700.0), 4)


def _penalidade_severidade_deficit_atual(
    classe_pagamento: str,
    subclasse_pagamento: str,
    valor_pagamento: float,
    deficit: float,
) -> float:
    valor = max(float(valor_pagamento or 0.0), 0.0)
    deficit_val = max(float(deficit or 0.0), 0.0)
    if valor <= 0.0:
        return 0.0
    deficit_relativo = deficit_val / valor
    if subclasse_pagamento == 'SEMIPROTEGIDA_A_CARTAO_MATERIAL':
        return round(max(deficit_relativo - 0.72, 0.0), 6)
    if classe_pagamento == 'SEMIPROTEGIDA':
        return round(max(deficit_relativo - 0.80, 0.0), 6)
    return 0.0

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


def _penalidade_escassez_protegida_futura(
    *,
    classe_pagamento: str,
    subclasse_pagamento: str,
    valor_pagamento: float,
    candidato: dict[str, Any],
    movimento_simulado: dict[str, Any],
    candidatos_ajustados: list[dict[str, Any]],
    demanda_futura: dict[str, float],
) -> tuple[float, float, float, bool]:
    demanda_ponderada = round(float(demanda_futura.get('demanda_protegida_futura_ponderada') or 0.0), 2)
    if demanda_ponderada <= 0.0:
        return 0.0, 0.0, 0.0, False
    saldo_fonte = round(float(candidato.get('saldo_antes_dinamico') or candidato.get('valor_disponivel') or 0.0), 2)
    if saldo_fonte <= 0.0:
        return 0.0, 0.0, 0.0, False
    total_disponivel = round(sum(max(float(item.get('saldo_antes_dinamico') or item.get('valor_disponivel') or 0.0), 0.0) for item in candidatos_ajustados), 2)
    capacidade_outras_fontes = max(round(total_disponivel - saldo_fonte, 2), 0.0)
    reserva_dependente_desta_fonte = max(round(demanda_ponderada - capacidade_outras_fontes, 2), 0.0)
    consumo_efetivo = round(float(movimento_simulado.get('patrimonio_delta') or movimento_simulado.get('liquido_central') or 0.0), 2)
    base_penalizada = min(consumo_efetivo, reserva_dependente_desta_fonte)
    multiplicador = {
        'FLEXIVEL': 1.85,
        'SEMIPROTEGIDA': 1.15,
        'PROTEGIDA': 0.75,
    }.get(classe_pagamento, 1.0)
    if subclasse_pagamento == 'SEMIPROTEGIDA_A_CARTAO_MATERIAL':
        multiplicador = 0.65
    penalidade_bruta = round(base_penalizada * multiplicador, 4)
    cap_penalidade = _cap_penalidade_escassez_protegida_futura(classe_pagamento, subclasse_pagamento, valor_pagamento)
    penalidade = round(min(penalidade_bruta, cap_penalidade), 4) if cap_penalidade > 0 else penalidade_bruta
    fonte_critica = bool(reserva_dependente_desta_fonte > 0.0)
    return penalidade, penalidade_bruta, cap_penalidade, fonte_critica


def _comparador_central(
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
    demanda_futura: dict[str, float],
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
    penalidade_escassez_futura, penalidade_escassez_bruta, cap_penalidade_escassez, fonte_critica = _penalidade_escassez_protegida_futura(
        classe_pagamento=classe_pagamento,
        subclasse_pagamento=subclasse_pagamento,
        valor_pagamento=valor_pagamento,
        candidato=candidato,
        movimento_simulado=movimento_simulado,
        candidatos_ajustados=candidatos_ajustados,
        demanda_futura=demanda_futura,
    )
    penalidade_deficit_atual = _penalidade_severidade_deficit_atual(
        classe_pagamento,
        subclasse_pagamento,
        valor_pagamento,
        deficit,
    )
    if classe_pagamento == 'PROTEGIDA':
        comparador = (
            violacao_protegida,
            round(severidade_protegida, 2),
            round(deficit, 2),
            uncovered,
            round(penalidade_escassez_futura, 4),
            -patrimonio,
            penalidade_estrategica,
            penalidade_fragmentacao,
            round(float(score_proxy or 0.0), 4),
            str(candidato.get('fonte_escolhida_id') or ''),
        )
    else:
        comparador = (
            violacao_protegida,
            round(penalidade_deficit_atual, 6),
            round(penalidade_escassez_futura, 4),
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
        'penalidade_escassez_protegida_futura': penalidade_escassez_futura,
        'penalidade_escassez_protegida_futura_bruta': penalidade_escassez_bruta,
        'cap_penalidade_escassez_protegida_futura': cap_penalidade_escassez,
        'penalidade_deficit_atual': penalidade_deficit_atual,
        'demanda_protegida_futura_ponderada': float(demanda_futura.get('demanda_protegida_futura_ponderada') or 0.0),
        'demanda_protegida_futura_7d': float(demanda_futura.get('demanda_protegida_futura_7d') or 0.0),
        'demanda_protegida_futura_14d': float(demanda_futura.get('demanda_protegida_futura_14d') or 0.0),
        'demanda_protegida_futura_21d': float(demanda_futura.get('demanda_protegida_futura_21d') or 0.0),
        'fonte_critica_para_protegida_futura': fonte_critica,
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
        'subclasse_pagamento_operacional', 'prioridade_intraclasse_operacional', 'lote_sugerido_original',
        'lote_final_central', 'fonte_final_id', 'tipo_fonte_final', 'mudou_vs_decisao_local', 'criterio_central',
        'status_central', 'score_proxy_central', 'violacao_protegida', 'severidade_protegida',
        'deficit_liquido_total', 'pagamento_sem_cobertura_integral', 'patrimonio_terminal_proxy',
        'penalidade_estrategica_central', 'penalidade_fragmentacao_central', 'penalidade_escassez_protegida_futura',
        'demanda_protegida_futura_ponderada', 'demanda_protegida_futura_7d', 'demanda_protegida_futura_14d',
        'demanda_protegida_futura_21d', 'fonte_critica_para_protegida_futura', 'penalidade_escassez_protegida_futura_bruta',
        'cap_penalidade_escassez_protegida_futura', 'penalidade_deficit_atual', 'fonte_preservada_por_reserva',
        'fonte_preservada_referencia', 'fallback_sem_fonte_viavel', 'motivo_indisponibilidade_central',
        'saldo_antes_central', 'bruto_central', 'imposto_central', 'liquido_central', 'saldo_remanescente_central',
        'pagamento_totalmente_coberto_central', 'observacao_central',
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

    pagamentos_alvo = pagamentos_alvo.copy()
    perfis = pagamentos_alvo.apply(lambda row: _perfil_pagamento_operacional(row.get('descricao'), float(row.get('valor') or 0.0)), axis=1)
    pagamentos_alvo['classe_pagamento_operacional'] = perfis.apply(lambda x: x['classe'])
    pagamentos_alvo['subclasse_pagamento_operacional'] = perfis.apply(lambda x: x['subclasse'])
    pagamentos_alvo['prioridade_classe_operacional'] = perfis.apply(lambda x: x['prioridade_classe'])
    pagamentos_alvo['prioridade_intraclasse_operacional'] = perfis.apply(lambda x: x['prioridade_intraclasse'])
    pagamentos_alvo = pagamentos_alvo.sort_values(
        by=['data', 'prioridade_classe_operacional', 'prioridade_intraclasse_operacional', 'despesa_id'],
        kind='stable',
    ).reset_index(drop=True)
    pagamentos_ordenados = pagamentos_alvo.to_dict(orient='records')

    registros: list[dict[str, Any]] = []
    primeira_sem = None
    primeira_protegida = None
    primeiro_sem_fonte_viavel = None
    primeira_fonte_preservada_por_reserva = None

    for indice, pagamento in enumerate(pagamentos_ordenados):
        pagamento_id = str(pagamento.get('despesa_id') or '').strip()
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        classe_pagamento = str(pagamento.get('classe_pagamento_operacional') or '')
        subclasse_pagamento = str(pagamento.get('subclasse_pagamento_operacional') or '')
        prioridade_intraclasse = int(pagamento.get('prioridade_intraclasse_operacional') or 99)
        data_pagamento = _coerce_date(pagamento.get('data')) or data_referencia
        pagamentos_futuros = pagamentos_ordenados[indice + 1:]
        demanda_futura = _demanda_protegida_futura_ponderada(pagamentos_futuros, data_pagamento)
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
            cmp_tuple, diag = _comparador_central(
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
                demanda_futura=demanda_futura,
            )
            avaliacoes.append({'candidato': candidato, 'movimento': movimento, 'comparador': cmp_tuple, 'diagnostico': diag})

        avaliacoes = sorted(avaliacoes, key=lambda item: item['comparador'])
        melhor = avaliacoes[0]
        melhor_liquidez = max(avaliacoes, key=lambda item: (round(float(item['movimento'].get('liquido_central') or 0.0), 2), -float(item['diagnostico'].get('penalidade_escassez_protegida_futura') or 0.0)))
        escolhido = melhor['candidato']
        melhor_diag = melhor['diagnostico']
        melhor_mov = melhor['movimento']
        max_liquido_potencial = round(float(melhor_liquidez['movimento'].get('liquido_central') or 0.0), 2)
        fonte_referencia_reserva = melhor_liquidez['candidato']
        fallback_sem_fonte_viavel = bool(max_liquido_potencial <= tolerancia_monetaria)
        fonte_preservada_por_reserva = bool(
            not fallback_sem_fonte_viavel
            and round(float(melhor_mov.get('liquido_central') or 0.0), 2) + tolerancia_monetaria < max_liquido_potencial
            and round(float(melhor_diag.get('penalidade_escassez_protegida_futura') or 0.0), 4) > 0.0
            and str(fonte_referencia_reserva.get('fonte_escolhida_id') or '') != str(escolhido.get('fonte_escolhida_id') or '')
        )
        motivo_indisponibilidade = 'nao_aplicavel'
        if fallback_sem_fonte_viavel:
            motivo_indisponibilidade = 'sem_fonte_viavel'
        elif fonte_preservada_por_reserva:
            motivo_indisponibilidade = 'fonte_preservada_por_reserva'

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
        if fallback_sem_fonte_viavel and primeiro_sem_fonte_viavel is None:
            primeiro_sem_fonte_viavel = {
                'Data': pagamento.get('data'),
                'Descrição': str(pagamento.get('descricao') or ''),
                'Valor': valor_pagamento,
            }
        if fonte_preservada_por_reserva and primeira_fonte_preservada_por_reserva is None:
            primeira_fonte_preservada_por_reserva = {
                'Data': pagamento.get('data'),
                'Descrição': str(pagamento.get('descricao') or ''),
                'Valor': valor_pagamento,
                'Fonte preservada': _rotulo_fonte(fonte_referencia_reserva),
            }

        decisao_original = mapa_decisao.get(pagamento_id, {})
        mudou = bool(str(decisao_original.get('fonte_escolhida_id') or '').strip() != fonte_final_id)
        if fallback_sem_fonte_viavel:
            status = 'sem fonte viável na recomputação central'
        elif fonte_preservada_por_reserva and coberto:
            status = 'coberto com fonte preservada por reserva'
        elif fonte_preservada_por_reserva and float(melhor_mov.get('liquido_central') or 0.0) > 0:
            status = 'cobertura parcial com fonte preservada por reserva'
        elif melhor_diag.get('violacao_protegida'):
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
            f"pen_escassez_protegida={melhor_diag.get('penalidade_escassez_protegida_futura'):.4f}, "
            f"pen_escassez_bruta={melhor_diag.get('penalidade_escassez_protegida_futura_bruta'):.4f}, cap_escassez={melhor_diag.get('cap_penalidade_escassez_protegida_futura'):.4f}, "
            f"demanda7d={melhor_diag.get('demanda_protegida_futura_7d'):.2f}, demanda14d={melhor_diag.get('demanda_protegida_futura_14d'):.2f}, pen_deficit_atual={melhor_diag.get('penalidade_deficit_atual'):.6f}, "
            f"pen_estrat={melhor_diag.get('penalidade_estrategica_central'):.4f}, pen_frag={melhor_diag.get('penalidade_fragmentacao_central'):.4f}."
        )
        if fallback_sem_fonte_viavel:
            observacao += ' fallback auditável acionado: sem fonte viável com liquidez positiva no evento.'
        elif fonte_preservada_por_reserva:
            observacao += f" reserva auditável acionada: fonte de maior liquidez preservada ({_rotulo_fonte(fonte_referencia_reserva)})."

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
            'criterio_central': 'metrica_canonica_minima_central_v109',
            'status_central': status,
            'score_proxy_central': melhor_diag.get('score_proxy_central'),
            'violacao_protegida': melhor_diag.get('violacao_protegida'),
            'severidade_protegida': melhor_diag.get('severidade_protegida'),
            'deficit_liquido_total': melhor_diag.get('deficit_liquido_total'),
            'pagamento_sem_cobertura_integral': melhor_diag.get('pagamento_sem_cobertura_integral'),
            'patrimonio_terminal_proxy': melhor_diag.get('patrimonio_terminal_proxy'),
            'penalidade_estrategica_central': melhor_diag.get('penalidade_estrategica_central'),
            'penalidade_fragmentacao_central': melhor_diag.get('penalidade_fragmentacao_central'),
            'penalidade_escassez_protegida_futura': melhor_diag.get('penalidade_escassez_protegida_futura'),
            'demanda_protegida_futura_ponderada': melhor_diag.get('demanda_protegida_futura_ponderada'),
            'demanda_protegida_futura_7d': melhor_diag.get('demanda_protegida_futura_7d'),
            'demanda_protegida_futura_14d': melhor_diag.get('demanda_protegida_futura_14d'),
            'demanda_protegida_futura_21d': melhor_diag.get('demanda_protegida_futura_21d'),
            'fonte_critica_para_protegida_futura': bool(melhor_diag.get('fonte_critica_para_protegida_futura')),
            'penalidade_escassez_protegida_futura_bruta': melhor_diag.get('penalidade_escassez_protegida_futura_bruta'),
            'cap_penalidade_escassez_protegida_futura': melhor_diag.get('cap_penalidade_escassez_protegida_futura'),
            'penalidade_deficit_atual': melhor_diag.get('penalidade_deficit_atual'),
            'fonte_preservada_por_reserva': fonte_preservada_por_reserva,
            'fonte_preservada_referencia': '' if not fonte_preservada_por_reserva else _rotulo_fonte(fonte_referencia_reserva),
            'fallback_sem_fonte_viavel': fallback_sem_fonte_viavel,
            'motivo_indisponibilidade_central': motivo_indisponibilidade,
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
        'fontes_preservadas_por_reserva': int(quadro['fonte_preservada_por_reserva'].sum()) if len(quadro) else 0,
        'primeira_sem_cobertura_data': primeira_sem.get('Data') if primeira_sem else None,
        'primeira_sem_cobertura_pagamento': primeira_sem.get('Descrição') if primeira_sem else None,
        'primeira_violation_protegida_data': primeira_protegida.get('Data') if primeira_protegida else None,
        'primeira_violation_protegida_pagamento': primeira_protegida.get('Descrição') if primeira_protegida else None,
        'primeiro_fallback_sem_fonte_viavel_data': primeiro_sem_fonte_viavel.get('Data') if primeiro_sem_fonte_viavel else None,
        'primeiro_fallback_sem_fonte_viavel_pagamento': primeiro_sem_fonte_viavel.get('Descrição') if primeiro_sem_fonte_viavel else None,
        'primeira_fonte_preservada_por_reserva_data': primeira_fonte_preservada_por_reserva.get('Data') if primeira_fonte_preservada_por_reserva else None,
        'primeira_fonte_preservada_por_reserva_pagamento': primeira_fonte_preservada_por_reserva.get('Descrição') if primeira_fonte_preservada_por_reserva else None,
        'primeira_fonte_preservada_por_reserva_fonte': primeira_fonte_preservada_por_reserva.get('Fonte preservada') if primeira_fonte_preservada_por_reserva else None,
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
            'Reserva': 'sim' if bool(row.get('fonte_preservada_por_reserva')) else '',
            'Motivo': row.get('motivo_indisponibilidade_central') or '',
        })
    auditoria = {
        'validacao': {'ok': True, 'erros': [], 'avisos': []},
        'resumo': resumo,
        'amostra_mudancas': amostra_mudancas,
        'amostra_sem_cobertura': amostra_sem_cobertura,
    }
    return PacoteRecomputacaoSequencialCentralV1(quadro_recomputacao_sequencial_central=quadro, auditoria=auditoria)
