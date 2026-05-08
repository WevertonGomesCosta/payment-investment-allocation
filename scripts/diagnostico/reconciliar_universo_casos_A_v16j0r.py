from __future__ import annotations
from pathlib import Path
import sys
import subprocess
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica

CSV_ATUAL = RAIZ / 'saidas/diagnostico/auditoria_casos_A_decisao_local_v16i.csv'
CSV_BASELINE = RAIZ / 'saidas/diagnostico/auditoria_casos_A_decisao_local_v16i_baseline_65.csv'


def _n(v):
    return str(v or '').strip().lower()


def _bool(v):
    tok = _n(v)
    return tok in {'1', '1.0', 'true', 'sim', 's', 'yes', 'y'} or v is True


def _git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=RAIZ, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f'erro: {e}'

def _git_ok(cmd: list[str]) -> bool:
    try:
        subprocess.check_output(cmd, cwd=RAIZ, text=True, stderr=subprocess.STDOUT)
        return True
    except Exception:
        return False


def _base_ref_disponivel_para_diff(base_ref: str) -> bool:
    commit_ok = _git_ok(['git', 'cat-file', '-e', f'{base_ref}^{{commit}}'])
    tree_ok = _git_ok(['git', 'cat-file', '-e', f'{base_ref}^{{tree}}'])
    print(f'base_ref_{base_ref}_commit_disponivel={str(commit_ok).lower()}')
    print(f'base_ref_{base_ref}_tree_disponivel={str(tree_ok).lower()}')
    if commit_ok and tree_ok:
        anc = _git_ok(['git', 'merge-base', '--is-ancestor', base_ref, 'HEAD'])
        print(f'base_ref_{base_ref}_is_ancestor_head={str(anc).lower()}')
    return commit_ok and tree_ok

def main() -> int:
    print('versao_alvo=V16-J.0-R')
    print('numero_de_versoes_usadas=1')
    print('fase=reconciliacao_diagnostica')

    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida = construir_saida_canonica(ctx)

    extrato = pd.DataFrame(saida.extrato_futuro)
    local = ctx.decisao_local_v1.quadro_decisao_local_v1.copy()
    fontes = ctx.fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()

    extrato['Despesa ID'] = extrato.get('Despesa ID', pd.Series(dtype='object')).astype(str)
    extrato['Status recomendação'] = extrato.get('Status recomendação', pd.Series(dtype='object')).astype(str).str.lower()
    local['pagamento_id'] = local.get('pagamento_id', pd.Series(dtype='object')).astype(str)
    fontes['pagamento_id'] = fontes.get('pagamento_id', pd.Series(dtype='object')).astype(str)

    etapa1 = extrato.copy()
    etapa2 = etapa1[etapa1['Status recomendação'].eq('sem_saldo_temporal_auditavel')].copy()
    etapa3 = etapa2.merge(local, left_on='Despesa ID', right_on='pagamento_id', how='left')
    etapa4 = etapa3[etapa3['tipo_fonte_escolhida'].astype(str).str.lower().eq('lote_resgatavel')].copy()

    ids4 = set(etapa4['Despesa ID'].astype(str))
    elegiveis, suficientes = set(), set()
    for pid in ids4:
        f = fontes[fontes['pagamento_id'].astype(str) == str(pid)].copy()
        r = f[(f.get('tipo_fonte', '').astype(str).str.lower() == 'recebido_disponivel') & (f.get('elegivel_na_data_pagamento', False).apply(_bool))].copy()
        if len(r):
            elegiveis.add(str(pid))
            maxv = pd.to_numeric(r.get('valor_liquido_disponivel', pd.Series(dtype='float')), errors='coerce').max()
            val = pd.to_numeric(etapa4.loc[etapa4['Despesa ID'].astype(str) == str(pid), 'valor_pagamento'], errors='coerce')
            vp = float(val.iloc[0]) if len(val) else float(pd.to_numeric(etapa4.loc[etapa4['Despesa ID'].astype(str) == str(pid), 'Valor'], errors='coerce').iloc[0])
            if pd.notna(maxv) and maxv + 0.01 >= vp:
                suficientes.add(str(pid))

    print(f'total_extrato_futuro={len(etapa1)}')
    print(f'total_status_sem_saldo_temporal_auditavel={len(etapa2)}')
    print(f'total_pos_merge_decisao_local={len(etapa3)}')
    print(f'total_tipo_fonte_lote_resgatavel={len(etapa4)}')
    print(f'total_com_recebido_disponivel_elegivel={len(elegiveis)}')
    print(f'total_com_recebido_disponivel_suficiente={len(suficientes)}')

    atual_ids = set()
    if CSV_ATUAL.exists():
        df_atual = pd.read_csv(CSV_ATUAL)
        if 'pagamento_id' in df_atual.columns:
            atual_ids = set(df_atual['pagamento_id'].astype(str))
        print(f'csv_atual_encontrado={CSV_ATUAL}')
        print(f'csv_atual_total_ids={len(atual_ids)}')
    else:
        atual_ids = ids4
        print('csv_atual_nao_encontrado=true')

    if CSV_BASELINE.exists():
        df_b = pd.read_csv(CSV_BASELINE)
        base_ids = set(df_b.get('pagamento_id', pd.Series(dtype='object')).astype(str))
        removidos = sorted(base_ids - atual_ids)
        print(f'csv_baseline_encontrado={CSV_BASELINE}')
        print(f'baseline_total_ids={len(base_ids)}')
        print(f'removidos_total={len(removidos)}')
        print(f'removidos_amostra={removidos[:20]}')
    else:
        print('csv_baseline_65_nao_encontrado=true')
        print('ids_atuais_etapa_lote_resgatavel_amostra=')
        print(sorted(list(ids4))[:20])

    base_ref = '01cd2fa'
    if _base_ref_disponivel_para_diff(base_ref):
        diff_script = _git(['git', 'diff', '--name-status', base_ref, 'HEAD', '--', 'scripts/diagnostico/auditar_casos_A_decisao_local_v16i.py'])
        diff_nucleo = _git(['git', 'diff', '--name-status', base_ref, 'HEAD', '--', 'nucleo/'])
        print('comparacao_script_v16i_entre_01cd2fa_e_head:')
        print(diff_script if diff_script else '(sem alteracoes)')
        print('modulos_funcionais_alterados_no_intervalo:')
        print(diff_nucleo if diff_nucleo else '(sem alteracoes)')
        print(f'sem_alteracao_no_script_v16i_no_intervalo={str(not bool(diff_script)).lower()}')
        print(f'sem_alteracao_em_modulos_funcionais_no_intervalo={str(not bool(diff_nucleo)).lower()}')
    else:
        print('base_ref_01cd2fa_sem_tree_disponivel=true')
        print('comparacao_git_diff_nao_executada=true')
        print('recomendacao_git=fetch_completo_ou_baseline_csv_para_comparar_ids')
        print('ultimos_commits_para_contexto=')
        print(_git(['git', 'log', '--oneline', '-n', '15']))

    print('recomendacao_objetiva=se_modulos_funcionais_alteraram_no_intervalo_entao_queda_pode_ser_legitima_por_contexto; se_nao_alteraram_e_filtro_cair_no_tipo_fonte_lote_resgatavel_investigar_regressao_diagnostica_no_script')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
