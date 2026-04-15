"""Replay controlado do passado.

Esta camada consome o núcleo financeiro mínimo já aberto e reconcilia
pagamentos históricos que possuem lote(s) explicitamente informado(s).

Escopo desta etapa:
- reprocessar contas pagas até a data de referência;
- consumir lotes explicitamente informados na despesa;
- materializar corretamente lotes históricos não aportados marcados com '-';
- atualizar saldos e remanescentes por lote;
- gerar log técnico do replay e snapshot pós-passado.

Fora do escopo desta etapa:
- heurísticas/solvers para escolher lote;
- switching econômico;
- score econômico final;
- relatório financeiro atual;
- replay de despesas sem lote informado.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

import pandas as pd

from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro, contar_dias_rendimento
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.nucleo_financeiro_minimo import (
    Lote,
    PacoteNucleoFinanceiroMinimo,
    atualizar_saldo_lotes_no_dia,
    construir_faixas_ir,
    construir_tabela_iof,
    criar_lote_de_aporte,
    executar_saque_lote,
)
from nucleo.utilitarios_neutros import arredondar_monetario, limpar_texto, normalizar_texto, para_float_monetario


@dataclass(slots=True)
class PacoteReplayPassadoControlado:
    lotes_apos_replay: list[Lote]
    log_passado: pd.DataFrame
    estado_lotes_passado: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def _clonar_lote(lote: Lote) -> Lote:
    return criar_lote_de_aporte(
        lote.data_aplicacao,
        lote.valor_inicial,
        lote.id,
        {
            'investimento': lote.investimento,
            'produto_key': lote.produto_key,
            'data_base_fiscal': lote.data_base_fiscal,
            'fator_acumulado_inicial': lote.fator_acumulado,
            'taxa_base_cdi': lote.taxa_base_cdi,
            'taxa_bonus_cdi': lote.taxa_bonus_cdi,
            'dias_bonus': lote.dias_bonus,
            'principal_remanescente': lote.principal_remanescente,
            'produto_isento_ir': lote.produto_isento_ir,
            'carencia_ate': lote.carencia_ate,
            'nao_disponivel_para_aporte': lote.nao_disponivel_para_aporte,
            'situacao_investimento': lote.situacao_investimento,
        },
    )


def _serializar_estado_lote(lote: Lote) -> dict[str, Any]:
    return {
        'Lote ID': lote.id,
        'Data Aplicação': lote.data_aplicacao,
        'Data Base Fiscal': lote.data_base_fiscal,
        'Valor Inicial': arredondar_monetario(lote.valor_inicial),
        'Saldo Após Replay': arredondar_monetario(lote.saldo_bruto),
        'Fator Acumulado': float(lote.fator_acumulado),
        'Esgotado no Replay': bool(lote.esgotado),
        'Vezes Usado no Replay': int(lote.vezes_usado),
        'Total Bruto Sacado': arredondar_monetario(lote.total_bruto_sacado),
        'Total Imposto Pago': arredondar_monetario(lote.total_imposto_pago),
        'Total Líquido Sacado': arredondar_monetario(lote.total_liquido_sacado),
        'Taxa Base CDI': float(lote.taxa_base_cdi),
        'Taxa Bonus CDI': float(lote.taxa_bonus_cdi),
        'Dias Bonus': int(lote.dias_bonus),
        'Principal Remanescente': float(getattr(lote, 'principal_remanescente', lote.valor_inicial)),
        'Investimento': str(getattr(lote, 'investimento', '') or ''),
        'Nao Disponivel para Aporte': bool(getattr(lote, 'nao_disponivel_para_aporte', False)),
        'Situacao Investimento': str(getattr(lote, 'situacao_investimento', '') or ''),
    }


def _materializar_lote_historico_nao_aportado(row: dict[str, Any]) -> Lote:
    lote_id = limpar_texto(row.get('lote_id'))
    data_aplicacao = row.get('data_aplicacao')
    valor_original = float(para_float_monetario(row.get('valor_original'), 0.0) or 0.0)
    meta = {
        'investimento': '-',
        'produto_key': None,
        'data_base_fiscal': row.get('data_base_fiscal') or data_aplicacao,
        'fator_acumulado_inicial': 1.0,
        'taxa_base_cdi': 0.0,
        'taxa_bonus_cdi': 0.0,
        'dias_bonus': 0,
        'principal_remanescente': float(valor_original),
        'produto_isento_ir': True,
        'carencia_ate': None,
        'nao_disponivel_para_aporte': True,
        'situacao_investimento': 'nao_aportado_exaurido',
    }
    return criar_lote_de_aporte(data_aplicacao, valor_original, lote_id, meta)


def _extrair_token_mes(lote_id: str) -> str:
    partes = [p for p in normalizar_texto(lote_id).split(' ') if p]
    if not partes:
        return ''
    return partes[-1]


def _extrair_numero_lote(lote_id: str) -> Optional[float]:
    txt = normalizar_texto(lote_id).replace('lote ', '').strip()
    partes = txt.split(' ')
    if not partes:
        return None
    num = partes[0].replace('.', '').replace(',', '.')
    try:
        return float(num)
    except Exception:
        return None


def _resolver_alias_lote_historico_nao_aportado(lote_id_faltante: str, candidatos: list[dict[str, Any]], data_conta: date) -> Optional[dict[str, Any]]:
    token_mes = _extrair_token_mes(lote_id_faltante)
    num_ref = _extrair_numero_lote(lote_id_faltante)
    melhores: list[tuple[float, dict[str, Any]]] = []
    for row in candidatos:
        lid = limpar_texto(row.get('lote_id'))
        token_cand = _extrair_token_mes(lid)
        if token_mes and token_cand and token_mes != token_cand:
            continue
        data_aplic = row.get('data_aplicacao')
        delta_dias = abs((data_conta - data_aplic).days) if (data_conta and data_aplic) else 999
        valor_orig = float(para_float_monetario(row.get('valor_original'), 0.0) or 0.0)
        num_cand = _extrair_numero_lote(lid)
        score = 0.0
        if token_mes and token_cand == token_mes:
            score += 100.0
        score += max(0.0, 30.0 - min(delta_dias, 30))
        if num_ref is not None and num_cand is not None and max(num_ref, num_cand) > 0:
            diff_rel = abs(num_ref - num_cand) / max(num_ref, num_cand)
            score += max(0.0, 40.0 - 80.0 * diff_rel)
        if valor_orig > 0.0 and num_ref is not None:
            diff_val = abs(num_ref - valor_orig) / max(valor_orig, num_ref)
            score += max(0.0, 30.0 - 60.0 * diff_val)
        melhores.append((score, row))
    if not melhores:
        return None
    melhores.sort(key=lambda x: x[0], reverse=True)
    melhor_score, melhor = melhores[0]
    if melhor_score < 90.0:
        return None
    return melhor


def _contexto_inconsistencia(conta: dict[str, Any], restante: Optional[float] = None) -> dict[str, Any]:
    lotes_informados = [x for x in [limpar_texto(conta.get('lote_usado_1')), limpar_texto(conta.get('lote_usado_2'))] if x]
    return {
        'despesa_id': conta.get('despesa_id'),
        'data': conta.get('data'),
        'descricao': conta.get('descricao'),
        'valor_conta': arredondar_monetario(float(conta.get('valor') or 0.0)),
        'lotes_informados': ' | '.join(lotes_informados),
        **({'valor_restante': arredondar_monetario(restante)} if restante is not None else {}),
    }


def _materializar_lotes_historicos_exauridos(dados_operacionais: PacoteDadosOperacionaisCanonicos) -> tuple[list[Lote], dict[str, Lote], dict[str, Any]]:
    inventario = dados_operacionais.inventario_canonico.copy()
    exauridos = inventario[inventario.get('situacao_investimento').eq('nao_aportado_exaurido')].copy() if len(inventario) else inventario
    lotes: list[Lote] = []
    por_id: dict[str, Lote] = {}
    for row in exauridos.to_dict(orient='records'):
        lote = _materializar_lote_historico_nao_aportado(row)
        lotes.append(lote)
        por_id[lote.id] = lote
    auditoria = {
        'qtd_lotes_historicos_nao_aportados_materializados': len(lotes),
        'qtd_lotes_historicos_alias_resolvidos': 0,
        'amostra_alias_historicos_resolvidos': [],
    }
    return lotes, por_id, auditoria


def carregar_replay_passado_controlado(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    nucleo_financeiro: PacoteNucleoFinanceiroMinimo,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    config: dict[str, Any],
    *,
    data_referencia: date,
    serie_cdi: Optional[dict[date, float]] = None,
) -> PacoteReplayPassadoControlado:
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    tolerancia = float(((config.get('replay') or {}).get('tolerancia_monetaria', 0.01)) or 0.01)
    valor_min_lote_ativo = float(((config.get('replay') or {}).get('valor_minimo_lote_ativo', 0.01)) or 0.01)

    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(gastos) == 0:
        validacao = {'ok': False, 'erros': ['gastos_canonicos_vazio'], 'avisos': []}
        return PacoteReplayPassadoControlado([], pd.DataFrame(), pd.DataFrame(), {'qtd_contas_historicas': 0}, validacao)

    contas_pagas = gastos[gastos['passado_pago_ate_data_referencia'] == True].copy()
    contas_pagas = contas_pagas.sort_values(by=['data', 'despesa_id'], kind='stable').reset_index(drop=True)

    lotes_base = [_clonar_lote(l) for l in nucleo_financeiro.lotes_financeiros]
    lotes_por_id = {l.id: l for l in lotes_base}

    lotes_historicos_exauridos, lotes_historicos_por_id, auditoria_hist = _materializar_lotes_historicos_exauridos(dados_operacionais)
    for lote in lotes_historicos_exauridos:
        if lote.id not in lotes_por_id:
            lotes_base.append(lote)
            lotes_por_id[lote.id] = lote

    inventario = dados_operacionais.inventario_canonico.copy()
    candidatos_alias = inventario[inventario.get('situacao_investimento').eq('nao_aportado_exaurido')].to_dict(orient='records') if len(inventario) else []

    if not lotes_base:
        validacao = {'ok': False, 'erros': ['nenhum_lote_financeiro_para_replay'], 'avisos': []}
        return PacoteReplayPassadoControlado([], pd.DataFrame(), pd.DataFrame(), {'qtd_contas_historicas': int(len(contas_pagas))}, validacao)

    if len(contas_pagas) == 0:
        estado = pd.DataFrame([_serializar_estado_lote(l) for l in lotes_base])
        auditoria = {
            'qtd_contas_historicas': 0,
            'qtd_contas_com_lote_informado': 0,
            'qtd_contas_processadas': 0,
            'qtd_contas_cobertas_integralmente': 0,
            'qtd_contas_parcialmente_cobertas': 0,
            'qtd_contas_nao_cobertas': 0,
            'qtd_lotes_historicos_nao_aportados_materializados': auditoria_hist['qtd_lotes_historicos_nao_aportados_materializados'],
            'qtd_lotes_historicos_alias_resolvidos': 0,
            'saldo_bruto_total_pos_replay': arredondar_monetario(sum(float(l.saldo_bruto) for l in lotes_base if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)),
            'saldo_liquido_total_pos_replay': arredondar_monetario(sum(float(l.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)) for l in lotes_base if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)),
        }
        validacao = {'ok': True, 'erros': [], 'avisos': ['nao_ha_contas_pagas_para_replay']}
        return PacoteReplayPassadoControlado(lotes_base, pd.DataFrame(), estado, auditoria, validacao)

    data_inicial = min(l.data_aplicacao for l in lotes_base)
    data_final = max(contas_pagas['data'])
    log_registros: list[dict[str, Any]] = []
    inconsistencias: list[dict[str, Any]] = []
    contas_por_data: dict[date, list[dict[str, Any]]] = {}
    for row in contas_pagas.to_dict(orient='records'):
        contas_por_data.setdefault(row['data'], []).append(row)

    data_atual = data_inicial
    seq_mov = 1
    qtd_contas_processadas = 0
    qtd_integral = 0
    qtd_parcial = 0
    qtd_nao = 0
    total_valor = 0.0
    total_coberto = 0.0
    qtd_sem_lote = 0
    qtd_nao_encontrado = 0
    qtd_alias_resolvido = 0

    while data_atual <= data_final:
        atualizar_saldo_lotes_no_dia(lotes_base, data_atual, calendario_financeiro, serie_cdi=serie_cdi, taxa_proj=calendario_financeiro.taxa_dia_base)
        for conta in contas_por_data.get(data_atual, []):
            qtd_contas_processadas += 1
            valor = float(conta.get('valor') or 0.0)
            total_valor += valor
            restante = valor
            lotes_informados = [x for x in [limpar_texto(conta.get('lote_usado_1')), limpar_texto(conta.get('lote_usado_2'))] if x]
            if not lotes_informados:
                qtd_sem_lote += 1
                inconsistencias.append({**_contexto_inconsistencia(conta), 'motivo': 'conta_historica_sem_lote_informado'})
                qtd_nao += 1
                continue

            consumiu_algo = False
            for lote_id_informado in lotes_informados:
                if restante <= tolerancia:
                    break
                lote = lotes_por_id.get(lote_id_informado)
                lote_id_resolvido = lote_id_informado
                alias_historico = False
                if lote is None:
                    row_alias = _resolver_alias_lote_historico_nao_aportado(lote_id_informado, candidatos_alias, data_atual)
                    if row_alias is not None:
                        lote_id_resolvido = limpar_texto(row_alias.get('lote_id'))
                        lote = lotes_por_id.get(lote_id_resolvido)
                        if lote is not None:
                            alias_historico = True
                            qtd_alias_resolvido += 1
                            auditoria_hist['qtd_lotes_historicos_alias_resolvidos'] += 1
                            if len(auditoria_hist['amostra_alias_historicos_resolvidos']) < 5:
                                auditoria_hist['amostra_alias_historicos_resolvidos'].append({
                                    'lote_informado': lote_id_informado,
                                    'lote_resolvido': lote_id_resolvido,
                                    'despesa_id': conta.get('despesa_id'),
                                    'data_conta': data_atual,
                                })
                    if lote is None:
                        qtd_nao_encontrado += 1
                        inconsistencias.append({**_contexto_inconsistencia(conta), 'lote_id': lote_id_informado, 'motivo': 'lote_informado_nao_encontrado'})
                        continue
                if lote.esgotado or float(lote.saldo_bruto) <= valor_min_lote_ativo:
                    inconsistencias.append({**_contexto_inconsistencia(conta), 'lote_id': lote_id_resolvido, 'motivo': 'lote_esgotado_ou_sem_saldo'})
                    continue
                if lote.data_aplicacao > data_atual:
                    inconsistencias.append({**_contexto_inconsistencia(conta), 'lote_id': lote_id_resolvido, 'motivo': 'lote_ainda_nao_recebido_na_data'})
                    continue
                if lote.carencia_ate and data_atual < lote.carencia_ate:
                    inconsistencias.append({**_contexto_inconsistencia(conta), 'lote_id': lote_id_resolvido, 'motivo': 'lote_em_carencia'})
                    continue
                valor_liquido_alvo = min(restante, float(lote.valor_liquido_hoje(data_atual, tabela_iof=tabela_iof, faixas_ir=faixas_ir)))
                if valor_liquido_alvo <= tolerancia:
                    continue
                movimento = executar_saque_lote(
                    lote,
                    valor_liquido_alvo,
                    data_atual,
                    tabela_iof=tabela_iof,
                    faixas_ir=faixas_ir,
                    tolerancia_monetaria=tolerancia,
                )
                if movimento is None:
                    inconsistencias.append({**_contexto_inconsistencia(conta), 'lote_id': lote_id_resolvido, 'motivo': 'movimento_nulo'})
                    continue
                liquido = float(movimento['liquido'])
                restante = max(restante - liquido, 0.0)
                total_coberto += liquido
                consumiu_algo = True
                log_registros.append({
                    'Data': data_atual,
                    'Despesa ID': conta.get('despesa_id'),
                    'Conta': conta.get('descricao'),
                    'Valor Conta': arredondar_monetario(valor),
                    'Lote': lote.id,
                    'Lote Informado': lote_id_informado,
                    'Alias Historico Resolvido': bool(alias_historico),
                    'Saldo Antes': arredondar_monetario(movimento['saldo_antes']),
                    'Bruto': arredondar_monetario(movimento['bruto']),
                    'Imposto': arredondar_monetario(movimento['imposto']),
                    'Liquido': arredondar_monetario(liquido),
                    'Dias Corridos': (data_atual - lote.data_base_fiscal).days,
                    'Dias Úteis': contar_dias_rendimento(lote.data_base_fiscal, data_atual, calendario_financeiro),
                    'Saldo Remanescente': arredondar_monetario(movimento['saldo_remanescente']),
                    'Sequencia Saque': seq_mov,
                    'Situacao Investimento Lote': str(getattr(lote, 'situacao_investimento', '') or ''),
                })
                seq_mov += 1

            if restante <= tolerancia:
                qtd_integral += 1
            elif consumiu_algo:
                qtd_parcial += 1
                inconsistencias.append({**_contexto_inconsistencia(conta, restante), 'motivo': 'conta_parcialmente_coberta'})
            else:
                qtd_nao += 1
                inconsistencias.append({**_contexto_inconsistencia(conta, restante), 'motivo': 'conta_nao_coberta'})
        data_atual += timedelta(days=1)

    estado = pd.DataFrame([_serializar_estado_lote(l) for l in lotes_base])
    log_df = pd.DataFrame(log_registros)
    saldo_bruto_pos = sum(float(l.saldo_bruto) for l in lotes_base if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)
    saldo_liquido_pos = sum(float(l.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir)) for l in lotes_base if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)

    auditoria = {
        'qtd_contas_historicas': int(len(contas_pagas)),
        'qtd_contas_com_lote_informado': int((contas_pagas['qtd_lotes_informados'] > 0).sum()),
        'qtd_contas_processadas': int(qtd_contas_processadas),
        'qtd_contas_cobertas_integralmente': int(qtd_integral),
        'qtd_contas_parcialmente_cobertas': int(qtd_parcial),
        'qtd_contas_nao_cobertas': int(qtd_nao),
        'qtd_contas_sem_lote_informado': int(qtd_sem_lote),
        'qtd_lotes_historicos_nao_aportados_materializados': int(auditoria_hist['qtd_lotes_historicos_nao_aportados_materializados']),
        'qtd_lotes_historicos_alias_resolvidos': int(auditoria_hist['qtd_lotes_historicos_alias_resolvidos']),
        'amostra_alias_historicos_resolvidos': auditoria_hist['amostra_alias_historicos_resolvidos'][:5],
        'qtd_lotes_informados_nao_encontrados': int(qtd_nao_encontrado),
        'qtd_movimentos_log': int(len(log_df)),
        'qtd_lotes_remanescentes_ativos': int(sum(1 for l in lotes_base if not l.esgotado and float(l.saldo_bruto) > valor_min_lote_ativo)),
        'total_valor_contas_historicas': arredondar_monetario(total_valor),
        'total_liquido_coberto': arredondar_monetario(total_coberto),
        'saldo_bruto_total_pos_replay': arredondar_monetario(saldo_bruto_pos),
        'saldo_liquido_total_pos_replay': arredondar_monetario(saldo_liquido_pos),
        'fonte_rendimento_replay': 'serie_cdi_bcb' if serie_cdi else 'taxa_modelo',
        'qtd_datas_serie_cdi': int(len(serie_cdi or {})),
        'amostra_log_passado': None if len(log_registros) == 0 else log_registros[0],
        'qtd_inconsistencias': int(len(inconsistencias)),
        'amostra_inconsistencias': inconsistencias[:5],
    }
    avisos = []
    if qtd_sem_lote > 0:
        avisos.append('existem_contas_historicas_sem_lote_informado_no_replay_controlado')
    if qtd_parcial > 0:
        avisos.append('existem_contas_historicas_parcialmente_cobertas_no_replay_controlado')
    if qtd_nao > 0:
        avisos.append('existem_contas_historicas_nao_cobertas_no_replay_controlado')
    if qtd_nao_encontrado > 0:
        avisos.append('existem_lotes_historicos_informados_nao_encontrados_apos_materializacao')
    validacao = {
        'ok': True,
        'erros': [],
        'avisos': avisos,
    }
    return PacoteReplayPassadoControlado(lotes_base, log_df, estado, auditoria, validacao)
