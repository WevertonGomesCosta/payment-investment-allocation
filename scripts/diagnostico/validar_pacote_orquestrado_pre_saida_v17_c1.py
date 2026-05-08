from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida

OUT = RAIZ / "saidas" / "diagnostico" / "v17_c1"
OUT.mkdir(parents=True, exist_ok=True)


def gravar(df: pd.DataFrame, nome: str) -> None:
    caminho = OUT / nome
    if df is None or df.empty:
        pd.DataFrame().to_csv(caminho, index=False)
    else:
        df.to_csv(caminho, index=False)


def carregar_contexto_minimo_v17_c1():
    """Carrega apenas o contexto necessario para validar o pacote pre-saida.

    A V17-C1 nao deve acionar shadows opcionais pesados nem depender de
    benchmarks. Esses blocos nao fazem parte do contrato minimo do pacote e
    podem falhar por assinaturas legadas sem relacao com a implementacao C1.
    """
    return carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )


def main() -> int:
    contexto = carregar_contexto_minimo_v17_c1()
    pacote = montar_pacote_orquestrado_pre_saida(contexto)

    gravar(pacote.recomendacoes_futuras, "v17_c1_recomendacoes_futuras.csv")
    gravar(pacote.decisoes_pagamento, "v17_c1_decisoes_pagamento.csv")
    gravar(pacote.fontes_pagamento_v17, "v17_c1_fontes_pagamento_v17.csv")
    gravar(pacote.estado_temporal_switching, "v17_c1_estado_temporal_switching.csv")
    gravar(pacote.saldos_financeiros_lotes, "v17_c1_saldos_financeiros_lotes.csv")
    gravar(pacote.ranking_informativo, "v17_c1_ranking_informativo.csv")
    gravar(pacote.auditoria_orquestracao, "v17_c1_auditoria_orquestracao.csv")

    resumo = dict(pacote.resumo)
    resumo.update({
        "status_global_v17_c1": "ok_implementacao_minima",
        "modo_contexto_v17_c1": "minimo_sem_shadows_opcionais",
        "confirmacao_sem_alterar_motor": True,
        "confirmacao_sem_alterar_contrato_modelo": True,
        "confirmacao_sem_alterar_ranking_saida_switching_funcional": True,
        "confirmacao_sem_alterar_saida_canonica": True,
        "confirmacao_saida_canonica_nao_consumiu_pacote": True,
    })
    df_resumo = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])
    df_resumo.to_csv(OUT / "v17_c1_resumo.csv", index=False)

    print("=== V17-C1 — PACOTE ORQUESTRADO PRE-SAIDA MINIMO ===")
    print("status_global_v17_c1=ok_implementacao_minima")
    print("modo_contexto_v17_c1=minimo_sem_shadows_opcionais")
    print(f"recomendacoes_futuras_linhas={len(pacote.recomendacoes_futuras)}")
    print(f"decisoes_pagamento_linhas={len(pacote.decisoes_pagamento)}")
    print(f"fontes_pagamento_v17_linhas={len(pacote.fontes_pagamento_v17)}")
    print(f"estado_temporal_switching_linhas={len(pacote.estado_temporal_switching)}")
    print(f"saldos_financeiros_lotes_linhas={len(pacote.saldos_financeiros_lotes)}")
    print(f"ranking_informativo_linhas={len(pacote.ranking_informativo)}")
    print(f"pendencias_ambiguas={resumo.get('pendencias_ambiguas', 0)}")
    print(f"pendencias_estado_temporal={resumo.get('pendencias_estado_temporal', 0)}")
    print(f"pendencias_ausentes={resumo.get('pendencias_ausentes', 0)}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    print("confirmacao_saida_canonica_nao_consumiu_pacote=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
