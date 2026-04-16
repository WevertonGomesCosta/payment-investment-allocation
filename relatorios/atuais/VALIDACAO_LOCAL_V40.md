# VALIDAÇÃO LOCAL V40

## Execuções realizadas

```bash
python -m compileall aplicacao nucleo scripts
python aplicacao/principal.py
python scripts/gerar_planilha_operacional.py
```

## Resultado validado

- o console passou a omitir as auditorias já encerradas solicitadas;
- a tabela de inconsistências do replay passou a usar apenas inconsistências materiais acima do limiar;
- os `Top produtos selecionados` ficaram em seção própria;
- o `RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS` foi reposicionado logo após a leitura das abas;
- a tabela final de lotes ativos passou a ser exibida na saída principal;
- a planilha operacional foi gerada com as abas:
  - `Extrato passado`
  - `Extrato futuro`
  - `Melhores produtos`
  - `Situação atual`

## Artefatos gerados

- `saidas/relatorio_operacional_v40.xlsx`
