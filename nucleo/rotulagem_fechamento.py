from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Mapping, Optional

from nucleo.calendario_financeiro import eh_dia_util_bancario


def _fmt_data(valor: Optional[date]) -> Optional[str]:
    return valor.isoformat() if hasattr(valor, 'isoformat') else None


def resumir_fechamento_situacao_atual(
    *,
    data_referencia: date,
    calendario_financeiro: Any,
    serie_cdi: Optional[Mapping[date, Any]] = None,
) -> dict[str, Any]:
    resumo: dict[str, Any] = {
        'data_referencia': _fmt_data(data_referencia),
        'status_fechamento': 'indisponível',
        'fonte_fechamento': 'indisponível',
        'usa_fallback_cdi': False,
        'qtd_fechamentos_fallback_cdi': 0,
        'data_ultimo_fator_explicito_cdi': None,
        'data_fechamento_confirmado': None,
        'observacao': '',
    }

    if serie_cdi:
        datas_disponiveis = sorted(dt for dt in serie_cdi.keys() if isinstance(dt, date))
        ultima_data_disponivel = max(datas_disponiveis) if datas_disponiveis else None
        resumo['data_ultimo_fator_explicito_cdi'] = _fmt_data(ultima_data_disponivel)
        if data_referencia in serie_cdi:
            resumo['status_fechamento'] = 'confirmado pela série CDI'
            resumo['fonte_fechamento'] = 'serie_cdi_bcb'
            resumo['data_fechamento_confirmado'] = _fmt_data(data_referencia)
            resumo['observacao'] = 'a própria data de referência possui fator explícito na série CDI.'
            return resumo

        qtd_fallback = 0
        if ultima_data_disponivel is not None:
            atual = ultima_data_disponivel + timedelta(days=1)
            while atual <= data_referencia:
                if eh_dia_util_bancario(atual, calendario_financeiro):
                    qtd_fallback += 1
                atual += timedelta(days=1)
            resumo['data_fechamento_confirmado'] = _fmt_data(ultima_data_disponivel)

        if qtd_fallback > 0:
            resumo['status_fechamento'] = 'estimado por fallback CDI'
            resumo['fonte_fechamento'] = 'fallback_encadeado_ultimo_fator_cdi'
            resumo['usa_fallback_cdi'] = True
            resumo['qtd_fechamentos_fallback_cdi'] = int(qtd_fallback)
            resumo['observacao'] = 'a situação atual usa o último fator explícito do CDI para fechar dias úteis consecutivos sem fator novo.'
            return resumo

        resumo['status_fechamento'] = 'confirmado até o último dia útil explícito'
        resumo['fonte_fechamento'] = 'serie_cdi_bcb_sem_novo_fechamento_util'
        resumo['observacao'] = 'não houve novo fechamento útil após o último fator explícito disponível na série CDI.'
        return resumo

    if eh_dia_util_bancario(data_referencia, calendario_financeiro):
        resumo['status_fechamento'] = 'estimado por taxa modelo'
        resumo['fonte_fechamento'] = 'taxa_modelo'
        resumo['observacao'] = 'a situação atual foi estimada pela taxa-base do modelo por ausência de série CDI carregada.'
    else:
        resumo['status_fechamento'] = 'sem fechamento útil novo na referência'
        resumo['fonte_fechamento'] = 'nao_eh_dia_util_bancario'
        resumo['observacao'] = 'a data de referência não exige fechamento útil novo para rendimento.'
    resumo['data_fechamento_confirmado'] = _fmt_data(data_referencia)
    return resumo
