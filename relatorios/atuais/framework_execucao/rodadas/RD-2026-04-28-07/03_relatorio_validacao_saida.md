# 03_relatorio_validacao_saida.md — RD-2026-04-28-07

## Validação executada
Comando obrigatório executado:

```bash
python aplicacao/principal.py > relatorios/atuais/framework_execucao/rodadas/RD-2026-04-28-07/evidencias/console_rd07.txt 2>&1
```

## Resultado observado
- A execução falhou antes da renderização da seção `SITUAÇÃO ATUAL` por dependência ausente (`ModuleNotFoundError: No module named 'scipy'`).
- Portanto, neste ambiente, não foi possível observar no `console_rd07.txt` os campos de metadados para checar ausência de `None` após a microcorreção.

## Validação estática da correção
- O mapeamento entre rótulos humanos e chaves técnicas foi aplicado no ponto de montagem de `resumo_fechamento_situacao_atual` em `aplicacao/console/principal.py`.
- Não houve alterações em motor, pagamentos, switching, função objetivo, dados oficiais, cache BCB/CDI e `requirements.txt`.

## Campos alvo da correção
- data de referência
- status do fechamento econômico
- fonte do fechamento
- último fator explícito CDI
- data confirmada da série
