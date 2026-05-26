from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from nucleo.contexto_operacional_canonico import ContextoOperacionalCanonico


@dataclass(slots=True)
class EstadoTemporalInicial:
    data_referencia: date
    calendario_financeiro: Any
    cache_cdi: Any
    inventario_temporal: list[dict[str, Any]]
    fontes_temporais: list[dict[str, Any]]
    recebidos_temporais: list[dict[str, Any]]
    pagamentos_temporais: list[dict[str, Any]]
    switching_temporal_realizado: list[dict[str, Any]]
    restricoes_temporais: list[dict[str, Any]]
    elegibilidades_preliminares: list[dict[str, Any]]
    auditoria_temporal: dict[str, Any]
    metadados: dict[str, Any]


def _status_data(data_pg: Any, data_ref: date, pago: bool) -> str:
    if pago:
        return 'historico'
    if data_pg is None:
        return 'futuro'
    if data_pg < data_ref:
        return 'vencido'
    if data_pg == data_ref:
        return 'hoje'
    return 'futuro'


def _bool_conservador_fonte(f: dict[str, Any]) -> bool:
    if 'disponivel' in f:
        return bool(f.get('disponivel'))
    if 'elegivel_na_data_pagamento' in f:
        return bool(f.get('elegivel_na_data_pagamento'))
    if 'elegivel_temporalmente' in f:
        return bool(f.get('elegivel_temporalmente'))
    return False


def _float_seguro(*valores: Any) -> float:
    for v in valores:
        if v is None or v == '':
            continue
        try:
            return float(v)
        except Exception:
            continue
    return 0.0


def construir_estado_temporal_inicial(contexto: ContextoOperacionalCanonico) -> EstadoTemporalInicial:
    data_ref = contexto.execucao.data_referencia
    gastos = contexto.dados_operacionais.gastos_canonicos
    recebidos = contexto.dados_operacionais.salarios_canonicos
    inventario = contexto.dados_operacionais.inventario_canonico
    switching = getattr(contexto.dados_operacionais, 'switching_canonico', None)

    pagamentos_temporais = []
    for row in gastos.to_dict(orient='records'):
        pago = bool(row.get('pago'))
        data_pg = row.get('data')
        status = _status_data(data_pg, data_ref, pago)
        futuro = status == 'futuro'
        pagamentos_temporais.append({
            'pagamento_id': row.get('despesa_id') or row.get('id') or f"pg_{len(pagamentos_temporais)+1:05d}",
            'data': data_pg,
            'descricao': row.get('descricao') or row.get('conta') or '',
            'valor': float(row.get('valor') or 0.0),
            'pago': pago,
            'status_temporal': status,
            'obrigacao_temporal': True,
            'fonte_informada': row.get('lote_usado_1') or row.get('lote_usado') or row.get('lote_origem'),
            'fonte_resolvida_historica': (row.get('lote_usado_1') or row.get('lote_usado')) if pago else None,
            'fonte_a_decidir': bool(futuro or not pago),
            'vencido_na_referencia': status == 'vencido',
            'futuro_na_referencia': futuro,
            'bloqueios_preliminares': ['fonte_futura_a_decidir'] if futuro else [],
        })

    inventario_temporal=[]
    for row in inventario.to_dict(orient='records'):
        status = 'ativo'
        if bool(row.get('futuro_na_referencia')):
            status='futuro'
        elif bool(row.get('exaurido')):
            status='exaurido'
        elif bool(row.get('vencido')):
            status='vencido_normalizado'
        inventario_temporal.append({'lote_id':row.get('lote_id'),'status_temporal':status,'disponibilidade':'disponivel' if bool(row.get('disponivel',True)) else 'indisponivel','migrado_por_switching':bool(row.get('migrado_por_switching')),'sintetico_pos_switching':bool(row.get('sintetico_pos_switching')),'origem_canonica':'inventario_canonico'})

    recebidos_temporais=[]
    for row in recebidos.to_dict(orient='records'):
        data_rec=row.get('data_recebimento')
        materializado = bool(data_rec and data_rec <= data_ref)
        recebidos_temporais.append({'recebido_id':row.get('recebido_id') or row.get('salario_id'),'data_recebimento':data_rec,'valor':row.get('valor_liquido') or row.get('valor_bruto') or 0.0,'materializado':materializado,'futuro_indisponivel':not materializado,'aplicado':bool(row.get('aplicado')),'vinculado':bool(row.get('vinculado')),'disponivel_na_referencia':materializado and not bool(row.get('aplicado'))})

    fontes_temporais=[]
    fontes_obj = getattr(contexto, 'fontes_elegiveis_pagamento', None)
    fontes_brutas = getattr(fontes_obj, 'quadro_fontes_elegiveis', fontes_obj)
    if fontes_brutas is None:
        fontes_brutas = []
    if hasattr(fontes_brutas, 'to_dict'):
        fontes_brutas = fontes_brutas.to_dict(orient='records')
    for f in fontes_brutas:
        disponivel_ref = _bool_conservador_fonte(f)
        valor_estimado = _float_seguro(
            f.get('valor_liquido_disponivel'),
            f.get('valor_bruto_disponivel'),
            f.get('valor_liquido'),
            f.get('valor'),
            0.0,
        )
        fontes_temporais.append({'fonte_id':f.get('lote_id') or f.get('fonte_id'),'tipo_fonte':f.get('tipo_fonte') or 'lote','data_disponibilidade':f.get('data_disponibilidade') or data_ref,'valor_estimado':valor_estimado,'status_temporal':'disponivel' if disponivel_ref else 'indisponivel','disponivel_na_referencia':disponivel_ref,'motivo_indisponibilidade':f.get('motivo_bloqueio') or '','origem_canonica':'fontes_elegiveis_pagamento'})

    switching_temporal_realizado = [] if switching is None else switching.to_dict(orient='records')

    restricoes_temporais=[]
    elegibilidades=[]
    for pg in pagamentos_temporais:
        if pg['futuro_na_referencia']:
            restricoes_temporais.append({'tipo':'pagamento_futuro','pagamento_id':pg['pagamento_id']})
        elegibilidades.append({'pagamento_id':pg['pagamento_id'],'elegivel_preliminar':True,'observacao':'sem_decisao_economica_etapa5'})

    estado = EstadoTemporalInicial(
        data_referencia=data_ref,
        calendario_financeiro=contexto.calendario_financeiro,
        cache_cdi=contexto.cache_cdi,
        inventario_temporal=inventario_temporal,
        fontes_temporais=fontes_temporais,
        recebidos_temporais=recebidos_temporais,
        pagamentos_temporais=pagamentos_temporais,
        switching_temporal_realizado=switching_temporal_realizado,
        restricoes_temporais=restricoes_temporais,
        elegibilidades_preliminares=elegibilidades,
        auditoria_temporal={},
        metadados={'etapa':'4','artefato':'EstadoTemporalInicial'},
    )
    estado.auditoria_temporal = auditar_estado_temporal_inicial(estado)
    return estado


def auditar_estado_temporal_inicial(estado: EstadoTemporalInicial) -> dict[str, Any]:
    bloqueios=[]
    if not estado.pagamentos_temporais:
        bloqueios.append('pagamentos_temporais_vazio')
    futuros=[p for p in estado.pagamentos_temporais if p.get('status_temporal')=='futuro']
    if not futuros:
        bloqueios.append('sem_pagamentos_futuros')
    if any(p.get('obrigacao_temporal') is not True for p in estado.pagamentos_temporais):
        bloqueios.append('pagamentos_sem_obrigacao_temporal')
    qtd_fontes = len(estado.fontes_temporais)
    qtd_fontes_disponiveis = sum(1 for f in estado.fontes_temporais if f.get('disponivel_na_referencia') is True)
    qtd_fontes_indisponiveis = sum(1 for f in estado.fontes_temporais if f.get('disponivel_na_referencia') is False)
    qtd_fontes_valor_positivo = sum(1 for f in estado.fontes_temporais if float(f.get('valor_estimado') or 0.0) > 0)
    return {'ok': len(bloqueios)==0, 'bloqueios': bloqueios, 'resumo': {'qtd_pagamentos':len(estado.pagamentos_temporais),'qtd_futuros':len(futuros),'qtd_fontes_temporais':qtd_fontes,'qtd_fontes_disponiveis':qtd_fontes_disponiveis,'qtd_fontes_indisponiveis':qtd_fontes_indisponiveis,'qtd_fontes_valor_positivo':qtd_fontes_valor_positivo}}
