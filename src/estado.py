from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from tipos import ConfigProjeto


@dataclass
class EstadoSistema:
    data_referencia: pd.Timestamp
    data_corte_modelo: pd.Timestamp
    data_inicio_otimizacao: pd.Timestamp
    horizonte_final: pd.Timestamp

    gastos: pd.DataFrame
    lotes: pd.DataFrame
    carteiras: pd.DataFrame

    gastos_historicos: pd.DataFrame
    gastos_futuros: pd.DataFrame
    lotes_historicos: pd.DataFrame
    lotes_ativos: pd.DataFrame
    lotes_futuros: pd.DataFrame

    movimentacoes: pd.DataFrame
    decisoes: pd.DataFrame
    eventos: pd.DataFrame

    caixa_livre_centavos: int
    config: ConfigProjeto
    cenario_id: str



def assert_estado_minimo(estado: EstadoSistema) -> None:
    if estado.data_corte_modelo > estado.horizonte_final:
        raise ValueError("data_corte_modelo não pode ser maior que horizonte_final")
    if estado.data_referencia < estado.data_corte_modelo:
        raise ValueError("data_referencia deve ser maior ou igual à data_corte_modelo")
    if estado.data_inicio_otimizacao < estado.data_corte_modelo:
        raise ValueError("data_inicio_otimizacao deve ser maior ou igual à data_corte_modelo")
    if estado.caixa_livre_centavos < 0:
        raise ValueError("caixa_livre_centavos não pode ser negativo")
