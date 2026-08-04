from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_operacional_canonico import carregar_contexto_operacional_canonico
from nucleo.estado_economico_canonico import (
    construir_estado_economico_canonico,
    exigir_estado_economico_canonico_valido,
)
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida identidade econômica e conservação patrimonial do Bloco 1."
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=RAIZ_REPOSITORIO / "saidas" / "diagnostico" / "estado_economico_canonico_bloco1.json",
        help="Caminho do JSON diagnóstico.",
    )
    parser.add_argument(
        "--nao-bloquear",
        action="store_true",
        help="Gera o diagnóstico sem retornar erro quando houver bloqueios.",
    )
    return parser.parse_args()


def main() -> int:
    args = _argumentos()
    contexto = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal = construir_estado_temporal_inicial(contexto)
    estado_economico = construir_estado_economico_canonico(estado_temporal)

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(estado_economico.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    resumo = dict(estado_economico.auditoria.resumo)
    saida_console = {
        "artefato": estado_economico.metadados.get("artefato"),
        "bloco": estado_economico.metadados.get("bloco"),
        "ok": estado_economico.auditoria.ok,
        "bloqueios": estado_economico.auditoria.bloqueios,
        "avisos": estado_economico.auditoria.avisos,
        "resumo": resumo,
        "arquivo": str(args.saida),
    }
    print("BLOCO1_ESTADO_ECONOMICO_CANONICO=" + json.dumps(saida_console, ensure_ascii=False, sort_keys=True))

    if args.nao_bloquear:
        return 0
    exigir_estado_economico_canonico_valido(estado_economico)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
