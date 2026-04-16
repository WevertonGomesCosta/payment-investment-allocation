# VALIDACAO LOCAL V31

Validação local executada com sucesso na baseline derivada da V30.

## Comandos executados

- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`

## Evidências principais

- fechamento da referência em `2026-04-15` aplicado no núcleo e no replay;
- fallback CDI controlado registrado com `data_valuation=2026-04-15` e `data_fator_utilizado=2026-04-14`;
- replay estendido até a data de referência completa;
- deltas críticos vs. app reduzidos para a faixa aproximada de `R$ 0,01` a `R$ 0,21` no líquido e `R$ 0,02` a `R$ 0,11` no bruto;
- resíduos remanescentes concentrados em:
  - duas contas parcialmente cobertas de `R$ 0,68` e `R$ 0,71`;
  - micro-saldos pós-replay de `R$ 3,19`, `R$ 0,49`, `R$ 0,38`, `R$ 0,09` e `R$ 0,04`.

## Observação do teste de -1 dia

O teste de `-1 dia de rendimento` ficou limpo para `Lote 3000 mar. V`, `Lote 3000 mar. B` e `Lote 8500 mar.`. Para `Lote 6630,64 fev.`, o console marca corretamente que houve saque em `15/04/2026`, então a comparação `ref` vs. `ref-1d` não isola apenas rendimento.
