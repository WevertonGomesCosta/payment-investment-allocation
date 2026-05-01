from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd
from nucleo.utilitarios_neutros import _coerce_date, _split_fontes_compostas


def _fonte_operacionalmente_disponivel_na_data_referencia(row: pd.Series | dict[str, Any], data_referencia: date) -> bool:
    tipo_fonte = str((row.get('tipo_fonte') if hasattr(row, 'get') else '') or '').strip()
    elegivel_pagamento = bool((row.get('elegivel_na_data_pagamento') if hasattr(row, 'get') else False))
    if not elegivel_pagamento and tipo_fonte != 'saldo_disponivel_geral':
        return False
    data_recebimento = _coerce_date(row.get('data_recebimento_origem') if hasattr(row, 'get') else None)
    data_aplicacao = _coerce_date(row.get('data_aplicacao_origem') if hasattr(row, 'get') else None)
    if tipo_fonte in {'recebido_disponivel', 'caixa_pre_aplicacao'} and data_recebimento is not None and data_recebimento > data_referencia:
        return False
    if tipo_fonte == 'lote_resgatavel' and data_aplicacao is not None and data_aplicacao > data_referencia:
        return False
    return True


@dataclass(slots=True)
class PacoteMotorRecomendacaoPagamentosSwitchingV1:
    quadro_recomendacoes: pd.DataFrame
    auditoria: dict[str, Any]


def _classe_rank(classe: str) -> int:
    mapa = {'PROTEGIDA': 0, 'SEMIPROTEGIDA': 1, 'FLEXIVEL': 2}
    return mapa.get(str(classe or ''), 9)


def _estrategia_rank(estrategia: str) -> int:
    ordem = {
        'sem_switching': 0,
        'switching_simples': 1,
        'combinacao_minima': 2,
    }
    return ordem.get(str(estrategia or ''), 9)


def _materialidade_switching(valor_pagamento: float) -> float:
    return round(max(20.0, 0.005 * float(valor_pagamento or 0.0)), 2)


def _selecionar_backup(candidatos_eligiveis: pd.DataFrame, lote_principal: str, fonte_principal: str) -> tuple[str, str]:
    for _, row in candidatos_eligiveis.iterrows():
        lote = str(row.get('lote_id') or '').strip()
        fonte = str(row.get('fonte_id') or '').strip()
        if lote and lote == lote_principal:
            continue
        if fonte and fonte == fonte_principal:
            continue
        return lote or str(row.get('produto_nome_canonico') or ''), fonte
    return '', ''


def _rotulo_candidato(row: pd.Series | dict[str, Any]) -> str:
    lote = str(row.get('lote_id') or '').strip()
    if lote:
        return lote
    return str(row.get('produto_nome_canonico') or row.get('fonte_id') or '').strip()


def _data_switching_janela(row: pd.Series | dict[str, Any]) -> date | None:
    for campo in ('data_sugerida_switching', 'data_evento', 'data_execucao', 'data'):
        valor = _coerce_date(row.get(campo) if hasattr(row, 'get') else None)
        if valor is not None:
            return valor
    return None


def _mapa_switching_janela_por_lote(quadro_switching: pd.DataFrame, switching_economico_shadow: Any) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}

    def _registrar(row: dict[str, Any]) -> None:
        lote = str(row.get('lote_id') or row.get('Lote origem') or '').strip()
        if not lote:
            return
        data_sw = _data_switching_janela(row)
        if data_sw is None:
            return
        atual = mapa.get(lote)
        if atual is None or data_sw < atual['data_switching_janela']:
            mapa[lote] = {
                'data_switching_janela': data_sw,
                'destino_janela': str(
                    row.get('produto_destino_nome')
                    or row.get('produto_destino_key')
                    or row.get('Destino')
                    or ''
                ).strip(),
            }

    if quadro_switching is not None and not quadro_switching.empty:
        for _, row in quadro_switching.iterrows():
            recomendado = bool(row.get('recomendado_shadow', row.get('elegivel_shadow', False)))
            if not recomendado:
                continue
            _registrar(row.to_dict() if hasattr(row, 'to_dict') else dict(row))

    plano_shadow = getattr(switching_economico_shadow, 'plano_shadow', None) if switching_economico_shadow is not None else None
    if isinstance(plano_shadow, pd.DataFrame) and len(plano_shadow):
        for _, row in plano_shadow.iterrows():
            recomendado = bool(row.get('recomendado_shadow', True))
            if not recomendado:
                continue
            _registrar(row.to_dict())
    return mapa


def _normalizar_chave_lote(valor: Any) -> str:
    txt = str(valor or '').strip().lower()
    txt = txt.replace('lote ', '').replace('lote', '').strip()
    return ''.join(ch for ch in txt if ch.isalnum())


def _info_switching_lote(mapa_switching_janela: dict[str, dict[str, Any]], lote_id: Any) -> dict[str, Any]:
    chave = str(lote_id or '').strip()
    if not chave:
        return {}
    if chave in mapa_switching_janela:
        return mapa_switching_janela.get(chave, {})
    norm = _normalizar_chave_lote(chave)
    if not norm:
        return {}
    for k, v in mapa_switching_janela.items():
        if _normalizar_chave_lote(k) == norm:
            return v
    return {}


def _aplicar_saldo_temporal_candidatos(
    candidatos: pd.DataFrame,
    saldo_residual_temporal_por_lote: dict[str, float],
) -> pd.DataFrame:
    if candidatos is None or candidatos.empty:
        return candidatos
    ajustado = candidatos.copy()
    valores = []
    elegiveis = []
    for _, row in ajustado.iterrows():
        lote = str(row.get('lote_id') or '').strip()
        valor = round(float(row.get('valor_liquido_disponivel') or 0.0), 2)
        if lote:
            valor = round(min(valor, float(saldo_residual_temporal_por_lote.get(lote, valor) or 0.0)), 2)
        valores.append(valor)
        elegiveis.append(valor > 0.01)
    ajustado['valor_liquido_disponivel'] = valores
    return ajustado[elegiveis].copy()


def _materializar_fontes_pos_switching_janela(
    candidatos: pd.DataFrame,
    mapa_switching_janela: dict[str, dict[str, Any]],
    data_pagamento: date | None,
    saldo_referencia_por_lote: dict[str, float] | None = None,
) -> pd.DataFrame:
    if candidatos is None or candidatos.empty or data_pagamento is None or not mapa_switching_janela:
        return candidatos, {}
    base = candidatos.copy()
    linhas_pos_switching: list[dict[str, Any]] = []
    diagnostico: dict[str, dict[str, Any]] = {}
    mapa_mes_pt = {
        1: 'jan.', 2: 'fev.', 3: 'mar.', 4: 'abr.', 5: 'mai.', 6: 'jun.',
        7: 'jul.', 8: 'ago.', 9: 'set.', 10: 'out.', 11: 'nov.', 12: 'dez.',
    }

    def _fmt_valor_lote(valor: float) -> str:
        v = round(float(valor or 0.0), 2)
        if abs(v - int(v)) <= 0.0001:
            return f"{int(v)}"
        return f"{v:.2f}".replace('.', ',')

    grupos: dict[tuple[str, str], dict[str, Any]] = {}
    lotes_processados: set[str] = set()
    for _, row in base.iterrows():
        lote = str(row.get('lote_id') or '').strip()
        if not lote:
            continue
        lotes_processados.add(lote)
        info_janela = _info_switching_lote(mapa_switching_janela, lote)
        data_sw = info_janela.get('data_switching_janela')
        if data_sw is None:
            continue
        if data_sw > data_pagamento:
            diagnostico[lote] = {
                'pos_sw_tentativa': True,
                'pos_sw_criada': False,
                'fonte_pos_sw': '',
                'saldo_pos_sw': 0.0,
                'motivo_pos_sw': 'nao_criada',
                'destino_pos_sw': str(info_janela.get('destino_janela') or '').strip(),
                'origem_saldo_pos_sw': 'nao_encontrado',
                'saldo_pos_sw_bruto_candidato': 0.0,
                'saldo_pos_sw_liquido_candidato': 0.0,
                'data_base_saldo_pos_sw': data_pagamento,
                'motivo_saldo_pos_sw': 'saldo_zero_ou_ausente',
            }
            continue
        valor = round(float(row.get('valor_liquido_disponivel') or row.get('valor_liquido') or 0.0), 2)
        if valor <= 0.01:
            diagnostico[lote] = {
                'pos_sw_tentativa': True,
                'pos_sw_criada': False,
                'fonte_pos_sw': '',
                'saldo_pos_sw': valor,
                'motivo_pos_sw': 'sem_saldo_confiavel',
                'destino_pos_sw': str(info_janela.get('destino_janela') or '').strip(),
                'origem_saldo_pos_sw': 'saldo_temporal_lote',
                'saldo_pos_sw_bruto_candidato': round(float(row.get('valor_bruto_disponivel') or row.get('valor_bruto') or 0.0), 2),
                'saldo_pos_sw_liquido_candidato': valor,
                'data_base_saldo_pos_sw': row.get('data_pagamento') or data_pagamento,
                'motivo_saldo_pos_sw': 'saldo_zero_ou_ausente',
            }
            continue
        destino = str(info_janela.get('destino_janela') or '').strip()
        data_sw_txt = data_sw.isoformat() if hasattr(data_sw, 'isoformat') else str(data_sw)
        chave = (data_sw_txt, destino)
        grupo = grupos.setdefault(chave, {
            'data_sw': data_sw,
            'destino': destino,
            'valor_liquido_total': 0.0,
            'valor_bruto_total': 0.0,
            'lotes_origem': [],
            'base_row': row.to_dict(),
        })
        grupo['valor_liquido_total'] = round(float(grupo['valor_liquido_total']) + valor, 2)
        grupo['valor_bruto_total'] = round(float(grupo['valor_bruto_total']) + float(row.get('valor_bruto_disponivel') or row.get('valor_bruto') or valor), 2)
        grupo['lotes_origem'].append(lote)
        diagnostico[lote] = {
            'pos_sw_tentativa': True,
            'pos_sw_criada': True,
            'fonte_pos_sw': '',
            'lote_nome_operacional_pos_sw': '',
            'saldo_pos_sw': valor,
            'motivo_pos_sw': 'materializada',
            'destino_pos_sw': destino,
            'origem_saldo_pos_sw': 'saldo_temporal_lote',
            'saldo_pos_sw_bruto_candidato': round(float(row.get('valor_bruto_disponivel') or row.get('valor_bruto') or valor), 2),
            'saldo_pos_sw_liquido_candidato': valor,
            'data_base_saldo_pos_sw': row.get('data_pagamento') or data_pagamento,
            'motivo_saldo_pos_sw': 'saldo_encontrado',
        }
    for (data_sw_txt, destino), grupo in grupos.items():
        valor_total = round(float(grupo.get('valor_liquido_total') or 0.0), 2)
        if valor_total <= 0.01:
            continue
        data_sw = grupo.get('data_sw')
        lotes_origem = [str(x) for x in grupo.get('lotes_origem', []) if str(x).strip()]
        mes_sw = mapa_mes_pt.get(data_sw.month, 'n/d') if hasattr(data_sw, 'month') else 'n/d'
        lote_nome_operacional = f"Lote {_fmt_valor_lote(valor_total)} {mes_sw}"
        fonte_pos_sw = f"pos_switch::{data_sw_txt}::{destino or 'destino'}::{' + '.join(lotes_origem)}"
        linha = dict(grupo.get('base_row') or {})
        linha['lote_id'] = fonte_pos_sw
        linha['lote_id_sintetico'] = fonte_pos_sw
        linha['lote_nome_operacional'] = lote_nome_operacional
        linha['lote_origem_pos_switching'] = ' + '.join(lotes_origem)
        linha['fonte_origem_pos_switching'] = 'estado_pos_switching_janela'
        linha['destino_switching_janela'] = destino
        linha['data_switching_janela'] = data_sw
        linha['valor_liquido_disponivel'] = valor_total
        linha['valor_bruto_disponivel'] = round(float(grupo.get('valor_bruto_total') or valor_total), 2)
        if destino:
            linha['produto_nome_canonico'] = destino
        linhas_pos_switching.append(linha)
        for lote in lotes_origem:
            if lote in diagnostico:
                diagnostico[lote]['fonte_pos_sw'] = fonte_pos_sw
                diagnostico[lote]['lote_nome_operacional_pos_sw'] = lote_nome_operacional
                diagnostico[lote]['saldo_pos_sw'] = valor_total
                diagnostico[lote]['saldo_pos_sw_liquido_candidato'] = valor_total
                diagnostico[lote]['saldo_pos_sw_bruto_candidato'] = round(float(grupo.get('valor_bruto_total') or valor_total), 2)

    saldo_ref = saldo_referencia_por_lote or {}
    for lote, info_janela in mapa_switching_janela.items():
        lote = str(lote or '').strip()
        if not lote or lote in lotes_processados:
            continue
        data_sw = info_janela.get('data_switching_janela')
        if data_sw is None or data_pagamento is None or data_sw > data_pagamento:
            continue
        valor_ref = round(float(saldo_ref.get(lote, 0.0) or 0.0), 2)
        diagnostico[lote] = {
            'pos_sw_tentativa': True,
            'pos_sw_criada': bool(valor_ref > 0.01),
            'fonte_pos_sw': '',
            'lote_nome_operacional_pos_sw': '',
            'saldo_pos_sw': valor_ref,
            'motivo_pos_sw': 'materializada' if valor_ref > 0.01 else 'sem_saldo_confiavel',
            'destino_pos_sw': str(info_janela.get('destino_janela') or '').strip(),
            'origem_saldo_pos_sw': 'saldo_temporal_lote',
            'saldo_pos_sw_bruto_candidato': valor_ref,
            'saldo_pos_sw_liquido_candidato': valor_ref,
            'data_base_saldo_pos_sw': data_sw,
            'motivo_saldo_pos_sw': 'ok' if valor_ref > 0.01 else 'saldo_zero_ou_ausente',
        }
        if valor_ref <= 0.01:
            continue
        data_sw_txt = data_sw.isoformat() if hasattr(data_sw, 'isoformat') else str(data_sw)
        destino = str(info_janela.get('destino_janela') or '').strip()
        mes_sw = mapa_mes_pt.get(data_sw.month, 'n/d') if hasattr(data_sw, 'month') else 'n/d'
        lote_nome_operacional = f"Lote {_fmt_valor_lote(valor_ref)} {mes_sw}"
        fonte_pos_sw = f"pos_switch::{data_sw_txt}::{destino or 'destino'}::{lote}"
        diagnostico[lote]['fonte_pos_sw'] = fonte_pos_sw
        diagnostico[lote]['lote_nome_operacional_pos_sw'] = lote_nome_operacional
        linha = {'lote_id': fonte_pos_sw, 'lote_id_sintetico': fonte_pos_sw, 'lote_nome_operacional': lote_nome_operacional, 'lote_origem_pos_switching': lote, 'fonte_origem_pos_switching': 'estado_pos_switching_janela', 'destino_switching_janela': destino, 'data_switching_janela': data_sw, 'valor_liquido_disponivel': valor_ref, 'valor_bruto_disponivel': valor_ref, 'produto_nome_canonico': destino}
        linhas_pos_switching.append(linha)
    if not linhas_pos_switching:
        return candidatos, diagnostico
    return pd.concat([base, pd.DataFrame(linhas_pos_switching)], ignore_index=True), diagnostico


def _consumir_saldo_temporal(
    saldo_residual_temporal_por_lote: dict[str, float],
    fontes: list[str],
    valor_pagamento: float,
) -> tuple[float, float]:
    restante = round(float(valor_pagamento or 0.0), 2)
    consumido_total = 0.0
    saldo_pos_ultimo = 0.0
    for fonte in fontes:
        if restante <= 0.01:
            break
        lote = str(fonte or '').strip()
        if not lote or lote not in saldo_residual_temporal_por_lote:
            continue
        saldo_atual = round(float(saldo_residual_temporal_por_lote.get(lote, 0.0) or 0.0), 2)
        if saldo_atual <= 0.01:
            saldo_residual_temporal_por_lote[lote] = 0.0
            continue
        consumo = round(min(restante, saldo_atual), 2)
        saldo_novo = round(max(saldo_atual - consumo, 0.0), 2)
        saldo_residual_temporal_por_lote[lote] = saldo_novo
        consumido_total = round(consumido_total + consumo, 2)
        saldo_pos_ultimo = saldo_novo
        restante = round(max(restante - consumo, 0.0), 2)
    return consumido_total, saldo_pos_ultimo


def _melhor_switching_para_pagamento(
    candidatos_eligiveis: pd.DataFrame,
    quadro_switching: pd.DataFrame,
    *,
    data_referencia: date,
    valor_pagamento: float,
    saldo_residual_temporal_por_lote: dict[str, float],
    saldo_inicial_temporal_por_lote: dict[str, float],
) -> dict[str, Any]:
    if quadro_switching is None or quadro_switching.empty or candidatos_eligiveis.empty:
        return {}
    dias_ate = max((_coerce_date(candidatos_eligiveis.iloc[0].get('data_pagamento')) - data_referencia).days, 0)
    if dias_ate <= 0:
        return {}
    horizonte_ref = max((_coerce_date(quadro_switching.iloc[0].get('data_horizonte')) - data_referencia).days, 1)
    melhores: list[dict[str, Any]] = []
    for _, cand in candidatos_eligiveis.iterrows():
        lote = str(cand.get('lote_id') or '').strip()
        if not lote:
            continue
        subset = quadro_switching[(quadro_switching['lote_id'] == lote) & (quadro_switching['elegivel_shadow'] == True)].copy()
        if subset.empty:
            continue
        subset = subset[subset['carencia_dias_destino'].fillna(10**9) <= dias_ate]
        if subset.empty:
            continue
        subset = subset.sort_values(by=['recomendado_shadow', 'ganho_liquido_estimado', 'score_switch_shadow'], ascending=[False, False, False], kind='stable')
        melhor = subset.iloc[0].to_dict()
        valor_base = round(float(cand.get('valor_liquido_disponivel') or 0.0), 2)
        valor_inicial_temporal = round(float(saldo_inicial_temporal_por_lote.get(lote, valor_base) or 0.0), 2)
        valor_residual_temporal = round(min(valor_base, float(saldo_residual_temporal_por_lote.get(lote, valor_base) or 0.0)), 2)
        if valor_residual_temporal <= 0.0:
            continue
        fracao_residual_temporal = min(max((valor_residual_temporal / valor_inicial_temporal), 0.0), 1.0) if valor_inicial_temporal > 0 else 0.0
        ganho_horizonte = float(melhor.get('ganho_liquido_estimado') or 0.0)
        ganho_horizonte_ajustado = ganho_horizonte * fracao_residual_temporal
        ganho_ate_pagamento = round(ganho_horizonte_ajustado * min(dias_ate, horizonte_ref) / horizonte_ref, 2)
        cobertura = round(min(valor_pagamento, valor_residual_temporal + max(ganho_ate_pagamento, 0.0)), 2)
        melhores.append({
            'estrategia': 'switching_simples',
            'lote_origem_switching': lote,
            'produto_destino_switching': str(melhor.get('produto_destino_nome') or ''),
            'produto_destino_key': str(melhor.get('produto_destino_key') or ''),
            'data_sugerida_switching': data_referencia,
            'ganho_liquido_estimado_switching': ganho_ate_pagamento,
            'cobertura_esperada': cobertura,
            'cobertura_integral': bool(cobertura + 0.009 >= valor_pagamento),
            'fonte_origem_id': str(cand.get('fonte_id') or ''),
            'tipo_fonte_origem': str(cand.get('tipo_fonte') or ''),
            'lote_recomendado': lote,
            'lote_reserva': '',
            'fonte_reserva_id': '',
            'valor_liquido_origem': valor_base,
            'valor_residual_temporal_lote': valor_residual_temporal,
            'fracao_residual_temporal_lote': round(fracao_residual_temporal, 6),
            'score_switch_shadow': round(float(melhor.get('score_switch_shadow') or 0.0), 4),
            'ordem_switch_shadow': int(melhor.get('ordem_prioridade') or 0) if str(melhor.get('ordem_prioridade') or '').strip() else 0,
        })
    if not melhores:
        return {}
    melhores.sort(key=lambda x: (not x['cobertura_integral'], -x['cobertura_esperada'], -x['ganho_liquido_estimado_switching']))
    return melhores[0]


def carregar_motor_recomendacao_pagamentos_switching_v1(
    dados_operacionais: Any,
    fontes_elegiveis_pagamento: Any,
    saldo_disponivel_geral: Any,
    decisao_local_v1: Any,
    recomputacao_sequencial_central_v1: Any,
    switching_economico_shadow: Any,
    *,
    data_referencia: date,
) -> PacoteMotorRecomendacaoPagamentosSwitchingV1:
    gastos = dados_operacionais.gastos_canonicos.copy()
    gastos = gastos[gastos['futuro_ou_pendente_na_data_referencia'] == True].copy()
    gastos = gastos.sort_values(by=['data', 'despesa_id'], kind='stable')

    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_fontes = quadro_fontes[quadro_fontes.apply(lambda row: _fonte_operacionalmente_disponivel_na_data_referencia(row, data_referencia), axis=1)].copy()
    quadro_fontes['valor_liquido_disponivel'] = quadro_fontes['valor_liquido_disponivel'].fillna(0.0).astype(float)

    quadro_local = decisao_local_v1.quadro_decisao_local_v1.copy() if decisao_local_v1 is not None else pd.DataFrame()
    quadro_central = recomputacao_sequencial_central_v1.quadro_recomputacao_sequencial_central.copy() if recomputacao_sequencial_central_v1 is not None else pd.DataFrame()
    quadro_switching = switching_economico_shadow.quadro_oportunidades.copy() if switching_economico_shadow is not None else pd.DataFrame()
    mapa_switching_janela = _mapa_switching_janela_por_lote(quadro_switching, switching_economico_shadow)

    quadro_fontes_temporais = quadro_fontes[quadro_fontes['lote_id'].fillna('').astype(str).str.strip() != ''].copy()
    saldo_inicial_temporal_por_lote = {
        str(lote): round(float(valor or 0.0), 2)
        for lote, valor in quadro_fontes_temporais.groupby('lote_id')['valor_liquido_disponivel'].max().items()
    }
    saldo_residual_temporal_por_lote = dict(saldo_inicial_temporal_por_lote)

    mapa_local = {str(r.get('pagamento_id') or ''): r for _, r in quadro_local.iterrows()}
    mapa_central = {str(r.get('pagamento_id') or ''): r for _, r in quadro_central.iterrows()}

    linhas: list[dict[str, Any]] = []
    contagem = {'sem_switching': 0, 'switching_simples': 0, 'combinacao_minima': 0}
    switching_acionado = 0
    combinacao_acionada = 0
    ganhos_switch = 0.0

    for item in gastos.to_dict('records'):
        pagamento_id = str(item.get('despesa_id') or '').strip()
        data_pagamento = _coerce_date(item.get('data'))
        valor_pagamento = round(float(item.get('valor') or 0.0), 2)
        row_local = mapa_local.get(pagamento_id, {})
        row_central = mapa_central.get(pagamento_id, {})
        classe = str(row_central.get('classe_pagamento_operacional') or '')
        subclasse = str(row_central.get('subclasse_pagamento_operacional') or '')

        candidatos = quadro_fontes[quadro_fontes['pagamento_id'] == pagamento_id].copy()
        candidatos, diagnostico_pos_switch = _materializar_fontes_pos_switching_janela(
            candidatos,
            mapa_switching_janela,
            data_pagamento,
            saldo_referencia_por_lote=saldo_residual_temporal_por_lote,
        )
        lotes_descartados_pos_sw: set[str] = set()
        if data_pagamento is not None and not candidatos.empty:
            def _manter_candidato(r: pd.Series) -> bool:
                lote_id = str(r.get('lote_id') or '').strip()
                if lote_id.startswith('pos_switch::'):
                    return True
                info = _info_switching_lote(mapa_switching_janela, lote_id)
                bloqueado = bool(info and info.get('data_switching_janela') is not None and info.get('data_switching_janela') <= data_pagamento)
                if bloqueado:
                    lotes_descartados_pos_sw.add(lote_id)
                return not bloqueado

            candidatos = candidatos[candidatos.apply(_manter_candidato, axis=1)].copy()
        candidatos = _aplicar_saldo_temporal_candidatos(candidatos, saldo_residual_temporal_por_lote)
        candidatos = candidatos.sort_values(by=['valor_liquido_disponivel', 'lote_id'], ascending=[False, True], kind='stable')

        lote_no_switch = str(row_central.get('lote_final_central') or row_local.get('lote_id_escolhido') or '')
        fonte_no_switch = str(row_central.get('fonte_final_id') or row_local.get('fonte_escolhida_id') or '')
        cobertura_no_switch = round(float(row_central.get('liquido_central') or 0.0), 2)
        score_no_switch = round(float(row_central.get('score_proxy_central') or row_local.get('custo_economico_proxy') or 0.0), 4)
        integral_no_switch = bool(row_central.get('pagamento_totalmente_coberto_central') or row_local.get('pagamento_totalmente_coberto'))
        lote_reserva, fonte_reserva = _selecionar_backup(candidatos, lote_no_switch, fonte_no_switch)

        estrategia_base = {
            'estrategia': 'sem_switching',
            'lote_recomendado': lote_no_switch,
            'lote_reserva': lote_reserva,
            'fonte_reserva_id': fonte_reserva,
            'necessidade_switching': False,
            'lote_origem_switching': '',
            'produto_destino_switching': '',
            'data_sugerida_switching': None,
            'ganho_liquido_estimado_switching': 0.0,
            'cobertura_esperada': cobertura_no_switch,
            'cobertura_integral': integral_no_switch,
            'score_base': score_no_switch,
            'tipo_fonte_recomendada': str(row_central.get('tipo_fonte_final') or row_local.get('tipo_fonte_escolhida') or ''),
            'motivo_recomendacao': 'usar a recomendação central atual sem switching',
            'comparador_rank': (0 if integral_no_switch else 1, -cobertura_no_switch, 0.0, score_no_switch),
        }
        info_janela_lote_base = _info_switching_lote(mapa_switching_janela, lote_no_switch)
        if (
            lote_no_switch
            and data_pagamento is not None
            and info_janela_lote_base
            and info_janela_lote_base.get('data_switching_janela') is not None
            and info_janela_lote_base.get('data_switching_janela') <= data_pagamento
        ):
            estrategia_base['lote_recomendado'] = 'não determinado'
            estrategia_base['motivo_recomendacao'] = 'lote original migrado por switching da janela antes do pagamento'

        estrategia_switch = _melhor_switching_para_pagamento(
            candidatos,
            quadro_switching,
            data_referencia=data_referencia,
            valor_pagamento=valor_pagamento,
            saldo_residual_temporal_por_lote=saldo_residual_temporal_por_lote,
            saldo_inicial_temporal_por_lote=saldo_inicial_temporal_por_lote,
        )
        if estrategia_switch:
            lote_reserva_sw, fonte_reserva_sw = _selecionar_backup(candidatos, estrategia_switch.get('lote_recomendado', ''), estrategia_switch.get('fonte_origem_id', ''))
            estrategia_switch.update({
                'necessidade_switching': True,
                'lote_reserva': lote_reserva_sw,
                'fonte_reserva_id': fonte_reserva_sw,
                'score_base': score_no_switch,
                'motivo_recomendacao': 'switching simples com melhor oportunidade shadow elegível até a data do pagamento',
                'comparador_rank': (
                    0 if estrategia_switch.get('cobertura_integral') else 1,
                    -float(estrategia_switch.get('cobertura_esperada') or 0.0),
                    -float(estrategia_switch.get('ganho_liquido_estimado_switching') or 0.0),
                    score_no_switch,
                ),
            })
            data_sw = _coerce_date(estrategia_switch.get('data_sugerida_switching'))
            if data_sw is not None and data_pagamento is not None and data_sw <= data_pagamento:
                estrategia_switch['lote_recomendado_rotulo'] = _rotulo_candidato({
                    'lote_id': '',
                    'produto_nome_canonico': estrategia_switch.get('produto_destino_switching') or 'não determinado',
                    'fonte_id': estrategia_switch.get('fonte_origem_id') or '',
                }) or 'não determinado'

        estrategia_combo: dict[str, Any] = {}
        top = []
        cobertura_acumulada = 0.0
        for cand_combo in candidatos.to_dict('records'):
            valor_cand_combo = round(float(cand_combo.get('valor_liquido_disponivel') or 0.0), 2)
            if valor_cand_combo <= 0.01:
                continue
            top.append(cand_combo)
            cobertura_acumulada = round(cobertura_acumulada + valor_cand_combo, 2)
            if cobertura_acumulada + 0.009 >= valor_pagamento:
                break
        if len(top) >= 2:
            principal = top[0]
            reservas = top[1:]
            cobertura_combo = round(min(valor_pagamento, cobertura_acumulada), 2)
            rotulos_combo = [_rotulo_candidato(cand) for cand in top]
            fontes_reserva = [str(cand.get('fonte_id') or '') for cand in reservas]
            estrategia_combo = {
                'estrategia': 'combinacao_minima',
                'lote_recomendado': ' + '.join([rotulo for rotulo in rotulos_combo if rotulo]),
                'lote_reserva': ' + '.join([rotulo for rotulo in rotulos_combo[1:] if rotulo]),
                'fonte_reserva_id': ' + '.join([fonte for fonte in fontes_reserva if fonte]),
                'necessidade_switching': False,
                'lote_origem_switching': '',
                'produto_destino_switching': '',
                'data_sugerida_switching': None,
                'ganho_liquido_estimado_switching': 0.0,
                'cobertura_esperada': cobertura_combo,
                'cobertura_integral': bool(cobertura_combo + 0.009 >= valor_pagamento),
                'score_base': score_no_switch,
                'tipo_fonte_recomendada': 'combinacao_minima_fontes',
                'motivo_recomendacao': 'combinação mínima sequencial de fontes para cobrir integralmente o pagamento',
                'comparador_rank': (
                    0 if cobertura_combo + 0.009 >= valor_pagamento else 1,
                    -cobertura_combo,
                    0.0,
                    score_no_switch,
                ),
            }

        candidatos_estrategia = [estrategia_base]
        limiar_switch = _materialidade_switching(valor_pagamento)
        if estrategia_switch and float(estrategia_switch.get('ganho_liquido_estimado_switching') or 0.0) >= limiar_switch:
            candidatos_estrategia.append(estrategia_switch)
        if estrategia_combo:
            candidatos_estrategia.append(estrategia_combo)

        dias_ate_pagamento = max((data_pagamento - data_referencia).days, 0) if data_pagamento is not None else 0
        limiar_switch_forte = round(max(50.0, 0.02 * valor_pagamento), 2)
        melhoria_minima_cobertura = round(max(25.0, 0.05 * valor_pagamento), 2)
        fallback_automatico_sem_switching = False
        motivo_fallback_automatico = ''

        # Regra operacional recalibrada: switching simples só compete quando há saldo temporal residual auditável.
        melhor = estrategia_base
        if estrategia_base.get('cobertura_integral'):
            if estrategia_switch:
                ganho_switch = float(estrategia_switch.get('ganho_liquido_estimado_switching') or 0.0)
                switch_cobre = bool(estrategia_switch.get('cobertura_integral'))
                cobertura_switch = float(estrategia_switch.get('cobertura_esperada') or 0.0)
                valor_residual_temporal = float(estrategia_switch.get('valor_residual_temporal_lote') or 0.0)
                if classe == 'PROTEGIDA':
                    if dias_ate_pagamento >= 45 and switch_cobre and ganho_switch >= limiar_switch_forte and cobertura_switch >= cobertura_no_switch and valor_residual_temporal >= valor_pagamento:
                        melhor = estrategia_switch
                    elif valor_residual_temporal < valor_pagamento:
                        fallback_automatico_sem_switching = True
                        motivo_fallback_automatico = 'fallback_sem_switching_por_residual_temporal_insuficiente'
                else:
                    if dias_ate_pagamento >= 30 and switch_cobre and ganho_switch >= limiar_switch_forte and cobertura_switch >= cobertura_no_switch and valor_residual_temporal >= valor_pagamento:
                        melhor = estrategia_switch
                    elif valor_residual_temporal < valor_pagamento:
                        fallback_automatico_sem_switching = True
                        motivo_fallback_automatico = 'fallback_sem_switching_por_residual_temporal_insuficiente'
        else:
            candidatos_validos = [estrategia_base]
            if estrategia_combo:
                candidatos_validos.append(estrategia_combo)
            if estrategia_switch:
                ganho_switch = float(estrategia_switch.get('ganho_liquido_estimado_switching') or 0.0)
                cobertura_switch = float(estrategia_switch.get('cobertura_esperada') or 0.0)
                valor_residual_temporal = float(estrategia_switch.get('valor_residual_temporal_lote') or 0.0)
                melhoria_cobertura = round(cobertura_switch - cobertura_no_switch, 2)
                if dias_ate_pagamento >= 21 and ganho_switch >= limiar_switch and melhoria_cobertura >= melhoria_minima_cobertura and valor_residual_temporal >= valor_pagamento:
                    candidatos_validos.append(estrategia_switch)
                else:
                    fallback_automatico_sem_switching = True
                    motivos = []
                    if dias_ate_pagamento < 21:
                        motivos.append('janela_curta')
                    if ganho_switch < limiar_switch:
                        motivos.append('ganho_abaixo_materialidade')
                    if melhoria_cobertura < melhoria_minima_cobertura:
                        motivos.append('melhoria_cobertura_insuficiente')
                    if valor_residual_temporal < valor_pagamento:
                        motivos.append('residual_temporal_insuficiente')
                    motivo_fallback_automatico = 'fallback_sem_switching_por_' + '_'.join(motivos or ['comparador_local'])
            melhor = min(candidatos_validos, key=lambda x: x['comparador_rank'])
            if estrategia_combo and estrategia_combo.get('cobertura_integral') and not bool(getattr(melhor, 'get', lambda *_: False)('cobertura_integral')):
                melhor = estrategia_combo

        lote_recomendado_candidato = str(melhor.get('lote_recomendado') or '').strip()
        lote_recomendado_origem = lote_recomendado_candidato.replace('pos_switch::', '') if lote_recomendado_candidato.startswith('pos_switch::') else lote_recomendado_candidato
        info_janela_lote_final = _info_switching_lote(mapa_switching_janela, lote_recomendado_candidato)
        bloqueio_janela = bool(
            lote_recomendado_candidato
            and data_pagamento is not None
            and info_janela_lote_final
            and info_janela_lote_final.get('data_switching_janela') is not None
            and info_janela_lote_final.get('data_switching_janela') <= data_pagamento
        )
        if bloqueio_janela:
            melhor['lote_recomendado'] = 'não determinado'
            melhor['lote_recomendado_consumivel'] = ''
            melhor['motivo_recomendacao'] = 'lote original migrado por switching da janela antes do pagamento'
        fonte_pos_switching = lote_recomendado_candidato.startswith('pos_switch::')
        lote_origem_pos_switching = str(melhor.get('lote_origem_pos_switching') or (lote_recomendado_candidato.replace('pos_switch::', '') if fonte_pos_switching else '')).strip()
        diag_pos_sw = diagnostico_pos_switch.get(lote_recomendado_origem, {})
        pos_sw_tentativa = bool(diag_pos_sw.get('pos_sw_tentativa'))
        fonte_pos_sw = str(diag_pos_sw.get('fonte_pos_sw') or '')
        lote_nome_operacional_pos_sw = str(diag_pos_sw.get('lote_nome_operacional_pos_sw') or '')
        saldo_pos_sw = round(float(diag_pos_sw.get('saldo_pos_sw') or 0.0), 2)
        motivo_pos_sw = str(diag_pos_sw.get('motivo_pos_sw') or '')
        origem_saldo_pos_sw = str(diag_pos_sw.get('origem_saldo_pos_sw') or '')
        saldo_pos_sw_bruto_candidato = round(float(diag_pos_sw.get('saldo_pos_sw_bruto_candidato') or 0.0), 2)
        saldo_pos_sw_liquido_candidato = round(float(diag_pos_sw.get('saldo_pos_sw_liquido_candidato') or 0.0), 2)
        data_base_saldo_pos_sw = diag_pos_sw.get('data_base_saldo_pos_sw')
        motivo_saldo_pos_sw = str(diag_pos_sw.get('motivo_saldo_pos_sw') or '')
        if lote_recomendado_origem in lotes_descartados_pos_sw and motivo_pos_sw in {'', 'nao_criada'}:
            motivo_pos_sw = 'descartada_por_filtro'
        if not pos_sw_tentativa and lote_recomendado_origem in mapa_switching_janela:
            motivo_pos_sw = 'nao_criada'
        if not motivo_pos_sw:
            motivo_pos_sw = 'n/d'
        if not origem_saldo_pos_sw:
            origem_saldo_pos_sw = 'nao_encontrado' if lote_recomendado_origem in mapa_switching_janela else 'n/d'
        if not motivo_saldo_pos_sw:
            motivo_saldo_pos_sw = 'saldo_zero_ou_ausente' if origem_saldo_pos_sw != 'n/d' and saldo_pos_sw_liquido_candidato <= 0.0 else 'n/d'

        contagem[melhor['estrategia']] += 1
        fontes_consumo = _split_fontes_compostas(melhor.get('lote_recomendado') or '')
        if melhor['estrategia'] == 'switching_simples':
            switching_acionado += 1
            ganhos_switch += float(melhor.get('ganho_liquido_estimado_switching') or 0.0)
        if melhor['estrategia'] == 'combinacao_minima':
            combinacao_acionada += 1
        if bloqueio_janela:
            melhor['saldo_temporal_antes_recomendacao'] = ''
            melhor['consumo_residual_temporal_estimado'] = ''
            melhor['saldo_residual_temporal_pos_recomendacao'] = ''
        else:
            saldo_temporal_antes = 0.0
            for fonte in fontes_consumo:
                if str(fonte or '').strip() in saldo_residual_temporal_por_lote:
                    saldo_temporal_antes = round(float(saldo_residual_temporal_por_lote.get(str(fonte).strip(), 0.0) or 0.0), 2)
                    break
            consumo_temporal, saldo_pos_temporal = _consumir_saldo_temporal(
                saldo_residual_temporal_por_lote,
                fontes_consumo,
                valor_pagamento,
            )
            melhor['saldo_temporal_antes_recomendacao'] = saldo_temporal_antes
            melhor['consumo_residual_temporal_estimado'] = consumo_temporal
            melhor['saldo_residual_temporal_pos_recomendacao'] = saldo_pos_temporal
        linhas.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': data_pagamento,
            'descricao_pagamento': item.get('descricao'),
            'valor_pagamento': valor_pagamento,
            'classe_pagamento_operacional': classe,
            'subclasse_pagamento_operacional': subclasse,
            'estrategia_recomendada': melhor['estrategia'],
            'lote_recomendado': 'não determinado' if bloqueio_janela else (melhor.get('lote_recomendado') or ''),
            'lote_recomendado_consumivel': melhor.get('lote_recomendado_consumivel') if melhor.get('lote_recomendado_consumivel') is not None else ('' if bloqueio_janela else (melhor.get('lote_recomendado') or '')),
            'lote_recomendado_rotulo': melhor.get('lote_recomendado_rotulo') or '',
            'lote_reserva': melhor.get('lote_reserva') or '',
            'necessidade_switching': bool(melhor.get('necessidade_switching')),
            'data_sugerida_switching': melhor.get('data_sugerida_switching'),
            'lote_origem_switching': melhor.get('lote_origem_switching') or '',
            'produto_destino_switching': melhor.get('produto_destino_switching') or '',
            'ganho_liquido_estimado_switching': round(float(melhor.get('ganho_liquido_estimado_switching') or 0.0), 2),
            'cobertura_esperada': round(float(melhor.get('cobertura_esperada') or 0.0), 2),
            'cobertura_integral_recomendada': bool(melhor.get('cobertura_integral')),
            'lote_central_referencia': lote_no_switch,
            'lote_reserva_referencia': lote_reserva,
            'score_central_referencia': score_no_switch,
            'tipo_fonte_recomendada': melhor.get('tipo_fonte_recomendada') or '',
            'fonte_reserva_id': melhor.get('fonte_reserva_id') or '',
            'materialidade_minima_switching': limiar_switch,
            'valor_residual_temporal_lote': round(float(melhor.get('valor_residual_temporal_lote') or 0.0), 2),
            'fracao_residual_temporal_lote': round(float(melhor.get('fracao_residual_temporal_lote') or 0.0), 6),
            'consumo_residual_temporal_estimado': round(float(melhor.get('consumo_residual_temporal_estimado') or 0.0), 2),
            'saldo_residual_temporal_pos_recomendacao': round(float(melhor.get('saldo_residual_temporal_pos_recomendacao') or 0.0), 2),
            'saldo_temporal_antes_recomendacao': round(float(melhor.get('saldo_temporal_antes_recomendacao') or 0.0), 2),
            'fallback_automatico_sem_switching': bool(fallback_automatico_sem_switching and melhor['estrategia'] == 'sem_switching'),
            'motivo_fallback_automatico': motivo_fallback_automatico if bool(fallback_automatico_sem_switching and melhor['estrategia'] == 'sem_switching') else '',
            'motivo_recomendacao': melhor.get('motivo_recomendacao') or '',
            'switching_antes_pagamento': bool(melhor.get('necessidade_switching')) and melhor.get('data_sugerida_switching') is not None and data_pagamento is not None and _coerce_date(melhor.get('data_sugerida_switching')) <= data_pagamento,
            'switching_depois_pagamento': bool(melhor.get('necessidade_switching')) and melhor.get('data_sugerida_switching') is not None and data_pagamento is not None and _coerce_date(melhor.get('data_sugerida_switching')) > data_pagamento,
            'motivo_bloqueio_lote': (
                'lote_ja_migrado_janela'
                if bloqueio_janela
                else (
                    'saldo insuficiente'
                    if float(melhor.get('valor_residual_temporal_lote') or 0.0) < valor_pagamento and bool(melhor.get('necessidade_switching'))
                    else ''
                )
            ),
            'status_recomendacao': (
                'lote_ja_migrado_janela'
                if bloqueio_janela
                else ('lote_indisponivel_pos_switching' if bool(melhor.get('necessidade_switching')) and str(melhor.get('lote_recomendado') or '').strip() in {'', 'não determinado'} else 'ok')
            ),
            'fonte_switching_quadro': 'estado_pos_switching_janela' if fonte_pos_switching else 'motor_pagamento',
            'data_switching_referencia': melhor.get('data_sugerida_switching'),
            'score_switching_shadow': round(float(melhor.get('score_switch_shadow') or 0.0), 4),
            'ordem_switching_shadow': int(melhor.get('ordem_switch_shadow') or 0),
            'data_switching_janela': _info_switching_lote(mapa_switching_janela, lote_origem_pos_switching if fonte_pos_switching else str(melhor.get('lote_recomendado') or '').strip()).get('data_switching_janela'),
            'destino_switching_janela': _info_switching_lote(mapa_switching_janela, lote_origem_pos_switching if fonte_pos_switching else str(melhor.get('lote_recomendado') or '').strip()).get('destino_janela', ''),
            'lote_origem_pos_switching': lote_origem_pos_switching,
            'pos_sw_tentativa': pos_sw_tentativa,
            'fonte_pos_sw': lote_nome_operacional_pos_sw or fonte_pos_sw,
            'lote_id_sintetico': fonte_pos_sw,
            'lote_nome_operacional': lote_nome_operacional_pos_sw,
            'saldo_pos_sw': saldo_pos_sw,
            'motivo_pos_sw': motivo_pos_sw,
            'origem_saldo_pos_sw': origem_saldo_pos_sw,
            'saldo_pos_sw_bruto_candidato': saldo_pos_sw_bruto_candidato,
            'saldo_pos_sw_liquido_candidato': saldo_pos_sw_liquido_candidato,
            'data_base_saldo_pos_sw': data_base_saldo_pos_sw,
            'motivo_saldo_pos_sw': motivo_saldo_pos_sw,
            'conciliacao_pos_switching': (
                'fonte_pos_switching_janela'
                if fonte_pos_switching
                else ('lote_ja_migrado_divergente' if bloqueio_janela else '')
            ),
        })

    quadro = pd.DataFrame(linhas)
    auditoria = {
        'resumo': {
            'total_pagamentos_auditados': int(len(quadro)),
            'estrategia_sem_switching': int(contagem['sem_switching']),
            'estrategia_switching_simples': int(contagem['switching_simples']),
            'estrategia_combinacao_minima': int(contagem['combinacao_minima']),
            'switching_acionado': int(switching_acionado),
            'combinacao_acionada': int(combinacao_acionada),
            'ganho_liquido_switching_estimado_total': round(ganhos_switch, 2),
            'pagamentos_com_fallback_automatico_sem_switching': int(quadro['fallback_automatico_sem_switching'].sum()) if len(quadro) else 0,
            'pagamentos_com_cobertura_integral_recomendada': int(quadro['cobertura_integral_recomendada'].sum()) if len(quadro) else 0,
        },
        'amostras': {
            'recomendacoes_switching': quadro[quadro['necessidade_switching']].head(10).to_dict('records') if len(quadro) else [],
            'recomendacoes_combinacao': quadro[quadro['estrategia_recomendada'] == 'combinacao_minima'].head(10).to_dict('records') if len(quadro) else [],
        },
    }
    return PacoteMotorRecomendacaoPagamentosSwitchingV1(quadro_recomendacoes=quadro, auditoria=auditoria)
