from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_ledger_temporal import construir_pacote_ledger_temporal_shadow
from nucleo.saida_canonica import _mapa_pagamentos_central, _quadro_futuro_preferencial
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _indexar_por_pagamento(eventos: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    for evento in eventos:
        pid = _txt(evento.get("pagamento_id") or evento.get("Despesa ID") or evento.get("despesa_id"))
        if pid and pid not in mapa:
            mapa[pid] = evento
    return mapa


def _comparar_eventos_legado_shadow(retorno_legado: dict[str, Any], pacote_shadow: Any) -> dict[str, Any]:
    eventos_legado = list(retorno_legado.get("eventos", []) or [])
    eventos_shadow = list(getattr(pacote_shadow, "eventos_temporais", []) or [])
    fifo_legado = list(retorno_legado.get("fifo_candidatos_avaliados", []) or [])
    fifo_shadow = list(getattr(pacote_shadow, "fifo_candidatos_avaliados", []) or [])

    mapa_legado = _indexar_por_pagamento(eventos_legado)
    mapa_shadow = _indexar_por_pagamento(eventos_shadow)
    ids_legado = set(mapa_legado)
    ids_shadow = set(mapa_shadow)

    divergencias_status = []
    divergencias_motivo = []
    divergencias_saldo = []
    for pid in sorted(ids_legado & ids_shadow):
        leg = mapa_legado[pid]
        sh = mapa_shadow[pid]
        if _txt(leg.get("status")) != _txt(sh.get("status")):
            divergencias_status.append({"pagamento_id": pid, "legado": leg.get("status"), "shadow": sh.get("status")})
        if _txt(leg.get("motivo_bloqueio")) != _txt(sh.get("motivo_bloqueio")):
            divergencias_motivo.append({"pagamento_id": pid, "legado": leg.get("motivo_bloqueio"), "shadow": sh.get("motivo_bloqueio")})
        for campo in ["saldo_antes", "consumo", "saldo_depois"]:
            if _txt(leg.get(campo)) != _txt(sh.get(campo)):
                divergencias_saldo.append({"pagamento_id": pid, "campo": campo, "legado": leg.get(campo), "shadow": sh.get(campo)})

    return {
        "qtd_eventos_legado": len(eventos_legado),
        "qtd_eventos_shadow": len(eventos_shadow),
        "qtd_fifo_legado": len(fifo_legado),
        "qtd_fifo_shadow": len(fifo_shadow),
        "pagamento_ids_legado_total": len(ids_legado),
        "pagamento_ids_shadow_total": len(ids_shadow),
        "pagamento_ids_apenas_legado": sorted(ids_legado - ids_shadow),
        "pagamento_ids_apenas_shadow": sorted(ids_shadow - ids_legado),
        "divergencias_status": divergencias_status,
        "divergencias_motivo": divergencias_motivo,
        "divergencias_saldo": divergencias_saldo,
        "equivalente_eventos": len(eventos_legado) == len(eventos_shadow),
        "equivalente_fifo": len(fifo_legado) == len(fifo_shadow),
        "equivalente_pagamento_ids": ids_legado == ids_shadow,
        "equivalente_status": len(divergencias_status) == 0,
        "equivalente_motivo": len(divergencias_motivo) == 0,
        "equivalente_saldos": len(divergencias_saldo) == 0,
    }


def _montar_linhas_resumo(comparacao: dict[str, Any], pacote_shadow: Any) -> list[dict[str, Any]]:
    validacao = getattr(pacote_shadow, "validacao_ledger_temporal", {}) or {}
    auditoria = getattr(pacote_shadow, "auditoria_ledger_temporal", {}) or {}
    return [
        {"metrica": "validacao_ok", "valor": bool(validacao.get("ok"))},
        {"metrica": "qtd_eventos_legado", "valor": comparacao["qtd_eventos_legado"]},
        {"metrica": "qtd_eventos_shadow", "valor": comparacao["qtd_eventos_shadow"]},
        {"metrica": "qtd_fifo_legado", "valor": comparacao["qtd_fifo_legado"]},
        {"metrica": "qtd_fifo_shadow", "valor": comparacao["qtd_fifo_shadow"]},
        {"metrica": "equivalente_eventos", "valor": comparacao["equivalente_eventos"]},
        {"metrica": "equivalente_fifo", "valor": comparacao["equivalente_fifo"]},
        {"metrica": "equivalente_pagamento_ids", "valor": comparacao["equivalente_pagamento_ids"]},
        {"metrica": "equivalente_status", "valor": comparacao["equivalente_status"]},
        {"metrica": "equivalente_motivo", "valor": comparacao["equivalente_motivo"]},
        {"metrica": "equivalente_saldos", "valor": comparacao["equivalente_saldos"]},
        {"metrica": "usa_contexto_amplo", "valor": auditoria.get("usa_contexto_amplo")},
        {"metrica": "usa_planilha_bruta", "valor": auditoria.get("usa_planilha_bruta")},
        {"metrica": "usa_switching_shadow", "valor": auditoria.get("usa_switching_shadow")},
        {"metrica": "usa_pos_injetado", "valor": auditoria.get("usa_pos_injetado")},
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita PacoteLedgerTemporal shadow V3.7K sem alterar saída canônica.")
    parser.add_argument("--raiz", type=Path, default=ROOT, help="Raiz do repositório")
    parser.add_argument("--sem-csv", action="store_true", help="Não grava CSV diagnóstico")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(raiz_repositorio=args.raiz, instalar_automaticamente=False)
    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)

    retorno_legado = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}
    pacote_shadow = construir_pacote_ledger_temporal_shadow(
        quadro_futuro,
        mapa_central,
        contexto,
        retorno_legado=retorno_legado,
    )
    comparacao = _comparar_eventos_legado_shadow(retorno_legado, pacote_shadow)
    linhas_resumo = _montar_linhas_resumo(comparacao, pacote_shadow)

    print("=== AUDITORIA PACOTE LEDGER TEMPORAL SHADOW V3.7K ===")
    for linha in linhas_resumo:
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(linhas_resumo).to_csv(saida_dir / "auditoria_pacote_ledger_temporal_shadow_v37k_resumo.csv", index=False)
        pd.DataFrame(comparacao.get("divergencias_status", [])).to_csv(saida_dir / "auditoria_pacote_ledger_temporal_shadow_v37k_divergencias_status.csv", index=False)
        pd.DataFrame(comparacao.get("divergencias_motivo", [])).to_csv(saida_dir / "auditoria_pacote_ledger_temporal_shadow_v37k_divergencias_motivo.csv", index=False)
        pd.DataFrame(comparacao.get("divergencias_saldo", [])).to_csv(saida_dir / "auditoria_pacote_ledger_temporal_shadow_v37k_divergencias_saldo.csv", index=False)

    sucesso = all([
        bool(getattr(pacote_shadow, "validacao_ledger_temporal", {}).get("ok")),
        comparacao["equivalente_eventos"],
        comparacao["equivalente_fifo"],
        comparacao["equivalente_pagamento_ids"],
        comparacao["equivalente_status"],
        comparacao["equivalente_motivo"],
        comparacao["equivalente_saldos"],
    ])
    return 0 if sucesso else 1


if __name__ == "__main__":
    raise SystemExit(main())
