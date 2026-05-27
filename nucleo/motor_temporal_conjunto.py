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
    indices = list(indice.pagamentos_por_data.get(data_motor, []))
    pagamentos = []
    for i in indices:
        pagamento = estado.pagamentos_temporais[i]
        if pagamento.get('pago') is True:
            continue
        if pagamento.get('fonte_a_decidir') is False:
            continue
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
    fontes_disponiveis = [f for f in estado_dia.fontes_referenciadas.fontes_referenciadas if _fonte_disponivel_referencialmente(f)]
    for idx, fonte in enumerate(fontes_disponiveis, start=1):
        pacote = _montar_pacote_base(estado_dia.data, 'pagamento_fonte_unica', str(idx))
        pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
        fonte_candidata = montar_fonte_candidata_pacote_temporal(fonte)
        pacote.fontes_candidatas = [fonte_candidata]
        pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
        valor_fonte, _ = extrair_valor_fonte_referencial(fonte)
        pacote.valor_cobertura_referencial = valor_fonte
        pacote.status_factibilidade = 'factivel_referencialmente' if valor_fonte is not None else 'nao_avaliado'
        pacotes.append(pacote)
    return pacotes


def gerar_pacote_pagamento_combinacao_fontes(estado_dia: EstadoDiarioMotorTemporal) -> PacoteTemporalCandidato | None:
    fontes_disponiveis = [f for f in estado_dia.fontes_referenciadas.fontes_referenciadas if _fonte_disponivel_referencialmente(f)]
    if not estado_dia.obrigacoes.pagamentos_referenciados or len(fontes_disponiveis) < 2:
        return None
    pacote = _montar_pacote_base(estado_dia.data, 'pagamento_combinacao_fontes', '1')
    pacote.obrigacoes_referenciadas = list(estado_dia.obrigacoes.pagamentos_referenciados)
    pacote.fontes_candidatas = [
        montar_fonte_candidata_pacote_temporal(fonte) for fonte in fontes_disponiveis
    ]
    pacote.valor_obrigacoes = sum(extrair_valor_obrigacao_referencial(o)[0] or 0.0 for o in pacote.obrigacoes_referenciadas)
    pacote.valor_cobertura_referencial = sum(extrair_valor_fonte_referencial(f)[0] or 0.0 for f in fontes_disponiveis)
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
    if valor_switchings > 0.0:
        pacote.status_factibilidade = 'factivel_referencialmente'
    else:
        pacote.status_factibilidade = 'bloqueado_estruturalmente'
        pacote.motivos_bloqueio.append('switching_sem_cobertura_referencial_positiva')
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
    for data_ref in resultado.horizonte_motor.datas_temporais:
        decisao, lista_descartados, vencedor = selecionar_pacote_temporal_vencedor_dia(data_ref, pacotes_valorados.get(data_ref, []))
        decisoes[data_ref] = decisao
        vencedores[data_ref] = vencedor
        descartados[data_ref] = lista_descartados
    return decisoes, vencedores, descartados


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
            'versao_contrato': 'ME-ETAPA5-A',
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
    resultado.auditoria_integridade_resultado = auditar_integridade_resultado_motor_temporal_conjunto(resultado)
    return resultado


__all__ = [
    'AuditoriaConsumoEtapa5',
    'AuditoriaDecisaoTemporalConjunto',
    'AuditoriaIntegridadeResultadoMotorTemporalConjunto',
    'AuditoriaMotorTemporalConjunto',
    'AuditoriaSchemaPacoteTemporalCandidato',
    'BloqueioEstruturalEtapa5',
    'CoberturaEstruturalReferencialDia',
    'DiaMotorTemporal',
    'EstadoDiarioMotorTemporal',
    'EstadoSimulacaoMotorTemporal',
    'EventosTemporaisBase',
    'FonteCandidataPacoteTemporal',
    'FontesTemporaisReferenciadasDia',
    'HorizonteMotorTemporal',
    'IndiceTemporalMotor',
    'JustificativaDecisaoTemporal',
    'ObrigacoesTemporaisDia',
    'PacoteTemporalCandidato',
    'PacoteTemporalDescartado',
    'PacoteTemporalValorado',
    'ParametrosEtapa5',
    'RecebidosTemporaisDia',
    'ResultadoMotorTemporalConjunto',
    'SchemaPacoteTemporalCandidato',
    'StatusInterfaceEtapa5',
    'SwitchingCandidatoPacoteTemporal',
    'SwitchingsRealizadosDia',
    'TransicaoCandidataPacoteTemporal',
    'ValoracaoPacoteTemporal',
    'auditar_decisoes_temporais',
    'auditar_integridade_resultado_motor_temporal_conjunto',
    'construir_resultado_motor_temporal_conjunto',
    'definir_horizonte_motor_temporal',
    'inicializar_estado_simulacao_motor',
    'inicializar_pacotes_temporais_candidatos_por_data',
    'montar_auditoria_consumo_etapa5',
    'montar_auditoria_motor_temporal_conjunto',
    'montar_auditoria_schema_pacote_temporal_candidato',
    'montar_dias_motor_temporal',
    'montar_estado_diario_motor_temporal',
    'montar_eventos_temporais_base',
    'montar_fontes_temporais_referenciadas_dia',
    'montar_indice_temporal_motor',
    'montar_obrigacoes_temporais_dia',
    'montar_recebidos_temporais_dia',
    'montar_schema_pacote_temporal_candidato',
    'montar_switchings_realizados_dia',
    'selecionar_pacote_temporal_vencedor_dia',
    'selecionar_pacotes_temporais_vencedores',
    'sintetizar_cobertura_estrutural_referencial_dia',
    'valorar_pacote_temporal_candidato',
    'valorar_pacotes_temporais_candidatos',
    'verificar_interface_estado_temporal_inicial',
]
