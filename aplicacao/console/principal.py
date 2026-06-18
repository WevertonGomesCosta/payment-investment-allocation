"Ponto de entrada do console operacional da baseline."

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import sys

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.common import (
    imprimir_pares as _imprimir_pares,
    imprimir_tabela as _imprimir_tabela,
    imprimir_titulo as _imprimir_titulo,
    severidade as _severidade,
)
from aplicacao.console.secoes_execucao import render_secao_execucao
from nucleo.contexto_operacional_canonico import carregar_contexto_operacional_canonico
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha


class PacoteSaidaObservavelOficialAusente(RuntimeError):
    """Falha contratual para rotas oficiais sem PacoteSaidaObservavelOficial."""


def construir_representacao_console_auditavel(secoes_observadas: dict | None = None) -> dict:
    """Constrói o envelope auditável produzido pelo caminho de renderização do console."""
    return {
        'origem_representacao': 'render_console',
        'forma': 'observavel_console_emitido',
        'secoes': dict(secoes_observadas or {}),
    }


def _objeto_para_dict(item: Any) -> dict[str, Any]:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, Mapping):
        return dict(item)
    if item is None:
        return {}
    return {
        chave: getattr(item, chave)
        for chave in dir(item)
        if not chave.startswith('_') and not callable(getattr(item, chave, None))
    }


def _lista_dicts(itens: Iterable[Any] | None) -> list[dict[str, Any]]:
    return [_objeto_para_dict(item) for item in list(itens or [])]


def _valor_oficial(item: Any, campo: str, padrao: Any = None) -> Any:
    if is_dataclass(item):
        item = asdict(item)
    if isinstance(item, Mapping):
        return item.get(campo, padrao)
    return getattr(item, campo, padrao)


def _normalizar_pares(itens: Iterable[Any] | Mapping[str, Any] | None) -> list[tuple[Any, Any]]:
    if isinstance(itens, Mapping):
        return list(itens.items())

    pares: list[tuple[Any, Any]] = []
    for item in list(itens or []):
        row = _objeto_para_dict(item)
        if 'Métrica' in row or 'Valor' in row:
            pares.append((row.get('Métrica'), row.get('Valor')))
        elif 'metrica' in row or 'valor' in row:
            pares.append((row.get('metrica'), row.get('valor')))
        elif len(row) == 1:
            chave, valor = next(iter(row.items()))
            pares.append((chave, valor))
        elif row:
            pares.extend(row.items())
    return pares


def _headers_dinamicos(linhas: Iterable[Mapping[str, Any]], preferidos: Iterable[str] | None = None) -> list[str]:
    vistos: set[str] = set()
    headers: list[str] = []
    for header in list(preferidos or []):
        if header not in vistos:
            headers.append(header)
            vistos.add(header)
    for linha in linhas:
        for header in dict(linha).keys():
            if header not in vistos:
                headers.append(header)
                vistos.add(header)
    return headers


def _filtrar_headers_presentes(linhas: list[dict[str, Any]], headers: list[str]) -> list[str]:
    if not linhas:
        return headers
    presentes = [h for h in headers if any(h in linha for linha in linhas)]
    return presentes or headers


def _imprimir_tabela_oficial(headers: list[str], linhas: list[dict[str, Any]], *, limite: int | None = None) -> None:
    headers_emitidos = _filtrar_headers_presentes(linhas, headers)
    _imprimir_tabela(headers_emitidos, linhas, limite=limite)


def _bloco_console(pacote_saida_observavel_oficial: Any) -> Any:
    return getattr(pacote_saida_observavel_oficial, 'bloco_console', None)


def _bloco_xlsx(pacote_saida_observavel_oficial: Any) -> Any:
    return getattr(pacote_saida_observavel_oficial, 'bloco_xlsx', None)


def _validar_pacote_saida_observavel_oficial_completo(pacote_saida_observavel_oficial: Any) -> None:
    if pacote_saida_observavel_oficial is None:
        raise PacoteSaidaObservavelOficialAusente(
            'Console oficial exige PacoteSaidaObservavelOficial; '
            'rota alternativa de console/XLSX foi desativada pela ME-518A.'
        )

    if not getattr(pacote_saida_observavel_oficial, 'preparado', False):
        raise PacoteSaidaObservavelOficialAusente(
            'Console oficial recebeu PacoteSaidaObservavelOficial não preparado.'
        )

    if _bloco_console(pacote_saida_observavel_oficial) is None:
        raise PacoteSaidaObservavelOficialAusente(
            'Console oficial recebeu PacoteSaidaObservavelOficial sem bloco_console.'
        )

    if _bloco_xlsx(pacote_saida_observavel_oficial) is None:
        raise PacoteSaidaObservavelOficialAusente(
            'Console oficial recebeu PacoteSaidaObservavelOficial sem bloco_xlsx.'
        )


def _render_pacote_saida_observavel_oficial(pacote_saida_observavel_oficial: Any) -> dict:
    _imprimir_titulo('SAÍDA OBSERVÁVEL OFICIAL — ETAPA 9')
    resumo = getattr(pacote_saida_observavel_oficial, 'resumo', None)
    auditoria = getattr(pacote_saida_observavel_oficial, 'auditoria', None)
    bloco_console = _bloco_console(pacote_saida_observavel_oficial)
    lacunas = list(getattr(pacote_saida_observavel_oficial, 'lacunas_renderizacao', []) or [])
    metadados = getattr(pacote_saida_observavel_oficial, 'metadados', {}) or {}

    saida_observavel_resumo = [
        {'Métrica': 'artefato', 'Valor': metadados.get('artefato', type(pacote_saida_observavel_oficial).__name__)},
        {'Métrica': 'saida_origem', 'Valor': getattr(pacote_saida_observavel_oficial, 'saida_origem', None)},
        {'Métrica': 'status', 'Valor': getattr(pacote_saida_observavel_oficial, 'status', None)},
        {'Métrica': 'preparado', 'Valor': getattr(pacote_saida_observavel_oficial, 'preparado', None)},
        {'Métrica': 'ok', 'Valor': getattr(pacote_saida_observavel_oficial, 'ok', None)},
        {'Métrica': 'data de referência', 'Valor': getattr(pacote_saida_observavel_oficial, 'data_referencia', None)},
        {'Métrica': 'origem formal', 'Valor': getattr(pacote_saida_observavel_oficial, 'origem_formal', None)},
        {'Métrica': 'qtd obrigações cobertas', 'Valor': getattr(resumo, 'qtd_obrigacoes_cobertas', None)},
        {'Métrica': 'qtd obrigações bloqueadas', 'Valor': getattr(resumo, 'qtd_obrigacoes_bloqueadas', None)},
        {'Métrica': 'qtd lacunas renderização', 'Valor': getattr(resumo, 'qtd_lacunas_renderizacao', len(lacunas))},
        {'Métrica': 'origem exclusiva auditoria', 'Valor': getattr(auditoria, 'origem_exclusiva', None)},
    ]
    _imprimir_pares([(item['Métrica'], item['Valor']) for item in saida_observavel_resumo])

    secoes = {'saida_observavel_resumo': saida_observavel_resumo}
    resumo_operacional = getattr(bloco_console, 'resumo_operacional', {}) or {}
    if resumo_operacional:
        print('\n- resumo operacional oficial:')
        _imprimir_pares(list(resumo_operacional.items()))
        secoes['resumo_operacional'] = [
            {'Métrica': chave, 'Valor': valor}
            for chave, valor in resumo_operacional.items()
        ]
    return secoes


def _data_obrigacao_oficial(item: Any) -> Any:
    data = _valor_oficial(item, 'data')
    referencia = _valor_oficial(item, 'referencia_original', {}) or {}
    return data or _valor_oficial(referencia, 'data')


def _descricao_obrigacao_oficial(item: Any) -> str:
    referencia = _valor_oficial(item, 'referencia_original', {}) or {}
    return (
        _valor_oficial(referencia, 'descricao')
        or _valor_oficial(referencia, 'conta')
        or _valor_oficial(item, 'obrigacao_id')
        or ''
    )


def _fontes_obrigacao_oficial(item: Any) -> str:
    fontes_operacionais = list(_valor_oficial(item, 'fontes_referenciadas_operacionais', []) or [])
    if fontes_operacionais:
        return ' + '.join(str(f) for f in fontes_operacionais if f) or 'n/d'
    fontes = list(_valor_oficial(item, 'fontes_referenciadas', []) or [])
    return ' + '.join(str(f) for f in fontes if f) or 'n/d'


def _valor_economico_oficial(item: Any, campo: str, status_campo: str | None = None, padrao: str = 'nao_materializado') -> Any:
    valor = _valor_oficial(item, campo)
    if valor is None and status_campo:
        status = _valor_oficial(item, status_campo)
        if status:
            return status
    if valor is None:
        return padrao
    if isinstance(valor, (int, float)):
        return f'{float(valor):.2f}'
    texto = str(valor).strip()
    return texto if texto else padrao


def _linha_pagamento_oficial(item: Any, bloqueada: bool = False) -> dict[str, Any]:
    fontes = _fontes_obrigacao_oficial(item)
    pacote_id = _valor_oficial(item, 'pacote_nome_operacional') or _valor_oficial(item, 'pacote_id') or 'n/d'
    motivo = _valor_oficial(item, 'motivo') or 'n/d'
    return {
        'Data': _data_obrigacao_oficial(item),
        'Conta': _descricao_obrigacao_oficial(item),
        'Lote': fontes if not bloqueada else 'n/d',
        'Pacote': pacote_id,
        'Sw. ant.': 'não',
        'Sw. dep.': 'não',
        'Status': _valor_oficial(item, 'status_observavel') or _valor_oficial(item, 'status') or ('bloqueada_oficial' if bloqueada else 'coberta_oficial'),
        'Bloq.': motivo if bloqueada else 'n/d',
        'Saldo ant.': _valor_economico_oficial(item, 'saldo_antes_fonte', 'status_saldo_antes_fonte') if not bloqueada else 'nao_aplicavel',
        'Bruto': _valor_economico_oficial(item, 'valor_bruto_resgate', 'status_valor_bruto_resgate') if not bloqueada else 'nao_aplicavel',
        'Imposto': _valor_economico_oficial(item, 'imposto_resgate', 'status_imposto_resgate') if not bloqueada else 'nao_aplicavel',
        'Liq.': _valor_economico_oficial(item, 'valor_liquido_resgate', 'status_valor_liquido_resgate') if not bloqueada else 'nao_aplicavel',
        'Rem.': _valor_economico_oficial(item, 'saldo_remanescente_fonte', 'status_saldo_remanescente_fonte') if not bloqueada else 'nao_aplicavel',
    }


def _eh_obrigacao_bloqueada(item: Any) -> bool:
    return (
        str(_valor_oficial(item, 'status_observavel') or '').startswith('bloqueada')
        or str(_valor_oficial(item, 'tipo') or '').endswith('bloqueada_referencialmente')
        or str(_valor_oficial(item, 'status') or '').startswith('bloqueada')
    )


def _render_amostras_pagamentos_operacionais_oficiais(pacote_saida_observavel_oficial: Any) -> dict:
    bloco_console = _bloco_console(pacote_saida_observavel_oficial)
    _imprimir_titulo('PAGAMENTOS — AMOSTRAS OPERACIONAIS')

    cobertas = list(getattr(bloco_console, 'obrigacoes_cobertas', []) or [])
    bloqueadas = list(getattr(bloco_console, 'obrigacoes_bloqueadas', []) or [])
    secoes: dict[str, list[dict[str, Any]]] = {}

    ultimas_cobertas = list(getattr(bloco_console, 'ultimos_pagamentos', []) or [])
    print('- últimos 5 pagamentos realizados:')
    colunas_ultimos = ['Data', 'Conta', 'Lote', 'Saldo ant.', 'Bruto', 'Imposto', 'Liq.', 'Rem.']
    linhas_ultimos = [
        {k: linha[k] for k in colunas_ultimos}
        for linha in (_linha_pagamento_oficial(item, bloqueada=False) for item in ultimas_cobertas[:5])
    ]
    secoes['pagamentos_ultimos'] = linhas_ultimos
    if linhas_ultimos:
        _imprimir_tabela(colunas_ultimos, linhas_ultimos, limite=5)
    else:
        print('  sem_pagamentos_realizados_ate_data_referencia')

    pagamentos_data_referencia = list(getattr(bloco_console, 'pagamentos_data_referencia', []) or [])
    print('\n- pagamentos na data de referência — saída oficial:')
    colunas_data_ref = ['Data', 'Conta', 'Lote', 'Pacote', 'Saldo ant.', 'Bruto', 'Imposto', 'Liq.', 'Rem.', 'Status', 'Bloq.']
    linhas_data_ref = [
        {k: linha[k] for k in colunas_data_ref}
        for linha in (
            _linha_pagamento_oficial(item, bloqueada=_eh_obrigacao_bloqueada(item))
            for item in pagamentos_data_referencia[:5]
        )
    ]
    secoes['pagamentos_data_referencia'] = linhas_data_ref
    if linhas_data_ref:
        _imprimir_tabela(colunas_data_ref, linhas_data_ref, limite=5)
    else:
        print('  sem_pagamentos_na_data_referencia')

    proximas_ordenadas = list(getattr(bloco_console, 'proximos_pagamentos', []) or [])
    print('\n- próximos 5 pagamentos:')
    colunas_proximos = ['Data', 'Conta', 'Lote', 'Saldo ant.', 'Bruto', 'Imposto', 'Liq.', 'Rem.']
    linhas_proximos = [
        {k: linha[k] for k in colunas_proximos}
        for linha in (
            _linha_pagamento_oficial(item, bloqueada=_eh_obrigacao_bloqueada(item))
            for item in proximas_ordenadas[:5]
        )
    ]
    secoes['pagamentos_proximos'] = linhas_proximos
    if linhas_proximos:
        _imprimir_tabela(colunas_proximos, linhas_proximos, limite=5)
    else:
        print('  sem_proximos_pagamentos')

    if bloqueadas:
        print('\n- obrigações bloqueadas oficiais:')
        linhas_bloqueadas = [
            {k: linha[k] for k in ['Data', 'Conta', 'Pacote', 'Status', 'Bloq.']}
            for linha in (_linha_pagamento_oficial(item, bloqueada=True) for item in bloqueadas[:5])
        ]
        secoes['obrigacoes_bloqueadas_oficiais'] = linhas_bloqueadas
        _imprimir_tabela(['Data', 'Conta', 'Pacote', 'Status', 'Bloq.'], linhas_bloqueadas, limite=5)

    print('\n- alertas operacionais:')
    if bloqueadas:
        linhas_alerta = [
            {
                'Data': _data_obrigacao_oficial(item),
                'Conta': _descricao_obrigacao_oficial(item),
                'problema': 'obrigacao_bloqueada_oficial',
                'motivo': _valor_oficial(item, 'motivo') or 'n/d',
            }
            for item in bloqueadas[:5]
        ]
        secoes['alertas_operacionais'] = linhas_alerta
        _imprimir_tabela(['Data', 'Conta', 'problema', 'motivo'], linhas_alerta, limite=5)
    else:
        secoes['alertas_operacionais'] = [{'status': '[OK] sem alertas na amostra atual'}]
        print('  [OK] sem alertas na amostra atual')
    return secoes


def _render_secao_ranking_oficial(pacote_saida_observavel_oficial: Any) -> dict:
    bloco_console = _bloco_console(pacote_saida_observavel_oficial)
    metricas = _lista_dicts(getattr(bloco_console, 'ranking_metricas', []) or [])
    amostra = _lista_dicts(getattr(bloco_console, 'ranking_amostra', []) or [])

    _imprimir_titulo('RANQUEAMENTO OFICIAL DA CARTEIRA')
    if metricas:
        _imprimir_pares(_normalizar_pares(metricas))
    else:
        print('- status: ranking_oficial_sem_metricas_materializadas')

    print('- amostra do ranking relevante do dia:')
    headers = ['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.']
    if amostra:
        _imprimir_tabela_oficial(headers, amostra, limite=10)
    else:
        print('  ranking_amostra_nao_materializada_no_pacote_saida_observavel_oficial')
    return {'ranking_metricas': metricas, 'ranking_amostra': amostra[:10]}


def _render_secao_switchings_oficiais(pacote_saida_observavel_oficial: Any) -> dict:
    bloco_console = _bloco_console(pacote_saida_observavel_oficial)
    metricas = _lista_dicts(getattr(bloco_console, 'switchings_metricas', []) or [])
    amostra = _lista_dicts(getattr(bloco_console, 'switchings_amostra', []) or [])
    resumo_curto = _lista_dicts(getattr(bloco_console, 'switchings_resumo_operacional', []) or [])

    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    if metricas:
        _imprimir_tabela_oficial(['Métrica', 'Valor'], metricas, limite=None)
    else:
        print('- status: switchings_oficiais_sem_metricas_materializadas')

    print('\n- amostra de switchings reais da janela:')
    headers = ['Data', 'Lote origem', 'Lote destino', 'Produto origem', 'Produto destino']
    if amostra:
        _imprimir_tabela_oficial(headers, amostra, limite=10)
    else:
        print('  sem_switchings_oficiais_materializados')

    print('\n- resumo operacional curto:')
    if resumo_curto:
        _imprimir_tabela_oficial(['Métrica', 'Valor'], resumo_curto, limite=None)
    else:
        print('  resumo_switching_nao_materializado_no_pacote_saida_observavel_oficial')
    return {
        'switching_metricas': metricas,
        'switching_amostra': amostra[:10],
        'switching_resumo_operacional': resumo_curto,
    }


def _render_lotes_situacao(titulo: str, linhas_id: list[dict[str, Any]], linhas_valores: list[dict[str, Any]]) -> None:
    print(f'\n- {titulo}:')
    if linhas_id:
        print('  identificação:')
        _imprimir_tabela_oficial(_headers_dinamicos(linhas_id), linhas_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela_oficial(_headers_dinamicos(linhas_valores), linhas_valores, limite=None)
    else:
        print(f'  [OK] sem {titulo} nesta execução')




def _render_situacao_atual_oficial(pacote_saida_observavel_oficial: Any) -> dict:
    bloco_console = _bloco_console(pacote_saida_observavel_oficial)
    _imprimir_titulo('SITUAÇÃO ATUAL')

    fechamento = _lista_dicts(getattr(bloco_console, 'situacao_atual_fechamento', []) or [])
    fechamento_por_metrica = {chave: valor for chave, valor in _normalizar_pares(fechamento)}
    fechamento_emitido = [
        {'Métrica': 'data de referência', 'Valor': fechamento_por_metrica.get('Data de referência')},
        {'Métrica': 'status do fechamento econômico', 'Valor': fechamento_por_metrica.get('Status do fechamento econômico')},
        {'Métrica': 'fonte do fechamento', 'Valor': fechamento_por_metrica.get('Fonte do fechamento')},
        {'Métrica': 'fechamentos com fallback CDI', 'Valor': fechamento_por_metrica.get('Fechamentos com fallback CDI', 0)},
        {'Métrica': 'último fator explícito CDI', 'Valor': fechamento_por_metrica.get('Último fator explícito CDI')},
        {'Métrica': 'data confirmada da série', 'Valor': fechamento_por_metrica.get('Data confirmada da série')},
    ]
    if fechamento:
        _imprimir_pares(_normalizar_pares(fechamento))

    exauridos_id = _lista_dicts(getattr(bloco_console, 'situacao_atual_lotes_exauridos_id', []) or [])
    exauridos_val = _lista_dicts(getattr(bloco_console, 'situacao_atual_lotes_exauridos_valores', []) or [])
    _render_lotes_situacao('lotes exauridos', exauridos_id, exauridos_val)

    ativos_id = _lista_dicts(getattr(bloco_console, 'situacao_atual_lotes_ativos_id', []) or [])
    ativos_val = _lista_dicts(getattr(bloco_console, 'situacao_atual_lotes_ativos_valores', []) or [])
    _render_lotes_situacao('lotes ativos', ativos_id, ativos_val)

    patrimonio_total = _lista_dicts(getattr(bloco_console, 'situacao_atual_patrimonio_total', []) or [])
    print('\n- patrimônio total dos lotes:')
    if patrimonio_total:
        _imprimir_tabela_oficial(['Métrica', 'Valor'], patrimonio_total, limite=None)
    else:
        print('  patrimonio_total_nao_materializado_no_pacote_saida_observavel_oficial')


    resumo_recebidos = _lista_dicts(getattr(bloco_console, 'situacao_atual_resumo_recebidos', []) or [])
    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(_normalizar_pares(resumo_recebidos))

    return {
        'situacao_atual_fechamento': fechamento_emitido,
        'situacao_atual_lotes_exauridos_id': exauridos_id,
        'situacao_atual_lotes_exauridos_valores': exauridos_val,
        'situacao_atual_lotes_ativos_id': ativos_id,
        'situacao_atual_lotes_ativos_valores': ativos_val,
        'situacao_atual_patrimonio_total': patrimonio_total,
        'situacao_atual_resumo_recebidos': resumo_recebidos,
    }


def _render_secao_execucao_contexto(contexto_operacional: Any) -> None:
    pacote_config = contexto_operacional.pacote_config
    contexto = contexto_operacional.execucao
    pacote_planilha = contexto_operacional.pacote_planilha
    carteira_canonica = contexto_operacional.carteira_canonica
    cache_cdi = contexto_operacional.cache_cdi

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item['nome_aba']: item for item in resumo_planilha}

    abas_cfg = pacote_config.conteudo.get('abas', {}) if isinstance(pacote_config.conteudo.get('abas'), dict) else {}
    nome_aba_carteira_real = getattr(carteira_canonica, 'nome_aba', abas_cfg.get('carteira', 'Carteira'))
    dados_operacionais = getattr(contexto_operacional, 'dados_operacionais', None)

    nome_aba_salarios_real = (
        getattr(dados_operacionais, 'nome_aba_salarios', '')
        or abas_cfg.get('salarios', '')
        or ('Salários' if 'Salários' in pacote_planilha.nomes_abas else '')
    )
    nome_aba_switching_real = (
        getattr(dados_operacionais, 'nome_aba_switching', '')
        or abas_cfg.get('switching', '')
        or ('Switching' if 'Switching' in pacote_planilha.nomes_abas else '')
    )

    abas_operacionais_canonicas = [
        ('carteira', nome_aba_carteira_real),
        ('salarios', nome_aba_salarios_real),
        ('despesas', abas_cfg.get('despesas', 'Todos os Gastos')),
        ('switching', nome_aba_switching_real),
        ('lotes', abas_cfg.get('lotes', 'Inventário de Lotes')),
    ]
    abas_primarias_reais = [(chave, nome_aba) for chave, nome_aba in abas_operacionais_canonicas if nome_aba]
    abas_auxiliares = [
        nome for nome in pacote_planilha.nomes_abas
        if nome not in {aba for _, aba in abas_primarias_reais}
    ]

    severidade_dependencias = _severidade(
        avisos=contexto.relatorio_dependencias.get('ausentes', []),
        condicao_ok=len(contexto.relatorio_dependencias.get('ausentes', [])) == 0,
    )
    auditoria_cache_cdi = cache_cdi.auditoria or {}
    data_ultimo_fator_cdi = max(cache_cdi.serie_cdi.keys()) if cache_cdi.serie_cdi else None

    render_secao_execucao(
        versao=VERSAO_BASELINE,
        pacote_config=pacote_config,
        pacote_planilha=pacote_planilha,
        contexto=contexto,
        severidade_dependencias=severidade_dependencias,
        auditoria_cache_cdi=auditoria_cache_cdi,
        data_ultimo_fator_cdi=data_ultimo_fator_cdi,
        resumo_por_aba=resumo_por_aba,
        abas_primarias_reais=abas_primarias_reais,
        abas_auxiliares=abas_auxiliares,
    )


def render_console(
    contexto_operacional: Any,
    saida_canonica: Any = None,
    estado_temporal_inicial: Any = None,
    pacote_saida_observavel_oficial: Any = None,
) -> dict:
    """Renderiza exclusivamente o PacoteSaidaObservavelOficial recebido pela rota integrada."""
    _ = saida_canonica
    _ = estado_temporal_inicial
    _validar_pacote_saida_observavel_oficial_completo(pacote_saida_observavel_oficial)

    _render_secao_execucao_contexto(contexto_operacional)

    secoes_console_observadas: dict[str, Any] = {}
    secoes_console_observadas.update(_render_pacote_saida_observavel_oficial(pacote_saida_observavel_oficial))
    secoes_console_observadas.update(_render_amostras_pagamentos_operacionais_oficiais(pacote_saida_observavel_oficial))
    secoes_console_observadas.update(_render_secao_ranking_oficial(pacote_saida_observavel_oficial))
    secoes_console_observadas.update(_render_secao_switchings_oficiais(pacote_saida_observavel_oficial))
    secoes_console_observadas.update(_render_situacao_atual_oficial(pacote_saida_observavel_oficial))

    return construir_representacao_console_auditavel(secoes_console_observadas)


def main() -> None:
    """Execução standalone: falha de forma explícita sem o pacote oficial preparado."""
    contexto_operacional = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal_inicial = construir_estado_temporal_inicial(contexto_operacional)
    render_console(
        contexto_operacional,
        estado_temporal_inicial=estado_temporal_inicial,
        pacote_saida_observavel_oficial=None,
    )


if __name__ == '__main__':
    main()
