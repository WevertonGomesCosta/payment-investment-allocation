from __future__ import annotations

from aplicacao.console.common import imprimir_linha_status, imprimir_pares, imprimir_tabela, imprimir_titulo


def render_secao_triagem(*, auditoria_triagem, contexto_triagem, severidade_triagem):
    imprimir_titulo('TRIAGEM PRELIMINAR PROXY DO MOTOR — SCORE V1')
    imprimir_linha_status('Seleção contextual preliminar de candidatos', severidade_triagem, 'proxy de triagem; nao e decisao final do motor, sem replay, sem nucleo financeiro e sem switching economico; calibracao conservadora nesta fase')
    imprimir_pares([
        ('produtos totais no universo', auditoria_triagem.get('qtd_total_produtos', 0)),
        ('elegíveis brutos', auditoria_triagem.get('qtd_elegiveis_brutos', 0)),
        ('candidatos motor v1', auditoria_triagem.get('qtd_candidatos_motor_v1', 0)),
        ('top_k global', auditoria_triagem.get('top_k_global', 0)),
        ('top_k por família', auditoria_triagem.get('top_k_por_familia', 0)),
        ('score mínimo seleção', auditoria_triagem.get('score_minimo_selecao', 0.0)),
        ('modo de calibração', auditoria_triagem.get('modo_calibracao', 'nao informado')),
        ('fração elegíveis selecionados', auditoria_triagem.get('fracao_elegiveis_selecionados', 0.0)),
        ('elegíveis não selecionados', auditoria_triagem.get('qtd_elegiveis_nao_selecionados', 0)),
        ('recursos disponíveis para aporte', contexto_triagem.get('recursos_disponiveis_para_aporte', 0.0)),
        ('recursos aportados observados', contexto_triagem.get('recursos_aportados_observados', 0.0)),
        ('despesas futuras 30 dias', contexto_triagem.get('despesas_futuras_30_dias', 0.0)),
        ('cobertura caixa 30 dias', round(float(contexto_triagem.get('cobertura_caixa_30_dias', 0.0) or 0.0), 4)),
    ])
    if auditoria_triagem.get('resumo_familia_produto'):
        print('- famílias no universo único da carteira:')
        for chave, valor in auditoria_triagem.get('resumo_familia_produto', {}).items():
            print(f"  [OK] {chave}: {valor}")

    imprimir_titulo('TOP PRODUTOS SELECIONADOS — SCORE V1')
    if auditoria_triagem.get('amostra_top_produtos'):
        linhas_top = []
        for idx, item in enumerate(auditoria_triagem.get('amostra_top_produtos', []), start=1):
            linhas_top.append({
                'Rank': idx,
                'Produto': item.get('nome'),
                'Score': round(float(item.get('score_final') or 0.0), 2),
                'Família': item.get('familia_produto'),
                'Regime': item.get('regime_taxa'),
            })
        imprimir_tabela(['Rank', 'Produto', 'Score', 'Família', 'Regime'], linhas_top, limite=10)
    else:
        print('  [OK] sem produtos selecionados nesta execução')
