"""Ledger temporal conjunto mínimo para Extrato Futuro.

Esta camada consolida eventos canônicos (pagamento + switching) sem recalcular
resgates, impostos ou saldos em camada de saída.
"""
from __future__ import annotations

from typing import Any

import pandas as pd


def _txt(v: Any) -> str:
    return str(v or '').strip()


def _norm(v: Any) -> str:
    return _txt(v).lower()


def _round(v: Any) -> Any:
    try:
        return round(float(v), 2)
    except Exception:
        return ''


def _bool_to_sim_nao(v: Any) -> str:
    if isinstance(v, bool):
        return 'sim' if v else 'não'
    return ''


def _inferir_pacote(row: dict[str, Any]) -> str:
    pacote = _txt(row.get('pacote_dia_escolhido'))
    if pacote:
        return pacote
    estrategia = _txt(row.get('estrategia_recomendada'))
    if estrategia in {'sem_switching', 'combinacao_minima'}:
        return 'pay_only'
    if estrategia == 'switching_simples':
        ant = bool(row.get('switching_antes_pagamento'))
        dep = bool(row.get('switching_depois_pagamento'))
        if ant and not dep:
            return 'switch_then_pay'
        if dep and not ant:
            return 'pay_then_switch'
    return 'não determinado'


def construir_ledger_temporal_conjunto(quadro_futuro: pd.DataFrame | None, mapa_central: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if not isinstance(quadro_futuro, pd.DataFrame) or quadro_futuro.empty:
        return []
    mapa_central = mapa_central or {}
    eventos: list[dict[str, Any]] = []
    for _, row in quadro_futuro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable').iterrows():
        d = row.to_dict()
        pid = _txt(d.get('pagamento_id'))
        central = mapa_central.get(pid, {})

        fonte_origem = _txt(d.get('lote_recomendado_consumivel') or d.get('lote_recomendado') or d.get('lote_id_escolhido') or d.get('fonte_origem_id') or central.get('lote_final_central'))
        fonte_destino = _txt(d.get('lote_nome_operacional') or d.get('fonte_pos_sw') or d.get('lote_id_sintetico'))

        bruto = _round(d.get('bruto_recomendado') if d.get('bruto_recomendado') is not None else central.get('bruto_central'))
        imposto = _round(d.get('imposto_recomendado') if d.get('imposto_recomendado') is not None else central.get('imposto_central'))
        liquido = _round(d.get('liquido_recomendado') if d.get('liquido_recomendado') is not None else central.get('liquido_central'))
        saldo_antes = _round(d.get('saldo_temporal_antes_recomendacao') if d.get('saldo_temporal_antes_recomendacao') is not None else central.get('saldo_antes_central'))
        saldo_depois = _round(d.get('saldo_residual_temporal_pos_recomendacao') if d.get('saldo_residual_temporal_pos_recomendacao') is not None else central.get('saldo_remanescente_central'))

        status = _txt(d.get('status_recomendacao') or central.get('status_recomendacao') or 'não determinado')
        motivo = _txt(d.get('motivo_bloqueio_lote') or central.get('motivo_bloqueio_lote'))

        switching_candidato = bool(_txt(d.get('produto_destino_switching')))
        switching_promovido = bool(d.get('switching_antes_pagamento') or d.get('switching_depois_pagamento'))
        switching_materializado = bool(fonte_destino)

        fonte_consumida = fonte_origem if fonte_origem else 'não determinado'
        fonte_exaurida = bool(saldo_depois != '' and saldo_depois <= 0.01)
        residual = '' if saldo_depois == '' else max(saldo_depois, 0.0)

        cobertura = d.get('cobertura_integral_recomendada')
        if isinstance(cobertura, bool):
            cobertura_txt = 'sim' if cobertura else 'não'
        else:
            valor_pag = _round(d.get('valor_pagamento'))
            cobertura_txt = 'sim' if (liquido != '' and valor_pag != '' and liquido + 0.01 >= valor_pag) else 'não'

        eventos.append({
            'data': d.get('data_pagamento'),
            'pagamento_id': pid,
            'pacote_do_dia': _inferir_pacote(d),
            'pagamento_associado': {'conta': d.get('descricao_pagamento') or '', 'valor': _round(d.get('valor_pagamento'))},
            'lote_fonte_origem': fonte_origem,
            'lote_fonte_destino': fonte_destino,
            'switching_candidato': switching_candidato,
            'switching_promovido': switching_promovido,
            'switching_materializado': switching_materializado,
            'fonte_consumida_em_pagamento': fonte_consumida,
            'fonte_exaurida': fonte_exaurida,
            'residual': residual,
            'saldo_antes': saldo_antes,
            'bruto': bruto,
            'imposto': imposto,
            'liquido': liquido,
            'consumo': liquido,
            'saldo_depois': saldo_depois,
            'cobertura_integral': cobertura_txt,
            'status': status,
            'motivo_bloqueio': motivo,
            'estado_final_por_data': {
                'saldo_temp_antes': saldo_antes,
                'consumo_temp': liquido,
                'saldo_temp_depois': saldo_depois,
            },
            'switching_antes_pagamento': _bool_to_sim_nao(d.get('switching_antes_pagamento')),
            'switching_depois_pagamento': _bool_to_sim_nao(d.get('switching_depois_pagamento')),
        })
    return eventos
