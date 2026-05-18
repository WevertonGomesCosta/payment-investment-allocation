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
from nucleo.validacao_pre_execucao import PacoteValidacaoPreExecucao

AVISOS_SHADOW_ACEITOS = {
    "Última data da série CDI é anterior à data de referência.",
    "Série CDI começa após data_inicial_consulta da JanelaConsultaCDI.",
}

FLAGS_SHADOW_ESPERADAS = {
    "tipo": "gate_puro_pre_execucao_pacote_entrada_resolvida",
    "modo_paralelo": True,
    "nao_substitui_validacao_legada": True,
    "nao_reconstroi_aliases": True,
    "nao_cria_dados_canonicos": True,
    "nao_altera_motor": True,
    "nao_altera_saida": True,
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


def _resumo_validacao(validacao: Any) -> dict[str, Any]:
    if not isinstance(validacao, PacoteValidacaoPreExecucao):
        return {
            "tipo_objeto": type(validacao).__name__,
            "eh_PacoteValidacaoPreExecucao": False,
        }
    evidencias = validacao.evidencias if isinstance(validacao.evidencias, dict) else {}
    return {
        "tipo_objeto": type(validacao).__name__,
        "eh_PacoteValidacaoPreExecucao": True,
        "ok": validacao.ok,
        "erros": list(validacao.erros_bloqueantes or []),
        "avisos": list(validacao.avisos or []),
        "qtd_erros": len(validacao.erros_bloqueantes or []),
        "qtd_avisos": len(validacao.avisos or []),
        "evidencia_tipo": evidencias.get("tipo"),
        "qtd_evidencias": len(evidencias),
        "chaves_evidencias": sorted(str(k) for k in evidencias.keys()),
    }


def carregar_contexto_para_auditoria():
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


def auditar_validacao_shadow_etapa2_contexto(ctx: Any) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {}

    legada = getattr(ctx, "validacao_pre_execucao", None)
    shadow = getattr(ctx, "validacao_pre_execucao_pacote_entrada_resolvida_shadow", None)

    evidencias["validacao_legada"] = _resumo_validacao(legada)
    evidencias["validacao_shadow"] = _resumo_validacao(shadow)

    if not isinstance(legada, PacoteValidacaoPreExecucao):
        erros.append("validacao_legada_nao_e_PacoteValidacaoPreExecucao")
    if not isinstance(shadow, PacoteValidacaoPreExecucao):
        erros.append("validacao_shadow_nao_e_PacoteValidacaoPreExecucao")

    if isinstance(legada, PacoteValidacaoPreExecucao):
        if legada.ok is not True:
            erros.append("validacao_legada_ok_nao_true")
        if legada.erros_bloqueantes:
            erros.append("validacao_legada_tem_erros_bloqueantes")

    if isinstance(shadow, PacoteValidacaoPreExecucao):
        if shadow.ok is not True:
            erros.append("validacao_shadow_ok_nao_true")
        if shadow.erros_bloqueantes:
            erros.append("validacao_shadow_tem_erros_bloqueantes")

        avisos_shadow = set(shadow.avisos or [])
        avisos_nao_previstos = sorted(avisos_shadow - AVISOS_SHADOW_ACEITOS)
        evidencias["validacao_shadow_avisos_nao_previstos"] = avisos_nao_previstos
        if avisos_nao_previstos:
            avisos.append(f"Avisos não previstos na validação shadow: {avisos_nao_previstos}")

        flags_observadas = {chave: shadow.evidencias.get(chave) for chave in FLAGS_SHADOW_ESPERADAS}
        evidencias["validacao_shadow_flags_observadas"] = flags_observadas
        for chave, esperado in FLAGS_SHADOW_ESPERADAS.items():
            observado = flags_observadas.get(chave)
            if observado is not esperado and observado != esperado:
                erros.append(f"validacao_shadow_flag_divergente:{chave}:{observado!r}")

    comparacao = {
        "objetos_distintos": legada is not shadow,
        "legada_preservada_no_contexto": isinstance(legada, PacoteValidacaoPreExecucao),
        "shadow_anexado_ao_contexto": isinstance(shadow, PacoteValidacaoPreExecucao),
        "ambas_ok": (
            isinstance(legada, PacoteValidacaoPreExecucao)
            and isinstance(shadow, PacoteValidacaoPreExecucao)
            and legada.ok is True
            and shadow.ok is True
        ),
        "erros_legada_iguais_a_zero": isinstance(legada, PacoteValidacaoPreExecucao) and not legada.erros_bloqueantes,
        "erros_shadow_iguais_a_zero": isinstance(shadow, PacoteValidacaoPreExecucao) and not shadow.erros_bloqueantes,
    }
    evidencias["comparacao_legada_vs_shadow"] = comparacao

    if comparacao["objetos_distintos"] is not True:
        erros.append("validacao_legada_foi_substituida_pelo_shadow")
    if comparacao["ambas_ok"] is not True:
        erros.append("validacao_legada_ou_shadow_nao_ok")

    pacote_shadow = getattr(ctx, "pacote_entrada_resolvida_shadow", None)
    auditoria_pacote_shadow = getattr(ctx, "auditoria_pacote_entrada_resolvida_shadow", None)
    evidencias["pacote_entrada_resolvida_shadow_presente"] = pacote_shadow is not None
    evidencias["auditoria_pacote_entrada_resolvida_shadow_presente"] = auditoria_pacote_shadow is not None
    evidencias["auditoria_pacote_entrada_resolvida_shadow_ok"] = getattr(auditoria_pacote_shadow, "ok", None)

    if pacote_shadow is None:
        erros.append("pacote_entrada_resolvida_shadow_ausente")
    if getattr(auditoria_pacote_shadow, "ok", None) is not True:
        erros.append("auditoria_pacote_entrada_resolvida_shadow_nao_ok")

    ok = len(erros) == 0
    return {
        "ok": ok,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
        "resumo": {
            "tipo_contexto": type(ctx).__name__,
            "validacao_legada_ok": getattr(legada, "ok", None),
            "validacao_shadow_ok": getattr(shadow, "ok", None),
            "validacao_shadow_qtd_avisos": len(getattr(shadow, "avisos", []) or []),
            "validacao_shadow_qtd_erros": len(getattr(shadow, "erros_bloqueantes", []) or []),
            "objetos_distintos": comparacao["objetos_distintos"],
            "pacote_shadow_presente": pacote_shadow is not None,
            "auditoria_pacote_shadow_ok": getattr(auditoria_pacote_shadow, "ok", None),
        },
    }


def imprimir_resultado(resultado: dict[str, Any]) -> None:
    print("=== AUDITORIA VALIDACAO SHADOW ETAPA 2 CONTEXTO V34E ===")
    print("ok=", resultado["ok"])
    print("erros=", resultado["erros"])
    print("avisos=", resultado["avisos"])
    print("resumo=", json.dumps(_serializar(resultado["resumo"]), ensure_ascii=False, sort_keys=True))

    print("\n=== VALIDACAO LEGADA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("validacao_legada")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== VALIDACAO SHADOW PACOTE ENTRADA RESOLVIDA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("validacao_shadow")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== COMPARACAO LEGADA VS SHADOW ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("comparacao_legada_vs_shadow")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== FLAGS SHADOW ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("validacao_shadow_flags_observadas")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== PACOTE ENTRADA RESOLVIDA SHADOW ===")
    print("pacote_entrada_resolvida_shadow_presente=", resultado["evidencias"].get("pacote_entrada_resolvida_shadow_presente"))
    print("auditoria_pacote_entrada_resolvida_shadow_presente=", resultado["evidencias"].get("auditoria_pacote_entrada_resolvida_shadow_presente"))
    print("auditoria_pacote_entrada_resolvida_shadow_ok=", resultado["evidencias"].get("auditoria_pacote_entrada_resolvida_shadow_ok"))

    print("\n=== RESULTADO FINAL ===")
    if resultado["ok"]:
        print("AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO_V34E_OK")
    else:
        print("AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO_V34E_COM_ERROS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita ctx.validacao_pre_execucao contra ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help="Caminho opcional para salvar o resultado em JSON. Não é usado por padrão.",
    )
    args = parser.parse_args()

    ctx = carregar_contexto_para_auditoria()
    resultado = auditar_validacao_shadow_etapa2_contexto(ctx)
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
