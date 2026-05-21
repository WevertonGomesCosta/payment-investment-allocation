from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow

VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL = "V17-F0-V.4U"
TOL = 0.01


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


@dataclass
class PacoteSaidaObservavelTemporal:
    versao: str
    modo_execucao: str
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
    auditoria_saida_observavel_temporal: dict[str, Any]
    validacao_saida_observavel_temporal: dict[str, Any]
    metadados_origem: dict[str, Any]

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def construir_pacote_saida_observavel_temporal(
    contexto: Any,
    saida: Any,
    *,
    pacotes_temporais: Any | None = None,
    modo_execucao: str = "shadow",
    lotes_ativos_observaveis: list[dict[str, Any]] | None = None,
    lotes_exauridos_observaveis: list[dict[str, Any]] | None = None,
    pagamentos_realizados_observaveis: list[dict[str, Any]] | None = None,
) -> PacoteSaidaObservavelTemporal:
    pacotes = pacotes_temporais or construir_pacotes_temporais_agregados_saida_shadow(contexto)
    replay = getattr(pacotes, "pacote_replay_passado", None)
    log = _iter_rows(getattr(replay, "log_movimentos_passados", []))

    rows_ordenadas = sorted(list(enumerate(log)), key=lambda x: (_data_ord(x[1].get("Data")), x[0]))
    saldos_finais: dict[str, float] = {}
    pagamentos: dict[str, dict[str, Any]] = {}
    valores_sacados: dict[str, dict[str, float]] = {}
    for ordem_original, r in rows_ordenadas:
        lote = _txt(r.get("Lote"))
        if lote:
            saldos_finais[lote] = _f(r.get("Saldo Remanescente"))
        chave = "|".join([
            _data_ord(r.get("Data"))[1],
            _txt(r.get("Descrição") or r.get("Historico") or r.get("Histórico")).lower(),
            f"{_f(r.get('Valor')):.2f}",
            _lote_norm(lote),
        ])
        pagamentos[chave] = {"ordem_original": ordem_original, **r}
        if lote:
            acc = valores_sacados.setdefault(lote, {"valor_sacado_total": 0.0, "qtd_movimentos": 0.0})
            acc["valor_sacado_total"] = round(acc["valor_sacado_total"] + abs(_f(r.get("Valor"))), 2)
            acc["qtd_movimentos"] = round(acc["qtd_movimentos"] + 1.0, 2)

    origem = "snapshot_observavel_consolidado"
    if lotes_ativos_observaveis is None:
        lotes_ativos = _iter_rows(getattr(saida, "lotes_ativos", []))
        origem = "snapshot_canonico_bruto_fallback"
    else:
        lotes_ativos = list(lotes_ativos_observaveis)
    if lotes_exauridos_observaveis is None:
        lotes_exauridos = _iter_rows(getattr(saida, "lotes_exauridos", []))
        origem = "snapshot_canonico_bruto_fallback"
    else:
        lotes_exauridos = list(lotes_exauridos_observaveis)
    if pagamentos_realizados_observaveis is None:
        pagamentos_realizados = _iter_rows(getattr(saida, "extrato_passado", []))
    else:
        pagamentos_realizados = list(pagamentos_realizados_observaveis)

    lotes_base = lotes_ativos + lotes_exauridos
    aplic, prod, orig = {}, {}, {}
    for r in lotes_base:
        lote = _txt(r.get("Lote"))
        if not lote:
            continue
        aplic[lote] = r.get("Aplicação") or r.get("Aplicacao")
        prod[lote] = _txt(r.get("Produto") or r.get("Carteira"))
        orig[lote] = _f(r.get("Valor Original") or r.get("Bruto atual") or r.get("Líq. atual"))

    lote_alvo = "Lote 3120 mai"
    ativos_set = {_lote_norm(r.get("Lote")) for r in lotes_ativos}
    ex_set = {_lote_norm(r.get("Lote")) for r in lotes_exauridos}
    saldo_3120 = saldos_finais.get(lote_alvo, 0.0)

    erros = []
    if not saldos_finais: erros.append("saldos_finais_replay_por_lote_vazio")
    if not pagamentos: erros.append("pagamentos_replay_por_chave_vazio")
    if not lotes_ativos: erros.append("lotes_ativos_observaveis_vazio")
    if not lotes_exauridos: erros.append("lotes_exauridos_observaveis_vazio")
    if _lote_norm(lote_alvo) not in ativos_set: erros.append("lote_3120_mai_ausente_ativos")
    if _lote_norm(lote_alvo) in ex_set: erros.append("lote_3120_mai_presente_exauridos")
    if abs(saldo_3120 - 50.52) > TOL: erros.append("lote_3120_mai_saldo_final_incompativel")
    if ativos_set & ex_set: erros.append("lotes_duplicados_ativos_exauridos")
    if origem != "snapshot_observavel_consolidado": erros.append("origem_lotes_ativos_exauridos_fallback")

    validacao = {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": ["etapa5_pode_abrir_agora=False"],
        "evidencias": {"origem_lotes_ativos_exauridos": origem, "lote_3120_mai_saldo_final": saldo_3120},
    }
    auditoria = {
        "ok": len(erros) == 0,
        "versao_microetapa": VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL,
        "modo_shadow": modo_execucao == "shadow",
        "origem_execucao": "construir_pacote_saida_observavel_temporal",
        "contrato_alvo": "PacoteSaidaObservavelTemporal",
        "usa_pacotes_temporais_agregados": True,
        "usa_saida_apenas_como_snapshot_observavel": True,
        "nao_importa_saida_observavel": True,
        "nao_altera_saida_observavel": True,
        "nao_altera_saida_canonica": True,
        "nao_altera_replay_efetivo": True,
        "nao_altera_ledger_efetivo": True,
        "qtd_saldos_finais_replay_por_lote": len(saldos_finais),
        "qtd_pagamentos_replay_por_chave": len(pagamentos),
        "qtd_aplicacoes_por_lote": len(aplic),
        "qtd_produtos_por_lote": len(prod),
        "qtd_valores_originais_por_lote": len(orig),
        "qtd_valores_sacados_por_lote": len(valores_sacados),
        "qtd_lotes_ativos_observaveis": len(lotes_ativos),
        "qtd_lotes_exauridos_observaveis": len(lotes_exauridos),
        "qtd_pagamentos_realizados_observaveis": len(pagamentos_realizados),
        "lote_3120_mai_saldo_final": saldo_3120,
        "lote_3120_mai_presente_ativos_snapshot": _lote_norm(lote_alvo) in ativos_set,
        "lote_3120_mai_presente_exauridos_snapshot": _lote_norm(lote_alvo) in ex_set,
        "prepara_migracao_v4v": origem == "snapshot_observavel_consolidado" and validacao["ok"],
        "prepara_remocao_helpers_v4w": True,
        "origem_lotes_ativos_exauridos": origem,
    }

    return PacoteSaidaObservavelTemporal(
        versao=VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL,
        modo_execucao=modo_execucao,
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
        auditoria_saida_observavel_temporal=auditoria,
        validacao_saida_observavel_temporal=validacao,
        metadados_origem={"origem_lotes_ativos_exauridos": origem, "etapa5_pode_abrir_agora": False},
    )
