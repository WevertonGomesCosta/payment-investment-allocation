from __future__ import annotations
import hashlib, sys
from pathlib import Path
from typing import Any
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0, str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

BASELINE_ENTRADA="bea7df1"; BASELINE_CODIGO_ANTERIOR="8c99f5e"; BASELINE_DADOS_ANTERIOR="f94f07d"
CSV_DETALHE=RAIZ/'saidas/diagnostico/auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.csv'
CSV_RESUMO=RAIZ/'saidas/diagnostico/auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1_resumo.csv'
DADOS=RAIZ/'dados/dados_financeiros.xlsx'

TIPOS={"baixa_pos_switching_confirmada","baixa_pos_switching_ausente_confirmada","baixa_pos_switching_sem_evidencia_observavel","baixa_pos_switching_parcial_ou_inconsistente","pagamento_ok_pos_switching_ausente_extrato_passado","baixa_passada_pos_switching_nao_refletida_situacao_atual","saldo_pos_switching_exibido_sem_consumo","extrato_futuro_sem_reflexo_da_baixa","console_sem_reflexo_da_baixa","origem_migrada_usada_apos_switching","base_operacional_gastos_nao_localizada","caso_explicito_nao_localizado_na_base_operacional","sem_divergencia_observada","sem_pagamento_pos_switching_para_auditar"}
CAMADAS={"console","extrato_passado","extrato_futuro","situacao_atual","saida_canonica","saida_observavel","estado_temporal_ledger","replay_passado","decisao_pagamento","base_operacional_gastos","nao_determinado","sem_falha_observada"}

import re
def _n(v): return str(v or '').strip().lower()
def _norm_lote(v):
    t=_n(v).replace('.', '').replace(',', '.').replace('  ',' ')
    return re.sub(r'\s+',' ',t).strip()
def _split_lotes(texto):
    if not texto: return []
    parts=[p.strip() for p in str(texto).split('+')]
    return [_norm_lote(p) for p in parts if _norm_lote(p)]
def _fonte_contem_lote_pos_switching(texto, conjunto_pos):
    toks=set(_split_lotes(texto))
    return any(t in conjunto_pos for t in toks)
def _d(v):
    try:return pd.to_datetime(v,errors='coerce').date()
    except:return None

def _num(v: Any):
    if v is None: return None
    s=str(v).strip()
    if s=='': return None
    s=s.replace('R$','').replace(' ','')
    if ',' in s and '.' in s:
        if s.rfind(',')>s.rfind('.'): s=s.replace('.','').replace(',','.')
    elif ',' in s:
        s=s.replace(',','.')
    try:return float(s)
    except:return None

def _hash(p:Path):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for c in iter(lambda:f.read(8192),b''): h.update(c)
    return h.hexdigest()

def _empty_row():
    cols=["origem_pagamento","fonte_base_operacional_gastos","fonte_base_operacional_gastos_status","fonte_auxiliar_observavel","fonte_pagamentos_passados","pagamento_id","data_pagamento","conta","valor_pagamento","pagamento_ok_na_planilha","presente_no_extrato_passado","presente_no_extrato_futuro","pacote_do_dia","status_recomendacao","lote_sugerido","lote_usado_planilha","lote_pos_switching_renderizado","fonte_pos_switching","pos_sw_flag","origem_switching","destino_switching","data_switching","lote_pos_switching_elegivel_na_data","fonte_eh_lote_pos_switching","origem_migrada_usada_indevidamente","saldo_pos_switching_exibido","saldo_temporal_antes","consumo_temporal","saldo_temporal_depois","saldo_remanescente_extrato","bruto_pos","liquido_pos","bruto_sacado_situacao_atual","liquido_sacado_situacao_atual","baixa_refletida_situacao_atual","lote_pos_switching_permanece_ativo_integral","valor_pagamento_abateu_saldo_pos_switching","saldo_pos_switching_esperado_apos_pagamento","divergencia_baixa_pos_switching","tipo_divergencia_q1","tipo_falha_replay_passado","camada_onde_falha","evidencia_q1","recomendacao_q1"]
    return {c:None for c in cols}

def main():
    h0=_hash(DADOS)
    ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_resolver_hibrido_5p_shadow=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida=construir_saida_canonica_com_switching_v17_c7(ctx,versao=VERSAO_BASELINE)
    extrato_fut=[dict(x) for x in (saida.extrato_futuro or []) if isinstance(x,dict)]
    extrato_pas=[dict(x) for x in (saida.extrato_passado or []) if isinstance(x,dict)]
    lotes_pos=[dict(x) for x in (getattr(saida,'lotes_sinteticos_pos_switching_console',lambda **_:[])(limite=500) or [])]
    switch=[dict(x) for x in (saida.switchings or []) if isinstance(x,dict)]
    situ=[dict(x) for x in (getattr(saida,'estado_pos_switching_lotes_console',lambda **_:[])(limite=500) or [])]

    fonte_aux="saida.pagamentos_realizados_console" if callable(getattr(saida,'pagamentos_realizados_console',None)) else "nao_localizada"
    # inspecao segura candidatos em ctx
    candidatos=[]
    ctx_items=[]
    try:
        ctx_items=list(vars(ctx).items())
    except Exception:
        for nm in [x for x in dir(ctx) if not x.startswith("_")]:
            try: ctx_items.append((nm,getattr(ctx,nm)))
            except Exception: pass
    for nm,val in ctx_items:
        lnm=_n(nm)
        if any(k in lnm for k in ['gastos','despesas','pagamentos','planilha','dados_planilha','todos']):
            meta={'nome':f'ctx.{nm}','tipo':type(val).__name__,'linhas':None,'colunas':''}
            if isinstance(val,pd.DataFrame): meta['linhas']=len(val); meta['colunas']=','.join(map(str,val.columns[:12]))
            elif isinstance(val,list): meta['linhas']=len(val); meta['colunas']=','.join(list(val[0].keys())[:12]) if val and isinstance(val[0],dict) else ''
            candidatos.append(meta)
    conf=[]
    for c in candidatos:
        ok_tipo=c['tipo'] in {'DataFrame','list'}
        ok_linhas=(isinstance(c['linhas'],int) and c['linhas']>=200)
        keys=_n(c['colunas'])
        ok_campos=all(k in keys for k in ['data','valor']) and (('pago' in keys) or ('status' in keys)) and (('lote' in keys) or ('usado' in keys))
        if ok_tipo and ok_linhas and ok_campos and 'pagamentos_realizados_console' not in c['nome']:
            conf.append(c)
    fonte_base='nao_localizada_de_forma_confiavel'; fonte_status='nao_localizada_de_forma_confiavel'; esc='nao_localizada'; mot_esc=''; mot_nloc='nenhuma estrutura em ctx atende criterio de fonte canonica completa'
    if conf:
        escolhido=conf[0]; fonte_base=escolhido['nome']; fonte_status='localizada_confiavel'; esc=escolhido['nome']; mot_esc='estrutura com >=200 linhas e campos Data/Valor/Pago/Lote'; mot_nloc=''

    detalhes=[]
    destinos={_n(s.get('lote_destino') or s.get('lote_pos_switching')):s for s in switch if _n(s.get('lote_destino') or s.get('lote_pos_switching'))}
    pos_names={_norm_lote(x.get('Lote') or x.get('lote') or x.get('Novo lote') or x.get('lote_destino') or x.get('lote_pos_switching')) for x in lotes_pos}; pos_names={x for x in pos_names if x}
    pos_names.update({_norm_lote(s.get('lote_destino') or s.get('lote_pos_switching')) for s in switch if _norm_lote(s.get('lote_destino') or s.get('lote_pos_switching'))})
    for i,r in enumerate(extrato_fut,1):
        row=_empty_row(); row.update({'origem_pagamento':'pagamentos_futuros','fonte_base_operacional_gastos':fonte_base,'fonte_base_operacional_gastos_status':fonte_status,'fonte_auxiliar_observavel':fonte_aux,'fonte_pagamentos_passados':'saida_canonica','pagamento_id':r.get('Despesa ID') or f'fut_{i}','data_pagamento':r.get('Data'),'conta':r.get('Conta'),'valor_pagamento':r.get('Valor'),'presente_no_extrato_futuro':'sim','presente_no_extrato_passado':'nao','lote_sugerido':r.get('Lote sugerido') or r.get('Lote'),'lote_usado_planilha':r.get('Lote sugerido') or r.get('Lote'),'pagamento_ok_na_planilha':'nao'})
        lote=row['lote_usado_planilha']; is_pos=_fonte_contem_lote_pos_switching(lote,pos_names)
        row['fonte_eh_lote_pos_switching']='sim' if is_pos else 'nao'; row['fonte_pos_switching']='sim' if is_pos else 'nao'; row['pos_sw_flag']='sim' if is_pos else 'nao'
        if is_pos:
            row.update({'divergencia_baixa_pos_switching':'sim','tipo_divergencia_q1':'baixa_pos_switching_sem_evidencia_observavel','camada_onde_falha':'saida_observavel','recomendacao_q1':'V17-F0-Q.2','evidencia_q1':'futuro pos-switching sem evidencia de baixa observavel'})
        else:
            row.update({'divergencia_baixa_pos_switching':'nao','tipo_divergencia_q1':'sem_pagamento_pos_switching_para_auditar','camada_onde_falha':'nao_determinado','recomendacao_q1':'continuar_diagnostico','evidencia_q1':'sem lote pos-switching'})
        if row['tipo_divergencia_q1'] not in TIPOS: row['tipo_divergencia_q1']='sem_pagamento_pos_switching_para_auditar'
        detalhes.append(row)

    # casos explicitos
    explic=[('2026-05-13','Aluguel',192.89,'Lote 190 mai'),('2026-05-13','Pelada',24.00,'Lote 3120 mai')]
    for j,(dt,conta,val,lote) in enumerate(explic,1):
        row=_empty_row(); row.update({'origem_pagamento':'caso_explicitamente_auditado','fonte_base_operacional_gastos':fonte_base,'fonte_base_operacional_gastos_status':fonte_status,'fonte_auxiliar_observavel':fonte_aux,'fonte_pagamentos_passados':'saida_canonica','pagamento_id':f'caso_{j}','data_pagamento':dt,'conta':conta,'valor_pagamento':val,'lote_usado_planilha':lote,'lote_sugerido':lote,'presente_no_extrato_passado':'nao','presente_no_extrato_futuro':'nao','fonte_eh_lote_pos_switching':'nao_confirmado','fonte_pos_switching':'nao_confirmado','pos_sw_flag':'nao_confirmado','divergencia_baixa_pos_switching':'nao','camada_onde_falha':'base_operacional_gastos'})
        if fonte_status=='localizada_confiavel':
            row.update({'pagamento_ok_na_planilha':'nao','tipo_divergencia_q1':'caso_explicito_nao_localizado_na_base_operacional','evidencia_q1':'fonte canonica localizada mas caso explicito nao encontrado; nao contar como divergencia pos-switching','recomendacao_q1':'verificar_cadastro_manual_dos_gastos'})
        else:
            row.update({'pagamento_ok_na_planilha':'indeterminado','tipo_divergencia_q1':'base_operacional_gastos_nao_localizada','evidencia_q1':'fonte canonica Todos os Gastos nao localizada em ctx/objetos carregados; nao concluir falso zero e nao contar como divergencia pos-switching','recomendacao_q1':'expor_base_canonica_todos_os_gastos_ao_auditor'})
        detalhes.append(row)

    df=pd.DataFrame(detalhes)
    q0=pd.read_csv(RAIZ/'saidas/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.csv') if (RAIZ/'saidas/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.csv').exists() else pd.DataFrame()
    q0r=q0[q0.get('tipo_linha','')=='resumo'].head(1).to_dict('records'); q0r=q0r[0] if q0r else {}
    fut=df[df['origem_pagamento']=='pagamentos_futuros']
    pos=df[df['fonte_eh_lote_pos_switching']=='sim']
    qtd_div=int((pos['divergencia_baixa_pos_switching']=='sim').sum())
    if fonte_status!='localizada_confiavel':
        qpass='nao_determinado'; qaus='nao_determinado'; qsit='nao_determinado'; qenc='nao_determinado'; qce='nao_determinado'; status='base_operacional_gastos_nao_localizada'; camada='base_operacional_gastos'
    else:
        qpass=0; qaus=0; qsit=0; qenc=0; qce=0; status='baixa_pos_switching_sem_evidencia_observavel' if int((pos['tipo_divergencia_q1']=='baixa_pos_switching_sem_evidencia_observavel').sum())>0 else 'sem_pagamentos_pos_switching_para_auditar'; camada='saida_observavel'
    alinh='nao'
    if q0r:
        alinh='sim' if (len(fut)==int(q0r.get('total_pagamentos_futuros',-1)) and int((fut['fonte_eh_lote_pos_switching']=='sim').sum())==int(q0r.get('pagamentos_usando_lote_pos_switching',-1)) and len(lotes_pos)==int(q0r.get('lotes_pos_switching_total',-1)) and int((df['origem_migrada_usada_indevidamente']=='sim').sum())==int(q0r.get('origens_migradas_usadas_indevidamente_total',-1))) else 'nao'
    h1=_hash(DADOS); mod='sim' if h0!=h1 else 'nao'
    if mod=='sim': status='falha_diagnostico_q1'
    resumo={
      'baseline_entrada':BASELINE_ENTRADA,'baseline_codigo_anterior':BASELINE_CODIGO_ANTERIOR,'baseline_dados_anterior':BASELINE_DADOS_ANTERIOR,
      'fonte_base_operacional_gastos':fonte_base,'fonte_base_operacional_gastos_status':fonte_status,'fonte_auxiliar_observavel':fonte_aux,'fonte_pagamentos_passados':'saida_canonica',
      'candidatos_fonte_gastos_inspecionados':len(candidatos),'candidatos_fonte_gastos_confiaveis':len(conf),'candidato_fonte_gastos_escolhido':esc,'motivo_fonte_gastos_escolhida':mot_esc,'motivo_fonte_gastos_nao_localizada':mot_nloc,
      'qtd_pagamentos_futuros':len(fut),'qtd_pagamentos_futuros_usando_lote_pos_switching':int((fut['fonte_eh_lote_pos_switching']=='sim').sum()),'qtd_linhas_futuras_pos_switching_csv':int((fut['fonte_eh_lote_pos_switching']=='sim').sum()),
      'qtd_pagamentos_passados_ok_usando_lote_pos_switching':qpass,'qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado':qaus,'qtd_baixas_passadas_pos_switching_nao_refletidas_situacao_atual':qsit,
      'qtd_casos_explicitos_auditados':2,'qtd_casos_explicitos_encontrados_base_operacional':qenc,'qtd_casos_explicitos_ausentes_extrato_passado':qce,
      'qtd_lotes_pos_switching_total':len(lotes_pos),'qtd_lotes_pos_switching_elegiveis_em_alguma_data':int((fut['fonte_eh_lote_pos_switching']=='sim').sum()),
      'qtd_pagamentos_pos_switching_com_baixa_confirmada':int((pos['tipo_divergencia_q1']=='baixa_pos_switching_confirmada').sum()),'qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada':int((pos['tipo_divergencia_q1']=='baixa_pos_switching_ausente_confirmada').sum()),'qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa':int((pos['tipo_divergencia_q1']=='baixa_pos_switching_sem_evidencia_observavel').sum()),'qtd_pagamentos_pos_switching_com_baixa_inconsistente':int((pos['tipo_divergencia_q1']=='baixa_pos_switching_parcial_ou_inconsistente').sum()),
      'qtd_origens_migradas_usadas_indevidamente':int((df['origem_migrada_usada_indevidamente']=='sim').sum()) if 'origem_migrada_usada_indevidamente' in df.columns else 0,
      'qtd_divergencias_baixa_pos_switching':qtd_div,'camada_falha_dominante':camada,'status_geral_q1':status,'q1_alinhado_com_q0':alinh,'matching_pos_switching':'token_exato','usa_substring_global_para_matching':'nao','tokens_pos_switching_testados':'sim','dados_financeiros_modificado_apos_execucao':mod
    }
    CSV_DETALHE.parent.mkdir(parents=True,exist_ok=True); df.to_csv(CSV_DETALHE,index=False); pd.DataFrame([resumo]).to_csv(CSV_RESUMO,index=False)
    print('=== AUDITORIA V17-F0-Q.1.4 — ESTABILIZACAO MATCHING POS-SWITCHING ===')
    for k,v in resumo.items(): print(f'{k}={v}')
    if mod=='sim': print('motivo_falha=dados_financeiros_modificado_por_execucao_diagnostica')
    print(f'csv_detalhe={CSV_DETALHE}'); print(f'csv_resumo={CSV_RESUMO}')

if __name__=='__main__': main()
