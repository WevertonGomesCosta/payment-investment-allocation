from __future__ import annotations

from collections import Counter
from pathlib import Path
import pandas as pd

CSV_S2 = Path('saidas/diagnostico/auditoria_lacuna_integracao_temporal_v17_f0_s2.csv')
CSV_OUT = Path('saidas/diagnostico/auditoria_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.csv')
CSV_OUT_RES = Path('saidas/diagnostico/auditoria_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4_resumo_mensal.csv')
CLASSE = 'salario_sem_recebido_e_sem_aporte'


def _to_num(v):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return 0.0
        s = str(v).strip()
        if ',' in s and '.' in s:
            s = s.replace('.', '').replace(',', '.')
        elif ',' in s:
            s = s.replace(',', '.')
        return float(s)
    except Exception:
        return 0.0


def _norm_mes(v):
    s = str(v).strip()
    if len(s) >= 7 and s[4] == '-':
        return s[:7]
    dt = pd.to_datetime(v, errors='coerce')
    if pd.notna(dt):
        return dt.strftime('%Y-%m')
    return s


def _is_missing_salary_fields(row):
    return (
        not str(row.get('salario_id', '')).strip()
        or not str(row.get('descricao_salario', '')).strip()
        or _to_num(row.get('valor_liquido_salario')) <= 0
    )


def _classificar(row, min_mes_mat, max_mes_mat):
    mes = _norm_mes(row.get('mes'))
    s = _to_num(row.get('salario_mes_total'))
    r = _to_num(row.get('recebidos_mes_total'))
    a = _to_num(row.get('aportes_mes_total'))
    pf = _to_num(row.get('pagamentos_futuros_mes_total'))

    if _is_missing_salary_fields(row):
        return ('cadastro_incompleto', 'corrigir_cadastro', 'campo essencial de salário ausente/inválido', 'corrigir cadastro do salário na origem')

    if min_mes_mat and max_mes_mat and (mes < min_mes_mat or mes > max_mes_mat):
        return ('fora_do_horizonte_materializado', 'documentar_horizonte_ou_filtrar_previsao', 'mês fora do intervalo materializado de recebidos/aportes', 'documentar horizonte materializado e filtrar previsão fora de janela')

    if s > 0 and r == 0 and a == 0 and pf == 0:
        return ('salario_previsto_sem_materializacao', 'documentacao_semantica_ou_horizonte', 'salário no mês sem recebido/aporte e sem pagamentos futuros', 'avaliar se é previsão sem materialização ou recorte de horizonte')

    if s > 0 and r == 0 and a == 0 and pf > 0:
        return ('recebido_auditavel_ausente', 'auditar_integracao_recebidos', 'há pagamentos futuros no mês sem recebido/aporte auditável', 'auditar integração entre salário e recebidos auditáveis')

    if s > 0 and r > 0 and a == 0:
        return ('aporte_ausente', 'auditar_regra_aporte', 'recebido presente no mês sem aporte correspondente', 'auditar regra temporal de materialização para aporte')

    if s > r and abs(r - a) <= 0.01:
        return ('diferenca_semantica_escopo_salarios', 'reconciliacao_semantica', 'escopo de salários supera recebidos/aportes materializados', 'reconciliar escopo semântico entre previsto e materializado')

    if s > 0 and r == 0 and a == 0:
        return ('regra_temporal_auditar', 'auditar_regra_temporal', 'esperava-se materialização temporal sem evidência no mês', 'auditar regra temporal de transição salário->recebido->aporte')

    return ('indefinida', 'auditoria_manual', 'regras automáticas insuficientes para classificar a linha', 'revisão manual da linha com contexto de origem')


def main():
    print('=== AUDITORIA V17-F0-S.4 — AMOSTRAS CLASSE DOMINANTE ===')
    print('correcao_aplicada=V17-F0-S.4')

    if not CSV_S2.exists():
        print('csv_s2_lido=nao')
        print('status_geral=csv_s2_ausente')
        print('CSV S.2 ausente; execute primeiro python scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py')
        return

    s2 = pd.read_csv(CSV_S2)
    print('csv_s2_lido=sim')
    print(f'qtd_linhas_s2={len(s2)}')

    cls = s2.loc[s2.get('classe_lacuna', pd.Series([], dtype=str)) == CLASSE].copy()
    if cls.empty:
        print('qtd_linhas_classe_dominante=0')
        print('status_geral=classe_dominante_nao_encontrada')
        return

    s2['mes_norm'] = s2['mes'].map(_norm_mes)
    mat = s2.loc[(s2['recebidos_mes_total'].map(_to_num) > 0) | (s2['aportes_mes_total'].map(_to_num) > 0), 'mes_norm']
    min_mes_mat = mat.min() if not mat.empty else ''
    max_mes_mat = mat.max() if not mat.empty else ''

    cls['mes'] = cls['mes'].map(_norm_mes)
    hip = cls.apply(lambda r: _classificar(r, min_mes_mat, max_mes_mat), axis=1, result_type='expand')
    cls['hipotese_causal_s4'] = hip[0]
    cls['tipo_proxima_acao'] = hip[1]
    cls['evidencia_para_hipotese'] = hip[2]
    cls['recomendacao_s4'] = hip[3]
    cls['causa_provavel_s2'] = cls.get('causa_provavel', '')
    cls['severidade_diagnostica_s2'] = cls.get('severidade_diagnostica', '')
    cls['observacao_auditavel_s2'] = cls.get('observacao_auditavel', '')

    cols = [
        'mes','salario_id','data_recebimento_salario','descricao_salario','valor_bruto_salario','valor_liquido_salario',
        'salario_mes_total','qtd_salarios_mes','recebidos_mes_total','qtd_recebidos_mes','aportes_mes_total','qtd_aportes_mes',
        'pagamentos_historicos_mes_total','qtd_pagamentos_historicos_mes','pagamentos_futuros_mes_total','qtd_pagamentos_futuros_mes',
        'pagamentos_futuros_sem_cobertura_total','qtd_pagamentos_futuros_sem_cobertura','diferenca_salario_mes_vs_recebidos_mes',
        'diferenca_salario_mes_vs_aportes_mes','classe_lacuna','causa_provavel_s2','severidade_diagnostica_s2','observacao_auditavel_s2',
        'hipotese_causal_s4','evidencia_para_hipotese','tipo_proxima_acao','recomendacao_s4'
    ]
    for c in cols:
        if c not in cls.columns:
            cls[c] = ''

    det = cls[cols].copy()
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    det.to_csv(CSV_OUT, index=False)

    resumo = det.groupby('mes', dropna=False).agg(
        qtd_linhas_classe_dominante=('salario_id', 'count'),
        total_salarios_classe_dominante=('valor_liquido_salario', lambda s: sum(_to_num(v) for v in s)),
        salario_mes_total=('salario_mes_total', 'first'),
        recebidos_mes_total=('recebidos_mes_total', 'first'),
        aportes_mes_total=('aportes_mes_total', 'first'),
        pagamentos_futuros_mes_total=('pagamentos_futuros_mes_total', 'first'),
        qtd_pagamentos_futuros_mes=('qtd_pagamentos_futuros_mes', 'first'),
    ).reset_index()

    dom_hip = det.groupby('mes')['hipotese_causal_s4'].agg(lambda s: Counter(s).most_common(1)[0][0]).rename('hipotese_causal_dominante_mes')
    dom_acao = det.groupby('mes')['tipo_proxima_acao'].agg(lambda s: Counter(s).most_common(1)[0][0]).rename('tipo_proxima_acao_dominante_mes')
    dom_rec = det.groupby('mes')['recomendacao_s4'].agg(lambda s: Counter(s).most_common(1)[0][0]).rename('recomendacao_mes')
    resumo = resumo.merge(dom_hip, on='mes').merge(dom_acao, on='mes').merge(dom_rec, on='mes')
    resumo.to_csv(CSV_OUT_RES, index=False)

    cnt = Counter(det['hipotese_causal_s4'])
    hip_dom = cnt.most_common(1)[0][0]
    acao_dom = Counter(det.loc[det['hipotese_causal_s4'] == hip_dom, 'tipo_proxima_acao']).most_common(1)[0][0]

    print(f'qtd_linhas_classe_dominante={len(det)}')
    print(f'qtd_meses_classe_dominante={det["mes"].nunique()}')
    print(f'total_salarios_classe_dominante={sum(_to_num(v) for v in det["valor_liquido_salario"]):.2f}')
    print(f'hipotese_causal_dominante={hip_dom}')
    print(f'tipo_proxima_acao_dominante={acao_dom}')
    print(f'qtd_salario_previsto_sem_materializacao={cnt.get("salario_previsto_sem_materializacao",0)}')
    print(f'qtd_recebido_auditavel_ausente={cnt.get("recebido_auditavel_ausente",0)}')
    print(f'qtd_aporte_ausente={cnt.get("aporte_ausente",0)}')
    print(f'qtd_fora_do_horizonte_materializado={cnt.get("fora_do_horizonte_materializado",0)}')
    print(f'qtd_diferenca_semantica_escopo_salarios={cnt.get("diferenca_semantica_escopo_salarios",0)}')
    print(f'qtd_cadastro_incompleto={cnt.get("cadastro_incompleto",0)}')
    print(f'qtd_regra_temporal_auditar={cnt.get("regra_temporal_auditar",0)}')
    print(f'qtd_indefinida={cnt.get("indefinida",0)}')
    print('status_geral=classe_dominante_auditada')
    print(f'csv_detalhe={CSV_OUT}')
    print(f'csv_resumo_mensal={CSV_OUT_RES}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('=== AUDITORIA V17-F0-S.4 — AMOSTRAS CLASSE DOMINANTE ===')
        print('correcao_aplicada=V17-F0-S.4')
        print('status_geral=falha_auditoria_s4')
        print(f'erro={e}')
        raise
