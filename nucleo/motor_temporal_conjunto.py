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
class AuditoriaIntegridadeResultadoMotorTemporalConjunto:
    ok: bool
    bloqueios: list[str]
    avisos: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class ObrigacoesTemporaisDia:
    data: date
    indices_pagamentos: list[int]
    pagamentos_referenciados: list[dict[str, Any]]


@dataclass(slots=True)
class RecebidosTemporaisDia:
    data: date
    indices_recebidos: list[int]
    recebidos_referenciados: list[dict[str, Any]]


@dataclass(slots=True)
class FontesTemporaisReferenciadasDia:
    data: date
    fontes_referenciadas: list[dict[str, Any]]
    possui_campo_temporal_explicito: bool
    aviso_estrutural: str | None = None


@dataclass(slots=True)
class SwitchingsRealizadosDia:
    data: date
    indices_switchings: list[int]
    switchings_referenciados: list[dict[str, Any]]


@dataclass(slots=True)
class CoberturaEstruturalReferencialDia:
    data: date
    status: str
    possui_obrigacao: bool
    possui_recebidos_referenciados: bool
    possui_fonte_referenciada: bool


@dataclass(slots=True)
class BloqueioEstruturalEtapa5:
    data: date
    codigo: str
    detalhe: str


@dataclass(slots=True)
class EstadoDiarioMotorTemporal:
    data: date
    obrigacoes: ObrigacoesTemporaisDia
    recebidos: RecebidosTemporaisDia
    fontes_referenciadas: FontesTemporaisReferenciadasDia
    switchings_realizados: SwitchingsRealizadosDia
    cobertura_estrutural: CoberturaEstruturalReferencialDia


@dataclass(slots=True)
class DiaMotorTemporal:
    data: date
    possui_eventos_indexados: bool


@dataclass(slots=True)
class AuditoriaMotorTemporalConjunto:
    ok: bool
    avisos: list[str]
    resumo: dict[str, Any]


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
    auditoria_integridade_resultado: AuditoriaIntegridadeResultadoMotorTemporalConjunto | None = None
    dias_motor: list[DiaMotorTemporal] | None = None
    estado_diario_motor: dict[date, EstadoDiarioMotorTemporal] | None = None
    obrigacoes_por_data: dict[date, ObrigacoesTemporaisDia] | None = None
    recebidos_por_data: dict[date, RecebidosTemporaisDia] | None = None
    fontes_referenciadas_por_data: dict[date, FontesTemporaisReferenciadasDia] | None = None
    switchings_realizados_por_data: dict[date, SwitchingsRealizadosDia] | None = None
    cobertura_estrutural_por_data: dict[date, CoberturaEstruturalReferencialDia] | None = None
    bloqueios_estruturais: list[BloqueioEstruturalEtapa5] | None = None
    auditoria_motor_temporal_conjunto: AuditoriaMotorTemporalConjunto | None = None


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


def _contar_itens_indexados(indice: dict[date, list[int]]) -> int:
    return sum(len(posicoes) for posicoes in indice.values())


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


def montar_dias_motor_temporal(
    estado: EstadoTemporalInicial,
    horizonte: HorizonteMotorTemporal,
    indice: IndiceTemporalMotor,
) -> list[DiaMotorTemporal]:
    dias: list[DiaMotorTemporal] = []
    datas_com_eventos = set(indice.datas_com_eventos)
    for data_motor in horizonte.datas_temporais:
        dias.append(DiaMotorTemporal(data=data_motor, possui_eventos_indexados=data_motor in datas_com_eventos))
    return dias


def montar_obrigacoes_temporais_dia(
    estado: EstadoTemporalInicial,
    indice: IndiceTemporalMotor,
    data_motor: date,
) -> ObrigacoesTemporaisDia:
    indices = list(indice.pagamentos_por_data.get(data_motor, []))
    pagamentos = [estado.pagamentos_temporais[i] for i in indices]
    return ObrigacoesTemporaisDia(data=data_motor, indices_pagamentos=indices, pagamentos_referenciados=pagamentos)


def montar_recebidos_temporais_dia(
    estado: EstadoTemporalInicial,
    indice: IndiceTemporalMotor,
    data_motor: date,
) -> RecebidosTemporaisDia:
    indices = list(indice.recebidos_por_data.get(data_motor, []))
    recebidos = [estado.recebidos_temporais[i] for i in indices]
    return RecebidosTemporaisDia(data=data_motor, indices_recebidos=indices, recebidos_referenciados=recebidos)


def montar_fontes_temporais_referenciadas_dia(
    estado: EstadoTemporalInicial,
    data_motor: date,
) -> FontesTemporaisReferenciadasDia:
    campos_temporais = ('data', 'data_disponibilidade', 'data_referencia', 'data_inicio', 'data_vencimento')
    fontes = [
        fonte
        for fonte in (estado.fontes_temporais or [])
        if isinstance(fonte, dict) and any(isinstance(fonte.get(campo), date) for campo in campos_temporais)
    ]
    if not fontes:
        return FontesTemporaisReferenciadasDia(
            data=data_motor,
            fontes_referenciadas=[],
            possui_campo_temporal_explicito=False,
            aviso_estrutural='fontes_sem_campo_temporal_explicito_no_estado',
        )
    return FontesTemporaisReferenciadasDia(
        data=data_motor,
        fontes_referenciadas=fontes,
        possui_campo_temporal_explicito=True,
    )


def montar_switchings_realizados_dia(
    estado: EstadoTemporalInicial,
    indice: IndiceTemporalMotor,
    data_motor: date,
) -> SwitchingsRealizadosDia:
    indices = list(indice.switchings_por_data.get(data_motor, []))
    switchings = [estado.switching_temporal_realizado[i] for i in indices]
    return SwitchingsRealizadosDia(data=data_motor, indices_switchings=indices, switchings_referenciados=switchings)


def sintetizar_cobertura_estrutural_referencial_dia(
    obrigacoes: ObrigacoesTemporaisDia,
    fontes_referenciadas: FontesTemporaisReferenciadasDia,
    recebidos: RecebidosTemporaisDia,
) -> CoberturaEstruturalReferencialDia:
    possui_obrigacao = bool(obrigacoes.pagamentos_referenciados)
    possui_fonte = bool(fontes_referenciadas.fontes_referenciadas)
    possui_recebidos = bool(recebidos.recebidos_referenciados)

    if not possui_obrigacao:
        status = 'sem_obrigacao'
    elif not fontes_referenciadas.possui_campo_temporal_explicito:
        status = 'estrutura_insuficiente'
    elif possui_fonte or possui_recebidos:
        status = 'obrigacao_com_fonte_referenciada'
    else:
        status = 'obrigacao_sem_fonte_referenciada'

    return CoberturaEstruturalReferencialDia(
        data=obrigacoes.data,
        status=status,
        possui_obrigacao=possui_obrigacao,
        possui_recebidos_referenciados=possui_recebidos,
        possui_fonte_referenciada=possui_fonte,
    )


def montar_estado_diario_motor_temporal(
    dia: DiaMotorTemporal,
    obrigacoes: ObrigacoesTemporaisDia,
    recebidos: RecebidosTemporaisDia,
    fontes_referenciadas: FontesTemporaisReferenciadasDia,
    switchings_realizados: SwitchingsRealizadosDia,
    cobertura_estrutural: CoberturaEstruturalReferencialDia,
) -> EstadoDiarioMotorTemporal:
    return EstadoDiarioMotorTemporal(
        data=dia.data,
        obrigacoes=obrigacoes,
        recebidos=recebidos,
        fontes_referenciadas=fontes_referenciadas,
        switchings_realizados=switchings_realizados,
        cobertura_estrutural=cobertura_estrutural,
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


def montar_auditoria_motor_temporal_conjunto(
    resultado: ResultadoMotorTemporalConjunto,
) -> AuditoriaMotorTemporalConjunto:
    dias_motor = resultado.dias_motor or []
    estado_diario_motor = resultado.estado_diario_motor or {}
    cobertura_por_data = resultado.cobertura_estrutural_por_data or {}
    obrigacoes_por_data = resultado.obrigacoes_por_data or {}
    fontes_por_data = resultado.fontes_referenciadas_por_data or {}
    bloqueios = resultado.bloqueios_estruturais or []

    avisos: list[str] = []
    datas_horizonte = resultado.horizonte_motor.datas_temporais
    datas_dias_motor = [dia.data for dia in dias_motor]
    if datas_dias_motor != datas_horizonte:
        avisos.append('dias_motor_divergentes_do_horizonte')
    if set(estado_diario_motor) != set(datas_horizonte):
        avisos.append('estado_diario_incompleto_ou_com_datas_extras')

    qtd_cobertura_insuficiente = sum(1 for c in cobertura_por_data.values() if c.status == 'estrutura_insuficiente')
    qtd_obrigacao_sem_fonte = sum(1 for c in cobertura_por_data.values() if c.status == 'obrigacao_sem_fonte_referenciada')

    resumo = {
        'qtd_dias_horizonte': len(datas_horizonte),
        'qtd_dias_motor': len(dias_motor),
        'qtd_estados_diarios': len(estado_diario_motor),
        'qtd_obrigacoes_indexadas': sum(len(o.indices_pagamentos) for o in obrigacoes_por_data.values()),
        'qtd_fontes_referenciadas_dia': sum(1 for f in fontes_por_data.values() if f.fontes_referenciadas),
        'qtd_cobertura_estrutura_insuficiente': qtd_cobertura_insuficiente,
        'qtd_obrigacao_sem_fonte_referenciada': qtd_obrigacao_sem_fonte,
        'qtd_bloqueios_estruturais': len(bloqueios),
    }

    return AuditoriaMotorTemporalConjunto(ok=not avisos, avisos=avisos, resumo=resumo)


def auditar_integridade_resultado_motor_temporal_conjunto(
    resultado: ResultadoMotorTemporalConjunto,
) -> AuditoriaIntegridadeResultadoMotorTemporalConjunto:
    bloqueios: list[str] = []
    avisos: list[str] = []

    status_interface = resultado.status_interface_etapa5
    horizonte = resultado.horizonte_motor
    indice = resultado.indice_temporal_motor
    eventos = resultado.eventos_temporais_base
    auditoria_consumo = resultado.auditoria_consumo_estado_temporal

    if not status_interface.ok:
        bloqueios.append('interface_estado_temporal_inicial_invalida')
    if resultado.data_referencia != horizonte.data_referencia:
        bloqueios.append('data_referencia_divergente_do_horizonte')
    if horizonte.data_inicio > horizonte.data_fim:
        bloqueios.append('horizonte_motor_com_inicio_apos_fim')
    if resultado.janela_temporal_motor != horizonte.datas_temporais:
        bloqueios.append('janela_temporal_divergente_do_horizonte')
    if not horizonte.datas_temporais:
        bloqueios.append('horizonte_motor_sem_datas_temporais')

    datas_fora_horizonte = [
        data_evento
        for data_evento in indice.datas_com_eventos
        if data_evento < horizonte.data_inicio or data_evento > horizonte.data_fim
    ]
    if datas_fora_horizonte:
        bloqueios.append('indice_temporal_com_datas_fora_do_horizonte')

    qtd_pagamentos_indexados = _contar_itens_indexados(indice.pagamentos_por_data)
    qtd_recebidos_indexados = _contar_itens_indexados(indice.recebidos_por_data)
    qtd_switchings_indexados = _contar_itens_indexados(indice.switchings_por_data)

    if qtd_pagamentos_indexados > len(eventos.pagamentos):
        bloqueios.append('indice_pagamentos_maior_que_eventos_base')
    if qtd_recebidos_indexados > len(eventos.recebidos):
        bloqueios.append('indice_recebidos_maior_que_eventos_base')
    if qtd_switchings_indexados > len(eventos.switchings_realizados):
        bloqueios.append('indice_switchings_maior_que_eventos_base')

    if not eventos.pagamentos and not eventos.recebidos and not eventos.switchings_realizados:
        bloqueios.append('eventos_temporais_base_vazios')

    if auditoria_consumo.origem_artefato != 'EstadoTemporalInicial':
        avisos.append('auditoria_consumo_origem_diferente_de_estado_temporal_inicial')
    if 'estado_temporal_inicial_consumido_diretamente' not in auditoria_consumo.observacoes:
        bloqueios.append('auditoria_consumo_sem_confirmacao_consumo_direto')

    resumo = {
        'qtd_datas_horizonte': len(horizonte.datas_temporais),
        'qtd_datas_com_eventos': len(indice.datas_com_eventos),
        'qtd_pagamentos_base': len(eventos.pagamentos),
        'qtd_pagamentos_indexados': qtd_pagamentos_indexados,
        'qtd_recebidos_base': len(eventos.recebidos),
        'qtd_recebidos_indexados': qtd_recebidos_indexados,
        'qtd_switchings_base': len(eventos.switchings_realizados),
        'qtd_switchings_indexados': qtd_switchings_indexados,
        'qtd_campos_interface_presentes': len(status_interface.campos_presentes),
        'qtd_campos_interface_ausentes': len(status_interface.campos_ausentes),
        'qtd_avisos_interface': len(status_interface.avisos),
        'qtd_dias_motor': len(resultado.dias_motor or []),
        'qtd_estados_diarios': len(resultado.estado_diario_motor or {}),
    }

    return AuditoriaIntegridadeResultadoMotorTemporalConjunto(ok=not bloqueios, bloqueios=bloqueios, avisos=avisos, resumo=resumo)


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
    dias_motor = montar_dias_motor_temporal(estado, horizonte, indice)

    obrigacoes_por_data: dict[date, ObrigacoesTemporaisDia] = {}
    recebidos_por_data: dict[date, RecebidosTemporaisDia] = {}
    fontes_referenciadas_por_data: dict[date, FontesTemporaisReferenciadasDia] = {}
    switchings_realizados_por_data: dict[date, SwitchingsRealizadosDia] = {}
    cobertura_por_data: dict[date, CoberturaEstruturalReferencialDia] = {}
    estado_diario_motor: dict[date, EstadoDiarioMotorTemporal] = {}
    bloqueios_estruturais: list[BloqueioEstruturalEtapa5] = []

    for dia in dias_motor:
        obrigacoes = montar_obrigacoes_temporais_dia(estado, indice, dia.data)
        recebidos = montar_recebidos_temporais_dia(estado, indice, dia.data)
        fontes = montar_fontes_temporais_referenciadas_dia(estado, dia.data)
        switchings = montar_switchings_realizados_dia(estado, indice, dia.data)
        cobertura = sintetizar_cobertura_estrutural_referencial_dia(obrigacoes, fontes, recebidos)
        estado_diario = montar_estado_diario_motor_temporal(dia, obrigacoes, recebidos, fontes, switchings, cobertura)

        obrigacoes_por_data[dia.data] = obrigacoes
        recebidos_por_data[dia.data] = recebidos
        fontes_referenciadas_por_data[dia.data] = fontes
        switchings_realizados_por_data[dia.data] = switchings
        cobertura_por_data[dia.data] = cobertura
        estado_diario_motor[dia.data] = estado_diario

        if cobertura.status in {'estrutura_insuficiente', 'obrigacao_sem_fonte_referenciada'}:
            bloqueios_estruturais.append(
                BloqueioEstruturalEtapa5(
                    data=dia.data,
                    codigo=cobertura.status,
                    detalhe='bloqueio_estrutural_referencial_sem_decisao_economica',
                ),
            )

    auditoria = montar_auditoria_consumo_etapa5(estado, status_interface)
    metadados_estado = getattr(estado, 'metadados', {}) or {}

    resultado = ResultadoMotorTemporalConjunto(
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
            'versao_contrato': 'ME-ETAPA5-05',
            'sem_decisao_economica': True,
            'sem_ledger': True,
            'sem_console_xlsx': True,
        },
        dias_motor=dias_motor,
        estado_diario_motor=estado_diario_motor,
        obrigacoes_por_data=obrigacoes_por_data,
        recebidos_por_data=recebidos_por_data,
        fontes_referenciadas_por_data=fontes_referenciadas_por_data,
        switchings_realizados_por_data=switchings_realizados_por_data,
        cobertura_estrutural_por_data=cobertura_por_data,
        bloqueios_estruturais=bloqueios_estruturais,
    )
    resultado.auditoria_motor_temporal_conjunto = montar_auditoria_motor_temporal_conjunto(resultado)
    resultado.auditoria_integridade_resultado = auditar_integridade_resultado_motor_temporal_conjunto(resultado)
    return resultado


__all__ = [
    'AuditoriaConsumoEtapa5',
    'AuditoriaIntegridadeResultadoMotorTemporalConjunto',
    'AuditoriaMotorTemporalConjunto',
    'BloqueioEstruturalEtapa5',
    'CoberturaEstruturalReferencialDia',
    'DiaMotorTemporal',
    'EstadoDiarioMotorTemporal',
    'EstadoSimulacaoMotorTemporal',
    'EventosTemporaisBase',
    'FontesTemporaisReferenciadasDia',
    'HorizonteMotorTemporal',
    'IndiceTemporalMotor',
    'ObrigacoesTemporaisDia',
    'ParametrosEtapa5',
    'RecebidosTemporaisDia',
    'ResultadoMotorTemporalConjunto',
    'StatusInterfaceEtapa5',
    'SwitchingsRealizadosDia',
    'auditar_integridade_resultado_motor_temporal_conjunto',
    'construir_resultado_motor_temporal_conjunto',
    'definir_horizonte_motor_temporal',
    'inicializar_estado_simulacao_motor',
    'montar_auditoria_consumo_etapa5',
    'montar_auditoria_motor_temporal_conjunto',
    'montar_dias_motor_temporal',
    'montar_estado_diario_motor_temporal',
    'montar_eventos_temporais_base',
    'montar_fontes_temporais_referenciadas_dia',
    'montar_indice_temporal_motor',
    'montar_obrigacoes_temporais_dia',
    'montar_recebidos_temporais_dia',
    'montar_switchings_realizados_dia',
    'sintetizar_cobertura_estrutural_referencial_dia',
    'verificar_interface_estado_temporal_inicial',
]
