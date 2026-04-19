from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Mapping

import pandas as pd

from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro
from nucleo.cache_cdi_bcb import PacoteCacheCDIDiario
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.helpers_shadow_compartilhados import simular_lote_ate_data_shadow
from nucleo.nucleo_financeiro_minimo import (
    Lote,
    atualizar_saldo_lotes_no_dia,
    criar_lote_de_aporte,
    executar_saque_lote,
)
from nucleo.replay_passado_controlado import PacoteReplayPassadoControlado
from nucleo.caixa_recebidos_auditaveis import PacoteDecisaoLocalV1
from nucleo.utilitarios_neutros import arredondar_monetario, limpar_texto, normalizar_identificador


@dataclass(slots=True)
class PacoteBenchmarkRunnerFuturoShadow:
    quadro_pagamentos_shadow: pd.DataFrame
    quadro_comparativo_vigente: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


COLUNAS_SHADOW = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'valor_liquido_total_usado', 'valor_excesso_liquido', 'pagamento_totalmente_coberto',
    'qtd_lotes_usados', 'lote_principal_shadow', 'lotes_usados_shadow',
    'valor_lote_principal_shadow', 'imposto_pago_shadow', 'criterio_shadow', 'observacao_auditavel',
]


def _clonar_lote(lote: Lote) -> Lote:
    return criar_lote_de_aporte(
        lote.data_aplicacao,
        float(lote.saldo_bruto),
        lote.id,
        {
            'investimento': lote.investimento,
            'produto_key': lote.produto_key,
            'data_base_fiscal': lote.data_base_fiscal,
            'data_recebimento': lote.data_recebimento,
            'fator_acumulado_inicial': lote.fator_acumulado,
            'taxa_base_cdi': lote.taxa_base_cdi,
            'taxa_bonus_cdi': lote.taxa_bonus_cdi,
            'dias_bonus': lote.dias_bonus,
            'principal_remanescente': lote.principal_remanescente,
            'produto_isento_ir': lote.produto_isento_ir,
            'carencia_ate': lote.carencia_ate,
            'nao_disponivel_para_aporte': lote.nao_disponivel_para_aporte,
            'situacao_investimento': lote.situacao_investimento,
        },
    )


def _pagamentos_futuros(dados_operacionais: PacoteDadosOperacionaisCanonicos, *, data_referencia: date) -> pd.DataFrame:
    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(gastos) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'descricao', 'valor'])
    datas = pd.to_datetime(gastos.get('data'), errors='coerce').dt.date
    mask = datas.notna() & (datas >= data_referencia)
    if 'futuro_ou_pendente_na_data_referencia' in gastos.columns:
        mask &= gastos['futuro_ou_pendente_na_data_referencia'].fillna(False)
    cols = [c for c in ['despesa_id', 'data', 'descricao', 'valor', 'lote_usado_1', 'lote_usado_2'] if c in gastos.columns]
    out = gastos.loc[mask, cols].copy()
    if len(out) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'descricao', 'valor', 'lote_usado_1', 'lote_usado_2'])
    out = out.sort_values(['data', 'despesa_id'], kind='stable').reset_index(drop=True)
    out['valor'] = out['valor'].fillna(0.0).astype(float)
    return out


def _lotes_ativos_para_runner(replay_passado: PacoteReplayPassadoControlado | None) -> list[Lote]:
    if replay_passado is None:
        return []
    lotes: list[Lote] = []
    for lote in replay_passado.lotes_apos_replay:
        if lote.esgotado:
            continue
        if float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.01:
            continue
        lotes.append(_clonar_lote(lote))
    return lotes


def _fator_oportunidade_lote(
    lote: Lote,
    *,
    data_cur: date,
    data_fim: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
) -> float:
    try:
        valor_liquido_hoje = float(lote.valor_liquido_hoje(data_cur))
    except Exception:
        valor_liquido_hoje = 0.0
    if valor_liquido_hoje <= 1e-9:
        return 1e18
    try:
        clone = simular_lote_ate_data_shadow(
            lote,
            data_cur,
            data_fim,
            calendario_financeiro,
            taxa_proj=float(calendario_financeiro.taxa_dia_base),
            serie_cdi=cache_cdi.serie_cdi,
        )
        valor_liquido_fim = float(clone.valor_liquido_hoje(data_fim))
    except Exception:
        valor_liquido_fim = valor_liquido_hoje
    custo_por_real = valor_liquido_fim / max(valor_liquido_hoje, 1e-9)
    taxa_bonus = float(getattr(lote, 'taxa_bonus_cdi', 0.0) or 0.0)
    taxa_base = float(getattr(lote, 'taxa_base_cdi', 0.0) or 0.0)
    taxa_ref = max(taxa_bonus, taxa_base)
    idade = max((data_cur - lote.data_base_fiscal).days, 0)
    penalidade = (taxa_ref * 0.001) + min(idade * 0.00001, 0.005)
    return float(custo_por_real + penalidade)


def _ordenar_lotes_para_pagamento(
    lotes_disponiveis: list[Lote],
    *,
    data_cur: date,
    data_fim: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    ids_preferidos: list[str] | None = None,
) -> list[Lote]:
    ids_pref = {limpar_texto(x) for x in (ids_preferidos or []) if limpar_texto(x)}
    ranqueados: list[tuple[float, Lote]] = []
    for lote in lotes_disponiveis:
        custo = _fator_oportunidade_lote(
            lote,
            data_cur=data_cur,
            data_fim=data_fim,
            calendario_financeiro=calendario_financeiro,
            cache_cdi=cache_cdi,
        )
        bonus_pref = -1e-9 if limpar_texto(lote.id) in ids_pref else 0.0
        ranqueados.append((custo + bonus_pref, lote))
    ranqueados.sort(key=lambda item: (item[0], limpar_texto(item[1].id)))
    return [l for _, l in ranqueados]


def _lotes_disponiveis_no_dia(lotes_ativos: list[Lote], data_cur: date) -> list[Lote]:
    return [
        lote for lote in lotes_ativos
        if not lote.esgotado
        and float(lote.saldo_bruto or 0.0) > 0.01
        and lote.data_aplicacao <= data_cur
        and not (lote.carencia_ate and data_cur < lote.carencia_ate)
    ]


def _simular_runner_futuro_shadow(
    pagamentos: pd.DataFrame,
    lotes_ativos: list[Lote],
    *,
    data_referencia: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if len(pagamentos) == 0:
        vazio = pd.DataFrame(columns=COLUNAS_SHADOW)
        return vazio, {
            'total_pagamentos': 0,
            'total_lotes_iniciais': len(lotes_ativos),
            'pagamentos_totalmente_cobertos': 0,
            'pagamentos_com_multifonte': 0,
            'valor_total_pagamentos': 0.0,
            'valor_total_resgatado_liquido': 0.0,
            'excesso_liquido_total': 0.0,
            'imposto_total_shadow': 0.0,
            'saldo_liquido_final_shadow': 0.0,
            'riqueza_total_shadow': 0.0,
        }
    data_fim = max(pagamentos['data'])
    pagamentos_por_data: dict[date, list[dict[str, Any]]] = {}
    for rec in pagamentos.to_dict(orient='records'):
        pagamentos_por_data.setdefault(rec['data'], []).append(rec)

    registros: list[dict[str, Any]] = []
    data_cur = data_referencia
    while data_cur <= data_fim:
        atualizar_saldo_lotes_no_dia(
            lotes_ativos,
            data_cur,
            calendario_financeiro,
            serie_cdi=cache_cdi.serie_cdi,
            taxa_proj=float(calendario_financeiro.taxa_dia_base),
            data_fechamento_referencia=data_cur,
        )
        for pagamento in pagamentos_por_data.get(data_cur, []):
            valor_pag = round(float(pagamento.get('valor') or 0.0), 2)
            falta = valor_pag
            disponiveis = _lotes_disponiveis_no_dia(lotes_ativos, data_cur)
            ids_preferidos = [limpar_texto(pagamento.get('lote_usado_1')), limpar_texto(pagamento.get('lote_usado_2'))]
            ordenados = _ordenar_lotes_para_pagamento(
                disponiveis,
                data_cur=data_cur,
                data_fim=data_fim,
                calendario_financeiro=calendario_financeiro,
                cache_cdi=cache_cdi,
                ids_preferidos=ids_preferidos,
            )
            movimentos: list[dict[str, Any]] = []
            for lote in ordenados:
                if falta <= 0.001:
                    break
                mov = executar_saque_lote(
                    lote,
                    falta,
                    data_cur,
                    tabela_iof=tabela_iof,
                    faixas_ir=faixas_ir,
                )
                if mov is None:
                    continue
                if float(mov.get('liquido') or 0.0) <= 0.0:
                    continue
                movimentos.append(mov)
                falta = round(max(falta - float(mov['liquido']), 0.0), 6)
            valor_liq_total = round(sum(float(m['liquido']) for m in movimentos), 2)
            imposto_total = round(sum(float(m['imposto']) for m in movimentos), 2)
            lotes_usados = [normalizar_identificador(m['lote'].id) for m in movimentos if normalizar_identificador(m['lote'].id)]
            lotes_usados_str = ' | '.join(lotes_usados)
            lote_principal = lotes_usados[0] if lotes_usados else None
            valor_principal = round(float(movimentos[0]['liquido']), 2) if movimentos else 0.0
            crit = 'runner_shadow_monofonte' if len(movimentos) <= 1 else 'runner_shadow_multifonte'
            obs = 'runner futuro shadow processado dia a dia com ordenação por custo de oportunidade do lote até o horizonte-base.'
            if falta > 0.01:
                obs += ' Pagamento ficou parcialmente descoberto nesta simulação shadow.'
            registros.append({
                'pagamento_id': limpar_texto(pagamento.get('despesa_id')),
                'data_pagamento': pagamento.get('data'),
                'descricao_pagamento': limpar_texto(pagamento.get('descricao')),
                'valor_pagamento': valor_pag,
                'valor_liquido_total_usado': valor_liq_total,
                'valor_excesso_liquido': round(max(valor_liq_total - valor_pag, 0.0), 2),
                'pagamento_totalmente_coberto': bool(falta <= 0.01),
                'qtd_lotes_usados': int(len(movimentos)),
                'lote_principal_shadow': lote_principal,
                'lotes_usados_shadow': lotes_usados_str,
                'valor_lote_principal_shadow': valor_principal,
                'imposto_pago_shadow': imposto_total,
                'criterio_shadow': crit,
                'observacao_auditavel': obs,
            })
        data_cur += timedelta(days=1)
    quadro = pd.DataFrame(registros).sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    saldo_liq_final = round(sum(float(l.valor_liquido_hoje(data_fim, tabela_iof=tabela_iof, faixas_ir=faixas_ir)) for l in lotes_ativos if not l.esgotado and float(l.saldo_bruto or 0.0) > 0.01), 2)
    total_resgatado_liq = round(sum(float(l.total_liquido_sacado or 0.0) for l in lotes_ativos), 2)
    imposto_total_shadow = round(sum(float(l.total_imposto_pago or 0.0) for l in lotes_ativos), 2)
    auditoria = {
        'total_pagamentos': int(len(quadro)),
        'total_lotes_iniciais': int(len(lotes_ativos)),
        'pagamentos_totalmente_cobertos': int(quadro['pagamento_totalmente_coberto'].fillna(False).sum()) if len(quadro) else 0,
        'pagamentos_com_multifonte': int((quadro['qtd_lotes_usados'].fillna(0) > 1).sum()) if len(quadro) else 0,
        'valor_total_pagamentos': round(float(quadro['valor_pagamento'].sum()), 2) if len(quadro) else 0.0,
        'valor_total_resgatado_liquido': total_resgatado_liq,
        'excesso_liquido_total': round(float(quadro['valor_excesso_liquido'].sum()), 2) if len(quadro) else 0.0,
        'imposto_total_shadow': imposto_total_shadow,
        'saldo_liquido_final_shadow': saldo_liq_final,
        'riqueza_total_shadow': round(saldo_liq_final + total_resgatado_liq, 2),
    }
    return quadro, auditoria


def _comparar_com_vigente(quadro_shadow: pd.DataFrame, quadro_vigente: pd.DataFrame) -> pd.DataFrame:
    if len(quadro_shadow) == 0:
        return pd.DataFrame(columns=[
            'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
            'lote_vigente', 'lote_principal_shadow', 'mudou_lote_principal',
            'qtd_lotes_usados', 'pagamento_totalmente_coberto_vigente', 'pagamento_totalmente_coberto_shadow',
            'delta_excesso_shadow_vs_vigente', 'delta_cobertura_shadow_vs_vigente',
        ])
    vigente = quadro_vigente.copy()
    vig_cols = {
        'pagamento_id': 'pagamento_id',
        'data_pagamento': 'data_pagamento',
        'descricao_pagamento': 'descricao_pagamento',
        'valor_pagamento': 'valor_pagamento',
        'lote_id_escolhido': 'lote_vigente',
        'valor_disponivel_escolhido': 'valor_disponivel_vigente',
        'pagamento_totalmente_coberto': 'pagamento_totalmente_coberto_vigente',
        'criterio_decisao': 'criterio_vigente',
        'custo_economico_proxy': 'custo_proxy_vigente',
    }
    vigente = vigente[[c for c in vig_cols if c in vigente.columns]].rename(columns=vig_cols)
    base = quadro_shadow.merge(vigente, on='pagamento_id', how='left', suffixes=('', '_vig'))
    base['excesso_vigente'] = (base['valor_disponivel_vigente'].fillna(0.0) - base['valor_pagamento']).clip(lower=0.0)
    base['mudou_lote_principal'] = base.apply(lambda r: (normalizar_identificador(r.get('lote_principal_shadow')) or '') != (normalizar_identificador(r.get('lote_vigente')) or ''), axis=1)
    base['delta_excesso_shadow_vs_vigente'] = (base['valor_excesso_liquido'].fillna(0.0) - base['excesso_vigente'].fillna(0.0)).round(2)
    base['delta_cobertura_shadow_vs_vigente'] = base['pagamento_totalmente_coberto'].fillna(False).astype(int) - base['pagamento_totalmente_coberto_vigente'].fillna(False).astype(int)
    cols = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
        'lote_vigente', 'lote_principal_shadow', 'mudou_lote_principal',
        'qtd_lotes_usados', 'pagamento_totalmente_coberto_vigente', 'pagamento_totalmente_coberto',
        'delta_excesso_shadow_vs_vigente', 'delta_cobertura_shadow_vs_vigente',
        'criterio_vigente', 'criterio_shadow', 'custo_proxy_vigente', 'observacao_auditavel',
    ]
    out = base[cols].rename(columns={'pagamento_totalmente_coberto': 'pagamento_totalmente_coberto_shadow', 'qtd_lotes_usados': 'qtd_lotes_usados_shadow'}).copy()
    return out.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)


def carregar_benchmark_runner_futuro_shadow(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    replay_passado: PacoteReplayPassadoControlado | None,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    decisao_local_v1: PacoteDecisaoLocalV1,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> PacoteBenchmarkRunnerFuturoShadow:
    pagamentos = _pagamentos_futuros(dados_operacionais, data_referencia=data_referencia)
    lotes = _lotes_ativos_para_runner(replay_passado)
    quadro_shadow, resumo_shadow = _simular_runner_futuro_shadow(
        pagamentos,
        lotes,
        data_referencia=data_referencia,
        calendario_financeiro=calendario_financeiro,
        cache_cdi=cache_cdi,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
    )
    quadro_comp = _comparar_com_vigente(quadro_shadow, decisao_local_v1.quadro_decisao_local_v1.copy())
    mudou = int(quadro_comp['mudou_lote_principal'].fillna(False).sum()) if len(quadro_comp) else 0
    multifonte = int((quadro_shadow['qtd_lotes_usados'].fillna(0) > 1).sum()) if len(quadro_shadow) else 0
    cob_shadow = int(quadro_shadow['pagamento_totalmente_coberto'].fillna(False).sum()) if len(quadro_shadow) else 0
    cob_vig = int(decisao_local_v1.quadro_decisao_local_v1['pagamento_totalmente_coberto'].fillna(False).sum()) if len(decisao_local_v1.quadro_decisao_local_v1) else 0
    recomendacao = 'inconclusivo'
    justificativa = 'benchmark do runner futuro shadow não produziu sinal forte o suficiente para governança.'
    if cob_shadow < cob_vig:
        recomendacao = 'vigente'
        justificativa = 'runner futuro shadow cobre menos pagamentos integralmente do que a decisão vigente.'
    elif multifonte > 0 and mudou > 0:
        recomendacao = 'benchmark_shadow_apenas_diagnostico'
        justificativa = 'runner futuro shadow altera a escolha e usa multifonte em parte dos pagamentos, mas permanece como benchmark diagnóstico.'
    elif mudou == 0:
        recomendacao = 'equivalente'
        justificativa = 'runner futuro shadow não alterou lote principal em relação à decisão vigente.'
    validacao = {'ok': True, 'erros': [], 'avisos': []}
    if len(pagamentos) and len(quadro_shadow) != len(pagamentos):
        validacao['ok'] = False
        validacao['erros'].append('runner_futuro_shadow_sem_resultado_para_todos_os_pagamentos')
    if multifonte > 0:
        validacao['avisos'].append('runner_futuro_shadow_com_multifonte_em_parte_dos_pagamentos')
    if mudou > 0:
        validacao['avisos'].append('runner_futuro_shadow_altera_lote_principal_em_parte_dos_pagamentos')
    auditoria = {
        'validacao': validacao,
        'resumo': {
            'total_pagamentos': int(len(pagamentos)),
            'pagamentos_totalmente_cobertos_shadow': cob_shadow,
            'pagamentos_totalmente_cobertos_vigente': cob_vig,
            'pagamentos_multifonte_shadow': multifonte,
            'pagamentos_com_mudanca_lote_principal': mudou,
            'recomendacao_shadow': recomendacao,
            'justificativa_recomendacao': justificativa,
            'resumo_shadow': resumo_shadow,
        },
    }
    return PacoteBenchmarkRunnerFuturoShadow(
        quadro_pagamentos_shadow=quadro_shadow,
        quadro_comparativo_vigente=quadro_comp,
        auditoria=auditoria,
        validacao=validacao,
    )
