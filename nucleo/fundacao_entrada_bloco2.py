"""Fundação de entrada reutilizável do Bloco 2.

Consolida a proveniência portátil do cache JSON e o gate de suficiência
temporal CDI. Não baixa dados, não constrói estado econômico e não altera
decisão.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping

from nucleo.proveniencia_portatil import (
    ProvenienciaArquivoPortatil,
    auditar_json_portatil,
)
from nucleo.suficiencia_temporal_cdi import (
    ResultadoSuficienciaTemporalCDI,
    avaliar_suficiencia_temporal_cdi,
)


@dataclass(frozen=True, slots=True)
class FundacaoEntradaBloco2:
    data_referencia: date
    proveniencia_cache_json: ProvenienciaArquivoPortatil
    suficiencia_temporal_cdi: ResultadoSuficienciaTemporalCDI
    auditoria_cache_cdi: Mapping[str, Any]
    bloqueios: tuple[str, ...]
    avisos: tuple[str, ...]
    metadados: Mapping[str, Any]

    @property
    def ok(self) -> bool:
        return not self.bloqueios

    def como_dict(self) -> dict[str, Any]:
        return {
            "artefato": "FundacaoEntradaBloco2",
            "bloco": "BLOCO-2-FUNDACAO",
            "ok": self.ok,
            "bloqueios": list(self.bloqueios),
            "avisos": list(self.avisos),
            "data_referencia": self.data_referencia.isoformat(),
            "proveniencia_cache_json": self.proveniencia_cache_json.como_dict(),
            "suficiencia_temporal_cdi": self.suficiencia_temporal_cdi.como_dict(),
            "auditoria_cache_cdi": dict(self.auditoria_cache_cdi),
            "limites_preservados": dict(self.metadados),
        }


class FundacaoEntradaBloco2Invalida(RuntimeError):
    pass


def construir_fundacao_entrada_bloco2_do_cache(
    cache_cdi: Any,
    *,
    data_referencia: date,
    raiz_repositorio: Path,
    datas_requeridas: Iterable[date] = (),
    datas_sem_observacao_permitidas: Iterable[date] = (),
    max_defasagem_dias: int = 2,
    max_lacuna_inicial_dias: int = 1,
) -> FundacaoEntradaBloco2:
    if cache_cdi is None:
        raise FundacaoEntradaBloco2Invalida(
            "PacoteCacheCDIDiario ausente na fundacao do Bloco 2."
        )
    if not isinstance(data_referencia, date):
        raise FundacaoEntradaBloco2Invalida(
            "Data de referencia invalida na fundacao do Bloco 2."
        )

    caminho_cache = getattr(cache_cdi, "caminho_cache", None)
    if caminho_cache is None:
        raise FundacaoEntradaBloco2Invalida(
            "PacoteCacheCDIDiario sem caminho_cache."
        )

    data_inicial = getattr(cache_cdi, "data_inicial_consulta", None)
    data_final = getattr(cache_cdi, "data_final_consulta", None)
    if not isinstance(data_inicial, date) or not isinstance(data_final, date):
        raise FundacaoEntradaBloco2Invalida(
            "PacoteCacheCDIDiario sem janela temporal valida."
        )

    proveniencia = auditar_json_portatil(
        Path(caminho_cache),
        raiz_repositorio=Path(raiz_repositorio),
    )
    suficiencia = avaliar_suficiencia_temporal_cdi(
        getattr(cache_cdi, "serie_cdi", None),
        data_inicial_consulta=data_inicial,
        data_final_consulta=data_final,
        data_referencia=data_referencia,
        datas_requeridas=datas_requeridas,
        datas_sem_observacao_permitidas=datas_sem_observacao_permitidas,
        max_defasagem_dias=max_defasagem_dias,
        max_lacuna_inicial_dias=max_lacuna_inicial_dias,
    )

    bloqueios: list[str] = []
    if not proveniencia.ok:
        bloqueios.append("proveniencia_semantica_cache_json_invalida")
    if proveniencia.status_git:
        bloqueios.append("cache_json_com_alteracoes_locais_nao_versionadas")
    if not proveniencia.git_blob_sha:
        bloqueios.append("git_blob_sha_cache_json_nao_resolvido")
    if not suficiencia.ok:
        bloqueios.extend(suficiencia.bloqueios)

    return FundacaoEntradaBloco2(
        data_referencia=data_referencia,
        proveniencia_cache_json=proveniencia,
        suficiencia_temporal_cdi=suficiencia,
        auditoria_cache_cdi=dict(getattr(cache_cdi, "auditoria", {}) or {}),
        bloqueios=tuple(bloqueios),
        avisos=tuple(suficiencia.avisos),
        metadados={
            "conecta_estado_ao_motor": False,
            "gera_pacotes": False,
            "executa_argmax": False,
            "altera_ledger": False,
            "altera_console_operacional": False,
            "altera_xlsx": False,
        },
    )


def construir_fundacao_entrada_bloco2(
    contexto_operacional: Any,
    *,
    raiz_repositorio: Path,
    datas_requeridas: Iterable[date] = (),
    datas_sem_observacao_permitidas: Iterable[date] = (),
    max_defasagem_dias: int = 2,
    max_lacuna_inicial_dias: int = 1,
) -> FundacaoEntradaBloco2:
    if contexto_operacional is None:
        raise FundacaoEntradaBloco2Invalida(
            "ContextoOperacionalCanonico ausente na fundacao do Bloco 2."
        )

    execucao = getattr(contexto_operacional, "execucao", None)
    data_referencia = getattr(execucao, "data_referencia", None)
    return construir_fundacao_entrada_bloco2_do_cache(
        getattr(contexto_operacional, "cache_cdi", None),
        data_referencia=data_referencia,
        raiz_repositorio=raiz_repositorio,
        datas_requeridas=datas_requeridas,
        datas_sem_observacao_permitidas=datas_sem_observacao_permitidas,
        max_defasagem_dias=max_defasagem_dias,
        max_lacuna_inicial_dias=max_lacuna_inicial_dias,
    )


def exigir_fundacao_entrada_bloco2_valida(
    fundacao: FundacaoEntradaBloco2,
) -> None:
    if type(fundacao) is not FundacaoEntradaBloco2:
        raise FundacaoEntradaBloco2Invalida(
            "Fundacao do Bloco 2 exige FundacaoEntradaBloco2."
        )
    if fundacao.ok:
        return
    raise FundacaoEntradaBloco2Invalida(
        "FundacaoEntradaBloco2 reprovada: " + "; ".join(fundacao.bloqueios[:10])
    )


__all__ = [
    "FundacaoEntradaBloco2",
    "FundacaoEntradaBloco2Invalida",
    "construir_fundacao_entrada_bloco2",
    "construir_fundacao_entrada_bloco2_do_cache",
    "exigir_fundacao_entrada_bloco2_valida",
]
