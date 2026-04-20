"""Inspeciona a segunda estrutura real da F1: fonte_elegivel_pagamento por data de pagamento."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline


COLUNAS_EXIBICAO = [
    'pagamento_id',
    'data_pagamento',
    'descricao_pagamento',
    'valor_pagamento',
    'fonte_id',
    'tipo_fonte',
    'lote_id',
    'recebido_id',
    'valor_bruto_disponivel',
    'valor_liquido_disponivel',
    'elegivel_na_data_pagamento',
    'origem_status',
    'motivo_bloqueio_temporal',
    'metodo_valor_disponivel',
    'observacao_auditavel',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.fontes_elegiveis_pagamento
    quadro = pacote.quadro_fontes_elegiveis
    auditoria = pacote.auditoria

    print('=== FONTES ELEGÍVEIS DE PAGAMENTO (F1 / ETAPA 4) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_alvo: {auditoria.get('resumo', {}).get('total_pagamentos_alvo')}")
    print(f"total_fontes_pagamento: {len(quadro)}")
    print(f"status_validacao: {'OK' if auditoria.get('validacao', {}).get('ok') else 'FALHA'}")
    print(f"resumo_tipo: {auditoria.get('resumo', {}).get('tipo_fonte', {})}")
    print(f"resumo_status: {auditoria.get('resumo', {}).get('origem_status', {})}")
    print(f"resumo_elegibilidade: {auditoria.get('resumo', {}).get('elegivel_na_data_pagamento', {})}")
    print(
        'pagamentos_com_alguma_fonte_elegivel: '
        f"{auditoria.get('resumo', {}).get('pagamentos_com_alguma_fonte_elegivel')}"
    )
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
