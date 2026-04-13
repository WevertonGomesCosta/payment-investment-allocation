
from __future__ import annotations

from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.exportacao_workbook_operacional_principal import build_operational_workbook


def main() -> None:
    parser = argparse.ArgumentParser(description='Gera o workbook operacional principal da baseline v2.')
    parser.add_argument('--raw', default=str(ROOT / 'examples' / 'dados_financeiros.xlsx'))
    parser.add_argument('--reference', default=str(ROOT / 'examples' / 'resultado_economica_cliff_agrupado.xlsx'))
    parser.add_argument('--switchings', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_switchings.csv'))
    parser.add_argument('--resgates', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_resgates.csv'))
    parser.add_argument('--timeline', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_timeline.csv'))
    parser.add_argument('--output', default=str(ROOT / 'outputs' / 'workbook_operacional_principal_v2.xlsx'))
    args = parser.parse_args()

    output_workbook = Path(args.output)
    output_workbook.parent.mkdir(parents=True, exist_ok=True)

    build_operational_workbook(
        raw_workbook_path=Path(args.raw),
        reference_workbook_path=Path(args.reference),
        official_switchings_csv=Path(args.switchings),
        official_resgates_csv=Path(args.resgates),
        official_timeline_csv=Path(args.timeline),
        output_path=output_workbook,
    )
    print(f'Workbook gerado em: {output_workbook}')


if __name__ == "__main__":
    main()
