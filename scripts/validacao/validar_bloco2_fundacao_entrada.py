from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.ambiente import bootstrap_ambiente
from nucleo.cache_cdi_bcb import carregar_cache_cdi_diario
from nucleo.carregador_config import carregar_config
from nucleo.fundacao_entrada_bloco2 import (
    construir_fundacao_entrada_bloco2_do_cache,
)
from nucleo.leitor_planilha import carregar_planilha


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Valida proveniencia portatil e suficiencia temporal CDI da "
            "fundacao do Bloco 2."
        )
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=(
            RAIZ_REPOSITORIO
            / "saidas"
            / "diagnostico"
            / "bloco2_fundacao_entrada.json"
        ),
    )
    parser.add_argument(
        "--nao-bloquear",
        action="store_true",
        help="Gera diagnostico sem retornar erro quando houver bloqueios.",
    )
    return parser.parse_args()


def main() -> int:
    args = _argumentos()
    pacote_config = carregar_config(raiz_repositorio=RAIZ_REPOSITORIO)
    execucao = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=["financeiro"],
        instalar_automaticamente=False,
    )
    planilha = carregar_planilha(
        pacote_config.conteudo,
        raiz_repositorio=RAIZ_REPOSITORIO,
        caminho_explicito=RAIZ_REPOSITORIO / "dados" / "dados_financeiros.xlsx",
        data_referencia=execucao.data_referencia,
    )
    cache = carregar_cache_cdi_diario(
        None,
        pacote_config.conteudo,
        data_referencia=execucao.data_referencia,
        raiz_repositorio=RAIZ_REPOSITORIO,
        janela_consulta_cdi=planilha.janela_consulta_cdi,
    )
    fundacao = construir_fundacao_entrada_bloco2_do_cache(
        cache,
        data_referencia=execucao.data_referencia,
        raiz_repositorio=RAIZ_REPOSITORIO,
    )
    resultado = fundacao.como_dict()

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "BLOCO2_FUNDACAO_ENTRADA="
        + json.dumps(
            resultado,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    )

    if args.nao_bloquear or resultado["ok"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
