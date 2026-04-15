"""Triagem programática v1 do motor.

Esta camada reduz o universo completo da aba `Carteira` para um subconjunto
promissor e auditável por cenário, funcionando apenas como **triagem preliminar
proxy** do motor. Ela não representa decisão econômica final e não substitui
o motor conjunto futuro.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

import pandas as pd

from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro
from nucleo.carteira_canonica import PacoteCarteiraCanonica
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import limitar_intervalo, normalizar_texto, para_float_monetario, para_int


@dataclass(slots=True)
class PacoteTriagemMotor:
    contexto: dict[str, Any]
    quadro_triagem: pd.DataFrame
    quadro_candidatos: pd.DataFrame
    auditoria: dict[str, Any]


def _cfg(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


def _mapa_risco(valor: str) -> float:
    texto = normalizar_texto(valor)
    mapa = {
        'muito baixo': 100.0,
        'baixo': 85.0,
        'medio': 60.0,
        'alto': 30.0,
        'muito alto': 10.0,
    }
    return mapa.get(texto, 55.0)


def _proxy_retorno_anual(row: pd.Series, config: Mapping[str, Any]) -> float:
    regime = str(row.get('regime_taxa') or '')
    base = float(para_float_monetario(row.get('taxa_base_cdi'), 0.0))
    bonus = float(para_float_monetario(row.get('taxa_bonus_cdi'), 0.0))
    dias_bonus = int(para_int(row.get('dias_bonus'), 0))
    horizonte = int(_cfg(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180)
    cdi = float(_cfg(config, 'premissas_mercado', 'cdi_anual_modelo', padrao=0.149) or 0.149)
    selic = float(_cfg(config, 'premissas_mercado', 'selic_anual_modelo', padrao=cdi) or cdi)
    ipca = float(_cfg(config, 'premissas_mercado', 'ipca_anual_modelo', padrao=0.045) or 0.045)
    cap_var = float(_cfg(config, 'triagem_motor', 'cap_anual_variavel', padrao=1.0) or 1.0)
    cap_mult = float(_cfg(config, 'triagem_motor', 'cap_anual_cdi_multiplicador', padrao=1.5) or 1.5)

    if regime == 'combo':
        retorno = (1.0 + cdi) ** max(min(base, cap_mult), 0.0) - 1.0
    elif regime == 'cdi_bonus':
        frac_bonus = min(max(dias_bonus, 0), max(horizonte, 1)) / max(horizonte, 1)
        mult = base * (1.0 - frac_bonus) + max(base, bonus) * frac_bonus
        retorno = (1.0 + cdi) ** max(min(mult, cap_mult), 0.0) - 1.0
    elif regime == 'cdi_escalonado':
        mult = max(base, bonus or base)
        retorno = (1.0 + cdi) ** max(min(mult, cap_mult), 0.0) - 1.0
    elif regime == 'cdi_base':
        retorno = (1.0 + cdi) ** max(min(base, cap_mult), 0.0) - 1.0
    elif regime == 'selic':
        retorno = (1.0 + selic) ** max(min(base, cap_mult), 0.0) - 1.0
    elif regime == 'prefixado':
        retorno = max(base, 0.0)
    elif regime == 'ipca':
        retorno = ((1.0 + ipca) * (1.0 + max(base, 0.0))) - 1.0
    elif regime == 'variavel':
        retorno = min(max(base, 0.0) * cdi, cap_var)
    else:
        retorno = min(max(base, 0.0) * cdi, cap_var)
    return float(max(retorno, 0.0))


def _score_liquidez(row: pd.Series, contexto: Mapping[str, Any]) -> float:
    bloqueio = max(int(para_int(row.get('carencia_dias'), 0)), int(para_int(row.get('liquidez_dias'), 0)))
    prazo = int(para_int(row.get('prazo_dias'), 0))
    dias_primeira = contexto.get('dias_ate_primeira_despesa_futura')
    cobertura30 = float(contexto.get('cobertura_caixa_30_dias', 10.0) or 10.0)
    despesas30 = float(contexto.get('despesas_futuras_30_dias', 0.0) or 0.0)
    score = 100.0

    if bloqueio == 0:
        score = 100.0
    elif bloqueio <= 7:
        score = 85.0
    elif bloqueio <= 30:
        score = 70.0
    elif bloqueio <= 60:
        score = 55.0
    elif bloqueio <= 90:
        score = 40.0
    else:
        score = 20.0

    if dias_primeira is not None and bloqueio > int(dias_primeira):
        score -= min(40.0, float(bloqueio - int(dias_primeira)) * 0.6)
    if despesas30 > 0 and cobertura30 < 1.0 and bloqueio > 0:
        score -= 20.0
    if str(row.get('regime_liquidez') or '') == 'vencimento' and prazo > 0 and dias_primeira is not None and prazo > int(dias_primeira):
        score -= 10.0
    return limitar_intervalo(score)


def _score_viabilidade(row: pd.Series, contexto: Mapping[str, Any]) -> float:
    minimo = float(para_float_monetario(row.get('aplicacao_minima'), 0.0))
    maximo = float(para_float_monetario(row.get('aplicacao_maxima'), 0.0))
    disp = float(contexto.get('recursos_disponiveis_para_aporte', 0.0) or 0.0)
    total = float(contexto.get('recursos_totais_mobilizaveis', 0.0) or 0.0)
    if minimo <= 0 or minimo <= disp + 1e-9:
        score = 100.0
    elif minimo <= total + 1e-9:
        ratio = minimo / max(total, 1.0)
        score = 85.0 - (35.0 * ratio)
    else:
        ratio = minimo / max(total, 1.0)
        score = 40.0 - min(40.0, (ratio - 1.0) * 20.0)
    if maximo > 0 and disp > (3.0 * maximo):
        score -= 10.0
    if bool(row.get('permite_combo', False)):
        score -= 3.0
    return limitar_intervalo(score)


def _score_risco(row: pd.Series) -> float:
    score = _mapa_risco(str(row.get('risco_real') or ''))
    if bool(row.get('fgc', False)):
        score += 10.0
    familia = str(row.get('familia_produto') or '')
    regime = str(row.get('regime_taxa') or '')
    if 'variavel' in familia or regime == 'variavel':
        score -= 10.0
    return limitar_intervalo(score)


def _construir_contexto_triagem(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    config: Mapping[str, Any],
    data_referencia: date,
) -> dict[str, Any]:
    inventario = dados_operacionais.inventario_canonico.copy()
    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(inventario) == 0:
        inventario = pd.DataFrame([])
    if len(gastos) == 0:
        gastos = pd.DataFrame([])

    nao_aportado_disp = inventario[inventario.get('nao_aportado_disponivel').fillna(False)] if len(inventario) else inventario
    aportados = inventario[inventario.get('aportado').fillna(False)] if len(inventario) else inventario
    futuros = inventario[inventario.get('recebido_futuro_nao_disponivel').fillna(False)] if len(inventario) else inventario
    gastos_futuros = gastos[gastos.get('futuro_ou_pendente_na_data_referencia').fillna(False)] if len(gastos) else gastos

    recursos_disponiveis = float(nao_aportado_disp.get('valor_original', pd.Series(dtype=float)).sum()) if len(nao_aportado_disp) else 0.0
    recursos_aportados = float(aportados.get('valor_original', pd.Series(dtype=float)).sum()) if len(aportados) else 0.0
    recursos_futuros = float(futuros.get('valor_original', pd.Series(dtype=float)).sum()) if len(futuros) else 0.0
    recursos_totais = recursos_disponiveis + recursos_aportados

    def soma_ate(dias: int) -> float:
        if len(gastos_futuros) == 0:
            return 0.0
        limite = pd.Timestamp(data_referencia) + pd.Timedelta(days=dias)
        serie_data = pd.to_datetime(gastos_futuros['data'], errors='coerce')
        mask = serie_data <= limite
        return float(pd.to_numeric(gastos_futuros.loc[mask, 'valor'], errors='coerce').fillna(0.0).sum())

    serie_data = pd.to_datetime(gastos_futuros.get('data'), errors='coerce') if len(gastos_futuros) else pd.Series(dtype='datetime64[ns]')
    dias_ate_primeira = None
    if len(serie_data.dropna()) > 0:
        primeira = serie_data.dropna().min().date()
        dias_ate_primeira = max((primeira - data_referencia).days, 0)

    despesas_30 = soma_ate(30)
    despesas_60 = soma_ate(60)
    despesas_90 = soma_ate(90)

    return {
        'data_referencia': data_referencia,
        'horizonte_principal_dias': int(_cfg(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180),
        'horizonte_minimo_dias': int(_cfg(config, 'simulacao', 'horizonte_minimo_dias', padrao=30) or 30),
        'recursos_disponiveis_para_aporte': recursos_disponiveis,
        'recursos_aportados_observados': recursos_aportados,
        'recursos_futuros_nao_disponiveis': recursos_futuros,
        'recursos_totais_mobilizaveis': recursos_totais,
        'despesas_futuras_total': float(pd.to_numeric(gastos_futuros.get('valor', pd.Series(dtype=float)), errors='coerce').fillna(0.0).sum()) if len(gastos_futuros) else 0.0,
        'despesas_futuras_30_dias': despesas_30,
        'despesas_futuras_60_dias': despesas_60,
        'despesas_futuras_90_dias': despesas_90,
        'dias_ate_primeira_despesa_futura': dias_ate_primeira,
        'cobertura_caixa_30_dias': recursos_disponiveis / max(despesas_30, 1.0) if despesas_30 > 0 else 10.0,
        'taxa_dia_base': calendario_financeiro.taxa_dia_base,
        'cdi_anual_modelo': calendario_financeiro.cdi_anual_modelo,
    }


def carregar_triagem_motor(
    carteira_canonica: PacoteCarteiraCanonica,
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
) -> PacoteTriagemMotor:
    contexto = _construir_contexto_triagem(dados_operacionais, calendario_financeiro, config, data_referencia)
    df = carteira_canonica.quadro_canonico.copy()
    if len(df) == 0:
        return PacoteTriagemMotor(contexto=contexto, quadro_triagem=df, quadro_candidatos=df, auditoria={'qtd_total_produtos': 0})

    df['elegivel_bruto'] = (
        df['ativo'].fillna(False)
        & df['elegivel_motor'].fillna(False)
        & (~df['somente_combo'].fillna(False) | df['permite_combo'].fillna(False))
    )
    df['motivo_nao_elegibilidade'] = ''
    df.loc[~df['ativo'].fillna(False), 'motivo_nao_elegibilidade'] = 'produto_inativo'
    df.loc[df['ativo'].fillna(False) & ~df['elegivel_motor'].fillna(False), 'motivo_nao_elegibilidade'] = 'nao_elegivel_motor'
    df.loc[df['somente_combo'].fillna(False) & ~df['permite_combo'].fillna(False), 'motivo_nao_elegibilidade'] = 'somente_combo_sem_combo'

    df['retorno_anual_proxy'] = df.apply(lambda r: _proxy_retorno_anual(r, config), axis=1)
    retorno_vals = [float(v) for v in df.loc[df['elegivel_bruto'], 'retorno_anual_proxy'].tolist()] or [0.0]
    min_ret, max_ret = min(retorno_vals), max(retorno_vals)
    if abs(max_ret - min_ret) <= 1e-12:
        df['score_retorno'] = 100.0
    else:
        df['score_retorno'] = df['retorno_anual_proxy'].apply(lambda v: limitar_intervalo(((float(v) - min_ret) / (max_ret - min_ret)) * 100.0))
    df['score_liquidez'] = df.apply(lambda r: _score_liquidez(r, contexto), axis=1)
    df['score_viabilidade'] = df.apply(lambda r: _score_viabilidade(r, contexto), axis=1)
    df['score_risco'] = df.apply(_score_risco, axis=1)

    w_ret = float(_cfg(config, 'triagem_motor', 'peso_retorno', padrao=0.35) or 0.35)
    w_liq = float(_cfg(config, 'triagem_motor', 'peso_liquidez', padrao=0.30) or 0.30)
    w_via = float(_cfg(config, 'triagem_motor', 'peso_viabilidade', padrao=0.20) or 0.20)
    w_ris = float(_cfg(config, 'triagem_motor', 'peso_risco', padrao=0.15) or 0.15)
    df['score_final'] = (
        (df['score_retorno'] * w_ret)
        + (df['score_liquidez'] * w_liq)
        + (df['score_viabilidade'] * w_via)
        + (df['score_risco'] * w_ris)
    )
    df['score_final'] = df['score_final'].apply(limitar_intervalo)

    df = df.sort_values(by=['elegivel_bruto', 'score_final', 'score_retorno'], ascending=[False, False, False], kind='stable').reset_index(drop=True)
    df['rank_global'] = 0
    if df['elegivel_bruto'].any():
        elegiveis_idx = df.index[df['elegivel_bruto']].tolist()
        for rank, idx in enumerate(elegiveis_idx, start=1):
            df.at[idx, 'rank_global'] = rank
    df['rank_familia'] = 0
    for familia, sub in df[df['elegivel_bruto']].groupby('familia_produto', sort=False):
        for rank, idx in enumerate(sub.sort_values(by=['score_final', 'score_retorno'], ascending=[False, False], kind='stable').index.tolist(), start=1):
            df.at[idx, 'rank_familia'] = rank

    top_k_global = int(_cfg(config, 'triagem_motor', 'top_k_global', padrao=24) or 24)
    top_k_familia = int(_cfg(config, 'triagem_motor', 'top_k_por_familia', padrao=4) or 4)
    score_minimo = float(_cfg(config, 'triagem_motor', 'score_minimo_selecao', padrao=35.0) or 35.0)

    df['selecionado_motor_v1'] = (
        df['elegivel_bruto']
        & (df['score_final'] >= score_minimo)
        & ((df['rank_global'] > 0) & ((df['rank_global'] <= top_k_global) | (df['rank_familia'] <= top_k_familia) | df['produto_padrao'].fillna(False)))
    )

    candidatos = df[df['selecionado_motor_v1']].copy().reset_index(drop=True)

    auditoria = {
        'qtd_total_produtos': int(len(df)),
        'qtd_elegiveis_brutos': int(df['elegivel_bruto'].sum()),
        'natureza_triagem': 'proxy_preliminar',
        'qtd_candidatos_motor_v1': int(df['selecionado_motor_v1'].sum()),
        'qtd_produtos_padrao': int(df['produto_padrao'].sum()),
        'pesos_score_v1': {'retorno': w_ret, 'liquidez': w_liq, 'viabilidade': w_via, 'risco': w_ris},
        'top_k_global': top_k_global,
        'top_k_por_familia': top_k_familia,
        'score_minimo_selecao': score_minimo,
        'observacao': 'Score v1 usado apenas como triagem preliminar proxy; nao e decisao final do motor.',
        'contexto': contexto,
        'resumo_familia_produto': {str(k): int(v) for k, v in df['familia_produto'].fillna('vazio').value_counts(dropna=False).to_dict().items()},
        'resumo_regime_taxa': {str(k): int(v) for k, v in df['regime_taxa'].fillna('vazio').value_counts(dropna=False).to_dict().items()},
        'resumo_regime_liquidez': {str(k): int(v) for k, v in df['regime_liquidez'].fillna('vazio').value_counts(dropna=False).to_dict().items()},
        'amostra_top_produtos': candidatos[['produto_key', 'nome', 'familia_produto', 'regime_taxa', 'score_final']].head(10).to_dict('records') if len(candidatos) else [],
    }
    return PacoteTriagemMotor(contexto=contexto, quadro_triagem=df, quadro_candidatos=candidatos, auditoria=auditoria)
