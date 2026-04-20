"""Inspeciona o planejamento conjunto local do bloco crítico."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'politica_id', 'lote_final_planejamento',
    'status_planejamento', 'score_planejamento', 'saldo_antes_planejamento', 'liquido_planejamento', 'pagamento_totalmente_coberto_planejamento',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.planejamento_conjunto_local_bloco_critico_v1
    quadro = pacote.quadro_planejamento_conjunto_local
    comparativo = pacote.quadro_comparativo_politicas
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== PLANEJAMENTO CONJUNTO LOCAL — BLOCO CRÍTICO V1 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'pagamentos_no_bloco_critico', 'politicas_avaliadas', 'politica_escolhida', 'descricao_politica_escolhida',
        'evento_ancora_data', 'evento_ancora_pagamento', 'evento_ancora_valor',
        'liquido_coberto_ancora_escolhida', 'deficit_ancora_escolhida', 'cobertura_integral_ancora_escolhida',
        'pagamentos_cobertos_bloco_escolhida', 'deficit_total_bloco_escolhida',
        'delta_liquido_ancora_vs_v102', 'delta_liquido_ancora_vs_v103', 'mudancas_vs_v103_escolhida',
        'primeira_sem_cobertura_data_escolhida', 'primeira_sem_cobertura_pagamento_escolhida', 'ganho_material_vs_v103',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1
    print('\n--- AMOSTRA DO COMPARATIVO DE POLÍTICAS ---')
    for item in auditoria.get('amostra_comparativo_politicas', [])[:10]:
        print(item)
    print('\n--- AMOSTRA DAS MUDANÇAS VS V103 ---')
    for item in auditoria.get('amostra_mudancas_vs_v103', [])[:10]:
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
