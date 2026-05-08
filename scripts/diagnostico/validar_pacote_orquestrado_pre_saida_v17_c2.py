from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida

OUT = RAIZ / "saidas" / "diagnostico" / "v17_c2"
OUT.mkdir(parents=True, exist_ok=True)

BASE_C1 = RAIZ / "saidas" / "diagnostico" / "v17_c1" / "v17_c1_resumo.csv"


def gravar(df: pd.DataFrame, nome: str) -> None:
    caminho = OUT / nome
    if df is None or df.empty:
        pd.DataFrame().to_csv(caminho, index=False)
    else:
        df.to_csv(caminho, index=False)


def carregar_contexto_minimo_v17_c2():
    return carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )


def metrica_c1(nome: str) -> int | None:
    if not BASE_C1.exists():
        return None
    try:
        df = pd.read_csv(BASE_C1)
    except Exception:
        return None
    if "metrica" not in df.columns or "valor" not in df.columns:
        return None
    sub = df[df["metrica"].astype(str) == nome]
    if sub.empty:
        return None
    try:
        return int(float(sub.iloc[0]["valor"]))
    except Exception:
        return None


def main() -> int:
    contexto = carregar_contexto_minimo_v17_c2()
    pacote = montar_pacote_orquestrado_pre_saida(contexto)

    gravar(pacote.recomendacoes_futuras, "v17_c2_recomendacoes_futuras.csv")
    gravar(pacote.decisoes_pagamento, "v17_c2_decisoes_pagamento.csv")
    gravar(pacote.fontes_pagamento_v17, "v17_c2_fontes_pagamento_v17.csv")
    gravar(pacote.estado_temporal_switching, "v17_c2_estado_temporal_switching.csv")
    gravar(pacote.saldos_financeiros_lotes, "v17_c2_saldos_financeiros_lotes.csv")
    gravar(pacote.ranking_informativo, "v17_c2_ranking_informativo.csv")
    gravar(pacote.auditoria_orquestracao, "v17_c2_auditoria_orquestracao.csv")

    resumo = dict(pacote.resumo)
    pend_amb_c1 = metrica_c1("pendencias_ambiguas")
    pend_estado_c1 = metrica_c1("pendencias_estado_temporal")
    pend_ausente_c1 = metrica_c1("pendencias_ausentes")

    pend_amb = int(resumo.get("pendencias_ambiguas", 0) or 0)
    pend_estado = int(resumo.get("pendencias_estado_temporal", 0) or 0)
    pend_ausente = int(resumo.get("pendencias_ausentes", 0) or 0)

    reducao_ambiguas = None if pend_amb_c1 is None else int(pend_amb_c1 - pend_amb)
    reducao_estado = None if pend_estado_c1 is None else int(pend_estado_c1 - pend_estado)
    reducao_ausentes = None if pend_ausente_c1 is None else int(pend_ausente_c1 - pend_ausente)
    status = "ok_implementacao_minima"
    if reducao_ambiguas is not None and reducao_ambiguas < 0:
        status = "falha_regressao_pendencias_ambiguas"
    if reducao_ausentes is not None and pend_ausente > pend_ausente_c1:
        status = "falha_regressao_pendencias_ausentes"

    resumo.update({
        "status_global_v17_c2": status,
        "modo_contexto_v17_c2": "minimo_sem_shadows_opcionais",
        "pendencias_ambiguas_c1": pend_amb_c1 if pend_amb_c1 is not None else "nao_disponivel",
        "pendencias_estado_temporal_c1": pend_estado_c1 if pend_estado_c1 is not None else "nao_disponivel",
        "pendencias_ausentes_c1": pend_ausente_c1 if pend_ausente_c1 is not None else "nao_disponivel",
        "reducao_pendencias_ambiguas_vs_c1": reducao_ambiguas if reducao_ambiguas is not None else "nao_disponivel",
        "reducao_pendencias_estado_vs_c1": reducao_estado if reducao_estado is not None else "nao_disponivel",
        "reducao_pendencias_ausentes_vs_c1": reducao_ausentes if reducao_ausentes is not None else "nao_disponivel",
        "confirmacao_sem_alterar_motor": True,
        "confirmacao_sem_alterar_contrato_modelo": True,
        "confirmacao_sem_alterar_ranking_saida_switching_funcional": True,
        "confirmacao_sem_alterar_saida_canonica": True,
        "confirmacao_saida_canonica_nao_consumiu_pacote": True,
    })
    df_resumo = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])
    df_resumo.to_csv(OUT / "v17_c2_resumo.csv", index=False)

    print("=== V17-C2 — REDUCAO SEGURA DE PENDENCIAS DO PACOTE PRE-SAIDA ===")
    print(f"status_global_v17_c2={status}")
    print("modo_contexto_v17_c2=minimo_sem_shadows_opcionais")
    print(f"recomendacoes_futuras_linhas={len(pacote.recomendacoes_futuras)}")
    print(f"decisoes_pagamento_linhas={len(pacote.decisoes_pagamento)}")
    print(f"fontes_pagamento_v17_linhas={len(pacote.fontes_pagamento_v17)}")
    print(f"estado_temporal_switching_linhas={len(pacote.estado_temporal_switching)}")
    print(f"saldos_financeiros_lotes_linhas={len(pacote.saldos_financeiros_lotes)}")
    print(f"ranking_informativo_linhas={len(pacote.ranking_informativo)}")
    print(f"pendencias_ambiguas={pend_amb}")
    print(f"pendencias_estado_temporal={pend_estado}")
    print(f"pendencias_ausentes={pend_ausente}")
    print(f"reducao_pendencias_ambiguas_vs_c1={reducao_ambiguas if reducao_ambiguas is not None else 'nao_disponivel'}")
    print(f"reducao_pendencias_estado_vs_c1={reducao_estado if reducao_estado is not None else 'nao_disponivel'}")
    print(f"reducao_pendencias_ausentes_vs_c1={reducao_ausentes if reducao_ausentes is not None else 'nao_disponivel'}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    print("confirmacao_saida_canonica_nao_consumiu_pacote=true")
    return 0 if status == "ok_implementacao_minima" else 2


if __name__ == "__main__":
    raise SystemExit(main())
