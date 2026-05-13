from __future__ import annotations
import sys
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path: sys.path.insert(0, str(RAIZ))
from aplicacao.principal import carregar_contexto_e_saida

OUT_MENSAL = RAIZ / "saidas" / "diagnostico" / "auditoria_divergencias_salarios_recebidos_v17_f0_s1_mensal.csv"
OUT_SAL = RAIZ / "saidas" / "diagnostico" / "auditoria_divergencias_salarios_recebidos_v17_f0_s1_salarios.csv"
OUT_REC = RAIZ / "saidas" / "diagnostico" / "auditoria_divergencias_salarios_recebidos_v17_f0_s1_recebidos.csv"

def _n(v): return str(v or "").strip().lower()
def _f(v):
    try:
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    try: return float(v)
    except Exception: return 0.0

def _to_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    try:
        if pd.isna(v):
            return False
    except Exception:
        pass
    t = str(v).strip().lower()
    if t in {"true", "1", "sim", "s", "yes", "y"}:
        return True
    if t in {"false", "0", "nao", "não", "n", "no", "", "none", "nan", "null"}:
        return False
    return False

def _mes(v):
    try: return pd.to_datetime(v).strftime("%Y-%m")
    except Exception: return None

def _rows(obj):
    if obj is None: return []
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient="records")
    if isinstance(obj, list): return [dict(x) for x in obj if isinstance(x, dict)]
    return []

def _sem_cobertura(r):
    return (_n(r.get("Cobertura integral")) != "sim" or _n(r.get("Status recomendação")) == "sem_saldo_temporal_auditavel" or _n(r.get("Motivo bloqueio lote")) == "saldo_temporal_insuficiente_cumulativo")


def _rows_recebidos_auditaveis(obj):
    if obj is None:
        return [], "nao_localizada"
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records"), "objeto_dataframe"
    if isinstance(obj, list):
        return [dict(x) for x in obj if isinstance(x, dict)], "objeto_lista"
    for attr in ["quadro_recebidos_auditaveis", "quadro", "df", "dados", "recebidos_auditaveis"]:
        if not hasattr(obj, attr):
            continue
        v = getattr(obj, attr)
        if isinstance(v, pd.DataFrame):
            return v.to_dict(orient="records"), attr
        if isinstance(v, list):
            return [dict(x) for x in v if isinstance(x, dict)], attr
    return [], "nao_localizada"

def main():
    contexto, saida = carregar_contexto_e_saida()
    salarios = _rows(contexto.dados_operacionais.salarios_canonicos)
    recebidos, fonte_recebidos = _rows_recebidos_auditaveis(contexto.recebidos_auditaveis)
    inventario = _rows(contexto.dados_operacionais.inventario_canonico)
    gastos = _rows(contexto.dados_operacionais.gastos_canonicos)
    extrato = _rows(saida.extrato_futuro)

    sal_m = defaultdict(lambda: {"tot":0.0,"qtd":0})
    for i,r in enumerate(salarios,1):
        m=_mes(r.get("data_recebimento"));
        if not m: continue
        sal_m[m]["tot"] += _f(r.get("valor_liquido")); sal_m[m]["qtd"] += 1

    rec_m = defaultdict(lambda: {"tot":0.0,"qtd":0})
    rec_det=[]
    for i,r in enumerate(recebidos,1):
        m=_mes(r.get("data_recebimento"));
        if not m: continue
        vl=_f(r.get("valor_liquido")); rec_m[m]["tot"]+=vl; rec_m[m]["qtd"]+=1
        pre=_f(r.get("valor_pagamentos_pre_aplicacao")); sts=_n(r.get("status_recebido"))
        rec_det.append({"recebido_id":r.get("recebido_id") or f"rec_{i}","lote_id_origem":r.get("lote_id_origem") or r.get("lote_id"),"mes_recebimento":m,"data_recebimento":r.get("data_recebimento"),"data_aplicacao":r.get("data_aplicacao"),"valor_bruto":_f(r.get("valor_bruto")),"valor_liquido":vl,"status_recebido":r.get("status_recebido"),"destino_potencial":r.get("destino_potencial"),"lote_destino_id":r.get("lote_destino_id"),"situacao_investimento_origem":r.get("situacao_investimento_origem"),"qtd_pagamentos_vinculados":int(_f(r.get("qtd_pagamentos_vinculados"))),"valor_total_vinculado":_f(r.get("valor_total_vinculado")),"valor_pagamentos_pre_aplicacao":pre,"valor_residual_para_aplicacao_origem":_f(r.get("valor_residual_para_aplicacao_origem")),"salario_mes_total":0.0,"classificacao_recebido":"possivel_pagamento_antes_aporte" if (pre>0 or sts=="uso_pre_aplicacao_com_aporte_posterior") else "recebido_materializado","causa_provavel":"uso_pre_aplicacao" if (pre>0 or sts=="uso_pre_aplicacao_com_aporte_posterior") else "fluxo_materializado_inventario","recomendacao":"avaliar janela temporal pagamento->aporte" if (pre>0 or sts=="uso_pre_aplicacao_com_aporte_posterior") else "manter"})

    aporte_m=defaultdict(lambda:{"tot":0.0,"qtd":0})
    for r in inventario:
        if not _to_bool(r.get("aportado")): continue
        m=_mes(r.get("data_aplicacao"));
        if not m: continue
        aporte_m[m]["tot"]+=_f(r.get("valor_original")); aporte_m[m]["qtd"]+=1

    gh_m=defaultdict(lambda:{"tot":0.0,"qtd":0})
    for r in gastos:
        if not _to_bool(r.get("passado_pago_ate_data_referencia")): continue
        m=_mes(r.get("data"));
        if not m: continue
        gh_m[m]["tot"]+=_f(r.get("valor")); gh_m[m]["qtd"]+=1

    gf_m=defaultdict(lambda:{"tot":0.0,"qtd":0,"semcov_tot":0.0,"semcov_qtd":0})
    for r in extrato:
        m=_mes(r.get("Data"));
        if not m: continue
        v=_f(r.get("Valor")); gf_m[m]["tot"]+=v; gf_m[m]["qtd"]+=1
        if _sem_cobertura(r): gf_m[m]["semcov_tot"]+=v; gf_m[m]["semcov_qtd"]+=1

    meses=sorted(set(sal_m)|set(rec_m)|set(aporte_m)|set(gh_m)|set(gf_m))
    mens=[]; sal_det=[]; causas=[]
    for m in meses:
        s,r,a=sal_m[m]["tot"],rec_m[m]["tot"],aporte_m[m]["tot"]
        qsa,qra,qaa=sal_m[m]["qtd"],rec_m[m]["qtd"],aporte_m[m]["qtd"]
        gh, qgh=gh_m[m]["tot"], gh_m[m]["qtd"]; gf,qgf=gf_m[m]["tot"],gf_m[m]["qtd"]
        if fonte_recebidos == "nao_localizada":
            d_sr=None; d_sa=s-a; d_ra=None
            f_div_sr=False; f_div_sa=abs(d_sa)>0.01; f_div_ra=False
        else:
            d_sr=s-r; d_sa=s-a; d_ra=r-a
            f_div_sr=abs(d_sr)>0.01; f_div_sa=abs(d_sa)>0.01; f_div_ra=abs(d_ra)>0.01
        f_ssr=s>0 and r==0
        f_ssa=s>0 and a==0
        f_rss=r>0 and s==0
        poss_pre=any((x["mes_recebimento"]==m and x["classificacao_recebido"]=="possivel_pagamento_antes_aporte") for x in rec_det)
        f_sem=(s>0 and r==0 and qaa==0)
        f_lac=(s>0 and r==0 and a==0 and gf>0)
        if fonte_recebidos == "nao_localizada": cls="falha_extracao_recebidos_auditaveis"; causa="fonte_recebidos_auditaveis_nao_localizada"; recm="corrigir extracao diagnostica antes de inferir divergencia economica"
        elif f_lac: cls="lacuna_integracao_temporal"; causa="salario_sem_materializacao_em_recebidos_e_inventario_com_pressao_de_pagamentos"; recm="S.2: rastrear elo salario->fonte temporal"
        elif f_sem: cls="diferenca_semantica_salarios_vs_inventario"; causa="salarios_representam_fluxo_distinto_do_inventario_materializado"; recm="S.2: explicitar fronteira semantica"
        elif f_ssa: cls="salario_sem_aporte_no_mes"; causa="salario_sem_evento_aporte_no_inventario"; recm="S.2: investigar regra de aporte"
        elif f_ssr: cls="salario_sem_recebido_auditavel_no_mes"; causa="salario_sem_linha_correspondente_em_recebidos_auditaveis"; recm="S.2: rastrear materializacao"
        elif f_rss: cls="recebido_sem_salario_no_mes"; causa="recebido_materializado_sem_linha_salarial_no_mes"; recm="S.2: mapear origem nao salarial"
        elif poss_pre: cls="possivel_pagamento_antes_aporte"; causa="uso_pre_aplicacao_detectado_em_recebidos"; recm="S.2: auditar janela temporal"
        elif f_div_sr: cls="divergencia_mensal_salarios_vs_recebidos"; causa="totais_mensais_salarios_e_recebidos_nao_batem"; recm="S.2: decompor divergencia mensal salario->recebido"
        elif f_div_sa: cls="divergencia_mensal_salarios_vs_aportes"; causa="totais_mensais_salarios_e_aportes_nao_batem"; recm="S.2: decompor divergencia mensal salario->aporte"
        elif f_div_ra: cls="divergencia_mensal_recebidos_vs_aportes"; causa="totais_mensais_recebidos_e_aportes_nao_batem"; recm="S.2: decompor recebido->aporte"
        else: cls="mes_reconciliado"; causa="sem_divergencia_relevante"; recm="manter"
        causas.append(cls)
        mens.append({"mes":m,"salario_liquido_canonico":s,"qtd_salarios_canonicos":qsa,"recebidos_auditaveis_total":r,"qtd_recebidos_auditaveis":qra,"aportes_no_mes_total":a,"qtd_aportes_no_mes":qaa,"pagamentos_historicos_no_mes_total":gh,"qtd_pagamentos_historicos_no_mes":qgh,"pagamentos_futuros_no_mes_total":gf,"qtd_pagamentos_futuros_no_mes":qgf,"pagamentos_no_mes_total":gh+gf,"qtd_pagamentos_no_mes":qgh+qgf,"pagamentos_futuros_sem_cobertura_total":gf_m[m]["semcov_tot"],"qtd_pagamentos_futuros_sem_cobertura":gf_m[m]["semcov_qtd"],"diferenca_salario_vs_recebidos":d_sr,"diferenca_salario_vs_aportes":d_sa,"diferenca_recebidos_vs_aportes":d_ra,"flag_salario_sem_recebido":f_ssr,"flag_salario_sem_aporte":f_ssa,"flag_recebido_sem_salario_no_mes":f_rss,"flag_possivel_pagamento_antes_aporte":poss_pre,"flag_possivel_diferenca_semantica_salarios_vs_inventario":f_sem,"flag_possivel_lacuna_integracao_temporal":f_lac,"flag_divergencia_mensal_salarios_vs_recebidos":f_div_sr,"flag_divergencia_mensal_salarios_vs_aportes":f_div_sa,"flag_divergencia_mensal_recebidos_vs_aportes":f_div_ra,"classificacao_causa":cls,"causa_provavel":causa,"recomendacao_proxima_microetapa":recm})

    for i,r in enumerate(salarios,1):
        m=_mes(r.get("data_recebimento"));
        if not m: continue
        sliq=_f(r.get("valor_liquido")); smt,rt,at=sal_m[m]["tot"],rec_m[m]["tot"],aporte_m[m]["tot"]
        gh,gf=gh_m[m]["tot"],gf_m[m]["tot"]
        dsr,dsa=smt-rt,smt-at
        tem_r,tem_a=rt>0,at>0
        if sliq>0 and rt==0: cls="salario_em_mes_sem_recebido_auditavel"; causa="mes_sem_recebido_auditavel_materializado"; recm="S.2 rastrear materializacao mensal"
        elif sliq>0 and at==0: cls="salario_em_mes_sem_aporte"; causa="mes_sem_aporte_materializado"; recm="S.2 investigar regra de aporte"
        elif abs(dsr)>0.01: cls="salario_em_mes_com_divergencia_mensal_salarios_vs_recebidos"; causa="divergencia_no_nivel_agregado_mensal_salarios_vs_recebidos"; recm="S.2 decompor agregado mensal"
        elif abs(dsa)>0.01: cls="salario_em_mes_com_divergencia_mensal_salarios_vs_aportes"; causa="divergencia_no_nivel_agregado_mensal_salarios_vs_aportes"; recm="S.2 decompor agregado mensal"
        else: cls="salario_em_mes_reconciliado_no_agregado"; causa="agregado_mensal_reconciliado"; recm="manter"
        sal_det.append({"salario_id":r.get("salario_id") or f"sal_{i}","mes":m,"data_recebimento":r.get("data_recebimento"),"descricao_salario":r.get("descricao") or r.get("origem"),"valor_bruto_salario":_f(r.get("valor_bruto")),"valor_liquido_salario":sliq,"salario_mes_total":smt,"recebido_auditavel_mes_total":rt,"aporte_mes_total":at,"pagamentos_historicos_mes_total":gh,"pagamentos_futuros_mes_total":gf,"pagamento_mes_total":gh+gf,"diferenca_salario_mes_total_vs_recebido_mes_total":dsr,"diferenca_salario_mes_total_vs_aporte_mes_total":dsa,"tem_recebido_no_mes":tem_r,"tem_aporte_no_mes":tem_a,"tem_pagamento_historico_no_mes":gh>0,"tem_pagamento_futuro_no_mes":gf>0,"classificacao_salario":cls,"causa_provavel":causa,"recomendacao":recm})

    sal_mes_map={x["mes"]:x["salario_liquido_canonico"] for x in mens}
    for x in rec_det: x["salario_mes_total"]=sal_mes_map.get(x["mes_recebimento"],0.0)

    OUT_MENSAL.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(mens).to_csv(OUT_MENSAL,index=False)
    pd.DataFrame(sal_det).to_csv(OUT_SAL,index=False)
    pd.DataFrame(rec_det).to_csv(OUT_REC,index=False)

    dfm=pd.DataFrame(mens)
    num_cols=["salario_liquido_canonico","recebidos_auditaveis_total","aportes_no_mes_total","pagamentos_historicos_no_mes_total","pagamentos_futuros_no_mes_total","pagamentos_no_mes_total","pagamentos_futuros_sem_cobertura_total","diferenca_salario_vs_recebidos","diferenca_salario_vs_aportes","diferenca_recebidos_vs_aportes"]
    for col in num_cols:
        if col in dfm.columns:
            if col in {"diferenca_salario_vs_recebidos","diferenca_recebidos_vs_aportes"} and fonte_recebidos=="nao_localizada":
                continue
            dfm[col]=pd.to_numeric(dfm[col], errors="coerce").fillna(0.0)
    c=Counter(causas)
    principal = c.most_common(1)[0][0] if c else "indefinida"
    tem_meses = len(mens) > 0
    tem_salarios = len(salarios) > 0
    tem_recebidos = len(recebidos) > 0
    recebidos_localizados = fonte_recebidos != "nao_localizada"
    if not tem_meses:
        status_geral = "falha_decomposicao_diagnostica"
    elif not recebidos_localizados:
        status_geral = "falha_extracao_recebidos_auditaveis"
    elif tem_salarios and not tem_recebidos:
        status_geral = "divergencias_decompostas_sem_recebidos_auditaveis"
    else:
        status_geral = "divergencias_decompostas"
    print("=== AUDITORIA V17-F0-S.1 — DECOMPOSICAO SALARIOS X RECEBIDOS ===")
    print("correcao_aplicada=V17-F0-S.1.6")
    print(f"fonte_recebidos_auditaveis={fonte_recebidos}")
    print(f"qtd_salarios_canonicos={len(salarios)}")
    print(f"qtd_recebidos_auditaveis={len(recebidos)}")
    print(f"total_meses_auditados={len(dfm)}")
    print(f"meses_com_salario_sem_recebido={int(dfm['flag_salario_sem_recebido'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_salario_sem_aporte={int(dfm['flag_salario_sem_aporte'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_recebido_sem_salario={int(dfm['flag_recebido_sem_salario_no_mes'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_possivel_pagamento_antes_aporte={int(dfm['flag_possivel_pagamento_antes_aporte'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_possivel_diferenca_semantica_salarios_vs_inventario={int(dfm['flag_possivel_diferenca_semantica_salarios_vs_inventario'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_possivel_lacuna_integracao_temporal={int(dfm['flag_possivel_lacuna_integracao_temporal'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_divergencia_mensal_salarios_vs_recebidos={int(dfm['flag_divergencia_mensal_salarios_vs_recebidos'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_divergencia_mensal_salarios_vs_aportes={int(dfm['flag_divergencia_mensal_salarios_vs_aportes'].sum()) if not dfm.empty else 0}")
    print(f"meses_com_divergencia_mensal_recebidos_vs_aportes={int(dfm['flag_divergencia_mensal_recebidos_vs_aportes'].sum()) if not dfm.empty else 0}")
    print(f"total_salarios_liquidos={dfm['salario_liquido_canonico'].sum() if not dfm.empty else 0.0:.2f}")
    print(f"total_recebidos_auditaveis={dfm['recebidos_auditaveis_total'].sum() if not dfm.empty else 0.0:.2f}")
    print(f"total_aportes={dfm['aportes_no_mes_total'].sum() if not dfm.empty else 0.0:.2f}")
    print(f"total_pagamentos_historicos={dfm['pagamentos_historicos_no_mes_total'].sum() if not dfm.empty else 0.0:.2f}")
    print(f"total_pagamentos_futuros={dfm['pagamentos_futuros_no_mes_total'].sum() if not dfm.empty else 0.0:.2f}")
    print(f"diferenca_total_salarios_vs_recebidos={(dfm['salario_liquido_canonico'].sum()-dfm['recebidos_auditaveis_total'].sum()) if not dfm.empty else 0.0:.2f}")
    print(f"diferenca_total_salarios_vs_aportes={(dfm['salario_liquido_canonico'].sum()-dfm['aportes_no_mes_total'].sum()) if not dfm.empty else 0.0:.2f}")
    print(f"principal_causa_observada={principal}")
    print(f"status_geral={status_geral}")
    print(f"csv_mensal={OUT_MENSAL}")
    print(f"csv_salarios={OUT_SAL}")
    print(f"csv_recebidos={OUT_REC}")

if __name__=='__main__': main()
