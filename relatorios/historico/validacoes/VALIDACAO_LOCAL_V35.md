# VALIDACAO LOCAL V35

Validação local executada com sucesso na derivação V35.

## Comandos executados

- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`

## Evidências principais

- a transição de bônus passou a respeitar o primeiro dia útil de rendimento quando o fim da janela corrida cai em dia sem rendimento bancário;
- o `Lote 5400 fev.` foi reprocessado e seu evento final de `2026-03-20` saiu de um desvio material para um resíduo de `R$ 0,09`;
- o imposto do evento final do `Lote 5400 fev.` passou a bater exatamente com o app: `R$ 19,74`.

## Revalidação do `Lote 5400 fev.`

### Evento 1 — `2026-03-13` — `Escola`
- bruto modelo V35: `R$ 810,20`
- imposto modelo V35: `R$ 3,00`
- líquido modelo V35: `R$ 807,20`

### Evento 2 — `2026-03-16` — `Internet`
- bruto modelo V35: `R$ 132,91`
- imposto modelo V35: `R$ 0,51`
- líquido modelo V35: `R$ 132,40`

### Evento 3 — `2026-03-20` — `Cartão Azul`
- bruto app: `R$ 4.560,29`
- imposto app: `R$ 19,74`
- líquido app: `R$ 4.540,55`
- bruto modelo V35: `R$ 4.560,20`
- imposto modelo V35: `R$ 19,74`
- líquido modelo V35: `R$ 4.540,46`
- delta bruto: `-R$ 0,09`
- delta imposto: `R$ 0,00`
- delta líquido: `-R$ 0,09`

## Deltas críticos vs. app em 15/04/2026

- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
- `Lote 8500 mar.`: bruto `-0,08`, líquido `-0,06`

## Resultado da reauditoria residual

### Resolvidos por limiar
- `despesa_auto_00037` → `R$ 0,09`
- `Lote 2063,11 fev.` → `R$ 0,04`

### Pendentes para validação
- `despesa_auto_00014` → `R$ 0,52`
- `Lote 4124,75 fev.` → `R$ 0,52`
- `Lote 4000 fev.` → `R$ 0,49`
