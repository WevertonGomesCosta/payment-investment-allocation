# VALIDACAO LOCAL V34

Validação local executada com sucesso na derivação V34.

## Comandos executados

- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`

## Evidências principais

- a criação de lotes passou a preservar `taxa_base_cdi = 0.0` quando essa taxa é explicitamente informada;
- os lotes históricos `nao_aportado_exaurido` deixaram de render indevidamente no replay;
- a auditoria residual foi revalidada após a correção, sem alterar os deltas críticos contra os apps.

## Resultado da reauditoria residual

### Casos removidos pela correção estrutural
- `Lote 3600 abr.`
- `Lote 7800 abr.`

### Resíduo resolvido por limiar
- `Lote 2063,11 fev.` → `R$ 0,04`

### Resíduos pendentes para validação
- `despesa_auto_00037` → `R$ 0,71`
- `despesa_auto_00014` → `R$ 0,68`
- `Lote 4000 fev.` → `R$ 0,49`
- `Lote 4124,75 fev.` → `R$ 0,38`

## Deltas críticos vs. app em 15/04/2026

- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
- `Lote 8500 mar.`: bruto `-0,08`, líquido `-0,06`

## Observação metodológica

Nesta derivação, a remoção dos resíduos de `Lote 3600 abr.` e `Lote 7800 abr.` ocorreu por correção causal da modelagem histórica dos lotes `nao_aportado_exaurido`, e não por limiar de materialidade.
