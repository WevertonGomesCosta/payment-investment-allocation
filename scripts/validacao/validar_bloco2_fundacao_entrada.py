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
from nucleo.leitor_planilha import carregar_planilha
from nucleo.proveniencia_portatil import auditar_json_portatil
from nucleo.suficiencia_temporal_cdi import avaliar_suficiencia_temporal_cdi


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
    janela = planilha.janela_consulta_cdi
    cache = carregar_cache_cdi_diario(
        None,
        pacote_config.conteudo,
        data_referencia=execucao.data_referencia,
        raiz_repositorio=RAIZ_REPOSITORIO,
        janela_consulta_cdi=janela,
    )

    proveniencia = auditar_json_portatil(
        cache.caminho_cache,
        raiz_repositorio=RAIZ_REPOSITORIO,
    )
    suficiencia = avaliar_suficiencia_temporal_cdi(
        cache.serie_cdi,
        data_inicial_consulta=cache.data_inicial_consulta,
        data_final_consulta=cache.data_final_consulta,
        data_referencia=execucao.data_referencia,
        datas_requeridas=(),
        datas_sem_observacao_permitidas=(),
        max_defasagem_dias=2,
        max_lacuna_inicial_dias=1,
    )

    bloqueios: list[str] = []
    avisos: list[str] = []
    if not proveniencia.ok:
        bloqueios.append("Proveniencia semantica do cache JSON invalida.")
    if proveniencia.status_git:
        bloqueios.append("Cache JSON possui alteracoes locais nao versionadas.")
    if not proveniencia.git_blob_sha:
        bloqueios.append("Git blob SHA do cache JSON nao foi resolvido.")
    if not suficiencia.ok:
        bloqueios.extend(suficiencia.bloqueios)
    avisos.extend(suficiencia.avisos)

    resultado = {
        "artefato": "FundacaoEntradaBloco2",
        "bloco": "BLOCO-2-FUNDACAO",
        "ok": not bloqueios,
        "bloqueios": bloqueios,
        "avisos": avisos,
        "data_referencia": execucao.data_referencia.isoformat(),
        "proveniencia_cache_json": proveniencia.como_dict(),
        "suficiencia_temporal_cdi": suficiencia.como_dict(),
        "auditoria_cache_cdi": cache.auditoria,
        "limites_preservados": {
            "conecta_estado_ao_motor": False,
            "gera_pacotes": False,
            "executa_argmax": False,
            "altera_ledger": False,
            "altera_console_operacional": False,
            "altera_xlsx": False,
        },
    }

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
        + json.dumps(resultado, ensure_ascii=False, sort_keys=True, default=str)
    )

    if args.nao_bloquear or resultado["ok"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
