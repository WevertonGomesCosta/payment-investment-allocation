# VALIDAÇÃO LOCAL V36

## Ambiente e execução

Base usada na validação:
- repositório derivado da V35;
- nova planilha substituindo `dados/dados_financeiros.xlsx`;
- cache CDI mantido em `dados/cache_bcb.json`;
- data de referência da execução: `2026-04-15`.

## Comandos executados

```bash
python -m compileall aplicacao nucleo
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado

- execução local concluída com sucesso;
- leitura da nova planilha estabilizada após o tratamento de `NaT`;
- auditoria crítica dos lotes vs. app permaneceu estável para os lotes de referência em `15/04/2026`;
- reauditoria residual reduziu os casos pendentes acima do limiar para dois itens novos ligados ao `Lote 5680 abr.`, fora do bloco atual dos lotes criticamente auditados.

## Deltas críticos vs. app em 15/04/2026

- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
- `Lote 8500 mar.`: bruto `-0,08`, líquido `-0,06`

## Situação do bloco auditado nesta etapa

- `Lote 5400 fev.`: `R$ 0,09`, resolvido por limiar;
- `Lote 10342 fev.`: dentro do limiar após nova planilha + correção do IOF;
- `Lote 4000 fev.`: dentro do limiar;
- `Lote 4124,75 fev.`: `R$ 0,12`, resolvido por limiar.
