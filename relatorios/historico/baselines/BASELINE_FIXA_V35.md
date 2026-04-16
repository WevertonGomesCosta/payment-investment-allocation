# BASELINE FIXA V35

Derivada da V34 para aplicar uma correção cirúrgica apenas na transição de taxa bônus para taxa base dos lotes aportados com `Dias_Bonus > 0`, sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.

## Ajuste desta derivação

- a regra de `get_taxa_dia()` deixou de cortar a taxa bônus imediatamente quando `data_base_fiscal + dias_bonus` cai em fim de semana/feriado bancário;
- a nova convenção preserva a taxa bônus no **primeiro dia útil de rendimento** imediatamente posterior ao fim da janela corrida, apenas quando a virada ocorre em dia sem rendimento;
- a regra geral dos lotes sem bônus e dos lotes cuja virada já ocorre em dia útil foi mantida.

## Causa raiz encontrada

A V34 tratava a virada `taxa_bonus_cdi -> taxa_base_cdi` apenas por `idade < dias_bonus`, em dias corridos puros.

No `Lote 5400 fev.`, isso fazia a taxa bônus morrer cedo demais:

- data base fiscal: `2026-02-05`
- `Dias_Bonus`: `30`
- data de corte corrida: `2026-03-07`
- `2026-03-07` caiu em sábado
- o primeiro dia útil de rendimento posterior foi `2026-03-09`

Sem a extensão operacional até `2026-03-09`, o lote chegava subcapitalizado ao resgate de `2026-03-20`.

## Resultado consolidado desta correção

### Revalidação do `Lote 5400 fev.`

#### Evento 1 — `2026-03-13` — `Escola`
- modelo V35: bruto `R$ 810,20`, imposto `R$ 3,00`, líquido `R$ 807,20`
- leitura: segue na faixa de arredondamento operacional informada para o app

#### Evento 2 — `2026-03-16` — `Internet`
- modelo V35: bruto `R$ 132,91`, imposto `R$ 0,51`, líquido `R$ 132,40`
- leitura: segue na faixa de arredondamento operacional informada para o app

#### Evento 3 — `2026-03-20` — `Cartão Azul`
- app: bruto `R$ 4.560,29`, imposto `R$ 19,74`, líquido `R$ 4.540,55`
- modelo V34: bruto `R$ 4.559,42`, imposto `R$ 19,58`, líquido `R$ 4.539,84`
- modelo V35: bruto `R$ 4.560,20`, imposto `R$ 19,74`, líquido `R$ 4.540,46`
- delta V35 vs. app: bruto `-R$ 0,09`, imposto `R$ 0,00`, líquido `-R$ 0,09`

Leitura: o erro estrutural principal do evento 3 foi removido. Restou apenas resíduo centesimal pequeno.

### Impacto na auditoria residual

#### Resolvidos por limiar (`<= R$ 0,20`)
- `2026-03-20` | conta `Cartão Azul` | lote `Lote 5400 fev.` | referência `despesa_auto_00037` | resíduo `R$ 0,09`
- `Lote 2063,11 fev.` | resíduo `R$ 0,04`

#### Pendentes para validação (`> R$ 0,20`)
- `2026-03-13` | conta `Escola` | lote `Lote 10342 fev.` | referência `despesa_auto_00014` | resíduo `R$ 0,52`
- `2026-03-13` | conta `Escola` | lote `Lote 4124,75 fev.` | resíduo `R$ 0,52`
- `2026-03-13` | conta `Aluguel` | lote `Lote 4000 fev.` | resíduo `R$ 0,49`

## Implicação operacional desta etapa

A frente do `Lote 5400 fev.` deixou de apontar insuficiência líquida material e passou a ficar dentro do limiar operacional aprovado.
