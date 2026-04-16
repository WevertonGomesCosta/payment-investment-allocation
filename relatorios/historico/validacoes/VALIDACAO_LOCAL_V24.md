# Validação local V24

Esta validação foi executada no ambiente disponível antes da entrega da V24.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado

- ambos retornaram `0`;
- o replay controlado do passado passou a materializar lotes históricos `Investimento='-'`;
- aliases históricos auditáveis foram resolvidos;
- a cobertura de contas históricas passou a 59/59.
