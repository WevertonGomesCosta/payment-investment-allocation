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
from nucleo.entrada_resolvida import AuditoriaPacoteEntradaResolvida, PacoteEntradaResolvida
from nucleo.validacao_pre_execucao import PacoteValidacaoPreExecucao

ARQUIVO_ETAPA3 = ROOT / "nucleo" / "dados_operacionais_canonicos.py"

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


def auditar_etapa3_inalterada() -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {
        "arquivo": str(ARQUIVO_ETAPA3.relative_to(ROOT)),
        "existe": ARQUIVO_ETAPA3.exists(),
    }

    if not ARQUIVO_ETAPA3.exists():
        erros.append("arquivo_etapa3_dados_operacionais_canonicos_ausente")
        return {"ok": False, "erros": erros, "avisos": avisos, "evidencias": evidencias}

    texto = ARQUIVO_ETAPA3.read_text(encoding="utf-8")
    checks = {
        "importa_PacotePlanilha_e_resolver_coluna": "from nucleo.leitor_planilha import PacotePlanilha, resolver_coluna" in texto,
        "assinatura_legada_carregar_dados": "def carregar_dados_operacionais_canonicos(\n    pacote_planilha: PacotePlanilha," in texto,
        "usa_quadros_brutos": "pacote_planilha.quadros_brutos" in texto,
        "usa_resolver_coluna": "resolver_coluna(" in texto,
        "sem_import_PacoteEntradaResolvida": "PacoteEntradaResolvida" not in texto,
        "sem_nome_operacional_pacote_entrada_resolvida": "pacote_entrada_resolvida" not in texto,
    }
    evidencias["checks"] = checks

    for nome, ok in checks.items():
        if not ok:
            erros.append(f"etapa3_nao_preserva_estado_esperado:{nome}")

    evidencias["interpretacao"] = (
        "A Etapa 3 permanece com assinatura legada baseada em PacotePlanilha/config "
        "e ainda não foi adaptada para consumir PacoteEntradaResolvida."
    )

    return {
        "ok": len(erros) == 0,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
    }


def auditar_pacote_entrada_resolvida_operacional(ctx: Any) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {}

    pacote_operacional = getattr(ctx, "pacote_entrada_resolvida", None)
    pacote_shadow = getattr(ctx, "pacote_entrada_resolvida_shadow", None)
    auditoria_operacional = getattr(ctx, "auditoria_pacote_entrada_resolvida", None)
    auditoria_shadow = getattr(ctx, "auditoria_pacote_entrada_resolvida_shadow", None)
    gate = getattr(ctx, "validacao_pre_execucao", None)
    gate_shadow = getattr(ctx, "validacao_pre_execucao_pacote_entrada_resolvida_shadow", None)
    legada = getattr(ctx, "validacao_pre_execucao_legada_shadow", None)
    dados = getattr(ctx, "dados_operacionais", None)

    evidencias["atributos"] = {
        "tem_pacote_entrada_resolvida": hasattr(ctx, "pacote_entrada_resolvida"),
        "tem_pacote_entrada_resolvida_shadow": hasattr(ctx, "pacote_entrada_resolvida_shadow"),
        "tem_auditoria_pacote_entrada_resolvida": hasattr(ctx, "auditoria_pacote_entrada_resolvida"),
        "tem_auditoria_pacote_entrada_resolvida_shadow": hasattr(ctx, "auditoria_pacote_entrada_resolvida_shadow"),
    }
    evidencias["tipos"] = {
        "pacote_operacional": type(pacote_operacional).__name__,
        "pacote_shadow": type(pacote_shadow).__name__,
        "auditoria_operacional": type(auditoria_operacional).__name__,
        "auditoria_shadow": type(auditoria_shadow).__name__,
        "gate": type(gate).__name__,
        "gate_shadow": type(gate_shadow).__name__,
        "legada": type(legada).__name__,
        "dados_operacionais": type(dados).__name__,
    }
    evidencias["identidade"] = {
        "pacote_operacional_is_shadow": pacote_operacional is pacote_shadow,
        "auditoria_operacional_is_shadow": auditoria_operacional is auditoria_shadow,
        "gate_operacional_is_shadow_pacote": gate is gate_shadow,
        "legada_is_gate": legada is gate,
    }

    if not isinstance(pacote_operacional, PacoteEntradaResolvida):
        erros.append("pacote_operacional_nao_e_PacoteEntradaResolvida")
    if not isinstance(pacote_shadow, PacoteEntradaResolvida):
        erros.append("pacote_shadow_nao_e_PacoteEntradaResolvida")
    if pacote_operacional is not pacote_shadow:
        erros.append("pacote_entrada_resolvida_shadow_nao_e_alias_do_operacional")

    if not isinstance(auditoria_operacional, AuditoriaPacoteEntradaResolvida):
        erros.append("auditoria_operacional_nao_e_AuditoriaPacoteEntradaResolvida")
    if not isinstance(auditoria_shadow, AuditoriaPacoteEntradaResolvida):
        erros.append("auditoria_shadow_nao_e_AuditoriaPacoteEntradaResolvida")
    if auditoria_operacional is not auditoria_shadow:
        erros.append("auditoria_pacote_entrada_resolvida_shadow_nao_e_alias_da_operacional")
    if getattr(auditoria_operacional, "ok", None) is not True:
        erros.append("auditoria_pacote_entrada_resolvida_operacional_nao_ok")

    metadados = dict(getattr(pacote_operacional, "metadados", {}) or {}) if pacote_operacional is not None else {}
    evidencias["pacote_entrada_resolvida_metadados"] = metadados
    checks_metadados = {
        "artefato": metadados.get("artefato") == "PacoteEntradaResolvida",
        "etapa": metadados.get("etapa") == "Etapa 1",
        "modo_shadow_contexto_baseline_false": metadados.get("modo_shadow_contexto_baseline") is False,
        "artefato_operacional_contexto_baseline_true": metadados.get("artefato_operacional_contexto_baseline") is True,
        "alias_shadow_preservado_temporariamente_true": metadados.get("alias_shadow_preservado_temporariamente") is True,
        "substitui_validacao_pre_execucao_true": metadados.get("substitui_validacao_pre_execucao") is True,
        "validacao_legada_preservada_shadow_true": metadados.get("validacao_legada_preservada_shadow") is True,
        "substitui_dados_operacionais_canonicos_false": metadados.get("substitui_dados_operacionais_canonicos") is False,
        "substitui_cache_cdi_operacional_false": metadados.get("substitui_cache_cdi_operacional") is False,
        "altera_dados_operacionais_canonicos_false": metadados.get("altera_dados_operacionais_canonicos") is False,
        "altera_motor_false": metadados.get("altera_motor") is False,
        "altera_saida_false": metadados.get("altera_saida") is False,
    }
    evidencias["checks_metadados"] = checks_metadados
    for nome, ok in checks_metadados.items():
        if not ok:
            erros.append(f"metadado_operacional_incorreto:{nome}:{metadados.get(nome)!r}")

    evidencias["gate_operacional"] = _resumo_validacao(gate)
    evidencias["gate_shadow"] = _resumo_validacao(gate_shadow)
    evidencias["validacao_legada_shadow"] = _resumo_validacao(legada)

    if not isinstance(gate, PacoteValidacaoPreExecucao):
        erros.append("gate_operacional_nao_e_PacoteValidacaoPreExecucao")
    else:
        if gate.ok is not True:
            erros.append("gate_operacional_ok_nao_true")
        if gate.erros_bloqueantes:
            erros.append("gate_operacional_tem_erros_bloqueantes")
        if gate.evidencias.get("tipo") != "gate_puro_pre_execucao_pacote_entrada_resolvida":
            erros.append(f"gate_operacional_tipo_incorreto:{gate.evidencias.get('tipo')!r}")
        avisos_nao_previstos = sorted(set(gate.avisos or []) - AVISOS_GATE_ACEITOS)
        evidencias["gate_operacional_avisos_nao_previstos"] = avisos_nao_previstos
        if avisos_nao_previstos:
            avisos.append(f"Avisos não previstos no gate operacional: {avisos_nao_previstos}")

    if gate is not gate_shadow:
        erros.append("validacao_pre_execucao_pacote_entrada_resolvida_shadow_nao_espelha_gate")

    if not isinstance(legada, PacoteValidacaoPreExecucao):
        erros.append("validacao_legada_shadow_nao_e_PacoteValidacaoPreExecucao")
    else:
        if legada.ok is not True:
            erros.append("validacao_legada_shadow_ok_nao_true")
        if legada.erros_bloqueantes:
            erros.append("validacao_legada_shadow_tem_erros_bloqueantes")
        if legada.evidencias.get("tipo") != "gate_puro_pre_execucao":
            erros.append(f"validacao_legada_shadow_tipo_incorreto:{legada.evidencias.get('tipo')!r}")
        if legada is gate:
            erros.append("validacao_legada_shadow_nao_e_objeto_distinto_do_gate_operacional")

    evidencias["dados_operacionais"] = {
        "tipo": type(dados).__name__,
        "shape.inventario_canonico": _shape(getattr(dados, "inventario_canonico", None)) if dados is not None else None,
        "shape.gastos_canonicos": _shape(getattr(dados, "gastos_canonicos", None)) if dados is not None else None,
        "shape.salarios_canonicos": _shape(getattr(dados, "salarios_canonicos", None)) if dados is not None else None,
        "shape.switching_canonico": _shape(getattr(dados, "switching_canonico", None)) if dados is not None else None,
    }

    for chave, valor in evidencias["dados_operacionais"].items():
        if chave.startswith("shape.") and valor is None:
            erros.append(f"dados_operacionais_shape_ausente:{chave}")

    auditoria_etapa3 = auditar_etapa3_inalterada()
    evidencias["etapa3_inalterada"] = auditoria_etapa3["evidencias"]
    erros.extend(auditoria_etapa3["erros"])
    avisos.extend(auditoria_etapa3["avisos"])

    return {
        "ok": len(erros) == 0,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
        "resumo": {
            "tipo_contexto": type(ctx).__name__,
            "pacote_operacional_tipo": type(pacote_operacional).__name__,
            "pacote_operacional_is_shadow": pacote_operacional is pacote_shadow,
            "auditoria_operacional_ok": getattr(auditoria_operacional, "ok", None),
            "auditoria_operacional_is_shadow": auditoria_operacional is auditoria_shadow,
            "gate_ok": getattr(gate, "ok", None),
            "gate_tipo": getattr(gate, "evidencias", {}).get("tipo") if isinstance(gate, PacoteValidacaoPreExecucao) else None,
            "gate_is_shadow_pacote": gate is gate_shadow,
            "legada_ok": getattr(legada, "ok", None),
            "legada_tipo": getattr(legada, "evidencias", {}).get("tipo") if isinstance(legada, PacoteValidacaoPreExecucao) else None,
            "legada_is_gate": legada is gate,
            "etapa3_inalterada_ok": auditoria_etapa3["ok"],
            "dados_operacionais_tipo": type(dados).__name__,
        },
    }


def imprimir_resultado(resultado: dict[str, Any]) -> None:
    print("=== AUDITORIA PACOTE ENTRADA RESOLVIDA OPERACIONAL V36B ===")
    print("ok=", resultado["ok"])
    print("erros=", resultado["erros"])
    print("avisos=", resultado["avisos"])
    print("resumo=", json.dumps(_serializar(resultado["resumo"]), ensure_ascii=False, sort_keys=True))

    print("\n=== IDENTIDADE OPERACIONAL / SHADOW ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("identidade")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== METADADOS DO PACOTE ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("pacote_entrada_resolvida_metadados")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== GATE OPERACIONAL ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("gate_operacional")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== VALIDACAO LEGADA SHADOW ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("validacao_legada_shadow")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== ETAPA 3 INALTERADA ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("etapa3_inalterada")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== DADOS OPERACIONAIS ===")
    print(json.dumps(_serializar(resultado["evidencias"].get("dados_operacionais")), ensure_ascii=False, indent=2, sort_keys=True))

    print("\n=== RESULTADO FINAL ===")
    if resultado["ok"]:
        print("AUDITORIA_PACOTE_ENTRADA_RESOLVIDA_OPERACIONAL_V36B_OK")
    else:
        print("AUDITORIA_PACOTE_ENTRADA_RESOLVIDA_OPERACIONAL_V36B_COM_ERROS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita a promoção operacional do PacoteEntradaResolvida no ContextoBaseline."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help="Caminho opcional para salvar o resultado em JSON. Não é usado por padrão.",
    )
    args = parser.parse_args()

    ctx = carregar_contexto_para_auditoria()
    resultado = auditar_pacote_entrada_resolvida_operacional(ctx)
    imprimir_resultado(resultado)

    if args.json_path:
        destino = Path(args.json_path)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(_serializar(resultado), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
