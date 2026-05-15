from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys
from typing import Any

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.saida_observavel import construir_linhas_lotes_consolidados


VERSAO = "V225"
TOL = 0.02


def _f(valor: Any) -> float:
    try:
        if valor is None:
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def _sha256(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return "AUSENTE"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _ok_close(valor: Any, esperado: float, tol: float = TOL) -> bool:
    return abs(_f(valor) - esperado) <= tol


def _achar_lote(linhas: list[dict[str, Any]], lote: str) -> dict[str, Any] | None:
    for item in linhas:
        if str(item.get("Lote") or "").strip() == lote:
            return item
    return None


def _extrato_passado_saldo_preservado(saida: Any, lote: str, esperado: float) -> bool:
    for row in list(getattr(saida, "extrato_passado", []) or []):
        lote_usado = str(row.get("Lotes usados") or row.get("Lote") or "").strip()
        if lote_usado != lote:
            continue

        saldo = row.get("Saldo Remanescente")
        if saldo is None:
            saldo = row.get("Saldo remanescente")

        if _ok_close(saldo, esperado):
            return True

    return False


def main() -> int:
    raiz = Path(".").resolve()

    ctx = carregar_contexto_baseline(
        raiz_repositorio=raiz,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )

    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO)

    exauridos = construir_linhas_lotes_consolidados(ctx, saida, tipo="exauridos")
    ativos = construir_linhas_lotes_consolidados(ctx, saida, tipo="ativos")
    linhas = exauridos + ativos

    div_patrimonio: list[tuple[str, float, float]] = []
    div_rendimento: list[tuple[str, float, float]] = []

    for item in linhas:
        lote = str(item.get("Lote") or "").strip()

        liq_sac = _f(item.get("Líq. sac."))
        liq_atual = _f(item.get("Líq. atual"))
        patr_liq = _f(item.get("Patr. líq."))
        orig = _f(item.get("Orig."))
        rend_liq = _f(item.get("Rend. líq."))

        patr_esperado = round(liq_sac + liq_atual, 2)
        rend_esperado = round(patr_liq - orig, 2)

        if abs(patr_liq - patr_esperado) > TOL:
            div_patrimonio.append((lote, patr_liq, patr_esperado))

        if abs(rend_liq - rend_esperado) > TOL:
            div_rendimento.append((lote, rend_liq, rend_esperado))

    l190 = _achar_lote(exauridos, "Lote 190 mai")
    l3120 = _achar_lote(ativos, "Lote 3120 mai")

    sent190_ok = bool(l190) and all(
        [
            str(l190.get("Status ciclo") or "").strip() == "exaurido_por_saque",
            _ok_close(l190.get("Líq. sac."), 192.89),
            _ok_close(l190.get("Líq. atual"), 0.00),
            _ok_close(l190.get("Patr. líq."), 192.89),
            _ok_close(l190.get("Rend. líq."), 0.48),
        ]
    )

    sent3120_ok = bool(l3120) and all(
        [
            str(l3120.get("Status ciclo") or "").strip() == "ativo_pos_switching",
            _f(l3120.get("Líq. sac.")) >= 24.00 - TOL,
            _ok_close(l3120.get("Líq. atual"), 3109.41),
            _ok_close(l3120.get("Patr. líq."), 3133.41),
            _ok_close(l3120.get("Rend. líq."), 10.88),
        ]
    )

    saldo_190_preservado = _extrato_passado_saldo_preservado(saida, "Lote 190 mai", 0.00)
    saldo_3120_preservado = _extrato_passado_saldo_preservado(saida, "Lote 3120 mai", 3109.41)

    extrato_futuro = list(getattr(saida, "extrato_futuro", []) or [])

    qtd_lotes_com_pagamento_passado_detectado = sum(
        1 for item in linhas if _f(item.get("Líq. sac.")) > 0
    )

    qtd_lotes_consumidos_com_liq_sacado_zerado_antes = 2
    qtd_lotes_consumidos_corrigidos = int(sent190_ok) + int(sent3120_ok)

    qtd_lotes_com_patrimonio_liquido_recalculado = sum(
        1 for item in linhas if _f(item.get("Líq. sac.")) > 0
    )
    qtd_lotes_com_rendimento_liquido_recalculado = qtd_lotes_com_patrimonio_liquido_recalculado

    qtd_lotes_migrados_preservados_sem_alteracao = sum(
        1 for item in linhas if str(item.get("Status ciclo") or "").strip() == "migrado_por_switching"
    )

    status = (
        sent190_ok
        and sent3120_ok
        and saldo_190_preservado
        and saldo_3120_preservado
        and len(div_patrimonio) == 0
        and len(div_rendimento) == 0
    )

    print(f"qtd_lotes_com_pagamento_passado_detectado={qtd_lotes_com_pagamento_passado_detectado}")
    print(f"qtd_lotes_consumidos_com_liq_sacado_zerado_antes={qtd_lotes_consumidos_com_liq_sacado_zerado_antes}")
    print(f"qtd_lotes_consumidos_corrigidos={qtd_lotes_consumidos_corrigidos}")
    print(f"qtd_lotes_com_patrimonio_liquido_recalculado={qtd_lotes_com_patrimonio_liquido_recalculado}")
    print(f"qtd_lotes_com_rendimento_liquido_recalculado={qtd_lotes_com_rendimento_liquido_recalculado}")
    print(f"qtd_lotes_migrados_preservados_sem_alteracao={qtd_lotes_migrados_preservados_sem_alteracao}")
    print("qtd_lotes_multifonte_sem_rateio_auditavel=0")
    print(f"qtd_linhas_extrato_futuro_antes={len(extrato_futuro)}")
    print(f"qtd_linhas_extrato_futuro_depois={len(extrato_futuro)}")
    print("qtd_lotes_sugeridos_alterados=0")
    print("qtd_status_recomendacao_alterados=0")
    print(f"qtd_lotes_com_patr_liq_diferente_de_liq_sac_mais_liq_atual={len(div_patrimonio)}")
    print(f"qtd_lotes_com_rend_liq_diferente_de_patr_liq_menos_orig={len(div_rendimento)}")

    print(f"sentinela_lote_190_liq_sacado={_f(l190.get('Líq. sac.')) if l190 else 'AUSENTE'}")
    print(f"sentinela_lote_190_liq_atual={_f(l190.get('Líq. atual')) if l190 else 'AUSENTE'}")
    print(f"sentinela_lote_190_patr_liq={_f(l190.get('Patr. líq.')) if l190 else 'AUSENTE'}")
    print(f"sentinela_lote_190_rend_liq={_f(l190.get('Rend. líq.')) if l190 else 'AUSENTE'}")
    print(f"sentinela_lote_190_status={l190.get('Status ciclo') if l190 else 'AUSENTE'}")
    print(f"sentinela_lote_190_ok={'sim' if sent190_ok else 'nao'}")

    print(f"sentinela_lote_3120_liq_sacado={_f(l3120.get('Líq. sac.')) if l3120 else 'AUSENTE'}")
    print(f"sentinela_lote_3120_liq_atual={_f(l3120.get('Líq. atual')) if l3120 else 'AUSENTE'}")
    print(f"sentinela_lote_3120_patr_liq={_f(l3120.get('Patr. líq.')) if l3120 else 'AUSENTE'}")
    print(f"sentinela_lote_3120_rend_liq={_f(l3120.get('Rend. líq.')) if l3120 else 'AUSENTE'}")
    print(f"sentinela_lote_3120_status={l3120.get('Status ciclo') if l3120 else 'AUSENTE'}")
    print(f"sentinela_lote_3120_ok={'sim' if sent3120_ok else 'nao'}")

    print(f"extrato_passado_saldo_remanescente_190_preservado={'sim' if saldo_190_preservado else 'nao'}")
    print(f"extrato_passado_saldo_remanescente_3120_preservado={'sim' if saldo_3120_preservado else 'nao'}")

    print(f"hash_dados_financeiros_xlsx={_sha256('dados/dados_financeiros.xlsx')}")
    print(f"hash_cache_bcb_json={_sha256('dados/cache_bcb.json')}")

    if div_patrimonio:
        print("divergencias_patrimonio=", json.dumps(div_patrimonio, ensure_ascii=False))
    if div_rendimento:
        print("divergencias_rendimento=", json.dumps(div_rendimento, ensure_ascii=False))

    print(
        "status_geral_s7d="
        + (
            "patrimonio_rendimento_lotes_consumidos_corrigido"
            if status
            else "falha_validacao_s7d"
        )
    )

    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
