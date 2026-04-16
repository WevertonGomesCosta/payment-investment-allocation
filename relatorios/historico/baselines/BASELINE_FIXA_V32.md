# BASELINE FIXA V32

Derivada da V31 para aprofundar a auditoria dos resíduos de saque/arredondamento sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.

## Ajustes desta derivação

- fixação explícita de `execucao.data_referencia_simulacao = 2026-04-15` em `dados/config_atualizado.json` para manter a auditoria alinhada às referências dos apps;
- ampliação da auditoria no console com uma nova seção de rastreamento causal dos resíduos no nível do evento histórico;
- manutenção da convenção temporal já corrigida na V31.

## Resultado consolidado da auditoria dos resíduos

### Contas parcialmente cobertas

- `despesa_auto_00014` (`Escola`, 2026-03-13): faltam `R$ 0,68` porque o `Lote 10342 fev.` foi totalmente zerado no evento e o líquido máximo disponível do lote na data foi `R$ 1.367,44`;
- `despesa_auto_00037` (`Cartão Azul`, 2026-03-20): faltam `R$ 0,71` porque o `Lote 5400 fev.` foi totalmente zerado no evento e o líquido máximo disponível do lote na data foi `R$ 4.539,84`.

Leitura: esses dois casos não indicam mais problema de convenção temporal. O déficit aparece no próprio evento histórico de saque e é compatível com teto líquido do lote no esgotamento.

### Micro-saldos remanescentes

#### Remanescente por rendimento histórico
- `Lote 3600 abr.` → `R$ 3,19`
- `Lote 7800 abr.` → `R$ 0,09`

Leitura: ambos são lotes históricos marcados como `nao_aportado_exaurido` que ainda acumularam rendimento até o último uso. O resíduo não nasce do fechamento temporal global.

#### Saldo residual após saque líquido-alvo
- `Lote 4000 fev.` → `R$ 0,49`
- `Lote 4124,75 fev.` → `R$ 0,38`

Leitura: os saques cobriram exatamente as contas históricas informadas, mas preservaram pequeno saldo bruto remanescente no lote.

#### Micro-saldo centesimal compatível com arredondamento
- `Lote 2063,11 fev.` → `R$ 0,04`

Leitura: caso limpo de micro-resíduo compatível com conversão líquido→bruto e arredondamento monetário.

## Implicação operacional desta etapa

A auditoria dos resíduos indica três naturezas distintas:

1. teto líquido do lote no esgotamento;
2. remanescente por rendimento histórico em lotes `-`/não aportados historicamente consumidos;
3. micro-saldo compatível com arredondamento ou com preservação de saldo residual após saque líquido-alvo.

Com isso, o próximo passo já pode discutir materialidade/zeramento com bem mais precisão, sem tratar todos os resíduos como se tivessem a mesma causa.
