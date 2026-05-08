from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

COLUNAS_COMPATIVEIS_SAIDA_SWITCHING = [
    "Data",
    "Data sugerida",
    "Lote origem",
    "Lote destino",
    "Destino",
    "Produto destino switching",
    "Valor líquido origem",
    "valor_liquido_origem",
    "Valor líquido total",
    "Status reconciliação",
    "Origem renderização",
    "Decisão consumo",
]


@dataclass(slots=True)
class PonteRenderizacaoSwitchingV17C6:
    quadro_switching_compativel_saida: pd.DataFrame = field(default_factory=pd.DataFrame)
    switchings_compativeis_saida: list[dict[str, Any]] = field(default_factory=list)
    resumo: dict[str, Any] = field(default_factory=dict)


def _vazio(valor: Any) -> bool:
    if valor is None:
        return True
    if isinstance(valor, float) and pd.isna(valor):
        return True
    return str(valor).strip() == ""


def _valor(row: pd.Series, nome: str, padrao: Any = "") -> Any:
    if nome in row.index and not _vazio(row.get(nome)):
        return row.get(nome)
    return padrao


def _normalizar_data(valor: Any) -> Any:
    if hasattr(valor, "date") and not isinstance(valor, str):
        try:
            return valor.date().isoformat()
        except Exception:
            pass
    if hasattr(valor, "isoformat") and not isinstance(valor, str):
        try:
            return valor.isoformat()[:10]
        except Exception:
            pass
    return str(valor or "").strip()


def _normalizar_numero(valor: Any) -> Any:
    if _vazio(valor):
        return ""
    try:
        return round(float(valor), 2)
    except Exception:
        try:
            return round(float(str(valor).replace(".", "").replace(",", ".")), 2)
        except Exception:
            return valor


def renderizar_switchings_compativeis_saida(pacote_orquestrado_pre_saida: Any) -> PonteRenderizacaoSwitchingV17C6:
    """Renderiza switching do pacote pre-saida em formato compativel com saida.

    Esta ponte e intencionalmente isolada: ela nao altera saida_canonica,
    nao altera motor, nao altera ranking e nao substitui consumo funcional.
    """
    df = getattr(pacote_orquestrado_pre_saida, "estado_temporal_switching", pd.DataFrame())
    if not isinstance(df, pd.DataFrame) or df.empty:
        quadro = pd.DataFrame(columns=COLUNAS_COMPATIVEIS_SAIDA_SWITCHING)
        return PonteRenderizacaoSwitchingV17C6(
            quadro_switching_compativel_saida=quadro,
            switchings_compativeis_saida=[],
            resumo={
                "versao": "V17-C6",
                "switchings_renderizados": 0,
                "campos_essenciais_ausentes": 0,
                "consumido_por_saida_canonica": False,
                "altera_motor": False,
            },
        )

    linhas: list[dict[str, Any]] = []
    essenciais_ausentes = 0
    for i, row in df.iterrows():
        data = _normalizar_data(_valor(row, "data_switching", ""))
        lote_origem = _valor(row, "lote_id_origem", "")
        lote_destino = _valor(row, "lote_id_destino", "")
        destino = _valor(row, "produto_destino", "")
        valor = _normalizar_numero(_valor(row, "valor_liquido_migrado", ""))
        status = _valor(row, "status_reconciliacao", "")
        if any(_vazio(x) for x in [data, lote_origem, lote_destino, destino, valor]):
            essenciais_ausentes += 1
        linhas.append({
            "Data": data,
            "Data sugerida": data,
            "Lote origem": lote_origem,
            "Lote destino": lote_destino,
            "Destino": destino,
            "Produto destino switching": destino,
            "Valor líquido origem": valor,
            "valor_liquido_origem": valor,
            "Valor líquido total": valor,
            "Status reconciliação": status,
            "Origem renderização": "pacote_orquestrado_pre_saida.estado_temporal_switching",
            "Decisão consumo": "ponte_renderizacao_diagnostica_sem_substituir_saida_canonica",
        })

    quadro = pd.DataFrame(linhas)
    for col in COLUNAS_COMPATIVEIS_SAIDA_SWITCHING:
        if col not in quadro.columns:
            quadro[col] = ""
    quadro = quadro[COLUNAS_COMPATIVEIS_SAIDA_SWITCHING].copy()
    return PonteRenderizacaoSwitchingV17C6(
        quadro_switching_compativel_saida=quadro,
        switchings_compativeis_saida=quadro.to_dict(orient="records"),
        resumo={
            "versao": "V17-C6",
            "switchings_renderizados": int(len(quadro)),
            "campos_essenciais_ausentes": int(essenciais_ausentes),
            "consumido_por_saida_canonica": False,
            "altera_motor": False,
        },
    )
