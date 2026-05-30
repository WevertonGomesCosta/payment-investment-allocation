from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime, timezone
from typing import Any

from nucleo.saida_canonica_oficial import SaidaCanonicaOficial


_ORIGEM_FORMAL = 'SaidaCanonicaOficial'
_ARTEFATO = 'PacoteRenderizacaoSaidaCanonica'
_VERSAO_SCHEMA = 'MACRO-ETAPA8-SAIDA-02'


@dataclass(slots=True)
class BloqueioRenderizacaoSaidaCanonica:
    codigo: str
    mensagem: str
    severidade: str = 'bloqueio'
    origem: str = 'AdaptadorRenderizacaoSaidaCanonica'
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ComponenteRenderizacaoSaidaCanonica:
    nome: str
    disponivel: bool
    origem: str
    headers: list[str] = field(default_factory=list)
    linhas: list[dict[str, Any]] = field(default_factory=list)
    motivo_indisponibilidade: str | None = None


@dataclass(slots=True)
class PacoteRenderizacaoSaidaCanonica:
    ok: bool
    preparado: bool
    status: str
    origem_formal: str
    componentes: dict[str, ComponenteRenderizacaoSaidaCanonica]
    metadados_renderizacao: dict[str, Any]
    bloqueios_renderizacao: list[BloqueioRenderizacaoSaidaCanonica] = field(default_factory=list)
    avisos_renderizacao: list[str] = field(default_factory=list)


def _snapshot(valor: Any) -> Any:
    if is_dataclass(valor):
        return asdict(valor)
    if isinstance(valor, dict):
        return dict(valor)
    return valor


def _lista(valores: list[Any] | None) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for valor in valores or []:
        item = _snapshot(valor)
        if isinstance(item, dict):
            linhas.append(item)
        else:
            linhas.append({'valor': item})
    return linhas


def _headers(linhas: list[dict[str, Any]]) -> list[str]:
    return sorted({str(chave) for linha in linhas for chave in linha.keys()})


def _linha(metrica: str, valor: Any) -> dict[str, Any]:
    return {'metrica': metrica, 'valor': valor}


def _componente(
    nome: str,
    origem: str,
    linhas: list[dict[str, Any]],
    motivo_vazio: str | None = None,
) -> ComponenteRenderizacaoSaidaCanonica:
    disponivel = bool(linhas) or motivo_vazio is None
    return ComponenteRenderizacaoSaidaCanonica(
        nome=nome,
        disponivel=disponivel,
        origem=origem,
        headers=_headers(linhas),
        linhas=linhas,
        motivo_indisponibilidade=None if disponivel else motivo_vazio,
    )


def _indisponivel(nome: str, motivo: str) -> ComponenteRenderizacaoSaidaCanonica:
    return ComponenteRenderizacaoSaidaCanonica(
        nome=nome,
        disponivel=False,
        origem=_ORIGEM_FORMAL,
        motivo_indisponibilidade=motivo,
    )


def _bloqueio(codigo: str, mensagem: str, referencias: dict[str, Any] | None = None) -> BloqueioRenderizacaoSaidaCanonica:
    return BloqueioRenderizacaoSaidaCanonica(
        codigo=codigo,
        mensagem=mensagem,
        referencias=referencias or {},
    )


def _situacao_atual(saida: SaidaCanonicaOficial) -> ComponenteRenderizacaoSaidaCanonica:
    resumo = saida.resumo
    linhas = [
        _linha('data_referencia', saida.data_referencia),
        _linha('status_saida_oficial', saida.status),
        _linha('saida_oficial_ok', saida.ok),
        _linha('saida_oficial_preparada', saida.preparada),
        _linha('qtd_eventos_ledger', resumo.qtd_eventos_ledger),
        _linha('qtd_obrigacoes_cobertas', resumo.qtd_obrigacoes_cobertas),
        _linha('qtd_obrigacoes_bloqueadas', resumo.qtd_obrigacoes_bloqueadas),
        _linha('qtd_fontes_utilizadas', resumo.qtd_fontes_utilizadas),
        _linha('qtd_fontes_reservadas', resumo.qtd_fontes_reservadas),
        _linha('qtd_switchings_escolhidos', resumo.qtd_switchings_escolhidos),
        _linha('qtd_bloqueios_ledger', resumo.qtd_bloqueios_ledger),
        _linha('qtd_avisos_ledger', resumo.qtd_avisos_ledger),
        _linha('qtd_bloqueios_gates', resumo.qtd_bloqueios_gates),
        _linha('qtd_avisos_gates', resumo.qtd_avisos_gates),
        _linha('qtd_evidencias_gates', resumo.qtd_evidencias_gates),
    ]
    return _componente('situacao_atual_renderizavel', 'SaidaCanonicaOficial.resumo', linhas)


def _auditoria(saida: SaidaCanonicaOficial) -> ComponenteRenderizacaoSaidaCanonica:
    linhas = [
        _linha('origem_formal', saida.origem_formal),
        _linha('ledger_origem', saida.ledger_origem),
        _linha('gates_origem', saida.gates_origem),
    ]
    for chave, valor in (saida.metadados or {}).items():
        if not isinstance(valor, (dict, list, tuple, set)):
            linhas.append(_linha(str(chave), valor))
    return _componente('auditoria_renderizavel', 'SaidaCanonicaOficial.metadados', linhas)


def _saldos(saida: SaidaCanonicaOficial) -> ComponenteRenderizacaoSaidaCanonica:
    linhas: list[dict[str, Any]] = []
    for data_ref, saldos in (saida.saldos_referenciais_por_data or {}).items():
        for saldo in saldos:
            item = dict(saldo)
            item['data_referencia_saldo'] = data_ref
            linhas.append(item)
    return _componente(
        'saldos_referenciais_renderizaveis',
        'SaidaCanonicaOficial.saldos_referenciais_por_data',
        linhas,
        motivo_vazio='sem saldos referenciais materializados na saida oficial',
    )


def _componentes(saida: SaidaCanonicaOficial) -> dict[str, ComponenteRenderizacaoSaidaCanonica]:
    motivo_legado = 'componente legado ainda nao derivavel diretamente do schema consolidado de SaidaCanonicaOficial'
    componentes = {
        'situacao_atual_renderizavel': _situacao_atual(saida),
        'auditoria_renderizavel': _auditoria(saida),
        'switchings_renderizaveis': _componente(
            'switchings_renderizaveis',
            'SaidaCanonicaOficial.switchings_escolhidos',
            _lista(saida.switchings_escolhidos),
            motivo_vazio='sem switchings escolhidos materializados na saida oficial',
        ),
        'obrigacoes_cobertas_renderizaveis': _componente(
            'obrigacoes_cobertas_renderizaveis',
            'SaidaCanonicaOficial.obrigacoes_cobertas',
            _lista(saida.obrigacoes_cobertas),
            motivo_vazio='sem obrigacoes cobertas materializadas na saida oficial',
        ),
        'obrigacoes_bloqueadas_renderizaveis': _componente(
            'obrigacoes_bloqueadas_renderizaveis',
            'SaidaCanonicaOficial.obrigacoes_bloqueadas',
            _lista(saida.obrigacoes_bloqueadas),
            motivo_vazio='sem obrigacoes bloqueadas materializadas na saida oficial',
        ),
        'fontes_utilizadas_renderizaveis': _componente(
            'fontes_utilizadas_renderizaveis',
            'SaidaCanonicaOficial.fontes_utilizadas',
            _lista(saida.fontes_utilizadas),
            motivo_vazio='sem fontes utilizadas materializadas na saida oficial',
        ),
        'fontes_reservadas_renderizaveis': _componente(
            'fontes_reservadas_renderizaveis',
            'SaidaCanonicaOficial.fontes_reservadas',
            _lista(saida.fontes_reservadas),
            motivo_vazio='sem fontes reservadas materializadas na saida oficial',
        ),
        'saldos_referenciais_renderizaveis': _saldos(saida),
        'bloqueios_renderizaveis': _componente(
            'bloqueios_renderizaveis',
            'SaidaCanonicaOficial.bloqueios_ledger+gates+preparacao',
            _lista(saida.bloqueios_ledger) + _lista(saida.bloqueios_gates) + _lista(saida.bloqueios_preparacao),
            motivo_vazio='sem bloqueios preservados na saida oficial',
        ),
        'avisos_renderizaveis': _componente(
            'avisos_renderizaveis',
            'SaidaCanonicaOficial.avisos_ledger+avisos_gates',
            [{'aviso': aviso} for aviso in (saida.avisos_ledger or [])] + _lista(saida.avisos_gates),
            motivo_vazio='sem avisos preservados na saida oficial',
        ),
        'evidencias_gates_renderizaveis': _componente(
            'evidencias_gates_renderizaveis',
            'SaidaCanonicaOficial.evidencias_gates',
            _lista(saida.evidencias_gates),
            motivo_vazio='sem evidencias dos gates preservadas na saida oficial',
        ),
        'extrato_passado_renderizavel': _indisponivel('extrato_passado_renderizavel', motivo_legado),
        'extrato_futuro_renderizavel': _indisponivel('extrato_futuro_renderizavel', motivo_legado),
        'resumo_recebidos_renderizavel': _indisponivel('resumo_recebidos_renderizavel', motivo_legado),
        'fechamento_atual_renderizavel': _indisponivel('fechamento_atual_renderizavel', motivo_legado),
        'ranking_renderizavel': _indisponivel('ranking_renderizavel', 'ranking nao integra a SaidaCanonicaOficial atual'),
    }
    return componentes


def _metadados(saida: SaidaCanonicaOficial, preparado: bool) -> dict[str, Any]:
    return {
        'artefato': _ARTEFATO,
        'versao_schema': _VERSAO_SCHEMA,
        'origem_exclusiva': _ORIGEM_FORMAL,
        'saida_oficial_status': saida.status,
        'saida_oficial_ok': saida.ok,
        'saida_oficial_preparada': saida.preparada,
        'pacote_preparado': preparado,
        'sem_reotimizacao': True,
        'sem_revaloracao': True,
        'sem_nova_escolha_fonte': True,
        'sem_alteracao_obrigacao': True,
        'sem_alteracao_switching': True,
        'sem_alteracao_saldo': True,
        'sem_consulta_dados_brutos': True,
        'sem_consulta_planilha': True,
        'sem_execucao_motor': True,
        'sem_execucao_ledger': True,
        'sem_execucao_gates': True,
        'sem_geracao_console': True,
        'sem_geracao_xlsx': True,
        'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def construir_pacote_renderizacao_saida_canonica(
    saida_oficial: SaidaCanonicaOficial,
) -> PacoteRenderizacaoSaidaCanonica:
    if not isinstance(saida_oficial, SaidaCanonicaOficial):
        bloqueio = _bloqueio(
            'entrada_nao_saida_canonica_oficial',
            'Entrada deve ser SaidaCanonicaOficial.',
            {'tipo_recebido': type(saida_oficial).__name__},
        )
        return PacoteRenderizacaoSaidaCanonica(
            ok=False,
            preparado=False,
            status='bloqueado_entrada_invalida',
            origem_formal=_ORIGEM_FORMAL,
            componentes={},
            metadados_renderizacao={
                'artefato': _ARTEFATO,
                'versao_schema': _VERSAO_SCHEMA,
                'origem_exclusiva': _ORIGEM_FORMAL,
                'gerado_em': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            },
            bloqueios_renderizacao=[bloqueio],
        )

    bloqueios: list[BloqueioRenderizacaoSaidaCanonica] = []
    if not saida_oficial.preparada:
        bloqueios.append(_bloqueio('saida_oficial_nao_preparada', 'SaidaCanonicaOficial.preparada=False bloqueia pacote renderizavel.'))
    if not saida_oficial.ok:
        bloqueios.append(_bloqueio('saida_oficial_nao_aprovada', 'SaidaCanonicaOficial.ok=False bloqueia pacote renderizavel.'))

    componentes = _componentes(saida_oficial)
    indisponiveis = [nome for nome, componente in componentes.items() if not componente.disponivel]
    preparado = not bloqueios
    avisos = [f'componentes_indisponiveis:{",".join(indisponiveis)}'] if indisponiveis else []

    return PacoteRenderizacaoSaidaCanonica(
        ok=preparado,
        preparado=preparado,
        status='preparado_com_indisponibilidades_explicitas' if preparado else 'bloqueado_por_saida_oficial',
        origem_formal=_ORIGEM_FORMAL,
        componentes=componentes,
        metadados_renderizacao=_metadados(saida_oficial, preparado),
        bloqueios_renderizacao=bloqueios,
        avisos_renderizacao=avisos,
    )


__all__ = [
    'BloqueioRenderizacaoSaidaCanonica',
    'ComponenteRenderizacaoSaidaCanonica',
    'PacoteRenderizacaoSaidaCanonica',
    'construir_pacote_renderizacao_saida_canonica',
]
