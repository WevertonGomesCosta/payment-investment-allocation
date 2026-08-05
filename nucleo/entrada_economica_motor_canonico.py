"""Interface econômica exclusiva do novo motor.

A interface é uma projeção imutável do EstadoEconomicoCanonico. Ela transporta
somente identidades econômicas, saldos líquidos atuais e estados de ciclo já
auditados. ContextoOperacionalCanonico, EstadoTemporalInicial, listas e mapas
legados são recusados sem coerção.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import json
from typing import Any, Mapping

from nucleo.estado_economico_canonico import (
    EstadoEconomicoCanonico,
    exigir_estado_economico_canonico_valido,
)
from nucleo.fundacao_entrada_bloco2 import (
    FundacaoEntradaBloco2,
    exigir_fundacao_entrada_bloco2_valida,
)


_ESTADOS_ENCERRADOS_MOTOR = {
    "aplicado_em_lote",
    "consumido_ou_vinculado",
    "exaurido_sem_saldo_atual",
    "exaurido",
    "exaurido_por_saque",
    "exaurido_por_switching",
    "migrado_por_switching",
}


@dataclass(frozen=True, slots=True)
class UnidadeEconomicaEntradaMotor:
    unidade_id: str
    identidade_origem: str
    tipo_unidade: str
    estado_ciclo: str
    valor_liquido_atual: float
    produto: str | None
    data_origem: date | None
    data_aplicacao: date | None
    data_disponibilidade_resgate: date | None


@dataclass(frozen=True, slots=True)
class AuditoriaEntradaEconomicaMotorCanonico:
    ok: bool
    bloqueios: tuple[str, ...]
    resumo: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class EntradaEconomicaMotorCanonico:
    data_referencia: date
    fontes_disponiveis: tuple[UnidadeEconomicaEntradaMotor, ...]
    unidades_bloqueadas: tuple[UnidadeEconomicaEntradaMotor, ...]
    unidades_encerradas: tuple[UnidadeEconomicaEntradaMotor, ...]
    eventos_conservacao_ids: tuple[str, ...]
    auditoria: AuditoriaEntradaEconomicaMotorCanonico
    metadados: Mapping[str, Any]

    def como_dict(self) -> dict[str, Any]:
        def serializar(unidade: UnidadeEconomicaEntradaMotor) -> dict[str, Any]:
            dados = asdict(unidade)
            for campo in (
                "data_origem",
                "data_aplicacao",
                "data_disponibilidade_resgate",
            ):
                valor = dados.get(campo)
                dados[campo] = valor.isoformat() if isinstance(valor, date) else None
            return dados

        return {
            "artefato": "EntradaEconomicaMotorCanonico",
            "data_referencia": self.data_referencia.isoformat(),
            "fontes_disponiveis": [serializar(item) for item in self.fontes_disponiveis],
            "unidades_bloqueadas": [serializar(item) for item in self.unidades_bloqueadas],
            "unidades_encerradas": [serializar(item) for item in self.unidades_encerradas],
            "eventos_conservacao_ids": list(self.eventos_conservacao_ids),
            "auditoria": {
                "ok": self.auditoria.ok,
                "bloqueios": list(self.auditoria.bloqueios),
                "resumo": dict(self.auditoria.resumo),
            },
            "metadados": dict(self.metadados),
        }


class EntradaEconomicaMotorCanonicoInvalida(TypeError):
    pass


def _snapshot_unidade(unidade: Any) -> UnidadeEconomicaEntradaMotor:
    return UnidadeEconomicaEntradaMotor(
        unidade_id=str(unidade.unidade_id),
        identidade_origem=str(unidade.identidade_origem),
        tipo_unidade=str(unidade.tipo_unidade),
        estado_ciclo=str(unidade.estado_ciclo),
        valor_liquido_atual=round(float(unidade.valor_liquido_atual), 10),
        produto=unidade.produto,
        data_origem=unidade.data_origem,
        data_aplicacao=unidade.data_aplicacao,
        data_disponibilidade_resgate=unidade.data_disponibilidade_resgate,
    )


def _hash_estado(estado: EstadoEconomicoCanonico) -> str:
    conteudo = json.dumps(
        estado.como_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(conteudo).hexdigest()


def construir_entrada_economica_motor_canonico(
    estado: EstadoEconomicoCanonico,
    fundacao: FundacaoEntradaBloco2,
    *,
    tolerancia_monetaria: float = 0.01,
) -> EntradaEconomicaMotorCanonico:
    if type(estado) is not EstadoEconomicoCanonico:
        raise EntradaEconomicaMotorCanonicoInvalida(
            "Novo motor aceita exclusivamente EstadoEconomicoCanonico; "
            f"recebido={type(estado).__name__}."
        )
    if type(fundacao) is not FundacaoEntradaBloco2:
        raise EntradaEconomicaMotorCanonicoInvalida(
            "Novo motor exige FundacaoEntradaBloco2 aprovada; "
            f"recebido={type(fundacao).__name__}."
        )

    exigir_fundacao_entrada_bloco2_valida(fundacao)
    exigir_estado_economico_canonico_valido(estado)

    bloqueios: list[str] = []
    if estado.data_referencia != fundacao.data_referencia:
        bloqueios.append(
            "data_referencia_divergente_entre_fundacao_e_estado:"
            f"{fundacao.data_referencia.isoformat()}:"
            f"{estado.data_referencia.isoformat()}"
        )

    fontes_disponiveis: list[UnidadeEconomicaEntradaMotor] = []
    unidades_bloqueadas: list[UnidadeEconomicaEntradaMotor] = []
    unidades_encerradas: list[UnidadeEconomicaEntradaMotor] = []
    ids: list[str] = []

    for unidade in estado.unidades:
        snapshot = _snapshot_unidade(unidade)
        ids.append(snapshot.unidade_id)
        if unidade.disponivel_pagamento_na_referencia:
            if snapshot.valor_liquido_atual <= tolerancia_monetaria:
                bloqueios.append(
                    f"fonte_disponivel_sem_saldo_positivo:{snapshot.unidade_id}"
                )
            fontes_disponiveis.append(snapshot)
        elif snapshot.estado_ciclo in _ESTADOS_ENCERRADOS_MOTOR:
            if abs(snapshot.valor_liquido_atual) > tolerancia_monetaria:
                bloqueios.append(
                    f"unidade_encerrada_com_saldo:{snapshot.unidade_id}:"
                    f"{snapshot.valor_liquido_atual:.2f}"
                )
            unidades_encerradas.append(snapshot)
        else:
            unidades_bloqueadas.append(snapshot)

    if len(ids) != len(set(ids)):
        bloqueios.append("identidade_economica_duplicada_na_entrada_motor")

    total_particionado = (
        len(fontes_disponiveis)
        + len(unidades_bloqueadas)
        + len(unidades_encerradas)
    )
    if total_particionado != len(estado.unidades):
        bloqueios.append("particao_unidades_incompleta")

    valor_disponivel = round(
        sum(item.valor_liquido_atual for item in fontes_disponiveis),
        10,
    )
    valor_estado = round(
        float(
            estado.auditoria.resumo.get(
                "valor_total_disponivel_canonico",
                0.0,
            )
        ),
        10,
    )
    if abs(valor_disponivel - valor_estado) > tolerancia_monetaria:
        bloqueios.append(
            "valor_disponivel_interface_divergente_estado:"
            f"{valor_disponivel:.2f}:{valor_estado:.2f}"
        )

    auditoria = AuditoriaEntradaEconomicaMotorCanonico(
        ok=not bloqueios,
        bloqueios=tuple(bloqueios),
        resumo={
            "qtd_unidades_estado": len(estado.unidades),
            "qtd_fontes_disponiveis": len(fontes_disponiveis),
            "qtd_unidades_bloqueadas": len(unidades_bloqueadas),
            "qtd_unidades_encerradas": len(unidades_encerradas),
            "valor_total_disponivel": valor_disponivel,
            "valor_total_disponivel_estado": valor_estado,
            "qtd_eventos_conservacao": len(estado.eventos_conservacao),
        },
    )
    if not auditoria.ok:
        raise EntradaEconomicaMotorCanonicoInvalida(
            "EntradaEconomicaMotorCanonico reprovada: "
            + "; ".join(auditoria.bloqueios[:10])
        )

    return EntradaEconomicaMotorCanonico(
        data_referencia=estado.data_referencia,
        fontes_disponiveis=tuple(
            sorted(fontes_disponiveis, key=lambda item: item.unidade_id)
        ),
        unidades_bloqueadas=tuple(
            sorted(unidades_bloqueadas, key=lambda item: item.unidade_id)
        ),
        unidades_encerradas=tuple(
            sorted(unidades_encerradas, key=lambda item: item.unidade_id)
        ),
        eventos_conservacao_ids=tuple(
            sorted(evento.evento_id for evento in estado.eventos_conservacao)
        ),
        auditoria=auditoria,
        metadados={
            "origem_formal_exclusiva": "EstadoEconomicoCanonico",
            "fundacao_entrada": "FundacaoEntradaBloco2",
            "estado_economico_sha256": _hash_estado(estado),
            "cache_json_sha256_semantico": (
                fundacao.proveniencia_cache_json.sha256_semantico
            ),
            "aceita_contexto_operacional_canonico": False,
            "aceita_estado_temporal_inicial": False,
            "aceita_listas_ou_mapas_legados": False,
            "gera_pacotes": False,
            "executa_argmax": False,
            "altera_ledger": False,
            "altera_console": False,
            "altera_xlsx": False,
        },
    )


def exigir_entrada_economica_motor_canonico(
    entrada: EntradaEconomicaMotorCanonico,
) -> None:
    if type(entrada) is not EntradaEconomicaMotorCanonico:
        raise EntradaEconomicaMotorCanonicoInvalida(
            "Novo motor aceita exclusivamente EntradaEconomicaMotorCanonico; "
            f"recebido={type(entrada).__name__}."
        )
    if not entrada.auditoria.ok:
        raise EntradaEconomicaMotorCanonicoInvalida(
            "EntradaEconomicaMotorCanonico possui bloqueios."
        )


__all__ = [
    "AuditoriaEntradaEconomicaMotorCanonico",
    "EntradaEconomicaMotorCanonico",
    "EntradaEconomicaMotorCanonicoInvalida",
    "UnidadeEconomicaEntradaMotor",
    "construir_entrada_economica_motor_canonico",
    "exigir_entrada_economica_motor_canonico",
]
