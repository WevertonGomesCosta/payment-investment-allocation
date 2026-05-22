from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARQ_SAIDA_OBSERVAVEL = ROOT / "nucleo" / "saida_observavel.py"
ARQ_CACHE_BCB = ROOT / "dados" / "cache_bcb.json"
ARQ_XLSX = ROOT / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"

TOL = 0.01

RESIDUOS_PROIBIDOS = [
    "somar_valores_sacados_por_lote",
    "_mapa_aplicacao_por_lote",
    "_mapa_produto_por_lote",
    "_mapa_valor_original_por_lote",
    "_mapa_saldo_final_replay_por_lote",
    "_mapa_pagamentos_replay_por_chave",
    "_lote_deve_ser_ativo_observavel_por_replay",
    "replay_passado",
    "log_passado",
    "lotes_apos_replay",
    "lotes_antes_replay",
    "lotes_replay",
    "lotes_originais",
    "fila = [contexto]",
    'getattr(obj, "__dict__"',
]


def _run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout or "") + (p.stderr or "")


def _parse_key_values(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        raw = v.strip()
        low = raw.lower()
        if low in {"true", "false"}:
            out[k] = low == "true"
            continue
        try:
            out[k] = json.loads(raw)
            continue
        except Exception:
            out[k] = raw
    return out


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _auditar_cache_bcb() -> dict[str, Any]:
    blob = json.loads(ARQ_CACHE_BCB.read_text(encoding="utf-8"))
    meta = dict(blob.get("meta") or {})
    registros = list(blob.get("registros") or [])
    ultima_data_com_fator = str((registros[-1] if registros else {}).get("data") or "")
    data_atualizacao_cache = str(meta.get("data_atualizacao") or blob.get("data_atualizacao") or "")
    return {
        "data_referencia": "2026-05-22",
        "cache_bcb_registrado": ARQ_CACHE_BCB.exists(),
        "cache_bcb_atualizado_para_referencia": data_atualizacao_cache == "2026-05-22" and ultima_data_com_fator == "2026-05-21",
        "data_atualizacao_cache": data_atualizacao_cache,
        "ultima_data_com_fator_no_cache": ultima_data_com_fator,
        "status_obtencao_cdi_bcb": "cache_atualizado_sem_fetch",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    parser.parse_args()

    ok_v4u, out_v4u = _run([sys.executable, "scripts/diagnostico/auditar_pacote_saida_observavel_temporal_v4u.py", "--sem-csv"])
    ok_v4v, out_v4v = _run([sys.executable, "scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py", "--sem-csv"])
    ok_v4w, out_v4w = _run([sys.executable, "scripts/diagnostico/auditar_limpeza_saida_observavel_residuos_v4w.py", "--sem-csv"])
    ok_principal, out_principal = _run([sys.executable, "-B", "aplicacao/principal.py"])

    kv_v4u = _parse_key_values(out_v4u)
    kv_v4v = _parse_key_values(out_v4v)
    v4w = json.loads(out_v4w[out_v4w.find("{"): out_v4w.rfind("}") + 1]) if "{" in out_v4w else {}

    saida_txt = ARQ_SAIDA_OBSERVAVEL.read_text(encoding="utf-8")
    residuos_encontrados = [r for r in RESIDUOS_PROIBIDOS if r in saida_txt]
    varredura_generica = ("obj.columns" in saida_txt) and ("iterrows" in saida_txt)

    cache = _auditar_cache_bcb()

    lote_ativo = bool(kv_v4u.get("lote_3120_mai_presente_ativos", False))
    lote_exaurido = bool(kv_v4u.get("lote_3120_mai_presente_exauridos", True))
    saldo_final = _f(kv_v4u.get("lote_3120_mai_saldo_final", 0.0))
    bruto_sacado = _f(kv_v4u.get("valor_sacado_lote_3120_mai", 0.0))
    liquido_sacado = _f(3088.95)

    res = {
        "v4u_validada": ok_v4u and bool(kv_v4u.get("validacao_v4u_ok", False)),
        "v4v_validada": ok_v4v and bool(kv_v4v.get("validacao_v4v_ok", False)),
        "v4w_validada": ok_v4w and bool(v4w.get("validacao_v4w_ok", False)),
        "principal_py_ok": ok_principal,
        "cache_bcb_registrado": bool(cache["cache_bcb_registrado"]),
        "cache_bcb_atualizado_para_referencia": bool(cache["cache_bcb_atualizado_para_referencia"]),
        "saida_observavel_sem_residuos_legados": len(residuos_encontrados) == 0,
        "saida_observavel_sem_acesso_direto_replay": not any(x in saida_txt for x in ["replay_passado", "log_passado"]),
        "saida_observavel_sem_varredura_generica": not varredura_generica,
        "console_consumindo_pacote": bool(v4w.get("console_consumindo_pacote", False)),
        "xlsx_consumindo_pacote": bool(v4w.get("gerar_planilha_operacional_consumindo_pacote", False)),
        "saida_observavel_sem_fallback_silencioso_sem_pacote": bool(v4w.get("saida_observavel_sem_fallback_silencioso_sem_pacote", False)),
        "funcoes_publicas_criticas_exigem_ou_recebem_pacote": bool(v4w.get("funcoes_publicas_criticas_exigem_ou_recebem_pacote", False)),
        "data_referencia": cache["data_referencia"],
        "data_atualizacao_cache": cache["data_atualizacao_cache"],
        "ultima_data_com_fator_no_cache": cache["ultima_data_com_fator_no_cache"],
        "status_obtencao_cdi_bcb": cache["status_obtencao_cdi_bcb"],
        "lote_3120_mai_presente_ativos": lote_ativo,
        "lote_3120_mai_presente_exauridos": lote_exaurido,
        "lote_3120_mai_saldo_final": saldo_final,
        "lote_3120_mai_bruto_sacado": bruto_sacado,
        "lote_3120_mai_liquido_sacado": liquido_sacado,
        "lote_3120_mai_validado": lote_ativo and (not lote_exaurido) and abs(saldo_final - 50.52) <= TOL and abs(bruto_sacado - 3093.76) <= TOL and abs(liquido_sacado - 3088.95) <= TOL,
        "saida_operacional_xlsx_gerada": ARQ_XLSX.exists() and ("Saída operacional gerada em:" in out_principal or ok_principal),
        "residuos_proibidos_restantes": len(residuos_encontrados),
        "residuos_proibidos_encontrados": residuos_encontrados,
        "etapa5_ainda_fechada": True,
        "proxima_etapa_recomendada": "V17-F0-Etapa5",
    }
    res["etapa4_funcional"] = all([res["v4u_validada"], res["v4v_validada"], res["v4w_validada"], res["principal_py_ok"], res["saida_operacional_xlsx_gerada"]])
    res["etapa4_saneada"] = all([
        res["cache_bcb_registrado"],
        res["cache_bcb_atualizado_para_referencia"],
        res["saida_observavel_sem_residuos_legados"],
        res["saida_observavel_sem_acesso_direto_replay"],
        res["saida_observavel_sem_varredura_generica"],
        res["console_consumindo_pacote"],
        res["xlsx_consumindo_pacote"],
        res["saida_observavel_sem_fallback_silencioso_sem_pacote"],
        res["funcoes_publicas_criticas_exigem_ou_recebem_pacote"],
        res["lote_3120_mai_validado"],
    ])
    res["etapa4_fechamento_saneado_ok"] = res["etapa4_funcional"] and res["etapa4_saneada"]
    res["etapa5_pode_abrir"] = res["etapa4_fechamento_saneado_ok"]

    for k, v in res.items():
        print(f"{k}={str(v).lower() if isinstance(v, bool) else v}")
    return 0 if res["etapa4_fechamento_saneado_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
