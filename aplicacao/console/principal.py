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
from aplicacao.console.secoes_financeiras import (
    render_secao_amostras_pagamentos,
    render_secao_situacao_atual,
)
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


def _lotes_exauridos_com_valores_usados(contexto_baseline, saida_canonica) -> list[dict]:
    """Retorna linhas de exauridos com Bruto/Líquido efetivamente usados.

    A saída canônica mantém os lotes exauridos com saldo atual zerado.
    Para a tabela observável do console, contudo, Bruto e Líquido devem
    representar o total usado/resgatado do lote no replay histórico.
    """
    linhas = [dict(item) for item in (getattr(saida_canonica, 'lotes_exauridos', []) or [])]
    replay = getattr(contexto_baseline, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    if not isinstance(log, pd.DataFrame) or len(log) == 0 or 'Lote' not in log.columns:
        return linhas

    bruto_por_lote: dict[str, float] = {}
    liquido_por_lote: dict[str, float] = {}
    for _, row in log.iterrows():
        lote_id = str(row.get('Lote') or '').strip()
        if not lote_id:
            continue
        bruto_por_lote[lote_id] = round(bruto_por_lote.get(lote_id, 0.0) + _para_float(row.get('Bruto')), 2)
        liquido_por_lote[lote_id] = round(liquido_por_lote.get(lote_id, 0.0) + _para_float(row.get('Liquido')), 2)

    for item in linhas:
        lote_id = str(item.get('Lote') or '').strip()
        if lote_id in bruto_por_lote or lote_id in liquido_por_lote:
            item['Bruto'] = round(bruto_por_lote.get(lote_id, 0.0), 2)
            item['Líquido'] = round(liquido_por_lote.get(lote_id, 0.0), 2)
            item['Saldo rem'] = 0.0
    return linhas


def _calcular_rendimento_total_lotes(contexto_baseline, saida_canonica) -> dict[str, float]:
    lotes_exauridos = list(getattr(saida_canonica, 'lotes_exauridos', []) or [])
    lotes_ativos = list(getattr(saida_canonica, 'lotes_ativos', []) or [])
    lotes_visiveis = lotes_exauridos + lotes_ativos

    valor_original_total = round(sum(_para_float(item.get('Valor original')) for item in lotes_visiveis), 2)
    valor_original_exaurido_sem_aplicacao = round(
        sum(_para_float(item.get('Valor original')) for item in lotes_exauridos if _lote_exaurido_sem_aplicacao(item)),
        2,
    )
    valor_original_aplicado_ajustado = round(valor_original_total - valor_original_exaurido_sem_aplicacao, 2)

    bruto_atual_total = round(sum(_para_float(item.get('Bruto')) for item in lotes_visiveis), 2)
    liquido_atual_total = round(sum(_para_float(item.get('Líquido')) for item in lotes_visiveis), 2)

    replay = getattr(contexto_baseline, 'replay_passado', None)
    log = getattr(replay, 'log_passado', None) if replay is not None else None
    if isinstance(log, pd.DataFrame) and len(log):
        bruto_resgatado_total = round(float(log['Bruto'].fillna(0).sum()) if 'Bruto' in log.columns else 0.0, 2)
        liquido_resgatado_total = round(float(log['Liquido'].fillna(0).sum()) if 'Liquido' in log.columns else 0.0, 2)
    else:
        bruto_resgatado_total = 0.0
        liquido_resgatado_total = 0.0

    rendimento_bruto_total = round(valor_original_aplicado_ajustado - bruto_resgatado_total - bruto_atual_total, 2)
    rendimento_liquido_total = round(valor_original_aplicado_ajustado - liquido_resgatado_total - liquido_atual_total, 2)

    return {
        'valor_original_total': valor_original_total,
        'valor_original_exaurido_sem_aplicacao': valor_original_exaurido_sem_aplicacao,
        'valor_original_aplicado_ajustado': valor_original_aplicado_ajustado,
        'bruto_resgatado_total': bruto_resgatado_total,
        'liquido_resgatado_total': liquido_resgatado_total,
        'bruto_atual_total': bruto_atual_total,
        'liquido_atual_total': liquido_atual_total,
        'rendimento_bruto_total': rendimento_bruto_total,
        'rendimento_liquido_total': rendimento_liquido_total,
        'qtd_lotes_considerados': len(lotes_visiveis),
        'qtd_lotes_exauridos': len(lotes_exauridos),
        'qtd_lotes_ativos': len(lotes_ativos),
        'qtd_lotes_exauridos_sem_aplicacao': sum(1 for item in lotes_exauridos if _lote_exaurido_sem_aplicacao(item)),
    }


def _render_secao_rendimento_total_lotes(contexto_baseline, saida_canonica) -> None:
    resumo = _calcular_rendimento_total_lotes(contexto_baseline, saida_canonica)
    _imprimir_titulo('RENDIMENTO TOTAL DOS LOTES')
    _imprimir_pares([
        ('lotes considerados', resumo['qtd_lotes_considerados']),
        ('lotes exauridos incluídos', resumo['qtd_lotes_exauridos']),
        ('lotes ativos incluídos', resumo['qtd_lotes_ativos']),
        ('lotes exauridos sem aplicação', resumo['qtd_lotes_exauridos_sem_aplicacao']),
        ('valor original total', resumo['valor_original_total']),
        ('valor original exaurido sem aplicação', resumo['valor_original_exaurido_sem_aplicacao']),
        ('valor original aplicado ajustado', resumo['valor_original_aplicado_ajustado']),
        ('bruto já resgatado', resumo['bruto_resgatado_total']),
        ('líquido já resgatado', resumo['liquido_resgatado_total']),
        ('bruto atual remanescente', resumo['bruto_atual_total']),
        ('líquido atual remanescente', resumo['liquido_atual_total']),
        ('rendimento bruto total obtido', resumo['rendimento_bruto_total']),
        ('rendimento líquido total obtido', resumo['rendimento_liquido_total']),
    ])


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
    render_secao_situacao_atual(
        lotes_ativos=saida_canonica.lotes_ativos,
        lotes_exauridos=saida_canonica.lotes_exauridos,
        lotes_exauridos_valores=_lotes_exauridos_com_valores_usados(contexto_baseline, saida_canonica),
        recebidos_atuais=saida_canonica.recebidos_atuais,
        resumo_fechamento=resumo_fechamento_situacao_atual,
        resumo_recebidos=resumo_recebidos_saida,
    )
    _render_secao_rendimento_total_lotes(contexto_baseline, saida_canonica)


if __name__ == '__main__':
    main()
