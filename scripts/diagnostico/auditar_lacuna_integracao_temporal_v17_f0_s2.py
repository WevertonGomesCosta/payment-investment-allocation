from __future__ import annotations
import sys
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0, str(RAIZ))
from aplicacao.principal import carregar_contexto_e_saida
OUT = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_lacuna_integracao_temporal_v17_f0_s2.csv'

def _rows_generico(obj):
    if obj is None: return []
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient='records')
    if isinstance(obj, list): return [dict(x) for x in obj if isinstance(x, dict)]
    return []
def _rows_recebidos_auditaveis(obj):
    if obj is None: return [], 'nao_localizada'
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient='records'), 'objeto_dataframe'
    if isinstance(obj, list): return [dict(x) for x in obj if isinstance(x, dict)], 'objeto_lista'
    for a in ['quadro_recebidos_auditaveis','quadro','df','dados','recebidos_auditaveis']:
        if hasattr(obj,a):
            v=getattr(obj,a)
            if isinstance(v,pd.DataFrame): return v.to_dict(orient='records'), a
            if isinstance(v,list): return [dict(x) for x in v if isinstance(x, dict)], a
    return [], 'nao_localizada'
def _to_mes(v):
    try:return pd.to_datetime(v).strftime('%Y-%m')
    except Exception:return None
def _to_num(v):
    try:
        if pd.isna(v): return 0.0
    except Exception: pass
    try:return float(v)
    except Exception:return 0.0
def _to_bool(v):
    if isinstance(v,bool): return v
    if v is None:return False
    try:
        if pd.isna(v): return False
    except Exception: pass
    s=str(v).strip().lower()
    if s in {'true','1','sim','s','yes','y'}: return True
    if s in {'false','0','nao','não','n','no','','none','nan','null'}: return False
    return False
def _get_any(d,campos):
    for c in campos:
        if c in d and d[c] not in (None,''): return d[c]
    return None

def main():
    contexto, saida = carregar_contexto_e_saida()
    salarios=_rows_generico(contexto.dados_operacionais.salarios_canonicos)
    recebidos,fonte_rec=_rows_recebidos_auditaveis(contexto.recebidos_auditaveis)
    inventario=_rows_generico(contexto.dados_operacionais.inventario_canonico)
    gastos=_rows_generico(contexto.dados_operacionais.gastos_canonicos)
    extrato=_rows_generico(saida.extrato_futuro)
    
    sal_m=defaultdict(lambda:{'tot':0.0,'qtd':0,'rows':[]})
    for i,r in enumerate(salarios,1):
        m=_to_mes(r.get('data_recebimento')); 
        if not m: continue
        sal_m[m]['tot']+=_to_num(r.get('valor_liquido')); sal_m[m]['qtd']+=1; sal_m[m]['rows'].append((i,r))
    rec_m=defaultdict(lambda:{'tot':0.0,'qtd':0,'rows':[],'pre':False})
    for i,r in enumerate(recebidos,1):
        m=_to_mes(r.get('data_recebimento')); 
        if not m: continue
        v=_to_num(r.get('valor_liquido')); rec_m[m]['tot']+=v; rec_m[m]['qtd']+=1; rec_m[m]['rows'].append((i,r))
        if _to_num(r.get('valor_pagamentos_pre_aplicacao'))>0 or str(r.get('status_recebido') or '').lower()=='uso_pre_aplicacao_com_aporte_posterior': rec_m[m]['pre']=True
    ap_m=defaultdict(lambda:{'tot':0.0,'qtd':0,'rows':[]})
    for i,r in enumerate(inventario,1):
        if not _to_bool(r.get('aportado')): continue
        m=_to_mes(r.get('data_aplicacao')); 
        if not m: continue
        ap_m[m]['tot']+=_to_num(r.get('valor_original')); ap_m[m]['qtd']+=1; ap_m[m]['rows'].append((i,r))
    gh_m=defaultdict(lambda:{'tot':0.0,'qtd':0})
    for r in gastos:
        if not _to_bool(r.get('passado_pago_ate_data_referencia')): continue
        m=_to_mes(r.get('data')); 
        if not m: continue
        gh_m[m]['tot']+=_to_num(r.get('valor')); gh_m[m]['qtd']+=1
    gf_m=defaultdict(lambda:{'tot':0.0,'qtd':0,'sc_tot':0.0,'sc_qtd':0})
    for r in extrato:
        m=_to_mes(r.get('Data')); 
        if not m: continue
        v=_to_num(r.get('Valor')); gf_m[m]['tot']+=v; gf_m[m]['qtd']+=1
        semcov=(str(r.get('Cobertura integral') or '').strip().lower()!='sim' or str(r.get('Status recomendação') or '').strip().lower()=='sem_saldo_temporal_auditavel' or str(r.get('Motivo bloqueio lote') or '').strip().lower()=='saldo_temporal_insuficiente_cumulativo')
        if semcov: gf_m[m]['sc_tot']+=v; gf_m[m]['sc_qtd']+=1

    meses=sorted(set(sal_m)|set(rec_m)|set(ap_m)|set(gh_m)|set(gf_m))
    rows=[]
    for m in meses:
        s,r,a=sal_m[m]['tot'],rec_m[m]['tot'],ap_m[m]['tot']
        d_sr,d_sa,d_ra=s-r,s-a,r-a
        has_pre=rec_m[m]['pre']
        pay_sc=gf_m[m]['sc_tot']>0
        base={"mes":m,"salario_mes_total":s,"qtd_salarios_mes":sal_m[m]['qtd'],"recebidos_mes_total":r,"qtd_recebidos_mes":rec_m[m]['qtd'],"aportes_mes_total":a,"qtd_aportes_mes":ap_m[m]['qtd'],"pagamentos_historicos_mes_total":gh_m[m]['tot'],"qtd_pagamentos_historicos_mes":gh_m[m]['qtd'],"pagamentos_futuros_mes_total":gf_m[m]['tot'],"qtd_pagamentos_futuros_mes":gf_m[m]['qtd'],"pagamentos_futuros_sem_cobertura_total":gf_m[m]['sc_tot'],"qtd_pagamentos_futuros_sem_cobertura":gf_m[m]['sc_qtd'],"diferenca_salario_mes_vs_recebidos_mes":d_sr,"diferenca_salario_mes_vs_aportes_mes":d_sa,"diferenca_recebidos_mes_vs_aportes_mes":d_ra,"tem_recebido_no_mes":r>0,"tem_aporte_no_mes":a>0,"tem_pagamento_historico_no_mes":gh_m[m]['tot']>0,"tem_pagamento_futuro_no_mes":gf_m[m]['tot']>0,"tem_pagamento_futuro_sem_cobertura_no_mes":pay_sc,"tem_uso_pre_aplicacao_no_mes":has_pre}
        sal_rows=sal_m[m]['rows'] or [(None,{})]
        for i,sr in sal_rows:
            if i is None:
                sid='sem_salario_no_mes'; dts=None; desc='sem_salario_canonico_no_mes'; vb=0.0; vl=0.0
            else:
                sid=sr.get('salario_id') or f'sal_{i}'; dts=sr.get('data_recebimento'); desc=sr.get('descricao') or sr.get('origem'); vb=_to_num(sr.get('valor_bruto')); vl=_to_num(sr.get('valor_liquido'))
            rec_c=rec_m[m]['rows'][0][1] if rec_m[m]['rows'] else {}
            ap_c=ap_m[m]['rows'][0][1] if ap_m[m]['rows'] else {}
            cls='classificacao_indefinida'; causa='indefinida'; acao='revisar_dados'; sev='media'; cad=tmp=sem=False; mot=False; obs=''
            if fonte_rec=='nao_localizada': cls='classificacao_indefinida'; causa='fonte_recebidos_nao_localizada'; acao='corrigir_extracao'; sev='alta'; obs='falha_extracao_fonte_essencial'
            elif s>0 and r==0 and a==0: cls='salario_sem_recebido_e_sem_aporte'; causa='sem_materializacao'; acao='rastrear salario->recebido->aporte'; sev='alta'; cad=True
            elif has_pre: cls='recebido_materializado_com_uso_pre_aplicacao'; causa='uso_pre_aplicacao'; acao='auditar_janela_temporal'; sev='alta'; tmp=True
            elif pay_sc: cls='pagamento_sem_fonte_temporal_no_mes'; causa='sem_cobertura'; acao='decompor_fonte_temporal'; sev='alta'; tmp=True
            elif s>0 and r>0 and a==0: cls='salario_com_recebido_mas_sem_aporte'; causa='recebido_sem_aporte'; acao='validar regra aporte'; sev='alta'; tmp=True
            elif s>0 and r==0 and a>0: cls='salario_com_aporte_mas_sem_recebido'; causa='aporte_sem_recebido'; acao='reconciliar_semantica'; sev='media'; sem=True
            elif s>0 and r==0: cls='salario_sem_recebido_auditavel'; causa='salario_sem_recebido'; acao='rastrear materializacao'; sev='alta'; cad=True
            elif s>0 and a==0: cls='salario_sem_aporte'; causa='salario_sem_aporte'; acao='validar inventario'; sev='media'; cad=True
            elif r>0 and s==0: cls='recebido_sem_salario_mesmo_mes'; causa='recebido_sem_salario'; acao='mapear origem'; sev='media'; sem=True
            elif abs(d_sr)>0.01: cls='divergencia_mensal_salarios_vs_recebidos'; causa='totais_nao_batem'; acao='decompor divergencia'; sev='alta' if abs(d_sr)>1000 else 'media'; sem=True
            elif abs(d_sa)>0.01: cls='divergencia_mensal_salarios_vs_aportes'; causa='totais_nao_batem'; acao='decompor divergencia'; sev='alta' if abs(d_sa)>1000 else 'media'; sem=True
            elif abs(d_ra)>0.01: cls='divergencia_mensal_recebidos_vs_aportes'; causa='totais_nao_batem'; acao='decompor divergencia'; sev='media'; sem=True
            elif s>r and r==a: cls='diferenca_semantica_salarios_vs_inventario'; causa='escopo_salarios_maior_que_materializacao'; acao='reconciliacao_semantica'; sev='media'; sem=True
            else: cls='mes_reconciliado_no_agregado'; causa='sem_divergencia'; acao='manter_monitoramento'; sev='baixa'
            rows.append({**base,'salario_id':sid,'data_recebimento_salario':dts,'descricao_salario':desc,'valor_bruto_salario':vb,'valor_liquido_salario':vl,'recebido_id_candidato':rec_c.get('recebido_id'),'data_recebido_candidato':rec_c.get('data_recebimento'),'valor_recebido_candidato':_to_num(rec_c.get('valor_liquido')),'lote_id_destino_candidato':ap_c.get('lote_id') or ap_c.get('lote_destino_id'),'data_aplicacao_lote':ap_c.get('data_aplicacao'),'valor_aporte_lote':_to_num(ap_c.get('valor_original')),'classe_lacuna':cls,'causa_provavel':causa,'acao_recomendada':acao,'severidade_diagnostica':sev,'pode_exigir_correcao_cadastro':cad,'pode_exigir_regra_temporal':tmp,'pode_exigir_reconciliacao_semantica':sem,'pode_exigir_motor':mot,'observacao_auditavel':obs})

    df=pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT,index=False)
    cnt=Counter(df['classe_lacuna']) if not df.empty else Counter()
    principal=cnt.most_common(1)[0][0] if cnt else 'nenhuma'
    classes_lacuna={"salario_sem_recebido_auditavel","salario_sem_aporte","salario_sem_recebido_e_sem_aporte","salario_com_recebido_mas_sem_aporte","salario_com_aporte_mas_sem_recebido","recebido_sem_salario_mesmo_mes","recebido_materializado_com_uso_pre_aplicacao","aporte_sem_vinculo_salarial_explicito","pagamento_sem_fonte_temporal_no_mes","divergencia_mensal_salarios_vs_recebidos","divergencia_mensal_salarios_vs_aportes","divergencia_mensal_recebidos_vs_aportes","diferenca_semantica_salarios_vs_inventario"}
    meses_com_lacuna = int(df.loc[df['classe_lacuna'].isin(classes_lacuna),'mes'].nunique()) if not df.empty else 0
    if not df.empty:
        df_mensal=df.drop_duplicates(subset=['mes'])[['mes','salario_mes_total','recebidos_mes_total','aportes_mes_total','pagamentos_historicos_mes_total','pagamentos_futuros_mes_total','pagamentos_futuros_sem_cobertura_total']]
    else:
        df_mensal=df
    if fonte_rec=='nao_localizada': status='falha_extracao_fonte_essencial'
    elif df.empty: status='lacuna_integracao_sem_linhas'
    else: status='lacuna_integracao_decomposta'
    print('=== AUDITORIA V17-F0-S.2 — LACUNA INTEGRACAO TEMPORAL ===')
    print('correcao_aplicada=V17-F0-S.2.1')
    print(f'qtd_salarios_canonicos={len(salarios)}')
    print(f'qtd_recebidos_auditaveis={len(recebidos)}')
    print(f'qtd_lotes_inventario={len(inventario)}')
    print(f'total_meses_auditados={len(df_mensal)}')
    print(f'total_linhas_lacuna={len(df)}')
    print(f'total_salarios_liquidos={df_mensal.salario_mes_total.sum() if not df_mensal.empty else 0.0:.2f}')
    print(f'total_recebidos_auditaveis={df_mensal.recebidos_mes_total.sum() if not df_mensal.empty else 0.0:.2f}')
    print(f'total_aportes={df_mensal.aportes_mes_total.sum() if not df_mensal.empty else 0.0:.2f}')
    print(f'diferenca_total_salarios_vs_recebidos={(df_mensal.salario_mes_total.sum()-df_mensal.recebidos_mes_total.sum()) if not df_mensal.empty else 0.0:.2f}')
    print(f'diferenca_total_salarios_vs_aportes={(df_mensal.salario_mes_total.sum()-df_mensal.aportes_mes_total.sum()) if not df_mensal.empty else 0.0:.2f}')
    print(f'meses_com_lacuna_integracao_temporal={meses_com_lacuna}')
    print(f'linhas_classe_salario_sem_recebido_e_sem_aporte={int((df.classe_lacuna=="salario_sem_recebido_e_sem_aporte").sum()) if not df.empty else 0}')
    print(f'linhas_classe_pagamento_sem_fonte_temporal_no_mes={int((df.classe_lacuna=="pagamento_sem_fonte_temporal_no_mes").sum()) if not df.empty else 0}')
    print(f'linhas_classe_uso_pre_aplicacao={int((df.classe_lacuna=="recebido_materializado_com_uso_pre_aplicacao").sum()) if not df.empty else 0}')
    print(f'linhas_classe_diferenca_semantica={int((df.classe_lacuna=="diferenca_semantica_salarios_vs_inventario").sum()) if not df.empty else 0}')
    print(f'principal_classe_lacuna={principal}')
    print(f'status_geral={status}')
    print(f'csv={OUT}')

if __name__=='__main__': main()
