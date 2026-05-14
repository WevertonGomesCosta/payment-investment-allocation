from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b

CSV = RAIZ / "saidas" / "diagnostico" / "auditoria_matriz_elegibilidade_fontes_v17_f0_s7b.csv"


def main() -> int:
    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    try:
        df = construir_matriz_elegibilidade_fontes_s7b(ctx)
    except (ValueError, RuntimeError) as exc:
        msg = str(exc)
        if "erro_coluna_classe_s6_nao_encontrada" in msg:
            print("status_geral_s7b=erro_coluna_classe_s6_nao_encontrada")
            return 2
        if "erro_csv_s6_indisponivel_para_matriz_elegibilidade" in msg:
            print("status_geral_s7b=erro_csv_s6_indisponivel_para_matriz_elegibilidade")
            return 3
        if "erro_s6_csv_nao_produzido" in msg:
            print("status_geral_s7b=erro_s6_csv_nao_produzido")
            return 4
        if "erro_csv_s6_vazio_para_matriz_elegibilidade" in msg:
            print("status_geral_s7b=erro_csv_s6_vazio_para_matriz_elegibilidade")
            return 5
        raise
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False)

    qtd = len(df)
    elegiveis = int((df["elegivel_para_pagamento"] == "sim").sum())
    bloqueadas = int((df["elegivel_para_pagamento"] == "nao").sum())
    bloqueada = (df["elegivel_para_pagamento"] == "nao") & (df["pode_ser_lote_sugerido"] == "nao")
    prev = int(((df["classe_temporal_s6"] == "salario_previsto_futuro_nao_materializado") & bloqueada).sum())
    lac = int(((df["classe_temporal_s6"] == "lacuna_real_de_integracao") & bloqueada).sum())
    pre = int(((df["classe_temporal_s6"] == "uso_pre_aplicacao_no_mes_sem_vinculo_linha") & bloqueada).sum())
    exauridos = int((df["motivo_bloqueio"] == "lote_exaurido").sum())
    migrados = int((df["motivo_bloqueio"] == "lote_migrado_por_switching").sum())
    pos_elegiveis = int(((df["status_ciclo"] == "ativo_pos_switching") & (df["elegivel_para_pagamento"] == "sim")).sum())
    saldo_insuf = int((df["motivo_bloqueio_cumulativo"] == "nao_disponivel_sem_motor").sum())

    s190 = df[df["fonte_id"].astype(str).str.contains("190 mai", case=False, na=False)]
    s3120 = df[df["fonte_id"].astype(str).str.contains("3120 mai", case=False, na=False)]

    print("=== AUDITORIA V17-F0-S.7-B — MATRIZ ELEGIBILIDADE FONTES ===")
    print(f"qtd_fontes_avaliadas={qtd}")
    print(f"qtd_fontes_elegiveis_para_pagamento={elegiveis}")
    print(f"qtd_fontes_bloqueadas={bloqueadas}")
    print(f"qtd_salarios_previstos_bloqueados={prev}")
    print(f"qtd_lacunas_reais_bloqueadas={lac}")
    print(f"qtd_uso_pre_aplicacao_sem_vinculo_bloqueados={pre}")
    print(f"qtd_lotes_exauridos_bloqueados={exauridos}")
    print(f"qtd_lotes_migrados_bloqueados={migrados}")
    print(f"qtd_lotes_pos_switching_elegiveis={pos_elegiveis}")
    print(f"qtd_fontes_com_saldo_temporal_insuficiente={saldo_insuf}")
    print(f"coluna_classe_s6_usada={df['coluna_classe_s6_usada'].iloc[0] if 'coluna_classe_s6_usada' in df.columns and not df.empty else 'indisponivel'}")
    print(f"sentinela_lote_190_nao_elegivel={'sim' if (not s190.empty and (s190['elegivel_para_pagamento'] == 'nao').all()) else 'nao'}")
    print(f"sentinela_lote_3120_ativo_pos={'sim' if (not s3120.empty and (s3120['status_ciclo'] == 'ativo_pos_switching').any()) else 'nao'}")
    print("status_geral_s7b=matriz_elegibilidade_fontes_construida")
    print(f"csv={CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
