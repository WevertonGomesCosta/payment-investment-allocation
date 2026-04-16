# BASELINE FIXA V37

## Escopo desta derivação

Esta derivação consolida quatro ajustes operacionais sobre a baseline V36:

1. leitura da nova coluna `Data Recebimento` na aba `Inventário de Lotes`;
2. separação entre **data de recebimento** e **data de aplicação** para o replay histórico;
3. retorno da **data de referência dinâmica** para a data atual da execução;
4. limpeza da saída do console, priorizando apenas auditorias ainda ativas.

## Regra operacional nova

Quando um lote possui `Data Recebimento < Data Aplicação`:

- o lote fica **disponível para pagamentos** a partir de `Data Recebimento`;
- até `Data Aplicação` inclusive, ele é tratado como **caixa pré-aplicação**, sem rendimento e sem tributação de investimento;
- o rendimento do produto começa apenas **após** a data de aplicação;
- a carência do produto passa a bloquear resgates apenas **depois** da data de aplicação.

## Caso motivador

### `Lote 5680 abr.`
- recebimento: `2026-04-06`
- aplicação: `2026-04-14`
- produto: `CDB Neon Planejado 150% CDI - 60 dias`

Na V36, o lote ficava indisponível antes da aplicação e gerava inconsistências materiais em `2026-04-08` e `2026-04-10`.

Na V37, o lote passa a ser usado corretamente como caixa pré-aplicação nas despesas históricas antes da aplicação.

## Resultado consolidado da V37

- `Lote 5680 abr.` deixa de gerar resíduos pendentes acima do limiar;
- a reauditoria residual volta a ficar sem pendências materiais;
- a data de referência volta a seguir a data atual da execução, com fallback controlado do CDI quando necessário;
- a auditoria ativa do console fica concentrada no bloco `RECEBIMENTO VS APLICAÇÃO`.

## Arquivos e limpeza operacional

Foram removidos do pacote final os artefatos temporários de validação em `.txt` mantidos na raiz do repositório em versões anteriores (`run_*`, `inspect_*` e equivalentes), preservando apenas os relatórios oficiais em `relatorios/`.
