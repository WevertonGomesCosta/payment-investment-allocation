"""Ponto de entrada do console operacional da baseline."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.common import (
    imprimir_pares as _imprimir_pares,
    imprimir_tabela as _imprimir_tabela,
    imprimir_titulo as _imprimir_titulo,
    severidade as _severidade,
)
from aplicacao.console.secoes_execucao import render_secao_execucao
from aplicacao.console.secoes_financeiras import render_secao_amostras_pagamentos
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica

COLUNAS_LOTES_CONSOLIDADOS = [
    'Lote ID',
    'Carteira',
    'Data Aplicação',
    'Data Base Fiscal',
    'Dias Corridos até Hoje',
    'Dias Úteis até Hoje',
    'Valor Original (R$)',
    'Total Bruto Sacado (R$)',
    'Total Líquido Sacado (R$)',
    'Saldo Bruto Atual (R$)',
    'Saldo Líquido Atual (R$)',
    'Patrimônio Líquido até Hoje (R$)',
    'Rendimento Líquido Acumulado dos Lotes (R$)',
]


def _render_secao_ranking_oficial(contexto_baseline, saida_canonica=None) -> None:
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    if ranking is None:
        return
    _imprimir_titulo('RANQUEAMENTO OFICIAL DA CARTEIRA')
    _imprimir_pares([
        ('produtos totais', ranking.resumo.get('produtos_total')),
        ('produtos ativos ranqueados', ranking.resumo.get('produtos_ativos_ranqueados')),
        ('destinos elegíveis de switching', ranking.auditoria.get('qtd_destinos_switch')),
        ('destino top 1', ranking.auditoria.get('destino_top1')),
        ('método', ranking.auditoria.get('metodo')),
        ('origem da amostra', 'saida_canonica_v202'),
    ])
    linhas = list(getattr(saida_canonica, 'ranking_amostra', []) or [])
    print('- amostra do ranking relevante do dia:')
    _imprimir_tabela(['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.'], linhas, limite=10)


def _render_secao_switchings_oficiais(contexto_baseline, saida_canonica=None) -> None:
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    destino_top1 = ranking.auditoria.get('destino_top1') if ranking is not None else None
    linhas = list(getattr(saida_canonica, 'switchings', []) or [])[:10]
    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    _imprimir_pares([
        ('lotes avaliados para switching', len(linhas)),
        ('destinos elegíveis de switching', len(ranking.quadro_destinos_switch) if ranking is not None and isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame) else 0),
        ('switchings promovidos/executados', len(linhas)),
        ('destino top 1 do ranking', destino_top1),
        ('origem da amostra', 'saida_canonica_v202'),
    ])
    print('- amostra de switchings reais da janela (independente de pagamentos):')
    _imprimir_tabela(['Data', 'Lote origem', 'Produto origem', 'Destino'], linhas, limite=10)


def _para_float(valor: Any) -> float:
    try:
        if valor is None or valor == '':
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def _somas_sacadas_por_lote(contexto_baseline, saida_canonica=None) -> dict[str, dict[str, float]]:
    """Soma valores sacados por lote.

    Para lotes não aplicados/exauridos, o log de replay pode trazer apenas
    movimentos parciais associados explicitamente ao lote. Por isso a auditoria
    de recebidos é usada como fonte complementar e prevalece quando o valor
    vinculado é maior que a soma encontrada no log.
    """
    replay = getattr(contexto_baseline, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    somas: dict[str, dict[str, float]] = {}

    if isinstance(log, pd.DataFrame) and len(log) and 'Lote' in log.columns:
        for _, row in log.iterrows():
            lote_id = str(row.get('Lote') or '').strip()
            if not lote_id:
                continue
            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(atual['bruto_sacado'] + _para_float(row.get('Bruto')), 2)
            atual['liquido_sacado'] = round(atual['liquido_sacado'] + _para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')), 2)

    if saida_canonica is not None:
        for recebido in (getattr(saida_canonica, 'recebidos_atuais', []) or []):
            lote_id = str(recebido.get('Lote origem') or '').strip()
            if not lote_id:
                continue
            status = str(recebido.get('Status') or '').strip().lower()
            destino = str(recebido.get('Destino') or '').strip().lower()
            valor_vinculado = _para_float(recebido.get('Valor vinculado'))
            valor_liquido = _para_float(recebido.get('Valor líquido'))
            valor_bruto = _para_float(recebido.get('Valor bruto'))
            usar_recebido = status in {'exaurido', 'uso_pre_aplicacao_com_aporte_posterior'} or destino in {'pagamento', 'pagamento_e_aplicacao'}
            if not usar_recebido:
                continue
            liquido_ref = valor_vinculado if valor_vinculado > 0 else valor_liquido
            bruto_ref = max(valor_vinculado, valor_bruto if status == 'exaurido' else 0.0, liquido_ref)
            atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
            atual['bruto_sacado'] = round(max(atual['bruto_sacado'], bruto_ref), 2)
            atual['liquido_sacado'] = round(max(atual['liquido_sacado'], liquido_ref), 2)

    return somas


def _linhas_lotes_consolidados(contexto_baseline, saida_canonica, *, tipo: str) -> list[dict[str, Any]]:
    itens = list(getattr(saida_canonica, 'lotes_exauridos' if tipo == 'exauridos' else 'lotes_ativos', []) or [])
    somas = _somas_sacadas_por_lote(contexto_baseline, saida_canonica)
    linhas: list[dict[str, Any]] = []
    for item in itens:
        lote_id = str(item.get('Lote') or '').strip()
        sacado = somas.get(lote_id, {})
        valor_original = round(_para_float(item.get('Valor original')), 2)
        total_bruto_sacado = round(_para_float(sacado.get('bruto_sacado')), 2)
        total_liquido_sacado = round(_para_float(sacado.get('liquido_sacado')), 2)
        saldo_bruto_atual = 0.0 if tipo == 'exauridos' else round(_para_float(item.get('Bruto')), 2)
        saldo_liquido_atual = 0.0 if tipo == 'exauridos' else round(_para_float(item.get('Líquido')), 2)
        patrimonio_liquido = round(total_liquido_sacado + saldo_liquido_atual, 2)
        rendimento_liquido = round(patrimonio_liquido - valor_original, 2)
        linhas.append({
            'Lote ID': item.get('Lote'),
            'Carteira': item.get('Produto'),
            'Data Aplicação': item.get('Aplicação'),
            'Data Base Fiscal': item.get('Aplicação'),
            'Dias Corridos até Hoje': item.get('Dias corridos'),
            'Dias Úteis até Hoje': item.get('Dias úteis'),
            'Valor Original (R$)': valor_original,
            'Total Bruto Sacado (R$)': total_bruto_sacado,
            'Total Líquido Sacado (R$)': total_liquido_sacado,
            'Saldo Bruto Atual (R$)': saldo_bruto_atual,
            'Saldo Líquido Atual (R$)': saldo_liquido_atual,
            'Patrimônio Líquido até Hoje (R$)': patrimonio_liquido,
            'Rendimento Líquido Acumulado dos Lotes (R$)': rendimento_liquido,
        })
    return linhas


def _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica) -> list[dict[str, object]]:
    linhas = _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo='exauridos') + _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo='ativos')
    valor_original_total = round(sum(_para_float(item.get('Valor Original (R$)')) for item in linhas), 2)
    valor_total_bruto_sacado = round(sum(_para_float(item.get('Total Bruto Sacado (R$)')) for item in linhas), 2)
    valor_total_liquido_sacado = round(sum(_para_float(item.get('Total Líquido Sacado (R$)')) for item in linhas), 2)
    valor_bruto_atual = round(sum(_para_float(item.get('Saldo Bruto Atual (R$)')) for item in linhas), 2)
    valor_liquido_atual = round(sum(_para_float(item.get('Saldo Líquido Atual (R$)')) for item in linhas), 2)
    patrimonio_liquido_atual = round(sum(_para_float(item.get('Patrimônio Líquido até Hoje (R$)')) for item in linhas), 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_total, 2)
    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor total bruto sacado', 'Valor': valor_total_bruto_sacado},
        {'Métrica': 'Valor total líquido sacado', 'Valor': valor_total_liquido_sacado},
        {'Métrica': 'Valor bruto atual', 'Valor': valor_bruto_atual},
        {'Métrica': 'Valor líquido atual', 'Valor': valor_liquido_atual},
        {'Métrica': 'Patrimônio líquido atual', 'Valor': patrimonio_liquido_atual},
        {'Métrica': 'Rendimento líquido atual', 'Valor': rendimento_liquido_atual},
    ]


def _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None:
    _imprimir_titulo('SITUAÇÃO ATUAL')
    if resumo_fechamento:
        _imprimir_pares([
            ('data de referência', resumo_fechamento.get('data_referencia')),
            ('status do fechamento econômico', resumo_fechamento.get('status_fechamento')),
            ('fonte do fechamento', resumo_fechamento.get('fonte_fechamento')),
            ('fechamentos com fallback CDI', resumo_fechamento.get('qtd_fechamentos_fallback_cdi', 0)),
            ('último fator explícito CDI', resumo_fechamento.get('data_ultimo_fator_explicito_cdi')),
            ('data confirmada da série', resumo_fechamento.get('data_fechamento_confirmado')),
        ])
        if resumo_fechamento.get('observacao'):
            print(f"- leitura auditável: {resumo_fechamento.get('observacao')}")

    print('\n- lotes exauridos:')
    linhas_exauridos = _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo='exauridos')
    if linhas_exauridos:
        _imprimir_tabela(COLUNAS_LOTES_CONSOLIDADOS, linhas_exauridos, limite=None)
    else:
        print('  [OK] sem lotes exauridos nesta execução')

    print('\n- lotes ativos:')
    linhas_ativos = _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo='ativos')
    if linhas_ativos:
        _imprimir_tabela(COLUNAS_LOTES_CONSOLIDADOS, linhas_ativos, limite=None)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')

    print('\n- patrimônio total dos lotes:')
    _imprimir_tabela(['Métrica', 'Valor'], _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica), limite=None)

    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))


def main() -> None:
    contexto_baseline = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    pacote_config = contexto_baseline.pacote_config
    contexto = contexto_baseline.execucao
    pacote_planilha = contexto_baseline.pacote_planilha
    carteira_canonica = contexto_baseline.carteira_canonica
    cache_cdi = contexto_baseline.cache_cdi
    saida_canonica = construir_saida_canonica(contexto_baseline, versao=VERSAO_BASELINE)

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item['nome_aba']: item for item in resumo_planilha}
    abas_cfg = pacote_config.conteudo.get('abas', {}) if isinstance(pacote_config.conteudo.get('abas'), dict) else {}
    nome_aba_carteira_real = getattr(carteira_canonica, 'nome_aba', abas_cfg.get('carteira', 'Carteira'))
    abas_primarias_reais = [
        ('carteira', nome_aba_carteira_real),
        ('lotes', abas_cfg.get('lotes', 'Inventário de Lotes')),
        ('despesas', abas_cfg.get('despesas', 'Todos os Gastos')),
    ]
    abas_auxiliares = [nome for nome in pacote_planilha.nomes_abas if nome not in {aba for _, aba in abas_primarias_reais}]

    severidade_dependencias = _severidade(
        avisos=contexto.relatorio_dependencias.get('ausentes', []),
        condicao_ok=len(contexto.relatorio_dependencias.get('ausentes', [])) == 0,
    )
    auditoria_cache_cdi = cache_cdi.auditoria or {}
    data_ultimo_fator_cdi = max(cache_cdi.serie_cdi.keys()) if cache_cdi.serie_cdi else None

    render_secao_execucao(
        versao=VERSAO_BASELINE,
        pacote_config=pacote_config,
        pacote_planilha=pacote_planilha,
        contexto=contexto,
        severidade_dependencias=severidade_dependencias,
        auditoria_cache_cdi=auditoria_cache_cdi,
        data_ultimo_fator_cdi=data_ultimo_fator_cdi,
        resumo_por_aba=resumo_por_aba,
        abas_primarias_reais=abas_primarias_reais,
        abas_auxiliares=abas_auxiliares,
    )

    render_secao_amostras_pagamentos(
        pagamentos_realizados=saida_canonica.pagamentos_realizados_console(limite=5),
        pagamentos_proximos=saida_canonica.pagamentos_proximos_console(limite=5),
    )
    _render_secao_ranking_oficial(contexto_baseline, saida_canonica)
    _render_secao_switchings_oficiais(contexto_baseline, saida_canonica)

    resumo_fechamento_bruto = {item.get('Métrica'): item.get('Valor') for item in saida_canonica.fechamento_atual}
    mapeamento_fechamento = {
        'Data de referência': 'data_referencia',
        'Status do fechamento econômico': 'status_fechamento',
        'Fonte do fechamento': 'fonte_fechamento',
        'Fechamentos com fallback CDI': 'qtd_fechamentos_fallback_cdi',
        'Último fator explícito CDI': 'data_ultimo_fator_explicito_cdi',
        'Data confirmada da série': 'data_fechamento_confirmado',
        'Leitura auditável': 'observacao',
    }
    resumo_fechamento_situacao_atual = {chave: valor for chave, valor in resumo_fechamento_bruto.items() if chave is not None}
    for rotulo_humano, chave_tecnica in mapeamento_fechamento.items():
        if chave_tecnica not in resumo_fechamento_situacao_atual and rotulo_humano in resumo_fechamento_bruto:
            resumo_fechamento_situacao_atual[chave_tecnica] = resumo_fechamento_bruto.get(rotulo_humano)
    resumo_recebidos_saida = {item.get('Métrica'): item.get('Valor') for item in saida_canonica.resumo_recebidos}
    _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento_situacao_atual, resumo_recebidos_saida)


# ============================================================
# OVERRIDE V225 — Situação Atual em tabelas curtas
# ============================================================

COLS_LOTES_ID_CURTAS = [
    'Lote',
    'Carteira',
    'Aplic.',
    'Base fiscal',
    'Dias corr.',
    'Dias úteis',
]

COLS_LOTES_VALORES_CURTAS = [
    'Lote',
    'Orig.',
    'Bruto sac.',
    'Líq. sac.',
    'Bruto atual',
    'Líq. atual',
    'Patr. líq.',
    'Rend. líq.',
]


def _linhas_lotes_id_curta(contexto_baseline, saida_canonica, *, tipo: str) -> list[dict]:
    linhas_base = _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo=tipo)
    linhas = []
    for item in linhas_base:
        linhas.append({
            'Lote': item.get('Lote ID'),
            'Carteira': item.get('Carteira'),
            'Aplic.': item.get('Data Aplicação'),
            'Base fiscal': item.get('Data Base Fiscal'),
            'Dias corr.': item.get('Dias Corridos até Hoje'),
            'Dias úteis': item.get('Dias Úteis até Hoje'),
        })
    return linhas


def _linhas_lotes_valores_curta(contexto_baseline, saida_canonica, *, tipo: str) -> list[dict]:
    linhas_base = _linhas_lotes_consolidados(contexto_baseline, saida_canonica, tipo=tipo)
    linhas = []
    for item in linhas_base:
        linhas.append({
            'Lote': item.get('Lote ID'),
            'Orig.': item.get('Valor Original (R$)'),
            'Bruto sac.': item.get('Total Bruto Sacado (R$)'),
            'Líq. sac.': item.get('Total Líquido Sacado (R$)'),
            'Bruto atual': item.get('Saldo Bruto Atual (R$)'),
            'Líq. atual': item.get('Saldo Líquido Atual (R$)'),
            'Patr. líq.': item.get('Patrimônio Líquido até Hoje (R$)'),
            'Rend. líq.': item.get('Rendimento Líquido Acumulado dos Lotes (R$)'),
        })
    return linhas


def _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None:
    _imprimir_titulo('SITUAÇÃO ATUAL')

    if resumo_fechamento:
        _imprimir_pares([
            ('data de referência', resumo_fechamento.get('data_referencia')),
            ('status do fechamento econômico', resumo_fechamento.get('status_fechamento')),
            ('fonte do fechamento', resumo_fechamento.get('fonte_fechamento')),
            ('fechamentos com fallback CDI', resumo_fechamento.get('qtd_fechamentos_fallback_cdi', 0)),
            ('último fator explícito CDI', resumo_fechamento.get('data_ultimo_fator_explicito_cdi')),
            ('data confirmada da série', resumo_fechamento.get('data_fechamento_confirmado')),
        ])
        if resumo_fechamento.get('observacao'):
            print(f"- leitura auditável: {resumo_fechamento.get('observacao')}")

    print('\n- lotes exauridos:')
    linhas_exauridos_id = _linhas_lotes_id_curta(contexto_baseline, saida_canonica, tipo='exauridos')
    linhas_exauridos_val = _linhas_lotes_valores_curta(contexto_baseline, saida_canonica, tipo='exauridos')
    if linhas_exauridos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_ID_CURTAS, linhas_exauridos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, linhas_exauridos_val, limite=None)
    else:
        print('  [OK] sem lotes exauridos nesta execução')

    print('\n- lotes ativos:')
    linhas_ativos_id = _linhas_lotes_id_curta(contexto_baseline, saida_canonica, tipo='ativos')
    linhas_ativos_val = _linhas_lotes_valores_curta(contexto_baseline, saida_canonica, tipo='ativos')
    if linhas_ativos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_ID_CURTAS, linhas_ativos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, linhas_ativos_val, limite=None)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')

    print('\n- patrimônio total dos lotes:')
    _imprimir_tabela(['Métrica', 'Valor'], _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica), limite=None)

    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))



from nucleo.saida_observavel import (
    COLS_LOTES_ID_CURTAS,
    COLS_LOTES_VALORES_CURTAS,
    construir_linhas_lotes_id_curta,
    construir_linhas_lotes_valores_curta,
    construir_resumo_patrimonio_total_lotes,
)


def _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None:
    _imprimir_titulo('SITUAÇÃO ATUAL')

    if resumo_fechamento:
        _imprimir_pares([
            ('data de referência', resumo_fechamento.get('data_referencia')),
            ('status do fechamento econômico', resumo_fechamento.get('status_fechamento')),
            ('fonte do fechamento', resumo_fechamento.get('fonte_fechamento')),
            ('fechamentos com fallback CDI', resumo_fechamento.get('qtd_fechamentos_fallback_cdi', 0)),
            ('último fator explícito CDI', resumo_fechamento.get('data_ultimo_fator_explicito_cdi')),
            ('data confirmada da série', resumo_fechamento.get('data_fechamento_confirmado')),
        ])
        if resumo_fechamento.get('observacao'):
            print(f"- leitura auditável: {resumo_fechamento.get('observacao')}")

    print('\n- lotes exauridos:')
    exauridos_id = construir_linhas_lotes_id_curta(contexto_baseline, saida_canonica, tipo='exauridos')
    exauridos_val = construir_linhas_lotes_valores_curta(contexto_baseline, saida_canonica, tipo='exauridos')
    if exauridos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_ID_CURTAS, exauridos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, exauridos_val, limite=None)
    else:
        print('  [OK] sem lotes exauridos nesta execução')

    print('\n- lotes ativos:')
    ativos_id = construir_linhas_lotes_id_curta(contexto_baseline, saida_canonica, tipo='ativos')
    ativos_val = construir_linhas_lotes_valores_curta(contexto_baseline, saida_canonica, tipo='ativos')
    if ativos_id:
        print('  identificação:')
        _imprimir_tabela(COLS_LOTES_ID_CURTAS, ativos_id, limite=None)
        print('\n  valores e patrimônio:')
        _imprimir_tabela(COLS_LOTES_VALORES_CURTAS, ativos_val, limite=None)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')

    print('\n- patrimônio total dos lotes:')
    _imprimir_tabela(['Métrica', 'Valor'], construir_resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica), limite=None)

    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))


if __name__ == '__main__':
    main()
