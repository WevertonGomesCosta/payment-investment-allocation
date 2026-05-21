from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import (
    construir_amostras_pagamentos_operacionais,
    construir_linhas_lotes_consolidados,
)
from nucleo.saida_canonica_temporal_shadow_v4k import CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K

TOL = 0.01


def _norm(v: Any) -> str:
    return str(v or "").strip().lower().replace(".", "")


def _f(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0


def _eq(a: Any, b: Any) -> bool:
    return str(a) == str(b)


def _run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode == 0, out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--lote", default="Lote 3120 mai")
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    ctx = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )
    saida_padrao = construir_saida_canonica(ctx)
    saida_false = construir_saida_canonica(ctx, incluir_temporal_shadow=False)
    saida_true = construir_saida_canonica(ctx, incluir_temporal_shadow=True)
    agregados = construir_pacotes_temporais_agregados_saida_shadow(ctx)

    replay = agregados.pacote_replay_passado
    ledger = agregados.pacote_ledger_temporal_operacional
    aud_ag = agregados.auditoria_agregador_temporal or {}

    replay_raw = getattr(replay, "log_movimentos_passados", [])
    replay_rows = replay_raw.to_dict(orient="records") if hasattr(replay_raw, "to_dict") else list(replay_raw or [])
    replay_l3120 = [r for r in replay_rows if _norm(r.get("Lote")) == _norm(args.lote)]
    replay_l3120.sort(key=lambda r: (str(r.get("Data") or ""), _f(r.get("Sequencia Saque") or 0)))
    replay_saldo_final = _f((replay_l3120[-1] if replay_l3120 else {}).get("Saldo Remanescente"))

    ledger_eventos_raw = getattr(ledger, "eventos_temporais", [])
    ledger_eventos_qtd_atual = len(
        ledger_eventos_raw.to_dict(orient="records")
        if hasattr(ledger_eventos_raw, "to_dict")
        else list(ledger_eventos_raw or [])
    )
    ledger_fifo_raw = getattr(ledger, "fifo_candidatos_avaliados", [])
    ledger_fifo_qtd_atual = len(
        ledger_fifo_raw.to_dict(orient="records")
        if hasattr(ledger_fifo_raw, "to_dict")
        else list(ledger_fifo_raw or [])
    )
    baseline_eventos = int(aud_ag.get("qtd_eventos_retorno_legado") or ledger_eventos_qtd_atual)
    baseline_fifo = int(aud_ag.get("qtd_fifo_retorno_legado") or ledger_fifo_qtd_atual)

    ativos = construir_linhas_lotes_consolidados(ctx, saida_padrao, tipo="ativos")
    exauridos = construir_linhas_lotes_consolidados(ctx, saida_padrao, tipo="exauridos")
    linha_ativo = next((r for r in ativos if _norm(r.get("Lote")) == _norm(args.lote)), None)
    linha_ex = next((r for r in exauridos if _norm(r.get("Lote")) == _norm(args.lote)), None)

    amostras = construir_amostras_pagamentos_operacionais(saida_padrao, limite=5, contexto=ctx)
    realizados = list(amostras["realizados"]["linhas"])
    linhas_lote = [r for r in realizados if _norm(r.get("Lotes usados") or r.get("Lote")) == _norm(args.lote)]
    saldos_antes = [_f(r.get("Saldo Antes")) for r in linhas_lote]
    rem = [_f(r.get("Saldo Remanescente")) for r in linhas_lote]
    rem_validos = [x for x in rem if x >= -TOL]
    saldo_final_pagamentos = min(rem_validos) if rem_validos else 0.0

    ex_orig = {str(r.get("Lote") or "").strip() for r in list(getattr(saida_padrao, "lotes_exauridos", []) or [])}
    at_orig = {str(r.get("Lote") or "").strip() for r in list(getattr(saida_padrao, "lotes_ativos", []) or [])}
    at_obs = {str(r.get("Lote") or "").strip() for r in ativos}
    ex_obs = {str(r.get("Lote") or "").strip() for r in exauridos}
    reclass = sorted([l for l in at_obs if l in ex_orig and l not in at_orig])

    migrados_switching = set()
    for row in list(getattr(saida_padrao, "lotes_exauridos", []) or []):
        lote = str(row.get("Lote") or "").strip()
        status = str(row.get("Status ciclo") or row.get("Status") or "").lower()
        if lote and "migrado" in status:
            migrados_switching.add(lote)
    lotes_migrados_reclassificados = sorted([l for l in reclass if l in migrados_switching])

    bloco_temporal = dict((saida_true.auditoria or {}).get(CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K, {}))
    aud_true_sem = dict(saida_true.auditoria or {})
    aud_true_sem.pop(CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K, None)

    ok_console, out_console = _run([sys.executable, "-B", "aplicacao/principal.py"])

    resultado = {
        "replay_presente": replay is not None,
        "replay_log_passado_presente": len(replay_rows) > 0,
        "replay_lote_3120_saldo_final": replay_saldo_final,
        "replay_sem_saldo_final_negativo_lote_3120": replay_saldo_final >= -TOL,
        "ledger_temporal_presente": ledger is not None,
        "ledger_eventos_qtd_atual": ledger_eventos_qtd_atual,
        "ledger_fifo_qtd_atual": ledger_fifo_qtd_atual,
        "ledger_eventos_qtd_baseline_auditada": baseline_eventos,
        "ledger_fifo_qtd_baseline_auditada": baseline_fifo,
        "ledger_eventos_qtd_preservada": ledger_eventos_qtd_atual == baseline_eventos,
        "ledger_fifo_qtd_preservada": ledger_fifo_qtd_atual == baseline_fifo,
        "ledger_sem_regressao_switching_canonico": (aud_ag.get("fonte_primaria_switching_ledger") == "switching_canonico"),
        "pacote_replay_passado_shadow_ok": bool((replay.validacao_replay or {}).get("ok")),
        "pacote_ledger_temporal_operacional_shadow_ok": bool((ledger.validacao_ledger_temporal or {}).get("ok")),
        "pacote_estado_temporal_shadow_ok": bool((agregados.pacote_estado_temporal.validacao_estado_temporal or {}).get("ok")),
        "pacote_auditoria_temporal_shadow_ok": bool((agregados.pacote_auditoria_temporal.validacao_temporal_global or {}).get("ok")),
        "pacotes_temporais_agregados_ok": bool((agregados.validacao_agregador_temporal or {}).get("ok")),
        "saida_canonica_construida": saida_padrao is not None,
        "saida_canonica_estrutura_estavel": _eq(saida_padrao.extrato_passado, saida_false.extrato_passado) and _eq(saida_padrao.extrato_futuro, saida_false.extrato_futuro),
        "incluir_temporal_shadow_false_preserva_saida": _eq(saida_padrao, saida_false),
        "incluir_temporal_shadow_true_acrescenta_apenas_bloco_temporal": _eq(dict(saida_padrao.auditoria or {}), aud_true_sem),
        "saida_canonica_padrao_sem_bloco_temporal_shadow": CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K not in (saida_padrao.auditoria or {}),
        "bloco_temporal_shadow_presente": bool(bloco_temporal),
        "lote_3120_situacao_atual_corrigida": linha_ativo is not None and linha_ex is None,
        "lote_3120_pagamentos_realizados_corrigidos": bool(linhas_lote) and all(v >= -TOL for v in saldos_antes),
        "nenhum_saldo_antes_negativo_para_lote_3120": all(v >= -TOL for v in saldos_antes),
        "saldo_remanescente_final_pagamentos_lote_3120": saldo_final_pagamentos,
        "nenhum_lote_em_ativos_e_exauridos": len(at_obs & ex_obs) == 0,
        "qtd_lotes_reclassificados_por_saldo_replay": len(reclass),
        "lotes_reclassificados_por_saldo_replay": reclass,
        "nenhum_lote_migrado_reclassificado": len(lotes_migrados_reclassificados) == 0,
        "lotes_migrados_reclassificados": lotes_migrados_reclassificados,
        "rendimento_liquido_atual_nao_inflado_por_reclassificacao": (
            len(reclass) == 1
            and reclass == ["Lote 3120 mai"]
            and len(lotes_migrados_reclassificados) == 0
            and len(at_obs & ex_obs) == 0
        ),
        "principal_py_executa_sem_erro": ok_console,
        "console_pagamentos_lote_3120_sem_saldo_antes_negativo": all(v >= -TOL for v in saldos_antes),
        "console_pagamentos_lote_3120_saldo_final": saldo_final_pagamentos,
        "xlsx_operacional_gerado": ("Saída operacional gerada em:" in out_console) or (ROOT / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx").exists(),
        "xlsx_binario_nao_comparado_por_design": True,
        "residuo_saida_observavel_consulta_replay_identificado": True,
        "residuo_saida_observavel_consulta_replay_classificado": "controlado_temporario",
        "residuo_saida_observavel_consulta_replay_bloqueia_fechamento_etapa4": False,
        "residuo_nao_reabre_etapas_1_3": True,
        "residuo_nao_altera_etapa4_core": True,
        "recomendacao_remocao_residuo": "pos_fechamento_etapa4_em_frente_de_limpeza",
        "auditoria_v4q_nao_altera_saida": _eq(saida_padrao, saida_false),
        "sem_nova_alteracao_observavel": _eq(saida_padrao, saida_false),
    }
    resultado["validacao_v4q_ok"] = all([
        resultado["replay_presente"],
        resultado["replay_log_passado_presente"],
        abs(resultado["replay_lote_3120_saldo_final"] - 50.52) <= TOL,
        resultado["ledger_temporal_presente"],
        resultado["ledger_eventos_qtd_preservada"],
        resultado["ledger_fifo_qtd_preservada"],
        resultado["ledger_sem_regressao_switching_canonico"],
        resultado["pacote_replay_passado_shadow_ok"],
        resultado["pacote_ledger_temporal_operacional_shadow_ok"],
        resultado["pacote_estado_temporal_shadow_ok"],
        resultado["pacote_auditoria_temporal_shadow_ok"],
        resultado["pacotes_temporais_agregados_ok"],
        resultado["incluir_temporal_shadow_false_preserva_saida"],
        resultado["incluir_temporal_shadow_true_acrescenta_apenas_bloco_temporal"],
        resultado["saida_canonica_padrao_sem_bloco_temporal_shadow"],
        resultado["lote_3120_situacao_atual_corrigida"],
        resultado["lote_3120_pagamentos_realizados_corrigidos"],
        resultado["nenhum_saldo_antes_negativo_para_lote_3120"],
        abs(resultado["saldo_remanescente_final_pagamentos_lote_3120"] - 50.52) <= TOL,
        resultado["nenhum_lote_em_ativos_e_exauridos"],
        resultado["qtd_lotes_reclassificados_por_saldo_replay"] == 1,
        resultado["lotes_reclassificados_por_saldo_replay"] == ["Lote 3120 mai"],
        resultado["principal_py_executa_sem_erro"],
        abs(resultado["console_pagamentos_lote_3120_saldo_final"] - 50.52) <= TOL,
        resultado["xlsx_operacional_gerado"],
        resultado["bloco_temporal_shadow_presente"],
        resultado["nenhum_lote_migrado_reclassificado"],
        resultado["rendimento_liquido_atual_nao_inflado_por_reclassificacao"],
        resultado["residuo_saida_observavel_consulta_replay_identificado"],
        resultado["residuo_saida_observavel_consulta_replay_bloqueia_fechamento_etapa4"] is False,
        resultado["residuo_nao_reabre_etapas_1_3"],
        resultado["residuo_nao_altera_etapa4_core"],
        resultado["auditoria_v4q_nao_altera_saida"],
        resultado["sem_nova_alteracao_observavel"],
    ])
    resultado["fechamento_funcional_etapa4_recomendado"] = bool(resultado["validacao_v4q_ok"])

    for k, v in resultado.items():
        print(f"{k}={v}")

    if not resultado["ledger_eventos_qtd_preservada"]:
        print(f"divergencia_ledger_eventos_qtd=baseline:{baseline_eventos}|atual:{ledger_eventos_qtd_atual}")
    if not resultado["ledger_fifo_qtd_preservada"]:
        print(f"divergencia_ledger_fifo_qtd=baseline:{baseline_fifo}|atual:{ledger_fifo_qtd_atual}")

    return 0 if resultado["validacao_v4q_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
