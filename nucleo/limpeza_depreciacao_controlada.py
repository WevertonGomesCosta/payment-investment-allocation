from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping
import unicodedata

from nucleo.paridade_renderizacao_oficial import ResultadoParidadeRenderizacaoOficial


ARTEFATO_LIMPEZA = 'ResultadoLimpezaDepreciacaoControlada'
ETAPA_LIMPEZA = 11
ENTRADA_FORMAL = 'ResultadoParidadeRenderizacaoOficial'
MODULO_LIMPEZA = 'nucleo/limpeza_depreciacao_controlada.py'

_CLASSIFICACAO_OFICIAL = 'rota_oficial_preservada'
_CLASSIFICACAO_LEGADO = 'legado_candidato_depreciacao'
_CLASSIFICACAO_HISTORICO = 'historico_preservado'
_CLASSIFICACAO_DIAGNOSTICO = 'diagnostico_preservado_fora_pipeline'
_CLASSIFICACAO_BLOQUEADO = 'bloqueado_dependencia_ativa'
_CLASSIFICACAO_FALLBACK = 'fallback_temporario_bloqueado_para_remocao'
_CLASSIFICACAO_LIMITADA = 'classificacao_limitada_por_ausencia_inventario'
_CLASSIFICACAO_INVENTARIO_AUSENTE = 'inventario_auxiliar_ausente'
_CLASSIFICACAO_AVALIACAO_FUTURA = 'avaliacao_remocao_futura'

_CLASSIFICACOES_PADRONIZADAS = {
    _CLASSIFICACAO_OFICIAL,
    _CLASSIFICACAO_LEGADO,
    _CLASSIFICACAO_BLOQUEADO,
    _CLASSIFICACAO_HISTORICO,
    _CLASSIFICACAO_DIAGNOSTICO,
    _CLASSIFICACAO_FALLBACK,
    _CLASSIFICACAO_AVALIACAO_FUTURA,
}

_CLASSIFICACOES_LEGADO_IDENTIFICADO = {
    _CLASSIFICACAO_LEGADO,
    _CLASSIFICACAO_BLOQUEADO,
    _CLASSIFICACAO_FALLBACK,
    _CLASSIFICACAO_AVALIACAO_FUTURA,
}


@dataclass(slots=True)
class ItemLimpezaDepreciacaoControlada:
    identificador: str
    classificacao: str
    origem: str
    motivo: str
    remocao_automatica_autorizada: bool = False
    evidencia_dependencia_ativa: bool = False
    referencias: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResumoLimpezaDepreciacaoControlada:
    status: str
    ok: bool
    qtd_artefatos_avaliados: int
    qtd_rotas_oficiais_preservadas: int
    qtd_rotas_legadas_identificadas: int
    qtd_rotas_legadas_bloqueadas: int
    qtd_rotas_legadas_candidatas_depreciacao: int
    qtd_pendencias_nao_materiais: int
    qtd_bloqueios_limpeza: int
    classificacao_limitada_por_ausencia_inventario: bool
    remocao_automatica_autorizada: bool = False
    qtd_historicos_diagnosticos_preservados: int = 0
    qtd_fallbacks_temporarios_bloqueados: int = 0


@dataclass(slots=True)
class AuditoriaLimpezaDepreciacaoControlada:
    paridade_status: str | None
    paridade_ok: bool | None
    inventario_auxiliar_fornecido: bool
    classificacao_limitada_por_ausencia_inventario: bool
    divergencias_materiais_paridade: list[str] = field(default_factory=list)
    ressalvas_paridade: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MetadadosLimpezaDepreciacaoControlada:
    artefato: str = ARTEFATO_LIMPEZA
    etapa: int = ETAPA_LIMPEZA
    entrada_formal: str = ENTRADA_FORMAL
    modulo: str = MODULO_LIMPEZA
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
    remocao_automatica_autorizada: bool = False


@dataclass(slots=True)
class ResultadoLimpezaDepreciacaoControlada:
    artefato: str
    etapa: int
    status: str
    ok: bool
    entrada_formal: str
    origem_formal: str
    data_referencia: str | None
    artefatos_avaliados: list[ItemLimpezaDepreciacaoControlada]
    rotas_oficiais_preservadas: list[ItemLimpezaDepreciacaoControlada]
    rotas_legadas_identificadas: list[ItemLimpezaDepreciacaoControlada]
    rotas_legadas_bloqueadas_remocao: list[ItemLimpezaDepreciacaoControlada]
    rotas_legadas_candidatas_depreciacao: list[ItemLimpezaDepreciacaoControlada]
    classes_candidatas_avaliacao_remocao_futura: list[ItemLimpezaDepreciacaoControlada]
    classes_preservadas_historico: list[ItemLimpezaDepreciacaoControlada]
    pendencias_nao_materiais_release: list[str]
    bloqueios_limpeza: list[str]
    recomendacoes_depreciacao_controlada: list[str]
    plano_retorno_etapa1: list[str]
    resumo: ResumoLimpezaDepreciacaoControlada
    auditoria: AuditoriaLimpezaDepreciacaoControlada
    metadados: MetadadosLimpezaDepreciacaoControlada


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

    if 'sem uso' in texto_completo or 'deprecated' in texto_completo or 'depreciad' in texto_completo:
        return False
    if texto_valor in {'bloqueado', 'dependencia ativa', 'dependencia_ativa', 'ativa'}:
        return True
    if texto_valor == 'ativo' and ({'dependencia', 'dependencias'} & tokens_chave):
        return True
    return bool({'bloqueado'} & tokens_valor) or _contem_frase(texto_completo, 'dependencia ativa')


def _indica_legado(chave: Any, valor: Any) -> bool:
    tokens = _tokenizar(chave) | _tokenizar(valor)
    texto = f'{_normalizar_texto(chave)} {_normalizar_texto(valor)}'
    return bool({'legacy', 'legado', 'deprecated', 'depreciado', 'depreciacao'} & tokens) or 'deprecated' in texto


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
    if _indica_legado('classificacao', tipo):
        return _CLASSIFICACAO_LEGADO
    return _CLASSIFICACAO_AVALIACAO_FUTURA


def _converter_item_inventario(item: Mapping[str, Any]) -> ItemLimpezaDepreciacaoControlada:
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
    return ItemLimpezaDepreciacaoControlada(
        identificador=str(item.get('identificador')),
        classificacao=classificacao,
        origem='inventario_legado_pipeline_estatico',
        motivo=motivo,
        remocao_automatica_autorizada=False,
        evidencia_dependencia_ativa=dependencia_ativa,
        referencias=dict(item),
    )


def validar_entrada_limpeza_depreciacao(resultado_paridade_renderizacao: Any) -> list[str]:
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


def _classificar_evidencias(evidencias_auxiliares: Any) -> tuple[list[ItemLimpezaDepreciacaoControlada], bool]:
    if evidencias_auxiliares in (None, {}, []):
        item = ItemLimpezaDepreciacaoControlada(
            identificador='inventario_auxiliar',
            classificacao=_CLASSIFICACAO_INVENTARIO_AUSENTE,
            origem='evidencia_auxiliar_nao_decisoria',
            motivo='Inventário auxiliar não fornecido; classificação de limpeza fica limitada.',
            referencias={'classificacao_limitada_por_ausencia_inventario': True},
        )
        return [item], True

    itens_formais = _extrair_itens_formais_inventario(evidencias_auxiliares)
    if itens_formais:
        return [_converter_item_inventario(item) for item in itens_formais], False

    itens: list[ItemLimpezaDepreciacaoControlada] = []
    vistos: set[str] = set()
    for identificador, chave, valor in _iterar_evidencias(evidencias_auxiliares):
        if identificador in vistos:
            continue
        vistos.add(identificador)
        if _indica_dependencia_ativa(chave, valor):
            classificacao = _CLASSIFICACAO_BLOQUEADO
            motivo = 'Evidência auxiliar indica bloqueio por dependência ativa; remoção futura deve permanecer bloqueada.'
            dependencia_ativa = True
        elif _indica_legado(chave, valor):
            classificacao = _CLASSIFICACAO_LEGADO
            motivo = 'Evidência auxiliar indica rota/artefato legado candidato à depreciação controlada.'
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
            ItemLimpezaDepreciacaoControlada(
                identificador=identificador,
                classificacao=classificacao,
                origem='evidencia_auxiliar_nao_decisoria',
                motivo=motivo,
                remocao_automatica_autorizada=False,
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


def montar_metadados_limpeza_depreciacao(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
) -> MetadadosLimpezaDepreciacaoControlada:
    return MetadadosLimpezaDepreciacaoControlada(data_referencia=_extrair_data_referencia(resultado_paridade_renderizacao))


def consolidar_resultado_limpeza_depreciacao(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
    itens: list[ItemLimpezaDepreciacaoControlada],
    classificacao_limitada_por_ausencia_inventario: bool,
) -> ResultadoLimpezaDepreciacaoControlada:
    materiais = _mensagens_divergencias(resultado_paridade_renderizacao, materiais=True)
    ressalvas = _mensagens_divergencias(resultado_paridade_renderizacao, materiais=False)
    bloqueados = [
        item
        for item in itens
        if item.classificacao == _CLASSIFICACAO_BLOQUEADO
        or item.classificacao == _CLASSIFICACAO_FALLBACK
        or item.evidencia_dependencia_ativa
    ]
    legados = [item for item in itens if item.classificacao in _CLASSIFICACOES_LEGADO_IDENTIFICADO]
    candidatos = [item for item in itens if item.classificacao == _CLASSIFICACAO_LEGADO]
    oficiais = [item for item in itens if item.classificacao == _CLASSIFICACAO_OFICIAL]
    historicos = [
        item
        for item in itens
        if item.classificacao in {_CLASSIFICACAO_HISTORICO, _CLASSIFICACAO_DIAGNOSTICO}
    ]
    avaliacao_futura = [item for item in itens if item.classificacao == _CLASSIFICACAO_AVALIACAO_FUTURA]
    fallbacks = [item for item in itens if item.classificacao == _CLASSIFICACAO_FALLBACK]
    inventario_ausente = [item for item in itens if item.classificacao == _CLASSIFICACAO_INVENTARIO_AUSENTE]

    bloqueios_limpeza = []
    if materiais or getattr(resultado_paridade_renderizacao, 'status', None) in {'bloqueado', 'reprovado'}:
        bloqueios_limpeza.append('paridade_renderizacao_sem_aprovacao_material')
    if bloqueados:
        bloqueios_limpeza.append('bloqueado_dependencia_ativa')
    if fallbacks:
        bloqueios_limpeza.append('fallback_temporario_bloqueado_para_remocao')
    if inventario_ausente:
        bloqueios_limpeza.append('inventario_auxiliar_ausente')

    if materiais or getattr(resultado_paridade_renderizacao, 'status', None) in {'bloqueado', 'reprovado'}:
        status = 'bloqueado'
    elif bloqueados or classificacao_limitada_por_ausencia_inventario or ressalvas:
        status = 'aprovado_com_ressalva'
    else:
        status = 'aprovado'
    ok = status == 'aprovado'

    pendencias = list(ressalvas)
    if classificacao_limitada_por_ausencia_inventario:
        pendencias.append('inventario_auxiliar_ausente')

    recomendacoes = [
        'Preservar rotas oficiais e artefatos históricos.',
        'Executar depreciação ou remoção apenas em frente posterior específica, sem remoção automática nesta etapa.',
    ]
    if candidatos:
        recomendacoes.append('Priorizar candidatos legados sem dependência ativa em plano controlado de depreciação.')
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

    resumo = ResumoLimpezaDepreciacaoControlada(
        status=status,
        ok=ok,
        qtd_artefatos_avaliados=len(itens),
        qtd_rotas_oficiais_preservadas=len(oficiais),
        qtd_rotas_legadas_identificadas=len(legados),
        qtd_rotas_legadas_bloqueadas=len(bloqueados),
        qtd_rotas_legadas_candidatas_depreciacao=len(candidatos),
        qtd_pendencias_nao_materiais=len(pendencias),
        qtd_bloqueios_limpeza=len(bloqueios_limpeza),
        classificacao_limitada_por_ausencia_inventario=classificacao_limitada_por_ausencia_inventario,
        remocao_automatica_autorizada=False,
        qtd_historicos_diagnosticos_preservados=len(historicos),
        qtd_fallbacks_temporarios_bloqueados=len(fallbacks),
    )
    auditoria = AuditoriaLimpezaDepreciacaoControlada(
        paridade_status=getattr(resultado_paridade_renderizacao, 'status', None),
        paridade_ok=getattr(resultado_paridade_renderizacao, 'ok', None),
        inventario_auxiliar_fornecido=not classificacao_limitada_por_ausencia_inventario,
        classificacao_limitada_por_ausencia_inventario=classificacao_limitada_por_ausencia_inventario,
        divergencias_materiais_paridade=materiais,
        ressalvas_paridade=ressalvas,
        avisos=list(bloqueios_limpeza),
    )
    metadados = montar_metadados_limpeza_depreciacao(resultado_paridade_renderizacao)
    return ResultadoLimpezaDepreciacaoControlada(
        artefato=ARTEFATO_LIMPEZA,
        etapa=ETAPA_LIMPEZA,
        status=status,
        ok=ok,
        entrada_formal=ENTRADA_FORMAL,
        origem_formal=getattr(resultado_paridade_renderizacao, 'artefato', ENTRADA_FORMAL),
        data_referencia=metadados.data_referencia,
        artefatos_avaliados=itens,
        rotas_oficiais_preservadas=oficiais,
        rotas_legadas_identificadas=legados,
        rotas_legadas_bloqueadas_remocao=bloqueados,
        rotas_legadas_candidatas_depreciacao=candidatos,
        classes_candidatas_avaliacao_remocao_futura=avaliacao_futura,
        classes_preservadas_historico=historicos,
        pendencias_nao_materiais_release=pendencias,
        bloqueios_limpeza=bloqueios_limpeza,
        recomendacoes_depreciacao_controlada=recomendacoes,
        plano_retorno_etapa1=plano_retorno,
        resumo=resumo,
        auditoria=auditoria,
        metadados=metadados,
    )


def construir_resultado_limpeza_depreciacao_controlada(
    resultado_paridade_renderizacao: ResultadoParidadeRenderizacaoOficial,
    evidencias_auxiliares: Any = None,
) -> ResultadoLimpezaDepreciacaoControlada:
    bloqueios_entrada = validar_entrada_limpeza_depreciacao(resultado_paridade_renderizacao)
    if bloqueios_entrada:
        raise TypeError(bloqueios_entrada[0])
    itens, classificacao_limitada = _classificar_evidencias(evidencias_auxiliares)
    return consolidar_resultado_limpeza_depreciacao(resultado_paridade_renderizacao, itens, classificacao_limitada)
