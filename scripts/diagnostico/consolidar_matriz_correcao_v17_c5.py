from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

IN_C4 = RAIZ / "saidas" / "diagnostico" / "v17_c4"
IN_C3 = RAIZ / "saidas" / "diagnostico" / "v17_c3"
OUT = RAIZ / "saidas" / "diagnostico" / "v17_c5"
OUT.mkdir(parents=True, exist_ok=True)

ARQ_VALORES_C4 = IN_C4 / "v17_c4_classificacao_divergencias_valores.csv"
ARQ_SWITCHING_C4 = IN_C4 / "v17_c4_classificacao_divergencia_switching.csv"
ARQ_DECISOES_C4 = IN_C4 / "v17_c4_matriz_decisao_correcao.csv"
ARQ_SWITCHING_C3 = IN_C3 / "v17_c3_comparativo_switching.csv"

OUT_CAUSAS = OUT / "v17_c5_matriz_causas_correcao.csv"
OUT_SWITCHING_PONTE = OUT / "v17_c5_switching_ponte_comparavel.csv"
OUT_PRIORIDADE = OUT / "v17_c5_primeira_correcao_segura_priorizada.csv"
OUT_RESUMO = OUT / "v17_c5_resumo.csv"


def ler_csv(caminho: Path, colunas: list[str]) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame(columns=colunas)
    try:
        df = pd.read_csv(caminho)
    except Exception:
        return pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df


def gravar(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def to_num(v: Any) -> float | None:
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).replace(".", "").replace(",", "."))
        except Exception:
            return None


def consolidar_causas() -> pd.DataFrame:
    df_val = ler_csv(ARQ_VALORES_C4, [
        "chave_pagamento", "campo", "valor_pacote", "valor_saida", "diferenca", "classe_causa_provavel",
        "origem_valor_pacote", "origem_valor_saida_canonica", "decisao_correcao", "observacao",
    ])
    df_sw = ler_csv(ARQ_SWITCHING_C4, [
        "item", "qtd_pacote", "qtd_saida", "classe_causa_provavel", "origem_valor_pacote",
        "origem_valor_saida_canonica", "decisao_correcao", "observacao",
    ])
    linhas: list[dict[str, Any]] = []

    if not df_val.empty:
        for classe, sub in df_val.groupby("classe_causa_provavel", dropna=False):
            qtd = int(len(sub))
            campos = ",".join(sorted(set(sub["campo"].astype(str))))
            diffs = [abs(x) for x in (to_num(v) for v in sub["diferenca"].tolist()) if x is not None]
            linhas.append({
                "area": "valores_bruto_imposto_liquido",
                "classe_causa_provavel": classe,
                "qtd_ocorrencias": qtd,
                "campos_afetados": campos,
                "diferenca_abs_max": max(diffs) if diffs else "",
                "origem_valor_pacote": str(sub.iloc[0].get("origem_valor_pacote") or ""),
                "origem_valor_saida_canonica": str(sub.iloc[0].get("origem_valor_saida_canonica") or ""),
                "decisao_correcao_c4": str(sub.iloc[0].get("decisao_correcao") or ""),
                "primeira_correcao_segura_v17_c5": "nao_aplicar_ainda",
                "motivo_priorizacao": "divergencia de valor exige confirmar fonte de verdade antes de alterar pacote ou saida",
                "bloqueia_consumo_saida": True,
            })

    if not df_sw.empty:
        for _, row in df_sw.iterrows():
            linhas.append({
                "area": "switching",
                "classe_causa_provavel": row.get("classe_causa_provavel"),
                "qtd_ocorrencias": int(row.get("qtd_pacote") or 0) + int(row.get("qtd_saida") or 0),
                "campos_afetados": "lote_origem,lote_destino,data,produto_destino,valor",
                "diferenca_abs_max": "",
                "origem_valor_pacote": row.get("origem_valor_pacote"),
                "origem_valor_saida_canonica": row.get("origem_valor_saida_canonica"),
                "decisao_correcao_c4": row.get("decisao_correcao"),
                "primeira_correcao_segura_v17_c5": "criar_ponte_switching_comparavel_sem_consumo_saida",
                "motivo_priorizacao": "expor switching em CSV comparavel nao altera motor nem saida_canonica e reduz ambiguidade estrutural",
                "bloqueia_consumo_saida": True,
            })

    return pd.DataFrame(linhas)


def criar_ponte_switching() -> pd.DataFrame:
    df = ler_csv(ARQ_SWITCHING_C3, ["origem", "indice", "lote_origem", "lote_destino", "data", "produto_destino", "valor"])
    if df.empty:
        return pd.DataFrame(columns=[
            "switching_key", "origem_pacote_existe", "origem_saida_existe", "lote_origem", "lote_destino",
            "data", "produto_destino", "valor_pacote", "valor_saida", "status_ponte", "decisao_consumo",
        ])

    pacote = df[df["origem"].astype(str).str.contains("pacote_orquestrado", na=False)].copy()
    saida = df[df["origem"].astype(str).str.contains("saida_canonica", na=False)].copy()
    linhas: list[dict[str, Any]] = []

    for i, row in pacote.iterrows():
        lote_origem = str(row.get("lote_origem") or "").strip()
        lote_destino = str(row.get("lote_destino") or "").strip()
        data = str(row.get("data") or "").strip()
        produto_destino = str(row.get("produto_destino") or "").strip()
        valor = to_num(row.get("valor"))
        key = f"{data}|{lote_origem}|{lote_destino}|{valor if valor is not None else ''}"
        linhas.append({
            "switching_key": key,
            "origem_pacote_existe": True,
            "origem_saida_existe": False,
            "lote_origem": lote_origem,
            "lote_destino": lote_destino,
            "data": data,
            "produto_destino": produto_destino,
            "valor_pacote": valor,
            "valor_saida": "",
            "status_ponte": "ponte_comparavel_criada_a_partir_do_pacote",
            "decisao_consumo": "diagnostico_apenas_sem_substituir_saida_canonica",
        })

    for i, row in saida.iterrows():
        lote_origem = str(row.get("lote_origem") or "").strip()
        lote_destino = str(row.get("lote_destino") or "").strip()
        data = str(row.get("data") or "").strip()
        valor = to_num(row.get("valor"))
        key = f"{data}|{lote_origem}|{lote_destino}|{valor if valor is not None else ''}"
        linhas.append({
            "switching_key": key,
            "origem_pacote_existe": False,
            "origem_saida_existe": True,
            "lote_origem": lote_origem,
            "lote_destino": lote_destino,
            "data": data,
            "produto_destino": str(row.get("produto_destino") or "").strip(),
            "valor_pacote": "",
            "valor_saida": valor,
            "status_ponte": "evento_switching_exposto_pela_saida",
            "decisao_consumo": "diagnostico_apenas_sem_substituir_saida_canonica",
        })

    out = pd.DataFrame(linhas)
    if out.empty:
        return out

    # Consolidacao por chave: se no futuro a saida passar a expor o mesmo evento,
    # a ponte ja mostrara equivalencia sem alterar a saida atual.
    agg = []
    for key, sub in out.groupby("switching_key", dropna=False):
        pacote_existe = bool(sub["origem_pacote_existe"].astype(bool).any())
        saida_existe = bool(sub["origem_saida_existe"].astype(bool).any())
        p = sub[sub["origem_pacote_existe"].astype(bool)].head(1)
        s = sub[sub["origem_saida_existe"].astype(bool)].head(1)
        base = p.iloc[0].to_dict() if not p.empty else s.iloc[0].to_dict()
        agg.append({
            "switching_key": key,
            "origem_pacote_existe": pacote_existe,
            "origem_saida_existe": saida_existe,
            "lote_origem": base.get("lote_origem"),
            "lote_destino": base.get("lote_destino"),
            "data": base.get("data"),
            "produto_destino": base.get("produto_destino"),
            "valor_pacote": p.iloc[0].get("valor_pacote") if not p.empty else "",
            "valor_saida": s.iloc[0].get("valor_saida") if not s.empty else "",
            "status_ponte": "equivalente_em_pacote_e_saida" if pacote_existe and saida_existe else ("somente_pacote" if pacote_existe else "somente_saida"),
            "decisao_consumo": "diagnostico_apenas_sem_substituir_saida_canonica",
        })
    return pd.DataFrame(agg)


def priorizar_primeira_correcao(df_causas: pd.DataFrame, df_ponte: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    qtd_switching_ponte = int(len(df_ponte)) if df_ponte is not None else 0
    qtd_switching_somente_pacote = int((df_ponte["status_ponte"] == "somente_pacote").sum()) if qtd_switching_ponte else 0
    linhas.append({
        "prioridade": "P0",
        "correcao_segura": "expor_switching_em_ponte_comparavel_diagnostica",
        "escopo": "gera CSV comparavel a partir de V17-C3 sem alterar saida_canonica",
        "qtd_itens_afetados": qtd_switching_ponte,
        "qtd_ainda_somente_pacote": qtd_switching_somente_pacote,
        "reduz_divergencia_valores": False,
        "reduz_ambiguidade_switching": True,
        "altera_saida_canonica": False,
        "altera_motor": False,
        "decisao": "aprovada_como_primeira_correcao_segura_diagnostica",
    })
    if not df_causas.empty:
        valores = df_causas[df_causas["area"] == "valores_bruto_imposto_liquido"].copy()
        for _, row in valores.iterrows():
            linhas.append({
                "prioridade": "P1",
                "correcao_segura": f"investigar_{row.get('classe_causa_provavel')}",
                "escopo": "nao aplicar correcao de valor sem definir fonte de verdade entre pacote e saida",
                "qtd_itens_afetados": row.get("qtd_ocorrencias"),
                "qtd_ainda_somente_pacote": "",
                "reduz_divergencia_valores": False,
                "reduz_ambiguidade_switching": False,
                "altera_saida_canonica": False,
                "altera_motor": False,
                "decisao": "pendente_classificacao_mais_fina_antes_de_corrigir_valor",
            })
    return pd.DataFrame(linhas)


def main() -> int:
    df_causas = consolidar_causas()
    df_ponte = criar_ponte_switching()
    df_prioridade = priorizar_primeira_correcao(df_causas, df_ponte)

    gravar(df_causas, OUT_CAUSAS, [
        "area", "classe_causa_provavel", "qtd_ocorrencias", "campos_afetados", "diferenca_abs_max",
        "origem_valor_pacote", "origem_valor_saida_canonica", "decisao_correcao_c4",
        "primeira_correcao_segura_v17_c5", "motivo_priorizacao", "bloqueia_consumo_saida",
    ])
    gravar(df_ponte, OUT_SWITCHING_PONTE, [
        "switching_key", "origem_pacote_existe", "origem_saida_existe", "lote_origem", "lote_destino",
        "data", "produto_destino", "valor_pacote", "valor_saida", "status_ponte", "decisao_consumo",
    ])
    gravar(df_prioridade, OUT_PRIORIDADE, [
        "prioridade", "correcao_segura", "escopo", "qtd_itens_afetados", "qtd_ainda_somente_pacote",
        "reduz_divergencia_valores", "reduz_ambiguidade_switching", "altera_saida_canonica", "altera_motor", "decisao",
    ])

    causas_valores = int(df_causas[df_causas["area"] == "valores_bruto_imposto_liquido"]["classe_causa_provavel"].nunique()) if not df_causas.empty else 0
    causas_switching = int(df_causas[df_causas["area"] == "switching"]["classe_causa_provavel"].nunique()) if not df_causas.empty else 0
    linhas_ponte = int(len(df_ponte))
    somente_pacote = int((df_ponte["status_ponte"] == "somente_pacote").sum()) if not df_ponte.empty else 0
    somente_saida = int((df_ponte["status_ponte"] == "somente_saida").sum()) if not df_ponte.empty else 0
    equivalente = int((df_ponte["status_ponte"] == "equivalente_em_pacote_e_saida").sum()) if not df_ponte.empty else 0

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_c5", "valor": "ok_consolidacao_correcao_segura", "status": "ok", "observacao": "C5 consolida classes e cria ponte comparavel de switching"},
        {"metrica": "decisao_consumo_saida_canonica", "valor": "nao_substituir_saida_canonica_ainda", "status": "bloqueio_preventivo", "observacao": "C5 nao muda consumo"},
        {"metrica": "classes_causa_valores_consolidadas", "valor": causas_valores, "status": "ok", "observacao": "esperado: 3 conforme C4"},
        {"metrica": "classes_causa_switching_consolidadas", "valor": causas_switching, "status": "ok", "observacao": "divergencia switching pacote vs saida"},
        {"metrica": "switchings_na_ponte_comparavel", "valor": linhas_ponte, "status": "ok", "observacao": "eventos normalizados para comparacao futura"},
        {"metrica": "switchings_somente_pacote", "valor": somente_pacote, "status": "alerta" if somente_pacote else "ok", "observacao": "saida ainda nao expoe esses eventos"},
        {"metrica": "switchings_somente_saida", "valor": somente_saida, "status": "alerta" if somente_saida else "ok", "observacao": "eventos presentes apenas na saida"},
        {"metrica": "switchings_equivalentes", "valor": equivalente, "status": "info", "observacao": "eventos iguais na ponte"},
        {"metrica": "primeira_correcao_segura", "valor": "ponte_switching_comparavel", "status": "ok", "observacao": "sem alterar saida nem motor"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script pos-comparacao"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo funcional"},
        {"metrica": "confirmacao_sem_substituir_consumo_saida_canonica", "valor": True, "status": "ok", "observacao": "saida permanece atual"},
    ])
    gravar(resumo, OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-C5 — MATRIZ DE CORRECAO E PONTE COMPARAVEL DE SWITCHING ===")
    print("status_global_v17_c5=ok_consolidacao_correcao_segura")
    print("decisao_consumo_saida_canonica=nao_substituir_saida_canonica_ainda")
    print(f"classes_causa_valores_consolidadas={causas_valores}")
    print(f"classes_causa_switching_consolidadas={causas_switching}")
    print(f"switchings_na_ponte_comparavel={linhas_ponte}")
    print(f"switchings_somente_pacote={somente_pacote}")
    print(f"switchings_somente_saida={somente_saida}")
    print(f"switchings_equivalentes={equivalente}")
    print("primeira_correcao_segura=ponte_switching_comparavel")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_substituir_consumo_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
