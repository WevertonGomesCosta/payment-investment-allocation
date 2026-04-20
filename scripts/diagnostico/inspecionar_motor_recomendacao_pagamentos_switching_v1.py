from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ


from nucleo.contexto_baseline import carregar_contexto_baseline


def main() -> None:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False)
    pacote = contexto.motor_recomendacao_pagamentos_switching_v1
    df = pacote.quadro_recomendacoes.copy()
    resumo = pacote.auditoria.get('resumo', {})
    print('=== MOTOR RECOMENDACAO PAGAMENTOS + SWITCHING V1 ===')
    for chave, valor in resumo.items():
        print(f'- {chave}: {valor}')
    if len(df):
        print('\nAmostra de recomendações:')
        cols = ['data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'estrategia_recomendada', 'lote_recomendado', 'lote_reserva', 'necessidade_switching', 'produto_destino_switching', 'ganho_liquido_estimado_switching', 'cobertura_esperada']
        print(df[cols].head(15).to_string(index=False))


if __name__ == '__main__':
    main()
