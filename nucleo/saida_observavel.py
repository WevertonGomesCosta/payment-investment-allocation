from __future__ import annotations

from typing import Any


COLS_LOTES_ID_CURTAS = [
    'Lote',
    'Carteira',
    'Aplic.',
    'Base fiscal',
    'Dias corr.',
    'Dias úteis',
]

COLS_LOTES_VALORES_CURTAS = [
    'Lote',
    'Orig.',
    'Bruto sac.',
    'Líq. sac.',
    'Bruto atual',
    'Líq. atual',
    'Patr. líq.',
    'Rend. líq.',
]

COLS_RECEBIDOS_AUDITAVEIS = [
    'Recebido',
    'Lote origem',
    'Recebimento',
    'Aplicação',
    'Valor bruto',
    'Valor líquido',
    'Status',
    'Destino',
    'Pagamentos vinculados',
    'Valor vinculado',
    'Residual aplicação',
    'Disponível ref',
    'Observação',
]


def para_float(valor: Any) -> float:
    try:
        if valor is None or valor == '':
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def somar_valores_sacados_por_lote(contexto, saida=None) -> dict[str, dict[str, float]]:
    """Soma valores sacados por lote usando replay + auditoria de recebidos.

    O replay é a fonte principal. Para lotes não aplicados/exauridos, a
    auditoria de recebidos complementa a soma, pois alguns desses lotes podem
    ter sido usados diretamente em pagamento e aparecer subcontados no log.
    """
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    somas: dict[str, dict[str, float]] = {}

    if log is not None and hasattr(log, 'iterrows') and len(log) and 'Lote' in getattr(log, 'columns', []):
        for _, row in log.iterrows():
            lote_id = str(row.get('Lote') or '').strip()
            if not lote_id:
                continue

            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(atual['bruto_sacado'] + para_float(row.get('Bruto')), 2)
            atual['liquido_sacado'] = round(
                atual['liquido_sacado'] + para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')),
                2,
            )

    if saida is not None:
        for recebido in (getattr(saida, 'recebidos_atuais', []) or []):
            lote_id = str(recebido.get('Lote origem') or '').strip()
            if not lote_id:
                continue

            status = str(recebido.get('Status') or '').strip().lower()
            destino = str(recebido.get('Destino') or '').strip().lower()

            usar_recebido = (
                status in {'exaurido', 'uso_pre_aplicacao_com_aporte_posterior'}
                or destino in {'pagamento', 'pagamento_e_aplicacao'}
            )
            if not usar_recebido:
                continue

            valor_vinculado = para_float(recebido.get('Valor vinculado'))
            valor_liquido = para_float(recebido.get('Valor líquido'))
            valor_bruto = para_float(recebido.get('Valor bruto'))

            liquido_ref = valor_vinculado if valor_vinculado > 0 else valor_liquido
            bruto_ref = max(valor_vinculado, valor_bruto if status == 'exaurido' else 0.0, liquido_ref)

            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(max(atual['bruto_sacado'], bruto_ref), 2)
            atual['liquido_sacado'] = round(max(atual['liquido_sacado'], liquido_ref), 2)

    return somas


def construir_linhas_lotes_consolidados(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    campo = 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos'
    itens = list(getattr(saida, campo, []) or [])
    somas = somar_valores_sacados_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in itens:
        lote_id = str(item.get('Lote') or '').strip()
        sacado = somas.get(lote_id, {})

        valor_original = round(para_float(item.get('Valor original')), 2)
        bruto_sacado = round(para_float(sacado.get('bruto_sacado')), 2)
        liquido_sacado = round(para_float(sacado.get('liquido_sacado')), 2)

        bruto_atual = 0.0 if tipo == 'exauridos' else round(para_float(item.get('Bruto')), 2)
        liquido_atual = 0.0 if tipo == 'exauridos' else round(para_float(item.get('Líquido')), 2)

        patrimonio_liquido = round(liquido_sacado + liquido_atual, 2)
        rendimento_liquido = round(patrimonio_liquido - valor_original, 2)

        linhas.append({
            'Lote': item.get('Lote'),
            'Carteira': item.get('Produto'),
            'Aplic.': item.get('Aplicação'),
            'Base fiscal': item.get('Aplicação'),
            'Dias corr.': item.get('Dias corridos'),
            'Dias úteis': item.get('Dias úteis'),
            'Orig.': valor_original,
            'Bruto sac.': bruto_sacado,
            'Líq. sac.': liquido_sacado,
            'Bruto atual': bruto_atual,
            'Líq. atual': liquido_atual,
            'Patr. líq.': patrimonio_liquido,
            'Rend. líq.': rendimento_liquido,
        })

    return linhas


def construir_linhas_lotes_id_curta(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    return [
        {chave: item.get(chave) for chave in COLS_LOTES_ID_CURTAS}
        for item in construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo)
    ]


def construir_linhas_lotes_valores_curta(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    return [
        {chave: item.get(chave) for chave in COLS_LOTES_VALORES_CURTAS}
        for item in construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo)
    ]


def construir_resumo_patrimonio_total_lotes(contexto, saida) -> list[dict[str, Any]]:
    linhas = (
        construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos')
        + construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos')
    )

    valor_original_total = round(sum(para_float(item.get('Orig.')) for item in linhas), 2)
    valor_total_bruto_sacado = round(sum(para_float(item.get('Bruto sac.')) for item in linhas), 2)
    valor_total_liquido_sacado = round(sum(para_float(item.get('Líq. sac.')) for item in linhas), 2)
    valor_bruto_atual = round(sum(para_float(item.get('Bruto atual')) for item in linhas), 2)
    valor_liquido_atual = round(sum(para_float(item.get('Líq. atual')) for item in linhas), 2)
    patrimonio_liquido_atual = round(sum(para_float(item.get('Patr. líq.')) for item in linhas), 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_total, 2)

    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
    ]


def construir_blocos_situacao_atual(contexto, saida) -> list[dict[str, Any]]:
    return [
        {
            'titulo': 'Lotes exauridos — identificação',
            'headers': COLS_LOTES_ID_CURTAS,
            'linhas': construir_linhas_lotes_id_curta(contexto, saida, tipo='exauridos'),
        },
        {
            'titulo': 'Lotes exauridos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_CURTAS,
            'linhas': construir_linhas_lotes_valores_curta(contexto, saida, tipo='exauridos'),
        },
        {
            'titulo': 'Lotes ativos — identificação',
            'headers': COLS_LOTES_ID_CURTAS,
            'linhas': construir_linhas_lotes_id_curta(contexto, saida, tipo='ativos'),
        },
        {
            'titulo': 'Lotes ativos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_CURTAS,
            'linhas': construir_linhas_lotes_valores_curta(contexto, saida, tipo='ativos'),
        },
        {
            'titulo': 'Patrimônio total dos lotes',
            'headers': ['Métrica', 'Valor'],
            'linhas': construir_resumo_patrimonio_total_lotes(contexto, saida),
        },
        {
            'titulo': 'Recebidos auditáveis',
            'headers': COLS_RECEBIDOS_AUDITAVEIS,
            'linhas': list(getattr(saida, 'recebidos_atuais', []) or []),
        },
        {
            'titulo': 'Fechamento econômico',
            'headers': ['Métrica', 'Valor'],
            'linhas': list(getattr(saida, 'fechamento_atual', []) or []),
        },
        {
            'titulo': 'Resumo de recebidos',
            'headers': ['Métrica', 'Valor'],
            'linhas': list(getattr(saida, 'resumo_recebidos', []) or []),
        },
    ]

# ============================================================
# V225 — Amostras operacionais de pagamentos
# Fonte única para console.
# ============================================================

COLS_PAGAMENTOS_REALIZADOS_CONSOLE = [
    'Data',
    'Descrição',
    'Valor',
    'Lotes usados',
    'Saldo Antes',
    'Bruto',
    'Imposto',
    'Líquido',
    'Saldo Remanescente',
]

COLS_PAGAMENTOS_PROXIMOS_CONSOLE = [
    'Data',
    'Conta',
    'Valor',
    'Lote',
    'Pacote',
    'Switch?',
    'Reserva',
    'Saldo ant.',
    'Bruto',
    'IR',
    'Liq.',
    'Rem.',
    'Sw. ant.',
    'Sw. dep.',
    'Status',
    'Bloq.',
]

COLS_PAGAMENTOS_PROXIMOS_VALORES_FONTE = [
    'Data',
    'Conta',
    'Valor',
    'Lote',
    'Pacote',
    'Switch?',
    'Reserva',
    'Saldo ant.',
    'Bruto',
    'IR',
    'Liq.',
    'Rem.',
]

COLS_PAGAMENTOS_PROXIMOS_SWITCHING_STATUS = [
    'Data',
    'Conta',
    'Lote',
    'Pacote',
    'Sw. ant.',
    'Sw. dep.',
    'Status',
    'Bloq.',
]

COLS_PAGAMENTOS_FUTUROS_SWITCHING_RELEVANTE = [
    'Data',
    'Conta',
    'Valor',
    'Lote',
    'Pós-switch',
    'Destino sw.',
    'Origem sw.',
    'Fonte sw.',
    'Data sw.',
    'Score sw.',
    'Pacote',
    'Sw. ant.',
    'Status',
    'Saldo temp. ant.',
    'Consumo temp.',
    'Saldo temp. dep.',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_DECISAO = [
    'Data',
    'Conta',
    'Valor',
    'Lote',
    'Pós-switch',
    'Destino sw.',
    'Origem sw.',
    'Pacote',
    'Sw. ant.',
    'Status',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_CONSUMO = [
    'Data',
    'Conta',
    'Lote',
    'Saldo ant.',
    'Consumo',
    'Saldo dep.',
]

COLS_RECEBIDOS_FUTUROS_CONSOLE = [
    'Data',
    'Lote',
    'Valor',
    'Status',
    'Destino',
    'Carteira',
    'Usado',
    'Saldo',
]


def construir_amostras_pagamentos_operacionais(saida, *, limite: int = 5) -> dict[str, object]:
    """Constrói as amostras operacionais de pagamentos para o console.

    Fonte dos dados:
        saida_canonica.pagamentos_realizados_console(...)
        saida_canonica.pagamentos_proximos_console(...)

    Esta função centraliza apenas o contrato observável das amostras.
    Não altera cálculo, replay ou regra de pagamentos.
    """
    return {
        'titulo': 'PAGAMENTOS — AMOSTRAS OPERACIONAIS',
        'realizados': {
            'rotulo': 'últimos 5 pagamentos já realizados',
            'headers': list(COLS_PAGAMENTOS_REALIZADOS_CONSOLE),
            'linhas': saida.pagamentos_realizados_console(limite=limite),
            'limite': limite,
        },
        'proximos': {
            'rotulo': 'próximos 5 pagamentos',
            'headers': list(COLS_PAGAMENTOS_PROXIMOS_CONSOLE),
            'linhas': saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_valores_fonte': {
            'rotulo': 'próximos 5 pagamentos — valores/fonte',
            'headers': list(COLS_PAGAMENTOS_PROXIMOS_VALORES_FONTE),
            'linhas': saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_switching_status': {
            'rotulo': 'próximos 5 pagamentos — switching/status',
            'headers': list(COLS_PAGAMENTOS_PROXIMOS_SWITCHING_STATUS),
            'linhas': saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_relevantes_switching_status': construir_amostra_pagamentos_futuros_switching_relevante(saida, limite=limite),
    }


def construir_amostra_pagamentos_futuros_switching_relevante(saida, *, limite: int = 5) -> dict[str, object]:
    if hasattr(saida, 'pagamentos_futuros_console_completo'):
        linhas_base = list(saida.pagamentos_futuros_console_completo() or [])
    else:
        linhas_base = list(getattr(saida, 'pagamentos_proximos_console', lambda **_: [])(limite=limite) or [])
    relevantes: list[dict[str, object]] = []
    for item in linhas_base:
        sw_ant = str(item.get('Sw. ant.') or '').strip().lower()
        sw_dep = str(item.get('Sw. dep.') or '').strip().lower()
        status = str(item.get('Status') or '').strip().lower()
        bloq = str(item.get('Bloq.') or '').strip().lower()
        pacote = str(item.get('Pacote') or '').strip().lower()
        switch = str(item.get('Switch?') or '').strip().lower()
        eh_relevante = (
            sw_ant == 'sim'
            or sw_dep == 'sim'
            or (status not in {'', 'ok', 'n/d'})
            or (bloq not in {'', 'n/d'})
            or (pacote not in {'', 'pay_only'})
            or switch == 'sim'
        )
        if eh_relevante:
            relevantes.append(item)
    return {
        'rotulo': 'pagamentos futuros com switching/status relevante',
        'headers': list(COLS_PAGAMENTOS_FUTUROS_SWITCHING_RELEVANTE),
        'linhas': relevantes[:limite],
        'limite': limite,
        'decisao': {
            'rotulo': 'pagamentos futuros com switching/status relevante — decisão',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_DECISAO),
            'linhas': relevantes[:limite],
            'limite': limite,
        },
        'consumo_temporal': {
            'rotulo': 'pagamentos futuros com switching/status relevante — consumo temporal',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_CONSUMO),
            'linhas': [
                {
                    'Data': row.get('Data'),
                    'Conta': row.get('Conta'),
                    'Lote': row.get('Lote'),
                    'Saldo ant.': row.get('Saldo temp. ant.'),
                    'Consumo': row.get('Consumo temp.'),
                    'Saldo dep.': row.get('Saldo temp. dep.'),
                }
                for row in relevantes[:limite]
            ],
            'limite': limite,
        },
    }


def construir_amostra_alocacao_recebidos_futuros(saida, *, limite: int = 5) -> dict[str, object]:
    return {
        'rotulo': 'aportes futuros / alocação',
        'headers': list(COLS_RECEBIDOS_FUTUROS_CONSOLE),
        'linhas': saida.recebidos_futuros_console(limite=limite),
        'limite': limite,
    }
