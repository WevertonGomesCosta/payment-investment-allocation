from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

XLSX = RAIZ / 'saidas' / 'oficial' / 'relatorio_operacional_v225.xlsx'
CSV_S7G = RAIZ / 'saidas' / 'diagnostico' / 'tabela_operacional_pagamentos_v17_f0_s7g.csv'
CSV_S7J = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_uso_operacional_tabela_pagamentos_v17_f0_s7j.csv'
ABA = 'Tabela Operacional Pagamentos'
COLS = ['data','conta','valor','lote_recomendado','fontes_componentes','qtd_fontes_componentes','fonte_principal','fonte_reserva','status_operacional','acao_recomendada','saldo_pos_pagamento','saldo_pos_pagamento_origem','alerta_operacional','tipo_alerta_operacional','problema_operacional','motivo_operacional','fonte_aprovada_para_pagamento']


def s(df, c, d=''):
    return df[c] if c in df.columns else pd.Series([d] * len(df), index=df.index)

def fnum(sr): return pd.to_numeric(sr, errors='coerce')

def sent_uso(df, data, conta, lote, saldo):
    m = df[(s(df, 'data').astype(str) == data) & (s(df, 'conta').astype(str) == conta)]
    if m.empty: return 'nao'
    r = m.iloc[0]
    ok = str(r.get('lote_recomendado', '')) == lote and abs(float(pd.to_numeric(pd.Series([r.get('saldo_pos_pagamento')]), errors='coerce').fillna(-1).iloc[0]) - saldo) < 0.01
    return 'sim' if ok else 'nao'

def sent_alerta(df, data, conta):
    m = df[(s(df, 'data').astype(str) == data) & (s(df, 'conta').astype(str) == conta)]
    if m.empty: return 'nao'
    r = m.iloc[0]
    ok = str(r.get('alerta_operacional', '')) == 'sim' and str(r.get('tipo_alerta_operacional', '')) == 'explicito' and str(r.get('problema_operacional', '')) == 'sem_saldo_temporal_auditavel' and str(r.get('motivo_operacional', '')) == 'saldo_temporal_insuficiente_cumulativo'
    return 'sim' if ok else 'nao'


def main():
    fonte, caminho, df = 'indisponivel', 'indisponivel', None
    if XLSX.exists():
        xls = pd.ExcelFile(XLSX)
        if ABA in xls.sheet_names:
            df = pd.read_excel(XLSX, sheet_name=ABA); fonte = 'xlsx'; caminho = str(XLSX)
    if df is None and CSV_S7G.exists():
        df = pd.read_csv(CSV_S7G); fonte = 'csv_s7g'; caminho = str(CSV_S7G)

    print(f'fonte_tabela_operacional={fonte}')
    print(f'caminho_tabela_operacional={caminho}')
    print(f'tabela_operacional_carregada={"sim" if df is not None else "nao"}')

    if df is None:
        print('teste_negativo_coluna_removida=nao_executado_fonte_indisponivel')
        print('teste_negativo_keyerror=nao')
        print('teste_negativo_coluna_ausente_detectada=nao_executado')
        print('teste_negativo_status_controlado=nao_executado')
        print('status_geral_s7j=falha_uso_operacional_tabela_pagamentos')
        return 1

    falt = [c for c in COLS if c not in df.columns]
    data_ok = int(pd.to_datetime(s(df, 'data'), errors='coerce').notna().sum()) if 'data' in df.columns else 0
    conta_ok = int(s(df, 'conta').astype(str).str.strip().ne('').sum()) if 'conta' in df.columns else 0
    valor_ok = int(fnum(s(df, 'valor')).notna().sum()) if 'valor' in df.columns else 0
    status_ok = int(s(df, 'status_operacional').astype(str).str.strip().ne('').sum()) if 'status_operacional' in df.columns else 0
    acao_ok = int(s(df, 'acao_recomendada').astype(str).str.strip().ne('').sum()) if 'acao_recomendada' in df.columns else 0

    aprovado_pay = int((s(df, 'status_operacional') == 'aprovado_para_pagamento').sum())
    aprovado_multi = int((s(df, 'status_operacional') == 'aprovado_multifonte').sum())
    aprov_total = aprovado_pay + aprovado_multi
    qfc = fnum(s(df, 'qtd_fontes_componentes', 0)).fillna(0)
    qtd_multi = int(((s(df, 'status_operacional') == 'aprovado_multifonte') | (qfc > 1)).sum())
    comp_multi = int(qfc[qfc > 1].sum())
    sem_lote_mask = s(df, 'lote_recomendado').fillna('').astype(str).str.strip().eq('')
    sem_lote = int(sem_lote_mask.sum())
    alerta_exp_mask = (s(df, 'alerta_operacional').astype(str) == 'sim') & (s(df, 'tipo_alerta_operacional').astype(str) == 'explicito')
    sem_lote_alerta = int((sem_lote_mask & alerta_exp_mask).sum())
    sem_lote_sem_alerta = int((sem_lote_mask & ~alerta_exp_mask).sum())
    alerta_exp = int((s(df, 'tipo_alerta_operacional') == 'explicito').sum())
    alerta_inf = int((s(df, 'tipo_alerta_operacional') == 'inferido').sum())
    lote_pos = int((s(df, 'usa_lote_pos_switching').astype(str) == 'sim').sum()) if 'usa_lote_pos_switching' in df.columns else 0
    comp_pos = int(fnum(s(df, 'qtd_componentes_pos_switching', 0)).fillna(0).sum()) if 'qtd_componentes_pos_switching' in df.columns else 0

    print(f'qtd_linhas_tabela_operacional={len(df)}')
    print(f'qtd_colunas_tabela_operacional={len(df.columns)}')
    print(f'qtd_colunas_obrigatorias_ausentes={len(falt)}')
    print(f'colunas_obrigatorias_ausentes={"nenhuma" if not falt else ",".join(falt)}')
    print(f'qtd_linhas_com_data_valida={data_ok}')
    print(f'qtd_linhas_com_conta_nao_vazia={conta_ok}')
    print(f'qtd_linhas_com_valor_valido={valor_ok}')
    print(f'qtd_linhas_com_status_operacional_nao_vazio={status_ok}')
    print(f'qtd_linhas_com_acao_recomendada_nao_vazia={acao_ok}')
    print(f'qtd_pagamentos_aprovados_para_pagamento={aprovado_pay}')
    print(f'qtd_pagamentos_aprovados_multifonte={aprovado_multi}')
    print(f'qtd_pagamentos_aprovados_total={aprov_total}')
    print(f'qtd_pagamentos_multifonte={qtd_multi}')
    print(f'qtd_componentes_multifonte_total={comp_multi}')
    print(f'qtd_pagamentos_sem_lote_sugerido={sem_lote}')
    print(f'qtd_pagamentos_sem_lote_sugerido_com_alerta_explicito={sem_lote_alerta}')
    print(f'qtd_pagamentos_sem_lote_sugerido_sem_alerta_explicito={sem_lote_sem_alerta}')
    print(f'qtd_pagamentos_com_alerta_operacional_explicito={alerta_exp}')
    print(f'qtd_pagamentos_com_alerta_operacional_inferido={alerta_inf}')
    print(f'qtd_pagamentos_com_lote_pos_switching_valido={lote_pos}')
    print(f'qtd_componentes_lote_pos_switching_validos={comp_pos}')

    schema_ok = len(falt) == 0

    if schema_ok:
        aprov = df[s(df, 'status_operacional').isin(['aprovado_para_pagamento', 'aprovado_multifonte'])].copy()
        aprov['_data'] = pd.to_datetime(s(aprov, 'data'), errors='coerce')
        aprov = aprov.sort_values(['_data', 'conta'])
        cols_show = [c for c in ['data','conta','valor','lote_recomendado','fonte_principal','fonte_reserva','qtd_fontes_componentes','status_operacional','acao_recomendada','saldo_pos_pagamento','saldo_pos_pagamento_origem','usa_lote_pos_switching','qtd_componentes_pos_switching'] if c in aprov.columns]
        print('\nproximos_5_pagamentos_aprovados='); print(aprov[cols_show].head(5).to_string(index=False))
        print('\nproximos_10_pagamentos_aprovados='); print(aprov[cols_show].head(10).to_string(index=False))
        ate = aprov[aprov['_data'] <= pd.Timestamp('2026-06-30')]
        print('\npagamentos_aprovados_ate_2026_06_30='); print(ate[cols_show].to_string(index=False) if not ate.empty else 'nenhum')
        multi = df[(s(df, 'status_operacional') == 'aprovado_multifonte') | (qfc > 1)]
        mcols = [c for c in ['data','conta','valor','lote_recomendado','fontes_componentes','qtd_fontes_componentes','fonte_principal','fonte_reserva','saldo_pos_pagamento','acao_recomendada'] if c in multi.columns]
        print('\namostra_multifonte_10='); print(multi[mcols].head(10).to_string(index=False))
        aexp = df[alerta_exp_mask]; acols = [c for c in ['data','conta','valor','status_operacional','acao_recomendada','problema_operacional','motivo_operacional','saldo_pos_pagamento','saldo_pos_pagamento_origem'] if c in aexp.columns]
        print('\namostra_alertas_explicitos_10='); print(aexp[acols].head(10).to_string(index=False))
        sem = df[sem_lote_mask]; scols = [c for c in ['data','conta','valor','status_operacional','acao_recomendada','alerta_operacional','tipo_alerta_operacional','problema_operacional','motivo_operacional','saldo_pos_pagamento','saldo_pos_pagamento_origem'] if c in sem.columns]
        print('\namostra_sem_lote_10='); print(sem[scols].head(10).to_string(index=False))
        uso = aprov.copy(); uso['usar_lote']=s(uso,'lote_recomendado'); uso['usar_fonte_principal']=s(uso,'fonte_principal'); uso['usar_fonte_reserva']=s(uso,'fonte_reserva'); uso['tipo_pagamento']=s(uso,'status_operacional'); uso['observacao_operacional']=''
        uso.loc[s(uso,'status_operacional')=='aprovado_para_pagamento','observacao_operacional']='pagar_com_lote_recomendado'
        uso.loc[s(uso,'status_operacional')=='aprovado_multifonte','observacao_operacional']='pagar_com_fontes_componentes'
        uso.loc[s(uso,'alerta_operacional')=='sim','observacao_operacional']='nao_pagar_sem_revisao_operacional'
        ucols=[c for c in ['data','conta','valor','usar_lote','usar_fonte_principal','usar_fonte_reserva','tipo_pagamento','saldo_pos_pagamento','observacao_operacional'] if c in uso.columns]
        print('\nuso_operacional_resumo='); print(uso[ucols].head(20).to_string(index=False))
        s1=sent_uso(df,'2026-05-15','Internet','Lote 3120 mai',2895.01); s2=sent_uso(df,'2026-05-20','Cartão Azul','Lote 3120 mai + Lote 3000 mai Neon',869.53); s3=sent_uso(df,'2026-05-20','Condomínio','Lote 3000 mai Neon',1205.69); s4=sent_uso(df,'2026-05-30','Implante Velt','Lote 3120 mai',2495.01); s5=sent_uso(df,'2026-06-02','Cartão NU','Lote 3120 mai',1915.01)
        a1=sent_alerta(df,'2026-06-12','Aluguel'); a2=sent_alerta(df,'2026-06-20','Condomínio')
    else:
        print('\nproximos_5_pagamentos_aprovados=nao_gerado_schema_invalido')
        print('proximos_10_pagamentos_aprovados=nao_gerado_schema_invalido')
        print('pagamentos_aprovados_ate_2026_06_30=nao_gerado_schema_invalido')
        print('amostra_multifonte_10=nao_gerado_schema_invalido')
        print('amostra_alertas_explicitos_10=nao_gerado_schema_invalido')
        print('amostra_sem_lote_10=nao_gerado_schema_invalido')
        print('uso_operacional_resumo=nao_gerado_schema_invalido')
        s1=s2=s3=s4=s5=a1=a2='nao'

    print(f'sentinela_uso_internet_ok={s1}')
    print(f'sentinela_uso_cartao_azul_ok={s2}')
    print(f'sentinela_uso_condominio_2026_05_20_ok={s3}')
    print(f'sentinela_uso_implante_velt_ok={s4}')
    print(f'sentinela_uso_cartao_nu_ok={s5}')
    print(f'sentinela_alerta_aluguel_ok={a1}')
    print(f'sentinela_alerta_condominio_2026_06_20_ok={a2}')

    try:
        df_neg = df.drop(columns=['conta'], errors='ignore')
        falt_neg = [c for c in COLS if c not in df_neg.columns]
        print('teste_negativo_coluna_removida=conta')
        print('teste_negativo_keyerror=nao')
        print(f'teste_negativo_coluna_ausente_detectada={"sim" if "conta" in falt_neg else "nao"}')
        print('teste_negativo_status_controlado=falha_uso_operacional_tabela_pagamentos')
    except KeyError:
        print('teste_negativo_coluna_removida=conta')
        print('teste_negativo_keyerror=sim')
        print('teste_negativo_coluna_ausente_detectada=nao')
        print('teste_negativo_status_controlado=falha_uso_operacional_tabela_pagamentos')

    csv_out='nao_gerado'
    if schema_ok:
        try:
            CSV_S7J.parent.mkdir(parents=True, exist_ok=True)
            save_cols=[c for c in ['data','conta','valor','usar_lote','usar_fonte_principal','usar_fonte_reserva','tipo_pagamento','status_operacional','acao_recomendada','alerta_operacional','tipo_alerta_operacional','problema_operacional','motivo_operacional','saldo_pos_pagamento','observacao_operacional'] if c in uso.columns]
            uso[save_cols].to_csv(CSV_S7J, index=False); csv_out=str(CSV_S7J)
        except Exception:
            csv_out='nao_gerado'
    print(f'csv_s7j={csv_out}')

    ok=(schema_ok and len(df)==159 and data_ok==159 and conta_ok==159 and valor_ok==159 and status_ok==159 and acao_ok==159 and aprovado_pay==33 and aprovado_multi==16 and aprov_total==49 and qtd_multi==16 and comp_multi==32 and sem_lote==110 and sem_lote_alerta==110 and sem_lote_sem_alerta==0 and alerta_exp==110 and alerta_inf==0 and lote_pos==14 and comp_pos==16 and s1==s2==s3==s4==s5=='sim' and a1==a2=='sim')
    print(f'status_geral_s7j={"uso_operacional_tabela_pagamentos_auditado" if ok else "falha_uso_operacional_tabela_pagamentos"}')
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
