# Contrato suplementar — pós-vencimento e gate de switching diário (V177)

## Objetivo
Fixar duas invariantes operacionais para evitar regressões na validação diária:

1. lotes normalizados por pós-vencimento devem permanecer auditáveis no próprio dia da conversão e nos dias seguintes;
2. em dias sem pagamento, o melhor cenário diário promovível de switching deve ser executado pelo runner de validação, e não neutralizado por uma comparação posterior de pacote.

## Invariantes obrigatórias

### 1) Pós-vencimento auditável
Quando `_normalizar_lote_pos_vencimento_no_dia(...)` converter um lote aportado em recebido disponível:
- o runner diário deve registrar o item em `lotes_normalizados_pos_vencimento`;
- o lote monitorado deve continuar visível em `lotes_monitorados`;
- `valor_relevante` deve refletir `valor_disponivel` quando `valor_liquido_resgatavel` não existir;
- `origem_pos_vencimento` e `data_vencimento_origem` devem permanecer auditáveis.

### 2) Gate de switching diário promovível
Em dias sem pagamento:
- se existir `melhor_cenario_promovivel` com `promovivel_hibrido=True`,
- e existir pacote `switch_only` correspondente,
- o runner diário deve executar esse pacote como vencedor do dia.

Esse override é restrito aos dias sem pagamento nesta versão. Em dias com pagamento, a comparação entre `pay_only` e `switch_then_pay` permanece ativa.

## Fora de escopo
- expansão do espaço de busca do switching;
- mudança na valoração terminal global;
- mudança em `_calcular_metrica`;
- mudança no executor central.
