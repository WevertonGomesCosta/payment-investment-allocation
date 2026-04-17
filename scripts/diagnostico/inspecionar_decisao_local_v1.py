"""Inspeciona a quarta estrutura real da F1: decisão local v1 por pagamento."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'pagamento_id', 'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'fonte_escolhida_id', 'tipo_fonte_escolhida',
    'criterio_decisao', 'custo_economico_proxy', 'valor_disponivel_escolhido', 'pagamento_totalmente_coberto', 'fonte_origem_status',
    'fonte_elegivel_na_data', 'motivo_bloqueio_ou_restricao',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.decisao_local_v1
    quadro = pacote.quadro_decisao_local_v1
    auditoria = pacote.auditoria

    print('=== DECISÃO LOCAL V1 (F1 / ETAPA 6) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_alvo: {auditoria.get('resumo', {}).get('total_pagamentos_alvo')}")
    print(f"total_linhas_decisao: {len(quadro)}")
    print(f"status_validacao: {'OK' if auditoria.get('validacao', {}).get('ok') else 'FALHA'}")
    print(f"resumo_tipo_fonte_escolhida: {auditoria.get('resumo', {}).get('tipo_fonte_escolhida', {})}")
    print(f"resumo_criterio_decisao: {auditoria.get('resumo', {}).get('criterio_decisao', {})}")
    print(f"resumo_fonte_origem_status: {auditoria.get('resumo', {}).get('fonte_origem_status', {})}")
    print('pagamentos_totalmente_cobertos: ' f"{auditoria.get('resumo', {}).get('pagamentos_totalmente_cobertos')}")
    if auditoria.get('validacao', {}).get('avisos'):
        print(f"avisos: {auditoria['validacao']['avisos']}")
    if auditoria.get('validacao', {}).get('erros'):
        print(f"erros: {auditoria['validacao']['erros']}")
        return 1
    if len(quadro) == 0:
        print('quadro vazio')
        return 1
    print('\n--- AMOSTRA ---')
    print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
