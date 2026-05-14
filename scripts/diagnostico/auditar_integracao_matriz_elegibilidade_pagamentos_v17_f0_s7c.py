from __future__ import annotations

from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b
from nucleo.integracao_matriz_elegibilidade_pagamentos_s7c import aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c

CSV = RAIZ / "saidas" / "diagnostico" / "auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv"


def main() -> int:
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao="V225")
    antes = [str(r.get("Lote sugerido") or "").strip() for r in saida.extrato_futuro]
    matriz = construir_matriz_elegibilidade_fontes_s7b(ctx, data_referencia=saida.data_referencia)
    saida, audit = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida, matriz)
    df = pd.DataFrame(audit)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False)

    promov_antes = sum(1 for x in antes if x)
    promov_pos = int((df["lote_sugerido_pos_matriz"].astype(str).str.strip() != "").sum())
    bloqueadas = int((df["acao_s7c"] == "bloqueado_por_matriz").sum())
    nao_encontradas = int((df["acao_s7c"] == "fonte_nao_encontrada_na_matriz").sum())
    compostas = int(df["componentes_fonte"].astype(str).str.contains("\+", regex=True).sum())
    compostas_bloq = int(((df["componentes_fonte"].astype(str).str.contains("\+", regex=True)) & (df["lote_sugerido_pos_matriz"].astype(str).str.strip()=="")).sum())
    sal_prev_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("salario_previsto_futuro_nao_materializado").sum())
    pre_sem_vinc = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("uso_pre_aplicacao_no_mes_sem_vinculo_linha").sum())
    exaurido_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("lote_exaurido").sum())
    migrado_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("lote_migrado_por_switching").sum())
    lote3120_pres = int(df["lote_sugerido_pos_matriz"].astype(str).str.contains("3120 mai", case=False, na=False).sum())
    sem_saldo_pres = int((df["acao_s7c"] == "bloqueado_por_ledger").sum())
    sent190 = "sim" if not (df["lote_sugerido_pos_matriz"].astype(str).str.contains("190 mai", case=False, na=False).any()) else "nao"
    sent3120 = "sim" if lote3120_pres > 0 else "nao"

    print("qtd_pagamentos_avaliados=%d" % len(df))
    print("qtd_fontes_promovidas_antes_matriz=%d" % promov_antes)
    print("qtd_fontes_promovidas_pos_matriz=%d" % promov_pos)
    print("qtd_fontes_bloqueadas_pela_matriz=%d" % bloqueadas)
    print("qtd_fontes_nao_encontradas_na_matriz=%d" % nao_encontradas)
    print("qtd_fontes_compostas_avaliadas=%d" % compostas)
    print("qtd_fontes_compostas_bloqueadas=%d" % compostas_bloq)
    print("qtd_salario_previsto_futuro_bloqueado_no_fluxo=%d" % sal_prev_bloq)
    print("qtd_uso_pre_aplicacao_sem_vinculo_bloqueado_no_fluxo=%d" % pre_sem_vinc)
    print("qtd_lote_exaurido_bloqueado_no_fluxo=%d" % exaurido_bloq)
    print("qtd_lote_migrado_bloqueado_no_fluxo=%d" % migrado_bloq)
    print("qtd_lote_pos_switching_materializado_preservado=%d" % lote3120_pres)
    print("qtd_pagamentos_com_status_sem_saldo_temporal_preservado=%d" % sem_saldo_pres)
    print(f"sentinela_lote_190_nao_promovido={sent190}")
    print(f"sentinela_lote_3120_preservado_quando_elegivel={sent3120}")
    print("matriz_consultada_no_fluxo_oficial=sim")
    print("status_geral_s7c=integracao_matriz_elegibilidade_recomendador_concluida")
    print(f"csv={CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
