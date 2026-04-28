# 01_revisao_proximas_alocacoes.md — RD-2026-04-28-08

## Objetivo
Formalizar revisão objetiva das próximas alocações de pagamentos recomendadas na aba **Extrato Futuro**, usando o pacote local já gerado para RD-08.

## Escopo das evidências utilizadas
- `evidencias/01_inventario_planilha_rd08.txt`
- `evidencias/02_proximas_alocacoes_pagamentos.csv`
- `evidencias/03_alertas_proximas_alocacoes.csv`
- `evidencias/04_resumo_rd08.txt`
- `evidencias_rd08_proximas_alocacoes_corrigidas.zip`

## Resultado consolidado
- Total de pagamentos extraídos: **30**
- Período: **2026-04-29 a 2026-07-08**
- Valor total: **R$ 30.803,29**
- Cobertura integral: **30/30**
- Sem switching real: **17**
- Com switching real: **13**
- Alertas totais: **13** (todos do tipo “Pagamento envolve switching real”)
- Cobertura parcial: **0**
- Lote sugerido vazio: **0**
- Saldo remanescente negativo: **0**

## Regras observadas
- `sem_switching` não foi tratado como switching real.
- Não há evidência de cobertura parcial indevida no recorte.

## Pontos de atenção
- `Lote 3600 mai.` fica quase exaurido, com saldo mínimo **R$ 18,05**.
- `Lote 3000 mar. B` fica com saldo mínimo **R$ 47,63**.
