from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.principal import render_console
from nucleo.contexto_operacional_canonico import carregar_contexto_operacional_canonico
from nucleo.gerar_planilha_operacional import main as gerar_planilha_operacional
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial
from nucleo.motor_temporal_conjunto import construir_resultado_motor_temporal_conjunto
from nucleo.ledger_temporal_canonico import construir_ledger_temporal_canonico
from nucleo.gates_validacao_nucleo import validar_gates_nucleo
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b
from nucleo.integracao_matriz_elegibilidade_pagamentos_s7c import aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c


def carregar_contexto_e_saida():
    """Carrega a cadeia canônica Etapas 1-4 e constrói a saída estrutural inicial da Etapa 5."""
    contexto_operacional_canonico = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal_inicial = construir_estado_temporal_inicial(contexto_operacional_canonico)
    resultado_motor_temporal_conjunto = construir_resultado_motor_temporal_conjunto(estado_temporal_inicial)
    ledger_temporal_canonico = construir_ledger_temporal_canonico(resultado_motor_temporal_conjunto)
    resultado_gates_validacao_nucleo = validar_gates_nucleo(ledger_temporal_canonico)
    saida_canonica = construir_saida_canonica_com_switching_v17_c7(contexto_operacional_canonico, versao=VERSAO_BASELINE)
    matriz = construir_matriz_elegibilidade_fontes_s7b(
        contexto_operacional_canonico,
        data_referencia=saida_canonica.data_referencia,
        saida_canonica_preconstruida=saida_canonica,
    )
    saida_canonica, _ = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz)
    return contexto_operacional_canonico, estado_temporal_inicial, resultado_motor_temporal_conjunto, ledger_temporal_canonico, resultado_gates_validacao_nucleo, saida_canonica


def main():
    contexto_operacional_canonico, estado_temporal_inicial, resultado_motor_temporal_conjunto, ledger_temporal_canonico, resultado_gates_validacao_nucleo, saida_canonica = carregar_contexto_e_saida()

    _ = resultado_motor_temporal_conjunto
    _ = ledger_temporal_canonico

    if not resultado_gates_validacao_nucleo.pronto_para_etapa8:
        print(
            "Execução bloqueada pelos gates de validação de núcleo: "
            "ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False. "
            "Console e XLSX oficiais não foram gerados."
        )
        return None

    render_console(contexto_operacional_canonico, saida_canonica, estado_temporal_inicial=estado_temporal_inicial)

    caminho_saida = gerar_planilha_operacional(
        contexto=contexto_operacional_canonico,
        saida=saida_canonica,
    )

    print(f"Saída operacional gerada em: {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    main()
