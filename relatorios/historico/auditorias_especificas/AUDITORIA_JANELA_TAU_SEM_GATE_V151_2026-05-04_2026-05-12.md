# Auditoria da janela 2026-05-04 a 2026-05-12 sem pré-gate

Baseline operacional: V150.

## Contrato auditado

- tau = **10,0**
- sem depender de `_melhor_plano_switching_diario_v143`
- em cada dia, o pacote base foi comparado apenas contra o **melhor switching bruto do dia**

## Resumo comparativo contra a V150 (gate + tau)

- Switching promovidos sem gate: **1**
- Dias com vencedor alterado vs V150: **1**
- Patrimônio final V150 (gate + tau): **R$ 25,993.97**
- Patrimônio final sem gate: **R$ 26,036.28**
- Delta agregado vs V150: **R$ 42.31**
- switch_then_pay V150: **0**
- switch_only V150: **0**
- switch_then_pay sem gate: **1**
- switch_only sem gate: **0**

## Decisões por dia

### 2026-05-04
- Pagamentos do dia: **1**
- IDs: despesa_auto_00070
- Lotes normalizados: Lote 6630,64 fev., Lote 3000 mar. V, Lote 3000 mar. B
- Pacote base: **pay_only** | patrimônio **R$ 25,993.97** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0)
- Melhor switching bruto: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.0)
- Vencedor sem gate: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **True** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-05
- Pagamentos do dia: **0**
- Pacote base: **no_action** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0)
- Melhor switching bruto: **switch_only** | rotulo `Lote 3000 mar. B -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,041.06** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0)
- Vencedor sem gate: **no_action** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **no_action** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-06
- Pagamentos do dia: **2**
- IDs: despesa_auto_00072, despesa_auto_00071
- Recebidos ativados: Lote 3600 mai., Lote 5680 mai.
- Pacote base: **pay_only** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0)
- Melhor switching bruto: **switch_then_pay** | rotulo `Lote 3600 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,045.48** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0)
- Vencedor sem gate: **pay_only** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-07
- Pagamentos do dia: **0**
- Pacote base: **no_action** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0)
- Melhor switching bruto: **switch_only** | rotulo `Lote 5680 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,045.94** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.0)
- Vencedor sem gate: **no_action** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **no_action** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-08
- Pagamentos do dia: **1**
- IDs: despesa_auto_00073
- Pacote base: **pay_only** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0)
- Melhor switching bruto: **switch_then_pay** | rotulo `Lote 5680 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,044.00** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.0)
- Vencedor sem gate: **pay_only** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-09
- Pagamentos do dia: **0**
- Pacote base: **no_action** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0)
- Melhor switching bruto: **switch_only** | rotulo `Lote 5680 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,041.92** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0)
- Vencedor sem gate: **no_action** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **no_action** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-10
- Pagamentos do dia: **1**
- IDs: despesa_auto_00074
- Pacote base: **pay_only** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0)
- Melhor switching bruto: **switch_then_pay** | rotulo `Lote 5680 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,040.04** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0)
- Vencedor sem gate: **pay_only** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-11
- Pagamentos do dia: **1**
- IDs: despesa_auto_00075
- Pacote base: **pay_only** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0)
- Melhor switching bruto: **switch_then_pay** | rotulo `Lote 5680 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | patrimônio **R$ 26,038.13** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0)
- Vencedor sem gate: **pay_only** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**

### 2026-05-12
- Pagamentos do dia: **3**
- IDs: despesa_auto_00078, despesa_auto_00077, despesa_auto_00076
- Pacote base: **pay_only** | patrimônio **R$ 26,036.28** | vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0)
- Melhor switching bruto: nenhum cenário bruto disponível.
- Vencedor sem gate: **pay_only** | rotulo `None` | patrimônio **R$ 26,036.28**
- Comparação com V150: vencedor V150 = **pay_only** | mudou = **False** | delta patrimônio vs V150 = **R$ 42.31**
