from __future__ import annotations

from datetime import date, timedelta
from typing import Mapping

from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro, obter_taxa_dia_rendimento_lote
from nucleo.nucleo_financeiro_minimo import Lote, criar_lote_de_aporte


def iterar_datas_intervalo_exclusivo(inicio: date, fim: date):
    """Itera do dia seguinte a ``inicio`` até ``fim`` inclusive."""
    atual = inicio + timedelta(days=1)
    while atual <= fim:
        yield atual
        atual += timedelta(days=1)


def simular_lote_ate_data_shadow(
    lote: Lote,
    data_inicio: date,
    data_fim: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    *,
    taxa_proj: float,
    serie_cdi: Mapping[date, float] | None = None,
) -> Lote:
    """Projeta um clone do lote até ``data_fim`` para benchmarks shadow.

    Helper compartilhado entre as camadas shadow, sem acoplar decisão ao fluxo
    principal. O comportamento é mantido compatível com as implementações locais
    previamente duplicadas.
    """
    clone = criar_lote_de_aporte(
        data_inicio,
        float(lote.saldo_bruto),
        lote.id,
        {
            'investimento': lote.investimento,
            'produto_key': lote.produto_key,
            'data_base_fiscal': lote.data_base_fiscal,
            'data_recebimento': lote.data_recebimento,
            'fator_acumulado_inicial': lote.fator_acumulado,
            'taxa_base_cdi': lote.taxa_base_cdi,
            'taxa_bonus_cdi': lote.taxa_bonus_cdi,
            'dias_bonus': lote.dias_bonus,
            'principal_remanescente': lote.principal_remanescente,
            'produto_isento_ir': lote.produto_isento_ir,
            'carencia_ate': lote.carencia_ate,
            'nao_disponivel_para_aporte': lote.nao_disponivel_para_aporte,
            'situacao_investimento': lote.situacao_investimento,
        },
    )
    if data_fim <= data_inicio:
        return clone
    for data_cur in iterar_datas_intervalo_exclusivo(data_inicio, data_fim):
        aplicar, taxa_dia, _ = obter_taxa_dia_rendimento_lote(
            data_cur,
            clone.data_aplicacao,
            calendario_financeiro,
            data_recebimento=clone.data_recebimento,
            serie_cdi=serie_cdi,
            taxa_proj=taxa_proj,
            data_fechamento_referencia=data_cur,
        )
        if aplicar and taxa_dia is not None:
            kwargs = {'data_fechamento_referencia': data_cur}
            if serie_cdi is not None:
                kwargs['serie_cdi'] = serie_cdi
            clone.atualizar_juros(data_cur, taxa_dia, calendario_financeiro, **kwargs)
    return clone
