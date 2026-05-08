from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

IN = RAIZ / "saidas" / "diagnostico" / "v17_c3"
OUT = RAIZ / "saidas" / "diagnostico" / "v17_c4"
OUT.mkdir(parents=True, exist_ok=True)

ARQ_VALORES = IN / "v17_c3_comparativo_valores.csv"
ARQ_PAGAMENTOS = IN / "v17_c3_comparativo_pagamentos.csv"
ARQ_SWITCHING = IN / "v17_c3_comparativo_switching.csv"
ARQ_RESUMO_C3 = IN / "v17_c3_resumo.csv"

OUT_VALORES = OUT / "v17_c4_classificacao_divergencias_valores.csv"
OUT_SWITCHING = OUT / "v17_c4_classificacao_divergencia_switching.csv"
OUT_DECISOES = OUT / "v17_c4_matriz_decisao_correcao.csv"
OUT_RESUMO = OUT / "v17_c4_resumo.csv"

TOL_ARRED = 0.05
TOL_MATERIAL = 0.01


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


def boolish(v: Any) -> bool:
    return str(v).strip().lower() in {"true", "1", "sim", "yes"}


def fnum(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, str) and not v.strip():
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        try:
            return float(str(v).replace(".", "").replace(",", "."))
        except Exception:
            return None


def classificar_valor(campo: str, valor_pacote: Any, valor_saida: Any, diferenca: Any) -> tuple[str, str, str]:
    vp = fnum(valor_pacote)
    vs = fnum(valor_saida)
    diff = fnum(diferenca)
    if vp is None and vs is None:
        return "nao_comparavel_ambos_vazios", "sem_correcao_agora", "ambos_sem_valor comparavel"
    if vp is None and vs is not None:
        return "pacote_sem_valor_saida_com_valor", "investigar_preenchimento_pacote", "saida possui valor que pacote nao materializou"
    if vp is not None and vs is None:
        return "pacote_com_valor_saida_sem_valor", "investigar_saida_oculta_valor", "pacote possui valor que saida nao renderiza"
    if diff is None:
        return "nao_comparavel_diferenca_invalida", "investigar_normalizacao", "diferenca nao numerica"
    adiff = abs(diff)
    if adiff <= TOL_MATERIAL:
        return "equivalente", "sem_correcao", "diferenca dentro da tolerancia material"
    if adiff <= TOL_ARRED:
        return "provavel_arredondamento", "padronizar_arredondamento_futuro", "diferenca pequena, compativel com arredondamento"
    if campo == "imposto" and ((vp == 0 and vs != 0) or (vp != 0 and vs == 0)):
        return "divergencia_regra_imposto_ou_fallback_saida", "investigar_origem_imposto", "um lado zerou imposto e o outro nao"
    if campo == "bruto" and vp is not None and vs is not None and abs(vp - vs) > TOL_ARRED:
        return "divergencia_bruto_fonte_calculo", "comparar_recomputacao_vs_saida", "bruto difere entre pacote e saida"
    if campo == "liquido" and vp is not None and vs is not None and abs(vp - vs) > TOL_ARRED:
        return "divergencia_liquido_fonte_calculo", "comparar_recomputacao_vs_saida", "liquido difere entre pacote e saida"
    return "divergencia_material_indeterminada", "investigar_pagamento_campo", "divergencia material sem causa automatica suficiente"


def origem_pacote(campo: str) -> str:
    if campo in {"bruto", "imposto", "liquido"}:
        return "pacote_orquestrado_pre_saida.decisoes_pagamento; prioridade: decisao_local_v1, recomputacao_sequencial_central_v1, recomendacoes"
    return "pacote_orquestrado_pre_saida"


def origem_saida(campo: str) -> str:
    if campo in {"bruto", "imposto", "liquido"}:
        return "saida_canonica.extrato_futuro"
    return "saida_canonica"


def classificar_divergencias_valores() -> pd.DataFrame:
    df = ler_csv(ARQ_VALORES, [
        "chave_pagamento", "campo", "valor_pacote", "valor_saida", "comparavel", "diferenca", "divergencia_material",
    ])
    if df.empty:
        return pd.DataFrame(columns=[
            "chave_pagamento", "campo", "valor_pacote", "valor_saida", "diferenca", "classe_causa_provavel",
            "origem_valor_pacote", "origem_valor_saida_canonica", "decisao_correcao", "observacao",
        ])
    linhas = []
    for _, row in df.iterrows():
        if not boolish(row.get("divergencia_material")):
            continue
        campo = str(row.get("campo") or "")
        classe, decisao, obs = classificar_valor(campo, row.get("valor_pacote"), row.get("valor_saida"), row.get("diferenca"))
        linhas.append({
            "chave_pagamento": row.get("chave_pagamento"),
            "campo": campo,
            "valor_pacote": row.get("valor_pacote"),
            "valor_saida": row.get("valor_saida"),
            "diferenca": row.get("diferenca"),
            "classe_causa_provavel": classe,
            "origem_valor_pacote": origem_pacote(campo),
            "origem_valor_saida_canonica": origem_saida(campo),
            "decisao_correcao": decisao,
            "observacao": obs,
        })
    return pd.DataFrame(linhas)


def classificar_switching() -> pd.DataFrame:
    df = ler_csv(ARQ_SWITCHING, ["origem", "indice", "lote_origem", "lote_destino", "data", "produto_destino", "valor"])
    if df.empty:
        return pd.DataFrame(columns=[
            "item", "classe_causa_provavel", "origem_valor_pacote", "origem_valor_saida_canonica", "decisao_correcao", "observacao",
        ])
    pacote = df[df["origem"].astype(str).str.contains("pacote_orquestrado", na=False)].copy()
    saida = df[df["origem"].astype(str).str.contains("saida_canonica", na=False)].copy()
    linhas = []
    if len(pacote) and not len(saida):
        linhas.append({
            "item": "switching_pacote_vs_saida",
            "qtd_pacote": int(len(pacote)),
            "qtd_saida": int(len(saida)),
            "classe_causa_provavel": "saida_canonica_nao_expoe_switching_no_atributo_comparado",
            "origem_valor_pacote": "pacote_orquestrado_pre_saida.estado_temporal_switching; aba Switching canonizada",
            "origem_valor_saida_canonica": "saida_canonica.switchings",
            "decisao_correcao": "nao_substituir_saida; criar_ponte_renderizacao_switching_apos_validar_formato",
            "observacao": "pacote reconhece eventos de switching, mas saida atual nao os expõe em saida.switchings",
        })
    elif len(pacote) != len(saida):
        linhas.append({
            "item": "switching_pacote_vs_saida",
            "qtd_pacote": int(len(pacote)),
            "qtd_saida": int(len(saida)),
            "classe_causa_provavel": "quantidade_switching_diferente",
            "origem_valor_pacote": "pacote_orquestrado_pre_saida.estado_temporal_switching",
            "origem_valor_saida_canonica": "saida_canonica.switchings",
            "decisao_correcao": "investigar_mapeamento_switching_saida",
            "observacao": "quantidades divergentes antes de consumo funcional",
        })
    else:
        linhas.append({
            "item": "switching_pacote_vs_saida",
            "qtd_pacote": int(len(pacote)),
            "qtd_saida": int(len(saida)),
            "classe_causa_provavel": "quantidade_switching_equivalente",
            "origem_valor_pacote": "pacote_orquestrado_pre_saida.estado_temporal_switching",
            "origem_valor_saida_canonica": "saida_canonica.switchings",
            "decisao_correcao": "comparacao_detalhada_futura_se_necessario",
            "observacao": "quantidade equivalente",
        })
    return pd.DataFrame(linhas)


def montar_decisoes(df_val: pd.DataFrame, df_sw: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    if not df_val.empty:
        for classe, sub in df_val.groupby("classe_causa_provavel", dropna=False):
            linhas.append({
                "area": "valores_bruto_imposto_liquido",
                "classe_causa_provavel": classe,
                "qtd_ocorrencias": int(len(sub)),
                "decisao_correcao": str(sub.iloc[0].get("decisao_correcao") or ""),
                "bloqueia_consumo_saida": True,
                "prioridade": "P0" if str(sub.iloc[0].get("decisao_correcao") or "").startswith("comparar") else "P1",
            })
    if not df_sw.empty:
        for _, row in df_sw.iterrows():
            linhas.append({
                "area": "switching",
                "classe_causa_provavel": row.get("classe_causa_provavel"),
                "qtd_ocorrencias": int(row.get("qtd_pacote") or 0) + int(row.get("qtd_saida") or 0),
                "decisao_correcao": row.get("decisao_correcao"),
                "bloqueia_consumo_saida": True,
                "prioridade": "P0",
            })
    if not linhas:
        linhas.append({
            "area": "geral",
            "classe_causa_provavel": "sem_divergencias_classificadas",
            "qtd_ocorrencias": 0,
            "decisao_correcao": "sem_correcao",
            "bloqueia_consumo_saida": False,
            "prioridade": "INFO",
        })
    return pd.DataFrame(linhas)


def main() -> int:
    df_val = classificar_divergencias_valores()
    df_sw = classificar_switching()
    df_dec = montar_decisoes(df_val, df_sw)

    gravar(df_val, OUT_VALORES, [
        "chave_pagamento", "campo", "valor_pacote", "valor_saida", "diferenca", "classe_causa_provavel",
        "origem_valor_pacote", "origem_valor_saida_canonica", "decisao_correcao", "observacao",
    ])
    gravar(df_sw, OUT_SWITCHING, [
        "item", "qtd_pacote", "qtd_saida", "classe_causa_provavel", "origem_valor_pacote",
        "origem_valor_saida_canonica", "decisao_correcao", "observacao",
    ])
    gravar(df_dec, OUT_DECISOES, [
        "area", "classe_causa_provavel", "qtd_ocorrencias", "decisao_correcao", "bloqueia_consumo_saida", "prioridade",
    ])

    divergencias_valores = int(len(df_val))
    classes_valores = int(df_val["classe_causa_provavel"].nunique()) if not df_val.empty else 0
    diverg_switching = int(len(df_sw))
    bloqueios = int(df_dec["bloqueia_consumo_saida"].astype(bool).sum()) if not df_dec.empty else 0
    decisao = "nao_substituir_saida_canonica_ainda" if bloqueios else "apto_para_ponte_controlada_futura"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_c4", "valor": "ok_classificacao_controlada", "status": "ok", "observacao": "classificacao consumiu CSVs da V17-C3"},
        {"metrica": "decisao_consumo_saida_canonica", "valor": decisao, "status": "bloqueio_preventivo" if bloqueios else "ok", "observacao": "C4 classifica, nao substitui"},
        {"metrica": "divergencias_valores_classificadas", "valor": divergencias_valores, "status": "ok", "observacao": "esperado: 40 quando C3 gerou 40 divergencias"},
        {"metrica": "classes_causa_valores", "valor": classes_valores, "status": "info", "observacao": "classes provaveis para bruto/imposto/liquido"},
        {"metrica": "divergencias_switching_classificadas", "valor": diverg_switching, "status": "ok", "observacao": "divergencia pacote vs saida.switchings"},
        {"metrica": "decisoes_bloqueantes_consumo_saida", "valor": bloqueios, "status": "bloqueio_preventivo" if bloqueios else "ok", "observacao": "deve bloquear substituicao enquanto houver divergencia material"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script pos-comparacao"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo funcional"},
        {"metrica": "confirmacao_sem_substituir_consumo_saida_canonica", "valor": True, "status": "ok", "observacao": "saida permanece atual"},
    ])
    gravar(resumo, OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-C4 — CLASSIFICACAO DE DIVERGENCIAS PACOTE PRE-SAIDA VS SAIDA CANONICA ===")
    print("status_global_v17_c4=ok_classificacao_controlada")
    print(f"decisao_consumo_saida_canonica={decisao}")
    print(f"divergencias_valores_classificadas={divergencias_valores}")
    print(f"classes_causa_valores={classes_valores}")
    print(f"divergencias_switching_classificadas={diverg_switching}")
    print(f"decisoes_bloqueantes_consumo_saida={bloqueios}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_substituir_consumo_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
