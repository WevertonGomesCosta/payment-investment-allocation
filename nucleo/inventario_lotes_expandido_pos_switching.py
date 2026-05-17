from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Optional

import pandas as pd

from nucleo.carteira_canonica import PacoteCarteiraCanonica, normalizar_nome_produto
from nucleo.utilitarios_neutros import limpar_texto, normalizar_identificador, para_data, para_float_monetario


def _resolver_produto_canonico_local(valor_produto: str, carteira: Optional[PacoteCarteiraCanonica]) -> dict[str, Any]:
    if not valor_produto:
        return {
            'produto_key': None, 'produto_nome_canonico': None, 'produto_nome_norm': None,
            'produto_encontrado': False, 'tipo_match_produto': 'vazio', 'score_match_produto': 0.0, 'referencia_match_produto': ''
        }
    if carteira is None:
        return {
            'produto_key': None, 'produto_nome_canonico': valor_produto, 'produto_nome_norm': normalizar_nome_produto(valor_produto),
            'produto_encontrado': False, 'tipo_match_produto': 'sem_carteira_canonica', 'score_match_produto': 0.0, 'referencia_match_produto': ''
        }
    by_key = carteira.mapa_produtos.get('by_key', {})
    by_nome = carteira.mapa_produtos.get('by_nome_norm', {})
    valor_norm = normalizar_nome_produto(valor_produto)
    if valor_produto in by_key:
        info = by_key.get(valor_produto, {})
        return {'produto_key': info.get('produto_key'),'produto_nome_canonico': info.get('nome'),'produto_nome_norm': info.get('nome_norm'),'produto_encontrado': True,'tipo_match_produto': 'produto_key_exato','score_match_produto': 1.0,'referencia_match_produto': info.get('nome') or valor_produto}
    if valor_norm in by_nome:
        info = by_key.get(by_nome[valor_norm], {})
        return {'produto_key': info.get('produto_key'),'produto_nome_canonico': info.get('nome'),'produto_nome_norm': info.get('nome_norm'),'produto_encontrado': True,'tipo_match_produto': 'nome_norm','score_match_produto': 1.0,'referencia_match_produto': info.get('nome') or valor_produto}
    return {'produto_key': None,'produto_nome_canonico': valor_produto,'produto_nome_norm': valor_norm,'produto_encontrado': False,'tipo_match_produto': 'nao_encontrado','score_match_produto': 0.0,'referencia_match_produto': ''}

COLUNAS_SCHEMA = [
    'lote_id','lote_id_raw','ordem_planilha_lote','origem_registro','data_recebimento','data_aplicacao','valor_original',
    'data_base_fiscal','data_base_fiscal_inferida','status_lote_informado','investimento_bruto','produto_informado',
    'situacao_investimento','aportado','nao_aportado_disponivel','nao_aportado_exaurido','recebido_futuro_nao_disponivel',
    'disponivel_na_data_referencia','produto_key','produto_nome_canonico','produto_nome_norm','produto_encontrado',
    'tipo_match_produto','score_match_produto','referencia_match_produto',
]


def normalizar_lotes_pos_switching_para_schema_inventario(
    switching_canonico: Optional[pd.DataFrame],
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    carteira_canonica: Optional[PacoteCarteiraCanonica] = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    if switching_canonico is None or len(switching_canonico) == 0:
        return pd.DataFrame([], columns=COLUNAS_SCHEMA), {
            'qtd_lotes_pos_switching_normalizados': 0,
            'qtd_lotes_pos_com_schema_valido': 0,
            'qtd_lotes_pos_sem_produto_destino': 0,
            'qtd_lotes_pos_sem_valor': 0,
            'qtd_lotes_pos_sem_data_recebimento': 0,
            'qtd_lotes_pos_sem_data_aplicacao': 0,
        }

    for idx, row in switching_canonico.iterrows():
        lote_destino_raw = row.get('lote_destino')
        lote_id = normalizar_identificador(lote_destino_raw)
        if not lote_id:
            continue

        data_recebimento = para_data(row.get('data_recebimento')) or para_data(row.get('data_switching')) or para_data(row.get('data_aplicacao'))
        data_aplicacao = para_data(row.get('data_aplicacao')) or para_data(row.get('data_switching')) or data_recebimento
        data_base_fiscal = data_aplicacao

        valor = para_float_monetario(row.get('valor_liquido_origem'), 0.0)
        produto_destino = limpar_texto(row.get('produto_destino'))

        produto_resolvido = _resolver_produto_canonico_local(produto_destino, carteira_canonica)
        data_disponibilidade = data_recebimento or data_aplicacao

        registros.append({
            'lote_id': lote_id,
            'lote_id_raw': lote_destino_raw,
            'ordem_planilha_lote': int(row.get('ordem_planilha_switching') or idx + 1),
            'origem_registro': 'lote_pos_switching_normalizado',
            'data_recebimento': data_recebimento,
            'data_aplicacao': data_aplicacao,
            'valor_original': valor,
            'data_base_fiscal': data_base_fiscal,
            'data_base_fiscal_inferida': True,
            'status_lote_informado': limpar_texto(row.get('status')),
            'investimento_bruto': produto_destino,
            'produto_informado': produto_destino,
            'situacao_investimento': 'aportado',
            'aportado': True,
            'nao_aportado_disponivel': False,
            'nao_aportado_exaurido': False,
            'recebido_futuro_nao_disponivel': False,
            'disponivel_na_data_referencia': bool(data_disponibilidade is None or data_disponibilidade <= data_referencia),
            **produto_resolvido,
        })

    df = pd.DataFrame(registros, columns=COLUNAS_SCHEMA)
    auditoria = {
        'qtd_lotes_pos_switching_normalizados': int(len(df)),
        'qtd_lotes_pos_com_schema_valido': int(len(df)),
        'qtd_lotes_pos_sem_produto_destino': int((df['produto_informado'].fillna('') == '').sum()) if len(df) else 0,
        'qtd_lotes_pos_sem_valor': int((pd.to_numeric(df['valor_original'], errors='coerce').fillna(0.0) <= 0).sum()) if len(df) else 0,
        'qtd_lotes_pos_sem_data_recebimento': int(df['data_recebimento'].isna().sum()) if len(df) else 0,
        'qtd_lotes_pos_sem_data_aplicacao': int(df['data_aplicacao'].isna().sum()) if len(df) else 0,
        'qtd_lotes_pos_sem_data_base_fiscal': int(df['data_base_fiscal'].isna().sum()) if len(df) else 0,
        'qtd_lotes_pos_com_produto_resolvido': int(df['produto_encontrado'].fillna(False).astype(bool).sum()) if len(df) else 0,
    }
    return df, auditoria


def construir_inventario_lotes_expandido(
    inventario_canonico: pd.DataFrame,
    lotes_pos_switching_normalizados: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = inventario_canonico.copy()
    pos = lotes_pos_switching_normalizados.copy()
    for c in base.columns:
        if c not in pos.columns:
            pos[c] = None
    for c in pos.columns:
        if c not in base.columns:
            base[c] = None
    pos = pos[base.columns]
    duplicados = 0
    if 'lote_id' in base.columns and 'lote_id' in pos.columns and len(pos):
        ids_base = set(base['lote_id'].astype(str).str.strip().str.lower())
        duplicados = int(pos['lote_id'].astype(str).str.strip().str.lower().isin(ids_base).sum())
    expandido = pd.concat([base, pos], ignore_index=True)
    auditoria = {
        'qtd_lotes_inventario_original': int(len(base)),
        'qtd_lotes_pos_switching_normalizados': int(len(pos)),
        'qtd_lotes_inventario_expandido': int(len(expandido)),
        'qtd_lotes_pos_duplicados_com_inventario_original': duplicados,
    }
    return expandido, auditoria
