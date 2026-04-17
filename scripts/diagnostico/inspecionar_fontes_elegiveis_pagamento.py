"""Inspeciona a segunda estrutura real da F1: fonte_elegivel_pagamento."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline


COLUNAS_EXIBICAO = [
    'fonte_id',
    'tipo_fonte',
    'data_evento',
    'lote_id',
    'recebido_id',
    'produto_nome_canonico',
    'valor_bruto_disponivel',
    'valor_liquido_disponivel',
    'origem_status',
    'carencia_ate_origem',
    'observacao_auditavel',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.fontes_elegiveis_pagamento
    quadro = pacote.quadro_fontes_elegiveis
    auditoria = pacote.auditoria

    print('=== FONTES ELEGÍVEIS DE PAGAMENTO (F1 / ETAPA 3) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_fontes: {len(quadro)}")
    print(f"status_validacao: {'OK' if auditoria.get('validacao', {}).get('ok') else 'FALHA'}")
    print(f"resumo_tipo: {auditoria.get('resumo', {}).get('tipo_fonte', {})}")
    print(f"resumo_status: {auditoria.get('resumo', {}).get('origem_status', {})}")
    if auditoria.get('validacao', {}).get('avisos'):
        print(f"avisos: {auditoria['validacao']['avisos']}")
    if auditoria.get('validacao', {}).get('erros'):
        print(f"erros: {auditoria['validacao']['erros']}")
        return 1

    if len(quadro) == 0:
        print('quadro vazio')
        return 1

    print('\n--- AMOSTRA ---')
    print(quadro[COLUNAS_EXIBICAO].to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
