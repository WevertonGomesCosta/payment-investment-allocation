"""Leitura e canonização inicial da planilha base do projeto."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

import pandas as pd


@dataclass(slots=True)
class WorkbookBundle:
    """Representa a planilha canônica carregada."""

    path: Path
    sheet_names: list[str]
    raw_frames: dict[str, pd.DataFrame]
    canonical_frames: dict[str, pd.DataFrame]


def _strip_accents(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )


def normalize_text(text: Any) -> str:
    text = "" if text is None else str(text)
    text = _strip_accents(text).strip().lower()
    for old, new in [("/", " "), ("-", " "), ("(", " "), (")", " ")]:
        text = text.replace(old, new)
    return " ".join(text.split())


def build_alias_lookup(alias_map: Mapping[str, Iterable[str]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical_name, aliases in alias_map.items():
        lookup[normalize_text(canonical_name)] = canonical_name
        for alias in aliases:
            lookup[normalize_text(alias)] = canonical_name
    return lookup


def canonicalize_columns(
    frame: pd.DataFrame,
    alias_map: Optional[Mapping[str, Iterable[str]]] = None,
) -> pd.DataFrame:
    """Renomeia colunas a partir do mapa de aliases do config."""
    canonical = frame.copy()
    if not alias_map:
        canonical.columns = [normalize_text(c) for c in canonical.columns]
        return canonical

    lookup = build_alias_lookup(alias_map)
    rename_map: dict[str, str] = {}
    used_targets: set[str] = set()

    for original in canonical.columns:
        normalized = normalize_text(original)
        target = lookup.get(normalized)
        if target is None:
            target = normalized
        if target in used_targets:
            suffix = 2
            candidate = f"{target}__dup{suffix}"
            while candidate in used_targets:
                suffix += 1
                candidate = f"{target}__dup{suffix}"
            target = candidate
        rename_map[original] = target
        used_targets.add(target)

    canonical = canonical.rename(columns=rename_map)
    return canonical


def resolve_workbook_path(
    config: Mapping[str, Any],
    *,
    project_root: Optional[Path] = None,
    explicit_path: Optional[str | Path] = None,
) -> Path:
    if explicit_path is not None:
        path = Path(explicit_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Planilha explícita não encontrada: {path}")
        return path

    root = (project_root or Path.cwd()).resolve()
    arquivos_cfg = config.get("arquivos", {}) if isinstance(config.get("arquivos", {}), Mapping) else {}
    file_name = arquivos_cfg.get("planilha", "dados_financeiros.xlsx")

    candidates = [
        root / "data" / file_name,
        root / file_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = "\n - ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"Planilha não encontrada. Caminhos testados:\n - {tried}")


def load_workbook(
    config: Mapping[str, Any],
    *,
    project_root: Optional[Path] = None,
    explicit_path: Optional[str | Path] = None,
    load_all_sheets: bool = True,
) -> WorkbookBundle:
    """Carrega a planilha base e aplica canonização inicial de colunas."""
    workbook_path = resolve_workbook_path(
        config,
        project_root=project_root,
        explicit_path=explicit_path,
    )

    excel = pd.ExcelFile(workbook_path)
    raw_frames: dict[str, pd.DataFrame] = {}
    canonical_frames: dict[str, pd.DataFrame] = {}

    target_sheets = list(excel.sheet_names) if load_all_sheets else []
    config_sheets = config.get("abas", {}) if isinstance(config.get("abas", {}), Mapping) else {}
    alias_by_block = config.get("colunas", {}) if isinstance(config.get("colunas", {}), Mapping) else {}

    for block_name, sheet_name in config_sheets.items():
        if sheet_name in excel.sheet_names and sheet_name not in target_sheets:
            target_sheets.append(sheet_name)

    for sheet_name in target_sheets:
        frame = pd.read_excel(workbook_path, sheet_name=sheet_name)
        raw_frames[sheet_name] = frame

        block_name = next(
            (block for block, configured_sheet in config_sheets.items() if configured_sheet == sheet_name),
            None,
        )
        alias_map = alias_by_block.get(block_name, {}) if block_name else {}
        canonical_frames[sheet_name] = canonicalize_columns(frame, alias_map=alias_map)

    return WorkbookBundle(
        path=workbook_path,
        sheet_names=list(excel.sheet_names),
        raw_frames=raw_frames,
        canonical_frames=canonical_frames,
    )


def build_workbook_summary(bundle: WorkbookBundle) -> list[dict[str, Any]]:
    """Resumo simples das abas carregadas para auditoria inicial."""
    summary: list[dict[str, Any]] = []
    for sheet_name in bundle.sheet_names:
        frame = bundle.raw_frames.get(sheet_name)
        if frame is None:
            continue
        summary.append(
            {
                "sheet_name": sheet_name,
                "n_rows": int(frame.shape[0]),
                "n_cols": int(frame.shape[1]),
                "columns": list(map(str, frame.columns)),
            }
        )
    return summary
