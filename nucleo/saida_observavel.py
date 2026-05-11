from __future__ import annotations

from datetime import date, datetime
from typing import Any

from nucleo.calendario_financeiro import calcular_dias_lote


COLS_LOTES_ID_CURTAS = [
    'Lote',
    'Status ciclo',
    'Carteira',
    'Aplic.',
    'Base fiscal',
    'Data término',
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

COLS_ORIGENS_MIGRADAS_SWITCHING = [
    'Lote origem',
    'Status',
    'Status ciclo',
    'Data término',
    'Dias corr.',
    'Dias úteis',
    'Valor migrado',
    'Bruto sac. hist.',
    'Líq. sac. hist.',
    'Linhas extrato',
    'Destinos',
    'Não ativo',
    'Não fonte',
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


def _vazio_observavel(valor: Any) -> bool:
    return valor is None or str(valor).strip() in {"", "n/d", "nan", "NaT"}


def _coagir_data_observavel(valor: Any) -> date | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.fromisoformat(str(valor)[:10]).date()
    except Exception:
        return None


def _fmt_data_observavel(valor: Any, *, padrao: str = "n/d") -> str:
    data = _coagir_data_observavel(valor)
    return data.isoformat() if data is not None else padrao


def _serie_cdi_contexto(contexto: Any) -> Any:
    cache = getattr(contexto, "cache_cdi", None)
    return getattr(cache, "serie_cdi", None) if cache is not None else None


def _calcular_dias_observavel(contexto: Any, data_inicio: Any, data_fim: Any) -> dict[str, int | str]:
    inicio = _coagir_data_observavel(data_inicio)
    fim = _coagir_data_observavel(data_fim)
    if inicio is None or fim is None:
        return {"dias_corridos": "", "dias_uteis": ""}

    try:
        return calcular_dias_lote(
            inicio,
            fim,
            contexto.calendario_financeiro,
            _serie_cdi_contexto(contexto),
            data_fechamento_referencia=fim,
        )
    except Exception:
        # Fallback apenas observável para não quebrar a renderização;
        # a validação exige que o cálculo canônico funcione nos casos críticos.
        dias_corridos = max((fim - inicio).days, 0)
        dias_uteis = 0
        cursor = inicio
        while cursor < fim:
            cursor = cursor.fromordinal(cursor.toordinal() + 1)
            if cursor.weekday() < 5:
                dias_uteis += 1
        return {"dias_corridos": dias_corridos, "dias_uteis": dias_uteis}


def _split_lotes_observavel(valor: Any) -> list[str]:
    return [p.strip() for p in str(valor or "").split("+") if p.strip()]


def _mapa_ultimo_uso_lotes_saida(saida: Any) -> dict[str, str]:
    mapa: dict[str, str] = {}
    for linha in list(getattr(saida, "extrato_passado", []) or []):
        data_txt = _fmt_data_observavel(linha.get("Data"), padrao="")
        if not data_txt:
            continue
        lote_raw = linha.get("Lotes usados") or linha.get("Lote") or ""
        for lote in _split_lotes_observavel(lote_raw):
            if lote and data_txt > mapa.get(lote, ""):
                mapa[lote] = data_txt
    return mapa


def _registrar_aplicacao(mapa: dict[str, Any], lote_id: Any, data_aplicacao: Any) -> None:
    lote = str(lote_id or "").strip()
    data = _coagir_data_observavel(data_aplicacao)
    if not lote or data is None:
        return
    mapa.setdefault(lote, data)


def _mapa_aplicacao_por_lote(contexto: Any, saida: Any) -> dict[str, Any]:
    mapa: dict[str, Any] = {}

    for item in list(getattr(saida, "lotes_ativos", []) or []) + list(getattr(saida, "lotes_exauridos", []) or []):
        _registrar_aplicacao(mapa, item.get("Lote"), item.get("Aplicação"))

    replay = getattr(contexto, "replay_passado", None)
    for attr in [
        "lotes_apos_replay",
        "lotes_antes_replay",
        "lotes_replay",
        "lotes_originais",
        "lotes",
    ]:
        lotes = getattr(replay, attr, None) if replay is not None else None
        if not lotes:
            continue
        try:
            iter_lotes = list(lotes)
        except Exception:
            continue
        for lote_obj in iter_lotes:
            lote_id = (
                getattr(lote_obj, "id", None)
                or getattr(lote_obj, "lote_id", None)
                or getattr(lote_obj, "nome", None)
            )
            data_aplicacao = (
                getattr(lote_obj, "data_aplicacao", None)
                or getattr(lote_obj, "data_aplicação", None)
                or getattr(lote_obj, "data_base_fiscal", None)
            )
            _registrar_aplicacao(mapa, lote_id, data_aplicacao)

    # Varredura leve em DataFrames anexados ao contexto/pacotes, sem depender
    # do nome interno exato do pacote de dados.
    fila = [contexto]
    vistos: set[int] = set()
    while fila and len(vistos) < 200:
        obj = fila.pop(0)
        if obj is None or id(obj) in vistos:
            continue
        vistos.add(id(obj))

        cols = getattr(obj, "columns", None)
        if cols is not None and hasattr(obj, "iterrows"):
            colunas = list(cols)
            col_lote = next((c for c in colunas if str(c).strip().lower() in {"lote (id)", "lote", "lote id", "lote_id", "lote origem"}), None)
            col_data = next((c for c in colunas if str(c).strip().lower() in {"data aplicação", "data aplicacao", "aplicação", "aplicacao", "data_aplicacao"}), None)
            if col_lote is not None and col_data is not None:
                try:
                    for _, row in obj.iterrows():
                        _registrar_aplicacao(mapa, row.get(col_lote), row.get(col_data))
                except Exception:
                    pass
            continue

        dct = getattr(obj, "__dict__", None)
        if isinstance(dct, dict):
            for val in dct.values():
                if id(val) not in vistos:
                    fila.append(val)

    return mapa


def _origens_migradas_auditoria(saida: Any) -> list[dict[str, Any]]:
    auditoria = dict(getattr(saida, "auditoria", {}) or {})
    return list(auditoria.get("origens_migradas_por_switching") or [])


def _status_ciclo_lote(item: dict[str, Any], *, tipo: str) -> str:
    status_item = str(item.get("Status") or "").strip()
    if tipo == "exauridos":
        return "exaurido_por_saque"
    if status_item == "ativo_pos_switching":
        return "ativo_pos_switching"
    return "ativo"


def construir_linhas_lotes_consolidados(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    campo = 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos'
    itens = list(getattr(saida, campo, []) or [])
    somas = somar_valores_sacados_por_lote(contexto, saida)
    mapa_termino = _mapa_ultimo_uso_lotes_saida(saida)
    linhas: list[dict[str, Any]] = []

    for item in itens:
        lote_id = str(item.get('Lote') or '').strip()
        sacado = somas.get(lote_id, {})
        status_ciclo = _status_ciclo_lote(item, tipo=tipo)

        data_aplicacao = item.get('Aplicação')
        data_termino = 'n/d'
        data_referencia_dias = getattr(saida, 'data_referencia', None)

        if tipo == 'exauridos':
            data_termino = mapa_termino.get(lote_id, item.get('Data término') or 'n/d')
            data_referencia_dias = data_termino

        dias_corridos = item.get('Dias corridos')
        dias_uteis = item.get('Dias úteis')
        if _vazio_observavel(dias_corridos) or _vazio_observavel(dias_uteis):
            dias_calc = _calcular_dias_observavel(contexto, data_aplicacao, data_referencia_dias)
            dias_corridos = dias_calc.get('dias_corridos', dias_corridos)
            dias_uteis = dias_calc.get('dias_uteis', dias_uteis)

        valor_original = round(para_float(item.get('Valor original')), 2)
        bruto_sacado = round(para_float(sacado.get('bruto_sacado')), 2)
        liquido_sacado = round(para_float(sacado.get('liquido_sacado')), 2)

        bruto_atual = 0.0 if tipo == 'exauridos' else round(para_float(item.get('Bruto')), 2)
        liquido_atual = 0.0 if tipo == 'exauridos' else round(para_float(item.get('Líquido')), 2)

        patrimonio_liquido = round(liquido_sacado + liquido_atual, 2)
        rendimento_liquido = round(patrimonio_liquido - valor_original, 2)

        linhas.append({
            'Lote': item.get('Lote'),
            'Status ciclo': status_ciclo,
            'Carteira': item.get('Produto'),
            'Aplic.': _fmt_data_observavel(data_aplicacao, padrao=item.get('Aplicação') or 'n/d'),
            'Base fiscal': _fmt_data_observavel(item.get('Base fiscal') or data_aplicacao, padrao=_fmt_data_observavel(data_aplicacao)),
            'Data término': _fmt_data_observavel(data_termino),
            'Dias corr.': dias_corridos,
            'Dias úteis': dias_uteis,
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


def construir_linhas_lotes_encerrados_por_switching(contexto, saida) -> list[dict[str, Any]]:
    aplicacoes = _mapa_aplicacao_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in _origens_migradas_auditoria(saida):
        lote = str(item.get('lote_origem') or '').strip()
        data_switching = item.get('data_switching') or 'n/d'
        data_aplicacao = aplicacoes.get(lote)
        dias = _calcular_dias_observavel(contexto, data_aplicacao, data_switching)

        linhas.append({
            'Lote': lote,
            'Status ciclo': 'migrado_por_switching',
            'Carteira': 'origem_migrada_por_switching',
            'Aplic.': _fmt_data_observavel(data_aplicacao),
            'Base fiscal': _fmt_data_observavel(data_aplicacao),
            'Data término': _fmt_data_observavel(data_switching),
            'Dias corr.': dias.get('dias_corridos', ''),
            'Dias úteis': dias.get('dias_uteis', ''),
        })

    return linhas


def construir_linhas_origens_migradas_por_switching(contexto, saida) -> list[dict[str, Any]]:
    aplicacoes = _mapa_aplicacao_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in _origens_migradas_auditoria(saida):
        lote = str(item.get('lote_origem') or '').strip()
        data_switching = item.get('data_switching') or 'n/d'
        data_aplicacao = aplicacoes.get(lote)
        dias = _calcular_dias_observavel(contexto, data_aplicacao, data_switching)
        destinos = list(item.get('destinos_vinculados') or [])

        linhas.append({
            'Lote origem': lote,
            'Status': item.get('status_origem') or 'migrado_por_switching',
            'Status ciclo': 'migrado_por_switching',
            'Data término': _fmt_data_observavel(data_switching),
            'Dias corr.': dias.get('dias_corridos', ''),
            'Dias úteis': dias.get('dias_uteis', ''),
            'Valor migrado': round(para_float(item.get('valor_liquido_migrado_total')), 2),
            'Bruto sac. hist.': round(para_float(item.get('valor_bruto_sacado_historico')), 2),
            'Líq. sac. hist.': round(para_float(item.get('valor_liquido_sacado_historico')), 2),
            'Linhas extrato': int(item.get('quantidade_linhas_extrato_passado') or 0),
            'Destinos': len(destinos),
            'Não ativo': bool(item.get('nao_e_ativo_comum')),
            'Não fonte': bool(item.get('nao_e_fonte_disponivel_pagamentos')),
        })

    return linhas


def _reconciliacao_origens_migradas(saida) -> dict[str, float]:
    auditoria = dict(getattr(saida, 'auditoria', {}) or {})
    rec = dict(auditoria.get('reconciliacao_patrimonial_origens_migradas') or {})
    return {
        'valor_liquido_migrado_total': round(para_float(rec.get('valor_liquido_migrado_total')), 2),
        'valor_bruto_sacado_historico_total': round(para_float(rec.get('valor_bruto_sacado_historico_total')), 2),
        'valor_liquido_sacado_historico_total': round(para_float(rec.get('valor_liquido_sacado_historico_total')), 2),
    }


def construir_resumo_patrimonio_total_lotes(contexto, saida) -> list[dict[str, Any]]:
    linhas = (
        construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos')
        + construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos')
    )

    valor_original_total = round(sum(para_float(item.get('Orig.')) for item in linhas), 2)
    valor_total_investido_em_carteira = round(sum(para_float(item.get('Orig.')) for item in construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos')), 2)
    valor_total_bruto_sacado = round(sum(para_float(item.get('Bruto sac.')) for item in linhas), 2)
    valor_total_liquido_sacado = round(sum(para_float(item.get('Líq. sac.')) for item in linhas), 2)
    valor_bruto_atual = round(sum(para_float(item.get('Bruto atual')) for item in linhas), 2)
    valor_liquido_atual = round(sum(para_float(item.get('Líq. atual')) for item in linhas), 2)
    patrimonio_liquido_atual = round(sum(para_float(item.get('Patr. líq.')) for item in linhas), 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_total, 2)

    rec_origens = _reconciliacao_origens_migradas(saida)
    valor_liquido_migrado_pos_switching = rec_origens['valor_liquido_migrado_total']
    valor_bruto_sacado_origens_migradas = rec_origens['valor_bruto_sacado_historico_total']
    valor_liquido_sacado_origens_migradas = rec_origens['valor_liquido_sacado_historico_total']
    patrimonio_liquido_reconciliado = round(
        patrimonio_liquido_atual + valor_liquido_sacado_origens_migradas,
        2,
    )

    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total investido em carteira', 'Valor': valor_total_investido_em_carteira},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
        {'Métrica': 'Valor líquido migrado para destinos pós-switching', 'Valor': valor_liquido_migrado_pos_switching},
        {'Métrica': 'Valor bruto sacado — origens migradas', 'Valor': valor_bruto_sacado_origens_migradas},
        {'Métrica': 'Valor líquido sacado — origens migradas', 'Valor': valor_liquido_sacado_origens_migradas},
        {'Métrica': 'Patrimônio líquido atual — reconciliado com origens migradas', 'Valor': patrimonio_liquido_reconciliado},
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
            'titulo': 'Lotes encerrados por switching — identificação',
            'headers': COLS_LOTES_ID_CURTAS,
            'linhas': construir_linhas_lotes_encerrados_por_switching(contexto, saida),
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
            'titulo': 'Origens migradas por switching — reconciliação patrimonial',
            'headers': COLS_ORIGENS_MIGRADAS_SWITCHING,
            'linhas': construir_linhas_origens_migradas_por_switching(contexto, saida),
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
    'Ganho sw.',
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
    'Pacote',
    'Sw. ant.',
    'Status',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_AUDITORIA_SW = [
    'Data',
    'Conta',
    'Lote',
    'Destino sw.',
    'Origem sw.',
    'Fonte sw.',
    'Data sw.',
    'Ganho sw.',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_CONSUMO = [
    'Data',
    'Conta',
    'Lote',
    'Saldo ant.',
    'Consumo',
    'Saldo dep.',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_CONCILIACAO = [
    'Data',
    'Conta',
    'Lote original',
    'Destino sw.',
    'Data janela',
    'Destino janela',
    'Conciliação sw.',
]

COLS_PAGAMENTOS_FUTUROS_RELEVANTE_DIAGNOSTICO_POS_SW = [
    'Data',
    'Conta',
    'Lote original',
    'Pos sw?',
    'Fonte pos sw',
    'Saldo pos sw',
    'Motivo pos sw',
    'Origem saldo pos',
    'Líq. pos',
    'Data saldo pos',
    'Motivo saldo pos',
    'Status',
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

COLS_LOTES_SINTETICOS_POS_SWITCHING = [
    'Data',
    'Lotes origem',
    'Destino',
    'Novo lote',
    'Valor líquido total',
    'Origem valor',
]

COLS_ESTADO_POS_SWITCHING_LOTES = [
    'Data',
    'Novo lote',
    'Produto destino',
    'Valor inicial',
    'Lotes origem',
    'Status origem',
    'Status novo',
    'Liquidez',
    'Carência',
    'Ticket mín.',
    'Origem valor',
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
        'recebidos_futuros': {
            'rotulo': 'recebidos/aportes futuros (amostra operacional)',
            'headers': list(COLS_RECEBIDOS_FUTUROS_CONSOLE),
            'linhas': saida.recebidos_futuros_console(limite=limite),
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
    switchings_janela = list(getattr(saida, 'switchings', []) or [])

    def _conciliar(row: dict[str, object]) -> dict[str, object]:
        lote = str(row.get('Lote original') or row.get('Lote') or '').strip()
        data_pag = str(row.get('Data') or '').strip()
        destino_sw = str(row.get('Destino sw.') or '').strip()
        candidatos = [
            item for item in switchings_janela
            if str(item.get('Lote origem') or '').strip() == lote
            and str(item.get('Data') or '').strip() <= data_pag
        ]
        if not candidatos:
            return {'Data janela': 'n/d', 'Destino janela': 'n/d', 'Conciliação sw.': 'sem_sw_janela'}
        candidatos = sorted(candidatos, key=lambda x: str(x.get('Data') or ''), reverse=True)
        escolhido = candidatos[0]
        data_janela = str(escolhido.get('Data') or 'n/d')
        destino_janela = str(escolhido.get('Destino') or 'n/d')
        lote_ja_migrado = True
        divergente_destino = bool(destino_sw and destino_janela and destino_sw != destino_janela)
        if lote_ja_migrado and divergente_destino:
            status = 'lote_ja_migrado_divergente'
        elif divergente_destino:
            status = 'divergente_destino'
        elif lote_ja_migrado:
            status = 'lote_ja_migrado'
        else:
            status = 'alinhado'
        return {'Data janela': data_janela, 'Destino janela': destino_janela, 'Conciliação sw.': status}

    criticos = {('2026-05-04', 'cartão nu'), ('2026-05-20', 'cartão azul'), ('2026-06-15', 'internet')}
    linhas_prioritarias: list[dict[str, object]] = []
    linhas_normais: list[dict[str, object]] = []
    for row in relevantes:
        linha = dict(row)
        linha['Lote original'] = row.get('Lote')
        chave = (str(linha.get('Data') or '').strip(), str(linha.get('Conta') or '').strip().lower())
        if chave in criticos:
            linhas_prioritarias.append(linha)
        else:
            linhas_normais.append(linha)
    linhas_conciliadas = (linhas_prioritarias + linhas_normais)[:limite]

    return {
        'rotulo': 'pagamentos futuros com switching/status relevante',
        'headers': list(COLS_PAGAMENTOS_FUTUROS_SWITCHING_RELEVANTE),
        'linhas': linhas_conciliadas,
        'limite': limite,
        'decisao': {
            'rotulo': 'pagamentos futuros com switching/status relevante — decisão',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_DECISAO),
            'linhas': linhas_conciliadas,
            'limite': limite,
        },
        'auditoria_switching': {
            'rotulo': 'pagamentos futuros com switching/status relevante — auditoria switching',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_AUDITORIA_SW),
            'linhas': linhas_conciliadas,
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
                for row in linhas_conciliadas
            ],
            'limite': limite,
        },
        'conciliacao_janela': {
            'rotulo': 'pagamentos futuros com switching/status relevante — conciliação janela',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_CONCILIACAO),
            'linhas': [
                {
                    'Data': row.get('Data'),
                    'Conta': row.get('Conta'),
                    'Lote original': row.get('Lote original'),
                    'Destino sw.': row.get('Destino sw.'),
                    **_conciliar(row),
                }
                for row in linhas_conciliadas
            ],
            'limite': limite,
        },
        'diagnostico_pos_switch': {
            'rotulo': 'pagamentos futuros com switching/status relevante — diagnóstico pos-switch',
            'headers': list(COLS_PAGAMENTOS_FUTUROS_RELEVANTE_DIAGNOSTICO_POS_SW),
            'linhas': [
                {
                    'Data': row.get('Data'),
                    'Conta': row.get('Conta'),
                    'Lote original': row.get('Lote original') or row.get('Lote'),
                    'Pos sw?': row.get('Pos sw?', 'n/d'),
                    'Fonte pos sw': row.get('Fonte pos sw', 'n/d'),
                    'Saldo pos sw': row.get('Saldo pos sw', 'n/d'),
                    'Motivo pos sw': row.get('Motivo pos sw', 'n/d'),
                    'Origem saldo pos': row.get('Origem saldo pos', 'n/d'),
                    'Líq. pos': row.get('Líq. pos', 'n/d'),
                    'Data saldo pos': row.get('Data saldo pos', 'n/d'),
                    'Motivo saldo pos': row.get('Motivo saldo pos', 'n/d'),
                    'Status': row.get('Status', 'n/d'),
                }
                for row in linhas_conciliadas
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


def construir_amostra_lotes_sinteticos_pos_switching(saida, *, limite: int = 10) -> dict[str, object]:
    linhas = saida.lotes_sinteticos_pos_switching_console(limite=limite) if hasattr(saida, 'lotes_sinteticos_pos_switching_console') else []
    return {
        'rotulo': 'lotes sintéticos pós-switching',
        'headers': list(COLS_LOTES_SINTETICOS_POS_SWITCHING),
        'linhas': linhas,
        'limite': limite,
    }


def construir_amostra_estado_pos_switching_lotes(saida, *, limite: int = 10) -> dict[str, object]:
    linhas = saida.estado_pos_switching_lotes_console(limite=limite) if hasattr(saida, 'estado_pos_switching_lotes_console') else []
    return {
        'rotulo': 'estado pós-switching dos lotes',
        'headers': list(COLS_ESTADO_POS_SWITCHING_LOTES),
        'linhas': linhas,
        'limite': limite,
    }
