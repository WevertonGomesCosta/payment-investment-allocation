# VALIDACAO LOTE 5400 FEV - V35

## Hipótese aplicada

Quando `data_base_fiscal + dias_bonus` cair em dia sem rendimento bancário, a taxa bônus deve permanecer válida no primeiro dia útil de rendimento subsequente.

## Traço do replay após a correção

| Data | Conta | Despesa ID | Valor da conta | Saldo antes | Bruto | Imposto | Líquido | Saldo remanescente |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-03-13 | Escola | despesa_auto_00035 | 807,20 | 5.490,39 | 810,20 | 3,00 | 807,20 | 4.680,19 |
| 2026-03-16 | Internet | despesa_auto_00036 | 132,40 | 4.682,85 | 132,91 | 0,51 | 132,40 | 4.549,94 |
| 2026-03-20 | Cartão Azul | despesa_auto_00037 | 4.540,55 | 4.560,20 | 4.560,20 | 19,74 | 4.540,46 | 0,00 |

## Comparação explícita do evento 3 contra o app

| Métrica | App | Modelo V34 | Modelo V35 | Delta V35 vs. app |
|---|---:|---:|---:|---:|
| Bruto | 4.560,29 | 4.559,42 | 4.560,20 | -0,09 |
| Imposto | 19,74 | 19,58 | 19,74 | 0,00 |
| Líquido | 4.540,55 | 4.539,84 | 4.540,46 | -0,09 |

## Conclusão

A correção cirúrgica removeu o erro estrutural principal do evento 3 do `Lote 5400 fev.`. O desvio remanescente caiu para `R$ 0,09`, abaixo do limiar operacional aprovado.
