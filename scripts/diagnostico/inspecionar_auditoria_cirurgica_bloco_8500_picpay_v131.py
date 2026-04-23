from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
JSON_FONTES = [
    Path('/mnt/data/grade_diaria_parametrizada_v130_consolidado.json'),
    REPO_ROOT / 'saidas' / 'operacional' / 'grade_diaria_parametrizada_v130_consolidado.json',
]


def _carregar_grade() -> dict:
    for caminho in JSON_FONTES:
        if caminho.exists():
            return json.loads(caminho.read_text(encoding='utf-8'))
    raise FileNotFoundError('grade_diaria_parametrizada_v130_consolidado.json não encontrada')


def main() -> int:
    bruto = _carregar_grade()
    df = pd.DataFrame(bruto['resultados'])
    bloco = df.loc[(df['data_solicitada'] >= '2026-05-13') & (df['data_solicitada'] <= '2026-05-20')].copy().reset_index(drop=True)
    vec = pd.DataFrame(bloco['vetor_lexicografico'].tolist(), columns=['viol', 'deficit', 'sem', 'perda', 'destruicao', 'liq', 'fiscal', 'oper'])
    basev = pd.DataFrame(bloco['vetor_baseline'].tolist(), columns=['b_viol', 'b_deficit', 'b_sem', 'b_perda', 'b_destruicao', 'b_liq', 'b_fiscal', 'b_oper'])
    bloco = pd.concat([bloco, vec, basev], axis=1)
    key_cols = ['viol', 'deficit', 'sem', 'perda', 'destruicao', 'liq', 'fiscal', 'oper', 'rotulo']
    vencedores = bloco.sort_values(key_cols).groupby('data_solicitada', as_index=False).first()
    print('Dias auditados:', bloco['data_solicitada'].nunique())
    print('Cenários auditados:', len(bloco))
    print('Vencedor lexicográfico único:', vencedores['rotulo'].nunique() == 1)
    if vencedores['rotulo'].nunique() == 1:
        print('Vencedor lexicográfico:', vencedores['rotulo'].iloc[0])
    print('Todos os vencedores pioram terminal vs baseline:', bool((vencedores['delta_perda_terminal_vs_baseline'] > 0).all()))
    print('Todos os vencedores pioram patrimônio proxy vs baseline:', bool((vencedores['delta_patrimonio_proxy_vs_baseline'] < 0).all()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
