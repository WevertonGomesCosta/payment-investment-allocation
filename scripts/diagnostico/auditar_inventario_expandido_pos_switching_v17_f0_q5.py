from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline

CSV = RAIZ / 'saidas/diagnostico/auditar_inventario_expandido_pos_switching_v17_f0_q5.csv'


def main() -> None:
    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    dop = ctx.dados_operacionais
    inv = getattr(dop, 'inventario_canonico', pd.DataFrame())
    inv_exp = getattr(dop, 'inventario_lotes_expandido', pd.DataFrame())
    pos = getattr(dop, 'lotes_pos_switching_normalizados', pd.DataFrame())
    aud = dict(getattr(dop, 'auditoria_inventario_expandido', {}) or {})

    sentinelas = {'lote 190 mai', 'lote 3120 mai'}
    pos_ids = set(pos.get('lote_id', pd.Series(dtype=str)).astype(str).str.strip().str.lower())

    resumo = {
        'qtd_lotes_inventario_original': int(len(inv)),
        'qtd_lotes_pos_switching_normalizados': int(len(pos)),
        'qtd_lotes_inventario_expandido': int(len(inv_exp)),
        'lote_190_mai_no_expandido': 'sim' if 'lote 190 mai' in pos_ids else 'nao',
        'lote_3120_mai_no_expandido': 'sim' if 'lote 3120 mai' in pos_ids else 'nao',
        'qtd_sentinelas_encontradas': int(len(sentinelas.intersection(pos_ids))),
    }
    resumo.update(aud)

    CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([resumo]).to_csv(CSV, index=False)
    for k, v in resumo.items():
        print(f'{k}={v}')
    print(f'csv={CSV}')


if __name__ == '__main__':
    main()
