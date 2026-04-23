# Auditoria do motor diário com normalização pós-vencimento — V146

Janela: **2026-05-03** a **2026-05-06**.

## O que foi implementado

- inclusão de `prazo_dias_atual`, `regime_liquidez_atual` e `data_vencimento` na construção do estado dos lotes;
- normalização diária pós-vencimento no simulador e no motor diário, convertendo lote vencido em caixa líquido disponível segundo `politicas.pos_vencimento`;
- aplicação da normalização antes do planner diário, antes da execução do pacote do dia e dentro do simulador temporal.

## Resumo do motor corrigido

- decisões `pay_only`: **2**
- decisões `switch_then_pay`: **0**
- decisões `switch_only`: **0**
- decisões `no_action`: **2**
- pagamentos no horizonte: **3**
- patrimônio líquido terminal proxy final: **R$ 37.136,83**
- fontes finais de pagamento: **3 pagamentos por `combinacao_minima_fontes`**

## Decisões diárias do motor corrigido

### 2026-05-03
- pacote vencedor: **no_action**
- evento estrutural do dia: ativação de `Lote 7000 mai.`
- normalização pós-vencimento detectada: `Lote 6630,64 fev.` convertido para caixa disponível (**R$ 0,21**)

### 2026-05-04
- pacote vencedor: **pay_only**
- pagamentos do dia: **1** (`despesa_auto_00070`)
- normalização pós-vencimento aplicada antes da decisão do dia:
  - `Lote 3000 mar. V` → caixa disponível (**R$ 3.104,32**)
  - `Lote 3000 mar. B` → caixa disponível (**R$ 3.101,24**)

### 2026-05-05
- pacote vencedor: **no_action**
- sem pagamentos no dia

### 2026-05-06
- pacote vencedor: **pay_only**
- pagamentos do dia: **2** (`despesa_auto_00072`, `despesa_auto_00071`)
- recebidos ativados no dia:
  - `Lote 3600 mai.` (**R$ 3.600,00**)
  - `Lote 5680 mai.` (**R$ 5.680,00**)

## Auditoria forçada `pay_only` vs `switch_then_pay`

### 2026-05-04
- `pay_only`: vetor `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0)` | patrimônio proxy **R$ 37.136,83**
- fontes em `pay_only`: `['combinacao_minima_fontes']`
- switching diário após a correção: **14 ações elegíveis**, **14 cenários gerados**, **0 promovíveis**
- melhor switching bruto do dia: `Lote 7000 mai. + Lote 3000 mar. V + Lote 3000 mar. B -> CDB XP 150%`
- classe do comparador híbrido: **dominado_pelo_baseline**
- `switch_then_pay` forçado: vetor `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0)` | patrimônio proxy **R$ 37.136,83**
- `switch_then_pay` forçado vence `pay_only`? **Não**

### 2026-05-06
- `pay_only`: vetor `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0)` | patrimônio proxy **R$ 38.636,83** no recorte local do dia
- fontes em `pay_only`: `['combinacao_minima_fontes', 'combinacao_minima_fontes']`
- switching diário após a correção: **0 ações elegíveis**, **0 cenários gerados**, **0 promovíveis**

## Conclusão

A correção estrutural foi efetiva: os lotes vencidos passaram a ser tratados como **caixa líquido disponível antes da decisão diária**, eliminando o viés identificado na V145.

Entretanto, na janela **2026-05-03 a 2026-05-06**, essa correção **não foi suficiente para promover `switch_then_pay`**. Mesmo no teste forçado do dia crítico **2026-05-04**, o melhor switching bruto continuou inferior ao baseline e gerou pior vetor operacional do pacote do dia.

Portanto:
- a **semântica pós-vencimento estava errada e foi corrigida**;
- o caso crítico dos lotes `3k mar` **deixou de ficar escondido no estado**;
- mas, **nesta janela curta**, o vencedor econômico continua sendo **`pay_only`**.
