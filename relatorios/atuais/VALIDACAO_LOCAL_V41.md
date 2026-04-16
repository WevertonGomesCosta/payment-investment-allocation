# Validação local V41

## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

## Resultado auditado
Na reexecução local da V41, o lote `Lote 6630,64 fev.` foi reproduzido com os seguintes valores na seção `Situação atual — lotes ativos`:

- Recebimento: `2026-02-04`
- Aplicação: `2026-02-04`
- Produto: `CDB Turbinado`
- Valor original: `R$ 6.630,64`
- Dias corridos: `71`
- Dias úteis: `47`
- Bruto: `R$ 2.852,48`
- Líquido: `R$ 2.833,92`
- Saldo rem.: `R$ 2.770,00`

## Observação
A discrepância maior (`R$ 2.854,13` / `R$ 2.835,21`) não foi reproduzida na V40 entregue. Ainda assim, a V41 força a tabela e a planilha a usarem o mesmo caminho explícito de cálculo para evitar divergências futuras entre exibição e estado interno do lote.
