from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from typing import Any

from nucleo.ledger_temporal_canonico import LedgerTemporalCanonico


_ORIGEM_FORMAL = 'LedgerTemporalCanonico'
_ORIGEM_ETAPA6_ESPERADA = 'ResultadoMotorTemporal' + 'Conjunto'
_FONTES_DIRETAS_PROIBIDAS = {
    'console',
    'xlsx',
    'xls',
    'saida_observavel',
    'saída observável',
    'logs',
    'log',
    'diagnostico',
    'diagnóstico',
    'script_diagnostico',
    'script diagnóstico',
    'estado_temporal' + '_inicial',
    'resultado_motor_temporal' + '_conjunto',
}


@dataclass(slots=True)
class ParametrosGatesValidacaoNucleo:
    tolerancia_valor: float = 0.01
    tolerancia_residual: float = 0.20
    bloquear_sem_evidencia_minima: bool = False
    validar_liquidez_carencia_quando_disponivel: bool = True
    validar_aderencia_terminal_quando_disponivel: bool = True


@dataclass(slots=True)
class EvidenciaGateNucleo:
    gate_id: str
    data_referencia: date | None
    entidade_tipo: str
    entidade_id: str | None
    campo: str | None
    valor_observado: object | None
    valor_esperado: object | None
    diferenca: float | None
    severidade: str
    mensagem: str
    referencias_ledger: dict[str, object]


@dataclass(slots=True)
class BloqueioGateNucleo:
    gate_id: str
    codigo: str
    mensagem: str
    data_referencia: date | None
    entidade_tipo: str
    entidade_id: str | None
    severidade: str = 'bloqueio'
    evidencias: list[EvidenciaGateNucleo] = field(default_factory=list)


@dataclass(slots=True)
class AvisoGateNucleo:
    gate_id: str
    codigo: str
    mensagem: str
    data_referencia: date | None
    entidade_tipo: str
    entidade_id: str | None
    severidade: str = 'aviso'
    evidencias: list[EvidenciaGateNucleo] = field(default_factory=list)


@dataclass(slots=True)
class GateValidacaoNucleo:
    gate_id: str
    nome: str
    executado: bool
    aprovado: bool
    nao_aplicavel: bool
    motivo_nao_aplicavel: str | None
    bloqueios: list[BloqueioGateNucleo] = field(default_factory=list)
    avisos: list[AvisoGateNucleo] = field(default_factory=list)
    evidencias: list[EvidenciaGateNucleo] = field(default_factory=list)
    resumo: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoGatesValidacaoNucleo:
    qtd_gates: int
    qtd_gates_executados: int
    qtd_gates_aprovados: int
    qtd_gates_reprovados: int
    qtd_gates_nao_aplicaveis: int
    qtd_bloqueios: int
    qtd_avisos: int
    qtd_obrigacoes_cobertas: int
    qtd_obrigacoes_bloqueadas: int
    qtd_fontes_utilizadas: int
    qtd_fontes_reservadas: int
    qtd_switchings: int
    pronto_para_etapa8: bool


@dataclass(slots=True)
class ResultadoGatesValidacaoNucleo:
    ok: bool
    pronto_para_etapa8: bool
    origem_formal: str
    gates: list[GateValidacaoNucleo]
    bloqueios: list[BloqueioGateNucleo]
    avisos: list[AvisoGateNucleo]
    evidencias: list[EvidenciaGateNucleo]
    resumo: ResumoGatesValidacaoNucleo
    metadados: dict[str, object]


def _valor(objeto: Any, campo: str, padrao: Any = None) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(campo, padrao)
    return getattr(objeto, campo, padrao)


def _dict_referencia(valor: Any) -> dict[str, object]:
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return dict(valor)
    if is_dataclass(valor):
        return asdict(valor)
    return {'valor': valor}


def _float_ou_none(valor: Any) -> float | None:
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _id_entidade(objeto: Any, *campos: str) -> str | None:
    for campo in campos:
        valor = _valor(objeto, campo)
        if valor not in (None, ''):
            return str(valor)
    return None


def _referencias(objeto: Any, indice: int | None = None) -> dict[str, object]:
    refs = {
        'origem_formal': _ORIGEM_FORMAL,
        'tipo_ledger': type(objeto).__name__ if objeto is not None else None,
    }
    if indice is not None:
        refs['indice_ledger'] = indice
    if objeto is not None:
        metadados = _valor(objeto, 'metadados')
        if isinstance(metadados, dict):
            refs['metadados'] = dict(metadados)
        referencia_original = _valor(objeto, 'referencia_original')
        if isinstance(referencia_original, dict):
            refs['referencia_original'] = dict(referencia_original)
    return refs


def _nova_evidencia(
    gate_id: str,
    data_referencia: date | None,
    entidade_tipo: str,
    entidade_id: str | None,
    campo: str | None,
    valor_observado: object | None,
    valor_esperado: object | None,
    diferenca: float | None,
    severidade: str,
    mensagem: str,
    referencias_ledger: dict[str, object],
) -> EvidenciaGateNucleo:
    return EvidenciaGateNucleo(
        gate_id=gate_id,
        data_referencia=data_referencia,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        campo=campo,
        valor_observado=valor_observado,
        valor_esperado=valor_esperado,
        diferenca=diferenca,
        severidade=severidade,
        mensagem=mensagem,
        referencias_ledger=referencias_ledger,
    )


def _adicionar_bloqueio(
    gate: GateValidacaoNucleo,
    codigo: str,
    mensagem: str,
    data_referencia: date | None,
    entidade_tipo: str,
    entidade_id: str | None,
    evidencia: EvidenciaGateNucleo | None = None,
) -> None:
    evidencias = [evidencia] if evidencia else []
    gate.bloqueios.append(
        BloqueioGateNucleo(
            gate_id=gate.gate_id,
            codigo=codigo,
            mensagem=mensagem,
            data_referencia=data_referencia,
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            evidencias=evidencias,
        )
    )
    if evidencia:
        gate.evidencias.append(evidencia)


def _adicionar_aviso(
    gate: GateValidacaoNucleo,
    codigo: str,
    mensagem: str,
    data_referencia: date | None,
    entidade_tipo: str,
    entidade_id: str | None,
    evidencia: EvidenciaGateNucleo | None = None,
) -> None:
    evidencias = [evidencia] if evidencia else []
    gate.avisos.append(
        AvisoGateNucleo(
            gate_id=gate.gate_id,
            codigo=codigo,
            mensagem=mensagem,
            data_referencia=data_referencia,
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            evidencias=evidencias,
        )
    )
    if evidencia:
        gate.evidencias.append(evidencia)


def _novo_gate(gate_id: str, nome: str) -> GateValidacaoNucleo:
    return GateValidacaoNucleo(
        gate_id=gate_id,
        nome=nome,
        executado=True,
        aprovado=True,
        nao_aplicavel=False,
        motivo_nao_aplicavel=None,
    )


def _finalizar_gate(gate: GateValidacaoNucleo, total_itens: int | None = None, motivo_nao_aplicavel: str | None = None) -> GateValidacaoNucleo:
    if motivo_nao_aplicavel is not None:
        gate.nao_aplicavel = True
        gate.motivo_nao_aplicavel = motivo_nao_aplicavel
    gate.aprovado = not gate.bloqueios
    gate.resumo.update(
        {
            'qtd_bloqueios': len(gate.bloqueios),
            'qtd_avisos': len(gate.avisos),
            'qtd_evidencias': len(gate.evidencias),
        }
    )
    if total_itens is not None:
        gate.resumo['qtd_itens_avaliados'] = total_itens
    return gate


def _finalizar_gate_sem_evidencia_minima(
    gate: GateValidacaoNucleo,
    parametros: ParametrosGatesValidacaoNucleo,
    motivo: str,
    entidade_tipo: str,
    data_referencia: date | None = None,
) -> GateValidacaoNucleo:
    if parametros.bloquear_sem_evidencia_minima:
        evidencia = _nova_evidencia(
            gate.gate_id,
            data_referencia,
            entidade_tipo,
            None,
            'evidencia_minima',
            None,
            'evidência mínima materializada no ledger',
            None,
            'bloqueio',
            motivo,
            {'origem_formal': _ORIGEM_FORMAL, 'bloquear_sem_evidencia_minima': True},
        )
        _adicionar_bloqueio(
            gate,
            'evidencia_minima_ausente',
            motivo,
            data_referencia,
            entidade_tipo,
            None,
            evidencia,
        )
        gate.motivo_nao_aplicavel = motivo
        return _finalizar_gate(gate, 0)
    return _finalizar_gate(gate, 0, motivo)


def _data_ou_none(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if hasattr(valor, 'date'):
        try:
            data = valor.date()
            if isinstance(data, date):
                return data
        except (TypeError, ValueError, AttributeError):
            pass
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto:
            return None
        for formato in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
            try:
                return datetime.strptime(texto[:10], formato).date()
            except ValueError:
                continue
    return None


def _valor_materializado(item: Any, *campos: str) -> tuple[str, Any]:
    referencias = _dict_referencia(_valor(item, 'referencia_original', {}))
    metadados = _dict_referencia(_valor(item, 'metadados', {}))
    for campo in campos:
        valor = _valor(item, campo)
        if valor is not None:
            return campo, valor
        if campo in referencias:
            return f'referencia_original.{campo}', referencias[campo]
        if campo in metadados:
            return f'metadados.{campo}', metadados[campo]
    return '', None


def _bool_false(valor: Any) -> bool:
    if valor is False:
        return True
    if isinstance(valor, str):
        return valor.strip().lower() in {'false', 'falso', 'não', 'nao', 'no', '0', 'bloqueado', 'ineligivel', 'inelegivel'}
    if isinstance(valor, (int, float)):
        return valor == 0
    return False


def _fonte_compativel_com_obrigacao(fonte: Any, obrigacao: Any) -> bool:
    for campo in ('data', 'pacote_id'):
        valor_fonte = _valor(fonte, campo)
        valor_obrigacao = _valor(obrigacao, campo)
        if valor_fonte is not None and valor_obrigacao is not None and valor_fonte != valor_obrigacao:
            return False
    return True


def _valor_movimento_fonte(fonte: Any) -> float | None:
    valor = _float_ou_none(_valor(fonte, 'valor_referencial'))
    if valor is not None:
        return valor
    return _float_ou_none(_valor(fonte, 'valor_reservado_referencial'))


def _chave_movimento_fonte(fonte: Any) -> tuple[object, object, object]:
    return (_valor(fonte, 'fonte_id'), _valor(fonte, 'data'), _valor(fonte, 'pacote_id'))


def _fonte_compativel_com_grupo(
    fonte: Any,
    pacote_id: object | None,
    data_grupo: object | None,
    fontes_referenciadas: set[str],
) -> bool:
    fonte_id = _valor(fonte, 'fonte_id')
    fonte_pacote = _valor(fonte, 'pacote_id')
    fonte_data = _valor(fonte, 'data')
    if data_grupo is not None and fonte_data is not None and fonte_data != data_grupo:
        return False
    if pacote_id is not None:
        if fonte_pacote is not None and fonte_pacote != pacote_id:
            return False
        if fonte_pacote == pacote_id:
            return True
    if fonte_id is not None and str(fonte_id) in fontes_referenciadas:
        return True
    return pacote_id is None and not fontes_referenciadas


def _total_fontes_sem_dupla_soma(fontes: list[Any]) -> float:
    valores_por_chave: dict[tuple[object, object, object], float] = {}
    for fonte in fontes:
        valor = _valor_movimento_fonte(fonte)
        if valor is None:
            continue
        chave = _chave_movimento_fonte(fonte)
        valores_por_chave[chave] = max(valores_por_chave.get(chave, 0.0), valor)
    return sum(valores_por_chave.values())


def _validar_liquidez_carencia_materializada(
    gate: GateValidacaoNucleo,
    item: Any,
    entidade_tipo: str,
    entidade_id: str | None,
    indice: int,
    data_item: date | None,
) -> None:
    for campo in ('elegivel_na_data_pagamento', 'elegivel'):
        origem_campo, valor_campo = _valor_materializado(item, campo)
        if origem_campo and _bool_false(valor_campo):
            evidencia = _nova_evidencia(gate.gate_id, data_item, entidade_tipo, entidade_id, origem_campo, valor_campo, True, None, 'bloqueio', 'Movimento de fonte marcado como inelegível no próprio ledger.', _referencias(item, indice))
            _adicionar_bloqueio(gate, f'{campo}_false', 'Movimento de fonte possui evidência de inelegibilidade no ledger.', data_item, entidade_tipo, entidade_id, evidencia)
    origem_liquido, liquido = _valor_materializado(item, 'liquido')
    if origem_liquido and _bool_false(liquido):
        evidencia = _nova_evidencia(gate.gate_id, data_item, entidade_tipo, entidade_id, origem_liquido, liquido, True, None, 'bloqueio', 'Movimento de fonte com liquidez bloqueada conforme evidência do ledger.', _referencias(item, indice))
        _adicionar_bloqueio(gate, 'liquido_false', 'Movimento de fonte possui evidência de liquidez bloqueada no ledger.', data_item, entidade_tipo, entidade_id, evidencia)
    for campo_carencia in ('carencia_ate_origem', 'carencia_ate'):
        origem_carencia, valor_carencia = _valor_materializado(item, campo_carencia)
        data_carencia = _data_ou_none(valor_carencia)
        data_item_parseada = _data_ou_none(data_item)
        if origem_carencia and data_carencia is not None and data_item_parseada is not None and data_carencia > data_item_parseada:
            evidencia = _nova_evidencia(gate.gate_id, data_item_parseada, entidade_tipo, entidade_id, origem_carencia, data_carencia, f'<= {data_item_parseada}', None, 'bloqueio', 'Movimento de fonte em carência posterior à data de uso/reserva.', _referencias(item, indice))
            _adicionar_bloqueio(gate, 'carencia_posterior_data_movimento', 'Movimento de fonte possui carência posterior à data materializada no ledger.', data_item_parseada, entidade_tipo, entidade_id, evidencia)


def _contem_fonte_direta_proibida(valor: Any) -> bool:
    texto = str(valor).lower()
    return any(fonte in texto for fonte in _FONTES_DIRETAS_PROIBIDAS)


def _gate_origem_exclusiva_ledger(ledger: LedgerTemporalCanonico) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_origem_exclusiva_ledger', 'Origem exclusiva no ledger temporal canônico')
    metadados = dict(ledger.metadados or {})
    evidencia_tipo = _nova_evidencia(
        gate.gate_id,
        ledger.data_referencia,
        'ledger',
        None,
        'tipo',
        type(ledger).__name__,
        _ORIGEM_FORMAL,
        None,
        'info',
        'Objeto de entrada formal identificado como ledger temporal canônico.',
        {'metadados_ledger': metadados},
    )
    gate.evidencias.append(evidencia_tipo)

    origem_etapa6 = metadados.get('origem_exclusiva')
    if origem_etapa6 != _ORIGEM_ETAPA6_ESPERADA:
        evidencia = _nova_evidencia(
            gate.gate_id,
            ledger.data_referencia,
            'ledger',
            None,
            'metadados.origem_exclusiva',
            origem_etapa6,
            _ORIGEM_ETAPA6_ESPERADA,
            None,
            'bloqueio',
            'Origem histórica da Etapa 6 não está materializada conforme esperado nos metadados do ledger.',
            {'metadados_ledger': metadados},
        )
        _adicionar_bloqueio(
            gate,
            'origem_etapa6_invalida',
            'Metadados do ledger não confirmam a origem histórica esperada da Etapa 6.',
            ledger.data_referencia,
            'ledger',
            None,
            evidencia,
        )

    entrada_direta_etapa7 = metadados.get('entrada_direta_etapa7') or metadados.get('entrada_formal_etapa7')
    if entrada_direta_etapa7 and str(entrada_direta_etapa7) != _ORIGEM_FORMAL:
        evidencia = _nova_evidencia(
            gate.gate_id,
            ledger.data_referencia,
            'ledger',
            None,
            'metadados.entrada_etapa7',
            entrada_direta_etapa7,
            _ORIGEM_FORMAL,
            None,
            'bloqueio',
            'Entrada direta declarada para a Etapa 7 difere do ledger temporal canônico.',
            {'metadados_ledger': metadados},
        )
        _adicionar_bloqueio(gate, 'entrada_etapa7_nao_ledger', 'Entrada direta da Etapa 7 não é o ledger.', ledger.data_referencia, 'ledger', None, evidencia)

    fontes_declaradas = metadados.get('fontes_diretas_etapa7') or metadados.get('fontes_consumidas_etapa7') or []
    if fontes_declaradas and _contem_fonte_direta_proibida(fontes_declaradas):
        evidencia = _nova_evidencia(
            gate.gate_id,
            ledger.data_referencia,
            'ledger',
            None,
            'metadados.fontes_etapa7',
            fontes_declaradas,
            _ORIGEM_FORMAL,
            None,
            'bloqueio',
            'Metadados indicam fonte direta proibida para a Etapa 7.',
            {'metadados_ledger': metadados},
        )
        _adicionar_bloqueio(gate, 'fonte_direta_proibida_etapa7', 'Fonte direta proibida declarada para a Etapa 7.', ledger.data_referencia, 'ledger', None, evidencia)

    gate.resumo['origem_resultado_etapa7'] = _ORIGEM_FORMAL
    gate.resumo['origem_historica_etapa6'] = origem_etapa6
    return _finalizar_gate(gate)


def _gate_auditoria_ledger(ledger: LedgerTemporalCanonico) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_auditoria_ledger', 'Auditoria interna do ledger')
    auditoria = ledger.auditoria
    if auditoria is None:
        evidencia = _nova_evidencia(gate.gate_id, ledger.data_referencia, 'ledger', None, 'auditoria', None, 'AuditoriaLedgerTemporalCanonico', None, 'bloqueio', 'Auditoria do ledger ausente.', {'origem_formal': _ORIGEM_FORMAL})
        _adicionar_bloqueio(gate, 'auditoria_ledger_ausente', 'Ledger não possui auditoria interna materializada.', ledger.data_referencia, 'ledger', None, evidencia)
        return _finalizar_gate(gate)

    gate.evidencias.append(
        _nova_evidencia(gate.gate_id, ledger.data_referencia, 'auditoria_ledger', None, 'ok', auditoria.ok, True, None, 'info', 'Auditoria interna do ledger foi lida do próprio ledger.', {'auditoria_resumo': dict(auditoria.resumo or {})})
    )
    if not auditoria.ok:
        evidencia = _nova_evidencia(gate.gate_id, ledger.data_referencia, 'auditoria_ledger', None, 'ok', auditoria.ok, True, None, 'bloqueio', 'Auditoria interna do ledger reprovada.', {'auditoria_bloqueios': list(auditoria.bloqueios or [])})
        _adicionar_bloqueio(gate, 'auditoria_ledger_reprovada', 'Auditoria interna do ledger reprovou o artefato.', ledger.data_referencia, 'auditoria_ledger', None, evidencia)

    for indice, bloqueio in enumerate(ledger.bloqueios or []):
        evidencia = _nova_evidencia(gate.gate_id, _valor(bloqueio, 'data'), 'bloqueio_ledger', _id_entidade(bloqueio, 'codigo', 'pacote_id', 'obrigacao_id'), 'bloqueios', _dict_referencia(bloqueio), 'preservado', None, 'bloqueio', 'Bloqueio do ledger preservado nos gates de núcleo.', _referencias(bloqueio, indice))
        _adicionar_bloqueio(gate, str(_valor(bloqueio, 'codigo', 'bloqueio_ledger_preservado')), str(_valor(bloqueio, 'motivo', 'Bloqueio do ledger preservado.')), _valor(bloqueio, 'data'), 'bloqueio_ledger', _id_entidade(bloqueio, 'codigo', 'pacote_id', 'obrigacao_id'), evidencia)

    for indice, aviso in enumerate(ledger.avisos or []):
        evidencia = _nova_evidencia(gate.gate_id, ledger.data_referencia, 'aviso_ledger', None, 'avisos', aviso, 'preservado', None, 'aviso', 'Aviso do ledger preservado nos gates de núcleo.', {'indice_ledger': indice, 'origem_formal': _ORIGEM_FORMAL})
        _adicionar_aviso(gate, 'aviso_ledger_preservado', str(aviso), ledger.data_referencia, 'aviso_ledger', None, evidencia)

    if auditoria.avisos:
        for indice, aviso in enumerate(auditoria.avisos):
            evidencia = _nova_evidencia(gate.gate_id, ledger.data_referencia, 'aviso_auditoria_ledger', None, 'auditoria.avisos', aviso, 'preservado', None, 'aviso', 'Aviso da auditoria do ledger preservado.', {'indice_auditoria': indice, 'origem_formal': _ORIGEM_FORMAL})
            _adicionar_aviso(gate, 'aviso_auditoria_ledger_preservado', str(aviso), ledger.data_referencia, 'aviso_auditoria_ledger', None, evidencia)

    gate.resumo['qtd_bloqueios_ledger_preservados'] = len(ledger.bloqueios or [])
    gate.resumo['qtd_avisos_ledger_preservados'] = len(ledger.avisos or []) + len(auditoria.avisos or [])
    return _finalizar_gate(gate)


def _validar_valor_nao_negativo(gate: GateValidacaoNucleo, item: Any, campo: str, entidade_tipo: str, entidade_id: str | None, indice: int, tolerancia: float) -> None:
    valor = _float_ou_none(_valor(item, campo))
    if valor is not None and valor < -abs(tolerancia):
        evidencia = _nova_evidencia(gate.gate_id, _valor(item, 'data'), entidade_tipo, entidade_id, campo, valor, '>= 0', valor, 'bloqueio', f'Valor negativo incompatível no campo {campo}.', _referencias(item, indice))
        _adicionar_bloqueio(gate, f'{campo}_negativo', f'Valor negativo incompatível no campo {campo}.', _valor(item, 'data'), entidade_tipo, entidade_id, evidencia)


def _gate_obrigacoes_cobertas(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_obrigacoes_cobertas', 'Obrigações cobertas')
    obrigacoes = list(ledger.obrigacoes_cobertas or [])
    if not obrigacoes:
        return _finalizar_gate_sem_evidencia_minima(
            gate,
            parametros,
            'Ledger não disponibiliza obrigações cobertas para validação.',
            'obrigacao_coberta',
            ledger.data_referencia,
        )

    fontes_utilizadas = list(ledger.fontes_utilizadas or [])
    fontes_reservadas = list(ledger.fontes_reservadas or [])
    fontes_materializadas = fontes_utilizadas + fontes_reservadas
    datas_referencia_original = ('data_pagamento', 'data_vencimento', 'Data', 'data', 'vencimento')
    grupos_cobertura: dict[tuple[str, object, object], dict[str, object]] = {}

    for indice, obrigacao in enumerate(obrigacoes):
        entidade_id = _id_entidade(obrigacao, 'obrigacao_id', 'pacote_id')
        data_obrigacao = _valor(obrigacao, 'data')
        if data_obrigacao is None:
            evidencia = _nova_evidencia(gate.gate_id, None, 'obrigacao_coberta', entidade_id, 'data', None, 'data válida', None, 'bloqueio', 'Obrigação coberta sem data.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_sem_data', 'Obrigação coberta não possui data.', None, 'obrigacao_coberta', entidade_id, evidencia)
        if entidade_id is None:
            evidencia = _nova_evidencia(gate.gate_id, data_obrigacao, 'obrigacao_coberta', None, 'identificador', None, 'obrigacao_id ou pacote_id', None, 'bloqueio', 'Obrigação coberta sem identificador mínimo.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_sem_identificador', 'Obrigação coberta não possui identificador mínimo.', data_obrigacao, 'obrigacao_coberta', None, evidencia)
        _validar_valor_nao_negativo(gate, obrigacao, 'valor_coberto_referencial', 'obrigacao_coberta', entidade_id, indice, parametros.tolerancia_valor)

        referencia_original = _dict_referencia(_valor(obrigacao, 'referencia_original', {}))
        data_obrigacao_parseada = _data_ou_none(data_obrigacao)
        for campo_data in datas_referencia_original:
            if campo_data not in referencia_original:
                continue
            data_referencia_original = _data_ou_none(referencia_original.get(campo_data))
            if data_obrigacao_parseada is not None and data_referencia_original is not None and data_referencia_original != data_obrigacao_parseada:
                evidencia = _nova_evidencia(
                    gate.gate_id,
                    data_obrigacao_parseada,
                    'obrigacao_coberta',
                    entidade_id,
                    f'referencia_original.{campo_data}',
                    data_referencia_original,
                    data_obrigacao_parseada,
                    None,
                    'bloqueio',
                    'Data preservada na referência original diverge da data da obrigação coberta no ledger.',
                    _referencias(obrigacao, indice),
                )
                _adicionar_bloqueio(gate, 'data_obrigacao_coberta_divergente_referencia_original', 'Obrigação coberta possui data divergente na referência original preservada.', data_obrigacao_parseada, 'obrigacao_coberta', entidade_id, evidencia)

        valor_obrigacao = _float_ou_none(_valor(obrigacao, 'valor_obrigacao_referencial'))
        valor_coberto = _float_ou_none(_valor(obrigacao, 'valor_coberto_referencial'))
        if valor_obrigacao is None:
            evidencia = _nova_evidencia(gate.gate_id, data_obrigacao, 'obrigacao_coberta', entidade_id, 'valor_obrigacao_referencial', None, 'valor obrigatório materializado no ledger', None, 'bloqueio', 'Obrigação coberta sem valor de obrigação referencial mínimo.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_sem_valor_obrigacao', 'Obrigação coberta não possui valor_obrigacao_referencial para validar pagamento integral.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)
        if valor_coberto is None:
            evidencia = _nova_evidencia(gate.gate_id, data_obrigacao, 'obrigacao_coberta', entidade_id, 'valor_coberto_referencial', None, 'valor coberto materializado no ledger', None, 'bloqueio', 'Obrigação coberta sem valor coberto referencial mínimo.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_sem_valor_coberto', 'Obrigação coberta não possui valor_coberto_referencial para validar pagamento integral.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)
        if valor_obrigacao is not None and valor_coberto is not None:
            diferenca = round(valor_coberto - valor_obrigacao, 10)
            if abs(diferenca) > parametros.tolerancia_valor:
                evidencia = _nova_evidencia(gate.gate_id, data_obrigacao, 'obrigacao_coberta', entidade_id, 'valor_coberto_referencial', valor_coberto, valor_obrigacao, diferenca, 'bloqueio', 'Cobertura referencial incompatível com o valor da obrigação.', _referencias(obrigacao, indice))
                _adicionar_bloqueio(gate, 'cobertura_obrigacao_incompativel', 'Obrigação coberta possui diferença material entre valor coberto e valor da obrigação.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)

        fontes = list(_valor(obrigacao, 'fontes_referenciadas', []) or [])
        if 'fontes_referenciadas' in _dict_referencia(obrigacao) and not fontes:
            evidencia = _nova_evidencia(gate.gate_id, data_obrigacao, 'obrigacao_coberta', entidade_id, 'fontes_referenciadas', fontes, 'fonte associada quando evidenciada', None, 'aviso', 'Obrigação coberta não possui fonte associada no ledger.', _referencias(obrigacao, indice))
            _adicionar_aviso(gate, 'obrigacao_coberta_sem_fonte_associada', 'Obrigação coberta sem fonte associada no ledger.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)
        fontes_compativeis: list[Any] = []
        for fonte_id in fontes:
            fonte_id_str = str(fonte_id)
            utilizadas_da_obrigacao = [
                fonte
                for fonte in fontes_utilizadas
                if str(_valor(fonte, 'fonte_id')) == fonte_id_str and _fonte_compativel_com_obrigacao(fonte, obrigacao)
            ]
            reservadas_da_obrigacao = [
                fonte
                for fonte in fontes_reservadas
                if str(_valor(fonte, 'fonte_id')) == fonte_id_str and _fonte_compativel_com_obrigacao(fonte, obrigacao)
            ]
            fontes_da_obrigacao = utilizadas_da_obrigacao if utilizadas_da_obrigacao else reservadas_da_obrigacao
            fontes_compativeis.extend(fontes_da_obrigacao)
            if not fontes_da_obrigacao:
                evidencia = _nova_evidencia(
                    gate.gate_id,
                    data_obrigacao,
                    'obrigacao_coberta',
                    entidade_id,
                    'fontes_referenciadas',
                    fonte_id,
                    'fonte materializada em fontes_utilizadas ou fontes_reservadas compatível com a obrigação',
                    None,
                    'bloqueio',
                    'Fonte referenciada pela obrigação coberta não existe no ledger com compatibilidade mínima.',
                    _referencias(obrigacao, indice),
                )
                _adicionar_bloqueio(gate, 'fonte_referenciada_nao_materializada', 'Fonte referenciada pela obrigação coberta não foi materializada no ledger.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)
        if fontes and valor_coberto is not None:
            soma_fontes = _total_fontes_sem_dupla_soma(fontes_compativeis)
            diferenca_fontes = round(valor_coberto - soma_fontes, 10)
            if diferenca_fontes > parametros.tolerancia_valor:
                evidencia = _nova_evidencia(
                    gate.gate_id,
                    data_obrigacao,
                    'obrigacao_coberta',
                    entidade_id,
                    'valor_coberto_referencial/fontes_referenciadas',
                    soma_fontes,
                    valor_coberto,
                    diferenca_fontes,
                    'bloqueio',
                    'Soma de fontes materializadas compatíveis é menor que o valor coberto da obrigação.',
                    {**_referencias(obrigacao, indice), 'qtd_fontes_compativeis': len(fontes_compativeis)},
                )
                _adicionar_bloqueio(gate, 'valor_coberto_sem_lastro_em_fontes', 'Valor coberto da obrigação excede a soma das fontes materializadas compatíveis no ledger.', data_obrigacao, 'obrigacao_coberta', entidade_id, evidencia)
        pacote_id = _valor(obrigacao, 'pacote_id')
        obrigacao_id = _valor(obrigacao, 'obrigacao_id')
        chave_grupo = ('pacote', pacote_id, data_obrigacao) if pacote_id is not None else ('obrigacao', obrigacao_id, data_obrigacao)
        grupo = grupos_cobertura.setdefault(
            chave_grupo,
            {
                'total_coberto': 0.0,
                'qtd_obrigacoes': 0,
                'fontes_referenciadas': set(),
                'indice': indice,
                'obrigacao': obrigacao,
            },
        )
        if valor_coberto is not None:
            grupo['total_coberto'] = float(grupo['total_coberto']) + valor_coberto
        grupo['qtd_obrigacoes'] = int(grupo['qtd_obrigacoes']) + 1
        grupo['fontes_referenciadas'].update(str(fonte_id) for fonte_id in fontes)

    for chave_grupo, grupo in grupos_cobertura.items():
        tipo_grupo, grupo_id, data_grupo = chave_grupo
        total_coberto_grupo = float(grupo['total_coberto'])
        if total_coberto_grupo <= 0:
            continue
        pacote_id_grupo = grupo_id if tipo_grupo == 'pacote' else None
        fontes_referenciadas = set(grupo['fontes_referenciadas'])
        utilizadas_compativeis = [
            fonte
            for fonte in fontes_utilizadas
            if _fonte_compativel_com_grupo(fonte, pacote_id_grupo, data_grupo, fontes_referenciadas)
        ]
        reservadas_compativeis = [
            fonte
            for fonte in fontes_reservadas
            if _fonte_compativel_com_grupo(fonte, pacote_id_grupo, data_grupo, fontes_referenciadas)
        ]
        fontes_lastro = utilizadas_compativeis if utilizadas_compativeis else reservadas_compativeis
        origem_lastro = 'fontes_utilizadas' if utilizadas_compativeis else 'fontes_reservadas'
        total_fontes_grupo = _total_fontes_sem_dupla_soma(fontes_lastro)
        diferenca_grupo = round(total_coberto_grupo - total_fontes_grupo, 10)
        if diferenca_grupo > parametros.tolerancia_valor:
            obrigacao_referencia = grupo['obrigacao']
            evidencia = _nova_evidencia(
                gate.gate_id,
                data_grupo,
                'grupo_obrigacoes_cobertas',
                str(grupo_id) if grupo_id is not None else None,
                'valor_coberto_referencial_agregado',
                total_fontes_grupo,
                total_coberto_grupo,
                diferenca_grupo,
                'bloqueio',
                'Total coberto agregado por pacote/data excede o lastro de fontes materializadas compatíveis no ledger.',
                {
                    **_referencias(obrigacao_referencia, int(grupo['indice'])),
                    'chave_grupo': chave_grupo,
                    'qtd_obrigacoes_grupo': grupo['qtd_obrigacoes'],
                    'origem_lastro': origem_lastro,
                    'regra_deduplicacao': 'usa fontes_utilizadas quando existirem para a chave; caso contrário usa fontes_reservadas; não soma ambas',
                    'qtd_fontes_lastro': len(fontes_lastro),
                },
            )
            _adicionar_bloqueio(gate, 'valor_coberto_agregado_sem_lastro_em_fontes', 'Valor coberto agregado por pacote/data excede fontes materializadas compatíveis no ledger.', data_grupo, 'grupo_obrigacoes_cobertas', str(grupo_id) if grupo_id is not None else None, evidencia)
    gate.resumo['regra_lastro_individual'] = 'fontes_utilizadas_preferenciais; fontes_reservadas_apenas_quando_sem_utilizadas; dedup_por_fonte_data_pacote'
    gate.resumo['regra_lastro_agregado'] = 'fontes_utilizadas_preferenciais; fontes_reservadas_apenas_quando_sem_utilizadas; sem_soma_dupla_utilizadas_reservadas'
    gate.resumo['qtd_grupos_cobertura_agregada'] = len(grupos_cobertura)

    return _finalizar_gate(gate, len(obrigacoes))

def _gate_obrigacoes_bloqueadas(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_obrigacoes_bloqueadas', 'Obrigações bloqueadas')
    obrigacoes = list(ledger.obrigacoes_bloqueadas or [])
    if not obrigacoes:
        return _finalizar_gate_sem_evidencia_minima(
            gate,
            parametros,
            'Ledger não disponibiliza obrigações bloqueadas para validação.',
            'obrigacao_bloqueada',
            ledger.data_referencia,
        )

    for indice, obrigacao in enumerate(obrigacoes):
        entidade_id = _id_entidade(obrigacao, 'obrigacao_id', 'pacote_id')
        motivo = _valor(obrigacao, 'motivo')
        if not motivo:
            evidencia = _nova_evidencia(gate.gate_id, _valor(obrigacao, 'data'), 'obrigacao_bloqueada', entidade_id, 'motivo', motivo, 'motivo explícito', None, 'bloqueio', 'Obrigação bloqueada sem motivo explícito.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_bloqueada_sem_motivo', 'Obrigação bloqueada não possui motivo explícito.', _valor(obrigacao, 'data'), 'obrigacao_bloqueada', entidade_id, evidencia)
        if _valor(obrigacao, 'data') is None and not _valor(obrigacao, 'referencia_original'):
            evidencia = _nova_evidencia(gate.gate_id, None, 'obrigacao_bloqueada', entidade_id, 'data', None, 'data ou referência temporal', None, 'bloqueio', 'Obrigação bloqueada sem data ou referência temporal mínima.', _referencias(obrigacao, indice))
            _adicionar_bloqueio(gate, 'obrigacao_bloqueada_sem_referencia_temporal', 'Obrigação bloqueada não possui data ou referência temporal mínima.', None, 'obrigacao_bloqueada', entidade_id, evidencia)
        valor = _float_ou_none(_valor(obrigacao, 'valor_obrigacao_referencial'))
        if valor is None:
            evidencia = _nova_evidencia(gate.gate_id, _valor(obrigacao, 'data'), 'obrigacao_bloqueada', entidade_id, 'valor_obrigacao_referencial', None, 'valor quando disponível', None, 'aviso', 'Valor da obrigação bloqueada não está disponível no ledger.', _referencias(obrigacao, indice))
            _adicionar_aviso(gate, 'obrigacao_bloqueada_sem_valor_disponivel', 'Valor da obrigação bloqueada ausente no ledger.', _valor(obrigacao, 'data'), 'obrigacao_bloqueada', entidade_id, evidencia)
    gate.resumo['qtd_bloqueios_finais_ledger'] = len(ledger.bloqueios or [])
    return _finalizar_gate(gate, len(obrigacoes))


def _gate_fontes_utilizadas(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_fontes_utilizadas', 'Fontes utilizadas')
    fontes = list(ledger.fontes_utilizadas or [])
    if not fontes:
        return _finalizar_gate_sem_evidencia_minima(
            gate,
            parametros,
            'Ledger não disponibiliza fontes utilizadas para validação.',
            'fonte_utilizada',
            ledger.data_referencia,
        )

    usos_por_chave: dict[tuple[object, object], dict[str, object]] = {}
    for indice, fonte in enumerate(fontes):
        entidade_id = _id_entidade(fonte, 'fonte_id', 'pacote_id')
        if not _valor(fonte, 'fonte_id'):
            evidencia = _nova_evidencia(gate.gate_id, _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, 'fonte_id', _valor(fonte, 'fonte_id'), 'identificador de fonte', None, 'bloqueio', 'Fonte utilizada sem identificador.', _referencias(fonte, indice))
            _adicionar_bloqueio(gate, 'fonte_utilizada_sem_identificador', 'Fonte utilizada não possui identificador.', _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, evidencia)
        if _valor(fonte, 'data') is None:
            evidencia = _nova_evidencia(gate.gate_id, None, 'fonte_utilizada', entidade_id, 'data', None, 'data de uso', None, 'bloqueio', 'Fonte utilizada sem data de uso.', _referencias(fonte, indice))
            _adicionar_bloqueio(gate, 'fonte_utilizada_sem_data', 'Fonte utilizada não possui data de uso.', None, 'fonte_utilizada', entidade_id, evidencia)
        for campo in ('valor_referencial', 'valor_disponivel_antes_referencial', 'valor_disponivel_depois_referencial'):
            _validar_valor_nao_negativo(gate, fonte, campo, 'fonte_utilizada', entidade_id, indice, parametros.tolerancia_valor)
        antes = _float_ou_none(_valor(fonte, 'valor_disponivel_antes_referencial'))
        depois = _float_ou_none(_valor(fonte, 'valor_disponivel_depois_referencial'))
        uso = _float_ou_none(_valor(fonte, 'valor_referencial'))
        chave_uso = (_valor(fonte, 'fonte_id'), _valor(fonte, 'data'))
        if chave_uso[0] is not None and uso is not None:
            acumulado = usos_por_chave.setdefault(
                chave_uso,
                {'total': 0.0, 'saldo_antes_maximo': None, 'indice': indice, 'fonte': fonte},
            )
            acumulado['total'] = float(acumulado['total']) + uso
            if antes is not None:
                saldo_antes_maximo = acumulado['saldo_antes_maximo']
                acumulado['saldo_antes_maximo'] = antes if saldo_antes_maximo is None else max(float(saldo_antes_maximo), antes)
        if antes is not None and depois is not None and uso is not None:
            diferenca = round((antes - uso) - depois, 10)
            if abs(diferenca) > parametros.tolerancia_residual:
                evidencia = _nova_evidencia(gate.gate_id, _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, 'saldo_depois', depois, antes - uso, diferenca, 'bloqueio', 'Saldo depois da fonte utilizada é incompatível com saldo antes e valor usado.', _referencias(fonte, indice))
                _adicionar_bloqueio(gate, 'saldo_fonte_utilizada_incompativel', 'Saldo depois de fonte utilizada incompatível.', _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, evidencia)
        if _valor(fonte, 'obrigacao_id') is None and _valor(fonte, 'pacote_id') is None:
            evidencia = _nova_evidencia(gate.gate_id, _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, 'obrigacao_id', None, 'obrigação ou evento associado', None, 'aviso', 'Fonte utilizada sem obrigação ou pacote associado no ledger.', _referencias(fonte, indice))
            _adicionar_aviso(gate, 'fonte_utilizada_sem_associacao', 'Fonte utilizada sem obrigação ou pacote associado no ledger.', _valor(fonte, 'data'), 'fonte_utilizada', entidade_id, evidencia)
        if parametros.validar_liquidez_carencia_quando_disponivel:
            _validar_liquidez_carencia_materializada(gate, fonte, 'fonte_utilizada', entidade_id, indice, _valor(fonte, 'data'))
    for chave, acumulado in usos_por_chave.items():
        saldo_antes_maximo = acumulado.get('saldo_antes_maximo')
        total_usado = float(acumulado.get('total', 0.0))
        if saldo_antes_maximo is not None and total_usado - float(saldo_antes_maximo) > parametros.tolerancia_residual:
            fonte_referencia = acumulado.get('fonte')
            evidencia = _nova_evidencia(
                gate.gate_id,
                chave[1],
                'fonte_utilizada',
                str(chave[0]),
                'soma_usada_por_fonte_data',
                total_usado,
                saldo_antes_maximo,
                round(total_usado - float(saldo_antes_maximo), 10),
                'bloqueio',
                'Soma acumulada de usos por fonte/data excede o saldo disponível antes preservado no ledger.',
                _referencias(fonte_referencia, int(acumulado.get('indice', 0)) if fonte_referencia is not None else None),
            )
            _adicionar_bloqueio(gate, 'sobre_uso_acumulado', 'Usos acumulados excedem saldo disponível antes no ledger.', chave[1], 'fonte_utilizada', str(chave[0]), evidencia)
    gate.resumo['qtd_chaves_fontes_utilizadas_acumuladas'] = len(usos_por_chave)
    return _finalizar_gate(gate, len(fontes))


def _gate_fontes_reservadas(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_fontes_reservadas', 'Fontes reservadas')
    reservas = list(ledger.fontes_reservadas or [])
    if not reservas:
        return _finalizar_gate_sem_evidencia_minima(
            gate,
            parametros,
            'Ledger não disponibiliza fontes reservadas para validação.',
            'fonte_reservada',
            ledger.data_referencia,
        )

    bloqueadas = {(_valor(o, 'obrigacao_id'), _valor(o, 'data')) for o in (ledger.obrigacoes_bloqueadas or []) if _valor(o, 'obrigacao_id')}
    reservas_por_chave: dict[tuple[object, object], dict[str, object]] = {}
    for indice, reserva in enumerate(reservas):
        entidade_id = _id_entidade(reserva, 'fonte_id', 'pacote_id')
        data_reserva = _valor(reserva, 'data')
        if not _valor(reserva, 'fonte_id'):
            evidencia = _nova_evidencia(gate.gate_id, data_reserva, 'fonte_reservada', entidade_id, 'fonte_id', _valor(reserva, 'fonte_id'), 'identificador de fonte', None, 'bloqueio', 'Reserva sem fonte.', _referencias(reserva, indice))
            _adicionar_bloqueio(gate, 'reserva_sem_fonte', 'Reserva não possui fonte associada.', data_reserva, 'fonte_reservada', entidade_id, evidencia)
        if data_reserva is None:
            evidencia = _nova_evidencia(gate.gate_id, None, 'fonte_reservada', entidade_id, 'data', None, 'data da reserva', None, 'bloqueio', 'Reserva sem data.', _referencias(reserva, indice))
            _adicionar_bloqueio(gate, 'reserva_sem_data', 'Reserva não possui data.', None, 'fonte_reservada', entidade_id, evidencia)
        _validar_valor_nao_negativo(gate, reserva, 'valor_reservado_referencial', 'fonte_reservada', entidade_id, indice, parametros.tolerancia_valor)
        antes = _float_ou_none(_valor(reserva, 'valor_disponivel_antes_referencial'))
        depois = _float_ou_none(_valor(reserva, 'valor_disponivel_depois_referencial'))
        reservado = _float_ou_none(_valor(reserva, 'valor_reservado_referencial'))
        chave_reserva = (_valor(reserva, 'fonte_id'), data_reserva)
        if chave_reserva[0] is not None and reservado is not None:
            acumulado = reservas_por_chave.setdefault(
                chave_reserva,
                {'total': 0.0, 'saldo_antes_maximo': None, 'indice': indice, 'reserva': reserva},
            )
            acumulado['total'] = float(acumulado['total']) + reservado
            if antes is not None:
                saldo_antes_maximo = acumulado['saldo_antes_maximo']
                acumulado['saldo_antes_maximo'] = antes if saldo_antes_maximo is None else max(float(saldo_antes_maximo), antes)
        if antes is not None and depois is not None and reservado is not None:
            diferenca = round((antes - reservado) - depois, 10)
            if abs(diferenca) > parametros.tolerancia_residual:
                evidencia = _nova_evidencia(gate.gate_id, data_reserva, 'fonte_reservada', entidade_id, 'saldo_depois', depois, antes - reservado, diferenca, 'bloqueio', 'Saldo depois da reserva é incompatível com saldo antes e valor reservado.', _referencias(reserva, indice))
                _adicionar_bloqueio(gate, 'saldo_reserva_incompativel', 'Saldo depois de reserva incompatível.', data_reserva, 'fonte_reservada', entidade_id, evidencia)
        chave_obrigacao = (_valor(reserva, 'obrigacao_id'), data_reserva)
        if chave_obrigacao in bloqueadas:
            evidencia = _nova_evidencia(gate.gate_id, data_reserva, 'fonte_reservada', entidade_id, 'obrigacao_id', _valor(reserva, 'obrigacao_id'), 'obrigação não bloqueada simultaneamente', None, 'bloqueio', 'Reserva persistida associada a obrigação bloqueada na mesma data.', _referencias(reserva, indice))
            _adicionar_bloqueio(gate, 'reserva_para_obrigacao_bloqueada', 'Reserva associada a obrigação bloqueada identificável no ledger.', data_reserva, 'fonte_reservada', entidade_id, evidencia)

        if parametros.validar_liquidez_carencia_quando_disponivel:
            _validar_liquidez_carencia_materializada(gate, reserva, 'fonte_reservada', entidade_id, indice, data_reserva)

    for chave, acumulado in reservas_por_chave.items():
        saldo_antes_maximo = acumulado.get('saldo_antes_maximo')
        total_reservado = float(acumulado.get('total', 0.0))
        if saldo_antes_maximo is not None and total_reservado - float(saldo_antes_maximo) > parametros.tolerancia_residual:
            reserva_referencia = acumulado.get('reserva')
            evidencia = _nova_evidencia(
                gate.gate_id,
                chave[1],
                'fonte_reservada',
                str(chave[0]),
                'soma_reservada_por_fonte_data',
                total_reservado,
                saldo_antes_maximo,
                round(total_reservado - float(saldo_antes_maximo), 10),
                'bloqueio',
                'Soma acumulada de reservas por fonte/data excede o saldo disponível antes preservado no ledger.',
                _referencias(reserva_referencia, int(acumulado.get('indice', 0)) if reserva_referencia is not None else None),
            )
            _adicionar_bloqueio(gate, 'sobre_reserva_acumulada', 'Reservas acumuladas excedem saldo disponível antes no ledger.', chave[1], 'fonte_reservada', str(chave[0]), evidencia)

    return _finalizar_gate(gate, len(reservas))

def _gate_saldos_residuais(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_saldos_residuais', 'Saldos residuais')
    saldos_por_data = dict(ledger.saldos_referenciais_por_data or {})
    movimentos = list(ledger.fontes_utilizadas or []) + list(ledger.fontes_reservadas or [])
    movimentos_por_chave: dict[tuple[object, object], dict[str, object]] = {}
    saldos_depois_movimentos: dict[tuple[object, object], dict[str, object]] = {}
    for indice_movimento, movimento in enumerate(movimentos):
        chave = (_valor(movimento, 'fonte_id'), _valor(movimento, 'data'))
        if chave[0] is None or chave[1] is None:
            continue
        movimentos_por_chave.setdefault(chave, {'movimento': movimento, 'indice': indice_movimento})
        saldo_depois = _float_ou_none(_valor(movimento, 'valor_disponivel_depois_referencial'))
        if saldo_depois is None:
            continue
        atual = saldos_depois_movimentos.get(chave)
        if atual is None or saldo_depois < float(atual['saldo_depois']):
            saldos_depois_movimentos[chave] = {
                'saldo_depois': saldo_depois,
                'movimento': movimento,
                'indice': indice_movimento,
            }

    if not saldos_por_data:
        if not movimentos_por_chave:
            return _finalizar_gate_sem_evidencia_minima(
                gate,
                parametros,
                'Ledger não disponibiliza saldos referenciais por data para validação.',
                'saldo_referencial',
                ledger.data_referencia,
            )
        for chave, info_movimento in movimentos_por_chave.items():
            evidencia = _nova_evidencia(
                gate.gate_id,
                chave[1],
                'saldo_referencial',
                str(chave[0]),
                'saldos_referenciais_por_data',
                None,
                'saldo residual correspondente para fonte/data movimentada',
                None,
                'bloqueio',
                'Fonte movimentada não possui saldo residual correspondente no ledger.',
                _referencias(info_movimento.get('movimento'), int(info_movimento.get('indice', 0))),
            )
            _adicionar_bloqueio(gate, 'saldo_residual_ausente_para_fonte_movimentada', 'Fonte movimentada sem saldo residual correspondente no ledger.', chave[1], 'saldo_referencial', str(chave[0]), evidencia)
        gate.resumo['qtd_fontes_movimentadas_sem_saldo'] = len(movimentos_por_chave)
        return _finalizar_gate(gate, 0)

    chaves_saldos: set[tuple[object, object]] = set()
    qtd_saldos = 0
    for data_ref, saldos in saldos_por_data.items():
        if not saldos:
            evidencia = _nova_evidencia(gate.gate_id, data_ref, 'saldo_referencial', None, 'saldos_referenciais_por_data', saldos, 'lista não vazia quando chave existe', None, 'aviso', 'Data de saldo referencial sem itens no ledger.', {'data_ledger': data_ref, 'origem_formal': _ORIGEM_FORMAL})
            _adicionar_aviso(gate, 'data_saldo_sem_itens', 'Data de saldo referencial sem itens no ledger.', data_ref, 'saldo_referencial', None, evidencia)
        for indice, saldo in enumerate(saldos):
            qtd_saldos += 1
            entidade_id = _id_entidade(saldo, 'fonte_id', 'pacote_id')
            data_saldo = _valor(saldo, 'data', data_ref)
            chave_saldo = (_valor(saldo, 'fonte_id'), data_saldo)
            if chave_saldo[0] is not None and chave_saldo[1] is not None:
                chaves_saldos.add(chave_saldo)
            valor_disponivel = _float_ou_none(_valor(saldo, 'valor_disponivel_referencial'))
            if valor_disponivel is not None and valor_disponivel < -abs(parametros.tolerancia_residual):
                evidencia = _nova_evidencia(gate.gate_id, data_saldo, 'saldo_referencial', entidade_id, 'valor_disponivel_referencial', valor_disponivel, '>= 0', valor_disponivel, 'bloqueio', 'Saldo referencial negativo além da tolerância residual.', _referencias(saldo, indice))
                _adicionar_bloqueio(gate, 'saldo_referencial_negativo_material', 'Saldo referencial negativo além da tolerância.', data_saldo, 'saldo_referencial', entidade_id, evidencia)
            reservado = _float_ou_none(_valor(saldo, 'valor_reservado_acumulado_referencial'))
            if reservado is not None and reservado < -abs(parametros.tolerancia_residual):
                evidencia = _nova_evidencia(gate.gate_id, data_saldo, 'saldo_referencial', entidade_id, 'valor_reservado_acumulado_referencial', reservado, '>= 0', reservado, 'bloqueio', 'Reservado acumulado negativo além da tolerância residual.', _referencias(saldo, indice))
                _adicionar_bloqueio(gate, 'reservado_acumulado_negativo_material', 'Reservado acumulado negativo além da tolerância.', data_saldo, 'saldo_referencial', entidade_id, evidencia)
            movimento_restritivo = saldos_depois_movimentos.get(chave_saldo)
            if valor_disponivel is not None and movimento_restritivo is not None:
                saldo_depois_movimento = float(movimento_restritivo['saldo_depois'])
                diferenca = round(valor_disponivel - saldo_depois_movimento, 10)
                if abs(diferenca) > parametros.tolerancia_residual:
                    evidencia = _nova_evidencia(
                        gate.gate_id,
                        data_saldo,
                        'saldo_referencial',
                        entidade_id,
                        'valor_disponivel_referencial',
                        valor_disponivel,
                        saldo_depois_movimento,
                        diferenca,
                        'bloqueio',
                        'Saldo referencial por fonte/data diverge do menor saldo depois materializado nos movimentos de fonte.',
                        {
                            **_referencias(saldo, indice),
                            'criterio_movimentos_multiplos': 'menor_valor_disponivel_depois_referencial',
                            'movimento_restritivo': _dict_referencia(movimento_restritivo.get('movimento')),
                        },
                    )
                    _adicionar_bloqueio(gate, 'saldo_residual_divergente_movimento_fonte', 'Saldo residual diverge do saldo depois mais restritivo dos movimentos de fonte.', data_saldo, 'saldo_referencial', entidade_id, evidencia)
    chaves_movimentos_sem_saldo = set(movimentos_por_chave) - chaves_saldos
    for chave in chaves_movimentos_sem_saldo:
        info_movimento = movimentos_por_chave[chave]
        evidencia = _nova_evidencia(
            gate.gate_id,
            chave[1],
            'saldo_referencial',
            str(chave[0]),
            'saldos_referenciais_por_data',
            None,
            'saldo residual correspondente para fonte/data movimentada',
            None,
            'bloqueio',
            'Fonte movimentada não possui saldo residual correspondente no ledger.',
            _referencias(info_movimento.get('movimento'), int(info_movimento.get('indice', 0))),
        )
        _adicionar_bloqueio(gate, 'saldo_residual_ausente_para_fonte_movimentada', 'Fonte movimentada sem saldo residual correspondente no ledger.', chave[1], 'saldo_referencial', str(chave[0]), evidencia)
    gate.resumo['criterio_movimentos_multiplos'] = 'menor_valor_disponivel_depois_referencial'
    gate.resumo['qtd_fontes_movimentadas_sem_saldo'] = len(chaves_movimentos_sem_saldo)
    return _finalizar_gate(gate, qtd_saldos)

def _gate_switchings(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_switchings', 'Switchings materializados no ledger')
    switchings = list(ledger.switchings_escolhidos or [])
    if not switchings:
        return _finalizar_gate_sem_evidencia_minima(
            gate,
            parametros,
            'Ledger não disponibiliza switchings escolhidos para validação.',
            'switching',
            ledger.data_referencia,
        )

    for indice, switching in enumerate(switchings):
        entidade_id = _id_entidade(switching, 'switching_id', 'pacote_id')
        if not _valor(switching, 'lote_origem_id'):
            evidencia = _nova_evidencia(gate.gate_id, _valor(switching, 'data'), 'switching', entidade_id, 'lote_origem_id', _valor(switching, 'lote_origem_id'), 'origem quando disponível', None, 'aviso', 'Switching sem origem materializada no ledger.', _referencias(switching, indice))
            _adicionar_aviso(gate, 'switching_sem_origem', 'Switching sem origem materializada no ledger.', _valor(switching, 'data'), 'switching', entidade_id, evidencia)
        if not _valor(switching, 'lote_destino_id'):
            evidencia = _nova_evidencia(gate.gate_id, _valor(switching, 'data'), 'switching', entidade_id, 'lote_destino_id', _valor(switching, 'lote_destino_id'), 'destino quando disponível', None, 'aviso', 'Switching sem destino materializado no ledger.', _referencias(switching, indice))
            _adicionar_aviso(gate, 'switching_sem_destino', 'Switching sem destino materializada no ledger.', _valor(switching, 'data'), 'switching', entidade_id, evidencia)
        _validar_valor_nao_negativo(gate, switching, 'valor_liquido_migrado_referencial', 'switching', entidade_id, indice, parametros.tolerancia_valor)
        status = str(_valor(switching, 'status', '') or '').lower()
        if 'candidato' in status and 'escolhido' not in status:
            evidencia = _nova_evidencia(gate.gate_id, _valor(switching, 'data'), 'switching', entidade_id, 'status', status, 'switching escolhido/materializado', None, 'bloqueio', 'Switching do ledger parece ser apenas candidato não materializado.', _referencias(switching, indice))
            _adicionar_bloqueio(gate, 'switching_candidato_nao_materializado', 'Switching escolhido não pode ser apenas candidato.', _valor(switching, 'data'), 'switching', entidade_id, evidencia)
        if _valor(switching, 'lote_origem_id') and _valor(switching, 'lote_destino_id') and _valor(switching, 'lote_origem_id') == _valor(switching, 'lote_destino_id'):
            evidencia = _nova_evidencia(gate.gate_id, _valor(switching, 'data'), 'switching', entidade_id, 'lote_destino_id', _valor(switching, 'lote_destino_id'), 'diferente da origem', None, 'bloqueio', 'Switching possui origem e destino iguais.', _referencias(switching, indice))
            _adicionar_bloqueio(gate, 'switching_origem_destino_iguais', 'Switching possui origem e destino iguais.', _valor(switching, 'data'), 'switching', entidade_id, evidencia)
    return _finalizar_gate(gate, len(switchings))


def _gate_dupla_contagem(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_dupla_contagem', 'Dupla contagem evidente')
    cobertas: dict[tuple[object, object], Any] = {}
    chaves_cobertas_vistas: set[tuple[object, object]] = set()
    for indice, coberta in enumerate(ledger.obrigacoes_cobertas or []):
        chave = (_valor(coberta, 'obrigacao_id'), _valor(coberta, 'data'))
        if not chave[0]:
            continue
        if chave in chaves_cobertas_vistas:
            evidencia = _nova_evidencia(gate.gate_id, _valor(coberta, 'data'), 'obrigacao_coberta', str(chave[0]), 'obrigacao_id/data', chave, 'obrigação coberta única por identificador e data', None, 'bloqueio', 'Obrigação coberta duplicada com mesmo identificador e data.', _referencias(coberta, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_duplicada', 'Obrigação coberta duplicada no ledger antes de qualquer deduplicação.', _valor(coberta, 'data'), 'obrigacao_coberta', str(chave[0]), evidencia)
        else:
            chaves_cobertas_vistas.add(chave)
            cobertas[chave] = coberta

    for indice, bloqueada in enumerate(ledger.obrigacoes_bloqueadas or []):
        chave = (_valor(bloqueada, 'obrigacao_id'), _valor(bloqueada, 'data'))
        if chave[0] and chave in cobertas and 'parcial' not in str(_valor(bloqueada, 'motivo', '')).lower():
            evidencia = _nova_evidencia(gate.gate_id, _valor(bloqueada, 'data'), 'obrigacao', str(chave[0]), 'obrigacao_id/data', chave, 'não simultânea coberta e bloqueada', None, 'bloqueio', 'Mesma obrigação aparece como coberta e bloqueada sem motivo explícito de parcialidade.', _referencias(bloqueada, indice))
            _adicionar_bloqueio(gate, 'obrigacao_coberta_e_bloqueada', 'Obrigação aparece simultaneamente como coberta e bloqueada.', _valor(bloqueada, 'data'), 'obrigacao', str(chave[0]), evidencia)

    usos_por_chave: dict[tuple[object, object], float] = {}
    for fonte in ledger.fontes_utilizadas or []:
        chave = (_valor(fonte, 'fonte_id'), _valor(fonte, 'data'))
        usos_por_chave[chave] = usos_por_chave.get(chave, 0.0) + (_float_ou_none(_valor(fonte, 'valor_referencial')) or 0.0)
    reservas_por_chave: dict[tuple[object, object], float] = {}
    for reserva in ledger.fontes_reservadas or []:
        chave = (_valor(reserva, 'fonte_id'), _valor(reserva, 'data'))
        reservas_por_chave[chave] = reservas_por_chave.get(chave, 0.0) + (_float_ou_none(_valor(reserva, 'valor_reservado_referencial')) or 0.0)
    for chave, valor_uso in usos_por_chave.items():
        valor_reserva = reservas_por_chave.get(chave)
        if chave[0] and valor_reserva is not None and abs(valor_uso - valor_reserva) > parametros.tolerancia_residual:
            evidencia = _nova_evidencia(gate.gate_id, chave[1], 'fonte', str(chave[0]), 'uso_reserva_mesma_data', {'uso': valor_uso, 'reserva': valor_reserva}, 'compatível', round(valor_uso - valor_reserva, 10), 'bloqueio', 'Fonte usada e reservada com valores materialmente incompatíveis na mesma data.', {'fonte_id': chave[0], 'data': chave[1], 'origem_formal': _ORIGEM_FORMAL})
            _adicionar_bloqueio(gate, 'fonte_usada_reservada_incompativel', 'Fonte usada e reservada de modo incompatível na mesma data.', chave[1], 'fonte', str(chave[0]), evidencia)

    eventos_vistos: set[tuple[object, object, object]] = set()
    for indice, evento in enumerate(ledger.eventos or []):
        chave = (_id_entidade(evento, 'pacote_id'), _valor(evento, 'tipo'), _valor(evento, 'data'))
        if chave[0] is not None and chave in eventos_vistos:
            evidencia = _nova_evidencia(gate.gate_id, _valor(evento, 'data'), 'evento', str(chave[0]), 'pacote_id/tipo/data', chave, 'evento único', None, 'bloqueio', 'Evento duplicado com mesmo identificador, tipo e data.', _referencias(evento, indice))
            _adicionar_bloqueio(gate, 'evento_duplicado', 'Evento duplicado no ledger.', _valor(evento, 'data'), 'evento', str(chave[0]), evidencia)
        if chave[0] is not None:
            eventos_vistos.add(chave)

    gate.resumo['qtd_chaves_obrigacoes_cobertas'] = len(chaves_cobertas_vistas)
    gate.resumo['qtd_chaves_fontes_utilizadas'] = len(usos_por_chave)
    gate.resumo['qtd_chaves_fontes_reservadas'] = len(reservas_por_chave)
    gate.resumo['qtd_eventos_avaliados'] = len(ledger.eventos or [])
    total = len(ledger.obrigacoes_cobertas or []) + len(ledger.obrigacoes_bloqueadas or []) + len(usos_por_chave) + len(reservas_por_chave) + len(ledger.eventos or [])
    return _finalizar_gate(gate, total)

def _gate_bloqueios_prontidao(ledger: LedgerTemporalCanonico, gates_anteriores: list[GateValidacaoNucleo]) -> GateValidacaoNucleo:
    gate = _novo_gate('gate_bloqueios_prontidao', 'Bloqueios e prontidão para a Etapa 8')
    qtd_bloqueios_gates = sum(len(g.bloqueios) for g in gates_anteriores)
    auditoria_ok = bool(ledger.auditoria and ledger.auditoria.ok)
    pronto = auditoria_ok and not ledger.bloqueios and qtd_bloqueios_gates == 0
    gate.evidencias.append(
        _nova_evidencia(
            gate.gate_id,
            ledger.data_referencia,
            'prontidao',
            None,
            'pronto_para_etapa8',
            pronto,
            True,
            None,
            'info' if pronto else 'bloqueio',
            'Prontidão calculada exclusivamente a partir de auditoria e bloqueios já materializados no ledger/gates.',
            {'qtd_bloqueios_ledger': len(ledger.bloqueios or []), 'qtd_bloqueios_gates': qtd_bloqueios_gates, 'auditoria_ok': auditoria_ok},
        )
    )
    if ledger.bloqueios:
        _adicionar_bloqueio(gate, 'ledger_com_bloqueios_impeditivos', 'Ledger possui bloqueios impeditivos preservados.', ledger.data_referencia, 'ledger', None)
    if not auditoria_ok:
        _adicionar_bloqueio(gate, 'auditoria_ledger_nao_ok', 'Auditoria do ledger não está aprovada.', ledger.data_referencia, 'auditoria_ledger', None)
    if qtd_bloqueios_gates:
        _adicionar_bloqueio(gate, 'gates_com_bloqueios_impeditivos', 'Há bloqueios impeditivos gerados pelos gates de núcleo.', ledger.data_referencia, 'gates_validacao_nucleo', None)
    gate.resumo['pronto_para_etapa8'] = pronto
    return _finalizar_gate(gate)


def validar_gates_nucleo(
    ledger: LedgerTemporalCanonico,
    parametros: ParametrosGatesValidacaoNucleo | None = None,
) -> ResultadoGatesValidacaoNucleo:
    parametros = parametros or ParametrosGatesValidacaoNucleo()
    if not isinstance(ledger, LedgerTemporalCanonico):
        gate = GateValidacaoNucleo(
            gate_id='gate_origem_exclusiva_ledger',
            nome='Origem exclusiva no ledger temporal canônico',
            executado=True,
            aprovado=False,
            nao_aplicavel=False,
            motivo_nao_aplicavel=None,
        )
        evidencia = _nova_evidencia(gate.gate_id, None, 'entrada', None, 'tipo', type(ledger).__name__, _ORIGEM_FORMAL, None, 'bloqueio', 'Objeto recebido não é o ledger temporal canônico.', {'origem_formal': _ORIGEM_FORMAL})
        _adicionar_bloqueio(gate, 'entrada_nao_ledger_temporal_canonico', 'Entrada formal da Etapa 7 deve ser o ledger temporal canônico.', None, 'entrada', None, evidencia)
        gate = _finalizar_gate(gate)
        resumo = ResumoGatesValidacaoNucleo(
            qtd_gates=1,
            qtd_gates_executados=1,
            qtd_gates_aprovados=0,
            qtd_gates_reprovados=1,
            qtd_gates_nao_aplicaveis=0,
            qtd_bloqueios=len(gate.bloqueios),
            qtd_avisos=0,
            qtd_obrigacoes_cobertas=0,
            qtd_obrigacoes_bloqueadas=0,
            qtd_fontes_utilizadas=0,
            qtd_fontes_reservadas=0,
            qtd_switchings=0,
            pronto_para_etapa8=False,
        )
        return ResultadoGatesValidacaoNucleo(False, False, _ORIGEM_FORMAL, [gate], gate.bloqueios, [], gate.evidencias, resumo, {'entrada_formal_exclusiva': _ORIGEM_FORMAL})

    gates: list[GateValidacaoNucleo] = []
    gates.append(_gate_origem_exclusiva_ledger(ledger))
    gates.append(_gate_auditoria_ledger(ledger))
    gates.append(_gate_obrigacoes_cobertas(ledger, parametros))
    gates.append(_gate_obrigacoes_bloqueadas(ledger, parametros))
    gates.append(_gate_fontes_utilizadas(ledger, parametros))
    gates.append(_gate_fontes_reservadas(ledger, parametros))
    gates.append(_gate_saldos_residuais(ledger, parametros))
    gates.append(_gate_switchings(ledger, parametros))
    gates.append(_gate_dupla_contagem(ledger, parametros))
    gates.append(_gate_bloqueios_prontidao(ledger, gates))

    bloqueios = [bloqueio for gate in gates for bloqueio in gate.bloqueios]
    avisos = [aviso for gate in gates for aviso in gate.avisos]
    evidencias = [evidencia for gate in gates for evidencia in gate.evidencias]
    pronto_para_etapa8 = not bloqueios and bool(ledger.auditoria and ledger.auditoria.ok)
    resumo = ResumoGatesValidacaoNucleo(
        qtd_gates=len(gates),
        qtd_gates_executados=sum(1 for gate in gates if gate.executado),
        qtd_gates_aprovados=sum(1 for gate in gates if gate.aprovado),
        qtd_gates_reprovados=sum(1 for gate in gates if not gate.aprovado and not gate.nao_aplicavel),
        qtd_gates_nao_aplicaveis=sum(1 for gate in gates if gate.nao_aplicavel),
        qtd_bloqueios=len(bloqueios),
        qtd_avisos=len(avisos),
        qtd_obrigacoes_cobertas=len(ledger.obrigacoes_cobertas or []),
        qtd_obrigacoes_bloqueadas=len(ledger.obrigacoes_bloqueadas or []),
        qtd_fontes_utilizadas=len(ledger.fontes_utilizadas or []),
        qtd_fontes_reservadas=len(ledger.fontes_reservadas or []),
        qtd_switchings=len(ledger.switchings_escolhidos or []),
        pronto_para_etapa8=pronto_para_etapa8,
    )
    return ResultadoGatesValidacaoNucleo(
        ok=not bloqueios,
        pronto_para_etapa8=pronto_para_etapa8,
        origem_formal=_ORIGEM_FORMAL,
        gates=gates,
        bloqueios=bloqueios,
        avisos=avisos,
        evidencias=evidencias,
        resumo=resumo,
        metadados={
            'artefato': 'ResultadoGatesValidacaoNucleo',
            'entrada_formal_exclusiva': _ORIGEM_FORMAL,
            'origem_formal': _ORIGEM_FORMAL,
            'sem_mutacao_ledger': True,
            'sem_consulta_fontes_externas': True,
            'parametros': asdict(parametros),
        },
    )


__all__ = [
    'AvisoGateNucleo',
    'BloqueioGateNucleo',
    'EvidenciaGateNucleo',
    'GateValidacaoNucleo',
    'ParametrosGatesValidacaoNucleo',
    'ResultadoGatesValidacaoNucleo',
    'ResumoGatesValidacaoNucleo',
    'validar_gates_nucleo',
]
