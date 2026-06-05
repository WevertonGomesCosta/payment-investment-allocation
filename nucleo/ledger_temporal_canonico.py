from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date
from typing import Any

from nucleo.motor_temporal_conjunto import ResultadoMotorTemporalConjunto


@dataclass(slots=True)
class ParametrosLedgerTemporal:
    versao_schema: str = 'MACRO-ETAPA6-FULL'
    preservar_referencias_originais: bool = True
    origem_exclusiva: str = 'ResultadoMotorTemporalConjunto'


@dataclass(slots=True)
class EventoLedgerTemporal:
    data: date | None
    tipo: str
    pacote_id: str | None = None
    tipo_pacote: str | None = None
    status: str | None = None
    decisao_status: str | None = None
    origem_evento_etapa5: str | None = None
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LancamentoObrigacaoLedger:
    data: date | None
    tipo: str
    obrigacao_id: str | None
    pacote_id: str | None
    valor_obrigacao_referencial: float | None = None
    valor_coberto_referencial: float | None = None
    fontes_referenciadas: list[str] = field(default_factory=list)
    status: str = 'referencial_sem_execucao_bancaria'
    motivo: str | None = None
    referencia_original: dict[str, Any] = field(default_factory=dict)
    metadados: dict[str, Any] = field(default_factory=dict)
    detalhes_fontes_resgate: list[dict[str, Any]] = field(default_factory=list)
    saldo_antes_fonte: float | str | None = None
    valor_bruto_resgate: float | str | None = None
    imposto_resgate: float | str | None = None
    valor_liquido_resgate: float | str | None = None
    saldo_remanescente_fonte: float | str | None = None
    status_saldo_antes_fonte: str | None = None
    status_valor_bruto_resgate: str | None = None
    status_imposto_resgate: str | None = None
    status_valor_liquido_resgate: str | None = None
    status_saldo_remanescente_fonte: str | None = None


@dataclass(slots=True)
class LancamentoFonteLedger:
    data: date | None
    tipo: str
    fonte_id: str | None
    pacote_id: str | None
    obrigacao_id: str | None = None
    valor_referencial: float | None = None
    valor_disponivel_antes_referencial: float | None = None
    valor_disponivel_depois_referencial: float | None = None
    tipo_fonte: str | None = None
    origem_fonte: str | None = None
    status: str = 'uso_referencial_sem_alteracao_real'
    referencia_original: dict[str, Any] = field(default_factory=dict)
    metadados: dict[str, Any] = field(default_factory=dict)
    fonte_id_tecnico: str | None = None
    lote_id_operacional: str | None = None
    saldo_antes_fonte: float | str | None = None
    valor_bruto_resgate: float | str | None = None
    imposto_resgate: float | str | None = None
    valor_liquido_resgate: float | str | None = None
    saldo_remanescente_fonte: float | str | None = None
    status_saldo_antes_fonte: str | None = None
    status_valor_bruto_resgate: str | None = None
    status_imposto_resgate: str | None = None
    status_valor_liquido_resgate: str | None = None
    status_saldo_remanescente_fonte: str | None = None


@dataclass(slots=True)
class LancamentoReservaLedger:
    data: date | None
    tipo: str
    fonte_id: str | None
    pacote_id: str | None
    valor_reservado_referencial: float | None = None
    obrigacao_id: str | None = None
    valor_disponivel_antes_referencial: float | None = None
    valor_disponivel_depois_referencial: float | None = None
    tipo_fonte: str | None = None
    origem_fonte: str | None = None
    status: str = 'reserva_referencial_sem_bloqueio_bancario_real'
    referencia_original: dict[str, Any] = field(default_factory=dict)
    metadados: dict[str, Any] = field(default_factory=dict)
    fonte_id_tecnico: str | None = None
    lote_id_operacional: str | None = None
    saldo_antes_fonte: float | str | None = None
    valor_bruto_resgate: float | str | None = None
    imposto_resgate: float | str | None = None
    valor_liquido_resgate: float | str | None = None
    saldo_remanescente_fonte: float | str | None = None
    status_saldo_antes_fonte: str | None = None
    status_valor_bruto_resgate: str | None = None
    status_imposto_resgate: str | None = None
    status_valor_liquido_resgate: str | None = None
    status_saldo_remanescente_fonte: str | None = None


@dataclass(slots=True)
class LancamentoSwitchingLedger:
    data: date | None
    tipo: str
    switching_id: str | None
    pacote_id: str | None
    lote_origem_id: str | None
    lote_destino_id: str | None
    tipo_switching: str | None = None
    valor_liquido_migrado_referencial: float | None = None
    status: str = 'switching_referencial_sem_execucao_real'
    referencia_original: dict[str, Any] = field(default_factory=dict)
    metadados: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LancamentoBloqueioLedger:
    data: date | None
    tipo: str
    codigo: str
    motivo: str
    pacote_id: str | None = None
    obrigacao_id: str | None = None
    severidade: str = 'bloqueio'
    referencia_original: dict[str, Any] = field(default_factory=dict)
    metadados: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SaldoLedgerTemporal:
    data: date | None
    fonte_id: str | None
    valor_disponivel_referencial: float | None
    valor_reservado_acumulado_referencial: float | None
    pacote_id: str | None = None
    status: str = 'saldo_referencial_sem_alteracao_real'
    referencia_original: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaLedgerTemporalCanonico:
    ok: bool
    bloqueios: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    resumo: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LedgerTemporalCanonico:
    data_referencia: date | None
    horizonte: list[date]
    eventos: list[EventoLedgerTemporal] = field(default_factory=list)
    lancamentos_por_data: dict[date, list[dict[str, Any]]] = field(default_factory=dict)
    obrigacoes_cobertas: list[LancamentoObrigacaoLedger] = field(default_factory=list)
    obrigacoes_bloqueadas: list[LancamentoObrigacaoLedger] = field(default_factory=list)
    pagamentos_historicos_realizados: list[dict[str, Any]] = field(default_factory=list)
    fontes_utilizadas: list[LancamentoFonteLedger] = field(default_factory=list)
    fontes_reservadas: list[LancamentoReservaLedger] = field(default_factory=list)
    switchings_escolhidos: list[LancamentoSwitchingLedger] = field(default_factory=list)
    switchings_realizados_operacionais: list[dict[str, Any]] = field(default_factory=list)
    lotes_pos_switching_materializados: list[dict[str, Any]] = field(default_factory=list)
    lotes_patrimoniais: list[dict[str, Any]] = field(default_factory=list)
    auditoria_lotes_patrimoniais: dict[str, Any] = field(default_factory=dict)
    saldos_referenciais_por_data: dict[date, list[SaldoLedgerTemporal]] = field(default_factory=dict)
    destinos_sobras_recebidos: list[dict[str, Any]] = field(default_factory=list)
    lotes_futuros_materializados: list[dict[str, Any]] = field(default_factory=list)
    bloqueios: list[LancamentoBloqueioLedger] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    auditoria: AuditoriaLedgerTemporalCanonico | None = None
    metadados: dict[str, Any] = field(default_factory=dict)
    pronto_para_etapa_posterior: bool = False


_CAMPOS_ESPERADOS_RESULTADO = [
    'data_referencia',
    'horizonte_motor',
    'decisoes_temporais_por_data',
    'pacote_vencedor_por_data',
    'eventos_trajetoria_temporal',
    'estado_temporal_interno_por_data',
    'fontes_reservadas_temporalmente',
    'obrigacoes_cobertas_temporalmente',
    'obrigacoes_bloqueadas_temporalmente',
    'switchings_escolhidos_temporalmente',
    'eventos_temporais_base',
    'destinos_sobras_recebidos_temporais',
    'lotes_futuros_materializados',
    'lotes_patrimoniais_temporais',
    'auditoria_trajetoria_temporal_interna',
    'auditoria_final_etapa5',
    'fechamento_funcional_etapa5',
    'contrato_consumo_etapa6',
    'pronto_para_etapa6',
    'metadados',
]

_TIPOS_EXECUCAO_REAL_PROIBIDOS = {'execucao_bancaria_real', 'pagamento_bancario_real', 'switching_real'}


def _valor(objeto: Any, campo: str, padrao: Any = None) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(campo, padrao)
    return getattr(objeto, campo, padrao)


def _lista(valor: Any) -> list[Any]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return valor
    if isinstance(valor, tuple):
        return list(valor)
    return [valor]


def _dict_referencia(valor: Any) -> dict[str, Any]:
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return dict(valor)
    if is_dataclass(valor):
        return asdict(valor)
    return {'valor': valor}


def _horizonte(resultado: ResultadoMotorTemporalConjunto, avisos: list[str]) -> list[date]:
    horizonte_motor = _valor(resultado, 'horizonte_motor')
    datas = _valor(horizonte_motor, 'datas_temporais')
    if datas is None:
        datas = _valor(resultado, 'janela_temporal_motor')
    if datas is None:
        avisos.append('campo_horizonte_temporal_ausente_ledger_construido_com_horizonte_vazio')
        return []
    return list(datas)


def _registrar_lancamento(ledger: LedgerTemporalCanonico, data_lancamento: date | None, lancamento: Any) -> None:
    chave = data_lancamento or ledger.data_referencia
    if chave is None:
        ledger.avisos.append('lancamento_sem_data_nao_indexado_em_lancamentos_por_data')
        return
    ledger.lancamentos_por_data.setdefault(chave, []).append(_dict_referencia(lancamento))


def _decisao_por_data(resultado: ResultadoMotorTemporalConjunto, data_ref: date | None) -> Any:
    decisoes = _valor(resultado, 'decisoes_temporais_por_data') or {}
    if data_ref in decisoes:
        return decisoes[data_ref]
    return None


def _evento_para_ledger(evento: Any, resultado: ResultadoMotorTemporalConjunto) -> EventoLedgerTemporal:
    data_evento = _valor(evento, 'data')
    decisao = _decisao_por_data(resultado, data_evento)
    detalhes = _valor(evento, 'detalhes', {}) or {}
    return EventoLedgerTemporal(
        data=data_evento,
        tipo=_valor(evento, 'tipo_evento_interno', 'evento_temporal_etapa5'),
        pacote_id=_valor(evento, 'pacote_id'),
        tipo_pacote=_valor(evento, 'tipo_pacote'),
        status=_valor(evento, 'status_referencial'),
        decisao_status=_valor(decisao, 'status_decisao') if decisao else None,
        origem_evento_etapa5='eventos_trajetoria_temporal',
        referencias={'evento_etapa5': _dict_referencia(evento), 'detalhes': _dict_referencia(detalhes)},
    )


def _reserva_para_lancamentos(reserva: Any) -> tuple[LancamentoReservaLedger, LancamentoFonteLedger]:
    data_reserva = _valor(reserva, 'data')
    fonte_id = _valor(reserva, 'fonte_id')
    pacote_id = _valor(reserva, 'pacote_id')
    referencia = _dict_referencia(_valor(reserva, 'referencia_estado_temporal', {}))
    fonte_id_tecnico = _valor(reserva, 'fonte_id_tecnico') or fonte_id
    lote_id_operacional = (
        _valor(reserva, 'lote_id_operacional')
        or referencia.get('lote_id_operacional')
        or referencia.get('lote_id_operacional_previsto')
        or referencia.get('lote_id')
        or referencia.get('Lote (ID)')
        or referencia.get('lote')
    )
    lote_id_operacional_ausente = not bool(lote_id_operacional)
    reserva_ledger = LancamentoReservaLedger(
        data=data_reserva,
        tipo='reserva_fonte_referencial',
        fonte_id=fonte_id,
        pacote_id=pacote_id,
        valor_reservado_referencial=_valor(reserva, 'valor_reservado_referencial'),
        obrigacao_id=_valor(reserva, 'obrigacao_id'),
        valor_disponivel_antes_referencial=_valor(reserva, 'valor_disponivel_antes_referencial'),
        valor_disponivel_depois_referencial=_valor(reserva, 'valor_disponivel_depois_referencial'),
        tipo_fonte=_valor(reserva, 'tipo_fonte'),
        origem_fonte=_valor(reserva, 'origem_fonte'),
        referencia_original=referencia,
        metadados={
            'origem': 'fontes_reservadas_temporalmente',
            'fonte_id_tecnico': fonte_id_tecnico,
            'lote_id_operacional': lote_id_operacional,
            'lote_id_operacional_ausente': lote_id_operacional_ausente,
        },
        fonte_id_tecnico=fonte_id_tecnico,
        lote_id_operacional=lote_id_operacional,
        saldo_antes_fonte=_valor(reserva, 'saldo_antes_fonte'),
        valor_bruto_resgate=_valor(reserva, 'valor_bruto_resgate'),
        imposto_resgate=_valor(reserva, 'imposto_resgate'),
        valor_liquido_resgate=_valor(reserva, 'valor_liquido_resgate'),
        saldo_remanescente_fonte=_valor(reserva, 'saldo_remanescente_fonte'),
        status_saldo_antes_fonte=_valor(reserva, 'status_saldo_antes_fonte'),
        status_valor_bruto_resgate=_valor(reserva, 'status_valor_bruto_resgate'),
        status_imposto_resgate=_valor(reserva, 'status_imposto_resgate'),
        status_valor_liquido_resgate=_valor(reserva, 'status_valor_liquido_resgate'),
        status_saldo_remanescente_fonte=_valor(reserva, 'status_saldo_remanescente_fonte'),
    )
    fonte_ledger = LancamentoFonteLedger(
        data=data_reserva,
        tipo='uso_fonte_referencial_materializado_por_reserva',
        fonte_id=fonte_id,
        pacote_id=pacote_id,
        obrigacao_id=_valor(reserva, 'obrigacao_id'),
        valor_referencial=_valor(reserva, 'valor_reservado_referencial'),
        valor_disponivel_antes_referencial=_valor(reserva, 'valor_disponivel_antes_referencial'),
        valor_disponivel_depois_referencial=_valor(reserva, 'valor_disponivel_depois_referencial'),
        tipo_fonte=_valor(reserva, 'tipo_fonte'),
        origem_fonte=_valor(reserva, 'origem_fonte'),
        referencia_original=referencia,
        metadados={
            'origem': 'fontes_reservadas_temporalmente',
            'fonte_id_tecnico': fonte_id_tecnico,
            'lote_id_operacional': lote_id_operacional,
            'lote_id_operacional_ausente': lote_id_operacional_ausente,
        },
        fonte_id_tecnico=fonte_id_tecnico,
        lote_id_operacional=lote_id_operacional,
        saldo_antes_fonte=_valor(reserva, 'saldo_antes_fonte'),
        valor_bruto_resgate=_valor(reserva, 'valor_bruto_resgate'),
        imposto_resgate=_valor(reserva, 'imposto_resgate'),
        valor_liquido_resgate=_valor(reserva, 'valor_liquido_resgate'),
        saldo_remanescente_fonte=_valor(reserva, 'saldo_remanescente_fonte'),
        status_saldo_antes_fonte=_valor(reserva, 'status_saldo_antes_fonte'),
        status_valor_bruto_resgate=_valor(reserva, 'status_valor_bruto_resgate'),
        status_imposto_resgate=_valor(reserva, 'status_imposto_resgate'),
        status_valor_liquido_resgate=_valor(reserva, 'status_valor_liquido_resgate'),
        status_saldo_remanescente_fonte=_valor(reserva, 'status_saldo_remanescente_fonte'),
    )
    return reserva_ledger, fonte_ledger


def _obrigacao_coberta_para_ledger(obrigacao: Any) -> LancamentoObrigacaoLedger:
    return LancamentoObrigacaoLedger(
        data=_valor(obrigacao, 'data'),
        tipo='obrigacao_coberta_referencialmente',
        obrigacao_id=_valor(obrigacao, 'obrigacao_id'),
        pacote_id=_valor(obrigacao, 'pacote_id'),
        valor_obrigacao_referencial=_valor(obrigacao, 'valor_obrigacao_referencial'),
        valor_coberto_referencial=_valor(obrigacao, 'valor_coberto_referencial'),
        fontes_referenciadas=list(_valor(obrigacao, 'fontes_reservadas_ids', []) or []),
        status='coberta_referencialmente_sem_pagamento_bancario_real',
        referencia_original=_dict_referencia(_valor(obrigacao, 'referencia_obrigacao_temporal', {})),
        metadados={'origem': 'obrigacoes_cobertas_temporalmente'},
        detalhes_fontes_resgate=list(_valor(obrigacao, 'detalhes_fontes_resgate', []) or []),
        saldo_antes_fonte=_valor(obrigacao, 'saldo_antes_fonte'),
        valor_bruto_resgate=_valor(obrigacao, 'valor_bruto_resgate'),
        imposto_resgate=_valor(obrigacao, 'imposto_resgate'),
        valor_liquido_resgate=_valor(obrigacao, 'valor_liquido_resgate'),
        saldo_remanescente_fonte=_valor(obrigacao, 'saldo_remanescente_fonte'),
        status_saldo_antes_fonte=_valor(obrigacao, 'status_saldo_antes_fonte'),
        status_valor_bruto_resgate=_valor(obrigacao, 'status_valor_bruto_resgate'),
        status_imposto_resgate=_valor(obrigacao, 'status_imposto_resgate'),
        status_valor_liquido_resgate=_valor(obrigacao, 'status_valor_liquido_resgate'),
        status_saldo_remanescente_fonte=_valor(obrigacao, 'status_saldo_remanescente_fonte'),
    )


def _obrigacao_bloqueada_para_ledger(obrigacao: Any, avisos: list[str]) -> LancamentoObrigacaoLedger:
    motivo = _valor(obrigacao, 'motivo_bloqueio_referencial')
    if not motivo:
        motivo = 'motivo_bloqueio_ausente_no_resultado_motor_temporal_conjunto'
        avisos.append('obrigacao_bloqueada_sem_motivo_explicito_na_etapa5')
    return LancamentoObrigacaoLedger(
        data=_valor(obrigacao, 'data'),
        tipo='obrigacao_bloqueada_referencialmente',
        obrigacao_id=_valor(obrigacao, 'obrigacao_id'),
        pacote_id=_valor(obrigacao, 'pacote_id'),
        valor_obrigacao_referencial=_valor(obrigacao, 'valor_obrigacao_referencial'),
        valor_coberto_referencial=_valor(obrigacao, 'valor_cobertura_referencial'),
        status='bloqueada_referencialmente_sem_execucao',
        motivo=motivo,
        referencia_original=_dict_referencia(_valor(obrigacao, 'referencia_obrigacao_temporal', {})),
        metadados={'origem': 'obrigacoes_bloqueadas_temporalmente'},
    )



def _pagamento_historico_realizado_para_ledger(pagamento: Any) -> dict[str, Any]:
    snapshot = _dict_referencia(pagamento)
    snapshot['origem'] = 'ResultadoMotorTemporalConjunto.eventos_temporais_base.pagamentos'
    snapshot['status_observavel'] = 'realizada_oficial'
    return snapshot

def _switching_para_ledger(switching: Any) -> LancamentoSwitchingLedger:
    referencia = _dict_referencia(_valor(switching, 'referencia_estado_temporal', {}))
    valor_migrado = (
        referencia.get('valor_liquido_migrado')
        or referencia.get('valor_migrado')
        or referencia.get('valor_liquido')
        or referencia.get('valor')
    )
    return LancamentoSwitchingLedger(
        data=_valor(switching, 'data'),
        tipo='switching_escolhido_referencialmente',
        switching_id=_valor(switching, 'switching_id'),
        pacote_id=_valor(switching, 'pacote_id'),
        lote_origem_id=_valor(switching, 'lote_origem_id'),
        lote_destino_id=_valor(switching, 'lote_destino_id'),
        tipo_switching=_valor(switching, 'tipo_switching'),
        valor_liquido_migrado_referencial=valor_migrado,
        status=_valor(switching, 'status_referencial', 'switching_referencial_sem_execucao_real'),
        referencia_original=referencia,
        metadados={'origem': 'switchings_escolhidos_temporalmente'},
    )


def _switching_operacional_para_ledger(switching: Any) -> dict[str, Any]:
    snapshot = _dict_referencia(switching)
    snapshot['origem'] = 'ResultadoMotorTemporalConjunto.eventos_temporais_base.switchings_realizados'
    snapshot['status_observavel'] = snapshot.get('status_temporal') or 'switching_operacional_preservado'
    snapshot['data'] = snapshot.get('data_switching') or snapshot.get('data_aplicacao')
    snapshot['lote_origem_id'] = snapshot.get('lote_origem') or snapshot.get('lote_origem_id')
    snapshot['lote_destino_id'] = snapshot.get('lote_destino') or snapshot.get('lote_destino_id')
    snapshot['valor_liquido_migrado_referencial'] = snapshot.get('valor_liquido_migrado')
    return snapshot


def _lote_pos_switching_materializado_para_ledger(switching: Any) -> dict[str, Any] | None:
    snapshot = _dict_referencia(switching)
    if str(snapshot.get('status_temporal') or '').strip() != 'materializado':
        return None
    lote_destino = snapshot.get('lote_destino') or snapshot.get('lote_destino_id')
    if not lote_destino:
        return None
    return {
        'lote_id': lote_destino,
        'lote_id_operacional': lote_destino,
        'status_temporal': 'ativo_pos_switching',
        'origem_canonica': 'switching_canonico_preservado_etapa6',
        'origem': 'ResultadoMotorTemporalConjunto.eventos_temporais_base.switchings_realizados',
        'origem_switching': snapshot.get('lote_origem') or snapshot.get('lote_origem_id'),
        'switching_id': snapshot.get('switching_id'),
        'produto': snapshot.get('produto_destino'),
        'produto_destino': snapshot.get('produto_destino'),
        'data_switching': snapshot.get('data_switching'),
        'data_aplicacao': snapshot.get('data_aplicacao'),
        'data_recebimento': snapshot.get('data_recebimento'),
        'valor_liquido_migrado': snapshot.get('valor_liquido_migrado'),
        'referencia_switching_temporal': snapshot,
    }


def _numero_ledger(valor: Any) -> float | None:
    if valor is None:
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    if numero != numero:
        return None
    return numero


def _somar_materializado(itens: list[Any], campo: str, status_campo: str) -> float | None:
    valores: list[float] = []
    for item in itens:
        status = str(_valor(item, status_campo, '') or '').strip()
        valor = _numero_ledger(_valor(item, campo))
        if valor is None:
            if status and status not in {'nao_aplicavel'}:
                return None
            continue
        valores.append(valor)
    if not valores:
        return 0.0
    return round(sum(valores), 10)


def _status_ciclo_lote(lote: dict[str, Any], switching_por_origem: dict[str, dict[str, Any]]) -> str:
    lote_id = str(lote.get('lote_id_operacional') or lote.get('lote_id') or '').strip()
    status = str(lote.get('status_temporal') or lote.get('status_ciclo') or '').strip()
    if lote_id in switching_por_origem or status in {'migrado_por_switching', 'exaurido_por_switching'} or bool(lote.get('migrado_por_switching')):
        return 'migrado_por_switching'
    if status.startswith('exaurido'):
        return 'exaurido_por_saque'
    if status in {'ativo_pos_switching', 'ativo'} or bool(lote.get('sintetico_pos_switching')):
        return 'ativo'
    return status or 'status_ciclo_nao_materializado'


def _data_inicio_lote(lote: dict[str, Any]) -> Any:
    return lote.get('data_aplicacao') or lote.get('data_recebimento')


def _valor_lote(lote: dict[str, Any], *campos: str) -> Any:
    for campo in campos:
        if campo in lote and lote.get(campo) is not None:
            return lote.get(campo)
    return None


def _auditar_lote_patrimonial(lote: dict[str, Any]) -> dict[str, Any]:
    lacunas: list[str] = []
    bloqueios: list[str] = []
    obrigatorios = [
        'lote_id_operacional',
        'status_ciclo',
        'data_inicio_rendimento',
        'data_fim_rendimento',
        'regra_data_fim_rendimento',
        'valor_original',
        'bruto_sacado',
        'liquido_sacado',
        'bruto_atual',
        'liquido_atual',
        'patrimonio_liquido',
        'rendimento_liquido',
        'origem_dados',
    ]
    for campo in obrigatorios:
        if lote.get(campo) is None:
            lacunas.append(f'{campo}_ausente')
    valor_original = _numero_ledger(lote.get('valor_original'))
    patrimonio_liquido = _numero_ledger(lote.get('patrimonio_liquido'))
    rendimento_liquido = _numero_ledger(lote.get('rendimento_liquido'))
    if valor_original is not None and patrimonio_liquido is not None and rendimento_liquido is not None:
        esperado = round(patrimonio_liquido - valor_original, 10)
        if abs(esperado - rendimento_liquido) > 0.01:
            bloqueios.append('rendimento_liquido_diverge_do_patrimonio_menos_original')
    status_ciclo = str(lote.get('status_ciclo') or '')
    if status_ciclo == 'exaurido_por_saque':
        if _numero_ledger(lote.get('bruto_atual')) != 0.0 or _numero_ledger(lote.get('liquido_atual')) != 0.0:
            bloqueios.append('exaurido_por_saque_com_atual_nao_zero')
        if lote.get('regra_data_fim_rendimento') != 'data_ultimo_uso':
            bloqueios.append('exaurido_por_saque_regra_data_fim_invalida')
    if status_ciclo == 'migrado_por_switching':
        if lote.get('data_fim_rendimento') != lote.get('data_switching'):
            bloqueios.append('migrado_por_switching_data_fim_diferente_data_switching')
        if lote.get('regra_data_fim_rendimento') != 'data_switching':
            bloqueios.append('migrado_por_switching_regra_data_fim_invalida')
    if status_ciclo == 'ativo' and lote.get('regra_data_fim_rendimento') != 'data_referencia':
        bloqueios.append('ativo_regra_data_fim_invalida')
    status_auditoria = 'ok' if not lacunas and not bloqueios else ('lacuna' if lacunas and not bloqueios else 'bloqueio')
    return {
        'lote_id_operacional': lote.get('lote_id_operacional'),
        'status_auditoria': status_auditoria,
        'lacunas': lacunas,
        'bloqueios': bloqueios,
    }


def _construir_lotes_patrimoniais(ledger: LedgerTemporalCanonico, resultado: ResultadoMotorTemporalConjunto) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lotes_origem = [_dict_referencia(lote) for lote in _lista(_valor(resultado, 'lotes_patrimoniais_temporais', []))]
    reservas_por_lote: dict[str, list[Any]] = {}
    for reserva in ledger.fontes_reservadas:
        lote_id = str(_valor(reserva, 'lote_id_operacional') or '').strip()
        if not lote_id:
            continue
        reservas_por_lote.setdefault(lote_id, []).append(reserva)

    eventos_base = _valor(resultado, 'eventos_temporais_base')
    switching_por_origem: dict[str, dict[str, Any]] = {}
    for switching in _lista(_valor(eventos_base, 'switchings_realizados', [])):
        snapshot = _dict_referencia(switching)
        origem = str(snapshot.get('lote_origem') or snapshot.get('lote_origem_id') or '').strip()
        if origem:
            switching_por_origem[origem] = snapshot

    saida: list[dict[str, Any]] = []
    auditorias: list[dict[str, Any]] = []
    for lote in lotes_origem:
        lote_id = str(lote.get('lote_id_operacional') or lote.get('lote_id') or '').strip()
        if not lote_id:
            continue
        reservas = reservas_por_lote.get(lote_id, [])
        bruto_sacado = _somar_materializado(reservas, 'valor_bruto_resgate', 'status_valor_bruto_resgate')
        liquido_sacado = _somar_materializado(reservas, 'valor_liquido_resgate', 'status_valor_liquido_resgate')
        data_ultimo_uso = max((_valor(reserva, 'data') for reserva in reservas if _valor(reserva, 'data') is not None), default=None)
        status_ciclo = _status_ciclo_lote(lote, switching_por_origem)
        switching = switching_por_origem.get(lote_id)
        data_switching = _valor(switching, 'data_switching') or _valor(switching, 'data_aplicacao') if switching else lote.get('data_switching')
        valor_migrado = _numero_ledger(_valor(switching, 'valor_liquido_migrado') if switching else lote.get('valor_liquido_migrado'))
        valor_original = _numero_ledger(_valor_lote(lote, 'valor_original'))
        bruto_atual = _numero_ledger(_valor_lote(lote, 'investimento_bruto', 'bruto_atual'))
        liquido_atual = _numero_ledger(_valor_lote(lote, 'valor_liquido_disponivel_atual', 'saldo_disponivel_atual', 'liquido_atual'))

        regra_data_fim = None
        data_fim = None
        patrimonio_liquido = None
        if status_ciclo == 'ativo':
            regra_data_fim = 'data_referencia'
            data_fim = ledger.data_referencia
            if bruto_atual == 0.0:
                bruto_atual = None
            if liquido_atual == 0.0:
                liquido_atual = None
            if liquido_sacado is not None and liquido_atual is not None:
                patrimonio_liquido = round(liquido_sacado + liquido_atual, 10)
        elif status_ciclo == 'exaurido_por_saque':
            regra_data_fim = 'data_ultimo_uso'
            data_fim = data_ultimo_uso
            bruto_atual = 0.0
            liquido_atual = 0.0
            if liquido_sacado is not None:
                patrimonio_liquido = liquido_sacado
        elif status_ciclo == 'migrado_por_switching':
            regra_data_fim = 'data_switching'
            data_fim = data_switching
            bruto_atual = 0.0
            liquido_atual = 0.0
            if liquido_sacado is not None and valor_migrado is not None:
                patrimonio_liquido = round(liquido_sacado + valor_migrado, 10)
        rendimento_liquido = None
        if patrimonio_liquido is not None and valor_original is not None:
            rendimento_liquido = round(patrimonio_liquido - valor_original, 10)

        item = {
            'lote_id_operacional': lote_id,
            'status_ciclo': status_ciclo,
            'data_inicio_rendimento': _data_inicio_lote(lote),
            'data_fim_rendimento': data_fim,
            'regra_data_fim_rendimento': regra_data_fim,
            'valor_original': valor_original,
            'bruto_sacado': bruto_sacado,
            'liquido_sacado': liquido_sacado,
            'bruto_atual': bruto_atual,
            'liquido_atual': liquido_atual,
            'patrimonio_liquido': patrimonio_liquido,
            'rendimento_liquido': rendimento_liquido,
            'data_ultimo_uso': data_ultimo_uso,
            'data_switching': data_switching,
            'valor_liquido_migrado': valor_migrado,
            'origem_dados': 'ResultadoMotorTemporalConjunto.lotes_patrimoniais_temporais+fontes_reservadas_temporalmente',
            'referencia_lote_temporal': lote,
        }
        auditoria_lote = _auditar_lote_patrimonial(item)
        item['status_auditoria'] = auditoria_lote['status_auditoria']
        item['lacunas_auditoria'] = auditoria_lote['lacunas']
        item['bloqueios_auditoria'] = auditoria_lote['bloqueios']
        saida.append(item)
        auditorias.append(auditoria_lote)

    auditoria = {
        'origem': 'LedgerTemporalCanonico.lotes_patrimoniais',
        'qtd_lotes': len(saida),
        'qtd_ok': sum(1 for item in auditorias if item.get('status_auditoria') == 'ok'),
        'qtd_lacunas': sum(1 for item in auditorias if item.get('lacunas')),
        'qtd_bloqueios': sum(1 for item in auditorias if item.get('bloqueios')),
        'lotes': auditorias,
    }
    return saida, auditoria


def _saldos_por_data(resultado: ResultadoMotorTemporalConjunto) -> dict[date, list[SaldoLedgerTemporal]]:
    saida: dict[date, list[SaldoLedgerTemporal]] = {}
    trajetoria = _valor(resultado, 'trajetoria_temporal_interna_escolhida')
    saldos_origem = _valor(trajetoria, 'saldos_referenciais_fontes_temporais') if trajetoria else None
    if saldos_origem is None:
        estados = _valor(resultado, 'estado_temporal_interno_por_data') or {}
        saldos_origem = {
            data_ref: _valor(estado, 'saldos_fontes_referenciais', [])
            for data_ref, estado in estados.items()
        }
    for data_ref, saldos in (saldos_origem or {}).items():
        saida[data_ref] = [
            SaldoLedgerTemporal(
                data=_valor(saldo, 'data', data_ref),
                fonte_id=_valor(saldo, 'fonte_id'),
                valor_disponivel_referencial=_valor(saldo, 'valor_disponivel_referencial'),
                valor_reservado_acumulado_referencial=_valor(saldo, 'valor_reservado_acumulado_referencial'),
                referencia_original=_dict_referencia(saldo),
            )
            for saldo in _lista(saldos)
        ]
    return saida


def _bloqueios_finais(resultado: ResultadoMotorTemporalConjunto) -> list[Any]:
    auditoria_final = _valor(resultado, 'auditoria_final_etapa5')
    return _lista(_valor(auditoria_final, 'bloqueios', []))


def _avisos_finais(resultado: ResultadoMotorTemporalConjunto) -> list[str]:
    avisos: list[str] = []
    for campo in ('auditoria_final_etapa5', 'auditoria_trajetoria_temporal_interna', 'auditoria_integridade_resultado'):
        auditoria = _valor(resultado, campo)
        avisos.extend(str(aviso) for aviso in _lista(_valor(auditoria, 'avisos', [])))
    return avisos


def _auditar_ledger(ledger: LedgerTemporalCanonico, resultado: ResultadoMotorTemporalConjunto) -> AuditoriaLedgerTemporalCanonico:
    bloqueios: list[str] = []
    avisos = list(ledger.avisos)

    if not isinstance(resultado, ResultadoMotorTemporalConjunto):
        bloqueios.append('entrada_nao_e_resultado_motor_temporal_conjunto')

    for evento in ledger.eventos:
        if evento.data is None:
            bloqueios.append('evento_ledger_sem_data')
        if evento.tipo in _TIPOS_EXECUCAO_REAL_PROIBIDOS or 'real' in (evento.tipo or '') and 'referencial' not in (evento.tipo or ''):
            bloqueios.append('evento_indica_execucao_real_proibida')

    colecoes_lancamentos: list[Any] = []
    colecoes_lancamentos.extend(ledger.obrigacoes_cobertas)
    colecoes_lancamentos.extend(ledger.obrigacoes_bloqueadas)
    colecoes_lancamentos.extend(ledger.fontes_utilizadas)
    colecoes_lancamentos.extend(ledger.fontes_reservadas)
    colecoes_lancamentos.extend(ledger.switchings_escolhidos)
    colecoes_lancamentos.extend(ledger.bloqueios)
    for lancamento in colecoes_lancamentos:
        if not _valor(lancamento, 'tipo'):
            bloqueios.append('lancamento_ledger_sem_tipo')

    for obrigacao in ledger.obrigacoes_cobertas:
        if not obrigacao.obrigacao_id and not obrigacao.referencia_original:
            bloqueios.append('obrigacao_coberta_sem_referencia_minima')

    for obrigacao in ledger.obrigacoes_bloqueadas:
        if not obrigacao.motivo:
            avisos.append('obrigacao_bloqueada_sem_motivo_com_aviso_explicito')

    for fonte in ledger.fontes_utilizadas:
        if not fonte.fonte_id:
            avisos.append('uso_fonte_sem_fonte_referenciada_no_resultado')

    for reserva in ledger.fontes_reservadas:
        if not reserva.fonte_id or reserva.data is None:
            avisos.append('reserva_sem_fonte_ou_data_no_resultado')

    for switching in ledger.switchings_escolhidos:
        if not switching.lote_origem_id or not switching.lote_destino_id:
            avisos.append('switching_sem_origem_ou_destino_no_resultado')

    metadados = ledger.metadados
    if metadados.get('origem_exclusiva') != 'ResultadoMotorTemporalConjunto':
        bloqueios.append('origem_exclusiva_nao_declarada_como_resultado_motor_temporal_conjunto')

    fontes_proibidas = set(metadados.get('fontes_proibidas_nao_consumidas', []))
    if not {'console', 'XLSX', 'saida_observavel', 'diagnostico_operacional'}.issubset(fontes_proibidas):
        bloqueios.append('declaracao_fontes_proibidas_incompleta')

    if metadados.get('decisao_nova_criada_etapa6') is not False:
        bloqueios.append('declaracao_sem_decisao_nova_ausente')

    if metadados.get('bloqueios_finais_etapa5_preservados') is not True:
        bloqueios.append('bloqueios_finais_etapa5_nao_preservados')

    if any(palavra in str(metadados).lower() for palavra in ('shadow', 'fallback legado', 'rota paralela')):
        bloqueios.append('metadados_indicam_rota_paralela_proibida')

    if ledger.pronto_para_etapa_posterior and not _valor(resultado, 'pronto_para_etapa6', False):
        bloqueios.append('ledger_pronto_para_etapa_posterior_com_resultado_etapa5_bloqueado')

    resumo = {
        'qtd_eventos': len(ledger.eventos),
        'qtd_obrigacoes_cobertas': len(ledger.obrigacoes_cobertas),
        'qtd_obrigacoes_bloqueadas': len(ledger.obrigacoes_bloqueadas),
        'qtd_fontes_utilizadas': len(ledger.fontes_utilizadas),
        'qtd_fontes_reservadas': len(ledger.fontes_reservadas),
        'qtd_switchings_escolhidos': len(ledger.switchings_escolhidos),
        'qtd_switchings_realizados_operacionais': len(ledger.switchings_realizados_operacionais),
        'qtd_lotes_pos_switching_materializados': len(ledger.lotes_pos_switching_materializados),
        'qtd_lotes_patrimoniais': len(ledger.lotes_patrimoniais),
        'qtd_destinos_sobras_recebidos': len(ledger.destinos_sobras_recebidos),
        'qtd_lotes_futuros_materializados': len(ledger.lotes_futuros_materializados),
        'qtd_bloqueios': len(ledger.bloqueios),
        'origem_exclusiva': metadados.get('origem_exclusiva'),
        'pronto_para_etapa6_origem': _valor(resultado, 'pronto_para_etapa6', False),
        'pronto_para_etapa_posterior': ledger.pronto_para_etapa_posterior,
    }
    return AuditoriaLedgerTemporalCanonico(ok=not bloqueios, bloqueios=bloqueios, avisos=avisos, resumo=resumo)


def construir_ledger_temporal_canonico(
    resultado: ResultadoMotorTemporalConjunto,
    parametros: ParametrosLedgerTemporal | None = None,
) -> LedgerTemporalCanonico:
    parametros = parametros or ParametrosLedgerTemporal()
    avisos: list[str] = []
    campos_ausentes = [campo for campo in _CAMPOS_ESPERADOS_RESULTADO if not hasattr(resultado, campo)]
    for campo in campos_ausentes:
        avisos.append(f'campo_ausente_em_resultado_motor_temporal_conjunto:{campo}')

    horizonte = _horizonte(resultado, avisos)
    pronto_para_etapa6 = bool(_valor(resultado, 'pronto_para_etapa6', False))
    bloqueios_finais = _bloqueios_finais(resultado)
    avisos.extend(_avisos_finais(resultado))

    ledger = LedgerTemporalCanonico(
        data_referencia=_valor(resultado, 'data_referencia'),
        horizonte=horizonte,
        avisos=avisos,
        metadados={
            'etapa': '6',
            'artefato': 'LedgerTemporalCanonico',
            'versao_schema': parametros.versao_schema,
            'origem_exclusiva': parametros.origem_exclusiva,
            'resultado_origem_metadados': dict(_valor(resultado, 'metadados', {}) or {}),
            'campos_ausentes_resultado': campos_ausentes,
            'pronto_para_etapa6_origem': pronto_para_etapa6,
            'sem_execucao_pagamento_bancario_real': True,
            'sem_execucao_switching_real': True,
            'sem_reotimizacao': True,
            'sem_revaloracao': True,
            'sem_nova_escolha_fonte_ou_pacote': True,
            'decisao_nova_criada_etapa6': False,
            'fontes_proibidas_nao_consumidas': ['console', 'XLSX', 'saida_observavel', 'diagnostico_operacional', 'logs'],
            'bloqueios_finais_etapa5_preservados': True,
        },
        pronto_para_etapa_posterior=pronto_para_etapa6 and not bloqueios_finais,
    )

    for evento in _lista(_valor(resultado, 'eventos_trajetoria_temporal', [])):
        evento_ledger = _evento_para_ledger(evento, resultado)
        ledger.eventos.append(evento_ledger)
        _registrar_lancamento(ledger, evento_ledger.data, evento_ledger)

    for obrigacao in _lista(_valor(resultado, 'obrigacoes_cobertas_temporalmente', [])):
        lancamento = _obrigacao_coberta_para_ledger(obrigacao)
        ledger.obrigacoes_cobertas.append(lancamento)
        _registrar_lancamento(ledger, lancamento.data, lancamento)

    for obrigacao in _lista(_valor(resultado, 'obrigacoes_bloqueadas_temporalmente', [])):
        lancamento = _obrigacao_bloqueada_para_ledger(obrigacao, ledger.avisos)
        ledger.obrigacoes_bloqueadas.append(lancamento)
        _registrar_lancamento(ledger, lancamento.data, lancamento)

    eventos_base = _valor(resultado, 'eventos_temporais_base')
    for pagamento in _lista(_valor(eventos_base, 'pagamentos', [])):
        if _valor(pagamento, 'pago') is True:
            ledger.pagamentos_historicos_realizados.append(_pagamento_historico_realizado_para_ledger(pagamento))

    for reserva in _lista(_valor(resultado, 'fontes_reservadas_temporalmente', [])):
        reserva_ledger, fonte_ledger = _reserva_para_lancamentos(reserva)
        ledger.fontes_reservadas.append(reserva_ledger)
        ledger.fontes_utilizadas.append(fonte_ledger)
        _registrar_lancamento(ledger, reserva_ledger.data, reserva_ledger)
        _registrar_lancamento(ledger, fonte_ledger.data, fonte_ledger)

    for switching in _lista(_valor(resultado, 'switchings_escolhidos_temporalmente', [])):
        lancamento = _switching_para_ledger(switching)
        ledger.switchings_escolhidos.append(lancamento)
        _registrar_lancamento(ledger, lancamento.data, lancamento)

    eventos_base = _valor(resultado, 'eventos_temporais_base')
    for switching in _lista(_valor(eventos_base, 'switchings_realizados', [])):
        switching_snapshot = _switching_operacional_para_ledger(switching)
        ledger.switchings_realizados_operacionais.append(switching_snapshot)
        _registrar_lancamento(ledger, switching_snapshot.get('data'), switching_snapshot)
        lote_pos = _lote_pos_switching_materializado_para_ledger(switching)
        if lote_pos is not None:
            ledger.lotes_pos_switching_materializados.append(lote_pos)
            _registrar_lancamento(ledger, lote_pos.get('data_aplicacao') or lote_pos.get('data_switching'), lote_pos)

    for destino in _lista(_valor(resultado, 'destinos_sobras_recebidos_temporais', [])):
        destino_snapshot = _dict_referencia(destino)
        destino_snapshot['origem'] = 'ResultadoMotorTemporalConjunto.destinos_sobras_recebidos_temporais'
        ledger.destinos_sobras_recebidos.append(destino_snapshot)
        _registrar_lancamento(ledger, _valor(destino, 'data_recebimento'), destino_snapshot)

    for lote in _lista(_valor(resultado, 'lotes_futuros_materializados', [])):
        lote_snapshot = _dict_referencia(lote)
        lote_snapshot['origem'] = 'ResultadoMotorTemporalConjunto.lotes_futuros_materializados'
        ledger.lotes_futuros_materializados.append(lote_snapshot)
        _registrar_lancamento(ledger, _valor(lote, 'data_aplicacao') or _valor(lote, 'data_recebimento'), lote_snapshot)

    ledger.lotes_patrimoniais, ledger.auditoria_lotes_patrimoniais = _construir_lotes_patrimoniais(ledger, resultado)
    for lote_patrimonial in ledger.lotes_patrimoniais:
        _registrar_lancamento(ledger, lote_patrimonial.get('data_fim_rendimento'), lote_patrimonial)

    ledger.saldos_referenciais_por_data = _saldos_por_data(resultado)
    for data_ref, saldos in ledger.saldos_referenciais_por_data.items():
        for saldo in saldos:
            _registrar_lancamento(ledger, data_ref, saldo)

    for bloqueio in bloqueios_finais:
        lancamento = LancamentoBloqueioLedger(
            data=_valor(bloqueio, 'data'),
            tipo='bloqueio_final_etapa5_preservado',
            codigo=str(_valor(bloqueio, 'codigo', 'bloqueio_final_etapa5')),
            motivo=str(_valor(bloqueio, 'detalhe', 'bloqueio_final_etapa5_sem_detalhe')),
            severidade=str(_valor(bloqueio, 'severidade', 'bloqueio')),
            referencia_original=_dict_referencia(bloqueio),
            metadados={'origem': 'auditoria_final_etapa5.bloqueios'},
        )
        ledger.bloqueios.append(lancamento)
        _registrar_lancamento(ledger, lancamento.data, lancamento)

    if not pronto_para_etapa6:
        ledger.avisos.append('resultado_motor_temporal_conjunto_nao_pronto_para_etapa6_ledger_nao_finge_completude')
        if not ledger.bloqueios:
            bloqueio = LancamentoBloqueioLedger(
                data=ledger.data_referencia,
                tipo='pronto_para_etapa6_false_preservado',
                codigo='resultado_etapa5_nao_pronto_para_etapa6',
                motivo='ResultadoMotorTemporalConjunto.pronto_para_etapa6=False',
                metadados={'origem': 'pronto_para_etapa6'},
            )
            ledger.bloqueios.append(bloqueio)
            _registrar_lancamento(ledger, bloqueio.data, bloqueio)

    ledger.auditoria = _auditar_ledger(ledger, resultado)
    ledger.pronto_para_etapa_posterior = ledger.pronto_para_etapa_posterior and ledger.auditoria.ok
    return ledger


__all__ = [
    'AuditoriaLedgerTemporalCanonico',
    'EventoLedgerTemporal',
    'LancamentoBloqueioLedger',
    'LancamentoFonteLedger',
    'LancamentoObrigacaoLedger',
    'LancamentoReservaLedger',
    'LancamentoSwitchingLedger',
    'LedgerTemporalCanonico',
    'ParametrosLedgerTemporal',
    'SaldoLedgerTemporal',
    'construir_ledger_temporal_canonico',
]
