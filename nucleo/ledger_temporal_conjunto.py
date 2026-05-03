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



def _eh_nd(v: Any) -> bool:
    return _norm(v) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'none'}


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
    materializados: dict[tuple[str, str], dict[str, Any]] = {}

    quadro_ord = quadro_futuro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    for _, row in quadro_ord.iterrows():
        d = row.to_dict()
        lote_origem = _txt(d.get('lote_recomendado_consumivel') or d.get('lote_recomendado') or d.get('lote_id_escolhido') or d.get('fonte_origem_id'))
        lote_pos = _txt(d.get('lote_nome_operacional') or d.get('fonte_pos_sw') or d.get('lote_id_sintetico'))
        if lote_origem and lote_pos:
            k=(str(d.get('data_pagamento') or ''), lote_origem)
            materializados[k]={
                'evento_switching_id': f"sw::{str(d.get('data_pagamento') or '')}::{lote_origem}::{lote_pos}",
                'data_switching': d.get('data_switching_referencia') if d.get('data_switching_referencia') is not None else d.get('data_sugerida_switching'),
                'lote_origem': lote_origem,
                'lote_pos_switching': lote_pos,
                'produto_destino': _txt(d.get('produto_destino_switching')),
                'valor_liquido_materializado': _round(d.get('saldo_pos_sw') if d.get('saldo_pos_sw') is not None else d.get('liquido_recomendado')),
                'estado': 'materializado',
            }

    for _, row in quadro_ord.iterrows():
        d = row.to_dict(); pid=_txt(d.get('pagamento_id')); central=mapa_central.get(pid,{})
        pacote=_inferir_pacote(d)
        lote_origem=_txt(d.get('lote_recomendado_consumivel') or d.get('lote_recomendado') or d.get('lote_id_escolhido') or d.get('fonte_origem_id') or central.get('lote_final_central'))
        reserva=_txt(d.get('lote_reserva') or central.get('lote_reserva'))
        fonte_candidata_id = lote_origem if not _eh_nd(lote_origem) else (reserva if not _eh_nd(reserva) else '')
        tipo_fonte_candidata = 'lote' if not _eh_nd(fonte_candidata_id) else 'indeterminada'
        origem_fonte_candidata = 'motor_recomendacao' if not _eh_nd(lote_origem) else ('reserva' if not _eh_nd(reserva) else 'nao_rastreada')
        if not lote_origem or _norm(lote_origem) in {'não determinado','nao determinado','n/d'}:
            lote_origem='não determinado'
        ev_sw=materializados.get((str(d.get('data_pagamento') or ''), lote_origem))
        sw_mat=ev_sw is not None
        necessita_sw=_norm(d.get('necessita_switching') if d.get('necessita_switching') is not None else d.get('necessidade_switching')) in {'sim','true','1'}

        if lote_origem != 'não determinado' and not sw_mat and pacote=='switch_then_pay':
            pacote='pay_only'; necessita_sw=False

        if pacote=='switch_then_pay' and not sw_mat:
            status='switch_then_pay_sem_materializacao'; motivo=status; cobertura='não'; lote_op='não determinado'
            sal_ant=br=imp=liq=cons=sal_dep=''
            elegivel_temporalmente=False; saldo_liquido_disponivel=''; elegivel_liquidez_carencia=False
            promovida_para_lote_sugerido=False; etapa_descarte_fonte='injecao_pos_switching_no_fluxo'; motivo_descarte_fonte=status; origem_motivo_descarte='registrada_pipeline'
        else:
            status=_txt(d.get('status_recomendacao') or central.get('status_recomendacao') or 'não determinado')
            motivo=_txt(d.get('motivo_bloqueio_lote') or central.get('motivo_bloqueio_lote'))
            sal_ant=_round(d.get('saldo_temporal_antes_recomendacao') if d.get('saldo_temporal_antes_recomendacao') is not None else central.get('saldo_antes_central'))
            br=_round(d.get('bruto_recomendado') if d.get('bruto_recomendado') is not None else central.get('bruto_central'))
            imp=_round(d.get('imposto_recomendado') if d.get('imposto_recomendado') is not None else central.get('imposto_central'))
            liq=_round(d.get('liquido_recomendado') if d.get('liquido_recomendado') is not None else central.get('liquido_central'))
            cons=liq
            sal_dep=_round(d.get('saldo_residual_temporal_pos_recomendacao') if d.get('saldo_residual_temporal_pos_recomendacao') is not None else central.get('saldo_remanescente_central'))
            val=_round(d.get('valor_pagamento'))
            cobertura='sim' if (liq!='' and val!='' and liq+0.01>=val) else 'não'
            lote_op = ev_sw['lote_pos_switching'] if sw_mat and pacote=='switch_then_pay' else lote_origem
            promovida_reserva=False
            if _eh_nd(lote_op) and (not _eh_nd(reserva)) and liq != '' and val != '' and liq + 0.01 >= val:
                lote_op = reserva
                promovida_reserva=True
            elegivel_temporalmente = (not _eh_nd(fonte_candidata_id))
            saldo_liquido_disponivel = liq if liq != '' else ''
            elegivel_liquidez_carencia = bool(liq != '' and liq > 0)
            promovida_para_lote_sugerido = bool((not _eh_nd(lote_op)) and (_eh_nd(lote_origem) and not _eh_nd(reserva))) if 'promovida_reserva' in locals() else False
            etapa_descarte_fonte = ''
            motivo_descarte_fonte = ''
            origem_motivo_descarte = ''
            if lote_op=='não determinado':
                cobertura='não'
                if status in {'','ok','não determinado'}: status='sem_fonte_auditavel'
                if not motivo: motivo='sem_fonte_auditavel'
            if necessita_sw and not sw_mat:
                cobertura='não'
                if status in {'','ok','não determinado'}: status='fonte_pos_switching_nao_materializada'
                if not motivo: motivo='fonte_pos_switching_nao_materializada'
            if lote_op=='não determinado':
                etapa_descarte_fonte = 'selecao_fonte_operacional'
                motivo_descarte_fonte = motivo or status or 'sem_fonte_auditavel'
                origem_motivo_descarte = 'registrada_pipeline' if motivo else 'inferida'

        eventos.append({
            'pagamento_id': pid,'data': d.get('data_pagamento'),'conta': d.get('descricao_pagamento') or '',
            'pacote_do_dia': pacote,'necessita_switching': 'sim' if necessita_sw else 'não',
            'lote_fonte_origem': lote_origem,'lote_sugerido_operacional': lote_op,
            'switching_candidato': bool(_txt(d.get('produto_destino_switching'))),
            'switching_promovido': bool(d.get('switching_antes_pagamento') or d.get('switching_depois_pagamento')),
            'switching_materializado': sw_mat,
            'evento_switching_id': ev_sw.get('evento_switching_id') if ev_sw else '',
            'data_switching_operacional': ev_sw.get('data_switching') if ev_sw and pacote=='switch_then_pay' else None,
            'destino_switching_operacional': ev_sw.get('produto_destino') if ev_sw and pacote=='switch_then_pay' else '',
            'lote_pos_switching_materializado': ev_sw.get('lote_pos_switching') if ev_sw and pacote=='switch_then_pay' else '',
            'saldo_antes': sal_ant,'bruto': br,'imposto': imp,'liquido': liq,'consumo': cons,'saldo_depois': sal_dep,
            'cobertura_integral': cobertura,'status': status or 'não determinado','motivo_bloqueio': motivo or '',
            'fonte_candidata_id': fonte_candidata_id or 'n/d',
            'tipo_fonte_candidata': tipo_fonte_candidata,
            'origem_fonte_candidata': origem_fonte_candidata,
            'elegivel_temporalmente': bool(elegivel_temporalmente),
            'saldo_liquido_disponivel': saldo_liquido_disponivel,
            'elegivel_liquidez_carencia': bool(elegivel_liquidez_carencia),
            'promovida_para_lote_sugerido': bool((not _eh_nd(lote_op)) and (_eh_nd(lote_origem) and not _eh_nd(reserva))),
            'etapa_descarte_fonte': etapa_descarte_fonte or '',
            'motivo_descarte_fonte': motivo_descarte_fonte or '',
            'origem_motivo_descarte': origem_motivo_descarte or '',
        })
    return eventos
