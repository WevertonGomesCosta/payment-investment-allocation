from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import pandas as pd

from nucleo.auditoria_runner_futuro_shadow import PacoteAuditoriaRunnerFuturoShadow
from nucleo.benchmark_runner_futuro_shadow import (
    PacoteBenchmarkRunnerFuturoShadow,
    _lotes_ativos_para_runner,
    _lotes_disponiveis_no_dia,
    _ordenar_lotes_para_pagamento,
    _pagamentos_futuros,
)
from nucleo.cache_cdi_bcb import PacoteCacheCDIDiario
from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.nucleo_financeiro_minimo import Lote, atualizar_saldo_lotes_no_dia, executar_saque_lote
from nucleo.replay_passado_controlado import PacoteReplayPassadoControlado
from nucleo.utilitarios_neutros import limpar_texto, normalizar_identificador


@dataclass(slots=True)
class PacoteAuditoriaPrimeiraQuebraRunnerFuturoShadow:
    quadro_pagamentos_primeira_quebra: pd.DataFrame
    quadro_lotes_primeira_quebra: pd.DataFrame
    quadro_consumo_lote_critico: pd.DataFrame
    quadro_trajetoria_liquidez: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


COLUNAS_PAGAMENTOS = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_vigente', 'lote_principal_shadow', 'qtd_lotes_usados_shadow', 'lotes_usados_shadow',
    'valor_liquido_total_usado', 'valor_descoberto', 'pagamento_totalmente_coberto_vigente',
    'pagamento_totalmente_coberto_shadow', 'delta_excesso_shadow_vs_vigente', 'criterio_vigente',
    'criterio_shadow', 'ordem_lotes_shadow', 'lotes_disponiveis_shadow', 'observacao_auditavel',
]

COLUNAS_LOTES = [
    'data_referencia', 'lote_id', 'saldo_bruto', 'saldo_liquido_estimado',
    'disponivel_para_pagamento', 'motivo_indisponibilidade', 'carencia_ate', 'produto_key',
]

COLUNAS_CONSUMO = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'lote_critico', 'usou_lote_critico', 'lote_principal_shadow', 'qtd_lotes_usados_shadow',
    'valor_liquido_total_usado', 'pagamento_totalmente_coberto', 'lotes_usados_shadow',
]

COLUNAS_TRAJETORIA = [
    'data_pagamento', 'qtd_pagamentos_dia', 'valor_total_pagamentos_dia',
    'liquidez_disponivel_pre_dia', 'liquidez_bloqueada_pre_dia', 'liquidez_total_pre_dia',
    'lotes_disponiveis_pre_dia', 'lotes_bloqueados_pre_dia', 'houve_quebra_no_dia',
]


def _motivo_indisponibilidade(lote: Lote, data_cur: date) -> str:
    if lote.esgotado or float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.01:
        return 'esgotado'
    if lote.data_aplicacao > data_cur:
        return 'aplicacao_futura'
    if lote.carencia_ate and data_cur < lote.carencia_ate:
        return 'carencia'
    return 'disponivel'


def _snapshot_lotes(lotes: list[Lote], data_cur: date, *, tabela_iof: list[float], faixas_ir: list[dict[str, Any]]) -> pd.DataFrame:
    registros: list[dict[str, Any]] = []
    for lote in lotes:
        saldo_bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
        saldo_liq = round(float(lote.valor_liquido_hoje(data_cur, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        motivo = _motivo_indisponibilidade(lote, data_cur)
        registros.append({
            'data_referencia': data_cur,
            'lote_id': lote.id,
            'saldo_bruto': saldo_bruto,
            'saldo_liquido_estimado': saldo_liq,
            'disponivel_para_pagamento': motivo == 'disponivel',
            'motivo_indisponibilidade': motivo,
            'carencia_ate': lote.carencia_ate,
            'produto_key': getattr(lote, 'produto_key', None) or getattr(lote, 'investimento', None),
        })
    out = pd.DataFrame(registros)
    if len(out) == 0:
        return pd.DataFrame(columns=COLUNAS_LOTES)
    for col in COLUNAS_LOTES:
        if col not in out.columns:
            out[col] = None
    return out[COLUNAS_LOTES].sort_values(['disponivel_para_pagamento', 'saldo_liquido_estimado', 'lote_id'], ascending=[False, False, True], kind='stable').reset_index(drop=True)


def _simular_ate_primeira_quebra(
    pagamentos: pd.DataFrame,
    lotes: list[Lote],
    *,
    data_referencia: date,
    primeira_quebra: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pagamentos = pagamentos.loc[pagamentos['data'] <= primeira_quebra].copy()
    pagamentos_por_data: dict[date, list[dict[str, Any]]] = {}
    for rec in pagamentos.to_dict(orient='records'):
        pagamentos_por_data.setdefault(rec['data'], []).append(rec)

    registros_pag: list[dict[str, Any]] = []
    registros_traj: list[dict[str, Any]] = []
    snapshot_primeira_quebra = pd.DataFrame(columns=COLUNAS_LOTES)
    data_cur = data_referencia
    while data_cur <= primeira_quebra:
        atualizar_saldo_lotes_no_dia(
            lotes,
            data_cur,
            calendario_financeiro,
            serie_cdi=cache_cdi.serie_cdi,
            taxa_proj=float(calendario_financeiro.taxa_dia_base),
            data_fechamento_referencia=data_cur,
        )
        snapshot_pre = _snapshot_lotes(lotes, data_cur, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
        if data_cur == primeira_quebra:
            snapshot_primeira_quebra = snapshot_pre.copy()
        disponiveis_df = snapshot_pre.loc[snapshot_pre['disponivel_para_pagamento'].fillna(False)].copy()
        bloqueados_df = snapshot_pre.loc[~snapshot_pre['disponivel_para_pagamento'].fillna(False)].copy()
        registros_traj.append({
            'data_pagamento': data_cur,
            'qtd_pagamentos_dia': int(len(pagamentos_por_data.get(data_cur, []))),
            'valor_total_pagamentos_dia': round(sum(float(p.get('valor') or 0.0) for p in pagamentos_por_data.get(data_cur, [])), 2),
            'liquidez_disponivel_pre_dia': round(float(disponiveis_df['saldo_liquido_estimado'].sum()), 2) if len(disponiveis_df) else 0.0,
            'liquidez_bloqueada_pre_dia': round(float(bloqueados_df['saldo_liquido_estimado'].sum()), 2) if len(bloqueados_df) else 0.0,
            'liquidez_total_pre_dia': round(float(snapshot_pre['saldo_liquido_estimado'].sum()), 2) if len(snapshot_pre) else 0.0,
            'lotes_disponiveis_pre_dia': ' | '.join(disponiveis_df['lote_id'].astype(str).tolist()),
            'lotes_bloqueados_pre_dia': ' | '.join((bloqueados_df['lote_id'].astype(str) + ':' + bloqueados_df['motivo_indisponibilidade'].astype(str)).tolist()),
            'houve_quebra_no_dia': False,
        })
        for pagamento in pagamentos_por_data.get(data_cur, []):
            valor_pag = round(float(pagamento.get('valor') or 0.0), 2)
            falta = valor_pag
            disponiveis = _lotes_disponiveis_no_dia(lotes, data_cur)
            ids_preferidos = [limpar_texto(pagamento.get('lote_usado_1')), limpar_texto(pagamento.get('lote_usado_2'))]
            ordenados = _ordenar_lotes_para_pagamento(
                disponiveis,
                data_cur=data_cur,
                data_fim=primeira_quebra,
                calendario_financeiro=calendario_financeiro,
                cache_cdi=cache_cdi,
                ids_preferidos=ids_preferidos,
            )
            movimentos: list[dict[str, Any]] = []
            for lote in ordenados:
                if falta <= 0.001:
                    break
                mov = executar_saque_lote(lote, falta, data_cur, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
                if mov is None or float(mov.get('liquido') or 0.0) <= 0.0:
                    continue
                movimentos.append(mov)
                falta = round(max(falta - float(mov['liquido']), 0.0), 6)
            valor_liq_total = round(sum(float(m['liquido']) for m in movimentos), 2)
            lotes_usados = [normalizar_identificador(m['lote'].id) for m in movimentos if normalizar_identificador(m['lote'].id)]
            registros_pag.append({
                'pagamento_id': limpar_texto(pagamento.get('despesa_id')),
                'data_pagamento': data_cur,
                'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
                'valor_pagamento': valor_pag,
                'valor_liquido_total_usado_shadow_replay': valor_liq_total,
                'valor_descoberto_shadow_replay': round(max(valor_pag - valor_liq_total, 0.0), 2),
                'pagamento_totalmente_coberto_shadow_replay': bool(falta <= 0.01),
                'qtd_lotes_usados_shadow_replay': int(len(movimentos)),
                'lote_principal_shadow_replay': lotes_usados[0] if lotes_usados else None,
                'lotes_usados_shadow_replay': ' | '.join(lotes_usados),
                'ordem_lotes_shadow_replay': ' | '.join(normalizar_identificador(l.id) for l in ordenados if normalizar_identificador(l.id)),
                'lotes_disponiveis_shadow_replay': ' | '.join(disponiveis_df['lote_id'].astype(str).tolist()),
            })
            if falta > 0.01:
                registros_traj[-1]['houve_quebra_no_dia'] = True
        data_cur += timedelta(days=1)
    return pd.DataFrame(registros_pag), pd.DataFrame(registros_traj), snapshot_primeira_quebra


def _selecionar_lote_critico(quadro_primeira_quebra: pd.DataFrame) -> str | None:
    if len(quadro_primeira_quebra) == 0:
        return None
    base = quadro_primeira_quebra.copy()
    base['lote_vigente'] = base['lote_vigente'].fillna('').astype(str)
    base['valor_pagamento'] = base['valor_pagamento'].fillna(0.0).astype(float)
    base = base.loc[base['lote_vigente'].str.strip() != '']
    if len(base) == 0:
        return None
    base = base.sort_values(['valor_pagamento'], ascending=False, kind='stable')
    return str(base.iloc[0]['lote_vigente']).strip() or None


def carregar_auditoria_primeira_quebra_runner_futuro_shadow(
    benchmark_runner_futuro_shadow: PacoteBenchmarkRunnerFuturoShadow,
    auditoria_runner_futuro_shadow: PacoteAuditoriaRunnerFuturoShadow | None,
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    replay_passado: PacoteReplayPassadoControlado | None,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> PacoteAuditoriaPrimeiraQuebraRunnerFuturoShadow:
    resumo_critico = (auditoria_runner_futuro_shadow.auditoria.get('resumo', {}) if auditoria_runner_futuro_shadow is not None else {})
    data_quebra_iso = resumo_critico.get('primeira_data_sem_cobertura')
    if not data_quebra_iso:
        vazio = pd.DataFrame()
        auditoria = {'resumo': {'tem_primeira_quebra': False, 'recomendacao': 'sem_quebra_no_benchmark_runner_shadow'}}
        return PacoteAuditoriaPrimeiraQuebraRunnerFuturoShadow(vazio, vazio, vazio, vazio, auditoria, {'ok': True, 'erros': [], 'avisos': ['sem_primeira_quebra_no_runner_shadow']})
    primeira_quebra = date.fromisoformat(str(data_quebra_iso))
    pagamentos = _pagamentos_futuros(dados_operacionais, data_referencia=data_referencia)
    lotes = _lotes_ativos_para_runner(replay_passado)
    quadro_replay, quadro_traj, snapshot_primeira_quebra = _simular_ate_primeira_quebra(
        pagamentos,
        lotes,
        data_referencia=data_referencia,
        primeira_quebra=primeira_quebra,
        calendario_financeiro=calendario_financeiro,
        cache_cdi=cache_cdi,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
    )
    shadow_comp = benchmark_runner_futuro_shadow.quadro_comparativo_vigente.copy()
    shadow_raw = benchmark_runner_futuro_shadow.quadro_pagamentos_shadow.copy()
    shadow_join = shadow_comp.merge(
        shadow_raw[['pagamento_id','valor_liquido_total_usado','valor_excesso_liquido','lotes_usados_shadow','valor_lote_principal_shadow','imposto_pago_shadow','criterio_shadow','observacao_auditavel']],
        on='pagamento_id', how='left', suffixes=('', '_raw')
    )
    if 'criterio_shadow_raw' in shadow_join.columns:
        shadow_join['criterio_shadow'] = shadow_join['criterio_shadow'].where(shadow_join['criterio_shadow'].notna(), shadow_join['criterio_shadow_raw'])
        shadow_join = shadow_join.drop(columns=['criterio_shadow_raw'])
    if 'observacao_auditavel_raw' in shadow_join.columns:
        shadow_join['observacao_auditavel'] = shadow_join['observacao_auditavel'].where(shadow_join['observacao_auditavel'].notna(), shadow_join['observacao_auditavel_raw'])
        shadow_join = shadow_join.drop(columns=['observacao_auditavel_raw'])
    primeira_data_df = shadow_join.loc[shadow_join['data_pagamento'] == primeira_quebra].copy()
    primeira_data_df = primeira_data_df.merge(
        quadro_replay[['pagamento_id','ordem_lotes_shadow_replay','lotes_disponiveis_shadow_replay','valor_liquido_total_usado_shadow_replay','valor_descoberto_shadow_replay','pagamento_totalmente_coberto_shadow_replay','qtd_lotes_usados_shadow_replay','lote_principal_shadow_replay','lotes_usados_shadow_replay']],
        on='pagamento_id', how='left'
    )
    primeira_data_df['ordem_lotes_shadow'] = primeira_data_df['ordem_lotes_shadow_replay'].where(primeira_data_df['ordem_lotes_shadow_replay'].notna(), primeira_data_df.get('ordem_lotes_shadow'))
    primeira_data_df['lotes_disponiveis_shadow'] = primeira_data_df['lotes_disponiveis_shadow_replay'].where(primeira_data_df['lotes_disponiveis_shadow_replay'].notna(), primeira_data_df.get('lotes_disponiveis_shadow'))
    primeira_data_df['valor_descoberto'] = (primeira_data_df['valor_pagamento'].fillna(0.0) - primeira_data_df['valor_liquido_total_usado'].fillna(0.0)).clip(lower=0.0).round(2)
    for col in COLUNAS_PAGAMENTOS:
        if col not in primeira_data_df.columns:
            primeira_data_df[col] = None
    quadro_pagamentos = primeira_data_df[COLUNAS_PAGAMENTOS].sort_values(['data_pagamento','pagamento_id'], kind='stable').reset_index(drop=True)

    snapshot_quebra = snapshot_primeira_quebra.copy()
    for col in COLUNAS_LOTES:
        if col not in snapshot_quebra.columns:
            snapshot_quebra[col] = None
    quadro_lotes = snapshot_quebra[COLUNAS_LOTES].copy()

    lote_critico = _selecionar_lote_critico(quadro_pagamentos)
    consumo = shadow_raw.loc[shadow_raw['data_pagamento'] < primeira_quebra].copy()
    if lote_critico:
        consumo['usou_lote_critico'] = consumo['lotes_usados_shadow'].fillna('').astype(str).str.contains(lote_critico, regex=False)
        consumo = consumo.loc[consumo['usou_lote_critico']].copy()
        consumo['lote_critico'] = lote_critico
    else:
        consumo = consumo.iloc[0:0].copy()
        consumo['lote_critico'] = None
        consumo['usou_lote_critico'] = False
    for col in COLUNAS_CONSUMO:
        if col not in consumo.columns:
            consumo[col] = None
    quadro_consumo = consumo[COLUNAS_CONSUMO].sort_values(['data_pagamento','pagamento_id'], kind='stable').reset_index(drop=True)

    traj = quadro_traj.loc[(quadro_traj['qtd_pagamentos_dia'] > 0) | (quadro_traj['data_pagamento'] == primeira_quebra)].copy()
    if len(traj):
        janela_inicio = max(data_referencia, primeira_quebra - timedelta(days=35))
        traj = traj.loc[traj['data_pagamento'] >= janela_inicio].copy()
    for col in COLUNAS_TRAJETORIA:
        if col not in traj.columns:
            traj[col] = None
    quadro_traj = traj[COLUNAS_TRAJETORIA].sort_values('data_pagamento', kind='stable').reset_index(drop=True)

    liq_disp_quebra = float(quadro_lotes.loc[quadro_lotes['disponivel_para_pagamento'].fillna(False), 'saldo_liquido_estimado'].sum()) if len(quadro_lotes) else 0.0
    liq_bloq_quebra = float(quadro_lotes.loc[~quadro_lotes['disponivel_para_pagamento'].fillna(False), 'saldo_liquido_estimado'].sum()) if len(quadro_lotes) else 0.0
    primeiro_pag = None
    if len(quadro_pagamentos):
        primeira_ordem = quadro_pagamentos.sort_values(['data_pagamento','pagamento_id'], kind='stable')
        primeira_descoberta = primeira_ordem.loc[~primeira_ordem['pagamento_totalmente_coberto_shadow'].fillna(False)]
        alvo = primeira_descoberta if len(primeira_descoberta) else primeira_ordem
        primeiro_pag = alvo.iloc[0]
    auditoria = {
        'resumo': {
            'data_referencia': data_referencia.isoformat(),
            'primeira_data_quebra': primeira_quebra.isoformat(),
            'pagamentos_na_primeira_quebra': int(len(quadro_pagamentos)),
            'lote_critico_identificado': lote_critico,
            'eventos_previos_com_consumo_lote_critico': int(len(quadro_consumo)),
            'liquidez_disponivel_na_primeira_quebra': round(liq_disp_quebra, 2),
            'liquidez_bloqueada_na_primeira_quebra': round(liq_bloq_quebra, 2),
            'primeiro_pagamento_critico': str(primeiro_pag['descricao_pagamento']) if primeiro_pag is not None else None,
            'valor_primeiro_pagamento_critico': round(float(primeiro_pag['valor_pagamento']), 2) if primeiro_pag is not None else 0.0,
            'valor_descoberto_no_primeiro_dia': round(float(quadro_pagamentos['valor_descoberto'].sum()), 2) if len(quadro_pagamentos) else 0.0,
            'causa_raiz_resumida': 'quebra causada por exaustao previa do lote critico e presenca de liquidez bloqueada por carencia no primeiro dia de insuficiencia.',
            'recomendacao_auditoria': 'nao_absorver_runner_shadow; usar a primeira quebra apenas como evidencia causal da agressividade estrutural da simulacao futura legada.',
        }
    }
    validacao = {'ok': True, 'erros': [], 'avisos': []}
    if len(quadro_pagamentos) == 0:
        validacao['ok'] = False
        validacao['erros'].append('primeira_quebra_sem_pagamentos_mapeados')
    if lote_critico is None:
        validacao['avisos'].append('lote_critico_nao_identificado')
    return PacoteAuditoriaPrimeiraQuebraRunnerFuturoShadow(
        quadro_pagamentos_primeira_quebra=quadro_pagamentos,
        quadro_lotes_primeira_quebra=quadro_lotes,
        quadro_consumo_lote_critico=quadro_consumo,
        quadro_trajetoria_liquidez=quadro_traj,
        auditoria=auditoria,
        validacao=validacao,
    )
