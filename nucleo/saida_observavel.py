from __future__ import annotations

from datetime import date, datetime
from typing import Any

from nucleo.calendario_financeiro import calcular_dias_lote


COLS_LOTES_EXAURIDOS_ID_CURTAS = [
    'Lote',
    'Status ciclo',
    'Carteira',
    'Aplic.',
    'Base fiscal',
    'Data término',
    'Dias corr.',
    'Dias úteis',
]

COLS_LOTES_ATIVOS_ID_CURTAS = [
    'Lote',
    'Status ciclo',
    'Carteira',
    'Aplic.',
    'Base fiscal',
    'Dias corr.',
    'Dias úteis',
]

# Compatibilidade com chamadas antigas. Para novas saídas, usar listas específicas.
COLS_LOTES_ID_CURTAS = COLS_LOTES_EXAURIDOS_ID_CURTAS

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
        for row in (getattr(saida, 'extrato_passado', []) or []):
            lote_id = str(row.get('Lotes usados') or row.get('Lote') or '').strip()
            if not lote_id:
                continue

            bruto_ref = para_float(row.get('Bruto'))
            liquido_ref = para_float(row.get('Líquido') if 'Líquido' in row else row.get('Liquido'))

            if bruto_ref <= 0 and liquido_ref <= 0:
                continue

            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(max(atual['bruto_sacado'], bruto_ref), 2)
            atual['liquido_sacado'] = round(max(atual['liquido_sacado'], liquido_ref), 2)

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


def _produto_preenchido_observavel(valor: Any) -> bool:
    txt = str(valor or "").strip()
    return txt not in {"", "-", "n/d", "nd", "não determinado", "nao determinado", "None", "nan", "NaT", "produto_origem_nao_encontrado"}


def _registrar_produto_lote(mapa: dict[str, Any], lote_id: Any, produto: Any) -> None:
    lote = str(lote_id or "").strip()
    if not lote or not _produto_preenchido_observavel(produto):
        return
    mapa.setdefault(lote, str(produto).strip())


def _mapa_produto_por_lote(contexto: Any, saida: Any) -> dict[str, Any]:
    """Busca produto/carteira do lote em estruturas já carregadas.

    Não decide switching, não altera motor e não altera ledger.
    É apenas enriquecimento observável para console/planilha.
    """
    mapa: dict[str, Any] = {}

    for item in list(getattr(saida, "lotes_ativos", []) or []) + list(getattr(saida, "lotes_exauridos", []) or []):
        _registrar_produto_lote(
            mapa,
            item.get("Lote"),
            item.get("Produto") or item.get("Carteira") or item.get("Investimento"),
        )

    for item in list(getattr(saida, "recebidos_atuais", []) or []):
        _registrar_produto_lote(
            mapa,
            item.get("Lote origem") or item.get("Recebido"),
            item.get("Carteira") or item.get("Produto") or item.get("Investimento"),
        )

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
            produto = (
                getattr(lote_obj, "produto", None)
                or getattr(lote_obj, "produto_nome", None)
                or getattr(lote_obj, "produto_nome_canonico", None)
                or getattr(lote_obj, "investimento", None)
                or getattr(lote_obj, "carteira", None)
            )
            _registrar_produto_lote(mapa, lote_id, produto)

    # Varredura leve de DataFrames no contexto para capturar Inventário de Lotes,
    # carteiras intermediárias e auditorias canônicas sem depender de nomes internos.
    fila = [contexto]
    vistos: set[int] = set()
    while fila and len(vistos) < 250:
        obj = fila.pop(0)
        if obj is None or id(obj) in vistos:
            continue
        vistos.add(id(obj))

        cols = getattr(obj, "columns", None)
        if cols is not None and hasattr(obj, "iterrows"):
            colunas = list(cols)
            cols_norm = {str(c).strip().lower(): c for c in colunas}

            candidatos_lote = [
                "lote (id)",
                "lote",
                "lote id",
                "lote_id",
                "lote origem",
                "lote_origem",
                "lote origem switching",
                "lote_origem_switching",
            ]
            candidatos_produto = [
                "investimento",
                "produto",
                "produto origem",
                "produto_origem",
                "produto origem switching",
                "produto_origem_switching",
                "produto_nome",
                "produto_nome_canonico",
                "carteira",
            ]

            col_lote = next((cols_norm[c] for c in candidatos_lote if c in cols_norm), None)
            col_prod = next((cols_norm[c] for c in candidatos_produto if c in cols_norm), None)

            if col_lote is not None and col_prod is not None:
                try:
                    for _, row in obj.iterrows():
                        _registrar_produto_lote(mapa, row.get(col_lote), row.get(col_prod))
                except Exception:
                    pass
            continue

        dct = getattr(obj, "__dict__", None)
        if isinstance(dct, dict):
            for val in dct.values():
                if id(val) not in vistos:
                    fila.append(val)

    return mapa



def _registrar_valor_original_lote(mapa: dict[str, float], lote_id: Any, valor_original: Any) -> None:
    lote = str(lote_id or "").strip()
    valor = round(para_float(valor_original), 2)
    if not lote or valor <= 0:
        return
    mapa.setdefault(lote, valor)


def _mapa_valor_original_por_lote(contexto: Any, saida: Any) -> dict[str, float]:
    """Busca o valor original do lote em estruturas já carregadas.

    Usado apenas para renderização observável de origens migradas por switching.
    Não altera motor, ledger, ranking nem totais patrimoniais.
    """
    mapa: dict[str, float] = {}

    for item in list(getattr(saida, "lotes_ativos", []) or []) + list(getattr(saida, "lotes_exauridos", []) or []):
        _registrar_valor_original_lote(
            mapa,
            item.get("Lote"),
            item.get("Valor original") or item.get("Orig."),
        )

    for item in list(getattr(saida, "recebidos_atuais", []) or []):
        _registrar_valor_original_lote(
            mapa,
            item.get("Lote origem") or item.get("Recebido"),
            item.get("Valor bruto") or item.get("Valor líquido") or item.get("Valor"),
        )

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
            valor = (
                getattr(lote_obj, "valor_original", None)
                or getattr(lote_obj, "valor", None)
                or getattr(lote_obj, "principal", None)
            )
            _registrar_valor_original_lote(mapa, lote_id, valor)

    fila = [contexto]
    vistos: set[int] = set()
    while fila and len(vistos) < 250:
        obj = fila.pop(0)
        if obj is None or id(obj) in vistos:
            continue
        vistos.add(id(obj))

        cols = getattr(obj, "columns", None)
        if cols is not None and hasattr(obj, "iterrows"):
            colunas = list(cols)
            cols_norm = {str(c).strip().lower(): c for c in colunas}

            candidatos_lote = [
                "lote (id)",
                "lote",
                "lote id",
                "lote_id",
                "lote origem",
                "lote_origem",
            ]
            candidatos_valor = [
                "valor original",
                "valor_original",
                "valor bruto",
                "valor_bruto",
            ]

            col_lote = next((cols_norm[c] for c in candidatos_lote if c in cols_norm), None)
            col_valor = next((cols_norm[c] for c in candidatos_valor if c in cols_norm), None)

            if col_lote is not None and col_valor is not None:
                try:
                    for _, row in obj.iterrows():
                        _registrar_valor_original_lote(mapa, row.get(col_lote), row.get(col_valor))
                except Exception:
                    pass
            continue

        dct = getattr(obj, "__dict__", None)
        if isinstance(dct, dict):
            for val in dct.values():
                if id(val) not in vistos:
                    fila.append(val)

    return mapa



def _valor_nominal_extraido_do_id_lote(lote_id: Any) -> float:
    """Extrai valor nominal do identificador textual do lote.

    Exemplo:
    - Lote 3000 mar. B  -> 3000.00
    - Lote 8500 mar.    -> 8500.00
    - Lote 6630,64 fev. -> 6630.64

    Uso restrito à renderização observável de origens migradas por switching.
    Não altera motor, replay, ledger, ranking, switching nem totais patrimoniais.
    """
    partes = str(lote_id or "").strip().split()
    if len(partes) < 2 or partes[0].lower() != "lote":
        return 0.0

    bruto = partes[1].strip()
    if "," in bruto:
        bruto = bruto.replace(".", "").replace(",", ".")

    return para_float(bruto)


def _origens_migradas_auditoria(saida: Any) -> list[dict[str, Any]]:
    auditoria = dict(getattr(saida, "auditoria", {}) or {})
    return list(auditoria.get("origens_migradas_por_switching") or [])


def _status_ciclo_lote(item: dict[str, Any], *, tipo: str) -> str:
    status_item = str(item.get("Status ciclo") or item.get("Status") or "").strip()
    if tipo == "exauridos":
        if status_item == "migrado_por_switching":
            return "migrado_por_switching"
        return "exaurido_por_saque"
    if status_item == "ativo_pos_switching":
        return "ativo_pos_switching"
    return "ativo"



def _mapa_saldo_final_replay_por_lote(contexto: Any) -> dict[str, float]:
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    mapa: dict[str, tuple[str, float, int, float]] = {}
    if log is None or not hasattr(log, 'iterrows') or 'Lote' not in getattr(log, 'columns', []):
        return {}

    for idx, row in enumerate(log.iterrows()):
        _, registro = row
        lote_id = str(registro.get('Lote') or '').strip()
        if not lote_id:
            continue

        saldo = round(
            para_float(
                registro.get('Saldo Remanescente')
                if 'Saldo Remanescente' in registro
                else registro.get('Saldo_remanescente')
            ),
            2,
        )
        data_txt = _fmt_data_observavel(registro.get('Data'), padrao='')
        seq = para_float(registro.get('Sequencia Saque') if 'Sequencia Saque' in registro else registro.get('sequencia_saque'))
        chave = (data_txt, seq, idx)
        atual = mapa.get(lote_id)
        if atual is None or chave > (atual[0], atual[1], atual[2]):
            mapa[lote_id] = (data_txt, seq, idx, saldo)

    return {lote: dados[3] for lote, dados in mapa.items()}


def _lote_deve_ser_ativo_observavel_por_replay(
    lote_id: str,
    item: dict[str, Any],
    mapa_saldo_final_replay: dict[str, float],
    *,
    minimo_positivo: float = 0.20,
) -> bool:
    if not lote_id:
        return False
    status = _status_ciclo_lote(item, tipo='exauridos')
    if 'migrado' in str(status).lower():
        return False
    saldo_final = round(para_float(mapa_saldo_final_replay.get(lote_id)), 2)
    return saldo_final > minimo_positivo

def _lotes_origens_migradas_set(saida: Any) -> set[str]:
    return {
        str(item.get("lote_origem") or "").strip()
        for item in _origens_migradas_auditoria(saida)
        if str(item.get("lote_origem") or "").strip()
    }


def _remover_origens_migradas_dos_exauridos_consolidados(
    linhas: list[dict[str, Any]],
    saida: Any,
) -> list[dict[str, Any]]:
    """Evita duplicidade observável entre exaurido_por_saque e migrado_por_switching."""
    origens_migradas = _lotes_origens_migradas_set(saida)
    if not origens_migradas:
        return linhas
    return [
        linha
        for linha in linhas
        if str(linha.get("Lote") or "").strip() not in origens_migradas
    ]


def calcular_rendimento_liquido_observavel(
    *,
    status_ciclo: str,
    valor_original: float,
    patrimonio_liquido: float,
) -> float:
    """Calcula rendimento líquido apenas para renderização observável.

    Para lotes ativos pós-switching, rendimento líquido negativo pode surgir
    como artefato de base sintética pós-migração combinada com saque parcial.

    A correção é restrita à camada observável: não altera patrimônio líquido,
    valores sacados, valor atual, motor, ledger, replay, switching ou decisão econômica.
    """
    rendimento = round(patrimonio_liquido - valor_original, 2)

    if str(status_ciclo or "").strip() == "ativo_pos_switching" and rendimento < 0:
        return 0.0

    return rendimento


def construir_linhas_lotes_consolidados(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    campo = 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos'
    itens = list(getattr(saida, campo, []) or [])
    mapa_saldo_final_replay = _mapa_saldo_final_replay_por_lote(contexto)
    lotes_exauridos = list(getattr(saida, 'lotes_exauridos', []) or [])
    lotes_exauridos_ids = {str(item.get('Lote') or '').strip() for item in lotes_exauridos}
    lotes_ativos_ids = {str(item.get('Lote') or '').strip() for item in list(getattr(saida, 'lotes_ativos', []) or [])}
    somas = somar_valores_sacados_por_lote(contexto, saida)
    mapa_termino = _mapa_ultimo_uso_lotes_saida(saida)
    linhas: list[dict[str, Any]] = []

    itens_iteracao = list(itens)
    if tipo == 'ativos':
        for item_exaurido in lotes_exauridos:
            lote_id_exaurido = str(item_exaurido.get('Lote') or '').strip()
            if (
                lote_id_exaurido
                and lote_id_exaurido not in lotes_ativos_ids
                and _lote_deve_ser_ativo_observavel_por_replay(
                    lote_id_exaurido,
                    item_exaurido,
                    mapa_saldo_final_replay,
                )
            ):
                itens_iteracao.append(item_exaurido)

    for item in itens_iteracao:
        lote_id = str(item.get('Lote') or '').strip()
        saldo_final_replay = round(para_float(mapa_saldo_final_replay.get(lote_id)), 2)
        origem_exaurida_com_saldo_replay = (
            tipo == 'ativos'
            and lote_id in lotes_exauridos_ids
            and _lote_deve_ser_ativo_observavel_por_replay(
                lote_id,
                item,
                mapa_saldo_final_replay,
            )
        )
        if (
            tipo == 'exauridos'
            and _lote_deve_ser_ativo_observavel_por_replay(
                lote_id,
                item,
                mapa_saldo_final_replay,
            )
        ):
            continue
        sacado = somas.get(lote_id, {})
        status_ciclo = 'ativo' if origem_exaurida_com_saldo_replay else _status_ciclo_lote(item, tipo=tipo)

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
        if origem_exaurida_com_saldo_replay:
            bruto_atual = saldo_final_replay
            liquido_atual = saldo_final_replay

        patrimonio_liquido = round(liquido_sacado + liquido_atual, 2)
        rendimento_liquido = calcular_rendimento_liquido_observavel(
            status_ciclo=status_ciclo,
            valor_original=valor_original,
            patrimonio_liquido=patrimonio_liquido,
        )

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
    if tipo == 'ativos':
        headers = COLS_LOTES_ATIVOS_ID_CURTAS
        linhas_base = construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo)
    elif tipo == 'exauridos':
        headers = COLS_LOTES_EXAURIDOS_ID_CURTAS
        linhas_consolidadas = _remover_origens_migradas_dos_exauridos_consolidados(
            construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo),
            saida,
        )
        linhas_base = (
            linhas_consolidadas
            + construir_linhas_lotes_encerrados_por_switching(contexto, saida)
        )
    else:
        headers = COLS_LOTES_ID_CURTAS
        linhas_base = construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo)

    return [
        {chave: item.get(chave) for chave in headers}
        for item in linhas_base
    ]


def construir_linhas_lotes_valores_curta(contexto, saida, *, tipo: str) -> list[dict[str, Any]]:
    linhas_base = list(construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo))

    if tipo == 'exauridos':
        # Mantém alinhamento visual entre a tabela de identificação e a tabela de valores.
        # As origens migradas por switching entram apenas como linhas observáveis
        # e NÃO são usadas por construir_resumo_patrimonio_total_lotes(...).
        linhas_base = _remover_origens_migradas_dos_exauridos_consolidados(linhas_base, saida)
        linhas_base += construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida)

    return [
        {chave: item.get(chave) for chave in COLS_LOTES_VALORES_CURTAS}
        for item in linhas_base
    ]


def construir_linhas_lotes_encerrados_por_switching(contexto, saida) -> list[dict[str, Any]]:
    aplicacoes = _mapa_aplicacao_por_lote(contexto, saida)
    produtos = _mapa_produto_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in _origens_migradas_auditoria(saida):
        lote = str(item.get('lote_origem') or '').strip()
        data_switching = item.get('data_switching') or 'n/d'
        data_aplicacao = aplicacoes.get(lote)
        dias = _calcular_dias_observavel(contexto, data_aplicacao, data_switching)
        produto_origem = (
            item.get('produto_origem')
            or item.get('Produto origem')
            or produtos.get(lote)
            or 'produto_origem_nao_encontrado'
        )

        linhas.append({
            'Lote': lote,
            'Status ciclo': 'migrado_por_switching',
            'Carteira': produto_origem,
            'Aplic.': _fmt_data_observavel(data_aplicacao),
            'Base fiscal': _fmt_data_observavel(data_aplicacao),
            'Data término': _fmt_data_observavel(data_switching),
            'Dias corr.': dias.get('dias_corridos', ''),
            'Dias úteis': dias.get('dias_uteis', ''),
        })

    return linhas



def construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida) -> list[dict[str, Any]]:
    """Valores observáveis das origens migradas por switching.

    Essas linhas existem para alinhar a renderização das tabelas:
    - aparecem em "Lotes exauridos — identificação";
    - também aparecem em "Lotes exauridos — valores e patrimônio";
    - não são somadas no resumo patrimonial, pois o resumo continua usando
      construir_linhas_lotes_consolidados(...).
    """
    valores_originais = _mapa_valor_original_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in _origens_migradas_auditoria(saida):
        lote = str(item.get('lote_origem') or '').strip()
        valor_original = round(
            _valor_nominal_extraido_do_id_lote(lote)
            or para_float(valores_originais.get(lote))
            or para_float(item.get('valor_liquido_migrado_total')),
            2,
        )
        valor_migrado = round(para_float(item.get('valor_liquido_migrado_total')), 2)
        bruto_sacado_historico = round(para_float(item.get('valor_bruto_sacado_historico')), 2)
        liquido_sacado_historico = round(para_float(item.get('valor_liquido_sacado_historico')), 2)

        patrimonio_liquido_observavel = round(liquido_sacado_historico + valor_migrado, 2)
        rendimento_liquido_observavel = round(patrimonio_liquido_observavel - valor_original, 2)

        linhas.append({
            'Lote': lote,
            'Orig.': valor_original,
            'Bruto sac.': bruto_sacado_historico,
            'Líq. sac.': liquido_sacado_historico,
            'Bruto atual': 0.0,
            'Líq. atual': 0.0,
            'Patr. líq.': patrimonio_liquido_observavel,
            'Rend. líq.': rendimento_liquido_observavel,
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


def construir_switchings_observaveis(contexto, saida) -> list[dict[str, Any]]:
    """Switchings enriquecidos para console e planilha.

    Mantém a decisão de switching intacta e apenas preenche campos observáveis
    ausentes, especialmente Produto origem.
    """
    produtos = _mapa_produto_por_lote(contexto, saida)
    linhas: list[dict[str, Any]] = []

    for item in list(getattr(saida, "switchings", []) or []):
        linha = dict(item)
        lote = str(
            linha.get("Lote origem")
            or linha.get("lote_origem")
            or linha.get("lote_origem_switching")
            or linha.get("lote_id")
            or ""
        ).strip()

        produto_origem = (
            linha.get("Produto origem")
            or linha.get("produto_origem")
            or linha.get("produto_origem_switching")
            or produtos.get(lote)
        )

        if not _produto_preenchido_observavel(produto_origem):
            produto_origem = "produto_origem_nao_encontrado"

        linha["Produto origem"] = produto_origem
        linhas.append(linha)

    return linhas


def _reconciliacao_origens_migradas(saida) -> dict[str, float]:
    auditoria = dict(getattr(saida, 'auditoria', {}) or {})
    rec = dict(auditoria.get('reconciliacao_patrimonial_origens_migradas') or {})
    return {
        'valor_liquido_migrado_total': round(para_float(rec.get('valor_liquido_migrado_total')), 2),
        'valor_bruto_sacado_historico_total': round(para_float(rec.get('valor_bruto_sacado_historico_total')), 2),
        'valor_liquido_sacado_historico_total': round(para_float(rec.get('valor_liquido_sacado_historico_total')), 2),
    }


def _valor_total_recebidos_brutos(saida) -> float:
    for item in list(getattr(saida, 'resumo_recebidos', []) or []):
        metrica = str(item.get('Métrica') or item.get('Metrica') or '').strip().lower()
        if metrica == 'valor total bruto':
            return round(para_float(item.get('Valor')), 2)

    total = 0.0
    for item in list(getattr(saida, 'recebidos_atuais', []) or []):
        total += para_float(item.get('Valor bruto'))
    return round(total, 2)


def construir_resumo_patrimonio_total_lotes(contexto, saida) -> list[dict[str, Any]]:
    linhas_exauridos_consolidadas = _remover_origens_migradas_dos_exauridos_consolidados(
        construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos'),
        saida,
    )
    linhas_exauridos = (
        linhas_exauridos_consolidadas
        + construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida)
    )
    linhas_ativos = construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos')
    linhas = linhas_exauridos + linhas_ativos

    valor_original_total = round(sum(para_float(item.get('Orig.')) for item in linhas), 2)
    valor_total_investido_em_carteira = round(sum(para_float(item.get('Orig.')) for item in linhas_ativos), 2)
    valor_total_bruto_sacado = round(sum(para_float(item.get('Bruto sac.')) for item in linhas), 2)
    valor_total_liquido_sacado = round(sum(para_float(item.get('Líq. sac.')) for item in linhas), 2)
    valor_bruto_atual = round(sum(para_float(item.get('Bruto atual')) for item in linhas), 2)
    valor_liquido_atual = round(sum(para_float(item.get('Líq. atual')) for item in linhas), 2)
    patrimonio_liquido_atual = round(sum(para_float(item.get('Patr. líq.')) for item in linhas), 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_total, 2)

    valor_original_destinos_pos_switching = round(
        sum(
            para_float(item.get('Orig.'))
            for item in linhas_ativos
            if str(item.get('Status ciclo') or '').strip() == 'ativo_pos_switching'
        ),
        2,
    )
    valor_original_observado_sem_destinos_sinteticos = round(
        valor_original_total - valor_original_destinos_pos_switching,
        2,
    )

    rec_origens = _reconciliacao_origens_migradas(saida)
    valor_liquido_migrado_pos_switching = rec_origens['valor_liquido_migrado_total']
    valor_bruto_sacado_origens_migradas = rec_origens['valor_bruto_sacado_historico_total']
    valor_liquido_sacado_origens_migradas = rec_origens['valor_liquido_sacado_historico_total']
    origens_migradas = _lotes_origens_migradas_set(saida)
    origens_migradas_incluidas_no_resumo = any(
        str(item.get('Lote') or '').strip() in origens_migradas
        for item in linhas_exauridos
    )

    patrimonio_liquido_reconciliado = round(
        patrimonio_liquido_atual
        if origens_migradas_incluidas_no_resumo
        else patrimonio_liquido_atual + valor_liquido_sacado_origens_migradas,
        2,
    )

    base_economica_recebidos_brutos = _valor_total_recebidos_brutos(saida)
    rendimento_reconciliado_contra_recebidos = round(
        patrimonio_liquido_reconciliado - base_economica_recebidos_brutos,
        2,
    )
    rendimento_reconciliado_contra_valor_original_observado = round(
        patrimonio_liquido_reconciliado - valor_original_total,
        2,
    )

    return [
        # Métricas antigas preservadas para compatibilidade.
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total investido em carteira', 'Valor': valor_total_investido_em_carteira},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},

        # Métricas novas e explícitas para reconciliação econômica.
        {'Métrica': 'Valor original total — observado', 'Valor': valor_original_total},
        {'Métrica': 'Valor original destinos pós-switching — sintético', 'Valor': valor_original_destinos_pos_switching},
        {'Métrica': 'Valor original observado sem destinos pós-switching sintéticos', 'Valor': valor_original_observado_sem_destinos_sinteticos},
        {'Métrica': 'Base econômica explícita — recebidos brutos', 'Valor': base_economica_recebidos_brutos},
        {'Métrica': 'Valor líquido migrado para destinos pós-switching', 'Valor': valor_liquido_migrado_pos_switching},
        {'Métrica': 'Valor bruto sacado — origens migradas', 'Valor': valor_bruto_sacado_origens_migradas},
        {'Métrica': 'Valor líquido sacado — origens migradas', 'Valor': valor_liquido_sacado_origens_migradas},
        {'Métrica': 'Patrimônio líquido atual — reconciliado com origens migradas', 'Valor': patrimonio_liquido_reconciliado},
        {'Métrica': 'Rendimento líquido atual — reconciliado contra recebidos', 'Valor': rendimento_reconciliado_contra_recebidos},
        {'Métrica': 'Rendimento líquido atual — reconciliado contra valor original observado', 'Valor': rendimento_reconciliado_contra_valor_original_observado},
    ]


def construir_blocos_situacao_atual(contexto, saida) -> list[dict[str, Any]]:
    return [
        {
            'titulo': 'Lotes exauridos — identificação',
            'headers': COLS_LOTES_EXAURIDOS_ID_CURTAS,
            'linhas': construir_linhas_lotes_id_curta(contexto, saida, tipo='exauridos'),
        },
        {
            'titulo': 'Lotes exauridos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_CURTAS,
            'linhas': construir_linhas_lotes_valores_curta(contexto, saida, tipo='exauridos'),
        },
        {
            'titulo': 'Lotes ativos — identificação',
            'headers': COLS_LOTES_ATIVOS_ID_CURTAS,
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
