from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.matriz_pacotes_diarios import construir_matriz_pacotes_diarios, PACOTES_SWITCHING




def _classificar_causa_principal_switching_zero(df: pd.DataFrame) -> str:
    sw = df[df["pacote"].isin(list(PACOTES_SWITCHING))].copy()

    if len(sw) == 0:
        return "diagnostico_ainda_insuficiente"

    total_construido = int(sw["pacote_construido_no_motor"].sum())
    total_materializado = int(sw["pacote_materializado_no_fluxo_atual"].sum())

    if total_materializado > 0:
        return "switching_materializado_observado"

    if total_construido == 0:
        return "pacote_switching_nao_implementado"

    motivos = (
        sw["motivo_nao_materializado"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace({"": "n/d"})
    )

    contagens = motivos.value_counts()

    prioridade = [
        "sem_candidato_switching",
        "bloqueado_por_gate",
        "candidato_switching_promovivel_nao_materializado",
        "pacote_nao_materializado_por_restricao_da_etapa",
        "comparador_de_pacotes_ainda_nao_decisorio",
        "ledger_nao_materializa_pacote",
    ]

    for motivo in prioridade:
        if motivo in contagens.index:
            if motivo == "candidato_switching_promovivel_nao_materializado":
                return "switching_nao_materializado_na_etapa"
            return motivo

    return str(contagens.index[0]) if len(contagens) else "diagnostico_ainda_insuficiente"


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
        "total_candidatos_switching_disponiveis": int(df["candidatos_switching_disponiveis"].sum()),
        "total_candidatos_switching_bloqueados_gate": int(df["candidatos_switching_bloqueados_gate"].sum()),
        "total_candidatos_switching_promoviveis": int(df["candidatos_switching_promoviveis"].sum()),
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
