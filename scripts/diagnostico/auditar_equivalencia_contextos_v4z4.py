from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import (  # noqa: E402
    carregar_contexto_baseline,
    carregar_contexto_operacional_canonico,
)


MICROETAPA = "V17-F0-V.4Z4"
CAMPOS_COMUNS_RUNTIME = (
    "pacote_config",
    "execucao",
    "calendario_financeiro",
    "pacote_planilha",
    "pacote_entrada_resolvida",
    "auditoria_pacote_entrada_resolvida",
    "validacao_pre_execucao",
    "carteira_canonica",
    "dados_operacionais",
    "recebidos_auditaveis",
    "fontes_elegiveis_pagamento",
    "saldo_disponivel_geral",
    "cache_cdi",
    "nucleo_financeiro",
    "replay_passado",
    "ranking_carteira",
    "tabela_iof",
    "faixas_ir",
)
CAMPOS_DIVERGENTES_ALVO = (
    "pacote_entrada_resolvida",
    "validacao_pre_execucao",
    "fontes_elegiveis_pagamento",
    "cache_cdi",
)
CAMPOS_BASELINE_TRANSICIONAIS_PROIBIDOS_NO_CONTEXTO_CANONICO = (
    "validacao_pre_execucao_legada_shadow",
    "validacao_pre_execucao_pacote_entrada_resolvida_shadow",
    "pacote_entrada_resolvida_shadow",
    "auditoria_pacote_entrada_resolvida_shadow",
    "decisao_local_v1",
    "auditoria_temporal_decisao_local",
    "reescolha_dinamica_pos_quebra",
    "heuristica_conjunta_parcial_bloco_critico",
    "planejamento_conjunto_local_bloco_critico_v1",
    "microplanejamento_conjunto_bloco_critico_v2",
    "recomputacao_sequencial_central_v1",
    "motor_recomendacao_pagamentos_switching_v1",
    "switching_shadow",
    "switching_economico_shadow",
    "resolver_hibrido_5p_shadow",
    "benchmark_agrupado_individual_shadow",
    "benchmark_runner_futuro_shadow",
    "auditoria_runner_futuro_shadow",
    "auditoria_primeira_quebra_runner_futuro_shadow",
    "triagem_motor",
)
CHAVES_METADADOS = {
    "metadados",
    "metadata",
    "evidencias",
    "evidências",
    "observacoes",
    "observações",
    "avisos",
    "mensagens",
}


def _shape(obj: Any) -> Any:
    shape = getattr(obj, "shape", None)
    if shape is None:
        return None
    try:
        return list(shape)
    except Exception:
        return str(shape)


def _len(obj: Any) -> int | None:
    try:
        return len(obj)  # type: ignore[arg-type]
    except Exception:
        return None


def _safe_attr_raw(obj: Any, attr: str) -> Any:
    if not hasattr(obj, attr):
        return None
    try:
        return getattr(obj, attr)
    except Exception as exc:
        return {"erro_attr": str(exc)}


def _safe_attr(obj: Any, attr: str) -> Any:
    return _serializar_simples(_safe_attr_raw(obj, attr))


def _serializar_simples(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    if isinstance(value, dict):
        return {str(k): _serializar_simples(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple, set)):
        return [_serializar_simples(v) for v in list(value)[:100]]
    return str(value)


def _dataclass_field_names(obj: Any) -> list[str]:
    if not is_dataclass(obj):
        return []
    try:
        return sorted(asdict(obj).keys())
    except Exception:
        return []


def _asdict_safe(obj: Any) -> dict[str, Any]:
    if not is_dataclass(obj):
        return {}
    try:
        return asdict(obj)
    except Exception:
        return {}


def _round_float(value: Any) -> float:
    try:
        return round(float(value), 8)
    except Exception:
        return 0.0


def _numeric_totals_dataframe(obj: Any) -> dict[str, float]:
    try:
        numeric = obj.select_dtypes(include="number")
    except Exception:
        return {}
    try:
        sums = numeric.sum(numeric_only=True)
    except Exception:
        return {}
    return {str(col): _round_float(val) for col, val in sums.items()}


def _sample_rows_dataframe(obj: Any, max_rows: int = 5) -> list[dict[str, Any]]:
    if not hasattr(obj, "head") or not hasattr(obj, "to_dict"):
        return []
    try:
        return _serializar_simples(obj.head(max_rows).to_dict(orient="records"))
    except Exception:
        return []


def _dataframe_summary(obj: Any) -> dict[str, Any]:
    resumo: dict[str, Any] = {
        "type": type(obj).__name__,
        "shape": _shape(obj),
        "len": _len(obj),
        "columns": [],
        "numeric_totals": {},
        "sample_rows": [],
    }
    if hasattr(obj, "columns"):
        try:
            resumo["columns"] = [str(c) for c in list(obj.columns)]
        except Exception:
            pass
    if hasattr(obj, "select_dtypes"):
        resumo["numeric_totals"] = _numeric_totals_dataframe(obj)
    resumo["sample_rows"] = _sample_rows_dataframe(obj)
    return resumo


def _serie_summary(serie: Any) -> dict[str, Any]:
    resumo: dict[str, Any] = {
        "type": type(serie).__name__,
        "shape": _shape(serie),
        "len": _len(serie),
    }
    if serie is None:
        return resumo
    try:
        if hasattr(serie, "index") and len(serie) > 0:
            resumo["primeira_data"] = _serializar_simples(serie.index.min())
            resumo["ultima_data"] = _serializar_simples(serie.index.max())
    except Exception as exc:
        resumo["erro_datas"] = str(exc)
    try:
        if len(serie) > 0:
            ultimo = serie.iloc[-1] if hasattr(serie, "iloc") else list(serie)[-1]
            resumo["ultimo_valor"] = _round_float(ultimo)
    except Exception as exc:
        resumo["erro_ultimo_valor"] = str(exc)
    try:
        if hasattr(serie, "sum"):
            resumo["soma"] = _round_float(serie.sum())
    except Exception:
        pass
    return resumo


def _fingerprint_resumido(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return value.as_posix()
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    shape = _shape(value)
    if shape is not None:
        resumo = {"type": type(value).__name__, "shape": shape}
        if hasattr(value, "columns"):
            try:
                resumo["columns"] = [str(c) for c in list(value.columns)]
            except Exception:
                pass
        return resumo
    length = _len(value)
    if length is not None and not isinstance(value, (str, bytes)):
        return {"type": type(value).__name__, "len": length}
    return {"type": type(value).__name__}


def _object_fingerprint(obj: Any) -> dict[str, Any]:
    fp: dict[str, Any] = {
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "shape": _shape(obj),
        "len": _len(obj),
        "dataclass_fields": _dataclass_field_names(obj),
    }

    if hasattr(obj, "shape") and hasattr(obj, "columns"):
        fp["dataframe"] = _dataframe_summary(obj)

    for attr in (
        "ok",
        "data_referencia",
        "origem",
        "status",
        "status_obtencao",
        "raiz_repositorio",
        "caminho_config",
        "versao",
        "erros_bloqueantes",
        "avisos",
    ):
        valor = _safe_attr(obj, attr)
        if valor is not None:
            fp[attr] = valor

    if hasattr(obj, "serie_cdi"):
        fp["serie_cdi"] = _serie_summary(_safe_attr_raw(obj, "serie_cdi"))

    if is_dataclass(obj):
        data = _asdict_safe(obj)
        fp["dataclass_resumo"] = {
            k: _fingerprint_resumido(v)
            for k, v in sorted(data.items(), key=lambda kv: str(kv[0]))
            if not str(k).lower().endswith("shadow")
        }
    return fp


def _comparar_fingerprints(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    chaves = sorted(set(a) | set(b))
    diferencas = {}
    for chave in chaves:
        if a.get(chave) != b.get(chave):
            diferencas[chave] = {"baseline": a.get(chave), "canonico": b.get(chave)}
    return {"equivalente": not diferencas, "diferencas": diferencas}


def _comparar_campo(nome: str, baseline: Any, canonico: Any) -> dict[str, Any]:
    existe_baseline = hasattr(baseline, nome)
    existe_canonico = hasattr(canonico, nome)
    if not existe_baseline or not existe_canonico:
        return {
            "campo": nome,
            "existe_baseline": existe_baseline,
            "existe_canonico": existe_canonico,
            "equivalente": False,
            "motivo": "campo ausente em um dos contextos",
        }

    valor_baseline = getattr(baseline, nome)
    valor_canonico = getattr(canonico, nome)
    fp_baseline = _object_fingerprint(valor_baseline)
    fp_canonico = _object_fingerprint(valor_canonico)
    comparacao = _comparar_fingerprints(fp_baseline, fp_canonico)
    return {
        "campo": nome,
        "existe_baseline": True,
        "existe_canonico": True,
        "equivalente": comparacao["equivalente"],
        "fingerprint_baseline": fp_baseline,
        "fingerprint_canonico": fp_canonico,
        "diferencas": comparacao["diferencas"],
    }


def _auditar_campos_proibidos(canonico: Any) -> dict[str, Any]:
    presentes = [campo for campo in CAMPOS_BASELINE_TRANSICIONAIS_PROIBIDOS_NO_CONTEXTO_CANONICO if hasattr(canonico, campo)]
    return {
        "campos_proibidos_presentes_no_canonico": presentes,
        "canonico_sem_campos_transicionais": not presentes,
    }


def _dict_keys_diff(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ka = {str(k) for k in a}
    kb = {str(k) for k in b}
    common = sorted(ka & kb)
    changed = []
    for key in common:
        if _serializar_simples(a.get(key)) != _serializar_simples(b.get(key)):
            changed.append(key)
    return {
        "somente_baseline": sorted(ka - kb),
        "somente_canonico": sorted(kb - ka),
        "comuns_alteradas": sorted(changed),
    }


def _classificacao_por_diferencas(diferencas: dict[str, Any], chaves_operacionais: set[str]) -> str:
    if not diferencas:
        return "equivalente"
    chaves = set(diferencas)
    if chaves <= CHAVES_METADADOS:
        return "documental"
    if chaves.isdisjoint(chaves_operacionais):
        return "estrutural"
    return "operacional"


def _validation_evidencias(ctx: Any) -> dict[str, Any]:
    validacao = _safe_attr_raw(ctx, "validacao_pre_execucao")
    evidencias = _safe_attr_raw(validacao, "evidencias")
    return evidencias if isinstance(evidencias, dict) else {}


def _extrair_proveniencia_entrada(ctx: Any) -> dict[str, Any]:
    evid = _validation_evidencias(ctx)
    pacote_cache = _safe_attr_raw(_safe_attr_raw(ctx, "pacote_entrada_resolvida"), "pacote_cache_cdi")
    cache = _safe_attr_raw(ctx, "cache_cdi")
    pacote_planilha = _safe_attr_raw(_safe_attr_raw(ctx, "pacote_entrada_resolvida"), "pacote_planilha")
    return {
        "planilha_fonte": evid.get("planilha_fonte") or _safe_attr(pacote_planilha, "fonte"),
        "planilha_fetch_status": evid.get("planilha_fetch_status") or _safe_attr(pacote_planilha, "fetch_status"),
        "auditoria_entrada_bruta_fonte_planilha": evid.get("auditoria_entrada_bruta_fonte_planilha"),
        "auditoria_entrada_bruta_fetch_status": evid.get("auditoria_entrada_bruta_fetch_status"),
        "janela_cdi_data_inicial_consulta": evid.get("janela_cdi_data_inicial_consulta"),
        "janela_cdi_data_final_consulta": evid.get("janela_cdi_data_final_consulta"),
        "cache_cdi_data_inicial_consulta": _serializar_simples(_safe_attr_raw(pacote_cache, "data_inicial_consulta") or _safe_attr_raw(cache, "data_inicial_consulta")),
        "cache_cdi_data_final_consulta": _serializar_simples(_safe_attr_raw(pacote_cache, "data_final_consulta") or _safe_attr_raw(cache, "data_final_consulta")),
        "cache_cdi_qtd_datas_serie": evid.get("cache_cdi_qtd_datas_serie") or evid.get("auditoria_cache_cdi_qtd_datas"),
        "cache_cdi_ultima_data_serie": evid.get("cache_cdi_ultima_data_serie"),
        "cache_cdi_fonte_serie": evid.get("auditoria_cache_cdi_fonte_serie"),
        "cache_cdi_fetch_status": evid.get("auditoria_cache_cdi_fetch_status"),
    }


def _comparar_proveniencia_entrada(baseline_ctx: Any, canonico_ctx: Any) -> dict[str, Any]:
    baseline = _extrair_proveniencia_entrada(baseline_ctx)
    canonico = _extrair_proveniencia_entrada(canonico_ctx)
    chaves_divergentes = sorted(k for k in sorted(set(baseline) | set(canonico)) if baseline.get(k) != canonico.get(k))
    causas = []
    if baseline.get("planilha_fonte") != canonico.get("planilha_fonte") or baseline.get("auditoria_entrada_bruta_fonte_planilha") != canonico.get("auditoria_entrada_bruta_fonte_planilha"):
        causas.append("fonte_planilha_divergente")
    if baseline.get("planilha_fetch_status") != canonico.get("planilha_fetch_status") or baseline.get("auditoria_entrada_bruta_fetch_status") != canonico.get("auditoria_entrada_bruta_fetch_status"):
        causas.append("status_download_planilha_divergente")
    if baseline.get("cache_cdi_data_inicial_consulta") != canonico.get("cache_cdi_data_inicial_consulta"):
        causas.append("janela_cache_cdi_inicial_divergente")
    if baseline.get("cache_cdi_qtd_datas_serie") != canonico.get("cache_cdi_qtd_datas_serie"):
        causas.append("tamanho_serie_cdi_divergente")
    return {
        "baseline": baseline,
        "canonico": canonico,
        "chaves_divergentes": chaves_divergentes,
        "causas_provaveis": sorted(set(causas)),
        "proveniencia_equivalente": not chaves_divergentes,
    }


def _detalhar_pacote_entrada_resolvida(baseline: Any, canonico: Any, diferencas: dict[str, Any]) -> dict[str, Any]:
    db = _asdict_safe(baseline)
    dc = _asdict_safe(canonico)
    diff = _dict_keys_diff(db, dc)
    chaves_operacionais = {"pacote_config", "contexto_execucao", "pacote_planilha", "pacote_cache_cdi"}
    operacionais_alteradas = sorted([k for k in diff["comuns_alteradas"] if k in chaves_operacionais])
    classificacao = "documental" if not operacionais_alteradas else "operacional"
    return {
        "campo": "pacote_entrada_resolvida",
        "classificacao_divergencia": classificacao,
        "impacta_runtime": bool(operacionais_alteradas),
        "chaves_operacionais_alteradas": operacionais_alteradas,
        "chaves_diff": diff,
        "resumo_baseline": _object_fingerprint(baseline),
        "resumo_canonico": _object_fingerprint(canonico),
        "diferencas_fingerprint": diferencas,
        "interpretacao": "Divergência documental/metadados se apenas metadados/evidências mudaram; operacional se planilha ou cache diferirem.",
    }


def _detalhar_validacao_pre_execucao(baseline: Any, canonico: Any, diferencas: dict[str, Any]) -> dict[str, Any]:
    attrs = ("ok", "erros_bloqueantes", "avisos", "evidencias", "metadados")
    resumo_b = {attr: _safe_attr(baseline, attr) for attr in attrs if hasattr(baseline, attr)}
    resumo_c = {attr: _safe_attr(canonico, attr) for attr in attrs if hasattr(canonico, attr)}
    campos_operacionais = {"ok", "erros_bloqueantes"}
    divergentes = {k for k in set(resumo_b) | set(resumo_c) if resumo_b.get(k) != resumo_c.get(k)}
    classificacao = "documental" if divergentes.isdisjoint(campos_operacionais) else "bloqueante"
    return {
        "campo": "validacao_pre_execucao",
        "classificacao_divergencia": classificacao,
        "impacta_runtime": not divergentes.isdisjoint(campos_operacionais),
        "atributos_divergentes": sorted(divergentes),
        "resumo_baseline": resumo_b,
        "resumo_canonico": resumo_c,
        "diferencas_fingerprint": diferencas,
        "interpretacao": "Divergência é bloqueante se ok ou erros_bloqueantes diferirem; avisos/evidências/metadados tendem a ser documentais.",
    }


def _quadro_fontes(obj: Any) -> Any:
    return _safe_attr_raw(obj, "quadro_fontes_elegiveis")


def _detalhar_fontes_elegiveis(baseline: Any, canonico: Any, diferencas: dict[str, Any]) -> dict[str, Any]:
    quadro_b = _quadro_fontes(baseline)
    quadro_c = _quadro_fontes(canonico)
    resumo_b = {
        "pacote": _object_fingerprint(baseline),
        "quadro_fontes_elegiveis": _dataframe_summary(quadro_b),
        "auditoria": _serializar_simples(_safe_attr_raw(baseline, "auditoria")),
    }
    resumo_c = {
        "pacote": _object_fingerprint(canonico),
        "quadro_fontes_elegiveis": _dataframe_summary(quadro_c),
        "auditoria": _serializar_simples(_safe_attr_raw(canonico, "auditoria")),
    }
    operacionais = []
    for key in ("shape", "len", "columns", "numeric_totals"):
        if resumo_b["quadro_fontes_elegiveis"].get(key) != resumo_c["quadro_fontes_elegiveis"].get(key):
            operacionais.append(f"quadro_fontes_elegiveis.{key}")
    classificacao = "operacional" if operacionais else "documental"
    return {
        "campo": "fontes_elegiveis_pagamento",
        "classificacao_divergencia": classificacao,
        "impacta_runtime": bool(operacionais),
        "atributos_operacionais_divergentes": operacionais,
        "resumo_baseline": resumo_b,
        "resumo_canonico": resumo_c,
        "diferencas_fingerprint": diferencas,
        "interpretacao": "Divergência é operacional se shape, len, colunas ou totais do dataframe interno quadro_fontes_elegiveis divergirem.",
    }


def _detalhar_cache_cdi(baseline: Any, canonico: Any, diferencas: dict[str, Any]) -> dict[str, Any]:
    serie_b = _safe_attr_raw(baseline, "serie_cdi")
    serie_c = _safe_attr_raw(canonico, "serie_cdi")
    resumo_b = {
        "objeto": _object_fingerprint(baseline),
        "serie_cdi": _serie_summary(serie_b),
    }
    resumo_c = {
        "objeto": _object_fingerprint(canonico),
        "serie_cdi": _serie_summary(serie_c),
    }
    attrs_operacionais = []
    for key in ("shape", "len", "primeira_data", "ultima_data", "ultimo_valor", "soma"):
        if resumo_b["serie_cdi"].get(key) != resumo_c["serie_cdi"].get(key):
            attrs_operacionais.append(f"serie_cdi.{key}")
    classificacao = "operacional" if attrs_operacionais else "documental"
    return {
        "campo": "cache_cdi",
        "classificacao_divergencia": classificacao,
        "impacta_runtime": bool(attrs_operacionais),
        "atributos_operacionais_divergentes": attrs_operacionais,
        "resumo_baseline": resumo_b,
        "resumo_canonico": resumo_c,
        "diferencas_fingerprint": diferencas,
        "interpretacao": "Divergência é operacional se série CDI, janela temporal, último fator ou soma diferirem; origem/status isolados tendem a ser documentais.",
    }


def _detalhar_divergencia(nome: str, baseline_ctx: Any, canonico_ctx: Any, comparacao: dict[str, Any]) -> dict[str, Any]:
    vb = getattr(baseline_ctx, nome)
    vc = getattr(canonico_ctx, nome)
    diferencas = comparacao.get("diferencas", {})
    if nome == "pacote_entrada_resolvida":
        return _detalhar_pacote_entrada_resolvida(vb, vc, diferencas)
    if nome == "validacao_pre_execucao":
        return _detalhar_validacao_pre_execucao(vb, vc, diferencas)
    if nome == "fontes_elegiveis_pagamento":
        return _detalhar_fontes_elegiveis(vb, vc, diferencas)
    if nome == "cache_cdi":
        return _detalhar_cache_cdi(vb, vc, diferencas)
    return {
        "campo": nome,
        "classificacao_divergencia": _classificacao_por_diferencas(diferencas, set()),
        "impacta_runtime": bool(diferencas),
        "diferencas_fingerprint": diferencas,
    }


def _resumir_classificacoes(detalhes: dict[str, Any]) -> dict[str, int]:
    resumo: dict[str, int] = {}
    for item in detalhes.values():
        chave = str(item.get("classificacao_divergencia", "indefinida"))
        resumo[chave] = resumo.get(chave, 0) + 1
    return dict(sorted(resumo.items()))


def auditar_equivalencia(raiz_repositorio: Path) -> dict[str, Any]:
    contexto_baseline = carregar_contexto_baseline(
        raiz_repositorio=raiz_repositorio,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    contexto_canonico = carregar_contexto_operacional_canonico(
        raiz_repositorio=raiz_repositorio,
        instalar_automaticamente=False,
        incluir_replay=True,
    )

    comparacoes = [_comparar_campo(campo, contexto_baseline, contexto_canonico) for campo in CAMPOS_COMUNS_RUNTIME]
    comparacoes_por_campo = {c["campo"]: c for c in comparacoes}
    campos_equivalentes = [c["campo"] for c in comparacoes if c["equivalente"]]
    campos_divergentes = [c["campo"] for c in comparacoes if not c["equivalente"]]
    auditoria_proibidos = _auditar_campos_proibidos(contexto_canonico)
    proveniencia_entrada = _comparar_proveniencia_entrada(contexto_baseline, contexto_canonico)

    detalhamento_divergencias = {
        campo: _detalhar_divergencia(campo, contexto_baseline, contexto_canonico, comparacoes_por_campo[campo])
        for campo in campos_divergentes
        if campo in CAMPOS_DIVERGENTES_ALVO
    }
    campos_com_impacto_runtime = sorted(
        campo for campo, detalhe in detalhamento_divergencias.items()
        if detalhe.get("impacta_runtime")
    )
    resumo_classificacao_divergencias = _resumir_classificacoes(detalhamento_divergencias)

    equivalencia_contextos_ok = (
        not campos_divergentes
        and auditoria_proibidos["canonico_sem_campos_transicionais"]
    )
    equivalencia_operacional_minima_ok = (
        not campos_com_impacto_runtime
        and proveniencia_entrada["proveniencia_equivalente"]
        and auditoria_proibidos["canonico_sem_campos_transicionais"]
    )

    return {
        "microetapa": MICROETAPA,
        "objetivo": "provar equivalencia entre ContextoBaseline e ContextoOperacionalCanonico nos campos comuns consumiveis pela rota runtime, sem migrar principal.py",
        "altera_runtime": False,
        "altera_contexto_baseline": False,
        "altera_motor": False,
        "altera_replay": False,
        "altera_ledger": False,
        "altera_ranking": False,
        "altera_xlsx": False,
        "campos_comuns_runtime": list(CAMPOS_COMUNS_RUNTIME),
        "qtd_campos_comparados": len(comparacoes),
        "campos_equivalentes": campos_equivalentes,
        "campos_divergentes": campos_divergentes,
        "equivalencia_contextos_ok": equivalencia_contextos_ok,
        "equivalencia_operacional_minima_ok": equivalencia_operacional_minima_ok,
        "campos_com_impacto_runtime": campos_com_impacto_runtime,
        "resumo_classificacao_divergencias": resumo_classificacao_divergencias,
        "auditoria_campos_proibidos": auditoria_proibidos,
        "proveniencia_entrada": proveniencia_entrada,
        "detalhamento_divergencias": detalhamento_divergencias,
        "comparacoes": comparacoes,
        "decisao_pre_etapa5": "nao_migrar_runtime; alinhar fonte da planilha e janela CDI antes de qualquer substituicao",
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    linhas = [
        "# V17-F0-V.4Z4 — Auditoria de equivalência entre contextos",
        "",
        f"- equivalencia_contextos_ok: `{payload['equivalencia_contextos_ok']}`",
        f"- equivalencia_operacional_minima_ok: `{payload['equivalencia_operacional_minima_ok']}`",
        f"- campos comparados: `{payload['qtd_campos_comparados']}`",
        f"- campos equivalentes: `{len(payload['campos_equivalentes'])}`",
        f"- campos divergentes: `{len(payload['campos_divergentes'])}`",
        f"- campos com impacto runtime: `{payload['campos_com_impacto_runtime']}`",
        "",
        "## Proveniência da entrada",
        "",
        "```json",
        json.dumps(payload["proveniencia_entrada"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Classificação das divergências",
        "",
        "```json",
        json.dumps(payload["resumo_classificacao_divergencias"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Campos divergentes",
        "",
    ]
    if payload["campos_divergentes"]:
        for campo in payload["campos_divergentes"]:
            detalhe = payload["detalhamento_divergencias"].get(campo, {})
            classificacao = detalhe.get("classificacao_divergencia", "nao_detalhado")
            impacto = detalhe.get("impacta_runtime", "indefinido")
            linhas.append(f"- `{campo}` — classificação: `{classificacao}`; impacta_runtime: `{impacto}`")
    else:
        linhas.append("- nenhum")
    linhas.extend([
        "",
        "## Auditoria de campos proibidos no contexto canônico",
        "",
        "```json",
        json.dumps(payload["auditoria_campos_proibidos"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Detalhamento das divergências",
        "",
        "```json",
        json.dumps(payload["detalhamento_divergencias"], ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Decisão pré-Etapa 5",
        "",
        f"`{payload['decisao_pre_etapa5']}`",
        "",
    ])
    path.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V17-F0-V.4Z4 — audita equivalência entre contextos sem migrar runtime.")
    parser.add_argument("--raiz", type=Path, default=RAIZ_REPOSITORIO)
    parser.add_argument("--sem-arquivos", action="store_true")
    args = parser.parse_args()

    payload = auditar_equivalencia(args.raiz.resolve())
    print("=== AUDITORIA EQUIVALENCIA CONTEXTOS V4Z4 ===")
    print("microetapa=", payload["microetapa"])
    print("qtd_campos_comparados=", payload["qtd_campos_comparados"])
    print("equivalencia_contextos_ok=", payload["equivalencia_contextos_ok"])
    print("equivalencia_operacional_minima_ok=", payload["equivalencia_operacional_minima_ok"])
    print("campos_equivalentes=", json.dumps(payload["campos_equivalentes"], ensure_ascii=False))
    print("campos_divergentes=", json.dumps(payload["campos_divergentes"], ensure_ascii=False))
    print("campos_com_impacto_runtime=", json.dumps(payload["campos_com_impacto_runtime"], ensure_ascii=False))
    print("resumo_classificacao_divergencias=", json.dumps(payload["resumo_classificacao_divergencias"], ensure_ascii=False, sort_keys=True))
    print("auditoria_campos_proibidos=", json.dumps(payload["auditoria_campos_proibidos"], ensure_ascii=False, sort_keys=True))
    print("proveniencia_entrada=", json.dumps(payload["proveniencia_entrada"], ensure_ascii=False, sort_keys=True))
    print("detalhamento_divergencias=", json.dumps(payload["detalhamento_divergencias"], ensure_ascii=False, sort_keys=True))

    if not args.sem_arquivos:
        out = args.raiz / "relatorios" / "atuais" / "auditoria_equivalencia_contextos_v4z4"
        out.mkdir(parents=True, exist_ok=True)
        _write_json(out / "equivalencia_contextos_v4z4.json", payload)
        _write_md(out / "resumo_equivalencia_contextos_v4z4.md", payload)
        print("saida_dir=", out)
    return 0 if payload["auditoria_campos_proibidos"]["canonico_sem_campos_transicionais"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
