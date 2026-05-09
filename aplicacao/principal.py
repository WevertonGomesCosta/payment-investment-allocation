from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.principal import render_console
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.gerar_planilha_operacional import main as gerar_planilha_operacional
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7


def carregar_contexto_e_saida():
    """Carrega a baseline uma única vez para console e planilha."""
    contexto_baseline = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida_canonica = construir_saida_canonica_com_switching_v17_c7(contexto_baseline, versao=VERSAO_BASELINE)
    return contexto_baseline, saida_canonica


def main():
    contexto_baseline, saida_canonica = carregar_contexto_e_saida()

    render_console(contexto_baseline, saida_canonica)

    caminho_saida = gerar_planilha_operacional(
        contexto=contexto_baseline,
        saida=saida_canonica,
    )

    print(f"Saída operacional gerada em: {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    main()
