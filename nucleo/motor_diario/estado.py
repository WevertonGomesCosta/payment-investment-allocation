from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from nucleo.simulador_central_eventos_v1 import _coerce_date, construir_estado_global_recorte_curto_v117


def _ordenar_pagamentos(pagamentos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [deepcopy(dict(x)) for x in pagamentos],
        key=lambda item: (
            _coerce_date(item.get('data')) or date.max,
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )


def _remover_pagamentos_ate_dia(estado: dict[str, Any], dia: date) -> None:
    estado['pagamentos_futuros'] = [
        deepcopy(dict(item))
        for item in (estado.get('pagamentos_futuros') or [])
        if (_coerce_date(item.get('data')) or date.max) > dia
    ]


def _carregar_estado_janela(
    *,
    contexto: Any,
    data_inicio: date,
    data_fim: date,
    limite_pagamentos: int = 200,
) -> dict[str, Any]:
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    pagamentos = [
        deepcopy(dict(x))
        for x in (estado.get('pagamentos_futuros') or [])
        if data_inicio <= (_coerce_date(x.get('data')) or date.max) <= data_fim
    ]
    recebidos_futuros = [
        deepcopy(dict(x))
        for x in (estado.get('recebidos_nao_aportados_futuros') or [])
        if data_inicio <= (_coerce_date(x.get('data_recebimento')) or date.max) <= data_fim
    ]
    estado['pagamentos_futuros'] = _ordenar_pagamentos(pagamentos)
    estado['recebidos_nao_aportados_futuros'] = recebidos_futuros
    estado['data_referencia'] = data_inicio
    estado['data_evento_corrente'] = data_inicio
    estado['data_fim_recorte'] = data_fim
    return estado
