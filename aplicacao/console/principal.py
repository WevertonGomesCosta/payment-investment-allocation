"Ponto de entrada do console operacional da baseline."

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

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
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b
from nucleo.integracao_matriz_elegibilidade_pagamentos_s7c import aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c
from nucleo.saida_observavel import (
    construir_amostras_pagamentos_operacionais,
    construir_linhas_lotes_consolidados,
    COLS_LOTES_EXAURIDOS_ID_CURTAS,
    COLS_LOTES_ATIVOS_ID_CURTAS,
    COLS_LOTES_VALORES_CURTAS,
    construir_linhas_lotes_id_curta,
    construir_linhas_lotes_valores_curta,
    construir_resumo_patrimonio_total_lotes,
    construir_switchings_observaveis,
)


def _filtrar_lotes_ativos_com_estado_temporal(linhas: list[dict], estado_temporal_inicial=None) -> list[dict]:
    if estado_temporal_inicial is None:
        return linhas
    migrados = {str(l.get('lote_id') or '').strip() for l in (estado_temporal_inicial.inventario_temporal or []) if l.get('status_temporal') in {'migrado_por_switching','exaurido_por_switching'}}
    if not migrados:
        return linhas
    return [row for row in linhas if str(row.get('Lote') or '').strip() not in migrados]


def _render_amostras_pagamentos_operacionais(contexto_operacional, saida_canonica, pacote_saida_observavel_temporal=None, estado_temporal_inicial=None) -> None:
    amostras = construir_amostras_pagamentos_operacionais(
        saida_canonica,
        limite=5,
        contexto=contexto_operacional,
        pacote_saida_observavel_temporal=pacote_saida_observavel_temporal,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    amostras.pop('recebidos_futuros', None)

    _imprimir_titulo(amostras['titulo'])

    realizados = amostras['realizados']
    print(f"- {realizados['rotulo']}:")
    _imprimir_tabela(realizados['headers'], realizados['linhas'], limite=realizados['limite'])

    proximos_decisao = amostras['proximos_switching_status']
    print(f"\n- {proximos_decisao['rotulo']}:")
    _imprimir_tabela(proximos_decisao['headers'], proximos_decisao['linhas'], limite=proximos_decisao['limite'])

    proximos_valores = amostras['proximos_valores_fonte']
    print("\n- próximos 5 pagamentos — valores:")
    _imprimir_tabela(['Data','Conta','Saldo ant.','Bruto','IR','Liq.','Rem.'], proximos_valores['linhas'], limite=proximos_valores['limite'])

    relevantes = amostras['proximos_relevantes_switching_status']
    alertas = []
    for row in relevantes.get('linhas', []):
        status = str(row.get('Status') or '').strip().lower()
        lote = str(row.get('Lote') or '').strip().lower()
        cobertura = str(row.get('Cobertura') or '').strip().lower()
        bloq = str(row.get('Bloq.') or '').strip().lower()
        pacote = str(row.get('Pacote') or '').strip().lower()
        necessita_sw = str(row.get('Switch?') or '').strip().lower()

        lote_nd = lote in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}
        cobertura_nao_sim = cobertura not in {'sim'}
        status_nao_ok = status not in {'ok'}
        bloqueio_real = bloq not in {'', 'n/d', 'nd', 'não determinado', 'nao determinado'}

        problema = None
        motivo = None
        if status_nao_ok:
            problema = row.get('Status')
            motivo = row.get('Bloq.') if bloqueio_real else row.get('Status')
        elif lote_nd:
            problema = 'lote_nao_determinado'
            motivo = row.get('Status')
        elif cobertura_nao_sim:
            problema = 'cobertura_nao_integral'
            motivo = row.get('Cobertura')
        elif bloqueio_real:
            problema = 'motivo_bloqueio_lote'
            motivo = row.get('Bloq.')

        # Não considerar ausência de campos de switching como alerta quando pay_only + ok + lote definido + sem switching.
        if problema and (not status_nao_ok) and (not lote_nd) and pacote == 'pay_only' and necessita_sw == 'não' and not bloqueio_real:
            problema = None
            motivo = None

        if problema:
            alertas.append({'Data': row.get('Data'), 'Conta': row.get('Conta'), 'problema': problema, 'motivo': motivo})
    print("\n- alertas operacionais:")
    if alertas:
        _imprimir_tabela(['Data','Conta','problema','motivo'], alertas, limite=5)
    else:
        print('  [OK] sem alertas na amostra atual')


def _render_pacote_saida_observavel_oficial(pacote_saida_observavel_oficial=None) -> None:
    if pacote_saida_observavel_oficial is None:
        return

    _imprimir_titulo('SAÍDA OBSERVÁVEL OFICIAL — ETAPA 9')
    resumo = getattr(pacote_saida_observavel_oficial, 'resumo', None)
    auditoria = getattr(pacote_saida_observavel_oficial, 'auditoria', None)
    bloco_console = getattr(pacote_saida_observavel_oficial, 'bloco_console', None)
    lacunas = list(getattr(pacote_saida_observavel_oficial, 'lacunas_renderizacao', []) or [])
    metadados = getattr(pacote_saida_observavel_oficial, 'metadados', {}) or {}

    _imprimir_pares([
        ('artefato', metadados.get('artefato', type(pacote_saida_observavel_oficial).__name__)),
        ('saida_origem', getattr(pacote_saida_observavel_oficial, 'saida_origem', None)),
        ('status', getattr(pacote_saida_observavel_oficial, 'status', None)),
        ('preparado', getattr(pacote_saida_observavel_oficial, 'preparado', None)),
        ('ok', getattr(pacote_saida_observavel_oficial, 'ok', None)),
        ('data de referência', getattr(pacote_saida_observavel_oficial, 'data_referencia', None)),
        ('origem formal', getattr(pacote_saida_observavel_oficial, 'origem_formal', None)),
        ('qtd obrigações cobertas', getattr(resumo, 'qtd_obrigacoes_cobertas', None)),
        ('qtd obrigações bloqueadas', getattr(resumo, 'qtd_obrigacoes_bloqueadas', None)),
        ('qtd lacunas renderização', getattr(resumo, 'qtd_lacunas_renderizacao', len(lacunas))),
        ('origem exclusiva auditoria', getattr(auditoria, 'origem_exclusiva', None)),
    ])

    resumo_operacional = getattr(bloco_console, 'resumo_operacional', {}) or {}
    if resumo_operacional:
        print('\n- resumo operacional oficial:')
        _imprimir_pares(list(resumo_operacional.items()))

    if lacunas:
        print('\n- lacunas de renderização classificadas:')
        linhas = []
        for lacuna in lacunas[:8]:
            linhas.append({
                'codigo': getattr(lacuna, 'codigo', None),
                'severidade': getattr(lacuna, 'severidade', None),
                'origem': getattr(lacuna, 'origem', None),
                'mensagem': getattr(lacuna, 'mensagem', None),
            })
        _imprimir_tabela(['codigo', 'severidade', 'origem', 'mensagem'], linhas, limite=8)



def _valor_oficial(item, campo, padrao=None):
    if isinstance(item, dict):
        return item.get(campo, padrao)
    return getattr(item, campo, padrao)


def _data_obrigacao_oficial(item):
    data = _valor_oficial(item, 'data')
    referencia = _valor_oficial(item, 'referencia_original', {}) or {}
    return data or _valor_oficial(referencia, 'data')


def _descricao_obrigacao_oficial(item):
    referencia = _valor_oficial(item, 'referencia_original', {}) or {}
    return _valor_oficial(referencia, 'descricao') or _valor_oficial(referencia, 'conta') or _valor_oficial(item, 'obrigacao_id') or ''


def _fontes_obrigacao_oficial(item):
    fontes = list(_valor_oficial(item, 'fontes_referenciadas', []) or [])
    return ' + '.join(str(f) for f in fontes if f) or 'n/d'


def _linha_pagamento_oficial(item, bloqueada=False):
    referencia = _valor_oficial(item, 'referencia_original', {}) or {}
    valor = _valor_oficial(item, 'valor_obrigacao_referencial', _valor_oficial(referencia, 'valor', 0.0))
    fontes = _fontes_obrigacao_oficial(item)
    pacote_id = _valor_oficial(item, 'pacote_id') or 'n/d'
    motivo = _valor_oficial(item, 'motivo') or 'n/d'
    return {
        'Data': _data_obrigacao_oficial(item),
        'Conta': _descricao_obrigacao_oficial(item),
        'Lote': fontes if not bloqueada else 'n/d',
        'Pacote': pacote_id,
        'Sw. ant.': 'não',
        'Sw. dep.': 'não',
        'Status': 'bloqueada_oficial' if bloqueada else 'coberta_oficial',
        'Bloq.': motivo if bloqueada else 'n/d',
        'Saldo ant.': 'n/d',
        'Bruto': f'{float(valor or 0.0):.2f}',
        'IR': 'n/d',
        'Liq.': f'{float(_valor_oficial(item, "valor_coberto_referencial", valor) or 0.0):.2f}',
        'Rem.': 'n/d',
    }


def _render_amostras_pagamentos_operacionais_oficiais(pacote_saida_observavel_oficial) -> None:
    bloco_console = getattr(pacote_saida_observavel_oficial, 'bloco_console', None)
    if bloco_console is None:
        return

    _imprimir_titulo('PAGAMENTOS — AMOSTRAS OPERACIONAIS')
    data_ref = getattr(pacote_saida_observavel_oficial, 'data_referencia', None)
    cobertas = list(getattr(bloco_console, 'obrigacoes_cobertas', []) or [])
    bloqueadas = list(getattr(bloco_console, 'obrigacoes_bloqueadas', []) or [])

    ultimas_cobertas = sorted(
        cobertas,
        key=lambda item: (_data_obrigacao_oficial(item) is None, _data_obrigacao_oficial(item), _valor_oficial(item, 'obrigacao_id') or ''),
        reverse=True,
    )[:5]
    print('- últimos 5 pagamentos cobertos pela saída oficial:')
    _imprimir_tabela(
        ['Data', 'Conta', 'Lote', 'Pacote', 'Status'],
        [
            {k: linha[k] for k in ['Data', 'Conta', 'Lote', 'Pacote', 'Status']}
            for linha in (_linha_pagamento_oficial(item, bloqueada=False) for item in ultimas_cobertas)
        ],
        limite=5,
    )

    proximas = []
    for item in cobertas:
        data_item = _data_obrigacao_oficial(item)
        if data_ref is None or data_item is None or data_item >= data_ref:
            proximas.append((data_item, False, item))
    for item in bloqueadas:
        data_item = _data_obrigacao_oficial(item)
        if data_ref is None or data_item is None or data_item >= data_ref:
            proximas.append((data_item, True, item))
    proximas_ordenadas = [item for _, _, item in sorted(
        proximas,
        key=lambda entrada: (entrada[0] is None, entrada[0], entrada[1], _valor_oficial(entrada[2], 'obrigacao_id') or ''),
    )]

    linhas_decisao = [
        {k: linha[k] for k in ['Data', 'Conta', 'Lote', 'Pacote', 'Sw. ant.', 'Sw. dep.', 'Status', 'Bloq.']}
        for linha in (
            _linha_pagamento_oficial(item, bloqueada=str(_valor_oficial(item, 'tipo') or '').endswith('bloqueada_referencialmente'))
            for item in proximas_ordenadas[:5]
        )
    ]
    print('\n- próximos 5 pagamentos — saída oficial:')
    _imprimir_tabela(['Data', 'Conta', 'Lote', 'Pacote', 'Sw. ant.', 'Sw. dep.', 'Status', 'Bloq.'], linhas_decisao, limite=5)

    linhas_valores = [
        {k: linha[k] for k in ['Data', 'Conta', 'Saldo ant.', 'Bruto', 'IR', 'Liq.', 'Rem.']}
        for linha in (
            _linha_pagamento_oficial(item, bloqueada=str(_valor_oficial(item, 'tipo') or '').endswith('bloqueada_referencialmente'))
            for item in proximas_ordenadas[:5]
        )
    ]
    print('\n- próximos 5 pagamentos — valores oficiais:')
    _imprimir_tabela(['Data', 'Conta', 'Saldo ant.', 'Bruto', 'IR', 'Liq.', 'Rem.'], linhas_valores, limite=5)

    if bloqueadas:
        print('\n- obrigações bloqueadas oficiais:')
        linhas_bloqueadas = [
            {k: linha[k] for k in ['Data', 'Conta', 'Pacote', 'Status', 'Bloq.']}
            for linha in (_linha_pagamento_oficial(item, bloqueada=True) for item in bloqueadas[:5])
        ]
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
        _imprimir_tabela(['Data', 'Conta', 'problema', 'motivo'], linhas_alerta, limite=5)
    else:
        print('  [OK] sem alertas na amostra atual')

def _render_secao_ranking_oficial(contexto_operacional, saida_canonica=None) -> None:
    ranking = getattr(contexto_operacional, 'ranking_carteira', None)
    if ranking is None:
        return

    _imprimir_titulo('RANQUEAMENTO OFICIAL DA CARTEIRA')
    _imprimir_pares([
        ('produtos totais', ranking.resumo.get('produtos_total')),
        ('produtos ativos ranqueados', ranking.resumo.get('produtos_ativos_ranqueados')),
        ('destinos elegíveis de switching', ranking.auditoria.get('qtd_destinos_switch')),
        ('destino top 1', ranking.auditoria.get('destino_top1')),
        ('método', ranking.auditoria.get('metodo')),
        ('origem da amostra', getattr(saida_canonica, 'versao', VERSAO_BASELINE)),
    ])

    linhas = list(getattr(saida_canonica, 'ranking_amostra', []) or [])
    print('- amostra do ranking relevante do dia:')
    _imprimir_tabela(
        ['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.'],
        linhas,
        limite=10,
    )


def _render_secao_switchings_oficiais(contexto_operacional, saida_canonica=None, pacote_saida_observavel_temporal=None) -> None:
    ranking = getattr(contexto_operacional, 'ranking_carteira', None)
    destino_top1 = ranking.auditoria.get('destino_top1') if ranking is not None else None
    linhas = construir_switchings_observaveis(contexto_operacional, saida_canonica, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)[:10]
    lotes_avaliados = len(linhas)
    candidatos_avaliados = len(linhas)

    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    _imprimir_pares([
        ('lotes avaliados para switching', lotes_avaliados),
        ('candidatos avaliados para switching', candidatos_avaliados),
        (
            'destinos elegíveis de switching',
            len(ranking.quadro_destinos_switch)
            if ranking is not None and isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame)
            else 0,
        ),
        ('switchings promovidos/executados', len(linhas)),
        ('destino top 1 do ranking', destino_top1),
        ('origem da amostra', getattr(saida_canonica, 'versao', VERSAO_BASELINE)),
    ])

    print('- amostra de switchings reais da janela (independente de pagamentos):')
    _imprimir_tabela(['Data', 'Lote origem', 'Lote destino', 'Produto origem', 'Produto destino'], linhas, limite=5)
    bloqueados = list(getattr(contexto_operacional, '_switchings_bloqueados_gate_auditoria', []) or [])[:10]
    if bloqueados:
        print('- candidatos bloqueados por gate (auditoria):')
        _imprimir_tabela(['Data', 'Lote origem', 'Produto origem', 'Destino', 'Status'], bloqueados, limite=5)

    total_sinteticos = len(getattr(saida_canonica, 'lotes_sinteticos_pos_switching_console', lambda **_: [])(limite=200) or [])
    total_aportes = len(getattr(saida_canonica, 'recebidos_atuais', []) or [])
    alocacao = {'linhas': list(getattr(saida_canonica, 'recebidos_futuros_console', lambda **_: [])(limite=3) or [])}

    print('\n- resumo operacional curto:')
    _imprimir_pares([
        ('total de switchings promovidos', len(linhas)),
        ('total de lotes sintéticos pós-switching', total_sinteticos),
        ('total de aportes futuros', total_aportes),
    ])
    if alocacao['linhas']:
        print('- próximos 3 aportes (resumo):')
        _imprimir_tabela(['Data', 'Lote', 'Valor', 'Status'], alocacao['linhas'], limite=3)

def _render_situacao_atual_operacional(contexto_operacional, saida_canonica, resumo_fechamento, resumo_recebidos, pacote_saida_observavel_temporal=None, estado_temporal_inicial=None) -> None:
    _imprimir_titulo('SITUAÇÃO ATUAL')

    if resumo_fechamento:
        _imprimir_pares([
            ('data de referência', resumo_fechamento.get('data_referencia')),
            ('status do fechamento econômico', resumo_fechamento.get('status_fechamento')),
            ('fonte do fechamento', resumo_fechamento.get('fonte_fechamento')),
            ('fechamentos com fallback CDI', resumo_fechamento.get('qtd_fechamentos_fallback_cdi', 0)),
            ('último fator explícito CDI', resumo_fechamento.get('data_ultimo_fator_explicito_cdi')),
            ('data confirmada da série', resumo_fechamento.get('data_fechamento_confirmado')),
        ])
        if resumo_fechamento.get('observacao'):
            print(f"- leitura auditável: {resumo_fechamento.get('observacao')}")

    print('\n- lotes exauridos:')
    exauridos_id = construir_linhas_lotes_id_curta(contexto_operacional, saida_canonica, tipo='exauridos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)
    exauridos_val = construir_linhas_lotes_valores_curta(contexto_operacional, saida_canonica, tipo='exauridos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)
    if exauridos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_EXAURIDOS_ID_CURTAS, exauridos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, exauridos_val, limite=None)
    else:
        print('  [OK] sem lotes exauridos nesta execução')

    print('\n- lotes ativos:')
    ativos_id = construir_linhas_lotes_id_curta(contexto_operacional, saida_canonica, tipo='ativos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)
    ativos_val = construir_linhas_lotes_valores_curta(contexto_operacional, saida_canonica, tipo='ativos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)
    ativos_id = _filtrar_lotes_ativos_com_estado_temporal(ativos_id, estado_temporal_inicial=estado_temporal_inicial)
    ativos_val = _filtrar_lotes_ativos_com_estado_temporal(ativos_val, estado_temporal_inicial=estado_temporal_inicial)
    if ativos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_ATIVOS_ID_CURTAS, ativos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, ativos_val, limite=None)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')

    print('\n- patrimônio total dos lotes:')
    _imprimir_tabela(
        ['Métrica', 'Valor'],
        construir_resumo_patrimonio_total_lotes(
            contexto_operacional,
            saida_canonica,
            pacote_saida_observavel_temporal=pacote_saida_observavel_temporal,
            estado_temporal_inicial=estado_temporal_inicial,
        ),
        limite=None,
    )

    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))

def render_console(contexto_operacional, saida_canonica=None, estado_temporal_inicial=None, pacote_saida_observavel_oficial=None) -> None:
    """Renderiza o console usando contexto e saída canônica já construídos.

    Esta função não carrega planilha, não baixa dados e não reconstrói cache.
    Ela apenas renderiza o estado recebido.
    """
    if saida_canonica is None:
        saida_canonica = construir_saida_canonica_com_switching_v17_c7(contexto_operacional, versao=VERSAO_BASELINE)
        matriz = construir_matriz_elegibilidade_fontes_s7b(
            contexto_operacional,
            data_referencia=saida_canonica.data_referencia,
            saida_canonica_preconstruida=saida_canonica,
        )
        saida_canonica, _ = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz)
    ativos_obs = construir_linhas_lotes_consolidados(contexto_operacional, saida_canonica, tipo="ativos", modo_bootstrap_pacote=True)
    exauridos_obs = construir_linhas_lotes_consolidados(contexto_operacional, saida_canonica, tipo="exauridos", modo_bootstrap_pacote=True)
    amostras_obs = construir_amostras_pagamentos_operacionais(saida_canonica, limite=1000, contexto=contexto_operacional, pacote_saida_observavel_temporal=construir_pacote_saida_observavel_temporal(contexto_operacional, saida_canonica, lotes_ativos_observaveis=ativos_obs, lotes_exauridos_observaveis=exauridos_obs), estado_temporal_inicial=estado_temporal_inicial)
    pagamentos_obs = list((amostras_obs.get("realizados") or {}).get("linhas") or [])
    pacote_saida_observavel_temporal = construir_pacote_saida_observavel_temporal(
        contexto_operacional,
        saida_canonica,
        lotes_ativos_observaveis=ativos_obs,
        lotes_exauridos_observaveis=exauridos_obs,
        pagamentos_realizados_observaveis=pagamentos_obs,
    )

    pacote_config = contexto_operacional.pacote_config
    contexto = contexto_operacional.execucao
    pacote_planilha = contexto_operacional.pacote_planilha
    carteira_canonica = contexto_operacional.carteira_canonica
    cache_cdi = contexto_operacional.cache_cdi

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item["nome_aba"]: item for item in resumo_planilha}

    abas_cfg = pacote_config.conteudo.get("abas", {}) if isinstance(pacote_config.conteudo.get("abas"), dict) else {}
    nome_aba_carteira_real = getattr(carteira_canonica, "nome_aba", abas_cfg.get("carteira", "Carteira"))
    dados_operacionais = getattr(contexto_operacional, "dados_operacionais", None)

    nome_aba_salarios_real = (
        getattr(dados_operacionais, "nome_aba_salarios", "")
        or abas_cfg.get("salarios", "")
        or ("Salários" if "Salários" in pacote_planilha.nomes_abas else "")
    )
    nome_aba_switching_real = (
        getattr(dados_operacionais, "nome_aba_switching", "")
        or abas_cfg.get("switching", "")
        or ("Switching" if "Switching" in pacote_planilha.nomes_abas else "")
    )

    abas_operacionais_canonicas = [
        ("carteira", nome_aba_carteira_real),
        ("salarios", nome_aba_salarios_real),
        ("despesas", abas_cfg.get("despesas", "Todos os Gastos")),
        ("switching", nome_aba_switching_real),
        ("lotes", abas_cfg.get("lotes", "Inventário de Lotes")),
    ]

    abas_primarias_reais = [
        (chave, nome_aba)
        for chave, nome_aba in abas_operacionais_canonicas
        if nome_aba
    ]

    abas_auxiliares = [
        nome for nome in pacote_planilha.nomes_abas
        if nome not in {aba for _, aba in abas_primarias_reais}
    ]

    severidade_dependencias = _severidade(
        avisos=contexto.relatorio_dependencias.get("ausentes", []),
        condicao_ok=len(contexto.relatorio_dependencias.get("ausentes", [])) == 0,
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

    _render_pacote_saida_observavel_oficial(pacote_saida_observavel_oficial)

    if pacote_saida_observavel_oficial is not None and getattr(pacote_saida_observavel_oficial, 'preparado', False):
        _render_amostras_pagamentos_operacionais_oficiais(pacote_saida_observavel_oficial)
    else:
        _render_amostras_pagamentos_operacionais(contexto_operacional, saida_canonica, pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)

    _render_secao_ranking_oficial(contexto_operacional, saida_canonica)
    _render_secao_switchings_oficiais(contexto_operacional, saida_canonica, pacote_saida_observavel_temporal)

    resumo_fechamento_bruto = {
        item.get("Métrica"): item.get("Valor")
        for item in saida_canonica.fechamento_atual
    }

    mapeamento_fechamento = {
        "Data de referência": "data_referencia",
        "Status do fechamento econômico": "status_fechamento",
        "Fonte do fechamento": "fonte_fechamento",
        "Fechamentos com fallback CDI": "qtd_fechamentos_fallback_cdi",
        "Último fator explícito CDI": "data_ultimo_fator_explicito_cdi",
        "Data confirmada da série": "data_fechamento_confirmado",
        "Leitura auditável": "observacao",
    }

    resumo_fechamento_situacao_atual = {
        chave: valor
        for chave, valor in resumo_fechamento_bruto.items()
        if chave is not None
    }

    for rotulo_humano, chave_tecnica in mapeamento_fechamento.items():
        if chave_tecnica not in resumo_fechamento_situacao_atual and rotulo_humano in resumo_fechamento_bruto:
            resumo_fechamento_situacao_atual[chave_tecnica] = resumo_fechamento_bruto.get(rotulo_humano)

    resumo_recebidos_saida = {
        item.get("Métrica"): item.get("Valor")
        for item in saida_canonica.resumo_recebidos
    }

    _render_situacao_atual_operacional(
        contexto_operacional,
        saida_canonica,
        resumo_fechamento_situacao_atual,
        resumo_recebidos_saida,
        pacote_saida_observavel_temporal,
        estado_temporal_inicial=estado_temporal_inicial,
    )


def main() -> None:
    """Execução standalone do console. Para a rota oficial integrada, use aplicacao/principal.py."""
    contexto_operacional = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal_inicial = construir_estado_temporal_inicial(contexto_operacional)
    saida_canonica = construir_saida_canonica_com_switching_v17_c7(contexto_operacional, versao=VERSAO_BASELINE)
    matriz = construir_matriz_elegibilidade_fontes_s7b(
        contexto_operacional,
        data_referencia=saida_canonica.data_referencia,
        saida_canonica_preconstruida=saida_canonica,
    )
    saida_canonica, _ = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz)
    render_console(contexto_operacional, saida_canonica, estado_temporal_inicial=estado_temporal_inicial)

if __name__ == '__main__':
    main()
