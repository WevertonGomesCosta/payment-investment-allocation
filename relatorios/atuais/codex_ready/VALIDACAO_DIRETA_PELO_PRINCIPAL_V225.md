# Validação direta pelo arquivo principal — V225

## Identificação

- Data/hora local: 2026-04-30T14:10:00
- Baseline: V225 Codex-ready enxuta

## Decisão

A pasta `scripts/` foi removida do repositório.

A validação oficial passa a ser feita diretamente por:

```bash
python aplicacao/principal.py
```

## Arquivos documentais atualizados

```text
AGENTS.md
relatorios/atuais/codex_ready/CODEX_READY_V225.md
relatorios/atuais/codex_ready/INVENTARIO_LEGADO_INATIVO_V225.md
relatorios/atuais/codex_ready/AUDITORIA_RESIDUAIS_APLICACAO_NUCLEO_V225.md
relatorios/atuais/codex_ready/REMOCAO_SECOES_TRIAGEM_PRE_CODEX_V225.md
relatorios/atuais/codex_ready/ENXUGAMENTO_FINAL_REPOSITORIO_PRE_CODEX_V225.md
```

## Regra para Codex

Não recriar `scripts/validacao/`.

Qualquer alteração futura deve ser validada executando:

```bash
python aplicacao/principal.py
```

Critério esperado:

- execução sem erro;
- saída oficial gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável quando a tarefa for estrutural/documental.
