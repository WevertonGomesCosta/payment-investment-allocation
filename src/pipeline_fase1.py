from __future__ import annotations

from pathlib import Path

from config_loader import load_config
from carregamento import (
    load_workbook_from_config,
    read_raw_carteiras,
    read_raw_gastos,
    read_raw_lotes,
)
from normalizacao import (
    normalize_carteiras,
    normalize_gastos,
    normalize_lotes,
    vincular_lotes_investidos_a_carteiras,
)
from reconstrucao_historica import construir_estado_inicial_prospectivo
from estado import EstadoSistema
from tipos import ConfigProjeto



def executar_pipeline_inicial(
    config_path: str | Path,
    workbook_path: str | Path | None = None,
) -> tuple[ConfigProjeto, EstadoSistema]:
    config = load_config(config_path)
    sheets = load_workbook_from_config(config, workbook_path=workbook_path)

    gastos_raw = read_raw_gastos(sheets, config)
    lotes_raw = read_raw_lotes(sheets, config)
    carteiras_raw = read_raw_carteiras(sheets, config)

    gastos = normalize_gastos(gastos_raw, config)
    carteiras = normalize_carteiras(carteiras_raw, config)
    lotes = normalize_lotes(lotes_raw, config)
    lotes = vincular_lotes_investidos_a_carteiras(lotes, carteiras)

    estado = construir_estado_inicial_prospectivo(
        gastos=gastos,
        lotes=lotes,
        carteiras=carteiras,
        config=config,
    )
    return config, estado
