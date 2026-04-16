"""Camada neutra compartilhada de calendário financeiro e taxas/CDI base.

Este módulo consolida apenas primitivas já sustentadas pelos blocos auditados:
- CDI anual de modelo e taxa diária base;
- convenção de dias do ano para CDI;
- cálculo de Páscoa e dias sem rendimento bancário;
- verificação de dia de rendimento;
- contagem de dias de rendimento;
- metadados básicos de série CDI, sem fetch de rede.

Ele NÃO implementa:
- fetch do BCB;
- cache operacional da série CDI;
- aplicação do CDI aos lotes;
- regras fiscais;
- replay do passado.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable, Mapping, Optional

try:
    from workalendar.america import Brazil
except Exception:  # pragma: no cover
    Brazil = None  # type: ignore


@dataclass(slots=True)
class PacoteCalendarioFinanceiro:
    data_referencia: date
    cdi_anual_modelo: float
    convencao_dias_ano_cdi: int
    taxa_dia_base: float
    ano_inicio_dias_sem_rendimento: int
    ano_fim_dias_sem_rendimento: int
    dias_sem_rendimento_bancario: set[date]
    calendario_brasil_disponivel: bool
    workalendar_disponivel: bool
    auditoria: dict[str, Any]


@dataclass(slots=True)
class MetadataSerieCDI:
    data_inicial: Optional[date]
    data_final: Optional[date]
    qtd_observacoes: int


def _cfg_get(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


def obter_cdi_anual_modelo(config: Mapping[str, Any]) -> float:
    valor = _cfg_get(config, "premissas_mercado", "cdi_anual_modelo", padrao=None)
    if valor in (None, ""):
        raise KeyError("Config obrigatório ausente: premissas_mercado/cdi_anual_modelo")
    return float(valor)


def obter_convencao_dias_ano_cdi(config: Mapping[str, Any]) -> int:
    valor = _cfg_get(config, "execucao", "convencao_dias_ano", "cdi", padrao=None)
    if valor in (None, ""):
        raise KeyError("Config obrigatório ausente: execucao/convencao_dias_ano/cdi")
    return int(valor)


def calcular_taxa_dia_base(cdi_anual_modelo: float, convencao_dias_ano_cdi: int) -> float:
    if convencao_dias_ano_cdi <= 0:
        raise ValueError("A convenção de dias do ano para CDI deve ser positiva.")
    return ((1.0 + float(cdi_anual_modelo)) ** (1.0 / int(convencao_dias_ano_cdi))) - 1.0


def calcular_pascoa(ano: int) -> date:
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def gerar_dias_sem_rendimento_bancario(ano_inicio: int, ano_fim: int) -> set[date]:
    if ano_fim < ano_inicio:
        raise ValueError("ano_fim < ano_inicio na geração de dias sem rendimento bancário.")
    dias: set[date] = set()
    for ano in range(int(ano_inicio), int(ano_fim) + 1):
        pascoa = calcular_pascoa(ano)
        terca_carnaval = pascoa - timedelta(days=47)
        dias.add(terca_carnaval)
    return dias


def _coagir_para_date(valor: Any) -> Optional[date]:
    if valor is None:
        return None
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor
    try:
        if hasattr(valor, "date"):
            return valor.date()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(str(valor)).date()
    except Exception:
        return None


def extrair_metadata_serie_cdi(serie_cdi: Any) -> MetadataSerieCDI:
    datas: list[date] = []

    try:
        if isinstance(serie_cdi, Mapping):
            datas = [_coagir_para_date(k) for k in serie_cdi.keys()]
        elif isinstance(serie_cdi, list):
            for item in serie_cdi:
                if isinstance(item, (tuple, list)) and len(item) >= 1:
                    datas.append(_coagir_para_date(item[0]))
                elif isinstance(item, Mapping):
                    datas.append(_coagir_para_date(item.get("Data") or item.get("data")))
        elif hasattr(serie_cdi, "index") and not hasattr(serie_cdi, "columns"):
            datas = [_coagir_para_date(x) for x in list(serie_cdi.index)]
        elif hasattr(serie_cdi, "columns"):
            col_data = None
            for cand in ("Data", "data", "DATE", "date"):
                if cand in getattr(serie_cdi, "columns", []):
                    col_data = cand
                    break
            if col_data is not None:
                datas = [_coagir_para_date(x) for x in list(serie_cdi[col_data])]
    except Exception:
        datas = []

    datas = [d for d in datas if d is not None]
    if not datas:
        return MetadataSerieCDI(data_inicial=None, data_final=None, qtd_observacoes=0)
    return MetadataSerieCDI(
        data_inicial=min(datas),
        data_final=max(datas),
        qtd_observacoes=len(datas),
    )


def construir_calendario_financeiro(
    config: Mapping[str, Any],
    *,
    data_referencia: date,
) -> PacoteCalendarioFinanceiro:
    cdi_anual_modelo = obter_cdi_anual_modelo(config)
    convencao_dias_ano_cdi = obter_convencao_dias_ano_cdi(config)
    taxa_dia_base = calcular_taxa_dia_base(cdi_anual_modelo, convencao_dias_ano_cdi)

    ano_inicio = int(_cfg_get(config, "calendario", "ano_inicio_dias_sem_rendimento", padrao=data_referencia.year))
    ano_fim = int(_cfg_get(config, "calendario", "ano_fim_dias_sem_rendimento", padrao=data_referencia.year + 10))
    dias_sem_rendimento = gerar_dias_sem_rendimento_bancario(ano_inicio, ano_fim)

    calendario_brasil = None
    if Brazil is not None:
        try:
            calendario_brasil = Brazil()
        except Exception:
            calendario_brasil = None

    auditoria = {
        "cdi_anual_modelo": cdi_anual_modelo,
        "convencao_dias_ano_cdi": convencao_dias_ano_cdi,
        "taxa_dia_base": taxa_dia_base,
        "ano_inicio_dias_sem_rendimento": ano_inicio,
        "ano_fim_dias_sem_rendimento": ano_fim,
        "qtd_dias_sem_rendimento": len(dias_sem_rendimento),
    }

    return PacoteCalendarioFinanceiro(
        data_referencia=data_referencia,
        cdi_anual_modelo=cdi_anual_modelo,
        convencao_dias_ano_cdi=convencao_dias_ano_cdi,
        taxa_dia_base=taxa_dia_base,
        ano_inicio_dias_sem_rendimento=ano_inicio,
        ano_fim_dias_sem_rendimento=ano_fim,
        dias_sem_rendimento_bancario=dias_sem_rendimento,
        calendario_brasil_disponivel=calendario_brasil is not None,
        workalendar_disponivel=Brazil is not None,
        auditoria=auditoria,
    )


def eh_dia_util_bancario(data_atual: date, pacote: PacoteCalendarioFinanceiro) -> bool:
    if data_atual in pacote.dias_sem_rendimento_bancario:
        return False

    if Brazil is not None:
        try:
            return bool(Brazil().is_working_day(data_atual))
        except Exception:
            pass

    # Fallback neutro: dias úteis padrão de segunda a sexta.
    return data_atual.weekday() < 5


def obter_taxa_dia_rendimento(
    data_atual: date,
    pacote: PacoteCalendarioFinanceiro,
    *,
    serie_cdi: Optional[Mapping[date, Any]] = None,
    taxa_proj: Optional[float] = None,
    data_fechamento_referencia: Optional[date] = None,
) -> tuple[bool, Optional[float], dict[str, Any]]:
    if data_atual in pacote.dias_sem_rendimento_bancario:
        return False, None, {'fonte': 'feriado_sem_rendimento', 'data_fator': None, 'fallback': False}

    if serie_cdi:
        if data_atual in serie_cdi:
            fator_dia = float(serie_cdi[data_atual])
            return True, fator_dia - 1.0, {'fonte': 'serie_cdi_bcb', 'data_fator': data_atual, 'fallback': False}

        permitir_fallback = (
            data_fechamento_referencia is not None
            and data_atual == data_fechamento_referencia
            and eh_dia_util_bancario(data_atual, pacote)
        )
        if permitir_fallback:
            datas_anteriores = [dt for dt in serie_cdi.keys() if isinstance(dt, date) and dt < data_atual]
            if datas_anteriores:
                data_fator = max(datas_anteriores)
                fator_dia = float(serie_cdi[data_fator])
                return True, fator_dia - 1.0, {
                    'fonte': 'fallback_ultimo_fator_cdi',
                    'data_fator': data_fator,
                    'fallback': True,
                }

        return False, None, {'fonte': 'serie_cdi_sem_data', 'data_fator': None, 'fallback': False}

    if eh_dia_util_bancario(data_atual, pacote):
        taxa_uso = float(pacote.taxa_dia_base if taxa_proj is None else taxa_proj)
        return True, taxa_uso, {'fonte': 'taxa_modelo', 'data_fator': data_atual, 'fallback': False}

    return False, None, {'fonte': 'nao_eh_dia_util_bancario', 'data_fator': None, 'fallback': False}


def is_dia_rendimento(
    data_atual: date,
    pacote: PacoteCalendarioFinanceiro,
    serie_cdi: Optional[Mapping[date, Any]] = None,
    *,
    data_fechamento_referencia: Optional[date] = None,
) -> bool:
    aplicar, _, _ = obter_taxa_dia_rendimento(
        data_atual,
        pacote,
        serie_cdi=serie_cdi,
        data_fechamento_referencia=data_fechamento_referencia,
    )
    return bool(aplicar)


def contar_dias_rendimento(
    data_inicio: date,
    data_fim: date,
    pacote: PacoteCalendarioFinanceiro,
    serie_cdi: Optional[Mapping[date, Any]] = None,
    *,
    data_fechamento_referencia: Optional[date] = None,
) -> int:
    if data_fim <= data_inicio:
        return 0
    dias = 0
    atual = data_inicio + timedelta(days=1)
    while atual <= data_fim:
        if is_dia_rendimento(atual, pacote, serie_cdi=serie_cdi, data_fechamento_referencia=data_fechamento_referencia):
            dias += 1
        atual += timedelta(days=1)
    return dias
