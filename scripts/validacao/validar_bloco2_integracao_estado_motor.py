from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_operacional_canonico import (
    carregar_contexto_operacional_canonico,
)
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial
from nucleo.integracao_estado_motor_canonico import (
    construir_integracao_estado_motor_canonico,
)


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Valida a integracao bloqueante entre FundacaoEntradaBloco2, "
            "EstadoEconomicoCanonico e EntradaEconomicaMotorCanonico."
        )
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=(
            RAIZ_REPOSITORIO
            / "saidas"
            / "diagnostico"
            / "bloco2_integracao_estado_motor.json"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _argumentos()
    contexto = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal = construir_estado_temporal_inicial(contexto)
    integracao = construir_integracao_estado_motor_canonico(
        contexto,
        estado_temporal,
        raiz_repositorio=RAIZ_REPOSITORIO,
    )
    resultado = integracao.resumo()
    resultado["fundacao"] = integracao.fundacao.como_dict()
    resultado["estado_economico"] = {
        "ok": integracao.estado_economico.auditoria.ok,
        "bloqueios": list(integracao.estado_economico.auditoria.bloqueios),
        "avisos": list(integracao.estado_economico.auditoria.avisos),
        "resumo": dict(integracao.estado_economico.auditoria.resumo),
    }
    resultado["entrada_motor"] = integracao.entrada_motor.como_dict()

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
        "BLOCO2_INTEGRACAO_ESTADO_MOTOR="
        + json.dumps(
            resultado,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    )
    return 0 if integracao.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
