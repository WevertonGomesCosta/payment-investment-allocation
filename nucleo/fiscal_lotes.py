"""Funções fiscais centralizadas para lotes.

A V219 separa a idade fiscal usada para estimativa de IR da idade visual
`Dias corridos`/`Dias úteis` exibida na saída canônica.

Regra:
- idade fiscal usa dias corridos entre aplicação e data de resgate/pagamento;
- não usa date.today() como fallback;
- quando uma data essencial está ausente, retorna 0 dias e a faixa mais
  conservadora de curto prazo fica aplicada pelo chamador.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _coagir_data_fiscal(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        texto = str(valor).strip()
        if not texto or texto.lower() in {"nan", "nat", "none"}:
            return None
        return datetime.fromisoformat(texto[:10]).date()
    except Exception:
        return None


def calcular_idade_fiscal_lote(data_aplicacao: Any, data_referencia: Any) -> int:
    """Calcula idade fiscal em dias corridos para IR regressivo.

    Esta função é diferente de `calcular_dias_lote(...)`:
    - `calcular_dias_lote(...)` alimenta campos visuais e usa dias úteis de
      rendimento para a coluna `Dias úteis`;
    - `calcular_idade_fiscal_lote(...)` alimenta estimativas fiscais e usa
      apenas dias corridos fiscais.
    """
    inicio = _coagir_data_fiscal(data_aplicacao)
    fim = _coagir_data_fiscal(data_referencia)
    if inicio is None or fim is None:
        return 0
    return max((fim - inicio).days, 0)


def aliquota_ir_regressiva_renda_fixa(dias_corridos: Any) -> float:
    """Retorna alíquota de IR regressivo para renda fixa segundo dias corridos."""
    try:
        dias = max(int(dias_corridos), 0)
    except Exception:
        dias = 0
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


def calcular_aliquota_ir_lote(data_aplicacao: Any, data_referencia: Any) -> float:
    """Calcula a alíquota de IR de um lote pela idade fiscal centralizada."""
    dias = calcular_idade_fiscal_lote(data_aplicacao, data_referencia)
    return aliquota_ir_regressiva_renda_fixa(dias)
