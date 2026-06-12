from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping
import unicodedata

from nucleo.paridade_renderizacao_oficial import ResultadoParidadeRenderizacaoOficial


ARTEFATO_GOVERNANCA_RESIDUOS = 'ResultadoGovernancaResiduosPipeline'
ETAPA_GOVERNANCA_RESIDUOS = 11
ENTRADA_FORMAL = 'ResultadoParidadeRenderizacaoOficial'
MODULO_GOVERNANCA_RESIDUOS = 'nucleo/governanca_residuos_pipeline.py'

_CLASSIFICACAO_OFICIAL = 'rota_oficial_preservada'
_CLASSIFICACAO_RESIDUO = 'residuo_candidato_tratamento'
_CLASSIFICACAO_RESIDUO_REMOVIDO = 'residuo_removido'
_CLASSIFICACAO_HISTORICO = 'referencia_historica_preservada'
_CLASSIFICACAO_DIAGNOSTICO = 'diagnostico_preservado_fora_pipeline'
_CLASSIFICACAO_BLOQUEADO = 'residuo_bloqueado_dependencia_ativa'
_CLASSIFICACAO_FALLBACK = 'rota_alternativa_temporaria_bloqueada_tratamento'
_CLASSIFICACAO_LIMITADA = 'classificacao_limitada_por_ausencia_inventario'
_CLASSIFICACAO_INVENTARIO_AUSENTE = 'inventario_residuos_auxiliar_ausente'
_CLASSIFICACAO_AVALIACAO_FUTURA = 'avaliacao_tratamento_futuro'

_CLASSIFICACOES_PADRONIZADAS = {
    _CLASSIFICACAO_OFICIAL,
    _CLASSIFICACAO_RESIDUO,
    _CLASSIFICACAO_RESIDUO_REMOVIDO,
    _CLASSIFICACAO_BLOQUEADO,
    _CLASSIFICACAO_HISTORICO,
    _CLASSIFICACAO_DIAGNOSTICO,
    _CLASSIFICACAO_FALLBACK,
    _CLASSIFICACAO_AVALIACAO_FUTURA,
}

_CLASSIFICACOES_RESIDUO_IDENTIFICADO = {
    _CLASSIFICACAO_RESIDUO,
    _CLASSIFICACAO_RESIDUO_REMOVIDO,
    _CLASSIFICACAO_BLOQUEADO,
    _CLASSIFICACAO_FALLBACK,
    _CLASSIFICACAO_AVALIACAO_FUTURA,
}


@dataclass(slots=True)
class ItemGovernancaResiduoPipeline:
    identificador: str
    classificacao: str
    origem: str
    motivo: str
    acao_automatica_autorizada: bool = False
    evidencia_dependencia_ativa: bool = False
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoGovernancaResiduosPipeline:
    status: str
    ok: bool
    qtd_artefatos_avaliados: int
    qtd_rotas_oficiais_preservadas: int
    qtd_residuos_identificados: int
    qtd_residuos_bloqueados: int
    qtd_residuos_candidatos_tratamento: int
    qtd_pendencias_nao_materiais: int
    qtd_bloqueios_governanca: int
    classificacao_limitada_por_ausencia_inventario: bool
    acao_automatica_autorizada: bool = False
    qtd_historicos_diagnosticos_preservados: int = 0
    qtd_fallbacks_temporarios_bloqueados: int = 0


@dataclass(slots=True)
class AuditoriaGovernancaResiduosPipeline:
    paridade_status: str | None
    paridade_ok: bool | None
    inventario_residuos_auxiliar_fornecido: bool
    classificacao_limitada_por_ausencia_inventario: bool
    divergencias_materiais_paridade: list[str] = field(default_factory=list)
    ressalvas_paridade: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MetadadosGovernancaResiduosPipeline:
    artefato: str = ARTEFATO_GOVERNANCA_RESIDUOS
    etapa: int = ETAPA_GOVERNANCA_RESIDUOS
    entrada_formal: str = ENTRADA_FORMAL
    modulo: str = MODULO_GOVERNANCA_RESIDUOS
    data_referencia: str | None = None
    evidencias_auxiliares_nao_decisorias: bool = True
    sem_reotimizacao: bool = True
    sem_revaloracao: bool = True
    sem_alteracao_decisao: bool = True
    sem_consulta_motor: bool = True
    sem_consulta_ledger: bool = True
    sem_consulta_gates: bool = True
    sem_alteracao_etapa9: bool = True
    sem_alteracao_etapa10: bool = True
    sem_alteracao_dados_financeiros: bool = True
    acao_automatica_autorizada: bool = False


@dataclass(slots=True)
class ResultadoGovernancaResiduosPipeline:
    artefato: str
    etapa: int
    status: str
    ok: bool
    entrada_formal: str
    origem_formal: str
    data_referencia: str | None
    artefatos_avaliados: list[ItemGovernancaResiduoPipeline]
    rotas_oficiais_preservadas: list[ItemGovernancaResiduoPipeline]
    residuos_identificados: list[ItemGovernancaResiduoPipeline]
    residuos_bloqueados_tratamento: list[ItemGovernancaResiduoPipeline]
    residuos_candidatos_tratamento: list[ItemGovernancaResiduoPipeline]
    classes_candidatas_avaliacao_tratamento_futuro: list[ItemGovernancaResiduoPipeline]
    classes_preservadas_historico: list[ItemGovernancaResiduoPipeline]
    pendencias_nao_materiais_release: list[str]
    bloqueios_governanca: list[str]
    recomendacoes_governanca_residuos: list[str]
    plano_retorno_etapa1: list[str]
    resumo: ResumoGovernancaResiduosPipeline
    auditoria: AuditoriaGovernancaResiduosPipeline
    metadados: MetadadosGovernancaResiduosPipeline


def _sem_acentos(texto: str) -> str:
    return ''.join(
        caractere for caractere in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(caractere)
    )


def _normalizar_texto(valor: Any) -> str:
    return _sem_acentos(str(valor).casefold()).strip()


def _tokenizar(valor: Any) -> set[str]:
    texto = _normalizar_texto(valor)
    tokens = []
    atual = []
    for caractere in texto:
        if caractere.isalnum():
            atual.append(caractere)
            continue
        if atual:
            tokens.append(''.join(atual))
            atual = []
    if atual:
        tokens.append(''.join(atual))
    return set(tokens)


def _contem_frase(valor: Any, frase: str) -> bool:
    texto = f' {_normalizar_texto(valor)} '
    frase_normalizada = f' {_normalizar_texto(frase)} '
    return frase_normalizada in texto


def _indicador_negacao_bloqueio(valor: Any) -> bool:
    texto = _normalizar_texto(valor)
    return any(
        padrao in f' {texto} '
        for padrao in (
            ' nao bloqueado ',
            ' nao-bloqueado ',
            ' desbloqueado ',
            ' sem bloqueio ',
            ' livre de bloqueio ',
        )
    )


def _indica_dependencia_ativa(chave: Any, valor: Any) -> bool:
    if _indicador_negacao_bloqueio(chave) or _indicador_negacao_bloqueio(valor):
        return False
    texto_chave = _normalizar_texto(chave)
    texto_valor = _normalizar_texto(valor)
    tokens_chave = _tokenizar(chave)
    tokens_valor = _tokenizar(valor)
    texto_completo = f'{texto_chave} {texto_valor}'

    if 'sem uso' in texto_completo or 'fora_do_pipeline' in texto_completo or 'depreciad' in texto_completo:
        return False
    if texto_valor in {'bloqueado', 'dependencia ativa', 'dependencia_ativa', 'ativa'}:
        return True
    if texto_valor == 'ativo' and ({'dependencia', 'dependencias'} & tokens_chave):
        return True
    return bool({'bloqueado'} & tokens_valor) or _contem_frase(texto_completo, 'dependencia ativa')


def _indica_residuo(chave: Any, valor: Any) -> bool:
    tokens = _tokenizar(chave) | _tokenizar(valor)
    texto = f'{_normalizar_texto(chave)} {_normalizar_texto(valor)}'
    return bool({'historica', 'residual', 'fora_do_pipeline', 'fora_do_pipeline', 'tratamento'} & tokens) or 'fora_do_pipeline' in texto


def _indica_oficial(chave: Any, valor: Any) -> bool:
    tokens = _tokenizar(chave) | _tokenizar(valor)
    return bool({'oficial', 'preservada', 'preservado', 'canonica', 'canonico'} & tokens)


def _indica_historico(chave: Any, valor: Any) -> bool:
    tokens = _tokenizar(chave) | _tokenizar(valor)
    return bool({'historico', 'historica', 'arquivo', 'memoria'} & tokens)


def _valor_bool(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return bool(valor)
    return _normalizar_texto(valor) in {'true', '1', 'sim', 's', 'yes', 'dependencia ativa', 'ativa'}


def _iterar_evidencias(evidencias_auxiliares: Any, prefixo: str = 'inventario') -> Iterable[tuple[str, Any, Any]]:
    if isinstance(evidencias_auxiliares, Mapping):
        for chave, valor in evidencias_auxiliares.items():
            identificador = f'{prefixo}.{chave}'
            yield identificador, chave, valor
            if isinstance(valor, Mapping):
                yield from _iterar_evidencias(valor, identificador)
            elif isinstance(valor, (list, tuple)):
                yield from _iterar_evidencias(valor, identificador)
    elif isinstance(evidencias_auxiliares, (list, tuple)):
        for indice, valor in enumerate(evidencias_auxiliares):
            identificador = f'{prefixo}[{indice}]'
            yield identificador, indice, valor
            if isinstance(valor, (Mapping, list, tuple)):
                yield from _iterar_evidencias(valor, identificador)


def _como_mapping(valor: Any) -> Mapping[str, Any] | None:
    if isinstance(valor, Mapping):
        return valor
    como_dict = getattr(valor, 'como_dict', None)
    if callable(como_dict):
        convertido = como_dict()
        if isinstance(convertido, Mapping):
            return convertido
    return None


def _parece_item_inventario(valor: Any) -> bool:
    item = _como_mapping(valor)
    return bool(
        item
        and item.get('identificador')
        and item.get('arquivo')
        and (item.get('simbolo_funcao_classe') or item.get('símbolo/função/classe') or item.get('simbolo'))
    )


def _extrair_itens_formais_inventario(evidencias_auxiliares: Any) -> list[Mapping[str, Any]] | None:
    evidencia = _como_mapping(evidencias_auxiliares)
    if evidencia is not None:
        candidatos = (
            evidencia.get('itens')
            or evidencia.get('itens_inventario')
            or evidencia.get('artefatos_avaliados')
            or evidencia.get('rotas')
        )
        if isinstance(candidatos, (list, tuple)):
            itens = [_como_mapping(item) for item in candidatos]
            itens_validos = [item for item in itens if item is not None and _parece_item_inventario(item)]
            if itens_validos:
                return itens_validos
        if _parece_item_inventario(evidencia):
            return [evidencia]
    if isinstance(evidencias_auxiliares, (list, tuple)):
        itens = [_como_mapping(item) for item in evidencias_auxiliares]
        itens_validos = [item for item in itens if item is not None and _parece_item_inventario(item)]
        if itens_validos:
            return itens_validos
    return None


def _normalizar_classificacao_inventario(item: Mapping[str, Any]) -> str:
    classificacao = str(item.get('classificacao') or '').strip()
    if classificacao in _CLASSIFICACOES_PADRONIZADAS:
        return classificacao
    if _valor_bool(item.get('dependencia_ativa')):
        return _CLASSIFICACAO_BLOQUEADO
    tipo = f"{item.get('tipo', '')} {item.get('decisao_recomendada', '')} {item.get('uso_atual', '')}"
    if _indica_oficial('classificacao', tipo):
        return _CLASSIFICACAO_OFICIAL
    if 'fallback' in _normalizar_texto(tipo):
        return _CLASSIFICACAO_FALLBACK
    if 'diagnostico' in _normalizar_texto(tipo):
        return _CLASSIFICACAO_DIAGNOSTICO
    if _indica_historico('classificacao', tipo):
        return _CLASSIFICACAO_HISTORICO
    if _indica_residuo('classificacao', tipo):
        return _CLASSIFICACAO_RESIDUO
    return _CLASSIFICACAO_AVALIACAO_FUTURA


def _converter_item_inventario(item: Mapping[str, Any]) -> ItemGovernancaResiduoPipeline:
    classificacao = _normalizar_classificacao_inventario(item)
    dependencia_ativa = _valor_bool(item.get('dependencia_ativa')) or classificacao in {
        _CLASSIFICACAO_BLOQUEADO,
        _CLASSIFICACAO_FALLBACK,
    }
    motivo = str(
        item.get('justificativa_de_classificacao')
        or item.get('justificativa')
        or item.get('evidencia')
        or 'Item de inventário formal classificado como evidência auxiliar não decisória.'
    )
    return ItemGovernancaResiduoPipeline(
        identificador=str(item.get('identificador')),
        classificacao=classificacao,
        origem='inventario_residuos_pipeline_estatico',
        motivo=motivo,
        acao_automatica_autorizada=False,
        evidencia_dependencia_ativa=dependencia_ativa,
        referencias=dict(item),
    )


def validar_entrada_governanca_residuos(resultado_paridade_renderizacao: Any) -> list[str]:
    if not isinstance(resultado_paridade_renderizacao, ResultadoParidadeRenderizacaoOficial):
        return [
            'Entrada da Etapa 11 deve ser ResultadoParidadeRenderizacaoOficial; '
            f'observado={type(resultado_paridade_renderizacao).__name__}.'
        ]
    return []


def _extrair_data_referencia(resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial) -> str | None:
    for objeto in (resultado_paridade_renderizacao, getattr(resultado_paridade_renderizacao, 'metadados', None)):
        data = getattr(objeto, 'data_referencia', None)
        if data:
            return str(data)
    return date.today().isoformat()


def _classificar_evidencias(evidencias_auxiliares: Any) -> tuple[list[ItemGovernancaResiduoPipeline], bool]:
    if evidencias_auxiliares in (None, {}, []):
        item = ItemGovernancaResiduoPipeline(
            identificador='inventario_residuos_auxiliar',
            classificacao=_CLASSIFICACAO_INVENTARIO_AUSENTE,
            origem='evidencia_auxiliar_nao_decisoria',
            motivo='Inventário auxiliar não fornecido; classificação de limpeza fica limitada.',
            referencias={'classificacao_limitada_por_ausencia_inventario': True},
        )
        return [item], True

    itens_formais = _extrair_itens_formais_inventario(evidencias_auxiliares)
    if itens_formais:
        return [_converter_item_inventario(item) for item in itens_formais], False

    itens: list[ItemGovernancaResiduoPipeline] = []
    vistos: set[str] = set()
    for identificador, chave, valor in _iterar_evidencias(evidencias_auxiliares):
        if identificador in vistos:
            continue
        vistos.add(identificador)
        if _indica_dependencia_ativa(chave, valor):
            classificacao = _CLASSIFICACAO_BLOQUEADO
            motivo = 'Evidência auxiliar indica bloqueio por dependência ativa; remoção futura deve permanecer bloqueada.'
            dependencia_ativa = True
        elif _indica_residuo(chave, valor):
            classificacao = _CLASSIFICACAO_RESIDUO
            motivo = 'Evidência auxiliar indica rota/artefato residual candidato à tratamento controlada.'
            dependencia_ativa = False
        elif _indica_oficial(chave, valor):
            classificacao = _CLASSIFICACAO_OFICIAL
            motivo = 'Evidência auxiliar indica rota/artefato oficial preservado.'
            dependencia_ativa = False
        elif _indica_historico(chave, valor):
            classificacao = _CLASSIFICACAO_HISTORICO
            motivo = 'Evidência auxiliar indica artefato histórico a preservar.'
            dependencia_ativa = False
        else:
            classificacao = _CLASSIFICACAO_AVALIACAO_FUTURA
            motivo = 'Evidência auxiliar não decisória requer avaliação futura em frente específica.'
            dependencia_ativa = False
        itens.append(
            ItemGovernancaResiduoPipeline(
                identificador=identificador,
                classificacao=classificacao,
                origem='evidencia_auxiliar_nao_decisoria',
                motivo=motivo,
                acao_automatica_autorizada=False,
                evidencia_dependencia_ativa=dependencia_ativa,
                referencias={'chave': chave, 'valor': valor},
            )
        )
    return itens, False


def _mensagens_divergencias(resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial, *, materiais: bool) -> list[str]:
    mensagens = []
    for divergencia in list(getattr(resultado_paridade_renderizacao, 'divergencias', []) or []):
        if bool(getattr(divergencia, 'material', False)) is materiais:
            categoria = getattr(divergencia, 'categoria', 'DIVERGENCIA')
            alvo = getattr(divergencia, 'alvo', 'alvo_indefinido')
            mensagem = getattr(divergencia, 'mensagem', '')
            mensagens.append(f'{categoria} em {alvo}: {mensagem}')
    return mensagens


def montar_metadados_governanca_residuos(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
) -> MetadadosGovernancaResiduosPipeline:
    return MetadadosGovernancaResiduosPipeline(data_referencia=_extrair_data_referencia(resultado_paridade_renderizacao))


def consolidar_resultado_governanca_residuos(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
    itens: list[ItemGovernancaResiduoPipeline],
    classificacao_limitada_por_ausencia_inventario: bool,
) -> ResultadoGovernancaResiduosPipeline:
    materiais = _mensagens_divergencias(resultado_paridade_renderizacao, materiais=True)
    ressalvas = _mensagens_divergencias(resultado_paridade_renderizacao, materiais=False)
    bloqueados = [
        item
        for item in itens
        if item.classificacao == _CLASSIFICACAO_BLOQUEADO
        or item.classificacao == _CLASSIFICACAO_FALLBACK
        or item.evidencia_dependencia_ativa
    ]
    resíduos = [item for item in itens if item.classificacao in _CLASSIFICACOES_RESIDUO_IDENTIFICADO]
    candidatos = [item for item in itens if item.classificacao == _CLASSIFICACAO_RESIDUO]
    oficiais = [item for item in itens if item.classificacao == _CLASSIFICACAO_OFICIAL]
    historicos = [
        item
        for item in itens
        if item.classificacao in {_CLASSIFICACAO_HISTORICO, _CLASSIFICACAO_DIAGNOSTICO}
    ]
    avaliacao_futura = [item for item in itens if item.classificacao == _CLASSIFICACAO_AVALIACAO_FUTURA]
    fallbacks = [item for item in itens if item.classificacao == _CLASSIFICACAO_FALLBACK]
    inventario_ausente = [item for item in itens if item.classificacao == _CLASSIFICACAO_INVENTARIO_AUSENTE]

    bloqueios_governanca = []
    if materiais or getattr(resultado_paridade_renderizacao, 'status', None) in {'bloqueado', 'reprovado'}:
        bloqueios_governanca.append('paridade_renderizacao_sem_aprovacao_material')
    if bloqueados:
        bloqueios_governanca.append('residuo_bloqueado_dependencia_ativa')
    if fallbacks:
        bloqueios_governanca.append('rota_alternativa_temporaria_bloqueada_tratamento')
    if inventario_ausente:
        bloqueios_governanca.append('inventario_residuos_auxiliar_ausente')

    if materiais or getattr(resultado_paridade_renderizacao, 'status', None) in {'bloqueado', 'reprovado'}:
        status = 'bloqueado'
    elif bloqueados or classificacao_limitada_por_ausencia_inventario or ressalvas:
        status = 'aprovado_com_ressalva'
    else:
        status = 'aprovado'
    ok = status == 'aprovado'

    pendencias = list(ressalvas)
    if classificacao_limitada_por_ausencia_inventario:
        pendencias.append('inventario_residuos_auxiliar_ausente')

    recomendacoes = [
        'Preservar rotas oficiais e artefatos históricos.',
        'Executar tratamento ou remoção apenas em frente posterior específica, sem remoção automática nesta etapa.',
    ]
    if candidatos:
        recomendacoes.append('Priorizar resíduos candidatos sem dependência ativa em plano controlado de tratamento.')
    if bloqueados:
        recomendacoes.append('Manter bloqueio de remoção para itens com dependência ativa até evidência posterior de desuso.')
    if fallbacks:
        recomendacoes.append('Manter fallback temporário bloqueado para remoção nesta etapa; migrar apenas em frente posterior específica.')
    if classificacao_limitada_por_ausencia_inventario:
        recomendacoes.append('Fornecer inventário auxiliar estático em frente posterior para ampliar a classificação não decisória.')

    plano_retorno = [
        'Retornar à Etapa 1 somente após frente posterior específica aplicar limpezas autorizadas fora da Etapa 11.',
        'Preservar cadeia oficial validada pela Etapa 10 no novo ciclo operacional.',
    ]

    resumo = ResumoGovernancaResiduosPipeline(
        status=status,
        ok=ok,
        qtd_artefatos_avaliados=len(itens),
        qtd_rotas_oficiais_preservadas=len(oficiais),
        qtd_residuos_identificados=len(resíduos),
        qtd_residuos_bloqueados=len(bloqueados),
        qtd_residuos_candidatos_tratamento=len(candidatos),
        qtd_pendencias_nao_materiais=len(pendencias),
        qtd_bloqueios_governanca=len(bloqueios_governanca),
        classificacao_limitada_por_ausencia_inventario=classificacao_limitada_por_ausencia_inventario,
        acao_automatica_autorizada=False,
        qtd_historicos_diagnosticos_preservados=len(historicos),
        qtd_fallbacks_temporarios_bloqueados=len(fallbacks),
    )
    auditoria = AuditoriaGovernancaResiduosPipeline(
        paridade_status=getattr(resultado_paridade_renderizacao, 'status', None),
        paridade_ok=getattr(resultado_paridade_renderizacao, 'ok', None),
        inventario_residuos_auxiliar_fornecido=not classificacao_limitada_por_ausencia_inventario,
        classificacao_limitada_por_ausencia_inventario=classificacao_limitada_por_ausencia_inventario,
        divergencias_materiais_paridade=materiais,
        ressalvas_paridade=ressalvas,
        avisos=list(bloqueios_governanca),
    )
    metadados = montar_metadados_governanca_residuos(resultado_paridade_renderizacao)
    return ResultadoGovernancaResiduosPipeline(
        artefato=ARTEFATO_GOVERNANCA_RESIDUOS,
        etapa=ETAPA_GOVERNANCA_RESIDUOS,
        status=status,
        ok=ok,
        entrada_formal=ENTRADA_FORMAL,
        origem_formal=getattr(resultado_paridade_renderizacao, 'artefato', ENTRADA_FORMAL),
        data_referencia=metadados.data_referencia,
        artefatos_avaliados=itens,
        rotas_oficiais_preservadas=oficiais,
        residuos_identificados=resíduos,
        residuos_bloqueados_tratamento=bloqueados,
        residuos_candidatos_tratamento=candidatos,
        classes_candidatas_avaliacao_tratamento_futuro=avaliacao_futura,
        classes_preservadas_historico=historicos,
        pendencias_nao_materiais_release=pendencias,
        bloqueios_governanca=bloqueios_governanca,
        recomendacoes_governanca_residuos=recomendacoes,
        plano_retorno_etapa1=plano_retorno,
        resumo=resumo,
        auditoria=auditoria,
        metadados=metadados,
    )


def construir_resultado_governanca_residuos_pipeline(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
    evidencias_auxiliares: Any = None,
) -> ResultadoGovernancaResiduosPipeline:
    bloqueios_entrada = validar_entrada_governanca_residuos(resultado_paridade_renderizacao)
    if bloqueios_entrada:
        raise TypeError(bloqueios_entrada[0])
    itens, classificacao_limitada = _classificar_evidencias(evidencias_auxiliares)
    return consolidar_resultado_governanca_residuos(resultado_paridade_renderizacao, itens, classificacao_limitada)
