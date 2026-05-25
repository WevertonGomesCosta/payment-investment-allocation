"""Ledger temporal conjunto mínimo para Extrato Futuro.

Esta camada consolida eventos canônicos (pagamento + switching) sem recalcular
resgates, impostos ou saldos em camada de saída.
"""
from __future__ import annotations

from typing import Any
from datetime import timedelta

import pandas as pd
from nucleo.calendario_financeiro import proximo_dia_util_bancario_em_ou_apos
from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2


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


def _extrair_lotes_compostos(v: Any) -> list[str]:
    txt = _txt(v)
    if not txt:
        return []
    lotes = [_txt(p) for p in txt.split('+')]
    return [x for x in lotes if x and not _eh_nd(x)]


def _primeira_data_valida_em_ordem(row: dict[str, Any], colunas: list[str]) -> Any:
    for col in colunas:
        v = row.get(col)
        if _normalizar_data_comparavel(v) is not None:
            return v
    return None


def _mapa_switchings_aba_operacional_legado_v37s(contexto: Any) -> dict[str, dict[str, Any]]:
    pacote_planilha = getattr(contexto, 'pacote_planilha', None) if contexto is not None else None
    quadros_brutos = getattr(pacote_planilha, 'quadros_brutos', {}) if pacote_planilha is not None else {}
    df = quadros_brutos.get('Switching') if isinstance(quadros_brutos, dict) else None
    if not isinstance(df, pd.DataFrame):
        return {}
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}
    mapa: dict[str, dict[str, Any]] = {}
    for _, row in df.iterrows():
        r = row.to_dict()
        lote = _txt(r.get('Lote (ID) Antes') or r.get('Lote') or r.get('Lote origem') or r.get('Lote Origem') or r.get('lote_origem') or r.get('lote_id'))
        if not lote:
            continue
        data_sw = _primeira_data_valida_em_ordem(
            r,
            ['Data Aplicação', 'Data', 'Data switching', 'data_switching', 'data_operacional', 'Data operação', 'Data Recebimento'],
        )
        if _normalizar_data_comparavel(data_sw) is None:
            continue
        meta = {
            'lote_origem': lote,
            'data_switching': data_sw,
            'produto_destino': _txt(r.get('Investimento') or r.get('Destino') or r.get('Produto destino') or r.get('produto_destino')),
            'valor_liquido_origem': _round(r.get('Valor Líquido Migrado') or r.get('Valor líquido origem') or r.get('valor_liquido_origem')),
            'status_switching': 'classificado_promovido',
            'origem_mapa_migracao': 'aba_switching_operacional',
            'lote_pos_switching': _txt(r.get('Lote (ID) Depois') or r.get('lote_pos_switching')),
        }
        atual = mapa.get(lote)
        if atual is None or _normalizar_data_comparavel(meta.get('data_switching')) > _normalizar_data_comparavel(atual.get('data_switching')):
            mapa[lote] = meta
    return mapa


def _eventos_switching_aba_operacional_legado_v37s(contexto: Any) -> list[dict[str, Any]]:
    pacote_planilha = getattr(contexto, 'pacote_planilha', None) if contexto is not None else None
    quadros_brutos = getattr(pacote_planilha, 'quadros_brutos', {}) if pacote_planilha is not None else {}
    df = quadros_brutos.get('Switching') if isinstance(quadros_brutos, dict) else None
    if not isinstance(df, pd.DataFrame):
        return []
    eventos: list[dict[str, Any]] = []
    for i, row in df.iterrows():
        r = row.to_dict()
        lote_origem = _txt(r.get('Lote (ID) Antes') or r.get('lote_origem') or r.get('lote_id'))
        if not lote_origem:
            continue
        data_sw = _primeira_data_valida_em_ordem(r, ['Data Aplicação', 'Data', 'Data Recebimento'])
        if _normalizar_data_comparavel(data_sw) is None:
            continue
        lote_destino = _txt(r.get('Lote (ID) Depois') or r.get('lote_pos_switching'))
        eventos.append({
            'evento_switching_id': _txt(r.get('evento_switching_id')) or f"swop::{_normalizar_data_comparavel(data_sw)}::{lote_origem}::{lote_destino or i}",
            'lote_origem': lote_origem,
            'data_switching': _normalizar_data_comparavel(data_sw),
            'produto_destino': _txt(r.get('Investimento') or r.get('produto_destino')),
            'valor_liquido_origem': _round(r.get('Valor Líquido Migrado') or r.get('valor_liquido_origem')),
            'lote_pos_switching': lote_destino or f"lote_pos_switching_audit::{lote_origem}::{i}",
            'status_materializacao_passiva': 'materializado_passivo',
            'origem_mapa_migracao': 'aba_switching_operacional',
        })
    return eventos


def _mapa_switchings_aba_operacional(contexto: Any) -> dict[str, dict[str, Any]]:
    return _mapa_switchings_aba_operacional_legado_v37s(contexto)


def _eventos_switching_aba_operacional(contexto: Any) -> list[dict[str, Any]]:
    return _eventos_switching_aba_operacional_legado_v37s(contexto)


def _propagar_migracao_para_estado_lotes(
    estado_lotes: dict[str, dict[str, Any]],
    lote_origem: Any,
    data_switching: Any,
    produto_destino: Any,
    lote_pos_switching: Any,
    status_switching: Any,
    origem_mapa_migracao: Any,
) -> None:
    componentes = _extrair_lotes_compostos(lote_origem)
    if not componentes and _txt(lote_origem):
        componentes = [_txt(lote_origem)]
    data_norm = _normalizar_data_comparavel(data_switching)
    for comp in componentes:
        if comp not in estado_lotes:
            continue
        estado_lotes[comp]['migrado_em'] = data_norm
        estado_lotes[comp]['destino_switching'] = produto_destino
        estado_lotes[comp]['lote_pos_switching'] = lote_pos_switching
        estado_lotes[comp]['status_switching'] = status_switching
        estado_lotes[comp]['origem_mapa_migracao'] = origem_mapa_migracao





def _normalizar_data_comparavel(v: Any) -> Any:
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if hasattr(v, 'date') and not isinstance(v, str):
        try:
            if hasattr(v, 'hour'):
                return v.date()
        except Exception:
            pass
    if isinstance(v, str):
        txt = v.strip()
        if _norm(txt) in {'', 'n/d', 'nd', 'não determinado', 'nao determinado', 'none'}:
            return None
        for dayfirst in (False, True):
            try:
                dt = pd.to_datetime(txt, errors='raise', dayfirst=dayfirst)
                if pd.isna(dt):
                    continue
                return dt.date()
            except Exception:
                continue
        return None
    try:
        dt = pd.to_datetime(v, errors='raise')
        if pd.isna(dt):
            return None
        return dt.date()
    except Exception:
        return None


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
        data_pag_cmp = _normalizar_data_comparavel(data_pag)
        da_cmp = _normalizar_data_comparavel(da)
        car_cmp = _normalizar_data_comparavel(car)
        bs = saldo + 0.01 < valor_pag
        bd = (not bs) and (da_cmp is not None and data_pag_cmp is not None and da_cmp > data_pag_cmp)
        bc = (not bs and not bd) and (car_cmp is not None and data_pag_cmp is not None and car_cmp > data_pag_cmp)
        motivo_mig = _motivo_bloqueio_migracao(data_pag, mig, pacote)
        bm = (not bs and not bd and not bc) and bool(motivo_mig)
        eleg = not (bs or bd or bc or bm)
        if bs: b_saldo += 1
        if bd: b_data += 1
        if bc: b_car += 1
        if bm: b_mig += 1
        if not bs: qtd_suf += 1
        candidatos.append({'Data': d.get('data_pagamento'),'Conta': d.get('descricao_pagamento') or '','Despesa ID': pid,'Valor': valor_pag,'lote_id': lid,'data_aplicacao': da,'carencia_ate': car,'migrado_em': mig,'saldo_liquido': round(saldo,2),'avaliado_fifo': True,'bloqueado_por_saldo': bs,'bloqueado_por_data': bd,'bloqueado_por_carencia': bc,'bloqueado_por_migracao': bm,'elegivel_fifo': eleg,'ordem_fifo': ordem,'motivo_bloqueio_fifo': 'saldo' if bs else ('data' if bd else ('carencia' if bc else ('migracao' if bm else '')) ),'motivo_bloqueio_migracao_detalhe': motivo_mig if bm else '','status_funcional': meta.get('status_funcional',''),'fonte_temporal': meta.get('fonte_temporal',''),'fonte_eh_lote_pos_switching': _norm(meta.get('status_funcional')) == 'ativo_pos_switching','evento_switching_id': meta.get('evento_switching_id',''),'lote_origem_switching': meta.get('lote_origem_switching',''),'produto_destino': meta.get('produto_destino','')})
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
    data_pag_cmp = _normalizar_data_comparavel(data_pag)
    migrado_em_cmp = _normalizar_data_comparavel(migrado_em)
    if migrado_em_cmp is None or data_pag_cmp is None:
        return ''
    if migrado_em_cmp < data_pag_cmp:
        return 'bloqueado_por_migracao_antes_do_pagamento'
    if migrado_em_cmp == data_pag_cmp:
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
    return _mapa_switchings_aba_operacional(contexto)


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
    val_pag = _round(ev.get('fifo_valor_pagamento'))
    liq = _round(ev.get('liquido'))
    if (
        _norm(ev.get('status')) == 'ok'
        and _norm(ev.get('cobertura_integral')) == 'não'
        and val_pag != ''
        and liq != ''
        and float(liq) + 0.01 < float(val_pag)
    ):
        ev['status'] = 'sem_saldo_temporal_auditavel'
        ev['motivo_bloqueio'] = _txt(ev.get('motivo_bloqueio')) or 'status_ok_sem_cobertura_corrigido_v17_f0a'
        ev['cobertura_integral'] = 'não'
        for k in ['saldo_antes','bruto','imposto','liquido','consumo','saldo_depois']:
            ev[k] = ''
        ev['_v17_f0a_status_ok_sem_cobertura_corrigido'] = True
    return ev


def _float_recebido_funcional(v: Any) -> float:
    try:
        if v is None:
            return 0.0
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        return 0.0


def _bool_recebido_funcional(v: Any) -> bool:
    return _norm(v) in {'true', '1', 'sim', 'yes', 'elegivel'}


def _coluna_recebido_funcional(df: pd.DataFrame, candidatos: list[str]) -> str:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return ''
    mapa = {str(c).strip().lower(): c for c in df.columns}
    for c in candidatos:
        if c.lower() in mapa:
            return str(mapa[c.lower()])
    for c in df.columns:
        cn = str(c).strip().lower()
        if any(k.lower() in cn for k in candidatos):
            return str(c)
    return ''


def _mapa_recebidos_funcionais_por_pagamento(contexto: Any) -> dict[str, list[dict[str, Any]]]:
    """V16-D: consumo funcional contido de recebido_disponivel já escolhido.

    Prepara fontes recebidas elegíveis por pagamento. Esta função não muda a
    decisão, não altera prioridade e não promove switching. O uso funcional é
    restrito ao evento cuja decisão já escolheu recebido_disponivel.
    """
    pacote = getattr(contexto, 'fontes_elegiveis_pagamento', None) if contexto is not None else None
    quadro = getattr(pacote, 'quadro_fontes_elegiveis', None) if pacote is not None else None

    if not isinstance(quadro, pd.DataFrame) or quadro.empty:
        return {}

    col_pid = _coluna_recebido_funcional(quadro, ['pagamento_id', 'Despesa ID', 'despesa_id'])
    col_tipo = _coluna_recebido_funcional(quadro, ['tipo_fonte', 'tipo_fonte_candidata'])
    col_eleg = _coluna_recebido_funcional(quadro, ['elegivel_na_data_pagamento', 'elegivel'])
    col_liq = _coluna_recebido_funcional(quadro, ['valor_liquido_disponivel', 'valor_liquido'])
    col_bruto = _coluna_recebido_funcional(quadro, ['valor_bruto_disponivel', 'valor_bruto'])
    col_fonte = _coluna_recebido_funcional(quadro, ['fonte_id', 'fonte_pagamento_id', 'fonte_candidata_id'])
    col_recebido = _coluna_recebido_funcional(quadro, ['recebido_id'])
    col_lote = _coluna_recebido_funcional(quadro, ['lote_id'])
    col_data = _coluna_recebido_funcional(quadro, ['data_evento', 'data_pagamento'])

    if not col_pid or not col_tipo:
        return {}

    fontes_por_id: dict[str, dict[str, Any]] = {}
    mapa: dict[str, list[dict[str, Any]]] = {}

    for _, row in quadro.iterrows():
        pid = _txt(row.get(col_pid))
        if not pid:
            continue

        if _norm(row.get(col_tipo)) != 'recebido_disponivel':
            continue

        if col_eleg and not _bool_recebido_funcional(row.get(col_eleg)):
            continue

        valor_liq = _float_recebido_funcional(row.get(col_liq)) if col_liq else 0.0
        valor_bruto = _float_recebido_funcional(row.get(col_bruto)) if col_bruto else valor_liq
        saldo_inicial = valor_liq if valor_liq > 0.0 else valor_bruto

        if saldo_inicial <= 0.01:
            continue

        fonte_id = _txt(row.get(col_fonte)) if col_fonte else ''
        recebido_id = _txt(row.get(col_recebido)) if col_recebido else ''
        lote_id = _txt(row.get(col_lote)) if col_lote else ''
        fonte_key = fonte_id or recebido_id or lote_id or f'recebido_disponivel::{pid}::{len(fontes_por_id)}'

        if fonte_key not in fontes_por_id:
            fontes_por_id[fonte_key] = {
                'fonte_key': fonte_key,
                'fonte_id': fonte_id or fonte_key,
                'recebido_id': recebido_id,
                'lote_id': lote_id,
                'data_evento': row.get(col_data) if col_data else '',
                'saldo_inicial': round(saldo_inicial, 2),
                'saldo': round(saldo_inicial, 2),
                'valor_bruto': round(valor_bruto, 2),
            }
        else:
            fontes_por_id[fonte_key]['saldo_inicial'] = max(
                _float_recebido_funcional(fontes_por_id[fonte_key].get('saldo_inicial')),
                round(saldo_inicial, 2),
            )
            fontes_por_id[fonte_key]['saldo'] = max(
                _float_recebido_funcional(fontes_por_id[fonte_key].get('saldo')),
                round(saldo_inicial, 2),
            )

        mapa.setdefault(pid, []).append(fontes_por_id[fonte_key])

    for pid, fontes in mapa.items():
        mapa[pid] = sorted(
            fontes,
            key=lambda f: (-_float_recebido_funcional(f.get('saldo')), _txt(f.get('fonte_key'))),
        )

    return mapa


def _pagamentos_decisao_recebido_disponivel(contexto: Any) -> set[str]:
    """V16-H: decisão real exclusiva do quadro local."""
    decisao = getattr(contexto, 'decisao_local_v1', None) if contexto is not None else None
    quadro = getattr(decisao, 'quadro_decisao_local_v1', None) if decisao is not None else None

    if not isinstance(quadro, pd.DataFrame) or quadro.empty:
        return set()

    if 'pagamento_id' not in quadro.columns:
        return set()

    if 'tipo_fonte_escolhida' not in quadro.columns:
        return set()

    permitidos: set[str] = set()

    for _, row in quadro.iterrows():
        if _norm(row.get('tipo_fonte_escolhida')) != 'recebido_disponivel':
            continue

        pagamento_id = _txt(row.get('pagamento_id'))
        if pagamento_id:
            permitidos.add(pagamento_id)

    return permitidos


def _selecionar_recebido_funcional(
    pagamento_id: str,
    valor_pagamento: float,
    mapa_recebidos: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    fontes = list(mapa_recebidos.get(_txt(pagamento_id), []) or [])
    fontes = sorted(
        fontes,
        key=lambda f: (-_float_recebido_funcional(f.get('saldo')), _txt(f.get('fonte_key'))),
    )
    for fonte in fontes:
        if _float_recebido_funcional(fonte.get('saldo')) + 0.01 >= valor_pagamento:
            return fonte
    return None


def _valor_monetario_pos_switching(v: Any) -> float:
    try:
        if v is None:
            return 0.0
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    try:
        return float(v)
    except Exception:
        pass

    txt = _txt(v).replace('R$', '').strip()
    if not txt or _eh_nd(txt):
        return 0.0
    if ',' in txt:
        txt = txt.replace('.', '').replace(',', '.')
    try:
        return float(txt)
    except Exception:
        return 0.0


def _injetar_lotes_pos_switching_em_estado_lotes(
    contexto: Any,
    estado_lotes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Insere destinos pós-switching no estado temporal local de fontes.

    Não escolhe fonte, não altera ranking e não cria motor paralelo.
    Apenas torna os lotes materializados por switching visíveis ao mesmo
    avaliador temporal que já processa os demais lotes em estado_lotes.
    """
    auditoria = {
        'eventos_switching_recebidos': 0,
        'lotes_pos_switching_injetados': 0,
        'origens_migradas_marcadas': 0,
        'eventos_sem_lote_destino': 0,
        'eventos_sem_valor_valido': 0,
    }

    if contexto is None:
        return auditoria

    try:
        eventos = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)
    except Exception:
        eventos = []

    auditoria['eventos_switching_recebidos'] = len(eventos)

    for ev in eventos:
        if not isinstance(ev, dict):
            continue

        data_sw = _normalizar_data_comparavel(
            ev.get('data_switching')
            or ev.get('Data')
            or ev.get('Data sugerida')
        )
        lote_origem = _txt(
            ev.get('lote_origem')
            or ev.get('Lote origem')
            or ev.get('lote_id_origem')
        )
        lote_destino = _txt(
            ev.get('lote_pos_switching')
            or ev.get('lote_destino')
            or ev.get('Lote destino')
            or ev.get('lote_id_destino')
        )
        valor = _valor_monetario_pos_switching(
            ev.get('valor_liquido_origem')
            or ev.get('valor_liquido_migrado')
            or ev.get('Valor líquido origem')
            or ev.get('Valor Líquido Migrado')
        )
        produto_destino = _txt(
            ev.get('produto_destino')
            or ev.get('Produto destino switching')
            or ev.get('Destino')
        )
        evento_id = (
            _txt(ev.get('evento_switching_id'))
            or f"switching::{data_sw}::{lote_origem}::{lote_destino}"
        )
        origem_materializacao = (
            _txt(ev.get('origem_materializacao') or ev.get('origem_mapa_migracao'))
            or 'switching_materializado_v17_f0_o2'
        )

        if lote_origem:
            componentes = _extrair_lotes_compostos(lote_origem) or [lote_origem]
            for comp in componentes:
                if comp in estado_lotes:
                    estado_lotes[comp]['migrado_em'] = data_sw
                    estado_lotes[comp]['destino_switching'] = produto_destino
                    estado_lotes[comp]['lote_pos_switching'] = lote_destino
                    estado_lotes[comp]['status_switching'] = (
                        ev.get('status_materializacao')
                        or ev.get('status_materializacao_passiva')
                        or 'materializado_estado_temporal_v17_f0_o2'
                    )
                    estado_lotes[comp]['origem_mapa_migracao'] = origem_materializacao
                    auditoria['origens_migradas_marcadas'] += 1

        if not lote_destino:
            auditoria['eventos_sem_lote_destino'] += 1
            continue

        if valor <= 0.0:
            auditoria['eventos_sem_valor_valido'] += 1
            continue

        estado_lotes[lote_destino] = {
            'data_aplicacao': data_sw,
            'carencia_ate': data_sw,
            'saldo_liquido': round(valor, 2),
            'migrado_em': None,
            'status_funcional': 'ativo_pos_switching',
            'fonte_temporal': 'switching_materializado_v17_f0_o2',
            'evento_switching_id': evento_id,
            'lote_origem_switching': lote_origem,
            'produto_destino': produto_destino,
            'origem_materializacao': origem_materializacao,
        }
        auditoria['lotes_pos_switching_injetados'] += 1

    return auditoria


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

    auditoria_pos_switching_estado_lotes = _injetar_lotes_pos_switching_em_estado_lotes(contexto, estado_lotes)

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
    mapa_sw_quadro: dict[str, dict[str, Any]] = {}
    for _, row in quadro_ord.iterrows():
        dsw = row.to_dict()
        lote_sw = _txt(dsw.get('lote_recomendado_consumivel') or dsw.get('lote_recomendado') or dsw.get('lote_id_escolhido') or dsw.get('fonte_origem_id'))
        if not lote_sw:
            continue
        houve_switch = bool(dsw.get('switching_antes_pagamento') or dsw.get('switching_depois_pagamento'))
        if not houve_switch:
            continue
        lote_pos_sw = _txt(dsw.get('lote_nome_operacional') or dsw.get('fonte_pos_sw') or dsw.get('lote_id_sintetico'))
        if not lote_pos_sw:
            continue
        data_sw = _primeira_data_valida_em_ordem(
            dsw,
            ['data_switching_referencia', 'data_sugerida_switching', 'data_operacional', 'data_pagamento'],
        )
        if _normalizar_data_comparavel(data_sw) is None:
            continue
        ev_sw = {
            'lote_origem': lote_sw,
            'data_switching': data_sw,
            'produto_destino': _txt(dsw.get('produto_destino_switching')),
            'valor_liquido_origem': _round(dsw.get('liquido_recomendado')),
            'status_switching': 'classificado_promovido',
            'origem_mapa_migracao': 'quadro_futuro::switching_promovido',
            'lote_pos_switching': lote_pos_sw,
        }
        atual = mapa_sw_quadro.get(lote_sw)
        if atual is None or (
            _normalizar_data_comparavel(atual.get('data_switching')) is None
            or _normalizar_data_comparavel(data_sw) > _normalizar_data_comparavel(atual.get('data_switching'))
        ):
            mapa_sw_quadro[lote_sw] = ev_sw
    for lo, meta in mapa_sw_quadro.items():
        atual = mapa_global_sw.get(lo)
        if atual is None or (
            _normalizar_data_comparavel(atual.get('data_switching')) is None
            or _normalizar_data_comparavel(meta.get('data_switching')) > _normalizar_data_comparavel(atual.get('data_switching'))
        ):
            mapa_global_sw[lo] = meta
    mapa_sw_operacional = _mapa_switchings_aba_operacional(contexto)
    eventos_sw_operacional = _eventos_switching_aba_operacional(contexto)
    for lo, meta in mapa_sw_operacional.items():
        atual = mapa_global_sw.get(lo)
        if atual is None or (
            _normalizar_data_comparavel(atual.get('data_switching')) is None
            or _normalizar_data_comparavel(meta.get('data_switching')) >= _normalizar_data_comparavel(atual.get('data_switching'))
        ):
            mapa_global_sw[lo] = meta
    v17_f0a = {
        'v17_f0a_origens_migradas_detectadas': len(mapa_global_sw),
        'v17_f0a_bloqueios_origem_migrada': 0,
        'v17_f0a_status_ok_sem_cobertura_corrigidos': 0,
        'v17_f0a_eventos_intradia_migracao_bloqueados': 0,
    }
    destinos_pos_switching_passivos = list(eventos_sw_operacional)
    vinculos_origem_destino_passivos = [
        {
            'evento_switching_id': e.get('evento_switching_id'),
            'lote_origem': e.get('lote_origem'),
            'lote_pos_switching': e.get('lote_pos_switching'),
            'produto_destino': e.get('produto_destino'),
            'data_switching': e.get('data_switching'),
            'status_materializacao_passiva': e.get('status_materializacao_passiva'),
        }
        for e in destinos_pos_switching_passivos
    ]
    for lo, meta_sw in mapa_global_sw.items():
        _propagar_migracao_para_estado_lotes(
            estado_lotes=estado_lotes,
            lote_origem=lo,
            data_switching=meta_sw.get('data_switching'),
            produto_destino=meta_sw.get('produto_destino'),
            lote_pos_switching=meta_sw.get('lote_pos_switching'),
            status_switching=meta_sw.get('status_switching'),
            origem_mapa_migracao=meta_sw.get('origem_mapa_migracao'),
        )

    for ev in materializados.values():
        _propagar_migracao_para_estado_lotes(
            estado_lotes=estado_lotes,
            lote_origem=ev.get('lote_origem'),
            data_switching=ev.get('data_switching'),
            produto_destino=ev.get('produto_destino'),
            lote_pos_switching=ev.get('lote_pos_switching'),
            status_switching=ev.get('estado'),
            origem_mapa_migracao='materializacao_no_quadro_futuro',
        )

    saldo_temporal = {
        'comparativo_funcoes_legadas_mapeadas': 0,
        'comparativo_funcoes_sem_equivalente_atual': 0,
        'recebidos_total_origem_situacao_atual': 0,
        'recebidos_total_integrados_ledger': 0,
        'saldo_temporal_lotes_auditados': 0,
        'saldo_temporal_lotes_com_consumo_acima_saldo': 0,
        'saldo_temporal_pagamentos_auditados': 0,
        'saldo_temporal_pagamentos_ok_antes': 0,
        'saldo_temporal_pagamentos_ok_depois': 0,
        'saldo_temporal_pagamentos_rebaixados_por_saldo': 0,
        'saldo_temporal_divergencias_saldo_antes': 0,
        'saldo_temporal_divergencias_saldo_depois': 0,
        'saldo_temporal_invariantes_violados': 0,
        'recebidos_futuros_total': 0,
        'recebidos_futuros_incorporados_total': 0,
        'recebidos_disponiveis_incorporados_total': 0,
        'recebidos_disponiveis_nao_incorporados': 0,
        'recebidos_futuros_auditoria_linhas': 0,
        'pagamentos_rebaixados_por_fonte_nao_incorporada': 0,
        'pagamentos_rebaixados_por_recebido_nao_incorporado': 0,
        'pagamentos_rebaixados_por_saldo_real_insuficiente': 0,
        'saldo_temporal_fontes_auditadas_total': 0,
        'alocacao_fontes_disponiveis_total': 0,
        'alocacao_valor_liquido_disponivel_total': 0.0,
        'alocacao_valor_reservado_pagamentos_total': 0.0,
        'alocacao_valor_alocavel_total': 0.0,
        'alocacao_fontes_candidatas_aporte': 0,
        'alocacao_fontes_reservadas_pagamento': 0,
        'alocacao_fontes_mantidas_caixa': 0,
        'alocacao_fontes_com_destino_carteira': 0,
        'alocacao_fontes_sem_destino_carteira': 0,
        'alocacao_inconsistencias_classificacao': 0,
        'alocacao_decisoes_integradas_ao_ledger': 0,
        'pagamentos_rebaixados_saldo_real_insuficiente_pos_recebidos': 0,
    }
    saldo_temporal_auditoria_lotes: list[dict[str, Any]] = []
    saldo_temporal_pagamentos_rebaixados_detalhe: list[dict[str, Any]] = []
    recebidos_futuros_auditoria: list[dict[str, Any]] = []
    alocacao_fontes_auditoria: list[dict[str, Any]] = []

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
    saldo_temporal['recebidos_funcionais_entraram_bloco_promocao'] = 0
    saldo_temporal['recebidos_funcionais_passaram_filtro_data'] = 0
    saldo_temporal['recebidos_funcionais_passaram_filtro_saldo'] = 0
    saldo_temporal['recebidos_funcionais_promovidos_evento'] = 0
    saldo_temporal['recebidos_funcionais_sobrescritos_apos_promocao'] = 0
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
    promovidos_ids: set[str] = set()
    for ev in eventos:
        pid_ev = str(ev.get('pagamento_id') or '')
        status_ev = str(ev.get('status') or '')
        eh_candidato = (status_ev != 'ok')
        if not eh_candidato:
            continue
        saldo_temporal['recebidos_funcionais_entraram_bloco_promocao'] += 1
        data_ev = str(ev.get('data') or '')
        val = round(float(ev.get('valor') or ev.get('valor_pagamento') or ev.get('liquido') or ev.get('consumo') or 0.0), 2)
        if val <= 0:
            continue
        restante = val
        usadas = []
        for f in fontes_funcionais:
            if str(f.get('data') or '') > data_ev:
                continue
            saldo_temporal['recebidos_funcionais_passaram_filtro_data'] += 1
            if float(f.get('saldo') or 0.0) <= 0:
                continue
            saldo_temporal['recebidos_funcionais_passaram_filtro_saldo'] += 1
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
            ev['origem_fonte_candidata'] = 'recebidos_funcionais_v1'
            ev['status'] = 'ok'
            ev['cobertura_integral'] = 'sim'
            ev['motivo_bloqueio'] = 'n/d'
            ev['saldo_antes'] = round(usadas[0][1], 2)
            ev['consumo'] = val
            ev['liquido'] = val
            ev['saldo_depois'] = round(usadas[-1][3], 2)
            saldo_temporal['pagamentos_funcionais_recuperados_por_recebidos'] += 1
            saldo_temporal['recebidos_funcionais_valor_usado_pagamentos'] += val
            saldo_temporal['recebidos_funcionais_promovidos_evento'] += 1
            if pid_ev:
                promovidos_ids.add(pid_ev)
        else:
            saldo_temporal['pagamentos_funcionais_nao_recuperados_por_saldo'] += 1
    saldo_temporal['recebidos_funcionais_sobrescritos_apos_promocao'] = len([pid for pid in promovidos_ids if any(str(e.get('pagamento_id') or '') == pid and str(e.get('status') or '') != 'ok' for e in eventos)])
    saldo_temporal['recebidos_funcionais_valor_alocavel_pos_pagamento'] = round(sum(float(f.get('saldo') or 0.0) for f in fontes_funcionais), 2)
    for f in fontes_funcionais:
        if float(f.get('saldo') or 0.0) < -0.01:
            saldo_temporal['recebidos_funcionais_fontes_com_saldo_negativo'] += 1
    # Auditoria cumulativa de saldo temporal por lote (cronológica).
    consumo_por_lote: dict[str, dict[str, Any]] = {}
    saldo_exec = {k: float(v.get('saldo_liquido') or 0.0) for k, v in estado_lotes.items()}
    recebidos_funcionais_por_pagamento = _mapa_recebidos_funcionais_por_pagamento(contexto)
    pagamentos_decisao_recebido = _pagamentos_decisao_recebido_disponivel(contexto)
    saldo_temporal['recebidos_funcionais_mapa_pagamentos_v16d'] = len(recebidos_funcionais_por_pagamento)
    saldo_temporal['recebidos_funcionais_decisoes_recebido_disponivel_v16d'] = len(pagamentos_decisao_recebido)
    saldo_temporal['recebidos_funcionais_consumidos_ledger_v16d'] = 0
    saldo_temporal['valor_recebidos_funcionais_consumidos_ledger_v16d'] = 0.0
    saldo_temporal['recebidos_funcionais_casos_sem_fonte_suficiente_v16d'] = 0
    saldo_temporal['recebidos_funcionais_contencao_saldo_lote_preservada_v16d'] = 0
    eventos.sort(key=lambda e: (str(e.get('data') or ''), str(e.get('pagamento_id') or '')))
    for ev in eventos:
        lote = str(ev.get('lote_sugerido_operacional') or '')
        if not lote or lote == 'não determinado' or '+' in lote:
            continue
        if lote not in consumo_por_lote:
            consumo_por_lote[lote] = {'total_pagamentos_planejados': 0,'total_consumo_d2a': 0.0,'total_consumo_d2b': 0.0,'total_consumo_fifo': 0.0,'total_consumo_motor': 0.0,'pagamentos_afetados': [],'primeiro_evento_que_estoura_saldo': ''}
        rec = consumo_por_lote[lote]
        consumo = float(ev.get('consumo') or ev.get('liquido') or 0.0)

        # V16-D: prepara consumo funcional contido de recebido_disponivel.
        pagamento_id_evento = _txt(ev.get('pagamento_id'))
        # V16-G: consumo funcional recebido_disponivel exige decisão real.
        # Não aceitar gatilho por campos do evento, pois tipo_fonte_candidata,
        # tipo_fonte_recomendada ou tipo_fonte_final podem refletir fallback
        # auditável e reclassificar casos A com decisão lote_resgatavel.
        decisao_recebido_disponivel = pagamento_id_evento in pagamentos_decisao_recebido
        fonte_recebida_funcional = (
            _selecionar_recebido_funcional(
                pagamento_id_evento,
                consumo,
                recebidos_funcionais_por_pagamento,
            )
            if decisao_recebido_disponivel and consumo > 0.0
            else None
        )
        saldo_depois_recebido_v16d = None
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
        if decisao_recebido_disponivel and consumo > 0.0 and fonte_recebida_funcional is None:
            saldo_temporal['recebidos_funcionais_casos_sem_fonte_suficiente_v16d'] += 1

        if consumo > saldo_antes_real + 0.01 and fonte_recebida_funcional is not None:
            saldo_antes_recebido = round(_float_recebido_funcional(fonte_recebida_funcional.get('saldo')), 2)
            saldo_depois_recebido_v16d = round(saldo_antes_recebido - consumo, 2)
            fonte_recebida_funcional['saldo'] = saldo_depois_recebido_v16d

            ev['status'] = 'ok'
            ev['cobertura_integral'] = 'sim'
            ev['motivo_bloqueio'] = 'n/d'
            ev['saldo_antes'] = saldo_antes_recebido
            ev['bruto'] = consumo
            ev['imposto'] = 0.0
            ev['liquido'] = consumo
            ev['consumo'] = consumo
            ev['fonte_temporal_consumida'] = 'recebido_disponivel'
            ev['tipo_fonte_candidata'] = 'recebido_disponivel'
            ev['fonte_candidata_id'] = fonte_recebida_funcional.get('fonte_id') or fonte_recebida_funcional.get('fonte_key')
            ev['origem_fonte_candidata'] = (
                'ledger_temporal_conjunto.v16d.recebido_disponivel_funcional_contido'
                f"|recebido_id={fonte_recebida_funcional.get('recebido_id') or ''}"
                f"|lote_id={fonte_recebida_funcional.get('lote_id') or ''}"
            )
            ev['recebido_id_funcional'] = fonte_recebida_funcional.get('recebido_id') or ''
            ev['lote_id_recebido_funcional'] = fonte_recebida_funcional.get('lote_id') or ''
            ev['data_recebido_funcional'] = fonte_recebida_funcional.get('data_evento') or ''

            saldo_temporal['recebidos_funcionais_consumidos_ledger_v16d'] += 1
            saldo_temporal['valor_recebidos_funcionais_consumidos_ledger_v16d'] = round(
                float(saldo_temporal.get('valor_recebidos_funcionais_consumidos_ledger_v16d') or 0.0) + consumo,
                2,
            )
            saldo_temporal['recebidos_funcionais_contencao_saldo_lote_preservada_v16d'] += 1

        elif consumo > saldo_antes_real + 0.01:
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

        if saldo_depois_recebido_v16d is not None:
            ev['saldo_depois'] = saldo_depois_recebido_v16d
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
        saldo_temporal_auditoria_lotes.append({'lote_id': lote,'saldo_inicial_liquido': ini,**rec,'total_consumo_geral': total,'saldo_final_temporal': round(ini-total,2),'consumo_excede_saldo': excede})
    saldo_temporal['saldo_temporal_lotes_auditados'] = len(saldo_temporal_auditoria_lotes)
    saldo_temporal['alocacao_decisoes_integradas_ao_ledger'] = saldo_temporal['alocacao_fontes_disponiveis_total']
    saldo_temporal['extrato_futuro_status_ok_total'] = sum(1 for e in eventos if str(e.get('status') or '') == 'ok')
    saldo_temporal['extrato_futuro_nao_determinado_total'] = sum(1 for e in eventos if _eh_nd(e.get('lote_sugerido_operacional')))
    saldo_temporal['extrato_futuro_sem_saldo_temporal_total'] = sum(1 for e in eventos if str(e.get('status') or '') == 'sem_saldo_temporal_auditavel')
    saldo_temporal['divergencias_auditoria_fontes_extrato_futuro'] = 0
    saldo_temporal['pre_invariante_total'] = 0
    return {
        "eventos": eventos,
        "fifo_candidatos_avaliados": fifo_candidatos_avaliados,
        **v17_f0a,
        "switchings_promovidos_ledger": len(destinos_pos_switching_passivos),
        "destinos_pos_switching_materializados_passivos": destinos_pos_switching_passivos,
        "destinos_pos_switching_materializados_passivos_total": len(destinos_pos_switching_passivos),
        "vinculos_origem_destino_pos_switching": vinculos_origem_destino_passivos,
        "vinculos_origem_destino_pos_switching_total": len(vinculos_origem_destino_passivos),
        **saldo_temporal,
        "saldo_temporal_auditoria_lotes": saldo_temporal_auditoria_lotes,
        "saldo_temporal_pagamentos_rebaixados_detalhe": saldo_temporal_pagamentos_rebaixados_detalhe,
        "recebidos_futuros_auditoria": recebidos_futuros_auditoria,
        "alocacao_fontes_auditoria": alocacao_fontes_auditoria,
    }
