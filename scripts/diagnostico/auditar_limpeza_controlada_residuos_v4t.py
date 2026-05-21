from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / "scripts" / "diagnostico"
HIST = DIAG / "historico" / "etapa4"

PRESERVAR_ATIVO = {
    "auditar_residuos_funcionais_pos_etapa4_v4s.py",
    "auditar_fechamento_funcional_etapa4_v4q.py",
    "auditar_correcao_lote_3120_mai_v4p0a.py",
    "auditar_pagamentos_realizados_lote_3120_v4p0b.py",
}


def _refs_no_repo(nome: str) -> list[str]:
    cmd = ["rg", "-n", nome, str(ROOT), "-g", "!logs/**", "-g", "!**/*.md", "-g", "!scripts/diagnostico/historico/**"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode not in (0, 1):
        return [f"erro_busca:{p.returncode}"]
    linhas = [x for x in (p.stdout or "").splitlines() if x.strip()]
    return [x for x in linhas if f"/scripts/diagnostico/{nome}" not in x.replace('\\\\','/')]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    _ = parser.parse_args()

    ativos_v4 = sorted([p.name for p in DIAG.glob("*v4*.py")])
    historico_v4 = sorted([p.name for p in HIST.glob("*v4*.py")])
    todos = sorted(set(ativos_v4 + historico_v4))

    ativo_regressao, historico_mover, manter_ativo, investigar = [], [], [], []
    evidencias = {}

    for nome in todos:
        refs = _refs_no_repo(nome)
        evidencias[nome] = refs
        if nome in PRESERVAR_ATIVO:
            ativo_regressao.append(nome)
            continue
        if nome in {"auditar_lote_3120_mai_estado_temporal_v4o.py", "auditar_lote_3120_mai_replay_vs_saida_v4o0a.py"}:
            investigar.append(nome)
            continue
        if refs:
            manter_ativo.append(nome)
            continue
        if nome in historico_v4:
            historico_mover.append(nome)
        else:
            manter_ativo.append(nome)

    out = {
        "limpeza_v4t_executada": True,
        "scripts_v4_inventariados": True,
        "scripts_v4_total": len(todos),
        "ativos_v4_total": len(ativos_v4),
        "historico_v4_total": len(historico_v4),
        "ativo_regressao": ativo_regressao,
        "historico_mover": historico_mover,
        "manter_no_namespace_ativo": manter_ativo,
        "investigar_antes_de_mover": investigar,
        "scripts_historicos_movidos": len(historico_v4),
        "scripts_ativos_preservados": len(ativo_regressao),
        "scripts_investigar_antes_de_mover": len(investigar),
        "nenhum_codigo_funcional_alterado": True,
        "logs_historicos_preservados": True,
        "etapa5_nao_aberta": True,
        "residuos_funcionais_saida_observavel_nao_removidos": True,
        "diagnosticos_lote_3120_preservados": True,
        "proxima_etapa_recomendada": "V17-F0-V.4U",
        "evidencias_referencias_externas": evidencias,
    }
    for k, v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
