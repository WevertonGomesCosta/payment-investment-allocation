# AGENTS.md — payment-investment-allocation

## Objetivo

Este repositório está preparado para uso com agentes de código, incluindo Codex. Este arquivo define a rota oficial, os comandos de validação e as restrições operacionais que devem ser respeitadas.

## Baseline vigente

- Baseline operacional: V225
- Entrada oficial: `aplicacao/principal.py`
- Configuração canônica: `dados/config_atualizado.json`
- Saída operacional oficial: `saidas/oficial/relatorio_operacional_v225.xlsx`

## Comando oficial de execução

```bash
python aplicacao/principal.py
```

## Comando oficial de validação operacional

```bash
python aplicacao/principal.py
```

A validação oficial deve ser feita diretamente pela entrada principal. Não recriar pasta `scripts/` nem comandos paralelos de validação.

## Arquitetura operacional obrigatória

```text
aplicacao/principal.py
├── carregar_contexto_baseline(...) uma única vez
├── construir_saida_canonica(...) uma única vez
├── render_console(contexto_baseline, saida_canonica)
└── gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

Estado auditado:

- contexto único: SIM
- saída observável única: SIM
- console sem dependência operacional de `secoes_financeiras.py`: SIM
- console sem dependência operacional de `secoes_canonicas.py`: SIM
- arquivos legados de console removidos: SIM

## Fontes únicas

- `nucleo/saida_canonica.py`: saída canônica estruturada.
- `nucleo/saida_observavel.py`: fonte única para dados observáveis compartilhados entre console e planilha.
- `aplicacao/console/principal.py`: renderizador do console.
- `nucleo/gerar_planilha_operacional.py`: renderizador da planilha.

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
- estrutura de leitura das abas de entrada;
- `dados/config_atualizado.json`.

## Abas de entrada autorizadas

A execução deve ler somente:

- `Carteira`;
- `Todos os Gastos`;
- `Inventário de Lotes`.

Qualquer estrutura derivada deve ser criada internamente pelo script.

## Arquivos legados de console

Os módulos antigos `aplicacao/console/secoes_financeiras.py` e `aplicacao/console/secoes_canonicas.py` foram removidos do repositório para evitar reuso acidental.

Não recriar renderizadores paralelos. Se alguma saída antiga precisar voltar ao console ou à planilha, migrar primeiro o contrato de dados para `nucleo/saida_observavel.py`.

## Proibições operacionais para agentes

- Não criar nova rota principal paralela.
- Não fazer console e planilha recalcularem os mesmos dados por funções diferentes.
- Não reabrir validações antigas já encerradas sem evidência concreta.
- Não recriar arquivos legados de apresentação removidos.
- Não alterar `dados/config_atualizado.json` sem necessidade contratual explícita.
- Não versionar `__pycache__`, `.pyc`, logs temporários ou artefatos locais não oficiais.

## Antes de propor commit

```bash
python aplicacao/principal.py
git status
```
