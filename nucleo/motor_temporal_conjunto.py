from __future__ import annotations

from dataclasses import dataclass, field
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
class FonteCandidataPacoteTemporal:
    fonte_id: str | None
    tipo_fonte: str | None
    origem_fonte: str | None
    referencia_estado_temporal: dict[str, Any]


@dataclass(slots=True)
class SwitchingCandidatoPacoteTemporal:
    switching_id: str | None
    lote_origem_id: str | None
    lote_destino_id: str | None
    tipo_switching: str
    referencia_estado_temporal: dict[str, Any]


@dataclass(slots=True)
class TransicaoCandidataPacoteTemporal:
    tipo_transicao: str
    status_transicao: str
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PacoteTemporalCandidato:
    pacote_id: str
    data_referencia: date
    tipo_pacote: str
    obrigacoes_referenciadas: list[dict[str, Any]]
    fontes_candidatas: list[FonteCandidataPacoteTemporal]
    switchings_candidatos: list[SwitchingCandidatoPacoteTemporal]
    transicoes_candidatas: list[TransicaoCandidataPacoteTemporal]
    status_factibilidade: str
    motivos_bloqueio: list[str]
    valor_obrigacoes: float | None = None
    valor_cobertura_referencial: float | None = None
    metadados_auditoria: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SchemaPacoteTemporalCandidato:
    nome: str
    versao: str
    tipos_pacote_previstos: list[str]
    status_factibilidade_previstos: list[str]
    campos_obrigatorios: list[str]
    campos_proibidos_decisao: list[str]


@dataclass(slots=True)
class AuditoriaSchemaPacoteTemporalCandidato:
    ok: bool
    avisos: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class ValoracaoPacoteTemporal:
    valor_obrigacoes: float
    valor_cobertura_referencial: float
    valor_descoberto_referencial: float
    cobertura_integral_referencial: bool
    penalidade_bloqueio: float
    penalidade_status: float
    penalidade_switching: float
    score_referencial: float


@dataclass(slots=True)
class PacoteTemporalValorado:
    pacote_candidato: PacoteTemporalCandidato
    valoracao: ValoracaoPacoteTemporal
    valido_no_schema: bool


@dataclass(slots=True)
class JustificativaDecisaoTemporal:
    criterio_principal: str
    criterios_desempate_aplicados: list[str]
    resumo: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PacoteTemporalDescartado:
    pacote_id: str
    tipo_pacote: str
    motivos_descarte: list[str]
    score_referencial: float


@dataclass(slots=True)
class DecisaoTemporalDia:
    data_referencia: date
    pacote_vencedor_id: str | None
    status_decisao: str
    justificativa: JustificativaDecisaoTemporal
    executa_pagamento: bool = False
    executa_switching: bool = False
    gera_ledger: bool = False


@dataclass(slots=True)
class AuditoriaDecisaoTemporalConjunto:
    ok: bool
    avisos: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class EventoTrajetoriaTemporalInterna:
    data: date
    tipo_evento_interno: str
    pacote_id: str | None
    tipo_pacote: str | None
    status_referencial: str
    detalhes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FonteReservadaTemporalmente:
    data: date
    fonte_id: str
    pacote_id: str
    tipo_fonte: str | None
    origem_fonte: str | None
    valor_reservado_referencial: float
    valor_disponivel_antes_referencial: float
    valor_disponivel_depois_referencial: float
    obrigacao_id: str | None = None
    referencia_estado_temporal: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ObrigacaoCobertaTemporalmente:
    data: date
    obrigacao_id: str | None
    pacote_id: str
    valor_obrigacao_referencial: float
    valor_coberto_referencial: float
    fontes_reservadas_ids: list[str]
    referencia_obrigacao_temporal: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ObrigacaoBloqueadaTemporalmente:
    data: date
    obrigacao_id: str | None
    pacote_id: str | None
    motivo_bloqueio_referencial: str
    valor_obrigacao_referencial: float
    valor_cobertura_referencial: float
    referencia_obrigacao_temporal: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SwitchingEscolhidoTemporalmente:
    data: date
    switching_id: str | None
    pacote_id: str
    lote_origem_id: str | None
    lote_destino_id: str | None
    tipo_switching: str
    status_referencial: str
    referencia_estado_temporal: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SaldoReferencialFonteTemporal:
    data: date
    fonte_id: str
    valor_disponivel_referencial: float
    valor_reservado_acumulado_referencial: float


@dataclass(slots=True)
class EstadoTemporalInternoDia:
    data: date
    pacote_id: str | None
    tipo_pacote: str | None
    status_referencial: str
    eventos_internos: list[EventoTrajetoriaTemporalInterna] = field(default_factory=list)
    saldos_fontes_referenciais: list[SaldoReferencialFonteTemporal] = field(default_factory=list)
    fontes_reservadas: list[FonteReservadaTemporalmente] = field(default_factory=list)
    obrigacoes_cobertas: list[ObrigacaoCobertaTemporalmente] = field(default_factory=list)
    obrigacoes_bloqueadas: list[ObrigacaoBloqueadaTemporalmente] = field(default_factory=list)
    switchings_escolhidos: list[SwitchingEscolhidoTemporalmente] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TrajetoriaTemporalInternaEscolhida:
    estado_temporal_interno_por_data: dict[date, EstadoTemporalInternoDia]
    eventos_trajetoria_temporal: list[EventoTrajetoriaTemporalInterna]
    fontes_reservadas_temporalmente: list[FonteReservadaTemporalmente]
    obrigacoes_cobertas_temporalmente: list[ObrigacaoCobertaTemporalmente]
    obrigacoes_bloqueadas_temporalmente: list[ObrigacaoBloqueadaTemporalmente]
    switchings_escolhidos_temporalmente: list[SwitchingEscolhidoTemporalmente]
    saldos_referenciais_fontes_temporais: dict[date, list[SaldoReferencialFonteTemporal]]


@dataclass(slots=True)
class AuditoriaTrajetoriaTemporalInterna:
    ok: bool
    avisos: list[str]
    bloqueios: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class SumarioFinalEtapa5:
    qtd_datas_horizonte: int
    qtd_dias_motor: int
    qtd_pacotes_candidatos: int
    qtd_pacotes_valorados: int
    qtd_decisoes_temporais: int
    qtd_pacotes_vencedores: int
    qtd_eventos_trajetoria: int
    qtd_obrigacoes_cobertas: int
    qtd_obrigacoes_bloqueadas: int
    qtd_fontes_reservadas: int
    qtd_switchings_escolhidos: int
    qtd_bloqueios_estruturais: int
    qtd_bloqueios_trajetoria: int
    qtd_avisos_relevantes: int


@dataclass(slots=True)
class BloqueioFinalEtapa5:
    codigo: str
    detalhe: str
    data: date | None = None
    severidade: str = 'bloqueio'


@dataclass(slots=True)
class AuditoriaFinalResultadoMotorTemporalConjunto:
    ok: bool
    pronto_para_etapa6: bool
    bloqueios: list[BloqueioFinalEtapa5]
    avisos: list[str]
    resumo: dict[str, Any]


@dataclass(slots=True)
class FechamentoFuncionalEtapa5:
    etapa5_fechada_funcionalmente: bool
    pronto_para_etapa6: bool
    criterios_fechamento: list[str]
    criterios_atendidos: list[str]
    criterios_bloqueados: list[str]
    limites_preservados: list[str]


@dataclass(slots=True)
class ContratoConsumoEtapa6:
    artefato_exclusivo_consumo: str
    blocos_consumo: list[str]
    fontes_proibidas: list[str]
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
    schema_pacote_temporal_candidato: SchemaPacoteTemporalCandidato | None = None
    pacotes_temporais_candidatos_por_data: dict[date, list[PacoteTemporalCandidato]] | None = None
    auditoria_schema_pacote_temporal_candidato: AuditoriaSchemaPacoteTemporalCandidato | None = None
    pacotes_temporais_valorados_por_data: dict[date, list[PacoteTemporalValorado]] | None = None
    pacote_vencedor_por_data: dict[date, PacoteTemporalCandidato | None] | None = None
    decisoes_temporais_por_data: dict[date, DecisaoTemporalDia] | None = None
    pacotes_descartados_por_data: dict[date, list[PacoteTemporalDescartado]] | None = None
    auditoria_decisao_temporal_conjunto: AuditoriaDecisaoTemporalConjunto | None = None
    trajetoria_temporal_interna_escolhida: TrajetoriaTemporalInternaEscolhida | None = None
    eventos_trajetoria_temporal: list[EventoTrajetoriaTemporalInterna] | None = None
    estado_temporal_interno_por_data: dict[date, EstadoTemporalInternoDia] | None = None
    fontes_reservadas_temporalmente: list[FonteReservadaTemporalmente] | None = None
    obrigacoes_cobertas_temporalmente: list[ObrigacaoCobertaTemporalmente] | None = None
    obrigacoes_bloqueadas_temporalmente: list[ObrigacaoBloqueadaTemporalmente] | None = None
    switchings_escolhidos_temporalmente: list[SwitchingEscolhidoTemporalmente] | None = None
    auditoria_trajetoria_temporal_interna: AuditoriaTrajetoriaTemporalInterna | None = None
    sumario_final_etapa5: SumarioFinalEtapa5 | None = None
    auditoria_final_etapa5: AuditoriaFinalResultadoMotorTemporalConjunto | None = None
    fechamento_funcional_etapa5: FechamentoFuncionalEtapa5 | None = None
    contrato_consumo_etapa6: ContratoConsumoEtapa6 | None = None
    pronto_para_etapa6: bool = False


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
    total_dias = (data_fim - data_inicio).days
    datas_temporais = [date.fromordinal(data_inicio.toordinal() + deslocamento) for deslocamento in range(total_dias + 1)]

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
    indices_brutos = list(indice.pagamentos_por_data.get(data_motor, []))
    indices: list[int] = []
    pagamentos = []
    for i in indices_brutos:
        pagamento = estado.pagamentos_temporais[i]
        if pagamento.get('pago') is True:
            continue
        if pagamento.get('fonte_a_decidir') is False:
            continue
        indices.append(i)
        pagamentos.append(pagamento)
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
    fontes: list[dict[str, Any]] = []
    for fonte in estado.fontes_temporais or []:
        if not isinstance(fonte, dict):
            continue
        datas_fonte = [
            valor
            for campo in campos_temporais
            if isinstance((valor := fonte.get(campo)), date)
        ]
        if not datas_fonte:
            continue
        if data_motor >= min(datas_fonte):
            fontes.append(fonte)
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


def montar_schema_pacote_temporal_candidato() -> SchemaPacoteTemporalCandidato:
    return SchemaPacoteTemporalCandidato(
        nome='PacoteTemporalCandidato',
        versao='ME-ETAPA5-A',
        tipos_pacote_previstos=[
            'sem_obrigacao',
            'sem_cobertura',
            'pagamento_fonte_unica',
            'pagamento_combinacao_fontes',
            'pagamento_com_recebido',
            'switching_integral_simples',
            'switching_integral_agregado',
            'switching_mais_pagamento',
        ],
        status_factibilidade_previstos=[
            'factivel_referencialmente',
            'bloqueado_estruturalmente',
            'sem_obrigacao',
            'nao_avaliado',
        ],
        campos_obrigatorios=[
            'pacote_id',
            'data_referencia',
            'tipo_pacote',
            'obrigacoes_referenciadas',
            'fontes_candidatas',
            'switchings_candidatos',
            'transicoes_candidatas',
            'status_factibilidade',
            'motivos_bloqueio',
            'metadados_auditoria',
        ],
        campos_proibidos_decisao=[
            'fonte_otima_escolhida',
            'lote_escolhido',
            'pagamento_executado',
            'switching_promovido',
            'pacote_vencedor',
            'ledger_evento_id',
            'patrimonio_terminal_otimo',
        ],
    )


def inicializar_pacotes_temporais_candidatos_por_data(
    dias_motor: list[DiaMotorTemporal],
) -> dict[date, list[PacoteTemporalCandidato]]:
    return {dia.data: [] for dia in dias_motor}


def extrair_valor_obrigacao_referencial(obrigacao: dict[str, Any]) -> tuple[float | None, list[str]]:
    avisos: list[str] = []
    for campo in ('valor', 'valor_pagamento', 'valor_obrigacao'):
        valor = obrigacao.get(campo)
        if isinstance(valor, (int, float)):
            return float(valor), avisos
    avisos.append('valor_obrigacao_ausente')
    return None, avisos


def extrair_valor_fonte_referencial(fonte: dict[str, Any]) -> tuple[float | None, list[str]]:
    avisos: list[str] = []
    for campo in ('valor_estimado', 'valor_disponivel', 'saldo_disponivel', 'saldo', 'valor'):
        valor = fonte.get(campo)
        if isinstance(valor, (int, float)):
            return float(valor), avisos
    avisos.append('valor_fonte_ausente')
    return None, avisos


def extrair_valor_recebido_referencial(recebido: dict[str, Any]) -> tuple[float | None, list[str]]:
    avisos: list[str] = []
    for campo in ('valor', 'valor_recebido'):
        valor = recebido.get(campo)
        if isinstance(valor, (int, float)):
            return float(valor), avisos
    avisos.append('valor_recebido_ausente')
    return None, avisos


def extrair_valor_switching_referencial(switching: dict[str, Any]) -> tuple[float | None, list[str]]:
    avisos: list[str] = []
    for campo in ('valor_liquido_migrado', 'valor_migrado', 'valor'):
        valor = switching.get(campo)
        if isinstance(valor, (int, float)):
            return float(valor), avisos
    avisos.append('valor_switching_ausente')
    return None, avisos


def _chave_fonte_temporal_referencial(fonte: dict[str, Any]) -> str | None:
    for campo in ('fonte_id', 'id', 'identificador', 'codigo'):
        valor = fonte.get(campo)
        if valor is not None:
            return str(valor)
    return None


def _data_temporal_referencial_fonte(fonte: dict[str, Any], data_motor: date) -> date | None:
    campos_temporais = ('data', 'data_disponibilidade', 'data_referencia', 'data_inicio', 'data_vencimento')
    datas_ate_data_motor = [
        valor
        for campo in campos_temporais
        if isinstance((valor := fonte.get(campo)), date) and valor <= data_motor
    ]
    return max(datas_ate_data_motor) if datas_ate_data_motor else None


def deduplicar_fontes_temporais_referenciadas(
    fontes: list[dict[str, Any]],
    data_motor: date,
) -> list[dict[str, Any]]:
    fontes_unicas: list[dict[str, Any]] = []
    posicoes_por_chave: dict[str, int] = {}
    datas_por_chave: dict[str, date | None] = {}

    for fonte in fontes:
        chave = _chave_fonte_temporal_referencial(fonte)
        if chave is None:
            fontes_unicas.append(fonte)
            continue

        data_comparavel = _data_temporal_referencial_fonte(fonte, data_motor)
        if chave not in posicoes_por_chave:
            posicoes_por_chave[chave] = len(fontes_unicas)
            datas_por_chave[chave] = data_comparavel
            fontes_unicas.append(fonte)
            continue

        data_atual = datas_por_chave.get(chave)
        substituir = (
            (data_atual is None and data_comparavel is not None)
            or (data_atual is not None and data_comparavel is not None and data_comparavel >= data_atual)
            or (data_atual is None and data_comparavel is None)
        )
        if substituir:
            # Em empate de data, a ocorrência mais recente na lista é o snapshot mais atualizado observado no pipeline.
            fontes_unicas[posicoes_por_chave[chave]] = fonte
            datas_por_chave[chave] = data_comparavel

    return fontes_unicas

def montar_fonte_candidata_pacote_temporal(fonte: dict[str, Any]) -> FonteCandidataPacoteTemporal:
    return FonteCandidataPacoteTemporal(
        fonte_id=str(fonte.get('fonte_id') or fonte.get('id')) if (fonte.get('fonte_id') is not None or fonte.get('id') is not None) else None,
        tipo_fonte=str(fonte.get('tipo_fonte') or fonte.get('tipo')) if (fonte.get('tipo_fonte') is not None or fonte.get('tipo') is not None) else None,
        origem_fonte=str(fonte.get('origem_canonica') or fonte.get('origem')) if (fonte.get('origem_canonica') is not None or fonte.get('origem') is not None) else None,
        referencia_estado_temporal=fonte,
    )


def montar_switching_candidato_pacote_temporal(switching: dict[str, Any]) -> SwitchingCandidatoPacoteTemporal:
    return SwitchingCandidatoPacoteTemporal(
        switching_id=str(switching.get('switching_id') or switching.get('id')) if (switching.get('switching_id') is not None or switching.get('id') is not None) else None,
        lote_origem_id=str(switching.get('lote_origem') or switching.get('lote_origem_id')) if (switching.get('lote_origem') is not None or switching.get('lote_origem_id') is not None) else None,
        lote_destino_id=str(switching.get('lote_destino') or switching.get('lote_destino_id')) if (switching.get('lote_destino') is not None or switching.get('lote_destino_id') is not None) else None,
        tipo_switching='integral',
        referencia_estado_temporal=switching,
    )


def _fonte_disponivel_referencialmente(fonte: dict[str, Any]) -> bool:
    if fonte.get('disponivel_na_referencia') is False:
        return False
    if str(fonte.get('status_temporal') or '').lower() == 'indisponivel':
        return False
    return True


def _recebido_disponivel_referencialmente(recebido: dict[str, Any]) -> bool:
    if recebido.get('disponivel_na_referencia') is False:
        return False
    if recebido.get('aplicado') is True:
        return False
    if recebido.get('vinculado') is True:
        return False
    if recebido.get('futuro_indisponivel') is True:
        return False
    return True


def _montar_pacote_base(data_ref: date, tipo_pacote: str, idx: str) -> PacoteTemporalCandidato:
    return PacoteTemporalCandidato(
        pacote_id=f'{data_ref.isoformat()}::{tipo_pacote}::{idx}',
        data_referencia=data_ref,
        tipo_pacote=tipo_pacote,
        obrigacoes_referenciadas=[],
        fontes_candidatas=[],
        switchings_candidatos=[],
        transicoes_candidatas=[],
        status_factibilidade='nao_avaliado',
        motivos_bloqueio=[],
        metadados_auditoria={},
    )


def gerar_pacote_sem_obrigacao(estado_dia: EstadoDiarioMotorTemporal) -> PacoteTemporalCandidato | None:
    if estado_dia.obrigacoes.pagamentos_referenciados:
        return None
    pacote = _montar_pacote_base(estado_dia.data, 'sem_obrigacao', '1')
    pacote.status_factibilidade = 'sem_obrigacao'
    pacote.metadados_auditoria['macroetapa'] = 'MACRO-ETAPA5-A'
    return pacote


def gerar_pacote_sem_cobertura(estado_dia: EstadoDiarioMotorTemporal) -> PacoteTemporalCandidato | None:
    if not estado_dia.obrigacoes.pagamentos_referenciados:
        return None
    fontes_disponiveis = [f for f in estado_dia.fontes_referenciadas.fontes_referenciadas if _fonte_disponivel_referencialmente(f)]
    if fontes_disponiveis or estado_dia.recebidos.recebidos_referenciados or estado_dia.switchings_realizados.switchings_referenciados:
        return None
    pacote = _montar_pacote_base(estado_dia.data, 'sem_cobertura', '1')
    pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
    pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
    pacote.valor_cobertura_referencial = 0.0
    pacote.status_factibilidade = 'bloqueado_estruturalmente'
    pacote.motivos_bloqueio = ['sem_fonte_ou_recebido_ou_switching_referenciavel']
    return pacote


def montar_auditoria_schema_pacote_temporal_candidato(
    resultado: ResultadoMotorTemporalConjunto,
) -> AuditoriaSchemaPacoteTemporalCandidato:
    schema = resultado.schema_pacote_temporal_candidato
    pacotes_por_data = resultado.pacotes_temporais_candidatos_por_data or {}
    horizonte = resultado.horizonte_motor.datas_temporais
    avisos: list[str] = []

    if schema is None:
        avisos.append('schema_pacote_temporal_candidato_ausente')
    if set(pacotes_por_data) != set(horizonte):
        avisos.append('mapa_pacotes_candidatos_nao_cobre_horizonte')

    resumo = {
        'schema_definido': schema is not None,
        'qtd_tipos_pacote_previstos': len(schema.tipos_pacote_previstos) if schema else 0,
        'qtd_status_factibilidade_previstos': len(schema.status_factibilidade_previstos) if schema else 0,
        'qtd_datas_horizonte': len(horizonte),
        'qtd_datas_com_lista_pacotes': len(pacotes_por_data),
        'qtd_pacotes_gerados': sum(len(pacotes) for pacotes in pacotes_por_data.values()),
        'geracao_pacotes_adiada': True,
    }

    return AuditoriaSchemaPacoteTemporalCandidato(ok=not avisos, avisos=avisos, resumo=resumo)


def gerar_pacotes_pagamento_fonte_unica(estado_dia: EstadoDiarioMotorTemporal) -> list[PacoteTemporalCandidato]:
    pacotes: list[PacoteTemporalCandidato] = []
    if not estado_dia.obrigacoes.pagamentos_referenciados:
        return pacotes
    fontes_disponiveis = deduplicar_fontes_temporais_referenciadas(
        [f for f in estado_dia.fontes_referenciadas.fontes_referenciadas if _fonte_disponivel_referencialmente(f)],
        estado_dia.data,
    )
    for idx, fonte in enumerate(fontes_disponiveis, start=1):
        pacote = _montar_pacote_base(estado_dia.data, 'pagamento_fonte_unica', str(idx))
        pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
        fonte_candidata = montar_fonte_candidata_pacote_temporal(fonte)
        pacote.fontes_candidatas = [fonte_candidata]
        pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
        valor_fonte, _ = extrair_valor_fonte_referencial(fonte)
        pacote.valor_cobertura_referencial = valor_fonte
        if valor_fonte is None:
            pacote.status_factibilidade = 'bloqueado_estruturalmente'
            pacote.motivos_bloqueio.append('fonte_sem_valor_referencial')
        elif valor_fonte <= 0.0:
            pacote.status_factibilidade = 'bloqueado_estruturalmente'
            pacote.motivos_bloqueio.append('fonte_sem_cobertura_referencial_positiva')
        elif valor_fonte < (pacote.valor_obrigacoes or 0.0):
            pacote.status_factibilidade = 'bloqueado_estruturalmente'
            pacote.motivos_bloqueio.append('fonte_cobertura_referencial_insuficiente')
        else:
            pacote.status_factibilidade = 'factivel_referencialmente'
        pacotes.append(pacote)
    return pacotes


def gerar_pacote_pagamento_combinacao_fontes(estado_dia: EstadoDiarioMotorTemporal) -> PacoteTemporalCandidato | None:
    fontes_disponiveis = deduplicar_fontes_temporais_referenciadas(
        [f for f in estado_dia.fontes_referenciadas.fontes_referenciadas if _fonte_disponivel_referencialmente(f)],
        estado_dia.data,
    )
    if not estado_dia.obrigacoes.pagamentos_referenciados or len(fontes_disponiveis) < 2:
        return None
    pacote = _montar_pacote_base(estado_dia.data, 'pagamento_combinacao_fontes', '1')
    pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
    pacote.fontes_candidatas = [
        montar_fonte_candidata_pacote_temporal(fonte) for fonte in fontes_disponiveis
    ]
    pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
    pacote.valor_cobertura_referencial = sum(extrair_valor_fonte_referencial(f)[0] or 0.0 for f in fontes_disponiveis)
    if (pacote.valor_cobertura_referencial or 0.0) <= 0.0:
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('combinacao_fontes_sem_cobertura_referencial_positiva')
    elif (pacote.valor_cobertura_referencial or 0.0) < (pacote.valor_obrigacoes or 0.0):
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('combinacao_fontes_cobertura_referencial_insuficiente')
    else:
        pacote.status_factibilidade = 'factivel_referencialmente'
    return pacote


def gerar_pacote_pagamento_com_recebido(estado_dia: EstadoDiarioMotorTemporal) -> PacoteTemporalCandidato | None:
    if not estado_dia.obrigacoes.pagamentos_referenciados or not estado_dia.recebidos.recebidos_referenciados:
        return None
    recebidos_disponiveis = [r for r in estado_dia.recebidos.recebidos_referenciados if _recebido_disponivel_referencialmente(r)]
    pacote = _montar_pacote_base(estado_dia.data, 'pagamento_com_recebido', '1')
    pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
    pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
    pacote.valor_cobertura_referencial = sum(extrair_valor_recebido_referencial(r)[0] or 0.0 for r in recebidos_disponiveis)
    if not recebidos_disponiveis:
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('recebidos_indisponiveis_na_referencia')
    elif (pacote.valor_cobertura_referencial or 0.0) <= 0.0:
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('recebidos_sem_cobertura_referencial_positiva')
    elif (pacote.valor_cobertura_referencial or 0.0) < (pacote.valor_obrigacoes or 0.0):
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('recebidos_cobertura_referencial_insuficiente')
    else:
        pacote.status_factibilidade = 'factivel_referencialmente'
    pacote.metadados_auditoria['recebidos_referenciados'] = [
        {'recebido_id': recebido.get('recebido_id') or recebido.get('id'), 'referencia': recebido}
        for recebido in recebidos_disponiveis
    ]
    return pacote


def gerar_pacotes_switching_integral(estado_dia: EstadoDiarioMotorTemporal) -> list[PacoteTemporalCandidato]:
    switchings = estado_dia.switchings_realizados.switchings_referenciados
    pacotes: list[PacoteTemporalCandidato] = []
    for idx, switching in enumerate(switchings, start=1):
        pacote = _montar_pacote_base(estado_dia.data, 'switching_integral_simples', str(idx))
        pacote.switchings_candidatos = [montar_switching_candidato_pacote_temporal(switching)]
        pacote.status_factibilidade = 'nao_avaliado' if estado_dia.obrigacoes.pagamentos_referenciados else 'factivel_referencialmente'
        pacotes.append(pacote)
    if len(switchings) > 1:
        pacote_agregado = _montar_pacote_base(estado_dia.data, 'switching_integral_agregado', '1')
        pacote_agregado.switchings_candidatos = [montar_switching_candidato_pacote_temporal(s) for s in switchings]
        pacote_agregado.status_factibilidade = 'nao_avaliado' if estado_dia.obrigacoes.pagamentos_referenciados else 'factivel_referencialmente'
        pacotes.append(pacote_agregado)
    return pacotes


def gerar_pacotes_switching_mais_pagamento(estado_dia: EstadoDiarioMotorTemporal) -> list[PacoteTemporalCandidato]:
    if not estado_dia.obrigacoes.pagamentos_referenciados or not estado_dia.switchings_realizados.switchings_referenciados:
        return []
    pacote = _montar_pacote_base(estado_dia.data, 'switching_mais_pagamento', '1')
    pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
    pacote.switchings_candidatos = [
        montar_switching_candidato_pacote_temporal(s) for s in estado_dia.switchings_realizados.switchings_referenciados
    ]
    pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
    valor_switchings = sum(extrair_valor_switching_referencial(s)[0] or 0.0 for s in estado_dia.switchings_realizados.switchings_referenciados)
    pacote.valor_cobertura_referencial = valor_switchings
    if valor_switchings <= 0.0:
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('switching_sem_cobertura_referencial_positiva')
    elif valor_switchings < (pacote.valor_obrigacoes or 0.0):
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('switching_cobertura_referencial_insuficiente')
    else:
        pacote.status_factibilidade = 'factivel_referencialmente'
    return [pacote]


def gerar_pacotes_temporais_candidatos_dia(
    estado_dia: EstadoDiarioMotorTemporal,
    schema: SchemaPacoteTemporalCandidato,
) -> list[PacoteTemporalCandidato]:
    pacotes: list[PacoteTemporalCandidato] = []
    pacote_sem_obrigacao = gerar_pacote_sem_obrigacao(estado_dia)
    if pacote_sem_obrigacao:
        pacotes.append(pacote_sem_obrigacao)
    pacote_sem_cobertura = gerar_pacote_sem_cobertura(estado_dia)
    if pacote_sem_cobertura:
        pacotes.append(pacote_sem_cobertura)
    pacotes.extend(gerar_pacotes_pagamento_fonte_unica(estado_dia))
    pacote_combinacao = gerar_pacote_pagamento_combinacao_fontes(estado_dia)
    if pacote_combinacao:
        pacotes.append(pacote_combinacao)
    pacote_recebido = gerar_pacote_pagamento_com_recebido(estado_dia)
    if pacote_recebido:
        pacotes.append(pacote_recebido)
    pacotes.extend(gerar_pacotes_switching_integral(estado_dia))
    pacotes.extend(gerar_pacotes_switching_mais_pagamento(estado_dia))
    tipos_validos = set(schema.tipos_pacote_previstos)
    return [p for p in pacotes if p.tipo_pacote in tipos_validos]


def gerar_pacotes_temporais_candidatos(
    resultado: ResultadoMotorTemporalConjunto,
) -> dict[date, list[PacoteTemporalCandidato]]:
    schema = resultado.schema_pacote_temporal_candidato or montar_schema_pacote_temporal_candidato()
    estado_diario = resultado.estado_diario_motor or {}
    pacotes_por_data: dict[date, list[PacoteTemporalCandidato]] = {}
    for data_ref in resultado.horizonte_motor.datas_temporais:
        estado_dia = estado_diario.get(data_ref)
        pacotes_por_data[data_ref] = gerar_pacotes_temporais_candidatos_dia(estado_dia, schema) if estado_dia else []
    return pacotes_por_data


def auditar_pacotes_temporais_candidatos(resultado: ResultadoMotorTemporalConjunto) -> AuditoriaSchemaPacoteTemporalCandidato:
    schema = resultado.schema_pacote_temporal_candidato
    pacotes_por_data = resultado.pacotes_temporais_candidatos_por_data or {}
    estado_diario = resultado.estado_diario_motor or {}
    avisos: list[str] = []
    contagem_tipo: dict[str, int] = {}
    contagem_status: dict[str, int] = {}
    campos_proibidos = set(schema.campos_proibidos_decisao) if schema else set()
    tipos_validos = set(schema.tipos_pacote_previstos) if schema else set()
    status_validos = set(schema.status_factibilidade_previstos) if schema else set()
    for data_ref, pacotes in pacotes_por_data.items():
        if estado_diario.get(data_ref) and estado_diario[data_ref].obrigacoes.pagamentos_referenciados and not pacotes:
            avisos.append(f'data_com_obrigacao_sem_pacote:{data_ref.isoformat()}')
        for pacote in pacotes:
            contagem_tipo[pacote.tipo_pacote] = contagem_tipo.get(pacote.tipo_pacote, 0) + 1
            contagem_status[pacote.status_factibilidade] = contagem_status.get(pacote.status_factibilidade, 0) + 1
            if schema and pacote.tipo_pacote not in tipos_validos:
                avisos.append(f'tipo_fora_schema:{pacote.tipo_pacote}')
            if schema and pacote.status_factibilidade not in status_validos:
                avisos.append(f'status_fora_schema:{pacote.status_factibilidade}')
            campos_encontrados = campos_proibidos.intersection(pacote.metadados_auditoria.keys())
            if campos_encontrados:
                avisos.append(f'campo_proibido_decisao:{pacote.pacote_id}:{",".join(sorted(campos_encontrados))}')
    resumo = {'contagem_por_tipo': contagem_tipo, 'contagem_por_status': contagem_status, 'qtd_datas': len(pacotes_por_data)}
    return AuditoriaSchemaPacoteTemporalCandidato(ok=not avisos, avisos=avisos, resumo=resumo)


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

    possui_bloqueios_relevantes = any(
        bloqueio.codigo in {'estrutura_insuficiente', 'obrigacao_sem_fonte_referenciada'}
        for bloqueio in bloqueios
    )

    return AuditoriaMotorTemporalConjunto(
        ok=not avisos and not possui_bloqueios_relevantes,
        avisos=avisos,
        resumo=resumo,
    )


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


def valorar_pacote_temporal_candidato(
    pacote: PacoteTemporalCandidato,
    schema: SchemaPacoteTemporalCandidato,
) -> PacoteTemporalValorado:
    valor_obrigacoes = float(pacote.valor_obrigacoes or 0.0)
    valor_cobertura = float(pacote.valor_cobertura_referencial or 0.0)
    valor_descoberto = max(valor_obrigacoes - valor_cobertura, 0.0)
    cobertura_integral = valor_obrigacoes <= 0.0 or valor_descoberto <= 0.0

    penalidade_bloqueio = 100.0 if pacote.status_factibilidade == 'bloqueado_estruturalmente' else 0.0
    penalidade_status = 0.0
    if pacote.status_factibilidade == 'nao_avaliado':
        penalidade_status = 20.0
    elif pacote.status_factibilidade not in schema.status_factibilidade_previstos:
        penalidade_status = 200.0
    penalidade_switching = float(len(pacote.switchings_candidatos)) * 5.0
    if pacote.tipo_pacote == 'switching_integral_agregado':
        penalidade_switching += 10.0

    score = (valor_cobertura * 10.0) - (valor_descoberto * 8.0) - penalidade_bloqueio - penalidade_status - penalidade_switching
    if cobertura_integral:
        score += 50.0
    if pacote.tipo_pacote in {'pagamento_fonte_unica', 'sem_obrigacao'}:
        score += 5.0
    if pacote.tipo_pacote == 'pagamento_combinacao_fontes':
        score -= 2.0

    valoracao = ValoracaoPacoteTemporal(
        valor_obrigacoes=valor_obrigacoes,
        valor_cobertura_referencial=valor_cobertura,
        valor_descoberto_referencial=valor_descoberto,
        cobertura_integral_referencial=cobertura_integral,
        penalidade_bloqueio=penalidade_bloqueio,
        penalidade_status=penalidade_status,
        penalidade_switching=penalidade_switching,
        score_referencial=score,
    )
    valido = pacote.tipo_pacote in schema.tipos_pacote_previstos and pacote.status_factibilidade in schema.status_factibilidade_previstos
    return PacoteTemporalValorado(pacote_candidato=pacote, valoracao=valoracao, valido_no_schema=valido)


def valorar_pacotes_temporais_candidatos(resultado: ResultadoMotorTemporalConjunto) -> dict[date, list[PacoteTemporalValorado]]:
    schema = resultado.schema_pacote_temporal_candidato or montar_schema_pacote_temporal_candidato()
    valorados: dict[date, list[PacoteTemporalValorado]] = {}
    for data_ref in resultado.horizonte_motor.datas_temporais:
        pacotes = (resultado.pacotes_temporais_candidatos_por_data or {}).get(data_ref, [])
        valorados[data_ref] = [valorar_pacote_temporal_candidato(p, schema) for p in pacotes]
    return valorados


def selecionar_pacote_temporal_vencedor_dia(data_ref: date, pacotes_valorados: list[PacoteTemporalValorado]) -> tuple[DecisaoTemporalDia, list[PacoteTemporalDescartado], PacoteTemporalCandidato | None]:
    validos = [pv for pv in pacotes_valorados if pv.valido_no_schema]
    possui_obrigacao_aberta = any(pv.pacote_candidato.obrigacoes_referenciadas for pv in validos)
    if possui_obrigacao_aberta:
        validos = [
            pv
            for pv in validos
            if not (
                pv.pacote_candidato.tipo_pacote in {'switching_integral_simples', 'switching_integral_agregado'}
                and not pv.pacote_candidato.obrigacoes_referenciadas
            )
        ]
    if not validos:
        decisao = DecisaoTemporalDia(
            data_referencia=data_ref,
            pacote_vencedor_id=None,
            status_decisao='sem_pacote_valido',
            justificativa=JustificativaDecisaoTemporal(
                criterio_principal='ausencia_de_pacote_valido_no_schema',
                criterios_desempate_aplicados=[],
            ),
        )
        return decisao, [], None

    sem_obrigacao = [pv for pv in validos if pv.pacote_candidato.status_factibilidade == 'sem_obrigacao']
    if sem_obrigacao:
        vencedor = sorted(sem_obrigacao, key=lambda pv: pv.pacote_candidato.pacote_id)[0]
        criterio = 'data_sem_obrigacao_prioriza_pacote_sem_obrigacao'
    else:
        ordenados = sorted(
            validos,
            key=lambda pv: (
                0 if pv.pacote_candidato.status_factibilidade == 'factivel_referencialmente' else 1,
                0 if pv.valoracao.cobertura_integral_referencial else 1,
                -pv.valoracao.valor_cobertura_referencial,
                pv.valoracao.valor_descoberto_referencial,
                0 if pv.pacote_candidato.tipo_pacote in {'pagamento_fonte_unica', 'pagamento_com_recebido', 'sem_cobertura'} else 1,
                -pv.valoracao.score_referencial,
                pv.pacote_candidato.pacote_id,
            ),
        )
        vencedor = ordenados[0]
        criterio = 'ordenacao_heuristica_referencial'

    descartados = [
        PacoteTemporalDescartado(
            pacote_id=pv.pacote_candidato.pacote_id,
            tipo_pacote=pv.pacote_candidato.tipo_pacote,
            motivos_descarte=['nao_selecionado_na_data'],
            score_referencial=pv.valoracao.score_referencial,
        )
        for pv in validos
        if pv.pacote_candidato.pacote_id != vencedor.pacote_candidato.pacote_id
    ]
    decisao = DecisaoTemporalDia(
        data_referencia=data_ref,
        pacote_vencedor_id=vencedor.pacote_candidato.pacote_id,
        status_decisao='vencedor_selecionado',
        justificativa=JustificativaDecisaoTemporal(
            criterio_principal=criterio,
            criterios_desempate_aplicados=[
                'factivel_antes_bloqueado',
                'cobertura_integral_antes_parcial',
                'maior_cobertura_referencial',
                'menor_descoberto_referencial',
                'simplicidade_tipo',
                'ordem_estavel_pacote_id',
            ],
            resumo={'score_vencedor': vencedor.valoracao.score_referencial},
        ),
    )
    return decisao, descartados, vencedor.pacote_candidato


def selecionar_pacotes_temporais_vencedores(
    resultado: ResultadoMotorTemporalConjunto,
    pacotes_valorados: dict[date, list[PacoteTemporalValorado]],
) -> tuple[dict[date, DecisaoTemporalDia], dict[date, PacoteTemporalCandidato | None], dict[date, list[PacoteTemporalDescartado]]]:
    decisoes: dict[date, DecisaoTemporalDia] = {}
    vencedores: dict[date, PacoteTemporalCandidato | None] = {}
    descartados: dict[date, list[PacoteTemporalDescartado]] = {}
    reserva_por_fonte: dict[str, float] = {}
    for data_ref in resultado.horizonte_motor.datas_temporais:
        pacotes_data = list(pacotes_valorados.get(data_ref, []))
        filtrados: list[PacoteTemporalValorado] = []
        descartes_reserva: list[PacoteTemporalDescartado] = []
        for pv in pacotes_data:
            pacote = pv.pacote_candidato
            if pacote.tipo_pacote not in {'pagamento_fonte_unica', 'pagamento_combinacao_fontes'}:
                filtrados.append(pv)
                continue
            if not pacote.obrigacoes_referenciadas:
                filtrados.append(pv)
                continue
            fontes = pacote.fontes_candidatas
            if not fontes:
                descartes_reserva.append(PacoteTemporalDescartado(
                    pacote_id=pacote.pacote_id,
                    tipo_pacote=pacote.tipo_pacote,
                    motivos_descarte=['fonte_ausente_para_reserva_referencial'],
                    score_referencial=pv.valoracao.score_referencial,
                ))
                continue
            valor_obrig = float(pacote.valor_obrigacoes or 0.0)
            valor_cob = float(pacote.valor_cobertura_referencial or 0.0)
            if valor_cob <= 0.0:
                descartes_reserva.append(PacoteTemporalDescartado(
                    pacote_id=pacote.pacote_id,
                    tipo_pacote=pacote.tipo_pacote,
                    motivos_descarte=['fonte_sem_cobertura_referencial_positiva_para_reserva'],
                    score_referencial=pv.valoracao.score_referencial,
                ))
                continue
            valor_por_fonte = valor_cob / float(len(fontes))
            excedeu = False
            for fonte in fontes:
                if not fonte.fonte_id:
                    excedeu = True
                    break
                reservado = reserva_por_fonte.get(fonte.fonte_id, 0.0)
                if reservado + valor_por_fonte > valor_por_fonte and valor_obrig > 0.0 and reservado > 0.0:
                    excedeu = True
                    break
            if excedeu:
                descartes_reserva.append(PacoteTemporalDescartado(
                    pacote_id=pacote.pacote_id,
                    tipo_pacote=pacote.tipo_pacote,
                    motivos_descarte=['fonte_referencial_ja_reservada_em_data_anterior'],
                    score_referencial=pv.valoracao.score_referencial,
                ))
                continue
            filtrados.append(pv)
        decisao, lista_descartados, vencedor = selecionar_pacote_temporal_vencedor_dia(data_ref, filtrados)
        lista_descartados.extend(descartes_reserva)
        decisoes[data_ref] = decisao
        vencedores[data_ref] = vencedor
        descartados[data_ref] = lista_descartados
        if vencedor and vencedor.tipo_pacote in {'pagamento_fonte_unica', 'pagamento_combinacao_fontes'} and vencedor.fontes_candidatas:
            valor_cob = float(vencedor.valor_cobertura_referencial or 0.0)
            valor_por_fonte = valor_cob / float(len(vencedor.fontes_candidatas))
            for fonte in vencedor.fontes_candidatas:
                if fonte.fonte_id:
                    reserva_por_fonte[fonte.fonte_id] = reserva_por_fonte.get(fonte.fonte_id, 0.0) + valor_por_fonte
    return decisoes, vencedores, descartados



def _normalizar_valor_referencial(valor: Any) -> float | None:
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    return None


def extrair_identificador_fonte_pacote(fonte: FonteCandidataPacoteTemporal) -> tuple[str | None, str | None]:
    if fonte.fonte_id:
        return fonte.fonte_id, None
    referencia = fonte.referencia_estado_temporal or {}
    for campo in ('fonte_id', 'id', 'identificador', 'codigo'):
        valor = referencia.get(campo)
        if valor is not None:
            return str(valor), None
    return None, 'fonte_sem_identificador_estavel_para_reserva_referencial'


def extrair_valor_reservavel_fonte_pacote(
    fonte: FonteCandidataPacoteTemporal,
    pacote: PacoteTemporalCandidato | None = None,
) -> tuple[float | None, list[str]]:
    avisos: list[str] = []
    referencia = fonte.referencia_estado_temporal or {}
    for campo in ('valor_estimado', 'valor_disponivel', 'saldo_disponivel', 'saldo', 'valor'):
        valor = _normalizar_valor_referencial(referencia.get(campo))
        if valor is not None:
            return valor, avisos
    if pacote is not None and len(pacote.fontes_candidatas) == 1:
        valor_pacote = _normalizar_valor_referencial(pacote.valor_cobertura_referencial)
        if valor_pacote is not None:
            avisos.append('valor_reservavel_obtido_da_cobertura_referencial_do_pacote')
            return valor_pacote, avisos
    avisos.append('valor_reservavel_fonte_ausente_no_pacote')
    return None, avisos


def extrair_identificador_obrigacao_pacote(obrigacao: dict[str, Any]) -> tuple[str | None, list[str]]:
    avisos: list[str] = []
    for campo in ('obrigacao_id', 'pagamento_id', 'id', 'identificador', 'codigo'):
        valor = obrigacao.get(campo)
        if valor is not None:
            return str(valor), avisos
    avisos.append('obrigacao_sem_identificador_canonico_disponivel')
    return None, avisos


def _extrair_recebidos_referenciados_pacote(pacote: PacoteTemporalCandidato) -> list[dict[str, Any]]:
    recebidos: list[dict[str, Any]] = []
    for item in pacote.metadados_auditoria.get('recebidos_referenciados', []):
        if isinstance(item, dict) and isinstance(item.get('referencia'), dict):
            recebidos.append(item['referencia'])
    return recebidos


def _identificar_recebido_referencial(
    recebido: dict[str, Any],
    data_ref: date,
    pacote_id: str,
    posicao: int,
) -> str:
    for campo in ('recebido_id', 'id', 'identificador', 'codigo'):
        valor = recebido.get(campo)
        if valor is not None:
            return f'recebido:{valor}'
    return f'recebido_sem_id:{data_ref.isoformat()}:{pacote_id}:{posicao}'


def _valor_total_obrigacoes_pacote(pacote: PacoteTemporalCandidato) -> tuple[float, list[str]]:
    avisos: list[str] = []
    if pacote.valor_obrigacoes is not None:
        return float(pacote.valor_obrigacoes), avisos
    total = 0.0
    for obrigacao in pacote.obrigacoes_referenciadas:
        valor, avisos_obrigacao = extrair_valor_obrigacao_referencial(obrigacao)
        avisos.extend(avisos_obrigacao)
        total += float(valor or 0.0)
    return total, avisos


def _registrar_switchings_escolhidos(
    data_ref: date,
    pacote: PacoteTemporalCandidato,
) -> tuple[list[SwitchingEscolhidoTemporalmente], list[EventoTrajetoriaTemporalInterna]]:
    switchings: list[SwitchingEscolhidoTemporalmente] = []
    eventos: list[EventoTrajetoriaTemporalInterna] = []
    for switching in pacote.switchings_candidatos:
        escolhido = SwitchingEscolhidoTemporalmente(
            data=data_ref,
            switching_id=switching.switching_id,
            pacote_id=pacote.pacote_id,
            lote_origem_id=switching.lote_origem_id,
            lote_destino_id=switching.lote_destino_id,
            tipo_switching=switching.tipo_switching,
            status_referencial='escolhido_internamente_nao_executado',
            referencia_estado_temporal=switching.referencia_estado_temporal,
        )
        switchings.append(escolhido)
        eventos.append(EventoTrajetoriaTemporalInterna(
            data=data_ref,
            tipo_evento_interno='switching_escolhido_referencialmente',
            pacote_id=pacote.pacote_id,
            tipo_pacote=pacote.tipo_pacote,
            status_referencial='nao_executado_oficialmente',
            detalhes={'switching_id': switching.switching_id},
        ))
    return switchings, eventos


def _reservar_fontes_referenciais(
    data_ref: date,
    pacote: PacoteTemporalCandidato,
    valor_necessario: float,
    saldos_disponiveis: dict[str, float],
    reservas_acumuladas: dict[str, float],
    obrigacao_id: str | None,
) -> tuple[list[FonteReservadaTemporalmente], float, list[str]]:
    reservas: list[FonteReservadaTemporalmente] = []
    alertas: list[str] = []
    restante = valor_necessario
    fontes_ordenadas = sorted(
        pacote.fontes_candidatas,
        key=lambda f: (f.fonte_id or '', f.tipo_fonte or '', f.origem_fonte or ''),
    )
    for fonte in fontes_ordenadas:
        if restante <= 0.0:
            break
        fonte_id, alerta_id = extrair_identificador_fonte_pacote(fonte)
        if alerta_id:
            alertas.append(alerta_id)
            continue
        assert fonte_id is not None
        valor_fonte, avisos_valor = extrair_valor_reservavel_fonte_pacote(fonte, pacote)
        alertas.extend(avisos_valor)
        if valor_fonte is None:
            continue
        if fonte_id not in saldos_disponiveis:
            saldos_disponiveis[fonte_id] = max(float(valor_fonte) - reservas_acumuladas.get(fonte_id, 0.0), 0.0)
        antes = saldos_disponiveis.get(fonte_id, 0.0)
        valor_reserva = min(antes, restante)
        if valor_reserva <= 0.0:
            alertas.append(f'fonte_sem_saldo_referencial_disponivel:{fonte_id}')
            continue
        depois = antes - valor_reserva
        saldos_disponiveis[fonte_id] = depois
        reservas_acumuladas[fonte_id] = reservas_acumuladas.get(fonte_id, 0.0) + valor_reserva
        reservas.append(FonteReservadaTemporalmente(
            data=data_ref,
            fonte_id=fonte_id,
            pacote_id=pacote.pacote_id,
            tipo_fonte=fonte.tipo_fonte,
            origem_fonte=fonte.origem_fonte,
            valor_reservado_referencial=valor_reserva,
            valor_disponivel_antes_referencial=antes,
            valor_disponivel_depois_referencial=depois,
            obrigacao_id=obrigacao_id,
            referencia_estado_temporal=fonte.referencia_estado_temporal,
        ))
        restante -= valor_reserva
    return reservas, valor_necessario - restante, alertas


def _reservar_recebidos_referenciais(
    data_ref: date,
    pacote: PacoteTemporalCandidato,
    valor_necessario: float,
    saldos_disponiveis: dict[str, float],
    reservas_acumuladas: dict[str, float],
    obrigacao_id: str | None,
) -> tuple[list[FonteReservadaTemporalmente], float, list[str]]:
    reservas: list[FonteReservadaTemporalmente] = []
    alertas: list[str] = []
    restante = valor_necessario
    for posicao, recebido in enumerate(_extrair_recebidos_referenciados_pacote(pacote), start=1):
        if restante <= 0.0:
            break
        fonte_id = _identificar_recebido_referencial(recebido, data_ref, pacote.pacote_id, posicao)
        valor_recebido, avisos_recebido = extrair_valor_recebido_referencial(recebido)
        alertas.extend(avisos_recebido)
        if valor_recebido is None:
            continue
        if fonte_id not in saldos_disponiveis:
            saldos_disponiveis[fonte_id] = max(float(valor_recebido) - reservas_acumuladas.get(fonte_id, 0.0), 0.0)
        antes = saldos_disponiveis.get(fonte_id, 0.0)
        valor_reserva = min(antes, restante)
        if valor_reserva <= 0.0:
            alertas.append(f'recebido_sem_saldo_referencial_disponivel:{fonte_id}')
            continue
        depois = antes - valor_reserva
        saldos_disponiveis[fonte_id] = depois
        reservas_acumuladas[fonte_id] = reservas_acumuladas.get(fonte_id, 0.0) + valor_reserva
        reservas.append(FonteReservadaTemporalmente(
            data=data_ref,
            fonte_id=fonte_id,
            pacote_id=pacote.pacote_id,
            tipo_fonte='recebido_referencial',
            origem_fonte='pacote_temporal_vencedor',
            valor_reservado_referencial=valor_reserva,
            valor_disponivel_antes_referencial=antes,
            valor_disponivel_depois_referencial=depois,
            obrigacao_id=obrigacao_id,
            referencia_estado_temporal=recebido,
        ))
        restante -= valor_reserva
    return reservas, valor_necessario - restante, alertas


def _bloquear_obrigacoes_individualmente(
    data_ref: date,
    pacote: PacoteTemporalCandidato,
    motivo: str,
    valor_cobertura_referencial: float = 0.0,
) -> tuple[list[ObrigacaoBloqueadaTemporalmente], list[str]]:
    bloqueadas: list[ObrigacaoBloqueadaTemporalmente] = []
    alertas: list[str] = []
    for obrigacao in pacote.obrigacoes_referenciadas:
        valor_obrigacao, avisos_obrigacao = extrair_valor_obrigacao_referencial(obrigacao)
        obrigacao_id, avisos_id = extrair_identificador_obrigacao_pacote(obrigacao)
        alertas.extend(avisos_obrigacao)
        alertas.extend(avisos_id)
        bloqueadas.append(ObrigacaoBloqueadaTemporalmente(
            data=data_ref,
            obrigacao_id=obrigacao_id,
            pacote_id=pacote.pacote_id,
            motivo_bloqueio_referencial=motivo,
            valor_obrigacao_referencial=float(valor_obrigacao or 0.0),
            valor_cobertura_referencial=valor_cobertura_referencial,
            referencia_obrigacao_temporal=obrigacao,
        ))
    if not pacote.obrigacoes_referenciadas:
        bloqueadas.append(ObrigacaoBloqueadaTemporalmente(
            data=data_ref,
            obrigacao_id=None,
            pacote_id=pacote.pacote_id,
            motivo_bloqueio_referencial=motivo,
            valor_obrigacao_referencial=0.0,
            valor_cobertura_referencial=valor_cobertura_referencial,
            referencia_obrigacao_temporal={},
        ))
    return bloqueadas, alertas


def _bloquear_obrigacoes_sem_pacote_vencedor(
    data_ref: date,
    obrigacoes_do_dia: ObrigacoesTemporaisDia | None,
) -> tuple[list[ObrigacaoBloqueadaTemporalmente], list[str]]:
    bloqueadas: list[ObrigacaoBloqueadaTemporalmente] = []
    alertas: list[str] = []
    for obrigacao in (obrigacoes_do_dia.pagamentos_referenciados if obrigacoes_do_dia else []):
        valor_obrigacao, avisos_obrigacao = extrair_valor_obrigacao_referencial(obrigacao)
        obrigacao_id, avisos_id = extrair_identificador_obrigacao_pacote(obrigacao)
        alertas.extend(avisos_obrigacao)
        alertas.extend(avisos_id)
        bloqueadas.append(ObrigacaoBloqueadaTemporalmente(
            data=data_ref,
            obrigacao_id=obrigacao_id,
            pacote_id=None,
            motivo_bloqueio_referencial='sem_pacote_valido_para_obrigacao_temporal',
            valor_obrigacao_referencial=float(valor_obrigacao or 0.0),
            valor_cobertura_referencial=0.0,
            referencia_obrigacao_temporal=obrigacao,
        ))
    return bloqueadas, alertas

def _cobrir_obrigacoes_referencialmente(
    data_ref: date,
    pacote: PacoteTemporalCandidato,
    reservas: list[FonteReservadaTemporalmente],
    valor_coberto: float,
) -> tuple[list[ObrigacaoCobertaTemporalmente], list[ObrigacaoBloqueadaTemporalmente], list[str]]:
    cobertas: list[ObrigacaoCobertaTemporalmente] = []
    alertas: list[str] = []
    valor_obrigacoes, avisos_valor = _valor_total_obrigacoes_pacote(pacote)
    alertas.extend(avisos_valor)
    if valor_obrigacoes <= 0.0:
        return cobertas, [], alertas
    if valor_coberto + 0.000001 < valor_obrigacoes:
        bloqueadas, avisos_bloqueio = _bloquear_obrigacoes_individualmente(
            data_ref,
            pacote,
            'cobertura_referencial_insuficiente_na_aplicacao_interna',
            valor_coberto,
        )
        alertas.extend(avisos_bloqueio)
        return cobertas, bloqueadas, alertas
    for obrigacao in pacote.obrigacoes_referenciadas:
        valor_obrigacao, avisos_obrigacao = extrair_valor_obrigacao_referencial(obrigacao)
        obrigacao_id, avisos_id = extrair_identificador_obrigacao_pacote(obrigacao)
        alertas.extend(avisos_obrigacao)
        alertas.extend(avisos_id)
        valor = float(valor_obrigacao or 0.0)
        cobertas.append(ObrigacaoCobertaTemporalmente(
            data=data_ref,
            obrigacao_id=obrigacao_id,
            pacote_id=pacote.pacote_id,
            valor_obrigacao_referencial=valor,
            valor_coberto_referencial=valor,
            fontes_reservadas_ids=[r.fonte_id for r in reservas],
            referencia_obrigacao_temporal=obrigacao,
        ))
    return cobertas, [], alertas


def _saldos_do_dia(data_ref: date, saldos_disponiveis: dict[str, float], reservas_acumuladas: dict[str, float]) -> list[SaldoReferencialFonteTemporal]:
    return [
        SaldoReferencialFonteTemporal(
            data=data_ref,
            fonte_id=fonte_id,
            valor_disponivel_referencial=saldos_disponiveis.get(fonte_id, 0.0),
            valor_reservado_acumulado_referencial=reservas_acumuladas.get(fonte_id, 0.0),
        )
        for fonte_id in sorted(set(saldos_disponiveis) | set(reservas_acumuladas))
    ]


def aplicar_pacote_temporal_vencedor_dia(
    data_ref: date,
    decisao: DecisaoTemporalDia | None,
    pacote: PacoteTemporalCandidato | None,
    saldos_disponiveis: dict[str, float],
    reservas_acumuladas: dict[str, float],
    obrigacoes_do_dia: ObrigacoesTemporaisDia | None = None,
) -> EstadoTemporalInternoDia:
    eventos: list[EventoTrajetoriaTemporalInterna] = []
    reservas: list[FonteReservadaTemporalmente] = []
    cobertas: list[ObrigacaoCobertaTemporalmente] = []
    bloqueadas: list[ObrigacaoBloqueadaTemporalmente] = []
    switchings: list[SwitchingEscolhidoTemporalmente] = []
    alertas: list[str] = []

    if pacote is None:
        bloqueadas, alertas_bloqueio = _bloquear_obrigacoes_sem_pacote_vencedor(data_ref, obrigacoes_do_dia)
        alertas.extend(alertas_bloqueio)
        eventos.append(EventoTrajetoriaTemporalInterna(
            data=data_ref,
            tipo_evento_interno='sem_pacote_vencedor',
            pacote_id=None,
            tipo_pacote=None,
            status_referencial='bloqueado_sem_pacote_vencedor',
            detalhes={'status_decisao': decisao.status_decisao if decisao else None},
        ))
        return EstadoTemporalInternoDia(
            data=data_ref,
            pacote_id=None,
            tipo_pacote=None,
            status_referencial='bloqueado_sem_pacote_vencedor',
            eventos_internos=eventos,
            saldos_fontes_referenciais=_saldos_do_dia(data_ref, saldos_disponiveis, reservas_acumuladas),
            obrigacoes_bloqueadas=bloqueadas,
            alertas=alertas,
        )

    eventos.append(EventoTrajetoriaTemporalInterna(
        data=data_ref,
        tipo_evento_interno='pacote_temporal_vencedor_aplicado_internamente',
        pacote_id=pacote.pacote_id,
        tipo_pacote=pacote.tipo_pacote,
        status_referencial='aplicacao_referencial_sem_efeito_externo',
        detalhes={'status_decisao': decisao.status_decisao if decisao else None},
    ))

    if pacote.tipo_pacote == 'sem_obrigacao':
        eventos.append(EventoTrajetoriaTemporalInterna(
            data=data_ref,
            tipo_evento_interno='dia_sem_obrigacao_referencial',
            pacote_id=pacote.pacote_id,
            tipo_pacote=pacote.tipo_pacote,
            status_referencial='sem_obrigacao_a_cobrir',
        ))
    elif pacote.tipo_pacote == 'sem_cobertura':
        bloqueadas, avisos_bloqueio = _bloquear_obrigacoes_individualmente(
            data_ref,
            pacote,
            'pacote_vencedor_sem_cobertura_referencial',
            0.0,
        )
        alertas.extend(avisos_bloqueio)
    else:
        valor_necessario, avisos_valor = _valor_total_obrigacoes_pacote(pacote)
        alertas.extend(avisos_valor)
        saldos_antes_reserva = dict(saldos_disponiveis)
        reservas_antes_reserva = dict(reservas_acumuladas)
        obrigacao_ref = pacote.obrigacoes_referenciadas[0] if pacote.obrigacoes_referenciadas else {}
        obrigacao_id, avisos_id = extrair_identificador_obrigacao_pacote(obrigacao_ref) if obrigacao_ref else (None, [])
        alertas.extend(avisos_id)

        if pacote.tipo_pacote in {'switching_integral_simples', 'switching_integral_agregado', 'switching_mais_pagamento'}:
            switchings, eventos_switch = _registrar_switchings_escolhidos(data_ref, pacote)
            eventos.extend(eventos_switch)

        valor_coberto = 0.0
        if pacote.tipo_pacote in {'pagamento_fonte_unica', 'pagamento_combinacao_fontes'}:
            reservas, valor_coberto, alertas_reserva = _reservar_fontes_referenciais(
                data_ref,
                pacote,
                valor_necessario,
                saldos_disponiveis,
                reservas_acumuladas,
                obrigacao_id,
            )
            alertas.extend(alertas_reserva)
        elif pacote.tipo_pacote == 'pagamento_com_recebido':
            reservas, valor_coberto, alertas_reserva = _reservar_recebidos_referenciais(
                data_ref,
                pacote,
                valor_necessario,
                saldos_disponiveis,
                reservas_acumuladas,
                obrigacao_id,
            )
            alertas.extend(alertas_reserva)
        elif pacote.tipo_pacote == 'switching_mais_pagamento':
            valor_coberto = float(pacote.valor_cobertura_referencial or 0.0)

        if pacote.obrigacoes_referenciadas:
            cobertas, bloqueadas, alertas_cobertura = _cobrir_obrigacoes_referencialmente(
                data_ref,
                pacote,
                reservas,
                valor_coberto,
            )
            alertas.extend(alertas_cobertura)
            if bloqueadas and reservas:
                saldos_disponiveis.clear()
                saldos_disponiveis.update(saldos_antes_reserva)
                reservas_acumuladas.clear()
                reservas_acumuladas.update(reservas_antes_reserva)
                reservas = []
                alertas.append('reservas_referenciais_desfeitas_por_pacote_bloqueado')
            if cobertas:
                eventos.append(EventoTrajetoriaTemporalInterna(
                    data=data_ref,
                    tipo_evento_interno='pagamento_coberto_referencialmente',
                    pacote_id=pacote.pacote_id,
                    tipo_pacote=pacote.tipo_pacote,
                    status_referencial='coberto_internamente_sem_pagamento_oficial',
                    detalhes={'valor_coberto_referencial': valor_coberto},
                ))
            if bloqueadas:
                eventos.append(EventoTrajetoriaTemporalInterna(
                    data=data_ref,
                    tipo_evento_interno='obrigacao_bloqueada_referencialmente',
                    pacote_id=pacote.pacote_id,
                    tipo_pacote=pacote.tipo_pacote,
                    status_referencial='bloqueado_internamente',
                    detalhes={'valor_coberto_referencial': valor_coberto},
                ))

    status = 'aplicado_referencialmente'
    if bloqueadas:
        status = 'bloqueado_referencialmente'
    return EstadoTemporalInternoDia(
        data=data_ref,
        pacote_id=pacote.pacote_id,
        tipo_pacote=pacote.tipo_pacote,
        status_referencial=status,
        eventos_internos=eventos,
        saldos_fontes_referenciais=_saldos_do_dia(data_ref, saldos_disponiveis, reservas_acumuladas),
        fontes_reservadas=reservas,
        obrigacoes_cobertas=cobertas,
        obrigacoes_bloqueadas=bloqueadas,
        switchings_escolhidos=switchings,
        alertas=alertas,
    )


def aplicar_trajetoria_temporal_interna(
    resultado: ResultadoMotorTemporalConjunto,
) -> TrajetoriaTemporalInternaEscolhida:
    saldos_disponiveis: dict[str, float] = {}
    reservas_acumuladas: dict[str, float] = {}
    estados: dict[date, EstadoTemporalInternoDia] = {}
    eventos: list[EventoTrajetoriaTemporalInterna] = []
    reservas: list[FonteReservadaTemporalmente] = []
    cobertas: list[ObrigacaoCobertaTemporalmente] = []
    bloqueadas: list[ObrigacaoBloqueadaTemporalmente] = []
    switchings: list[SwitchingEscolhidoTemporalmente] = []
    saldos_por_data: dict[date, list[SaldoReferencialFonteTemporal]] = {}

    decisoes = resultado.decisoes_temporais_por_data or {}
    vencedores = resultado.pacote_vencedor_por_data or {}
    for data_ref in sorted(resultado.horizonte_motor.datas_temporais):
        estado_dia = aplicar_pacote_temporal_vencedor_dia(
            data_ref,
            decisoes.get(data_ref),
            vencedores.get(data_ref),
            saldos_disponiveis,
            reservas_acumuladas,
            (resultado.estado_diario_motor.get(data_ref).obrigacoes if resultado.estado_diario_motor.get(data_ref) else None),
        )
        estados[data_ref] = estado_dia
        eventos.extend(estado_dia.eventos_internos)
        reservas.extend(estado_dia.fontes_reservadas)
        cobertas.extend(estado_dia.obrigacoes_cobertas)
        bloqueadas.extend(estado_dia.obrigacoes_bloqueadas)
        switchings.extend(estado_dia.switchings_escolhidos)
        saldos_por_data[data_ref] = estado_dia.saldos_fontes_referenciais

    return TrajetoriaTemporalInternaEscolhida(
        estado_temporal_interno_por_data=estados,
        eventos_trajetoria_temporal=eventos,
        fontes_reservadas_temporalmente=reservas,
        obrigacoes_cobertas_temporalmente=cobertas,
        obrigacoes_bloqueadas_temporalmente=bloqueadas,
        switchings_escolhidos_temporalmente=switchings,
        saldos_referenciais_fontes_temporais=saldos_por_data,
    )


def _chave_obrigacao_referencial_auditoria(obrigacao: dict[str, Any]) -> str:
    obrigacao_id, _ = extrair_identificador_obrigacao_pacote(obrigacao)
    if obrigacao_id is not None:
        return f'id:{obrigacao_id}'
    return f'ref:{id(obrigacao)}'


def auditar_trajetoria_temporal_interna(
    resultado: ResultadoMotorTemporalConjunto,
) -> AuditoriaTrajetoriaTemporalInterna:
    avisos: list[str] = []
    bloqueios: list[str] = []
    trajetoria = resultado.trajetoria_temporal_interna_escolhida
    if trajetoria is None:
        return AuditoriaTrajetoriaTemporalInterna(
            ok=False,
            avisos=[],
            bloqueios=['trajetoria_temporal_interna_ausente'],
            resumo={},
        )

    datas_horizonte = set(resultado.horizonte_motor.datas_temporais)
    datas_estado = set(trajetoria.estado_temporal_interno_por_data)
    if datas_estado != datas_horizonte:
        bloqueios.append('estado_temporal_interno_nao_cobre_horizonte')

    vencedores = resultado.pacote_vencedor_por_data or {}
    for data_ref in resultado.horizonte_motor.datas_temporais:
        estado_dia = trajetoria.estado_temporal_interno_por_data.get(data_ref)
        decisao = (resultado.decisoes_temporais_por_data or {}).get(data_ref)
        if decisao is not None and estado_dia is None:
            bloqueios.append(f'decisao_sem_estado_interno:{data_ref.isoformat()}')
            continue
        if decisao is not None and estado_dia is not None and not estado_dia.eventos_internos and not estado_dia.obrigacoes_bloqueadas:
            bloqueios.append(f'decisao_sem_evento_ou_bloqueio:{data_ref.isoformat()}')
        pacote = vencedores.get(data_ref)
        if estado_dia is None:
            continue
        if pacote is None:
            obrigacoes_abertas = list((resultado.estado_diario_motor.get(data_ref).obrigacoes.pagamentos_referenciados if resultado.estado_diario_motor.get(data_ref) else []))
            if obrigacoes_abertas:
                chaves_obrigacoes = {_chave_obrigacao_referencial_auditoria(obrigacao) for obrigacao in obrigacoes_abertas}
                chaves_bloqueadas = {
                    _chave_obrigacao_referencial_auditoria(bloqueada.referencia_obrigacao_temporal)
                    for bloqueada in estado_dia.obrigacoes_bloqueadas
                    if bloqueada.pacote_id is None
                    and bloqueada.motivo_bloqueio_referencial == 'sem_pacote_valido_para_obrigacao_temporal'
                }
                if not chaves_obrigacoes.issubset(chaves_bloqueadas):
                    bloqueios.append(f'obrigacao_sem_pacote_valido_sem_bloqueio_individual:{data_ref.isoformat()}')
            if estado_dia.fontes_reservadas:
                bloqueios.append(f'reserva_persistida_sem_pacote_vencedor:{data_ref.isoformat()}')
            continue
        if not pacote.obrigacoes_referenciadas:
            continue
        chaves_obrigacoes = {
            _chave_obrigacao_referencial_auditoria(obrigacao)
            for obrigacao in pacote.obrigacoes_referenciadas
        }
        chaves_cobertas = {
            _chave_obrigacao_referencial_auditoria(coberta.referencia_obrigacao_temporal)
            for coberta in estado_dia.obrigacoes_cobertas
        }
        chaves_bloqueadas = {
            _chave_obrigacao_referencial_auditoria(bloqueada.referencia_obrigacao_temporal)
            for bloqueada in estado_dia.obrigacoes_bloqueadas
        }
        chaves_tratadas = chaves_cobertas | chaves_bloqueadas
        if not chaves_obrigacoes.issubset(chaves_tratadas):
            bloqueios.append(f'obrigacao_aberta_sem_cobertura_ou_bloqueio_individual:{data_ref.isoformat()}')
        if len(pacote.obrigacoes_referenciadas) > 1 and estado_dia.obrigacoes_bloqueadas:
            if len(estado_dia.obrigacoes_bloqueadas) not in {len(pacote.obrigacoes_referenciadas), len(chaves_bloqueadas)}:
                bloqueios.append(f'bloqueio_agregado_indevido_em_multiplas_obrigacoes:{data_ref.isoformat()}')
            if len(estado_dia.obrigacoes_bloqueadas) == 1 and len(chaves_obrigacoes) > 1:
                bloqueios.append(f'bloqueio_agregado_indevido_em_multiplas_obrigacoes:{data_ref.isoformat()}')
        if estado_dia.status_referencial == 'bloqueado_referencialmente' and estado_dia.fontes_reservadas:
            bloqueios.append(f'reserva_persistida_para_pacote_bloqueado:{data_ref.isoformat()}')

    disponibilidade_inicial: dict[str, float] = {}
    reservado_por_fonte: dict[str, float] = {}
    ids_recebidos_anonimos: dict[str, set[date]] = {}
    for reserva in trajetoria.fontes_reservadas_temporalmente:
        if reserva.valor_reservado_referencial > reserva.valor_disponivel_antes_referencial + 0.000001:
            bloqueios.append(f'reserva_acima_disponivel_referencial:{reserva.fonte_id}')
        valor_depois_esperado = reserva.valor_disponivel_antes_referencial - reserva.valor_reservado_referencial
        if abs(valor_depois_esperado - reserva.valor_disponivel_depois_referencial) > 0.000001:
            bloqueios.append(f'saldo_referencial_inconsistente_apos_reserva:{reserva.fonte_id}')
        if reserva.fonte_id.startswith('recebido_sem_id:'):
            ids_recebidos_anonimos.setdefault(reserva.fonte_id, set()).add(reserva.data)
        disponibilidade_inicial[reserva.fonte_id] = max(
            disponibilidade_inicial.get(reserva.fonte_id, 0.0),
            reserva.valor_disponivel_antes_referencial + reservado_por_fonte.get(reserva.fonte_id, 0.0),
        )
        reservado_por_fonte[reserva.fonte_id] = reservado_por_fonte.get(reserva.fonte_id, 0.0) + reserva.valor_reservado_referencial
        if reservado_por_fonte[reserva.fonte_id] > disponibilidade_inicial[reserva.fonte_id] + 0.000001:
            bloqueios.append(f'fonte_sobrecomprometida:{reserva.fonte_id}')
    for fonte_id, datas in ids_recebidos_anonimos.items():
        if len(datas) > 1:
            bloqueios.append(f'recebido_anonimo_com_id_duplicado_entre_datas:{fonte_id}')

    cobertas_insuficientes = [
        c
        for c in trajetoria.obrigacoes_cobertas_temporalmente
        if c.valor_coberto_referencial + 0.000001 < c.valor_obrigacao_referencial
    ]
    if cobertas_insuficientes:
        bloqueios.append('obrigacao_coberta_com_cobertura_insuficiente')

    for switching in trajetoria.switchings_escolhidos_temporalmente:
        if switching.status_referencial != 'escolhido_internamente_nao_executado':
            bloqueios.append(f'switching_com_status_nao_referencial:{switching.switching_id}')

    for evento in trajetoria.eventos_trajetoria_temporal:
        texto = f'{evento.tipo_evento_interno} {evento.status_referencial}'.lower()
        if 'ledger' in texto:
            bloqueios.append(f'evento_interno_indica_ledger:{evento.pacote_id}')
        if 'oficial' in texto and 'nao_' not in texto and 'sem_' not in texto:
            avisos.append(f'evento_interno_com_termo_oficial:{evento.pacote_id}')

    avisos.extend([
        'trajetoria_sem_alteracao_de_dados',
        'trajetoria_sem_console_xlsx_saida_canonica_como_fonte',
        'switching_escolhido_apenas_referencialmente',
    ])
    qtd_alertas_reserva_insuficiente = sum(
        1
        for estado_dia in trajetoria.estado_temporal_interno_por_data.values()
        for alerta in estado_dia.alertas
        if 'sem_saldo' in alerta or 'insuficiente' in alerta or 'ausente' in alerta
    )
    qtd_alertas_fonte_sobrecomprometida = sum(1 for b in bloqueios if b.startswith('fonte_sobrecomprometida:'))
    resumo = {
        'qtd_datas_horizonte': len(resultado.horizonte_motor.datas_temporais),
        'qtd_datas_com_estado_interno': len(trajetoria.estado_temporal_interno_por_data),
        'qtd_eventos_internos': len(trajetoria.eventos_trajetoria_temporal),
        'qtd_obrigacoes_cobertas_referencialmente': len(trajetoria.obrigacoes_cobertas_temporalmente),
        'qtd_obrigacoes_bloqueadas': len(trajetoria.obrigacoes_bloqueadas_temporalmente),
        'qtd_fontes_reservadas': len(trajetoria.fontes_reservadas_temporalmente),
        'qtd_switchings_escolhidos': len(trajetoria.switchings_escolhidos_temporalmente),
        'qtd_alertas_reserva_insuficiente': qtd_alertas_reserva_insuficiente,
        'qtd_alertas_fonte_sobrecomprometida': qtd_alertas_fonte_sobrecomprometida,
        'ok': not bloqueios and not trajetoria.obrigacoes_bloqueadas_temporalmente,
    }
    return AuditoriaTrajetoriaTemporalInterna(
        ok=bool(resumo['ok']),
        avisos=avisos,
        bloqueios=bloqueios,
        resumo=resumo,
    )

def auditar_decisoes_temporais(resultado: ResultadoMotorTemporalConjunto) -> AuditoriaDecisaoTemporalConjunto:
    avisos: list[str] = []
    schema = resultado.schema_pacote_temporal_candidato
    status_validos = set(schema.status_factibilidade_previstos) if schema else set()
    pacotes_por_data = resultado.pacotes_temporais_candidatos_por_data or {}
    decisoes = resultado.decisoes_temporais_por_data or {}
    estado_diario = resultado.estado_diario_motor or {}
    vencedores = resultado.pacote_vencedor_por_data or {}
    for data_ref in resultado.horizonte_motor.datas_temporais:
        decisao = decisoes.get(data_ref)
        if decisao is None:
            avisos.append(f'data_sem_decisao:{data_ref.isoformat()}')
            continue
        if estado_diario.get(data_ref) and estado_diario[data_ref].obrigacoes.pagamentos_referenciados and decisao.pacote_vencedor_id is None:
            avisos.append(f'data_com_obrigacao_sem_vencedor:{data_ref.isoformat()}')
        if estado_diario.get(data_ref):
            obrigacoes = estado_diario[data_ref].obrigacoes
            if len(obrigacoes.indices_pagamentos) != len(obrigacoes.pagamentos_referenciados):
                avisos.append(f'inconsistencia_indices_pagamentos_referenciados:{data_ref.isoformat()}')
        vencedor = vencedores.get(data_ref)
        ids = {p.pacote_id for p in pacotes_por_data.get(data_ref, [])}
        if decisao.pacote_vencedor_id and decisao.pacote_vencedor_id not in ids:
            avisos.append(f'vencedor_nao_pertence_a_data:{data_ref.isoformat()}')
        if vencedor and vencedor.status_factibilidade not in status_validos:
            avisos.append(f'status_vencedor_fora_schema:{data_ref.isoformat()}')
        possui_obrigacao_aberta = bool(estado_diario.get(data_ref) and estado_diario[data_ref].obrigacoes.pagamentos_referenciados)
        if (
            possui_obrigacao_aberta
            and vencedor
            and vencedor.tipo_pacote in {'switching_integral_simples', 'switching_integral_agregado'}
            and not vencedor.obrigacoes_referenciadas
        ):
            avisos.append(f'vencedor_switching_only_com_obrigacao_aberta:{data_ref.isoformat()}')
        if (
            vencedor
            and bool(vencedor.obrigacoes_referenciadas)
            and (vencedor.valor_obrigacoes or 0.0) > (vencedor.valor_cobertura_referencial or 0.0)
            and vencedor.status_factibilidade != 'bloqueado_estruturalmente'
        ):
            avisos.append(f'vencedor_com_descoberto_sem_bloqueio:{data_ref.isoformat()}')
        if vencedor and vencedor.tipo_pacote == 'pagamento_com_recebido' and vencedor.status_factibilidade == 'factivel_referencialmente':
            refs = vencedor.metadados_auditoria.get('recebidos_referenciados', [])
            indisponivel = any(
                r.get('referencia', {}).get('disponivel_na_referencia') is False
                or r.get('referencia', {}).get('aplicado') is True
                or r.get('referencia', {}).get('vinculado') is True
                or r.get('referencia', {}).get('futuro_indisponivel') is True
                for r in refs
                if isinstance(r, dict)
            )
            if indisponivel:
                avisos.append(f'pagamento_com_recebido_factivel_com_recebido_indisponivel:{data_ref.isoformat()}')
            if (vencedor.valor_cobertura_referencial or 0.0) < (vencedor.valor_obrigacoes or 0.0):
                avisos.append(f'pagamento_com_recebido_factivel_com_cobertura_parcial:{data_ref.isoformat()}')
        if vencedor and vencedor.tipo_pacote in {'pagamento_fonte_unica', 'pagamento_combinacao_fontes'}:
            if any(f.fonte_id is None for f in vencedor.fontes_candidatas):
                avisos.append(f'vencedor_com_fonte_sem_id:{data_ref.isoformat()}')
            if vencedor.valor_cobertura_referencial is None:
                avisos.append(f'vencedor_com_fonte_sem_valor_conhecido:{data_ref.isoformat()}')
        if decisao.executa_pagamento:
            avisos.append(f'decisao_indica_execucao_pagamento:{data_ref.isoformat()}')
        if decisao.executa_switching:
            avisos.append(f'decisao_indica_execucao_switching:{data_ref.isoformat()}')
        if decisao.gera_ledger:
            avisos.append(f'decisao_indica_ledger:{data_ref.isoformat()}')
    resumo = {
        'qtd_datas_horizonte': len(resultado.horizonte_motor.datas_temporais),
        'qtd_decisoes': len(decisoes),
        'qtd_vencedores': len([v for v in vencedores.values() if v is not None]),
    }
    return AuditoriaDecisaoTemporalConjunto(ok=not avisos, avisos=avisos, resumo=resumo)



def montar_sumario_final_etapa5(resultado: ResultadoMotorTemporalConjunto) -> SumarioFinalEtapa5:
    auditoria_trajetoria = resultado.auditoria_trajetoria_temporal_interna
    auditorias_avisos = [
        resultado.status_interface_etapa5.avisos,
        resultado.auditoria_motor_temporal_conjunto.avisos if resultado.auditoria_motor_temporal_conjunto else [],
        resultado.auditoria_schema_pacote_temporal_candidato.avisos if resultado.auditoria_schema_pacote_temporal_candidato else [],
        resultado.auditoria_decisao_temporal_conjunto.avisos if resultado.auditoria_decisao_temporal_conjunto else [],
        auditoria_trajetoria.avisos if auditoria_trajetoria else [],
        resultado.auditoria_integridade_resultado.avisos if resultado.auditoria_integridade_resultado else [],
    ]
    return SumarioFinalEtapa5(
        qtd_datas_horizonte=len(resultado.horizonte_motor.datas_temporais),
        qtd_dias_motor=len(resultado.dias_motor or []),
        qtd_pacotes_candidatos=sum(len(p) for p in (resultado.pacotes_temporais_candidatos_por_data or {}).values()),
        qtd_pacotes_valorados=sum(len(p) for p in (resultado.pacotes_temporais_valorados_por_data or {}).values()),
        qtd_decisoes_temporais=len(resultado.decisoes_temporais_por_data or {}),
        qtd_pacotes_vencedores=sum(1 for p in (resultado.pacote_vencedor_por_data or {}).values() if p is not None),
        qtd_eventos_trajetoria=len(resultado.eventos_trajetoria_temporal or []),
        qtd_obrigacoes_cobertas=len(resultado.obrigacoes_cobertas_temporalmente or []),
        qtd_obrigacoes_bloqueadas=len(resultado.obrigacoes_bloqueadas_temporalmente or []),
        qtd_fontes_reservadas=len(resultado.fontes_reservadas_temporalmente or []),
        qtd_switchings_escolhidos=len(resultado.switchings_escolhidos_temporalmente or []),
        qtd_bloqueios_estruturais=len(resultado.bloqueios_estruturais or []),
        qtd_bloqueios_trajetoria=len(auditoria_trajetoria.bloqueios) if auditoria_trajetoria else 0,
        qtd_avisos_relevantes=sum(len(a) for a in auditorias_avisos),
    )


def _adicionar_bloqueio_final(
    bloqueios: list[BloqueioFinalEtapa5],
    codigo: str,
    detalhe: str,
    data_ref: date | None = None,
) -> None:
    bloqueios.append(BloqueioFinalEtapa5(codigo=codigo, detalhe=detalhe, data=data_ref))


def _detalhar_obrigacao_bloqueio_final(obrigacao: dict[str, Any]) -> str:
    obrigacao_id, _ = extrair_identificador_obrigacao_pacote(obrigacao)
    valor_obrigacao, _ = extrair_valor_obrigacao_referencial(obrigacao)
    return (
        f'obrigacao_id={obrigacao_id};'
        f'valor_referencial={float(valor_obrigacao or 0.0)};'
        f'referencia_obrigacao={obrigacao!r}'
    )


def auditar_consistencia_final_etapa5(
    resultado: ResultadoMotorTemporalConjunto,
) -> AuditoriaFinalResultadoMotorTemporalConjunto:
    bloqueios: list[BloqueioFinalEtapa5] = []
    avisos: list[str] = []
    datas_horizonte = set(resultado.horizonte_motor.datas_temporais)
    estado_diario = resultado.estado_diario_motor or {}
    pacotes_candidatos = resultado.pacotes_temporais_candidatos_por_data or {}
    decisoes = resultado.decisoes_temporais_por_data or {}
    vencedores = resultado.pacote_vencedor_por_data or {}
    trajetoria = resultado.trajetoria_temporal_interna_escolhida
    estados_internos = resultado.estado_temporal_interno_por_data or {}

    if not resultado.status_interface_etapa5.ok:
        _adicionar_bloqueio_final(bloqueios, 'interface_etapa5_invalida', 'auditoria de interface da Etapa 5 não está ok')

    if resultado.auditoria_motor_temporal_conjunto and not resultado.auditoria_motor_temporal_conjunto.ok:
        _adicionar_bloqueio_final(
            bloqueios,
            'motor_temporal_conjunto_nao_ok',
            'auditoria do motor temporal conjunto não está ok',
        )

    for bloqueio_estrutural in resultado.bloqueios_estruturais or []:
        data_bloqueio = None
        if isinstance(bloqueio_estrutural, dict):
            data_bloqueio = (
                bloqueio_estrutural.get('data')
                or bloqueio_estrutural.get('data_referencia')
                or bloqueio_estrutural.get('data_motor')
            )
        else:
            data_bloqueio = (
                getattr(bloqueio_estrutural, 'data', None)
                or getattr(bloqueio_estrutural, 'data_referencia', None)
                or getattr(bloqueio_estrutural, 'data_motor', None)
            )
        _adicionar_bloqueio_final(
            bloqueios,
            'bloqueio_estrutural_etapa5',
            f'bloqueio_estrutural={bloqueio_estrutural!r}',
            data_bloqueio,
        )

    if resultado.auditoria_integridade_resultado and resultado.auditoria_integridade_resultado.bloqueios:
        for bloqueio in resultado.auditoria_integridade_resultado.bloqueios:
            _adicionar_bloqueio_final(bloqueios, 'integridade_resultado_bloqueada', bloqueio)
    if resultado.auditoria_decisao_temporal_conjunto and not resultado.auditoria_decisao_temporal_conjunto.ok:
        for aviso in resultado.auditoria_decisao_temporal_conjunto.avisos:
            _adicionar_bloqueio_final(bloqueios, 'decisao_temporal_inconsistente', aviso)

    if resultado.auditoria_trajetoria_temporal_interna and not resultado.auditoria_trajetoria_temporal_interna.ok:
        _adicionar_bloqueio_final(
            bloqueios,
            'trajetoria_temporal_nao_ok',
            'auditoria da trajetória temporal interna não está ok',
        )

    if resultado.auditoria_trajetoria_temporal_interna and resultado.auditoria_trajetoria_temporal_interna.bloqueios:
        for bloqueio in resultado.auditoria_trajetoria_temporal_interna.bloqueios:
            _adicionar_bloqueio_final(bloqueios, 'trajetoria_temporal_inconsistente', bloqueio)

    for obrigacao_bloqueada in resultado.obrigacoes_bloqueadas_temporalmente or []:
        data_bloqueio = getattr(obrigacao_bloqueada, 'data', None)
        detalhe = (
            f'obrigacao_id={getattr(obrigacao_bloqueada, "obrigacao_id", None)};'
            f'motivo={getattr(obrigacao_bloqueada, "motivo_bloqueio_referencial", None)};'
            f'valor_referencial={float(getattr(obrigacao_bloqueada, "valor_obrigacao_referencial", 0.0) or 0.0)};'
            f'referencia_obrigacao={getattr(obrigacao_bloqueada, "referencia_obrigacao_temporal", None)!r}'
        )
        _adicionar_bloqueio_final(
            bloqueios,
            'obrigacao_bloqueada_na_trajetoria',
            detalhe,
            data_bloqueio,
        )
    if resultado.auditoria_schema_pacote_temporal_candidato and not resultado.auditoria_schema_pacote_temporal_candidato.ok:
        avisos.extend(f'pacotes_candidatos_aviso_nao_impeditivo:{a}' for a in resultado.auditoria_schema_pacote_temporal_candidato.avisos)

    for data_ref in resultado.horizonte_motor.datas_temporais:
        if data_ref not in estado_diario:
            _adicionar_bloqueio_final(bloqueios, 'data_sem_estado_diario', 'data do horizonte sem estado diário', data_ref)
        if data_ref not in pacotes_candidatos:
            _adicionar_bloqueio_final(bloqueios, 'data_sem_lista_pacotes_candidatos', 'data do horizonte sem lista de pacotes candidatos', data_ref)
        if data_ref not in decisoes:
            _adicionar_bloqueio_final(bloqueios, 'data_sem_decisao_temporal', 'data do horizonte sem decisão temporal', data_ref)
        if data_ref not in estados_internos:
            _adicionar_bloqueio_final(bloqueios, 'data_sem_estado_temporal_interno', 'data do horizonte sem estado interno da trajetória', data_ref)

        decisao = decisoes.get(data_ref)
        vencedor = vencedores.get(data_ref)
        estado_interno = estados_internos.get(data_ref)
        if decisao and decisao.pacote_vencedor_id and vencedor is None:
            _adicionar_bloqueio_final(bloqueios, 'decisao_sem_pacote_vencedor_materializado', 'decisão referencia pacote vencedor ausente', data_ref)
        obrigacoes_abertas = []
        if estado_diario.get(data_ref):
            obrigacoes_abertas = list(estado_diario[data_ref].obrigacoes.pagamentos_referenciados)
        if decisao and decisao.pacote_vencedor_id is None and obrigacoes_abertas:
            bloqueios_individuais_existentes = estado_interno.obrigacoes_bloqueadas if estado_interno else []
            chaves_bloqueadas_sem_vencedor = {
                _chave_obrigacao_referencial_auditoria(b.referencia_obrigacao_temporal)
                for b in bloqueios_individuais_existentes
                if b.motivo_bloqueio_referencial == 'sem_pacote_valido_para_obrigacao_temporal'
            }
            for obrigacao in obrigacoes_abertas:
                chave_obrigacao = _chave_obrigacao_referencial_auditoria(obrigacao)
                if chave_obrigacao not in chaves_bloqueadas_sem_vencedor:
                    _adicionar_bloqueio_final(
                        bloqueios,
                        'sem_pacote_vencedor_para_obrigacao_aberta',
                        _detalhar_obrigacao_bloqueio_final(obrigacao),
                        data_ref,
                    )
        elif decisao and decisao.pacote_vencedor_id is None and estado_interno and not estado_interno.obrigacoes_bloqueadas and estado_interno.status_referencial != 'bloqueado_sem_pacote_vencedor':
            _adicionar_bloqueio_final(bloqueios, 'decisao_sem_vencedor_sem_bloqueio_explicito', 'decisão sem vencedor não possui bloqueio explícito', data_ref)
        if vencedor and vencedor.data_referencia != data_ref:
            _adicionar_bloqueio_final(bloqueios, 'pacote_vencedor_data_divergente', vencedor.pacote_id, data_ref)
        if decisao and decisao.executa_pagamento:
            _adicionar_bloqueio_final(bloqueios, 'decisao_indica_execucao_pagamento', 'decisão não pode executar pagamento na Etapa 5', data_ref)
        if decisao and decisao.executa_switching:
            _adicionar_bloqueio_final(bloqueios, 'decisao_indica_execucao_switching', 'decisão não pode executar switching na Etapa 5', data_ref)
        if decisao and decisao.gera_ledger:
            _adicionar_bloqueio_final(bloqueios, 'decisao_indica_ledger', 'decisão não pode gerar ledger na Etapa 5', data_ref)

        if vencedor and vencedor.obrigacoes_referenciadas and estado_interno:
            chaves_obrigacoes = {_chave_obrigacao_referencial_auditoria(o) for o in vencedor.obrigacoes_referenciadas}
            chaves_cobertas = {_chave_obrigacao_referencial_auditoria(o.referencia_obrigacao_temporal) for o in estado_interno.obrigacoes_cobertas}
            chaves_bloqueadas = {_chave_obrigacao_referencial_auditoria(o.referencia_obrigacao_temporal) for o in estado_interno.obrigacoes_bloqueadas}
            if not chaves_obrigacoes.issubset(chaves_cobertas | chaves_bloqueadas):
                _adicionar_bloqueio_final(bloqueios, 'obrigacao_aberta_sem_tratamento_referencial', 'obrigação aberta sem cobertura ou bloqueio individual', data_ref)
            if estado_interno.status_referencial == 'bloqueado_referencialmente' and estado_interno.fontes_reservadas:
                _adicionar_bloqueio_final(bloqueios, 'reserva_persistida_em_pacote_bloqueado', 'pacote bloqueado reteve reservas referenciais', data_ref)

    if trajetoria is None:
        _adicionar_bloqueio_final(bloqueios, 'trajetoria_temporal_interna_ausente', 'trajetória temporal interna não foi anexada')
    elif set(trajetoria.estado_temporal_interno_por_data) != datas_horizonte:
        _adicionar_bloqueio_final(bloqueios, 'trajetoria_nao_cobre_horizonte', 'trajetória interna não cobre exatamente o horizonte')

    for reserva in resultado.fontes_reservadas_temporalmente or []:
        if reserva.valor_reservado_referencial > reserva.valor_disponivel_antes_referencial + 0.000001:
            _adicionar_bloqueio_final(bloqueios, 'reserva_acima_disponibilidade_referencial', reserva.fonte_id, reserva.data)
        if reserva.valor_disponivel_depois_referencial < -0.000001:
            _adicionar_bloqueio_final(bloqueios, 'saldo_referencial_negativo_apos_reserva', reserva.fonte_id, reserva.data)

    for switching in resultado.switchings_escolhidos_temporalmente or []:
        if switching.status_referencial != 'escolhido_internamente_nao_executado':
            _adicionar_bloqueio_final(bloqueios, 'switching_nao_referencial', str(switching.switching_id), switching.data)

    for evento in resultado.eventos_trajetoria_temporal or []:
        texto = f'{evento.tipo_evento_interno} {evento.status_referencial}'.lower()
        if 'ledger' in texto:
            _adicionar_bloqueio_final(bloqueios, 'evento_interno_indica_ledger', str(evento.pacote_id), evento.data)
        indica_pagamento_oficial = 'pagamento_oficial' in texto and 'sem_pagamento_oficial' not in texto
        indica_execucao_oficial = 'executado_oficial' in texto and 'nao_executado_oficial' not in texto
        if indica_pagamento_oficial or indica_execucao_oficial or 'liquidado_oficial' in texto:
            _adicionar_bloqueio_final(bloqueios, 'evento_interno_indica_execucao_oficial', str(evento.pacote_id), evento.data)

    avisos.extend([
        'sem_alteracao_dados_confirmado_por_escopo_do_fechamento',
        'sem_console_xlsx_saida_canonica_como_fonte_confirmado_por_escopo_do_fechamento',
        'etapa6_deve_consumir_exclusivamente_resultado_motor_temporal_conjunto',
    ])
    resumo = {
        'qtd_datas_horizonte': len(datas_horizonte),
        'qtd_bloqueios_finais': len(bloqueios),
        'qtd_avisos_finais': len(avisos),
        'sem_ledger': True,
        'sem_execucao_pagamento': True,
        'sem_execucao_switching': True,
        'sem_console_xlsx': True,
        'sem_saida_canonica_final': True,
        'sem_alteracao_dados': True,
    }
    return AuditoriaFinalResultadoMotorTemporalConjunto(
        ok=not bloqueios,
        pronto_para_etapa6=not bloqueios,
        bloqueios=bloqueios,
        avisos=avisos,
        resumo=resumo,
    )


def montar_contrato_consumo_etapa6(resultado: ResultadoMotorTemporalConjunto) -> ContratoConsumoEtapa6:
    return ContratoConsumoEtapa6(
        artefato_exclusivo_consumo='ResultadoMotorTemporalConjunto',
        blocos_consumo=[
            'data_referencia',
            'horizonte_motor',
            'decisoes_temporais_por_data',
            'pacote_vencedor_por_data',
            'trajetoria_temporal_interna_escolhida',
            'eventos_trajetoria_temporal',
            'estado_temporal_interno_por_data',
            'fontes_reservadas_temporalmente',
            'obrigacoes_cobertas_temporalmente',
            'obrigacoes_bloqueadas_temporalmente',
            'switchings_escolhidos_temporalmente',
            'auditoria_final_etapa5',
            'metadados',
        ],
        fontes_proibidas=[
            'console',
            'XLSX',
            'saida_canonica',
            'logs',
            'scripts_diagnosticos',
            'dados_brutos_como_fonte_normativa_alternativa',
        ],
        observacoes=[
            'consumo_exclusivo_pela_etapa6',
            'sem_ledger_oficial',
            'sem_execucao_oficial_pagamento_ou_switching',
        ],
    )


def fechar_resultado_motor_temporal_conjunto(
    resultado: ResultadoMotorTemporalConjunto,
) -> ResultadoMotorTemporalConjunto:
    resultado.sumario_final_etapa5 = montar_sumario_final_etapa5(resultado)
    resultado.auditoria_final_etapa5 = auditar_consistencia_final_etapa5(resultado)
    resultado.contrato_consumo_etapa6 = montar_contrato_consumo_etapa6(resultado)
    criterios = [
        'interface_etapa5_ok',
        'integridade_resultado_sem_bloqueios_criticos',
        'pacotes_candidatos_presentes_por_data',
        'decisoes_temporais_consistentes',
        'trajetoria_interna_sem_bloqueios_criticos',
        'horizonte_com_decisao_e_estado_interno',
        'obrigacoes_abertas_cobertas_ou_bloqueadas_referencialmente',
        'sem_ledger',
        'sem_execucao_pagamento',
        'sem_execucao_switching',
        'sem_dependencia_console_xlsx_saida_logs_diagnosticos',
    ]
    criterios_bloqueados = [b.codigo for b in resultado.auditoria_final_etapa5.bloqueios]
    criterios_atendidos = criterios if not criterios_bloqueados else [
        'sem_ledger',
        'sem_execucao_pagamento',
        'sem_execucao_switching',
        'sem_dependencia_console_xlsx_saida_logs_diagnosticos',
    ]
    resultado.pronto_para_etapa6 = resultado.auditoria_final_etapa5.pronto_para_etapa6
    resultado.fechamento_funcional_etapa5 = FechamentoFuncionalEtapa5(
        etapa5_fechada_funcionalmente=True,
        pronto_para_etapa6=resultado.pronto_para_etapa6,
        criterios_fechamento=criterios,
        criterios_atendidos=criterios_atendidos,
        criterios_bloqueados=criterios_bloqueados,
        limites_preservados=[
            'sem_ledger',
            'sem_execucao_pagamento',
            'sem_execucao_switching',
            'sem_console_xlsx',
            'sem_saida_canonica_final',
            'sem_alteracao_dados',
        ],
    )
    resultado.metadados.update({
        'etapa': '5',
        'artefato': 'ResultadoMotorTemporalConjunto',
        'versao_contrato': 'MACRO-ETAPA5-D',
        'etapa5_fechada_funcionalmente': True,
        'pronto_para_etapa6': resultado.pronto_para_etapa6,
        'consumo_exclusivo_pela_etapa6': True,
        'sem_ledger': True,
        'sem_execucao_pagamento': True,
        'sem_execucao_switching': True,
        'sem_console_xlsx': True,
        'sem_saida_canonica_final': True,
        'sem_alteracao_dados': True,
    })
    resultado.sumario_final_etapa5 = montar_sumario_final_etapa5(resultado)
    return resultado

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
    schema_pacote = montar_schema_pacote_temporal_candidato()

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
            'versao_contrato': 'MACRO-ETAPA5-C',
            'com_valoracao_pacotes_temporais': True,
            'com_selecao_pacote_temporal': True,
            'com_trajetoria_temporal_interna_escolhida': True,
            'sem_execucao_pagamento': True,
            'sem_execucao_switching': True,
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
        schema_pacote_temporal_candidato=schema_pacote,
        pacotes_temporais_candidatos_por_data=inicializar_pacotes_temporais_candidatos_por_data(dias_motor),
    )
    resultado.auditoria_motor_temporal_conjunto = montar_auditoria_motor_temporal_conjunto(resultado)
    resultado.pacotes_temporais_candidatos_por_data = gerar_pacotes_temporais_candidatos(resultado)
    resultado.auditoria_schema_pacote_temporal_candidato = auditar_pacotes_temporais_candidatos(resultado)
    resultado.pacotes_temporais_valorados_por_data = valorar_pacotes_temporais_candidatos(resultado)
    (
        resultado.decisoes_temporais_por_data,
        resultado.pacote_vencedor_por_data,
        resultado.pacotes_descartados_por_data,
    ) = selecionar_pacotes_temporais_vencedores(
        resultado,
        resultado.pacotes_temporais_valorados_por_data,
    )
    resultado.auditoria_decisao_temporal_conjunto = auditar_decisoes_temporais(resultado)
    resultado.trajetoria_temporal_interna_escolhida = aplicar_trajetoria_temporal_interna(resultado)
    resultado.eventos_trajetoria_temporal = resultado.trajetoria_temporal_interna_escolhida.eventos_trajetoria_temporal
    resultado.estado_temporal_interno_por_data = resultado.trajetoria_temporal_interna_escolhida.estado_temporal_interno_por_data
    resultado.fontes_reservadas_temporalmente = resultado.trajetoria_temporal_interna_escolhida.fontes_reservadas_temporalmente
    resultado.obrigacoes_cobertas_temporalmente = resultado.trajetoria_temporal_interna_escolhida.obrigacoes_cobertas_temporalmente
    resultado.obrigacoes_bloqueadas_temporalmente = resultado.trajetoria_temporal_interna_escolhida.obrigacoes_bloqueadas_temporalmente
    resultado.switchings_escolhidos_temporalmente = resultado.trajetoria_temporal_interna_escolhida.switchings_escolhidos_temporalmente
    resultado.auditoria_trajetoria_temporal_interna = auditar_trajetoria_temporal_interna(resultado)
    resultado.auditoria_integridade_resultado = auditar_integridade_resultado_motor_temporal_conjunto(resultado)
    resultado = fechar_resultado_motor_temporal_conjunto(resultado)
    return resultado


__all__ = [
    'AuditoriaConsumoEtapa5',
    'AuditoriaDecisaoTemporalConjunto',
    'AuditoriaFinalResultadoMotorTemporalConjunto',
    'AuditoriaIntegridadeResultadoMotorTemporalConjunto',
    'AuditoriaMotorTemporalConjunto',
    'AuditoriaTrajetoriaTemporalInterna',
    'AuditoriaSchemaPacoteTemporalCandidato',
    'BloqueioFinalEtapa5',
    'BloqueioEstruturalEtapa5',
    'CoberturaEstruturalReferencialDia',
    'ContratoConsumoEtapa6',
    'DiaMotorTemporal',
    'EstadoDiarioMotorTemporal',
    'EstadoSimulacaoMotorTemporal',
    'EstadoTemporalInternoDia',
    'EventoTrajetoriaTemporalInterna',
    'EventosTemporaisBase',
    'FechamentoFuncionalEtapa5',
    'FonteCandidataPacoteTemporal',
    'FonteReservadaTemporalmente',
    'FontesTemporaisReferenciadasDia',
    'HorizonteMotorTemporal',
    'IndiceTemporalMotor',
    'JustificativaDecisaoTemporal',
    'ObrigacaoBloqueadaTemporalmente',
    'ObrigacaoCobertaTemporalmente',
    'ObrigacoesTemporaisDia',
    'PacoteTemporalCandidato',
    'PacoteTemporalDescartado',
    'PacoteTemporalValorado',
    'ParametrosEtapa5',
    'RecebidosTemporaisDia',
    'ResultadoMotorTemporalConjunto',
    'SchemaPacoteTemporalCandidato',
    'SaldoReferencialFonteTemporal',
    'StatusInterfaceEtapa5',
    'SumarioFinalEtapa5',
    'SwitchingCandidatoPacoteTemporal',
    'SwitchingEscolhidoTemporalmente',
    'SwitchingsRealizadosDia',
    'TrajetoriaTemporalInternaEscolhida',
    'TransicaoCandidataPacoteTemporal',
    'ValoracaoPacoteTemporal',
    'aplicar_pacote_temporal_vencedor_dia',
    'aplicar_trajetoria_temporal_interna',
    'auditar_consistencia_final_etapa5',
    'auditar_decisoes_temporais',
    'auditar_integridade_resultado_motor_temporal_conjunto',
    'auditar_trajetoria_temporal_interna',
    'construir_resultado_motor_temporal_conjunto',
    'extrair_identificador_fonte_pacote',
    'extrair_identificador_obrigacao_pacote',
    'extrair_valor_reservavel_fonte_pacote',
    'fechar_resultado_motor_temporal_conjunto',
    'deduplicar_fontes_temporais_referenciadas',
    'definir_horizonte_motor_temporal',
    'inicializar_estado_simulacao_motor',
    'inicializar_pacotes_temporais_candidatos_por_data',
    'montar_auditoria_consumo_etapa5',
    'montar_auditoria_motor_temporal_conjunto',
    'montar_auditoria_schema_pacote_temporal_candidato',
    'montar_contrato_consumo_etapa6',
    'montar_dias_motor_temporal',
    'montar_estado_diario_motor_temporal',
    'montar_eventos_temporais_base',
    'montar_fontes_temporais_referenciadas_dia',
    'montar_indice_temporal_motor',
    'montar_obrigacoes_temporais_dia',
    'montar_recebidos_temporais_dia',
    'montar_schema_pacote_temporal_candidato',
    'montar_sumario_final_etapa5',
    'montar_switchings_realizados_dia',
    'selecionar_pacote_temporal_vencedor_dia',
    'selecionar_pacotes_temporais_vencedores',
    'sintetizar_cobertura_estrutural_referencial_dia',
    'valorar_pacote_temporal_candidato',
    'valorar_pacotes_temporais_candidatos',
    'verificar_interface_estado_temporal_inicial',
]
