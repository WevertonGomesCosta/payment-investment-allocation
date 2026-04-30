# AGENTS.md — payment-investment-allocation

## Objetivo deste arquivo

Este repositório está preparado para uso com agentes de código, incluindo Codex. Este arquivo define a rota oficial, os comandos de validação e as restrições operacionais que devem ser respeitadas em qualquer alteração.

## Baseline vigente

- Baseline operacional: V225
- Entrada oficial: `aplicacao/principal.py`
- Configuração canônica: `dados/config_atualizado.json`
- Saída operacional oficial: `saidas/oficial/relatorio_operacional_v225.xlsx`

## Comando oficial de execução

```bash
python aplicacao/principal.py
```

## Comando mínimo de validação

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
python aplicacao/principal.py
```

Critérios mínimos:

- execução sem erro;
- saída gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável quando a tarefa for apenas estrutural, documental ou de apresentação;
- console e planilha usando o mesmo `contexto_baseline`;
- console e planilha usando a mesma `saida_canonica`.

## Arquitetura operacional obrigatória

A rota oficial deve permanecer:

```text
aplicacao/principal.py
├── carregar_contexto_baseline(...) uma única vez
├── construir_saida_canonica(...) uma única vez
├── render_console(contexto_baseline, saida_canonica)
└── gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

Estado auditado nesta preparação:

- contexto único: SIM
- saída observável única: NÃO
- console sem dependência operacional de `secoes_financeiras.py`: NÃO

## Fontes únicas

### Saída canônica

`nucleo/saida_canonica.py` é a fonte canônica para os objetos estruturados da execução.

### Saída observável

`nucleo/saida_observavel.py` é a fonte única para dados observáveis compartilhados entre console e planilha.

Atualmente, centraliza:

- Situação Atual;
- patrimônio dos lotes;
- amostras operacionais de pagamentos;
- blocos compartilháveis de apresentação.

### Renderizadores

`aplicacao/console/principal.py` deve ser apenas renderizador do console.

`nucleo/gerar_planilha_operacional.py` deve ser apenas renderizador da planilha.

Alterações em dados observáveis compartilhados devem ser feitas primeiro em `nucleo/saida_observavel.py`.

## Restrições fortes

Não alterar sem solicitação explícita:

- motor econômico;
- replay;
- regra de pagamentos;
- switching;
- ranking;
- cache CDI/BCB;
- identidade da baseline V225;
- contratos matemáticos/econômicos;
- estrutura de leitura das abas de entrada.

## Abas de entrada autorizadas

A execução deve ler somente as abas operacionais definidas no contrato do projeto, especialmente:

- `Carteira`;
- `Todos os Gastos`;
- `Inventário de Lotes`.

Qualquer estrutura derivada deve ser criada internamente pelo script.

## Arquivos legados

Não reativar diretamente arquivos ou funções legadas de apresentação. Se uma informação antiga precisar voltar ao console ou à planilha, migrar primeiro o contrato de dados para `nucleo/saida_observavel.py`.

Arquivos legados preservados nesta etapa:

- `aplicacao/console/secoes_financeiras.py`;
- `aplicacao/console/secoes_canonicas.py`.

## Relatórios

Toda microetapa estrutural deve registrar relatório em:

```text
relatorios/atuais/
```

Para preparação Codex-ready, usar:

```text
relatorios/atuais/codex_ready/
```

## Proibições operacionais para agentes

- Não criar nova rota principal paralela.
- Não fazer console e planilha recalcularem os mesmos dados por funções diferentes.
- Não reabrir validações antigas já encerradas sem evidência concreta.
- Não remover arquivos legados sem microetapa específica e validação local.
- Não alterar `dados/config_atualizado.json` sem necessidade contratual explícita.
- Não adicionar dependências novas sem justificar e validar.
- Não versionar `__pycache__`, `.pyc`, logs temporários ou artefatos locais não oficiais.

## Antes de propor commit

Rodar:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
python aplicacao/principal.py
git status
```

Registrar no relatório da microetapa:

- escopo;
- arquivos alterados;
- validação executada;
- confirmação de ausência de alteração econômica observável, quando aplicável.
