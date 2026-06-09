from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime, timezone
from typing import Any

from nucleo.saida_canonica_oficial import SaidaCanonicaOficial


_ORIGEM_FORMAL = 'SaidaCanonicaOficial'
_ARTEFATO = 'PacoteSaidaObservavelOficial'
_VERSAO_SCHEMA = 'ETAPA9-COMPLETA-01'


@dataclass(slots=True)
class LacunaRenderizacaoSaidaObservavel:
    codigo: str
    mensagem: str
    severidade: str = 'lacuna'
    origem: str = 'Etapa9'
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoSaidaObservavelOficial:
    qtd_eventos: int
    qtd_obrigacoes_cobertas: int
    qtd_obrigacoes_bloqueadas: int
    qtd_fontes_utilizadas: int
    qtd_fontes_reservadas: int
    qtd_switchings_escolhidos: int
    qtd_switchings_realizados_operacionais: int
    qtd_lotes_pos_switching_materializados: int
    qtd_destinos_sobras_recebidos: int
    qtd_lotes_futuros_materializados: int
    qtd_saldos_referenciais_datas: int
    qtd_avisos: int
    qtd_bloqueios: int
    qtd_lacunas_renderizacao: int
    pronto_para_console: bool
    pronto_para_xlsx: bool
    preparado: bool


@dataclass(slots=True)
class BlocoConsoleSaidaObservavel:
    resumo_operacional: dict[str, Any] = field(default_factory=dict)
    ultimos_pagamentos: list[dict[str, Any]] = field(default_factory=list)
    pagamentos_data_referencia: list[dict[str, Any]] = field(default_factory=list)
    proximos_pagamentos: list[dict[str, Any]] = field(default_factory=list)
    pagamentos_por_fonte: list[dict[str, Any]] = field(default_factory=list)
    fontes_utilizadas: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_cobertas: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_bloqueadas: list[dict[str, Any]] = field(default_factory=list)
    switchings_escolhidos: list[dict[str, Any]] = field(default_factory=list)
    switchings_realizados_operacionais: list[dict[str, Any]] = field(default_factory=list)
    switchings_metricas: list[dict[str, Any]] = field(default_factory=list)
    switchings_amostra: list[dict[str, Any]] = field(default_factory=list)
    switchings_resumo_operacional: list[dict[str, Any]] = field(default_factory=list)
    lotes_pos_switching_materializados: list[dict[str, Any]] = field(default_factory=list)
    saldos_referenciais: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    destinos_sobras_recebidos: list[dict[str, Any]] = field(default_factory=list)
    lotes_futuros_materializados: list[dict[str, Any]] = field(default_factory=list)
    avisos: list[Any] = field(default_factory=list)
    bloqueios: list[dict[str, Any]] = field(default_factory=list)
    lacunas_renderizacao: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class BlocoXLSXSaidaObservavel:
    abas: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    metadados_abas: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuditoriaSaidaObservavelOficial:
    entrada_tipo: str
    entrada_valida: bool
    origem_exclusiva: str
    blocos_console_preparados: bool
    blocos_xlsx_preparados: bool
    qtd_lacunas_renderizacao: int
    qtd_bloqueios_preservados: int
    qtd_avisos_preservados: int
    sem_reotimizacao: bool = True
    sem_revaloracao: bool = True
    sem_alteracao_decisao: bool = True
    sem_consulta_fontes_externas: bool = True
    sem_integracao_runtime: bool = False
    sem_alteracao_console: bool = False
    sem_alteracao_xlsx: bool = False


@dataclass(slots=True)
class PacoteSaidaObservavelOficial:
    ok: bool
    preparado: bool
    status: str
    data_referencia: date | None
    origem_formal: str
    saida_origem: str
    resumo: ResumoSaidaObservavelOficial
    bloco_console: BlocoConsoleSaidaObservavel
    bloco_xlsx: BlocoXLSXSaidaObservavel
    lacunas_renderizacao: list[LacunaRenderizacaoSaidaObservavel] = field(default_factory=list)
    auditoria: AuditoriaSaidaObservavelOficial | None = None
    metadados: dict[str, Any] = field(default_factory=dict)


def _valor(objeto: Any, campo: str, padrao: Any = None) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(campo, padrao)
    return getattr(objeto, campo, padrao)


def _snapshot_item(valor: Any) -> dict[str, Any]:
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return dict(valor)
    if is_dataclass(valor):
        return asdict(valor)
    return {'valor': valor}


def _snapshot_lista(valores: Any) -> list[dict[str, Any]]:
    if valores is None:
        return []
    return [_snapshot_item(valor) for valor in list(valores)]


def _snapshot_avisos(valores: Any) -> list[Any]:
    if valores is None:
        return []
    return [asdict(valor) if is_dataclass(valor) else valor for valor in list(valores)]


def _chave_data(data_ref: Any) -> str:
    if isinstance(data_ref, date):
        return data_ref.isoformat()
    return str(data_ref)


def _texto_material(valor: Any) -> str:
    texto = str(valor or '').strip()
    if texto.lower() in {'', 'nan', 'none', 'n/d', 'nd'}:
        return ''
    return texto


def _fonte_operacional_renderizavel(item: dict[str, Any]) -> str:
    return (
        _texto_material(item.get('lote_id_operacional'))
        or _texto_material((item.get('metadados') or {}).get('lote_id_operacional'))
    )


def _enriquecer_fonte_identificacao(item: dict[str, Any]) -> dict[str, Any]:
    saida = dict(item)
    fonte_id = _texto_material(saida.get('fonte_id'))
    fonte_id_tecnico = (
        _texto_material(saida.get('fonte_id_tecnico'))
        or _texto_material((saida.get('metadados') or {}).get('fonte_id_tecnico'))
        or fonte_id
    )
    lote_id_operacional = _fonte_operacional_renderizavel(saida)
    if fonte_id_tecnico:
        saida['fonte_id_tecnico'] = fonte_id_tecnico
    if lote_id_operacional:
        saida['lote_id_operacional'] = lote_id_operacional
        saida['fonte_nome_operacional'] = lote_id_operacional
    else:
        saida['lote_id_operacional_ausente'] = True
        saida['fonte_nome_operacional'] = 'lote_id_operacional_ausente'
    return saida


def _indice_nomes_fontes(fontes: list[dict[str, Any]]) -> dict[str, str]:
    indice: dict[str, str] = {}
    for item in fontes:
        fonte_id = _texto_material(item.get('fonte_id'))
        if not fonte_id:
            continue
        indice[fonte_id] = _fonte_operacional_renderizavel(item) or 'lote_id_operacional_ausente'
    return indice


def _tipo_pacote_legivel(tipo_pacote: str) -> str:
    mapa = {
        'pagamento_com_recebido': 'pagamento com recebido',
        'pagamento_combinacao_fontes': 'pagamento com combinação de fontes',
        'pagamento_fonte_unica': 'pagamento com fonte única',
        'sem_cobertura': 'sem cobertura',
        'sem_obrigacao': 'sem obrigação',
        'switching_integral_simples': 'switching integral',
        'switching_integral_agregado': 'switching integral agregado',
        'switching_mais_pagamento': 'switching mais pagamento',
        'pay_only': 'pagamento',
        'switch_then_pay': 'switching antes do pagamento',
        'pay_then_switch': 'pagamento antes do switching',
        'switch_only': 'switching',
        'no_action': 'sem ação',
    }
    return mapa.get(tipo_pacote, tipo_pacote.replace('_', ' '))


def _nome_pacote_operacional(pacote_id: Any, fontes_operacionais: list[str] | None = None) -> str:
    pacote_txt = _texto_material(pacote_id)
    if not pacote_txt:
        return 'sem pacote válido'
    partes = pacote_txt.split('::')
    if len(partes) >= 2:
        nome = f'{partes[0]} | {_tipo_pacote_legivel(partes[1])}'
    else:
        nome = pacote_txt
    fontes = [f for f in (fontes_operacionais or []) if _texto_material(f)]
    if len(fontes) == 1:
        nome = f'{nome} | {fontes[0]}'
    elif len(fontes) > 1:
        nome = f'{nome} | {len(fontes)} fontes'
    return nome


def _enriquecer_obrigacao_identificacao(item: dict[str, Any], nomes_fontes: dict[str, str]) -> dict[str, Any]:
    saida = dict(item)
    fontes_tecnicas = [
        str(f).strip()
        for f in list(saida.get('fontes_referenciadas') or [])
        if str(f).strip()
    ]
    fontes_operacionais = [
        nomes_fontes.get(fonte) or 'lote_id_operacional_ausente'
        for fonte in fontes_tecnicas
    ]
    saida['fontes_referenciadas_tecnicas'] = fontes_tecnicas
    saida['fontes_referenciadas_operacionais'] = fontes_operacionais
    saida['pacote_id_tecnico'] = saida.get('pacote_id')
    saida['pacote_nome_operacional'] = _nome_pacote_operacional(saida.get('pacote_id'), fontes_operacionais)
    return saida


def _enriquecer_switching_identificacao(item: dict[str, Any]) -> dict[str, Any]:
    saida = dict(item)
    origem = _texto_material(saida.get('lote_origem_id') or saida.get('lote_origem'))
    destino = _texto_material(saida.get('lote_destino_id') or saida.get('lote_destino'))
    if origem or destino:
        saida['switching_nome_operacional'] = f"{origem or 'origem n/d'} -> {destino or 'destino n/d'}"
    else:
        saida['switching_nome_operacional'] = _texto_material(saida.get('switching_id')) or 'switching sem identificação'
    return saida


def _enriquecer_identificacao_operacional_blocos(blocos: dict[str, Any]) -> dict[str, Any]:
    saida = dict(blocos)
    fontes_utilizadas = [
        _enriquecer_fonte_identificacao(item)
        for item in list(saida.get('fontes_utilizadas') or [])
    ]
    fontes_reservadas = [
        _enriquecer_fonte_identificacao(item)
        for item in list(saida.get('fontes_reservadas') or [])
    ]
    nomes_fontes = _indice_nomes_fontes(fontes_reservadas + fontes_utilizadas)
    saida['fontes_utilizadas'] = fontes_utilizadas
    saida['fontes_reservadas'] = fontes_reservadas
    saida['obrigacoes_cobertas'] = [
        _enriquecer_obrigacao_identificacao(item, nomes_fontes)
        for item in list(saida.get('obrigacoes_cobertas') or [])
    ]
    saida['obrigacoes_bloqueadas'] = [
        _enriquecer_obrigacao_identificacao(item, nomes_fontes)
        for item in list(saida.get('obrigacoes_bloqueadas') or [])
    ]
    saida['switchings_escolhidos'] = [
        _enriquecer_switching_identificacao(item)
        for item in list(saida.get('switchings_escolhidos') or [])
    ]
    saida['switchings_realizados_operacionais'] = [
        _enriquecer_switching_identificacao(item)
        for item in list(saida.get('switchings_realizados_operacionais') or [])
    ]
    return saida


def _snapshot_saldos(saldos_por_data: Any) -> dict[str, list[dict[str, Any]]]:
    if not saldos_por_data:
        return {}
    return {
        _chave_data(data_ref): _snapshot_lista(saldos)
        for data_ref, saldos in dict(saldos_por_data).items()
    }


def _nova_lacuna(
    codigo: str,
    mensagem: str,
    referencias: dict[str, Any] | None = None,
) -> LacunaRenderizacaoSaidaObservavel:
    return LacunaRenderizacaoSaidaObservavel(
        codigo=codigo,
        mensagem=mensagem,
        referencias=referencias or {},
    )


def validar_entrada_saida_observavel(saida: SaidaCanonicaOficial) -> list[LacunaRenderizacaoSaidaObservavel]:
    if not isinstance(saida, SaidaCanonicaOficial):
        return [
            _nova_lacuna(
                'entrada_nao_saida_canonica_oficial',
                'Entrada da Etapa 9 deve ser SaidaCanonicaOficial.',
                {'tipo_recebido': type(saida).__name__},
            )
        ]
    return []


def extrair_blocos_saida_canonica(saida: SaidaCanonicaOficial) -> dict[str, Any]:
    return {
        'data_referencia': saida.data_referencia,
        'status_saida_canonica': saida.status,
        'saida_canonica_preparada': saida.preparada,
        'saida_canonica_ok': saida.ok,
        'eventos': _snapshot_lista(saida.eventos),
        'obrigacoes_cobertas': _snapshot_lista(saida.obrigacoes_cobertas),
        'obrigacoes_bloqueadas': _snapshot_lista(saida.obrigacoes_bloqueadas),
        'pagamentos_historicos_realizados': _snapshot_lista(getattr(saida, 'pagamentos_historicos_realizados', [])),
        'fontes_utilizadas': _snapshot_lista(saida.fontes_utilizadas),
        'fontes_reservadas': _snapshot_lista(saida.fontes_reservadas),
        'switchings_escolhidos': _snapshot_lista(saida.switchings_escolhidos),
        'switchings_realizados_operacionais': _snapshot_lista(getattr(saida, 'switchings_realizados_operacionais', [])),
        'lotes_pos_switching_materializados': _snapshot_lista(getattr(saida, 'lotes_pos_switching_materializados', [])),
        'saldos_referenciais': _snapshot_saldos(saida.saldos_referenciais_por_data),
        'destinos_sobras_recebidos': _snapshot_lista(getattr(saida, 'destinos_sobras_recebidos', [])),
        'lotes_futuros_materializados': _snapshot_lista(getattr(saida, 'lotes_futuros_materializados', [])),
        'bloqueios_ledger': _snapshot_lista(saida.bloqueios_ledger),
        'bloqueios_gates': _snapshot_lista(saida.bloqueios_gates),
        'bloqueios_preparacao': _snapshot_lista(saida.bloqueios_preparacao),
        'avisos_ledger': _snapshot_avisos(saida.avisos_ledger),
        'avisos_gates': _snapshot_avisos(saida.avisos_gates),
        'evidencias_gates': _snapshot_lista(saida.evidencias_gates),
        'resumo_saida_canonica': _snapshot_item(saida.resumo),
        'metadados_saida_canonica': dict(saida.metadados or {}),
    }


def preparar_resumo_operacional_observavel(blocos: dict[str, Any]) -> dict[str, Any]:
    return {
        'data_referencia': blocos['data_referencia'],
        'status_saida_canonica': blocos['status_saida_canonica'],
        'saida_canonica_preparada': blocos['saida_canonica_preparada'],
        'saida_canonica_ok': blocos['saida_canonica_ok'],
        'qtd_eventos': len(blocos['eventos']),
        'qtd_obrigacoes_cobertas': len(blocos['obrigacoes_cobertas']),
        'qtd_obrigacoes_bloqueadas': len(blocos['obrigacoes_bloqueadas']),
        'qtd_fontes_utilizadas': len(blocos['fontes_utilizadas']),
        'qtd_fontes_reservadas': len(blocos['fontes_reservadas']),
        'qtd_switchings_escolhidos': len(blocos['switchings_escolhidos']),
        'qtd_switchings_realizados_operacionais': len(blocos.get('switchings_realizados_operacionais', [])),
        'qtd_lotes_pos_switching_materializados': len(blocos.get('lotes_pos_switching_materializados', [])),
        'qtd_destinos_sobras_recebidos': len(blocos.get('destinos_sobras_recebidos', [])),
        'qtd_lotes_futuros_materializados': len(blocos.get('lotes_futuros_materializados', [])),
        'qtd_datas_saldos_referenciais': len(blocos['saldos_referenciais']),
    }


def _data_observavel_item(item: dict[str, Any]) -> date | None:
    data_item = item.get('data')
    if isinstance(data_item, datetime):
        return data_item.date()
    if isinstance(data_item, date):
        return data_item
    if isinstance(data_item, str):
        try:
            return date.fromisoformat(data_item[:10])
        except ValueError:
            pass
    referencia = item.get('referencia_original') or {}
    data_ref = referencia.get('data') if isinstance(referencia, dict) else None
    if isinstance(data_ref, datetime):
        return data_ref.date()
    if isinstance(data_ref, date):
        return data_ref
    if isinstance(data_ref, str):
        try:
            return date.fromisoformat(data_ref[:10])
        except ValueError:
            return None
    return None


def _status_pagamento_observavel(item: dict[str, Any], *, bloqueada: bool) -> dict[str, Any]:
    saida = dict(item)
    saida['status_observavel'] = 'bloqueada_oficial' if bloqueada else 'coberta_oficial'
    return saida


def _valor_historico_materializado(item: dict[str, Any], *chaves: str, padrao: Any = 'nao_materializado') -> Any:
    for chave in chaves:
        if chave not in item:
            continue
        valor = item.get(chave)
        if valor is None:
            continue
        if isinstance(valor, float) and valor != valor:
            continue
        if isinstance(valor, str) and not valor.strip():
            continue
        return valor
    return padrao


def _status_valor_historico(valor: Any, padrao: str = 'nao_materializado') -> str:
    return padrao if valor == padrao else 'materializado'


def _data_extrato_passado_materializada(item: dict[str, Any]) -> Any:
    data_item = _data_observavel_item(item)
    if data_item is not None:
        return data_item
    return _valor_historico_materializado(item, 'Data', 'data')


def _linha_modelo_pagamento_historico_observavel(item: dict[str, Any]) -> dict[str, Any]:
    conta = _valor_historico_materializado(
        item,
        'Conta',
        'conta',
        'fonte_informada',
        'fonte_resolvida_historica',
    )
    lote = _valor_historico_materializado(
        item,
        'Lote',
        'lote',
        'lote_usado',
        'lote_id_operacional',
        'fonte_resolvida_historica',
    )
    liquido = _valor_historico_materializado(
        item,
        'Líquido',
        'Liquido',
        'valor_liquido_resgate',
        'valor_liquido',
        'valor',
    )
    return {
        'Data': _data_extrato_passado_materializada(item),
        'Conta': conta,
        'Despesa ID': _valor_historico_materializado(
            item,
            'Despesa ID',
            'despesa_id',
            'pagamento_id',
            'obrigacao_id',
            'id',
        ),
        'Lote': lote,
        'Saldo Antes': _valor_historico_materializado(
            item,
            'Saldo Antes',
            'saldo_antes',
            'saldo_antes_fonte',
        ),
        'Bruto': _valor_historico_materializado(
            item,
            'Bruto',
            'valor_bruto_resgate',
            'valor_bruto',
            'valor',
        ),
        'Imposto': _valor_historico_materializado(
            item,
            'Imposto',
            'imposto_resgate',
            'imposto',
        ),
        'Líquido': liquido,
        'Saldo Remanescente': _valor_historico_materializado(
            item,
            'Saldo Remanescente',
            'saldo_remanescente',
            'saldo_remanescente_fonte',
        ),
        '_referencia_original': dict(item),
        '_origem_formal': item.get('origem') or item.get('origem_valores_historicos') or 'historico_pago_oficial',
    }


def _chave_ordenacao_pagamento_historico(linha: dict[str, Any]) -> tuple[Any, ...]:
    data_linha = linha.get('Data')
    return (
        not isinstance(data_linha, date),
        data_linha if isinstance(data_linha, date) else date.max,
        str(linha.get('Despesa ID') or ''),
        str(linha.get('Lote') or ''),
    )


def preparar_modelo_pagamentos_historicos_observavel(blocos: dict[str, Any]) -> list[dict[str, Any]]:
    data_referencia = blocos.get('data_referencia')
    linhas: list[dict[str, Any]] = []
    for item in list(blocos.get('pagamentos_historicos_realizados') or []):
        data_item = _data_observavel_item(item)
        if isinstance(data_referencia, date) and data_item is not None and data_item > data_referencia:
            continue
        linhas.append(_linha_modelo_pagamento_historico_observavel(item))

    return sorted(linhas, key=_chave_ordenacao_pagamento_historico)


def _projetar_linha_extrato_passado(linha: dict[str, Any]) -> dict[str, Any]:
    return {
        'Data': linha.get('Data'),
        'Conta': linha.get('Conta'),
        'Despesa ID': linha.get('Despesa ID'),
        'Lote': linha.get('Lote'),
        'Saldo Antes': linha.get('Saldo Antes'),
        'Bruto': linha.get('Bruto'),
        'Imposto': linha.get('Imposto'),
        'Líquido': linha.get('Líquido'),
        'Saldo Remanescente': linha.get('Saldo Remanescente'),
    }


def preparar_bloco_extrato_passado(modelo_pagamentos_historicos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _projetar_linha_extrato_passado(linha)
        for linha in modelo_pagamentos_historicos
    ]


def _projetar_ultimo_pagamento_do_modelo(linha: dict[str, Any]) -> dict[str, Any]:
    referencia_original = linha.get('_referencia_original') if isinstance(linha.get('_referencia_original'), dict) else {}
    fonte = linha.get('Lote')
    liquido = linha.get('Líquido')
    return {
        'data': linha.get('Data') if isinstance(linha.get('Data'), date) else None,
        'obrigacao_id': linha.get('Despesa ID'),
        'pacote_id': 'nao_aplicavel',
        'valor_obrigacao_referencial': liquido,
        'valor_coberto_referencial': liquido,
        'fontes_referenciadas_operacionais': [fonte] if fonte and fonte != 'nao_materializado' else [],
        'fontes_referenciadas_tecnicas': [fonte] if fonte and fonte != 'nao_materializado' else [],
        'pacote_nome_operacional': 'nao_aplicavel',
        'origem': 'historico_pago_oficial',
        'origem_formal': linha.get('_origem_formal') or 'historico_pago_oficial',
        'status_observavel': 'realizada_oficial',
        'status': 'realizada_oficial',
        'referencia_original': referencia_original,
        'saldo_antes_fonte': linha.get('Saldo Antes'),
        'valor_bruto_resgate': linha.get('Bruto'),
        'imposto_resgate': linha.get('Imposto'),
        'valor_liquido_resgate': liquido,
        'saldo_remanescente_fonte': linha.get('Saldo Remanescente'),
        'status_saldo_antes_fonte': _status_valor_historico(linha.get('Saldo Antes')),
        'status_valor_bruto_resgate': _status_valor_historico(linha.get('Bruto')),
        'status_imposto_resgate': _status_valor_historico(linha.get('Imposto')),
        'status_valor_liquido_resgate': _status_valor_historico(liquido),
        'status_saldo_remanescente_fonte': _status_valor_historico(linha.get('Saldo Remanescente')),
    }


def preparar_bloco_ultimos_pagamentos(
    modelo_pagamentos_historicos: list[dict[str, Any]],
    limite: int = 5,
) -> list[dict[str, Any]]:
    realizados = [
        linha
        for linha in modelo_pagamentos_historicos
        if isinstance(linha.get('Data'), date)
    ]
    ultimos = sorted(
        realizados,
        key=lambda linha: (
            linha.get('Data') if isinstance(linha.get('Data'), date) else date.min,
            str(linha.get('Despesa ID') or ''),
            str(linha.get('Lote') or ''),
        ),
        reverse=True,
    )[:limite]
    return [_projetar_ultimo_pagamento_do_modelo(linha) for linha in ultimos]


def preparar_bloco_pagamentos_data_referencia(blocos: dict[str, Any]) -> list[dict[str, Any]]:
    data_referencia = blocos.get('data_referencia')
    if not isinstance(data_referencia, date):
        return []
    pagamentos: list[dict[str, Any]] = []
    for item in list(blocos['obrigacoes_cobertas']):
        if _data_observavel_item(item) == data_referencia:
            item_status = _status_pagamento_observavel(item, bloqueada=False)
            pagamentos.extend(_expandir_pagamento_multifonte_observavel(item_status))
    for item in list(blocos['obrigacoes_bloqueadas']):
        if _data_observavel_item(item) == data_referencia:
            pagamentos.append(_status_pagamento_observavel(item, bloqueada=True))
    return sorted(
        pagamentos,
        key=lambda item: (item.get('status_observavel') == 'bloqueada_oficial', str(item.get('obrigacao_id') or '')),
    )


def preparar_bloco_proximos_pagamentos(blocos: dict[str, Any], limite: int = 5) -> list[dict[str, Any]]:
    data_referencia = blocos.get('data_referencia')
    proximos: list[dict[str, Any]] = []
    for item in list(blocos['obrigacoes_cobertas']):
        data_item = _data_observavel_item(item)
        if data_item is None or not isinstance(data_referencia, date) or data_item > data_referencia:
            item_status = _status_pagamento_observavel(item, bloqueada=False)
            proximos.extend(_expandir_pagamento_multifonte_observavel(item_status))
    for item in list(blocos['obrigacoes_bloqueadas']):
        data_item = _data_observavel_item(item)
        if data_item is None or not isinstance(data_referencia, date) or data_item > data_referencia:
            proximos.append(_status_pagamento_observavel(item, bloqueada=True))
    return sorted(
        proximos,
        key=lambda item: (_data_observavel_item(item) is None, _data_observavel_item(item) or date.max, item.get('status_observavel') == 'bloqueada_oficial', str(item.get('obrigacao_id') or '')),
    )[:limite]


def _valor_economico_detalhe_observavel(detalhe: dict[str, Any], campo: str, status_campo: str) -> Any:
    valor = detalhe.get(campo)
    if valor is not None:
        return valor
    return detalhe.get(status_campo) or 'nao_materializado'


def _fonte_operacional_detalhe_observavel(detalhe: dict[str, Any]) -> Any:
    return (
        detalhe.get('lote_id_operacional')
        or detalhe.get('fonte_nome_operacional')
        or detalhe.get('fonte_id')
        or 'ausente_na_fonte'
    )


def _fonte_tecnica_detalhe_observavel(detalhe: dict[str, Any]) -> Any:
    return detalhe.get('fonte_id_tecnico') or detalhe.get('fonte_id') or 'ausente_na_fonte'


def _expandir_pagamento_multifonte_observavel(item: dict[str, Any]) -> list[dict[str, Any]]:
    detalhes = [detalhe for detalhe in list(item.get('detalhes_fontes_resgate') or []) if isinstance(detalhe, dict)]
    if not detalhes:
        return [item]

    linhas: list[dict[str, Any]] = []
    for detalhe in detalhes:
        fonte_operacional = _fonte_operacional_detalhe_observavel(detalhe)
        fonte_tecnica = _fonte_tecnica_detalhe_observavel(detalhe)
        liquido = _valor_economico_detalhe_observavel(detalhe, 'valor_liquido_resgate', 'status_valor_liquido_resgate')
        linha = dict(item)
        linha.update({
            'valor_obrigacao_referencial': liquido,
            'valor_coberto_referencial': liquido,
            'fontes_referenciadas': [fonte_operacional],
            'fontes_referenciadas_operacionais': [fonte_operacional],
            'fontes_referenciadas_tecnicas': [fonte_tecnica],
            'detalhes_fontes_resgate': [dict(detalhe)],
            'saldo_antes_fonte': _valor_economico_detalhe_observavel(detalhe, 'saldo_antes_fonte', 'status_saldo_antes_fonte'),
            'valor_bruto_resgate': _valor_economico_detalhe_observavel(detalhe, 'valor_bruto_resgate', 'status_valor_bruto_resgate'),
            'imposto_resgate': _valor_economico_detalhe_observavel(detalhe, 'imposto_resgate', 'status_imposto_resgate'),
            'valor_liquido_resgate': liquido,
            'saldo_remanescente_fonte': _valor_economico_detalhe_observavel(detalhe, 'saldo_remanescente_fonte', 'status_saldo_remanescente_fonte'),
            'status_saldo_antes_fonte': detalhe.get('status_saldo_antes_fonte') or 'nao_materializado',
            'status_valor_bruto_resgate': detalhe.get('status_valor_bruto_resgate') or 'nao_materializado',
            'status_imposto_resgate': detalhe.get('status_imposto_resgate') or 'nao_materializado',
            'status_valor_liquido_resgate': detalhe.get('status_valor_liquido_resgate') or 'nao_materializado',
            'status_saldo_remanescente_fonte': detalhe.get('status_saldo_remanescente_fonte') or 'nao_materializado',
            'fonte_id_tecnico': fonte_tecnica,
            'lote_id_operacional': fonte_operacional,
            'tipo_linha_observavel': 'detalhe_fonte_multifonte',
            'Obrigacao ID': item.get('obrigacao_id') or detalhe.get('obrigacao_id'),
            'Pacote ID': item.get('pacote_id') or detalhe.get('pacote_id'),
        })
        linhas.append(linha)
    return linhas


def preparar_bloco_pagamentos_por_fonte(blocos: dict[str, Any]) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for item in list(blocos['obrigacoes_cobertas']):
        detalhes = list(item.get('detalhes_fontes_resgate') or [])
        if not detalhes:
            continue
        referencia = item.get('referencia_original') or {}
        pacote_id = item.get('pacote_id')
        pacote = item.get('pacote_nome_operacional') or pacote_id or 'sem_pacote_valido'
        for detalhe in detalhes:
            if not isinstance(detalhe, dict):
                continue
            fonte_operacional = _fonte_operacional_detalhe_observavel(detalhe)
            fonte_tecnica = _fonte_tecnica_detalhe_observavel(detalhe)
            linhas.append({
                'Data': _data_observavel_item(item),
                'Conta': referencia.get('conta') or referencia.get('descricao') or referencia.get('Conta') or item.get('obrigacao_id'),
                'Lote/Fonte operacional': fonte_operacional,
                'Fonte técnica': fonte_tecnica,
                'Pacote': pacote,
                'Saldo Antes': _valor_economico_detalhe_observavel(detalhe, 'saldo_antes_fonte', 'status_saldo_antes_fonte'),
                'Bruto': _valor_economico_detalhe_observavel(detalhe, 'valor_bruto_resgate', 'status_valor_bruto_resgate'),
                'IR': _valor_economico_detalhe_observavel(detalhe, 'imposto_resgate', 'status_imposto_resgate'),
                'Líquido': _valor_economico_detalhe_observavel(detalhe, 'valor_liquido_resgate', 'status_valor_liquido_resgate'),
                'Saldo Remanescente': _valor_economico_detalhe_observavel(detalhe, 'saldo_remanescente_fonte', 'status_saldo_remanescente_fonte'),
                'Status': item.get('status_observavel') or 'coberta_oficial',
                'Obrigacao ID': item.get('obrigacao_id'),
                'Pacote ID': pacote_id,
            })
    return linhas


def preparar_bloco_fontes_utilizadas_reservadas(blocos: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        'fontes_utilizadas': list(blocos['fontes_utilizadas']),
        'fontes_reservadas': list(blocos['fontes_reservadas']),
    }


def preparar_bloco_obrigacoes(blocos: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        'obrigacoes_cobertas': list(blocos['obrigacoes_cobertas']),
        'obrigacoes_bloqueadas': list(blocos['obrigacoes_bloqueadas']),
    }


def _valor_switching_observavel(item: dict[str, Any], *campos: str, padrao: Any = None) -> Any:
    for campo in campos:
        valor = item.get(campo)
        if valor is not None and str(valor).strip():
            return valor
    referencia = item.get('referencia_original') or {}
    if isinstance(referencia, dict):
        for campo in campos:
            valor = referencia.get(campo)
            if valor is not None and str(valor).strip():
                return valor
    return padrao


def _linha_switching_observavel(item: dict[str, Any]) -> dict[str, Any]:
    return {
        'Data': _valor_switching_observavel(item, 'data', 'data_switching', 'data_aplicacao'),
        'Lote origem': _valor_switching_observavel(item, 'lote_origem_id', 'lote_origem'),
        'Lote destino': _valor_switching_observavel(item, 'lote_destino_id', 'lote_destino'),
        'Produto origem': _valor_switching_observavel(
            item,
            'produto_origem',
            'investimento_origem',
            'carteira_origem',
            padrao='nao_materializado',
        ),
        'Produto destino': _valor_switching_observavel(
            item,
            'produto_destino',
            'investimento_destino',
            'carteira_destino',
            padrao='nao_materializado',
        ),
    }


def preparar_bloco_switchings(blocos: dict[str, Any]) -> dict[str, Any]:
    switchings_escolhidos = list(blocos['switchings_escolhidos'])
    switchings_operacionais = list(blocos.get('switchings_realizados_operacionais', []))
    lotes_pos = list(blocos.get('lotes_pos_switching_materializados', []))

    # Na rota oficial pós-PR496, os switchings realizados operacionais são a evidência
    # materializada da janela. Se não houver switchings_escolhidos futuros/econômicos,
    # a contagem de candidatos avaliados para a janela observável deve refletir os
    # switchings operacionais preservados, sem inventar dados no console.
    candidatos_avaliados = len(switchings_escolhidos) if switchings_escolhidos else len(switchings_operacionais)

    metricas = [
        {'Métrica': 'Lotes avaliados para switching', 'Valor': len(switchings_operacionais)},
        {'Métrica': 'Candidatos avaliados para switching', 'Valor': candidatos_avaliados},
        {'Métrica': 'Switchings promovidos/executados', 'Valor': len(switchings_operacionais)},
        {'Métrica': 'Origem da amostra', 'Valor': 'V225'},
    ]

    resumo_operacional = [
        {'Métrica': 'Total de switchings promovidos', 'Valor': len(switchings_operacionais)},
        {'Métrica': 'Total de lotes sintéticos pós-switching', 'Valor': len(lotes_pos)},
        {
            'Métrica': 'Total de aportes futuros',
            'Valor': 'aportes_futuros_nao_materializados_na_rota_oficial',
        },
    ]

    return {
        'switchings_escolhidos': switchings_escolhidos,
        'switchings_realizados_operacionais': switchings_operacionais,
        'switchings_metricas': metricas,
        'switchings_amostra': [_linha_switching_observavel(item) for item in switchings_operacionais],
        'switchings_resumo_operacional': resumo_operacional,
    }


def preparar_bloco_saldos(blocos: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return dict(blocos['saldos_referenciais'])


def preservar_avisos_bloqueios_evidencias(blocos: dict[str, Any]) -> dict[str, Any]:
    return {
        'avisos': list(blocos['avisos_ledger']) + list(blocos['avisos_gates']),
        'bloqueios': (
            list(blocos['bloqueios_ledger'])
            + list(blocos['bloqueios_gates'])
            + list(blocos['bloqueios_preparacao'])
        ),
        'evidencias': list(blocos['evidencias_gates']),
        'destinos_sobras_recebidos': list(blocos.get('destinos_sobras_recebidos', [])),
        'lotes_futuros_materializados': list(blocos.get('lotes_futuros_materializados', [])),
        'lotes_pos_switching_materializados': list(blocos.get('lotes_pos_switching_materializados', [])),
    }


def registrar_lacunas_renderizacao(
    saida: SaidaCanonicaOficial,
    blocos: dict[str, Any],
) -> list[LacunaRenderizacaoSaidaObservavel]:
    lacunas: list[LacunaRenderizacaoSaidaObservavel] = []
    if not saida.preparada:
        lacunas.append(
            _nova_lacuna(
                'saida_canonica_nao_preparada',
                'SaidaCanonicaOficial.preparada=False limita a renderizacao observavel.',
                {'status_saida_canonica': saida.status},
            )
        )
    if blocos['obrigacoes_cobertas'] == [] and blocos['obrigacoes_bloqueadas'] == []:
        lacunas.append(
            _nova_lacuna(
                'obrigacoes_ausentes_para_renderizacao',
                'SaidaCanonicaOficial não contém obrigações cobertas nem bloqueadas para compor pagamentos observáveis.',
            )
        )

    resumo = blocos.get('resumo_saida_canonica') or {}
    campos_prioridade2 = {
        'patrimonio_total_lotes': 'patrimônio total dos lotes',
        'bruto_sacado': 'bruto sacado',
        'liquido_sacado': 'líquido sacado',
        'bruto_atual': 'bruto atual',
        'liquido_atual': 'líquido atual',
        'patrimonio_liquido': 'patrimônio líquido',
        'rendimento_liquido': 'rendimento líquido',
        'resumo_recebidos_valores': 'resumo de recebidos em valores',
    }
    for campo, rotulo in campos_prioridade2.items():
        if campo in blocos or campo in resumo:
            continue
        lacunas.append(
            _nova_lacuna(
                f'{campo}_nao_materializado_na_saida_canonica_oficial',
                f'{rotulo} não está materializado na SaidaCanonicaOficial; Etapa 9 preserva lacuna objetiva sem mascarar com zero.',
                {'campo': campo, 'origem_requerida': 'LedgerTemporalCanonico validado'},
            )
        )
    return lacunas


def preparar_blocos_console(
    resumo: dict[str, Any],
    ultimos_pagamentos: list[dict[str, Any]],
    pagamentos_data_referencia: list[dict[str, Any]],
    proximos_pagamentos: list[dict[str, Any]],
    pagamentos_por_fonte: list[dict[str, Any]],
    fontes: dict[str, list[dict[str, Any]]],
    obrigacoes: dict[str, list[dict[str, Any]]],
    switchings: dict[str, list[dict[str, Any]]],
    saldos: dict[str, list[dict[str, Any]]],
    preservados: dict[str, Any],
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> BlocoConsoleSaidaObservavel:
    return BlocoConsoleSaidaObservavel(
        resumo_operacional=resumo,
        ultimos_pagamentos=ultimos_pagamentos,
        pagamentos_data_referencia=pagamentos_data_referencia,
        proximos_pagamentos=proximos_pagamentos,
        pagamentos_por_fonte=pagamentos_por_fonte,
        fontes_utilizadas=fontes['fontes_utilizadas'],
        obrigacoes_cobertas=obrigacoes['obrigacoes_cobertas'],
        obrigacoes_bloqueadas=obrigacoes['obrigacoes_bloqueadas'],
        switchings_escolhidos=switchings.get('switchings_escolhidos', []),
        switchings_realizados_operacionais=switchings.get('switchings_realizados_operacionais', []),
        switchings_metricas=switchings.get('switchings_metricas', []),
        switchings_amostra=switchings.get('switchings_amostra', []),
        switchings_resumo_operacional=switchings.get('switchings_resumo_operacional', []),
        lotes_pos_switching_materializados=preservados.get('lotes_pos_switching_materializados', []),
        saldos_referenciais=saldos,
        destinos_sobras_recebidos=preservados.get('destinos_sobras_recebidos', []),
        lotes_futuros_materializados=preservados.get('lotes_futuros_materializados', []),
        avisos=preservados['avisos'],
        bloqueios=preservados['bloqueios'],
        lacunas_renderizacao=[asdict(lacuna) for lacuna in lacunas],
    )


def preparar_blocos_xlsx(
    resumo: dict[str, Any],
    extrato_passado: list[dict[str, Any]],
    ultimos_pagamentos: list[dict[str, Any]],
    pagamentos_data_referencia: list[dict[str, Any]],
    proximos_pagamentos: list[dict[str, Any]],
    pagamentos_por_fonte: list[dict[str, Any]],
    fontes: dict[str, list[dict[str, Any]]],
    obrigacoes: dict[str, list[dict[str, Any]]],
    switchings: dict[str, list[dict[str, Any]]],
    saldos: dict[str, list[dict[str, Any]]],
    preservados: dict[str, Any],
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> BlocoXLSXSaidaObservavel:
    abas = {
        'Resumo Operacional': [resumo],
        'Extrato Passado': extrato_passado,
        'Ultimos Pagamentos': ultimos_pagamentos,
        'Pagamentos Data Referencia': pagamentos_data_referencia,
        'Proximos Pagamentos': proximos_pagamentos,
        'Pagamentos Fontes': pagamentos_por_fonte,
        'Fontes Utilizadas': fontes['fontes_utilizadas'],
        'Fontes Reservadas': fontes['fontes_reservadas'],
        'Obrigacoes Cobertas': obrigacoes['obrigacoes_cobertas'],
        'Obrigacoes Bloqueadas': obrigacoes['obrigacoes_bloqueadas'],
        'Switchings Escolhidos': switchings.get('switchings_escolhidos', []),
        'Switchings Realizados Operacionais': switchings.get('switchings_realizados_operacionais', []),
        'Lotes Pos Switching Materializados': preservados.get('lotes_pos_switching_materializados', []),
        'Destinos Sobras Recebidos': preservados.get('destinos_sobras_recebidos', []),
        'Lotes Futuros Materializados': preservados.get('lotes_futuros_materializados', []),
        'Avisos': [{'aviso': aviso} if not isinstance(aviso, dict) else aviso for aviso in preservados['avisos']],
        'Bloqueios': preservados['bloqueios'],
        'Lacunas Renderizacao': [asdict(lacuna) for lacuna in lacunas],
    }
    for data_ref, registros in saldos.items():
        abas[f'Saldos {data_ref}'] = registros
    return BlocoXLSXSaidaObservavel(
        abas=abas,
        metadados_abas={
            'qtd_abas': len(abas),
            'abas': list(abas),
        },
    )


def auditar_pacote_saida_observavel(
    entrada_tipo: str,
    entrada_valida: bool,
    bloco_console: BlocoConsoleSaidaObservavel,
    bloco_xlsx: BlocoXLSXSaidaObservavel,
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> AuditoriaSaidaObservavelOficial:
    return AuditoriaSaidaObservavelOficial(
        entrada_tipo=entrada_tipo,
        entrada_valida=entrada_valida,
        origem_exclusiva=_ORIGEM_FORMAL,
        blocos_console_preparados=bool(bloco_console.resumo_operacional),
        blocos_xlsx_preparados=bool(bloco_xlsx.abas),
        qtd_lacunas_renderizacao=len(lacunas),
        qtd_bloqueios_preservados=len(bloco_console.bloqueios),
        qtd_avisos_preservados=len(bloco_console.avisos),
    )


def montar_metadados_renderizacao(status: str, preparado: bool) -> dict[str, Any]:
    return {
        'etapa': '9',
        'artefato': _ARTEFATO,
        'versao_schema': _VERSAO_SCHEMA,
        'origem_exclusiva': _ORIGEM_FORMAL,
        'status': status,
        'preparado': preparado,
        'sem_reotimizacao': True,
        'sem_revaloracao': True,
        'sem_alteracao_decisao': True,
        'sem_consulta_fontes_externas': True,
        'sem_integracao_runtime': False,
        'sem_alteracao_console': False,
        'sem_alteracao_xlsx': False,
        'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def _resumo_pacote(
    blocos: dict[str, Any],
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
    preparado: bool,
) -> ResumoSaidaObservavelOficial:
    qtd_avisos = len(blocos.get('avisos_ledger', [])) + len(blocos.get('avisos_gates', []))
    qtd_bloqueios = (
        len(blocos.get('bloqueios_ledger', []))
        + len(blocos.get('bloqueios_gates', []))
        + len(blocos.get('bloqueios_preparacao', []))
    )
    return ResumoSaidaObservavelOficial(
        qtd_eventos=len(blocos.get('eventos', [])),
        qtd_obrigacoes_cobertas=len(blocos.get('obrigacoes_cobertas', [])),
        qtd_obrigacoes_bloqueadas=len(blocos.get('obrigacoes_bloqueadas', [])),
        qtd_fontes_utilizadas=len(blocos.get('fontes_utilizadas', [])),
        qtd_fontes_reservadas=len(blocos.get('fontes_reservadas', [])),
        qtd_switchings_escolhidos=len(blocos.get('switchings_escolhidos', [])),
        qtd_switchings_realizados_operacionais=len(blocos.get('switchings_realizados_operacionais', [])),
        qtd_lotes_pos_switching_materializados=len(blocos.get('lotes_pos_switching_materializados', [])),
        qtd_destinos_sobras_recebidos=len(blocos.get('destinos_sobras_recebidos', [])),
        qtd_lotes_futuros_materializados=len(blocos.get('lotes_futuros_materializados', [])),
        qtd_saldos_referenciais_datas=len(blocos.get('saldos_referenciais', {})),
        qtd_avisos=qtd_avisos,
        qtd_bloqueios=qtd_bloqueios,
        qtd_lacunas_renderizacao=len(lacunas),
        pronto_para_console=preparado,
        pronto_para_xlsx=preparado,
        preparado=preparado,
    )


def _pacote_bloqueado_por_entrada_invalida(
    saida: Any,
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> PacoteSaidaObservavelOficial:
    blocos: dict[str, Any] = {}
    bloco_console = BlocoConsoleSaidaObservavel(lacunas_renderizacao=[asdict(lacuna) for lacuna in lacunas])
    bloco_xlsx = BlocoXLSXSaidaObservavel(
        abas={'Lacunas Renderizacao': [asdict(lacuna) for lacuna in lacunas]},
        metadados_abas={'qtd_abas': 1, 'abas': ['Lacunas Renderizacao']},
    )
    auditoria = auditar_pacote_saida_observavel(
        entrada_tipo=type(saida).__name__,
        entrada_valida=False,
        bloco_console=bloco_console,
        bloco_xlsx=bloco_xlsx,
        lacunas=lacunas,
    )
    return PacoteSaidaObservavelOficial(
        ok=False,
        preparado=False,
        status='bloqueado_entrada_invalida',
        data_referencia=None,
        origem_formal=_ORIGEM_FORMAL,
        saida_origem=type(saida).__name__,
        resumo=_resumo_pacote(blocos, lacunas, preparado=False),
        bloco_console=bloco_console,
        bloco_xlsx=bloco_xlsx,
        lacunas_renderizacao=lacunas,
        auditoria=auditoria,
        metadados=montar_metadados_renderizacao('bloqueado_entrada_invalida', preparado=False),
    )


def construir_pacote_saida_observavel_oficial(
    saida: SaidaCanonicaOficial,
) -> PacoteSaidaObservavelOficial:
    lacunas = validar_entrada_saida_observavel(saida)
    if lacunas:
        return _pacote_bloqueado_por_entrada_invalida(saida, lacunas)

    blocos = extrair_blocos_saida_canonica(saida)
    blocos = _enriquecer_identificacao_operacional_blocos(blocos)
    resumo_operacional = preparar_resumo_operacional_observavel(blocos)
    modelo_pagamentos_historicos = preparar_modelo_pagamentos_historicos_observavel(blocos)
    extrato_passado = preparar_bloco_extrato_passado(modelo_pagamentos_historicos)
    ultimos_pagamentos = preparar_bloco_ultimos_pagamentos(modelo_pagamentos_historicos)
    pagamentos_data_referencia = preparar_bloco_pagamentos_data_referencia(blocos)
    proximos_pagamentos = preparar_bloco_proximos_pagamentos(blocos)
    pagamentos_por_fonte = preparar_bloco_pagamentos_por_fonte(blocos)
    fontes = preparar_bloco_fontes_utilizadas_reservadas(blocos)
    obrigacoes = preparar_bloco_obrigacoes(blocos)
    switchings = preparar_bloco_switchings(blocos)
    saldos = preparar_bloco_saldos(blocos)
    preservados = preservar_avisos_bloqueios_evidencias(blocos)
    lacunas.extend(registrar_lacunas_renderizacao(saida, blocos))

    preparado = isinstance(saida, SaidaCanonicaOficial)
    status = 'preparado_com_lacunas' if lacunas else 'preparado'

    bloco_console = preparar_blocos_console(
        resumo_operacional,
        ultimos_pagamentos,
        pagamentos_data_referencia,
        proximos_pagamentos,
        pagamentos_por_fonte,
        fontes,
        obrigacoes,
        switchings,
        saldos,
        preservados,
        lacunas,
    )
    bloco_xlsx = preparar_blocos_xlsx(
        resumo_operacional,
        extrato_passado,
        ultimos_pagamentos,
        pagamentos_data_referencia,
        proximos_pagamentos,
        pagamentos_por_fonte,
        fontes,
        obrigacoes,
        switchings,
        saldos,
        preservados,
        lacunas,
    )
    auditoria = auditar_pacote_saida_observavel(
        entrada_tipo=type(saida).__name__,
        entrada_valida=True,
        bloco_console=bloco_console,
        bloco_xlsx=bloco_xlsx,
        lacunas=lacunas,
    )

    return PacoteSaidaObservavelOficial(
        ok=not lacunas,
        preparado=preparado,
        status=status,
        data_referencia=saida.data_referencia,
        origem_formal=_ORIGEM_FORMAL,
        saida_origem=type(saida).__name__,
        resumo=_resumo_pacote(blocos, lacunas, preparado=preparado),
        bloco_console=bloco_console,
        bloco_xlsx=bloco_xlsx,
        lacunas_renderizacao=lacunas,
        auditoria=auditoria,
        metadados=montar_metadados_renderizacao(status, preparado=preparado),
    )


__all__ = [
    'AuditoriaSaidaObservavelOficial',
    'BlocoConsoleSaidaObservavel',
    'BlocoXLSXSaidaObservavel',
    'LacunaRenderizacaoSaidaObservavel',
    'PacoteSaidaObservavelOficial',
    'ResumoSaidaObservavelOficial',
    'construir_pacote_saida_observavel_oficial',
]
