# Conclusão da migração das amostras de pagamentos para saída observável — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T12:43:55
- Escopo:
  - `nucleo/saida_observavel.py`
  - `aplicacao/console/principal.py`
  - `AGENTS.md`, se existente

## Problema corrigido

A auditoria Codex-ready ainda apontava que o console não usava amostras observáveis centralizadas e ainda dependia operacionalmente de `aplicacao/console/secoes_financeiras.py`.

## Correção aplicada

- Contrato de amostras em `nucleo/saida_observavel.py` criado/alterado: True
- Console principal alterado: True
- Import legado removido: True
- Import observável adicionado: True
- Renderizador local adicionado: True
- Chamada antiga substituída: True
- `AGENTS.md` ajustado: True

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- regra de pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline V225;
- planilha operacional.

## Validação necessária

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/principal.py aplicacao/console/secoes_financeiras.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
python aplicacao/principal.py
python preparar_codex_ready_v225.py
```

Critérios esperados em `CODEX_READY_V225.md`:

```text
Console usa amostras observáveis centralizadas: SIM
secoes_financeiras.py sem uso operacional na rota oficial: SIM
Estado mínimo Codex-ready: SIM
```
