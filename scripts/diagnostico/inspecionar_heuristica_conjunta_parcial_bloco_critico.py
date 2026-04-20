"""Inspeciona a heurística conjunta parcial do bloco crítico."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'pagamento_id', 'valor_pagamento', 'esta_no_bloco_critico',
    'lote_sugerido_original', 'lote_final_heuristica', 'mudou_fonte_heuristica', 'troca_preventiva_heuristica',
    'troca_por_inviabilidade_heuristica', 'score_proxy_original', 'score_proxy_ajustado_heuristica',
    'penalidade_preservacao_estrategica', 'reserva_planejada_fonte', 'status_heuristica',
    'saldo_antes_heuristica', 'saldo_remanescente_heuristica', 'pagamento_totalmente_coberto_heuristica',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.heuristica_conjunta_parcial_bloco_critico
    quadro = pacote.quadro_heuristica_conjunta_parcial
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== HEURÍSTICA CONJUNTA PARCIAL — BLOCO CRÍTICO ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    for chave in [
        'total_pagamentos_auditados', 'pagamentos_no_bloco_critico', 'pagamentos_cobertos_heuristica',
        'pagamentos_sem_cobertura_heuristica', 'pagamentos_cobertos_no_bloco_critico',
        'mudancas_efetivas_de_fonte', 'trocas_preventivas_heuristica', 'trocas_por_inviabilidade_heuristica',
        'primeira_troca_preventiva_data', 'primeira_troca_preventiva_pagamento',
        'primeira_sem_cobertura_data', 'primeira_sem_cobertura_pagamento',
        'atraso_dias_vs_primeira_quebra_temporal', 'atraso_dias_vs_primeira_sem_cobertura_reescolha',
        'quebra_estrutural_adiada_vs_temporal', 'quebra_estrutural_adiada_vs_reescolha',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    if not auditoria.get('validacao', {}).get('ok', False):
        print(f"erros: {auditoria.get('validacao', {}).get('erros', [])}")
        return 1
    print('\n--- AMOSTRA DE TROCAS PREVENTIVAS ---')
    for item in auditoria.get('amostra_trocas_preventivas', [])[:10]:
        print(item)
    print('\n--- AMOSTRA DE PLANEJAMENTO DE RESERVAS ---')
    for item in auditoria.get('amostra_planejamento_reservas', [])[:10]:
        print(item)
    print('\n--- AMOSTRA DE SEM COBERTURA ---')
    for item in auditoria.get('amostra_sem_cobertura', [])[:10]:
        print(item)
    print('\n--- QUADRO HEURÍSTICO (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
