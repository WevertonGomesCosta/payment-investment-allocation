from __future__ import annotations
from pathlib import Path
import sys
import subprocess
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica

OUT_DIR = RAIZ / 'saidas' / 'diagnostico'
OUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_PRINCIPAL = OUT_DIR / 'auditoria_casos_A_decisao_local_v16i.csv'
CSV_RESUMO = OUT_DIR / 'auditoria_casos_A_decisao_local_v16i_resumo.csv'

CONTRATO = RAIZ / 'relatorios' / 'principais' / 'CONTRATO_OPERACIONAL_PROJETO.md'
MODELO = RAIZ / 'relatorios' / 'principais' / 'MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md'

CAUSAS = {
    'sem_recebido_disponivel_elegivel',
    'recebido_disponivel_insuficiente',
    'recebido_disponivel_bloqueado_temporalmente',
    'recebido_disponivel_existe_mas_proxy_prefere_lote',
    'recebido_disponivel_existe_mas_ordem_local_prefere_lote',
    'lote_escolhido_sem_saldo_temporal_cumulativo',
    'fonte_recebido_nao_materializada_para_pagamento',
    'inconclusivo_exige_inspecao_manual',
}

CLASSES = {
    'decisao_local',
    'materializacao_recebidos',
    'saldo_temporal_cumulativo',
    'contrato_atual_sem_correcao',
    'inspecao_manual',
}

COLUNAS_SAIDA = [
    'pagamento_id',
    'data_pagamento',
    'descricao_pagamento',
    'valor_pagamento',
    'tipo_fonte_escolhida_decisao_local',
    'fonte_escolhida_id',
    'lote_id_escolhido',
    'saldo_antes_temporal_lote',
    'valor_disponivel_escolhido_local',
    'custo_economico_proxy_lote',
    'status_temporal_auditoria',
    'pagamento_totalmente_coberto_temporal',
    'requer_reescolha_dinamica_temporal',
    'lote_sem_saldo_derivado_auditoria_temporal',
    'existe_recebido_disponivel_elegivel',
    'qtd_recebidos_disponiveis_elegiveis',
    'maior_valor_liquido_recebido_disponivel',
    'recebido_cobre_pagamento',
    'melhor_recebido_id',
    'status_recebido',
    'destino_potencial_recebido',
    'data_recebimento',
    'data_aplicacao',
    'motivo_recebido_nao_escolhido',
    'diagnostico_causa_provavel',
    'classe_correcao_futura',
]


def _n(v):
    return str(v or '').strip().lower()


def _txt(v):
    return str(v or '').strip()


def _bool(v):
    return _n(v) in {'1', 'true', 'sim', 's', 'yes', 'y', 'elegivel'} or v is True


def _float(v, padrao=0.0):
    try:
        if pd.isna(v):
            return padrao
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        return padrao


def _valor_linha(row, candidatos, padrao=None):
    for col in candidatos:
        if hasattr(row, 'get') and col in row.index:
            valor = row.get(col)
            if valor not in (None, ''):
                try:
                    if pd.isna(valor):
                        continue
                except Exception:
                    pass
                return valor
    return padrao


def _head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RAIZ, text=True).strip()


def _commit_v16h_ok():
    try:
        msg = subprocess.check_output(
            ['git', 'show', '-s', '--format=%s', '15320e4e712e461c7b7a0d58d91ffd5484c65492'],
            cwd=RAIZ,
            text=True,
        ).strip()
        return msg == 'Restrict received-source handling to local payment decisions'
    except Exception:
        return False


def _ler_referenciais():
    for caminho in (CONTRATO, MODELO):
        if not caminho.exists():
            raise FileNotFoundError(f'referencial_obrigatorio_nao_encontrado: {caminho}')
        caminho.read_text(encoding='utf-8')


def _serie_bool(df, coluna):
    if coluna not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    return df[coluna].apply(_bool)


def _auditoria_temporal_por_pagamento(q_aud):
    if not isinstance(q_aud, pd.DataFrame) or q_aud.empty or 'pagamento_id' not in q_aud.columns:
        return {}
    ordenacao = [c for c in ['data_pagamento', 'pagamento_id'] if c in q_aud.columns]
    q = q_aud.copy()
    q['pagamento_id'] = q['pagamento_id'].astype(str)
    if ordenacao:
        q = q.sort_values(ordenacao, kind='stable')
    return {str(r.get('pagamento_id') or ''): r for _, r in q.iterrows() if str(r.get('pagamento_id') or '').strip()}


def _derivar_lote_sem_saldo(row_evento, aud_row):
    if aud_row is None:
        # Fallback apenas observacional: o caso A foi identificado no extrato canônico
        # como sem_saldo_temporal_auditavel. Quando a auditoria temporal detalhada
        # não trouxer a linha, não forçar a causa; deixar a taxonomia seguir.
        return False, '', False, False

    status_temporal = _txt(aud_row.get('status_temporal'))
    pagamento_totalmente_coberto = _bool(aud_row.get('pagamento_totalmente_coberto_temporal'))
    requer_reescolha = _bool(aud_row.get('requer_reescolha_dinamica'))

    status_norm = _n(status_temporal)
    lote_sem_saldo = bool(
        requer_reescolha
        or not pagamento_totalmente_coberto
        or 'quebra' in status_norm
        or 'sem_saldo' in status_norm
        or 'saldo_temporal_insuficiente' in status_norm
    )

    return lote_sem_saldo, status_temporal, pagamento_totalmente_coberto, requer_reescolha


def _classificar_causa(
    *,
    lote_sem_saldo,
    existe_eleg,
    receb_all,
    q_rec,
    cobre,
    proxy_lote,
    proxy_rec,
):
    if lote_sem_saldo:
        return (
            'lote_escolhido_sem_saldo_temporal_cumulativo',
            'saldo_temporal_cumulativo',
            'auditoria_temporal_indica_lote_sem_saldo_cumulativo',
        )

    if not existe_eleg and len(receb_all) > 0:
        return (
            'recebido_disponivel_bloqueado_temporalmente',
            'materializacao_recebidos',
            'recebidos_existem_mas_ineligiveis_na_data',
        )

    if not existe_eleg and len(receb_all) == 0:
        if len(q_rec) > 0:
            return (
                'fonte_recebido_nao_materializada_para_pagamento',
                'materializacao_recebidos',
                'recebiveis_auditaveis_nao_aparecem_nas_fontes_do_pagamento',
            )
        return (
            'sem_recebido_disponivel_elegivel',
            'contrato_atual_sem_correcao',
            'sem_fontes_recebido_no_pagamento',
        )

    if existe_eleg and not cobre:
        return (
            'recebido_disponivel_insuficiente',
            'contrato_atual_sem_correcao',
            'maior_recebido_nao_cobre_pagamento',
        )

    if existe_eleg and cobre and proxy_rec is not None and proxy_lote <= proxy_rec:
        return (
            'recebido_disponivel_existe_mas_proxy_prefere_lote',
            'decisao_local',
            'proxy_lote_melhor_ou_igual',
        )

    if existe_eleg and cobre:
        return (
            'recebido_disponivel_existe_mas_ordem_local_prefere_lote',
            'decisao_local',
            'ordem_local_priorizou_lote',
        )

    return (
        'inconclusivo_exige_inspecao_manual',
        'inspecao_manual',
        'sem_evidencia_conclusiva',
    )


def main() -> int:
    head_inicial = _head()
    commit_ok = _commit_v16h_ok()
    _ler_referenciais()

    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )

    q_local = ctx.decisao_local_v1.quadro_decisao_local_v1.copy()
    q_fontes = ctx.fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    q_rec = ctx.recebidos_auditaveis.quadro_recebidos_auditaveis.copy()
    q_aud = ctx.auditoria_temporal_decisao_local.quadro_auditoria_temporal.copy()
    saida = construir_saida_canonica(ctx)
    q_extrato = pd.DataFrame(saida.extrato_futuro)

    q_local['pagamento_id'] = q_local['pagamento_id'].astype(str)
    q_fontes['pagamento_id'] = q_fontes['pagamento_id'].astype(str)
    q_aud['pagamento_id'] = q_aud['pagamento_id'].astype(str)
    q_rec['recebido_id'] = q_rec['recebido_id'].astype(str)

    aud_por_pagamento = _auditoria_temporal_por_pagamento(q_aud)

    q_extrato['Despesa ID'] = q_extrato['Despesa ID'].astype(str)
    q_extrato['Status recomendação'] = q_extrato['Status recomendação'].astype(str).str.lower()
    casos_a = q_extrato[q_extrato['Status recomendação'].eq('sem_saldo_temporal_auditavel')].copy()
    casos_a = casos_a.merge(
        q_local,
        left_on='Despesa ID',
        right_on='pagamento_id',
        how='left',
        suffixes=('_ext', '_local'),
    )
    casos_a = casos_a[casos_a['tipo_fonte_escolhida'].astype(str).str.lower().eq('lote_resgatavel')].copy()

    rows = []
    for _, r in casos_a.iterrows():
        pid = str(r['Despesa ID'])
        vp = _float(r.get('valor_pagamento') or r.get('Valor') or 0.0)

        fontes_pid = q_fontes[q_fontes['pagamento_id'] == pid].copy()
        tipo_fonte_norm = fontes_pid['tipo_fonte'].astype(str).str.lower()
        receb_all = fontes_pid[tipo_fonte_norm == 'recebido_disponivel'].copy()
        receb_eleg = receb_all[_serie_bool(receb_all, 'elegivel_na_data_pagamento')].copy()

        qtd_eleg = int(len(receb_eleg))
        existe_eleg = qtd_eleg > 0
        maior_val = (
            _float(pd.to_numeric(receb_eleg['valor_liquido_disponivel'], errors='coerce').max())
            if existe_eleg and 'valor_liquido_disponivel' in receb_eleg.columns
            else 0.0
        )
        cobre = maior_val + 0.01 >= vp if existe_eleg else False

        melhor = (
            receb_eleg.sort_values('valor_liquido_disponivel', ascending=False).head(1)
            if existe_eleg and 'valor_liquido_disponivel' in receb_eleg.columns
            else pd.DataFrame()
        )
        melhor_id = str(melhor['recebido_id'].iloc[0]) if len(melhor) and 'recebido_id' in melhor.columns else ''

        rec_row = q_rec[q_rec['recebido_id'] == melhor_id].head(1)
        status_receb = rec_row['status_recebido'].iloc[0] if len(rec_row) and 'status_recebido' in rec_row.columns else ''
        dest_pot = rec_row['destino_potencial'].iloc[0] if len(rec_row) and 'destino_potencial' in rec_row.columns else ''
        data_rec = rec_row['data_recebimento'].iloc[0] if len(rec_row) and 'data_recebimento' in rec_row.columns else ''
        data_apl = rec_row['data_aplicacao'].iloc[0] if len(rec_row) and 'data_aplicacao' in rec_row.columns else ''

        aud_row = aud_por_pagamento.get(pid)
        lote_sem_saldo, status_temporal, temporal_coberto, requer_reescolha = _derivar_lote_sem_saldo(r, aud_row)

        saldo_antes_temporal = (
            _float(aud_row.get('saldo_antes_temporal'))
            if aud_row is not None and 'saldo_antes_temporal' in aud_row.index
            else _float(r.get('Saldo temp. ant.'), padrao=0.0)
        )

        proxy_lote = _float(_valor_linha(r, ['custo_economico_proxy', 'custo_economico_proxy_local'], 0.0))
        proxy_rec = (
            _float(pd.to_numeric(melhor.get('custo_economico_proxy'), errors='coerce').iloc[0], padrao=None)
            if len(melhor) and 'custo_economico_proxy' in melhor.columns
            else None
        )

        causa, classe, motivo = _classificar_causa(
            lote_sem_saldo=lote_sem_saldo,
            existe_eleg=existe_eleg,
            receb_all=receb_all,
            q_rec=q_rec,
            cobre=cobre,
            proxy_lote=proxy_lote,
            proxy_rec=proxy_rec,
        )

        rows.append({
            'pagamento_id': pid,
            'data_pagamento': r.get('data_pagamento') or r.get('Data'),
            'descricao_pagamento': r.get('descricao_pagamento') or r.get('Conta'),
            'valor_pagamento': vp,
            'tipo_fonte_escolhida_decisao_local': r.get('tipo_fonte_escolhida'),
            'fonte_escolhida_id': r.get('fonte_escolhida_id'),
            'lote_id_escolhido': r.get('lote_id_escolhido'),
            'saldo_antes_temporal_lote': saldo_antes_temporal,
            'valor_disponivel_escolhido_local': r.get('valor_disponivel_escolhido'),
            'custo_economico_proxy_lote': proxy_lote,
            'status_temporal_auditoria': status_temporal,
            'pagamento_totalmente_coberto_temporal': temporal_coberto,
            'requer_reescolha_dinamica_temporal': requer_reescolha,
            'lote_sem_saldo_derivado_auditoria_temporal': lote_sem_saldo,
            'existe_recebido_disponivel_elegivel': existe_eleg,
            'qtd_recebidos_disponiveis_elegiveis': qtd_eleg,
            'maior_valor_liquido_recebido_disponivel': maior_val,
            'recebido_cobre_pagamento': cobre,
            'melhor_recebido_id': melhor_id,
            'status_recebido': status_receb,
            'destino_potencial_recebido': dest_pot,
            'data_recebimento': data_rec,
            'data_aplicacao': data_apl,
            'motivo_recebido_nao_escolhido': motivo,
            'diagnostico_causa_provavel': causa if causa in CAUSAS else 'inconclusivo_exige_inspecao_manual',
            'classe_correcao_futura': classe if classe in CLASSES else 'inspecao_manual',
        })

    out = pd.DataFrame(rows, columns=COLUNAS_SAIDA)
    out.to_csv(CSV_PRINCIPAL, index=False)

    resumo = {
        'diagnostico_causa_provavel': out['diagnostico_causa_provavel'].value_counts().to_dict(),
        'classe_correcao_futura': out['classe_correcao_futura'].value_counts().to_dict(),
        'presenca_recebido_elegivel': out['existe_recebido_disponivel_elegivel'].value_counts().to_dict(),
        'suficiencia_recebido': out['recebido_cobre_pagamento'].value_counts().to_dict(),
        'lote_sem_saldo_temporal_cumulativo': int((out['diagnostico_causa_provavel'] == 'lote_escolhido_sem_saldo_temporal_cumulativo').sum()),
        'lote_sem_saldo_derivado_auditoria_temporal': out['lote_sem_saldo_derivado_auditoria_temporal'].value_counts().to_dict(),
    }
    pd.DataFrame([
        {'tipo_resumo': 'diagnostico_causa_provavel', 'chave': k, 'qtd': v} for k, v in resumo['diagnostico_causa_provavel'].items()
    ] + [
        {'tipo_resumo': 'classe_correcao_futura', 'chave': k, 'qtd': v} for k, v in resumo['classe_correcao_futura'].items()
    ] + [
        {'tipo_resumo': 'presenca_recebido_elegivel', 'chave': str(k), 'qtd': v} for k, v in resumo['presenca_recebido_elegivel'].items()
    ] + [
        {'tipo_resumo': 'suficiencia_recebido', 'chave': str(k), 'qtd': v} for k, v in resumo['suficiencia_recebido'].items()
    ] + [
        {'tipo_resumo': 'lote_sem_saldo_temporal_cumulativo', 'chave': 'total', 'qtd': resumo['lote_sem_saldo_temporal_cumulativo']}
    ] + [
        {'tipo_resumo': 'lote_sem_saldo_derivado_auditoria_temporal', 'chave': str(k), 'qtd': v}
        for k, v in resumo['lote_sem_saldo_derivado_auditoria_temporal'].items()
    ]).to_csv(CSV_RESUMO, index=False)

    print('versao_alvo=V16-I.1')
    print('numero_de_versoes_usadas=1')
    print(f'head_inicial={head_inicial}')
    print(f'commit_v16h_confirmado={commit_ok}')
    print(f'total_casos_A_auditados={len(out)}')
    if len(out) != 65:
        print(f'ALERTA: total_casos_A_diferente_de_65={len(out)}')
    print(f"total_por_diagnostico_causa_provavel={resumo['diagnostico_causa_provavel']}")
    print(f"total_por_classe_correcao_futura={resumo['classe_correcao_futura']}")
    print(f"qtd_com_recebido_disponivel_elegivel={int(out['existe_recebido_disponivel_elegivel'].sum()) if len(out) else 0}")
    print(f"qtd_com_recebido_disponivel_suficiente={int(out['recebido_cobre_pagamento'].sum()) if len(out) else 0}")
    print(f"qtd_sem_recebido_disponivel_elegivel={int((~out['existe_recebido_disponivel_elegivel']).sum()) if len(out) else 0}")
    print(f"qtd_lote_escolhido_sem_saldo_temporal_cumulativo={resumo['lote_sem_saldo_temporal_cumulativo']}")
    print(f"qtd_lote_sem_saldo_derivado_auditoria_temporal={int(out['lote_sem_saldo_derivado_auditoria_temporal'].sum()) if len(out) else 0}")
    print(f'caminho_csv_principal={CSV_PRINCIPAL}')
    print(f'caminho_csv_resumo={CSV_RESUMO}')
    print('confirmacao_contrato_modelo_lidos_e_nao_alterados=true')
    print('confirmacao_ledger_saida_canonica_ranking_switching_nao_alterados=true')
    print('ids_A_resolvidos_total=0')
    print('ids_B_ainda_sem_saldo=metrica_nao_disponivel_no_contexto_diagnostico; origem_tentada=contexto_baseline')
    print('ids_B_resolvidos=metrica_nao_disponivel_no_contexto_diagnostico; origem_tentada=contexto_baseline')
    print('switching_linhas=metrica_nao_disponivel_no_contexto_diagnostico; origem_tentada=contexto_baseline')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
