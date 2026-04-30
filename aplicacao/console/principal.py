"Ponto de entrada do console operacional da baseline."

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
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import (
    construir_amostras_pagamentos_operacionais,
    construir_amostra_alocacao_recebidos_futuros,
    COLS_LOTES_ID_CURTAS,
    COLS_LOTES_VALORES_CURTAS,
    construir_linhas_lotes_id_curta,
    construir_linhas_lotes_valores_curta,
    construir_resumo_patrimonio_total_lotes,
)



def _render_amostras_pagamentos_operacionais(saida_canonica) -> None:
    amostras = construir_amostras_pagamentos_operacionais(saida_canonica, limite=5)
    amostras.pop('recebidos_futuros', None)

    _imprimir_titulo(amostras['titulo'])

    realizados = amostras['realizados']
    print(f"- {realizados['rotulo']}:")
    _imprimir_tabela(
        realizados['headers'],
        realizados['linhas'],
        limite=realizados['limite'],
    )

    recebidos_futuros = amostras['recebidos_futuros']
    print(f"\n- {recebidos_futuros['rotulo']}:")
    _imprimir_tabela(
        recebidos_futuros['headers'],
        recebidos_futuros['linhas'],
        limite=recebidos_futuros['limite'],
    )

    proximos = amostras['proximos']
    print(f"\n- {proximos['rotulo']}:")
    _imprimir_tabela(
        proximos['headers'],
        proximos['linhas'],
        limite=proximos['limite'],
    )
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
    _imprimir_tabela(
        ['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.'],
        linhas,
        limite=10,
    )


def _render_secao_switchings_oficiais(contexto_baseline, saida_canonica=None) -> None:
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    destino_top1 = ranking.auditoria.get('destino_top1') if ranking is not None else None
    linhas = list(getattr(saida_canonica, 'switchings', []) or [])[:10]

    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    _imprimir_pares([
        ('lotes avaliados para switching', len(linhas)),
        (
            'destinos elegíveis de switching',
            len(ranking.quadro_destinos_switch)
            if ranking is not None and isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame)
            else 0,
        ),
        ('switchings promovidos/executados', len(linhas)),
        ('destino top 1 do ranking', destino_top1),
        ('origem da amostra', 'saida_canonica_v202'),
    ])

    print('- amostra de switchings reais da janela (independente de pagamentos):')
    _imprimir_tabela(['Data', 'Lote origem', 'Produto origem', 'Destino'], linhas, limite=10)

    alocacao = construir_amostra_alocacao_recebidos_futuros(saida_canonica, limite=5)
    print(f"\n- {alocacao['rotulo']}:")
    _imprimir_tabela(alocacao['headers'], alocacao['linhas'], limite=alocacao['limite'])


def _render_situacao_atual_operacional(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None:
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
    _imprimir_tabela(
        ['Métrica', 'Valor'],
        construir_resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica),
        limite=None,
    )

    if resumo_recebidos:
        print('\n- resumo de recebidos:')
        _imprimir_pares(list(resumo_recebidos.items()))

def render_console(contexto_baseline, saida_canonica=None) -> None:
    """Renderiza o console usando contexto e saída canônica já construídos.

    Esta função não carrega planilha, não baixa dados e não reconstrói cache.
    Ela apenas renderiza o estado recebido.
    """
    if saida_canonica is None:
        saida_canonica = construir_saida_canonica(contexto_baseline, versao=VERSAO_BASELINE)

    pacote_config = contexto_baseline.pacote_config
    contexto = contexto_baseline.execucao
    pacote_planilha = contexto_baseline.pacote_planilha
    carteira_canonica = contexto_baseline.carteira_canonica
    cache_cdi = contexto_baseline.cache_cdi

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item["nome_aba"]: item for item in resumo_planilha}

    abas_cfg = pacote_config.conteudo.get("abas", {}) if isinstance(pacote_config.conteudo.get("abas"), dict) else {}
    nome_aba_carteira_real = getattr(carteira_canonica, "nome_aba", abas_cfg.get("carteira", "Carteira"))

    abas_primarias_reais = [
        ("carteira", nome_aba_carteira_real),
        ("lotes", abas_cfg.get("lotes", "Inventário de Lotes")),
        ("despesas", abas_cfg.get("despesas", "Todos os Gastos")),
    ]

    abas_auxiliares = [
        nome for nome in pacote_planilha.nomes_abas
        if nome not in {aba for _, aba in abas_primarias_reais}
    ]

    severidade_dependencias = _severidade(
        avisos=contexto.relatorio_dependencias.get("ausentes", []),
        condicao_ok=len(contexto.relatorio_dependencias.get("ausentes", [])) == 0,
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

    _render_amostras_pagamentos_operacionais(saida_canonica)

    _render_secao_ranking_oficial(contexto_baseline, saida_canonica)
    _render_secao_switchings_oficiais(contexto_baseline, saida_canonica)

    resumo_fechamento_bruto = {
        item.get("Métrica"): item.get("Valor")
        for item in saida_canonica.fechamento_atual
    }

    mapeamento_fechamento = {
        "Data de referência": "data_referencia",
        "Status do fechamento econômico": "status_fechamento",
        "Fonte do fechamento": "fonte_fechamento",
        "Fechamentos com fallback CDI": "qtd_fechamentos_fallback_cdi",
        "Último fator explícito CDI": "data_ultimo_fator_explicito_cdi",
        "Data confirmada da série": "data_fechamento_confirmado",
        "Leitura auditável": "observacao",
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
        item.get("Métrica"): item.get("Valor")
        for item in saida_canonica.resumo_recebidos
    }

    _render_situacao_atual_operacional(
        contexto_baseline,
        saida_canonica,
        resumo_fechamento_situacao_atual,
        resumo_recebidos_saida,
    )


def main() -> None:
    """Execução standalone do console. Para a rota oficial integrada, use aplicacao/principal.py."""
    contexto_baseline = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida_canonica = construir_saida_canonica(contexto_baseline, versao=VERSAO_BASELINE)
    render_console(contexto_baseline, saida_canonica)

if __name__ == '__main__':
    main()
