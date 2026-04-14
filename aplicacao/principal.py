"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.ambiente import bootstrap_ambiente
from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha, construir_resumo_planilha


def main() -> None:
    pacote_config = carregar_config(raiz_repositorio=RAIZ_REPOSITORIO)
    contexto = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=["financeiro"],
        instalar_automaticamente=False,
    )
    pacote_planilha = carregar_planilha(
        pacote_config.conteudo,
        raiz_repositorio=pacote_config.raiz_repositorio,
    )

    payload = {
        "raiz_repositorio": str(pacote_config.raiz_repositorio),
        "caminho_config": str(pacote_config.caminho),
        "caminho_planilha": str(pacote_planilha.caminho),
        "timezone": contexto.timezone_nome,
        "relatorio_dependencias": contexto.relatorio_dependencias,
        "nomes_abas": pacote_planilha.nomes_abas,
        "resumo_planilha": construir_resumo_planilha(pacote_planilha),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
