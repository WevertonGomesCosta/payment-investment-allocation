"""Benchmark shadow do resolver_hibrido_5p legado.

Esta camada absorve, em modo shadow e auditável, a lógica material do legado
relativa ao `resolver_hibrido_5p`, sem acoplar a decisão ao fluxo principal.

Escopo desta etapa:
- avaliar pagamentos futuros/pendentes um a um;
- usar apenas lotes resgatáveis elegíveis na data de cada pagamento;
- rodar um benchmark de alocação multifonte baseado em pesos de IOF, IR,
  idade, liquidez, cliff e VPL;
- comparar o benchmark shadow com a decisão local v1 vigente.

Fora do escopo desta etapa:
- substituir a decisão local v1 do fluxo principal;
- abrir multifonte no runner principal;
- acoplar solver pesado ou treino de parâmetros;
- importar infraestrutura legada de treino/fallback/rede.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Mapping

import pandas as pd
from scipy.optimize import linprog

from nucleo.cache_cdi_bcb import PacoteCacheCDIDiario
from nucleo.calendario_financeiro import PacoteCalendarioFinanceiro, obter_taxa_dia_rendimento_lote
from nucleo.caixa_recebidos_auditaveis import PacoteDecisaoLocalV1, PacoteFontesElegiveisPagamento
from nucleo.config_utils import obter_config
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.nucleo_financeiro_minimo import Lote, _taxa_iof, _taxa_ir, criar_lote_de_aporte
from nucleo.replay_passado_controlado import PacoteReplayPassadoControlado
from nucleo.utilitarios_neutros import arredondar_monetario, limpar_texto, normalizar_identificador, para_float_monetario


@dataclass(slots=True)
class PacoteResolverHibrido5PShadow:
    quadro_pagamentos_benchmark: pd.DataFrame
    quadro_alocacoes_shadow: pd.DataFrame
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def _cfg(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, Mapping) or chave not in atual:
            return padrao
        atual = atual[chave]
    return atual


def _pagamentos_alvo(gastos_canonicos: pd.DataFrame, *, data_referencia: date) -> pd.DataFrame:
    if len(gastos_canonicos) == 0:
        return pd.DataFrame(columns=['despesa_id', 'data', 'descricao', 'valor'])
    quadro = gastos_canonicos.copy()
    mask = quadro['futuro_ou_pendente_na_data_referencia'].eq(True) & quadro['data'].notna() & (quadro['data'] >= data_referencia)
    quadro = quadro.loc[mask, ['despesa_id', 'data', 'descricao', 'valor']].copy()
    if len(quadro) == 0:
        return quadro
    quadro['despesa_id'] = quadro['despesa_id'].map(limpar_texto)
    quadro['descricao'] = quadro['descricao'].map(limpar_texto)
    quadro['valor'] = quadro['valor'].map(lambda x: round(float(x or 0.0), 2))
    return quadro.sort_values(['data', 'despesa_id'], kind='stable').reset_index(drop=True)


def _iterar_datas(inicio: date, fim: date):
    atual = inicio + timedelta(days=1)
    while atual <= fim:
        yield atual
        atual += timedelta(days=1)


def _simular_lote_ate_data(
    lote: Lote,
    data_inicio: date,
    data_fim: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    *,
    serie_cdi: Mapping[date, float] | None,
    taxa_proj: float,
) -> Lote:
    clone = criar_lote_de_aporte(
        data_inicio,
        float(lote.saldo_bruto),
        lote.id,
        {
            'investimento': lote.investimento,
            'produto_key': lote.produto_key,
            'data_base_fiscal': lote.data_base_fiscal,
            'data_recebimento': lote.data_recebimento,
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
    if data_fim <= data_inicio:
        return clone
    for data_cur in _iterar_datas(data_inicio, data_fim):
        aplicar, taxa_dia, _ = obter_taxa_dia_rendimento_lote(
            data_cur,
            clone.data_aplicacao,
            calendario_financeiro,
            data_recebimento=clone.data_recebimento,
            serie_cdi=serie_cdi,
            taxa_proj=taxa_proj,
            data_fechamento_referencia=data_cur,
        )
        if aplicar and taxa_dia is not None:
            clone.atualizar_juros(
                data_cur,
                taxa_dia,
                calendario_financeiro,
                serie_cdi=serie_cdi,
                data_fechamento_referencia=data_cur,
            )
    return clone


def _lotes_ativos(replay_passado: PacoteReplayPassadoControlado | None) -> dict[str, Lote]:
    lotes: dict[str, Lote] = {}
    if replay_passado is None:
        return lotes
    for lote in replay_passado.lotes_apos_replay:
        lote_id = normalizar_identificador(getattr(lote, 'id', None))
        if not lote_id:
            continue
        if getattr(lote, 'esgotado', False):
            continue
        if float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.01:
            continue
        lotes[lote_id] = lote
    return lotes


def _params_hibrido_shadow(config: Mapping[str, Any]) -> dict[str, float]:
    base = {
        'peso_iof': 100.0,
        'peso_ir': 0.0,
        'peso_idade': 0.1,
        'peso_liq': 0.0,
        'peso_cliff': 1000.0,
        'peso_vpl': 250.0,
    }
    cfg = _cfg(config, 'hibrido_shadow', padrao={}) or {}
    for chave in list(base.keys()):
        valor = cfg.get(chave)
        if valor is None:
            continue
        try:
            base[chave] = float(valor)
        except Exception:
            pass
    return base


def _dias_cliff(dias: int) -> int:
    if dias < 180:
        return max(180 - dias, 0)
    if dias < 360:
        return max(360 - dias, 0)
    if dias < 720:
        return max(720 - dias, 0)
    return 999


def _candidato_lote_para_pagamento(
    lote: Lote,
    data_pagamento: date,
    data_horizonte: date,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    *,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
    params: Mapping[str, float],
) -> dict[str, Any]:
    taxa_proj = float(calendario_financeiro.taxa_dia_base)
    lote_pag = _simular_lote_ate_data(
        lote,
        calendario_financeiro.data_referencia,
        data_pagamento,
        calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
        taxa_proj=taxa_proj,
    )
    bruto_disp = round(float(lote_pag.saldo_bruto or 0.0), 2)
    fator_liq = float(lote_pag.get_fator_liquido(data_pagamento, tabela_iof=tabela_iof, faixas_ir=faixas_ir))
    liquido_disp = round(float(lote_pag.valor_liquido_hoje(data_pagamento, tabela_iof=tabela_iof, faixas_ir=faixas_ir)), 2)
    dias = max((data_pagamento - lote_pag.data_aplicacao).days, 0)
    iof = float(_taxa_iof(dias, tabela_iof=tabela_iof))
    ir = float(_taxa_ir(dias, isento=bool(lote_pag.produto_isento_ir), faixas_ir=faixas_ir))
    dist_cliff = _dias_cliff(dias)
    penalty_cliff = 1.0 if dist_cliff <= 10 else 0.0

    oportunidade_vpl = 0.0
    if data_horizonte > data_pagamento and bruto_disp > 0.0 and params.get('peso_vpl', 0.0) > 0.0:
        lote_horizonte = _simular_lote_ate_data(
            lote_pag,
            data_pagamento,
            data_horizonte,
            calendario_financeiro,
            serie_cdi=cache_cdi.serie_cdi,
            taxa_proj=taxa_proj,
        )
        crescimento_bruto = float(lote_horizonte.saldo_bruto / max(lote_pag.saldo_bruto, 1e-9))
        fator_liq_horizonte = float(lote_horizonte.get_fator_liquido(data_horizonte, tabela_iof=tabela_iof, faixas_ir=faixas_ir))
        oportunidade_vpl = max((crescimento_bruto * fator_liq_horizonte) - fator_liq, 0.0)

    custo_unitario = (
        1.0
        + iof * float(params.get('peso_iof', 0.0) or 0.0)
        + ir * float(params.get('peso_ir', 0.0) or 0.0)
        + dias * float(params.get('peso_idade', 0.0) or 0.0)
        + fator_liq * float(params.get('peso_liq', 0.0) or 0.0)
        + penalty_cliff * float(params.get('peso_cliff', 0.0) or 0.0)
        + oportunidade_vpl * float(params.get('peso_vpl', 0.0) or 0.0)
    )

    return {
        'lote_id': normalizar_identificador(lote.id),
        'produto_nome': limpar_texto(lote.investimento),
        'data_pagamento': data_pagamento,
        'data_horizonte': data_horizonte,
        'saldo_bruto_pagamento': bruto_disp,
        'saldo_liquido_pagamento': liquido_disp,
        'fator_liquido_pagamento': fator_liq,
        'idade_dias_pagamento': dias,
        'iof_proxy': iof,
        'ir_proxy': ir,
        'distancia_cliff_dias': dist_cliff,
        'penalidade_cliff_ativa': penalty_cliff,
        'oportunidade_vpl_proxy': oportunidade_vpl,
        'custo_unitario_hibrido': float(custo_unitario),
    }


def _resolver_hibrido_shadow_lotes(
    candidatos: list[dict[str, Any]],
    alvo_liquido: float,
    *,
    valor_minimo_resgate_bruto: float,
) -> tuple[list[float], str, str | None]:
    if not candidatos:
        return [], 'sem_candidatos', 'sem_lotes_elegiveis_para_benchmark'
    fatores = [max(float(c.get('fator_liquido_pagamento') or 0.0), 0.0) for c in candidatos]
    bounds = [(0.0, max(float(c.get('saldo_bruto_pagamento') or 0.0), 0.0)) for c in candidatos]
    if sum(b * f for (a, b), f in zip(bounds, fatores)) + 1e-9 < float(alvo_liquido):
        return [0.0] * len(candidatos), 'sem_cobertura', 'capacidade_liquida_total_insuficiente'

    c = [float(cand.get('custo_unitario_hibrido') or 1.0) for cand in candidatos]
    A_ub = [[-f for f in fatores]]
    b_ub = [-float(alvo_liquido)]
    try:
        res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    except Exception as exc:
        return [0.0] * len(candidatos), 'erro_solver', f'linprog:{exc.__class__.__name__}'

    if not res.success or res.x is None:
        return [0.0] * len(candidatos), 'erro_solver', limpar_texto(getattr(res, 'message', None)) or 'linprog_sem_solucao'

    valores = [max(float(v or 0.0), 0.0) for v in res.x.tolist()]
    valores = [0.0 if v < float(valor_minimo_resgate_bruto) else arredondar_monetario(v) for v in valores]
    cobertura = sum(v * f for v, f in zip(valores, fatores))
    if cobertura + 1e-6 < float(alvo_liquido):
        ordem = sorted(range(len(candidatos)), key=lambda i: (float(candidatos[i].get('custo_unitario_hibrido') or 1.0), -float(candidatos[i].get('saldo_bruto_pagamento') or 0.0)))
        faltante = float(alvo_liquido) - cobertura
        for idx in ordem:
            disponivel = max(float(candidatos[idx].get('saldo_bruto_pagamento') or 0.0) - valores[idx], 0.0)
            fator = max(float(candidatos[idx].get('fator_liquido_pagamento') or 0.0), 0.0)
            if disponivel <= 0 or fator <= 0:
                continue
            adicional = min(disponivel, faltante / fator)
            if adicional <= 0:
                continue
            adicional = arredondar_monetario(adicional)
            valores[idx] = arredondar_monetario(valores[idx] + adicional)
            cobertura = sum(v * f for v, f in zip(valores, fatores))
            faltante = float(alvo_liquido) - cobertura
            if faltante <= 0.01:
                break
    return valores, 'ok', None


def carregar_resolver_hibrido_5p_shadow(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    fontes_elegiveis_pagamento: PacoteFontesElegiveisPagamento,
    decisao_local_v1: PacoteDecisaoLocalV1,
    replay_passado: PacoteReplayPassadoControlado | None,
    calendario_financeiro: PacoteCalendarioFinanceiro,
    cache_cdi: PacoteCacheCDIDiario,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    tabela_iof: list[float],
    faixas_ir: list[dict[str, Any]],
) -> PacoteResolverHibrido5PShadow:
    pagamentos_alvo = _pagamentos_alvo(dados_operacionais.gastos_canonicos.copy(), data_referencia=data_referencia)
    colunas_pag = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'status_benchmark', 'motivo_status',
        'qtd_lotes_candidatos', 'qtd_lotes_usados_hibrido', 'valor_bruto_total_hibrido', 'valor_liquido_total_hibrido',
        'custo_total_proxy_hibrido', 'benchmark_totalmente_coberto', 'lote_principal_hibrido', 'lote_principal_local_v1',
        'tipo_fonte_local_v1', 'diverge_decisao_local_v1', 'bruto_monofonte_local_estimado', 'delta_bruto_hibrido_vs_local',
        'observacao_auditavel',
    ]
    colunas_aloc = [
        'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'lote_id', 'produto_nome',
        'saldo_bruto_pagamento', 'saldo_liquido_pagamento', 'fator_liquido_pagamento', 'idade_dias_pagamento', 'iof_proxy',
        'ir_proxy', 'distancia_cliff_dias', 'penalidade_cliff_ativa', 'oportunidade_vpl_proxy', 'custo_unitario_hibrido',
        'valor_bruto_alocado_hibrido', 'valor_liquido_alocado_hibrido', 'participacao_liquida_pct', 'escolhido_no_benchmark',
        'ordem_no_plano', 'status_linha_benchmark', 'motivo_status_linha',
    ]
    if len(pagamentos_alvo) == 0:
        vazio_pag = pd.DataFrame(columns=colunas_pag)
        vazio_aloc = pd.DataFrame(columns=colunas_aloc)
        auditoria = {'resumo': {'total_pagamentos_alvo': 0}}
        validacao = {'ok': False, 'erros': ['resolver_hibrido_5p_shadow_sem_pagamentos_alvo'], 'avisos': []}
        return PacoteResolverHibrido5PShadow(vazio_pag, vazio_aloc, auditoria, validacao)

    params = _params_hibrido_shadow(config)
    horizonte_dias = int(_cfg(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180)
    valor_minimo_resgate_bruto = float(_cfg(config, 'pagamento', 'valor_minimo_resgate_bruto', padrao=0.01) or 0.01)
    data_horizonte_base = data_referencia + timedelta(days=horizonte_dias)
    lotes_ativos = _lotes_ativos(replay_passado)
    quadro_fontes = fontes_elegiveis_pagamento.quadro_fontes_elegiveis.copy()
    quadro_local = decisao_local_v1.quadro_decisao_local_v1.copy()

    registros_pag: list[dict[str, Any]] = []
    registros_aloc: list[dict[str, Any]] = []
    pagamentos_com_divergencia = 0
    pagamentos_totalmente_cobertos = 0
    pagamentos_multifonte = 0

    for pagamento in pagamentos_alvo.to_dict(orient='records'):
        pagamento_id = limpar_texto(pagamento.get('despesa_id'))
        data_pagamento = pagamento.get('data')
        valor_pagamento = round(float(pagamento.get('valor') or 0.0), 2)
        desc = limpar_texto(pagamento.get('descricao'))
        local_row = quadro_local[quadro_local['pagamento_id'] == pagamento_id]
        local_tipo = limpar_texto(local_row.iloc[0]['tipo_fonte_escolhida']) if len(local_row) else ''
        local_lote = normalizar_identificador(local_row.iloc[0]['lote_id_escolhido']) if len(local_row) else None

        if data_pagamento is None:
            registros_pag.append({
                'pagamento_id': pagamento_id,
                'data_pagamento': data_pagamento,
                'descricao_pagamento': desc,
                'valor_pagamento': valor_pagamento,
                'status_benchmark': 'sem_data',
                'motivo_status': 'pagamento_sem_data_valida',
                'qtd_lotes_candidatos': 0,
                'qtd_lotes_usados_hibrido': 0,
                'valor_bruto_total_hibrido': 0.0,
                'valor_liquido_total_hibrido': 0.0,
                'custo_total_proxy_hibrido': None,
                'benchmark_totalmente_coberto': False,
                'lote_principal_hibrido': None,
                'lote_principal_local_v1': local_lote,
                'tipo_fonte_local_v1': local_tipo,
                'diverge_decisao_local_v1': False,
                'bruto_monofonte_local_estimado': None,
                'delta_bruto_hibrido_vs_local': None,
                'observacao_auditavel': 'pagamento sem data válida para benchmark shadow.',
            })
            continue

        fontes_pag = quadro_fontes[
            (quadro_fontes['pagamento_id'] == pagamento_id)
            & (quadro_fontes['tipo_fonte'] == 'lote_resgatavel')
            & (quadro_fontes['elegivel_na_data_pagamento'].eq(True))
        ].copy()
        candidatos: list[dict[str, Any]] = []
        data_horizonte = max(data_pagamento, data_horizonte_base)
        for _, row in fontes_pag.iterrows():
            lote_id = normalizar_identificador(row.get('lote_id'))
            if not lote_id or lote_id not in lotes_ativos:
                continue
            candidato = _candidato_lote_para_pagamento(
                lotes_ativos[lote_id],
                data_pagamento,
                data_horizonte,
                calendario_financeiro,
                cache_cdi,
                tabela_iof=tabela_iof,
                faixas_ir=faixas_ir,
                params=params,
            )
            if float(candidato.get('saldo_liquido_pagamento') or 0.0) <= 0.01:
                continue
            candidatos.append(candidato)

        valores_alocados, status_benchmark, motivo_status = _resolver_hibrido_shadow_lotes(
            candidatos,
            valor_pagamento,
            valor_minimo_resgate_bruto=valor_minimo_resgate_bruto,
        )

        bruto_total = round(sum(valores_alocados), 2) if valores_alocados else 0.0
        liquido_total = round(sum(v * float(c.get('fator_liquido_pagamento') or 0.0) for v, c in zip(valores_alocados, candidatos)), 2) if valores_alocados else 0.0
        custo_total = round(sum(v * float(c.get('custo_unitario_hibrido') or 0.0) for v, c in zip(valores_alocados, candidatos)), 4) if valores_alocados else None
        totalmente_coberto = bool(liquido_total + 0.01 >= valor_pagamento and status_benchmark == 'ok')
        usados = [i for i, v in enumerate(valores_alocados) if float(v or 0.0) >= valor_minimo_resgate_bruto]
        qtd_lotes_usados = len(usados)
        if totalmente_coberto:
            pagamentos_totalmente_cobertos += 1
        if qtd_lotes_usados > 1:
            pagamentos_multifonte += 1

        lote_principal = None
        maior_liquido = -1.0
        for ordem_idx, candidato in enumerate(candidatos, start=1):
            bruto_alocado = round(float(valores_alocados[ordem_idx - 1] or 0.0), 2) if valores_alocados else 0.0
            liquido_alocado = round(bruto_alocado * float(candidato.get('fator_liquido_pagamento') or 0.0), 2)
            if liquido_alocado > maior_liquido:
                maior_liquido = liquido_alocado
                lote_principal = candidato.get('lote_id')
            registros_aloc.append({
                'pagamento_id': pagamento_id,
                'data_pagamento': data_pagamento,
                'descricao_pagamento': desc,
                'valor_pagamento': valor_pagamento,
                'lote_id': candidato.get('lote_id'),
                'produto_nome': candidato.get('produto_nome'),
                'saldo_bruto_pagamento': round(float(candidato.get('saldo_bruto_pagamento') or 0.0), 2),
                'saldo_liquido_pagamento': round(float(candidato.get('saldo_liquido_pagamento') or 0.0), 2),
                'fator_liquido_pagamento': round(float(candidato.get('fator_liquido_pagamento') or 0.0), 6),
                'idade_dias_pagamento': int(candidato.get('idade_dias_pagamento') or 0),
                'iof_proxy': round(float(candidato.get('iof_proxy') or 0.0), 6),
                'ir_proxy': round(float(candidato.get('ir_proxy') or 0.0), 6),
                'distancia_cliff_dias': int(candidato.get('distancia_cliff_dias') or 0),
                'penalidade_cliff_ativa': int(candidato.get('penalidade_cliff_ativa') or 0),
                'oportunidade_vpl_proxy': round(float(candidato.get('oportunidade_vpl_proxy') or 0.0), 6),
                'custo_unitario_hibrido': round(float(candidato.get('custo_unitario_hibrido') or 0.0), 6),
                'valor_bruto_alocado_hibrido': bruto_alocado,
                'valor_liquido_alocado_hibrido': liquido_alocado,
                'participacao_liquida_pct': round((liquido_alocado / max(liquido_total, 0.01)) * 100.0, 2) if liquido_total > 0 else 0.0,
                'escolhido_no_benchmark': bruto_alocado >= valor_minimo_resgate_bruto,
                'ordem_no_plano': ordem_idx,
                'status_linha_benchmark': status_benchmark,
                'motivo_status_linha': motivo_status,
            })

        bruto_local_estimado = None
        if local_lote and local_lote in {c.get('lote_id') for c in candidatos}:
            cand_local = next((c for c in candidatos if c.get('lote_id') == local_lote), None)
            fator_local = float(cand_local.get('fator_liquido_pagamento') or 0.0) if cand_local else 0.0
            if fator_local > 0:
                bruto_local_estimado = arredondar_monetario(valor_pagamento / fator_local)
        delta_bruto = round(float(bruto_local_estimado or 0.0) - bruto_total, 2) if bruto_local_estimado is not None else None
        diverge = bool(local_lote and lote_principal and local_lote != lote_principal) or bool(local_tipo == 'lote_resgatavel' and qtd_lotes_usados > 1)
        if diverge:
            pagamentos_com_divergencia += 1

        if status_benchmark == 'ok':
            obs = 'benchmark shadow do resolver_hibrido_5p executado sobre os lotes elegíveis na data do pagamento.'
            if qtd_lotes_usados > 1:
                obs += ' O benchmark sugeriu combinação multifonte entre lotes resgatáveis.'
            else:
                obs += ' O benchmark sugeriu resgate monofonte.'
        else:
            obs = f'benchmark shadow não produziu plano executável: {motivo_status or status_benchmark}.'

        registros_pag.append({
            'pagamento_id': pagamento_id,
            'data_pagamento': data_pagamento,
            'descricao_pagamento': desc,
            'valor_pagamento': valor_pagamento,
            'status_benchmark': status_benchmark,
            'motivo_status': motivo_status,
            'qtd_lotes_candidatos': len(candidatos),
            'qtd_lotes_usados_hibrido': qtd_lotes_usados,
            'valor_bruto_total_hibrido': bruto_total,
            'valor_liquido_total_hibrido': liquido_total,
            'custo_total_proxy_hibrido': custo_total,
            'benchmark_totalmente_coberto': totalmente_coberto,
            'lote_principal_hibrido': lote_principal,
            'lote_principal_local_v1': local_lote,
            'tipo_fonte_local_v1': local_tipo,
            'diverge_decisao_local_v1': diverge,
            'bruto_monofonte_local_estimado': bruto_local_estimado,
            'delta_bruto_hibrido_vs_local': delta_bruto,
            'observacao_auditavel': obs,
        })

    quadro_pag = pd.DataFrame(registros_pag, columns=colunas_pag).sort_values(['data_pagamento', 'pagamento_id'], kind='stable').reset_index(drop=True)
    quadro_aloc = pd.DataFrame(registros_aloc, columns=colunas_aloc).sort_values(['data_pagamento', 'pagamento_id', 'escolhido_no_benchmark', 'valor_liquido_alocado_hibrido'], ascending=[True, True, False, False], kind='stable').reset_index(drop=True)

    erros: list[str] = []
    avisos: list[str] = []
    if len(quadro_pag) != len(pagamentos_alvo):
        erros.append('resolver_hibrido_5p_shadow_nao_cobre_todos_os_pagamentos_alvo')
    if quadro_pag['pagamento_id'].duplicated().any():
        erros.append('resolver_hibrido_5p_shadow_pagamento_duplicado')
    if (~quadro_pag['benchmark_totalmente_coberto']).any():
        avisos.append('existem_pagamentos_nao_totalmente_cobertos_no_benchmark_shadow')
    if (quadro_pag['qtd_lotes_usados_hibrido'] > 1).any():
        avisos.append('existem_pagamentos_em_que_o_benchmark_shadow_sugere_multifonte')
    if (quadro_pag['diverge_decisao_local_v1']).any():
        avisos.append('existem_pagamentos_em_que_o_benchmark_shadow_diverge_da_decisao_local_v1')

    auditoria = {
        'parametros_hibrido_shadow': params,
        'resumo': {
            'total_pagamentos_alvo': int(len(quadro_pag)),
            'pagamentos_totalmente_cobertos': int(quadro_pag['benchmark_totalmente_coberto'].sum()) if len(quadro_pag) else 0,
            'pagamentos_multifonte_shadow': int(pagamentos_multifonte),
            'pagamentos_com_divergencia_vs_local_v1': int(pagamentos_com_divergencia),
            'status_benchmark': {str(k): int(v) for k, v in quadro_pag['status_benchmark'].value_counts(dropna=False).to_dict().items()} if len(quadro_pag) else {},
            'lote_principal_hibrido': {str(k): int(v) for k, v in quadro_pag['lote_principal_hibrido'].dropna().value_counts(dropna=False).to_dict().items()} if len(quadro_pag) else {},
            'qtd_linhas_alocacao_shadow': int(len(quadro_aloc)),
            'valor_bruto_total_hibrido': round(float(quadro_pag['valor_bruto_total_hibrido'].sum()), 2) if len(quadro_pag) else 0.0,
            'valor_liquido_total_hibrido': round(float(quadro_pag['valor_liquido_total_hibrido'].sum()), 2) if len(quadro_pag) else 0.0,
        },
    }
    validacao = {'ok': len(erros) == 0, 'erros': erros, 'avisos': avisos}
    return PacoteResolverHibrido5PShadow(quadro_pag, quadro_aloc, auditoria, validacao)
