from __future__ import annotations
import glob
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

OUT_DIR = Path('saidas/diagnostico')
OUT_DIR.mkdir(parents=True, exist_ok=True)

BLOCK_STATUS = {
    'sem_saldo_temporal_auditavel','sem_fonte_auditavel','switch_then_pay_sem_materializacao','fonte_pos_switching_nao_materializada'
}

def norm(v): return str(v or '').strip().lower()
def is_nd(v): return norm(v) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'nan', 'none'}

def _inferir_causa(row):
    status = norm(row.get('Status recomendação')); motivo = norm(row.get('Motivo bloqueio lote'))
    reserva = row.get('_reserva_preenchida', False)
    if status == 'switch_then_pay_sem_materializacao' or motivo == 'switch_then_pay_sem_materializacao':
        return ('lote pós-switching não injetado no fluxo','ledger_temporal_conjunto','registrada_pipeline')
    if reserva and is_nd(row.get('Saldo Antes')): return ('reserva não promovida por saldo','promocao_reserva_para_lote','inferida')
    if reserva and row.get('_reserva_futura_sinal', False): return ('reserva não promovida por data','elegibilidade_temporal','inferida')
    if reserva and row.get('_reserva_prazo_sinal', False): return ('reserva não promovida por liquidez/carência','elegibilidade_liquidez_carencia','inferida')
    if reserva and motivo in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}:
        return ('reserva descartada sem motivo estruturado','promocao_reserva_para_lote','causa_nao_rastreada_no_pipeline')
    if status in BLOCK_STATUS: return ('sem fonte elegível real','motor_recomendacao','registrada_pipeline')
    return ('outro','nao_classificado','causa_nao_rastreada_no_pipeline')

def _non_empty(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if len(df)==0: return df
    c=[x for x in cols if x in df.columns]
    if not c: return df.iloc[0:0]
    mask=df[c].apply(lambda r: any(not is_nd(v) for v in r), axis=1)
    return df[mask].copy()

def main()->int:
    candidates=sorted(glob.glob('saidas/oficial/*.xlsx'), key=lambda p: Path(p).stat().st_mtime)
    if not candidates:
        print('sem xlsx em saidas/oficial'); return 2
    print('candidatos_xlsx_ordenados_por_mtime:')
    for p in candidates:
        mt=datetime.fromtimestamp(Path(p).stat().st_mtime,tz=timezone.utc).isoformat()
        print(f'- {Path(p).resolve()} | mtime_utc={mt}')
    xlsx=Path(candidates[-1]).resolve()
    mtime=datetime.fromtimestamp(xlsx.stat().st_mtime,tz=timezone.utc).isoformat()

    xl=pd.ExcelFile(xlsx)
    abas=list(xl.sheet_names)
    print(f'xlsx_escolhido={xlsx}')
    print(f'xlsx_mtime_utc={mtime}')
    print(f'abas_disponiveis={abas}')

    extrato=pd.read_excel(xl, sheet_name='Extrato Futuro')
    extrato=extrato[~extrato.apply(lambda r: all(is_nd(v) for v in r), axis=1)].copy()

    aba_shapes=[]
    def ler(nome):
        if nome in abas:
            df=pd.read_excel(xl, sheet_name=nome)
            df=df[~df.apply(lambda r: all(is_nd(v) for v in r), axis=1)].copy()
            aba_shapes.append({'aba':nome,'linhas':len(df),'colunas':len(df.columns)})
            return df
        return pd.DataFrame()
    aba_shapes.append({'aba':'Extrato Futuro','linhas':len(extrato),'colunas':len(extrato.columns)})
    estado=ler('Estado Pos-Switching'); sint=ler('Lotes Sinteticos Pos-Sw'); sw=ler('Switching'); sws=ler('Switchings'); saida_can=ler('Saida Canonica')


    estruturado = pd.DataFrame()
    if len(saida_can):
        cand_cols = ['Despesa ID','fonte_candidata_id','tipo_fonte_candidata','origem_fonte_candidata','elegivel_temporalmente','saldo_liquido_disponivel','elegivel_liquidez_carencia','promovida_para_lote_sugerido','etapa_descarte_fonte','motivo_descarte_fonte','origem_motivo_descarte','evento_switching_id']
        has=[c for c in cand_cols if c in saida_can.columns]
        if has and 'Despesa ID' in has:
            estruturado = saida_can[has].copy()
            estruturado = estruturado.rename(columns={'Despesa ID':'_join_despesa_id'})
            extrato['_join_despesa_id']=extrato['Despesa ID'].astype(str)
            extrato = extrato.merge(estruturado, how='left', on='_join_despesa_id')

    extrato['_lote_nd']=extrato['Lote sugerido'].apply(is_nd)
    extrato['_reserva_preenchida']=~extrato['Lote reserva'].apply(is_nd)
    extrato['_reserva_futura_sinal']=extrato['Lote reserva'].astype(str).str.contains('mai\.|jun\.|jul\.|ago\.|set\.|out\.|nov\.|dez\.', case=False, na=False)
    extrato['_reserva_prazo_sinal']=extrato['Lote reserva'].astype(str).str.contains('cdb|lc[ai]|tesouro|prazo|carência|carencia', case=False, na=False)
    extrato['_consumiu_lote_pos_sw']=~extrato.get('Lote pós-switching', pd.Series(['']*len(extrato))).apply(is_nd)

    sem_lote=extrato[extrato['_lote_nd']].copy()
    causas=sem_lote.apply(_inferir_causa, axis=1, result_type='expand')
    sem_lote[['causa_raiz','etapa_descarte_fonte','tipo_causa']]=causas
    sem_lote['fontes_candidatas_motor']=sem_lote.get('fonte_candidata_id', sem_lote['Lote reserva']).fillna('n/d')
    sem_lote['saldo_liquido_reserva_data']=sem_lote.get('saldo_liquido_disponivel', sem_lote['Saldo Antes']).fillna('n/d')
    sem_lote['elegibilidade_temporal_reserva']=sem_lote['_reserva_futura_sinal'].map({True:'ineligivel_data_inferido',False:'sem_evidencia_ineligibilidade_data'})
    sem_lote['liquidez_carencia_reserva']=sem_lote['_reserva_prazo_sinal'].map({True:'sinal_produto_com_carencia_liquidez',False:'n/d'})
    sem_lote['reserva_descartada']=sem_lote['_reserva_preenchida'].map({True:'sim',False:'não'})
    sem_lote['motivo_descarte_fonte_estruturado']=sem_lote.get('motivo_descarte_fonte', pd.Series(['']*len(sem_lote))).fillna('')
    sem_lote['origem_motivo_descarte_estruturado']=sem_lote.get('origem_motivo_descarte', pd.Series(['']*len(sem_lote))).fillna('')

    sem_lote[['Data','Conta','Valor','Lote reserva','Status recomendação','Motivo bloqueio lote','fontes_candidatas_motor','saldo_liquido_reserva_data','elegibilidade_temporal_reserva','liquidez_carencia_reserva','reserva_descartada','etapa_descarte_fonte','motivo_descarte_fonte_estruturado','origem_motivo_descarte_estruturado','causa_raiz','tipo_causa']].to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_detalhe.csv',index=False)
    causas_agg=sem_lote['causa_raiz'].value_counts().rename_axis('causa_raiz').reset_index(name='qtd')
    causas_agg.to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_causas.csv',index=False)

    materiais=[]
    if len(estado):
        base=_non_empty(estado,['Novo lote','Data','Lotes origem'])
        for _,r in base.iterrows(): materiais.append({'lote':r.get('Novo lote'),'data':r.get('Data'),'origem':r.get('Lotes origem'),'destino':r.get('Produto destino') or r.get('Destino'),'valor':r.get('Valor inicial') or r.get('Valor líquido total')})
    elif len(sint):
        base=_non_empty(sint,['Novo lote','Data','Lotes origem'])
        for _,r in base.iterrows(): materiais.append({'lote':r.get('Novo lote'),'data':r.get('Data'),'origem':r.get('Lotes origem'),'destino':r.get('Destino'),'valor':r.get('Valor líquido total')})
    elif len(sw):
        base=_non_empty(sw,['Novo lote','Lote pós-switching','Data'])
        for _,r in base.iterrows(): materiais.append({'lote':r.get('Novo lote') or r.get('Lote pós-switching'),'data':r.get('Data') or r.get('Data sugerida'),'origem':r.get('Lote origem'),'destino':r.get('Destino') or r.get('Produto destino switching'),'valor':r.get('Valor líquido total') or r.get('Valor líquido origem')})
    elif len(sws):
        base=_non_empty(sws,['Novo lote','Lote pós-switching','Data'])
        for _,r in base.iterrows(): materiais.append({'lote':r.get('Novo lote') or r.get('Lote pós-switching'),'data':r.get('Data') or r.get('Data sugerida'),'origem':r.get('Lote origem'),'destino':r.get('Destino') or r.get('Produto destino switching'),'valor':r.get('Valor líquido total') or r.get('Valor líquido origem')})

    mat=pd.DataFrame(materiais)
    if len(mat):
        mat=mat[~mat['lote'].apply(is_nd)].drop_duplicates(subset=['lote','data'])
    sw_rows=[]
    for _,r in mat.iterrows():
        lote=str(r['lote']); data=str(r['data'] or '')
        eleg=extrato[extrato['Data'].astype(str)>=data] if data else extrato
        entrou=bool((extrato['Lote sugerido'].astype(str).str.strip().str.lower()==lote.strip().lower()).any())
        sw_rows.append({'evento_switching_id':f"sw::{data or 'n/d'}::{r.get('origem') or 'n/d'}::{lote}",'lote_pos_switching':lote,'data_materializacao':data or 'n/d','lotes_origem':r.get('origem') or 'n/d','produto_destino':r.get('destino') or 'n/d','valor_inicial_materializado':r.get('valor') or 'n/d','qtd_pagamentos_elegiveis_apos_materializacao':len(eleg),'entrou_como_fonte_no_extrato_futuro':'sim' if entrou else 'não','motivo_inferido_se_nao_entrou':'fonte disponível não propagada motor → ledger' if not entrou else 'n/d'})
    sw_df=pd.DataFrame(sw_rows)
    sw_df.to_csv(OUT_DIR/'diagnostico_switchings_materializados.csv',index=False)

    resumo=pd.DataFrame([{
        'xlsx_escolhido':str(xlsx),'xlsx_mtime_utc':mtime,'abas_disponiveis':' | '.join(abas),
        'total_pagamentos_futuros':len(extrato),'total_lote_sugerido_determinado':int((~extrato['_lote_nd']).sum()),'total_lote_sugerido_nao_determinado':int(extrato['_lote_nd'].sum()),
        'total_reserva_preenchida':int(extrato['_reserva_preenchida'].sum()),'total_reserva_preenchida_e_lote_nd':int((extrato['_reserva_preenchida'] & extrato['_lote_nd']).sum()),
        'total_lotes_pos_switching_materializados':len(sw_df),'total_pagamentos_que_consumiram_lote_pos_switching':int(extrato['_consumiu_lote_pos_sw'].sum())
    }])
    resumo.to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_resumo.csv',index=False)
    pd.DataFrame(aba_shapes).to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_abas_shapes.csv', index=False)

    print('shapes_lidos:')
    print(pd.DataFrame(aba_shapes).to_string(index=False))
    print(resumo.to_string(index=False))
    print('causas_raiz_agrupadas:'); print(causas_agg.to_string(index=False))
    print('lotes_pos_switching_materializados_encontrados:')
    if len(sw_df): print(sw_df[['lote_pos_switching','entrou_como_fonte_no_extrato_futuro']].to_string(index=False))
    else: print('nenhum')
    return 0

if __name__=='__main__': raise SystemExit(main())
