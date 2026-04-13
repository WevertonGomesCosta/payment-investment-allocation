"""Ponto de entrada mínimo da V2 para inspeção da baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.ambiente import bootstrap_ambiente
from core.config_loader import load_config
from core.io_planilha import build_workbook_summary, load_workbook


def main() -> None:
    config_bundle = load_config(project_root=REPO_ROOT)
    context = bootstrap_ambiente(
        config_bundle.payload,
        extra_groups=["financeiro"],
        instalar_automaticamente=False,
    )
    workbook_bundle = load_workbook(
        config_bundle.payload,
        project_root=config_bundle.project_root,
    )

    payload = {
        "project_root": str(config_bundle.project_root),
        "config_path": str(config_bundle.path),
        "workbook_path": str(workbook_bundle.path),
        "timezone": context.timezone_name,
        "dependency_report": context.dependency_report,
        "sheet_names": workbook_bundle.sheet_names,
        "workbook_summary": build_workbook_summary(workbook_bundle),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
