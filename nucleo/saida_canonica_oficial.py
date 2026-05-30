from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime, timezone
from typing import Any

from nucleo.gates_validacao_nucleo import ResultadoGatesValidacaoNucleo
from nucleo.ledger_temporal_canonico import LedgerTemporalCanonico


_ORIGEM_FORMAL = 'LedgerTemporalCanonico+ResultadoGatesValidacaoNucleo'
_ORIGEM_LEDGER_ESPERADA = 'LedgerTemporalCanonico'
_ARTEFATO = 'SaidaCanonicaOficial'


@dataclass(slots=True)
class BloqueioPreparacaoSaidaCanonicaOficial:
    codigo: str
    mensagem: str
    severidade: str = 'bloqueio'
    origem: str = 'Etapa8'
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoSaidaCanonicaOficial:
    qtd_eventos_ledger: int
    qtd_obrigacoes_cobertas: int
    qtd_obrigacoes_bloqueadas: int
    qtd_fontes_utilizadas: int
    qtd_fontes_reservadas: int
    qtd_switchings_escolhidos: int
    qtd_bloqueios_ledger: int
    qtd_avisos_ledger: int
    qtd_bloqueios_gates: int
    qtd_avisos_gates: int
    qtd_evidencias_gates: int
    qtd_bloqueios_preparacao: int
    gates_ok: bool
    pronto_para_etapa8: bool
    preparada: bool


@dataclass(slots=True)
class SaidaCanonicaOficial:
    ok: bool
    preparada: bool
    status: str
    data_referencia: date | None
    origem_formal: str
    ledger_origem: str
    gates_origem: str
    resumo: ResumoSaidaCanonicaOficial
    eventos: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_cobertas: list[dict[str, Any]] = field(default_factory=list)
    obrigacoes_bloqueadas: list[dict[str, Any]] = field(default_factory=list)
    fontes_utilizadas: list[dict[str, Any]] = field(default_factory=list)
    fontes_reservadas: list[dict[str, Any]] = field(default_factory=list)
    switchings_escolhidos: list[dict[str, Any]] = field(default_factory=list)
    saldos_referenciais_por_data: dict[date, list[dict[str, Any]]] = field(default_factory=dict)
    bloqueios_ledger: list[dict[str, Any]] = field(default_factory=list)
    avisos_ledger: list[str] = field(default_factory=list)
    bloqueios_gates: list[dict[str, Any]] = field(default_factory=list)
    avisos_gates: list[dict[str, Any]] = field(default_factory=list)
    evidencias_gates: list[dict[str, Any]] = field(default_factory=list)
    bloqueios_preparacao: list[BloqueioPreparacaoSaidaCanonicaOficial] = field(default_factory=list)
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


def _snapshot_saldos(saldos_por_data: dict[date, list[Any]] | None) -> dict[date, list[dict[str, Any]]]:
    return {
        data_ref: _snapshot_lista(saldos)
        for data_ref, saldos in (saldos_por_data or {}).items()
    }


def _novo_bloqueio(codigo: str, mensagem: str, referencias: dict[str, Any] | None = None) -> BloqueioPreparacaoSaidaCanonicaOficial:
    return BloqueioPreparacaoSaidaCanonicaOficial(
        codigo=codigo,
        mensagem=mensagem,
        referencias=referencias or {},
    )


def _resumo(
    ledger: LedgerTemporalCanonico | None,
    gates: ResultadoGatesValidacaoNucleo | None,
    bloqueios_preparacao: list[BloqueioPreparacaoSaidaCanonicaOficial],
    preparada: bool,
) -> ResumoSaidaCanonicaOficial:
    return ResumoSaidaCanonicaOficial(
        qtd_eventos_ledger=len(_valor(ledger, 'eventos', []) or []),
        qtd_obrigacoes_cobertas=len(_valor(ledger, 'obrigacoes_cobertas', []) or []),
        qtd_obrigacoes_bloqueadas=len(_valor(ledger, 'obrigacoes_bloqueadas', []) or []),
        qtd_fontes_utilizadas=len(_valor(ledger, 'fontes_utilizadas', []) or []),
        qtd_fontes_reservadas=len(_valor(ledger, 'fontes_reservadas', []) or []),
        qtd_switchings_escolhidos=len(_valor(ledger, 'switchings_escolhidos', []) or []),
        qtd_bloqueios_ledger=len(_valor(ledger, 'bloqueios', []) or []),
        qtd_avisos_ledger=len(_valor(ledger, 'avisos', []) or []),
        qtd_bloqueios_gates=len(_valor(gates, 'bloqueios', []) or []),
        qtd_avisos_gates=len(_valor(gates, 'avisos', []) or []),
        qtd_evidencias_gates=len(_valor(gates, 'evidencias', []) or []),
        qtd_bloqueios_preparacao=len(bloqueios_preparacao),
        gates_ok=bool(_valor(gates, 'ok', False)),
        pronto_para_etapa8=bool(_valor(gates, 'pronto_para_etapa8', False)),
        preparada=preparada,
    )


def _bloqueios_resumo_incompativel(
    ledger: LedgerTemporalCanonico,
    gates: ResultadoGatesValidacaoNucleo,
) -> list[BloqueioPreparacaoSaidaCanonicaOficial]:
    resumo_gates = _valor(gates, 'resumo')
    pares = [
        ('qtd_obrigacoes_cobertas', len(ledger.obrigacoes_cobertas or [])),
        ('qtd_obrigacoes_bloqueadas', len(ledger.obrigacoes_bloqueadas or [])),
        ('qtd_fontes_utilizadas', len(ledger.fontes_utilizadas or [])),
        ('qtd_fontes_reservadas', len(ledger.fontes_reservadas or [])),
        ('qtd_switchings', len(ledger.switchings_escolhidos or [])),
    ]
    bloqueios: list[BloqueioPreparacaoSaidaCanonicaOficial] = []
    for campo, observado_ledger in pares:
        observado_gates = _valor(resumo_gates, campo)
        if observado_gates is None:
            continue
        if int(observado_gates) != observado_ledger:
            bloqueios.append(
                _novo_bloqueio(
                    'resumo_gates_incompativel_com_ledger',
                    f'Resumo dos gates diverge do ledger no campo {campo}.',
                    {'campo': campo, 'valor_gates': observado_gates, 'valor_ledger': observado_ledger},
                )
            )
    return bloqueios


def _metadados(preparada: bool, status: str) -> dict[str, Any]:
    return {
        'etapa': '8',
        'artefato': _ARTEFATO,
        'versao_schema': 'MICRO-ETAPA8-FUNCIONAL-01',
        'origem_exclusiva': _ORIGEM_FORMAL,
        'status': status,
        'preparada': preparada,
        'sem_reotimizacao': True,
        'sem_revaloracao': True,
        'sem_nova_escolha_fonte_ou_pacote': True,
        'sem_alteracao_obrigacao': True,
        'sem_alteracao_switching': True,
        'sem_alteracao_saldo': True,
        'sem_consulta_fontes_externas': True,
        'sem_geracao_console': True,
        'sem_geracao_xlsx': True,
        'sem_integracao_runtime': True,
        'funcoes_legadas_runtime_nao_consumidas': True,
        'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def _montar_saida(
    ledger: LedgerTemporalCanonico | None,
    gates: ResultadoGatesValidacaoNucleo | None,
    bloqueios_preparacao: list[BloqueioPreparacaoSaidaCanonicaOficial],
    preparada: bool,
    status: str,
) -> SaidaCanonicaOficial:
    incluir_operacional = preparada and ledger is not None
    return SaidaCanonicaOficial(
        ok=preparada and not bloqueios_preparacao,
        preparada=preparada,
        status=status,
        data_referencia=_valor(ledger, 'data_referencia'),
        origem_formal=_ORIGEM_FORMAL,
        ledger_origem=type(ledger).__name__ if ledger is not None else 'entrada_ausente_ou_invalida',
        gates_origem=type(gates).__name__ if gates is not None else 'entrada_ausente_ou_invalida',
        resumo=_resumo(ledger, gates, bloqueios_preparacao, preparada),
        eventos=_snapshot_lista(_valor(ledger, 'eventos', [])) if incluir_operacional else [],
        obrigacoes_cobertas=_snapshot_lista(_valor(ledger, 'obrigacoes_cobertas', [])) if incluir_operacional else [],
        obrigacoes_bloqueadas=_snapshot_lista(_valor(ledger, 'obrigacoes_bloqueadas', [])) if incluir_operacional else [],
        fontes_utilizadas=_snapshot_lista(_valor(ledger, 'fontes_utilizadas', [])) if incluir_operacional else [],
        fontes_reservadas=_snapshot_lista(_valor(ledger, 'fontes_reservadas', [])) if incluir_operacional else [],
        switchings_escolhidos=_snapshot_lista(_valor(ledger, 'switchings_escolhidos', [])) if incluir_operacional else [],
        saldos_referenciais_por_data=_snapshot_saldos(_valor(ledger, 'saldos_referenciais_por_data', {})) if incluir_operacional else {},
        bloqueios_ledger=_snapshot_lista(_valor(ledger, 'bloqueios', [])),
        avisos_ledger=[str(aviso) for aviso in (_valor(ledger, 'avisos', []) or [])],
        bloqueios_gates=_snapshot_lista(_valor(gates, 'bloqueios', [])),
        avisos_gates=_snapshot_lista(_valor(gates, 'avisos', [])),
        evidencias_gates=_snapshot_lista(_valor(gates, 'evidencias', [])),
        bloqueios_preparacao=bloqueios_preparacao,
        metadados=_metadados(preparada, status),
    )


def construir_saida_canonica_oficial(
    ledger: LedgerTemporalCanonico,
    gates: ResultadoGatesValidacaoNucleo,
) -> SaidaCanonicaOficial:
    bloqueios_preparacao: list[BloqueioPreparacaoSaidaCanonicaOficial] = []

    ledger_valido = isinstance(ledger, LedgerTemporalCanonico)
    gates_validos = isinstance(gates, ResultadoGatesValidacaoNucleo)

    if not ledger_valido:
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'entrada_nao_ledger_temporal_canonico',
                'Entrada ledger deve ser LedgerTemporalCanonico.',
                {'tipo_recebido': type(ledger).__name__},
            )
        )
    if not gates_validos:
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'entrada_nao_resultado_gates_validacao_nucleo',
                'Entrada gates deve ser ResultadoGatesValidacaoNucleo.',
                {'tipo_recebido': type(gates).__name__},
            )
        )

    if not ledger_valido or not gates_validos:
        return _montar_saida(
            ledger if ledger_valido else None,
            gates if gates_validos else None,
            bloqueios_preparacao,
            preparada=False,
            status='bloqueada_entrada_invalida',
        )

    if not gates.pronto_para_etapa8:
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'gates_nao_prontos_para_etapa8',
                'ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False bloqueia a preparação da saída canônica oficial.',
                {'pronto_para_etapa8': gates.pronto_para_etapa8},
            )
        )
    if not gates.ok:
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'gates_nao_aprovados',
                'ResultadoGatesValidacaoNucleo.ok=False bloqueia a preparação da saída canônica oficial.',
                {'ok': gates.ok},
            )
        )
    if gates.origem_formal != _ORIGEM_LEDGER_ESPERADA:
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'origem_formal_gates_invalida',
                'ResultadoGatesValidacaoNucleo deve declarar origem formal LedgerTemporalCanonico.',
                {'origem_formal': gates.origem_formal},
            )
        )
    if not (ledger.auditoria and ledger.auditoria.ok):
        bloqueios_preparacao.append(
            _novo_bloqueio(
                'auditoria_ledger_nao_aprovada',
                'LedgerTemporalCanonico deve ter auditoria aprovada para preparação da saída canônica oficial.',
                {'auditoria_ok': bool(ledger.auditoria and ledger.auditoria.ok)},
            )
        )

    bloqueios_preparacao.extend(_bloqueios_resumo_incompativel(ledger, gates))

    if bloqueios_preparacao:
        return _montar_saida(
            ledger,
            gates,
            bloqueios_preparacao,
            preparada=False,
            status='bloqueada_por_validacao_etapa8',
        )

    return _montar_saida(
        ledger,
        gates,
        bloqueios_preparacao,
        preparada=True,
        status='preparada_para_consumo_posterior',
    )


__all__ = [
    'BloqueioPreparacaoSaidaCanonicaOficial',
    'ResumoSaidaCanonicaOficial',
    'SaidaCanonicaOficial',
    'construir_saida_canonica_oficial',
]
