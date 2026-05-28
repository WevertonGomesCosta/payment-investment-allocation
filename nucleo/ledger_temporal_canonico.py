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
    fontes_utilizadas: list[LancamentoFonteLedger] = field(default_factory=list)
    fontes_reservadas: list[LancamentoReservaLedger] = field(default_factory=list)
    switchings_escolhidos: list[LancamentoSwitchingLedger] = field(default_factory=list)
    saldos_referenciais_por_data: dict[date, list[SaldoLedgerTemporal]] = field(default_factory=dict)
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
        metadados={'origem': 'fontes_reservadas_temporalmente'},
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
        metadados={'origem': 'fontes_reservadas_temporalmente'},
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


def _switching_para_ledger(switching: Any) -> LancamentoSwitchingLedger:
    referencia = _dict_referencia(_valor(switching, 'referencia_estado_temporal', {}))
    valor_migrado = referencia.get('valor_liquido_migrado') or referencia.get('valor_liquido') or referencia.get('valor')
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
