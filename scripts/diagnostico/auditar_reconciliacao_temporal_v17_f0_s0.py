from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from aplicacao.principal import carregar_contexto_e_saida

ARQ = RAIZ / "saidas" / "diagnostico" / "auditoria_reconciliacao_temporal_v17_f0_s0.csv"


def _norm(v): return str(v or "").strip().lower()
def _to_num(v):
    try: return float(v)
    except Exception: return 0.0

def _to_mes(v):
    try: return pd.to_datetime(v).strftime("%Y-%m")
    except Exception: return None

def _get_any(d, campos):
    for c in campos:
        if c in d and d[c] not in (None, ""): return d[c]
    return None

def _rows_generico(obj):
    if obj is None: return []
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient="records")
    if isinstance(obj, list): return [dict(x) for x in obj if isinstance(x, dict)]
    return []

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

def _mes_valor_qtd(rows, campos_data, campos_valor, filtro=None):
    agg = defaultdict(lambda: {"total": 0.0, "qtd": 0})
    for r in rows:
        if not isinstance(r, dict): continue
        if filtro and not filtro(r): continue
        mes = _to_mes(_get_any(r, campos_data))
        if not mes: continue
        agg[mes]["total"] += _to_num(_get_any(r, campos_valor))
        agg[mes]["qtd"] += 1
    return agg

def _detectar_resumo_temporal(resumo_rows):
    if not resumo_rows: return False, False, None
    cols = {k for r in resumo_rows for k in r.keys()}
    temporal_cols = {"Data", "data", "data_recebimento", "Data Recebimento", "mes", "Mês"}
    has_temporal = any(c in cols for c in temporal_cols)
    has_kpi = ("Métrica" in cols or "Metrica" in cols) and ("Valor" in cols or "valor" in cols)
    total_global = None
    if has_kpi:
        for r in resumo_rows:
            met = _norm(r.get("Métrica") if "Métrica" in r else r.get("Metrica"))
            if met in {"valor total bruto", "total valor bruto", "valor_total_bruto"}:
                total_global = _to_num(r.get("Valor") if "Valor" in r else r.get("valor"))
                break
    return has_temporal, has_kpi, total_global


def main():
    contexto, saida = carregar_contexto_e_saida()

    salarios = _rows_generico(contexto.dados_operacionais.salarios_canonicos)
    recebidos, fonte_recebidos = _rows_recebidos_auditaveis(contexto.recebidos_auditaveis)
    resumo_rows = _rows_generico(saida.resumo_recebidos)
    extrato = _rows_generico(saida.extrato_futuro)
    inventario = _rows_generico(contexto.dados_operacionais.inventario_canonico)
    switchings = _rows_generico(contexto.dados_operacionais.switching_canonico)

    resumo_temporal, resumo_kpi, total_global_resumo = _detectar_resumo_temporal(resumo_rows)

    sal_bruto = _mes_valor_qtd(salarios, ["data_recebimento"], ["valor_bruto"])
    sal_liq = _mes_valor_qtd(salarios, ["data_recebimento"], ["valor_liquido"])
    rec_mes = _mes_valor_qtd(recebidos, ["Data", "Data Recebimento", "data_recebimento", "Recebimento"], ["valor_liquido", "Valor líquido", "valor", "Valor", "valor_bruto", "Valor bruto"])
    resumo_mes = _mes_valor_qtd(resumo_rows, ["Data", "data", "Data Recebimento", "data_recebimento", "mes", "Mês"], ["Valor", "valor", "total", "valor_total", "Valor líquido"]) if resumo_temporal else defaultdict(lambda: {"total": None, "qtd": 0})
    pag_mes = _mes_valor_qtd(extrato, ["Data"], ["Valor"])
    aportes_mes = _mes_valor_qtd(inventario, ["data_aplicacao", "data_recebimento", "Data"], ["valor_original", "Valor", "valor_liquido"], filtro=lambda r: bool(r.get("aportado")) is True)
    sw_mes = _mes_valor_qtd(switchings, ["data_switching", "data_aplicacao", "data_recebimento", "Data"], ["valor_liquido_migrado", "valor_liquido_origem", "Valor líquido origem", "Valor"])

    pag_sem_cov = defaultdict(lambda: {"qtd": 0, "total": 0.0})
    for r in extrato:
        mes = _to_mes(r.get("Data"))
        if not mes: continue
        sem_cov = (_norm(r.get("Cobertura integral")) != "sim" or _norm(r.get("Status recomendação")) == "sem_saldo_temporal_auditavel" or _norm(r.get("Motivo bloqueio lote")) == "saldo_temporal_insuficiente_cumulativo")
        if sem_cov:
            pag_sem_cov[mes]["qtd"] += 1
            pag_sem_cov[mes]["total"] += _to_num(r.get("Valor"))

    recv_futuro_nao_aportado_mes = defaultdict(int)
    for r in inventario:
        mes = _to_mes(_get_any(r, ["data_aplicacao", "data_recebimento", "Data"]))
        if not mes: continue
        if bool(r.get("recebido_futuro_nao_disponivel")) or _norm(r.get("situacao_temporal")) in {"recebido_futuro_nao_disponivel", "futuro_nao_disponivel"}:
            recv_futuro_nao_aportado_mes[mes] += 1

    meses = sorted(set(list(sal_bruto.keys()) + list(sal_liq.keys()) + list(rec_mes.keys()) + (list(resumo_mes.keys()) if resumo_temporal else []) + list(pag_mes.keys()) + list(aportes_mes.keys()) + list(sw_mes.keys()) + list(pag_sem_cov.keys()) + list(recv_futuro_nao_aportado_mes.keys())))
    recebidos_localizados = fonte_recebidos != "nao_localizada"

    rows = []
    for mes in meses:
        salario_bruto, salario_liquido = sal_bruto[mes]["total"], sal_liq[mes]["total"]
        qtd_sal = sal_liq[mes]["qtd"] or sal_bruto[mes]["qtd"]
        receb_total, qtd_receb = rec_mes[mes]["total"], rec_mes[mes]["qtd"]
        resumo_total = resumo_mes[mes]["total"] if resumo_temporal else None
        pag_total, qtd_pag = pag_mes[mes]["total"], pag_mes[mes]["qtd"]
        qtd_sem_cov, val_sem_cov = pag_sem_cov[mes]["qtd"], pag_sem_cov[mes]["total"]
        aporte_total, qtd_aporte = aportes_mes[mes]["total"], aportes_mes[mes]["qtd"]
        sw_total, qtd_sw = sw_mes[mes]["total"], sw_mes[mes]["qtd"]
        saldo_est = receb_total - aporte_total - pag_total

        d_sal_rec = (salario_liquido - receb_total) if recebidos_localizados else None
        d_rec_res = (receb_total - resumo_total) if (resumo_temporal and resumo_total is not None) else None

        f_sal_sem_aporte = salario_liquido > 0 and qtd_aporte == 0
        f_pag_sem_fonte = qtd_sem_cov > 0
        f_rec_fut_na = recv_futuro_nao_aportado_mes[mes] > 0
        f_div_sal_rec = recebidos_localizados and d_sal_rec is not None and abs(d_sal_rec) > 0.01
        f_div_rec_res = resumo_temporal and d_rec_res is not None and abs(d_rec_res) > 0.01
        f_div_temp = f_div_sal_rec or f_div_rec_res

        if not recebidos_localizados:
            cls = "falha_extracao_recebidos_auditaveis"
            causa, reco = "fonte_recebidos_auditaveis_nao_localizada", "corrigir extracao diagnostica antes de inferir divergencia economica"
        else:
            flags = [f_sal_sem_aporte, f_pag_sem_fonte, f_rec_fut_na, f_div_temp]
            if sum(flags) > 1: cls = "multiplas_divergencias"
            elif f_sal_sem_aporte: cls = "salario_sem_aporte"
            elif f_pag_sem_fonte: cls = "pagamento_sem_fonte_temporal"
            elif f_rec_fut_na: cls = "recebido_futuro_nao_aportado"
            elif f_div_sal_rec: cls = "divergencia_salario_recebido"
            elif f_div_rec_res: cls = "divergencia_recebido_resumo"
            else: cls = "temporal_reconciliado"
            causa, reco = "sem_divergencia_relevante", "manter_monitoramento"
            if f_sal_sem_aporte: causa, reco = "salario_canonico_sem_aporte_no_mes", "S.1: rastrear salario -> recebido -> aporte"
            elif f_pag_sem_fonte: causa, reco = "pagamentos_futuros_sem_fonte_temporal_reconciliada", "S.1/S.2: decompor falta real de fonte vs lacuna de integracao"
            elif f_rec_fut_na: causa, reco = "recebido_futuro_nao_aportado_ou_nao_materializado", "auditoria especifica de materializacao futura"
            elif f_div_sal_rec: causa, reco = "divergencia_entre_salarios_canonicos_e_recebidos_auditaveis", "S.1: reconciliar trilha de recebimento"
            elif f_div_rec_res: causa, reco = "divergencia_entre_recebidos_auditaveis_e_resumo_recebidos", "S.1: alinhar agregacao de resumo recebidos"

        rows.append({"mes": mes, "salario_bruto_canonico": salario_bruto, "salario_liquido_canonico": salario_liquido, "qtd_salarios_canonicos": qtd_sal, "recebidos_auditaveis_total": receb_total, "qtd_recebidos_auditaveis": qtd_receb, "resumo_recebidos_total": resumo_total, "resumo_recebidos_temporal": "sim" if resumo_temporal else "nao", "pagamentos_futuros_total": pag_total, "qtd_pagamentos_futuros": qtd_pag, "qtd_pagamentos_sem_cobertura_integral": qtd_sem_cov, "valor_pagamentos_sem_cobertura_integral": val_sem_cov, "aportes_no_mes_total": aporte_total, "qtd_aportes_no_mes": qtd_aporte, "switchings_no_mes": sw_total, "qtd_switchings_no_mes": qtd_sw, "saldo_temporal_estimado_mes": saldo_est, "diferenca_salarios_vs_recebidos": d_sal_rec, "diferenca_recebidos_vs_resumo": d_rec_res, "flag_salario_sem_aporte": f_sal_sem_aporte, "flag_pagamento_sem_fonte_temporal": f_pag_sem_fonte, "flag_recebido_futuro_nao_aportado": f_rec_fut_na, "flag_divergencia_temporal": f_div_temp, "classificacao_mes": cls, "causa_provavel": causa, "recomendacao_proxima_microetapa": reco})

    df = pd.DataFrame(rows)
    ARQ.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARQ, index=False)

    total_rec = df["recebidos_auditaveis_total"].sum() if not df.empty else 0.0
    total_global_diff = (total_rec - total_global_resumo) if total_global_resumo is not None else None
    meses_sal_sem_aporte = int(df["flag_salario_sem_aporte"].sum()) if not df.empty else 0
    meses_pag_sem_fonte = int(df["flag_pagamento_sem_fonte_temporal"].sum()) if not df.empty else 0
    meses_div_sal_rec = int(df["diferenca_salarios_vs_recebidos"].abs().fillna(0).gt(0.01).sum()) if not df.empty else 0
    meses_recv_fut = int(df["flag_recebido_futuro_nao_aportado"].sum()) if not df.empty else 0
    status = "temporal_reconciliado" if (meses_sal_sem_aporte + meses_pag_sem_fonte + meses_div_sal_rec + meses_recv_fut) == 0 else "temporal_com_divergencias_diagnosticadas"

    print("=== AUDITORIA V17-F0-S.0 — RECONCILIACAO TEMPORAL MENSAL ===")
    print("correcao_aplicada=V17-F0-S.0.1")
    print(f"fonte_recebidos_auditaveis={fonte_recebidos}")
    print(f"qtd_linhas_recebidos_auditaveis={len(recebidos)}")
    print(f"resumo_recebidos_temporal={'sim' if resumo_temporal else 'nao'}")
    print(f"resumo_recebidos_usado_apenas_como_kpi_global={'sim' if (not resumo_temporal and resumo_kpi) else 'nao'}")
    if total_global_resumo is not None: print(f"total_global_resumo_recebidos={total_global_resumo:.2f}")
    if total_global_diff is not None: print(f"diferenca_global_recebidos_vs_resumo={total_global_diff:.2f}")
    if fonte_recebidos == "nao_localizada": print("aviso_recebidos_auditaveis=fonte_nao_localizada_sem_inferencia_de_divergencia_economica")
    print(f"total_meses_auditados={len(df)}")
    print(f"meses_com_salario_sem_aporte={meses_sal_sem_aporte}")
    print(f"meses_com_pagamento_sem_fonte_temporal={meses_pag_sem_fonte}")
    print(f"meses_com_divergencia_salario_x_recebidos={meses_div_sal_rec}")
    print(f"meses_com_recebidos_futuros_ainda_nao_aportados={meses_recv_fut}")
    print(f"total_reconciliado_salarios={df['salario_liquido_canonico'].sum() if not df.empty else 0.0:.2f}")
    print(f"total_reconciliado_recebidos={total_rec:.2f}")
    print(f"total_pagamentos_futuros={df['pagamentos_futuros_total'].sum() if not df.empty else 0.0:.2f}")
    print(f"status_geral={status}")
    print(f"csv={ARQ}")


if __name__ == "__main__":
    main()
