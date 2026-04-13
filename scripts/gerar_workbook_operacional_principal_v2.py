
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.exportacao_workbook_operacional_principal import build_operational_workbook


def main() -> None:
    data_dir = ROOT / "examples"
    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_workbook = output_dir / "workbook_operacional_principal_v2.xlsx"
    build_operational_workbook(
        raw_workbook_path=data_dir / "dados_financeiros.xlsx",
        reference_workbook_path=data_dir / "resultado_economica_cliff_agrupado.xlsx",
        official_switchings_csv=data_dir / "full_end_to_end_confirmation_v2_switchings.csv",
        official_resgates_csv=data_dir / "full_end_to_end_confirmation_v2_resgates.csv",
        official_timeline_csv=data_dir / "full_end_to_end_confirmation_v2_timeline.csv",
        output_path=output_workbook,
    )
    print(f"Workbook gerado em: {output_workbook}")


if __name__ == "__main__":
    main()
