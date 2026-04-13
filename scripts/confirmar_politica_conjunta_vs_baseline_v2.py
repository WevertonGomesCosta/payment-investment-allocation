
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline_fase1 import executar_pipeline_inicial
from politica_conjunta_switching import diagnosticar_politica_conjunta_switching


def _normalize_switchings(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "data", "id_lote_origem", "destino", "valor_switching_centavos"
        ])
    out = pd.DataFrame({
        "data": pd.to_datetime(df["data_switching"], errors="coerce").dt.strftime("%Y-%m-%d"),
        "id_lote_origem": df["id_lote_origem"].astype(str),
        "destino": df["carteira_destino"].astype(str),
        "valor_switching_centavos": df["valor_switching_centavos"].astype(int),
    })
    return out.sort_values(["data", "id_lote_origem", "destino", "valor_switching_centavos"]).reset_index(drop=True)


def main() -> None:
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/mnt/data/dados_financeiros.xlsx')
    config_path = ROOT / 'config' / 'config_minimo_v1.json'
    baseline_path = ROOT / 'config' / 'baseline_v2_oficial.json'
    expected_switchings_path = ROOT / 'examples' / 'official_v2_selected_switchings.csv'

    with baseline_path.open('r', encoding='utf-8') as fh:
        baseline = json.load(fh)

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)
    started = time.perf_counter()
    resultado = diagnosticar_politica_conjunta_switching(estado)
    runtime_seconds = time.perf_counter() - started

    resumo = resultado.resumo
    baseline_ref = baseline['reference_summary']

    summary_keys = [
        'data_corte_modelo',
        'data_referencia',
        'horizonte_final',
        'qtd_datas_com_deficit',
        'qtd_datas_com_switching_escolhido',
        'qtd_eventos_switching',
        'qtd_eventos_resgate',
        'saldo_final_caixa_centavos',
        'saldo_final_investido_liquido_centavos',
        'riqueza_final_politica_conjunta_centavos',
        'riqueza_final_politica_base_centavos',
        'ganho_total_vs_politica_base_centavos',
        'cobertura_total_viavel',
    ]
    summary_differences = {}
    for key in summary_keys:
        if resumo.get(key) != baseline_ref.get(key):
            summary_differences[key] = {
                'baseline_v2': baseline_ref.get(key),
                'current_run': resumo.get(key),
            }

    expected_switchings = pd.read_csv(expected_switchings_path)
    expected_switchings['data'] = pd.to_datetime(expected_switchings['data'], errors='coerce').dt.strftime('%Y-%m-%d')
    expected_switchings = expected_switchings[["data", "id_lote_origem", "destino", "valor_switching_centavos"]]
    expected_switchings = expected_switchings.sort_values(["data", "id_lote_origem", "destino", "valor_switching_centavos"]).reset_index(drop=True)

    actual_switchings = _normalize_switchings(resultado.switchings)
    switchings_match = expected_switchings.equals(actual_switchings)

    payload = {
        'status': 'APPROVED' if not summary_differences and switchings_match else 'REJECTED',
        'purpose': 'full end-to-end confirmation of the joint policy with programmatic origin dominance rule embedded',
        'runtime_seconds': round(runtime_seconds, 3),
        'baseline_name': baseline.get('baseline_name'),
        'summary_matches_baseline_v2': not summary_differences,
        'switchings_match_official_v2': bool(switchings_match),
        'summary_differences': summary_differences,
        'baseline_summary': baseline_ref,
        'current_summary': resumo,
        'official_v2_switchings': expected_switchings.to_dict(orient='records'),
        'current_switchings': actual_switchings.to_dict(orient='records'),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
