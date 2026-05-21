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
    return str(v or '').strip().lower().replace('.', '')

def _buscar_linha(linhas: list[dict[str, Any]], lote: str) -> dict[str, Any] | None:
    alvo = _norm(lote)
    for row in linhas:
        if _norm(row.get('Lote')) == alvo:
            return row
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--raiz', type=Path, default=ROOT)
    parser.add_argument('--lote', default='Lote 3120 mai')
    parser.add_argument('--sem-csv', action='store_true')
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )
    saida = construir_saida_canonica(contexto)

    ativos = construir_linhas_lotes_consolidados(contexto, saida, tipo='ativos')
    exauridos = construir_linhas_lotes_consolidados(contexto, saida, tipo='exauridos')
    mapa_final = _mapa_saldo_final_replay_por_lote(contexto)

    linha_ativo = _buscar_linha(ativos, args.lote)
    linha_exaurido = _buscar_linha(exauridos, args.lote)
    saldo_3120 = _to_float(mapa_final.get(args.lote))
    liq_atual = _to_float((linha_ativo or {}).get('Líq. atual'))
    rend_liq = _to_float((linha_ativo or {}).get('Rend. líq.'))

    exauridos_originais = {str(row.get('Lote') or '').strip() for row in list(getattr(saida, 'lotes_exauridos', []) or [])}
    ativos_originais = {str(row.get('Lote') or '').strip() for row in list(getattr(saida, 'lotes_ativos', []) or [])}

    ativos_obs = {str(row.get('Lote') or '').strip() for row in ativos}
    exauridos_obs = {str(row.get('Lote') or '').strip() for row in exauridos}
    intersecao = sorted(ativos_obs & exauridos_obs)

    reclassificados = sorted([
        lote for lote in ativos_obs
        if lote in exauridos_originais and lote not in ativos_originais
    ])

    migrados_reclassificados = [
        lote for lote in reclassificados
        if any(
            str(row.get('Lote') or '').strip() == lote
            and 'migrado' in str(row.get('Status ciclo') or row.get('Status') or '').lower()
            for row in list(getattr(saida, 'lotes_exauridos', []) or [])
        )
    ]

    resultado = {
        'lote_3120_corrigido': linha_ativo is not None and linha_exaurido is None,
        'lote_3120_replay_saldo_final_preservado': abs(saldo_3120 - 50.52) <= TOL,
        'lote_3120_liquido_atual_corrigido': abs(liq_atual - saldo_3120) <= TOL,
        'lote_3120_rendimento_liquido_nao_negativo_por_zeragem_incorreta': rend_liq >= -TOL,
        'qtd_lotes_reclassificados_por_saldo_replay': len(reclassificados),
        'lotes_reclassificados_por_saldo_replay': reclassificados,
        'nenhum_lote_migrado_reclassificado': len(migrados_reclassificados) == 0,
        'lotes_migrados_reclassificados': migrados_reclassificados,
        'nenhum_lote_em_ativos_e_exauridos': len(intersecao) == 0,
        'lotes_em_ativos_e_exauridos': intersecao,
        'validacao_v4p0a_ok': (
            linha_ativo is not None
            and linha_exaurido is None
            and abs(saldo_3120 - 50.52) <= TOL
            and abs(liq_atual - saldo_3120) <= TOL
            and rend_liq >= -TOL
            and reclassificados == ['Lote 3120 mai']
            and len(migrados_reclassificados) == 0
            and len(intersecao) == 0
        ),
    }

    for k, v in resultado.items():
        print(f"{k}={v}")

    return 0 if resultado['validacao_v4p0a_ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
