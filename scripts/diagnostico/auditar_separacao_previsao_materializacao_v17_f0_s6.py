from __future__ import annotations

from collections import Counter
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CSV_S2 = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_lacuna_integracao_temporal_v17_f0_s2.csv'
CSV_S4 = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.csv'
CSV_OUT = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_separacao_previsao_materializacao_v17_f0_s6.csv'
CSV_OUT_RES = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_separacao_previsao_materializacao_v17_f0_s6_resumo_mensal.csv'

LACUNAS_REAIS_S2 = {
    'salario_sem_recebido_e_sem_aporte',
    'salario_sem_recebido_auditavel',
    'salario_sem_aporte',
    'salario_com_recebido_mas_sem_aporte',
    'salario_com_aporte_mas_sem_recebido',
}


def _to_num(v):
    try:
        if v is None or pd.isna(v):
            return 0.0
        return float(v)
    except Exception:
        return 0.0


def _norm_mes(v):
    s = str(v).strip()
    if len(s) >= 7 and s[4] == '-':
        return s[:7]
    dt = pd.to_datetime(v, errors='coerce')
    if pd.notna(dt):
        return dt.strftime('%Y-%m')
    return ''


def _norm_str(v):
    try:
        if v is None or pd.isna(v):
            return ''
    except Exception:
        pass
    s = str(v).strip()
    if s.lower() in {'', 'nan', 'na', 'none', 'null', 'nat', '<na>'}:
        return ''
    return s


def _classificar(row, min_mes_mat, max_mes_mat):
    classe_s2 = _norm_str(row.get('classe_lacuna_s2', ''))
    hip_s4 = _norm_str(row.get('hipotese_causal_s4', ''))
    mes = _norm_mes(row.get('mes'))
    r = _to_num(row.get('recebidos_mes_total'))
    a = _to_num(row.get('aportes_mes_total'))

    fora_horizonte = bool(min_mes_mat and max_mes_mat and mes and (mes < min_mes_mat or mes > max_mes_mat))

    if hip_s4 == 'fora_do_horizonte_materializado':
        return {
            'classe_politica_s6': 'salario_previsto_futuro_nao_materializado',
            'camada_temporal_s6': 'previsao_futura',
            'entra_lacuna_operacional_materializada': False,
            'entra_previsao_futura_nao_materializada': True,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': False,
            'requer_documentacao_horizonte': True,
            'evidencia_s6': 'hipotese_s4_fora_do_horizonte_materializado',
            'recomendacao_s6': 'documentar_horizonte_ou_filtrar_previsao',
        }

    if classe_s2 == 'uso_pre_aplicacao_no_mes_sem_vinculo_linha':
        return {
            'classe_politica_s6': 'uso_pre_aplicacao_no_mes_sem_vinculo_linha',
            'camada_temporal_s6': 'evidencia_temporal_sem_vinculo',
            'entra_lacuna_operacional_materializada': True,
            'entra_previsao_futura_nao_materializada': False,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': True,
            'requer_documentacao_horizonte': False,
            'evidencia_s6': 'classe_s2_pre_aplicacao_sem_vinculo',
            'recomendacao_s6': 'auditar_vinculo_recebido_salario_lote',
        }

    if classe_s2 in LACUNAS_REAIS_S2 and not fora_horizonte:
        return {
            'classe_politica_s6': 'lacuna_real_de_integracao',
            'camada_temporal_s6': 'lacuna_operacional',
            'entra_lacuna_operacional_materializada': True,
            'entra_previsao_futura_nao_materializada': False,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': True,
            'requer_documentacao_horizonte': False,
            'evidencia_s6': 'classe_s2_lacuna_real_dentro_horizonte',
            'recomendacao_s6': 'auditar_integracao_salario_recebido_aporte',
        }

    if a > 0:
        return {
            'classe_politica_s6': 'salario_materializado_em_aporte',
            'camada_temporal_s6': 'materializado_aporte',
            'entra_lacuna_operacional_materializada': False,
            'entra_previsao_futura_nao_materializada': False,
            'entra_fonte_disponivel_para_pagamento': True,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': False,
            'requer_documentacao_horizonte': False,
            'evidencia_s6': 'aportes_mes_total_maior_que_zero',
            'recomendacao_s6': 'manter_monitoramento_materializacao_aporte',
        }

    if r > 0:
        return {
            'classe_politica_s6': 'salario_materializado_em_recebido',
            'camada_temporal_s6': 'materializado_recebido',
            'entra_lacuna_operacional_materializada': False,
            'entra_previsao_futura_nao_materializada': False,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': False,
            'requer_documentacao_horizonte': False,
            'evidencia_s6': 'recebidos_mes_total_maior_que_zero',
            'recomendacao_s6': 'validar_transicao_recebido_para_aporte',
        }

    if classe_s2 == 'diferenca_semantica_salarios_vs_inventario':
        return {
            'classe_politica_s6': 'diferenca_semantica_escopo_salarios',
            'camada_temporal_s6': 'semantica',
            'entra_lacuna_operacional_materializada': False,
            'entra_previsao_futura_nao_materializada': False,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': False,
            'requer_documentacao_horizonte': True,
            'evidencia_s6': 'classe_s2_diferenca_semantica_salarios_vs_inventario',
            'recomendacao_s6': 'reconciliacao_semantica_e_horizonte',
        }

    if fora_horizonte and not hip_s4:
        return {
            'classe_politica_s6': 'fora_do_escopo_operacional_materializado',
            'camada_temporal_s6': 'previsao_futura',
            'entra_lacuna_operacional_materializada': False,
            'entra_previsao_futura_nao_materializada': True,
            'entra_fonte_disponivel_para_pagamento': False,
            'requer_correcao_motor': False,
            'requer_correcao_integracao': False,
            'requer_documentacao_horizonte': True,
            'evidencia_s6': 'fora_horizonte_sem_hipotese_s4',
            'recomendacao_s6': 'documentar_horizonte_materializado',
        }

    return {
        'classe_politica_s6': 'indefinida',
        'camada_temporal_s6': 'indefinida',
        'entra_lacuna_operacional_materializada': False,
        'entra_previsao_futura_nao_materializada': False,
        'entra_fonte_disponivel_para_pagamento': False,
        'requer_correcao_motor': False,
        'requer_correcao_integracao': False,
        'requer_documentacao_horizonte': False,
        'evidencia_s6': 'regras_automaticas_insuficientes',
        'recomendacao_s6': 'auditoria_manual',
    }


def main():
    print('=== AUDITORIA V17-F0-S.6 — SEPARAÇÃO PREVISÃO × MATERIALIZAÇÃO ===')
    print('correcao_aplicada=V17-F0-S.6.4')

    if not CSV_S2.exists():
        print('csv_s2_lido=nao')
        print('csv_s4_lido=nao')
        print('status_geral=csv_s2_ausente')
        print('CSV S.2 ausente; execute primeiro python scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py')
        return
    if not CSV_S4.exists():
        print('csv_s2_lido=sim')
        print('csv_s4_lido=nao')
        print('status_geral=csv_s4_ausente')
        print('CSV S.4 ausente; execute primeiro python scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py')
        return

    s2 = pd.read_csv(CSV_S2)
    s4 = pd.read_csv(CSV_S4)
    print('csv_s2_lido=sim')
    print('csv_s4_lido=sim')
    print(f'qtd_linhas_s2={len(s2)}')
    print(f'qtd_linhas_s4={len(s4)}')

    chaves = ['mes', 'salario_id', 'data_recebimento_salario', 'valor_liquido_salario', 'classe_lacuna']
    s2b = s2.copy().rename(columns={'classe_lacuna': 'classe_lacuna_s2', 'causa_provavel': 'causa_provavel_s2'})
    s4b = s4[[*chaves, 'hipotese_causal_s4', 'tipo_proxima_acao', 'evidencia_para_hipotese', 'recomendacao_s4']].copy()
    s4b = s4b.rename(columns={'tipo_proxima_acao': 'tipo_proxima_acao_s4'})

    det = s2b.merge(
        s4b,
        how='left',
        left_on=['mes', 'salario_id', 'data_recebimento_salario', 'valor_liquido_salario', 'classe_lacuna_s2'],
        right_on=chaves,
    )
    for c in chaves:
        if c in det.columns and c not in s2b.columns:
            det = det.drop(columns=[c])

    det['mes'] = det['mes'].map(_norm_mes)
    mat = det.loc[(det['recebidos_mes_total'].map(_to_num) > 0) | (det['aportes_mes_total'].map(_to_num) > 0), 'mes']
    min_mes_mat = mat.min() if not mat.empty else ''
    max_mes_mat = mat.max() if not mat.empty else ''

    regra = det.apply(lambda r: _classificar(r, min_mes_mat, max_mes_mat), axis=1, result_type='expand')
    for c in regra.columns:
        det[c] = regra[c]

    colunas = [
        'mes', 'salario_id', 'data_recebimento_salario', 'descricao_salario', 'valor_liquido_salario',
        'salario_mes_total', 'recebidos_mes_total', 'aportes_mes_total', 'pagamentos_futuros_mes_total',
        'qtd_pagamentos_futuros_mes', 'pagamentos_futuros_sem_cobertura_total', 'qtd_pagamentos_futuros_sem_cobertura',
        'classe_lacuna_s2', 'causa_provavel_s2', 'hipotese_causal_s4', 'tipo_proxima_acao_s4',
        'classe_politica_s6', 'camada_temporal_s6', 'entra_lacuna_operacional_materializada',
        'entra_previsao_futura_nao_materializada', 'entra_fonte_disponivel_para_pagamento', 'requer_correcao_motor',
        'requer_correcao_integracao', 'requer_documentacao_horizonte', 'evidencia_s6', 'recomendacao_s6',
    ]
    for c in colunas:
        if c not in det.columns:
            det[c] = ''
    det = det[colunas].copy()

    det['valor_liq_num'] = det['valor_liquido_salario'].map(_to_num)

    resumo = det.groupby('mes', dropna=False).agg(
        qtd_linhas=('salario_id', 'count'),
        total_salarios_mes=('valor_liq_num', 'sum'),
        total_salarios_previstos_nao_materializados=('valor_liq_num', lambda s: s[det.loc[s.index, 'classe_politica_s6'] == 'salario_previsto_futuro_nao_materializado'].sum()),
        total_lacuna_operacional_materializada=('valor_liq_num', lambda s: s[det.loc[s.index, 'entra_lacuna_operacional_materializada'].astype(bool)].sum()),
        total_materializado_recebido=('valor_liq_num', lambda s: s[det.loc[s.index, 'classe_politica_s6'] == 'salario_materializado_em_recebido'].sum()),
        total_materializado_aporte=('valor_liq_num', lambda s: s[det.loc[s.index, 'classe_politica_s6'] == 'salario_materializado_em_aporte'].sum()),
        qtd_salario_previsto_futuro_nao_materializado=('classe_politica_s6', lambda s: int((s == 'salario_previsto_futuro_nao_materializado').sum())),
        qtd_lacuna_real_de_integracao=('classe_politica_s6', lambda s: int((s == 'lacuna_real_de_integracao').sum())),
        qtd_uso_pre_aplicacao_no_mes_sem_vinculo_linha=('classe_politica_s6', lambda s: int((s == 'uso_pre_aplicacao_no_mes_sem_vinculo_linha').sum())),
        qtd_materializado_recebido=('classe_politica_s6', lambda s: int((s == 'salario_materializado_em_recebido').sum())),
        qtd_materializado_aporte=('classe_politica_s6', lambda s: int((s == 'salario_materializado_em_aporte').sum())),
    ).reset_index()
    resumo['classe_politica_dominante_mes'] = det.groupby('mes')['classe_politica_s6'].agg(lambda s: Counter(s).most_common(1)[0][0]).values
    resumo['camada_temporal_dominante_mes'] = det.groupby('mes')['camada_temporal_s6'].agg(lambda s: Counter(s).most_common(1)[0][0]).values
    resumo['recomendacao_mes'] = det.groupby('mes')['recomendacao_s6'].agg(lambda s: Counter(s).most_common(1)[0][0]).values

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    det.drop(columns=['valor_liq_num']).to_csv(CSV_OUT, index=False)
    resumo.to_csv(CSV_OUT_RES, index=False)

    cnt_cls = Counter(det['classe_politica_s6'])
    cnt_cam = Counter(det['camada_temporal_s6'])
    total_sal = det['valor_liq_num'].sum()
    total_prev = det.loc[det['entra_previsao_futura_nao_materializada'], 'valor_liq_num'].sum()
    total_lac = det.loc[det['entra_lacuna_operacional_materializada'], 'valor_liq_num'].sum()

    print(f'qtd_linhas_s6={len(det)}')
    print(f'qtd_meses_s6={det["mes"].nunique()}')
    print(f'horizonte_materializado_inicio={min_mes_mat}')
    print(f'horizonte_materializado_fim={max_mes_mat}')
    print(f'total_salarios_s6={total_sal:.2f}')
    print(f'total_previsao_futura_nao_materializada={total_prev:.2f}')
    print(f'total_lacuna_operacional_materializada={total_lac:.2f}')
    print(f'qtd_salario_previsto_futuro_nao_materializado={cnt_cls.get("salario_previsto_futuro_nao_materializado",0)}')
    print(f'qtd_lacuna_real_de_integracao={cnt_cls.get("lacuna_real_de_integracao",0)}')
    print(f'qtd_uso_pre_aplicacao_no_mes_sem_vinculo_linha={cnt_cls.get("uso_pre_aplicacao_no_mes_sem_vinculo_linha",0)}')
    print(f'qtd_materializado_recebido={cnt_cls.get("salario_materializado_em_recebido",0)}')
    print(f'qtd_materializado_aporte={cnt_cls.get("salario_materializado_em_aporte",0)}')
    print(f'qtd_indefinida={cnt_cls.get("indefinida",0)}')
    print(f'classe_politica_dominante={cnt_cls.most_common(1)[0][0] if cnt_cls else "indefinida"}')
    print(f'camada_temporal_dominante={cnt_cam.most_common(1)[0][0] if cnt_cam else "indefinida"}')
    print('status_geral=separacao_previsao_materializacao_concluida')
    print(f'csv_detalhe={CSV_OUT}')
    print(f'csv_resumo_mensal={CSV_OUT_RES}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('=== AUDITORIA V17-F0-S.6 — SEPARAÇÃO PREVISÃO × MATERIALIZAÇÃO ===')
        print('correcao_aplicada=V17-F0-S.6.4')
        print('status_geral=falha_separacao_s6')
        print(f'erro={e}')
        raise
