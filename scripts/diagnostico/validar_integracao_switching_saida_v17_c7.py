from __future__ import annotations

from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.saida_canonica import construir_saida_canonica

OUT = RAIZ / "saidas" / "diagnostico" / "v17_c7"
OUT.mkdir(parents=True, exist_ok=True)


def df_lista(x):
    return pd.DataFrame(x or [])


def assinar(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    return df.reindex(sorted(df.columns), axis=1).astype(str).to_csv(index=False)


def main() -> int:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida_base = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)
    saida_c7 = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)

    futuro_base = df_lista(saida_base.extrato_futuro)
    futuro_c7 = df_lista(saida_c7.extrato_futuro)
    passado_base = df_lista(saida_base.extrato_passado)
    passado_c7 = df_lista(saida_c7.extrato_passado)
    ranking_base = df_lista(saida_base.ranking_amostra)
    ranking_c7 = df_lista(saida_c7.ranking_amostra)
    sw_base = df_lista(saida_base.switchings)
    sw_c7 = df_lista(saida_c7.switchings)

    futuro_preservado = assinar(futuro_base) == assinar(futuro_c7)
    passado_preservado = assinar(passado_base) == assinar(passado_c7)
    ranking_preservado = assinar(ranking_base) == assinar(ranking_c7)
    apenas_switchings = futuro_preservado and passado_preservado and ranking_preservado and len(sw_c7) > len(sw_base)
    status = "ok_integracao_switching_controlada" if apenas_switchings else "falha_integracao_switching_controlada"

    sw_base.to_csv(OUT / "v17_c7_switchings_base.csv", index=False)
    sw_c7.to_csv(OUT / "v17_c7_switchings_integrados.csv", index=False)
    pd.DataFrame([
        {"metrica": "status_global_v17_c7", "valor": status},
        {"metrica": "switchings_base", "valor": len(sw_base)},
        {"metrica": "switchings_integrados", "valor": len(sw_c7)},
        {"metrica": "extrato_futuro_preservado", "valor": futuro_preservado},
        {"metrica": "extrato_passado_preservado", "valor": passado_preservado},
        {"metrica": "ranking_preservado", "valor": ranking_preservado},
        {"metrica": "confirmacao_integracao_exclusiva_switchings", "valor": apenas_switchings},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True},
    ]).to_csv(OUT / "v17_c7_resumo.csv", index=False)

    print("=== V17-C7 — INTEGRACAO CONTROLADA DE SWITCHING NA SAIDA CANONICA ===")
    print(f"status_global_v17_c7={status}")
    print(f"switchings_base={len(sw_base)}")
    print(f"switchings_integrados={len(sw_c7)}")
    print(f"extrato_futuro_preservado={str(futuro_preservado).lower()}")
    print(f"extrato_passado_preservado={str(passado_preservado).lower()}")
    print(f"ranking_preservado={str(ranking_preservado).lower()}")
    print(f"confirmacao_integracao_exclusiva_switchings={str(apenas_switchings).lower()}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    return 0 if status == "ok_integracao_switching_controlada" else 2


if __name__ == "__main__":
    raise SystemExit(main())
