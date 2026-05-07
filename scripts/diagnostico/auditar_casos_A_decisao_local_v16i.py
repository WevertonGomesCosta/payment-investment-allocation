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

CLASSES = {'decisao_local', 'materializacao_recebidos', 'saldo_temporal_cumulativo', 'contrato_atual_sem_correcao', 'inspecao_manual'}


def _n(v):
    return str(v or '').strip().lower()


def _bool(v):
    return _n(v) in {'1', 'true', 'sim', 's', 'yes', 'y'} or v is True


def _head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RAIZ, text=True).strip()


def _commit_v16h_ok():
    try:
        msg = subprocess.check_output(['git', 'show', '-s', '--format=%s', '15320e4e712e461c7b7a0d58d91ffd5484c65492'], cwd=RAIZ, text=True).strip()
        return msg == 'Restrict received-source handling to local payment decisions'
    except Exception:
        return False


def _to_float_or_none(v):
    num = pd.to_numeric(pd.Series([v]), errors='coerce').iloc[0]
    return None if pd.isna(num) else float(num)


def main() -> int:
    head_inicial = _head()
    commit_ok = _commit_v16h_ok()

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

    q_extrato['Despesa ID'] = q_extrato['Despesa ID'].astype(str)
    q_extrato['Status recomendação'] = q_extrato['Status recomendação'].astype(str).str.lower()
    casos_a = q_extrato[q_extrato['Status recomendação'].eq('sem_saldo_temporal_auditavel')].copy()
    casos_a = casos_a.merge(q_local, left_on='Despesa ID', right_on='pagamento_id', how='left', suffixes=('_ext', '_local'))
    q_aud_merge = q_aud.add_suffix('_aud')
    casos_a = casos_a.merge(q_aud_merge, left_on='Despesa ID', right_on='pagamento_id_aud', how='left')
    casos_a = casos_a[casos_a['tipo_fonte_escolhida'].astype(str).str.lower().eq('lote_resgatavel')].copy()

    rows = []
    schema_cols = [
        'pagamento_id','data_pagamento','descricao_pagamento','valor_pagamento',
        'tipo_fonte_escolhida_decisao_local','fonte_escolhida_id','lote_id_escolhido',
        'saldo_antes_temporal_lote','valor_disponivel_escolhido_local','custo_economico_proxy_lote',
        'existe_recebido_disponivel_elegivel','qtd_recebidos_disponiveis_elegiveis','maior_valor_liquido_recebido_disponivel',
        'recebido_cobre_pagamento','melhor_recebido_id','status_recebido','destino_potencial_recebido',
        'data_recebimento','data_aplicacao','motivo_recebido_nao_escolhido','diagnostico_causa_provavel','classe_correcao_futura',
        'gatilho_motivo_ledger_saldo_insuficiente','gatilho_cob_temporal_false','gatilho_requer_reescolha_temporal',
        'gatilho_saldo_antes_menor_pagamento','gatilho_consumo_menor_pagamento','gatilho_saldo_remanescente_negativo',
    ]
    for _, r in casos_a.iterrows():
        pid = str(r['Despesa ID'])
        vp = float(r.get('valor_pagamento') or r.get('Valor') or 0.0)
        fontes_pid = q_fontes[q_fontes['pagamento_id'] == pid].copy()
        receb_eleg = fontes_pid[(fontes_pid['tipo_fonte'].astype(str).str.lower() == 'recebido_disponivel') & (fontes_pid['elegivel_na_data_pagamento'].apply(_bool))].copy()
        receb_all = fontes_pid[fontes_pid['tipo_fonte'].astype(str).str.lower() == 'recebido_disponivel'].copy()

        qtd_eleg = int(len(receb_eleg))
        existe_eleg = qtd_eleg > 0
        maior_val = float(pd.to_numeric(receb_eleg['valor_liquido_disponivel'], errors='coerce').max()) if existe_eleg else 0.0
        cobre = maior_val + 0.01 >= vp if existe_eleg else False

        melhor = receb_eleg.sort_values('valor_liquido_disponivel', ascending=False).head(1)
        melhor_id = str(melhor['recebido_id'].iloc[0]) if len(melhor) else ''

        rec_row = q_rec[q_rec['recebido_id'] == melhor_id].head(1)
        status_receb = rec_row['status_recebido'].iloc[0] if len(rec_row) else ''
        dest_pot = rec_row['destino_potencial'].iloc[0] if len(rec_row) else ''
        data_rec = rec_row['data_recebimento'].iloc[0] if len(rec_row) else ''
        data_apl = rec_row['data_aplicacao'].iloc[0] if len(rec_row) else ''

        motivo_ledger = _n(r.get('motivo_bloqueio_ledger_aud') or r.get('motivo_bloqueio_ledger'))
        cob_temporal = _n(r.get('pagamento_totalmente_coberto_temporal_aud') or r.get('pagamento_totalmente_coberto_temporal'))
        requer_reescolha_temporal = _bool(r.get('requer_reescolha_dinamica_aud'))
        if not requer_reescolha_temporal:
            requer_reescolha_temporal = _bool(r.get('requer_reescolha_dinamica_temporal'))
        saldo_ant_temporal = _to_float_or_none(r.get('saldo_antes_temporal_aud') or r.get('saldo_antes_temporal'))
        saldo_dep_temporal = _to_float_or_none(r.get('saldo_remanescente_temporal_aud') or r.get('saldo_remanescente_temporal'))
        consumo_temporal = _to_float_or_none(r.get('liquido_temporal_aud') or r.get('Consumo temp.'))

        gatilho_motivo_ledger_saldo_insuficiente = motivo_ledger == 'saldo_temporal_insuficiente_cumulativo'
        gatilho_cob_temporal_false = cob_temporal in {'não', 'nao', 'n', 'false', '0'}
        gatilho_requer_reescolha_temporal = requer_reescolha_temporal
        gatilho_saldo_antes_menor_pagamento = (saldo_ant_temporal is not None and vp > 0 and saldo_ant_temporal + 0.01 < vp)
        gatilho_consumo_menor_pagamento = (consumo_temporal is not None and vp > 0 and consumo_temporal + 0.01 < vp)
        gatilho_saldo_remanescente_negativo = (
            saldo_ant_temporal is not None and saldo_dep_temporal is not None and saldo_ant_temporal >= 0 and saldo_dep_temporal < -0.01
        )
        lote_sem_saldo = any([
            gatilho_motivo_ledger_saldo_insuficiente,
            gatilho_cob_temporal_false,
            gatilho_requer_reescolha_temporal,
            gatilho_saldo_antes_menor_pagamento,
            gatilho_consumo_menor_pagamento,
            gatilho_saldo_remanescente_negativo,
        ])

        proxy_lote = _to_float_or_none(r.get('custo_economico_proxy'))
        if proxy_lote is None:
            proxy_lote = _to_float_or_none(r.get('custo_economico_proxy_local'))
        if proxy_lote is None:
            proxy_lote = 0.0

        proxy_rec = None
        if existe_eleg and len(melhor):
            if 'custo_economico_proxy' in melhor.columns:
                proxy_rec = _to_float_or_none(melhor['custo_economico_proxy'].iloc[0])
            if proxy_rec is None and 'metodo_valor_disponivel' in melhor.columns:
                metodo = str(melhor['metodo_valor_disponivel'].iloc[0] or '')
                extraido = pd.to_numeric(pd.Series([metodo]).astype(str).str.extract(r'([\-\d\.]+)')[0], errors='coerce').iloc[0]
                proxy_rec = None if pd.isna(extraido) else float(extraido)

        if lote_sem_saldo:
            causa = 'lote_escolhido_sem_saldo_temporal_cumulativo'; classe = 'saldo_temporal_cumulativo'; motivo = 'auditoria_temporal_indica_sem_saldo'
        elif not existe_eleg and len(receb_all) > 0:
            causa = 'recebido_disponivel_bloqueado_temporalmente'; classe = 'materializacao_recebidos'; motivo = 'recebidos_existem_mas_ineligiveis_na_data'
        elif not existe_eleg and len(receb_all) == 0:
            rec_comp = q_rec.copy()
            data_pg = r.get('data_pagamento') or r.get('Data')
            data_pg_ts = pd.to_datetime(data_pg, errors='coerce')
            rec_comp['data_recebimento_ts'] = pd.to_datetime(rec_comp.get('data_recebimento'), errors='coerce')
            rec_comp['data_aplicacao_ts'] = pd.to_datetime(rec_comp.get('data_aplicacao'), errors='coerce')
            rec_comp['valor_liquido_num'] = pd.to_numeric(rec_comp.get('valor_liquido'), errors='coerce')
            rec_comp['pagamento_vinculado_id_norm'] = rec_comp.get('pagamento_vinculado_id', '').astype(str)
            comp_pagto_id = rec_comp['pagamento_vinculado_id_norm'].eq(pid)
            comp_data = rec_comp['data_recebimento_ts'].notna() & data_pg_ts.notna() & rec_comp['data_recebimento_ts'].le(data_pg_ts)
            comp_valor = rec_comp['valor_liquido_num'].notna() & rec_comp['valor_liquido_num'].ge(max(vp - 0.01, 0.0))
            rec_compativel = rec_comp[comp_pagto_id | (comp_data & comp_valor)]
            if len(rec_compativel) > 0:
                causa = 'fonte_recebido_nao_materializada_para_pagamento'; classe = 'materializacao_recebidos'; motivo = 'recebido_compativel_no_auditavel_sem_materializacao_nas_fontes'
            elif len(q_rec) == 0:
                causa = 'sem_recebido_disponivel_elegivel'; classe = 'contrato_atual_sem_correcao'; motivo = 'sem_recebidos_auditaveis_no_contexto'
            else:
                causa = 'inconclusivo_exige_inspecao_manual'; classe = 'inspecao_manual'; motivo = 'nao_ha_vinculo_auditavel_do_recebido_ao_pagamento'
        elif existe_eleg and not cobre:
            causa = 'recebido_disponivel_insuficiente'; classe = 'contrato_atual_sem_correcao'; motivo = 'maior_recebido_nao_cobre_pagamento'
        elif existe_eleg and cobre and proxy_rec is not None and proxy_lote <= proxy_rec:
            causa = 'recebido_disponivel_existe_mas_proxy_prefere_lote'; classe = 'decisao_local'; motivo = 'proxy_lote_melhor_ou_igual'
        elif existe_eleg and cobre:
            causa = 'recebido_disponivel_existe_mas_ordem_local_prefere_lote'; classe = 'decisao_local'; motivo = 'ordem_local_priorizou_lote'
        else:
            causa = 'inconclusivo_exige_inspecao_manual'; classe = 'inspecao_manual'; motivo = 'sem_evidencia_conclusiva'

        rows.append({
            'pagamento_id': pid,
            'data_pagamento': r.get('data_pagamento') or r.get('Data'),
            'descricao_pagamento': r.get('descricao_pagamento') or r.get('Conta'),
            'valor_pagamento': vp,
            'tipo_fonte_escolhida_decisao_local': r.get('tipo_fonte_escolhida'),
            'fonte_escolhida_id': r.get('fonte_escolhida_id'),
            'lote_id_escolhido': r.get('lote_id_escolhido'),
            'saldo_antes_temporal_lote': r.get('Saldo temp. ant.'),
            'valor_disponivel_escolhido_local': r.get('valor_disponivel_escolhido'),
            'custo_economico_proxy_lote': r.get('custo_economico_proxy'),
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
            'gatilho_motivo_ledger_saldo_insuficiente': gatilho_motivo_ledger_saldo_insuficiente,
            'gatilho_cob_temporal_false': gatilho_cob_temporal_false,
            'gatilho_requer_reescolha_temporal': gatilho_requer_reescolha_temporal,
            'gatilho_saldo_antes_menor_pagamento': gatilho_saldo_antes_menor_pagamento,
            'gatilho_consumo_menor_pagamento': gatilho_consumo_menor_pagamento,
            'gatilho_saldo_remanescente_negativo': gatilho_saldo_remanescente_negativo,
        })

    out = pd.DataFrame(rows, columns=schema_cols)
    out.to_csv(CSV_PRINCIPAL, index=False)

    resumo = {
        'diagnostico_causa_provavel': out['diagnostico_causa_provavel'].value_counts().to_dict(),
        'classe_correcao_futura': out['classe_correcao_futura'].value_counts().to_dict(),
        'presenca_recebido_elegivel': out['existe_recebido_disponivel_elegivel'].value_counts().to_dict(),
        'suficiencia_recebido': out['recebido_cobre_pagamento'].value_counts().to_dict(),
        'lote_sem_saldo_temporal_cumulativo': int((out['diagnostico_causa_provavel'] == 'lote_escolhido_sem_saldo_temporal_cumulativo').sum()),
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
    print(f"gatilho_motivo_ledger_saldo_insuficiente={int(out['gatilho_motivo_ledger_saldo_insuficiente'].sum()) if len(out) else 0}")
    print(f"gatilho_cob_temporal_false={int(out['gatilho_cob_temporal_false'].sum()) if len(out) else 0}")
    print(f"gatilho_requer_reescolha_temporal={int(out['gatilho_requer_reescolha_temporal'].sum()) if len(out) else 0}")
    print(f"gatilho_saldo_antes_menor_pagamento={int(out['gatilho_saldo_antes_menor_pagamento'].sum()) if len(out) else 0}")
    print(f"gatilho_consumo_menor_pagamento={int(out['gatilho_consumo_menor_pagamento'].sum()) if len(out) else 0}")
    print(f"gatilho_saldo_remanescente_negativo={int(out['gatilho_saldo_remanescente_negativo'].sum()) if len(out) else 0}")
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
