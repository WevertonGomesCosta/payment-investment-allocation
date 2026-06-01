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
    proximos_pagamentos: list[dict[str, Any]] = field(default_factory=list)
    fontes_utilizadas: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_cobertas: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_bloqueadas: list[dict[str, Any]] = field(default_factory=list)
    switchings_escolhidos: list[dict[str, Any]] = field(default_factory=list)
    saldos_referenciais: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
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
        'fontes_utilizadas': _snapshot_lista(saida.fontes_utilizadas),
        'fontes_reservadas': _snapshot_lista(saida.fontes_reservadas),
        'switchings_escolhidos': _snapshot_lista(saida.switchings_escolhidos),
        'saldos_referenciais': _snapshot_saldos(saida.saldos_referenciais_por_data),
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
        'qtd_datas_saldos_referenciais': len(blocos['saldos_referenciais']),
    }


def preparar_bloco_ultimos_pagamentos(blocos: dict[str, Any], limite: int = 5) -> list[dict[str, Any]]:
    return list(blocos['obrigacoes_cobertas'])[-limite:]


def preparar_bloco_proximos_pagamentos(blocos: dict[str, Any], limite: int = 5) -> list[dict[str, Any]]:
    return list(blocos['obrigacoes_bloqueadas'])[:limite]


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


def preparar_bloco_switchings(blocos: dict[str, Any]) -> list[dict[str, Any]]:
    return list(blocos['switchings_escolhidos'])


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
    return lacunas


def preparar_blocos_console(
    resumo: dict[str, Any],
    ultimos_pagamentos: list[dict[str, Any]],
    proximos_pagamentos: list[dict[str, Any]],
    fontes: dict[str, list[dict[str, Any]]],
    obrigacoes: dict[str, list[dict[str, Any]]],
    switchings: list[dict[str, Any]],
    saldos: dict[str, list[dict[str, Any]]],
    preservados: dict[str, Any],
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> BlocoConsoleSaidaObservavel:
    return BlocoConsoleSaidaObservavel(
        resumo_operacional=resumo,
        ultimos_pagamentos=ultimos_pagamentos,
        proximos_pagamentos=proximos_pagamentos,
        fontes_utilizadas=fontes['fontes_utilizadas'],
        obrigacoes_cobertas=obrigacoes['obrigacoes_cobertas'],
        obrigacoes_bloqueadas=obrigacoes['obrigacoes_bloqueadas'],
        switchings_escolhidos=switchings,
        saldos_referenciais=saldos,
        avisos=preservados['avisos'],
        bloqueios=preservados['bloqueios'],
        lacunas_renderizacao=[asdict(lacuna) for lacuna in lacunas],
    )


def preparar_blocos_xlsx(
    resumo: dict[str, Any],
    ultimos_pagamentos: list[dict[str, Any]],
    proximos_pagamentos: list[dict[str, Any]],
    fontes: dict[str, list[dict[str, Any]]],
    obrigacoes: dict[str, list[dict[str, Any]]],
    switchings: list[dict[str, Any]],
    saldos: dict[str, list[dict[str, Any]]],
    preservados: dict[str, Any],
    lacunas: list[LacunaRenderizacaoSaidaObservavel],
) -> BlocoXLSXSaidaObservavel:
    abas = {
        'Resumo Operacional': [resumo],
        'Ultimos Pagamentos': ultimos_pagamentos,
        'Proximos Pagamentos': proximos_pagamentos,
        'Fontes Utilizadas': fontes['fontes_utilizadas'],
        'Fontes Reservadas': fontes['fontes_reservadas'],
        'Obrigacoes Cobertas': obrigacoes['obrigacoes_cobertas'],
        'Obrigacoes Bloqueadas': obrigacoes['obrigacoes_bloqueadas'],
        'Switchings Escolhidos': switchings,
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
    resumo_operacional = preparar_resumo_operacional_observavel(blocos)
    ultimos_pagamentos = preparar_bloco_ultimos_pagamentos(blocos)
    proximos_pagamentos = preparar_bloco_proximos_pagamentos(blocos)
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
        proximos_pagamentos,
        fontes,
        obrigacoes,
        switchings,
        saldos,
        preservados,
        lacunas,
    )
    bloco_xlsx = preparar_blocos_xlsx(
        resumo_operacional,
        ultimos_pagamentos,
        proximos_pagamentos,
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
