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


_MESES_PT_LOTE_ID = {
    1: 'jan.',
    2: 'fev.',
    3: 'mar.',
    4: 'abr.',
    5: 'mai.',
    6: 'jun.',
    7: 'jul.',
    8: 'ago.',
    9: 'set.',
    10: 'out.',
    11: 'nov.',
    12: 'dez.',
}


def _texto_material_temporal(valor: Any) -> str:
    texto = str(valor or '').strip()
    if texto.lower() in {'', 'nan', 'none', 'n/d', 'nd'}:
        return ''
    return texto


def _formatar_valor_lote_id_temporal(valor: Any) -> str:
    if isinstance(valor, bool) or valor is None:
        return ''
    try:
        numero = float(valor)
    except Exception:
        return ''
    if numero <= 0:
        return ''
    if abs(numero - round(numero)) < 0.005:
        return str(int(round(numero)))
    texto = f'{numero:.2f}'.replace('.', ',')
    texto = texto.rstrip('0').rstrip(',')
    return texto


def _lote_id_existente_ou_vazio(valor: Any) -> str:
    texto = _texto_material_temporal(valor)
    if texto.lower().startswith('lote '):
        return texto
    return ''


def _lote_id_operacional_previsto_recebido(valor: Any, data_ref: Any, lote_existente: Any = None) -> str:
    lote = _lote_id_existente_ou_vazio(lote_existente)
    if lote:
        return lote

    valor_txt = _formatar_valor_lote_id_temporal(valor)
    mes_txt = ''
    if isinstance(data_ref, date):
        mes_txt = _MESES_PT_LOTE_ID.get(data_ref.month, '')
    if valor_txt and mes_txt:
        return f'Lote {valor_txt} {mes_txt}'
    if valor_txt:
        return f'Lote {valor_txt}'
    return ''




def _status_switching_materializacao(data_ref: date, data_switching: Any, data_aplicacao: Any) -> str:
    data_evt = data_switching or data_aplicacao
    if data_evt is None:
        return 'declarado'
    return 'materializado' if data_evt <= data_ref else 'declarado'


def _status_inventario_temporal(row: dict[str, Any]) -> str:
    status_canonico = str(row.get('status_temporal') or row.get('status_ciclo') or row.get('situacao_investimento') or '').strip().lower()
    if status_canonico:
        if 'migrado' in status_canonico:
            return 'migrado_por_switching'
        if 'exaurido' in status_canonico:
            return 'exaurido'
        if 'vencido' in status_canonico:
            return 'vencido_normalizado'
        if 'futuro' in status_canonico:
            return 'futuro'
        if 'pos_switching' in status_canonico:
            return 'ativo_pos_switching'
        if 'indisponivel' in status_canonico:
            return 'indisponivel'
        if 'ativo' in status_canonico or 'disponivel' in status_canonico:
            return 'ativo'
    if bool(row.get('migrado_por_switching')):
        return 'migrado_por_switching'
    if bool(row.get('sintetico_pos_switching')):
        return 'ativo_pos_switching'
    if bool(row.get('futuro')) or bool(row.get('futuro_na_referencia')):
        return 'futuro'
    if bool(row.get('exaurido')):
        return 'exaurido'
    if bool(row.get('vencido')):
        return 'vencido_normalizado'
    if row.get('ativo') is False:
        return 'indisponivel'
    if row.get('disponivel_na_data_referencia') is False or row.get('disponivel') is False:
        return 'indisponivel'
    return 'ativo'


def _recebidos_temporais_canonicos(recebidos_auditaveis: Any, data_ref: date) -> list[dict[str, Any]]:
    if recebidos_auditaveis is None:
        return []
    if hasattr(recebidos_auditaveis, 'to_dict'):
        registros = recebidos_auditaveis.to_dict(orient='records')
    else:
        registros = list(recebidos_auditaveis)
    saida = []
    for row in registros:
        recebido_id = row.get('recebido_id')
        if not recebido_id:
            lote_origem = str(row.get('lote_id_origem') or '').strip()
            recebido_id = f'recebido::{lote_origem}' if lote_origem else None
        data_rec = row.get('data_recebimento')
        aplicado = str(row.get('destino_potencial') or '').strip().lower() == 'aplicacao'
        valor_pre_ap = _float_seguro(row.get('valor_pagamentos_pre_aplicacao'), 0.0)
        saida.append({
            'recebido_id': recebido_id,
            'data_recebimento': data_rec,
            'origem': row.get('lote_id_origem'),
            'valor': _float_seguro(row.get('valor_liquido'), row.get('valor_bruto'), 0.0),
            'status_recebido': row.get('status_recebido'),
            'destino_potencial': row.get('destino_potencial'),
            'data_aplicacao': row.get('data_aplicacao') or row.get('Data Aplicação'),
            'investimento': row.get('investimento') or row.get('Investimento') or row.get('produto_nome_canonico') or row.get('carteira_destino'),
            'carteira_destino': row.get('carteira_destino') or row.get('produto_nome_canonico') or row.get('investimento') or row.get('Investimento'),
            'aplicado': aplicado,
            'vinculado': int(row.get('qtd_pagamentos_vinculados') or 0) > 0,
            'disponivel_na_referencia': bool(row.get('disponivel_na_data_referencia', False)),
            'usado_antes_da_aplicacao': valor_pre_ap > 0,
            'pagamento_vinculado_id': row.get('pagamento_vinculado_id'),
            'futuro_indisponivel': not bool(row.get('disponivel_na_data_referencia', False)),
            'materializado': bool(data_rec and data_rec <= data_ref),
            'fonte_id_tecnico': recebido_id,
            'lote_id_operacional_previsto': _lote_id_operacional_previsto_recebido(
                _float_seguro(row.get('valor_liquido'), row.get('valor_bruto'), 0.0),
                data_rec,
                row.get('lote_id') or row.get('Lote (ID)') or row.get('lote'),
            ),
            'tipo_lote_operacional': 'recebido_temporal',
        })
    return saida

def _chave_recebido_temporal(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (
        row.get('recebido_id'),
        row.get('data_recebimento'),
        str(row.get('origem') or row.get('descricao') or '').strip().lower(),
    )


def _recebido_temporal_de_salario(row: dict[str, Any], data_ref: date) -> dict[str, Any]:
    data_rec = row.get('data_recebimento')
    materializado = bool(data_rec and data_rec <= data_ref)
    recebido_id = row.get('recebido_id')
    if not recebido_id:
        salario_id = str(row.get('salario_id') or '').strip()
        recebido_id = f'recebido::{salario_id}' if salario_id else None
    aplicado = bool(row.get('aplicado', False))
    vinculado = bool(row.get('vinculado', False))
    disponivel_ref = bool(row.get('disponivel_na_data_referencia', False))
    return {
        'recebido_id': recebido_id,
        'data_recebimento': data_rec,
        'data_disponibilidade': data_rec,
        'origem': row.get('origem') or row.get('descricao'),
        'valor': _float_seguro(row.get('valor_liquido'), row.get('valor_bruto'), row.get('valor'), 0.0),
        'status_recebido': row.get('status_recebido') or ('materializado' if materializado else 'futuro'),
        'destino_potencial': row.get('destino_potencial') or 'pagamento',
        'data_aplicacao': row.get('data_aplicacao') or row.get('Data Aplicação'),
        'investimento': row.get('investimento') or row.get('Investimento') or row.get('produto_nome_canonico') or row.get('carteira_destino'),
        'carteira_destino': row.get('carteira_destino') or row.get('produto_nome_canonico') or row.get('investimento') or row.get('Investimento'),
        'materializado': materializado,
        'futuro_indisponivel': not materializado,
        'aplicado': aplicado,
        'vinculado': vinculado,
        'disponivel_na_referencia': disponivel_ref,
        'usado_antes_da_aplicacao': bool(row.get('usado_antes_da_aplicacao')),
        'pagamento_vinculado_id': row.get('pagamento_vinculado_id'),
        'origem_canonica': 'salarios_canonicos',
        'fonte_id_tecnico': recebido_id,
        'lote_id_operacional_previsto': _lote_id_operacional_previsto_recebido(
            _float_seguro(row.get('valor_liquido'), row.get('valor_bruto'), row.get('valor'), 0.0),
            data_rec,
            row.get('lote_id') or row.get('Lote (ID)') or row.get('lote'),
        ),
        'tipo_lote_operacional': 'recebido_temporal',
    }


_STATUS_LOTE_INDISPONIVEL_FONTE = {
    'exaurido',
    'exaurido_por_saque',
    'migrado_por_switching',
    'exaurido_por_switching',
    'indisponivel',
}


def _normalizar_motivo_indisponibilidade(*partes: Any) -> str:
    motivos = [str(p).strip() for p in partes if p is not None and str(p).strip() and str(p).strip().lower() != 'nan']
    return ';'.join(motivos)


def _reconciliar_fontes_temporais_com_inventario_final(
    fontes_temporais: list[dict[str, Any]],
    inventario_temporal: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    inventario_por_lote = {
        str(item.get('lote_id') or '').strip(): item
        for item in inventario_temporal
        if str(item.get('lote_id') or '').strip()
    }
    fontes_reconciliadas: list[dict[str, Any]] = []
    for fonte in fontes_temporais:
        lote_id = str(fonte.get('lote_id') or fonte.get('fonte_id') or '').strip()
        inventario_lote = inventario_por_lote.get(lote_id)
        fonte_final = dict(fonte)
        valor_liquido = _float_seguro(
            fonte_final.get('valor_liquido_disponivel'),
            fonte_final.get('valor_estimado'),
            fonte_final.get('valor_disponivel'),
            fonte_final.get('saldo_disponivel'),
            fonte_final.get('saldo'),
            fonte_final.get('valor'),
            0.0,
        )
        motivos: list[str] = []
        if valor_liquido < 1.0:
            motivos.append('saldo_liquido_fonte_operacionalmente_indisponivel')
        if inventario_lote is not None:
            status_lote = str(inventario_lote.get('status_temporal') or '').strip().lower()
            fonte_final['status_inventario_temporal'] = inventario_lote.get('status_temporal')
            fonte_final['disponibilidade_inventario'] = inventario_lote.get('disponibilidade')
            fonte_final['migrado_por_switching'] = bool(inventario_lote.get('migrado_por_switching'))
            fonte_final['sintetico_pos_switching'] = bool(inventario_lote.get('sintetico_pos_switching'))
            if inventario_lote.get('origem_switching') is not None:
                fonte_final['origem_switching'] = inventario_lote.get('origem_switching')
            if inventario_lote.get('valor_liquido_migrado') is not None:
                fonte_final['valor_liquido_migrado'] = inventario_lote.get('valor_liquido_migrado')
            if status_lote in _STATUS_LOTE_INDISPONIVEL_FONTE or bool(inventario_lote.get('migrado_por_switching')):
                motivos.append(f'lote_{status_lote or "indisponivel"}_no_inventario_final')
            elif status_lote:
                fonte_final['status_temporal'] = status_lote
        if motivos:
            fonte_final['status_temporal'] = 'indisponivel'
            fonte_final['disponivel_na_referencia'] = False
            fonte_final['elegivel_na_data_pagamento'] = False
            fonte_final['motivo_indisponibilidade'] = _normalizar_motivo_indisponibilidade(
                fonte_final.get('motivo_indisponibilidade'),
                *motivos,
            )
        fontes_reconciliadas.append(fonte_final)
    return fontes_reconciliadas

def _valor_atual_auditavel_inventario(inventario_lote: dict[str, Any], data_ref: date) -> float:
    data_base = inventario_lote.get('data_aplicacao') or inventario_lote.get('data_recebimento')
    if isinstance(data_base, date) and data_base > data_ref:
        return 0.0
    if inventario_lote.get('disponibilidade') == 'indisponivel':
        return 0.0
    status = str(inventario_lote.get('status_temporal') or '').strip().lower()
    if status in _STATUS_LOTE_INDISPONIVEL_FONTE or 'migrado' in status or 'exaurido' in status:
        return 0.0
    return _float_seguro(
        inventario_lote.get('valor_liquido_disponivel_atual'),
        inventario_lote.get('saldo_disponivel_atual'),
        inventario_lote.get('valor_original'),
        inventario_lote.get('investimento_bruto'),
        inventario_lote.get('valor_liquido_migrado'),
        0.0,
    )


def _materializar_fontes_data_referencia_de_lotes_ativos(
    fontes_temporais: list[dict[str, Any]],
    inventario_temporal: list[dict[str, Any]],
    data_ref: date,
) -> list[dict[str, Any]]:
    inventario_por_lote = {
        str(item.get('lote_id') or '').strip(): item
        for item in inventario_temporal
        if str(item.get('lote_id') or '').strip()
    }
    fontes_por_lote: dict[str, list[dict[str, Any]]] = {}
    for fonte in fontes_temporais:
        lote_id = str(fonte.get('lote_id') or fonte.get('fonte_id') or '').strip()
        if not lote_id:
            continue
        fontes_por_lote.setdefault(lote_id, []).append(fonte)

    fontes_adicionais: list[dict[str, Any]] = []
    for lote_id, fontes_lote in fontes_por_lote.items():
        if any(f.get('data_disponibilidade') == data_ref for f in fontes_lote):
            continue
        inventario_lote = inventario_por_lote.get(lote_id)
        if inventario_lote is None:
            continue
        valor_atual = _valor_atual_auditavel_inventario(inventario_lote, data_ref)
        if valor_atual < 1.0:
            continue
        candidatas = [
            f
            for f in fontes_lote
            if isinstance(f.get('data_disponibilidade'), date)
            and f.get('data_disponibilidade') > data_ref
            and f.get('disponivel_na_referencia') is True
        ]
        if not candidatas:
            continue
        primeira = min(candidatas, key=lambda f: f.get('data_disponibilidade'))
        fonte_ref = dict(primeira)
        fonte_ref['data_disponibilidade'] = data_ref
        fonte_ref['data_pagamento'] = data_ref
        fonte_ref['data_evento'] = data_ref
        fonte_ref['pagamento_id'] = None
        fonte_ref['valor_estimado'] = valor_atual
        fonte_ref['valor_bruto_disponivel'] = valor_atual
        fonte_ref['valor_liquido_disponivel'] = valor_atual
        fonte_ref['valor_disponivel'] = valor_atual
        fonte_ref['saldo_disponivel'] = valor_atual
        fonte_ref['saldo'] = valor_atual
        fonte_ref['valor'] = valor_atual
        fonte_ref['valor_atual_auditavel_origem'] = valor_atual
        fonte_ref['origem_canonica'] = 'inventario_canonico_reconciliado_data_referencia'
        fonte_ref['observacao_reconciliacao'] = 'snapshot_data_referencia_usa_somente_valor_atual_auditavel_inventario'
        fontes_adicionais.append(fonte_ref)
    return fontes_temporais + fontes_adicionais



def _indice_valores_historicos_replay(contexto: ContextoOperacionalCanonico) -> dict[str, dict[str, object]]:
    replay = getattr(contexto, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None)
    if log is None or not hasattr(log, 'to_dict'):
        return {}
    indice: dict[str, dict[str, object]] = {}
    for row in log.to_dict(orient='records'):
        despesa_id = str(row.get('Despesa ID') or row.get('despesa_id') or '').strip()
        if not despesa_id:
            continue
        indice[despesa_id] = {
            'Lote': row.get('Lote'),
            'Saldo Antes': row.get('Saldo Antes'),
            'Bruto': row.get('Bruto'),
            'Imposto': row.get('Imposto'),
            'Líquido': row.get('Liquido') if row.get('Liquido') is not None else row.get('Líquido'),
            'Saldo Remanescente': row.get('Saldo Remanescente'),
            'origem_valores_historicos': 'replay_passado_controlado.log_passado',
        }
    return indice

def construir_estado_temporal_inicial(contexto: ContextoOperacionalCanonico) -> EstadoTemporalInicial:
    data_ref = contexto.execucao.data_referencia
    gastos = contexto.dados_operacionais.gastos_canonicos
    recebidos = contexto.dados_operacionais.salarios_canonicos
    recebidos_auditaveis = getattr(getattr(contexto, 'recebidos_auditaveis', None), 'quadro_recebidos_auditaveis', None)
    inventario = contexto.dados_operacionais.inventario_canonico
    switching = getattr(contexto.dados_operacionais, 'switching_canonico', None)

    valores_historicos_por_pagamento = _indice_valores_historicos_replay(contexto)
    pagamentos_temporais = []
    for row in gastos.to_dict(orient='records'):
        pago = bool(row.get('pago'))
        data_pg = row.get('data')
        status = _status_data(data_pg, data_ref, pago)
        futuro = status == 'futuro'
        pagamento_id = row.get('despesa_id') or row.get('id') or f"pg_{len(pagamentos_temporais)+1:05d}"
        valores_historicos = valores_historicos_por_pagamento.get(str(pagamento_id), {}) if pago else {}
        fonte_historica = valores_historicos.get('Lote') or row.get('lote_usado_1') or row.get('lote_usado')
        pagamento_temporal = {
            'pagamento_id': pagamento_id,
            'data': data_pg,
            'descricao': row.get('descricao') or row.get('conta') or '',
            'valor': float(row.get('valor') or 0.0),
            'pago': pago,
            'status_temporal': status,
            'obrigacao_temporal': True,
            'fonte_informada': row.get('lote_usado_1') or row.get('lote_usado') or row.get('lote_origem'),
            'fonte_resolvida_historica': fonte_historica if pago else None,
            'fonte_a_decidir': bool(futuro or not pago),
            'vencido_na_referencia': status == 'vencido',
            'futuro_na_referencia': futuro,
            'bloqueios_preliminares': ['fonte_futura_a_decidir'] if futuro else [],
        }
        if valores_historicos:
            pagamento_temporal.update(valores_historicos)
        pagamentos_temporais.append(pagamento_temporal)

    inventario_temporal=[]
    for row in inventario.to_dict(orient='records'):
        status = _status_inventario_temporal(row)
        disponivel_ref = row.get('disponivel_na_data_referencia')
        if disponivel_ref is None:
            disponivel_ref = row.get('disponivel', True)
        inventario_temporal.append({
            'lote_id': row.get('lote_id'),
            'status_temporal': status,
            'disponibilidade': 'disponivel' if bool(disponivel_ref) else 'indisponivel',
            'migrado_por_switching': bool(row.get('migrado_por_switching')),
            'sintetico_pos_switching': bool(row.get('sintetico_pos_switching')),
            'origem_canonica': row.get('origem_canonica') or 'inventario_canonico',
            'data_recebimento': row.get('data_recebimento'),
            'data_aplicacao': row.get('data_aplicacao'),
            'valor_original': _float_seguro(row.get('valor_original'), 0.0),
            'investimento_bruto': _float_seguro(row.get('investimento_bruto'), 0.0),
            'valor_liquido_disponivel_atual': _float_seguro(row.get('valor_liquido_disponivel'), row.get('saldo_disponivel'), 0.0),
            'saldo_disponivel_atual': _float_seguro(row.get('saldo_disponivel'), row.get('saldo'), 0.0),
        })

    recebidos_temporais = _recebidos_temporais_canonicos(recebidos_auditaveis, data_ref)
    chaves_recebidos = {_chave_recebido_temporal(r) for r in recebidos_temporais}
    for row in recebidos.to_dict(orient='records'):
        data_rec = row.get('data_recebimento')
        if data_rec is not None and data_rec < data_ref:
            continue
        recebido_salario = _recebido_temporal_de_salario(row, data_ref)
        chave = _chave_recebido_temporal(recebido_salario)
        if chave in chaves_recebidos:
            continue
        recebidos_temporais.append(recebido_salario)
        chaves_recebidos.add(chave)

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
        data_disponibilidade = (
            f.get('data_pagamento')
            or f.get('data_evento')
            or f.get('data_disponibilidade')
            or f.get('data_referencia')
            or data_ref
        )
        fontes_temporais.append({
            'fonte_id': f.get('lote_id') or f.get('fonte_id'),
            'tipo_fonte': f.get('tipo_fonte') or 'lote',
            'data_disponibilidade': data_disponibilidade,
            'data_pagamento': f.get('data_pagamento'),
            'data_evento': f.get('data_evento'),
            'pagamento_id': f.get('pagamento_id'),
            'lote_id': f.get('lote_id'),
            'valor_estimado': valor_estimado,
            'valor_bruto_disponivel': _float_seguro(f.get('valor_bruto_disponivel'), 0.0),
            'valor_liquido_disponivel': _float_seguro(f.get('valor_liquido_disponivel'), 0.0),
            'status_temporal': 'disponivel' if disponivel_ref else 'indisponivel',
            'disponivel_na_referencia': disponivel_ref,
            'elegivel_na_data_pagamento': bool(f.get('elegivel_na_data_pagamento', disponivel_ref)),
            'motivo_indisponibilidade': f.get('motivo_bloqueio_temporal') or f.get('motivo_bloqueio') or '',
            'carencia_ate': f.get('carencia_ate_origem'),
            'origem_status': f.get('origem_status'),
            'origem_canonica': 'fontes_elegiveis_pagamento',
        })

    inventario_por_lote = {str(item.get('lote_id') or '').strip(): item for item in inventario_temporal if str(item.get('lote_id') or '').strip()}
    switching_temporal_realizado = []
    if switching is not None:
        for row in switching.to_dict(orient='records'):
            lote_origem = str(row.get('lote_origem') or '').strip()
            lote_destino = str(row.get('lote_destino') or '').strip()
            data_switching = row.get('data_switching')
            data_aplicacao = row.get('data_aplicacao')
            status_sw = _status_switching_materializacao(data_ref, data_switching, data_aplicacao)
            valor_migrado = _float_seguro(row.get('valor_liquido_origem'), 0.0)
            evento = {
                'switching_id': row.get('switching_id') or f"sw_{len(switching_temporal_realizado)+1:05d}",
                'lote_origem': lote_origem,
                'lote_destino': lote_destino,
                'produto_destino': row.get('produto_destino'),
                'data_switching': data_switching,
                'data_aplicacao': data_aplicacao,
                'valor_liquido_migrado': valor_migrado,
                'status_temporal': status_sw,
            }
            switching_temporal_realizado.append(evento)
            if status_sw != 'materializado':
                continue
            if lote_origem and lote_origem in inventario_por_lote:
                origem_item = inventario_por_lote[lote_origem]
                origem_item['status_temporal'] = 'migrado_por_switching' if origem_item.get('status_temporal') != 'exaurido' else 'exaurido_por_switching'
                origem_item['migrado_por_switching'] = True
                origem_item['disponibilidade'] = 'indisponivel'
            if lote_destino:
                destino_item = inventario_por_lote.get(lote_destino)
                if destino_item is None:
                    destino_item = {
                        'lote_id': lote_destino,
                        'status_temporal': 'ativo_pos_switching',
                        'disponibilidade': 'disponivel',
                        'migrado_por_switching': False,
                        'sintetico_pos_switching': True,
                        'origem_canonica': 'switching_canonico',
                    }
                    inventario_temporal.append(destino_item)
                    inventario_por_lote[lote_destino] = destino_item
                destino_item['status_temporal'] = 'ativo_pos_switching' if destino_item.get('status_temporal') not in {'exaurido', 'exaurido_por_switching'} else destino_item.get('status_temporal')
                destino_item['origem_canonica'] = 'switching_canonico'
                destino_item['sintetico_pos_switching'] = True
                destino_item['origem_switching'] = lote_origem
                destino_item['produto'] = row.get('produto_destino')
                destino_item['valor_liquido_migrado'] = valor_migrado
                destino_item['data_aplicacao'] = data_aplicacao
                destino_item['data_recebimento'] = row.get('data_recebimento')

    fontes_temporais = _reconciliar_fontes_temporais_com_inventario_final(fontes_temporais, inventario_temporal)
    fontes_temporais = _materializar_fontes_data_referencia_de_lotes_ativos(fontes_temporais, inventario_temporal, data_ref)

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
    switchings = list(estado.switching_temporal_realizado or [])
    qtd_switchings_materializados = sum(1 for s in switchings if s.get('status_temporal') == 'materializado')
    qtd_lotes_origem_migrados = sum(1 for l in estado.inventario_temporal if l.get('status_temporal') in {'migrado_por_switching', 'exaurido_por_switching'})
    qtd_lotes_destino_pos_switching = sum(1 for l in estado.inventario_temporal if l.get('sintetico_pos_switching') is True or l.get('origem_canonica') == 'switching_canonico')
    valor_liquido_migrado_total = round(sum(_float_seguro(s.get('valor_liquido_migrado'), 0.0) for s in switchings if s.get('status_temporal') == 'materializado'), 2)
    if any(not str(s.get('lote_origem') or '').strip() for s in switchings):
        bloqueios.append('switching_sem_lote_origem')
    if any(not str(s.get('lote_destino') or '').strip() for s in switchings):
        bloqueios.append('switching_sem_lote_destino')
    return {'ok': len(bloqueios)==0, 'bloqueios': bloqueios, 'resumo': {'qtd_pagamentos':len(estado.pagamentos_temporais),'qtd_futuros':len(futuros),'qtd_fontes_temporais':qtd_fontes,'qtd_fontes_disponiveis':qtd_fontes_disponiveis,'qtd_fontes_indisponiveis':qtd_fontes_indisponiveis,'qtd_fontes_valor_positivo':qtd_fontes_valor_positivo,'qtd_switchings_temporais':len(switchings),'qtd_switchings_materializados':qtd_switchings_materializados,'qtd_lotes_origem_migrados':qtd_lotes_origem_migrados,'qtd_lotes_destino_pos_switching':qtd_lotes_destino_pos_switching,'valor_liquido_migrado_total':valor_liquido_migrado_total}}
