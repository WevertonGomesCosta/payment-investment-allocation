"""Ledger temporal conjunto mínimo para Extrato Futuro.

Esta camada consolida eventos canônicos (pagamento + switching) sem recalcular
resgates, impostos ou saldos em camada de saída.
"""
from __future__ import annotations

from typing import Any
from datetime import timedelta

import pandas as pd
from nucleo.calendario_financeiro import proximo_dia_util_bancario_em_ou_apos


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




def _mapa_global_switchings_contexto(contexto: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    shadow = getattr(contexto, 'switching_economico_shadow', None) if contexto is not None else None
    plano = getattr(shadow, 'plano_shadow', None) if shadow is not None else None
    if isinstance(plano, pd.DataFrame) and not plano.empty:
        plano_f = plano.copy()
        if 'recomendado_shadow' in plano_f.columns:
            plano_f = plano_f[plano_f['recomendado_shadow'].fillna(False)]
        for _, row in plano_f.iterrows():
            lote = _txt(row.get('lote_id'))
            if not lote:
                continue
            lote_obj = None
            for l in (getattr(getattr(contexto, 'replay_passado', None), 'lotes_apos_replay', []) or []):
                if str(getattr(l, 'id', '')) == lote:
                    lote_obj = l
                    break
            data_sw = None
            if lote_obj is not None:
                carteira = getattr(contexto, 'carteira_canonica', None)
                mapa = getattr(carteira, 'mapa_produtos', {}) if carteira is not None else {}
                meta_prod = ((mapa.get('by_key') or {}).get(getattr(lote_obj, 'produto_key', None)) or {}) if isinstance(mapa, dict) else {}
                prazo = int(meta_prod.get('prazo_dias') or 0)
                datas_candidatas = []
                if prazo > 0:
                    datas_candidatas.append(getattr(lote_obj, 'data_aplicacao', None) + timedelta(days=prazo))
                carencia = getattr(lote_obj, 'carencia_ate', None)
                if carencia is not None:
                    datas_candidatas.append(carencia)
                base = max([d for d in datas_candidatas if d is not None], default=getattr(contexto.execucao, 'data_referencia', None))
                if base is not None:
                    try:
                        data_sw = proximo_dia_util_bancario_em_ou_apos(base, contexto.calendario_financeiro)
                    except Exception:
                        data_sw = base
            if data_sw is None:
                data_sw = row.get('data_horizonte') or row.get('data_referencia')
            mapa[lote] = {
                'lote_origem': lote,
                'data_switching': data_sw,
                'produto_destino': _txt(row.get('produto_destino_nome') or row.get('produto_destino_key')),
                'valor_liquido_origem': _round(row.get('valor_liquido_resgatavel')),
                'status_switching': 'classificado_promovido',
                'origem_mapa_migracao': 'contexto.switching_economico_shadow.plano_shadow::data_operacional',
                'lote_pos_switching': '',
            }
    return mapa



def _normalizar_evento_operacional(ev: dict[str, Any]) -> dict[str, Any]:
    lote = _norm(ev.get('lote_sugerido_operacional'))
    status = _norm(ev.get('status'))
    motivo = _norm(ev.get('motivo_bloqueio'))
    cob = _norm(ev.get('cobertura_integral'))
    bloqueios = {'sem_saldo_temporal_auditavel','sem_fonte_auditavel','switch_then_pay_sem_materializacao','fonte_pos_switching_nao_materializada'}
    sem_lote = lote in {'','n/d','nd','não determinado','nao determinado'}
    if sem_lote:
        ev['lote_sugerido_operacional'] = 'não determinado'
        ev['cobertura_integral'] = 'não'
        ev['status'] = 'sem_fonte_auditavel'
        if motivo in {'','n/d','nd','não determinado','nao determinado'}:
            ev['motivo_bloqueio'] = 'sem_fonte_auditavel'
        for k in ['saldo_antes','bruto','imposto','liquido','consumo','saldo_depois']:
            ev[k] = ''
    if _norm(ev.get('cobertura_integral')) == 'sim':
        ev['status'] = 'ok'
        if _norm(ev.get('motivo_bloqueio')) not in {'','n/d','nd','não determinado','nao determinado'}:
            ev['motivo_bloqueio'] = 'n/d'
    if _norm(ev.get('motivo_bloqueio')) not in {'','n/d','nd','não determinado','nao determinado'} and _norm(ev.get('status')) == 'ok':
        ev['status'] = 'sem_saldo_temporal_auditavel'
        ev['cobertura_integral'] = 'não'
    if _norm(ev.get('status')) in bloqueios:
        ev['cobertura_integral'] = 'não'
        for k in ['saldo_antes','bruto','imposto','liquido','consumo','saldo_depois']:
            ev[k] = ''
    return ev

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

    mapa_global_sw = _mapa_global_switchings_contexto(contexto)
    for lo, meta_sw in mapa_global_sw.items():
        if lo in estado_lotes:
            estado_lotes[lo]['migrado_em'] = meta_sw.get('data_switching')
            estado_lotes[lo]['destino_switching'] = meta_sw.get('produto_destino')
            estado_lotes[lo]['lote_pos_switching'] = meta_sw.get('lote_pos_switching')
            estado_lotes[lo]['status_switching'] = meta_sw.get('status_switching')
            estado_lotes[lo]['origem_mapa_migracao'] = meta_sw.get('origem_mapa_migracao')

    for ev in materializados.values():
        lo = str(ev.get('lote_origem') or '')
        if lo in estado_lotes:
            estado_lotes[lo]['migrado_em'] = ev.get('data_switching')
            estado_lotes[lo]['destino_switching'] = ev.get('produto_destino')
            estado_lotes[lo]['lote_pos_switching'] = ev.get('lote_pos_switching')
            estado_lotes[lo]['status_switching'] = ev.get('estado')
            estado_lotes[lo]['origem_mapa_migracao'] = 'materializacao_no_quadro_futuro'

    # shadow diagnóstico pay_only_diario_v1 (sem impacto funcional)
    shadow_por_data: list[dict[str, Any]] = []
    shadow_counters = {
        'pay_only_diario_shadow_datas_total': 0,
        'pay_only_diario_shadow_datas_com_pagamento': 0,
        'pay_only_diario_shadow_datas_resolvidas_fonte_unica': 0,
        'pay_only_diario_shadow_datas_resolvidas_combinacao_minima': 0,
        'pay_only_diario_shadow_datas_nao_resolvidas': 0,
        'pay_only_diario_shadow_pagamentos_potencialmente_resolvidos': 0,
        'pay_only_diario_shadow_pagamentos_atualmente_nao_determinados_resolvidos_shadow': 0,
        'pay_only_diario_shadow_violacoes_residual_global': 0,
        'pay_only_diario_shadow_conflitos_migracao': 0,
        'pay_only_diario_shadow_consumo_pos_switching_indevido': 0,
    }
    estado_shadow = {k: dict(v) for k, v in estado_lotes.items()}
    dias = {}
    for _, row in quadro_ord.iterrows():
        dtmp = row.to_dict()
        if _inferir_pacote(dtmp) != 'pay_only':
            continue
        dt = str(dtmp.get('data_pagamento') or '')
        dias.setdefault(dt, []).append(dtmp)
    shadow_counters['pay_only_diario_shadow_datas_total'] = len(dias)
    shadow_counters['pay_only_diario_shadow_datas_com_pagamento'] = len(dias)
    for dt in sorted(dias.keys()):
        itens = dias[dt]
        valor_total = round(sum(float(_round(x.get('valor_pagamento')) or 0.0) for x in itens), 2)
        elegiveis = []
        b_saldo = b_car = b_data = b_mig = b_fut = 0
        for lid, meta in estado_shadow.items():
            saldo = float(meta.get('saldo_liquido') or 0.0)
            da = meta.get('data_aplicacao'); car = meta.get('carencia_ate'); mig = meta.get('migrado_em')
            if saldo <= 0.01:
                b_saldo += 1; continue
            if da is not None and str(da) > dt:
                b_data += 1; continue
            if car is not None and str(car) > dt:
                b_car += 1; continue
            if mig is not None and str(mig) <= dt:
                b_mig += 1; continue
            elegiveis.append((lid, saldo))
        elegiveis = sorted(elegiveis, key=lambda x: (-x[1], x[0]))
        escolhidas = []
        total_coberto = 0.0
        status_shadow = 'nao_resolvido'
        motivo_shadow = 'sem_fontes_elegiveis'
        if elegiveis:
            unica = next((x for x in elegiveis if x[1] + 0.01 >= valor_total), None)
            if unica:
                escolhidas = [unica]
                total_coberto = valor_total
                status_shadow = 'resolvido_fonte_unica'
                motivo_shadow = 'ok'
                shadow_counters['pay_only_diario_shadow_datas_resolvidas_fonte_unica'] += 1
            else:
                acum = 0.0
                for e in elegiveis:
                    escolhidas.append(e); acum += e[1]
                    if acum + 0.01 >= valor_total:
                        break
                if acum + 0.01 >= valor_total:
                    total_coberto = valor_total
                    restante = valor_total
                    resid_pos = 0
                    for _, s in escolhidas:
                        consumo = min(s, max(restante, 0.0))
                        residual = round(s - consumo, 2)
                        if residual > 0.01:
                            resid_pos += 1
                        restante = round(restante - consumo, 2)
                    if resid_pos > 1:
                        shadow_counters['pay_only_diario_shadow_violacoes_residual_global'] += 1
                    status_shadow = 'resolvido_combinacao_minima'
                    motivo_shadow = 'ok'
                    shadow_counters['pay_only_diario_shadow_datas_resolvidas_combinacao_minima'] += 1
                else:
                    total_coberto = round(acum, 2)
                    motivo_shadow = 'saldo_total_insuficiente'
        if status_shadow.startswith('resolvido'):
            shadow_counters['pay_only_diario_shadow_pagamentos_potencialmente_resolvidos'] += len(itens)
            for item in itens:
                lote_cur = _txt(item.get('lote_recomendado_consumivel') or item.get('lote_recomendado') or item.get('lote_id_escolhido') or item.get('fonte_origem_id'))
                if _eh_nd(lote_cur):
                    shadow_counters['pay_only_diario_shadow_pagamentos_atualmente_nao_determinados_resolvidos_shadow'] += 1
        else:
            shadow_counters['pay_only_diario_shadow_datas_nao_resolvidas'] += 1
        residual_por_fonte_shadow: dict[str, float] = {}
        restante_shadow = valor_total
        for lid, saldo in escolhidas:
            consumo_shadow = min(saldo, max(restante_shadow, 0.0))
            residual_por_fonte_shadow[lid] = round(saldo - consumo_shadow, 2)
            restante_shadow = round(restante_shadow - consumo_shadow, 2)
        num_residual_positivo = sum(1 for v in residual_por_fonte_shadow.values() if v > 0.01)
        shadow_por_data.append({
            'data': dt, 'quantidade_contas': len(itens), 'valor_total_dia': valor_total,
            'fontes_elegiveis': [x[0] for x in elegiveis], 'fontes_escolhidas_shadow': [x[0] for x in escolhidas],
            'total_coberto': total_coberto,
            'residual_por_fonte': residual_por_fonte_shadow,
            'numero_fontes_residual_positivo': num_residual_positivo,
            'status_shadow': status_shadow, 'motivo_shadow': motivo_shadow,
            'fontes_bloqueadas_por_saldo': b_saldo, 'fontes_bloqueadas_por_carencia': b_car,
            'fontes_bloqueadas_por_data': b_data, 'fontes_bloqueadas_por_migracao': b_mig,
            'fontes_futuras_ou_nao_materializadas': b_fut,
        })

    ativacao_fonte_unica_por_data: dict[str, str] = {}
    saldo_ativacao_por_data: dict[str, float] = {}
    for item_shadow in shadow_por_data:
        if str(item_shadow.get('status_shadow') or '') == 'resolvido_fonte_unica':
            data_key = str(item_shadow.get('data') or '')
            fontes = list(item_shadow.get('fontes_escolhidas_shadow') or [])
            if data_key and fontes:
                ativacao_fonte_unica_por_data[data_key] = str(fontes[0])
                meta_lote = estado_lotes.get(str(fontes[0]), {})
                saldo_ativacao_por_data[data_key] = float(meta_lote.get('saldo_liquido') or 0.0)

    d2a_funil = {
        'd2a_linhas_no_bloco_pay_only': 0,
        'd2a_com_data_no_mapa_fonte_unica': 0,
        'd2a_com_lote_op_nao_determinado': 0,
        'd2a_passa_filtro_status': 0,
        'd2a_rejeitadas_por_saldo': 0,
        'd2a_rejeitadas_por_data_carencia_migracao': 0,
        'd2a_promovidas_internamente_pay_only_diario_v1': 0,
        'd2a_promovidas_evento_final_pay_only_diario_v1': 0,
        'd2a_promovidas_extrato_futuro_auditoria_fontes': 0,
        'd2a_motivo_gap_shadow_vs_ativacao': 'rollback_d2a_parcial_sem_ganho_funcional',
    }
    d2a_plano_por_pagamento: list[dict[str, Any]] = []
    d2a_plano_por_data: list[dict[str, Any]] = []
    d2a_plano = {
        'd2a_plano_datas_fonte_unica_total': 0,
        'd2a_plano_datas_materializaveis': 0,
        'd2a_plano_datas_nao_materializaveis': 0,
        'd2a_plano_pagamentos_total': 0,
        'd2a_plano_pagamentos_validos_para_ativacao': 0,
        'd2a_plano_pagamentos_invalidos': 0,
        'd2a_plano_pagamentos_hoje_nao_determinados_validos': 0,
        'd2a_plano_conflitos_migracao': 0,
        'd2a_plano_consumo_pos_switching_indevido': 0,
        'd2a_plano_violacoes_residual_global': 0,
        'd2a_plano_divergencias_shadow_vs_plano': 0,
    }
    d2b0_plano_por_pagamento_fonte: list[dict[str, Any]] = []
    d2b0_plano_por_data: list[dict[str, Any]] = []
    d2b0 = {
        'd2b0_datas_combinacao_total': 0,
        'd2b0_datas_materializaveis': 0,
        'd2b0_datas_nao_materializaveis': 0,
        'd2b0_pagamentos_total': 0,
        'd2b0_pagamentos_validos_para_ativacao': 0,
        'd2b0_pagamentos_invalidos': 0,
        'd2b0_fontes_usadas_total': 0,
        'd2b0_fontes_com_residual_positivo_total': 0,
        'd2b0_violacoes_residual_global': 0,
        'd2b0_conflitos_migracao': 0,
        'd2b0_consumo_pos_switching_indevido': 0,
        'd2b0_divergencias_shadow_vs_plano': 0,
    }
    d2b1 = {
        'd2b1_datas_ativadas': 0,
        'd2b1_datas_bloqueadas': 0,
        'd2b1_pagamentos_ativados': 0,
        'd2b1_pagamentos_nao_determinados_ativados': 0,
        'd2b1_fontes_usadas_total': 0,
        'd2b1_fontes_com_residual_positivo_total': 0,
        'd2b1_violacoes_residual_global': 0,
        'd2b1_conflitos_migracao': 0,
        'd2b1_consumo_pos_switching_indevido': 0,
        'd2b1_divergencias_plano_vs_evento_final': 0,
        'd2b1_divergencias_evento_vs_extrato_futuro': 0,
        'd2b1_falhas_ativacao': 0,
    }
    d2a2 = {
        'd2a2_datas_ativadas': 0,
        'd2a2_datas_bloqueadas': 0,
        'd2a2_pagamentos_ativados': 0,
        'd2a2_pagamentos_nao_determinados_ativados': 0,
        'd2a2_pagamentos_fifo_substituidos': 0,
        'd2a2_falhas_ativacao': 0,
        'd2a2_violacoes_residual_global': 0,
        'd2a2_conflitos_migracao': 0,
        'd2a2_consumo_pos_switching_indevido': 0,
        'd2a2_divergencias_plano_vs_evento_final': 0,
        'd2a2_divergencias_evento_vs_extrato_futuro': 0,
    }

    linhas_por_data_pay_only: dict[str, list[dict[str, Any]]] = {}
    for _, row in quadro_ord.iterrows():
        dr = row.to_dict()
        if _inferir_pacote(dr) == 'pay_only':
            linhas_por_data_pay_only.setdefault(str(dr.get('data_pagamento') or ''), []).append(dr)

    datas_fonte_unica = [x for x in shadow_por_data if str(x.get('status_shadow') or '') == 'resolvido_fonte_unica']
    d2a_plano['d2a_plano_datas_fonte_unica_total'] = len(datas_fonte_unica)
    for info_data in datas_fonte_unica:
        dt = str(info_data.get('data') or '')
        fonte = str((info_data.get('fontes_escolhidas_shadow') or [''])[0] or '')
        linhas_dia = list(sorted(linhas_por_data_pay_only.get(dt, []), key=lambda z: str(z.get('pagamento_id') or '')))
        if not fonte or not linhas_dia:
            d2a_plano['d2a_plano_datas_nao_materializaveis'] += 1
            d2a_plano_por_data.append({'data': dt, 'status_plano_data': 'nao_materializavel', 'motivo_data': 'sem_fonte_ou_sem_linhas'})
            continue
        meta_fonte = estado_lotes.get(fonte, {})
        saldo_planejado = float(meta_fonte.get('saldo_liquido') or 0.0)
        data_apl = meta_fonte.get('data_aplicacao')
        car_ate = meta_fonte.get('carencia_ate')
        mig_em = meta_fonte.get('migrado_em')
        data_ok = not (data_apl is not None and str(data_apl) > dt)
        car_ok = not (car_ate is not None and str(car_ate) > dt)
        mig_motivo = _motivo_bloqueio_migracao(dt, mig_em, 'pay_only')
        mig_ok = not bool(mig_motivo)
        if not mig_ok:
            d2a_plano['d2a_plano_conflitos_migracao'] += 1

        validos_data = True
        saldo_cursor = saldo_planejado
        residuals = []
        for linha in linhas_dia:
            d2a_plano['d2a_plano_pagamentos_total'] += 1
            val_pag = float(_round(linha.get('valor_pagamento')) or 0.0)
            lote_atual = _txt(linha.get('lote_recomendado_consumivel') or linha.get('lote_recomendado') or linha.get('lote_id_escolhido') or linha.get('fonte_origem_id'))
            motivo_nao_ativavel = ''
            valido = True
            if not data_ok:
                valido = False; motivo_nao_ativavel = 'fonte_futura'
            elif not car_ok:
                valido = False; motivo_nao_ativavel = 'bloqueada_por_carencia'
            elif not mig_ok:
                valido = False; motivo_nao_ativavel = mig_motivo or 'bloqueada_por_migracao'
            elif saldo_cursor + 0.01 < val_pag:
                valido = False; motivo_nao_ativavel = 'saldo_insuficiente_no_plano'
            saldo_antes = round(saldo_cursor, 2)
            consumo = round(val_pag if valido else 0.0, 2)
            saldo_depois = round(saldo_cursor - consumo, 2)
            if valido:
                d2a_plano['d2a_plano_pagamentos_validos_para_ativacao'] += 1
                if _eh_nd(lote_atual):
                    d2a_plano['d2a_plano_pagamentos_hoje_nao_determinados_validos'] += 1
                saldo_cursor = saldo_depois
                residuals.append(saldo_depois)
            else:
                d2a_plano['d2a_plano_pagamentos_invalidos'] += 1
                validos_data = False
            d2a_plano_por_pagamento.append({
                'data': dt,
                'despesa_id': _txt(linha.get('pagamento_id')),
                'conta': _txt(linha.get('descricao_pagamento')),
                'valor_pagamento': round(val_pag, 2),
                'fonte_unica_escolhida': fonte,
                'saldo_antes_planejado': saldo_antes,
                'bruto_planejado': round(val_pag, 2) if valido else '',
                'imposto_planejado': 0.0 if valido else '',
                'liquido_planejado': round(val_pag, 2) if valido else '',
                'consumo_planejado': consumo,
                'saldo_depois_planejado': saldo_depois if valido else saldo_antes,
                'cobertura_integral_planejada': 'sim' if valido else 'não',
                'status_planejado': 'ok' if valido else 'nao_ativavel',
                'motivo_planejado': 'n/d' if valido else motivo_nao_ativavel,
                'origem_planejada': 'pay_only_diario_v1',
                'valido_para_ativacao': bool(valido),
                'motivo_nao_ativavel': motivo_nao_ativavel,
            })
        # D2A-1: plano desta etapa considera somente fonte única;
        # portanto não há violação da regra global de residual por múltiplas fontes.
        if validos_data:
            d2a_plano['d2a_plano_datas_materializaveis'] += 1
            status_plano = 'materializavel'
            motivo_data = 'ok'
        else:
            d2a_plano['d2a_plano_datas_nao_materializaveis'] += 1
            status_plano = 'nao_materializavel'
            motivo_data = 'pagamentos_invalidos_no_plano'
        d2a_plano_por_data.append({
            'data': dt, 'fonte_unica': fonte, 'qtd_pagamentos': len(linhas_dia),
            'status_plano_data': status_plano, 'motivo_data': motivo_data,
        })

    datas_combinacao = [x for x in shadow_por_data if str(x.get('status_shadow') or '') == 'resolvido_combinacao_minima']
    d2b0['d2b0_datas_combinacao_total'] = len(datas_combinacao)
    for info_data in datas_combinacao:
        dt = str(info_data.get('data') or '')
        fontes = [str(f) for f in list(info_data.get('fontes_escolhidas_shadow') or []) if str(f)]
        linhas_dia = list(sorted(linhas_por_data_pay_only.get(dt, []), key=lambda z: str(z.get('pagamento_id') or '')))
        if not fontes or not linhas_dia:
            d2b0['d2b0_datas_nao_materializaveis'] += 1
            d2b0_plano_por_data.append({'data': dt, 'status_plano_data': 'nao_materializavel', 'motivo_data': 'sem_fontes_ou_sem_linhas'})
            continue
        saldos = {f: float((estado_lotes.get(f, {}) or {}).get('saldo_liquido') or 0.0) for f in fontes}
        fontes_usadas_data = set()
        data_ok = True
        motivo_data = 'ok'
        for f in fontes:
            meta_f = estado_lotes.get(f, {})
            da = meta_f.get('data_aplicacao'); car = meta_f.get('carencia_ate'); mig = meta_f.get('migrado_em')
            if da is not None and str(da) > dt:
                data_ok = False; motivo_data = 'fonte_futura'
            if car is not None and str(car) > dt:
                data_ok = False; motivo_data = 'fonte_carencia'
            mig_motivo = ''
            if mig is not None and str(mig) <= str(dt):
                mig_motivo = 'fonte_migrada_antes_ou_no_dia_pagamento'
            if mig_motivo:
                data_ok = False; motivo_data = mig_motivo; d2b0['d2b0_conflitos_migracao'] += 1
        for linha in linhas_dia:
            d2b0['d2b0_pagamentos_total'] += 1
            pid = _txt(linha.get('pagamento_id'))
            conta = _txt(linha.get('descricao_pagamento'))
            restante = float(_round(linha.get('valor_pagamento')) or 0.0)
            pago_total = 0.0
            for idx, f in enumerate(fontes, start=1):
                if restante <= 0.0001:
                    break
                saldo_antes = float(saldos.get(f, 0.0))
                pago = round(min(saldo_antes, restante), 2) if data_ok else 0.0
                saldo_depois = round(saldo_antes - pago, 2)
                saldos[f] = saldo_depois
                restante = round(restante - pago, 2)
                pago_total = round(pago_total + pago, 2)
                if pago > 0:
                    fontes_usadas_data.add(f)
                d2b0_plano_por_pagamento_fonte.append({
                    'data': dt, 'despesa_id': pid, 'conta': conta, 'valor_pagamento': float(_round(linha.get('valor_pagamento')) or 0.0),
                    'fonte_usada': f, 'ordem_fonte': idx, 'valor_pago_pela_fonte': pago, 'saldo_antes_fonte': saldo_antes,
                    'bruto_planejado': pago, 'imposto_planejado': 0.0, 'liquido_planejado': pago, 'consumo_planejado': pago,
                    'saldo_depois_fonte': saldo_depois, 'residual_fonte': max(saldo_depois, 0.0), 'residual_positivo': bool(saldo_depois > 0.20),
                    'cobertura_integral_planejada': 'sim' if (restante <= 0.01 and data_ok) else 'não',
                    'status_planejado': 'ok' if (restante <= 0.01 and data_ok) else 'nao_ativavel',
                    'motivo_planejado': 'n/d' if (restante <= 0.01 and data_ok) else ('saldo_insuficiente_no_plano' if data_ok else motivo_data),
                    'origem_planejada': 'pay_only_diario_v1_combinacao_minima',
                    'valido_para_ativacao': bool(restante <= 0.01 and data_ok),
                    'motivo_nao_ativavel': '' if (restante <= 0.01 and data_ok) else ('saldo_insuficiente_no_plano' if data_ok else motivo_data),
                })
            if restante <= 0.01 and data_ok:
                d2b0['d2b0_pagamentos_validos_para_ativacao'] += 1
            else:
                d2b0['d2b0_pagamentos_invalidos'] += 1
                data_ok = False
                if motivo_data == 'ok':
                    motivo_data = 'pagamento_sem_cobertura_integral'
        resid_positivos = sum(1 for f in fontes_usadas_data if float(saldos.get(f, 0.0)) > 0.20)
        d2b0['d2b0_fontes_usadas_total'] += len(fontes_usadas_data)
        d2b0['d2b0_fontes_com_residual_positivo_total'] += resid_positivos
        if resid_positivos > 1:
            d2b0['d2b0_violacoes_residual_global'] += 1
            data_ok = False
            motivo_data = 'violacao_residual_global'
        if data_ok:
            d2b0['d2b0_datas_materializaveis'] += 1
            status_data = 'materializavel'
        else:
            d2b0['d2b0_datas_nao_materializaveis'] += 1
            status_data = 'nao_materializavel'
        d2b0_plano_por_data.append({
            'data': dt, 'fontes': fontes, 'qtd_pagamentos': len(linhas_dia),
            'status_plano_data': status_data, 'motivo_data': motivo_data,
        })
    plano_por_pagamento_id = {str(x.get('despesa_id') or ''): x for x in d2a_plano_por_pagamento}
    datas_bloqueadas_d2a2 = {str(x.get('data') or '') for x in d2a_plano_por_data if str(x.get('status_plano_data') or '') != 'materializavel'}
    datas_ativaveis_d2a2 = {str(x.get('data') or '') for x in d2a_plano_por_data if str(x.get('status_plano_data') or '') == 'materializavel'}
    datas_ativaveis_d2b1 = {str(x.get('data') or '') for x in d2b0_plano_por_data if str(x.get('status_plano_data') or '') == 'materializavel'}
    plano_d2b1_por_pagamento: dict[str, list[dict[str, Any]]] = {}
    for item in d2b0_plano_por_pagamento_fonte:
        plano_d2b1_por_pagamento.setdefault(str(item.get('despesa_id') or ''), []).append(item)
    for pid_plano in plano_d2b1_por_pagamento:
        plano_d2b1_por_pagamento[pid_plano] = sorted(plano_d2b1_por_pagamento[pid_plano], key=lambda x: int(x.get('ordem_fonte') or 0))

    for _, row in quadro_ord.iterrows():
        d = row.to_dict(); pid=_txt(d.get('pagamento_id')); central=mapa_central.get(pid,{})
        pacote=_inferir_pacote(d)
        data_pagamento_key = str(d.get('data_pagamento') or '')
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
            if pacote == 'pay_only':
                plano_d2b1_itens = plano_d2b1_por_pagamento.get(pid, [])
                ativado_d2b1 = False
                if plano_d2b1_itens:
                    dt_b1 = str(plano_d2b1_itens[0].get('data') or '')
                    if dt_b1 in datas_ativaveis_d2b1 and all(bool(x.get('valido_para_ativacao')) for x in plano_d2b1_itens):
                        fonte_composta = ' + '.join([str(x.get('fonte_usada') or '') for x in plano_d2b1_itens if float(x.get('valor_pago_pela_fonte') or 0.0) > 0.0])
                        pago_total = round(sum(float(x.get('valor_pago_pela_fonte') or 0.0) for x in plano_d2b1_itens), 2)
                        sal_ant_comp = round(sum(float(x.get('saldo_antes_fonte') or 0.0) for x in plano_d2b1_itens), 2)
                        residuals_pos = sum(1 for x in plano_d2b1_itens if bool(x.get('residual_positivo')))
                        if residuals_pos > 1:
                            d2b1['d2b1_violacoes_residual_global'] += 1
                        lote_op = fonte_composta if fonte_composta else lote_op
                        fonte_candidata_id = fonte_composta if fonte_composta else fonte_candidata_id
                        origem_fonte_candidata = 'pay_only_diario_v1_combinacao_minima'
                        tipo_fonte_candidata = 'lote_combinado'
                        sal_ant = sal_ant_comp
                        br = pago_total
                        imp = 0.0
                        liq = pago_total
                        cons = pago_total
                        sal_dep = round(sum(float(x.get('saldo_depois_fonte') or 0.0) for x in plano_d2b1_itens), 2)
                        cobertura = 'sim'
                        status = 'ok'
                        motivo = 'n/d'
                        ativado_d2b1 = True
                        d2b1['d2b1_pagamentos_ativados'] += 1
                        if _eh_nd(lote_origem):
                            d2b1['d2b1_pagamentos_nao_determinados_ativados'] += 1
                        d2b1['d2b1_fontes_usadas_total'] += len([x for x in plano_d2b1_itens if float(x.get('valor_pago_pela_fonte') or 0.0) > 0.0])
                        d2b1['d2b1_fontes_com_residual_positivo_total'] += residuals_pos
                    else:
                        d2b1['d2b1_falhas_ativacao'] += 1
                if not ativado_d2b1:
                    plano = plano_por_pagamento_id.get(pid, {})
                    data_plano = str(plano.get('data') or '')
                    if data_plano in datas_bloqueadas_d2a2:
                        d2a2['d2a2_datas_bloqueadas'] += 1
                    ativado_d2a2 = bool(
                        data_plano in datas_ativaveis_d2a2
                        and bool(plano.get('valido_para_ativacao'))
                        and str(plano.get('origem_planejada') or '') == 'pay_only_diario_v1'
                        and str(plano.get('status_planejado') or '') == 'ok'
                        and str(plano.get('cobertura_integral_planejada') or '') == 'sim'
                    )
                    if ativado_d2a2:
                        lote_planejado = str(plano.get('fonte_unica_escolhida') or '')
                        if lote_planejado:
                            lote_op = lote_planejado
                            fonte_candidata_id = lote_planejado
                            origem_fonte_candidata = 'pay_only_diario_v1'
                            tipo_fonte_candidata = 'lote_aportado'
                            sal_ant = _round(plano.get('saldo_antes_planejado'))
                            br = _round(plano.get('bruto_planejado'))
                            imp = _round(plano.get('imposto_planejado'))
                            liq = _round(plano.get('liquido_planejado'))
                            cons = _round(plano.get('consumo_planejado'))
                            sal_dep = _round(plano.get('saldo_depois_planejado'))
                            cobertura = 'sim'
                            status = 'ok'
                            motivo = 'n/d'
                            promovida_para_lote_sugerido = True
                            d2a2['d2a2_pagamentos_ativados'] += 1
                            if _eh_nd(lote_origem):
                                d2a2['d2a2_pagamentos_nao_determinados_ativados'] += 1
                            if lote_planejado in estado_lotes and sal_dep != '':
                                estado_lotes[lote_planejado]['saldo_liquido'] = float(sal_dep)
                # D2A permanece sem combinação mínima (D2B bloqueado)
                d2a_funil['d2a_linhas_no_bloco_pay_only'] += 1
                valor_pag = val if val != '' else 0.0
                # D2A: ativação funcional do pay_only_diario_v1 apenas para datas
                # resolvidas por fonte única no shadow.
                lote_diario = ativacao_fonte_unica_por_data.get(data_pagamento_key, '')
                if lote_diario:
                    d2a_funil['d2a_com_data_no_mapa_fonte_unica'] += 1
                if lote_op == 'não determinado':
                    d2a_funil['d2a_com_lote_op_nao_determinado'] += 1
                if status in {'sem_fonte_auditavel', 'sem_saldo_temporal_auditavel', '', 'não determinado'}:
                    d2a_funil['d2a_passa_filtro_status'] += 1
                if lote_diario and lote_diario in estado_lotes:
                    meta_diario = estado_lotes.get(lote_diario, {})
                    saldo_diario = float(meta_diario.get('saldo_liquido') or saldo_ativacao_por_data.get(data_pagamento_key, 0.0))
                    data_apl = meta_diario.get('data_aplicacao')
                    car_ate = meta_diario.get('carencia_ate')
                    mig_em = meta_diario.get('migrado_em')
                    motivo_mig = _motivo_bloqueio_migracao(d.get('data_pagamento'), mig_em, pacote)
                    bloqueado_temporal = bool(
                        (data_apl is not None and d.get('data_pagamento') is not None and data_apl > d.get('data_pagamento'))
                        or (car_ate is not None and d.get('data_pagamento') is not None and car_ate > d.get('data_pagamento'))
                        or bool(motivo_mig)
                    )
                    if bloqueado_temporal:
                        d2a_funil['d2a_rejeitadas_por_data_carencia_migracao'] += 1
                    elif saldo_diario + 0.01 < float(valor_pag or 0.0):
                        d2a_funil['d2a_rejeitadas_por_saldo'] += 1
                    else:
                        d2a_funil['d2a_promovidas_internamente_pay_only_diario_v1'] += 1

                if lote_op=='não determinado':
                    # pay_only_fifo_v1: escolhe lote elegível mais antigo que cobre integralmente
                    data_pag = d.get('data_pagamento')
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

        evento = {
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
        }
        if str(evento.get('origem_fonte_candidata') or '').strip() == 'pay_only_diario_v1':
            d2a_funil['d2a_promovidas_evento_final_pay_only_diario_v1'] += 1
            d2a_funil['d2a_promovidas_extrato_futuro_auditoria_fontes'] += 1
            d2a2['d2a2_datas_ativadas'] = len(datas_ativaveis_d2a2)
        if str(evento.get('origem_fonte_candidata') or '').strip() == 'pay_only_diario_v1_combinacao_minima':
            d2b1['d2b1_datas_ativadas'] = len(datas_ativaveis_d2b1)
        eventos.append(_normalizar_evento_operacional(evento))
    return {
        "eventos": eventos,
        "fifo_candidatos_avaliados": fifo_candidatos_avaliados,
        "pay_only_diario_shadow_por_data": shadow_por_data,
        "plano_pay_only_diario_v1_por_pagamento": d2a_plano_por_pagamento,
        "d2a_plano_por_data": d2a_plano_por_data,
        "plano_pay_only_diario_v1_combinacao_minima_por_pagamento_fonte": d2b0_plano_por_pagamento_fonte,
        "d2b0_plano_por_data": d2b0_plano_por_data,
        **d2a_funil,
        **d2a_plano,
        **d2a2,
        **d2b0,
        **d2b1,
        **shadow_counters,
    }
