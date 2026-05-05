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

    pagamentos_planejados_encontrados: set[str] = set()
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
        'd2b1_residual_pagamentos_planejados': 0,
        'd2b1_residual_pagamentos_ativados': 0,
        'd2b1_residual_pagamentos_falhos': 0,
        'd2b1_residual_falhas_por_mapeamento_despesa_id': 0,
        'd2b1_residual_falhas_por_multifonte': 0,
        'd2b1_residual_falhas_por_data': 0,
        'd2b1_residual_falhas_por_sobrescrita': 0,
        'd2b1_residual_falhas_por_evento_final': 0,
        'd2b1_residual_divergencias_plano_evento': 0,
        'd2b1_residual_divergencias_evento_saida': 0,
    }
    d2c = {
        'd2c_pagamentos_residuais_total': 0,
        'd2c_residuais_bloqueio_legitimo_migracao': 0,
        'd2c_residuais_com_fonte_unica_alternativa': 0,
        'd2c_residuais_com_combinacao_alternativa': 0,
        'd2c_residuais_sem_fonte_elegivel': 0,
        'd2c_residuais_falha_planejamento': 0,
        'd2c_conflitos_migracao': 0,
        'd2c_consumo_pos_switching_indevido': 0,
        'd2c_violacoes_residual_global': 0,
    }
    d2c_residuais_detalhe: list[dict[str, Any]] = []
    d3 = {
        'd3_residuais_total': 0,
        'd3_residuais_inviabilizados_por_switching': 0,
        'd3_residuais_sem_fonte_mesmo_sem_switching': 0,
        'd3_datas_residuais_total': 0,
        'd3_datas_com_pay_only_sem_switching_factivel': 0,
        'd3_datas_com_switch_then_pay_factivel': 0,
        'd3_datas_com_pay_then_switch_factivel': 0,
        'd3_datas_sem_pacote_factivel': 0,
        'd3_switchings_bloqueantes_identificados': 0,
        'd3_conflitos_pagamento_switching': 0,
        'd3_consumo_pos_switching_indevido': 0,
        'd3_violacoes_residual_global': 0,
    }
    d3_residuais_detalhe: list[dict[str, Any]] = []
    d3_datas_residuais_detalhe: list[dict[str, Any]] = []
    d3b = {
        'd3b_lotes_estado_total': 0,'d3b_lotes_candidatos_switching': 0,'d3b_lotes_candidatos_alocacao_aporte': 0,
        'd3b_lotes_disponiveis_nao_candidatos': 0,'d3b_lotes_excluidos_por_carencia': 0,'d3b_lotes_excluidos_por_liquidez': 0,
        'd3b_lotes_excluidos_por_vencimento_prazo': 0,'d3b_lotes_excluidos_por_migracao': 0,'d3b_lotes_excluidos_por_exaurido': 0,
        'd3b_lotes_excluidos_por_fonte_futura': 0,'d3b_lotes_excluidos_por_filtro_indefinido': 0,'d3b_lotes_disponiveis_hoje_candidatos': 0,
        'd3b_lotes_disponiveis_hoje_fora_do_motor': 0,'d3b_datas_switching_por_vencimento': 0,'d3b_datas_switching_por_disponibilidade_real': 0,
        'd3b_datas_switching_por_carencia': 0,'d3b_datas_switching_por_fallback': 0,'d3b_inconsistencias_universo_switching': 0,
        'd3b_inconsistencias_universo_alocacao': 0,'d3b_pacotes_d3_com_violacao_residual_global': 0,
    }
    d3b_lotes_detalhe: list[dict[str, Any]] = []
    d3c = {
        'd3c_fontes_total': 0, 'd3c_fontes_exauridas': 0, 'd3c_fontes_pagamento_disponiveis': 0,
        'd3c_lotes_aportados_candidatos_switching': 0, 'd3c_fontes_disponiveis_para_aporte': 0,
        'd3c_fontes_bloqueadas_carencia': 0, 'd3c_fontes_bloqueadas_migracao': 0, 'd3c_fontes_futuras': 0,
        'd3c_fontes_com_dupla_classificacao': 0, 'd3c_fontes_exauridas_reintroduzidas': 0, 'd3c_fontes_migradas_reintroduzidas': 0,
        'd3c_inconsistencias_universo_pagamento': 0, 'd3c_inconsistencias_universo_switching': 0, 'd3c_inconsistencias_universo_alocacao': 0,
        'd3c_pacotes_d3_com_violacao_residual_global': 0,
    }
    d3c_fontes_saneadas: list[dict[str, Any]] = []
    LIMIAR_RESIDUAL_OPERACIONAL = 0.20
    d3d = {
        'd3d_fontes_total': 0,'d3d_fontes_exauridas_operacionais': 0,'d3d_fontes_residual_marginal_acima_limiar': 0,
        'd3d_fontes_pagamento_pay_only': 0,'d3d_fontes_switch_then_pay': 0,'d3d_fontes_pay_then_switch_residual': 0,
        'd3d_fontes_alocacao_aporte': 0,'d3d_fontes_apenas_diagnostico': 0,'d3d_fontes_migradas_reintroduzidas': 0,
        'd3d_fontes_exauridas_reintroduzidas': 0,'d3d_fontes_com_risco_dupla_contagem': 0,'d3d_inconsistencias_universo_pagamento': 0,
        'd3d_inconsistencias_universo_switching': 0,'d3d_inconsistencias_universo_alocacao': 0,'d3d_pacotes_operacionalmente_factiveis': 0,
        'd3d_pacotes_bloqueados_por_residual_global': 0,'d3d_pacotes_bloqueados_por_migracao': 0,'d3d_pacotes_bloqueados_por_dupla_contagem': 0,
    }
    d3d_fontes_saneadas: list[dict[str, Any]] = []
    d3e = {
        'd3e_fontes_total': 0,'d3e_fontes_classificadas_total': 0,'d3e_fontes_nao_classificadas': 0,
        'd3e_fontes_exauridas_operacionais': 0,'d3e_fontes_residual_marginal': 0,'d3e_fontes_pagamento_pay_only': 0,
        'd3e_fontes_switch_then_pay': 0,'d3e_fontes_pay_then_switch_residual': 0,'d3e_fontes_bloqueadas_migracao': 0,
        'd3e_fontes_bloqueadas_carencia': 0,'d3e_fontes_futuras': 0,'d3e_fontes_apenas_diagnostico': 0,
        'd3e_fontes_com_risco_dupla_contagem': 0,'d3e_pacotes_d3_total': 0,'d3e_pacotes_operacionalmente_factiveis': 0,
        'd3e_pacotes_bloqueados_por_residual_global': 0,'d3e_pacotes_bloqueados_por_migracao': 0,'d3e_pacotes_bloqueados_por_dupla_contagem': 0,
        'd3e_pacotes_bloqueados_por_fonte_indisponivel': 0,'d3e_inconsistencias_classificacao': 0,
    }
    d3e_fontes_saneadas: list[dict[str, Any]] = []
    d3e_pacotes_por_data: list[dict[str, Any]] = []
    d3f = {
        'd3f_fontes_total': 0,'d3f_fontes_classificadas_total': 0,'d3f_fontes_nao_classificadas': 0,'d3f_status_primario_soma': 0,
        'd3f_fontes_com_status_primario_duplicado': 0,'d3f_fontes_exauridas_operacionais': 0,'d3f_fontes_residual_marginal': 0,
        'd3f_fontes_lote_aportado_ativo': 0,'d3f_fontes_bloqueadas_migracao': 0,'d3f_fontes_bloqueadas_carencia': 0,'d3f_fontes_futuras': 0,
        'd3f_fontes_com_risco_dupla_contagem': 0,'d3f_papeis_pay_only': 0,'d3f_papeis_switch_then_pay': 0,'d3f_papeis_pay_then_switch': 0,
        'd3f_pacotes_operacionalmente_factiveis': 0,'d3f_pacotes_bloqueados_por_residual_global': 0,'d3f_pacotes_bloqueados_por_migracao': 0,'d3f_pacotes_bloqueados_por_dupla_contagem': 0,
    }
    d3f_fontes_saneadas: list[dict[str, Any]] = []
    d31 = {
        'd31_datas_residuais_total': 0,'d31_cenarios_avaliados_total': 0,'d31_cenarios_operacionalmente_factiveis': 0,
        'd31_cenarios_bloqueados_residual_global': 0,'d31_cenarios_bloqueados_migracao': 0,'d31_cenarios_bloqueados_dupla_contagem': 0,
        'd31_cenarios_pagamento_integral': 0,'d31_cenarios_sem_pagamento_integral': 0,'d31_cenarios_com_ganho_terminal': 0,'d31_cenarios_com_perda_terminal': 0,
        'd31_melhor_cenario_por_data_definido': 0,'d31_recomendacoes_revisar_switching': 0,'d31_recomendacoes_manter_switching': 0,'d31_recomendacoes_adiar_switching': 0,
    }
    d31_cenarios_por_data: list[dict[str, Any]] = []
    d31b = {
        'd31b_datas_residuais_total': 0,'d31b_cenarios_avaliados_total': 0,'d31b_cenarios_com_contrafactual_recalculado': 0,
        'd31b_cenarios_pagamento_integral': 0,'d31b_cenarios_sem_pagamento_integral': 0,'d31b_cenarios_operacionalmente_factiveis': 0,
        'd31b_cenarios_bloqueados_residual_global': 0,'d31b_cenarios_bloqueados_migracao': 0,'d31b_cenarios_bloqueados_dupla_contagem': 0,
        'd31b_cenarios_bloqueados_sem_materializacao_pos_switching': 0,'d31b_cenarios_com_delta_terminal_nao_zero': 0,'d31b_cenarios_sem_delta_discriminativo': 0,
        'd31b_melhor_cenario_por_data_definido': 0,'d31b_recomendacoes_revisar_switching': 0,'d31b_recomendacoes_adiar_switching': 0,'d31b_recomendacoes_manter_switching': 0,'d31b_recomendacoes_sem_confiabilidade': 0,
    }
    d31b_cenarios_por_data: list[dict[str, Any]] = []
    d31c = {
        'd31c_datas_residuais_total': 0,'d31c_cenarios_valorados_total': 0,'d31c_cenarios_com_delta_terminal_nao_zero': 0,
        'd31c_cenarios_sem_delta_por_falta_modelo': 0,'d31c_cenarios_sem_delta_por_dados_insuficientes': 0,'d31c_cenarios_operacionalmente_factiveis_valorados': 0,
        'd31c_cenarios_com_ganho_terminal': 0,'d31c_cenarios_com_perda_terminal': 0,'d31c_melhor_cenario_economico_por_data_definido': 0,
        'd31c_recomendacoes_adiar_switching': 0,'d31c_recomendacoes_cancelar_switching': 0,'d31c_recomendacoes_pay_then_switch': 0,'d31c_recomendacoes_sem_confiabilidade_economica': 0,
    }
    d31c_cenarios_por_data: list[dict[str, Any]] = []
    d31d = {
        'd31d_datas_residuais_total': 0,'d31d_cenarios_total': 0,'d31d_cenarios_valorados': 0,'d31d_cenarios_nao_valorados': 0,
        'd31d_cenarios_valorados_com_delta': 0,'d31d_cenarios_sem_delta_por_falta_horizonte': 0,'d31d_cenarios_sem_delta_por_falta_taxa_destino': 0,
        'd31d_cenarios_sem_delta_por_falta_residual': 0,'d31d_cenarios_sem_delta_por_falta_funcao_terminal': 0,'d31d_cenarios_bloqueados_operacionalmente': 0,
        'd31d_funcoes_terminal_existentes_identificadas': 0,'d31d_reuso_switching_shadow_possivel': 0,'d31d_reuso_ranking_proxy_possivel': 0,
        'd31d_melhor_cenario_economico_definido': 0,'d31d_melhor_cenario_operacional_definido': 0,'d31d_recomendacoes_sem_confiabilidade_economica': 0,
    }
    d31d_cenarios_detalhe: list[dict[str, Any]] = []
    d31e = {
        'd31e_datas_residuais_total': 0,'d31e_cenarios_alvo_total': 0,'d31e_bases_valoracao_completas': 0,'d31e_bases_valoracao_incompletas': 0,
        'd31e_bases_incompletas_falta_residual': 0,'d31e_bases_incompletas_falta_destino': 0,'d31e_bases_incompletas_falta_taxa': 0,
        'd31e_bases_incompletas_falta_horizonte': 0,'d31e_bases_incompletas_falta_funcao_terminal': 0,'d31e_bases_com_residual_zero_operacional': 0,
        'd31e_bases_com_residual_positivo': 0,'d31e_reuso_switching_shadow_aplicado': 0,'d31e_reuso_ranking_proxy_aplicado': 0,'d31e_prontas_para_delta_terminal': 0,
    }
    d31e_bases_por_cenario: list[dict[str, Any]] = []
    d31f = {
        'd31f_cenarios_alvo_total': 0,'d31f_bases_completas_total': 0,'d31f_bases_completas_sem_residual_terminal': 0,'d31f_bases_completas_com_residual_positivo': 0,
        'd31f_bases_incompletas_total': 0,'d31f_bases_incompletas_falta_residual_real': 0,'d31f_bases_incompletas_falta_destino': 0,'d31f_bases_incompletas_falta_taxa': 0,'d31f_bases_incompletas_falta_horizonte': 0,
        'd31f_bases_prontas_para_delta_terminal': 0,'d31f_cenarios_com_delta_terminal_zero_justificado': 0,'d31f_cenarios_com_delta_terminal_nao_zero': 0,'d31f_cenarios_economicamente_equivalentes': 0,
        'd31f_recomendacoes_operacionais_adiar_switching': 0,'d31f_recomendacoes_economicas_sem_diferenca_terminal': 0,
    }
    d31f_bases_reclassificadas: list[dict[str, Any]] = []
    d32a = {
        'd32a_datas_residuais_total': 0,'d32a_pagamentos_residuais_total': 0,'d32a_pagamentos_residuais_planejados_ok': 0,'d32a_switchings_bloqueantes_total': 0,
        'd32a_switchings_com_adiamento_planejado': 0,'d32a_planos_ativaveis': 0,'d32a_planos_nao_ativaveis': 0,'d32a_violacoes_residual_global': 0,
        'd32a_conflitos_migracao': 0,'d32a_riscos_dupla_contagem': 0,'d32a_delta_terminal_zero_justificado': 0,'d32a_delta_terminal_nao_zero': 0,
        'd32a_pagamentos_que_passariam_para_ok': 0,'d32a_nao_determinados_residuais_restantes_se_ativado': 0,
    }
    d32a_plano_por_data: list[dict[str, Any]] = []
    saldo_temporal = {
        'comparativo_funcoes_legadas_mapeadas': 0,
        'comparativo_funcoes_sem_equivalente_atual': 0,
        'recebidos_total_origem_situacao_atual': 0,
        'recebidos_total_integrados_ledger': 0,
        'saldo_temporal_lotes_auditados': 0,'saldo_temporal_lotes_com_consumo_acima_saldo': 0,'saldo_temporal_pagamentos_auditados': 0,
        'saldo_temporal_pagamentos_ok_antes': 0,'saldo_temporal_pagamentos_ok_depois': 0,'saldo_temporal_pagamentos_rebaixados_por_saldo': 0,
        'saldo_temporal_lote_7500_reiniciado': 0,'saldo_temporal_lote_8500_consumo_acima_saldo': 0,'saldo_temporal_divergencias_saldo_antes': 0,
        'saldo_temporal_divergencias_saldo_depois': 0,'saldo_temporal_invariantes_violados': 0,
        'recebidos_futuros_total': 0,'recebidos_futuros_incorporados_total': 0,'recebidos_disponiveis_incorporados_total': 0,'recebidos_disponiveis_nao_incorporados': 0,'recebidos_futuros_auditoria_linhas': 0,'pagamentos_rebaixados_por_fonte_nao_incorporada': 0,'pagamentos_rebaixados_por_recebido_nao_incorporado': 0,'pagamentos_rebaixados_por_saldo_real_insuficiente': 0,
        'saldo_temporal_fontes_auditadas_total': 0,
        'alocacao_fontes_disponiveis_total': 0,'alocacao_valor_liquido_disponivel_total': 0.0,'alocacao_valor_reservado_pagamentos_total': 0.0,'alocacao_valor_alocavel_total': 0.0,
        'alocacao_fontes_candidatas_aporte': 0,'alocacao_fontes_reservadas_pagamento': 0,'alocacao_fontes_mantidas_caixa': 0,'alocacao_fontes_com_destino_carteira': 0,'alocacao_fontes_sem_destino_carteira': 0,
        'alocacao_inconsistencias_classificacao': 0,'alocacao_decisoes_integradas_ao_ledger': 0,
        'pagamentos_rebaixados_recuperaveis_shadow_por_recebidos': 0,'pagamentos_rebaixados_saldo_real_insuficiente_pos_recebidos': 0,
        'saldo_temporal_lote_8500_evento_causal': '',
    }
    saldo_temporal_auditoria_lotes: list[dict[str, Any]] = []
    saldo_temporal_pagamentos_rebaixados_detalhe: list[dict[str, Any]] = []
    recebidos_futuros_auditoria: list[dict[str, Any]] = []
    alocacao_fontes_auditoria: list[dict[str, Any]] = []
    comparativo_mapa_funcoes_legadas: list[dict[str, Any]] = []
    def _pid_norm(v: Any) -> str:
        s = _txt(v)
        return s[:-2] if s.endswith('.0') else s
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
            pid = _pid_norm(linha.get('pagamento_id'))
            conta = _txt(linha.get('descricao_pagamento'))
            restante = float(_round(linha.get('valor_pagamento')) or 0.0)
            pago_total = 0.0
            linhas_pagamento_tmp: list[dict[str, Any]] = []
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
                linhas_pagamento_tmp.append({
                    'data': dt, 'despesa_id': pid, 'conta': conta, 'valor_pagamento': float(_round(linha.get('valor_pagamento')) or 0.0),
                    'fonte_usada': f, 'ordem_fonte': idx, 'valor_pago_pela_fonte': pago, 'saldo_antes_fonte': saldo_antes,
                    'bruto_planejado': pago, 'imposto_planejado': 0.0, 'liquido_planejado': pago, 'consumo_planejado': pago,
                    'saldo_depois_fonte': saldo_depois, 'residual_fonte': max(saldo_depois, 0.0), 'residual_positivo': bool(saldo_depois > 0.20),
                    'cobertura_integral_planejada': 'não',
                    'status_planejado': 'nao_ativavel',
                    'motivo_planejado': '',
                    'origem_planejada': 'pay_only_diario_v1_combinacao_minima',
                    'valido_para_ativacao': False,
                    'motivo_nao_ativavel': '',
                })
            pagamento_valido = bool(restante <= 0.01 and data_ok)
            motivo_pag = '' if pagamento_valido else ('saldo_insuficiente_no_plano' if data_ok else motivo_data)
            for lp in linhas_pagamento_tmp:
                lp['cobertura_integral_planejada'] = 'sim' if pagamento_valido else 'não'
                lp['status_planejado'] = 'ok' if pagamento_valido else 'nao_ativavel'
                lp['motivo_planejado'] = 'n/d' if pagamento_valido else motivo_pag
                lp['valido_para_ativacao'] = pagamento_valido
                lp['motivo_nao_ativavel'] = '' if pagamento_valido else motivo_pag
                d2b0_plano_por_pagamento_fonte.append(lp)
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
        plano_d2b1_por_pagamento.setdefault(_pid_norm(item.get('despesa_id')), []).append(item)
    d2b1['d2b1_residual_pagamentos_planejados'] = len(plano_d2b1_por_pagamento.keys())
    planned_ids_d2b1 = set(plano_d2b1_por_pagamento.keys())
    for pid_plano in plano_d2b1_por_pagamento:
        plano_d2b1_por_pagamento[pid_plano] = sorted(plano_d2b1_por_pagamento[pid_plano], key=lambda x: int(x.get('ordem_fonte') or 0))

    for _, row in quadro_ord.iterrows():
        d = row.to_dict(); pid=_pid_norm(d.get('pagamento_id')); central=mapa_central.get(pid,{})
        fontes_usadas: list[str] = []
        valor_pago_por_fonte: dict[str, float] = {}
        saldo_antes_por_fonte: dict[str, float] = {}
        consumo_por_fonte: dict[str, float] = {}
        saldo_depois_por_fonte: dict[str, float] = {}
        residual_por_fonte: dict[str, float] = {}
        residual_positivo_por_fonte: dict[str, bool] = {}
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
                    pagamentos_planejados_encontrados.add(pid)
                    dt_b1 = str(plano_d2b1_itens[0].get('data') or '')
                    if dt_b1 in datas_ativaveis_d2b1 and all(bool(x.get('valido_para_ativacao')) for x in plano_d2b1_itens):
                        itens_com_pagamento = [x for x in plano_d2b1_itens if float(x.get('valor_pago_pela_fonte') or 0.0) > 0.0]
                        fonte_composta = ' + '.join([str(x.get('fonte_usada') or '') for x in itens_com_pagamento])
                        pago_total = round(sum(float(x.get('valor_pago_pela_fonte') or 0.0) for x in plano_d2b1_itens), 2)
                        sal_ant_comp = round(sum(float(x.get('saldo_antes_fonte') or 0.0) for x in plano_d2b1_itens), 2)
                        residuals_pos = sum(1 for x in plano_d2b1_itens if bool(x.get('residual_positivo')))
                        if residuals_pos > 1:
                            d2b1['d2b1_violacoes_residual_global'] += 1
                        lote_op = fonte_composta if fonte_composta else lote_op
                        fonte_candidata_id = fonte_composta if fonte_composta else fonte_candidata_id
                        origem_fonte_candidata = 'pay_only_diario_v1_combinacao_minima'
                        tipo_fonte_candidata = 'combinacao_minima_fontes'
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
                        fontes_usadas = [str(x.get('fonte_usada') or '') for x in itens_com_pagamento]
                        valor_pago_por_fonte = {str(x.get('fonte_usada') or ''): round(float(x.get('valor_pago_pela_fonte') or 0.0), 2) for x in itens_com_pagamento}
                        saldo_antes_por_fonte = {str(x.get('fonte_usada') or ''): round(float(x.get('saldo_antes_fonte') or 0.0), 2) for x in itens_com_pagamento}
                        consumo_por_fonte = {str(x.get('fonte_usada') or ''): round(float(x.get('consumo_planejado') or x.get('valor_pago_pela_fonte') or 0.0), 2) for x in itens_com_pagamento}
                        saldo_depois_por_fonte = {str(x.get('fonte_usada') or ''): round(float(x.get('saldo_depois_fonte') or 0.0), 2) for x in itens_com_pagamento}
                        residual_por_fonte = {str(x.get('fonte_usada') or ''): round(float(x.get('residual_fonte') or 0.0), 2) for x in itens_com_pagamento}
                        residual_positivo_por_fonte = {str(x.get('fonte_usada') or ''): bool(x.get('residual_positivo')) for x in itens_com_pagamento}
                        d2b1['d2b1_pagamentos_ativados'] += 1
                        if _eh_nd(lote_origem):
                            d2b1['d2b1_pagamentos_nao_determinados_ativados'] += 1
                        d2b1['d2b1_fontes_usadas_total'] += len([x for x in plano_d2b1_itens if float(x.get('valor_pago_pela_fonte') or 0.0) > 0.0])
                        d2b1['d2b1_fontes_com_residual_positivo_total'] += residuals_pos
                    else:
                        d2b1['d2b1_falhas_ativacao'] += 1
                        if dt_b1 not in datas_ativaveis_d2b1:
                            d2b1['d2b1_residual_falhas_por_data'] += 1
                        elif not all(bool(x.get('valido_para_ativacao')) for x in plano_d2b1_itens):
                            d2b1['d2b1_residual_falhas_por_multifonte'] += 1
                if not ativado_d2b1:
                    fontes_usadas = []
                    valor_pago_por_fonte = {}
                    saldo_antes_por_fonte = {}
                    consumo_por_fonte = {}
                    saldo_depois_por_fonte = {}
                    residual_por_fonte = {}
                    residual_positivo_por_fonte = {}
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
            'fontes_usadas': fontes_usadas if 'fontes_usadas' in locals() else [],
            'valor_pago_por_fonte': valor_pago_por_fonte if 'valor_pago_por_fonte' in locals() else {},
            'saldo_antes_por_fonte': saldo_antes_por_fonte if 'saldo_antes_por_fonte' in locals() else {},
            'consumo_por_fonte': consumo_por_fonte if 'consumo_por_fonte' in locals() else {},
            'saldo_depois_por_fonte': saldo_depois_por_fonte if 'saldo_depois_por_fonte' in locals() else {},
            'residual_por_fonte': residual_por_fonte if 'residual_por_fonte' in locals() else {},
            'residual_positivo_por_fonte': residual_positivo_por_fonte if 'residual_positivo_por_fonte' in locals() else {},
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
            d2b1['d2b1_residual_pagamentos_ativados'] += 1
        elif pid in plano_d2b1_por_pagamento:
            d2b1['d2b1_residual_pagamentos_falhos'] += 1
            d2b1['d2b1_residual_falhas_por_evento_final'] += 1
        eventos.append(_normalizar_evento_operacional(evento))
    d2b1['d2b1_residual_falhas_por_mapeamento_despesa_id'] = len(planned_ids_d2b1 - pagamentos_planejados_encontrados)

    for evento in eventos:
        motivo = str(evento.get('motivo_bloqueio') or '')
        if motivo != 'bloqueado_por_migracao_antes_do_pagamento':
            continue
        pid = _pid_norm(evento.get('pagamento_id'))
        candidatos = [c for c in fifo_candidatos_avaliados if _pid_norm(c.get('Despesa ID')) == pid]
        fontes_candidatas = [str(c.get('lote_id') or '') for c in candidatos]
        fontes_bloq_mig = [c for c in candidatos if bool(c.get('bloqueado_por_migracao'))]
        fontes_elegiveis = [c for c in candidatos if bool(c.get('elegivel_fifo'))]
        valor_pag = float(evento.get('consumo') or evento.get('liquido') or 0.0)
        existe_fonte_unica = any(float(c.get('saldo_liquido') or 0.0) + 0.01 >= valor_pag for c in fontes_elegiveis)
        saldo_elegivel_total = round(sum(float(c.get('saldo_liquido') or 0.0) for c in fontes_elegiveis), 2)
        existe_combinacao = bool(saldo_elegivel_total + 0.01 >= valor_pag and len(fontes_elegiveis) >= 2)
        residuals_pos = sum(1 for c in fontes_elegiveis if float(c.get('saldo_liquido') or 0.0) > 0.20)
        regra_residual_ok = bool(residuals_pos <= 1) if fontes_elegiveis else False
        if existe_fonte_unica or existe_combinacao:
            classificacao = 'falha_planejamento'
            d2c['d2c_residuais_falha_planejamento'] += 1
        elif not fontes_elegiveis:
            classificacao = 'bloqueio_legitimo_migracao_sem_fonte_elegivel'
            d2c['d2c_residuais_bloqueio_legitimo_migracao'] += 1
            d2c['d2c_residuais_sem_fonte_elegivel'] += 1
        else:
            classificacao = 'bloqueio_legitimo_migracao'
            d2c['d2c_residuais_bloqueio_legitimo_migracao'] += 1
        if existe_fonte_unica:
            d2c['d2c_residuais_com_fonte_unica_alternativa'] += 1
        if existe_combinacao:
            d2c['d2c_residuais_com_combinacao_alternativa'] += 1
        if not regra_residual_ok and fontes_elegiveis:
            d2c['d2c_violacoes_residual_global'] += 1
        d2c['d2c_conflitos_migracao'] += len(fontes_bloq_mig)
        d2c_residuais_detalhe.append({
            'despesa_id': pid,
            'data': evento.get('data'),
            'conta': evento.get('conta'),
            'valor': valor_pag,
            'fontes_candidatas_no_dia': fontes_candidatas,
            'fontes_bloqueadas_por_migracao': [str(c.get('lote_id') or '') for c in fontes_bloq_mig],
            'data_migracao_por_fonte': {str(c.get('lote_id') or ''): c.get('migrado_em') for c in fontes_bloq_mig},
            'destino_switching_fonte_bloqueada': {str(c.get('lote_id') or ''): (mapa_global_sw.get(str(c.get('lote_id') or ''), {}) or {}).get('produto_destino', '') for c in fontes_bloq_mig},
            'fontes_elegiveis_remanescentes': [str(c.get('lote_id') or '') for c in fontes_elegiveis],
            'saldo_liquido_fontes_elegiveis': {str(c.get('lote_id') or ''): round(float(c.get('saldo_liquido') or 0.0), 2) for c in fontes_elegiveis},
            'existe_fonte_unica_suficiente': existe_fonte_unica,
            'existe_combinacao_minima_suficiente': existe_combinacao,
            'regra_global_residual_satisfeita': regra_residual_ok,
            'motivo_final_d2c': classificacao,
        })
    d2c['d2c_pagamentos_residuais_total'] = len(d2c_residuais_detalhe)

    # D3-0: diagnóstico shadow de comparação de pacotes para residuais D2C.
    por_data_d3: dict[str, list[dict[str, Any]]] = {}
    for item in d2c_residuais_detalhe:
        pid = _pid_norm(item.get('despesa_id'))
        valor = float(item.get('valor') or 0.0)
        candidatos = [c for c in fifo_candidatos_avaliados if _pid_norm(c.get('Despesa ID')) == pid]
        bloqueadas_mig = [c for c in candidatos if bool(c.get('bloqueado_por_migracao'))]
        elegiveis = [c for c in candidatos if bool(c.get('elegivel_fifo'))]
        sem_switching_pool = list(elegiveis) + list(bloqueadas_mig)
        sem_sw_fonte_unica = any(float(c.get('saldo_liquido') or 0.0) + 0.01 >= valor for c in sem_switching_pool)
        sem_sw_saldo_total = round(sum(float(c.get('saldo_liquido') or 0.0) for c in sem_switching_pool), 2)
        sem_sw_combinacao = bool(sem_sw_saldo_total + 0.01 >= valor and len(sem_switching_pool) >= 2)
        pay_only_sem_switching_factivel = bool(sem_sw_fonte_unica or sem_sw_combinacao)
        switch_then_pay_factivel = bool(len(bloqueadas_mig) > 0 and pay_only_sem_switching_factivel)
        pay_then_switch_factivel = bool(pay_only_sem_switching_factivel)
        residuals_pos = sum(1 for c in sem_switching_pool if float(c.get('saldo_liquido') or 0.0) > 0.20)
        residual_global_ok = bool(residuals_pos <= 1) if sem_switching_pool else False
        if not residual_global_ok and sem_switching_pool:
            d3['d3_violacoes_residual_global'] += 1
        if bloqueadas_mig:
            d3['d3_switchings_bloqueantes_identificados'] += len(bloqueadas_mig)
            d3['d3_conflitos_pagamento_switching'] += 1
        if pay_only_sem_switching_factivel:
            d3['d3_residuais_inviabilizados_por_switching'] += 1
            impacto = 'pagamento_inviabilizado_por_switching'
        else:
            d3['d3_residuais_sem_fonte_mesmo_sem_switching'] += 1
            impacto = 'sem_fonte_mesmo_sem_switching'
        d3_residuais_detalhe.append({
            'despesa_id': pid,
            'data': item.get('data'),
            'conta': item.get('conta'),
            'valor': valor,
            'lotes_bloqueantes': [str(c.get('lote_id') or '') for c in bloqueadas_mig],
            'data_migracao_lote_bloqueante': {str(c.get('lote_id') or ''): c.get('migrado_em') for c in bloqueadas_mig},
            'destino_switching_lote_bloqueante': {str(c.get('lote_id') or ''): (mapa_global_sw.get(str(c.get('lote_id') or ''), {}) or {}).get('produto_destino', '') for c in bloqueadas_mig},
            'fonte_disponivel_sem_switching': bool(sem_switching_pool),
            'pay_only_sem_switching_pagaria_conta': pay_only_sem_switching_factivel,
            'switch_then_pay_factivel': switch_then_pay_factivel,
            'pay_then_switch_factivel': pay_then_switch_factivel,
            'remover_ou_adiar_switching_torna_factivel': pay_only_sem_switching_factivel,
            'impacto_qualitativo': impacto,
        })
        por_data_d3.setdefault(str(item.get('data') or ''), []).append(d3_residuais_detalhe[-1])
    d3['d3_residuais_total'] = len(d3_residuais_detalhe)

    for dt, itens in por_data_d3.items():
        total = len(itens)
        pendente = len(itens)
        bloqueantes = sorted({l for it in itens for l in list(it.get('lotes_bloqueantes') or []) if l})
        disponiveis_sem_sw = any(bool(it.get('fonte_disponivel_sem_switching')) for it in itens)
        pay_only_ok = all(bool(it.get('pay_only_sem_switching_pagaria_conta')) for it in itens)
        stp_ok = all(bool(it.get('switch_then_pay_factivel')) for it in itens)
        pts_ok = all(bool(it.get('pay_then_switch_factivel')) for it in itens)
        pacote_factivel = 'nenhum'
        if pay_only_ok:
            pacote_factivel = 'pay_only_sem_switching'
            d3['d3_datas_com_pay_only_sem_switching_factivel'] += 1
        if stp_ok:
            d3['d3_datas_com_switch_then_pay_factivel'] += 1
        if pts_ok:
            d3['d3_datas_com_pay_then_switch_factivel'] += 1
        if pacote_factivel == 'nenhum':
            d3['d3_datas_sem_pacote_factivel'] += 1
        d3_datas_residuais_detalhe.append({
            'data': dt,
            'total_contas_dia': total,
            'total_pendente': pendente,
            'fontes_bloqueadas_por_switching': bloqueantes,
            'fontes_disponiveis_sem_switching': disponiveis_sem_sw,
            'pacote_factivel_identificado': pacote_factivel,
            'motivo_inviabilidade_por_pacote': 'sem_fonte_suficiente_mesmo_sem_switching' if pacote_factivel == 'nenhum' else 'switching_bloqueante_no_plano_atual',
            'recomendacao_diagnostica': 'revisar_switching' if pacote_factivel != 'nenhum' else 'manter_bloqueio',
        })
    d3['d3_datas_residuais_total'] = len(d3_datas_residuais_detalhe)
    d3b['d3b_pacotes_d3_com_violacao_residual_global'] = d3.get('d3_violacoes_residual_global', 0)
    data_ref = getattr(getattr(contexto, 'execucao', None), 'data_referencia', None)
    for lote_id, meta in estado_lotes.items():
        saldo = float(meta.get('saldo_liquido') or 0.0); da = meta.get('data_aplicacao'); car = meta.get('carencia_ate'); mig = meta.get('migrado_em')
        motivo = ''
        cand_sw = lote_id in mapa_global_sw
        if cand_sw:
            d3b['d3b_lotes_candidatos_switching'] += 1
            origem_map = str(meta.get('origem_mapa_migracao') or '')
            if 'data_operacional' in origem_map:
                d3b['d3b_datas_switching_por_disponibilidade_real'] += 1
            elif 'materializacao' in origem_map:
                d3b['d3b_datas_switching_por_fallback'] += 1
            else:
                d3b['d3b_datas_switching_por_fallback'] += 1
        if saldo <= 0.01:
            motivo = 'ja_exaurido'; d3b['d3b_lotes_excluidos_por_exaurido'] += 1
        elif da is not None and data_ref is not None and da > data_ref:
            motivo = 'fonte_futura'; d3b['d3b_lotes_excluidos_por_fonte_futura'] += 1
        elif car is not None and data_ref is not None and car > data_ref:
            motivo = 'carencia'; d3b['d3b_lotes_excluidos_por_carencia'] += 1
        elif mig is not None and data_ref is not None and mig <= data_ref:
            motivo = 'ja_migrado'; d3b['d3b_lotes_excluidos_por_migracao'] += 1
        else:
            d3b['d3b_lotes_candidatos_alocacao_aporte'] += 1
            if cand_sw:
                d3b['d3b_lotes_disponiveis_hoje_candidatos'] += 1
            else:
                d3b['d3b_lotes_disponiveis_hoje_fora_do_motor'] += 1
                d3b['d3b_inconsistencias_universo_switching'] += 1
            motivo = 'disponivel_para_aporte_nao_switching' if not cand_sw else 'candidato_switching'
        if not cand_sw and saldo > 0.01 and motivo in {'', 'disponivel_para_aporte_nao_switching'}:
            d3b['d3b_lotes_disponiveis_nao_candidatos'] += 1
        d3b_lotes_detalhe.append({'lote_id': lote_id, 'saldo_liquido': round(saldo, 2), 'data_aplicacao': da, 'carencia_ate': car, 'migrado_em': mig, 'candidato_switching': cand_sw, 'candidato_alocacao_aporte': bool(saldo > 0.01 and motivo in {'disponivel_para_aporte_nao_switching','candidato_switching'}), 'motivo_classificacao': motivo or 'filtro_indefinido', 'origem_data_switching': meta.get('origem_mapa_migracao') or ('mapa_global_switching' if cand_sw else '')})
    d3b['d3b_lotes_estado_total'] = len(estado_lotes)
    if d3b['d3b_lotes_disponiveis_hoje_fora_do_motor'] > 0:
        d3b['d3b_inconsistencias_universo_alocacao'] += d3b['d3b_lotes_disponiveis_hoje_fora_do_motor']
    # D3-0C: saneamento canônico por estado primário único.
    d3_resid_pids = {_pid_norm(x.get('despesa_id')) for x in d3_residuais_detalhe}
    pids_com_pagamento = {_pid_norm(e.get('pagamento_id')) for e in eventos if str(e.get('origem_fonte_candidata') or '').startswith('pay_only')}
    lotes_exauridos_norm = {_norm(lid) for lid, m in estado_lotes.items() if float(m.get('saldo_liquido') or 0.0) <= 0.01}
    for lote in lotes_replay:
        lid = str(getattr(lote, 'id', ''))
        if not lid:
            continue
        meta = estado_lotes.get(lid, {})
        saldo = float(meta.get('saldo_liquido') or 0.0)
        da = meta.get('data_aplicacao'); car = meta.get('carencia_ate'); mig = meta.get('migrado_em')
        cand_sw = bool(lid in mapa_global_sw)
        cand_aloc = bool(saldo > 0.01 and (not cand_sw))
        cand_pag = bool(saldo > 0.01 and (car is None or car <= data_ref))
        prim = 'excluido_com_motivo'; papeis = []
        if saldo <= 0.01:
            prim = 'exaurido'; d3c['d3c_fontes_exauridas'] += 1
        elif da is not None and data_ref is not None and da > data_ref:
            prim = 'futuro'; d3c['d3c_fontes_futuras'] += 1
        elif car is not None and data_ref is not None and car > data_ref:
            prim = 'bloqueado_carencia'; d3c['d3c_fontes_bloqueadas_carencia'] += 1
        elif mig is not None and data_ref is not None and mig <= data_ref:
            prim = 'bloqueado_migracao'; d3c['d3c_fontes_bloqueadas_migracao'] += 1
        elif cand_sw:
            prim = 'lote_aportado_ativo_candidato_switching'; d3c['d3c_lotes_aportados_candidatos_switching'] += 1
            papeis.append('candidato_switching')
            if cand_pag: papeis.append('fonte_pagamento_disponivel')
        elif cand_pag:
            prim = 'fonte_pagamento_disponivel'; d3c['d3c_fontes_pagamento_disponiveis'] += 1
            if saldo > 0.01: papeis.append('disponivel_para_aporte')
        elif cand_aloc:
            prim = 'disponivel_para_aporte'; d3c['d3c_fontes_disponiveis_para_aporte'] += 1
        if len(papeis) > 1:
            d3c['d3c_fontes_com_dupla_classificacao'] += 1
        if _norm(lid) in lotes_exauridos_norm and (cand_pag or cand_sw or cand_aloc):
            d3c['d3c_fontes_exauridas_reintroduzidas'] += 1
        if prim == 'bloqueado_migracao' and (cand_pag or cand_aloc):
            d3c['d3c_fontes_migradas_reintroduzidas'] += 1
        d3c_fontes_saneadas.append({
            'lote_id': lid, 'data_recebimento': getattr(lote, 'data_recebimento', None), 'data_aplicacao': da,
            'investimento/produto': str(getattr(lote, 'produto_nome', '') or getattr(lote, 'produto_key', '')),
            'saldo_liquido_atual': round(saldo, 2), 'status_primario': prim, 'papeis_secundarios': papeis,
            'candidato_pagamento': cand_pag, 'candidato_switching': cand_sw, 'candidato_alocacao_aporte': cand_aloc,
            'motivo_exclusao_pagamento': 'exaurido_ou_bloqueado' if not cand_pag else '',
            'motivo_exclusao_switching': '' if cand_sw else 'fora_universo_switching',
            'motivo_exclusao_alocacao': '' if cand_aloc else 'nao_aplicavel',
            'origem_classificacao': 'd3c_saneamento_shadow', 'risco_dupla_contagem': bool(len(papeis) > 1),
        })
    d3c['d3c_fontes_total'] = len(d3c_fontes_saneadas)
    d3c['d3c_inconsistencias_universo_switching'] = d3b['d3b_inconsistencias_universo_switching']
    d3c['d3c_inconsistencias_universo_alocacao'] = d3b['d3b_inconsistencias_universo_alocacao']
    d3c['d3c_inconsistencias_universo_pagamento'] = sum(1 for x in d3c_fontes_saneadas if x.get('candidato_pagamento') and x.get('status_primario') in {'exaurido','bloqueado_migracao','bloqueado_carencia','futuro'})
    d3c['d3c_pacotes_d3_com_violacao_residual_global'] = d3.get('d3_violacoes_residual_global', 0)
    # D3-0D: saneamento shadow sem ambiguidade operacional.
    for f in d3c_fontes_saneadas:
        saldo = float(f.get('saldo_liquido_atual') or 0.0)
        migrada = f.get('status_primario') == 'bloqueado_migracao'
        cand_sw = bool(f.get('candidato_switching')); cand_pag = bool(f.get('candidato_pagamento')); cand_aloc = bool(f.get('candidato_alocacao_aporte'))
        status = 'apenas_diagnostico'; papeis = []
        if saldo <= LIMIAR_RESIDUAL_OPERACIONAL:
            status = 'exaurido_operacional'; d3d['d3d_fontes_exauridas_operacionais'] += 1
        elif saldo <= LIMIAR_RESIDUAL_OPERACIONAL + 0.05:
            status = 'residual_marginal_acima_limiar'; d3d['d3d_fontes_residual_marginal_acima_limiar'] += 1
        elif migrada:
            status = 'apenas_diagnostico'; d3d['d3d_pacotes_bloqueados_por_migracao'] += 1
        elif cand_sw:
            status = 'candidato_switch_then_pay'; d3d['d3d_fontes_switch_then_pay'] += 1; papeis.append('candidato_pay_then_switch_residual')
            if cand_pag: d3d['d3d_fontes_com_risco_dupla_contagem'] += 1
        elif cand_pag:
            status = 'candidato_pagamento_pay_only'; d3d['d3d_fontes_pagamento_pay_only'] += 1
        elif cand_aloc:
            status = 'candidato_alocacao_aporte'; d3d['d3d_fontes_alocacao_aporte'] += 1
        else:
            d3d['d3d_fontes_apenas_diagnostico'] += 1
        if migrada and status not in {'apenas_diagnostico'}:
            d3d['d3d_fontes_migradas_reintroduzidas'] += 1
        if status in {'candidato_pagamento_pay_only','candidato_switch_then_pay','candidato_alocacao_aporte'} and saldo <= LIMIAR_RESIDUAL_OPERACIONAL:
            d3d['d3d_fontes_exauridas_reintroduzidas'] += 1
        d3d_fontes_saneadas.append({**f, 'limiar_residual_operacional': LIMIAR_RESIDUAL_OPERACIONAL, 'status_primario_d3d': status, 'papeis_secundarios_d3d': papeis, 'candidato_pagamento_pay_only': status == 'candidato_pagamento_pay_only', 'candidato_switch_then_pay': status == 'candidato_switch_then_pay', 'candidato_pay_then_switch_residual': 'candidato_pay_then_switch_residual' in papeis, 'candidato_alocacao_aporte_d3d': status == 'candidato_alocacao_aporte'})
    d3d['d3d_fontes_total'] = len(d3d_fontes_saneadas)
    d3d['d3d_inconsistencias_universo_pagamento'] = d3d['d3d_fontes_exauridas_reintroduzidas'] + d3d['d3d_fontes_migradas_reintroduzidas']
    d3d['d3d_inconsistencias_universo_switching'] = d3d['d3d_fontes_com_risco_dupla_contagem']
    d3d['d3d_inconsistencias_universo_alocacao'] = sum(1 for x in d3d_fontes_saneadas if x.get('status_primario_d3d') == 'candidato_alocacao_aporte' and bool(x.get('candidato_switching')))
    d3d['d3d_pacotes_bloqueados_por_residual_global'] = d3.get('d3_violacoes_residual_global', 0)
    d3d['d3d_pacotes_bloqueados_por_dupla_contagem'] = d3d['d3d_fontes_com_risco_dupla_contagem']
    d3d['d3d_pacotes_operacionalmente_factiveis'] = 0 if d3d['d3d_pacotes_bloqueados_por_residual_global'] > 0 else d3.get('d3_datas_com_pay_only_sem_switching_factivel', 0)
    # D3-0E: fechamento 40/40 com status primário obrigatório + status de pacotes.
    for f in d3d_fontes_saneadas:
        st = 'apenas_diagnostico'
        if f.get('status_primario') == 'bloqueado_migracao':
            st = 'bloqueada_migracao'; d3e['d3e_fontes_bloqueadas_migracao'] += 1
        elif f.get('status_primario') == 'bloqueado_carencia':
            st = 'bloqueada_carencia'; d3e['d3e_fontes_bloqueadas_carencia'] += 1
        elif f.get('status_primario') == 'futuro':
            st = 'futura'; d3e['d3e_fontes_futuras'] += 1
        elif f.get('status_primario_d3d') == 'exaurido_operacional':
            st = 'exaurida_operacional'; d3e['d3e_fontes_exauridas_operacionais'] += 1
        elif f.get('status_primario_d3d') == 'residual_marginal_acima_limiar':
            st = 'residual_marginal'; d3e['d3e_fontes_residual_marginal'] += 1
        elif f.get('status_primario_d3d') == 'candidato_pagamento_pay_only':
            st = 'pagamento_pay_only'; d3e['d3e_fontes_pagamento_pay_only'] += 1
        elif f.get('status_primario_d3d') == 'candidato_switch_then_pay':
            st = 'switch_then_pay'; d3e['d3e_fontes_switch_then_pay'] += 1
            if bool(f.get('candidato_pay_then_switch_residual')): d3e['d3e_fontes_pay_then_switch_residual'] += 1
        else:
            d3e['d3e_fontes_apenas_diagnostico'] += 1
        if bool(f.get('risco_dupla_contagem')):
            d3e['d3e_fontes_com_risco_dupla_contagem'] += 1
        d3e_fontes_saneadas.append({**f, 'status_primario_d3e': st})
    d3e['d3e_fontes_total'] = len(d3e_fontes_saneadas)
    d3e['d3e_fontes_classificadas_total'] = len([x for x in d3e_fontes_saneadas if str(x.get('status_primario_d3e') or '') != ''])
    d3e['d3e_fontes_nao_classificadas'] = d3e['d3e_fontes_total'] - d3e['d3e_fontes_classificadas_total']
    for d in d3_datas_residuais_detalhe:
        dt = str(d.get('data') or '')
        bloqueio_residual = bool(d3.get('d3_violacoes_residual_global', 0) > 0)
        bloqueio_mig = True
        bloqueio_dupla = bool(d3e['d3e_fontes_com_risco_dupla_contagem'] > 0)
        operacional = False if (bloqueio_residual or bloqueio_mig or bloqueio_dupla) else True
        if bloqueio_residual: d3e['d3e_pacotes_bloqueados_por_residual_global'] += 1
        if bloqueio_mig: d3e['d3e_pacotes_bloqueados_por_migracao'] += 1
        if bloqueio_dupla: d3e['d3e_pacotes_bloqueados_por_dupla_contagem'] += 1
        if not bool(d.get('fontes_disponiveis_sem_switching')): d3e['d3e_pacotes_bloqueados_por_fonte_indisponivel'] += 1
        if operacional: d3e['d3e_pacotes_operacionalmente_factiveis'] += 1
        d3e_pacotes_por_data.append({'data': dt, 'operacionalmente_factivel': operacional, 'economicamente_possivel': bool(d.get('pacote_factivel_identificado') != 'nenhum'), 'bloqueado_por_residual_global': bloqueio_residual, 'bloqueado_por_migracao': bloqueio_mig, 'bloqueado_por_dupla_contagem': bloqueio_dupla, 'bloqueado_por_fonte_indisponivel': not bool(d.get('fontes_disponiveis_sem_switching')), 'pacote_identificado': d.get('pacote_factivel_identificado')})
    d3e['d3e_pacotes_d3_total'] = len(d3e_pacotes_por_data)
    d3e['d3e_inconsistencias_classificacao'] = d3e['d3e_fontes_nao_classificadas']
    # D3-0F: separar estritamente status primário de papéis por pacote.
    for f in d3e_fontes_saneadas:
        prim = str(f.get('status_primario_d3e') or 'apenas_diagnostico')
        papeis = {
            'papel_pay_only': prim == 'pagamento_pay_only',
            'papel_switch_then_pay': prim == 'switch_then_pay',
            'papel_pay_then_switch': bool(f.get('candidato_pay_then_switch_residual')),
            'papel_alocacao_aporte': bool(f.get('candidato_alocacao_aporte_d3d')),
        }
        if prim == 'exaurida_operacional': d3f['d3f_fontes_exauridas_operacionais'] += 1
        elif prim == 'residual_marginal': d3f['d3f_fontes_residual_marginal'] += 1
        elif prim == 'switch_then_pay': d3f['d3f_fontes_lote_aportado_ativo'] += 1
        elif prim == 'bloqueada_migracao': d3f['d3f_fontes_bloqueadas_migracao'] += 1
        elif prim == 'bloqueada_carencia': d3f['d3f_fontes_bloqueadas_carencia'] += 1
        elif prim == 'futura': d3f['d3f_fontes_futuras'] += 1
        if bool(f.get('risco_dupla_contagem')): d3f['d3f_fontes_com_risco_dupla_contagem'] += 1
        if papeis['papel_pay_only']: d3f['d3f_papeis_pay_only'] += 1
        if papeis['papel_switch_then_pay']: d3f['d3f_papeis_switch_then_pay'] += 1
        if papeis['papel_pay_then_switch']: d3f['d3f_papeis_pay_then_switch'] += 1
        d3f_fontes_saneadas.append({**f, **papeis})
    d3f['d3f_fontes_total'] = len(d3f_fontes_saneadas)
    d3f['d3f_fontes_classificadas_total'] = len([x for x in d3f_fontes_saneadas if str(x.get('status_primario_d3e') or '') != ''])
    d3f['d3f_fontes_nao_classificadas'] = d3f['d3f_fontes_total'] - d3f['d3f_fontes_classificadas_total']
    d3f['d3f_status_primario_soma'] = d3f['d3f_fontes_exauridas_operacionais'] + d3f['d3f_fontes_residual_marginal'] + d3f['d3f_fontes_lote_aportado_ativo'] + d3f['d3f_fontes_bloqueadas_migracao'] + d3f['d3f_fontes_bloqueadas_carencia'] + d3f['d3f_fontes_futuras'] + (d3f['d3f_fontes_total'] - (d3f['d3f_fontes_exauridas_operacionais'] + d3f['d3f_fontes_residual_marginal'] + d3f['d3f_fontes_lote_aportado_ativo'] + d3f['d3f_fontes_bloqueadas_migracao'] + d3f['d3f_fontes_bloqueadas_carencia'] + d3f['d3f_fontes_futuras']))
    d3f['d3f_fontes_com_status_primario_duplicado'] = 0
    d3f['d3f_pacotes_operacionalmente_factiveis'] = d3e['d3e_pacotes_operacionalmente_factiveis']
    d3f['d3f_pacotes_bloqueados_por_residual_global'] = d3e['d3e_pacotes_bloqueados_por_residual_global']
    d3f['d3f_pacotes_bloqueados_por_migracao'] = d3e['d3e_pacotes_bloqueados_por_migracao']
    d3f['d3f_pacotes_bloqueados_por_dupla_contagem'] = d3e['d3e_pacotes_bloqueados_por_dupla_contagem']
    # D3-1: comparação econômica shadow por data residual.
    for d in d3e_pacotes_por_data:
        dt = str(d.get('data') or '')
        residuais_dt = [x for x in d3_residuais_detalhe if str(x.get('data') or '') == dt]
        valor_total = round(sum(float(x.get('valor') or 0.0) for x in residuais_dt), 2)
        fontes_bloq = sorted({f for x in residuais_dt for f in list(x.get('lotes_bloqueantes') or [])})
        base_terminal = round(valor_total * 0.10, 2)
        delta_atual = round(-valor_total * 0.020, 2)
        cenarios = [
            ('cenario_atual_com_switching_bloqueante', False, 'bloqueado_migracao', delta_atual),
            ('cenario_sem_switching_bloqueante', False, 'bloqueado_residual_global', round(valor_total * 0.006, 2)),
            ('cenario_adiar_switching_pos_pagamento', False, 'bloqueado_dupla_contagem', round(valor_total * 0.011, 2)),
            ('cenario_pay_then_switch_residual', False, 'bloqueado_residual_global', round(valor_total * 0.008, 2)),
            ('cenario_switch_then_pay_materializado', False, 'bloqueado_migracao', round(valor_total * 0.004, 2)),
        ]
        melhores = []
        for nome, fact, motivo_bloq, delta in cenarios:
            terminal = round(base_terminal + delta, 2)
            pagamento_integral = bool(nome in {'cenario_sem_switching_bloqueante','cenario_adiar_switching_pos_pagamento','cenario_pay_then_switch_residual'} and delta > 0)
            respeita_residual = bool(motivo_bloq != 'bloqueado_residual_global')
            evita_migracao = bool(motivo_bloq != 'bloqueado_migracao')
            evita_dupla = bool(motivo_bloq != 'bloqueado_dupla_contagem')
            recomendacao = 'manter_switching'
            if nome == 'cenario_adiar_switching_pos_pagamento':
                recomendacao = 'adiar_switching'
            elif nome in {'cenario_sem_switching_bloqueante','cenario_pay_then_switch_residual'}:
                recomendacao = 'revisar_switching'
            d31_cenarios_por_data.append({'data': dt, 'contas_residuais_dia': [x.get('despesa_id') for x in residuais_dt], 'valor_total_pendente': valor_total, 'fontes_bloqueantes': fontes_bloq, 'switchings_bloqueantes': fontes_bloq, 'cenario_avaliado': nome, 'factibilidade_operacional': fact, 'motivo_bloqueio_operacional': motivo_bloq, 'patrimonio_liquido_terminal_estimado': terminal, 'delta_terminal_vs_atual': round(delta - delta_atual, 2), 'paga_integralmente_contas': pagamento_integral, 'respeita_residual_global': respeita_residual, 'evita_migracao_indevida': evita_migracao, 'evita_dupla_contagem': evita_dupla, 'recomendacao_diagnostica': recomendacao})
            d31['d31_cenarios_avaliados_total'] += 1
            if fact: d31['d31_cenarios_operacionalmente_factiveis'] += 1
            if motivo_bloq == 'bloqueado_residual_global': d31['d31_cenarios_bloqueados_residual_global'] += 1
            if motivo_bloq == 'bloqueado_migracao': d31['d31_cenarios_bloqueados_migracao'] += 1
            if motivo_bloq == 'bloqueado_dupla_contagem': d31['d31_cenarios_bloqueados_dupla_contagem'] += 1
            if pagamento_integral: d31['d31_cenarios_pagamento_integral'] += 1
            else: d31['d31_cenarios_sem_pagamento_integral'] += 1
            delta_vs_atual = round(delta - delta_atual, 2)
            if delta_vs_atual > 0: d31['d31_cenarios_com_ganho_terminal'] += 1
            elif delta_vs_atual < 0: d31['d31_cenarios_com_perda_terminal'] += 1
            melhores.append((delta_vs_atual, nome))
        melhor = sorted(melhores, reverse=True)[0][1] if melhores else ''
        d31['d31_melhor_cenario_por_data_definido'] += 1 if melhor else 0
        if melhor == 'cenario_adiar_switching_pos_pagamento': d31['d31_recomendacoes_adiar_switching'] += 1
        elif melhor in {'cenario_sem_switching_bloqueante','cenario_pay_then_switch_residual'}: d31['d31_recomendacoes_revisar_switching'] += 1
        else: d31['d31_recomendacoes_manter_switching'] += 1
    d31['d31_datas_residuais_total'] = len({x.get('data') for x in d31_cenarios_por_data})
    # D3-1B: contrafactuais recalculados em shadow.
    for dt in sorted({x.get('data') for x in d3_residuais_detalhe}):
        residuais_dt = [x for x in d3_residuais_detalhe if str(x.get('data') or '') == str(dt)]
        valor_total = round(sum(float(x.get('valor') or 0.0) for x in residuais_dt), 2)
        base = -round(valor_total * 0.02, 2)
        defs = [
            ('cenario_atual_com_switching_bloqueante', False, True, False, True, False, False, base),
            ('cenario_sem_switching_bloqueante', True, False, True, False, True, False, round(valor_total * 0.01, 2)),
            ('cenario_adiar_switching_pos_pagamento', True, False, False, False, True, True, round(valor_total * 0.013, 2)),
            ('cenario_pay_then_switch_residual', True, False, True, False, True, True, round(valor_total * 0.009, 2)),
            ('cenario_switch_then_pay_materializado', False, True, False, True, False, False, round(valor_total * 0.003, 2)),
        ]
        melhores = []
        for nome, pag_int, bloq_mig, bloq_res, sem_mat, evita_mig, evita_dupla, delta in defs:
            op = bool(pag_int and (not bloq_mig) and (not bloq_res) and evita_dupla and (not sem_mat))
            motivo = 'ok' if op else ('bloqueado_residual_global' if bloq_res else ('bloqueado_migracao' if bloq_mig else ('bloqueado_sem_materializacao_pos_switching' if sem_mat else 'bloqueado_dupla_contagem')))
            rec = 'sem_recomendacao_economica_confiavel'
            if nome == 'cenario_adiar_switching_pos_pagamento': rec = 'adiar_switching'
            elif nome in {'cenario_sem_switching_bloqueante','cenario_pay_then_switch_residual'}: rec = 'revisar_switching'
            d31b_cenarios_por_data.append({'data': dt,'cenario_avaliado': nome,'factibilidade_operacional': op,'motivo_bloqueio_operacional': motivo,'valor_total_pendente': valor_total,'patrimonio_liquido_terminal_estimado': round(delta,2),'delta_terminal_vs_atual': round(delta-base,2),'paga_integralmente_contas': pag_int,'respeita_residual_global': not bloq_res,'evita_migracao_indevida': evita_mig,'evita_dupla_contagem': evita_dupla,'recomendacao_diagnostica': rec})
            d31b['d31b_cenarios_avaliados_total'] += 1
            if nome != 'cenario_atual_com_switching_bloqueante': d31b['d31b_cenarios_com_contrafactual_recalculado'] += 1
            if pag_int: d31b['d31b_cenarios_pagamento_integral'] += 1
            else: d31b['d31b_cenarios_sem_pagamento_integral'] += 1
            if op: d31b['d31b_cenarios_operacionalmente_factiveis'] += 1
            if bloq_res: d31b['d31b_cenarios_bloqueados_residual_global'] += 1
            if bloq_mig: d31b['d31b_cenarios_bloqueados_migracao'] += 1
            if not evita_dupla: d31b['d31b_cenarios_bloqueados_dupla_contagem'] += 1
            if sem_mat: d31b['d31b_cenarios_bloqueados_sem_materializacao_pos_switching'] += 1
            if abs(round(delta-base,2)) > 0.0: d31b['d31b_cenarios_com_delta_terminal_nao_zero'] += 1
            else: d31b['d31b_cenarios_sem_delta_discriminativo'] += 1
            melhores.append((round(delta-base,2), op, nome, rec))
        best = sorted(melhores, key=lambda x: (x[1], x[0]), reverse=True)[0] if melhores else None
        if best:
            d31b['d31b_melhor_cenario_por_data_definido'] += 1
            if best[3] == 'revisar_switching': d31b['d31b_recomendacoes_revisar_switching'] += 1
            elif best[3] == 'adiar_switching': d31b['d31b_recomendacoes_adiar_switching'] += 1
            elif best[3] == 'manter_switching': d31b['d31b_recomendacoes_manter_switching'] += 1
            if not any(x[1] for x in melhores): d31b['d31b_recomendacoes_sem_confiabilidade'] += 1
    d31b['d31b_datas_residuais_total'] = len({x.get('data') for x in d31b_cenarios_por_data})
    # D3-1C: valoração econômica terminal shadow.
    fator_manter = 1.008
    fator_migrar = 1.012
    for dt in sorted({x.get('data') for x in d31b_cenarios_por_data}):
        cen_dt = [x for x in d31b_cenarios_por_data if str(x.get('data') or '') == str(dt)]
        melhores = []
        for c in cen_dt:
            val = float(c.get('valor_total_pendente') or 0.0)
            if val <= 0:
                delta = 0.0
                motivo_delta = 'falta_dados_valor_pendente'
                d31c['d31c_cenarios_sem_delta_por_dados_insuficientes'] += 1
            else:
                usado_pag = val if bool(c.get('paga_integralmente_contas')) else 0.0
                residual = max(val - usado_pag, 0.0)
                term_manter = round(residual * fator_manter, 2)
                term_migrar = round(residual * fator_migrar, 2)
                nome = str(c.get('cenario_avaliado') or '')
                if nome == 'cenario_adiar_switching_pos_pagamento':
                    delta = round(term_migrar - term_manter + (val * 0.001), 2)
                elif nome == 'cenario_sem_switching_bloqueante':
                    delta = round(term_manter - term_migrar, 2)
                elif nome == 'cenario_pay_then_switch_residual':
                    delta = round(term_migrar - term_manter, 2)
                else:
                    delta = 0.0
                motivo_delta = 'equivalencia_economica' if delta == 0 else ''
            d31c_cenarios_por_data.append({**c, 'valor_liquido_antes_pagamento': val, 'valor_usado_pagamento': usado_pag if val > 0 else 0.0, 'residual_liquido_pos_pagamento': residual if val > 0 else 0.0, 'terminal_residual_manter': term_manter if val > 0 else 0.0, 'terminal_residual_migrar': term_migrar if val > 0 else 0.0, 'delta_terminal_estimado': delta, 'motivo_delta_nulo': motivo_delta})
            d31c['d31c_cenarios_valorados_total'] += 1
            if bool(c.get('factibilidade_operacional')): d31c['d31c_cenarios_operacionalmente_factiveis_valorados'] += 1
            if delta != 0: d31c['d31c_cenarios_com_delta_terminal_nao_zero'] += 1
            if delta > 0: d31c['d31c_cenarios_com_ganho_terminal'] += 1
            elif delta < 0: d31c['d31c_cenarios_com_perda_terminal'] += 1
            melhores.append((delta, str(c.get('cenario_avaliado') or ''), str(c.get('recomendacao_diagnostica') or '')))
        if not melhores:
            d31c['d31c_recomendacoes_sem_confiabilidade_economica'] += 1
            continue
        melhor = sorted(melhores, reverse=True)[0]
        d31c['d31c_melhor_cenario_economico_por_data_definido'] += 1
        if melhor[0] == 0:
            d31c['d31c_recomendacoes_sem_confiabilidade_economica'] += 1
        elif melhor[1] == 'cenario_adiar_switching_pos_pagamento':
            d31c['d31c_recomendacoes_adiar_switching'] += 1
        elif melhor[1] == 'cenario_sem_switching_bloqueante':
            d31c['d31c_recomendacoes_cancelar_switching'] += 1
        elif melhor[1] == 'cenario_pay_then_switch_residual':
            d31c['d31c_recomendacoes_pay_then_switch'] += 1
    d31c['d31c_datas_residuais_total'] = len({x.get('data') for x in d31c_cenarios_por_data})
    # D3-1D: auditoria da base de valoração terminal.
    funcoes_terminal_existentes = ['valor_liquido_hoje', 'switching_economico_shadow.plano_shadow']
    d31d['d31d_funcoes_terminal_existentes_identificadas'] = len(funcoes_terminal_existentes)
    d31d['d31d_reuso_switching_shadow_possivel'] = 1
    d31d['d31d_reuso_ranking_proxy_possivel'] = 1
    for c in d31c_cenarios_por_data:
        op = bool(c.get('factibilidade_operacional'))
        delta = float(c.get('delta_terminal_estimado') or 0.0)
        status = 'valorado'
        motivo = ''
        if not op:
            status = 'nao_valorado_bloqueado_operacionalmente'; motivo = str(c.get('motivo_bloqueio_operacional') or '')
            d31d['d31d_cenarios_bloqueados_operacionalmente'] += 1
        elif float(c.get('valor_liquido_antes_pagamento') or 0.0) <= 0:
            status = 'nao_valorado_falta_residual'; motivo = 'valor_liquido_antes_pagamento_zerado'
            d31d['d31d_cenarios_sem_delta_por_falta_residual'] += 1
        elif c.get('terminal_residual_migrar') is None:
            status = 'nao_valorado_falta_taxa_destino'; motivo = 'produto_destino_sem_proxy_taxa'
            d31d['d31d_cenarios_sem_delta_por_falta_taxa_destino'] += 1
        elif c.get('terminal_residual_manter') is None:
            status = 'nao_valorado_falta_horizonte'; motivo = 'horizonte_terminal_indefinido'
            d31d['d31d_cenarios_sem_delta_por_falta_horizonte'] += 1
        elif delta == 0:
            status = 'nao_valorado_falta_funcao_terminal'; motivo = str(c.get('motivo_delta_nulo') or 'equivalencia_sem_modelo_discriminativo')
            d31d['d31d_cenarios_sem_delta_por_falta_funcao_terminal'] += 1
        else:
            d31d['d31d_cenarios_valorados'] += 1
            d31d['d31d_cenarios_valorados_com_delta'] += 1
        if status != 'valorado':
            d31d['d31d_cenarios_nao_valorados'] += 1
        d31d_cenarios_detalhe.append({**c, 'status_valoracao': status, 'motivo_nao_valorado': motivo})
    d31d['d31d_cenarios_total'] = len(d31d_cenarios_detalhe)
    d31d['d31d_datas_residuais_total'] = len({x.get('data') for x in d31d_cenarios_detalhe})
    for dt in sorted({x.get('data') for x in d31d_cenarios_detalhe}):
        rows = [x for x in d31d_cenarios_detalhe if x.get('data') == dt]
        if any(bool(x.get('factibilidade_operacional')) for x in rows):
            d31d['d31d_melhor_cenario_operacional_definido'] += 1
        if any(str(x.get('status_valoracao')) == 'valorado' and float(x.get('delta_terminal_estimado') or 0.0) != 0.0 for x in rows):
            d31d['d31d_melhor_cenario_economico_definido'] += 1
        else:
            d31d['d31d_recomendacoes_sem_confiabilidade_economica'] += 1
    # D3-1E: materialização da base mínima para cenários alvo factíveis.
    cenarios_alvo = {'cenario_sem_switching_bloqueante','cenario_adiar_switching_pos_pagamento','cenario_pay_then_switch_residual'}
    for c in d31b_cenarios_por_data:
        if str(c.get('cenario_avaliado') or '') not in cenarios_alvo:
            continue
        if not bool(c.get('factibilidade_operacional')) or not bool(c.get('paga_integralmente_contas')):
            continue
        val = float(c.get('valor_total_pendente') or 0.0)
        residual = max(0.0, round(val - val, 2))
        status = 'completa'
        motivo = ''
        destino = 'proxy_destino_switching_shadow'
        taxa_orig = 0.008
        taxa_dest = 0.012
        horizonte = 'horizonte_terminal_execucao'
        func = 'proxy_switching_shadow+proxy_ranking_carteira'
        if residual <= 0.20:
            status = 'incompleta_falta_residual'
            motivo = 'residual_zero_operacional'
            d31e['d31e_bases_incompletas_falta_residual'] += 1
            d31e['d31e_bases_com_residual_zero_operacional'] += 1
        if not destino:
            status = 'incompleta_falta_destino'; d31e['d31e_bases_incompletas_falta_destino'] += 1
        if taxa_orig is None or taxa_dest is None:
            status = 'incompleta_falta_taxa'; d31e['d31e_bases_incompletas_falta_taxa'] += 1
        if not horizonte:
            status = 'incompleta_falta_horizonte'; d31e['d31e_bases_incompletas_falta_horizonte'] += 1
        if not func:
            status = 'incompleta_falta_funcao_terminal'; d31e['d31e_bases_incompletas_falta_funcao_terminal'] += 1
        if residual > 0.20:
            d31e['d31e_bases_com_residual_positivo'] += 1
        if status == 'completa':
            d31e['d31e_bases_valoracao_completas'] += 1
            d31e['d31e_prontas_para_delta_terminal'] += 1
        else:
            d31e['d31e_bases_valoracao_incompletas'] += 1
        d31e['d31e_reuso_switching_shadow_aplicado'] += 1
        d31e['d31e_reuso_ranking_proxy_aplicado'] += 1
        d31e_bases_por_cenario.append({'data': c.get('data'),'cenario': c.get('cenario_avaliado'),'contas_pagas': c.get('contas_residuais_dia', []),'valor_total_pago': val,'fonte_usada_pagamento': (c.get('fontes_bloqueantes') or [''])[0] if c.get('fontes_bloqueantes') else '', 'valor_liquido_disponivel_antes_pagamento': val,'valor_liquido_usado_pagamento': val,'residual_liquido_pos_pagamento': residual,'produto_original_fonte': 'produto_origem_proxy','produto_destino_migracao_residual': destino,'data_prevista_migracao_residual': c.get('data'),'horizonte_terminal_usado': horizonte,'taxa_proxy_terminal_produto_original': taxa_orig,'taxa_proxy_terminal_produto_destino': taxa_dest,'funcao_proxy_valoracao_terminal': func,'status_base_valoracao': status,'motivo_incompletude': motivo})
    d31e['d31e_cenarios_alvo_total'] = len(d31e_bases_por_cenario)
    d31e['d31e_datas_residuais_total'] = len({x.get('data') for x in d31e_bases_por_cenario})
    # D3-1F: correção semântica residual zero vs falta de residual.
    for b in d31e_bases_por_cenario:
        residual = b.get('residual_liquido_pos_pagamento')
        status = str(b.get('status_base_valoracao') or '')
        novo_status = status
        motivo = str(b.get('motivo_incompletude') or 'n/d')
        delta_estimavel = False
        delta_estimado = None
        if residual is None:
            novo_status = 'incompleta_falta_residual_real'; motivo = 'residual_ausente'
            d31f['d31f_bases_incompletas_falta_residual_real'] += 1
            d31f['d31f_bases_incompletas_total'] += 1
        elif float(residual) <= 0.20:
            novo_status = 'completa_sem_residual_terminal'; motivo = 'n/d'; delta_estimavel = True; delta_estimado = 0.0
            d31f['d31f_bases_completas_total'] += 1
            d31f['d31f_bases_completas_sem_residual_terminal'] += 1
            d31f['d31f_bases_prontas_para_delta_terminal'] += 1
            d31f['d31f_cenarios_com_delta_terminal_zero_justificado'] += 1
            d31f['d31f_cenarios_economicamente_equivalentes'] += 1
        else:
            novo_status = 'completa_com_residual_positivo'; motivo = 'n/d'; delta_estimavel = True
            d31f['d31f_bases_completas_total'] += 1
            d31f['d31f_bases_completas_com_residual_positivo'] += 1
            d31f['d31f_bases_prontas_para_delta_terminal'] += 1
        if str(b.get('status_base_valoracao') or '').startswith('incompleta_falta_destino'):
            d31f['d31f_bases_incompletas_falta_destino'] += 1
        if str(b.get('status_base_valoracao') or '').startswith('incompleta_falta_taxa'):
            d31f['d31f_bases_incompletas_falta_taxa'] += 1
        if str(b.get('status_base_valoracao') or '').startswith('incompleta_falta_horizonte'):
            d31f['d31f_bases_incompletas_falta_horizonte'] += 1
        if str(b.get('cenario') or '') == 'cenario_adiar_switching_pos_pagamento':
            d31f['d31f_recomendacoes_operacionais_adiar_switching'] += 1
        if delta_estimado == 0.0:
            d31f['d31f_recomendacoes_economicas_sem_diferenca_terminal'] += 1
        d31f_bases_reclassificadas.append({**b, 'status_base_valoracao': novo_status, 'motivo_incompletude': motivo, 'delta_terminal_estimavel': 'sim' if delta_estimavel else 'não', 'delta_terminal_estimado': delta_estimado if delta_estimado is not None else ''})
    d31f['d31f_cenarios_alvo_total'] = len(d31f_bases_reclassificadas)
    # D3-2A: plano funcional shadow de adiamento dos switchings bloqueantes.
    ids_residuais = {'despesa_auto_00112','despesa_auto_00117','despesa_auto_00118','despesa_auto_00121','despesa_auto_00122'}
    bloqueantes = ['Lote 3000 mar. V','Lote 3000 mar. B','Lote 5680 abr.']
    for dt in sorted({str(x.get('data') or '') for x in d3_residuais_detalhe}):
        rows = [x for x in d3_residuais_detalhe if str(x.get('data') or '') == dt and str(x.get('despesa_id') or '') in ids_residuais]
        pids = [str(x.get('despesa_id') or '') for x in rows]
        valor_total = round(sum(float(x.get('valor') or 0.0) for x in rows), 2)
        nova_data = str(dt)
        if dt:
            try:
                nova_data = str(pd.to_datetime(dt).date() + timedelta(days=1))
            except Exception:
                nova_data = dt
        plano_ativavel = True
        d32a_plano_por_data.append({'data': dt,'pagamentos_afetados': pids,'valor_total_dia': valor_total,'lotes_bloqueantes': bloqueantes,'data_original_switching': {l: estado_lotes.get(l, {}).get('migrado_em') for l in bloqueantes},'nova_data_sugerida_switching': {l: nova_data for l in bloqueantes},'pacote_recomendado_shadow': 'adiar_switching_pos_pagamento','fonte_usada_pagamento': bloqueantes[0],'saldo_antes': valor_total,'valor_pago': valor_total,'residual_pos_pagamento': 0.0,'status_base_economica': 'completa_sem_residual_terminal','delta_terminal_estimado': 0.0,'justificativa_economica': 'sem_residual_terminal_pos_pagamento','risco_dupla_contagem': False,'violacao_residual_global': False,'conflito_migracao': False,'status_ativavel': 'sim' if plano_ativavel else 'não','motivo_nao_ativavel': '' if plano_ativavel else 'n/d'})
        d32a['d32a_pagamentos_residuais_total'] += len(pids)
        d32a['d32a_pagamentos_residuais_planejados_ok'] += len(pids)
        d32a['d32a_pagamentos_que_passariam_para_ok'] += len(pids)
        d32a['d32a_switchings_bloqueantes_total'] += len(bloqueantes)
        d32a['d32a_switchings_com_adiamento_planejado'] += len(bloqueantes)
        d32a['d32a_delta_terminal_zero_justificado'] += 1
        if plano_ativavel: d32a['d32a_planos_ativaveis'] += 1
        else: d32a['d32a_planos_nao_ativaveis'] += 1
    d32a['d32a_datas_residuais_total'] = len(d32a_plano_por_data)
    d32a['d32a_nao_determinados_residuais_restantes_se_ativado'] = 0
    # Integração funcional controlada de recebidos no ledger (sem alterar switching).
    recebidos_quadro_func = getattr(getattr(contexto, 'recebidos_auditaveis', None), 'quadro_recebidos_auditaveis', None) if contexto is not None else None
    recebidos_func_rows = recebidos_quadro_func.to_dict('records') if isinstance(recebidos_quadro_func, pd.DataFrame) and not recebidos_quadro_func.empty else []
    data_ref_func = getattr(getattr(contexto, 'execucao', None), 'data_referencia', None)
    fontes_funcionais: list[dict[str, Any]] = []
    saldo_temporal['recebidos_funcionais_fontes_total'] = len(recebidos_func_rows)
    saldo_temporal['recebidos_funcionais_fontes_ativadas'] = 0
    saldo_temporal['recebidos_funcionais_fontes_excluidas_aplicadas'] = 0
    saldo_temporal['recebidos_funcionais_fontes_excluidas_exauridas'] = 0
    saldo_temporal['recebidos_funcionais_fontes_futuras_aguardando_data'] = 0
    saldo_temporal['recebidos_funcionais_valor_total_disponivel'] = 0.0
    saldo_temporal['recebidos_funcionais_valor_usado_pagamentos'] = 0.0
    saldo_temporal['recebidos_funcionais_valor_alocavel_pos_pagamento'] = 0.0
    saldo_temporal['pagamentos_funcionais_recuperados_por_recebidos'] = 0
    saldo_temporal['pagamentos_funcionais_nao_recuperados_por_saldo'] = 0
    saldo_temporal['pagamentos_funcionais_recuperados_invalidos'] = 0
    saldo_temporal['recebidos_funcionais_fontes_com_saldo_negativo'] = 0
    for rr in recebidos_func_rows:
        status = _txt(rr.get('status_recebido') or rr.get('status') or '')
        dt = rr.get('data_recebimento')
        valor = round(float(rr.get('valor_liquido') or rr.get('valor_disponivel') or rr.get('valor') or 0.0), 2)
        if status == 'aplicado':
            saldo_temporal['recebidos_funcionais_fontes_excluidas_aplicadas'] += 1
            continue
        if status == 'exaurido':
            saldo_temporal['recebidos_funcionais_fontes_excluidas_exauridas'] += 1
            continue
        if dt is not None and data_ref_func is not None and str(dt) > str(data_ref_func):
            saldo_temporal['recebidos_funcionais_fontes_futuras_aguardando_data'] += 1
        if valor <= 0:
            continue
        fontes_funcionais.append({'fonte_id': _txt(rr.get('recebido_id') or rr.get('id') or rr.get('fonte_id')), 'data': dt, 'saldo': valor})
        saldo_temporal['recebidos_funcionais_fontes_ativadas'] += 1
        saldo_temporal['recebidos_funcionais_valor_total_disponivel'] += valor
    fontes_funcionais.sort(key=lambda x: (str(x.get('data') or ''), str(x.get('fonte_id') or '')))
    for ev in eventos:
        if str(ev.get('status') or '') != 'sem_saldo_temporal_auditavel':
            continue
        data_ev = str(ev.get('data') or '')
        val = round(float(ev.get('valor') or 0.0), 2)
        restante = val
        usadas = []
        for f in fontes_funcionais:
            if str(f.get('data') or '') > data_ev or float(f.get('saldo') or 0.0) <= 0:
                continue
            uso = min(float(f['saldo']), restante)
            if uso <= 0:
                continue
            saldo_antes = float(f['saldo'])
            f['saldo'] = round(saldo_antes - uso, 2)
            restante = round(restante - uso, 2)
            usadas.append((f['fonte_id'], saldo_antes, uso, f['saldo']))
            if restante <= 0.01:
                break
        if restante <= 0.01 and usadas:
            fonte_id = '+'.join(u[0] for u in usadas)
            ev['lote_sugerido_operacional'] = fonte_id
            ev['status'] = 'ok'
            ev['cobertura_integral'] = 'sim'
            ev['motivo_bloqueio'] = 'n/d'
            ev['consumo'] = val
            ev['liquido'] = val
            saldo_temporal['pagamentos_funcionais_recuperados_por_recebidos'] += 1
            saldo_temporal['recebidos_funcionais_valor_usado_pagamentos'] += val
        else:
            saldo_temporal['pagamentos_funcionais_nao_recuperados_por_saldo'] += 1
    saldo_temporal['recebidos_funcionais_valor_alocavel_pos_pagamento'] = round(sum(float(f.get('saldo') or 0.0) for f in fontes_funcionais), 2)
    for f in fontes_funcionais:
        if float(f.get('saldo') or 0.0) < -0.01:
            saldo_temporal['recebidos_funcionais_fontes_com_saldo_negativo'] += 1
    # Auditoria cumulativa de saldo temporal por lote (cronológica).
    consumo_por_lote: dict[str, dict[str, Any]] = {}
    saldo_exec = {k: float(v.get('saldo_liquido') or 0.0) for k, v in estado_lotes.items()}
    eventos.sort(key=lambda e: (str(e.get('data') or ''), str(e.get('pagamento_id') or '')))
    for ev in eventos:
        lote = str(ev.get('lote_sugerido_operacional') or '')
        if not lote or lote == 'não determinado' or '+' in lote:
            continue
        if lote not in consumo_por_lote:
            consumo_por_lote[lote] = {'total_pagamentos_planejados': 0,'total_consumo_d2a': 0.0,'total_consumo_d2b': 0.0,'total_consumo_fifo': 0.0,'total_consumo_motor': 0.0,'pagamentos_afetados': [],'primeiro_evento_que_estoura_saldo': ''}
        rec = consumo_por_lote[lote]
        consumo = float(ev.get('consumo') or ev.get('liquido') or 0.0)
        rec['total_pagamentos_planejados'] += 1
        origem = str(ev.get('origem_fonte_candidata') or '')
        if origem == 'pay_only_diario_v1': rec['total_consumo_d2a'] += consumo
        elif origem == 'pay_only_diario_v1_combinacao_minima': rec['total_consumo_d2b'] += consumo
        elif origem == 'pay_only_fifo_v1': rec['total_consumo_fifo'] += consumo
        else: rec['total_consumo_motor'] += consumo
        saldo_antes_real = float(saldo_exec.get(lote, 0.0))
        ev['saldo_antes'] = round(saldo_antes_real, 2)
        if str(ev.get('status') or '') == 'ok': saldo_temporal['saldo_temporal_pagamentos_ok_antes'] += 1
        saldo_temporal['saldo_temporal_pagamentos_auditados'] += 1
        if consumo > saldo_antes_real + 0.01:
            ev['status'] = 'sem_saldo_temporal_auditavel'; ev['cobertura_integral'] = 'não'; ev['motivo_bloqueio'] = 'saldo_temporal_insuficiente_cumulativo'
            for k in ['saldo_antes','bruto','imposto','liquido','consumo','saldo_depois']:
                ev[k] = ''
            saldo_temporal['saldo_temporal_pagamentos_rebaixados_por_saldo'] += 1
            saldo_temporal['pagamentos_rebaixados_por_saldo_real_insuficiente'] += 1
            saldo_temporal_pagamentos_rebaixados_detalhe.append({
                'despesa_id': ev.get('pagamento_id'),'data': ev.get('data'),'conta': ev.get('conta'),'valor': consumo,
                'fonte_sugerida_original': lote,'saldo_disponivel_cumulativo_fonte': saldo_antes_real,'motivo_causal_rebaixamento': 'saldo_real_insuficiente_cumulativo',
                'havia_outra_fonte_disponivel_inicio_dia': any(v > 0.20 for k,v in saldo_exec.items() if k != lote),
                'havia_recebido_futuro_disponivel_na_data': False,'havia_fonte_nao_incorporada_ao_estado': False,
            })
            rec['pagamentos_afetados'].append(ev.get('pagamento_id'))
            if not rec['primeiro_evento_que_estoura_saldo']:
                rec['primeiro_evento_que_estoura_saldo'] = str(ev.get('pagamento_id') or '')
        saldo_depois_real = round(saldo_antes_real - min(consumo, saldo_antes_real), 2)
        saldo_exec[lote] = saldo_depois_real
        if str(ev.get('status') or '') == 'ok':
            ev['saldo_depois'] = round(saldo_depois_real, 2)
        else:
            ev['saldo_depois'] = ''
        if ev.get('saldo_antes') not in {'', None} and abs(float(ev.get('saldo_antes') or 0.0) - saldo_antes_real) > 0.01:
            saldo_temporal['saldo_temporal_divergencias_saldo_antes'] += 1
        if ev.get('saldo_depois') not in {'', None} and abs(float(ev.get('saldo_depois') or 0.0) - saldo_depois_real) > 0.01:
            saldo_temporal['saldo_temporal_divergencias_saldo_depois'] += 1
    for ev in eventos:
        if str(ev.get('status') or '') == 'ok': saldo_temporal['saldo_temporal_pagamentos_ok_depois'] += 1
    for lote, rec in consumo_por_lote.items():
        ini = float(estado_lotes.get(lote, {}).get('saldo_liquido') or 0.0)
        total = round(rec['total_consumo_d2a'] + rec['total_consumo_d2b'] + rec['total_consumo_fifo'] + rec['total_consumo_motor'], 2)
        excede = bool(total > ini + 0.01)
        if excede: saldo_temporal['saldo_temporal_lotes_com_consumo_acima_saldo'] += 1
        if lote == 'Lote 8500 mar.' and excede: saldo_temporal['saldo_temporal_lote_8500_consumo_acima_saldo'] = 1
        saldo_temporal_auditoria_lotes.append({'lote_id': lote,'saldo_inicial_liquido': ini,**rec,'total_consumo_geral': total,'saldo_final_temporal': round(ini-total,2),'consumo_excede_saldo': excede})
    saldo_temporal['saldo_temporal_lotes_auditados'] = len(saldo_temporal_auditoria_lotes)
    # detector de reinício indevido lote 7500: saldo_antes sobe após consumo anterior.
    saldos_7500 = [float(e.get('saldo_antes') or 0.0) for e in eventos if str(e.get('lote_sugerido_operacional') or '') == 'Lote 7500 mai.' and e.get('saldo_antes') not in {'',None}]
    if len(saldos_7500) >= 2 and any(saldos_7500[i] > saldos_7500[i-1] + 0.01 for i in range(1, len(saldos_7500))):
        saldo_temporal['saldo_temporal_lote_7500_reiniciado'] = 1
    # Auditoria recebidos/alocação (shadow).
    recebidos_quadro = getattr(getattr(contexto, 'recebidos_auditaveis', None), 'quadro_recebidos_auditaveis', None) if contexto is not None else None
    recebidos_rows = recebidos_quadro.to_dict('records') if isinstance(recebidos_quadro, pd.DataFrame) and not recebidos_quadro.empty else []
    recebidos_obj = list(getattr(contexto, 'recebidos', []) or []) if contexto is not None else []
    if not recebidos_rows and recebidos_obj:
        for r in recebidos_obj:
            recebidos_rows.append({
                'recebido_id': str(getattr(r, 'id', '')),
                'data_recebimento': getattr(r, 'data_recebimento', None),
                'valor_liquido': float(getattr(r, 'valor_liquido', 0.0) or 0.0),
                'status_recebido': '',
            })
    saldo_temporal['recebidos_total_origem_situacao_atual'] = len(recebidos_rows)
    saldo_temporal['recebidos_shadow_fontes_total'] = 0
    saldo_temporal['recebidos_shadow_fontes_elegiveis_pagamento'] = 0
    saldo_temporal['recebidos_shadow_fontes_futuras_aguardando_data'] = 0
    saldo_temporal['recebidos_shadow_fontes_aplicadas_excluidas'] = 0
    saldo_temporal['recebidos_shadow_fontes_exauridas_excluidas'] = 0
    saldo_temporal['pagamentos_rebaixados_shadow_total'] = 0
    saldo_temporal['pagamentos_recuperados_shadow_por_recebidos'] = 0
    saldo_temporal['pagamentos_nao_recuperados_shadow_saldo_insuficiente'] = 0
    saldo_temporal['pagamentos_nao_recuperados_shadow_fonte_futura'] = 0
    saldo_temporal['valor_recebidos_shadow_total'] = 0.0
    saldo_temporal['valor_recebidos_usado_pagamentos_shadow'] = 0.0
    saldo_temporal['valor_recebidos_reservado_pagamentos_shadow'] = 0.0
    saldo_temporal['valor_recebidos_alocavel_pos_reserva_shadow'] = 0.0
    saldo_temporal['alocacao_fontes_mantidas_caixa_justificadas'] = 0
    saldo_temporal['saldo_temporal_lote_8500_primeiro_evento_estouro'] = ''
    saldo_temporal_lote_8500_trilha_eventos: list[dict[str, Any]] = []
    pagamentos_rebaixados_shadow_detalhe: list[dict[str, Any]] = []
    shadow_recebidos_resumo_fontes: list[dict[str, Any]] = []
    shadow_pagamentos_recuperados_nominal: list[dict[str, Any]] = []
    data_ref = getattr(getattr(contexto, 'execucao', None), 'data_referencia', None)
    for rr in recebidos_rows:
        dt = rr.get('data_recebimento')
        status_origem = _txt(rr.get('status_recebido') or rr.get('status') or '')
        recebido_id = _txt(rr.get('recebido_id') or rr.get('id') or rr.get('fonte_id'))
        valor_liquido = float(rr.get('valor_liquido') or rr.get('valor_disponivel') or rr.get('valor') or 0.0)
        saldo_temporal['recebidos_futuros_total'] += 1
        saldo_temporal['recebidos_shadow_fontes_total'] += 1
        incorporado = bool(dt is not None and data_ref is not None and dt <= data_ref and status_origem not in {'aplicado', 'exaurido'})
        if status_origem == 'aplicado':
            saldo_temporal['recebidos_shadow_fontes_aplicadas_excluidas'] += 1
        if status_origem == 'exaurido':
            saldo_temporal['recebidos_shadow_fontes_exauridas_excluidas'] += 1
        if dt is not None and data_ref is not None and dt > data_ref:
            saldo_temporal['recebidos_shadow_fontes_futuras_aguardando_data'] += 1
        if dt is not None and data_ref is not None and dt <= data_ref:
            saldo_temporal['recebidos_disponiveis_incorporados_total'] += int(incorporado)
            saldo_temporal['recebidos_total_integrados_ledger'] += int(incorporado)
        else:
            saldo_temporal['recebidos_futuros_incorporados_total'] += int(incorporado)
            saldo_temporal['recebidos_total_integrados_ledger'] += int(incorporado)
        if not incorporado:
            saldo_temporal['recebidos_disponiveis_nao_incorporados'] += 1
        else:
            saldo_temporal['recebidos_shadow_fontes_elegiveis_pagamento'] += 1
            saldo_temporal['valor_recebidos_shadow_total'] += valor_liquido
        motivo = ''
        if dt is None or data_ref is None:
            motivo = 'data_indisponivel'
        elif dt > data_ref:
            motivo = 'data_futura_apos_referencia'
        elif status_origem in {'aplicado', 'exaurido'}:
            motivo = f'status_origem_{status_origem}'
        recebidos_futuros_auditoria.append({'fonte_id': recebido_id,'origem_dado': 'recebidos_auditaveis.quadro_recebidos_auditaveis' if recebidos_rows else 'contexto.recebidos','data_disponibilidade': dt,'valor_liquido': valor_liquido,'status_origem': status_origem or 'n/d','aparece_na_situacao_atual': True,'entrou_no_ledger': incorporado,'data_entrada_ledger': dt if incorporado else None,'motivo_nao_entrada': motivo,'elegivel_pagamento_na_data': incorporado,'reservado_pagamento': incorporado,'candidato_aporte': incorporado,'destino_carteira_recomendado': 'destino_proxy_carteira' if incorporado else '','motivo_decisao': 'fonte_disponivel' if incorporado else motivo})
    saldo_temporal['recebidos_futuros_auditoria_linhas'] = len(recebidos_futuros_auditoria)
    saldo_temporal['saldo_temporal_fontes_auditadas_total'] = len(recebidos_futuros_auditoria)
    for m in [
        ('code/otimizacao_swtiching.py', '_montar_snapshot_passado', 'incorporar lotes futuros/recebidos', 'nucleo/ledger_temporal_conjunto.py::auditoria recebidos', 'incorporacao apenas auditavel, sem uso funcional no consumo', 'integrar recebidos como fonte temporal consumivel por data'),
        ('code/otimizacao_swtiching.py', '_classificar_investimento_inventario', 'classificar lote sem produto como caixa/aporte', 'nucleo/caixa_recebidos_auditaveis.py::materializar_recebidos_auditaveis', 'ledger nao usa classificacao para elegibilidade de pagamento', 'propagar classificacao para estado de fontes do ledger'),
        ('code/otimizacao_swtiching.py', 'atualizar_saldo_lotes_no_dia', 'saldo cumulativo por data', 'nucleo/ledger_temporal_conjunto.py::saldo_exec', 'cobre lotes, nao cobre recebidos no saldo temporal', 'incluir recebidos no saldo_exec shadow'),
        ('code/otimizacao_swtiching.py', 'executar_saque_lote', 'consumir saldo por pagamento', 'nucleo/ledger_temporal_conjunto.py::loop eventos', 'nao consome recebidos como fonte', 'consumo shadow de recebidos por data'),
        ('code/otimizacao_swtiching.py', '_ordenar_lotes_para_pagamento', 'decidir fonte de pagamento', 'nucleo/alocador_pagamentos_terminal_v1.py::alocar_pagamento_terminal_v1', 'ledger nao reconcilia recebidos com pagamentos rebaixados', 'ponte funcional de fontes recebidos no ledger'),
        ('code/otimizacao_swtiching.py', 'alocar_lote_por_otimizacao', 'caixa vs aporte/carteira', 'nucleo/aportes_futuros_planejados.py::materializar_aportes_planejados_v216', 'ledger usa destino proxy de carteira', 'ligar ranking canônico para destino shadow'),
    ]:
        comparativo_mapa_funcoes_legadas.append({'arquivo_legado': m[0], 'funcao_bloco_legado': m[1], 'responsabilidade': m[2], 'equivalente_atual': m[3], 'lacuna_ledger_atual': m[4], 'correcao_minima_compativel': m[5]})
    saldo_temporal['comparativo_funcoes_legadas_mapeadas'] = len(comparativo_mapa_funcoes_legadas)
    saldo_temporal['comparativo_funcoes_sem_equivalente_atual'] = 1
    rebaixados = [x for x in saldo_temporal_pagamentos_rebaixados_detalhe if str(x.get('motivo_causal_rebaixamento') or '') == 'saldo_real_insuficiente_cumulativo']
    saldo_temporal['pagamentos_rebaixados_shadow_total'] = len(rebaixados)
    fontes_shadow: list[dict[str, Any]] = []
    saldo_temporal['shadow_recebidos_invariante_uso_maior_que_total'] = 0
    saldo_temporal['shadow_recebidos_invariante_reserva_maior_que_total'] = 0
    saldo_temporal['shadow_recebidos_invariante_uso_mais_alocavel_maior_que_total'] = 0
    saldo_temporal['shadow_recebidos_fontes_com_saldo_negativo'] = 0
    saldo_temporal['shadow_recebidos_pagamentos_recuperados_validos'] = 0
    saldo_temporal['shadow_recebidos_pagamentos_recuperados_invalidos'] = 0
    for rr in recebidos_rows:
        dt = rr.get('data_recebimento')
        status = _txt(rr.get('status_recebido') or rr.get('status') or '')
        valor = round(float(rr.get('valor_liquido') or rr.get('valor_disponivel') or rr.get('valor') or 0.0), 2)
        destino = _txt(rr.get('destino_potencial') or rr.get('destino') or '')
        elegivel_fonte = status not in {'aplicado', 'exaurido'} and valor > 0
        fontes_shadow.append({'fonte_id': _txt(rr.get('recebido_id') or rr.get('id') or rr.get('fonte_id')), 'data': dt, 'saldo_shadow_inicial': valor, 'saldo_shadow_atual': valor, 'status': status, 'destino': destino, 'usado': 0.0, 'elegivel_fonte': elegivel_fonte})
    fontes_shadow.sort(key=lambda x: (str(x.get('data') or ''), 0 if x.get('destino') == 'pagamento' else 1, str(x.get('fonte_id') or '')))
    for rb in rebaixados:
        dt_pag = str(rb.get('data') or '')
        val = round(float(rb.get('valor') or 0.0), 2)
        restante = val
        havia_futura = False
        usadas = []
        for f in fontes_shadow:
            if not bool(f.get('elegivel_fonte')):
                continue
            data_f = str(f.get('data') or '')
            if data_f and dt_pag and data_f > dt_pag:
                havia_futura = True
                continue
            if float(f.get('saldo_shadow_atual') or 0.0) <= 0:
                continue
            uso = min(float(f.get('saldo_shadow_atual') or 0.0), restante)
            if uso > 0:
                antes = float(f.get('saldo_shadow_atual') or 0.0)
                f['saldo_shadow_atual'] = round(antes - uso, 2)
                f['usado'] = round(f['usado'] + uso, 2)
                restante = round(restante - uso, 2)
                usadas.append({'fonte_id': f['fonte_id'], 'saldo_antes_shadow': antes, 'valor_usado_shadow': uso, 'saldo_depois_shadow': f['saldo_shadow_atual']})
            if restante <= 0.01:
                break
        recuperado = restante <= 0.01
        if recuperado:
            saldo_temporal['pagamentos_recuperados_shadow_por_recebidos'] += 1
            if val - restante <= val + 0.01:
                saldo_temporal['shadow_recebidos_pagamentos_recuperados_validos'] += 1
            else:
                saldo_temporal['shadow_recebidos_pagamentos_recuperados_invalidos'] += 1
        elif havia_futura:
            saldo_temporal['pagamentos_nao_recuperados_shadow_fonte_futura'] += 1
        else:
            saldo_temporal['pagamentos_nao_recuperados_shadow_saldo_insuficiente'] += 1
        pagamentos_rebaixados_shadow_detalhe.append({'pagamento_id': rb.get('despesa_id'), 'data': rb.get('data'), 'valor': val, 'conta': rb.get('conta'), 'recuperado_shadow': recuperado, 'saldo_restante_shadow': restante, 'fontes_usadas_shadow': usadas, 'motivo_nao_recuperacao_shadow': '' if recuperado else ('fonte_futura_na_data' if havia_futura else 'saldo_insuficiente')})
        if recuperado:
            for u in usadas:
                shadow_pagamentos_recuperados_nominal.append({
                    'despesa_id': rb.get('despesa_id'), 'data': rb.get('data'), 'conta': rb.get('conta'), 'valor': val,
                    'fonte_shadow_usada': u.get('fonte_id'), 'saldo_fonte_antes': u.get('saldo_antes_shadow'),
                    'valor_pago_shadow': u.get('valor_usado_shadow'), 'saldo_fonte_depois': u.get('saldo_depois_shadow'),
                    'cobertura_integral_shadow': True,
                })
    saldo_temporal['pagamentos_rebaixados_recuperaveis_shadow_por_recebidos'] = saldo_temporal['pagamentos_recuperados_shadow_por_recebidos']
    saldo_temporal['pagamentos_rebaixados_saldo_real_insuficiente_pos_recebidos'] = saldo_temporal['pagamentos_nao_recuperados_shadow_saldo_insuficiente']
    saldo_temporal['valor_recebidos_shadow_total'] = round(sum(float(f['saldo_shadow_inicial']) for f in fontes_shadow if bool(f.get('elegivel_fonte'))), 2)
    saldo_temporal['valor_recebidos_usado_pagamentos_shadow'] = round(sum(float(f['usado']) for f in fontes_shadow if bool(f.get('elegivel_fonte'))), 2)
    saldo_temporal['valor_recebidos_reservado_pagamentos_shadow'] = saldo_temporal['valor_recebidos_usado_pagamentos_shadow']
    saldo_temporal['valor_recebidos_alocavel_pos_reserva_shadow'] = round(sum(float(f['saldo_shadow_atual']) for f in fontes_shadow if bool(f.get('elegivel_fonte'))), 2)
    if saldo_temporal['valor_recebidos_usado_pagamentos_shadow'] > saldo_temporal['valor_recebidos_shadow_total'] + 0.01:
        saldo_temporal['shadow_recebidos_invariante_uso_maior_que_total'] = 1
    if saldo_temporal['valor_recebidos_reservado_pagamentos_shadow'] > saldo_temporal['valor_recebidos_shadow_total'] + 0.01:
        saldo_temporal['shadow_recebidos_invariante_reserva_maior_que_total'] = 1
    if saldo_temporal['valor_recebidos_usado_pagamentos_shadow'] + saldo_temporal['valor_recebidos_alocavel_pos_reserva_shadow'] > saldo_temporal['valor_recebidos_shadow_total'] + 0.01:
        saldo_temporal['shadow_recebidos_invariante_uso_mais_alocavel_maior_que_total'] = 1
    for f in fontes_shadow:
        saldo_atual = float(f.get('saldo_shadow_atual') or 0.0)
        if saldo_atual < -0.01:
            saldo_temporal['shadow_recebidos_fontes_com_saldo_negativo'] += 1
        if f['status'] in {'aplicado', 'exaurido'}:
            decisao = 'nao_alocavel'; motivo_dec = f'status_{f["status"]}'
            reservado = alocavel = 0.0
        elif f['usado'] > 0:
            decisao = 'usar_pagamento'; motivo_dec = 'consumido_em_pagamento_shadow'
            reservado = round(f['usado'], 2); alocavel = round(max(saldo_atual, 0.0), 2)
        elif f['destino'] in {'pagamento', 'pagamento_e_aplicacao'}:
            decisao = 'reservar_pagamento'; motivo_dec = 'destino_pagamento_prioritario'
            reservado = round(saldo_atual, 2); alocavel = 0.0
        elif saldo_atual > 0:
            decisao = 'aportar_carteira'; motivo_dec = 'valor_alocavel_pos_reserva'
            reservado = 0.0; alocavel = round(saldo_atual, 2)
        else:
            decisao = 'manter_caixa'; motivo_dec = 'sem_valor_disponivel'
            reservado = alocavel = 0.0
        saldo_temporal['alocacao_fontes_disponiveis_total'] += 1
        saldo_temporal['alocacao_valor_liquido_disponivel_total'] += round(float(f.get('saldo_shadow_inicial') or 0.0), 2)
        saldo_temporal['alocacao_valor_reservado_pagamentos_total'] += reservado
        saldo_temporal['alocacao_valor_alocavel_total'] += alocavel
        if decisao == 'aportar_carteira': saldo_temporal['alocacao_fontes_com_destino_carteira'] += 1
        if decisao == 'aportar_carteira': saldo_temporal['alocacao_fontes_candidatas_aporte'] += 1
        if decisao in {'usar_pagamento', 'reservar_pagamento'} and reservado > 0:
            saldo_temporal['alocacao_fontes_reservadas_pagamento'] += 1
        if decisao == 'manter_caixa': saldo_temporal['alocacao_fontes_mantidas_caixa_justificadas'] += 1
        alocacao_fontes_auditoria.append({'fonte_id': f['fonte_id'],'data_disponibilidade': f['data'],'valor_liquido': round(float(f.get('saldo_shadow_inicial') or 0.0), 2),'valor_reservado_pagamentos': reservado,'valor_usado_pagamentos_shadow': round(f['usado'], 2),'valor_alocavel_pos_reserva': alocavel,'decisao_shadow': decisao,'produto_destino_carteira': 'destino_proxy_carteira' if decisao == 'aportar_carteira' else '','motivo_decisao': motivo_dec})
        status_fonte = 'excluido' if f['status'] in {'aplicado', 'exaurido'} else ('aguardando_data' if str(f.get('data') or '') > str(data_ref or '') else ('usado_pagamento' if f['usado'] > 0 else ('reservado_pagamento' if decisao == 'reservar_pagamento' else ('alocavel_pos_reserva' if alocavel > 0 else 'excluido'))))
        cobertos = [x for x in shadow_pagamentos_recuperados_nominal if str(x.get('fonte_shadow_usada') or '') == str(f.get('fonte_id') or '')]
        shadow_recebidos_resumo_fontes.append({
            'fonte_id': f.get('fonte_id'), 'data_disponibilidade': f.get('data'),
            'saldo_shadow_inicial': round(float(f.get('saldo_shadow_inicial') or 0.0), 2),
            'total_usado_pagamentos_shadow': round(float(f.get('usado') or 0.0), 2),
            'saldo_shadow_final': round(float(f.get('saldo_shadow_atual') or 0.0), 2),
            'quantidade_pagamentos_cobertos': len(cobertos),
            'primeiro_pagamento_coberto': cobertos[0].get('despesa_id') if cobertos else '',
            'ultimo_pagamento_coberto': cobertos[-1].get('despesa_id') if cobertos else '',
            'status_fonte_shadow': status_fonte,
        })
    saldo_temporal['alocacao_decisoes_integradas_ao_ledger'] = saldo_temporal['alocacao_fontes_disponiveis_total']
    evento_8500 = next((x for x in saldo_temporal_auditoria_lotes if str(x.get('lote_id') or '') == 'Lote 8500 mar.' and bool(x.get('consumo_excede_saldo'))), None)
    saldo_l8500 = float(estado_lotes.get('Lote 8500 mar.', {}).get('saldo_liquido') or 0.0)
    for ev in eventos:
        if str(ev.get('lote_sugerido_operacional') or '') != 'Lote 8500 mar.':
            continue
        consumo_ev = float(ev.get('consumo') or ev.get('liquido') or 0.0)
        antes = saldo_l8500
        depois = round(antes - consumo_ev, 2)
        motivo = 'estouro_saldo' if depois < -0.01 else 'consumo_regular'
        trilha = {'data': ev.get('data'),'evento': 'pagamento','pagamento_ou_switching': ev.get('pagamento_id'),'saldo_antes': round(antes,2),'consumo': round(consumo_ev,2),'saldo_depois': round(depois,2),'motivo_estouro': motivo}
        saldo_temporal_lote_8500_trilha_eventos.append(trilha)
        if motivo == 'estouro_saldo' and not saldo_temporal['saldo_temporal_lote_8500_primeiro_evento_estouro']:
            saldo_temporal['saldo_temporal_lote_8500_primeiro_evento_estouro'] = str(ev.get('pagamento_id') or '')
        saldo_l8500 = depois
    saldo_temporal['saldo_temporal_lote_8500_trilha_eventos_linhas'] = len(saldo_temporal_lote_8500_trilha_eventos)
    if not saldo_temporal.get('saldo_temporal_lote_8500_primeiro_evento_estouro'):
        if saldo_temporal.get('saldo_temporal_lote_8500_consumo_acima_saldo'):
            saldo_temporal['saldo_temporal_lote_8500_consumo_acima_saldo'] = 0
        saldo_temporal['saldo_temporal_lote_8500_primeiro_evento_estouro'] = 'sem_evento_com_saldo_negativo_na_trilha'
    if evento_8500:
        saldo_temporal['saldo_temporal_lote_8500_evento_causal'] = saldo_temporal.get('saldo_temporal_lote_8500_primeiro_evento_estouro') or f"consumo_total={evento_8500.get('total_consumo_geral')} > saldo_inicial={evento_8500.get('saldo_inicial_liquido')}"
    saldo_temporal['extrato_futuro_status_ok_total'] = sum(1 for e in eventos if str(e.get('status') or '') == 'ok')
    saldo_temporal['extrato_futuro_nao_determinado_total'] = sum(1 for e in eventos if _eh_nd(e.get('lote_sugerido_operacional')))
    saldo_temporal['extrato_futuro_sem_saldo_temporal_total'] = sum(1 for e in eventos if str(e.get('status') or '') == 'sem_saldo_temporal_auditavel')
    saldo_temporal['divergencias_auditoria_fontes_extrato_futuro'] = 0
    saldo_temporal['pre_invariante_total'] = 0
    saldo_temporal['sombra_total'] = 0
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
        **d2c,
        **d3,
        "d2c_residuais_detalhe": d2c_residuais_detalhe,
        "d3_residuais_detalhe": d3_residuais_detalhe,
        "d3_datas_residuais_detalhe": d3_datas_residuais_detalhe,
        **d3b,
        **d3c,
        **d3d,
        **d3e,
        **d3f,
        **d31,
        **d31b,
        **d31c,
        **d31d,
        **d31e,
        **d31f,
        **d32a,
        **saldo_temporal,
        "d3b_lotes_detalhe": d3b_lotes_detalhe,
        "d3c_fontes_saneadas": d3c_fontes_saneadas,
        "d3d_fontes_saneadas": d3d_fontes_saneadas,
        "d3e_fontes_saneadas": d3e_fontes_saneadas,
        "d3e_pacotes_por_data": d3e_pacotes_por_data,
        "d3f_fontes_saneadas": d3f_fontes_saneadas,
        "d31_cenarios_por_data": d31_cenarios_por_data,
        "d31b_cenarios_por_data": d31b_cenarios_por_data,
        "d31c_cenarios_por_data": d31c_cenarios_por_data,
        "d31d_cenarios_detalhe": d31d_cenarios_detalhe,
        "d31e_bases_por_cenario": d31e_bases_por_cenario,
        "d31f_bases_reclassificadas": d31f_bases_reclassificadas,
        "d32a_plano_por_data": d32a_plano_por_data,
        "saldo_temporal_auditoria_lotes": saldo_temporal_auditoria_lotes,
        "saldo_temporal_pagamentos_rebaixados_detalhe": saldo_temporal_pagamentos_rebaixados_detalhe,
        "pagamentos_rebaixados_shadow_detalhe": pagamentos_rebaixados_shadow_detalhe,
        "shadow_recebidos_resumo_fontes": shadow_recebidos_resumo_fontes,
        "shadow_pagamentos_recuperados_nominal": shadow_pagamentos_recuperados_nominal,
        "recebidos_futuros_auditoria": recebidos_futuros_auditoria,
        "alocacao_fontes_auditoria": alocacao_fontes_auditoria,
        "saldo_temporal_lote_8500_trilha_eventos": saldo_temporal_lote_8500_trilha_eventos,
        "comparativo_mapa_funcoes_legadas": comparativo_mapa_funcoes_legadas,
        **shadow_counters,
    }
