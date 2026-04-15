# Validação local V22

Esta validação foi executada antes da entrega da V22.

## Comandos

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais

- baseline carregou corretamente config, planilha e abas primárias;
- a `Carteira` segue como universo único de produtos;
- os metadados derivados permanecem explícitos como ponte transitória;
- a triagem v1 permanece auditável e calibrada de forma conservadora/transitória;
- matching canônico e resumo shadow continuam íntegros.
