# Auditoria cirúrgica do bloco 2026-05-13 a 2026-05-20 — V131

## Objetivo

Verificar se o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` é realmente superior em patrimônio líquido terminal ou se continua vencendo apenas pela prioridade excessiva dada a déficit/cobertura na métrica lexicográfica central.

## Base auditada

- Baseline de execução: **V130**
- Fonte: `grade_diaria_parametrizada_v130_consolidado.json`
- Janela auditada: **2026-05-13** a **2026-05-20**
- Cenários auditados: **24** (3 por dia)

## Resposta objetiva

**Não.** Neste bloco, o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` **não é superior em patrimônio líquido terminal** ao baseline.

Ele continua vencendo na métrica central porque:

1. mantém **o mesmo nível** de `violacoes_protegida`;
2. mantém **o mesmo nível** de `pagamentos_sem_cobertura_integral`;
3. reduz materialmente o `deficit_liquido_total`;

mas, ao mesmo tempo:

4. **piora** a `perda_patrimonio_liquido_terminal` em todos os dias;
5. **piora** o `patrimonio_liquido_terminal_proxy` em todos os dias;
6. aumenta `destruicao_estrategica_lotes` e `custo_fiscal_imediato`.

Portanto, a vitória observada no bloco é **lexicográfica**, não **terminal**.

## Vencedor lexicográfico por dia

| Data       | Vencedor lexicográfico                    | Destino                 |   Δ déficit vs baseline |   Δ perda terminal vs baseline |   Δ patrimônio proxy vs baseline |
|:-----------|:------------------------------------------|:------------------------|------------------------:|-------------------------------:|---------------------------------:|
| 2026-05-13 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3658.54 |                        2353.4  |                         -2353.4  |
| 2026-05-14 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3658.54 |                        2353.4  |                         -2353.4  |
| 2026-05-15 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3658.54 |                        2353.4  |                         -2353.4  |
| 2026-05-16 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3923.34 |                        2531.69 |                         -2531.69 |
| 2026-05-17 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3923.34 |                        2531.69 |                         -2531.69 |
| 2026-05-18 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3923.34 |                        2531.69 |                         -2531.69 |
| 2026-05-19 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3923.34 |                        2531.69 |                         -2531.69 |
| 2026-05-20 | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m |                -3923.34 |                        2531.69 |                         -2531.69 |

## Comparação direta: baseline vs PicPay 3m

| Data       |   Déficit baseline |   Perda terminal baseline |   Déficit PicPay 3m |   Perda terminal PicPay 3m |   Δ déficit PicPay 3m |   Δ perda terminal PicPay 3m |   Δ patrimônio proxy PicPay 3m |
|:-----------|-------------------:|--------------------------:|--------------------:|---------------------------:|----------------------:|-----------------------------:|-------------------------------:|
| 2026-05-13 |             150145 |                   6166.21 |              146486 |                    8519.61 |              -3658.54 |                      2353.4  |                       -2353.4  |
| 2026-05-14 |             150145 |                   6166.21 |              146486 |                    8519.61 |              -3658.54 |                      2353.4  |                       -2353.4  |
| 2026-05-15 |             150145 |                   6166.21 |              146486 |                    8519.61 |              -3658.54 |                      2353.4  |                       -2353.4  |
| 2026-05-16 |             150277 |                   6083.77 |              146354 |                    8615.46 |              -3923.34 |                      2531.69 |                       -2531.69 |
| 2026-05-17 |             150277 |                   6083.77 |              146354 |                    8615.46 |              -3923.34 |                      2531.69 |                       -2531.69 |
| 2026-05-18 |             150277 |                   6083.77 |              146354 |                    8615.46 |              -3923.34 |                      2531.69 |                       -2531.69 |
| 2026-05-19 |             150277 |                   6083.77 |              146354 |                    8615.46 |              -3923.34 |                      2531.69 |                       -2531.69 |
| 2026-05-20 |             150277 |                   6083.77 |              146354 |                    8615.46 |              -3923.34 |                      2531.69 |                       -2531.69 |

Leitura:
- o ganho do PicPay 3m vem todo do **déficit**: melhora entre **R$ -3923.34** e **R$ -3658.54** contra o baseline;
- mas ele piora a perda terminal entre **R$ 2353.40** e **R$ 2531.69**;
- e piora o patrimônio proxy exatamente na mesma ordem de grandeza, entre **R$ -2531.69** e **R$ -2353.40**.

Em outras palavras: o cenário vence porque o déficit aparece **antes** do patrimônio terminal na ordem de decisão.

## Comparação entre os três destinos do bloco

| Data       |   Mercado - PicPay 3m em perda terminal |   Mercado - PicPay 3m em destruição estratégica | PicPay 3m = PicPay 6m   |
|:-----------|----------------------------------------:|------------------------------------------------:|:------------------------|
| 2026-05-13 |                                  108.73 |                                          159.71 | True                    |
| 2026-05-14 |                                  108.82 |                                          159.71 | True                    |
| 2026-05-15 |                                  108.91 |                                          159.71 | True                    |
| 2026-05-16 |                                  108.94 |                                          159.7  | True                    |
| 2026-05-17 |                                  109.03 |                                          159.7  | True                    |
| 2026-05-18 |                                  109.12 |                                          159.7  | True                    |
| 2026-05-19 |                                  109.21 |                                          159.7  | True                    |
| 2026-05-20 |                                  109.3  |                                          159.7  | True                    |

Leitura:
- `Combo PicPay 100-120 3m` e `Combo PicPay 100-120 6m` ficam **idênticos** em todos os dias deste bloco sob o modelo atual;
- `Mercado Pago 120% CDI` nunca vence neste bloco porque, com o mesmo déficit e a mesma cobertura, ele entrega:
  - perda terminal **~R$ 108.73 a R$ 109.30 pior** que o PicPay 3m;
  - destruição estratégica **~R$ 159.70 a R$ 159.71 pior**.

Então, **dentro do conjunto de switchings testados**, o PicPay 3m/6m é o melhor.  
Mas **contra o baseline**, ele continua perdendo no objetivo terminal.

## Conclusão metodológica

Este bloco mostra uma tensão real entre:

- o objetivo operacional de curto prazo:
  - reduzir déficit;
  - preservar cobertura;
- e o objetivo final do projeto:
  - **maximizar patrimônio líquido terminal**.

Sob a métrica central atual, o cenário do `Lote 8500 mar.` para `Combo PicPay 100-120 3m` vence porque o componente `deficit_liquido_total` entra antes de `perda_patrimonio_liquido_terminal`.

Se o projeto exigir uma regra adicional do tipo:

- “não aceitar switching que piore patrimônio terminal contra o baseline”,

então **nenhum cenário deste bloco sobreviveria**.

## Decisão recomendada

- **Não promover** ainda `Lote 8500 mar. -> Combo PicPay 100-120 3m` como regra operacional final.
- Tratar este bloco como:
  - **vencedor operacional de déficit/cobertura**,
  - mas **não vencedor terminal**.
- A próxima micro-etapa correta é recalibrar o comparador central para distinguir explicitamente:
  - vencedor operacional;
  - vencedor terminal;
  - e vencedor híbrido aceitável.

## Resultado sintetizado

- `Combo PicPay 100-120 3m` vence a métrica lexicográfica do bloco.
- `Combo PicPay 100-120 6m` empata com ele no modelo atual.
- `Mercado Pago 120% CDI` é dominado por pior terminal e pior destruição estratégica, com o mesmo déficit.
- **O baseline continua superior em patrimônio líquido terminal** em todos os dias de `2026-05-13` a `2026-05-20`.
