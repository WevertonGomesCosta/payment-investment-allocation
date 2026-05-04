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




def avaliar_candidatos_fifo_pagamento(pid: str, d: dict[str, Any], estado_lotes: dict[str, dict[str, Any]], data_pag: Any, valor_pag: float, pacote: str, lote_sugerido: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidatos=[]
    qtd_estado=len(estado_lotes)
    qtd_av=qtd_suf=b_saldo=b_data=b_car=b_mig=0
    melhor_lote=''
    melhor_saldo=''
    melhor_data=''
    melhor_car=''
    motivo='n/d'
    if pacote != 'pay_only':
        motivo='fifo_nao_aplicavel_pacote_nao_pay_only'
        return candidatos, {'qtd_estado':qtd_estado,'qtd_av':0,'qtd_suf':0,'b_saldo':0,'b_data':0,'b_car':0,'b_mig':0,'melhor_lote':'','melhor_saldo':'','melhor_data':'','melhor_car':'','motivo':motivo}
    if valor_pag <= 0:
        motivo='fifo_nao_aplicavel_sem_valor_pagamento'
        return candidatos, {'qtd_estado':qtd_estado,'qtd_av':0,'qtd_suf':0,'b_saldo':0,'b_data':0,'b_car':0,'b_mig':0,'melhor_lote':'','melhor_saldo':'','melhor_data':'','melhor_car':'','motivo':motivo}
    if qtd_estado == 0:
        motivo='fifo_nao_aplicavel_sem_estado_lotes'
        return candidatos, {'qtd_estado':0,'qtd_av':0,'qtd_suf':0,'b_saldo':0,'b_data':0,'b_car':0,'b_mig':0,'melhor_lote':'','melhor_saldo':'','melhor_data':'','melhor_car':'','motivo':motivo}

    ordem=0
    for lid,meta in estado_lotes.items():
        ordem += 1
        qtd_av += 1
        saldo=float(meta.get('saldo_liquido') or 0.0)
        da=meta.get('data_aplicacao'); car=meta.get('carencia_ate'); mig=meta.get('migrado_em')
        if melhor_lote == '' or (da or '', -saldo, lid) < (melhor_data or '', -(float(melhor_saldo or 0) if melhor_saldo!='' else 0.0), melhor_lote):
            melhor_lote=lid; melhor_saldo=round(saldo,2); melhor_data=da; melhor_car=car
        bs = saldo + 0.01 < valor_pag
        bd = (not bs) and (da is not None and data_pag is not None and da > data_pag)
        bc = (not bs and not bd) and (car is not None and data_pag is not None and car > data_pag)
        motivo_mig = _motivo_bloqueio_migracao(data_pag, mig, pacote)
        bm = (not bs and not bd and not bc) and bool(motivo_mig)
        eleg = not (bs or bd or bc or bm)
        if bs: b_saldo += 1
        if bd: b_data += 1
        if bc: b_car += 1
        if bm: b_mig += 1
        if not bs: qtd_suf += 1
        candidatos.append({'Data': d.get('data_pagamento'),'Conta': d.get('descricao_pagamento') or '','Despesa ID': pid,'Valor': valor_pag,'lote_id': lid,'data_aplicacao': da,'carencia_ate': car,'migrado_em': mig,'saldo_liquido': round(saldo,2),'avaliado_fifo': True,'bloqueado_por_saldo': bs,'bloqueado_por_data': bd,'bloqueado_por_carencia': bc,'bloqueado_por_migracao': bm,'elegivel_fifo': eleg,'ordem_fifo': ordem,'motivo_bloqueio_fifo': 'saldo' if bs else ('data' if bd else ('carencia' if bc else ('migracao' if bm else '')) ),'motivo_bloqueio_migracao_detalhe': motivo_mig if bm else ''})
    if lote_sugerido and _norm(lote_sugerido) not in {'','n/d','nd','não determinado','nao determinado'}:
        motivo='fifo_nao_aplicavel_lote_ja_determinado'
    elif b_saldo == qtd_av:
        motivo='todos_bloqueados_por_saldo'
    elif b_data == qtd_suf and qtd_suf>0:
        motivo='todos_bloqueados_por_data'
    elif b_car == qtd_suf and qtd_suf>0:
        motivo='todos_bloqueados_por_carencia'
    elif b_mig == qtd_suf and qtd_suf>0:
        motivo='todos_bloqueados_por_migracao'
    else:
        motivo='sem_promocao_fifo'
    return candidatos, {'qtd_estado':qtd_estado,'qtd_av':qtd_av,'qtd_suf':qtd_suf,'b_saldo':b_saldo,'b_data':b_data,'b_car':b_car,'b_mig':b_mig,'melhor_lote':melhor_lote,'melhor_saldo':melhor_saldo,'melhor_data':melhor_data,'melhor_car':melhor_car,'motivo':motivo}



def _motivo_bloqueio_migracao(data_pag: Any, migrado_em: Any, pacote: str) -> str:
    if migrado_em is None or data_pag is None:
        return ''
    if migrado_em < data_pag:
        return 'bloqueado_por_migracao_antes_do_pagamento'
    if migrado_em == data_pag:
        if pacote == 'switch_then_pay':
            return 'bloqueado_por_migracao_intradia_switch_then_pay'
        return 'bloqueado_por_migracao_intradia_precedencia_ambigua'
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


def construir_ledger_temporal_conjunto(quadro_futuro: pd.DataFrame | None, mapa_central: dict[str, dict[str, Any]] | None = None, contexto: Any | None = None) -> dict[str, Any]:
    if not isinstance(quadro_futuro, pd.DataFrame) or quadro_futuro.empty:
        return {"eventos": [], "fifo_candidatos_avaliados": []}
    mapa_central = mapa_central or {}
    eventos: list[dict[str, Any]] = []
    fifo_candidatos_avaliados: list[dict[str, Any]] = []
    materializados: dict[tuple[str, str], dict[str, Any]] = {}

    quadro_ord = quadro_futuro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    # estado temporal simplificado de lotes para pay_only_fifo_v1
    estado_lotes: dict[str, dict[str, Any]] = {}
    lotes_replay = list(getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or []) if contexto is not None else []
    for l in lotes_replay:
        try:
            saldo_liq = float(l.valor_liquido_hoje(contexto.execucao.data_referencia, tabela_iof=contexto.tabela_iof, faixas_ir=contexto.faixas_ir) or 0.0)
        except Exception:
            saldo_liq = float(getattr(l, 'saldo_bruto', 0.0) or 0.0)
        estado_lotes[str(getattr(l, 'id', ''))] = {
            'data_aplicacao': getattr(l, 'data_aplicacao', None),
            'carencia_ate': getattr(l, 'carencia_ate', None),
            'saldo_liquido': round(saldo_liq, 2),
            'migrado_em': None,
        }

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

    for ev in materializados.values():
        lo = str(ev.get('lote_origem') or '')
        if lo in estado_lotes:
            estado_lotes[lo]['migrado_em'] = ev.get('data_switching')

    for _, row in quadro_ord.iterrows():
        d = row.to_dict(); pid=_txt(d.get('pagamento_id')); central=mapa_central.get(pid,{})
        pacote=_inferir_pacote(d)
        lote_origem_pipeline=_txt(d.get('lote_recomendado_consumivel') or d.get('lote_recomendado') or d.get('lote_id_escolhido') or d.get('fonte_origem_id'))
        lote_origem=_txt(lote_origem_pipeline or central.get('lote_final_central'))
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
            if pacote == 'pay_only' and status in {'sem_fonte_auditavel', 'sem_saldo_temporal_auditavel'}:
                lote_origem = 'não determinado'
                lote_op = 'não determinado'
                fonte_candidata_id = reserva if not _eh_nd(reserva) else ''
                tipo_fonte_candidata = 'lote' if fonte_candidata_id else 'indeterminada'
                origem_fonte_candidata = 'reserva' if fonte_candidata_id else 'nao_rastreada'
            promovida_reserva=False
            qtd_avaliados = qtd_saldo_suf = bloq_saldo = bloq_data = bloq_car = bloq_mig = 0
            melhor_lote = ''
            melhor_saldo = ''
            melhor_data = ''
            melhor_car = ''
            motivo_fifo = ''
            if _eh_nd(lote_op) and (not _eh_nd(reserva)) and liq != '' and val != '' and liq + 0.01 >= val and status not in {'sem_fonte_auditavel', 'sem_saldo_temporal_auditavel'}:
                lote_op = reserva
                promovida_reserva=True
            elegivel_temporalmente = (not _eh_nd(fonte_candidata_id))
            saldo_liquido_disponivel = liq if liq != '' else ''
            elegivel_liquidez_carencia = bool(liq != '' and liq > 0)
            promovida_para_lote_sugerido = bool((not _eh_nd(lote_op)) and (_eh_nd(lote_origem) and not _eh_nd(reserva))) if 'promovida_reserva' in locals() else False
            etapa_descarte_fonte = ''
            motivo_descarte_fonte = ''
            origem_motivo_descarte = ''
            if not _eh_nd(lote_op) and lote_op in estado_lotes:
                motivo_migracao_lote = _motivo_bloqueio_migracao(d.get('data_pagamento'), estado_lotes.get(lote_op, {}).get('migrado_em'), pacote)
                if motivo_migracao_lote:
                    lote_op = 'não determinado'
                    cobertura = 'não'
                    status = 'sem_fonte_auditavel'
                    motivo = motivo_migracao_lote
                    etapa_descarte_fonte = 'selecao_fonte_operacional'
                    motivo_descarte_fonte = motivo_migracao_lote
                    origem_motivo_descarte = 'registrada_pipeline'
            if lote_op=='não determinado':
                cobertura='não'
                if status in {'','ok','não determinado'}: status='sem_fonte_auditavel'
                if not motivo: motivo='sem_fonte_auditavel'
            if necessita_sw and not sw_mat:
                cobertura='não'
                if status in {'','ok','não determinado'}: status='fonte_pos_switching_nao_materializada'
                if not motivo: motivo='fonte_pos_switching_nao_materializada'
            if lote_op=='não determinado' and pacote == 'pay_only':
                # pay_only_fifo_v1: escolhe lote elegível mais antigo que cobre integralmente
                data_pag = d.get('data_pagamento')
                valor_pag = val if val != '' else 0.0
                elegiveis = []
                qtd_avaliados = 0
                qtd_saldo_suf = 0
                bloq_saldo = bloq_data = bloq_car = bloq_mig = 0
                melhor_lote = ''
                melhor_saldo = ''
                melhor_data = ''
                melhor_car = ''
                for lid, meta in estado_lotes.items():
                    qtd_avaliados += 1
                    saldo = float(meta.get('saldo_liquido') or 0.0)
                    da = meta.get('data_aplicacao')
                    car = meta.get('carencia_ate')
                    mig = meta.get('migrado_em')
                    if melhor_lote == '' or (da, -saldo, lid) < (melhor_data or '', -(float(melhor_saldo or 0) if melhor_saldo!='' else 0.0), str(melhor_lote)):
                        melhor_lote = lid; melhor_saldo = round(saldo,2); melhor_data = da; melhor_car = car
                    if saldo + 0.01 < float(valor_pag or 0.0):
                        bloq_saldo += 1
                        continue
                    qtd_saldo_suf += 1
                    if da is not None and data_pag is not None and da > data_pag:
                        bloq_data += 1
                        continue
                    if car is not None and data_pag is not None and car > data_pag:
                        bloq_car += 1
                        continue
                    if mig is not None and data_pag is not None and mig <= data_pag:
                        bloq_mig += 1
                        continue
                    elegiveis.append((da, -saldo, lid, saldo))
                elegiveis.sort(key=lambda x: (x[0] or '', x[1], x[2]))
                if elegiveis:
                    _, _, lid, saldo = elegiveis[0]
                    lote_op = lid
                    fonte_candidata_id = lid
                    origem_fonte_candidata = 'pay_only_fifo_v1'
                    tipo_fonte_candidata = 'lote_aportado'
                    saldo_liquido_disponivel = round(saldo, 2)
                    promovida_para_lote_sugerido = True
                    cobertura = 'sim'
                    status = 'ok'
                    motivo = 'n/d'
                    liq = round(float(valor_pag), 2)
                    cons = liq
                    sal_ant = round(float(saldo), 2)
                    sal_dep = round(float(saldo - liq), 2)
                    estado_lotes[lid]['saldo_liquido'] = sal_dep
                    etapa_descarte_fonte = ''
                    motivo_fifo = 'promovido_pay_only_fifo_v1'
                    motivo_descarte_fonte = ''
                    origem_motivo_descarte = ''
                else:
                    status = 'lote_individual_insuficiente' if estado_lotes else 'sem_fonte_auditavel'
                    if len(estado_lotes)==0:
                        motivo_fifo='sem_lotes_no_estado'
                    elif qtd_avaliados>0 and bloq_saldo==qtd_avaliados:
                        motivo_fifo='todos_bloqueados_por_saldo'
                    elif qtd_saldo_suf>0 and bloq_data>=qtd_saldo_suf:
                        motivo_fifo='todos_bloqueados_por_data'
                    elif qtd_saldo_suf>0 and bloq_car>=qtd_saldo_suf:
                        motivo_fifo='todos_bloqueados_por_carencia'
                    elif qtd_saldo_suf>0 and bloq_mig>=qtd_saldo_suf:
                        motivo_fifo='todos_bloqueados_por_migracao'
                    else:
                        motivo_fifo='outro'
                    cobertura = 'não'
                    etapa_descarte_fonte = 'selecao_fonte_operacional'
                    motivo_descarte_fonte = status
                    origem_motivo_descarte = 'registrada_pipeline'
            if lote_op=='não determinado':
                etapa_descarte_fonte = etapa_descarte_fonte or 'selecao_fonte_operacional'
                motivo_descarte_fonte = motivo_descarte_fonte or motivo or status or 'sem_fonte_auditavel'
                origem_motivo_descarte = origem_motivo_descarte or ('registrada_pipeline' if motivo else 'inferida')

        valor_pag_fifo = float(val or 0.0) if 'val' in locals() and val != '' else float(_round(d.get('valor_pagamento')) or 0.0)
        lote_sugerido_original = _txt(d.get('lote_recomendado_consumivel') or d.get('lote_recomendado') or d.get('lote_id_escolhido') or d.get('fonte_origem_id') or central.get('lote_final_central'))
        lote_ja_determinado = (not _eh_nd(lote_sugerido_original)) and (not _eh_nd(lote_op))
        cand_rows, cand_sum = avaliar_candidatos_fifo_pagamento(
            pid, d, estado_lotes, d.get('data_pagamento'), valor_pag_fifo, pacote,
            lote_op if not lote_ja_determinado else lote_sugerido_original,
        )
        fifo_candidatos_avaliados.extend(cand_rows)

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
            'fifo_pagamento_id': pid,
            'fifo_data_pagamento': d.get('data_pagamento'),
            'fifo_valor_pagamento': val if 'val' in locals() else '',
            'fifo_qtd_lotes_estado': len(estado_lotes),
            'fifo_qtd_lotes_avaliados': cand_sum.get('qtd_av', 0),
            'fifo_qtd_lotes_saldo_suficiente': cand_sum.get('qtd_suf', 0),
            'fifo_qtd_lotes_bloqueados_por_saldo': cand_sum.get('b_saldo', 0),
            'fifo_qtd_lotes_bloqueados_por_data': cand_sum.get('b_data', 0),
            'fifo_qtd_lotes_bloqueados_por_carencia': cand_sum.get('b_car', 0),
            'fifo_qtd_lotes_bloqueados_por_migracao': cand_sum.get('b_mig', 0),
            'fifo_melhor_lote_candidato': cand_sum.get('melhor_lote', ''),
            'fifo_saldo_melhor_lote': cand_sum.get('melhor_saldo', ''),
            'fifo_data_aplicacao_melhor_lote': cand_sum.get('melhor_data', ''),
            'fifo_carencia_melhor_lote': cand_sum.get('melhor_car', ''),
            'fifo_motivo_nao_promocao': cand_sum.get('motivo', ''),
        })
    return {"eventos": eventos, "fifo_candidatos_avaliados": fifo_candidatos_avaliados}
