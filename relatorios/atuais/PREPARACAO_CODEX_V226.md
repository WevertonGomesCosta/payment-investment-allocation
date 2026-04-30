# Preparação do repositório para Codex — V226

## Objetivo

Preparar o repositório `payment-investment-allocation` para uso mais eficiente com Codex, reduzindo risco de leitura de contexto defasado e evitando consumo excessivo de tokens por documentos históricos, logs e artefatos auxiliares.

## Escopo da V226

- Atualizar documentação de entrada para apontar corretamente para a baseline V225.
- Adicionar `AGENTS.md` como instrução raiz para Codex/agentes.
- Atualizar índice oficial e índice normativo curto.
- Registrar política de leitura eficiente e exclusões candidatas.
- Não alterar código funcional.
- Não alterar motor econômico.
- Não alterar regra de pagamentos, switching, ranking, cache ou config.

## Arquivos alterados/criados

| Arquivo | Ação | Motivo |
|---|---|---|
| `AGENTS.md` | criado | Instrução raiz para Codex: rota de leitura, restrições, validação e higiene de contexto. |
| `README.md` | atualizado | Remover foco excessivo em V216 e registrar V225 como baseline funcional estável. |
| `relatorios/atuais/LEIA-ME_OPERACIONAL.md` | atualizado | Substituir guia V208 por guia operacional V225. |
| `relatorios/atuais/INDICE_DOCUMENTOS_NORMATIVOS_VIGENTES.md` | atualizado | Corrigir hierarquia prática e caminhos principais. |
| `relatorios/INDICE_RELATORIOS.md` | atualizado | Reorganizar navegação para V225 e uso com Codex. |
| `relatorios/atuais/PREPARACAO_CODEX_V226.md` | criado | Registrar decisão auditável desta etapa. |

## Diagnóstico documental

Antes da V226, os pontos de entrada ainda tinham divergências relevantes:

- `README.md` declarava V225 no cabeçalho, mas o corpo continuava centrado em V216–V224 e comandos de diagnóstico antigos.
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md` ainda estava marcado como V208.
- Índices ainda apontavam documentos normativos como se estivessem em `relatorios/atuais/`, embora os arquivos principais vigentes estejam em `relatorios/principais/`.
- Não havia uma instrução raiz estável para Codex após a remoção anterior de `AGENTS.md`.

## Decisão sobre exclusões nesta etapa

Nenhuma exclusão física foi aplicada na V226.

Motivo: o repositório já passou por limpezas recentes e contém histórico/documentação útil para rastreabilidade. A redução de tokens deve ser feita primeiro por orientação explícita de leitura, não por remoção adicional sem auditoria específica.

## Diretórios/arquivos que Codex deve evitar por padrão

Evitar abrir em massa, salvo necessidade explícita:

```text
relatorios/historico/**
relatorios/atuais/limpeza_*/**
relatorios/atuais/auditoria_estrutura_repositorio/**
relatorios/atuais/codex_ready/*.csv
logs/iteracoes/**
saidas/**
*.csv
*.xlsx
*.zip
*.tar
*.gz
```

## Diretórios/arquivos que devem permanecer acessíveis

Manter disponíveis:

```text
README.md
AGENTS.md
requirements.txt
aplicacao/**
nucleo/**
config/**
dados/config_atualizado.json
dados/cache_bcb.json
dados/dados_financeiros.xlsx
relatorios/atuais/LEIA-ME_OPERACIONAL.md
relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md
relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md
relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md
relatorios/INDICE_RELATORIOS.md
```

## Política recomendada para futuras exclusões

Antes de remover arquivos/pastas, executar auditoria específica classificando cada item como:

1. funcional ativo;
2. normativo vigente;
3. evidência de validação vigente;
4. histórico útil;
5. artefato redundante consolidado;
6. temporário/gerado/local.

Somente itens nas classes 5 e 6 devem ser candidatos diretos à remoção, e mesmo assim com relatório de decisão.

## Validação esperada

Como a V226 é documental, a validação principal é revisão de diffs e consistência dos caminhos.

Validação funcional recomendada, se houver ambiente local completo:

```bash
python aplicacao/principal.py
```

## Status

```text
status: DOCUMENTAL_CODEX_READY
altera_codigo: false
altera_motor: false
altera_regra_economica: false
altera_dados: false
altera_config: false
baseline_preservada: V225
```
