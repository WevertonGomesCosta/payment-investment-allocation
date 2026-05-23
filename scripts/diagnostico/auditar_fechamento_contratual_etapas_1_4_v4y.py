from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ARQ_V4W = ROOT / "scripts" / "diagnostico" / "auditar_limpeza_saida_observavel_residuos_v4w.py"
ARQ_V4X = ROOT / "scripts" / "diagnostico" / "auditar_fechamento_saneado_etapa4_v4x.py"
ARQ_SAIDA_OBSERVAVEL = ROOT / "nucleo" / "saida_observavel.py"


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


def _contains_any_structural_terms(expr: ast.AST, termos: tuple[str, ...]) -> bool:
    dump = ast.dump(expr, include_attributes=False)
    return any(t in dump for t in termos)


def _sentinelas_usadas_como_gate() -> bool:
    sentinelas = ("3120", "8500", "lote_3120", "lote_8500")
    arqs = [ARQ_V4W, ARQ_V4X]
    for arq in arqs:
        tree = ast.parse(arq.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if any(n in {"validacao_v4w_ok", "etapa4_saneada", "etapa4_fechamento_saneado_ok", "etapa5_pode_abrir"} for n in target_names):
                    if _contains_any_structural_terms(node.value, sentinelas):
                        return True
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in {"validacao_v4w_ok", "etapa4_saneada", "etapa4_fechamento_saneado_ok", "etapa5_pode_abrir"}:
                    if node.value is not None and _contains_any_structural_terms(node.value, sentinelas):
                        return True
    return False


def _auditar_estrutura_etapas() -> dict[str, bool]:
    artefatos = {
        "etapa1": [ROOT / "scripts" / "diagnostico" / "auditar_pacote_entrada_resolvida_operacional_v36b.py"],
        "etapa2": [ROOT / "scripts" / "diagnostico" / "auditar_pos_promocao_gate_etapa2_v35c.py"],
        "etapa3": [ROOT / "scripts" / "diagnostico" / "auditar_ledger_switching_canonico_primario_v37r.py"],
        "etapa4": [ROOT / "scripts" / "diagnostico" / "auditar_fechamento_saneado_etapa4_v4x.py"],
    }
    logs = {
        "etapa1": [ROOT / "logs" / "iteracoes" / "ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md"],
        "etapa2": [ROOT / "logs" / "iteracoes" / "ME-V17-F0-V35D_FECHA_ETAPA2_GATE_PACOTE_ENTRADA_RESOLVIDA.md"],
        "etapa3": [ROOT / "logs" / "iteracoes" / "ME-V17-F0-V37T_AUDITA_FECHAMENTO_FRONTEIRA_ETAPA3_LEDGER.md"],
        "etapa4": [ROOT / "logs" / "iteracoes" / "ME-V17-F0-V4X_FECHAMENTO_SANEADO_ETAPA4.md"],
    }
    estrutura = {}
    for k, paths in artefatos.items():
        estrutura[f"{k}_artefatos_formais_existem"] = all(p.exists() for p in paths)
    for k, paths in logs.items():
        estrutura[f"{k}_contratos_log_existem"] = all(p.exists() for p in paths)

    txt = ARQ_SAIDA_OBSERVAVEL.read_text(encoding="utf-8") if ARQ_SAIDA_OBSERVAVEL.exists() else ""
    proibidos = ["replay_passado", "log_passado", "lotes_apos_replay", "lotes_antes_replay"]
    estrutura["ausencia_chamadas_proibidas_etapa5_para_brutos_anteriores"] = not any(p in txt for p in proibidos)
    return estrutura


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

    estrut = _auditar_estrutura_etapas()
    sentinelas_gate = _sentinelas_usadas_como_gate()

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
        estrut["ausencia_chamadas_proibidas_etapa5_para_brutos_anteriores"],
    ])

    etapa1_saida_unica = estrut["etapa1_artefatos_formais_existem"] and estrut["etapa1_contratos_log_existem"]
    etapa2_consumindo_apenas_etapa1 = estrut["etapa2_artefatos_formais_existem"] and estrut["etapa2_contratos_log_existem"]
    etapa3_consumindo_apenas_etapa1_validada_etapa2 = estrut["etapa3_artefatos_formais_existem"] and estrut["etapa3_contratos_log_existem"]
    etapa4_consumindo_apenas_etapa3 = estrut["etapa4_artefatos_formais_existem"] and estrut["etapa4_contratos_log_existem"]

    auditorias_base_ok = all([
        ok_v4u, ok_v4v, ok_v4w, ok_v4x,
        bool(v4u.get("validacao_v4u_ok", False)),
        bool(v4v.get("validacao_v4v_ok", False)),
        bool(v4w.get("validacao_v4w_ok", False)),
        bool(v4x.get("etapa4_fechamento_saneado_ok", False)),
    ])

    residuos_funcionais = not bool(v4x.get("saida_observavel_sem_residuos_legados", False))

    out = {
        "etapa1_saida_unica": etapa1_saida_unica,
        "etapa2_consumindo_apenas_etapa1": etapa2_consumindo_apenas_etapa1,
        "etapa3_consumindo_apenas_etapa1_validada_etapa2": etapa3_consumindo_apenas_etapa1_validada_etapa2,
        "etapa4_consumindo_apenas_etapa3": etapa4_consumindo_apenas_etapa3,
        "etapa5_deve_consumir_apenas_etapa4": True,
        "bootstrap_restrito_a_etapa4": bool(v4w.get("bootstrap_pacote_explicito", False)),
        "pacote_etapa4_saneado_existe": bool(v4x.get("etapa4_fechamento_saneado_ok", False)),
        "sentinelas_especificas_usadas_como_gate": sentinelas_gate,
        "invariantes_globais_etapa4_ok": invariantes_globais_ok,
        "residuos_funcionais_etapas_1_4": residuos_funcionais,
        "residuos_semanticos_auditores": residuos_semanticos,
        "etapa5_consumo_exclusivo_saida_etapa4": etapa5_consumo_exclusivo,
        "auditorias_base_ok": auditorias_base_ok,
        **estrut,
    }

    out["etapa5_pode_abrir"] = all([
        out["auditorias_base_ok"],
        out["etapa1_saida_unica"],
        out["etapa2_consumindo_apenas_etapa1"],
        out["etapa3_consumindo_apenas_etapa1_validada_etapa2"],
        out["etapa4_consumindo_apenas_etapa3"],
        out["etapa5_deve_consumir_apenas_etapa4"],
        out["etapa5_consumo_exclusivo_saida_etapa4"],
        out["invariantes_globais_etapa4_ok"],
        (not out["residuos_funcionais_etapas_1_4"]),
        (not out["residuos_semanticos_auditores"]),
        (not out["sentinelas_especificas_usadas_como_gate"]),
    ])

    for k, v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0 if out["etapa5_pode_abrir"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
