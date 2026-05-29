# MACRO-CONTRATOS-02 — Padroniza contratos individuais das Etapas 1–7

## Identificação

- Tipo: DOCUMENTAL / CONTRATUAL
- Classe: PADRONIZA_ESTRUTURA_DOS_CONTRATOS_INDIVIDUAIS
- Baseline de entrada: `6838288aabffb08ca9a9cf6537545d10730fd395`
- Branch: `docs/macro-contratos-02-padroniza-estrutura-contratos-1-7`
- Alteração funcional: não

## Objetivo

Padronizar os contratos individuais e fluxogramas das Etapas 1–7 em uma mesma estrutura documental de 19 seções, sem alterar conteúdo funcional, runtime, código, dados, console, XLSX ou saída canônica.

## Arquivos documentais alterados

- `relatorios/principais/contratos_individuais/README.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md`
- `logs/iteracoes/MACRO-CONTRATOS-02_PADRONIZA_CONTRATOS_INDIVIDUAIS_ETAPAS_1_7.md`

## Síntese das alterações

- README atualizado para declarar padrão estrutural único dos contratos individuais.
- Etapa 1 reestruturada em 19 seções, preservando `PacoteEntradaResolvida`, módulos/funções e fluxograma técnico original.
- Etapa 2 reestruturada em 19 seções, preservando o papel de gate puro, `PacoteValidacaoPreExecucao` e `validar_pre_execucao(...)`.
- Etapa 3 reestruturada em 19 seções, preservando canonização operacional, artefatos de saída e funções centrais do fluxograma.
- Etapas 4–7 preservadas como padronizadas pela MACRO-CONTRATOS-01, sem reabertura funcional.

## Ausência de alteração funcional

Esta macrofrente não altera `aplicacao/*`, `nucleo/*`, `dados/*`, `saidas/*`, `scripts/diagnostico/*`, console, XLSX, saída canônica, runtime, motor econômico, ledger funcional, gates funcionais, Etapa 8 ou stash antigo de cache BCB.

## Validações recomendadas

```bash
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
git status --short
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
```

`python -B aplicacao/principal.py` não é validação obrigatória desta PR documental.

## Critérios de aceite

A frente é aceitável se o diff ficar restrito aos arquivos documentais permitidos, todos os contratos 1–7 seguirem a estrutura de 19 seções, os fluxogramas permanecerem operacional-explicativos completos e nenhuma alteração funcional for introduzida.
