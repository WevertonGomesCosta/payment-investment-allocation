# VALIDAÇÃO LOCAL V37

## Ambiente
- data de referência da execução: `2026-04-16`
- cache CDI: último fator disponível em `2026-04-15`
- fechamento da referência em `2026-04-16`: fallback controlado para o último fator disponível

## Comandos executados

```bash
python -m compileall aplicacao nucleo
python scripts/inspecionar_base.py
python aplicacao/principal.py
```

## Resultados principais

### Replay controlado do passado
- contas históricas: `62`
- cobertas integralmente: `61`
- parcialmente cobertas: `1`
- não cobertas: `0`
- inconsistência remanescente: apenas `despesa_auto_00037` (`Lote 5400 fev.`) com `R$ 0,09`, já dentro do limiar

### Reauditoria dos resíduos
- limiar operacional: `R$ 0,20`
- resíduos pendentes acima do limiar: `0`
- bloco residual: encerrado nesta execução

### Auditoria ativa — recebimento vs aplicação
Para `Lote 5680 abr.`:
- `2026-04-08` — `Pelada e churrasco` — usado como `caixa_pre_aplicacao` — bruto/líquido `R$ 70,00`
- `2026-04-10` — `Concerto Carro` — usado como `caixa_pre_aplicacao` — bruto/líquido `R$ 434,75`
- `2026-04-14` — `Escola`, `Escola`, `Calça biola`, `Velt` — ainda tratado como `caixa_pre_aplicacao` no dia da aplicação — sem rendimento e sem tributação

### Auditoria comparativa dos lotes críticos vs app
As referências históricas dos apps permaneceram calculadas em `15/04/2026` para manter comparabilidade com a base observada já consolidada.

## Conclusão
A V37 estabiliza a distinção entre recebimento e aplicação sem reabrir solver, switching econômico, score final ou engine completa.
