from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import construir_amostras_pagamentos_operacionais, construir_linhas_lotes_consolidados

ARQ_SAIDA_OBSERVAVEL = ROOT / "nucleo" / "saida_observavel.py"
ARQ_CACHE_BCB = ROOT / "dados" / "cache_bcb.json"
ARQ_XLSX = ROOT / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
TOL = 0.01

FUNCOES_PROIBIDAS = {
    "somar_valores_sacados_por_lote",
    "_mapa_aplicacao_por_lote",
    "_mapa_produto_por_lote",
    "_mapa_valor_original_por_lote",
    "_mapa_saldo_final_replay_por_lote",
    "_mapa_pagamentos_replay_por_chave",
    "_lote_deve_ser_ativo_observavel_por_replay",
}


def _run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout or "") + (p.stderr or "")


def _parse_key_values(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        raw = v.strip()
        low = raw.lower()
        if low in {"true", "false"}:
            out[k.strip()] = low == "true"
        else:
            try:
                out[k.strip()] = json.loads(raw)
            except Exception:
                out[k.strip()] = raw
    return out


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _auditar_cache_bcb() -> dict[str, Any]:
    if not ARQ_CACHE_BCB.exists():
        return {
            "data_referencia": "2026-05-22",
            "cache_bcb_registrado": False,
            "cache_bcb_atualizado_para_referencia": False,
            "data_atualizacao_cache": "",
            "ultima_data_com_fator_no_cache": "",
            "status_obtencao_cdi_bcb": "cache_bcb_ausente",
        }
    blob = json.loads(ARQ_CACHE_BCB.read_text(encoding="utf-8"))
    meta = dict(blob.get("meta") or {})
    registros = list(blob.get("registros") or [])
    ultima_data = str((registros[-1] if registros else {}).get("data") or "")
    atualizacao = str(meta.get("data_atualizacao") or blob.get("data_atualizacao") or "")
    return {
        "data_referencia": "2026-05-22",
        "cache_bcb_registrado": True,
        "cache_bcb_atualizado_para_referencia": atualizacao == "2026-05-22" and ultima_data == "2026-05-21",
        "data_atualizacao_cache": atualizacao,
        "ultima_data_com_fator_no_cache": ultima_data,
        "status_obtencao_cdi_bcb": "cache_atualizado_sem_fetch",
    }


def _auditar_residuos_ast() -> dict[str, Any]:
    tree = ast.parse(ARQ_SAIDA_OBSERVAVEL.read_text(encoding="utf-8"))
    defs, calls, replay, dict_scan, df_scan = [], [], [], [], []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in FUNCOES_PROIBIDAS:
            defs.append(node.name)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FUNCOES_PROIBIDAS:
                calls.append(node.func.id)
            if isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
                arg1 = node.args[1]
                if isinstance(arg1, ast.Constant) and arg1.value in {"replay_passado", "log_passado", "__dict__"}:
                    if arg1.value == "__dict__":
                        dict_scan.append("getattr.__dict__")
                    else:
                        replay.append(f"getattr.{arg1.value}")
        if isinstance(node, ast.Attribute) and node.attr in {"replay_passado", "log_passado"}:
            replay.append(f"attr.{node.attr}")
        if isinstance(node, ast.Name) and node.id in {"lotes_apos_replay", "lotes_antes_replay", "lotes_replay", "lotes_originais"}:
            replay.append(f"name.{node.id}")
        if isinstance(node, ast.Attribute) and node.attr == "columns":
            df_scan.append("attr.columns")
        if isinstance(node, ast.Attribute) and node.attr == "iterrows":
            df_scan.append("attr.iterrows")

    ativos = sorted(set(defs + calls + replay + dict_scan))
    varredura_generica_ativa = ("attr.columns" in df_scan) and ("attr.iterrows" in df_scan)
    return {
        "residuos_proibidos_funcionais_restantes": len(ativos),
        "residuos_proibidos_funcionais_encontrados": ativos,
        "saida_observavel_sem_residuos_legados": len(ativos) == 0,
        "saida_observavel_sem_acesso_direto_replay": not any(x.startswith(("getattr.replay_passado", "getattr.log_passado", "attr.replay_passado", "attr.log_passado", "name.lotes_")) for x in ativos),
        "saida_observavel_sem_varredura_generica": not varredura_generica_ativa,
    }


def _auditar_lote_3120() -> dict[str, Any]:
    ctx = carregar_contexto_baseline(raiz_repositorio=ROOT, instalar_automaticamente=False, incluir_benchmark_agrupado_individual_shadow=False)
    saida = construir_saida_canonica(ctx)
    ativos = construir_linhas_lotes_consolidados(ctx, saida, tipo="ativos")
    exauridos = construir_linhas_lotes_consolidados(ctx, saida, tipo="exauridos")
    am = construir_amostras_pagamentos_operacionais(saida, limite=1000, contexto=ctx)
    realizados = list((am.get("realizados") or {}).get("linhas") or [])
    pacote = construir_pacote_saida_observavel_temporal(ctx, saida, lotes_ativos_observaveis=ativos, lotes_exauridos_observaveis=exauridos, pagamentos_realizados_observaveis=realizados)
    ativos_pkg = construir_linhas_lotes_consolidados(ctx, saida, tipo="ativos", pacote_saida_observavel_temporal=pacote)
    ex_pkg = construir_linhas_lotes_consolidados(ctx, saida, tipo="exauridos", pacote_saida_observavel_temporal=pacote)
    alvo = next((r for r in ativos_pkg if str(r.get("Lote") or "").strip().lower().replace('.', '') == "lote 3120 mai"), {})
    return {
        "lote_3120_mai_presente_ativos": bool(alvo),
        "lote_3120_mai_presente_exauridos": any(str(r.get("Lote") or "").strip().lower().replace('.', '') == "lote 3120 mai" for r in ex_pkg),
        "lote_3120_mai_saldo_final": _f(alvo.get("Líq. atual", 0.0)),
        "lote_3120_mai_bruto_sacado": _f(alvo.get("Bruto sac.", 0.0)),
        "lote_3120_mai_liquido_sacado": _f(alvo.get("Líq. sac.", 0.0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    parser.parse_args()
    ok_v4u, out_v4u = _run([sys.executable, "scripts/diagnostico/auditar_pacote_saida_observavel_temporal_v4u.py", "--sem-csv"])
    ok_v4v, out_v4v = _run([sys.executable, "scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py", "--sem-csv"])
    ok_v4w, out_v4w = _run([sys.executable, "scripts/diagnostico/auditar_limpeza_saida_observavel_residuos_v4w.py", "--sem-csv"])
    ok_principal, out_principal = _run([sys.executable, "-B", "aplicacao/principal.py"])
    kv_v4u, kv_v4v = _parse_key_values(out_v4u), _parse_key_values(out_v4v)
    v4w = {}
    v4w_parse_ok = True
    v4w_parse_erro = ""
    try:
        if "{" in out_v4w and "}" in out_v4w:
            v4w = json.loads(out_v4w[out_v4w.find("{"): out_v4w.rfind("}") + 1])
        else:
            raise ValueError("json_v4w_nao_encontrado_no_output")
    except Exception as exc:
        v4w_parse_ok = False
        v4w_parse_erro = str(exc)
        v4w = {}

    principal_ambiente = "erro_csv_s6_ausente_sem_recomposicao_segura" in out_principal
    cache = _auditar_cache_bcb()
    residuos = _auditar_residuos_ast()
    lote = _auditar_lote_3120()

    res = {
        "v4u_validada": ok_v4u and bool(kv_v4u.get("validacao_v4u_ok", False)),
        "v4v_validada": ok_v4v and bool(kv_v4v.get("validacao_v4v_ok", False)),
        "v4w_validada": ok_v4w and v4w_parse_ok and bool(v4w.get("validacao_v4w_ok", False)),
        "v4w_parse_ok": v4w_parse_ok,
        "v4w_parse_erro": v4w_parse_erro,
        "principal_py_ok": ok_principal,
        "principal_py_falha_ambiente": principal_ambiente,
        "principal_py_erro": "erro_csv_s6_ausente_sem_recomposicao_segura" if principal_ambiente else "",
        "cache_bcb_registrado": bool(cache["cache_bcb_registrado"]),
        "cache_bcb_atualizado_para_referencia": bool(cache["cache_bcb_atualizado_para_referencia"]),
        "console_consumindo_pacote": bool(v4w.get("console_consumindo_pacote", False)),
        "xlsx_consumindo_pacote": bool(v4w.get("gerar_planilha_operacional_consumindo_pacote", False)),
        "saida_observavel_sem_fallback_silencioso_sem_pacote": bool(v4w.get("saida_observavel_sem_fallback_silencioso_sem_pacote", False)),
        "funcoes_publicas_criticas_exigem_ou_recebem_pacote": bool(v4w.get("funcoes_publicas_criticas_exigem_ou_recebem_pacote", False)),
        "data_referencia": cache["data_referencia"],
        "data_atualizacao_cache": cache["data_atualizacao_cache"],
        "ultima_data_com_fator_no_cache": cache["ultima_data_com_fator_no_cache"],
        "status_obtencao_cdi_bcb": cache["status_obtencao_cdi_bcb"],
        **lote,
        **residuos,
        "saida_operacional_xlsx_gerada": ARQ_XLSX.exists() and ("Saída operacional gerada em:" in out_principal or ok_principal),
    }
    res["lote_3120_mai_validado"] = (
        res["lote_3120_mai_presente_ativos"]
        and (not res["lote_3120_mai_presente_exauridos"])
        and abs(res["lote_3120_mai_saldo_final"] - 50.52) <= TOL
        and abs(res["lote_3120_mai_bruto_sacado"] - 3093.76) <= TOL
        and abs(res["lote_3120_mai_liquido_sacado"] - 3088.95) <= TOL
    )
    res["etapa4_funcional"] = all([res["v4u_validada"], res["v4v_validada"], res["v4w_validada"], res["saida_operacional_xlsx_gerada"]]) and (res["principal_py_ok"] or res["principal_py_falha_ambiente"])
    res["etapa4_saneada"] = all([
        res["cache_bcb_registrado"], res["cache_bcb_atualizado_para_referencia"], res["saida_observavel_sem_residuos_legados"], res["saida_observavel_sem_acesso_direto_replay"], res["saida_observavel_sem_varredura_generica"], res["console_consumindo_pacote"], res["xlsx_consumindo_pacote"], res["saida_observavel_sem_fallback_silencioso_sem_pacote"], res["funcoes_publicas_criticas_exigem_ou_recebem_pacote"], res["lote_3120_mai_validado"]
    ])
    res["etapa4_fechamento_saneado_ok"] = res["etapa4_funcional"] and res["etapa4_saneada"]
    res["etapa5_pode_abrir"] = res["etapa4_fechamento_saneado_ok"]
    res["proxima_etapa_recomendada"] = "V17-F0-Etapa5" if res["etapa5_pode_abrir"] else "V17-F0-V.4X-ajuste"

    for k, v in res.items():
        print(f"{k}={str(v).lower() if isinstance(v, bool) else v}")
    return 0 if res["etapa4_fechamento_saneado_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
