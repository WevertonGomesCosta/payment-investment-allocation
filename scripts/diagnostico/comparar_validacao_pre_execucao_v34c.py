from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.validacao_pre_execucao import (
    PacoteValidacaoPreExecucao,
    validar_pre_execucao,
    validar_pre_execucao_pacote_entrada_resolvida,
)

AVISOS_PACOTE_ACEITOS = {
    "Última data da série CDI é anterior à data de referência.",
    "Série CDI começa após data_inicial_consulta da JanelaConsultaCDI.",
}


def _serializar(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _serializar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_serializar(v) for v in obj]
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def _chaves_evidencias(validacao: PacoteValidacaoPreExecucao) -> list[str]:
    evidencias = validacao.evidencias if isinstance(validacao.evidencias, dict) else {}
    return sorted(str(k) for k in evidencias.keys())


def _resumo_validacao(validacao: PacoteValidacaoPreExecucao) -> dict[str, Any]:
    return {
        "tipo": type(validacao).__name__,
        "ok": validacao.ok,
        "qtd_erros": len(validacao.erros_bloqueantes or []),
        "erros": list(validacao.erros_bloqueantes or []),
        "qtd_avisos": len(validacao.avisos or []),
        "avisos": list(validacao.avisos or []),
        "evidencia_tipo": (validacao.evidencias or {}).get("tipo") if isinstance(validacao.evidencias, dict) else None,
        "qtd_evidencias": len(validacao.evidencias or {}) if isinstance(validacao.evidencias, dict) else 0,
        "chaves_evidencias": _chaves_evidencias(validacao),
    }


def carregar_contexto_para_comparacao():
    return carregar_contexto_baseline(
        incluir_switching_shadow=False,
        incluir_triagem=False,
        incluir_replay=False,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )


def comparar_validacoes(ctx: Any) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {}

    validacao_contexto = getattr(ctx, "validacao_pre_execucao", None)
    validacao_legada_reexecutada = validar_pre_execucao(
        ctx.pacote_config,
        ctx.execucao,
        ctx.pacote_planilha,
    )
    validacao_pacote = validar_pre_execucao_pacote_entrada_resolvida(
        ctx.pacote_entrada_resolvida_shadow,
    )

    validacoes = {
        "contexto_legada": validacao_contexto,
        "legada_reexecutada": validacao_legada_reexecutada,
        "pacote_entrada_resolvida": validacao_pacote,
    }

    for nome, validacao in validacoes.items():
        if not isinstance(validacao, PacoteValidacaoPreExecucao):
            erros.append(f"{nome}:nao_e_PacoteValidacaoPreExecucao")
            continue
        evidencias[nome] = _resumo_validacao(validacao)
        if validacao.ok is not True:
            erros.append(f"{nome}:ok_nao_true")
        if validacao.erros_bloqueantes:
            erros.append(f"{nome}:erros_bloqueantes_presentes")

    if isinstance(validacao_contexto, PacoteValidacaoPreExecucao) and isinstance(
        validacao_legada_reexecutada,
        PacoteValidacaoPreExecucao,
    ):
        evidencias["comparacao_legada_contexto_vs_reexecutada"] = {
            "ok_igual": validacao_contexto.ok == validacao_legada_reexecutada.ok,
            "erros_iguais": list(validacao_contexto.erros_bloqueantes) == list(validacao_legada_reexecutada.erros_bloqueantes),
            "avisos_iguais": list(validacao_contexto.avisos) == list(validacao_legada_reexecutada.avisos),
            "tipo_evidencia_contexto": validacao_contexto.evidencias.get("tipo"),
            "tipo_evidencia_reexecutada": validacao_legada_reexecutada.evidencias.get("tipo"),
        }
        if validacao_contexto.ok != validacao_legada_reexecutada.ok:
            erros.append("validacao_legada_contexto_vs_reexecutada:ok_divergente")
        if list(validacao_contexto.erros_bloqueantes) != list(validacao_legada_reexecutada.erros_bloqueantes):
            erros.append("validacao_legada_contexto_vs_reexecutada:erros_divergentes")

    if isinstance(validacao_pacote, PacoteValidacaoPreExecucao):
        avisos_pacote = set(validacao_pacote.avisos or [])
        avisos_nao_previstos = sorted(avisos_pacote - AVISOS_PACOTE_ACEITOS)
        evidencias["pacote_entrada_resolvida_avisos_nao_previstos"] = avisos_nao_previstos
        if avisos_nao_previstos:
            avisos.append(f"Avisos não previstos na validação por pacote: {avisos_nao_previstos}")

        flags_esperadas = {
            "tipo": "gate_puro_pre_execucao_pacote_entrada_resolvida",
            "modo_paralelo": True,
            "nao_substitui_validacao_legada": True,
            "nao_reconstroi_aliases": True,
            "nao_cria_dados_canonicos": True,
            "nao_altera_motor": True,
            "nao_altera_saida": True,
        }
        flags_observadas = {
            chave: validacao_pacote.evidencias.get(chave)
            for chave in flags_esperadas
        }
        evidencias["pacote_entrada_resolvida_flags_observadas"] = flags_observadas
        for chave, esperado in flags_esperadas.items():
            observado = flags_observadas.get(chave)
            if observado is not esperado and observado != esperado:
                erros.append(f"pacote_entrada_resolvida:flag_divergente:{chave}:{observado!r}")

    referencias = {
        "ctx_validacao_pre_execucao_nao_substituida": validacao_contexto is not validacao_pacote,
        "pacote_shadow_mesmo_pacote_config": ctx.pacote_entrada_resolvida_shadow.pacote_config is ctx.pacote_config,
        "pacote_shadow_mesma_execucao": ctx.pacote_entrada_resolvida_shadow.contexto_execucao is ctx.execucao,
        "pacote_shadow_mesma_planilha": ctx.pacote_entrada_resolvida_shadow.pacote_planilha is ctx.pacote_planilha,
        "pacote_shadow_mesmo_cache_cdi": ctx.pacote_entrada_resolvida_shadow.pacote_cache_cdi is ctx.cache_cdi,
    }
    evidencias["referencias"] = referencias
    for nome, ok in referencias.items():
        if ok is not True:
            erros.append(f"referencia_divergente:{nome}")

    ok = len(erros) == 0
    return {
        "ok": ok,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
        "resumo": {
            "tipo_contexto": type(ctx).__name__,
            "validacao_contexto_ok": getattr(validacao_contexto, "ok", None),
            "validacao_legada_reexecutada_ok": getattr(validacao_legada_reexecutada, "ok", None),
            "validacao_pacote_ok": getattr(validacao_pacote, "ok", None),
            "validacao_pacote_qtd_avisos": len(getattr(validacao_pacote, "avisos", []) or []),
            "validacao_pacote_qtd_erros": len(getattr(validacao_pacote, "erros_bloqueantes", []) or []),
            "ctx_validacao_pre_execucao_nao_substituida": referencias["ctx_validacao_pre_execucao_nao_substituida"],
        },
    }


def imprimir_resultado(resultado: dict[str, Any]) -> None:
    print("=== COMPARACAO VALIDACAO PRE EXECUCAO V34C ===")
    print("ok=", resultado["ok"])
    print("erros=", resultado["erros"])
    print("avisos=", resultado["avisos"])
    print("resumo=", json.dumps(_serializar(resultado["resumo"]), ensure_ascii=False, sort_keys=True))

    print("\n=== VALIDACAO CONTEXTO LEGADA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("contexto_legada")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== VALIDACAO LEGADA REEXECUTADA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("legada_reexecutada")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== VALIDACAO PACOTE ENTRADA RESOLVIDA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("pacote_entrada_resolvida")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== COMPARACOES ===")
    print("comparacao_legada=", json.dumps(
        _serializar(resultado["evidencias"].get("comparacao_legada_contexto_vs_reexecutada")),
        ensure_ascii=False,
        sort_keys=True,
    ))
    print("flags_pacote=", json.dumps(
        _serializar(resultado["evidencias"].get("pacote_entrada_resolvida_flags_observadas")),
        ensure_ascii=False,
        sort_keys=True,
    ))
    print("referencias=", json.dumps(
        _serializar(resultado["evidencias"].get("referencias")),
        ensure_ascii=False,
        sort_keys=True,
    ))

    print("\n=== RESULTADO FINAL ===")
    if resultado["ok"]:
        print("COMPARACAO_VALIDACAO_PRE_EXECUCAO_V34C_OK")
    else:
        print("COMPARACAO_VALIDACAO_PRE_EXECUCAO_V34C_COM_ERROS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara validação pré-execução legada com validação por PacoteEntradaResolvida."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help="Caminho opcional para salvar o resultado em JSON. Não é usado por padrão.",
    )
    args = parser.parse_args()

    ctx = carregar_contexto_para_comparacao()
    resultado = comparar_validacoes(ctx)
    imprimir_resultado(resultado)

    if args.json_path:
        destino = Path(args.json_path)
        if not destino.is_absolute():
            destino = ROOT / destino
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(_serializar(resultado), ensure_ascii=False, indent=2), encoding="utf-8")
        print("json_salvo=", destino)

    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
