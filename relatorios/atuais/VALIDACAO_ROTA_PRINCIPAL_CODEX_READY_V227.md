# VALIDAÇÃO ROTA PRINCIPAL CODEX READY — V227

Data: 2026-04-30

## Objetivo

Registrar validação funcional mínima, executável e auxiliar para confirmar que a rota oficial `python aplicacao/principal.py` permanece íntegra após a preparação Codex-ready V226 documental.

## Escopo da microalteração

- Inclusão de script de diagnóstico curto em `scripts/diagnostico/validar_rota_principal_codex_ready_v227.py`.
- Verificações de existência de caminhos canônicos e leitura básica da configuração principal.
- Verificação de compilação e importabilidade estrutural de `aplicacao/principal.py`.
- Sem duplicação de lógica de negócio e sem criação de rota operacional paralela.

## Comandos executados

```bash
python scripts/diagnostico/validar_rota_principal_codex_ready_v227.py
python aplicacao/principal.py
```

## Resultado esperado

- Console com status `OK/ERRO` por item validado.
- Execução principal mantida em `python aplicacao/principal.py`.

## Declaração de preservação da baseline

- Não houve alteração de motor econômico.
- Não houve alteração de regra econômica.
- Não houve alteração de switching, ranking ou replay.
- Não houve alteração em `dados/config_atualizado.json`, `dados/dados_financeiros.xlsx` ou cache BCB.
- Baseline funcional preservada: V225.
