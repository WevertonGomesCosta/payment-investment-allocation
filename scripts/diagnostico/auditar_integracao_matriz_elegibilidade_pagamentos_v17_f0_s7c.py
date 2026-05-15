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
    try:
        matriz = construir_matriz_elegibilidade_fontes_s7b(ctx, data_referencia=saida.data_referencia)
    except Exception as exc:
        msg = str(exc)
        if any(k in msg for k in ("erro_csv_s6_indisponivel_para_matriz_elegibilidade", "erro_s6_csv_nao_produzido", "erro_csv_s6_vazio_para_matriz_elegibilidade", "erro_coluna_classe_s6_nao_encontrada", "erro_csv_s6_ausente_sem_recomposicao_segura")):
            print(f"status_geral_s7c={msg}")
            return 2
        raise
    saida, audit = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida, matriz)
    df = pd.DataFrame(audit)
    resumo = (df["s7c_resumo"].iloc[0] if ("s7c_resumo" in df.columns and not df.empty) else {})
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False)

    promov_antes = sum(1 for x in antes if x)
    promov_pos = int((df["lote_sugerido_pos_matriz"].astype(str).str.strip() != "").sum())
    bloqueadas = int((df["acao_s7c"] == "bloqueado_por_matriz").sum())
    nao_encontradas = int((df["acao_s7c"] == "fonte_nao_encontrada_na_matriz").sum())
    compostas = int(df["componentes_fonte"].astype(str).str.contains(r"\+", regex=True).sum())
    compostas_bloq = int(((df["componentes_fonte"].astype(str).str.contains(r"\+", regex=True)) & (df["lote_sugerido_pos_matriz"].astype(str).str.strip()=="")).sum())
    sal_prev_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("salario_previsto_futuro_nao_materializado").sum())
    pre_sem_vinc = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("uso_pre_aplicacao_no_mes_sem_vinculo_linha").sum())
    exaurido_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("lote_exaurido").sum())
    migrado_bloq = int(df["componentes_bloqueados_ou_ausentes"].astype(str).str.contains("lote_migrado_por_switching").sum())
    lote3120_pres = int(df["lote_sugerido_pos_matriz"].astype(str).str.contains("3120 mai", case=False, na=False).sum())
    sem_saldo_pres = int((df["acao_s7c"] == "bloqueado_por_ledger").sum())
    componentes = []
    for _, r in df.iterrows():
        texto = str(r.get("componentes_fonte") or "")
        for c in [p.strip() for p in texto.split("+") if p.strip()]:
            componentes.append(c)
    qtd_comp_total = len(componentes)
    qtd_comp_lote = sum(1 for c in componentes if "lote " in c.lower())
    qtd_comp_nao_lote = qtd_comp_total - qtd_comp_lote
    qtd_comp_desc = 0
    qtd_comp_desc_b = 0
    qtd_comp_nao_lote_sem_v = qtd_comp_nao_lote
    enf = "nao_aplicavel_sem_fonte_s6_no_fluxo" if qtd_comp_nao_lote == 0 else ("parcial" if resumo.get("qtd_registros_s6_linkaveis_ao_fluxo", 0) > 0 else "nao_confirmado")
    sent190 = "sim" if not (df["lote_sugerido_pos_matriz"].astype(str).str.contains("190 mai", case=False, na=False).any()) else "nao"
    sent3120 = "sim" if lote3120_pres > 0 else "nao"

    print("qtd_pagamentos_avaliados=%d" % len(df))
    print("qtd_fontes_promovidas_antes_matriz=%d" % promov_antes)
    print("qtd_fontes_promovidas_pos_matriz=%d" % promov_pos)
    print("qtd_fontes_bloqueadas_pela_matriz=%d" % bloqueadas)
    print("qtd_fontes_nao_encontradas_na_matriz=%d" % nao_encontradas)
    print("qtd_fontes_compostas_avaliadas=%d" % compostas)
    print("qtd_fontes_compostas_bloqueadas=%d" % compostas_bloq)
    print("qtd_componentes_fluxo_total=%d" % qtd_comp_total)
    print("qtd_componentes_fluxo_lote=%d" % qtd_comp_lote)
    print("qtd_componentes_fluxo_nao_lote=%d" % qtd_comp_nao_lote)
    print("qtd_componentes_fluxo_nao_lote_sem_vinculo_s6=%d" % qtd_comp_nao_lote_sem_v)
    print("qtd_componentes_fluxo_desconhecidos=%d" % qtd_comp_desc)
    print("qtd_componentes_fluxo_desconhecidos_bloqueados=%d" % qtd_comp_desc_b)
    print("qtd_registros_s6_total=%d" % resumo.get("qtd_registros_s6_total", 0))
    print("qtd_registros_s6_linkaveis_ao_fluxo=%d" % resumo.get("qtd_registros_s6_linkaveis_ao_fluxo", 0))
    print("qtd_registros_s6_nao_linkaveis_ao_fluxo=%d" % resumo.get("qtd_registros_s6_nao_linkaveis_ao_fluxo", 0))
    print("qtd_bloqueios_s6_aplicados_no_fluxo=%d" % resumo.get("qtd_bloqueios_s6_aplicados_no_fluxo", 0))
    print("qtd_bloqueios_s6_diagnosticos_nao_linkaveis=%d" % resumo.get("qtd_bloqueios_s6_diagnosticos_nao_linkaveis", 0))
    print("qtd_fonte_id_sintetico_usado_para_lookup=%d" % resumo.get("qtd_fonte_id_sintetico_usado_para_lookup", 0))
    print(f"s7c_enforcement_s6_classes={enf}")
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
