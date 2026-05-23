from __future__ import annotations

import argparse
import json
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


def _safe_attr(obj: Any, attr: str) -> Any:
    if not hasattr(obj, attr):
        return None
    try:
        value = getattr(obj, attr)
    except Exception as exc:
        return {"erro_attr": str(exc)}
    return _serializar_simples(value)


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
        return [_serializar_simples(v) for v in list(value)[:50]]
    return str(value)


def _dataclass_field_names(obj: Any) -> list[str]:
    if not is_dataclass(obj):
        return []
    try:
        return sorted(asdict(obj).keys())
    except Exception:
        return []


def _dataframe_fingerprint(obj: Any) -> dict[str, Any] | None:
    if not hasattr(obj, "shape") or not hasattr(obj, "columns"):
        return None
    try:
        columns = [str(c) for c in list(obj.columns)]
    except Exception:
        columns = []
    return {
        "shape": _shape(obj),
        "columns": columns,
    }


def _object_fingerprint(obj: Any) -> dict[str, Any]:
    fp: dict[str, Any] = {
        "type": type(obj).__name__,
        "module": type(obj).__module__,
        "shape": _shape(obj),
        "len": _len(obj),
        "dataclass_fields": _dataclass_field_names(obj),
    }

    dfp = _dataframe_fingerprint(obj)
    if dfp is not None:
        fp["dataframe"] = dfp

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
        try:
            serie = getattr(obj, "serie_cdi")
            fp["serie_cdi_shape"] = _shape(serie)
            fp["serie_cdi_len"] = _len(serie)
            if hasattr(serie, "index") and len(serie) > 0:
                fp["serie_cdi_primeira_data"] = _serializar_simples(serie.index.min())
                fp["serie_cdi_ultima_data"] = _serializar_simples(serie.index.max())
        except Exception as exc:
            fp["serie_cdi_erro"] = str(exc)

    if is_dataclass(obj):
        try:
            data = asdict(obj)
            fp["dataclass_resumo"] = {
                k: _fingerprint_resumido(v)
                for k, v in sorted(data.items(), key=lambda kv: str(kv[0]))
                if not str(k).lower().endswith("shadow")
            }
        except Exception as exc:
            fp["dataclass_resumo_erro"] = str(exc)

    return fp


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
        return {"type": type(value).__name__, "shape": shape}
    length = _len(value)
    if length is not None and not isinstance(value, (str, bytes)):
        return {"type": type(value).__name__, "len": length}
    return {"type": type(value).__name__}


def _comparar_fingerprints(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    chaves = sorted(set(a) | set(b))
    diferencas = {}
    for chave in chaves:
        if a.get(chave) != b.get(chave):
            diferencas[chave] = {"baseline": a.get(chave), "canonico": b.get(chave)}
    return {
        "equivalente": not diferencas,
        "diferencas": diferencas,
    }


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
    campos_equivalentes = [c["campo"] for c in comparacoes if c["equivalente"]]
    campos_divergentes = [c["campo"] for c in comparacoes if not c["equivalente"]]
    auditoria_proibidos = _auditar_campos_proibidos(contexto_canonico)

    equivalencia_contextos_ok = not campos_divergentes and auditoria_proibidos["canonico_sem_campos_transicionais"]

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
        "auditoria_campos_proibidos": auditoria_proibidos,
        "comparacoes": comparacoes,
        "decisao_pre_etapa5": "nao_migrar_runtime; usar resultado para decidir V4Z5/V4Z6",
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    linhas = [
        "# V17-F0-V.4Z4 — Auditoria de equivalência entre contextos",
        "",
        f"- equivalencia_contextos_ok: `{payload['equivalencia_contextos_ok']}`",
        f"- campos comparados: `{payload['qtd_campos_comparados']}`",
        f"- campos equivalentes: `{len(payload['campos_equivalentes'])}`",
        f"- campos divergentes: `{len(payload['campos_divergentes'])}`",
        "",
        "## Campos divergentes",
        "",
    ]
    if payload["campos_divergentes"]:
        for campo in payload["campos_divergentes"]:
            linhas.append(f"- `{campo}`")
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
    print("campos_equivalentes=", json.dumps(payload["campos_equivalentes"], ensure_ascii=False))
    print("campos_divergentes=", json.dumps(payload["campos_divergentes"], ensure_ascii=False))
    print("auditoria_campos_proibidos=", json.dumps(payload["auditoria_campos_proibidos"], ensure_ascii=False, sort_keys=True))

    if not args.sem_arquivos:
        out = args.raiz / "relatorios" / "atuais" / "auditoria_equivalencia_contextos_v4z4"
        out.mkdir(parents=True, exist_ok=True)
        _write_json(out / "equivalencia_contextos_v4z4.json", payload)
        _write_md(out / "resumo_equivalencia_contextos_v4z4.md", payload)
        print("saida_dir=", out)
    return 0 if payload["auditoria_campos_proibidos"]["canonico_sem_campos_transicionais"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
