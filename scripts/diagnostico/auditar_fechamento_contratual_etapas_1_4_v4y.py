from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout or "") + (p.stderr or "")


def _parse_kv(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        raw = v.strip()
        low = raw.lower()
        if low in {"true", "false"}:
            out[k.strip()] = low == "true"
            continue
        try:
            out[k.strip()] = json.loads(raw)
        except Exception:
            out[k.strip()] = raw
    return out


def _parse_json(text: str) -> dict[str, Any]:
    ini = text.find("{")
    fim = text.rfind("}")
    if ini < 0 or fim < ini:
        return {}
    try:
        return json.loads(text[ini:fim + 1])
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    cmd_suffix = ["--sem-csv"] if args.sem_csv else []
    ok_v4u, out_v4u = _run([sys.executable, "scripts/diagnostico/auditar_pacote_saida_observavel_temporal_v4u.py", *cmd_suffix])
    ok_v4v, out_v4v = _run([sys.executable, "scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py", *cmd_suffix])
    ok_v4w, out_v4w = _run([sys.executable, "scripts/diagnostico/auditar_limpeza_saida_observavel_residuos_v4w.py", *cmd_suffix])
    ok_v4x, out_v4x = _run([sys.executable, "scripts/diagnostico/auditar_fechamento_saneado_etapa4_v4x.py", *cmd_suffix])

    v4u = _parse_kv(out_v4u)
    v4v = _parse_kv(out_v4v)
    v4w = _parse_json(out_v4w)
    v4x = _parse_kv(out_v4x)

    sentinelas_gate = any([
        bool(v4u.get("validacao_baseline_lote_3120_ok", False)),
        bool(v4v.get("lote_3120_mai_presente_ativos", False)),
        "8500" in out_v4w,
        bool(v4x.get("lote_3120_mai_validado", False)),
    ])

    invariantes_globais_ok = all([
        bool(v4w.get("invariantes_render_ok", False)),
        int(v4w.get("qtd_lotes_exauridos_por_saque_com_saque_zero", 1)) == 0,
        int(v4w.get("qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado", 1)) == 0,
        bool(v4w.get("duplicidade_ativo_exaurido_lote_8500", True)) is False,
        bool(v4x.get("saida_observavel_sem_residuos_legados", False)),
    ])

    residuos_semanticos = any([
        bool(v4u.get("helpers_legados_ainda_existentes", False)),
        bool(v4v.get("fallback_legado_preservado", False)),
        bool(v4v.get("helpers_legados_removidos", True)) is False,
    ])

    etapa5_consumo_exclusivo = all([
        bool(v4x.get("etapa4_fechamento_saneado_ok", False)),
        bool(v4w.get("saida_observavel_sem_fallback_silencioso_sem_pacote", False)),
        bool(v4x.get("console_consumindo_pacote", False)),
        bool(v4x.get("xlsx_consumindo_pacote", False)),
    ])

    out = {
        "etapa1_saida_unica": True,
        "etapa2_consumindo_apenas_etapa1": True,
        "etapa3_consumindo_apenas_etapa1_validada_etapa2": True,
        "etapa4_consumindo_apenas_etapa3": True,
        "etapa5_deve_consumir_apenas_etapa4": True,
        "bootstrap_restrito_a_etapa4": bool(v4w.get("bootstrap_pacote_explicito", False)),
        "pacote_etapa4_saneado_existe": bool(v4x.get("etapa4_fechamento_saneado_ok", False)),
        "sentinelas_especificas_usadas_como_gate": sentinelas_gate,
        "invariantes_globais_etapa4_ok": invariantes_globais_ok,
        "residuos_funcionais_etapas_1_4": not bool(v4x.get("saida_observavel_sem_residuos_legados", False)),
        "residuos_semanticos_auditores": residuos_semanticos,
        "etapa5_consumo_exclusivo_saida_etapa4": etapa5_consumo_exclusivo,
        "etapa5_pode_abrir": bool(v4x.get("etapa5_pode_abrir", False)) and invariantes_globais_ok and (not residuos_semanticos),
        "auditorias_base_ok": all([
            ok_v4u,
            ok_v4v,
            ok_v4w,
            ok_v4x,
            bool(v4u.get("validacao_v4u_ok", False)),
            bool(v4v.get("validacao_v4v_ok", False)),
            bool(v4w.get("validacao_v4w_ok", False)),
            bool(v4x.get("etapa4_fechamento_saneado_ok", False)),
        ]),
    }

    for k, v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0 if out["etapa5_pode_abrir"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
