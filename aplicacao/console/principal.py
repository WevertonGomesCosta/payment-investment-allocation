"""Ponto de entrada do console operacional da baseline."""

from __future__ import annotations

import sys
from pathlib import Path
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


def _para_float(valor) -> float:
    try:
        if valor is None or valor == '':
            return 0.0
        return float(valor)
    except Exception:
        return 0.0


def _lote_exaurido_sem_aplicacao(item: dict) -> bool:
    produto = str(item.get('Produto') or '').strip().lower()
    return produto in {'-', '', 'sem aplicação', 'sem aplicacao', 'não aplicado', 'nao aplicado'}


def _somas_sacadas_por_lote(contexto_baseline) -> dict[str, dict[str, float]]:
    replay = getattr(contexto_baseline, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    somas: dict[str, dict[str, float]] = {}
    if not isinstance(log, pd.DataFrame) or len(log) == 0 or 'Lote' not in log.columns:
        return somas
    for _, row in log.iterrows():
        lote_id = str(row.get('Lote') or '').strip()
        if not lote_id:
            continue
        atual = somas.setdefault(lote_id, {'bruto_sacado': 0.0, 'liquido_sacado': 0.0})
        atual['bruto_sacado'] = round(atual['bruto_sacado'] + _para_float(row.get('Bruto')), 2)
        atual['liquido_sacado'] = round(atual['liquido_sacado'] + _para_float(row.get('Liquido') if 'Liquido' in row else row.get('Líquido')), 2)
    return somas


def _lotes_exauridos_com_valores_usados(contexto_baseline, saida_canonica) -> list[dict]:
    somas = _somas_sacadas_por_lote(contexto_baseline)
    linhas = []
    for item in (getattr(saida_canonica, 'lotes_exauridos', []) or []):
        lote_id = str(item.get('Lote') or '').strip()
        valores = somas.get(lote_id, {})
        valor_original = _para_float(item.get('Valor original'))
        liquido_sacado = round(_para_float(valores.get('liquido_sacado')), 2)
        patrimonio_liquido = round(liquido_sacado, 2)
        linhas.append({
            'Lote': item.get('Lote'),
            'Valor original': valor_original,
            'Bruto Sacado': round(_para_float(valores.get('bruto_sacado')), 2),
            'Líquido Sacado': liquido_sacado,
            'Patrimônio líquido': patrimonio_liquido,
            'Rendimento líquido': round(patrimonio_liquido - valor_original, 2),
        })
    return linhas


def _lotes_ativos_com_valores_atuais(contexto_baseline, saida_canonica) -> list[dict]:
    somas = _somas_sacadas_por_lote(contexto_baseline)
    linhas = []
    for item in (getattr(saida_canonica, 'lotes_ativos', []) or []):
        lote_id = str(item.get('Lote') or '').strip()
        valores = somas.get(lote_id, {})
        valor_original = _para_float(item.get('Valor original'))
        liquido_sacado = round(_para_float(valores.get('liquido_sacado')), 2)
        liquido_atual = round(_para_float(item.get('Líquido')), 2)
        patrimonio_liquido_atual = round(liquido_sacado + liquido_atual, 2)
        linhas.append({
            'Lote': item.get('Lote'),
            'Valor original': valor_original,
            'Bruto Atual': round(_para_float(item.get('Bruto')), 2),
            'Líquido Atual': liquido_atual,
            'Patrimônio líquido atual': patrimonio_liquido_atual,
            'Rendimento líquido atual': round(patrimonio_liquido_atual - valor_original, 2),
        })
    return linhas


def _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica) -> list[dict[str, object]]:
    lotes_exauridos = list(getattr(saida_canonica, 'lotes_exauridos', []) or [])
    lotes_ativos = list(getattr(saida_canonica, 'lotes_ativos', []) or [])
    lotes_visiveis = lotes_exauridos + lotes_ativos
    somas = _somas_sacadas_por_lote(contexto_baseline)

    valor_original_total = round(sum(_para_float(item.get('Valor original')) for item in lotes_visiveis), 2)
    valor_original_exaurido_sem_aplicacao = round(
        sum(_para_float(item.get('Valor original')) for item in lotes_exauridos if _lote_exaurido_sem_aplicacao(item)),
        2,
    )
    valor_original_aplicado_ajustado = round(valor_original_total - valor_original_exaurido_sem_aplicacao, 2)
    valor_total_bruto_sacado = round(sum(v['bruto_sacado'] for v in somas.values()), 2)
    valor_total_liquido_sacado = round(sum(v['liquido_sacado'] for v in somas.values()), 2)
    valor_bruto_atual = round(sum(_para_float(item.get('Bruto')) for item in lotes_ativos), 2)
    valor_liquido_atual = round(sum(_para_float(item.get('Líquido')) for item in lotes_ativos), 2)
    patrimonio_liquido_atual = round(valor_total_liquido_sacado + valor_liquido_atual, 2)
    rendimento_liquido_atual = round(patrimonio_liquido_atual - valor_original_aplicado_ajustado, 2)

    return [
        {'Métrica': 'Valor original total', 'Valor': valor_original_total},
        {'Métrica': 'Valor original exaurido sem aplicação', 'Valor': valor_original_exaurido_sem_aplicacao},
        {'Métrica': 'Valor original aplicado ajustado', 'Valor': valor_original_aplicado_ajustado},
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

    lotes_exauridos = list(getattr(saida_canonica, 'lotes_exauridos', []) or [])
    lotes_ativos = list(getattr(saida_canonica, 'lotes_ativos', []) or [])

    print('\n- lotes exauridos:')
    if lotes_exauridos:
        print('  identificação e tempo:')
        _imprimir_tabela(['Lote', 'Recebimento', 'Aplicação', 'Último uso', 'Produto', 'Dias corridos', 'Dias úteis'], lotes_exauridos, limite=None)
        print('\n  valores sacados e patrimônio:')
        _imprimir_tabela(['Lote', 'Valor original', 'Bruto Sacado', 'Líquido Sacado', 'Patrimônio líquido', 'Rendimento líquido'], _lotes_exauridos_com_valores_usados(contexto_baseline, saida_canonica), limite=None)
    else:
        print('  [OK] sem lotes exauridos nesta execução')

    print('\n- lotes ativos:')
    if lotes_ativos:
        print('  identificação e tempo:')
        _imprimir_tabela(['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias corridos', 'Dias úteis'], lotes_ativos, limite=None)
        print('\n  valores atuais e patrimônio:')
        _imprimir_tabela(['Lote', 'Valor original', 'Bruto Atual', 'Líquido Atual', 'Patrimônio líquido atual', 'Rendimento líquido atual'], _lotes_ativos_com_valores_atuais(contexto_baseline, saida_canonica), limite=None)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')

    print('\n- patrimônio total dos lotes:')
    _imprimir_tabela(['Métrica', 'Valor'], _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica), limite=None)

    recebidos_atuais = list(getattr(saida_canonica, 'recebidos_atuais', []) or [])
    print('\n- recebidos auditáveis:')
    if recebidos_atuais:
        _imprimir_tabela(['Recebido', 'Lote origem', 'Recebimento', 'Aplicação', 'Valor bruto', 'Valor líquido', 'Status', 'Destino', 'Pagamentos vinculados', 'Valor vinculado', 'Residual aplicação', 'Disponível ref', 'Observação'], recebidos_atuais, limite=None)
    else:
        print('  [OK] sem recebidos auditáveis nesta execução')
    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))


def _render_secao_patrimonio_total_lotes(contexto_baseline, saida_canonica) -> None:
    _imprimir_titulo('PATRIMÔNIO TOTAL DOS LOTES')
    _imprimir_pares([(item['Métrica'], item['Valor']) for item in _resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica)])


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

    resumo_fechamento_bruto = {
        item.get('Métrica'): item.get('Valor')
        for item in saida_canonica.fechamento_atual
    }
    mapeamento_fechamento = {
        'Data de referência': 'data_referencia',
        'Status do fechamento econômico': 'status_fechamento',
        'Fonte do fechamento': 'fonte_fechamento',
        'Fechamentos com fallback CDI': 'qtd_fechamentos_fallback_cdi',
        'Último fator explícito CDI': 'data_ultimo_fator_explicito_cdi',
        'Data confirmada da série': 'data_fechamento_confirmado',
        'Leitura auditável': 'observacao',
    }
    resumo_fechamento_situacao_atual = {
        chave: valor
        for chave, valor in resumo_fechamento_bruto.items()
        if chave is not None
    }
    for rotulo_humano, chave_tecnica in mapeamento_fechamento.items():
        if chave_tecnica not in resumo_fechamento_situacao_atual and rotulo_humano in resumo_fechamento_bruto:
            resumo_fechamento_situacao_atual[chave_tecnica] = resumo_fechamento_bruto.get(rotulo_humano)
    resumo_recebidos_saida = {
        item.get('Métrica'): item.get('Valor')
        for item in saida_canonica.resumo_recebidos
    }
    _render_secao_situacao_atual(
        contexto_baseline,
        saida_canonica,
        resumo_fechamento_situacao_atual,
        resumo_recebidos_saida,
    )
    _render_secao_patrimonio_total_lotes(contexto_baseline, saida_canonica)


if __name__ == '__main__':
    main()
