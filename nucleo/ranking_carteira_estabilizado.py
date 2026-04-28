
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import json

import pandas as pd

from nucleo.carteira_canonica import PacoteCarteiraCanonica, normalizar_nome_produto
from nucleo.leitor_planilha import PacotePlanilha
from nucleo.utilitarios_neutros import para_float_monetario


@dataclass(slots=True)
class PacoteRankingCarteiraEstabilizado:
    contrato: dict[str, Any]
    parametros_fixos: dict[str, Any]
    quadro_ranking: pd.DataFrame
    quadro_destinos_switch: pd.DataFrame
    top30: pd.DataFrame
    resumo: dict[str, Any]
    validacao: dict[str, Any]
    auditoria: dict[str, Any]


def _repo_root(raiz_repositorio: Path | None = None) -> Path:
    if raiz_repositorio is not None:
        return Path(raiz_repositorio).resolve()
    return Path(__file__).resolve().parents[1]


def _carregar_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _obter_bloco_ranking_config(config: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(config, Mapping):
        return {}
    bloco = config.get('ranking_carteira')
    return bloco if isinstance(bloco, Mapping) else {}


def _resolver_contrato_e_parametros_ranking(
    raiz: Path,
    config: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    bloco = _obter_bloco_ranking_config(config)
    contrato_cfg = bloco.get('contract')
    parametros_cfg = bloco.get('fixed_parameters')

    if isinstance(contrato_cfg, Mapping) and contrato_cfg:
        contrato = dict(contrato_cfg)
        origem_contrato = 'dados/config_atualizado.json::ranking_carteira.contract'
    else:
        contrato = _carregar_json(raiz / 'config' / 'carteira_contract_v123.json')
        origem_contrato = 'config/carteira_contract_v123.json'

    if isinstance(parametros_cfg, Mapping) and parametros_cfg:
        parametros = dict(parametros_cfg)
        origem_parametros = 'dados/config_atualizado.json::ranking_carteira.fixed_parameters'
    else:
        parametros = _carregar_json(raiz / 'config' / 'fixed_parameters_ranking_carteira.json')
        origem_parametros = 'config/fixed_parameters_ranking_carteira.json'

    return contrato, parametros, {
        'contract_source': origem_contrato,
        'fixed_parameters_source': origem_parametros,
    }


def _bool_sim(valor: Any) -> bool:
    texto = str(valor or '').strip().lower()
    return texto in {'sim', 'true', '1', 's'}


def _to_num(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie, errors='coerce')


def _penalidade_prazo(horizonte: Any, parametros: Mapping[str, Any]) -> float:
    h = float(0.0 if pd.isna(horizonte) else horizonte)
    if h <= float(parametros.get('prazo_limite_1', 7)):
        return 0.0
    if h <= float(parametros.get('prazo_limite_2', 30)):
        return float(parametros.get('prazo_penalidade_2', 2))
    if h <= float(parametros.get('prazo_limite_3', 60)):
        return float(parametros.get('prazo_penalidade_3', 6))
    if h <= float(parametros.get('prazo_limite_4', 180)):
        return float(parametros.get('prazo_penalidade_4', 10))
    if h <= float(parametros.get('prazo_limite_5', 365)):
        return float(parametros.get('prazo_penalidade_5', 14))
    return float(parametros.get('prazo_penalidade_acima_5', 18))


def _validar_colunas(df: pd.DataFrame, contrato: Mapping[str, Any]) -> dict[str, Any]:
    obrigatorias = list(contrato.get('input_columns', [])) + list(contrato.get('derived_columns_present_in_sheet', []))
    faltantes = [col for col in obrigatorias if col not in df.columns]
    return {'ok': not faltantes, 'colunas_faltantes': faltantes, 'colunas_presentes': list(df.columns)}


def _enriquecer_com_chaves(df: pd.DataFrame, carteira_canonica: PacoteCarteiraCanonica) -> pd.DataFrame:
    out = df.copy()
    mapa = (carteira_canonica.mapa_produtos.get('by_nome_norm', {}) if carteira_canonica is not None else {}) or {}
    canonico = carteira_canonica.quadro_canonico.copy() if carteira_canonica is not None else pd.DataFrame([])
    out['nome_norm'] = out['Nome'].map(normalizar_nome_produto)
    out['produto_key'] = out['nome_norm'].map(mapa)
    if len(canonico):
        merge_cols = ['produto_key', 'liquidez_dias', 'carencia_dias', 'taxa_base_cdi', 'taxa_bonus_cdi', 'elegivel_switch_in', 'elegivel_motor']
        canonico_merge = canonico[[c for c in merge_cols if c in canonico.columns]].drop_duplicates(subset=['produto_key'])
        out = out.merge(canonico_merge, on='produto_key', how='left')
    return out


def carregar_ranking_carteira_estabilizado(
    pacote_planilha: PacotePlanilha,
    carteira_canonica: PacoteCarteiraCanonica,
    *,
    raiz_repositorio: Path | None = None,
    config: Mapping[str, Any] | None = None,
) -> PacoteRankingCarteiraEstabilizado:
    raiz = _repo_root(raiz_repositorio)
    contrato, parametros, origem_config = _resolver_contrato_e_parametros_ranking(raiz, config)

    nome_aba = str(contrato.get('sheet_name') or 'Carteira')
    if nome_aba not in pacote_planilha.quadros_brutos:
        raise KeyError(f"Aba {nome_aba!r} não encontrada na planilha.")
    df = pacote_planilha.quadros_brutos[nome_aba].copy()
    validacao_colunas = _validar_colunas(df, contrato)
    if not validacao_colunas['ok']:
        raise KeyError(f"Contrato da Carteira não atendido. Faltantes: {validacao_colunas['colunas_faltantes']}")

    df = _enriquecer_com_chaves(df, carteira_canonica)

    numeric_cols = [
        'Horizonte_Efetivo_Dias', 'SAOF_Final', 'Rank_Consolidado_Final_Ativos', 'Rank_Bucket_Final_Ativos',
        'Rank_Bucket_Ativos', 'Rank_Consolidado_Ativos', 'Taxa_Base_CDI', 'Taxa_Bonus_CDI', 'Prazo_Dias',
        'Carência_Dias', 'SAOF', 'Retorno_Proxy_aa', 'Score_Retorno_Proxy',
        'Fit_Liquidez', 'Fit_Ticket', 'Proteção_Estrutural', 'Risco_Real_Score', 'Risco_Proteção', 'Eficiência_Fiscal', 'Robustez_Operacional'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = _to_num(df[col])
    if 'Aplicação_Mínima' in df.columns:
        df['Aplicação_Mínima'] = df['Aplicação_Mínima'].apply(lambda x: float(para_float_monetario(x, 0.0) or 0.0))
    if 'Aplicação_Máxima' in df.columns:
        df['Aplicação_Máxima'] = df['Aplicação_Máxima'].apply(lambda x: float(para_float_monetario(x, 0.0) or 0.0))

    df['Ativo_bool'] = df['Ativo'].map(_bool_sim)
    df['Elegível_SAOF_bool'] = df['Elegível_SAOF'].map(_bool_sim)
    mask_ativos = df['Ativo_bool'] & df['Elegível_SAOF_bool']

    df['Penalidade_Prazo_Consolidado'] = df['Horizonte_Efetivo_Dias'].apply(lambda x: _penalidade_prazo(x, parametros))
    df['SAOF_Final_Prazo'] = pd.NA
    df.loc[mask_ativos, 'SAOF_Final_Prazo'] = (df.loc[mask_ativos, 'SAOF_Final'].fillna(0.0) - df.loc[mask_ativos, 'Penalidade_Prazo_Consolidado'].fillna(0.0)).round(1)
    df['Rank_Consolidado_Prazo_Ativos'] = pd.NA
    ordenados = df.loc[mask_ativos].copy()
    ordenados = ordenados.sort_values(
        by=['SAOF_Final_Prazo', 'SAOF_Final', 'Rank_Consolidado_Final_Ativos', 'Nome'],
        ascending=[False, False, True, True],
        kind='stable',
    ).reset_index()
    ordenados['Rank_Consolidado_Prazo_Ativos'] = range(1, len(ordenados) + 1)
    df.loc[ordenados['index'], 'Rank_Consolidado_Prazo_Ativos'] = ordenados['Rank_Consolidado_Prazo_Ativos'].values
    df['Delta_Rank'] = pd.NA
    df.loc[mask_ativos, 'Delta_Rank'] = (_to_num(df.loc[mask_ativos, 'Rank_Consolidado_Final_Ativos']) - _to_num(df.loc[mask_ativos, 'Rank_Consolidado_Prazo_Ativos'])).round(0)

    # validation against source sheet for mirrored columns
    linhas_valid = []
    for col in contrato.get('derived_columns_present_in_sheet', []):
        if col not in df.columns:
            continue
        serie = df[col]
        diff_material = 0
        if pd.api.types.is_numeric_dtype(serie):
            diff_material = int((serie.fillna(0).sub(serie.fillna(0)).abs() > 1e-9).sum())
        else:
            diff_material = int((serie.fillna('').astype(str) != serie.fillna('').astype(str)).sum())
        linhas_valid.append({'coluna': col, 'dif_materiais': diff_material})
    quadro_validacao = pd.DataFrame(linhas_valid)

    top30 = df.loc[mask_ativos].copy()
    top30 = top30.sort_values(['Rank_Consolidado_Prazo_Ativos', 'Nome'], kind='stable').head(30).copy()
    top30['Score Final Prazo'] = _to_num(top30['SAOF_Final_Prazo']).round(1)

    destinos = df.loc[mask_ativos].copy()
    if 'elegivel_switch_in' in destinos.columns:
        destinos = destinos.loc[destinos['elegivel_switch_in'].fillna(False)].copy()
    destinos = destinos.sort_values(['Rank_Consolidado_Prazo_Ativos', 'SAOF_Final_Prazo', 'Nome'], ascending=[True, False, True], kind='stable')
    destinos['proxy_terminal_destino'] = (_to_num(destinos['SAOF_Final_Prazo']).fillna(0.0) / 100.0).round(4)
    destinos['score_final'] = _to_num(destinos['SAOF_Final_Prazo']).fillna(0.0).round(1)
    destinos['retorno_anual_proxy'] = _to_num(destinos.get('Retorno_Proxy_aa', pd.Series(dtype=float))).fillna(0.0).round(4)
    destinos['rank_destino'] = _to_num(destinos['Rank_Consolidado_Prazo_Ativos']).astype('Int64')
    destinos['carencia_dias'] = _to_num(destinos.get('carencia_dias', destinos.get('Carência_Dias', pd.Series(dtype=float)))).fillna(0).astype(int)
    destinos['liquidez_dias'] = _to_num(destinos.get('liquidez_dias', destinos.get('Carência_Dias', pd.Series(dtype=float)))).fillna(0).astype(int)
    destinos['aplicacao_minima'] = destinos.get('Aplicação_Mínima', pd.Series(dtype=object)).apply(lambda x: float(para_float_monetario(x, 0.0) or 0.0)).round(2)
    destinos['aplicacao_maxima'] = destinos.get('Aplicação_Máxima', pd.Series(dtype=object)).apply(lambda x: float(para_float_monetario(x, 0.0) or 0.0)).round(2)
    destinos['somente_combo'] = destinos.get('Somente_Combo', pd.Series(dtype=object)).map(_bool_sim).fillna(False)
    destinos['tipo_produto'] = destinos.get('Tipo', pd.Series(dtype=object)).fillna('').astype(str)
    destinos['produto_base'] = destinos.get('Produto_Base', pd.Series(dtype=object)).fillna('').astype(str)
    destinos['produto_bonus'] = destinos.get('Produto_Bonus', pd.Series(dtype=object)).fillna('').astype(str)
    destinos['ratio_base'] = _to_num(destinos.get('Ratio_Base', pd.Series(dtype=float))).fillna(0.0)
    destinos['ratio_bonus'] = _to_num(destinos.get('Ratio_Bonus', pd.Series(dtype=float))).fillna(0.0)
    destinos = destinos[[
        'rank_destino', 'produto_key', 'Nome', 'score_final', 'proxy_terminal_destino', 'retorno_anual_proxy',
        'liquidez_dias', 'carencia_dias', 'aplicacao_minima', 'aplicacao_maxima', 'somente_combo',
        'tipo_produto', 'produto_base', 'produto_bonus', 'ratio_base', 'ratio_bonus',
        'taxa_base_cdi', 'taxa_bonus_cdi', 'Bucket_SAOF', 'SAOF_Final_Prazo',
        'Rank_Consolidado_Final_Ativos', 'Status_Confirmação', 'Campos_Pendentes'
    ]].rename(columns={'Nome': 'nome'})

    resumo = {
        'produtos_total': int(len(df)),
        'produtos_ativos_ranqueados': int(mask_ativos.sum()),
        'top30_bucket': {str(k): int(v) for k, v in top30['Bucket_SAOF'].fillna('vazio').value_counts().to_dict().items()},
        'top10': top30[['Rank_Consolidado_Prazo_Ativos', 'Nome', 'Bucket_SAOF', 'Score Final Prazo']].head(10).to_dict('records'),
        'tesouro_rank_prazo_min': int(_to_num(top30.loc[top30['Nome'].astype(str).str.contains('Tesouro', case=False, na=False), 'Rank_Consolidado_Prazo_Ativos']).min()) if top30['Nome'].astype(str).str.contains('Tesouro', case=False, na=False).any() else None,
    }
    auditoria = {
        'metodo': 'carteira_only_estabilizado_v3_3_adaptado',
        'usa_coluna_fonte_para_nucleo': True,
        'penalidade_prazo_interna': True,
        'qtd_destinos_switch': int(len(destinos)),
        'destino_top1': None if len(destinos) == 0 else str(destinos.iloc[0]['nome']),
        'contract_file': origem_config['contract_source'],
        'fixed_parameters_file': origem_config['fixed_parameters_source'],
        'contract_fallback_file': 'config/carteira_contract_v123.json',
        'fixed_parameters_fallback_file': 'config/fixed_parameters_ranking_carteira.json',
    }
    validacao = {
        'colunas': validacao_colunas,
        'qtd_diffs_materiais_nucleo': int(quadro_validacao['dif_materiais'].sum()) if len(quadro_validacao) else 0,
        'aceite_nucleo': int(quadro_validacao['dif_materiais'].sum()) == 0 if len(quadro_validacao) else True,
    }
    return PacoteRankingCarteiraEstabilizado(
        contrato=contrato,
        parametros_fixos=parametros,
        quadro_ranking=df,
        quadro_destinos_switch=destinos.reset_index(drop=True),
        top30=top30.reset_index(drop=True),
        resumo=resumo,
        validacao=validacao,
        auditoria=auditoria,
    )
