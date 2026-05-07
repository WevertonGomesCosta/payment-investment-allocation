from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.matriz_pacotes_diarios import construir_matriz_pacotes_diarios, PACOTES_SWITCHING




def _num(row: pd.Series, col: str) -> int:
    try:
        return int(row.get(col, 0) or 0)
    except Exception:
        return 0


def _classificar_causa_divergencia_ponte(row: pd.Series) -> str:
    total = _num(row, "candidatos_shadow_total")
    por_data = _num(row, "candidatos_shadow_por_data")
    promoviveis = _num(row, "candidatos_shadow_promoviveis")

    if total <= 0:
        return "sem_candidato_shadow"

    if por_data <= 0:
        return "shadow_por_lote_sem_mapeamento_diario"

    if promoviveis <= 0:
        return "candidatos_shadow_existentes_mas_sem_promoviveis"

    return "candidatos_shadow_promoviveis_nao_materializados"


def _acao_recomendada_ponte(causa: str) -> str:
    mapa = {
        "sem_candidato_shadow": "verificar_geracao_shadow",
        "shadow_por_lote_sem_mapeamento_diario": "nao_inflar_contagem_diaria_sem_data",
        "candidatos_shadow_existentes_mas_sem_promoviveis": "usar_motivo_shadow_dominante",
        "candidatos_shadow_promoviveis_nao_materializados": "avaliar_materializacao_nao_decisoria",
    }
    return mapa.get(str(causa), "revisar_diagnostico_ponte")


def _classificar_causa_principal_switching_zero(df: pd.DataFrame) -> str:
    sw = df[df["pacote"].isin(list(PACOTES_SWITCHING))].copy()

    if len(sw) == 0:
        return "diagnostico_ainda_insuficiente"

    total_materializado = int(sw["pacote_materializado_no_fluxo_atual"].sum())
    if total_materializado > 0:
        return "switching_materializado_observado"

    total_construido = int(sw["pacote_construido_no_motor"].sum())
    if total_construido == 0:
        return "pacote_switching_nao_implementado"

    shadow_total = int(sw.get("candidatos_shadow_total", pd.Series([0])).max())
    shadow_mapeavel = int(sw.get("candidatos_shadow_mapeaveis_no_dia", pd.Series([0])).sum())
    shadow_promovivel = int(sw.get("candidatos_switching_promoviveis", pd.Series([0])).sum())

    if shadow_total <= 0:
        return "sem_candidato_shadow"

    if shadow_mapeavel <= 0:
        return "shadow_sem_mapeamento_diario"

    if shadow_promovivel <= 0:
        return "candidatos_shadow_existentes_mas_sem_promoviveis"

    return "candidato_switching_promovivel_nao_materializado"


def _max_col(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns:
        return 0
    s = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return int(s.max()) if len(s) else 0


def _sum_col(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns:
        return 0
    s = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return int(s.sum()) if len(s) else 0


def _sum_max_por_data(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns or "data" not in df.columns:
        return 0
    tmp = df[["data", col]].copy()
    tmp[col] = pd.to_numeric(tmp[col], errors="coerce").fillna(0)
    return int(tmp.groupby("data")[col].max().sum()) if len(tmp) else 0


def main() -> int:

    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )

    saida = construir_saida_canonica(ctx)

    df = construir_matriz_pacotes_diarios(ctx, saida, modo_observacional=True)

    out = RAIZ / "saidas/diagnostico/auditoria_matriz_pacotes_motor.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    ponte = df.copy()
    ponte["candidatos_matriz"] = ponte["candidatos_switching_disponiveis"]
    ponte["candidatos_shadow_total"] = ponte.get("candidatos_shadow_total", 0)
    ponte["candidatos_shadow_por_data"] = ponte.get("candidatos_shadow_mapeaveis_no_dia", 0)
    ponte["candidatos_shadow_por_lote_ativo"] = ponte["candidatos_shadow_por_data"]
    ponte["candidatos_shadow_bloqueados"] = ponte["candidatos_switching_bloqueados_gate"]
    ponte["candidatos_shadow_promoviveis"] = ponte["candidatos_switching_promoviveis"]
    ponte["top_motivos_shadow"] = ponte["motivo_nao_materializado"]
    ponte["origem_matriz_atual"] = "ctx.switching_economico_shadow.quadro_oportunidades"
    ponte["origem_shadow_real"] = "ctx.switching_economico_shadow.quadro_oportunidades"
    ponte["divergencia"] = (ponte["candidatos_shadow_total"] > 0) & (ponte["candidatos_shadow_por_data"] == 0)
    ponte["causa_divergencia"] = ponte.apply(_classificar_causa_divergencia_ponte, axis=1)
    ponte["acao_recomendada"] = ponte["causa_divergencia"].map(_acao_recomendada_ponte)
    ponte_cols = ["data","pacote","candidatos_matriz","candidatos_shadow_total","candidatos_shadow_por_data","candidatos_shadow_por_lote_ativo","candidatos_shadow_bloqueados","candidatos_shadow_promoviveis","top_motivos_shadow","origem_matriz_atual","origem_shadow_real","divergencia","causa_divergencia","acao_recomendada"]
    out_ponte = RAIZ / "saidas/diagnostico/auditoria_ponte_matriz_vs_shadow.csv"
    ponte[ponte_cols].to_csv(out_ponte, index=False)

    resumo = {
        "total_dias": int(df["data"].nunique()),
        "total_pacotes_conceituais": int(len(df)),
        "total_pacotes_construidos_no_motor": int(df["pacote_construido_no_motor"].sum()),
        "total_pacotes_avaliados_no_motor": int(df["pacote_avaliado_no_motor"].sum()),
        "total_switch_only_construidos": int(
            df[df["pacote"].eq("switch_only")]["pacote_construido_no_motor"].sum()
        ),
        "total_switch_then_pay_construidos": int(
            df[df["pacote"].eq("switch_then_pay")]["pacote_construido_no_motor"].sum()
        ),
        "total_pay_then_switch_construidos": int(
            df[df["pacote"].eq("pay_then_switch")]["pacote_construido_no_motor"].sum()
        ),
        "candidatos_shadow_total_unicos": _max_col(df, "candidatos_shadow_total"),
        "candidatos_shadow_mapeaveis_unicos": _sum_max_por_data(df, "candidatos_shadow_mapeaveis_no_dia"),
        "candidatos_shadow_bloqueados_unicos_por_data": _sum_max_por_data(df, "candidatos_switching_bloqueados_gate"),
        "candidatos_shadow_promoviveis_unicos_por_data": _sum_max_por_data(df, "candidatos_switching_promoviveis"),
        "candidatos_switching_disponiveis_linha_pacote": _sum_col(df, "candidatos_switching_disponiveis"),
        "candidatos_switching_bloqueados_linha_pacote": _sum_col(df, "candidatos_switching_bloqueados_gate"),
        "candidatos_switching_promoviveis_linha_pacote": _sum_col(df, "candidatos_switching_promoviveis"),
        "total_pacotes_switching_materializados": int(
            df[df["pacote"].isin(list(PACOTES_SWITCHING))]["pacote_materializado_no_fluxo_atual"].sum()
        ),
        "causa_principal_switching_zero": _classificar_causa_principal_switching_zero(df),
    }

    print(out)
    print(resumo)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
