"""Integração bloqueante entre fundação, estado econômico e novo motor.

A integração é executada no fluxo principal antes do motor temporal legado.
Nesta etapa ela apenas valida e materializa a futura entrada exclusiva; não
substitui o motor legado nem altera ledger, console ou XLSX.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from nucleo.entrada_economica_motor_canonico import (
    EntradaEconomicaMotorCanonico,
    construir_entrada_economica_motor_canonico,
    exigir_entrada_economica_motor_canonico,
)
from nucleo.estado_economico_canonico import (
    EstadoEconomicoCanonico,
    construir_estado_economico_canonico,
    exigir_estado_economico_canonico_valido,
)
from nucleo.fundacao_entrada_bloco2 import (
    FundacaoEntradaBloco2,
    construir_fundacao_entrada_bloco2,
    exigir_fundacao_entrada_bloco2_valida,
)


@dataclass(frozen=True, slots=True)
class IntegracaoEstadoMotorCanonico:
    fundacao: FundacaoEntradaBloco2
    estado_economico: EstadoEconomicoCanonico
    entrada_motor: EntradaEconomicaMotorCanonico
    metadados: Mapping[str, Any]

    @property
    def ok(self) -> bool:
        return bool(
            self.fundacao.ok
            and self.estado_economico.auditoria.ok
            and self.entrada_motor.auditoria.ok
        )

    def resumo(self) -> dict[str, Any]:
        return {
            "artefato": "IntegracaoEstadoMotorCanonico",
            "ok": self.ok,
            "data_referencia": self.entrada_motor.data_referencia.isoformat(),
            "fundacao_ok": self.fundacao.ok,
            "estado_economico_ok": self.estado_economico.auditoria.ok,
            "entrada_motor_ok": self.entrada_motor.auditoria.ok,
            "qtd_fontes_disponiveis": len(
                self.entrada_motor.fontes_disponiveis
            ),
            "qtd_unidades_bloqueadas": len(
                self.entrada_motor.unidades_bloqueadas
            ),
            "qtd_unidades_encerradas": len(
                self.entrada_motor.unidades_encerradas
            ),
            "valor_total_disponivel": self.entrada_motor.auditoria.resumo.get(
                "valor_total_disponivel"
            ),
            "metadados": dict(self.metadados),
        }


def construir_integracao_estado_motor_canonico(
    contexto_operacional: Any,
    estado_temporal_inicial: Any,
    *,
    raiz_repositorio: Path,
) -> IntegracaoEstadoMotorCanonico:
    fundacao = construir_fundacao_entrada_bloco2(
        contexto_operacional,
        raiz_repositorio=raiz_repositorio,
    )
    exigir_fundacao_entrada_bloco2_valida(fundacao)

    estado_economico = construir_estado_economico_canonico(
        estado_temporal_inicial
    )
    exigir_estado_economico_canonico_valido(estado_economico)

    entrada_motor = construir_entrada_economica_motor_canonico(
        estado_economico,
        fundacao,
    )
    exigir_entrada_economica_motor_canonico(entrada_motor)

    return IntegracaoEstadoMotorCanonico(
        fundacao=fundacao,
        estado_economico=estado_economico,
        entrada_motor=entrada_motor,
        metadados={
            "ordem_fluxo": (
                "FundacaoEntradaBloco2",
                "EstadoEconomicoCanonico",
                "EntradaEconomicaMotorCanonico",
            ),
            "executada_antes_motor_temporal_legado": True,
            "motor_temporal_legado_preservado": True,
            "altera_decisao_economica": False,
            "altera_ledger": False,
            "altera_console": False,
            "altera_xlsx": False,
        },
    )


__all__ = [
    "IntegracaoEstadoMotorCanonico",
    "construir_integracao_estado_motor_canonico",
]
