from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from nucleo.benchmark_runner_futuro_shadow import PacoteBenchmarkRunnerFuturoShadow
from nucleo.utilitarios_neutros import limpar_texto


@dataclass(slots=True)
class PacoteAuditoriaRunnerFuturoShadow:
    quadro_sem_cobertura: pd.DataFrame
    quadro_multifonte: pd.DataFrame
    quadro_datas_criticas: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


COLUNAS_SEM_COBERTURA = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'valor_liquido_total_usado', 'valor_descoberto', 'qtd_lotes_usados_shadow',
    'lote_principal_shadow', 'lotes_usados_shadow', 'motivo_sem_cobertura',
    'fase_temporal_shadow', 'lote_vigente', 'delta_excesso_shadow_vs_vigente',
    'criterio_shadow', 'criterio_vigente', 'observacao_auditavel',
]

COLUNAS_MULTIFONTE = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento',
    'valor_liquido_total_usado', 'valor_excesso_liquido', 'pagamento_totalmente_coberto_shadow',
    'qtd_lotes_usados_shadow', 'lote_principal_shadow', 'lotes_usados_shadow',
    'lote_vigente', 'mudou_lote_principal', 'delta_excesso_shadow_vs_vigente',
    'delta_cobertura_shadow_vs_vigente', 'criterio_shadow', 'criterio_vigente', 'observacao_auditavel',
]


def _bucket_valor(valor: float) -> str:
    valor = float(valor or 0.0)
    if valor < 250:
        return '0-250'
    if valor < 1000:
        return '250-1000'
    if valor < 5000:
        return '1000-5000'
    return '5000+'


def _classificar_motivo_sem_cobertura(qtd_lotes: int, valor_usado: float, valor_pag: float) -> str:
    qtd_lotes = int(qtd_lotes or 0)
    valor_usado = float(valor_usado or 0.0)
    valor_pag = float(valor_pag or 0.0)
    if qtd_lotes <= 0 and valor_usado <= 0.0:
        return 'sem_liquidez_disponivel_no_dia'
    if qtd_lotes > 1 and valor_usado < valor_pag:
        return 'multifonte_parcial_sem_cobertura'
    if qtd_lotes == 1 and valor_usado < valor_pag:
        return 'monofonte_parcial_sem_cobertura'
    return 'outra_insuficiencia_shadow'


def _montar_sem_cobertura(quadro: pd.DataFrame) -> pd.DataFrame:
    if len(quadro) == 0:
        return pd.DataFrame(columns=COLUNAS_SEM_COBERTURA)
    base = quadro.loc[~quadro['pagamento_totalmente_coberto_shadow'].fillna(False)].copy()
    if len(base) == 0:
        return pd.DataFrame(columns=COLUNAS_SEM_COBERTURA)
    primeira_data = min(base['data_pagamento']) if len(base) else None
    base['valor_descoberto'] = (base['valor_pagamento'].fillna(0.0) - base['valor_liquido_total_usado'].fillna(0.0)).clip(lower=0.0).round(2)
    base['motivo_sem_cobertura'] = base.apply(
        lambda r: _classificar_motivo_sem_cobertura(
            int(r.get('qtd_lotes_usados_shadow') or 0),
            float(r.get('valor_liquido_total_usado') or 0.0),
            float(r.get('valor_pagamento') or 0.0),
        ),
        axis=1,
    )
    base['fase_temporal_shadow'] = base['data_pagamento'].apply(
        lambda d: 'primeira_quebra_shadow' if primeira_data is not None and d == primeira_data else 'apos_primeira_quebra_shadow'
    )
    base['bucket_valor_pagamento'] = base['valor_pagamento'].apply(_bucket_valor)
    for col in COLUNAS_SEM_COBERTURA:
        if col not in base.columns:
            base[col] = None
    return base.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)


def _montar_multifonte(quadro: pd.DataFrame) -> pd.DataFrame:
    if len(quadro) == 0:
        return pd.DataFrame(columns=COLUNAS_MULTIFONTE)
    base = quadro.loc[quadro['qtd_lotes_usados_shadow'].fillna(0).astype(int) > 1].copy()
    if len(base) == 0:
        return pd.DataFrame(columns=COLUNAS_MULTIFONTE)
    for col in COLUNAS_MULTIFONTE:
        if col not in base.columns:
            base[col] = None
    return base.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)


def _montar_datas_criticas(quadro_sem_cobertura: pd.DataFrame, quadro_multifonte: pd.DataFrame) -> pd.DataFrame:
    if len(quadro_sem_cobertura) == 0:
        return pd.DataFrame(columns=['data_pagamento', 'qtd_pagamentos_sem_cobertura', 'valor_total_pagamentos_sem_cobertura', 'valor_total_descoberto', 'motivo_dominante', 'bucket_valor_dominante', 'ha_multifonte_no_dia'])
    base = quadro_sem_cobertura.copy()
    agg = base.groupby('data_pagamento', as_index=False).agg(
        qtd_pagamentos_sem_cobertura=('pagamento_id', 'count'),
        valor_total_pagamentos_sem_cobertura=('valor_pagamento', 'sum'),
        valor_total_descoberto=('valor_descoberto', 'sum'),
    )
    motivos = base.groupby(['data_pagamento', 'motivo_sem_cobertura']).size().reset_index(name='qtd').sort_values(['data_pagamento', 'qtd', 'motivo_sem_cobertura'], ascending=[True, False, True])
    buckets = base.groupby(['data_pagamento', 'bucket_valor_pagamento']).size().reset_index(name='qtd').sort_values(['data_pagamento', 'qtd', 'bucket_valor_pagamento'], ascending=[True, False, True])
    motivo_dom = motivos.groupby('data_pagamento', as_index=False).first()[['data_pagamento', 'motivo_sem_cobertura']].rename(columns={'motivo_sem_cobertura': 'motivo_dominante'})
    bucket_dom = buckets.groupby('data_pagamento', as_index=False).first()[['data_pagamento', 'bucket_valor_pagamento']].rename(columns={'bucket_valor_pagamento': 'bucket_valor_dominante'})
    out = agg.merge(motivo_dom, on='data_pagamento', how='left').merge(bucket_dom, on='data_pagamento', how='left')
    datas_multifonte = set(quadro_multifonte['data_pagamento'].tolist()) if len(quadro_multifonte) else set()
    out['ha_multifonte_no_dia'] = out['data_pagamento'].apply(lambda d: d in datas_multifonte)
    return out.sort_values('data_pagamento', kind='stable').reset_index(drop=True)


def carregar_auditoria_runner_futuro_shadow(
    benchmark_runner_futuro_shadow: PacoteBenchmarkRunnerFuturoShadow,
    *,
    data_referencia: date,
) -> PacoteAuditoriaRunnerFuturoShadow:
    quadro_comp = benchmark_runner_futuro_shadow.quadro_comparativo_vigente.copy()
    quadro_shadow = benchmark_runner_futuro_shadow.quadro_pagamentos_shadow.copy()
    base_auditoria = quadro_comp.merge(
        quadro_shadow[[
            'pagamento_id', 'valor_liquido_total_usado', 'valor_excesso_liquido', 'lotes_usados_shadow',
            'valor_lote_principal_shadow', 'imposto_pago_shadow', 'criterio_shadow', 'observacao_auditavel'
        ]],
        on='pagamento_id', how='left'
    )
    if 'criterio_shadow_x' in base_auditoria.columns or 'criterio_shadow_y' in base_auditoria.columns:
        base_auditoria['criterio_shadow'] = base_auditoria.get('criterio_shadow_x').where(base_auditoria.get('criterio_shadow_x').notna(), base_auditoria.get('criterio_shadow_y'))
        base_auditoria = base_auditoria.drop(columns=[c for c in ['criterio_shadow_x', 'criterio_shadow_y'] if c in base_auditoria.columns])
    if 'observacao_auditavel_x' in base_auditoria.columns or 'observacao_auditavel_y' in base_auditoria.columns:
        base_auditoria['observacao_auditavel'] = base_auditoria.get('observacao_auditavel_x').where(base_auditoria.get('observacao_auditavel_x').notna(), base_auditoria.get('observacao_auditavel_y'))
        base_auditoria = base_auditoria.drop(columns=[c for c in ['observacao_auditavel_x', 'observacao_auditavel_y'] if c in base_auditoria.columns])
    sem_cobertura = _montar_sem_cobertura(base_auditoria)
    multifonte = _montar_multifonte(base_auditoria)
    datas_criticas = _montar_datas_criticas(sem_cobertura, multifonte)

    primeira_data = sem_cobertura['data_pagamento'].min() if len(sem_cobertura) else None
    motivo_counts = sem_cobertura['motivo_sem_cobertura'].value_counts().to_dict() if len(sem_cobertura) else {}
    auditoria = {
        'resumo': {
            'data_referencia': data_referencia.isoformat(),
            'total_pagamentos_benchmark': int(benchmark_runner_futuro_shadow.auditoria['resumo'].get('total_pagamentos', 0)),
            'pagamentos_sem_cobertura_integral_shadow': int(len(sem_cobertura)),
            'datas_criticas_com_sem_cobertura': int(sem_cobertura['data_pagamento'].nunique()) if len(sem_cobertura) else 0,
            'primeira_data_sem_cobertura': primeira_data.isoformat() if hasattr(primeira_data, 'isoformat') else None,
            'valor_total_descoberto_shadow': round(float(sem_cobertura['valor_descoberto'].sum()), 2) if len(sem_cobertura) else 0.0,
            'motivos_sem_cobertura': motivo_counts,
            'pagamentos_multifonte_shadow': int(len(multifonte)),
            'multifonte_totalmente_cobertos': int(multifonte['pagamento_totalmente_coberto_shadow'].fillna(False).sum()) if len(multifonte) else 0,
            'multifonte_sem_cobertura': int((~multifonte['pagamento_totalmente_coberto_shadow'].fillna(False)).sum()) if len(multifonte) else 0,
            'recomendacao_auditoria': 'auditar_primeiro_sem_cobertura_integral_e_depois_multifonte',
            'justificativa_recomendacao': 'o runner shadow perde cobertura integral em massa; os 3 casos multifonte devem ser lidos como subbloco final, não como frente principal.',
        }
    }
    validacao = {'ok': True, 'erros': [], 'avisos': []}
    if len(multifonte) == 0:
        validacao['avisos'].append('sem_casos_multifonte_shadow')
    if len(sem_cobertura) == 0:
        validacao['avisos'].append('sem_casos_sem_cobertura_shadow')
    if len(sem_cobertura) and int(sem_cobertura['qtd_lotes_usados_shadow'].fillna(0).eq(0).sum()) == len(sem_cobertura):
        validacao['avisos'].append('sem_cobertura_predominantemente_por_ausencia_total_de_liquidez_no_dia')
    return PacoteAuditoriaRunnerFuturoShadow(
        quadro_sem_cobertura=sem_cobertura,
        quadro_multifonte=multifonte,
        quadro_datas_criticas=datas_criticas,
        auditoria=auditoria,
        validacao=validacao,
    )
