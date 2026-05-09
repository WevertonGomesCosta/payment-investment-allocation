from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DIR_C3 = RAIZ / 'saidas' / 'diagnostico' / 'v17_c3'
DIR_C4 = RAIZ / 'saidas' / 'diagnostico' / 'v17_c4'
DIR_C5 = RAIZ / 'saidas' / 'diagnostico' / 'v17_c5'
OUT = RAIZ / 'saidas' / 'diagnostico' / 'v17_c10'
OUT.mkdir(parents=True, exist_ok=True)

ARQ_C3_VALORES = DIR_C3 / 'v17_c3_comparativo_valores.csv'
ARQ_C4_CLASSES = DIR_C4 / 'v17_c4_classificacao_divergencias_valores.csv'
ARQ_C5_MATRIZ = DIR_C5 / 'v17_c5_matriz_causas_correcao.csv'

OUT_DET = OUT / 'v17_c10_divergencias_valores_detalhadas.csv'
OUT_RES_CLASSES = OUT / 'v17_c10_classes_divergencia_resumo.csv'
OUT_MATRIZ = OUT / 'v17_c10_matriz_decisao_proxima_correcao.csv'
OUT_RESUMO = OUT / 'v17_c10_resumo.csv'


def _run(script_rel: str) -> None:
    subprocess.run([sys.executable, str(RAIZ / script_rel)], check=True, cwd=RAIZ)


def _read(path: Path, cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns:
            df[c] = ''
    return df


def _num(v: Any) -> float:
    try:
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).replace('.', '').replace(',', '.'))
        except Exception:
            return 0.0


def _mapear_classe_tecnica(causa: str, campo: str, diff_abs: float) -> tuple[str, str, str, str, str]:
    c = (causa or '').lower()
    if 'arredond' in c or diff_abs <= 0.05:
        return (
            'diferenca_arredondamento', 'arredondamento', 'baixa', 'ajuste_de_arredondamento',
            'diferença de baixa magnitude compatível com política de arredondamento distinta',
        )
    if 'imposto' in c and ('zerou' in c or 'fallback' in c):
        return (
            'fallback_indevido_imposto', 'fallback', 'alta', 'ajuste_de_fonte_de_verdade',
            'indício de regra/fallback fiscal aplicada de forma diferente entre pacote e saída',
        )
    if 'bruto' in c or 'liquido' in c or campo in {'bruto', 'liquido'}:
        return (
            'recomputacao_vs_valor_decidido', 'ambos', 'alta', 'migracao_para_estado_temporal',
            'sintoma de recomputação em um lado versus leitura de valor já decidido no outro',
        )
    return (
        'fonte_verdade_indefinida', 'fonte_de_verdade_ainda_indefinida', 'media', 'ajuste_de_fonte_de_verdade',
        'não há evidência suficiente para atribuição unívoca sem rastrear quadro intermediário adicional',
    )


def main() -> int:
    # garante artefatos prévios
    if not ARQ_C3_VALORES.exists():
        _run('scripts/diagnostico/comparar_pacote_pre_saida_saida_canonica_v17_c3.py')
    if not ARQ_C4_CLASSES.exists():
        _run('scripts/diagnostico/classificar_divergencias_pacote_saida_v17_c4.py')
    if not ARQ_C5_MATRIZ.exists():
        try:
            _run('scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py')
        except Exception:
            pass

    df_c3 = _read(ARQ_C3_VALORES, ['chave_pagamento', 'campo', 'valor_pacote', 'valor_saida', 'diferenca', 'divergencia_material'])
    df_c4 = _read(ARQ_C4_CLASSES, ['chave_pagamento', 'campo', 'valor_pacote', 'valor_saida', 'diferenca', 'classe_causa_provavel'])

    df_base = df_c4.copy() if not df_c4.empty else df_c3[df_c3['divergencia_material'].astype(str).str.lower().isin({'true', '1'})].copy()
    if 'classe_causa_provavel' not in df_base.columns:
        df_base['classe_causa_provavel'] = 'sem_classificacao_v17_c4'

    detalhes = []
    for _, row in df_base.iterrows():
        diff = _num(row.get('diferenca'))
        cls_t, fonte, sev, cor, just = _mapear_classe_tecnica(str(row.get('classe_causa_provavel') or ''), str(row.get('campo') or ''), abs(diff))
        chave = str(row.get('chave_pagamento') or '')
        p = chave.split('|')
        detalhes.append({
            'chave_pagamento': chave,
            'data': p[0] if len(p) > 0 else '',
            'descricao': p[2] if len(p) > 2 else '',
            'campo': row.get('campo'),
            'valor_pacote': row.get('valor_pacote'),
            'valor_saida': row.get('valor_saida'),
            'diferenca': row.get('diferenca'),
            'classe_causa_v17_c4': row.get('classe_causa_provavel'),
            'classe_tecnica_v17_c10': cls_t,
            'fonte_provavel_divergencia': fonte,
            'severidade': sev,
            'corrigivel_agora': 'sim' if cor in {'ajuste_de_saida', 'ajuste_de_pacote', 'ajuste_de_arredondamento'} else 'nao',
            'tipo_correcao_recomendada': cor,
            'justificativa_tecnica': just,
        })

    df_det = pd.DataFrame(detalhes)
    if df_det.empty:
        df_det = pd.DataFrame(columns=[
            'chave_pagamento','data','descricao','campo','valor_pacote','valor_saida','diferenca','classe_causa_v17_c4',
            'classe_tecnica_v17_c10','fonte_provavel_divergencia','severidade','corrigivel_agora','tipo_correcao_recomendada','justificativa_tecnica'
        ])

    resumo_classes = []
    for (c4, c10), sub in df_det.groupby(['classe_causa_v17_c4', 'classe_tecnica_v17_c10'], dropna=False):
        diffs = sub['diferenca'].map(_num).abs()
        resumo_classes.append({
            'classe_causa_v17_c4': c4,
            'classe_tecnica_v17_c10': c10,
            'n_divergencias': int(len(sub)),
            'campos_afetados': ';'.join(sorted(set(sub['campo'].astype(str)))),
            'diferenca_abs_total': round(float(diffs.sum()), 2),
            'diferenca_abs_max': round(float(diffs.max() if len(diffs) else 0.0), 2),
            'fonte_provavel_divergencia': sub['fonte_provavel_divergencia'].mode().iloc[0] if len(sub) else '',
            'tipo_correcao_recomendada': sub['tipo_correcao_recomendada'].mode().iloc[0] if len(sub) else '',
            'bloquear_substituicao_saida': True,
            'justificativa_resumida': sub['justificativa_tecnica'].iloc[0] if len(sub) else '',
        })
    df_res_classes = pd.DataFrame(resumo_classes)

    df_matriz = pd.DataFrame([
        {
            'prioridade': 'P0',
            'classe_tecnica_v17_c10': c,
            'decisao': 'diagnosticar_sem_corrigir_agora',
            'escopo_correcao_futuro': r,
            'arquivos_provaveis': 'nucleo/saida_canonica.py;nucleo/pacote_orquestrado_pre_saida.py',
            'risco_de_regressao': 'alto',
            'validar_antes_de_corrigir': 'pagamentos, bruto/imposto/liquido, ranking, switching',
            'observacao': 'V17-C10 apenas classifica tecnicamente; nao aplicar mudanca funcional',
        }
        for c, r in sorted({(row['classe_tecnica_v17_c10'], row['tipo_correcao_recomendada']) for _, row in df_res_classes.iterrows()})
    ])

    total = int(len(df_det))
    classes_v17_c4_total = int(df_det['classe_causa_v17_c4'].nunique()) if total else 0
    classes_v17_c10_total = int(df_det['classe_tecnica_v17_c10'].nunique()) if total else 0

    resumo = pd.DataFrame([
        {'metrica': 'status_global_v17_c10', 'valor': 'ok_diagnostico'},
        {'metrica': 'divergencias_valores_total', 'valor': total},
        {'metrica': 'classes_v17_c4_total', 'valor': classes_v17_c4_total},
        {'metrica': 'classes_v17_c10_total', 'valor': classes_v17_c10_total},
        {'metrica': 'classes_corrigiveis_saida', 'valor': int((df_res_classes['tipo_correcao_recomendada'] == 'ajuste_de_saida').sum()) if not df_res_classes.empty else 0},
        {'metrica': 'classes_corrigiveis_pacote', 'valor': int((df_res_classes['tipo_correcao_recomendada'] == 'ajuste_de_pacote').sum()) if not df_res_classes.empty else 0},
        {'metrica': 'classes_dependentes_estado_temporal', 'valor': int((df_res_classes['tipo_correcao_recomendada'] == 'migracao_para_estado_temporal').sum()) if not df_res_classes.empty else 0},
        {'metrica': 'classes_arredondamento', 'valor': int((df_res_classes['tipo_correcao_recomendada'] == 'ajuste_de_arredondamento').sum()) if not df_res_classes.empty else 0},
        {'metrica': 'classes_fonte_verdade_indefinida', 'valor': int((df_res_classes['fonte_provavel_divergencia'] == 'fonte_de_verdade_ainda_indefinida').sum()) if not df_res_classes.empty else 0},
        {'metrica': 'decisao_consumo_saida_canonica', 'valor': 'nao_substituir_saida_canonica_ainda'},
        {'metrica': 'confirmacao_sem_alterar_motor', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_contrato_modelo', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_ranking', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_pagamentos', 'valor': True},
        {'metrica': 'confirmacao_sem_alterar_switching', 'valor': True},
    ])

    df_det.to_csv(OUT_DET, index=False)
    df_res_classes.to_csv(OUT_RES_CLASSES, index=False)
    df_matriz.to_csv(OUT_MATRIZ, index=False)
    resumo.to_csv(OUT_RESUMO, index=False)

    print('=== V17-C10 — AUDITORIA CLASSES DIVERGENCIAS DE VALORES ===')
    for _, row in resumo.iterrows():
        print(f"{row['metrica']}={row['valor']}")
    print(f'output_dir={OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
