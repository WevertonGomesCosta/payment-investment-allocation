from __future__ import annotations

from pathlib import Path
import sys
import unicodedata
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida
from nucleo.saida_canonica import construir_saida_canonica

OUT = RAIZ / "saidas" / "diagnostico" / "v17_c3"
OUT.mkdir(parents=True, exist_ok=True)

PENDENTE_PREFIXOS = ("pendente_", "nan", "none", "")
TOL = 0.01


def gravar(df: pd.DataFrame, nome: str, cols: list[str] | None = None) -> None:
    caminho = OUT / nome
    if df is None or df.empty:
        df = pd.DataFrame(columns=cols or [])
    if cols:
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df = df[cols]
    df.to_csv(caminho, index=False)


def norm_txt(v: Any) -> str:
    s = str(v or "").strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.split())


def data_txt(v: Any) -> str:
    if hasattr(v, "date") and not isinstance(v, str):
        try:
            return v.date().isoformat()
        except Exception:
            pass
    if hasattr(v, "isoformat") and not isinstance(v, str):
        try:
            return v.isoformat()[:10]
        except Exception:
            pass
    s = str(v or "").strip()
    return s[:10]


def num(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, str) and v.strip().lower().startswith(PENDENTE_PREFIXOS):
        return None
    if isinstance(v, str):
        s = v.replace("R$", "").replace(" ", "").strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        return None


def fmt_valor(v: Any) -> str:
    x = num(v)
    return "" if x is None else f"{x:.2f}"


def chave_pagamento(data: Any, valor: Any, descricao: Any) -> str:
    desc = norm_txt(descricao)[:48]
    return f"{data_txt(data)}|{fmt_valor(valor)}|{desc}"


def carregar_contexto_referencia_v17_c3():
    return carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )


def preparar_pagamentos_pacote(pacote) -> pd.DataFrame:
    rec = pacote.recomendacoes_futuras.copy()
    dec = pacote.decisoes_pagamento.copy()
    if rec.empty:
        return pd.DataFrame()
    if not dec.empty and "pagamento_id" in rec.columns and "pagamento_id" in dec.columns:
        dec_cols = [c for c in ["pagamento_id", "tipo_fonte_escolhida_v17", "fonte_id", "valor_bruto_resgate", "valor_imposto", "valor_liquido_resgate", "status_decisao"] if c in dec.columns]
        rec = rec.merge(dec[dec_cols], on="pagamento_id", how="left", suffixes=("", "_decisao"))
    linhas = []
    for _, row in rec.iterrows():
        data = row.get("data_pagamento")
        valor = row.get("valor_pagamento")
        desc = row.get("conta_descricao")
        linhas.append({
            "origem": "pacote_orquestrado_pre_saida",
            "chave_pagamento": chave_pagamento(data, valor, desc),
            "pagamento_id": row.get("pagamento_id", ""),
            "data": data_txt(data),
            "descricao": desc,
            "valor": num(valor),
            "fonte": row.get("fonte_id", ""),
            "tipo_fonte": row.get("tipo_fonte_escolhida_v17", ""),
            "bruto": num(row.get("valor_bruto_resgate")),
            "imposto": num(row.get("valor_imposto")),
            "liquido": num(row.get("valor_liquido_resgate")),
            "status": row.get("status_recomendacao", row.get("status_decisao", "")),
        })
    return pd.DataFrame(linhas)


def preparar_pagamentos_saida(saida) -> pd.DataFrame:
    linhas = []
    for i, item in enumerate(saida.extrato_futuro or []):
        data = item.get("Data")
        valor = item.get("Valor")
        desc = item.get("Conta") or item.get("Descrição") or item.get("Descricao") or ""
        linhas.append({
            "origem": "saida_canonica.extrato_futuro",
            "chave_pagamento": chave_pagamento(data, valor, desc),
            "pagamento_id": item.get("Pagamento ID") or item.get("Despesa ID") or f"saida_auto_{i}",
            "data": data_txt(data),
            "descricao": desc,
            "valor": num(valor),
            "fonte": item.get("Lote sugerido") or item.get("Lote") or "",
            "tipo_fonte": item.get("Tipo fonte") or item.get("Fonte") or "",
            "bruto": num(item.get("Bruto")),
            "imposto": num(item.get("Imposto")),
            "liquido": num(item.get("Líquido") or item.get("Liquido")),
            "status": item.get("Status recomendação") or item.get("Status recomendacao") or "",
        })
    return pd.DataFrame(linhas)


def comparar_pagamentos(df_pacote: pd.DataFrame, df_saida: pd.DataFrame) -> pd.DataFrame:
    ch_pac = set(df_pacote.get("chave_pagamento", pd.Series(dtype=str)).astype(str)) if not df_pacote.empty else set()
    ch_saida = set(df_saida.get("chave_pagamento", pd.Series(dtype=str)).astype(str)) if not df_saida.empty else set()
    linhas = []
    for ch in sorted(ch_pac | ch_saida):
        p = df_pacote[df_pacote["chave_pagamento"].astype(str) == ch].head(1) if not df_pacote.empty else pd.DataFrame()
        s = df_saida[df_saida["chave_pagamento"].astype(str) == ch].head(1) if not df_saida.empty else pd.DataFrame()
        p0 = p.iloc[0].to_dict() if not p.empty else {}
        s0 = s.iloc[0].to_dict() if not s.empty else {}
        linhas.append({
            "chave_pagamento": ch,
            "presente_pacote": not p.empty,
            "presente_saida": not s.empty,
            "data_pacote": p0.get("data", ""),
            "data_saida": s0.get("data", ""),
            "valor_pacote": p0.get("valor", ""),
            "valor_saida": s0.get("valor", ""),
            "descricao_pacote": p0.get("descricao", ""),
            "descricao_saida": s0.get("descricao", ""),
            "fonte_pacote": p0.get("fonte", ""),
            "fonte_saida": s0.get("fonte", ""),
            "status_pacote": p0.get("status", ""),
            "status_saida": s0.get("status", ""),
            "classe_comparacao": "em_ambos" if (not p.empty and not s.empty) else ("somente_pacote" if not p.empty else "somente_saida"),
        })
    return pd.DataFrame(linhas)


def comparar_valores(df_pacote: pd.DataFrame, df_saida: pd.DataFrame) -> pd.DataFrame:
    if df_pacote.empty or df_saida.empty:
        return pd.DataFrame()
    comum = sorted(set(df_pacote["chave_pagamento"].astype(str)) & set(df_saida["chave_pagamento"].astype(str)))
    linhas = []
    for ch in comum:
        p = df_pacote[df_pacote["chave_pagamento"].astype(str) == ch].iloc[0]
        s = df_saida[df_saida["chave_pagamento"].astype(str) == ch].iloc[0]
        for campo in ["bruto", "imposto", "liquido"]:
            vp = p.get(campo)
            vs = s.get(campo)
            comparavel = vp is not None and vs is not None
            diff = None if not comparavel else round(float(vp) - float(vs), 2)
            linhas.append({
                "chave_pagamento": ch,
                "campo": campo,
                "valor_pacote": vp,
                "valor_saida": vs,
                "comparavel": comparavel,
                "diferenca": diff,
                "divergencia_material": bool(comparavel and abs(float(diff)) > TOL),
            })
    return pd.DataFrame(linhas)


def comparar_switching(pacote, saida) -> pd.DataFrame:
    dfp = pacote.estado_temporal_switching.copy()
    linhas = []
    saida_sw = saida.switchings or []
    for i, row in dfp.iterrows():
        linhas.append({
            "origem": "pacote_orquestrado_pre_saida.estado_temporal_switching",
            "indice": i,
            "lote_origem": row.get("lote_id_origem", ""),
            "lote_destino": row.get("lote_id_destino", ""),
            "data": data_txt(row.get("data_switching")),
            "produto_destino": row.get("produto_destino", ""),
            "valor": num(row.get("valor_liquido_migrado")),
        })
    for i, row in enumerate(saida_sw):
        linhas.append({
            "origem": "saida_canonica.switchings",
            "indice": i,
            "lote_origem": row.get("Lote origem") or row.get("lote_origem_switching") or row.get("lote_id") or "",
            "lote_destino": row.get("Lote destino") or row.get("Lote pós-switching") or row.get("Novo lote") or "",
            "data": data_txt(row.get("Data") or row.get("Data sugerida") or row.get("data_sugerida_switching")),
            "produto_destino": row.get("Destino") or row.get("Produto destino switching") or row.get("produto_destino_switching") or "",
            "valor": num(row.get("Valor líquido origem") or row.get("valor_liquido_origem") or row.get("Valor líquido total")),
        })
    return pd.DataFrame(linhas)


def comparar_ranking(pacote, saida) -> pd.DataFrame:
    dfp = pacote.ranking_informativo.copy()
    saida_rank = saida.ranking_amostra or []
    linhas = []
    for i, row in dfp.head(30).iterrows():
        linhas.append({
            "origem": "pacote_orquestrado_pre_saida.ranking_informativo",
            "indice": i,
            "produto": row.get("produto_id", ""),
            "posicao": row.get("posicao_ranking", ""),
            "score": row.get("score", ""),
        })
    for i, row in enumerate(saida_rank[:30]):
        linhas.append({
            "origem": "saida_canonica.ranking_amostra",
            "indice": i,
            "produto": row.get("Produto") or row.get("Nome") or row.get("produto_nome_canonico") or "",
            "posicao": row.get("Rank") or row.get("Rank_Consolidado_Prazo_Ativos") or "",
            "score": row.get("Score") or row.get("Score Final Prazo") or row.get("SAOF_Final_Prazo") or "",
        })
    return pd.DataFrame(linhas)


def main() -> int:
    contexto = carregar_contexto_referencia_v17_c3()
    pacote = montar_pacote_orquestrado_pre_saida(contexto)
    saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)

    dfp = preparar_pagamentos_pacote(pacote)
    dfs = preparar_pagamentos_saida(saida)
    comp_pag = comparar_pagamentos(dfp, dfs)
    comp_val = comparar_valores(dfp, dfs)
    comp_sw = comparar_switching(pacote, saida)
    comp_rank = comparar_ranking(pacote, saida)

    gravar(dfp, "v17_c3_pagamentos_pacote_normalizados.csv")
    gravar(dfs, "v17_c3_pagamentos_saida_normalizados.csv")
    gravar(comp_pag, "v17_c3_comparativo_pagamentos.csv")
    gravar(comp_val, "v17_c3_comparativo_valores.csv")
    gravar(comp_sw, "v17_c3_comparativo_switching.csv")
    gravar(comp_rank, "v17_c3_comparativo_ranking.csv")

    pagamentos_pacote = len(dfp)
    pagamentos_saida = len(dfs)
    em_ambos = int((comp_pag["classe_comparacao"] == "em_ambos").sum()) if not comp_pag.empty else 0
    somente_pacote = int((comp_pag["classe_comparacao"] == "somente_pacote").sum()) if not comp_pag.empty else 0
    somente_saida = int((comp_pag["classe_comparacao"] == "somente_saida").sum()) if not comp_pag.empty else 0
    valores_comparaveis = int(comp_val["comparavel"].astype(bool).sum()) if not comp_val.empty else 0
    divergencias_valores = int(comp_val["divergencia_material"].astype(bool).sum()) if not comp_val.empty else 0
    switching_pacote = len(pacote.estado_temporal_switching)
    switching_saida = len(saida.switchings or [])
    ranking_pacote = len(pacote.ranking_informativo)
    ranking_saida = len(saida.ranking_amostra or [])

    decisao = "nao_substituir_saida_canonica_ainda"
    if somente_pacote == 0 and somente_saida == 0 and divergencias_valores == 0:
        decisao = "equivalencia_minima_pagamentos_valores_sem_divergencia_material"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_c3", "valor": "ok_comparacao_controlada", "status": "ok", "observacao": "comparacao executada sem consumo funcional do pacote"},
        {"metrica": "decisao_consumo_saida_canonica", "valor": decisao, "status": "bloqueio_preventivo" if decisao.startswith("nao") else "ok", "observacao": "V17-C3 compara, mas nao substitui"},
        {"metrica": "pagamentos_pacote", "valor": pagamentos_pacote, "status": "info", "observacao": "recomendacoes_futuras normalizadas"},
        {"metrica": "pagamentos_saida", "valor": pagamentos_saida, "status": "info", "observacao": "extrato_futuro normalizado"},
        {"metrica": "pagamentos_em_ambos", "valor": em_ambos, "status": "info", "observacao": "chave data|valor|descricao"},
        {"metrica": "pagamentos_somente_pacote", "valor": somente_pacote, "status": "alerta" if somente_pacote else "ok", "observacao": "nao bloquear; investigar antes de consumo"},
        {"metrica": "pagamentos_somente_saida", "valor": somente_saida, "status": "alerta" if somente_saida else "ok", "observacao": "nao bloquear; investigar antes de consumo"},
        {"metrica": "valores_comparaveis_bruto_imposto_liquido", "valor": valores_comparaveis, "status": "info", "observacao": "campos comparaveis em ambos"},
        {"metrica": "divergencias_materiais_valores", "valor": divergencias_valores, "status": "alerta" if divergencias_valores else "ok", "observacao": "tolerancia 0.01"},
        {"metrica": "switching_pacote", "valor": switching_pacote, "status": "info", "observacao": "estado_temporal_switching"},
        {"metrica": "switching_saida", "valor": switching_saida, "status": "info", "observacao": "saida.switchings"},
        {"metrica": "ranking_pacote", "valor": ranking_pacote, "status": "info", "observacao": "ranking_informativo"},
        {"metrica": "ranking_saida", "valor": ranking_saida, "status": "info", "observacao": "saida.ranking_amostra"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script de comparacao"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo funcional"},
        {"metrica": "confirmacao_sem_substituir_consumo_saida_canonica", "valor": True, "status": "ok", "observacao": "saida atual permanece fonte exibida"},
    ])
    gravar(resumo, "v17_c3_resumo.csv")

    print("=== V17-C3 — COMPARACAO PACOTE PRE-SAIDA VS SAIDA CANONICA ATUAL ===")
    print("status_global_v17_c3=ok_comparacao_controlada")
    print(f"decisao_consumo_saida_canonica={decisao}")
    print(f"pagamentos_pacote={pagamentos_pacote}")
    print(f"pagamentos_saida={pagamentos_saida}")
    print(f"pagamentos_em_ambos={em_ambos}")
    print(f"pagamentos_somente_pacote={somente_pacote}")
    print(f"pagamentos_somente_saida={somente_saida}")
    print(f"valores_comparaveis_bruto_imposto_liquido={valores_comparaveis}")
    print(f"divergencias_materiais_valores={divergencias_valores}")
    print(f"switching_pacote={switching_pacote}")
    print(f"switching_saida={switching_saida}")
    print(f"ranking_pacote={ranking_pacote}")
    print(f"ranking_saida={ranking_saida}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_substituir_consumo_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
