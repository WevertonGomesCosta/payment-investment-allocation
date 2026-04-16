# Validação local V42

## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

## Resultado reproduzido com o cache atual do repositório
Na execução local com a série CDI atualmente salva no repositório, a linha do `Lote 6630,64 fev.` na seção `Situação atual — lotes ativos` ficou em:

- Valor original: `R$ 6.630,64`
- Dias corridos: `71`
- Dias úteis: `47`
- Bruto: `R$ 2.852,48`
- Líquido: `R$ 2.833,92`
- Saldo rem.: `R$ 2.770,00`

## Resultado validado para o cenário da divergência reportada
A correção também foi validada contra o cenário em que a série CDI já contém `2026-04-15`, reproduzindo o padrão reportado pelo usuário (`48 dias úteis`, `R$ 2.854,13 / R$ 2.835,21`) antes da correção.

Após a V42, nesse mesmo cenário, a linha passa para:

- Dias corridos: `71`
- Dias úteis: `47`
- Bruto: `R$ 2.852,53`
- Líquido: `R$ 2.833,98`
- Saldo rem.: `R$ 2.770,06`

## Interpretação
A divergência vinha da extrapolação indevida de mais um dia econômico na seção `Situação atual` quando o cache já alcançava o fechamento útil imediatamente anterior à data corrente.
