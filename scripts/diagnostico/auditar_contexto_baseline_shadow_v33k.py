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

ATRIBUTOS_LEGADOS_OBRIGATORIOS = [
    "pacote_config",
    "execucao",
    "calendario_financeiro",
    "pacote_planilha",
    "validacao_pre_execucao",
    "carteira_canonica",
    "dados_operacionais",
    "recebidos_auditaveis",
    "fontes_elegiveis_pagamento",
    "saldo_disponivel_geral",
    "decisao_local_v1",
    "cache_cdi",
    "ranking_carteira",
    "nucleo_financeiro",
    "tabela_iof",
    "faixas_ir",
]

ATRIBUTOS_SHADOW_NOVOS = [
    "pacote_entrada_resolvida_shadow",
    "auditoria_pacote_entrada_resolvida_shadow",
]

ATRIBUTOS_SHADOW_PESADOS_DESATIVADOS = [
    "switching_shadow",
    "triagem_motor",
    "replay_passado",
    "switching_economico_shadow",
    "resolver_hibrido_5p_shadow",
    "benchmark_agrupado_individual_shadow",
    "benchmark_runner_futuro_shadow",
    "auditoria_runner_futuro_shadow",
    "auditoria_primeira_quebra_runner_futuro_shadow",
]

FLAGS_SHADOW_ESPERADAS = {
    "modo_shadow_contexto_baseline": True,
    "substitui_atributos_legados": False,
    "substitui_validacao_pre_execucao": False,
    "substitui_dados_operacionais_canonicos": False,
    "substitui_cache_cdi_operacional": False,
    "altera_leitura_planilha": False,
    "altera_cache_cdi": False,
    "altera_validacao_pre_execucao": False,
    "altera_dados_operacionais_canonicos": False,
    "altera_motor": False,
    "altera_saida": False,
}


def _tipo(obj: Any) -> str:
    return type(obj).__name__


def _len_seguro(obj: Any) -> int | None:
    try:
        return len(obj)
    except Exception:
        return None


def _df_shape(obj: Any) -> tuple[int, int] | None:
    shape = getattr(obj, "shape", None)
    if isinstance(shape, tuple) and len(shape) == 2:
        return int(shape[0]), int(shape[1])
    return None


def _serializar(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _serializar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
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


def auditar_contexto_baseline_shadow(ctx: Any) -> dict[str, Any]:
    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {}

    for nome in ATRIBUTOS_LEGADOS_OBRIGATORIOS:
        valor = getattr(ctx, nome, None)
        evidencias[f"legado.{nome}.tipo"] = _tipo(valor)
        evidencias[f"legado.{nome}.presente"] = valor is not None
        if valor is None:
            erros.append(f"atributo_legado_ausente:{nome}")

    for nome in ATRIBUTOS_SHADOW_NOVOS:
        valor = getattr(ctx, nome, None)
        evidencias[f"shadow.{nome}.tipo"] = _tipo(valor)
        evidencias[f"shadow.{nome}.presente"] = valor is not None
        if valor is None:
            erros.append(f"atributo_shadow_ausente:{nome}")

    pacote_shadow = getattr(ctx, "pacote_entrada_resolvida_shadow", None)
    auditoria_shadow = getattr(ctx, "auditoria_pacote_entrada_resolvida_shadow", None)

    if not isinstance(pacote_shadow, PacoteEntradaResolvida):
        erros.append("pacote_shadow_tipo_invalido")
    if not isinstance(auditoria_shadow, AuditoriaPacoteEntradaResolvida):
        erros.append("auditoria_shadow_tipo_invalido")

    if isinstance(auditoria_shadow, AuditoriaPacoteEntradaResolvida):
        evidencias["auditoria_shadow.ok"] = auditoria_shadow.ok
        evidencias["auditoria_shadow.erros"] = list(auditoria_shadow.erros)
        evidencias["auditoria_shadow.avisos"] = list(auditoria_shadow.avisos)
        if auditoria_shadow.ok is not True:
            erros.append("auditoria_shadow_nao_ok")
        if auditoria_shadow.erros:
            erros.append("auditoria_shadow_contem_erros")

    if isinstance(pacote_shadow, PacoteEntradaResolvida):
        referencias = {
            "pacote_config": getattr(ctx, "pacote_config", None) is pacote_shadow.pacote_config,
            "execucao": getattr(ctx, "execucao", None) is pacote_shadow.contexto_execucao,
            "pacote_planilha": getattr(ctx, "pacote_planilha", None) is pacote_shadow.pacote_planilha,
            "cache_cdi": getattr(ctx, "cache_cdi", None) is pacote_shadow.pacote_cache_cdi,
        }
        evidencias["referencias_identicas_legado_shadow"] = referencias
        for nome, ok in referencias.items():
            if ok is not True:
                erros.append(f"referencia_legado_shadow_nao_identica:{nome}")

        metadados = dict(pacote_shadow.metadados)
        evidencias["metadados_shadow"] = metadados
        for chave, esperado in FLAGS_SHADOW_ESPERADAS.items():
            observado = metadados.get(chave)
            evidencias[f"metadados_shadow.{chave}"] = observado
            if observado is not esperado:
                erros.append(f"metadado_shadow_divergente:{chave}:{observado!r}")

        evidencias["shadow.qtd_quadros_brutos"] = _len_seguro(pacote_shadow.quadros_brutos)
        evidencias["shadow.qtd_quadros_estruturais_resolvidos"] = _len_seguro(
            pacote_shadow.quadros_estruturais_resolvidos
        )
        evidencias["shadow.janela_consulta_cdi_presente"] = pacote_shadow.janela_consulta_cdi is not None

    cache_cdi = getattr(ctx, "cache_cdi", None)
    auditoria_cache = getattr(cache_cdi, "auditoria", {}) if cache_cdi is not None else {}
    evidencias["cache_cdi.origem_janela_consulta"] = auditoria_cache.get("origem_janela_consulta")
    evidencias["cache_cdi.janela_consulta_cdi_informada"] = auditoria_cache.get("janela_consulta_cdi_informada")
    evidencias["cache_cdi.qtd_datas_serie_cdi"] = auditoria_cache.get("qtd_datas_serie_cdi")
    evidencias["cache_cdi.ultima_data_serie_cdi"] = auditoria_cache.get("ultima_data_serie_cdi")

    if auditoria_cache.get("origem_janela_consulta") != "dados_operacionais_legado":
        erros.append("cache_cdi_origem_janela_nao_legada")
    if auditoria_cache.get("janela_consulta_cdi_informada") is not False:
        erros.append("cache_cdi_recebeu_janela_shadow_operacionalmente")

    for nome in ATRIBUTOS_SHADOW_PESADOS_DESATIVADOS:
        valor = getattr(ctx, nome, None)
        evidencias[f"shadow_pesado_desativado.{nome}"] = valor is None
        if valor is not None:
            erros.append(f"shadow_pesado_deveria_estar_desativado:{nome}")

    dados = getattr(ctx, "dados_operacionais", None)
    for nome_df in [
        "carteira_canonica",
        "dados_operacionais.inventario_canonico",
        "dados_operacionais.gastos_canonicos",
        "dados_operacionais.salarios_canonicos",
        "dados_operacionais.switching_canonico",
    ]:
        if nome_df == "carteira_canonica":
            obj = getattr(ctx, "carteira_canonica", None)
        else:
            _, attr = nome_df.split(".", 1)
            obj = getattr(dados, attr, None) if dados is not None else None
        evidencias[f"shape.{nome_df}"] = _df_shape(obj)

    ok = len(erros) == 0
    return {
        "ok": ok,
        "erros": erros,
        "avisos": avisos,
        "evidencias": evidencias,
        "resumo": {
            "tipo_contexto": _tipo(ctx),
            "pacote_shadow_presente": isinstance(pacote_shadow, PacoteEntradaResolvida),
            "auditoria_shadow_presente": isinstance(auditoria_shadow, AuditoriaPacoteEntradaResolvida),
            "auditoria_shadow_ok": getattr(auditoria_shadow, "ok", None),
            "cache_operacional_permanece_legado": auditoria_cache.get("origem_janela_consulta") == "dados_operacionais_legado",
            "atributos_legados_obrigatorios": len(ATRIBUTOS_LEGADOS_OBRIGATORIOS),
            "atributos_shadow_pesados_desativados": len(ATRIBUTOS_SHADOW_PESADOS_DESATIVADOS),
        },
    }


def imprimir_resultado(resultado: dict[str, Any]) -> None:
    print("=== AUDITORIA COMPARATIVA CONTEXTO BASELINE SHADOW V33K ===")
    print("ok=", resultado["ok"])
    print("erros=", resultado["erros"])
    print("avisos=", resultado["avisos"])
    print("resumo=", json.dumps(_serializar(resultado["resumo"]), ensure_ascii=False, sort_keys=True))

    print("\n=== EVIDENCIAS PRINCIPAIS ===")
    chaves = [
        "referencias_identicas_legado_shadow",
        "cache_cdi.origem_janela_consulta",
        "cache_cdi.janela_consulta_cdi_informada",
        "cache_cdi.qtd_datas_serie_cdi",
        "cache_cdi.ultima_data_serie_cdi",
        "auditoria_shadow.ok",
        "auditoria_shadow.erros",
        "auditoria_shadow.avisos",
        "shadow.qtd_quadros_brutos",
        "shadow.qtd_quadros_estruturais_resolvidos",
        "shadow.janela_consulta_cdi_presente",
    ]
    for chave in chaves:
        print(f"{chave}=", _serializar(resultado["evidencias"].get(chave)))

    print("\n=== SHAPES OPERACIONAIS ===")
    for chave, valor in resultado["evidencias"].items():
        if chave.startswith("shape."):
            print(f"{chave}=", valor)

    print("\n=== RESULTADO FINAL ===")
    if resultado["ok"]:
        print("AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW_V33K_OK")
    else:
        print("AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW_V33K_COM_ERROS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita comparativamente o ContextoBaseline após integração shadow do PacoteEntradaResolvida."
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
        help="Caminho opcional para salvar o resultado em JSON. Não é usado por padrão.",
    )
    args = parser.parse_args()

    ctx = carregar_contexto_para_auditoria()
    resultado = auditar_contexto_baseline_shadow(ctx)
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
