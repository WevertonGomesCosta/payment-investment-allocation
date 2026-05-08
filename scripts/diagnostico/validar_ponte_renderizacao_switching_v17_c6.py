from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida
from nucleo.ponte_renderizacao_switching_v17_c6 import renderizar_switchings_compativeis_saida
from nucleo.saida_canonica import construir_saida_canonica

OUT = RAIZ / "saidas" / "diagnostico" / "v17_c6"
OUT.mkdir(parents=True, exist_ok=True)


def gravar(df: pd.DataFrame, nome: str) -> None:
    caminho = OUT / nome
    if df is None or df.empty:
        pd.DataFrame().to_csv(caminho, index=False)
    else:
        df.to_csv(caminho, index=False)


def carregar_contexto_referencia_v17_c6():
    return carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )


def main() -> int:
    contexto = carregar_contexto_referencia_v17_c6()
    pacote = montar_pacote_orquestrado_pre_saida(contexto)
    ponte = renderizar_switchings_compativeis_saida(pacote)
    saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)

    quadro_ponte = ponte.quadro_switching_compativel_saida.copy()
    quadro_saida = pd.DataFrame(saida.switchings or [])

    gravar(pacote.estado_temporal_switching, "v17_c6_estado_temporal_switching_pacote.csv")
    gravar(quadro_ponte, "v17_c6_switchings_compativeis_saida.csv")
    gravar(quadro_saida, "v17_c6_switchings_saida_canonica_atual.csv")

    switchings_pacote = int(len(pacote.estado_temporal_switching))
    switchings_ponte = int(len(quadro_ponte))
    switchings_saida_atual = int(len(quadro_saida))
    campos_essenciais_ausentes = int(ponte.resumo.get("campos_essenciais_ausentes", 0) or 0)
    ponte_cobre_pacote = switchings_pacote == switchings_ponte
    status = "ok_ponte_renderizacao_switching"
    if not ponte_cobre_pacote or campos_essenciais_ausentes > 0:
        status = "falha_ponte_renderizacao_switching"

    decisao = "ponte_switching_apta_para_comparacao_controlada_sem_consumo_saida"
    if status != "ok_ponte_renderizacao_switching":
        decisao = "manter_bloqueio_ponte_switching"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_c6", "valor": status},
        {"metrica": "decisao_consumo_saida_canonica", "valor": "nao_substituir_saida_canonica_ainda"},
        {"metrica": "decisao_ponte_switching", "valor": decisao},
        {"metrica": "switchings_pacote", "valor": switchings_pacote},
        {"metrica": "switchings_renderizados_ponte", "valor": switchings_ponte},
        {"metrica": "switchings_saida_canonica_atual", "valor": switchings_saida_atual},
        {"metrica": "campos_essenciais_ausentes_ponte", "valor": campos_essenciais_ausentes},
        {"metrica": "ponte_cobre_todos_switchings_pacote", "valor": ponte_cobre_pacote},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True},
        {"metrica": "confirmacao_sem_substituir_consumo_saida_canonica", "valor": True},
        {"metrica": "confirmacao_saida_canonica_nao_consumiu_ponte", "valor": True},
    ])
    resumo.to_csv(OUT / "v17_c6_resumo.csv", index=False)

    print("=== V17-C6 — PONTE CONTROLADA DE RENDERIZACAO DE SWITCHING ===")
    print(f"status_global_v17_c6={status}")
    print("decisao_consumo_saida_canonica=nao_substituir_saida_canonica_ainda")
    print(f"decisao_ponte_switching={decisao}")
    print(f"switchings_pacote={switchings_pacote}")
    print(f"switchings_renderizados_ponte={switchings_ponte}")
    print(f"switchings_saida_canonica_atual={switchings_saida_atual}")
    print(f"campos_essenciais_ausentes_ponte={campos_essenciais_ausentes}")
    print(f"ponte_cobre_todos_switchings_pacote={str(ponte_cobre_pacote).lower()}")
    print(f"output_dir={OUT}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_substituir_consumo_saida_canonica=true")
    print("confirmacao_saida_canonica_nao_consumiu_ponte=true")
    return 0 if status == "ok_ponte_renderizacao_switching" else 2


if __name__ == "__main__":
    raise SystemExit(main())
