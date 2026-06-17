from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from types import SimpleNamespace
from typing import Any

from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida

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

# Cabeçalhos oficiais da Situação Atual.
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

COLS_LOTES_VALORES_AUDITORIA_CURTAS = COLS_LOTES_VALORES_CURTAS + [
    'Rend. líq. motor',
    'Dif. rend.',
    'Rend. motor teórico',
    'Dif. teórica',
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


def _valores_sacados_por_lote_do_pacote(snapshot_situacao_atual: Any) -> dict[str, dict[str, float]]:
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    out: dict[str, dict[str, float]] = {}
    for lote_id, dados in (getattr(snapshot, "valores_sacados_por_lote", {}) or {}).items():
        bruto = (dados or {}).get("bruto_sacado")
        liquido = (dados or {}).get("liquido_sacado")
        if bruto is None and liquido is None and "valor_sacado_total" in (dados or {}):
            liquido = (dados or {}).get("valor_sacado_total")
        out[str(lote_id)] = {"bruto_sacado": round(para_float(bruto), 2), "liquido_sacado": round(para_float(liquido), 2)}

    pagamentos = list((getattr(snapshot, "pagamentos_replay_por_chave", {}) or {}).values())
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
    except Exception as exc:
        raise RuntimeError("situacao_atual_oficial_falha_calculo_dias") from exc


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


def _aplicacoes_por_lote_do_pacote(snapshot_situacao_atual: Any) -> dict[str, Any]:
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    return dict(getattr(snapshot, "aplicacoes_por_lote", {}) or {})


def _produto_preenchido_observavel(valor: Any) -> bool:
    txt = str(valor or "").strip()
    return txt not in {"", "-", "n/d", "nd", "não determinado", "nao determinado", "None", "nan", "NaT", "produto_origem_nao_encontrado"}


def _registrar_produto_lote(mapa: dict[str, Any], lote_id: Any, produto: Any) -> None:
    lote = str(lote_id or "").strip()
    if not lote or not _produto_preenchido_observavel(produto):
        return
    mapa.setdefault(lote, str(produto).strip())


def _produtos_por_lote_do_pacote(snapshot_situacao_atual: Any) -> dict[str, Any]:
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    return dict(getattr(snapshot, "produtos_por_lote", {}) or {})


def _registrar_valor_original_lote(mapa: dict[str, float], lote_id: Any, valor_original: Any) -> None:
    lote = str(lote_id or "").strip()
    valor = round(para_float(valor_original), 2)
    if not lote or valor <= 0:
        return
    mapa.setdefault(lote, valor)


def _valores_originais_por_lote_do_pacote(snapshot_situacao_atual: Any) -> dict[str, float]:
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    return dict(getattr(snapshot, "valores_originais_por_lote", {}) or {})




def _exigir_snapshot_situacao_atual(snapshot_situacao_atual: Any) -> Any:
    if snapshot_situacao_atual is None:
        raise RuntimeError("situacao_atual_oficial_requer_snapshot")
    return snapshot_situacao_atual

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



def _saldos_finais_replay_por_lote_do_pacote(snapshot_situacao_atual: Any) -> dict[str, float]:
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    return dict(getattr(snapshot, "saldos_finais_replay_por_lote", {}) or {})


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


def _mapa_valores_switching_por_origem(estado_temporal_inicial: Any | None) -> dict[str, dict[str, float]]:
    """Agrega valores materializados de switching por lote de origem.

    A origem pode alimentar mais de um destino no mesmo ciclo. Por isso, esta
    função soma eventos materializados em vez de manter apenas um evento por
    origem.
    """
    mapa: dict[str, dict[str, float]] = {}
    if estado_temporal_inicial is None:
        return mapa

    for ev in list(getattr(estado_temporal_inicial, 'switching_temporal_realizado', []) or []):
        origem = str(ev.get('lote_origem') or '').strip()
        if not origem:
            continue

        slot = mapa.setdefault(
            origem,
            {
                'valor_liquido_migrado_total': 0.0,
                'valor_bruto_migrado_total': 0.0,
                'qtd_switchings': 0.0,
            },
        )

        valor_liquido = para_float(
            ev.get('valor_liquido_migrado')
            or ev.get('valor_liquido_migrado_total')
            or ev.get('valor_liquido_origem')
            or ev.get('Valor líquido origem')
            or ev.get('Valor Líquido Migrado')
        )
        valor_bruto = para_float(
            ev.get('valor_bruto_migrado')
            or ev.get('valor_bruto_migrado_total')
            or ev.get('valor_bruto_origem')
            or ev.get('Valor bruto origem')
        )

        if valor_bruto <= 0.0:
            valor_bruto = valor_liquido

        slot['valor_liquido_migrado_total'] = round(slot['valor_liquido_migrado_total'] + valor_liquido, 2)
        slot['valor_bruto_migrado_total'] = round(slot['valor_bruto_migrado_total'] + valor_bruto, 2)
        slot['qtd_switchings'] = round(slot['qtd_switchings'] + 1.0, 2)

    return mapa


def _filtrar_lotes_ativos_com_estado_temporal(
    linhas: list[dict[str, Any]],
    estado_temporal_inicial: Any | None = None,
) -> list[dict[str, Any]]:
    if estado_temporal_inicial is None:
        return linhas

    migrados = {
        str(l.get('lote_id') or '').strip()
        for l in (getattr(estado_temporal_inicial, 'inventario_temporal', []) or [])
        if l.get('status_temporal') in {'migrado_por_switching', 'exaurido_por_switching'}
        or l.get('migrado_por_switching') is True
    }

    if not migrados:
        return linhas

    return [
        row
        for row in linhas
        if str(row.get('Lote') or '').strip() not in migrados
    ]


def _remover_origens_migradas_dos_exauridos_consolidados(
    linhas: list[dict[str, Any]],
    saida: Any,
) -> list[dict[str, Any]]:
    """Remove origens migradas quando a base precisa conter apenas saques."""
    origens_migradas = _lotes_origens_migradas_set(saida)
    if not origens_migradas:
        return linhas
    return [
        linha
        for linha in linhas
        if str(linha.get("Lote") or "").strip() not in origens_migradas
    ]


def _remover_origens_migradas_dos_ativos_consolidados(
    linhas: list[dict[str, Any]],
    saida: Any,
) -> list[dict[str, Any]]:
    """Remove origens migradas da base ativa somável.

    Este filtro é complementar ao filtro por estado temporal. Ele cobre o caso
    em que as origens migradas existem apenas na auditoria da saída e
    `estado_temporal_inicial` não está disponível para filtrar os ativos.
    """
    origens_migradas = _lotes_origens_migradas_set(saida)
    if not origens_migradas:
        return linhas
    return [
        linha
        for linha in linhas
        if str(linha.get("Lote") or "").strip() not in origens_migradas
    ]


def _mesclar_lotes_exauridos_com_origens_switching(

    linhas_exauridos_por_saque: list[dict[str, Any]],
    linhas_encerrados_por_switching: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Monta tabela observável de exauridos sem duplicar origens migradas.

    Origens migradas por switching devem aparecer como ciclo encerrado, mas
    permanecem semanticamente diferentes de exauridos por saque. A exclusão da
    base somável principal continua sendo feita no resumo patrimonial.
    """
    chaves_switching = {
        _norm_lote_chave(linha.get("Lote"))
        for linha in linhas_encerrados_por_switching
        if _norm_lote_chave(linha.get("Lote"))
    }

    base_sem_origens_switching = [
        linha
        for linha in linhas_exauridos_por_saque
        if _norm_lote_chave(linha.get("Lote")) not in chaves_switching
    ]

    saida: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for linha in list(base_sem_origens_switching) + list(linhas_encerrados_por_switching):
        chave = _norm_lote_chave(linha.get("Lote"))
        if chave:
            if chave in vistos:
                continue
            vistos.add(chave)
        saida.append(linha)
    return saida


def calcular_rendimento_liquido_observavel(
    *,
    status_ciclo: str,
    valor_original: float,
    patrimonio_liquido: float,
) -> float:
    """Calcula rendimento líquido observável sem clamp por status.

    A função não corrige sinal nem mascara rendimento negativo. Se um lote
    ativo, exaurido ou pós-switching apresentar rendimento negativo, a saída
    deve expor o valor calculado para auditoria patrimonial posterior.

    Switching é tratado como transferência interna em bloco próprio, não como
    perda automática de patrimônio de origem.
    """
    _ = status_ciclo
    return round(patrimonio_liquido - valor_original, 2)


def _mapa_lotes_motor_contexto(contexto: Any) -> dict[str, Any]:
    """Indexa lotes do núcleo financeiro para auditoria visual de rendimento."""
    mapa: dict[str, Any] = {}

    nucleo = getattr(contexto, "nucleo_financeiro", None)
    for lote in list(getattr(nucleo, "lotes_financeiros", []) or []):
        chave = _norm_lote_chave(getattr(lote, "id", ""))
        if chave:
            mapa.setdefault(chave, lote)

    replay = getattr(contexto, "replay_passado", None)
    for lote in list(getattr(replay, "lotes_apos_replay", []) or []):
        chave = _norm_lote_chave(getattr(lote, "id", ""))
        if chave:
            mapa.setdefault(chave, lote)

    return mapa


def _rendimento_liquido_motor_lote(
    contexto: Any,
    lote_id: Any,
    data_alvo: Any,
) -> float | str:
    """Calcula rendimento líquido do motor para um lote e data-alvo.

    Não usa a saída observável como fallback. Quando o lote ou a data não são
    calculáveis pelo motor, retorna n/d para evitar comparação tautológica.
    """
    data = _coagir_data_observavel(data_alvo)
    if data is None:
        return "n/d"

    lote = _lookup_por_lote_normalizado(
        _mapa_lotes_motor_contexto(contexto),
        lote_id,
        None,
    )
    if lote is None:
        return "n/d"

    try:
        valor_liquido = lote.valor_liquido_em_data(
            data,
            contexto.calendario_financeiro,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=getattr(lote, "data_aplicacao", data),
        )
        return round(float(valor_liquido) - float(getattr(lote, "valor_inicial", 0.0)), 2)
    except Exception:
        return "n/d"


def _rendimento_liquido_motor_calibrado_por_ancoras(
    *,
    valor_original: float,
    liquido_sacado_realizado: float,
    liquido_residual_calibrado: float,
) -> float:
    """Rendimento do motor calibrado por âncoras financeiras upstream.

    A métrica usa valores já materializados pelo replay/contexto/estado
    temporal para representar a economia realizada do lote, sem depender da
    tabela renderizada e sem usar o cálculo teórico do lote como fonte
    primária.
    """
    patrimonio_calibrado = round(
        para_float(liquido_sacado_realizado) + para_float(liquido_residual_calibrado),
        2,
    )
    return round(patrimonio_calibrado - para_float(valor_original), 2)


def _diferenca_rendimento_motor(rendimento_observavel: float, rendimento_motor: Any) -> float | str:
    if isinstance(rendimento_motor, (int, float)):
        return round(float(rendimento_observavel) - float(rendimento_motor), 2)
    return "n/d"




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


def _montar_lotes_consolidados_oficial(contexto, saida, *, tipo: str, snapshot_situacao_atual: Any | None = None, modo_bootstrap_snapshot: bool = False) -> list[dict[str, Any]]:
    campo = 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos'
    itens = list(getattr(saida, campo, []) or [])
    lotes_exauridos = list(getattr(saida, 'lotes_exauridos', []) or [])
    if snapshot_situacao_atual is None:
        if not modo_bootstrap_snapshot:
            _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
        mapa_saldo_final_replay = _saldos_finais_por_lote_bootstrap(saida)
        somas = _valores_sacados_por_lote_bootstrap(saida)
    else:
        mapa_saldo_final_replay = _saldos_finais_replay_por_lote_do_pacote(snapshot_situacao_atual)
        somas = _valores_sacados_por_lote_do_pacote(snapshot_situacao_atual)
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
        if origem_exaurida_com_saldo_replay:
            bruto_atual = saldo_final_replay

        patrimonio_liquido = round(liquido_sacado + liquido_atual, 2)
        rendimento_liquido = calcular_rendimento_liquido_observavel(
            status_ciclo=status_ciclo,
            valor_original=valor_original,
            patrimonio_liquido=patrimonio_liquido,
        )
        rendimento_motor_teorico = _rendimento_liquido_motor_lote(
            contexto,
            lote_id,
            data_referencia_dias,
        )
        rendimento_liquido_motor = _rendimento_liquido_motor_calibrado_por_ancoras(
            valor_original=valor_original,
            liquido_sacado_realizado=liquido_sacado,
            liquido_residual_calibrado=liquido_atual,
        )
        diferenca_rendimento_motor = _diferenca_rendimento_motor(
            rendimento_liquido,
            rendimento_liquido_motor,
        )
        diferenca_teorica = _diferenca_rendimento_motor(
            rendimento_liquido_motor,
            rendimento_motor_teorico,
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
            'Rend. líq. motor': rendimento_liquido_motor,
            'Dif. rend.': diferenca_rendimento_motor,
            'Rend. motor teórico': rendimento_motor_teorico,
            'Dif. teórica': diferenca_teorica,
        })

    return linhas


def _montar_lotes_identificacao_oficial(contexto, saida, *, tipo: str, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    if tipo == 'ativos':
        headers = COLS_LOTES_ATIVOS_ID_CURTAS
        linhas_base = _montar_lotes_consolidados_oficial(contexto, saida, tipo=tipo, snapshot_situacao_atual=snapshot_situacao_atual)
    elif tipo == 'exauridos':
        headers = COLS_LOTES_EXAURIDOS_ID_CURTAS
        linhas_exauridos_por_saque = _remover_origens_migradas_dos_exauridos_consolidados(
            _montar_lotes_consolidados_oficial(contexto, saida, tipo=tipo, snapshot_situacao_atual=snapshot_situacao_atual),
            saida,
        )
        linhas_encerrados_por_switching = construir_linhas_lotes_encerrados_por_switching(
            contexto,
            saida,
            snapshot_situacao_atual=snapshot_situacao_atual,
            estado_temporal_inicial=estado_temporal_inicial,
        )
        linhas_base = _mesclar_lotes_exauridos_com_origens_switching(
            linhas_exauridos_por_saque,
            linhas_encerrados_por_switching,
        )
    else:
        headers = COLS_LOTES_ID_CURTAS
        linhas_base = _montar_lotes_consolidados_oficial(contexto, saida, tipo=tipo, snapshot_situacao_atual=snapshot_situacao_atual)

    return [
        {chave: item.get(chave) for chave in headers}
        for item in linhas_base
    ]


def _montar_lotes_valores_oficial(contexto, saida, *, tipo: str, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    linhas_base = list(_montar_lotes_consolidados_oficial(contexto, saida, tipo=tipo, snapshot_situacao_atual=snapshot_situacao_atual))

    if tipo == 'exauridos':
        linhas_exauridos_por_saque = _remover_origens_migradas_dos_exauridos_consolidados(linhas_base, saida)
        linhas_encerrados_por_switching = construir_linhas_lotes_valores_encerrados_por_switching(
            contexto,
            saida,
            snapshot_situacao_atual=snapshot_situacao_atual,
            estado_temporal_inicial=estado_temporal_inicial,
        )
        linhas_base = _mesclar_lotes_exauridos_com_origens_switching(
            linhas_exauridos_por_saque,
            linhas_encerrados_por_switching,
        )

    headers = COLS_LOTES_VALORES_AUDITORIA_CURTAS
    return [
        {chave: item.get(chave) for chave in headers}
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

def construir_linhas_lotes_encerrados_por_switching(contexto, saida, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    aplicacoes = _aplicacoes_por_lote_do_pacote(snapshot_situacao_atual)
    produtos = _produtos_por_lote_do_pacote(snapshot_situacao_atual)
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



def construir_linhas_lotes_valores_encerrados_por_switching(contexto, saida, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    """Valores observáveis das origens migradas por switching.

    ME-525A: origens migradas por switching aparecem também nas tabelas de
    lotes exauridos com status de migração. Elas continuam fora da base somável
    do patrimônio principal para evitar dupla contagem com os destinos.
    """
    valores_originais = _valores_originais_por_lote_do_pacote(snapshot_situacao_atual)
    linhas: list[dict[str, Any]] = []
    mapa_economico = _mapa_economico_origens_switching(saida)
    mapa_switching_valores = _mapa_valores_switching_por_origem(estado_temporal_inicial)
    mapa_switching_eventos = _mapa_switching_por_origem(estado_temporal_inicial)

    origens = list(_origens_migradas_auditoria(saida))
    if estado_temporal_inicial is not None:
        for inv in list(getattr(estado_temporal_inicial,'inventario_temporal',[]) or []):
            if inv.get('status_temporal') in {'migrado_por_switching','exaurido_por_switching'} or inv.get('migrado_por_switching') is True:
                origens.append({'lote_origem':inv.get('lote_id'),'produto_origem':inv.get('produto'),'data_switching':inv.get('data_switching'),'data_aplicacao_origem':inv.get('data_aplicacao'),'valor_liquido_migrado_total':inv.get('valor_liquido_migrado')})
    for item in origens:
        lote = str(item.get('lote_origem') or '').strip()
        valor_original = round(para_float(item.get('valor_original_origem')) or para_float(_lookup_por_lote_normalizado(valores_originais, lote, 0.0)) or para_float(item.get('valor_liquido_migrado_total')),2)
        valor_migrado_item = round(para_float(item.get('valor_liquido_migrado_total') or item.get('valor_liquido_migrado')), 2)
        bruto_sacado_historico = round(para_float(item.get('valor_bruto_sacado_historico')), 2)
        liquido_sacado_historico = round(para_float(item.get('valor_liquido_sacado_historico')), 2)

        econ = _lookup_por_lote_normalizado(mapa_economico, lote, {})
        sw_valores = _lookup_por_lote_normalizado(mapa_switching_valores, lote, {})

        valor_migrado = round(max(
            valor_migrado_item,
            para_float(econ.get('liquido_migrado')),
            para_float(sw_valores.get('valor_liquido_migrado_total')),
        ), 2)

        bruto_migrado = round(max(
            para_float(econ.get('bruto_migrado')),
            para_float(sw_valores.get('valor_bruto_migrado_total')),
            valor_migrado,
        ), 2)

        bruto_sacado_total = round(max(
            bruto_sacado_historico + bruto_migrado,
            para_float(econ.get('bruto_pagamentos')) + bruto_migrado,
            bruto_migrado,
        ), 2)

        liquido_sacado_total = round(max(
            liquido_sacado_historico + valor_migrado,
            para_float(econ.get('liquido_pagamentos')) + valor_migrado,
            valor_migrado,
        ), 2)

        patrimonio_liquido_observavel = round(liquido_sacado_total, 2)
        rendimento_liquido_observavel = round(patrimonio_liquido_observavel - valor_original, 2)

        ev_switching = _lookup_por_lote_normalizado(mapa_switching_eventos, lote, {})
        data_switching_motor = (
            item.get('data_switching')
            or item.get('data_aplicacao_switching')
            or item.get('data_recebimento_switching')
            or ev_switching.get('data_switching')
            or ev_switching.get('data_aplicacao')
            or ev_switching.get('data_recebimento')
        )
        rendimento_motor_teorico = _rendimento_liquido_motor_lote(
            contexto,
            lote,
            data_switching_motor,
        )
        rendimento_liquido_motor = _rendimento_liquido_motor_calibrado_por_ancoras(
            valor_original=valor_original,
            liquido_sacado_realizado=liquido_sacado_total,
            liquido_residual_calibrado=0.0,
        )
        diferenca_rendimento_motor = _diferenca_rendimento_motor(
            rendimento_liquido_observavel,
            rendimento_liquido_motor,
        )
        diferenca_teorica = _diferenca_rendimento_motor(
            rendimento_liquido_motor,
            rendimento_motor_teorico,
        )

        linhas.append({
            'Lote': lote,
            'Orig.': valor_original,
            'Bruto sac.': bruto_sacado_total,
            'Líq. sac.': liquido_sacado_total,
            'Bruto atual': 0.0,
            'Líq. atual': 0.0,
            'Patr. líq.': patrimonio_liquido_observavel,
            'Rend. líq.': rendimento_liquido_observavel,
            'Rend. líq. motor': rendimento_liquido_motor,
            'Dif. rend.': diferenca_rendimento_motor,
            'Rend. motor teórico': rendimento_motor_teorico,
            'Dif. teórica': diferenca_teorica,
        })

    return linhas



def construir_linhas_origens_migradas_por_switching(contexto, saida, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    aplicacoes = _aplicacoes_por_lote_do_pacote(snapshot_situacao_atual)
    linhas: list[dict[str, Any]] = []
    valores_encerrados = {
        str(row.get('Lote') or '').strip(): row
        for row in construir_linhas_lotes_valores_encerrados_por_switching(
            contexto,
            saida,
            snapshot_situacao_atual=snapshot_situacao_atual,
            estado_temporal_inicial=estado_temporal_inicial,
        )
        if str(row.get('Lote') or '').strip()
    }

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
        valores_lote = valores_encerrados.get(lote, {})
        valor_migrado = round(
            para_float(valores_lote.get('Líq. sac.'))
            or para_float(item.get('valor_liquido_migrado_total'))
            or para_float(item.get('valor_liquido_migrado')),
            2,
        )
        bruto_sacado_historico = round(
            para_float(valores_lote.get('Bruto sac.'))
            or para_float(item.get('valor_bruto_sacado_historico')),
            2,
        )
        liquido_sacado_historico = round(
            para_float(valores_lote.get('Líq. sac.'))
            or para_float(item.get('valor_liquido_sacado_historico'))
            or valor_migrado,
            2,
        )

        linhas.append({
            'Lote origem': lote,
            'Status': item.get('status_origem') or 'migrado_por_switching',
            'Status ciclo': 'migrado_por_switching',
            'Data término': _fmt_data_observavel(data_switching),
            'Dias corr.': dias.get('dias_corridos', ''),
            'Dias úteis': dias.get('dias_uteis', ''),
            'Valor migrado': valor_migrado,
            'Bruto sac. hist.': bruto_sacado_historico,
            'Líq. sac. hist.': liquido_sacado_historico,
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


def _valor_total_recebidos_brutos(saida) -> float:
    for item in list(getattr(saida, 'resumo_recebidos', []) or []):
        metrica = str(item.get('Métrica') or item.get('Metrica') or '').strip().lower()
        if metrica == 'valor total bruto':
            return round(para_float(item.get('Valor')), 2)

    total = 0.0
    for item in list(getattr(saida, 'recebidos_atuais', []) or []):
        total += para_float(item.get('Valor bruto'))
    return round(total, 2)


def _montar_patrimonio_total_lotes_oficial(contexto, saida, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    linhas_exauridos_por_saque = _remover_origens_migradas_dos_exauridos_consolidados(
        _montar_lotes_consolidados_oficial(
            contexto,
            saida,
            tipo='exauridos',
            snapshot_situacao_atual=snapshot_situacao_atual,
        ),
        saida,
    )
    linhas_origens_migradas = construir_linhas_lotes_valores_encerrados_por_switching(
        contexto,
        saida,
        snapshot_situacao_atual=snapshot_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    linhas_exauridos_consolidadas = _mesclar_lotes_exauridos_com_origens_switching(
        linhas_exauridos_por_saque,
        linhas_origens_migradas,
    )
    # ME-528: a base agregada deve usar a mesma semântica dos blocos publicados:
    # origens migradas por switching não permanecem como ativos comuns; elas
    # entram como ciclos encerrados por switching, evitando divergência entre
    # patrimônio total e linhas de Situação Atual.
    linhas_ativos = _remover_origens_migradas_dos_ativos_consolidados(
        _filtrar_lotes_ativos_com_estado_temporal(
            _montar_lotes_consolidados_oficial(
                contexto,
                saida,
                tipo='ativos',
                snapshot_situacao_atual=snapshot_situacao_atual,
            ),
            estado_temporal_inicial=estado_temporal_inicial,
        ),
        saida,
    )
    linhas_economicas = linhas_exauridos_consolidadas + linhas_ativos

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
    # ME-519: origens migradas por switching são transferência interna.
    # Elas não integram a base somável do resumo patrimonial.
    origens_migradas_incluidas_no_resumo = False

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

    bloco_principal = [
        {'Métrica': '--- Patrimônio econômico principal ---', 'Valor': ''},
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total investido em carteira', 'Valor': valor_total_investido_em_carteira},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
    ]

    bloco_reconciliacao = [
        {'Métrica': '--- Reconciliação patrimonial / auditoria ---', 'Valor': ''},
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

    return bloco_principal + bloco_reconciliacao


def _montar_blocos_situacao_atual_oficial(contexto, saida, snapshot_situacao_atual: Any | None = None, estado_temporal_inicial: Any | None = None) -> list[dict[str, Any]]:
    _exigir_snapshot_situacao_atual(snapshot_situacao_atual)

    lotes_exauridos_id = _montar_lotes_identificacao_oficial(
        contexto,
        saida,
        tipo='exauridos',
        snapshot_situacao_atual=snapshot_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    lotes_exauridos_valores = _montar_lotes_valores_oficial(
        contexto,
        saida,
        tipo='exauridos',
        snapshot_situacao_atual=snapshot_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    lotes_ativos_id = _filtrar_lotes_ativos_com_estado_temporal(
        _montar_lotes_identificacao_oficial(
            contexto,
            saida,
            tipo='ativos',
            snapshot_situacao_atual=snapshot_situacao_atual,
            estado_temporal_inicial=estado_temporal_inicial,
        ),
        estado_temporal_inicial=estado_temporal_inicial,
    )
    lotes_ativos_valores = _filtrar_lotes_ativos_com_estado_temporal(
        _montar_lotes_valores_oficial(
            contexto,
            saida,
            tipo='ativos',
            snapshot_situacao_atual=snapshot_situacao_atual,
            estado_temporal_inicial=estado_temporal_inicial,
        ),
        estado_temporal_inicial=estado_temporal_inicial,
    )
    origens_migradas = construir_linhas_origens_migradas_por_switching(
        contexto,
        saida,
        snapshot_situacao_atual=snapshot_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    patrimonio_total = _montar_patrimonio_total_lotes_oficial(
        contexto,
        saida,
        snapshot_situacao_atual=snapshot_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )

    return [
        {
            'titulo': 'Lotes exauridos — identificação',
            'headers': COLS_LOTES_EXAURIDOS_ID_CURTAS,
            'linhas': lotes_exauridos_id,
        },
        {
            'titulo': 'Lotes exauridos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_AUDITORIA_CURTAS,
            'linhas': lotes_exauridos_valores,
        },
        {
            'titulo': 'Lotes ativos — identificação',
            'headers': COLS_LOTES_ATIVOS_ID_CURTAS,
            'linhas': lotes_ativos_id,
        },
        {
            'titulo': 'Lotes ativos — valores e patrimônio',
            'headers': COLS_LOTES_VALORES_AUDITORIA_CURTAS,
            'linhas': lotes_ativos_valores,
        },
        {
            'titulo': 'Origens migradas por switching — reconciliação patrimonial',
            'headers': COLS_ORIGENS_MIGRADAS_SWITCHING,
            'linhas': origens_migradas,
        },
        {
            'titulo': 'Patrimônio total dos lotes',
            'headers': ['Métrica', 'Valor'],
            'linhas': patrimonio_total,
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


VERSAO_SITUACAO_ATUAL_OFICIAL = "ME-525A-SITUACAO-ATUAL-SWITCHING-EXAURIDOS-01"


@dataclass(slots=True)
class SnapshotSituacaoAtualOficial:
    versao: str
    data_referencia: Any
    saldos_finais_replay_por_lote: dict[str, float]
    pagamentos_replay_por_chave: dict[str, dict[str, Any]]
    aplicacoes_por_lote: dict[str, Any]
    produtos_por_lote: dict[str, str]
    valores_originais_por_lote: dict[str, float]
    valores_sacados_por_lote: dict[str, dict[str, float]]
    lotes_ativos_observaveis: list[dict[str, Any]]
    lotes_exauridos_observaveis: list[dict[str, Any]]
    pagamentos_realizados_observaveis: list[dict[str, Any]]
    auditoria_situacao_atual_oficial: dict[str, Any]
    validacao_situacao_atual_oficial: dict[str, Any]
    metadados_origem: dict[str, Any]

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def _txt(v: Any) -> str:
    return str(v or "").strip()


def _lote_norm(v: Any) -> str:
    return _txt(v).lower().replace(".", "")


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _data_ord(v: Any) -> tuple[int, str]:
    if isinstance(v, (datetime, date)):
        return (0, v.isoformat())
    s = _txt(v)
    if not s:
        return (2, "")
    try:
        return (0, datetime.fromisoformat(s).isoformat())
    except Exception:
        return (1, s)


def _iter_rows(obj: Any) -> list[dict[str, Any]]:
    if obj is None:
        return []
    if hasattr(obj, "to_dict"):
        try:
            return list(obj.to_dict(orient="records"))
        except Exception:
            pass
    if isinstance(obj, list):
        return [dict(x) if isinstance(x, dict) else {"valor": x} for x in obj]
    return []


def _valor_primeiro(row: dict[str, Any], nomes: list[str]) -> Any:
    for n in nomes:
        if n in row and row.get(n) not in (None, ""):
            return row.get(n)
    return None


def _num_primeiro(row: dict[str, Any], nomes: list[str]) -> float:
    return _f(_valor_primeiro(row, nomes))


def _txt_primeiro(row: dict[str, Any], nomes: list[str]) -> str:
    return _txt(_valor_primeiro(row, nomes))


def _construir_snapshot_situacao_atual_oficial(
    contexto: Any,
    saida: Any,
    *,
    pacotes_temporais: Any | None = None,
    lotes_ativos_observaveis: list[dict[str, Any]] | None = None,
    lotes_exauridos_observaveis: list[dict[str, Any]] | None = None,
    pagamentos_realizados_observaveis: list[dict[str, Any]] | None = None,
) -> SnapshotSituacaoAtualOficial:
    pacotes = pacotes_temporais or construir_pacotes_temporais_agregados_saida(contexto)
    replay = getattr(pacotes, "pacote_replay_passado", None)
    log = _iter_rows(getattr(replay, "log_movimentos_passados", []))

    rows_ordenadas = sorted(list(enumerate(log)), key=lambda x: (_data_ord(_valor_primeiro(x[1], ["Data"])), x[0]))
    saldos_finais: dict[str, float] = {}
    pagamentos: dict[str, dict[str, Any]] = {}
    valores_sacados: dict[str, dict[str, float]] = {}
    colisoes = 0
    for ordem_original, r in rows_ordenadas:
        lote = _txt_primeiro(r, ["Lote"])
        if lote:
            saldos_finais[lote] = _num_primeiro(r, ["Saldo Remanescente", "Saldo remanescente", "Remanescente"])

        data_iso = _data_ord(_valor_primeiro(r, ["Data"]))[1]
        conta = _txt_primeiro(r, ["Conta", "Descrição", "Descricao", "Histórico", "Historico"]).lower()
        valor_conta = _num_primeiro(r, ["Valor Conta", "Líquido", "Liquido", "Valor"])
        despesa_id = _txt_primeiro(r, ["Despesa ID", "despesa_id"])
        partes = [data_iso, conta, f"{valor_conta:.2f}", _lote_norm(lote)]
        if despesa_id:
            partes.append(despesa_id)
        partes.append(str(ordem_original))
        chave = "|".join(partes)

        if chave in pagamentos:
            colisoes += 1
        pagamentos[chave] = {"ordem_original": ordem_original, **r}

        if lote:
            acc = valores_sacados.setdefault(lote, {"valor_sacado_total": 0.0, "qtd_movimentos": 0.0})
            valor_saque = _num_primeiro(r, ["Líquido", "Liquido", "Valor Líquido", "Valor Liquido", "Valor"])
            acc["valor_sacado_total"] = round(acc["valor_sacado_total"] + abs(valor_saque), 2)
            acc["qtd_movimentos"] = round(acc["qtd_movimentos"] + 1.0, 2)

    origem = "snapshot_observavel_consolidado"
    lotes_ativos = list(lotes_ativos_observaveis or [])
    lotes_exauridos = list(lotes_exauridos_observaveis or [])
    pagamentos_realizados = list(pagamentos_realizados_observaveis or _iter_rows(getattr(saida, "extrato_passado", [])))

    lotes_base = lotes_ativos + lotes_exauridos
    aplic, prod, orig = {}, {}, {}
    for r in lotes_base:
        lote = _txt(r.get("Lote"))
        if not lote:
            continue
        aplic[lote] = _txt_primeiro(r, ["Aplic.", "Aplicação", "Aplicacao", "aplicacao"])
        prod[lote] = _txt(r.get("Produto") or r.get("Carteira"))
        orig[lote] = _num_primeiro(r, ["Orig.", "Orig", "Valor Original", "Valor original"])

    ativos_set = {_lote_norm(r.get("Lote")) for r in lotes_ativos}
    ex_set = {_lote_norm(r.get("Lote")) for r in lotes_exauridos}
    qtd_aplic_preenchidas = sum(1 for v in aplic.values() if _txt(v) != "")
    qtd_orig_positivos = sum(1 for v in orig.values() if _f(v) > 0)
    aplic_sem_vazios = qtd_aplic_preenchidas == len(aplic)
    orig_validos = qtd_orig_positivos == len(orig)

    erros = []
    if not saldos_finais:
        erros.append("saldos_finais_replay_por_lote_vazio")
    if not pagamentos:
        erros.append("pagamentos_replay_por_chave_vazio")
    if not lotes_ativos:
        erros.append("lotes_ativos_observaveis_vazio")
    if not lotes_exauridos:
        erros.append("lotes_exauridos_observaveis_vazio")
    if ativos_set & ex_set:
        erros.append("lotes_duplicados_ativos_exauridos")
    if colisoes != 0:
        erros.append("colisoes_chave_pagamento_replay")
    if not aplic_sem_vazios:
        erros.append("aplicacoes_por_lote_com_vazios")
    if not orig_validos:
        erros.append("valores_originais_por_lote_invalidos")

    validacao = {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": [],
        "evidencias": {
            "origem_lotes_ativos_exauridos": origem,
            "usa_snapshot_canonico_bruto": False,
            "validacao_generica_snapshot_ok": len(erros) == 0,
        },
    }
    auditoria = {
        "ok": len(erros) == 0,
        "versao_microetapa": VERSAO_SITUACAO_ATUAL_OFICIAL,
        "origem_execucao": "situacao_atual_oficial",
        "contrato_alvo": "SnapshotSituacaoAtualOficial",
        "usa_pacotes_temporais_agregados": True,
        "nao_altera_saida_canonica": True,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "qtd_saldos_finais_replay_por_lote": len(saldos_finais),
        "qtd_pagamentos_replay_por_chave": len(pagamentos),
        "qtd_pagamentos_replay_linhas": len(log),
        "qtd_pagamentos_replay_chaves_unicas": len(pagamentos),
        "pagamentos_replay_sem_colisao": colisoes == 0,
        "qtd_colisoes_chave_pagamento": colisoes,
        "qtd_aplicacoes_por_lote": len(aplic),
        "qtd_aplicacoes_por_lote_preenchidas": qtd_aplic_preenchidas,
        "aplicacoes_por_lote_sem_vazios": aplic_sem_vazios,
        "qtd_produtos_por_lote": len(prod),
        "qtd_valores_originais_por_lote": len(orig),
        "qtd_valores_originais_por_lote_positivos": qtd_orig_positivos,
        "valores_originais_por_lote_validos": orig_validos,
        "qtd_valores_sacados_por_lote": len(valores_sacados),
        "qtd_lotes_ativos_observaveis": len(lotes_ativos),
        "qtd_lotes_exauridos_observaveis": len(lotes_exauridos),
        "qtd_pagamentos_realizados_observaveis": len(pagamentos_realizados),
        "origem_lotes_ativos_exauridos": origem,
    }

    return SnapshotSituacaoAtualOficial(
        versao=VERSAO_SITUACAO_ATUAL_OFICIAL,
        data_referencia=getattr(contexto, "data_referencia", None),
        saldos_finais_replay_por_lote=saldos_finais,
        pagamentos_replay_por_chave=pagamentos,
        aplicacoes_por_lote=aplic,
        produtos_por_lote=prod,
        valores_originais_por_lote=orig,
        valores_sacados_por_lote=valores_sacados,
        lotes_ativos_observaveis=lotes_ativos,
        lotes_exauridos_observaveis=lotes_exauridos,
        pagamentos_realizados_observaveis=pagamentos_realizados,
        auditoria_situacao_atual_oficial=auditoria,
        validacao_situacao_atual_oficial=validacao,
        metadados_origem={"origem_lotes_ativos_exauridos": origem},
    )


def construir_situacao_atual_oficial(contexto: Any, saida: Any, estado_temporal_inicial: Any | None = None) -> SimpleNamespace:
    """Monta a Situação Atual oficial sem o contrato transitório pré-ME-518B."""
    lotes_ativos = _montar_lotes_consolidados_oficial(
        contexto,
        saida,
        tipo='ativos',
        modo_bootstrap_snapshot=True,
    )
    snapshot_semente = _construir_snapshot_situacao_atual_oficial(
        contexto,
        saida,
        lotes_ativos_observaveis=lotes_ativos,
    )
    lotes_exauridos = _montar_lotes_consolidados_oficial(
        contexto,
        saida,
        tipo='exauridos',
        snapshot_situacao_atual=snapshot_semente,
    )
    snapshot_final = _construir_snapshot_situacao_atual_oficial(
        contexto,
        saida,
        lotes_ativos_observaveis=lotes_ativos,
        lotes_exauridos_observaveis=lotes_exauridos,
        pagamentos_realizados_observaveis=list(getattr(saida, 'extrato_passado', []) or []),
    )
    blocos = _montar_blocos_situacao_atual_oficial(
        contexto,
        saida,
        snapshot_situacao_atual=snapshot_final,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    return SimpleNamespace(
        fechamento_atual=list(getattr(saida, 'fechamento_atual', []) or []),
        resumo_recebidos=list(getattr(saida, 'resumo_recebidos', []) or []),
        recebidos_atuais=list(getattr(saida, 'recebidos_atuais', []) or []),
        situacao_atual_blocos=blocos,
        auditoria_situacao_atual_oficial=snapshot_final.auditoria_situacao_atual_oficial,
        validacao_situacao_atual_oficial=snapshot_final.validacao_situacao_atual_oficial,
    )
