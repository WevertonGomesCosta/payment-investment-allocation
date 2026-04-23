"""Inspeciona o microplanejamento conjunto do bloco crítico v2."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'politica_id', 'lote_final_microplanejamento',
    'fontes_usadas_microplanejamento', 'multifonte_microplanejamento', 'status_microplanejamento', 'score_microplanejamento',
    'liquido_microplanejamento', 'pagamento_totalmente_coberto_microplanejamento',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.microplanejamento_conjunto_bloco_critico_v2
    quadro = pacote.quadro_microplanejamento_conjunto
    comparativo = pacote.quadro_comparativo_politicas
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== MICROPLANEJAMENTO CONJUNTO — BLOCO CRÍTICO V2 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'pagamentos_no_bloco_critico', 'politicas_avaliadas', 'politica_escolhida', 'descricao_politica_escolhida',
        'evento_ancora_data', 'evento_ancora_pagamento', 'evento_ancora_valor', 'liquido_coberto_ancora_escolhida',
        'deficit_ancora_escolhida', 'cobertura_integral_ancora_escolhida', 'pagamentos_cobertos_bloco_escolhida',
        'deficit_total_bloco_escolhida', 'uso_multifonte_escolhida', 'reservas_acionadas_escolhida',
        'delta_liquido_ancora_vs_v104', 'delta_pagamentos_cobertos_vs_v104', 'primeira_sem_cobertura_data_escolhida',
        'primeira_sem_cobertura_pagamento_escolhida', 'ganho_material_vs_v104', 'lotes_reserva_explicitos',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1
    print('\n--- AMOSTRA DO COMPARATIVO DE POLÍTICAS ---')
    for item in auditoria.get('amostra_comparativo_politicas', [])[:10]:
        print(item)
    print('\n--- AMOSTRA DAS MUDANÇAS VS V104 ---')
    for item in auditoria.get('amostra_mudancas_vs_v104', [])[:10]:
        print(item)
    print('\n--- QUADRO ESCOLHIDO (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    print('\n--- QUADRO COMPARATIVO (AMOSTRA) ---')
    if len(comparativo):
        print(comparativo.head(10).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
