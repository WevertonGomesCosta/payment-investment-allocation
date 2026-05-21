from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow

VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL = "V17-F0-V.4U"
TOL = 0.01


def _norm_txt(v: Any) -> str:
    return str(v or "").strip()


def _norm_lote(v: Any) -> str:
    return _norm_txt(v).lower().replace(".", "")


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _data_iso(v: Any) -> str:
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    s = _norm_txt(v)
    if not s:
        return ""
    try:
        return datetime.fromisoformat(s).date().isoformat()
    except Exception:
        return s


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
) -> PacoteSaidaObservavelTemporal:
    pacotes = pacotes_temporais or construir_pacotes_temporais_agregados_saida_shadow(contexto)
    replay = getattr(pacotes, "pacote_replay_passado", None)
    log = _iter_rows(getattr(replay, "log_movimentos_passados", []))

    saldos_finais: dict[str, float] = {}
    pagamentos: dict[str, dict[str, Any]] = {}
    valores_sacados: dict[str, dict[str, float]] = {}

    for i, r in enumerate(log):
        lote = _norm_txt(r.get("Lote"))
        if lote:
            saldos_finais[lote] = _f(r.get("Saldo Remanescente"))
        chave = "|".join([
            _data_iso(r.get("Data")),
            _norm_txt(r.get("Descrição") or r.get("Historico") or r.get("Histórico")).lower(),
            f"{_f(r.get('Valor')):.2f}",
            _norm_lote(lote),
        ])
        pagamentos[chave] = {"ordem": i, **r}
        if lote:
            acc = valores_sacados.setdefault(lote, {"valor_sacado_total": 0.0, "qtd_movimentos": 0.0})
            acc["valor_sacado_total"] = round(acc["valor_sacado_total"] + abs(_f(r.get("Valor") or 0.0)), 2)
            acc["qtd_movimentos"] = round(acc["qtd_movimentos"] + 1.0, 2)

    ativos = _iter_rows(getattr(saida, "lotes_ativos", []))
    exauridos = _iter_rows(getattr(saida, "lotes_exauridos", []))
    realizados = _iter_rows(getattr(saida, "extrato_passado", []))

    lotes_base = ativos + exauridos
    aplicacoes = {}
    produtos = {}
    originais = {}
    for r in lotes_base:
        lote = _norm_txt(r.get("Lote"))
        if not lote:
            continue
        aplicacoes[lote] = r.get("Aplicação") or r.get("Aplicacao") or r.get("aplicacao")
        produtos[lote] = _norm_txt(r.get("Produto") or r.get("Carteira"))
        originais[lote] = _f(r.get("Valor Original") or r.get("Bruto atual") or r.get("Líquido Final") or r.get("Líquido"))

    lote3120 = "Lote 3120 mai"
    ativos_set = {_norm_lote(r.get("Lote")) for r in ativos}
    ex_set = {_norm_lote(r.get("Lote")) for r in exauridos}
    lote_ativo = next((r for r in ativos if _norm_lote(r.get("Lote")) == _norm_lote(lote3120)), None)
    saldo_3120 = saldos_finais.get(lote3120, _f((lote_ativo or {}).get("Bruto atual") or (lote_ativo or {}).get("Líq. atual")))

    auditoria = {
        "ok": True,
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
        "qtd_aplicacoes_por_lote": len(aplicacoes),
        "qtd_produtos_por_lote": len(produtos),
        "qtd_valores_originais_por_lote": len(originais),
        "qtd_valores_sacados_por_lote": len(valores_sacados),
        "qtd_lotes_ativos_observaveis": len(ativos),
        "qtd_lotes_exauridos_observaveis": len(exauridos),
        "qtd_pagamentos_realizados_observaveis": len(realizados),
        "lote_3120_mai_saldo_final": saldo_3120,
        "lote_3120_mai_presente_ativos_snapshot": _norm_lote(lote3120) in ativos_set,
        "lote_3120_mai_presente_exauridos_snapshot": _norm_lote(lote3120) in ex_set,
        "prepara_migracao_v4v": True,
        "prepara_remocao_helpers_v4w": True,
    }

    erros = []
    if not saldos_finais:
        erros.append("saldos_finais_replay_por_lote_vazio")
    if not pagamentos:
        erros.append("pagamentos_replay_por_chave_vazio")
    if not ativos:
        erros.append("lotes_ativos_observaveis_vazio")
    if not exauridos:
        erros.append("lotes_exauridos_observaveis_vazio")
    if _norm_lote(lote3120) not in ativos_set:
        erros.append("lote_3120_mai_ausente_ativos")
    if _norm_lote(lote3120) in ex_set:
        erros.append("lote_3120_mai_presente_exauridos")
    if abs(saldo_3120 - 50.52) > TOL:
        erros.append("lote_3120_mai_saldo_final_incompativel")
    if ativos_set & ex_set:
        erros.append("lotes_duplicados_ativos_exauridos")

    validacao = {
        "ok": len(erros) == 0,
        "erros_bloqueantes": erros,
        "avisos": ["etapa5_pode_abrir_agora=False", "dependencia_saida_observavel_contexto_replay_ainda_nao_removida"],
        "evidencias": {
            "lote_3120_mai_saldo_final": saldo_3120,
            "qtd_lotes_ativos": len(ativos),
            "qtd_lotes_exauridos": len(exauridos),
            "intersecao_ativos_exauridos": sorted(ativos_set & ex_set),
        },
    }

    return PacoteSaidaObservavelTemporal(
        versao=VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL,
        modo_execucao=modo_execucao,
        data_referencia=getattr(contexto, "data_referencia", None),
        saldos_finais_replay_por_lote=saldos_finais,
        pagamentos_replay_por_chave=pagamentos,
        aplicacoes_por_lote=aplicacoes,
        produtos_por_lote=produtos,
        valores_originais_por_lote=originais,
        valores_sacados_por_lote=valores_sacados,
        lotes_ativos_observaveis=ativos,
        lotes_exauridos_observaveis=exauridos,
        pagamentos_realizados_observaveis=realizados,
        auditoria_saida_observavel_temporal=auditoria,
        validacao_saida_observavel_temporal=validacao,
        metadados_origem={"usa_pacotes_temporais": True, "usa_saida_snapshot": True, "etapa5_pode_abrir_agora": False},
    )
