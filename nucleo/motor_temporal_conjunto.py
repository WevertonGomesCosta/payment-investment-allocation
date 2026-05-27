from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from nucleo.estado_temporal_inicial import EstadoTemporalInicial


@dataclass(slots=True)
class ParametrosEtapa5:
    data_referencia: date | None = None
    data_inicio: date | None = None
    data_fim: date | None = None


@dataclass(slots=True)
class StatusInterfaceEtapa5:
    ok: bool
    campos_presentes: list[str]
    campos_ausentes: list[str]
    avisos: list[str]


@dataclass(slots=True)
class HorizonteMotorTemporal:
    data_referencia: date
    data_inicio: date
    data_fim: date
    datas_temporais: list[date]


@dataclass(slots=True)
class IndiceTemporalMotor:
    pagamentos_por_data: dict[date, list[int]]
    recebidos_por_data: dict[date, list[int]]
    switchings_por_data: dict[date, list[int]]
    datas_com_eventos: list[date]


@dataclass(slots=True)
class EstadoSimulacaoMotorTemporal:
    data_referencia: date
    qtd_inventario_temporal: int
    qtd_fontes_temporais: int
    qtd_pagamentos_temporais: int
    qtd_recebidos_temporais: int
    qtd_switchings_realizados: int
    status: str


@dataclass(slots=True)
class EventosTemporaisBase:
    pagamentos: list[dict[str, Any]]
    recebidos: list[dict[str, Any]]
    switchings_realizados: list[dict[str, Any]]


@dataclass(slots=True)
class AuditoriaConsumoEtapa5:
    origem_artefato: str
    campos_consumidos: list[str]
    status_interface: StatusInterfaceEtapa5
    observacoes: list[str]


@dataclass(slots=True)
class ResultadoMotorTemporalConjunto:
    data_referencia: date
    horizonte_motor: HorizonteMotorTemporal
    estado_temporal_inicial_id: str | None
    janela_temporal_motor: list[date]
    indice_temporal_motor: IndiceTemporalMotor
    estado_simulacao_inicial: EstadoSimulacaoMotorTemporal
    eventos_temporais_base: EventosTemporaisBase
    status_interface_etapa5: StatusInterfaceEtapa5
    auditoria_consumo_estado_temporal: AuditoriaConsumoEtapa5
    metadados: dict[str, Any]


_CAMPOS_OBRIGATORIOS_ESTADO = [
    'data_referencia',
    'pagamentos_temporais',
    'recebidos_temporais',
    'fontes_temporais',
    'inventario_temporal',
    'switching_temporal_realizado',
    'restricoes_temporais',
    'elegibilidades_preliminares',
    'auditoria_temporal',
    'metadados',
]


def _data_evento(registro: dict[str, Any], *campos: str) -> date | None:
    for campo in campos:
        valor = registro.get(campo)
        if isinstance(valor, date):
            return valor
    return None


def _adicionar_indice_por_data(indice: dict[date, list[int]], data_evento: date | None, posicao: int) -> None:
    if data_evento is None:
        return
    indice.setdefault(data_evento, []).append(posicao)


def verificar_interface_estado_temporal_inicial(estado: EstadoTemporalInicial) -> StatusInterfaceEtapa5:
    campos_presentes: list[str] = []
    campos_ausentes: list[str] = []
    avisos: list[str] = []

    for campo in _CAMPOS_OBRIGATORIOS_ESTADO:
        if hasattr(estado, campo):
            campos_presentes.append(campo)
        else:
            campos_ausentes.append(campo)

    metadados = getattr(estado, 'metadados', {}) or {}
    if metadados.get('artefato') != 'EstadoTemporalInicial':
        avisos.append('metadados_sem_artefato_estado_temporal_inicial')

    return StatusInterfaceEtapa5(
        ok=not campos_ausentes,
        campos_presentes=campos_presentes,
        campos_ausentes=campos_ausentes,
        avisos=avisos,
    )


def definir_horizonte_motor_temporal(
    estado: EstadoTemporalInicial,
    parametros: ParametrosEtapa5,
) -> HorizonteMotorTemporal:
    data_referencia = parametros.data_referencia or estado.data_referencia
    datas: set[date] = {data_referencia}

    for pagamento in estado.pagamentos_temporais or []:
        data_pg = _data_evento(pagamento, 'data', 'data_pagamento', 'data_vencimento')
        if data_pg is not None:
            datas.add(data_pg)

    for recebido in estado.recebidos_temporais or []:
        data_rec = _data_evento(recebido, 'data_recebimento', 'data')
        if data_rec is not None:
            datas.add(data_rec)

    for switching in estado.switching_temporal_realizado or []:
        data_sw = _data_evento(switching, 'data_switching', 'data_aplicacao')
        if data_sw is not None:
            datas.add(data_sw)

    data_inicio = parametros.data_inicio or min(datas)
    data_fim = parametros.data_fim or max(datas)
    datas_temporais = sorted(data for data in datas if data_inicio <= data <= data_fim)

    return HorizonteMotorTemporal(
        data_referencia=data_referencia,
        data_inicio=data_inicio,
        data_fim=data_fim,
        datas_temporais=datas_temporais,
    )


def montar_indice_temporal_motor(
    estado: EstadoTemporalInicial,
    horizonte: HorizonteMotorTemporal,
) -> IndiceTemporalMotor:
    pagamentos_por_data: dict[date, list[int]] = {}
    recebidos_por_data: dict[date, list[int]] = {}
    switchings_por_data: dict[date, list[int]] = {}

    for i, pagamento in enumerate(estado.pagamentos_temporais or []):
        data_pg = _data_evento(pagamento, 'data', 'data_pagamento', 'data_vencimento')
        if data_pg is not None and horizonte.data_inicio <= data_pg <= horizonte.data_fim:
            _adicionar_indice_por_data(pagamentos_por_data, data_pg, i)

    for i, recebido in enumerate(estado.recebidos_temporais or []):
        data_rec = _data_evento(recebido, 'data_recebimento', 'data')
        if data_rec is not None and horizonte.data_inicio <= data_rec <= horizonte.data_fim:
            _adicionar_indice_por_data(recebidos_por_data, data_rec, i)

    for i, switching in enumerate(estado.switching_temporal_realizado or []):
        data_sw = _data_evento(switching, 'data_switching', 'data_aplicacao')
        if data_sw is not None and horizonte.data_inicio <= data_sw <= horizonte.data_fim:
            _adicionar_indice_por_data(switchings_por_data, data_sw, i)

    datas_com_eventos = sorted(set(pagamentos_por_data) | set(recebidos_por_data) | set(switchings_por_data))

    return IndiceTemporalMotor(
        pagamentos_por_data=pagamentos_por_data,
        recebidos_por_data=recebidos_por_data,
        switchings_por_data=switchings_por_data,
        datas_com_eventos=datas_com_eventos,
    )


def inicializar_estado_simulacao_motor(
    estado: EstadoTemporalInicial,
    indice: IndiceTemporalMotor,
) -> EstadoSimulacaoMotorTemporal:
    return EstadoSimulacaoMotorTemporal(
        data_referencia=estado.data_referencia,
        qtd_inventario_temporal=len(estado.inventario_temporal or []),
        qtd_fontes_temporais=len(estado.fontes_temporais or []),
        qtd_pagamentos_temporais=len(estado.pagamentos_temporais or []),
        qtd_recebidos_temporais=len(estado.recebidos_temporais or []),
        qtd_switchings_realizados=len(estado.switching_temporal_realizado or []),
        status='inicializado_sem_decisao_economica',
    )


def montar_eventos_temporais_base(
    estado: EstadoTemporalInicial,
    indice: IndiceTemporalMotor,
) -> EventosTemporaisBase:
    return EventosTemporaisBase(
        pagamentos=list(estado.pagamentos_temporais or []),
        recebidos=list(estado.recebidos_temporais or []),
        switchings_realizados=list(estado.switching_temporal_realizado or []),
    )


def montar_auditoria_consumo_etapa5(
    estado: EstadoTemporalInicial,
    status_interface: StatusInterfaceEtapa5,
) -> AuditoriaConsumoEtapa5:
    metadados = getattr(estado, 'metadados', {}) or {}
    origem = str(metadados.get('artefato') or 'EstadoTemporalInicial')
    observacoes = [
        'estado_temporal_inicial_consumido_diretamente',
        'sem_reconstrucao_de_estado',
        'sem_decisao_economica',
        'sem_ledger',
        'sem_console_xlsx',
    ]
    return AuditoriaConsumoEtapa5(
        origem_artefato=origem,
        campos_consumidos=list(_CAMPOS_OBRIGATORIOS_ESTADO),
        status_interface=status_interface,
        observacoes=observacoes,
    )


def construir_resultado_motor_temporal_conjunto(
    estado: EstadoTemporalInicial,
    parametros: ParametrosEtapa5 | None = None,
) -> ResultadoMotorTemporalConjunto:
    parametros = parametros or ParametrosEtapa5()
    status_interface = verificar_interface_estado_temporal_inicial(estado)
    horizonte = definir_horizonte_motor_temporal(estado, parametros)
    indice = montar_indice_temporal_motor(estado, horizonte)
    estado_simulacao = inicializar_estado_simulacao_motor(estado, indice)
    eventos_base = montar_eventos_temporais_base(estado, indice)
    auditoria = montar_auditoria_consumo_etapa5(estado, status_interface)
    metadados_estado = getattr(estado, 'metadados', {}) or {}

    return ResultadoMotorTemporalConjunto(
        data_referencia=horizonte.data_referencia,
        horizonte_motor=horizonte,
        estado_temporal_inicial_id=metadados_estado.get('id'),
        janela_temporal_motor=horizonte.datas_temporais,
        indice_temporal_motor=indice,
        estado_simulacao_inicial=estado_simulacao,
        eventos_temporais_base=eventos_base,
        status_interface_etapa5=status_interface,
        auditoria_consumo_estado_temporal=auditoria,
        metadados={
            'etapa': '5',
            'artefato': 'ResultadoMotorTemporalConjunto',
            'versao_contrato': 'ME-ETAPA5-02',
            'sem_decisao_economica': True,
            'sem_ledger': True,
            'sem_console_xlsx': True,
        },
    )


__all__ = [
    'AuditoriaConsumoEtapa5',
    'EstadoSimulacaoMotorTemporal',
    'EventosTemporaisBase',
    'HorizonteMotorTemporal',
    'IndiceTemporalMotor',
    'ParametrosEtapa5',
    'ResultadoMotorTemporalConjunto',
    'StatusInterfaceEtapa5',
    'construir_resultado_motor_temporal_conjunto',
    'definir_horizonte_motor_temporal',
    'inicializar_estado_simulacao_motor',
    'montar_auditoria_consumo_etapa5',
    'montar_eventos_temporais_base',
    'montar_indice_temporal_motor',
    'verificar_interface_estado_temporal_inicial',
]
