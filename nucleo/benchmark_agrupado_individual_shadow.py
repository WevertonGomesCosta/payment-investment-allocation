
from __future__ import annotations

"""Benchmark shadow do teste agrupado vs individual do Script 1 legado.

Esta camada reproduz, em modo shadow e auditável, a governança legada que
comparava processamento agrupado por dia versus individual. A absorção nesta
etapa NÃO migra o runner original nem altera a decisão vigente do fluxo
principal; apenas recalcula a decisão local v1 (proxy v3) em duas superfícies:

- individual: pagamentos futuros/pedentes um a um;
- agrupado: soma dos pagamentos por data.

O objetivo é medir se a agregação por dia altera de forma material a escolha do
lote principal, o excesso e o custo proxy ponderado, oferecendo uma régua de
benchmark da orquestração legada sem reabrir o motor principal.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

import pandas as pd

from nucleo.caixa_recebidos_auditaveis import (
    PacoteDecisaoLocalV1,
    PacoteFontesElegiveisPagamento,
    PacoteSaldoDisponivelGeral,
    _construir_candidatos_decisao_local_v1,
    _construir_mapa_produtos_proxy,
    _pagamentos_alvo_f1_4,
    _selecionar_candidato_decisao_local_v1,
)
from nucleo.config_utils import obter_config
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import limpar_texto, normalizar_identificador


@dataclass(slots=True)
class PacoteBenchmarkAgrupadoIndividualShadow:
    quadro_pagamentos_individual: pd.DataFrame
    quadro_pagamentos_agrupados: pd.DataFrame
    quadro_comparativo_datas: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def _pagamentos_individuais(dados_operacionais: PacoteDadosOperacionaisCanonicos, *, data_referencia: date) -> pd.DataFrame:
    return _pagamentos_alvo_f1_4(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)


def _agrupar_pagamentos_por_data(pagamentos: pd.DataFrame) -> pd.DataFrame:
    if len(pagamentos) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'descricao', 'valor', 'qtd_pagamentos_dia'])
    agrupado = (
        pagamentos.groupby('data', as_index=False)
        .agg(
            valor=('valor', 'sum'),
            qtd_pagamentos_dia=('despesa_id', 'count'),
            descricoes=('descricao', lambda s: '; '.join([limpar_texto(v) for v in s.tolist() if limpar_texto(v)][:5])),
        )
        .sort_values('data', kind='stable')
        .reset_index(drop=True)
    )
    agrupado['despesa_id'] = agrupado['data'].map(lambda d: f"agrupado::{d.isoformat()}")
    agrupado['descricao'] = agrupado.apply(
        lambda r: f"AGRUPADO {r['data'].isoformat()} ({int(r['qtd_pagamentos_dia'])} pagamentos)"
        + (f" | {r['descricoes']}" if limpar_texto(r.get('descricoes')) else ''),
        axis=1,
    )
    agrupado['valor'] = agrupado['valor'].map(lambda x: round(float(x or 0.0), 2))
    return agrupado[['despesa_id', 'data', 'descricao', 'valor', 'qtd_pagamentos_dia']].copy()


def _agrupar_saldo_por_data(quadro_saldo: pd.DataFrame, pagamentos_agrupados: pd.DataFrame) -> pd.DataFrame:
    if len(pagamentos_agrupados) == 0:
        return pd.DataFrame(columns=[
            'saldo_disponivel_id', 'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
            'saldo_disponivel_bruto', 'saldo_disponivel_liquido', 'saldo_disponivel_elegivel', 'origem_status',
            'origem_saldo', 'qtd_fontes_componentes', 'tipos_fontes_componentes', 'regra_precedencia_intradiaria',
            'restricao_duplicidade_recebidos', 'data_base_saldo', 'metodo_saldo', 'observacao_auditavel',
        ])
    if len(quadro_saldo) == 0:
        return pd.DataFrame()
    mapa_pag = {row['data']: row for row in pagamentos_agrupados.to_dict(orient='records')}
    registros: list[dict[str, Any]] = []
    for data_pag, grupo in quadro_saldo.groupby('data_pagamento', sort=True):
        if data_pag not in mapa_pag:
            continue
        pag = mapa_pag[data_pag]
        bruto = round(float(grupo['saldo_disponivel_bruto'].fillna(0.0).sum()), 2)
        liquido = round(float(grupo['saldo_disponivel_liquido'].fillna(0.0).sum()), 2)
        elegivel = bool(grupo['saldo_disponivel_elegivel'].fillna(False).any())
        origem_status = 'confirmado' if elegivel else 'ausente'
        origem_saldo = '; '.join(sorted({limpar_texto(v) for v in grupo['origem_saldo'].tolist() if limpar_texto(v)}))
        metodo = '; '.join(sorted({limpar_texto(v) for v in grupo['metodo_saldo'].tolist() if limpar_texto(v)}))
        observacao = ' | '.join([limpar_texto(v) for v in grupo['observacao_auditavel'].tolist() if limpar_texto(v)][:5])
        registros.append({
            'saldo_disponivel_id': f"saldo_disponivel::{pag['despesa_id']}",
            'pagamento_id': pag['despesa_id'],
            'data_pagamento': data_pag,
            'descricao_pagamento': pag['descricao'],
            'valor_pagamento': round(float(pag['valor'] or 0.0), 2),
            'saldo_disponivel_bruto': bruto,
            'saldo_disponivel_liquido': liquido,
            'saldo_disponivel_elegivel': bool(elegivel and liquido > 0.0),
            'origem_status': origem_status,
            'origem_saldo': origem_saldo or 'sem_caixa_geral_observavel_na_base',
            'qtd_fontes_componentes': int(grupo['qtd_fontes_componentes'].fillna(0).sum()) if 'qtd_fontes_componentes' in grupo.columns else 0,
            'tipos_fontes_componentes': '; '.join(sorted({limpar_texto(v) for v in grupo['tipos_fontes_componentes'].tolist() if limpar_texto(v)})),
            'regra_precedencia_intradiaria': '; '.join(sorted({limpar_texto(v) for v in grupo['regra_precedencia_intradiaria'].tolist() if limpar_texto(v)})),
            'restricao_duplicidade_recebidos': bool(grupo['restricao_duplicidade_recebidos'].fillna(False).any()) if 'restricao_duplicidade_recebidos' in grupo.columns else False,
            'data_base_saldo': grupo['data_base_saldo'].dropna().iloc[0] if 'data_base_saldo' in grupo.columns and grupo['data_base_saldo'].notna().any() else data_pag,
            'metodo_saldo': metodo or 'agregado_por_data_shadow',
            'observacao_auditavel': observacao or 'saldo disponível geral agregado por data apenas para benchmark shadow agrupado vs individual.',
        })
    return pd.DataFrame(registros)


def _agrupar_fontes_por_data(quadro_fontes: pd.DataFrame, pagamentos_agrupados: pd.DataFrame) -> pd.DataFrame:
    if len(pagamentos_agrupados) == 0:
        return pd.DataFrame(columns=list(quadro_fontes.columns))
    if len(quadro_fontes) == 0:
        return pd.DataFrame(columns=list(quadro_fontes.columns))
    mapa_pag = {row['data']: row for row in pagamentos_agrupados.to_dict(orient='records')}
    registros: list[dict[str, Any]] = []
    for (data_pag, fonte_id), grupo in quadro_fontes.groupby(['data_pagamento', 'fonte_id'], sort=True):
        if data_pag not in mapa_pag:
            continue
        pag = mapa_pag[data_pag]
        produto_nome = grupo['produto_nome_canonico'].dropna().astype(str)
        recebido_id = grupo['recebido_id'].dropna().astype(str)
        lote_id = grupo['lote_id'].dropna().astype(str)
        motivos = [limpar_texto(v) for v in grupo['motivo_bloqueio_temporal'].tolist() if limpar_texto(v)] if 'motivo_bloqueio_temporal' in grupo.columns else []
        observacoes = [limpar_texto(v) for v in grupo['observacao_auditavel'].tolist() if limpar_texto(v)]
        origem_statuses = [limpar_texto(v) for v in grupo['origem_status'].tolist() if limpar_texto(v)]
        if any(v == 'confirmado' for v in origem_statuses):
            origem_status = 'confirmado'
        elif any(v == 'parcial' for v in origem_statuses):
            origem_status = 'parcial'
        elif any(v == 'estimado' for v in origem_statuses):
            origem_status = 'estimado'
        elif any(v == 'bloqueado' for v in origem_statuses):
            origem_status = 'bloqueado'
        else:
            origem_status = origem_statuses[0] if origem_statuses else ''
        registros.append({
            'fonte_pagamento_id': f"{limpar_texto(fonte_id)}::agrupado::{data_pag.isoformat()}",
            'fonte_id': limpar_texto(fonte_id),
            'pagamento_id': pag['despesa_id'],
            'data_pagamento': data_pag,
            'descricao_pagamento': pag['descricao'],
            'valor_pagamento': round(float(pag['valor'] or 0.0), 2),
            'tipo_fonte': grupo['tipo_fonte'].astype(str).iloc[0],
            'data_evento': grupo['data_evento'].iloc[0],
            'lote_id': lote_id.iloc[0] if len(lote_id) else None,
            'recebido_id': recebido_id.iloc[0] if len(recebido_id) else None,
            'produto_key': grupo['produto_key'].astype(str).iloc[0] if 'produto_key' in grupo.columns and pd.notna(grupo['produto_key'].iloc[0]) else None,
            'produto_nome_canonico': produto_nome.iloc[0] if len(produto_nome) else None,
            'valor_bruto_disponivel': round(float(grupo['valor_bruto_disponivel'].fillna(0.0).max()), 2),
            'valor_liquido_disponivel': round(float(grupo['valor_liquido_disponivel'].fillna(0.0).max()), 2),
            'elegivel_na_data_pagamento': bool(grupo['elegivel_na_data_pagamento'].fillna(False).all()),
            'origem_status': origem_status,
            'motivo_bloqueio_temporal': '; '.join(sorted(set(motivos))) or None,
            'data_base_valor': grupo['data_base_valor'].dropna().iloc[0] if grupo['data_base_valor'].notna().any() else data_pag,
            'metodo_valor_disponivel': '; '.join(sorted({limpar_texto(v) for v in grupo['metodo_valor_disponivel'].tolist() if limpar_texto(v)})) or 'agregado_por_data_shadow',
            'observacao_auditavel': ' | '.join(observacoes[:5]) if observacoes else 'fonte agregada por data apenas para benchmark shadow agrupado vs individual.',
            'data_recebimento_origem': grupo['data_recebimento_origem'].dropna().iloc[0] if 'data_recebimento_origem' in grupo.columns and grupo['data_recebimento_origem'].notna().any() else None,
            'data_aplicacao_origem': grupo['data_aplicacao_origem'].dropna().iloc[0] if 'data_aplicacao_origem' in grupo.columns and grupo['data_aplicacao_origem'].notna().any() else None,
            'carencia_ate_origem': grupo['carencia_ate_origem'].dropna().iloc[0] if 'carencia_ate_origem' in grupo.columns and grupo['carencia_ate_origem'].notna().any() else None,
            'origem_estrutura': 'benchmark_shadow_agrupado_por_data',
        })
    return pd.DataFrame(registros)


def _resolver_decisoes_shadow(
    pagamentos: pd.DataFrame,
    quadro_saldo: pd.DataFrame,
    quadro_fontes: pd.DataFrame,
    mapa_produtos_proxy: dict[str, dict[str, Any]],
    *,
    proxy_version: str,
) -> pd.DataFrame:
    registros: list[dict[str, Any]] = []
    for pagamento in pagamentos.to_dict(orient='records'):
        candidatos = _construir_candidatos_decisao_local_v1(pagamento, quadro_saldo, quadro_fontes, mapa_produtos_proxy)
        escolhido, criterio, observacao = _selecionar_candidato_decisao_local_v1(
            candidatos,
            valor_pagamento=round(float(pagamento.get('valor') or 0.0), 2),
            proxy_version=proxy_version,
        )
        registros.append({
            'pagamento_id': limpar_texto(pagamento.get('despesa_id')),
            'data_pagamento': pagamento.get('data'),
            'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
            'valor_pagamento': round(float(pagamento.get('valor') or 0.0), 2),
            'qtd_pagamentos_dia': int(pagamento.get('qtd_pagamentos_dia') or 1),
            'fonte_escolhida_id': limpar_texto(escolhido.get('fonte_escolhida_id')),
            'fonte_base_escolhida': limpar_texto(escolhido.get('fonte_base_escolhida')),
            'lote_id_escolhido': normalizar_identificador(escolhido.get('lote_id')) or None,
            'tipo_fonte_escolhida': limpar_texto(escolhido.get('tipo_fonte_escolhida')),
            'criterio_decisao': criterio,
            'custo_economico_proxy': round(float(escolhido.get('custo_economico_proxy') or 0.0), 4) if escolhido.get('custo_economico_proxy') is not None else None,
            'valor_disponivel_escolhido': round(float(escolhido.get('valor_disponivel') or 0.0), 2),
            'pagamento_totalmente_coberto': bool(escolhido.get('pagamento_totalmente_coberto', False)),
            'fonte_origem_status': limpar_texto(escolhido.get('origem_status')),
            'data_base_valor_escolhido': escolhido.get('data_base_valor'),
            'observacao_auditavel': limpar_texto(observacao),
        })
    return pd.DataFrame(registros).sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)


def _dominante_individual_do_dia(quadro_individual: pd.DataFrame, data_pagamento: date) -> tuple[str | None, str | None, int, float]:
    dia = quadro_individual.loc[quadro_individual['data_pagamento'] == data_pagamento].copy()
    if len(dia) == 0:
        return None, None, 0, 0.0
    grp = (
        dia.groupby(['fonte_base_escolhida', 'lote_id_escolhido'], dropna=False, as_index=False)
        .agg(qtd=('pagamento_id', 'count'), valor_total=('valor_pagamento', 'sum'))
        .sort_values(['valor_total', 'qtd'], ascending=[False, False], kind='stable')
        .reset_index(drop=True)
    )
    top = grp.iloc[0]
    return limpar_texto(top['fonte_base_escolhida']) or None, normalizar_identificador(top['lote_id_escolhido']) or None, int(top['qtd']), round(float(top['valor_total'] or 0.0), 2)


def _resumo_modo(quadro: pd.DataFrame) -> dict[str, Any]:
    if len(quadro) == 0:
        return {'total_pagamentos': 0}
    valor_total = float(quadro['valor_pagamento'].sum())
    score_ponderado = 0.0
    if valor_total > 0:
        score_ponderado = float((quadro['custo_economico_proxy'].fillna(0.0) * quadro['valor_pagamento'].fillna(0.0)).sum() / valor_total)
    excesso_total = float((quadro['valor_disponivel_escolhido'].fillna(0.0) - quadro['valor_pagamento'].fillna(0.0)).clip(lower=0.0).sum())
    return {
        'total_pagamentos': int(len(quadro)),
        'valor_total_pagamentos': round(valor_total, 2),
        'pagamentos_totalmente_cobertos': int(quadro['pagamento_totalmente_coberto'].fillna(False).sum()),
        'custo_proxy_ponderado_por_valor': round(score_ponderado, 4),
        'excesso_liquido_total': round(excesso_total, 2),
        'lote_id_escolhido': {str(k): int(v) for k, v in quadro['lote_id_escolhido'].dropna().value_counts(dropna=False).to_dict().items()},
        'fonte_base_escolhida': {str(k): int(v) for k, v in quadro['fonte_base_escolhida'].dropna().value_counts(dropna=False).to_dict().items()},
    }


def _avaliar_modo_recomendado(resumo_individual: Mapping[str, Any], resumo_agrupado: Mapping[str, Any], *, limiar_relativo: float) -> tuple[str, str]:
    cob_ind = int(resumo_individual.get('pagamentos_totalmente_cobertos', 0))
    cob_agr = int(resumo_agrupado.get('pagamentos_totalmente_cobertos', 0))
    if cob_agr > cob_ind:
        return 'agrupado', 'agrupado cobre mais pagamentos integralmente no benchmark shadow.'
    if cob_ind > cob_agr:
        return 'individual', 'individual cobre mais pagamentos integralmente no benchmark shadow.'
    score_ind = float(resumo_individual.get('custo_proxy_ponderado_por_valor', 0.0) or 0.0)
    score_agr = float(resumo_agrupado.get('custo_proxy_ponderado_por_valor', 0.0) or 0.0)
    excesso_ind = float(resumo_individual.get('excesso_liquido_total', 0.0) or 0.0)
    excesso_agr = float(resumo_agrupado.get('excesso_liquido_total', 0.0) or 0.0)
    score_delta_rel = (score_agr - score_ind) / max(abs(score_ind), 1e-9)
    excesso_delta_rel = (excesso_agr - excesso_ind) / max(abs(excesso_ind), 1e-9) if excesso_ind > 0 else 0.0
    if score_delta_rel < -limiar_relativo and excesso_delta_rel <= limiar_relativo:
        return 'agrupado', 'agrupado apresentou custo proxy ponderado materialmente menor sem piorar excesso de forma relevante.'
    if score_delta_rel > limiar_relativo and excesso_delta_rel >= -limiar_relativo:
        return 'individual', 'individual apresentou custo proxy ponderado materialmente menor sem piorar excesso de forma relevante.'
    if excesso_delta_rel < -limiar_relativo and score_delta_rel <= limiar_relativo:
        return 'agrupado', 'agrupado reduziu excesso líquido total materialmente sem piorar custo proxy de forma relevante.'
    if excesso_delta_rel > limiar_relativo and score_delta_rel >= -limiar_relativo:
        return 'individual', 'individual reduziu excesso líquido total materialmente sem piorar custo proxy de forma relevante.'
    return 'inconclusivo', 'benchmark shadow agrupado vs individual não mostrou vantagem material robusta entre os modos.'


def carregar_benchmark_agrupado_individual_shadow(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    saldo_disponivel_geral: PacoteSaldoDisponivelGeral,
    decisao_local_v1: PacoteDecisaoLocalV1,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    carteira_canonica: Any | None = None,
    proxy_version: str = 'v3',
) -> PacoteBenchmarkAgrupadoIndividualShadow:
    pagamentos_individuais = _pagamentos_individuais(dados_operacionais, data_referencia=data_referencia)
    pagamentos_agrupados = _agrupar_pagamentos_por_data(pagamentos_individuais)
    quadro_saldo_agr = _agrupar_saldo_por_data(saldo_disponivel_geral.quadro_saldo_disponivel.copy(), pagamentos_agrupados)
    quadro_fontes_agr = _agrupar_fontes_por_data(fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy(), pagamentos_agrupados)
    mapa_produtos_proxy = _construir_mapa_produtos_proxy(carteira_canonica)
    quadro_individual = decisao_local_v1.quadro_decisao_local_v1.copy()
    quadro_agrupado = _resolver_decisoes_shadow(pagamentos_agrupados, quadro_saldo_agr, quadro_fontes_agr, mapa_produtos_proxy, proxy_version=proxy_version)

    registros_comp: list[dict[str, Any]] = []
    for data_pag, grupo_ind in quadro_individual.groupby('data_pagamento', sort=True):
        reg_agr = quadro_agrupado.loc[quadro_agrupado['data_pagamento'] == data_pag]
        if len(reg_agr) == 0:
            continue
        agr = reg_agr.iloc[0].to_dict()
        fonte_dom, lote_dom, qtd_dom, valor_dom = _dominante_individual_do_dia(quadro_individual, data_pag)
        score_ind_pond = float((grupo_ind['custo_economico_proxy'].fillna(0.0) * grupo_ind['valor_pagamento'].fillna(0.0)).sum() / max(float(grupo_ind['valor_pagamento'].sum()), 1e-9))
        excesso_ind = float((grupo_ind['valor_disponivel_escolhido'].fillna(0.0) - grupo_ind['valor_pagamento'].fillna(0.0)).clip(lower=0.0).sum())
        registros_comp.append({
            'data_pagamento': data_pag,
            'qtd_pagamentos_individual': int(len(grupo_ind)),
            'valor_total_dia': round(float(grupo_ind['valor_pagamento'].sum()), 2),
            'fonte_base_dominante_individual': fonte_dom,
            'lote_dominante_individual': lote_dom,
            'qtd_pagamentos_fonte_dominante_individual': qtd_dom,
            'valor_fonte_dominante_individual': valor_dom,
            'score_proxy_ponderado_individual': round(score_ind_pond, 4),
            'excesso_liquido_total_individual': round(excesso_ind, 2),
            'fonte_base_agrupado': limpar_texto(agr.get('fonte_base_escolhida')),
            'lote_agrupado': normalizar_identificador(agr.get('lote_id_escolhido')) or None,
            'score_proxy_agrupado': round(float(agr.get('custo_economico_proxy') or 0.0), 4) if agr.get('custo_economico_proxy') is not None else None,
            'excesso_liquido_agrupado': round(max(float(agr.get('valor_disponivel_escolhido') or 0.0) - float(agr.get('valor_pagamento') or 0.0), 0.0), 2),
            'pagamento_totalmente_coberto_agrupado': bool(agr.get('pagamento_totalmente_coberto', False)),
            'mudou_lote_vs_dominante_individual': bool((normalizar_identificador(agr.get('lote_id_escolhido')) or '') != (lote_dom or '')),
            'delta_score_proxy_agrupado_vs_individual_ponderado': round(float((agr.get('custo_economico_proxy') or 0.0) - score_ind_pond), 4) if agr.get('custo_economico_proxy') is not None else None,
            'delta_excesso_liquido_agrupado_vs_individual': round(max(float(agr.get('valor_disponivel_escolhido') or 0.0) - float(agr.get('valor_pagamento') or 0.0), 0.0) - excesso_ind, 2),
        })
    quadro_comp = pd.DataFrame(registros_comp).sort_values('data_pagamento', kind='stable').reset_index(drop=True) if registros_comp else pd.DataFrame(columns=[
        'data_pagamento', 'qtd_pagamentos_individual', 'valor_total_dia', 'fonte_base_dominante_individual',
        'lote_dominante_individual', 'qtd_pagamentos_fonte_dominante_individual', 'valor_fonte_dominante_individual',
        'score_proxy_ponderado_individual', 'excesso_liquido_total_individual', 'fonte_base_agrupado', 'lote_agrupado',
        'score_proxy_agrupado', 'excesso_liquido_agrupado', 'pagamento_totalmente_coberto_agrupado',
        'mudou_lote_vs_dominante_individual', 'delta_score_proxy_agrupado_vs_individual_ponderado',
        'delta_excesso_liquido_agrupado_vs_individual',
    ])

    resumo_individual = _resumo_modo(quadro_individual)
    resumo_agrupado = _resumo_modo(quadro_agrupado)
    limiar_rel = float(obter_config(config, 'benchmark_shadow_script2', 'limiar_diferenca_relativa', padrao=0.05) or 0.05)
    modo_recomendado, justificativa = _avaliar_modo_recomendado(resumo_individual, resumo_agrupado, limiar_relativo=limiar_rel)

    erros: list[str] = []
    avisos: list[str] = []
    if len(quadro_agrupado) != len(pagamentos_agrupados):
        erros.append('benchmark_agrupado_sem_decisao_para_todas_as_datas')
    if (~quadro_individual['pagamento_totalmente_coberto'].fillna(False)).any() or (~quadro_agrupado['pagamento_totalmente_coberto'].fillna(False)).any():
        avisos.append('benchmark_shadow_com_pagamentos_sem_cobertura_integral_em_algum_modo')
    if len(quadro_comp) and quadro_comp['mudou_lote_vs_dominante_individual'].any():
        avisos.append('modo_agrupado_altera_lote_dominante_em_parte_das_datas')

    auditoria = {
        'validacao': {'ok': len(erros) == 0, 'erros': erros, 'avisos': avisos},
        'resumo': {
            'proxy_version': proxy_version,
            'total_pagamentos_individuais': int(len(quadro_individual)),
            'total_datas_agrupadas': int(len(quadro_agrupado)),
            'datas_com_mudanca_de_lote_dominante': int(quadro_comp['mudou_lote_vs_dominante_individual'].sum()) if len(quadro_comp) else 0,
            'modo_recomendado_shadow': modo_recomendado,
            'justificativa_modo_recomendado': justificativa,
            'resumo_individual': resumo_individual,
            'resumo_agrupado': resumo_agrupado,
        },
    }
    return PacoteBenchmarkAgrupadoIndividualShadow(
        quadro_pagamentos_individual=quadro_individual,
        quadro_pagamentos_agrupados=quadro_agrupado,
        quadro_comparativo_datas=quadro_comp,
        auditoria=auditoria,
        validacao=auditoria['validacao'],
    )
