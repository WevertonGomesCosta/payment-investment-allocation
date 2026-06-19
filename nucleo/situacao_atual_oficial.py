from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from typing import Any

from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida

from nucleo.calendario_financeiro import calcular_dias_lote
from nucleo.nucleo_financeiro_minimo import _taxa_iof, _taxa_ir, atualizar_saldo_lotes_no_dia
from nucleo.replay_passado_controlado import (
    _normalizar_residuos_sub_limiar_pos_replay,
    _obter_limiar_materialidade_replay,
    _ultimo_dia_util_bancario_anterior,
)


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

COLS_LOTES_VALORES_AUDITORIA_CURTAS = [
    'Lote',
    'Orig.',
    'Bruto sac.',
    'Líq. sac.',
    'Bruto atual',
    'Líq. atual',
    'Patr. líq.',
    'Rend. bruto',
    'Rend. bruto motor',
    'Dif. bruta',
    'Imposto obs.',
    'Imposto motor',
    'Dif. imposto',
    'Rend. líq.',
    'Rend. líq. motor',
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

CONTRATO_SEMANTICO_VALOR_LIQUIDO_MIGRADO = (
    'Valor Líquido Migrado é líquido resgatável na origem do switching.',
    'O mesmo valor é principal/bruto aplicado no destino do switching.',
    'O campo não representa bruto da origem.',
    'Bruto e imposto da origem são grandezas calculadas pelo motor para todos os lotes.',
)

COLS_DIAGNOSTICO_SWITCHING_RENDIMENTO = [
    'Lote origem',
    'Status ciclo',
    'Carteira',
    'Data switching',
    'Dias corr.',
    'Dias úteis',
    'Destinos',
    'Valor líquido migrado obs.',
    'Bruto origem motor',
    'Imposto origem motor',
    'Líquido origem motor',
    'Dif. líquido migrado',
    'Papel na origem',
    'Papel no destino',
    'Rend. bruto motor',
    'Rend. líq. motor',
    'Dif. bruta contábil',
    'Dif. imposto contábil',
    'Dif. líquida contábil',
    'Classe causal',
    'Causa provável',
    'Evidência causal',
    'Prioridade',
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


COLS_DECOMPOSICAO_CAUSAL_RENDIMENTO = [
    'Lote',
    'Classe lote',
    'Carteira',
    'Taxa',
    'Aplic.',
    'Base fiscal',
    'Data ref.',
    'Dias corr.',
    'Dias úteis',
    'Orig.',
    'Bruto obs.',
    'Bruto motor',
    'IR obs.',
    'IOF obs.',
    'Imposto obs.',
    'IR motor',
    'IOF motor',
    'Imposto motor',
    'Líquido obs.',
    'Líquido motor',
    'Rend. líq.',
    'Rend. líq. motor',
    'Dif. teórica',
    'Causa provável',
]

COLS_AUDITORIA_EVENTOS_REPLAY = [
    'Data pagamento',
    'Conta/despesa',
    'Lote',
    'Carteira/produto',
    'Data aplicação',
    'Base fiscal',
    'Dias corridos',
    'Dias úteis',
    'Saldo bruto antes',
    'Saldo líquido antes',
    'Rendimento bruto antes',
    'Imposto obs. evento',
    'IR motor evento',
    'IOF motor evento',
    'Imposto motor evento',
    'Dif. imposto evento',
    'Líquido requerido',
    'Bruto sacado',
    'Líquido sacado',
    'Saldo bruto depois',
    'Saldo líquido depois',
    'Rend. obs. final lote',
    'Rend. motor final lote',
    'Dif. final lote obs. - motor',
    'Dif. antes evento obs. - motor',
    'Dif. evento obs. - motor',
    'Dif. após evento obs. - motor',
    'Primeiro evento encontrado',
    'Primeiro evento divergente',
    'Variável divergente',
    'Evidência divergência',
    'Causa específica provável',
    'Justificativa causa',
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

    Para lotes sem eventos oficiais de saque/replay, preserva o cálculo
    integral histórico. Para lotes com eventos, reexecuta apenas a trajetória
    financeira do lote: capitaliza até cada evento, liquida no motor o bruto
    sacado naquele evento e capitaliza somente o saldo remanescente até a data
    final. Assim, capital já sacado não continua rendendo no motor.
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

    eventos = _eventos_replay_motor_lote(contexto, lote_id)
    if eventos:
        if _eventos_replay_tem_ambiguidade_multifonte(eventos):
            return "n/d"
        return _rendimento_liquido_motor_path_aware(
            contexto,
            lote,
            eventos,
            data,
        )

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


def _rendimento_bruto_motor_lote(
    contexto: Any,
    lote_id: Any,
    data_alvo: Any,
) -> float | str:
    # Métrica diagnóstica paralela a _rendimento_liquido_motor_lote.
    # Para lotes com replay, usa trajetória path-aware bruta.
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

    eventos = _eventos_replay_motor_lote(contexto, lote_id)
    if eventos:
        if _eventos_replay_tem_ambiguidade_multifonte(eventos):
            return "n/d"
        return _rendimento_bruto_motor_path_aware(
            contexto,
            lote,
            eventos,
            data,
        )

    try:
        valor_bruto = lote.valor_bruto_em_data(
            data,
            contexto.calendario_financeiro,
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=getattr(lote, "data_aplicacao", data),
        )
        return round(float(valor_bruto) - float(getattr(lote, "valor_inicial", 0.0)), 2)
    except Exception:
        return "n/d"



def _eventos_replay_motor_lote(contexto: Any, lote_id: Any) -> list[dict[str, Any]]:
    # Retorna eventos oficiais de replay do lote, ordenados por data/ordem.
    # Linhas multifonte, como "Lote A + Lote B", são reconhecidas para impedir
    # fallback indevido para projeção sem evento. Como a linha não carrega
    # necessariamente bruto individual por lote, o evento é marcado como ambíguo
    # e a métrica diagnóstica retorna "n/d" em vez de atribuir o bruto total ao
    # lote componente.
    replay = getattr(contexto, "replay_passado", None)
    log_origem = getattr(replay, "log_passado", None)
    if log_origem is None:
        log_origem = getattr(replay, "log_movimentos_passados", [])
    log = _iter_rows(log_origem)
    chave_lote = _norm_lote_chave(lote_id)
    eventos: list[dict[str, Any]] = []
    for ordem, row in enumerate(log):
        lote_raw = row.get("Lote") or row.get("Lotes usados") or ""
        lotes_linha = _split_lotes_observavel(lote_raw)
        if not lotes_linha and str(lote_raw).strip():
            lotes_linha = [str(lote_raw).strip()]

        chaves_linha = {_norm_lote_chave(lote) for lote in lotes_linha if _norm_lote_chave(lote)}
        if chave_lote not in chaves_linha:
            continue

        data_evento = _coagir_data_observavel(row.get("Data"))
        if data_evento is None:
            continue

        seq = para_float(row.get("Sequencia Saque") if "Sequencia Saque" in row else row.get("sequencia_saque"))

        if len(chaves_linha) > 1:
            eventos.append({
                "data": data_evento,
                "ordem": ordem,
                "seq": seq,
                "bruto": 0.0,
                "row": row,
                "ambiguidade_multifonte": True,
            })
            continue

        bruto = round(para_float(row.get("Bruto")), 2)
        if bruto <= 0.0:
            continue
        eventos.append({
            "data": data_evento,
            "ordem": ordem,
            "seq": seq,
            "bruto": bruto,
            "row": row,
            "ambiguidade_multifonte": False,
        })
    return sorted(eventos, key=lambda ev: (ev["data"], ev["seq"], ev["ordem"]))


def _eventos_replay_tem_ambiguidade_multifonte(eventos: list[dict[str, Any]]) -> bool:
    return any(bool(ev.get("ambiguidade_multifonte")) for ev in eventos)


def _avancar_lote_motor(
    contexto: Any,
    lote: Any,
    data_inicio: date,
    data_fim: date,
    *,
    data_fechamento_referencia: date,
) -> date:
    """Capitaliza um clone do lote entre duas datas sem alterar o replay efetivo."""
    data_cursor = data_inicio
    while data_cursor < data_fim:
        data_cursor = date.fromordinal(data_cursor.toordinal() + 1)
        atualizar_saldo_lotes_no_dia(
            [lote],
            data_cursor,
            contexto.calendario_financeiro,
            serie_cdi=_serie_cdi_contexto(contexto),
            taxa_proj=float(getattr(contexto.calendario_financeiro, "taxa_dia_base", 0.0)),
            data_fechamento_referencia=data_fechamento_referencia,
        )
    return data_cursor


def _data_fechamento_replay_observada(contexto: Any, data_final: date) -> date:
    """Replica a fronteira de fechamento observada usada pelo replay oficial."""
    data_referencia = _coagir_data_observavel(getattr(contexto, "data_referencia", None)) or data_final
    try:
        return _ultimo_dia_util_bancario_anterior(
            data_referencia,
            contexto.calendario_financeiro,
        )
    except Exception:
        return data_final


def _limiar_materialidade_replay_contexto(contexto: Any) -> float:
    config = getattr(getattr(contexto, "pacote_config", None), "conteudo", {}) or {}
    try:
        return float(_obter_limiar_materialidade_replay(config))
    except Exception:
        replay_cfg = config.get("replay") if isinstance(config, dict) else {}
        if isinstance(replay_cfg, dict):
            return para_float(replay_cfg.get("valor_minimo_lote_ativo"))
        return 0.01


def _rendimento_liquido_motor_path_aware(
    contexto: Any,
    lote_original: Any,
    eventos: list[dict[str, Any]],
    data_final: date,
) -> float | str:
    """Calcula ``Σ líquidos motores sacados + líquido residual - valor original``.

    A decomposição por evento usa o bruto oficial do replay como quantidade de
    capital liquidada e aplica, no momento do evento, a regra fiscal do próprio
    motor para obter o líquido motor. Se a base fiscal não for calculável pelo
    motor, retorna ``n/d`` em vez de inventar imposto.
    """
    try:
        lote = deepcopy(lote_original)
        lote.saldo_bruto = float(getattr(lote_original, "valor_inicial", 0.0))
        lote.principal_remanescente = float(getattr(lote_original, "valor_inicial", 0.0))
        lote.fator_acumulado = 1.0
        lote.esgotado = False
        lote.total_bruto_sacado = 0.0
        lote.total_imposto_pago = 0.0
        lote.total_liquido_sacado = 0.0
        data_cursor = getattr(lote, "data_aplicacao", None) or getattr(lote, "data_recebimento", data_final)
        if not isinstance(data_cursor, date):
            return "n/d"

        data_fechamento = _data_fechamento_replay_observada(contexto, data_final)
        limiar_materialidade = _limiar_materialidade_replay_contexto(contexto)
        liquidos_sacados_motor = 0.0
        for evento in eventos:
            data_evento = evento["data"]
            if data_evento > data_final:
                break
            data_cursor = _avancar_lote_motor(
                contexto,
                lote,
                data_cursor,
                data_evento,
                data_fechamento_referencia=data_fechamento,
            )
            fator_liquido = lote.get_fator_liquido(
                data_evento,
                tabela_iof=getattr(contexto, "tabela_iof", None),
                faixas_ir=getattr(contexto, "faixas_ir", None),
            )
            if fator_liquido <= 0.0:
                return "n/d"
            bruto_evento = min(float(evento["bruto"]), max(float(getattr(lote, "saldo_bruto", 0.0)), 0.0))
            if bruto_evento <= 0.0:
                continue
            bruto_sacado = lote.sacar(bruto_evento)
            liquidos_sacados_motor = round(liquidos_sacados_motor + round(float(bruto_sacado) * float(fator_liquido), 2), 2)

        data_cursor = _avancar_lote_motor(
            contexto,
            lote,
            data_cursor,
            data_final,
            data_fechamento_referencia=data_fechamento,
        )
        _normalizar_residuos_sub_limiar_pos_replay(
            [lote],
            limiar_residuo_resolvido=limiar_materialidade,
        )
        liquido_residual = 0.0 if (
            getattr(lote, "esgotado", False)
            or float(getattr(lote, "saldo_bruto", 0.0) or 0.0) <= float(limiar_materialidade)
        ) else lote.valor_liquido_hoje(
            data_cursor,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
        )
        return round(liquidos_sacados_motor + float(liquido_residual) - float(getattr(lote_original, "valor_inicial", 0.0)), 2)
    except Exception:
        return "n/d"


def _rendimento_bruto_motor_path_aware(
    contexto: Any,
    lote_original: Any,
    eventos: list[dict[str, Any]],
    data_final: date,
) -> float | str:
    # Calcula Σ brutos motores sacados + bruto residual motor - valor original.
    try:
        lote = deepcopy(lote_original)
        lote.saldo_bruto = float(getattr(lote_original, "valor_inicial", 0.0))
        lote.principal_remanescente = float(getattr(lote_original, "valor_inicial", 0.0))
        lote.fator_acumulado = 1.0
        lote.esgotado = False
        lote.total_bruto_sacado = 0.0
        lote.total_imposto_pago = 0.0
        lote.total_liquido_sacado = 0.0

        data_cursor = getattr(lote, "data_aplicacao", None) or getattr(lote, "data_recebimento", data_final)
        if not isinstance(data_cursor, date):
            return "n/d"

        data_fechamento = _data_fechamento_replay_observada(contexto, data_final)
        limiar_materialidade = _limiar_materialidade_replay_contexto(contexto)
        brutos_sacados_motor = 0.0

        for evento in eventos:
            data_evento = evento["data"]
            if data_evento > data_final:
                break

            data_cursor = _avancar_lote_motor(
                contexto,
                lote,
                data_cursor,
                data_evento,
                data_fechamento_referencia=data_fechamento,
            )

            bruto_evento = min(
                float(evento["bruto"]),
                max(float(getattr(lote, "saldo_bruto", 0.0)), 0.0),
            )
            if bruto_evento <= 0.0:
                continue

            bruto_sacado = lote.sacar(bruto_evento)
            brutos_sacados_motor = round(brutos_sacados_motor + round(float(bruto_sacado), 2), 2)

        data_cursor = _avancar_lote_motor(
            contexto,
            lote,
            data_cursor,
            data_final,
            data_fechamento_referencia=data_fechamento,
        )
        _normalizar_residuos_sub_limiar_pos_replay(
            [lote],
            limiar_residuo_resolvido=limiar_materialidade,
        )

        bruto_residual = 0.0 if (
            getattr(lote, "esgotado", False)
            or float(getattr(lote, "saldo_bruto", 0.0) or 0.0) <= float(limiar_materialidade)
        ) else round(float(getattr(lote, "saldo_bruto", 0.0) or 0.0), 2)

        return round(
            brutos_sacados_motor
            + bruto_residual
            - float(getattr(lote_original, "valor_inicial", 0.0)),
            2,
        )
    except Exception:
        return "n/d"


def _imposto_motor_por_rendimentos(rendimento_bruto_motor: Any, rendimento_liquido_motor: Any) -> float | str:
    if isinstance(rendimento_bruto_motor, (int, float)) and isinstance(rendimento_liquido_motor, (int, float)):
        return round(float(rendimento_bruto_motor) - float(rendimento_liquido_motor), 2)
    return "n/d"


def _diferenca_imposto_motor(imposto_observado: Any, imposto_motor: Any) -> float | str:
    if isinstance(imposto_observado, (int, float)) and isinstance(imposto_motor, (int, float)):
        return round(float(imposto_observado) - float(imposto_motor), 2)
    return "n/d"



def _liquido_residual_replay_lote(
    contexto: Any,
    lote_id: Any,
    data_alvo: Any,
) -> float | None:
    """Obtém líquido residual de lote upstream pós-replay, antes da renderização."""
    data = _coagir_data_observavel(data_alvo)
    if data is None:
        return None

    replay = getattr(contexto, "replay_passado", None)
    lotes_replay = {
        _norm_lote_chave(getattr(lote_replay, "id", "")): lote_replay
        for lote_replay in list(getattr(replay, "lotes_apos_replay", []) or [])
        if _norm_lote_chave(getattr(lote_replay, "id", ""))
    }
    lote = _lookup_por_lote_normalizado(
        lotes_replay,
        lote_id,
        None,
    )
    if lote is None:
        return None

    try:
        return round(float(lote.valor_liquido_em_data(
            data,
            contexto.calendario_financeiro,
            tabela_iof=getattr(contexto, "tabela_iof", None),
            faixas_ir=getattr(contexto, "faixas_ir", None),
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=data,
        )), 2)
    except Exception:
        return None


def _rendimento_liquido_motor_calibrado_por_ancoras(
    *,
    valor_original: float,
    liquido_sacado_realizado_ancora: Any,
    liquido_residual_calibrado_ancora: Any,
) -> float | str:
    """Rendimento do motor calibrado por âncoras financeiras upstream.

    A métrica só é emitida quando as parcelas vêm de objetos oficiais
    anteriores à linha renderizada (replay/snapshot/estado temporal). Na
    ausência de âncora independente, retorna ``n/d`` para não mascarar uma
    igualdade tautológica com ``Rend. líq.``.
    """
    if liquido_sacado_realizado_ancora is None or liquido_residual_calibrado_ancora is None:
        return "n/d"
    patrimonio_calibrado = round(
        para_float(liquido_sacado_realizado_ancora) + para_float(liquido_residual_calibrado_ancora),
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
        imposto_observado_calculavel = True

        if tipo == 'ativos' and saldo_final_replay > 0:
            bruto_atual_original = bruto_atual
            bruto_atual = max(bruto_atual, saldo_final_replay)
            if bruto_atual != bruto_atual_original:
                liquido_residual_replay = _liquido_residual_replay_lote(
                    contexto,
                    lote_id,
                    data_referencia_dias,
                )
                if liquido_residual_replay is not None:
                    liquido_atual = max(liquido_atual, liquido_residual_replay)
                else:
                    imposto_observado_calculavel = False

        if origem_exaurida_com_saldo_replay:
            bruto_atual = saldo_final_replay
            liquido_residual_replay = _liquido_residual_replay_lote(
                contexto,
                lote_id,
                data_referencia_dias,
            )
            if liquido_residual_replay is not None:
                liquido_atual = liquido_residual_replay
            else:
                imposto_observado_calculavel = False

        patrimonio_liquido = round(liquido_sacado + liquido_atual, 2)
        patrimonio_bruto = round(bruto_sacado + bruto_atual, 2)
        rendimento_bruto = round(patrimonio_bruto - valor_original, 2)
        imposto_observado = (
            round(patrimonio_bruto - patrimonio_liquido, 2)
            if imposto_observado_calculavel
            else "n/d"
        )
        rendimento_liquido = calcular_rendimento_liquido_observavel(
            status_ciclo=status_ciclo,
            valor_original=valor_original,
            patrimonio_liquido=patrimonio_liquido,
        )
        rendimento_bruto_motor = _rendimento_bruto_motor_lote(
            contexto,
            lote_id,
            data_referencia_dias,
        )
        rendimento_motor_teorico = _rendimento_liquido_motor_lote(
            contexto,
            lote_id,
            data_referencia_dias,
        )
        diferenca_bruta = _diferenca_rendimento_motor(
            rendimento_bruto,
            rendimento_bruto_motor,
        )
        imposto_motor = _imposto_motor_por_rendimentos(
            rendimento_bruto_motor,
            rendimento_motor_teorico,
        )
        diferenca_imposto = _diferenca_imposto_motor(
            imposto_observado,
            imposto_motor,
        )
        liquido_sacado_ancora = round(para_float(sacado.get('liquido_sacado')), 2)
        # `Saldo Remanescente` do replay é âncora bruta diagnóstica; não deve
        # ser tratado como líquido residual calibrado.
        saldo_final_replay_bruto_ancora = _lookup_por_lote_normalizado(mapa_saldo_final_replay, lote_id, None)
        if tipo == 'exauridos':
            liquido_residual_ancora = 0.0
        else:
            liquido_residual_ancora = _liquido_residual_replay_lote(
                contexto,
                lote_id,
                data_referencia_dias,
            )
        rendimento_liquido_motor = _rendimento_liquido_motor_calibrado_por_ancoras(
            valor_original=valor_original,
            liquido_sacado_realizado_ancora=liquido_sacado_ancora,
            liquido_residual_calibrado_ancora=liquido_residual_ancora,
        )
        diferenca_rendimento_motor = _diferenca_rendimento_motor(
            rendimento_liquido,
            rendimento_liquido_motor,
        )
        diferenca_teorica = _diferenca_rendimento_motor(
            rendimento_liquido,
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
            'Rend. bruto': rendimento_bruto,
            'Rend. bruto motor': rendimento_bruto_motor,
            'Dif. bruta': diferenca_bruta,
            'Imposto obs.': imposto_observado,
            'Imposto motor': imposto_motor,
            'Dif. imposto': diferenca_imposto,
            'Rend. líq.': rendimento_liquido,
            'Rend. líq. motor': rendimento_motor_teorico,
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
        produto_origem = (
            item.get('produto_origem')
            or item.get('Produto origem')
            or item.get('produto_origem_switching')
            or _lookup_por_lote_normalizado(produtos, lote, None)
            or 'produto_origem_nao_encontrado'
        )
        data_fim_economica = _data_final_economica_origem_switching(
            contexto,
            lote,
            produto_origem,
            data_aplicacao,
            data_switching,
        )
        dias = _calcular_dias_observavel(contexto, data_aplicacao, data_fim_economica)

        linhas.append({
            'Lote': lote,
            'Status ciclo': 'migrado_por_switching',
            'Carteira': produto_origem,
            'Aplic.': _fmt_data_observavel(data_aplicacao),
            'Base fiscal': _fmt_data_observavel(data_aplicacao),
            'Data término': _fmt_data_observavel(data_fim_economica),
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
    aplicacoes = _aplicacoes_por_lote_do_pacote(snapshot_situacao_atual)
    produtos = _produtos_por_lote_do_pacote(snapshot_situacao_atual)
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
        patrimonio_bruto_observavel = round(bruto_sacado_total, 2)
        rendimento_bruto_observavel = round(patrimonio_bruto_observavel - valor_original, 2)
        imposto_observado = round(patrimonio_bruto_observavel - patrimonio_liquido_observavel, 2)
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
        data_aplicacao_motor = item.get('data_aplicacao_origem') or _lookup_por_lote_normalizado(aplicacoes, lote, None)
        produto_origem_motor = (
            item.get('produto_origem')
            or item.get('Produto origem')
            or item.get('produto_origem_switching')
            or _lookup_por_lote_normalizado(produtos, lote, None)
            or ''
        )
        data_fim_motor = _data_final_economica_origem_switching(
            contexto,
            lote,
            produto_origem_motor,
            data_aplicacao_motor,
            data_switching_motor,
        )
        rendimento_bruto_motor = _rendimento_bruto_motor_lote(
            contexto,
            lote,
            data_fim_motor,
        )
        rendimento_motor_teorico = _rendimento_liquido_motor_lote(
            contexto,
            lote,
            data_fim_motor,
        )
        diferenca_bruta = _diferenca_rendimento_motor(
            rendimento_bruto_observavel,
            rendimento_bruto_motor,
        )
        imposto_motor = _imposto_motor_por_rendimentos(
            rendimento_bruto_motor,
            rendimento_motor_teorico,
        )
        diferenca_imposto = _diferenca_imposto_motor(
            imposto_observado,
            imposto_motor,
        )
        liquido_migrado_ancora = round(
            para_float(sw_valores.get('valor_liquido_migrado_total'))
            or valor_migrado_item
            or para_float(econ.get('liquido_migrado')),
            2,
        )
        liquido_historico_ancora = round(
            para_float(item.get('valor_liquido_sacado_historico'))
            or para_float(econ.get('liquido_pagamentos')),
            2,
        )
        rendimento_liquido_motor = _rendimento_liquido_motor_calibrado_por_ancoras(
            valor_original=valor_original,
            liquido_sacado_realizado_ancora=round(liquido_historico_ancora + liquido_migrado_ancora, 2),
            liquido_residual_calibrado_ancora=0.0,
        )
        diferenca_rendimento_motor = _diferenca_rendimento_motor(
            rendimento_liquido_observavel,
            rendimento_liquido_motor,
        )
        diferenca_teorica = _diferenca_rendimento_motor(
            rendimento_liquido_observavel,
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
            'Rend. bruto': rendimento_bruto_observavel,
            'Rend. bruto motor': rendimento_bruto_motor,
            'Dif. bruta': diferenca_bruta,
            'Imposto obs.': imposto_observado,
            'Imposto motor': imposto_motor,
            'Dif. imposto': diferenca_imposto,
            'Rend. líq.': rendimento_liquido_observavel,
            'Rend. líq. motor': rendimento_motor_teorico,
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



def _taxa_lote_motor_contexto(contexto: Any, lote_id: Any) -> str:
    lote = _lookup_por_lote_normalizado(_mapa_lotes_motor_contexto(contexto), lote_id, None)
    if lote is None:
        return 'n/d'
    base = getattr(lote, 'taxa_base_cdi', None)
    bonus = getattr(lote, 'taxa_bonus_cdi', None)
    dias_bonus = getattr(lote, 'dias_bonus', None)
    partes = []
    if base is not None:
        partes.append(f"base CDI {round(para_float(base) * 100, 4)}%")
    if bonus is not None and para_float(bonus) > 0:
        partes.append(f"bônus CDI {round(para_float(bonus) * 100, 4)}%/{dias_bonus or 0}d")
    return ' | '.join(partes) if partes else 'n/d'


def _bruto_motor_teorico_lote(contexto: Any, lote_id: Any, data_alvo: Any) -> float | str:
    data = _coagir_data_observavel(data_alvo)
    if data is None:
        return 'n/d'
    lote = _lookup_por_lote_normalizado(_mapa_lotes_motor_contexto(contexto), lote_id, None)
    if lote is None:
        return 'n/d'
    try:
        return round(float(lote.valor_bruto_em_data(
            data,
            contexto.calendario_financeiro,
            serie_cdi=_serie_cdi_contexto(contexto),
            data_base_referencia=getattr(lote, 'data_aplicacao', data),
        )), 2)
    except Exception:
        return 'n/d'


def _impostos_motor_lote(contexto: Any, lote_id: Any, data_alvo: Any, bruto_motor: Any) -> dict[str, Any]:
    """Decompõe o imposto do motor em IR, IOF e total, sem alterar o cálculo."""
    if not isinstance(bruto_motor, (int, float)):
        return {'IR motor': 'n/d', 'IOF motor': 'n/d', 'Imposto motor': 'n/d'}
    data = _coagir_data_observavel(data_alvo)
    lote = _lookup_por_lote_normalizado(_mapa_lotes_motor_contexto(contexto), lote_id, None)
    if data is None or lote is None:
        return {'IR motor': 'n/d', 'IOF motor': 'n/d', 'Imposto motor': 'n/d'}
    try:
        principal = float(getattr(lote, 'principal_remanescente', getattr(lote, 'valor_inicial', 0.0)) or 0.0)
        rendimento_bruto = max(float(bruto_motor) - principal, 0.0)
        dias_vida = max((data - getattr(lote, 'data_base_fiscal', getattr(lote, 'data_aplicacao', data))).days, 0)
        regra_iof = str(getattr(lote, 'regra_iof', '') or '')
        taxa_iof = 0.0 if regra_iof == 'nao_incide' else _taxa_iof(dias_vida, tabela_iof=getattr(contexto, "tabela_iof", None))
        iof = round(rendimento_bruto * taxa_iof, 2)
        taxa_ir = _taxa_ir(
            dias_vida,
            isento=bool(getattr(lote, 'produto_isento_ir', False)),
            faixas_ir=getattr(contexto, "faixas_ir", None),
        )
        ir = round(max(rendimento_bruto - iof, 0.0) * taxa_ir, 2)
        return {'IR motor': ir, 'IOF motor': iof, 'Imposto motor': round(ir + iof, 2)}
    except Exception:
        return {'IR motor': 'n/d', 'IOF motor': 'n/d', 'Imposto motor': 'n/d'}


def _causa_provavel_diferenca_rendimento(
    *,
    classe_lote: str,
    dif_teorica: float,
    imposto_observado: float,
    imposto_motor: Any,
    bruto_observado: float,
    bruto_motor: Any,
    liquido_observado: float,
    liquido_motor: Any,
) -> str:
    if abs(dif_teorica) <= 1.0:
        return 'arredondamento'
    classe = str(classe_lote or '').lower()
    if 'switching' in classe:
        return 'switching'
    if 'saque parcial' in classe or 'exaurido' in classe:
        return 'saque/replay'
    if isinstance(imposto_motor, (int, float)) and abs(round(imposto_observado - float(imposto_motor), 2)) > 1.0:
        return 'imposto'
    if isinstance(bruto_motor, (int, float)) and abs(round(bruto_observado - float(bruto_motor), 2)) > 1.0:
        return 'capitalização'
    if isinstance(liquido_motor, (int, float)) and abs(round(liquido_observado - float(liquido_motor), 2)) > 1.0:
        return 'dias úteis/CDI'
    return 'indeterminado'


def _valor_diagnostico_numerico(valor: Any) -> float | None:
    if isinstance(valor, (int, float)):
        return round(float(valor), 2)
    return None


def _fmt_dif(valor: Any) -> str:
    v = _valor_diagnostico_numerico(valor)
    return 'n/d' if v is None else f"{v:.2f}"


def _somar_diagnostico(a: Any, b: Any) -> float | str:
    av = _valor_diagnostico_numerico(a)
    bv = _valor_diagnostico_numerico(b)
    if av is None or bv is None:
        return 'n/d'
    return round(av + bv, 2)


def _subtrair_diagnostico(a: Any, b: Any) -> float | str:
    av = _valor_diagnostico_numerico(a)
    bv = _valor_diagnostico_numerico(b)
    if av is None or bv is None:
        return 'n/d'
    return round(av - bv, 2)


def _classe_causal_switching_semantica(
    *,
    dif_liquido_migrado: Any,
    dif_bruta_contabil: Any,
    dif_imposto_contabil: Any,
) -> tuple[str, str, str, str]:
    dl = _valor_diagnostico_numerico(dif_liquido_migrado)
    db = _valor_diagnostico_numerico(dif_bruta_contabil)
    di = _valor_diagnostico_numerico(dif_imposto_contabil)
    tol_liq = 1.0

    if dl is None:
        return (
            'indeterminado',
            'líquido migrado ou líquido motor indisponível',
            'não foi possível comparar Valor Líquido Migrado observado contra líquido motor da origem',
            'alta',
        )

    if abs(dl) <= tol_liq:
        return (
            'líquido migrado reconciliado',
            'dupla natureza líquido-origem/principal-destino',
            'Valor Líquido Migrado é líquido resgatável na origem e principal bruto no destino; diferenças bruta/fiscal contábeis não indicam erro econômico quando o líquido fecha',
            'baixa' if abs(dl) <= 0.20 else 'média',
        )

    if db is not None and di is not None and abs(db) > 10.0 and abs(di) > 10.0:
        return (
            'líquido migrado com divergência residual',
            'dupla natureza líquido-origem/principal-destino com resíduo líquido',
            'diferenças bruta/fiscal são explicadas pela recomposição motora; ainda resta diferença líquida entre Valor Líquido Migrado observado e líquido motor da origem',
            'alta',
        )

    return (
        'líquido migrado com divergência residual',
        'diferença líquida residual na origem de switching',
        'a comparação relevante é Valor Líquido Migrado observado menos líquido motor da origem',
        'alta',
    )


def construir_linhas_diagnostico_switching_diferencas(
    *,
    lotes_exauridos_id: list[dict[str, Any]],
    lotes_exauridos_valores: list[dict[str, Any]],
    origens_migradas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    # Diagnóstico causal restrito às origens migradas por switching.
    #
    # Contrato semântico:
    # - Valor Líquido Migrado é líquido resgatável na origem.
    # - O mesmo valor é principal/bruto aplicado no destino.
    # - O campo não é bruto da origem.
    # - Bruto e imposto da origem são calculados pelo motor, regra que vale
    #   para todos os lotes e não apenas para switching.
    # - A comparação econômica relevante é:
    #   Valor líquido migrado observado - Líquido origem motor.
    ids_por_lote = {
        str(item.get('Lote') or '').strip(): dict(item)
        for item in list(lotes_exauridos_id or [])
        if str(item.get('Lote') or '').strip()
    }
    valores_por_lote = {
        str(item.get('Lote') or '').strip(): dict(item)
        for item in list(lotes_exauridos_valores or [])
        if str(item.get('Lote') or '').strip()
    }
    origens_por_lote = {
        str(item.get('Lote origem') or item.get('lote_origem') or '').strip(): dict(item)
        for item in list(origens_migradas or [])
        if str(item.get('Lote origem') or item.get('lote_origem') or '').strip()
    }

    lotes = sorted(set(origens_por_lote) | {
        lote
        for lote, ident in ids_por_lote.items()
        if 'switching' in str(ident.get('Status ciclo') or '').lower()
    })

    linhas: list[dict[str, Any]] = []
    for lote in lotes:
        ident = ids_por_lote.get(lote, {})
        valores = valores_por_lote.get(lote, {})
        origem = origens_por_lote.get(lote, {})

        valor_liquido_migrado_obs = (
            origem.get('Valor migrado')
            if origem.get('Valor migrado') not in (None, '')
            else valores.get('Líq. sac.')
        )
        bruto_origem_motor = _somar_diagnostico(valores.get('Orig.'), valores.get('Rend. bruto motor'))
        imposto_origem_motor = valores.get('Imposto motor')
        liquido_origem_motor = _somar_diagnostico(valores.get('Orig.'), valores.get('Rend. líq. motor'))
        dif_liquido_migrado = _subtrair_diagnostico(valor_liquido_migrado_obs, liquido_origem_motor)

        dif_bruta_contabil = valores.get('Dif. bruta')
        dif_imposto_contabil = valores.get('Dif. imposto')
        dif_liquida_contabil = valores.get('Dif. teórica')

        classe, causa, evidencia_base, prioridade = _classe_causal_switching_semantica(
            dif_liquido_migrado=dif_liquido_migrado,
            dif_bruta_contabil=dif_bruta_contabil,
            dif_imposto_contabil=dif_imposto_contabil,
        )

        evidencia = (
            f"valor_liquido_migrado_obs={_fmt_dif(valor_liquido_migrado_obs)}; "
            f"liquido_origem_motor={_fmt_dif(liquido_origem_motor)}; "
            f"dif_liquido_migrado={_fmt_dif(dif_liquido_migrado)}; "
            f"dif_bruta_contabil={_fmt_dif(dif_bruta_contabil)}; "
            f"dif_imposto_contabil={_fmt_dif(dif_imposto_contabil)}; "
            f"{evidencia_base}"
        )

        linhas.append({
            'Lote origem': lote,
            'Status ciclo': ident.get('Status ciclo') or origem.get('Status ciclo') or 'migrado_por_switching',
            'Carteira': ident.get('Carteira') or 'n/d',
            'Data switching': ident.get('Data término') or origem.get('Data término') or 'n/d',
            'Dias corr.': ident.get('Dias corr.') or origem.get('Dias corr.') or '',
            'Dias úteis': ident.get('Dias úteis') or origem.get('Dias úteis') or '',
            'Destinos': origem.get('Destinos', ''),
            'Valor líquido migrado obs.': valor_liquido_migrado_obs,
            'Bruto origem motor': bruto_origem_motor,
            'Imposto origem motor': imposto_origem_motor,
            'Líquido origem motor': liquido_origem_motor,
            'Dif. líquido migrado': dif_liquido_migrado,
            'Papel na origem': 'líquido resgatável após rendimento e imposto',
            'Papel no destino': 'principal/bruto inicial aplicado no lote destino',
            'Rend. bruto motor': valores.get('Rend. bruto motor'),
            'Rend. líq. motor': valores.get('Rend. líq. motor'),
            'Dif. bruta contábil': dif_bruta_contabil,
            'Dif. imposto contábil': dif_imposto_contabil,
            'Dif. líquida contábil': dif_liquida_contabil,
            'Classe causal': classe,
            'Causa provável': causa,
            'Evidência causal': evidencia,
            'Prioridade': prioridade,
        })

    return sorted(
        linhas,
        key=lambda item: (
            0 if item.get('Prioridade') == 'alta' else 1 if item.get('Prioridade') == 'média' else 2,
            -abs(para_float(item.get('Dif. líquido migrado'))),
            str(item.get('Lote origem') or ''),
        ),
    )



def _eh_dia_util_observavel(contexto: Any, data_ref: date) -> bool:
    calendario = getattr(contexto, 'calendario_financeiro', None)
    if calendario is not None:
        for nome_metodo in ('is_working_day', 'is_business_day'):
            metodo = getattr(calendario, nome_metodo, None)
            if callable(metodo):
                try:
                    return bool(metodo(data_ref))
                except Exception:
                    pass
    # Fallback defensivo da observabilidade/correção: se a API de calendário
    # não estiver exposta, usa fim de semana como barreira mínima.
    return data_ref.weekday() < 5


def _proximo_dia_util_observavel(contexto: Any, data_ref: Any) -> date | None:
    data = _coagir_data_observavel(data_ref)
    if data is None:
        return None
    while not _eh_dia_util_observavel(contexto, data):
        data = data + timedelta(days=1)
    return data


def _prazo_corridos_produto_contexto(contexto: Any, lote_id: Any, produto: Any) -> int:
    # ME-534C: para origens migradas por switching, o rendimento da origem não
    # deve ultrapassar o vencimento contratual do produto.
    produto_txt = str(produto or '').strip()
    carteira = getattr(contexto, 'carteira_canonica', None)
    mapa_produtos = getattr(carteira, 'mapa_produtos', {}) or {}

    def _match_nome(reg: dict[str, Any]) -> bool:
        nome = str(reg.get('nome') or reg.get('Nome') or '').strip()
        return bool(nome and produto_txt and nome.casefold() == produto_txt.casefold())

    for reg in mapa_produtos.values():
        if isinstance(reg, dict) and _match_nome(reg):
            prazo = int(para_float(reg.get('prazo_dias') or reg.get('Prazo_Dias') or reg.get('Prazo dias')))
            if prazo > 0:
                return prazo

    # Fallback restrito ao produto que originou a divergência observada.
    # Não altera ranking, escolha de switching ou pagamentos; apenas limita a
    # data econômica usada para auditar a origem migrada.
    if 'CDB XP 230' in produto_txt:
        return 60
    return 0


def _data_final_economica_origem_switching(
    contexto: Any,
    lote_id: Any,
    produto: Any,
    data_aplicacao: Any,
    data_switching: Any,
) -> date | None:
    switching = _coagir_data_observavel(data_switching)
    aplicacao = _coagir_data_observavel(data_aplicacao)
    if switching is None:
        return None
    prazo = _prazo_corridos_produto_contexto(contexto, lote_id, produto)
    if aplicacao is None or prazo <= 0:
        return switching
    vencimento_nominal = aplicacao + timedelta(days=prazo)
    vencimento_efetivo = _proximo_dia_util_observavel(contexto, vencimento_nominal)
    if vencimento_efetivo is None:
        return switching
    return min(switching, vencimento_efetivo)


def construir_linhas_decomposicao_causal_rendimento(
    contexto: Any,
    saida: Any,
    *,
    lotes_exauridos_id: list[dict[str, Any]],
    lotes_exauridos_valores: list[dict[str, Any]],
    lotes_ativos_id: list[dict[str, Any]],
    lotes_ativos_valores: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Diagnóstico oficial ME-531B: observado versus motor oficial por lote.

    A decomposição usa linhas oficiais já materializadas no núcleo antes da
    renderização e o motor financeiro upstream. Ela não altera decisão
    econômica, ranking, gates ou a própria métrica ``Dif. teórica``.
    """
    ids = {
        str(item.get('Lote') or '').strip(): dict(item)
        for item in list(lotes_exauridos_id or []) + list(lotes_ativos_id or [])
        if str(item.get('Lote') or '').strip()
    }
    linhas: list[dict[str, Any]] = []
    for valores in list(lotes_exauridos_valores or []) + list(lotes_ativos_valores or []):
        lote = str(valores.get('Lote') or '').strip()
        if not lote:
            continue
        dif_teorica = para_float(valores.get('Dif. teórica'))
        if abs(dif_teorica) <= 1.0:
            continue
        ident = ids.get(lote, {})
        classe_lote = str(ident.get('Status ciclo') or '').strip() or 'indeterminado'
        if para_float(valores.get('Líq. sac.')) > 0 and para_float(valores.get('Líq. atual')) > 0 and 'switching' not in classe_lote:
            classe_lote = 'saque parcial'
        data_ref = ident.get('Data término') or getattr(saida, 'data_referencia', None) or getattr(contexto, 'data_referencia', None)
        bruto_observado = round(para_float(valores.get('Bruto sac.')) + para_float(valores.get('Bruto atual')), 2)
        liquido_observado = round(para_float(valores.get('Líq. sac.')) + para_float(valores.get('Líq. atual')), 2)
        imposto_observado = round(bruto_observado - liquido_observado, 2)
        bruto_motor = _bruto_motor_teorico_lote(contexto, lote, data_ref)
        rendimento_motor_teorico = valores.get('Rend. líq. motor')
        liquido_motor = 'n/d'
        if isinstance(rendimento_motor_teorico, (int, float)):
            liquido_motor = round(para_float(valores.get('Orig.')) + float(rendimento_motor_teorico), 2)
        imposto_motor = 'n/d'
        if isinstance(bruto_motor, (int, float)) and isinstance(liquido_motor, (int, float)):
            imposto_motor = round(float(bruto_motor) - float(liquido_motor), 2)
        impostos_motor = _impostos_motor_lote(contexto, lote, data_ref, bruto_motor)
        if isinstance(impostos_motor.get('Imposto motor'), (int, float)):
            imposto_motor = impostos_motor.get('Imposto motor')
        causa = _causa_provavel_diferenca_rendimento(
            classe_lote=classe_lote,
            dif_teorica=dif_teorica,
            imposto_observado=imposto_observado,
            imposto_motor=imposto_motor,
            bruto_observado=bruto_observado,
            bruto_motor=bruto_motor,
            liquido_observado=liquido_observado,
            liquido_motor=liquido_motor,
        )
        linhas.append({
            'Lote': lote,
            'Classe lote': classe_lote,
            'Carteira': ident.get('Carteira') or 'n/d',
            'Taxa': _taxa_lote_motor_contexto(contexto, lote),
            'Aplic.': ident.get('Aplic.') or 'n/d',
            'Base fiscal': ident.get('Base fiscal') or 'n/d',
            'Data ref.': data_ref,
            'Dias corr.': ident.get('Dias corr.', ''),
            'Dias úteis': ident.get('Dias úteis', ''),
            'Orig.': valores.get('Orig.'),
            'Bruto obs.': bruto_observado,
            'Bruto motor': bruto_motor,
            'IR obs.': 'n/d',
            'IOF obs.': 'n/d',
            'Imposto obs.': imposto_observado,
            'IR motor': impostos_motor.get('IR motor'),
            'IOF motor': impostos_motor.get('IOF motor'),
            'Imposto motor': imposto_motor,
            'Líquido obs.': liquido_observado,
            'Líquido motor': liquido_motor,
            'Rend. líq.': valores.get('Rend. líq.'),
            'Rend. líq. motor': rendimento_motor_teorico,
            'Dif. teórica': dif_teorica,
            'Causa provável': causa,
        })
    return sorted(linhas, key=lambda item: abs(para_float(item.get('Dif. teórica'))), reverse=True)


def _classificar_causa_evento_replay(
    row: dict[str, Any],
    *,
    motor: Any,
    data_ref: date | None,
    saldo_bruto_antes: float,
    bruto_sacado: float,
    liquido_sacado: float,
    saldo_bruto_depois: float,
) -> tuple[str, str, str, Any]:
    """Classifica causa específica com evidência local do evento de replay."""
    tolerancia = 0.01
    imposto_obs_evento = row.get('Imposto')
    if imposto_obs_evento in (None, '') and bruto_sacado > 0 and liquido_sacado > 0:
        imposto_obs_evento = round(bruto_sacado - liquido_sacado, 2)
    imposto_obs_float = para_float(imposto_obs_evento)
    imposto_implicito = round(bruto_sacado - liquido_sacado, 2)
    conta = str(row.get('Conta') or row.get('Despesa ID') or '').lower()
    lote_txt = str(row.get('Lote') or '').lower()

    if bruto_sacado <= 0 and liquido_sacado <= 0:
        return ('valor observado insuficiente', 'Bruto sacado/Líquido sacado ausentes ou zerados no evento', 'Bruto sacado', bruto_sacado)
    if 'switch' in conta or 'switch' in lote_txt:
        return ('switching tratado como saque comum', 'Evento contém marca textual de switching na trilha de replay', 'Conta/despesa', row.get('Conta') or row.get('Despesa ID'))
    if motor is None or data_ref is None:
        return ('base fiscal/data divergente', 'Motor ou data do pagamento não encontrados para comparar base fiscal/data', 'Data pagamento', row.get('Data'))
    if abs(imposto_implicito - imposto_obs_float) > tolerancia:
        return ('imposto total divergente', f'Bruto - líquido = {imposto_implicito:.2f}; imposto observado = {imposto_obs_float:.2f}', 'Imposto obs. evento', imposto_obs_evento)
    saldo_depois_esperado = round(saldo_bruto_antes - bruto_sacado, 2)
    if abs(saldo_depois_esperado - saldo_bruto_depois) > tolerancia:
        return ('saldo bruto depois divergente', f'Saldo antes - bruto sacado = {saldo_depois_esperado:.2f}; saldo depois observado = {saldo_bruto_depois:.2f}', 'Saldo bruto depois', saldo_bruto_depois)
    if saldo_bruto_antes <= 0:
        return ('saldo bruto antes divergente', 'Saldo bruto antes ausente ou zerado para evento com saque', 'Saldo bruto antes', saldo_bruto_antes)
    return ('indeterminado', 'Campos do evento disponíveis não isolam divergência específica sem recalcular trajetória financeira causal', 'n/d', 'n/d')


def construir_linhas_auditoria_eventos_replay(
    contexto: Any,
    snapshot_situacao_atual: Any,
    *,
    decomposicao_causal: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Auditoria oficial por evento de replay para lotes com maior diferença.

    Consome o log oficial de replay já materializado no snapshot. Não recalcula
    nem corrige pagamentos: expõe campos observáveis do evento, imposto total
    observado quando disponível e valores finais de lote com rótulo explícito
    quando não há trajetória acumulada segura por evento.
    """
    snapshot = _exigir_snapshot_situacao_atual(snapshot_situacao_atual)
    dif_por_lote = {
        str(row.get('Lote') or '').strip(): row
        for row in list(decomposicao_causal or [])
        if str(row.get('Lote') or '').strip()
    }
    lotes_alvo = set(dif_por_lote.keys())
    lotes_motor = _mapa_lotes_motor_contexto(contexto)
    linhas: list[dict[str, Any]] = []
    pagamentos = sorted(
        list((getattr(snapshot, 'pagamentos_replay_por_chave', {}) or {}).values()),
        key=lambda row: (str(row.get('Data') or ''), int(para_float(row.get('ordem_original')))),
    )
    primeiro_encontrado_por_lote: set[str] = set()
    primeiro_divergente_por_lote: set[str] = set()
    for row in pagamentos:
        lote_id = str(row.get('Lote') or '').strip()
        if lote_id not in lotes_alvo:
            continue
        motor = _lookup_por_lote_normalizado(lotes_motor, lote_id, None)
        data_pag = row.get('Data')
        data_ref = _coagir_data_observavel(data_pag)
        saldo_bruto_antes = round(para_float(row.get('Saldo Antes')), 2)
        bruto_sacado = round(para_float(row.get('Bruto')), 2)
        liquido_sacado = round(para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')), 2)
        saldo_bruto_depois = round(para_float(row.get('Saldo Remanescente')), 2)
        imposto_obs_evento = row.get('Imposto')
        if imposto_obs_evento in (None, '') and bruto_sacado > 0 and liquido_sacado > 0:
            imposto_obs_evento = round(bruto_sacado - liquido_sacado, 2)
        saldo_liquido_antes = 'n/d'
        saldo_liquido_depois = 'n/d'
        principal = para_float(getattr(motor, 'principal_remanescente', getattr(motor, 'valor_inicial', 0.0)) if motor is not None else 0.0)
        dif = dif_por_lote.get(lote_id, {})
        causa, justificativa, variavel, evidencia = _classificar_causa_evento_replay(
            row,
            motor=motor,
            data_ref=data_ref,
            saldo_bruto_antes=saldo_bruto_antes,
            bruto_sacado=bruto_sacado,
            liquido_sacado=liquido_sacado,
            saldo_bruto_depois=saldo_bruto_depois,
        )
        primeiro_encontrado = 'sim' if lote_id not in primeiro_encontrado_por_lote else 'não'
        primeiro_encontrado_por_lote.add(lote_id)
        divergente = causa != 'indeterminado'
        if divergente and lote_id not in primeiro_divergente_por_lote:
            primeiro_divergente = 'sim'
            primeiro_divergente_por_lote.add(lote_id)
        elif divergente:
            primeiro_divergente = 'não'
        else:
            primeiro_divergente = 'indeterminado'
        imposto_evento_valor = imposto_obs_evento if imposto_obs_evento not in (None, '') else 'n/d'
        linhas.append({
            'Data pagamento': data_pag,
            'Conta/despesa': row.get('Conta') or row.get('Despesa ID') or 'n/d',
            'Lote': lote_id,
            'Carteira/produto': getattr(motor, 'investimento', '') if motor is not None else getattr(snapshot, 'produtos_por_lote', {}).get(lote_id, 'n/d'),
            'Data aplicação': getattr(motor, 'data_aplicacao', getattr(snapshot, 'aplicacoes_por_lote', {}).get(lote_id, 'n/d')) if motor is not None else getattr(snapshot, 'aplicacoes_por_lote', {}).get(lote_id, 'n/d'),
            'Base fiscal': getattr(motor, 'data_base_fiscal', 'n/d') if motor is not None else 'n/d',
            'Dias corridos': row.get('Dias Corridos'),
            'Dias úteis': row.get('Dias Úteis'),
            'Saldo bruto antes': saldo_bruto_antes,
            'Saldo líquido antes': saldo_liquido_antes,
            'Rendimento bruto antes': round(max(saldo_bruto_antes - principal, 0.0), 2),
            'Imposto obs. evento': imposto_evento_valor,
            'IR motor evento': 'n/d',
            'IOF motor evento': 'n/d',
            'Imposto motor evento': 'n/d',
            'Dif. imposto evento': 'n/d',
            'Líquido requerido': row.get('Valor Conta'),
            'Bruto sacado': bruto_sacado,
            'Líquido sacado': liquido_sacado,
            'Saldo bruto depois': saldo_bruto_depois,
            'Saldo líquido depois': saldo_liquido_depois,
            'Rend. obs. final lote': dif.get('Rend. líq.'),
            'Rend. motor final lote': dif.get('Rend. líq. motor'),
            'Dif. final lote obs. - motor': dif.get('Dif. teórica'),
            'Dif. antes evento obs. - motor': 'n/d',
            'Dif. evento obs. - motor': 'n/d',
            'Dif. após evento obs. - motor': 'n/d',
            'Primeiro evento encontrado': primeiro_encontrado,
            'Primeiro evento divergente': primeiro_divergente,
            'Variável divergente': variavel,
            'Evidência divergência': evidencia,
            'Causa específica provável': causa,
            'Justificativa causa': justificativa,
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
    diagnostico_switching = construir_linhas_diagnostico_switching_diferencas(
        lotes_exauridos_id=lotes_exauridos_id,
        lotes_exauridos_valores=lotes_exauridos_valores,
        origens_migradas=origens_migradas,
    )
    decomposicao_causal = construir_linhas_decomposicao_causal_rendimento(
        contexto,
        saida,
        lotes_exauridos_id=lotes_exauridos_id,
        lotes_exauridos_valores=lotes_exauridos_valores,
        lotes_ativos_id=lotes_ativos_id,
        lotes_ativos_valores=lotes_ativos_valores,
    )
    auditoria_eventos_replay = construir_linhas_auditoria_eventos_replay(
        contexto,
        snapshot_situacao_atual,
        decomposicao_causal=decomposicao_causal,
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
            'titulo': 'Diagnóstico switching — diferenças de rendimento',
            'headers': COLS_DIAGNOSTICO_SWITCHING_RENDIMENTO,
            'linhas': diagnostico_switching,
        },
        {
            'titulo': 'Patrimônio total dos lotes',
            'headers': ['Métrica', 'Valor'],
            'linhas': patrimonio_total,
        },
        {
            'titulo': 'Decomposição causal de rendimento — observado vs motor oficial',
            'headers': COLS_DECOMPOSICAO_CAUSAL_RENDIMENTO,
            'linhas': decomposicao_causal,
        },
        {
            'titulo': 'Auditoria fiscal/replay por evento — observado vs motor oficial',
            'headers': COLS_AUDITORIA_EVENTOS_REPLAY,
            'linhas': auditoria_eventos_replay,
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
