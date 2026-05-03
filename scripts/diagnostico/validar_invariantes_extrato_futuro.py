from __future__ import annotations
import glob
import sys
from pathlib import Path
import pandas as pd


def _norm(v):
    return str(v or '').strip().lower()

def _has_val(v):
    if v is None:
        return False
    t=str(v).strip().lower()
    return t not in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'nan', 'none'}

files=sorted(glob.glob('saidas/oficial/*.xlsx'), key=lambda p: Path(p).stat().st_mtime)
if not files:
    print('ERRO: sem planilha em saidas/oficial')
    sys.exit(2)
path=files[-1]
df=pd.read_excel(path, sheet_name='Extrato Futuro')
viol=[]
for i,r in df.iterrows():
    lote=_norm(r.get('Lote sugerido'))
    cob=_norm(r.get('Cobertura integral'))
    status=_norm(r.get('Status recomendação'))
    motivo=_norm(r.get('Motivo bloqueio lote'))
    pacote=_norm(r.get('Pacote do dia'))
    lote_pos=_norm(r.get('Lote pós-switching'))

    if cob=='sim' and status!='ok': viol.append((i,'cob_sim_status_nao_ok'))
    if cob=='sim' and motivo not in {'','n/d','nd','não determinado','nao determinado','nan','none'}: viol.append((i,'cob_sim_com_motivo'))
    if status in {'sem_saldo_temporal_auditavel','sem_fonte_auditavel','switch_then_pay_sem_materializacao','fonte_pos_switching_nao_materializada'}:
        for k in ['Saldo Antes','Bruto','Imposto','Líquido','Saldo Remanescente']:
            if _has_val(r.get(k)): viol.append((i,f'status_bloqueio_com_valor_{k}'))
    if _norm(r.get('Estratégia'))=='switching_simples' and _norm(r.get('Pacote do dia'))=='pay_only' and _norm(r.get('Necessita switching'))=='não':
        viol.append((i,'estrategia_switching_incoerente_pay_only'))
    if lote in {'não determinado','nao determinado','n/d','nd',''} and cob=='sim': viol.append((i,'lote_nd_cob_sim'))
    if lote in {'não determinado','nao determinado','n/d','nd',''} and status=='ok': viol.append((i,'lote_nd_status_ok'))
    if lote in {'não determinado','nao determinado','n/d','nd',''}:
        for k in ['Saldo Antes','Bruto','Imposto','Líquido','Saldo Remanescente']:
            if _has_val(r.get(k)): viol.append((i,f'lote_nd_valor_{k}'))
        for k in ['Saldo temp. ant.','Consumo temp.','Saldo temp. dep.']:
            if _has_val(r.get(k)): viol.append((i,f'lote_nd_temp_{k}'))
    if motivo not in {'','n/d','nd','não determinado','nao determinado','nan','none'} and status=='ok': viol.append((i,'motivo_com_status_ok'))
    if pacote=='switch_then_pay' and lote_pos in {'','n/d','nd'}:
        for k in ['Saldo Antes','Bruto','Imposto','Líquido','Saldo Remanescente']:
            if _has_val(r.get(k)): viol.append((i,f'stp_sem_mat_com_valor_{k}'))
    if _has_val(r.get('Destino switching')) and not _has_val(r.get('Evento switching ID')):
        viol.append((i,'switch_operacional_sem_evento_materializado'))

print(f'arquivo={path}')
print(f'linhas_extrato_futuro={len(df)}')
print(f'violacoes={len(viol)}')
for i,v in viol[:50]:
    print(f'linha={int(i)+2} tipo={v}')
sys.exit(1 if viol else 0)
