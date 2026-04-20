"""Inspeciona a terceira estrutura real da F1: saldo_disponivel geral por pagamento."""

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
    'saldo_disponivel_bruto',
    'saldo_disponivel_liquido',
    'saldo_disponivel_elegivel',
    'origem_status',
    'origem_saldo',
    'qtd_fontes_componentes',
    'tipos_fontes_componentes',
    'regra_precedencia_intradiaria',
    'restricao_duplicidade_recebidos',
    'metodo_saldo',
    'observacao_auditavel',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ)
    pacote = contexto.saldo_disponivel_geral
    quadro = pacote.quadro_saldo_disponivel
    auditoria = pacote.auditoria

    print('=== SALDO DISPONÍVEL GERAL (F1 / ETAPA 5) ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_alvo: {auditoria.get('resumo', {}).get('total_pagamentos_alvo')}")
    print(f"total_linhas_saldo: {len(quadro)}")
    print(f"status_validacao: {'OK' if auditoria.get('validacao', {}).get('ok') else 'FALHA'}")
    print(f"resumo_origem_status: {auditoria.get('resumo', {}).get('origem_status', {})}")
    print(f"resumo_origem_saldo: {auditoria.get('resumo', {}).get('origem_saldo', {})}")
    print('pagamentos_com_saldo_disponivel: ' f"{auditoria.get('resumo', {}).get('pagamentos_com_saldo_disponivel')}")
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
