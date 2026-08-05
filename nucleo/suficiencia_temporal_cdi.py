"""Gate independente de suficiência temporal da série CDI.

O gate não calcula rendimento e não escolhe investimentos. Ele apenas decide
se a série disponível é suficiente para as datas explicitamente requeridas e
classifica lacunas de borda de forma auditável.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Any, Iterable, Mapping


class ClassificacaoSuficienciaCDI(str, Enum):
    SUFICIENTE = "suficiente"
    DIA_SEM_OBSERVACAO = "dia_sem_observacao"
    DEFASAGEM_ADMISSIVEL = "defasagem_admissivel"
    FATOR_REQUERIDO_AUSENTE = "fator_requerido_ausente"


_ORDEM_SEVERIDADE = {
    ClassificacaoSuficienciaCDI.SUFICIENTE: 0,
    ClassificacaoSuficienciaCDI.DIA_SEM_OBSERVACAO: 1,
    ClassificacaoSuficienciaCDI.DEFASAGEM_ADMISSIVEL: 2,
    ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE: 3,
}


@dataclass(frozen=True, slots=True)
class ResultadoSuficienciaTemporalCDI:
    ok: bool
    classificacao_principal: ClassificacaoSuficienciaCDI
    classificacoes: tuple[ClassificacaoSuficienciaCDI, ...]
    bloqueios: tuple[str, ...]
    avisos: tuple[str, ...]
    evidencias: dict[str, Any]

    def como_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["classificacao_principal"] = self.classificacao_principal.value
        dados["classificacoes"] = [item.value for item in self.classificacoes]
        dados["bloqueios"] = list(self.bloqueios)
        dados["avisos"] = list(self.avisos)
        return dados


def _intervalo_datas(inicio: date, fim_exclusivo: date) -> tuple[date, ...]:
    if fim_exclusivo <= inicio:
        return ()
    quantidade = (fim_exclusivo - inicio).days
    return tuple(
        inicio + timedelta(days=deslocamento)
        for deslocamento in range(quantidade)
    )


def _normalizar_serie(
    serie_cdi: Mapping[date, float] | None,
) -> tuple[dict[date, float], tuple[date, ...]]:
    validos: dict[date, float] = {}
    invalidos: list[date] = []
    for data_fator, fator in (serie_cdi or {}).items():
        if not isinstance(data_fator, date):
            continue
        try:
            fator_float = float(fator)
        except Exception:
            invalidos.append(data_fator)
            continue
        if fator_float <= 1.0:
            invalidos.append(data_fator)
            continue
        validos[data_fator] = fator_float
    return dict(sorted(validos.items())), tuple(sorted(set(invalidos)))


def avaliar_suficiencia_temporal_cdi(
    serie_cdi: Mapping[date, float] | None,
    *,
    data_inicial_consulta: date,
    data_final_consulta: date,
    data_referencia: date,
    datas_requeridas: Iterable[date] = (),
    datas_sem_observacao_permitidas: Iterable[date] = (),
    max_defasagem_dias: int = 2,
    max_lacuna_inicial_dias: int = 1,
) -> ResultadoSuficienciaTemporalCDI:
    """Classifica a cobertura da série para a janela e datas requeridas.

    Datas explicitamente requeridas têm precedência: ausência de fator em data
    requerida bloqueia, exceto quando a data consta explicitamente em
    ``datas_sem_observacao_permitidas``.
    """

    if data_final_consulta < data_inicial_consulta:
        raise ValueError("data_final_consulta anterior a data_inicial_consulta")
    if data_referencia < data_inicial_consulta:
        raise ValueError("data_referencia anterior a data_inicial_consulta")
    if max_defasagem_dias < 0 or max_lacuna_inicial_dias < 0:
        raise ValueError("tolerancias temporais devem ser nao negativas")

    serie, fatores_invalidos = _normalizar_serie(serie_cdi)
    limite_final = min(data_final_consulta, data_referencia)
    requeridas = tuple(
        sorted(
            {
                dt
                for dt in datas_requeridas
                if isinstance(dt, date)
                and data_inicial_consulta <= dt <= limite_final
            }
        )
    )
    permitidas = {
        dt
        for dt in datas_sem_observacao_permitidas
        if isinstance(dt, date)
    }

    classificacoes: set[ClassificacaoSuficienciaCDI] = set()
    bloqueios: list[str] = []
    avisos: list[str] = []

    primeira_data: date | None = None
    ultima_data: date | None = None

    if not serie:
        classificacoes.add(ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE)
        bloqueios.append("Serie CDI ausente ou sem fatores validos.")
    else:
        primeira_data = min(serie)
        ultima_data = max(serie)

        requeridas_ausentes = [dt for dt in requeridas if dt not in serie]
        ausentes_permitidas = [dt for dt in requeridas_ausentes if dt in permitidas]
        ausentes_bloqueantes = [dt for dt in requeridas_ausentes if dt not in permitidas]

        if ausentes_permitidas:
            classificacoes.add(ClassificacaoSuficienciaCDI.DIA_SEM_OBSERVACAO)
            avisos.append(
                "Datas requeridas sem observacao, mas explicitamente permitidas: "
                + ", ".join(dt.isoformat() for dt in ausentes_permitidas)
            )

        if ausentes_bloqueantes:
            classificacoes.add(ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE)
            bloqueios.append(
                "Fatores CDI requeridos ausentes: "
                + ", ".join(dt.isoformat() for dt in ausentes_bloqueantes)
            )

        if primeira_data > data_inicial_consulta:
            lacuna_inicial = (primeira_data - data_inicial_consulta).days
            datas_lacuna = _intervalo_datas(data_inicial_consulta, primeira_data)
            requeridas_na_lacuna = [
                dt for dt in datas_lacuna if dt in requeridas and dt not in permitidas
            ]
            if lacuna_inicial <= max_lacuna_inicial_dias and not requeridas_na_lacuna:
                classificacoes.add(ClassificacaoSuficienciaCDI.DIA_SEM_OBSERVACAO)
                avisos.append(
                    "Serie CDI comeca apos a borda inicial normalizada, sem fator "
                    "requerido na lacuna."
                )
            else:
                classificacoes.add(ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE)
                bloqueios.append(
                    "Cobertura inicial CDI insuficiente: primeira observacao em "
                    f"{primeira_data.isoformat()}."
                )

        if ultima_data < limite_final:
            defasagem = (limite_final - ultima_data).days
            requeridas_apos_ultima = [
                dt
                for dt in requeridas
                if ultima_data < dt <= limite_final
                and dt not in permitidas
                and dt not in serie
            ]
            if requeridas_apos_ultima:
                classificacoes.add(ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE)
            elif defasagem <= max_defasagem_dias:
                classificacoes.add(ClassificacaoSuficienciaCDI.DEFASAGEM_ADMISSIVEL)
                avisos.append(
                    "Ultima observacao CDI anterior ao limite final dentro da "
                    f"tolerancia de {max_defasagem_dias} dias."
                )
            else:
                classificacoes.add(ClassificacaoSuficienciaCDI.FATOR_REQUERIDO_AUSENTE)
                bloqueios.append(
                    "Defasagem CDI superior a tolerancia: "
                    f"{defasagem} dias, limite {max_defasagem_dias}."
                )

    if fatores_invalidos:
        avisos.append(
            "Fatores CDI invalidos ignorados: "
            + ", ".join(dt.isoformat() for dt in fatores_invalidos)
        )

    if not classificacoes:
        classificacoes.add(ClassificacaoSuficienciaCDI.SUFICIENTE)

    classificacoes_ordenadas = tuple(
        sorted(classificacoes, key=lambda item: _ORDEM_SEVERIDADE[item])
    )
    principal = max(
        classificacoes_ordenadas,
        key=lambda item: _ORDEM_SEVERIDADE[item],
    )

    evidencias = {
        "data_inicial_consulta": data_inicial_consulta.isoformat(),
        "data_final_consulta": data_final_consulta.isoformat(),
        "data_referencia": data_referencia.isoformat(),
        "limite_final_avaliado": limite_final.isoformat(),
        "primeira_data_serie": primeira_data.isoformat() if primeira_data else None,
        "ultima_data_serie": ultima_data.isoformat() if ultima_data else None,
        "qtd_fatores_validos": len(serie),
        "datas_fator_invalido": [dt.isoformat() for dt in fatores_invalidos],
        "datas_requeridas": [dt.isoformat() for dt in requeridas],
        "datas_sem_observacao_permitidas": [
            dt.isoformat() for dt in sorted(permitidas)
        ],
        "max_defasagem_dias": max_defasagem_dias,
        "max_lacuna_inicial_dias": max_lacuna_inicial_dias,
    }

    return ResultadoSuficienciaTemporalCDI(
        ok=not bloqueios,
        classificacao_principal=principal,
        classificacoes=classificacoes_ordenadas,
        bloqueios=tuple(bloqueios),
        avisos=tuple(avisos),
        evidencias=evidencias,
    )
