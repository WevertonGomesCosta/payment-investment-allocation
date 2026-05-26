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


def _valores_sacados_por_lote_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[str, dict[str, float]]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    out: dict[str, dict[str, float]] = {}
    for lote_id, dados in (getattr(pacote, "valores_sacados_por_lote", {}) or {}).items():
        bruto = (dados or {}).get("bruto_sacado")
        liquido = (dados or {}).get("liquido_sacado")
        if bruto is None and liquido is None and "valor_sacado_total" in (dados or {}):
            liquido = (dados or {}).get("valor_sacado_total")
        out[str(lote_id)] = {"bruto_sacado": round(para_float(bruto), 2), "liquido_sacado": round(para_float(liquido), 2)}

    pagamentos = list((getattr(pacote, "pagamentos_replay_por_chave", {}) or {}).values())
    somas_pag: dict[str, dict[str, float]] = {}
    for row in pagamentos:
        lote_id = str(row.get("Lote") or row.get("Lotes usados") or "").strip()
        if not lote_id:
            continue
        acc = somas_pag.setdefault(lote_id, {"bruto": 0.0, "liq": 0.0})
        acc["bruto"] = round(acc["bruto"] + para_float(row.get("Bruto")), 2)
        liq = row.get("Líquido") if "Líquido" in row else row.get("Liquido")
        acc["liq"] = round(acc["liq"] + para_float(liq), 2)

    for lote_id, soma in somas_pag.items():
        cur = out.setdefault(lote_id, {"bruto_sacado": 0.0, "liquido_sacado": 0.0})
        if cur["bruto_sacado"] <= 0:
            cur["bruto_sacado"] = round(soma["bruto"], 2)
        if cur["liquido_sacado"] <= 0:
            cur["liquido_sacado"] = round(soma["liq"], 2)
    return out







def _norm_lote_chave(valor: Any) -> str:
    return str(valor or "").strip().lower().replace(".", "")


def _lookup_por_lote_normalizado(mapa: dict[str, Any], lote_id: Any, default: Any) -> Any:
    chave = _norm_lote_chave(lote_id)
    if not chave:
        return default
    for k, v in (mapa or {}).items():
        if _norm_lote_chave(k) == chave:
            return v
    return default

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


def _aplicacoes_por_lote_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[str, Any]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    return dict(getattr(pacote, "aplicacoes_por_lote", {}) or {})


def _produto_preenchido_observavel(valor: Any) -> bool:
    txt = str(valor or "").strip()
    return txt not in {"", "-", "n/d", "nd", "não determinado", "nao determinado", "None", "nan", "NaT", "produto_origem_nao_encontrado"}


def _registrar_produto_lote(mapa: dict[str, Any], lote_id: Any, produto: Any) -> None:
    lote = str(lote_id or "").strip()
    if not lote or not _produto_preenchido_observavel(produto):
        return
    mapa.setdefault(lote, str(produto).strip())


def _produtos_por_lote_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[str, Any]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    return dict(getattr(pacote, "produtos_por_lote", {}) or {})


def _registrar_valor_original_lote(mapa: dict[str, float], lote_id: Any, valor_original: Any) -> None:
    lote = str(lote_id or "").strip()
    valor = round(para_float(valor_original), 2)
    if not lote or valor <= 0:
        return
    mapa.setdefault(lote, valor)


def _valores_originais_por_lote_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[str, float]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    return dict(getattr(pacote, "valores_originais_por_lote", {}) or {})




def _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal: Any) -> Any:
    if pacote_saida_observavel_temporal is None:
        raise RuntimeError("saida_observavel_requer_pacote_saida_observavel_temporal_na_V4W")
    return pacote_saida_observavel_temporal

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



def _saldos_finais_replay_por_lote_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[str, float]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    return dict(getattr(pacote, "saldos_finais_replay_por_lote", {}) or {})


def _saldos_finais_por_lote_de_linhas(linhas: list[dict[str, Any]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in linhas:
        lote = str(item.get("Lote") or "").strip()
        if not lote:
            continue
        out[lote] = round(para_float(item.get("Líq. atual") or item.get("Líquido") or 0.0), 2)
    return out


def _lotes_origens_migradas_set(saida: Any) -> set[str]:
    return {
        str(item.get("lote_origem") or "").strip()
        for item in _origens_migradas_auditoria(saida)
        if str(item.get("lote_origem") or "").strip()
    }




def _mapa_switching_por_origem(estado_temporal_inicial: Any | None) -> dict[str, dict[str, Any]]:
    mapa = {}
    if estado_temporal_inicial is None:
        return mapa
    for ev in list(getattr(estado_temporal_inicial, 'switching_temporal_realizado', []) or []):
        origem = str(ev.get('lote_origem') or '').strip()
        if origem:
            mapa[origem] = ev
    return mapa

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




def _valores_sacados_por_lote_bootstrap(saida: Any) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in list(getattr(saida, "extrato_passado", []) or []):
        lote = str(row.get("Lotes usados") or row.get("Lote") or "").strip()
        if not lote:
            continue
        bruto = round(para_float(row.get("Bruto")), 2)
        liq = round(para_float(row.get("Líquido") if "Líquido" in row else row.get("Liquido")), 2)
        cur = out.setdefault(lote, {"bruto_sacado": 0.0, "liquido_sacado": 0.0})
        cur["bruto_sacado"] = round(cur["bruto_sacado"] + bruto, 2)
        cur["liquido_sacado"] = round(cur["liquido_sacado"] + liq, 2)
    return out


def _saldos_finais_por_lote_bootstrap(saida: Any) -> dict[str, float]:
    acc: dict[str, tuple[str, float, int]] = {}
    for i, row in enumerate(list(getattr(saida, "extrato_passado", []) or [])):
        lote = str(row.get("Lotes usados") or row.get("Lote") or "").strip()
        if not lote:
            continue
        data_txt = _fmt_data_observavel(row.get("Data"), padrao="")
        seq = para_float(row.get("Sequencia Saque") if "Sequencia Saque" in row else row.get("sequencia_saque"))
        saldo = round(para_float(row.get("Saldo Remanescente") if "Saldo Remanescente" in row else row.get("Saldo remanescente")), 2)
        key = (data_txt, seq, i)
        prev = acc.get(lote)
        if prev is None or key > (prev[0], prev[1], prev[2]):
            acc[lote] = (data_txt, seq, i, saldo)
    return {k: v[3] for k, v in acc.items()}


def construir_linhas_lotes_consolidados(contexto, saida, *, tipo: str, pacote_saida_observavel_temporal: Any | None = None, modo_bootstrap_pacote: bool = False) -> list[dict[str, Any]]:
    campo = 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos'
    itens = list(getattr(saida, campo, []) or [])
    lotes_exauridos = list(getattr(saida, 'lotes_exauridos', []) or [])
    if pacote_saida_observavel_temporal is None:
        if not modo_bootstrap_pacote:
            _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
        mapa_saldo_final_replay = _saldos_finais_por_lote_bootstrap(saida)
        somas = _valores_sacados_por_lote_bootstrap(saida)
    else:
        mapa_saldo_final_replay = _saldos_finais_replay_por_lote_do_pacote(pacote_saida_observavel_temporal)
        somas = _valores_sacados_por_lote_do_pacote(pacote_saida_observavel_temporal)
    lotes_exauridos_ids = {str(item.get('Lote') or '').strip() for item in lotes_exauridos}
    lotes_ativos_ids = {str(item.get('Lote') or '').strip() for item in list(getattr(saida, 'lotes_ativos', []) or [])}
    mapa_termino = _mapa_ultimo_uso_lotes_saida(saida)
    linhas: list[dict[str, Any]] = []

    itens_iteracao = list(itens)
    if tipo == 'ativos':
        for item_exaurido in lotes_exauridos:
            lote_id_exaurido = str(item_exaurido.get('Lote') or '').strip()
            if (
                lote_id_exaurido
                and lote_id_exaurido not in lotes_ativos_ids
                and round(para_float(_lookup_por_lote_normalizado(mapa_saldo_final_replay, lote_id_exaurido, 0.0)), 2) > 0.20
                and "migrado" not in str(_status_ciclo_lote(item_exaurido, tipo="exauridos")).lower()
            ):
                itens_iteracao.append(item_exaurido)

    for item in itens_iteracao:
        lote_id = str(item.get('Lote') or '').strip()
        saldo_final_replay = round(para_float(_lookup_por_lote_normalizado(mapa_saldo_final_replay, lote_id, 0.0)), 2)
        origem_exaurida_com_saldo_replay = (
            tipo == 'ativos'
            and lote_id in lotes_exauridos_ids
            and lote_id not in lotes_ativos_ids
            and round(para_float(_lookup_por_lote_normalizado(mapa_saldo_final_replay, lote_id, 0.0)), 2) > 0.20
            and "migrado" not in str(_status_ciclo_lote(item, tipo="exauridos")).lower()
        )
        if (
            tipo == 'exauridos'
            and round(para_float(_lookup_por_lote_normalizado(mapa_saldo_final_replay, lote_id, 0.0)), 2) > 0.20
            and "migrado" not in str(_status_ciclo_lote(item, tipo="exauridos")).lower()
        ):
            continue
        sacado = _lookup_por_lote_normalizado(somas, lote_id, {})
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
        if tipo == 'ativos' and saldo_final_replay > 0:
            bruto_atual = max(bruto_atual, saldo_final_replay)
            liquido_atual = max(liquido_atual, saldo_final_replay)
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


def construir_linhas_lotes_id_curta(contexto, saida, *, tipo: str, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    if tipo == 'ativos':
        headers = COLS_LOTES_ATIVOS_ID_CURTAS
        linhas_base = construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)
    elif tipo == 'exauridos':
        headers = COLS_LOTES_EXAURIDOS_ID_CURTAS
        linhas_consolidadas = _remover_origens_migradas_dos_exauridos_consolidados(
            construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
            saida,
        )
        linhas_base = (
            linhas_consolidadas
            + construir_linhas_lotes_encerrados_por_switching(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)
        )
    else:
        headers = COLS_LOTES_ID_CURTAS
        linhas_base = construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)

    return [
        {chave: item.get(chave) for chave in headers}
        for item in linhas_base
    ]


def construir_linhas_lotes_valores_curta(contexto, saida, *, tipo: str, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    linhas_base = list(construir_linhas_lotes_consolidados(contexto, saida, tipo=tipo, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal))

    if tipo == 'exauridos':
        # Mantém alinhamento visual entre a tabela de identificação e a tabela de valores.
        # As origens migradas por switching entram apenas como linhas observáveis
        # e NÃO são usadas por construir_resumo_patrimonio_total_lotes(...).
        linhas_base = _remover_origens_migradas_dos_exauridos_consolidados(linhas_base, saida)
        linhas_base += construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)

    return [
        {chave: item.get(chave) for chave in COLS_LOTES_VALORES_CURTAS}
        for item in linhas_base
    ]




def _mapa_economico_origens_switching(saida: Any) -> dict[str, dict[str, float]]:
    mapa: dict[str, dict[str, float]] = {}

    def _slot(lote: str) -> dict[str, float]:
        return mapa.setdefault(lote, {'bruto_pagamentos': 0.0, 'liquido_pagamentos': 0.0, 'bruto_migrado': 0.0, 'liquido_migrado': 0.0})

    origens = list(_origens_migradas_auditoria(saida))
    tem_hist_auditoria = bool(origens)
    tem_migracao_auditoria = any(para_float(item.get('valor_liquido_migrado_total')) > 0 for item in origens)

    for item in origens:
        lote = str(item.get('lote_origem') or '').strip()
        if not lote:
            continue
        slot = _slot(lote)
        slot['bruto_pagamentos'] += para_float(item.get('valor_bruto_sacado_historico'))
        slot['liquido_pagamentos'] += para_float(item.get('valor_liquido_sacado_historico'))
        liq_mig = para_float(item.get('valor_liquido_migrado_total'))
        slot['liquido_migrado'] += liq_mig
        slot['bruto_migrado'] += para_float(item.get('valor_bruto_migrado_total')) or liq_mig

    if not tem_migracao_auditoria:
        for sw in list(getattr(saida, 'switchings', []) or []):
            lote = str(sw.get('Lote origem') or sw.get('lote_origem') or sw.get('lote_origem_switching') or '').strip()
            if not lote:
                continue
            slot = _slot(lote)
            liq_mig = para_float(sw.get('valor_liquido_origem') or sw.get('Valor líquido origem') or sw.get('valor_liquido_migrado'))
            br_mig = para_float(sw.get('valor_bruto_origem') or sw.get('Valor bruto origem'))
            slot['liquido_migrado'] += liq_mig
            slot['bruto_migrado'] += br_mig if br_mig > 0 else liq_mig

    if not tem_hist_auditoria:
        for linha in list(getattr(saida, 'extrato_passado', []) or []):
            lote_raw = linha.get('Lotes usados') or linha.get('Lote') or ''
            lote_txt = str(lote_raw or '').strip()
            tokens = lote_txt.replace('+', '|').split('|')
            lotes_usados = [part.strip() for part in tokens if part.strip()]
            if not lotes_usados and lote_txt:
                lotes_usados = [lote_txt]
            for lote in lotes_usados:
                lote = str(lote or '').strip()
                if not lote:
                    continue
                slot = _slot(lote)
                slot['bruto_pagamentos'] += para_float(linha.get('Bruto'))
                slot['liquido_pagamentos'] += para_float(linha.get('Líquido'))

    for _, slot in mapa.items():
        for k in list(slot.keys()):
            slot[k] = round(para_float(slot[k]), 2)
    return mapa

def construir_linhas_lotes_encerrados_por_switching(contexto, saida, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    aplicacoes = _aplicacoes_por_lote_do_pacote(pacote_saida_observavel_temporal)
    produtos = _produtos_por_lote_do_pacote(pacote_saida_observavel_temporal)
    linhas: list[dict[str, Any]] = []

    origens = list(_origens_migradas_auditoria(saida))
    mapa_sw = _mapa_switching_por_origem(estado_temporal_inicial)
    if estado_temporal_inicial is not None:
        for inv in list(getattr(estado_temporal_inicial,'inventario_temporal',[]) or []):
            if inv.get('status_temporal') in {'migrado_por_switching','exaurido_por_switching'} or inv.get('migrado_por_switching') is True:
                ev = mapa_sw.get(str(inv.get('lote_id') or '').strip(), {})
                origens.append({'lote_origem':inv.get('lote_id'),'produto_origem':inv.get('produto'),'data_switching':ev.get('data_switching') or inv.get('data_switching'),'data_aplicacao_origem':inv.get('data_aplicacao'),'data_aplicacao_switching':ev.get('data_aplicacao'),'data_recebimento_switching':ev.get('data_recebimento'),'valor_liquido_migrado_total':inv.get('valor_liquido_migrado'),'valor_original_origem':inv.get('valor_original')})
    for item in origens:
        lote = str(item.get('lote_origem') or '').strip()
        data_switching = item.get('data_switching') or item.get('data_aplicacao_switching') or item.get('data_recebimento_switching') or 'n/d'
        data_aplicacao = item.get('data_aplicacao_origem') or _lookup_por_lote_normalizado(aplicacoes, lote, None)
        dias = _calcular_dias_observavel(contexto, data_aplicacao, data_switching)
        produto_origem = (
            item.get('produto_origem')
            or item.get('Produto origem')
            or item.get('produto_origem_switching')
            or _lookup_por_lote_normalizado(produtos, lote, None)
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



def construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    """Valores observáveis das origens migradas por switching.

    Essas linhas existem para alinhar a renderização das tabelas:
    - aparecem em "Lotes exauridos — identificação";
    - também aparecem em "Lotes exauridos — valores e patrimônio";
    - não são somadas no resumo patrimonial, pois o resumo continua usando
      construir_linhas_lotes_consolidados(...).
    """
    valores_originais = _valores_originais_por_lote_do_pacote(pacote_saida_observavel_temporal)
    linhas: list[dict[str, Any]] = []
    mapa_economico = _mapa_economico_origens_switching(saida)

    origens = list(_origens_migradas_auditoria(saida))
    if estado_temporal_inicial is not None:
        for inv in list(getattr(estado_temporal_inicial,'inventario_temporal',[]) or []):
            if inv.get('status_temporal') in {'migrado_por_switching','exaurido_por_switching'} or inv.get('migrado_por_switching') is True:
                origens.append({'lote_origem':inv.get('lote_id'),'produto_origem':inv.get('produto'),'data_switching':inv.get('data_switching'),'data_aplicacao_origem':inv.get('data_aplicacao'),'valor_liquido_migrado_total':inv.get('valor_liquido_migrado')})
    for item in origens:
        lote = str(item.get('lote_origem') or '').strip()
        valor_original = round(para_float(item.get('valor_original_origem')) or para_float(_lookup_por_lote_normalizado(valores_originais, lote, 0.0)) or para_float(item.get('valor_liquido_migrado_total')),2)
        valor_migrado = round(para_float(item.get('valor_liquido_migrado_total') or item.get('valor_liquido_migrado')), 2)
        bruto_sacado_historico = round(para_float(item.get('valor_bruto_sacado_historico')), 2)
        liquido_sacado_historico = round(para_float(item.get('valor_liquido_sacado_historico')), 2)
        econ = mapa_economico.get(lote, {})
        bruto_sacado_total = round(max(bruto_sacado_historico + max(0.0, para_float(econ.get('bruto_migrado'))), para_float(econ.get('bruto_pagamentos')) + para_float(econ.get('bruto_migrado'))), 2)
        liquido_sacado_total = round(max(liquido_sacado_historico + max(0.0, para_float(econ.get('liquido_migrado'))), para_float(econ.get('liquido_pagamentos')) + para_float(econ.get('liquido_migrado')), valor_migrado), 2)

        patrimonio_liquido_observavel = round(liquido_sacado_total, 2)
        rendimento_liquido_observavel = round(patrimonio_liquido_observavel - valor_original, 2)

        linhas.append({
            'Lote': lote,
            'Orig.': valor_original,
            'Bruto sac.': bruto_sacado_total,
            'Líq. sac.': liquido_sacado_total,
            'Bruto atual': 0.0,
            'Líq. atual': 0.0,
            'Patr. líq.': patrimonio_liquido_observavel,
            'Rend. líq.': rendimento_liquido_observavel,
        })

    return linhas



def construir_linhas_origens_migradas_por_switching(contexto, saida, pacote_saida_observavel_temporal: Any | None = None) -> list[dict[str, Any]]:
    estado_temporal_inicial = None
    aplicacoes = _aplicacoes_por_lote_do_pacote(pacote_saida_observavel_temporal)
    linhas: list[dict[str, Any]] = []

    origens = list(_origens_migradas_auditoria(saida))
    mapa_sw = _mapa_switching_por_origem(estado_temporal_inicial)
    if estado_temporal_inicial is not None:
        for inv in list(getattr(estado_temporal_inicial,'inventario_temporal',[]) or []):
            if inv.get('status_temporal') in {'migrado_por_switching','exaurido_por_switching'} or inv.get('migrado_por_switching') is True:
                ev = mapa_sw.get(str(inv.get('lote_id') or '').strip(), {})
                origens.append({'lote_origem':inv.get('lote_id'),'produto_origem':inv.get('produto'),'data_switching':ev.get('data_switching') or inv.get('data_switching'),'data_aplicacao_origem':inv.get('data_aplicacao'),'data_aplicacao_switching':ev.get('data_aplicacao'),'data_recebimento_switching':ev.get('data_recebimento'),'valor_liquido_migrado_total':inv.get('valor_liquido_migrado'),'valor_original_origem':inv.get('valor_original')})
    for item in origens:
        lote = str(item.get('lote_origem') or '').strip()
        data_switching = item.get('data_switching') or item.get('data_aplicacao_switching') or item.get('data_recebimento_switching') or 'n/d'
        data_aplicacao = item.get('data_aplicacao_origem') or _lookup_por_lote_normalizado(aplicacoes, lote, None)
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


def construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal: Any | None = None) -> list[dict[str, Any]]:
    _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    """Switchings enriquecidos para console e planilha.

    Mantém a decisão de switching intacta e apenas preenche campos observáveis
    ausentes, especialmente Produto origem.
    """
    produtos = _produtos_por_lote_do_pacote(pacote_saida_observavel_temporal)
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
            or _lookup_por_lote_normalizado(produtos, lote, None)
        )

        if not _produto_preenchido_observavel(produto_origem):
            produto_origem = "produto_origem_nao_encontrado"

        linha["Produto origem"] = produto_origem
        linha['Data'] = linha.get('Data') or linha.get('data_switching') or linha.get('data_aplicacao')
        linha['Lote origem'] = linha.get('Lote origem') or linha.get('lote_origem') or linha.get('lote_origem_switching') or linha.get('lote_id')
        linha['Lote destino'] = linha.get('Lote destino') or linha.get('lote_destino') or linha.get('Lote (ID) Depois')
        linha['Produto destino'] = linha.get('Produto destino') or linha.get('Produto destino switching') or linha.get('produto_destino') or linha.get('Destino')
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


def construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    linhas_exauridos_consolidadas = _remover_origens_migradas_dos_exauridos_consolidados(
        construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        saida,
    )
    linhas_exauridos = (
        linhas_exauridos_consolidadas
        + construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal, estado_temporal_inicial=estado_temporal_inicial)
    )
    linhas_ativos = construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)
    linhas_economicas = linhas_exauridos_consolidadas + linhas_ativos
    linhas = linhas_exauridos + linhas_ativos

    valor_original_total = round(sum(para_float(item.get('Orig.')) for item in linhas_economicas), 2)
    valor_total_investido_em_carteira = round(sum(para_float(item.get('Orig.')) for item in linhas_ativos), 2)
    valor_total_bruto_sacado = round(sum(para_float(item.get('Bruto sac.')) for item in linhas_economicas), 2)
    valor_total_liquido_sacado = round(sum(para_float(item.get('Líq. sac.')) for item in linhas_economicas), 2)
    valor_bruto_atual = round(sum(para_float(item.get('Bruto atual')) for item in linhas_economicas), 2)
    valor_liquido_atual = round(sum(para_float(item.get('Líq. atual')) for item in linhas_economicas), 2)
    patrimonio_liquido_atual = round(sum(para_float(item.get('Patr. líq.')) for item in linhas_economicas), 2)
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
    if estado_temporal_inicial is not None and valor_liquido_migrado_pos_switching == 0.0:
        switchings_estado = list(getattr(estado_temporal_inicial, 'switching_temporal_realizado', []) or [])
        materializados = [s for s in switchings_estado if s.get('status_temporal') == 'materializado']
        total_migrado = round(sum(para_float(s.get('valor_liquido_migrado')) for s in materializados), 2)
        if total_migrado > 0:
            valor_liquido_migrado_pos_switching = total_migrado
            valor_bruto_sacado_origens_migradas = total_migrado
            valor_liquido_sacado_origens_migradas = total_migrado
    origens_migradas = _lotes_origens_migradas_set(saida)
    origens_migradas_incluidas_no_resumo = any(
        str(item.get('Lote') or '').strip() in origens_migradas
        for item in linhas_exauridos
    )

    patrimonio_liquido_reconciliado = round(patrimonio_liquido_atual, 2)

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
        {'Métrica': 'Valor original destinos pós-switching ativos/sintéticos atuais', 'Valor': valor_original_destinos_pos_switching},
        {'Métrica': 'Valor original observado sem destinos pós-switching sintéticos', 'Valor': valor_original_observado_sem_destinos_sinteticos},
        {'Métrica': 'Base econômica explícita — recebidos brutos', 'Valor': base_economica_recebidos_brutos},
        {'Métrica': 'Valor líquido migrado para destinos pós-switching', 'Valor': valor_liquido_migrado_pos_switching},
        {'Métrica': 'Valor transferido internamente por switching (bruto histórico)', 'Valor': valor_bruto_sacado_origens_migradas},
        {'Métrica': 'Origens encerradas por switching — valor migrado', 'Valor': valor_liquido_migrado_pos_switching},
        {'Métrica': 'Patrimônio líquido atual — reconciliado com origens migradas', 'Valor': patrimonio_liquido_reconciliado},
        {'Métrica': 'Rendimento líquido atual — reconciliado contra recebidos', 'Valor': rendimento_reconciliado_contra_recebidos},
        {'Métrica': 'Rendimento líquido atual — reconciliado contra valor original observado', 'Valor': rendimento_reconciliado_contra_valor_original_observado},
    ]


def construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal: Any | None = None) -> list[dict[str, Any]]:
    _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    return [
        {
            'titulo': 'Lotes exauridos — identificação',
            'headers': COLS_LOTES_EXAURIDOS_ID_CURTAS,
            'linhas': construir_linhas_lotes_id_curta(contexto, saida, tipo='exauridos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        },
        {
            'titulo': 'Lotes exauridos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_CURTAS,
            'linhas': construir_linhas_lotes_valores_curta(contexto, saida, tipo='exauridos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        },
        {
            'titulo': 'Lotes ativos — identificação',
            'headers': COLS_LOTES_ATIVOS_ID_CURTAS,
            'linhas': construir_linhas_lotes_id_curta(contexto, saida, tipo='ativos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        },
        {
            'titulo': 'Lotes ativos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_CURTAS,
            'linhas': construir_linhas_lotes_valores_curta(contexto, saida, tipo='ativos', pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        },
        {
            'titulo': 'Origens migradas por switching — reconciliação patrimonial',
            'headers': COLS_ORIGENS_MIGRADAS_SWITCHING,
            'linhas': construir_linhas_origens_migradas_por_switching(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
        },
        {
            'titulo': 'Patrimônio total dos lotes',
            'headers': ['Métrica', 'Valor'],
            'linhas': construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal),
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



def _normalizar_chave_pagamento(valor: Any) -> str:
    txt = str(valor or "").strip().lower()
    for a, b in [
        ("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"),
        ("é", "e"), ("ê", "e"),
        ("í", "i"),
        ("ó", "o"), ("ô", "o"), ("õ", "o"),
        ("ú", "u"),
        ("ç", "c"),
    ]:
        txt = txt.replace(a, b)
    return " ".join(txt.split())


def _chave_pagamento_replay(row: Any) -> tuple[str, str, str, float]:
    data = _fmt_data_observavel(row.get("Data"), padrao="")
    descricao = _normalizar_chave_pagamento(
        row.get("Conta")
        or row.get("Descrição")
        or row.get("Descricao")
        or ""
    )
    lote = str(row.get("Lote") or row.get("Lotes usados") or "").strip()
    liquido = round(
        para_float(
            row.get("Líquido")
            if "Líquido" in row
            else row.get("Liquido")
        ),
        2,
    )
    return data, descricao, lote, liquido


def _chave_pagamento_console(row: dict[str, Any]) -> tuple[str, str, str, float]:
    data = _fmt_data_observavel(row.get("Data"), padrao="")
    descricao = _normalizar_chave_pagamento(
        row.get("Descrição")
        or row.get("Descricao")
        or row.get("Conta")
        or ""
    )
    lote = str(row.get("Lotes usados") or row.get("Lote") or "").strip()
    liquido = round(
        para_float(
            row.get("Líquido")
            if "Líquido" in row
            else row.get("Liquido") or row.get("Valor")
        ),
        2,
    )
    return data, descricao, lote, liquido


def _pagamentos_replay_por_chave_do_pacote(pacote_saida_observavel_temporal: Any) -> dict[tuple[str, str, str, float], dict[str, Any]]:
    pacote = _exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)
    mapa_pacote: dict[tuple[str, str, str, float], dict[str, Any]] = {}
    for row in (getattr(pacote, "pagamentos_replay_por_chave", {}) or {}).values():
        chave = _chave_pagamento_replay(row)
        if chave[0] and chave[1] and chave[2]:
            mapa_pacote[chave] = {
                "Saldo Antes": row.get("Saldo Antes"),
                "Bruto": row.get("Bruto"),
                "Imposto": row.get("Imposto"),
                "Líquido": row.get("Líquido") if "Líquido" in row else row.get("Liquido"),
                "Saldo Remanescente": row.get("Saldo Remanescente"),
            }
    return mapa_pacote


def corrigir_pagamentos_realizados_console_com_pacote(
    contexto: Any,
    linhas: list[dict[str, Any]],
    pacote_saida_observavel_temporal: Any | None = None,
) -> list[dict[str, Any]]:
    """Normaliza a amostra observável de pagamentos realizados usando o replay.

    Não altera `saida.extrato_passado`, replay, ledger ou regras econômicas.
    Apenas corrige a renderização da amostra do console quando a linha observável
    diverge da linha auditável do replay para o mesmo pagamento/lote.
    """
    mapa_replay = _pagamentos_replay_por_chave_do_pacote(pacote_saida_observavel_temporal) if pacote_saida_observavel_temporal is not None else {}
    if not mapa_replay:
        return list(linhas)

    corrigidas: list[dict[str, Any]] = []
    for linha in linhas:
        nova = dict(linha)
        chave = _chave_pagamento_console(nova)
        ref = mapa_replay.get(chave)
        if ref:
            nova["Saldo Antes"] = ref.get("Saldo Antes")
            nova["Bruto"] = ref.get("Bruto")
            nova["Imposto"] = ref.get("Imposto")
            nova["Líquido"] = ref.get("Líquido")
            nova["Valor"] = ref.get("Líquido")
            nova["Saldo Remanescente"] = ref.get("Saldo Remanescente")
        corrigidas.append(nova)

    return corrigidas

def construir_amostras_pagamentos_operacionais(saida, *, limite: int = 5, contexto: Any | None = None, pacote_saida_observavel_temporal: Any | None = None, estado_temporal_inicial: Any | None = None) -> dict[str, object]:
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
            'linhas': corrigir_pagamentos_realizados_console_com_pacote(
                contexto,
                saida.pagamentos_realizados_console(limite=limite),
                pacote_saida_observavel_temporal=pacote_saida_observavel_temporal,
            ) if contexto is not None else saida.pagamentos_realizados_console(limite=limite),
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
            'linhas': (saida.pagamentos_proximos_console(limite=limite) or _construir_proximos_pagamentos_por_estado_temporal(estado_temporal_inicial, limite)) if estado_temporal_inicial is not None else saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_valores_fonte': {
            'rotulo': 'próximos 5 pagamentos — valores/fonte',
            'headers': list(COLS_PAGAMENTOS_PROXIMOS_VALORES_FONTE),
            'linhas': (saida.pagamentos_proximos_console(limite=limite) or _construir_proximos_pagamentos_por_estado_temporal(estado_temporal_inicial, limite)) if estado_temporal_inicial is not None else saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_switching_status': {
            'rotulo': 'próximos 5 pagamentos — switching/status',
            'headers': list(COLS_PAGAMENTOS_PROXIMOS_SWITCHING_STATUS),
            'linhas': (saida.pagamentos_proximos_console(limite=limite) or _construir_proximos_pagamentos_por_estado_temporal(estado_temporal_inicial, limite)) if estado_temporal_inicial is not None else saida.pagamentos_proximos_console(limite=limite),
            'limite': limite,
        },
        'proximos_relevantes_switching_status': construir_amostra_pagamentos_futuros_switching_relevante(saida, limite=limite),
    }




def _construir_proximos_pagamentos_por_estado_temporal(estado_temporal_inicial: Any, limite: int) -> list[dict[str, Any]]:
    pagamentos = list(getattr(estado_temporal_inicial, 'pagamentos_temporais', []) or [])
    futuros = [p for p in pagamentos if p.get('status_temporal') == 'futuro' or p.get('futuro_na_referencia') is True]
    futuros.sort(key=lambda p: str(p.get('data') or ''))
    linhas = []
    for p in futuros[:limite]:
        linhas.append({
            'Data': p.get('data'),
            'Conta': p.get('descricao') or p.get('pagamento_id') or '',
            'Valor': p.get('valor'),
            'Lote': 'fonte_a_decidir' if p.get('fonte_a_decidir') else (p.get('fonte_resolvida_historica') or 'não decidido_etapa5'),
            'Pós-switch': 'não decidido_etapa5',
            'Destino sw.': 'não decidido_etapa5',
            'Origem sw.': 'não decidido_etapa5',
            'Fonte sw.': 'não decidido_etapa5',
            'Data sw.': 'não decidido_etapa5',
            'Ganho sw.': 'n/d',
            'Pacote': 'não decidido_etapa5',
            'Switch?': 'não',
            'Reserva': 'n/d',
            'Saldo ant.': 'n/d',
            'Bruto': p.get('valor'),
            'IR': 'n/d',
            'Liq.': p.get('valor'),
            'Rem.': 'n/d',
            'Sw. ant.': 'n/d',
            'Sw. dep.': 'n/d',
            'Status': 'obrigacao_temporal_futura_sem_decisao_etapa5',
            'Bloq.': 'fonte_a_decidir',
            'Cobertura': 'não',
        })
    return linhas
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
