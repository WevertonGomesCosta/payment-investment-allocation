from __future__ import annotations

from pathlib import Path

import pandas as pd

from tipos import ConfigProjeto


class WorkbookError(FileNotFoundError):
    """Erro ao localizar ou interpretar o workbook de entrada."""



def resolve_workbook_path(config: ConfigProjeto, workbook_path: str | Path | None = None) -> Path:
    """Resolve o caminho do workbook a partir do config ou de override explícito."""
    if workbook_path is not None:
        path = Path(workbook_path)
    else:
        path = Path(config.arquivos.planilha)

    if not path.exists():
        raise WorkbookError(f"Workbook não encontrado: {path}")
    return path



def load_workbook_from_config(
    config: ConfigProjeto,
    workbook_path: str | Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Carrega o workbook completo preservando todas as abas."""
    path = resolve_workbook_path(config, workbook_path)
    return pd.read_excel(path, sheet_name=None)



def _require_sheet(sheets: dict[str, pd.DataFrame], sheet_name: str) -> pd.DataFrame:
    if sheet_name not in sheets:
        available = sorted(sheets.keys())
        raise WorkbookError(
            f"Aba obrigatória '{sheet_name}' não encontrada. Abas disponíveis: {available}"
        )
    return sheets[sheet_name].copy()



def read_raw_gastos(sheets: dict[str, pd.DataFrame], config: ConfigProjeto) -> pd.DataFrame:
    return _require_sheet(sheets, config.abas.gastos)



def read_raw_lotes(sheets: dict[str, pd.DataFrame], config: ConfigProjeto) -> pd.DataFrame:
    return _require_sheet(sheets, config.abas.lotes)



def read_raw_carteiras(sheets: dict[str, pd.DataFrame], config: ConfigProjeto) -> pd.DataFrame:
    return _require_sheet(sheets, config.abas.carteiras)
