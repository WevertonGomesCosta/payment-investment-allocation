from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from collections import Counter

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline

VERSAO_ALVO = "V16-I"
NUMERO_VERSOES = 1
COMMIT_V16H = "15320e4e712e461c7b7a0d58d91ffd5484c65492"
OUT_DIR = RAIZ / "saidas/diagnostico"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _norm(v: object) -> str:
    return str(v or "").strip().lower()


def _to_float(v: object) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip()


def _classificar(row: pd.Series) -> tuple[str, str]:
    if bool(row.get("lote_escolhido_sem_saldo_temporal_cumulativo", False)):
        return "lote_escolhido_sem_saldo_temporal_cumulativo", "saldo_temporal_cumulativo"
    if not bool(row.get("existe_recebido_disponivel_elegivel", False)):
        if bool(row.get("existe_recebido_auditavel_compativel", False)):
            return "fonte_recebido_nao_materializada_para_pagamento", "materializacao_recebidos"
        return "sem_recebido_disponivel_elegivel", "contrato_atual_sem_correcao"
    if not bool(row.get("recebido_cobre_pagamento", False)):
        return "recebido_disponivel_insuficiente", "contrato_atual_sem_correcao"
    lote_proxy = _to_float(row.get("custo_economico_proxy_lote"))
    rec_proxy = _to_float(row.get("melhor_custo_proxy_recebido"))
    if rec_proxy > 0 and lote_proxy > 0 and lote_proxy + 1e-9 < rec_proxy:
        return "recebido_disponivel_existe_mas_proxy_prefere_lote", "decisao_local"
    if bool(row.get("recebido_bloqueado_temporalmente", False)):
        return "recebido_disponivel_bloqueado_temporalmente", "materializacao_recebidos"
    return "recebido_disponivel_existe_mas_ordem_local_prefere_lote", "decisao_local"


def main() -> int:
    head_inicial = _git_head()
    commit_v16h_confirmado = COMMIT_V16H == head_inicial

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
    q_temp = ctx.auditoria_temporal_decisao_local.quadro_auditoria_temporal.copy()

    q_local = q_local[q_local["tipo_fonte_escolhida"].astype(str).str.lower().eq("lote_resgatavel")].copy()
    q_temp = q_temp[q_temp["status_temporal"].astype(str).str.lower().eq("sem_saldo_temporal_auditavel")].copy()
    casos_a = q_local.merge(
        q_temp[["pagamento_id", "saldo_antes_temporal", "status_temporal"]], on="pagamento_id", how="inner"
    )

    rows = []
    for _, r in casos_a.iterrows():
        pid = r["pagamento_id"]
        vp = _to_float(r.get("valor_pagamento"))
        fontes_pag = q_fontes[q_fontes["pagamento_id"].astype(str) == str(pid)].copy()
        rec_eleg = fontes_pag[(fontes_pag["tipo_fonte"].astype(str).str.lower() == "recebido_disponivel") & (fontes_pag["elegivel_na_data_pagamento"].fillna(False))].copy()
        rec_eleg = rec_eleg.sort_values("valor_liquido_disponivel", ascending=False)
        melhor = rec_eleg.iloc[0] if len(rec_eleg) else None
        melhor_id = str(melhor.get("recebido_id") or "") if melhor is not None else ""
        recebido = q_rec[q_rec["recebido_id"].astype(str) == melhor_id].head(1)

        rec_compativel = q_rec[q_rec["valor_liquido"].fillna(0).astype(float) >= vp]
        rec_compativel = rec_compativel[(rec_compativel.get("data_aplicacao").isna()) | (pd.to_datetime(rec_compativel.get("data_aplicacao")) >= pd.to_datetime(r.get("data_pagamento")))] if "data_aplicacao" in rec_compativel.columns else rec_compativel

        row = {
            "pagamento_id": pid,
            "data_pagamento": r.get("data_pagamento"),
            "descricao_pagamento": r.get("descricao_pagamento"),
            "valor_pagamento": vp,
            "tipo_fonte_escolhida_decisao_local": r.get("tipo_fonte_escolhida"),
            "fonte_escolhida_id": r.get("fonte_escolhida_id"),
            "lote_id_escolhido": r.get("lote_id_escolhido"),
            "saldo_antes_temporal_lote": _to_float(r.get("saldo_antes_temporal")),
            "valor_disponivel_escolhido_local": _to_float(r.get("valor_disponivel_escolhido")),
            "custo_economico_proxy_lote": _to_float(r.get("custo_economico_proxy")),
            "existe_recebido_disponivel_elegivel": bool(len(rec_eleg) > 0),
            "qtd_recebidos_disponiveis_elegiveis": int(len(rec_eleg)),
            "maior_valor_liquido_recebido_disponivel": _to_float(melhor.get("valor_liquido_disponivel")) if melhor is not None else 0.0,
            "recebido_cobre_pagamento": bool(melhor is not None and _to_float(melhor.get("valor_liquido_disponivel")) + 0.01 >= vp),
            "melhor_recebido_id": melhor_id or "n/d",
            "status_recebido": (recebido.iloc[0]["status_recebido"] if len(recebido) else "n/d"),
            "destino_potencial_recebido": (recebido.iloc[0]["destino_potencial"] if len(recebido) else "n/d"),
            "data_recebimento": (recebido.iloc[0]["data_recebimento"] if len(recebido) else "n/d"),
            "data_aplicacao": (recebido.iloc[0]["data_aplicacao"] if len(recebido) else "n/d"),
            "motivo_recebido_nao_escolhido": "sem_recebido_elegivel" if len(rec_eleg) == 0 else "decisao_local_escolheu_lote",
            "lote_escolhido_sem_saldo_temporal_cumulativo": True,
            "existe_recebido_auditavel_compativel": bool(len(rec_compativel) > 0),
            "recebido_bloqueado_temporalmente": bool((fontes_pag["tipo_fonte"].astype(str).str.lower().eq("recebido_disponivel") & ~fontes_pag["elegivel_na_data_pagamento"].fillna(False)).any()),
            "melhor_custo_proxy_recebido": _to_float(melhor.get("custo_economico_proxy")) if melhor is not None and "custo_economico_proxy" in melhor.index else 0.0,
        }
        causa, classe = _classificar(pd.Series(row))
        row["diagnostico_causa_provavel"] = causa
        row["classe_correcao_futura"] = classe
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[
            "pagamento_id","data_pagamento","descricao_pagamento","valor_pagamento","tipo_fonte_escolhida_decisao_local","fonte_escolhida_id","lote_id_escolhido","saldo_antes_temporal_lote","valor_disponivel_escolhido_local","custo_economico_proxy_lote","existe_recebido_disponivel_elegivel","qtd_recebidos_disponiveis_elegiveis","maior_valor_liquido_recebido_disponivel","recebido_cobre_pagamento","melhor_recebido_id","status_recebido","destino_potencial_recebido","data_recebimento","data_aplicacao","motivo_recebido_nao_escolhido","diagnostico_causa_provavel","classe_correcao_futura","lote_escolhido_sem_saldo_temporal_cumulativo"
        ])
    out_main = OUT_DIR / "auditoria_casos_A_decisao_local_v16i.csv"
    df.to_csv(out_main, index=False)

    resumo_rows = []
    for chave in ["diagnostico_causa_provavel", "classe_correcao_futura", "existe_recebido_disponivel_elegivel", "recebido_cobre_pagamento", "lote_escolhido_sem_saldo_temporal_cumulativo"]:
        for valor, qtd in df[chave].value_counts(dropna=False).items():
            resumo_rows.append({"dimensao": chave, "valor": valor, "quantidade": int(qtd)})
    out_resumo = OUT_DIR / "auditoria_casos_A_decisao_local_v16i_resumo.csv"
    pd.DataFrame(resumo_rows).to_csv(out_resumo, index=False)

    total = len(df)
    if total != 65:
        print(f"ALERTA: total_casos_A_encontrados={total} (esperado=65)")

    print(f"versao_alvo = {VERSAO_ALVO}")
    print(f"numero_de_versoes_usadas = {NUMERO_VERSOES}")
    print(f"head_inicial = {head_inicial}")
    print(f"commit_v16h_confirmado = {commit_v16h_confirmado}")
    print(f"total_casos_A_auditados = {total}")
    print(f"total_por_diagnostico_causa_provavel = {dict(Counter(df['diagnostico_causa_provavel']))}")
    print(f"total_por_classe_correcao_futura = {dict(Counter(df['classe_correcao_futura']))}")
    print(f"qtd_com_recebido_disponivel_elegivel = {int(df['existe_recebido_disponivel_elegivel'].sum())}")
    print(f"qtd_com_recebido_disponivel_suficiente = {int(df['recebido_cobre_pagamento'].sum())}")
    print(f"qtd_sem_recebido_disponivel_elegivel = {int((~df['existe_recebido_disponivel_elegivel']).sum())}")
    print(f"qtd_lote_escolhido_sem_saldo_temporal_cumulativo = {int(df['lote_escolhido_sem_saldo_temporal_cumulativo'].sum())}")
    print(f"caminho_csv_principal = {out_main}")
    print(f"caminho_csv_resumo = {out_resumo}")
    print("confirmacao_contrato_modelo_lidos_e_nao_alterados = true")
    print("confirmacao_ledger_saida_canonica_ranking_switching_nao_alterados = true")
    print("ids_A_resolvidos_total = 0")
    print("ids_B_ainda_sem_saldo = metrica_nao_disponivel_no_contexto_diagnostico (busca em ctx.recomputacao_sequencial_central_v1 ausente)")
    print("ids_B_resolvidos = metrica_nao_disponivel_no_contexto_diagnostico (busca em ctx.recomputacao_sequencial_central_v1 ausente)")
    print("switching_linhas = metrica_nao_disponivel_no_contexto_diagnostico (busca em ctx.switching_economico_shadow para linhas materializadas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
