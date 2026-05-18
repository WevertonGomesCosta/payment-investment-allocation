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

AVISOS_GATE_ACEITOS = {
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


def _shape(obj: Any) -> tuple[int, int] | None:
    shape = getattr(obj, "shape", None)
    if isinstance(shape, tuple) and len(shape) == 2:
        return int(shape[0]), int(shape[1])
    return None


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
        "modo_paralelo": evidencias.get("modo_paralelo"),
        "nao_reconstroi_aliases": evidencias.get("nao_reconstroi_aliases"),
        "nao_cria_dados_canonicos": evidencias.get("nao_cria_dados_canonicos"),
        "nao_altera_motor": evidencias.get("nao_altera_motor"),
        "nao_altera_saida": evidencias.get("nao_altera_saida"),
        "qtd_evidencias": len(evidencias),
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


def auditar_pos_promocao_gate_etapa2(ctx: Any) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {}

    gate = getattr(ctx, "validacao_pre_execucao", None)
    legada = getattr(ctx, "validacao_pre_execucao_legada_shadow", None)
    shadow_pacote = getattr(ctx, "validacao_pre_execucao_pacote_entrada_resolvida_shadow", None)
    pacote = getattr(ctx, "pacote_entrada_resolvida_shadow", None)
    auditoria_pacote = getattr(ctx, "auditoria_pacote_entrada_resolvida_shadow", None)
    dados = getattr(ctx, "dados_operacionais", None)

    evidencias["gate_operacional"] = _resumo_validacao(gate)
    evidencias["validacao_legada_shadow"] = _resumo_validacao(legada)
    evidencias["validacao_pacote_shadow"] = _resumo_validacao(shadow_pacote)

    if not isinstance(gate, PacoteValidacaoPreExecucao):
        erros.append("gate_operacional_nao_e_PacoteValidacaoPreExecucao")
    if not isinstance(legada, PacoteValidacaoPreExecucao):
        erros.append("validacao_legada_shadow_nao_e_PacoteValidacaoPreExecucao")
    if not isinstance(shadow_pacote, PacoteValidacaoPreExecucao):
        erros.append("validacao_pacote_shadow_nao_e_PacoteValidacaoPreExecucao")

    if isinstance(gate, PacoteValidacaoPreExecucao):
        if gate.ok is not True:
            erros.append("gate_operacional_ok_nao_true")
        if gate.erros_bloqueantes:
            erros.append("gate_operacional_tem_erros_bloqueantes")
        if gate.evidencias.get("tipo") != "gate_puro_pre_execucao_pacote_entrada_resolvida":
            erros.append(f"gate_operacional_tipo_incorreto:{gate.evidencias.get('tipo')!r}")
        for flag in (
            "modo_paralelo",
            "nao_reconstroi_aliases",
            "nao_cria_dados_canonicos",
            "nao_altera_motor",
            "nao_altera_saida",
        ):
            if gate.evidencias.get(flag) is not True:
                erros.append(f"gate_operacional_flag_incorreta:{flag}:{gate.evidencias.get(flag)!r}")
        avisos_nao_previstos = sorted(set(gate.avisos or []) - AVISOS_GATE_ACEITOS)
        evidencias["gate_operacional_avisos_nao_previstos"] = avisos_nao_previstos
        if avisos_nao_previstos:
            avisos.append(f"Avisos não previstos no gate operacional: {avisos_nao_previstos}")

    if isinstance(legada, PacoteValidacaoPreExecucao):
        if legada.ok is not True:
            erros.append("validacao_legada_shadow_ok_nao_true")
        if legada.erros_bloqueantes:
            erros.append("validacao_legada_shadow_tem_erros_bloqueantes")
        if legada.evidencias.get("tipo") != "gate_puro_pre_execucao":
            erros.append(f"validacao_legada_shadow_tipo_incorreto:{legada.evidencias.get('tipo')!r}")

    comparacao = {
        "gate_e_shadow_pacote_mesmo_objeto": shadow_pacote is gate,
        "legada_e_gate_objetos_distintos": legada is not gate,
        "gate_por_pacote": isinstance(gate, PacoteValidacaoPreExecucao) and gate.evidencias.get("tipo") == "gate_puro_pre_execucao_pacote_entrada_resolvida",
        "legada_preservada_shadow": isinstance(legada, PacoteValidacaoPreExecucao) and legada.evidencias.get("tipo") == "gate_puro_pre_execucao",
    }
    evidencias["comparacao"] = comparacao

    if comparacao["gate_e_shadow_pacote_mesmo_objeto"] is not True:
        erros.append("shadow_pacote_nao_espelha_gate_operacional")
    if comparacao["legada_e_gate_objetos_distintos"] is not True:
        erros.append("validacao_legada_nao_foi_preservada_como_shadow_distinto")

    evidencias["pacote_entrada_resolvida_shadow_presente"] = pacote is not None
    evidencias["auditoria_pacote_entrada_resolvida_shadow_presente"] = auditoria_pacote is not None
    evidencias["auditoria_pacote_entrada_resolvida_shadow_ok"] = getattr(auditoria_pacote, "ok", None)
    if pacote is None:
        erros.append("pacote_entrada_resolvida_shadow_ausente")
    if getattr(auditoria_pacote, "ok", None) is not True:
        erros.append("auditoria_pacote_entrada_resolvida_shadow_nao_ok")

    metadados = dict(getattr(pacote, "metadados", {}) or {}) if pacote is not None else {}
    evidencias["pacote_entrada_resolvida_metadados"] = metadados
    if metadados.get("substitui_validacao_pre_execucao") is not True:
        erros.append("metadado_substitui_validacao_pre_execucao_nao_true")
    if metadados.get("validacao_legada_preservada_shadow") is not True:
        erros.append("metadado_validacao_legada_preservada_shadow_nao_true")
    if metadados.get("substitui_dados_operacionais_canonicos") is not False:
        erros.append("metadado_substitui_dados_operacionais_canonicos_nao_false")
    if metadados.get("substitui_cache_cdi_operacional") is not False:
        erros.append("metadado_substitui_cache_cdi_operacional_nao_false")

    evidencias["dados_operacionais_tipo"] = type(dados).__name__
    evidencias["shape.inventario_canonico"] = _shape(getattr(dados, "inventario_canonico", None)) if dados is not None else None
    evidencias["shape.gastos_canonicos"] = _shape(getattr(dados, "gastos_canonicos", None)) if dados is not None else None
    evidencias["shape.salarios_canonicos"] = _shape(getattr(dados, "salarios_canonicos", None)) if dados is not None else None
    evidencias["shape.switching_canonico"] = _shape(getattr(dados, "switching_canonico", None)) if dados is not None else None

    for chave in (
        "shape.inventario_canonico",
        "shape.gastos_canonicos",
        "shape.salarios_canonicos",
        "shape.switching_canonico",
    ):
        if evidencias[chave] is None:
            erros.append(f"dados_operacionais_shape_ausente:{chave}")

    ok = len(erros) == 0
    return {
        "ok": ok,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
        "resumo": {
            "tipo_contexto": type(ctx).__name__,
            "gate_ok": getattr(gate, "ok", None),
            "gate_tipo": getattr(gate, "evidencias", {}).get("tipo") if isinstance(gate, PacoteValidacaoPreExecucao) else None,
            "legada_ok": getattr(legada, "ok", None),
            "legada_tipo": getattr(legada, "evidencias", {}).get("tipo") if isinstance(legada, PacoteValidacaoPreExecucao) else None,
            "shadow_pacote_is_gate": shadow_pacote is gate,
            "legada_is_gate": legada is gate,
            "auditoria_pacote_ok": getattr(auditoria_pacote, "ok", None),
            "dados_operacionais_tipo": type(dados).__name__,
        },
    }


def imprimir_resultado(resultado: dict[str, Any]) -> None:
    print("=== AUDITORIA POS-PROMOCAO GATE ETAPA 2 V35C ===")
    print("ok=", resultado["ok"])
    print("erros=", resultado["erros"])
    print("avisos=", resultado["avisos"])
    print("resumo=", json.dumps(_serializar(resultado["resumo"]), ensure_ascii=False, sort_keys=True))

    print("\n=== GATE OPERACIONAL ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("gate_operacional")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== VALIDACAO LEGADA SHADOW ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("validacao_legada_shadow")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== COMPARACAO ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("comparacao")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== PACOTE ENTRADA RESOLVIDA ===")
    print("pacote_entrada_resolvida_shadow_presente=", resultado["evidencias"].get("pacote_entrada_resolvida_shadow_presente"))
    print("auditoria_pacote_entrada_resolvida_shadow_ok=", resultado["evidencias"].get("auditoria_pacote_entrada_resolvida_shadow_ok"))
    print("metadados=", json.dumps(_serializar(resultado["evidencias"].get("pacote_entrada_resolvida_metadados")), ensure_ascii=False, sort_keys=True))

    print("\n=== DADOS OPERACIONAIS ===")
    for chave in (
        "dados_operacionais_tipo",
        "shape.inventario_canonico",
        "shape.gastos_canonicos",
        "shape.salarios_canonicos",
        "shape.switching_canonico",
    ):
        print(f"{chave}=", resultado["evidencias"].get(chave))

    print("\n=== RESULTADO FINAL ===")
    if resultado["ok"]:
        print("AUDITORIA_POS_PROMOCAO_GATE_ETAPA2_V35C_OK")
    else:
        print("AUDITORIA_POS_PROMOCAO_GATE_ETAPA2_V35C_COM_ERROS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita pós-promoção do gate da Etapa 2 por PacoteEntradaResolvida."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help="Caminho opcional para salvar o resultado em JSON. Não é usado por padrão.",
    )
    args = parser.parse_args()

    ctx = carregar_contexto_para_auditoria()
    resultado = auditar_pos_promocao_gate_etapa2(ctx)
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
