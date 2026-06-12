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
    qtd_switchings_realizados_operacionais: int
    qtd_lotes_pos_switching_materializados: int
    qtd_destinos_sobras_recebidos: int
    qtd_lotes_futuros_materializados: int
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
    pagamentos_historicos_realizados: list[dict[str, Any]] = field(default_factory=list)
    fontes_utilizadas: list[dict[str, Any]] = field(default_factory=list)
    fontes_reservadas: list[dict[str, Any]] = field(default_factory=list)
    switchings_escolhidos: list[dict[str, Any]] = field(default_factory=list)
    switchings_realizados_operacionais: list[dict[str, Any]] = field(default_factory=list)
    lotes_pos_switching_materializados: list[dict[str, Any]] = field(default_factory=list)
    saldos_referenciais_por_data: dict[date, list[dict[str, Any]]] = field(default_factory=dict)
    destinos_sobras_recebidos: list[dict[str, Any]] = field(default_factory=list)
    lotes_futuros_materializados: list[dict[str, Any]] = field(default_factory=list)
    ranking_metricas: list[dict[str, Any]] = field(default_factory=list)
    ranking_amostra: list[dict[str, Any]] = field(default_factory=list)
    ranking_carteira: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_fechamento: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_lotes_exauridos_id: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_lotes_exauridos_valores: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_lotes_ativos_id: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_lotes_ativos_valores: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_origens_migradas: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_patrimonio_total: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_recebidos_auditaveis: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_resumo_recebidos: list[dict[str, Any]] = field(default_factory=list)
    situacao_atual_blocos: list[dict[str, Any]] = field(default_factory=list)
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


_COLUNAS_CARTEIRA_RANKING = [
    'rank_destino',
    'nome',
    'score_final',
    'proxy_terminal_destino',
    'retorno_anual_proxy',
    'liquidez_dias',
    'carencia_dias',
    'aplicacao_minima',
    'aplicacao_maxima',
    'tipo_produto',
    'somente_combo',
    'Status_Confirmação',
    'Campos_Pendentes',
]

_CABECALHOS_CARTEIRA_RANKING = [
    'Rank',
    'Produto',
    'Score Final',
    'Proxy Terminal',
    'Retorno Proxy aa',
    'Liquidez Dias',
    'Carência Dias',
    'Aplicação Mínima',
    'Aplicação Máxima',
    'Tipo Produto',
    'Somente Combo',
    'Status Confirmação',
    'Campos Pendentes',
]


def _valor_nan_para_vazio(valor: Any) -> Any:
    try:
        if valor != valor:
            return ''
    except Exception:
        return valor
    return valor


def _registros_tabela(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    to_dict = getattr(valor, 'to_dict', None)
    if callable(to_dict):
        try:
            return [dict(item) for item in to_dict('records')]
        except TypeError:
            pass
    if isinstance(valor, list):
        return [_snapshot_item(item) for item in valor]
    return []


def _normalizar_linha_ranking(item: dict[str, Any]) -> dict[str, Any]:
    aliases = {
        'rank_destino': ['rank_destino', 'Rank_Consolidado_Prazo_Ativos', 'Rank'],
        'nome': ['nome', 'Nome', 'Produto'],
        'score_final': ['score_final', 'Score Final Prazo', 'Score Final', 'Score'],
        'proxy_terminal_destino': ['proxy_terminal_destino', 'Proxy terminal', 'Proxy Terminal'],
        'retorno_anual_proxy': ['retorno_anual_proxy', 'Retorno Proxy aa'],
        'liquidez_dias': ['liquidez_dias', 'Liquidez'],
        'carencia_dias': ['carencia_dias', 'Carência'],
        'aplicacao_minima': ['aplicacao_minima', 'Ticket mín.'],
        'aplicacao_maxima': ['aplicacao_maxima'],
        'tipo_produto': ['tipo_produto'],
        'somente_combo': ['somente_combo'],
        'Status_Confirmação': ['Status_Confirmação'],
        'Campos_Pendentes': ['Campos_Pendentes'],
    }
    linha: dict[str, Any] = {}
    for coluna, nomes in aliases.items():
        valor = None
        for nome in nomes:
            if nome in item:
                valor = item.get(nome)
                break
        linha[coluna] = _valor_nan_para_vazio(valor)
    return linha


def _linha_carteira_ranking(item: dict[str, Any]) -> dict[str, Any]:
    normalizada = _normalizar_linha_ranking(item)
    return {
        cabecalho: normalizada.get(coluna)
        for coluna, cabecalho in zip(_COLUNAS_CARTEIRA_RANKING, _CABECALHOS_CARTEIRA_RANKING, strict=False)
    }


def _linha_amostra_ranking(item: dict[str, Any]) -> dict[str, Any]:
    normalizada = _normalizar_linha_ranking(item)
    return {
        'Rank': normalizada.get('rank_destino'),
        'Produto': normalizada.get('nome'),
        'Score': normalizada.get('score_final'),
        'Proxy terminal': normalizada.get('proxy_terminal_destino'),
        'Liquidez': normalizada.get('liquidez_dias'),
        'Carência': normalizada.get('carencia_dias'),
        'Ticket mín.': normalizada.get('aplicacao_minima'),
    }


def _materializar_ranking_carteira(ranking_carteira: Any | None) -> dict[str, list[dict[str, Any]]]:
    if ranking_carteira is None:
        return {'metricas': [], 'amostra': [], 'carteira': []}

    resumo = dict(getattr(ranking_carteira, 'resumo', {}) or {})
    auditoria = dict(getattr(ranking_carteira, 'auditoria', {}) or {})
    quadro = _registros_tabela(getattr(ranking_carteira, 'quadro_destinos_switch', None))
    return {
        'metricas': [
            {'Métrica': 'produtos totais', 'Valor': resumo.get('produtos_total')},
            {'Métrica': 'produtos ativos ranqueados', 'Valor': resumo.get('produtos_ativos_ranqueados')},
            {'Métrica': 'destinos elegíveis de switching', 'Valor': auditoria.get('qtd_destinos_switch')},
            {'Métrica': 'destino top 1', 'Valor': auditoria.get('destino_top1')},
            {'Métrica': 'método', 'Valor': auditoria.get('metodo')},
        ],
        'amostra': [_linha_amostra_ranking(item) for item in quadro[:10]],
        'carteira': [_linha_carteira_ranking(item) for item in quadro],
    }



def _materializar_situacao_atual_origem(origem: Any | None) -> dict[str, Any]:
    if origem is None:
        return {
            'fechamento': [],
            'lotes_exauridos_id': [],
            'lotes_exauridos_valores': [],
            'lotes_ativos_id': [],
            'lotes_ativos_valores': [],
            'origens_migradas': [],
            'patrimonio_total': [],
            'recebidos_auditaveis': [],
            'resumo_recebidos': [],
            'blocos': [],
        }

    blocos = list(_valor(origem, 'situacao_atual_blocos', []) or [])

    def _linhas_bloco(titulo: str) -> list[dict[str, Any]]:
        for bloco in blocos:
            if not isinstance(bloco, dict):
                continue
            if str(bloco.get('titulo') or '').strip() == titulo:
                return _snapshot_lista(bloco.get('linhas') or [])
        return []

    return {
        'fechamento': _snapshot_lista(_valor(origem, 'fechamento_atual', [])) or _linhas_bloco('Fechamento econômico'),
        'lotes_exauridos_id': _snapshot_lista(_valor(origem, 'situacao_atual_lotes_exauridos_id', [])) or _linhas_bloco('Lotes exauridos — identificação'),
        'lotes_exauridos_valores': _snapshot_lista(_valor(origem, 'situacao_atual_lotes_exauridos_valores', [])) or _linhas_bloco('Lotes exauridos — valores e patrimônio'),
        'lotes_ativos_id': _snapshot_lista(_valor(origem, 'situacao_atual_lotes_ativos_id', [])) or _linhas_bloco('Lotes ativos — identificação'),
        'lotes_ativos_valores': _snapshot_lista(_valor(origem, 'situacao_atual_lotes_ativos_valores', [])) or _linhas_bloco('Lotes ativos — valores e patrimônio'),
        'origens_migradas': _snapshot_lista(_valor(origem, 'situacao_atual_origens_migradas', [])) or _linhas_bloco('Origens migradas por switching — reconciliação patrimonial'),
        'patrimonio_total': _snapshot_lista(_valor(origem, 'situacao_atual_patrimonio_total', [])) or _linhas_bloco('Patrimônio total dos lotes'),
        'recebidos_auditaveis': _snapshot_lista(_valor(origem, 'recebidos_atuais', [])) or _linhas_bloco('Recebidos auditáveis'),
        'resumo_recebidos': _snapshot_lista(_valor(origem, 'resumo_recebidos', [])) or _linhas_bloco('Resumo de recebidos'),
        'blocos': _snapshot_lista(blocos),
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
        qtd_switchings_realizados_operacionais=len(_valor(ledger, 'switchings_realizados_operacionais', []) or []),
        qtd_lotes_pos_switching_materializados=len(_valor(ledger, 'lotes_pos_switching_materializados', []) or []),
        qtd_destinos_sobras_recebidos=len(_valor(ledger, 'destinos_sobras_recebidos', []) or []),
        qtd_lotes_futuros_materializados=len(_valor(ledger, 'lotes_futuros_materializados', []) or []),
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
        'funcoes_residuais_runtime_nao_consumidas': True,
        'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def _montar_saida(
    ledger: LedgerTemporalCanonico | None,
    gates: ResultadoGatesValidacaoNucleo | None,
    bloqueios_preparacao: list[BloqueioPreparacaoSaidaCanonicaOficial],
    preparada: bool,
    status: str,
    ranking_carteira: Any | None = None,
    situacao_atual_origem: Any | None = None,
) -> SaidaCanonicaOficial:
    incluir_operacional = preparada and ledger is not None
    ranking_materializado = _materializar_ranking_carteira(ranking_carteira) if incluir_operacional else {'metricas': [], 'amostra': [], 'carteira': []}
    situacao_atual = _materializar_situacao_atual_origem(situacao_atual_origem) if incluir_operacional else _materializar_situacao_atual_origem(None)
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
        pagamentos_historicos_realizados=_snapshot_lista(_valor(ledger, 'pagamentos_historicos_realizados', [])) if incluir_operacional else [],
        fontes_utilizadas=_snapshot_lista(_valor(ledger, 'fontes_utilizadas', [])) if incluir_operacional else [],
        fontes_reservadas=_snapshot_lista(_valor(ledger, 'fontes_reservadas', [])) if incluir_operacional else [],
        switchings_escolhidos=_snapshot_lista(_valor(ledger, 'switchings_escolhidos', [])) if incluir_operacional else [],
        switchings_realizados_operacionais=_snapshot_lista(_valor(ledger, 'switchings_realizados_operacionais', [])) if incluir_operacional else [],
        lotes_pos_switching_materializados=_snapshot_lista(_valor(ledger, 'lotes_pos_switching_materializados', [])) if incluir_operacional else [],
        saldos_referenciais_por_data=_snapshot_saldos(_valor(ledger, 'saldos_referenciais_por_data', {})) if incluir_operacional else {},
        destinos_sobras_recebidos=_snapshot_lista(_valor(ledger, 'destinos_sobras_recebidos', [])) if incluir_operacional else [],
        lotes_futuros_materializados=_snapshot_lista(_valor(ledger, 'lotes_futuros_materializados', [])) if incluir_operacional else [],
        ranking_metricas=ranking_materializado['metricas'],
        ranking_amostra=ranking_materializado['amostra'],
        ranking_carteira=ranking_materializado['carteira'],
        situacao_atual_fechamento=situacao_atual['fechamento'],
        situacao_atual_lotes_exauridos_id=situacao_atual['lotes_exauridos_id'],
        situacao_atual_lotes_exauridos_valores=situacao_atual['lotes_exauridos_valores'],
        situacao_atual_lotes_ativos_id=situacao_atual['lotes_ativos_id'],
        situacao_atual_lotes_ativos_valores=situacao_atual['lotes_ativos_valores'],
        situacao_atual_origens_migradas=situacao_atual['origens_migradas'],
        situacao_atual_patrimonio_total=situacao_atual['patrimonio_total'],
        situacao_atual_recebidos_auditaveis=situacao_atual['recebidos_auditaveis'],
        situacao_atual_resumo_recebidos=situacao_atual['resumo_recebidos'],
        situacao_atual_blocos=situacao_atual['blocos'],
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
    *,
    ranking_carteira: Any | None = None,
    situacao_atual_origem: Any | None = None,
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
        ranking_carteira=ranking_carteira,
        situacao_atual_origem=situacao_atual_origem,
    )


__all__ = [
    'BloqueioPreparacaoSaidaCanonicaOficial',
    'ResumoSaidaCanonicaOficial',
    'SaidaCanonicaOficial',
    'construir_saida_canonica_oficial',
]
