from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from nucleo.paridade_renderizacao_oficial import ResultadoParidadeRenderizacaoOficial


ARTEFATO_LIMPEZA_DEPRECIACAO = 'ResultadoLimpezaDepreciacaoControlada'
ENTRADA_FORMAL_LIMPEZA_DEPRECIACAO = 'ResultadoParidadeRenderizacaoOficial'
ORIGEM_FORMAL_LIMPEZA_DEPRECIACAO = 'Etapa 10 - ResultadoParidadeRenderizacaoOficial'
MODULO_LIMPEZA_DEPRECIACAO = 'nucleo/limpeza_depreciacao_controlada.py'
ETAPA_LIMPEZA_DEPRECIACAO = 11
CLASSIFICACOES_CONTROLADAS = (
    'oficial_preservar',
    'legado_candidato_depreciacao',
    'legado_manter_temporariamente',
    'historico_preservar',
    'bloqueado_dependencia_ativa',
    'avaliar_em_frente_posterior',
)
CATEGORIAS_RESSALVA_NAO_MATERIAL = {
    'CONSOLE_NAO_AUDITADO',
    'CONSOLE_AUDITADO_COM_RESSALVA',
    'MELHORIA_ERGONOMICA',
}
STATUS_PARIDADE_MATERIAL = {'bloqueado', 'reprovado'}


@dataclass(slots=True)
class ItemLimpezaDepreciacaoControlada:
    identificador: str
    classificacao: str
    origem: str
    descricao: str
    acao_recomendada: str
    decisorio: bool = False
    bloqueado_remocao: bool = True
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoLimpezaDepreciacaoControlada:
    qtd_itens_avaliados: int
    qtd_rotas_oficiais_preservadas: int
    qtd_rotas_legadas_candidatas: int
    qtd_itens_bloqueados_remocao: int
    qtd_ressalvas_nao_materiais: int
    qtd_bloqueios_paridade: int
    qtd_recomendacoes: int
    classificacao_limitada_por_ausencia_inventario: bool


@dataclass(slots=True)
class AuditoriaLimpezaDepreciacaoControlada:
    entrada_valida: bool
    paridade_status: str | None
    paridade_ok: bool | None
    qtd_divergencias_paridade: int
    qtd_divergencias_materiais: int
    evidencias_auxiliares_fornecidas: bool
    evidencias_auxiliares_decisorias: bool = False
    remocao_automatica_executada: bool = False
    fronteiras_preservadas: tuple[str, ...] = (
        'motor',
        'ledger',
        'gates',
        'etapa9',
        'etapa10',
        'contrato_mestre',
        'modelo_oficial',
        'dados_financeiros',
        'console_xlsx_economico',
        'logica_economica',
    )
    observacoes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MetadadosLimpezaDepreciacaoControlada:
    artefato: str = ARTEFATO_LIMPEZA_DEPRECIACAO
    etapa: int = ETAPA_LIMPEZA_DEPRECIACAO
    entrada_formal: str = ENTRADA_FORMAL_LIMPEZA_DEPRECIACAO
    origem_formal: str = ORIGEM_FORMAL_LIMPEZA_DEPRECIACAO
    modulo: str = MODULO_LIMPEZA_DEPRECIACAO
    gerado_em_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec='seconds'))
    evidencias_auxiliares_nao_decisorias: bool = True
    sem_remocao_automatica: bool = True
    sem_reotimizacao: bool = True
    sem_revaloracao: bool = True
    sem_alteracao_decisao: bool = True
    sem_consulta_motor: bool = True
    sem_consulta_ledger: bool = True
    sem_consulta_gates: bool = True
    classifica_sem_corrigir_paridade: bool = True
    classificacoes_controladas: tuple[str, ...] = CLASSIFICACOES_CONTROLADAS


@dataclass(slots=True)
class ResultadoLimpezaDepreciacaoControlada:
    artefato: str
    etapa: int
    status: str
    ok: bool
    entrada_formal: str
    origem_formal: str
    itens: list[ItemLimpezaDepreciacaoControlada]
    resumo: ResumoLimpezaDepreciacaoControlada
    auditoria: AuditoriaLimpezaDepreciacaoControlada
    metadados: MetadadosLimpezaDepreciacaoControlada
    recomendacoes: list[str]
    retorno_etapa1: dict[str, Any]


def _objeto_para_mapping(objeto: Any) -> dict[str, Any]:
    if objeto is None:
        return {}
    if isinstance(objeto, Mapping):
        return dict(objeto)
    if is_dataclass(objeto):
        return asdict(objeto)
    if hasattr(objeto, '__dict__'):
        return dict(vars(objeto))
    return {}


def _texto_minusculo(valor: Any) -> str:
    return str(valor or '').strip().lower()


def _classificacao_valida(classificacao: Any) -> str | None:
    texto = _texto_minusculo(classificacao)
    return texto if texto in CLASSIFICACOES_CONTROLADAS else None


def _classificar_evidencia_auxiliar(nome: str, dados: Mapping[str, Any] | None = None) -> str:
    dados = dados or {}
    classificacao_explicita = _classificacao_valida(
        dados.get('classificacao') or dados.get('categoria') or dados.get('status') or dados.get('tipo')
    )
    if classificacao_explicita:
        return classificacao_explicita

    texto = _texto_minusculo(' '.join([nome, *(str(v) for v in dados.values())]))
    if any(marcador in texto for marcador in ('dependencia ativa', 'dependência ativa', 'bloqueado', 'em uso')):
        return 'bloqueado_dependencia_ativa'
    if any(marcador in texto for marcador in ('oficial', 'canonic', 'canonico', 'canônico', 'principal', 'etapa 9', 'etapa9', 'etapa 10', 'etapa10')):
        return 'oficial_preservar'
    if any(marcador in texto for marcador in ('historico', 'histórico', 'contrato', 'relatorio', 'relatório', 'log')):
        return 'historico_preservar'
    if any(marcador in texto for marcador in ('temporario', 'temporário', 'transitorio', 'transitório', 'compatibilidade')):
        return 'legado_manter_temporariamente'
    if any(marcador in texto for marcador in ('legado', 'legacy', 'deprecated', 'depreciar', 'deprecar', 'v15', 'v16', 'old')):
        return 'legado_candidato_depreciacao'
    return 'avaliar_em_frente_posterior'


def _item(
    identificador: str,
    classificacao: str,
    origem: str,
    descricao: str,
    acao_recomendada: str,
    *,
    referencias: dict[str, Any] | None = None,
) -> ItemLimpezaDepreciacaoControlada:
    classificacao_final = _classificacao_valida(classificacao) or 'avaliar_em_frente_posterior'
    bloqueado_remocao = classificacao_final != 'legado_candidato_depreciacao'
    return ItemLimpezaDepreciacaoControlada(
        identificador=identificador,
        classificacao=classificacao_final,
        origem=origem,
        descricao=descricao,
        acao_recomendada=acao_recomendada,
        decisorio=False,
        bloqueado_remocao=bloqueado_remocao,
        referencias=referencias or {},
    )


def validar_entrada_limpeza_depreciacao(
    resultado_paridade_renderizacao: Any,
) -> tuple[bool, list[ItemLimpezaDepreciacaoControlada]]:
    if isinstance(resultado_paridade_renderizacao, ResultadoParidadeRenderizacaoOficial):
        return True, []
    return False, [
        _item(
            'entrada_formal',
            'bloqueado_dependencia_ativa',
            'validacao_entrada',
            'Entrada formal da Etapa 11 deve ser ResultadoParidadeRenderizacaoOficial.',
            'Bloquear limpeza/depreciação controlada até que a Etapa 10 forneça o artefato formal contratado.',
            referencias={
                'esperado': ENTRADA_FORMAL_LIMPEZA_DEPRECIACAO,
                'observado': type(resultado_paridade_renderizacao).__name__,
            },
        )
    ]


def extrair_evidencias_paridade(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
) -> dict[str, Any]:
    divergencias = list(getattr(resultado_paridade_renderizacao, 'divergencias', []) or [])
    materiais = [div for div in divergencias if bool(getattr(div, 'material', False))]
    ressalvas = [div for div in divergencias if not bool(getattr(div, 'material', False))]
    return {
        'artefato': getattr(resultado_paridade_renderizacao, 'artefato', None),
        'etapa': getattr(resultado_paridade_renderizacao, 'etapa', None),
        'status': getattr(resultado_paridade_renderizacao, 'status', None),
        'ok': getattr(resultado_paridade_renderizacao, 'ok', None),
        'entrada_formal': getattr(resultado_paridade_renderizacao, 'entrada_formal', None),
        'divergencias': divergencias,
        'divergencias_materiais': materiais,
        'ressalvas': ressalvas,
    }


def verificar_status_paridade(evidencias_paridade: Mapping[str, Any]) -> dict[str, Any]:
    status = _texto_minusculo(evidencias_paridade.get('status'))
    materiais = list(evidencias_paridade.get('divergencias_materiais') or [])
    bloqueado = status in STATUS_PARIDADE_MATERIAL or bool(materiais)
    return {
        'status_paridade': status or None,
        'paridade_bloqueante': bloqueado,
        'qtd_divergencias_materiais': len(materiais),
    }


def _normalizar_evidencias_iteraveis(evidencias_auxiliares: object | None) -> list[dict[str, Any]]:
    if evidencias_auxiliares is None:
        return []
    normalizadas: list[dict[str, Any]] = []
    if isinstance(evidencias_auxiliares, Mapping):
        for chave, valor in evidencias_auxiliares.items():
            if isinstance(valor, (list, tuple, set)):
                for item_aux in valor:
                    dados = _objeto_para_mapping(item_aux)
                    identificador = dados.get('identificador') or dados.get('nome') or dados.get('path') or str(item_aux)
                    normalizadas.append({'grupo': str(chave), 'identificador': str(identificador), **dados})
            else:
                dados = _objeto_para_mapping(valor)
                identificador = dados.get('identificador') or dados.get('nome') or dados.get('path') or str(chave)
                normalizadas.append({'grupo': str(chave), 'identificador': str(identificador), **dados})
        return normalizadas
    if isinstance(evidencias_auxiliares, (list, tuple, set)):
        for item_aux in evidencias_auxiliares:
            dados = _objeto_para_mapping(item_aux)
            identificador = dados.get('identificador') or dados.get('nome') or dados.get('path') or str(item_aux)
            normalizadas.append({'grupo': 'inventario_auxiliar', 'identificador': str(identificador), **dados})
        return normalizadas
    dados = _objeto_para_mapping(evidencias_auxiliares)
    if dados:
        identificador = dados.get('identificador') or dados.get('nome') or type(evidencias_auxiliares).__name__
        normalizadas.append({'grupo': 'inventario_auxiliar', 'identificador': str(identificador), **dados})
    return normalizadas


def incorporar_evidencias_auxiliares_nao_decisorias(
    evidencias_auxiliares: object | None,
) -> list[ItemLimpezaDepreciacaoControlada]:
    itens: list[ItemLimpezaDepreciacaoControlada] = []
    for evidencia in _normalizar_evidencias_iteraveis(evidencias_auxiliares):
        identificador = str(evidencia.get('identificador') or evidencia.get('nome') or evidencia.get('path') or 'evidencia_auxiliar')
        classificacao = _classificar_evidencia_auxiliar(identificador, evidencia)
        acao = 'Preservar sem alteração automática.'
        if classificacao == 'legado_candidato_depreciacao':
            acao = 'Registrar como candidato para depreciação em frente posterior, sem remoção automática nesta etapa.'
        elif classificacao == 'legado_manter_temporariamente':
            acao = 'Manter temporariamente por compatibilidade e reavaliar em frente posterior.'
        elif classificacao == 'bloqueado_dependencia_ativa':
            acao = 'Bloquear remoção por indicação auxiliar de dependência ativa ou uso atual.'
        elif classificacao == 'avaliar_em_frente_posterior':
            acao = 'Avaliar em frente posterior com inventário dedicado antes de qualquer depreciação.'
        itens.append(
            _item(
                identificador,
                classificacao,
                'evidencia_auxiliar_nao_decisoria',
                f'Evidência auxiliar classificada de forma não decisória no grupo {evidencia.get("grupo", "inventario_auxiliar")}.',
                acao,
                referencias={k: v for k, v in evidencia.items() if k != 'identificador'},
            )
        )
    return itens


def classificar_ressalvas_nao_materiais(
    evidencias_paridade: Mapping[str, Any],
) -> list[ItemLimpezaDepreciacaoControlada]:
    itens: list[ItemLimpezaDepreciacaoControlada] = []
    for indice, ressalva in enumerate(evidencias_paridade.get('ressalvas') or [], start=1):
        categoria = getattr(ressalva, 'categoria', 'RESSALVA_NAO_MATERIAL')
        alvo = getattr(ressalva, 'alvo', 'paridade')
        mensagem = getattr(ressalva, 'mensagem', '')
        classificacao = 'avaliar_em_frente_posterior'
        acao = 'Registrar como pendência de compatibilidade ou melhoria futura; não tratar como falha econômica.'
        if categoria not in CATEGORIAS_RESSALVA_NAO_MATERIAL:
            acao = 'Reavaliar ressalva não material em frente posterior; não remover artefatos nesta etapa.'
        itens.append(
            _item(
                f'ressalva_nao_material_{indice}:{categoria}',
                classificacao,
                'resultado_paridade_renderizacao_oficial',
                f'Ressalva não material da paridade em {alvo}: {mensagem}',
                acao,
                referencias={'categoria': categoria, 'alvo': alvo},
            )
        )
    return itens


def identificar_rotas_oficiais_preservadas(itens: Iterable[ItemLimpezaDepreciacaoControlada]) -> list[ItemLimpezaDepreciacaoControlada]:
    return [item for item in itens if item.classificacao == 'oficial_preservar']


def identificar_rotas_legadas_candidatas(itens: Iterable[ItemLimpezaDepreciacaoControlada]) -> list[ItemLimpezaDepreciacaoControlada]:
    return [item for item in itens if item.classificacao == 'legado_candidato_depreciacao']


def classificar_itens_limpeza(
    evidencias_paridade: Mapping[str, Any],
    itens_auxiliares: list[ItemLimpezaDepreciacaoControlada],
    *,
    evidencias_auxiliares_fornecidas: bool,
) -> list[ItemLimpezaDepreciacaoControlada]:
    itens = [
        _item(
            'ResultadoParidadeRenderizacaoOficial',
            'oficial_preservar',
            'entrada_formal',
            'Artefato formal da Etapa 10 usado como estado exclusivo da Etapa 11.',
            'Preservar como entrada formal obrigatória; não corrigir nem substituir por inventário auxiliar.',
            referencias={
                'artefato': evidencias_paridade.get('artefato'),
                'etapa': evidencias_paridade.get('etapa'),
                'status': evidencias_paridade.get('status'),
            },
        )
    ]
    itens.extend(classificar_ressalvas_nao_materiais(evidencias_paridade))
    itens.extend(itens_auxiliares)
    if not evidencias_auxiliares_fornecidas:
        itens.append(
            _item(
                'inventario_auxiliar_ausente',
                'avaliar_em_frente_posterior',
                'classificacao_conservadora',
                'Nenhuma evidência auxiliar de inventário estático foi fornecida.',
                'Manter classificação mínima conservadora; rotas legadas devem ser inventariadas antes de qualquer depreciação.',
                referencias={'limitacao': 'classificacao_de_rotas_legadas_limitada'},
            )
        )
    return itens


def classificar_bloqueios_depreciacao(
    itens: list[ItemLimpezaDepreciacaoControlada],
    verificacao_paridade: Mapping[str, Any],
) -> list[ItemLimpezaDepreciacaoControlada]:
    bloqueios: list[ItemLimpezaDepreciacaoControlada] = []
    if verificacao_paridade.get('paridade_bloqueante'):
        bloqueios.append(
            _item(
                'paridade_material_bloqueante',
                'bloqueado_dependencia_ativa',
                'resultado_paridade_renderizacao_oficial',
                'ResultadoParidadeRenderizacaoOficial indica divergência material ou status bloqueante.',
                'Bloquear depreciação e limpeza automática; corrigir paridade em frente apropriada sem reabrir esta etapa.',
                referencias=dict(verificacao_paridade),
            )
        )
    bloqueios.extend(item for item in itens if item.classificacao == 'bloqueado_dependencia_ativa')
    return bloqueios


def montar_plano_retorno_etapa1(
    status: str,
    itens: list[ItemLimpezaDepreciacaoControlada],
    recomendacoes: list[str],
    bloqueios: list[ItemLimpezaDepreciacaoControlada] | None = None,
) -> dict[str, Any]:
    bloqueios = bloqueios or []
    bloqueios_dependencia_ativa = [item for item in bloqueios if item.classificacao == 'bloqueado_dependencia_ativa']
    retorno_operacional_permitido = status in {'aprovado', 'aprovado_com_ressalva'}
    return {
        'destino': 'Etapa 1',
        'permitido': retorno_operacional_permitido and not bloqueios_dependencia_ativa,
        'retorno_operacional_permitido': retorno_operacional_permitido,
        'modo': 'retorno_controlado_sem_alteracao_economica',
        'status_limpeza_depreciacao': status,
        'qtd_itens_para_revisao': sum(1 for item in itens if item.classificacao == 'avaliar_em_frente_posterior'),
        'qtd_candidatos_depreciacao': sum(1 for item in itens if item.classificacao == 'legado_candidato_depreciacao'),
        'qtd_bloqueios_dependencia_ativa': len(bloqueios_dependencia_ativa),
        'bloqueado_por_dependencia_ativa': bool(bloqueios_dependencia_ativa),
        'depreciacao_efetiva_permitida': False,
        'remocao_automatica_autorizada': False,
        'proximas_acoes': recomendacoes[:5],
    }


def consolidar_resultado_limpeza_depreciacao(
    *,
    entrada_valida: bool,
    evidencias_paridade: Mapping[str, Any],
    verificacao_paridade: Mapping[str, Any],
    itens: list[ItemLimpezaDepreciacaoControlada],
    bloqueios: list[ItemLimpezaDepreciacaoControlada],
    evidencias_auxiliares_fornecidas: bool,
) -> tuple[str, bool, ResumoLimpezaDepreciacaoControlada, AuditoriaLimpezaDepreciacaoControlada, list[str]]:
    ressalvas = list(evidencias_paridade.get('ressalvas') or [])
    bloqueios_dependencia_ativa = [item for item in bloqueios if item.classificacao == 'bloqueado_dependencia_ativa']
    if not entrada_valida or verificacao_paridade.get('paridade_bloqueante'):
        status = 'bloqueado'
    elif bloqueios_dependencia_ativa:
        status = 'aprovado_com_ressalva'
    elif ressalvas or not evidencias_auxiliares_fornecidas:
        status = 'aprovado_com_ressalva'
    else:
        status = 'aprovado'
    ok = status in {'aprovado', 'aprovado_com_ressalva'}
    qtd_oficiais = sum(1 for item in itens if item.classificacao == 'oficial_preservar')
    qtd_legadas = sum(1 for item in itens if item.classificacao == 'legado_candidato_depreciacao')
    qtd_bloqueados = sum(1 for item in itens if item.bloqueado_remocao) + len([b for b in bloqueios if b not in itens])
    recomendacoes = [
        'Não executar remoção automática nesta etapa.',
        'Preservar ResultadoParidadeRenderizacaoOficial como entrada formal exclusiva de estado.',
    ]
    if verificacao_paridade.get('paridade_bloqueante'):
        recomendacoes.append('Tratar divergências materiais de paridade antes de qualquer plano de limpeza efetiva.')
    if bloqueios_dependencia_ativa:
        recomendacoes.append('Resolver ou documentar dependências ativas antes de qualquer depreciação ou remoção efetiva.')
    if not evidencias_auxiliares_fornecidas:
        recomendacoes.append('Executar inventário estático auxiliar em frente posterior para classificar rotas legadas com maior precisão.')
    if ressalvas:
        recomendacoes.append('Manter ressalvas não materiais como pendências de compatibilidade ou melhoria futura.')
    if qtd_legadas:
        recomendacoes.append('Revisar candidatos legados em frente posterior antes de depreciação operacional.')

    resumo = ResumoLimpezaDepreciacaoControlada(
        qtd_itens_avaliados=len(itens),
        qtd_rotas_oficiais_preservadas=qtd_oficiais,
        qtd_rotas_legadas_candidatas=qtd_legadas,
        qtd_itens_bloqueados_remocao=qtd_bloqueados,
        qtd_ressalvas_nao_materiais=len(ressalvas),
        qtd_bloqueios_paridade=len(bloqueios),
        qtd_recomendacoes=len(recomendacoes),
        classificacao_limitada_por_ausencia_inventario=not evidencias_auxiliares_fornecidas,
    )
    auditoria = AuditoriaLimpezaDepreciacaoControlada(
        entrada_valida=entrada_valida,
        paridade_status=evidencias_paridade.get('status'),
        paridade_ok=evidencias_paridade.get('ok'),
        qtd_divergencias_paridade=len(evidencias_paridade.get('divergencias') or []),
        qtd_divergencias_materiais=int(verificacao_paridade.get('qtd_divergencias_materiais') or 0),
        evidencias_auxiliares_fornecidas=evidencias_auxiliares_fornecidas,
        observacoes=[
            'Evidências auxiliares são usadas apenas para classificação não decisória.',
            'Etapa 11 não reabre motor, ledger, gates, Etapa 9 ou Etapa 10.',
            'Dependências ativas rebaixam o status e bloqueiam depreciação/remoção efetiva.',
        ],
    )
    return status, ok, resumo, auditoria, recomendacoes


def montar_metadados_limpeza_depreciacao() -> MetadadosLimpezaDepreciacaoControlada:
    return MetadadosLimpezaDepreciacaoControlada()


def construir_resultado_limpeza_depreciacao_controlada(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
    evidencias_auxiliares: object | None = None,
) -> ResultadoLimpezaDepreciacaoControlada:
    entrada_valida, itens_validacao = validar_entrada_limpeza_depreciacao(resultado_paridade_renderizacao)
    if entrada_valida:
        evidencias_paridade = extrair_evidencias_paridade(resultado_paridade_renderizacao)
    else:
        evidencias_paridade = {
            'artefato': None,
            'etapa': None,
            'status': 'bloqueado',
            'ok': False,
            'entrada_formal': None,
            'divergencias': [],
            'divergencias_materiais': [],
            'ressalvas': [],
        }
    verificacao_paridade = verificar_status_paridade(evidencias_paridade)
    itens_auxiliares = incorporar_evidencias_auxiliares_nao_decisorias(evidencias_auxiliares)
    evidencias_auxiliares_fornecidas = evidencias_auxiliares is not None
    itens = itens_validacao + classificar_itens_limpeza(
        evidencias_paridade,
        itens_auxiliares,
        evidencias_auxiliares_fornecidas=evidencias_auxiliares_fornecidas,
    )
    bloqueios = classificar_bloqueios_depreciacao(itens, verificacao_paridade)
    status, ok, resumo, auditoria, recomendacoes = consolidar_resultado_limpeza_depreciacao(
        entrada_valida=entrada_valida,
        evidencias_paridade=evidencias_paridade,
        verificacao_paridade=verificacao_paridade,
        itens=itens,
        bloqueios=bloqueios,
        evidencias_auxiliares_fornecidas=evidencias_auxiliares_fornecidas,
    )
    retorno_etapa1 = montar_plano_retorno_etapa1(status, itens, recomendacoes, bloqueios=bloqueios)
    metadados = montar_metadados_limpeza_depreciacao()
    return ResultadoLimpezaDepreciacaoControlada(
        artefato=ARTEFATO_LIMPEZA_DEPRECIACAO,
        etapa=ETAPA_LIMPEZA_DEPRECIACAO,
        status=status,
        ok=ok,
        entrada_formal=ENTRADA_FORMAL_LIMPEZA_DEPRECIACAO,
        origem_formal=ORIGEM_FORMAL_LIMPEZA_DEPRECIACAO,
        itens=itens,
        resumo=resumo,
        auditoria=auditoria,
        metadados=metadados,
        recomendacoes=recomendacoes,
        retorno_etapa1=retorno_etapa1,
    )
