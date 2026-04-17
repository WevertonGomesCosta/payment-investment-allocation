"""Inspeciona a primeira estrutura real da F1: recebido_auditavel."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline


COLUNAS_EXIBICAO = [
    'recebido_id',
    'lote_id_origem',
    'data_recebimento',
    'data_aplicacao',
    'valor_bruto',
    'status_recebido',
    'destino_potencial',
    'qtd_pagamentos_vinculados',
    'valor_pagamentos_pre_aplicacao',
    'valor_pagamentos_pos_aplicacao',
    'valor_residual_para_aplicacao_origem',
    'observacao_auditavel',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.recebidos_auditaveis
    quadro = pacote.quadro_recebidos_auditaveis
    auditoria = pacote.auditoria

    print('=== RECEBIDOS AUDITÁVEIS (F1 / ETAPA 2) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_recebidos: {len(quadro)}")
    print(f"status_validacao: {'OK' if auditoria.get('validacao', {}).get('ok') else 'FALHA'}")
    print(f"resumo_status: {auditoria.get('resumo', {}).get('status_recebido', {})}")
    print(f"resumo_destino: {auditoria.get('resumo', {}).get('destino_potencial', {})}")
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
