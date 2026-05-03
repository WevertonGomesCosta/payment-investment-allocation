from __future__ import annotations
import glob
from pathlib import Path
import pandas as pd

OUT_DIR = Path('saidas/diagnostico')
OUT_DIR.mkdir(parents=True, exist_ok=True)

def norm(v):
    return str(v or '').strip().lower()

def is_nd(v):
    return norm(v) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'nan', 'none'}

def main() -> int:
    files=sorted(glob.glob('saidas/oficial/*.xlsx'), key=lambda p: Path(p).stat().st_mtime)
    if not files:
        print('sem xlsx em saidas/oficial')
        return 2
    xlsx=files[-1]
    extrato=pd.read_excel(xlsx, sheet_name='Extrato Futuro')
    try:
        switchings=pd.read_excel(xlsx, sheet_name='Switchings')
    except Exception:
        switchings=pd.DataFrame()

    total=len(extrato)
    status_counts=extrato['Status recomendação'].fillna('n/d').astype(str).value_counts(dropna=False)
    lote_nd=extrato['Lote sugerido'].apply(is_nd)

    # sinais auxiliares
    extrato['_reserva_preenchida']=~extrato['Lote reserva'].apply(is_nd)
    extrato['_saldo_geral_sinal']=extrato.get('Fonte switching', pd.Series(['']*len(extrato))).astype(str).str.contains('saldo_disponivel_geral', case=False, na=False)
    extrato['_lote_futuro_sinal']=extrato['Lote reserva'].astype(str).str.contains('mai\.|jun\.|jul\.|ago\.|set\.|out\.|nov\.|dez\.', case=False, na=False)
    extrato['_pos_sw_materializado']=~extrato.get('Lote pós-switching', pd.Series(['']*len(extrato))).apply(is_nd)

    sem_lote=extrato[lote_nd].copy()

    def causa_raiz(row):
        status=norm(row.get('Status recomendação'))
        motivo=norm(row.get('Motivo bloqueio lote'))
        if 'switch_then_pay_sem_materializacao' in {status,motivo}:
            return 'pós-switching não injetado como fonte'
        if row.get('_reserva_preenchida') and is_nd(row.get('Lote sugerido')):
            return 'reserva não promovida'
        if row.get('_lote_futuro_sinal'):
            return 'fonte existe mas foi descartada por data'
        if status in {'sem_saldo_temporal_auditavel'}:
            return 'fonte existe mas foi descartada por saldo'
        if status in {'sem_fonte_auditavel'}:
            return 'sem fonte elegível'
        return 'outro'

    sem_lote['causa_raiz']=sem_lote.apply(causa_raiz, axis=1)
    sem_lote['fontes_candidatas_motor']=sem_lote['Lote reserva'].fillna('n/d')
    sem_lote['motivo_reserva_nao_promovida']=sem_lote['Motivo bloqueio lote'].fillna('n/d')
    sem_lote['havia_saldo_disponivel_geral']=sem_lote['_saldo_geral_sinal'].map({True:'sim',False:'não'})
    sem_lote['havia_lote_futuro_disponivel_data']=sem_lote['_lote_futuro_sinal'].map({True:'sim',False:'não'})
    sem_lote['havia_lote_pos_switching_materializado_data']=sem_lote['_pos_sw_materializado'].map({True:'sim',False:'não'})
    sem_lote['etapa_descarte_fonte']=sem_lote['causa_raiz']

    cols=['Data','Conta','Valor','Lote reserva','Status recomendação','Motivo bloqueio lote',
          'fontes_candidatas_motor','motivo_reserva_nao_promovida','havia_saldo_disponivel_geral',
          'havia_lote_futuro_disponivel_data','havia_lote_pos_switching_materializado_data','etapa_descarte_fonte','causa_raiz']
    detalhe=sem_lote[cols]
    detalhe.to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_detalhe.csv', index=False)

    causa=sem_lote['causa_raiz'].value_counts().rename_axis('causa').reset_index(name='qtd')
    causa.to_csv(OUT_DIR/'diagnostico_baixa_resolutividade_causas.csv', index=False)

    # switchings materializados
    sw_diag=[]
    if len(switchings):
        for _,r in switchings.iterrows():
            data=str(r.get('Data') or r.get('Data sugerida') or '')
            lote_pos=str(r.get('Novo lote') or r.get('Lote pós-switching') or '')
            eleg=extrato[(extrato['Data'].astype(str)>=data) if data else [True]*len(extrato)]
            sw_diag.append({
                'evento_ou_lote_pos_switching': lote_pos or r.get('Lote origem') or 'n/d',
                'data': data or 'n/d',
                'valor': r.get('Valor líquido total') or r.get('Valor líquido origem') or 'n/d',
                'pagamentos_elegiveis_mesma_data_ou_posteriores': len(eleg),
                'entrou_como_fonte_candidata_no_motor': 'não evidenciado no xlsx',
                'motivo_descarte': 'não injetado no fluxo operacional de pagamento' if len(sem_lote) else 'n/d',
            })
    pd.DataFrame(sw_diag).to_csv(OUT_DIR/'diagnostico_switchings_materializados.csv', index=False)

    print(f'arquivo={xlsx}')
    print(f'total_pagamentos_futuros={total}')
    print('status_recomendacao:')
    print(status_counts.to_string())
    print(f'linhas_lote_nao_determinado={len(sem_lote)}')
    print(f'linhas_reserva_preenchida_sem_promocao={(sem_lote["_reserva_preenchida"]).sum()}')
    print('causas_raiz:')
    print(causa.to_string(index=False))
    print('arquivos_saida:')
    print(OUT_DIR/'diagnostico_baixa_resolutividade_detalhe.csv')
    print(OUT_DIR/'diagnostico_baixa_resolutividade_causas.csv')
    print(OUT_DIR/'diagnostico_switchings_materializados.csv')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
