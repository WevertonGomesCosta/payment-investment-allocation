from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import (
    construir_amostras_pagamentos_operacionais,
    construir_linhas_lotes_consolidados,
    _mapa_saldo_final_replay_por_lote,
)

TOL = 0.01

def _to_float(v: Any) -> float:
    try:
        return round(float(v), 2)
    except Exception:
        return 0.0

def _norm(v: Any) -> str:
    return str(v or "").strip().lower().replace(".", "")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--lote", default="Lote 3120 mai")
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )
    saida = construir_saida_canonica(contexto)

    ativos = construir_linhas_lotes_consolidados(contexto, saida, tipo="ativos")
    exauridos = construir_linhas_lotes_consolidados(contexto, saida, tipo="exauridos")
    linha_ativo = next((r for r in ativos if _norm(r.get("Lote")) == _norm(args.lote)), None)
    linha_exaurido = next((r for r in exauridos if _norm(r.get("Lote")) == _norm(args.lote)), None)

    amostras = construir_amostras_pagamentos_operacionais(saida, limite=5, contexto=contexto)
    realizados = list(amostras["realizados"]["linhas"])
    linhas_lote = [
        r for r in realizados
        if _norm(r.get("Lotes usados") or r.get("Lote")) == _norm(args.lote)
    ]

    saldos_antes = [_to_float(r.get("Saldo Antes")) for r in linhas_lote]
    remanescentes = [_to_float(r.get("Saldo Remanescente")) for r in linhas_lote]
    remanescentes_validos = [r for r in remanescentes if r >= -TOL]
    saldo_remanescente_final_pagamentos = min(remanescentes_validos) if remanescentes_validos else 0.0
    saldo_final_replay = _to_float(_mapa_saldo_final_replay_por_lote(contexto).get(args.lote))

    resultado = {
        "lote_3120_situacao_atual_corrigida": linha_ativo is not None and linha_exaurido is None,
        "lote_3120_pagamentos_realizados_corrigidos": bool(linhas_lote) and all(s >= -TOL for s in saldos_antes),
        "nenhum_saldo_antes_negativo_para_lote_3120": all(s >= -TOL for s in saldos_antes),
        "saldo_remanescente_final_pagamentos_lote_3120": saldo_remanescente_final_pagamentos,
        "saldo_final_replay_lote_3120": saldo_final_replay,
        "pagamentos_realizados_console_consistente_com_replay": bool(linhas_lote) and abs(saldo_remanescente_final_pagamentos - saldo_final_replay) <= TOL,
        "sem_regressao_lotes_ativos_exauridos": linha_ativo is not None and linha_exaurido is None,
        "linhas_pagamentos_lote_3120": linhas_lote,
    }

    resultado["validacao_v4p0b_ok"] = all([
        resultado["lote_3120_situacao_atual_corrigida"],
        resultado["lote_3120_pagamentos_realizados_corrigidos"],
        resultado["nenhum_saldo_antes_negativo_para_lote_3120"],
        abs(resultado["saldo_remanescente_final_pagamentos_lote_3120"] - 50.52) <= TOL,
        resultado["pagamentos_realizados_console_consistente_com_replay"],
        resultado["sem_regressao_lotes_ativos_exauridos"],
    ])

    for k, v in resultado.items():
        print(f"{k}={v}")

    return 0 if resultado["validacao_v4p0b_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
