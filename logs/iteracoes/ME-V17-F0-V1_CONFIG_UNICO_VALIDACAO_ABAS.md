# ME-V17-F0-V1 — Config único e validação mínima das cinco abas

## 1. Identificação

- MICROETAPA: ME-V17-F0-V1
- VERSAO_CANDIDATA: V17-F0-V.1
- TIPO: CÓDIGO / CONFIGURAÇÃO / DOCUMENTAL
- CLASSE: CORRIGE_ETAPA_1_CONFIG_UNICO_VALIDACAO_MINIMA
- STATUS: CONCLUÍDA
- BRANCH: main
- ALTERA_CODIGO: sim
- ALTERA_CONFIG: sim
- ALTERA_MOTOR: não
- ALTERA_MODELO_OFICIAL: não
- ALTERA_RUNNER_FINAL: não
- ALTERA_LEITOR_PLANILHA: não
- ALTERA_REGRA_ECONOMICA: não
- ALTERA_RENDERIZACAO: não

---

## 2. Objetivo

Corrigir a interpretação operacional da Etapa 1 — Entrada bruta e configuração — consolidando `dados/config_atualizado.json` como config operacional único e expandindo a validação mínima para as cinco abas operacionais do projeto.

---

## 3. Decisões implementadas

### 3.1. `aplicacao/principal.py`

`aplicacao/principal.py` não foi alterado.

Ele passa a ser tratado conceitualmente como runner final do pipeline completo, e não como componente interno da Etapa 1.

### 3.2. Config operacional único

O config operacional automático passa a ser apenas:

- `dados/config_atualizado.json`

A etapa remove dependência automática de:

- `config.json`;
- `dados/config_canonizacao_v17_a1.json` como overlay operacional.

As definições necessárias de `salarios` e `switching` foram promovidas para `dados/config_atualizado.json`.

### 3.3. Validação mínima

`validar_config_nucleo(...)` passa a validar também:

- `abas/salarios`;
- `abas/switching`;
- `colunas/salarios`;
- `colunas/switching`.

A validação de dicionários de colunas passa a incluir:

- `carteira`;
- `lotes`;
- `despesas`;
- `salarios`;
- `switching`.

---

## 4. Arquivos alterados

- `dados/config_atualizado.json`
- `nucleo/carregador_config.py`
- `logs/iteracoes/ME-V17-F0-V1_CONFIG_UNICO_VALIDACAO_ABAS.md`

---

## 5. Arquivos explicitamente não alterados

- `aplicacao/principal.py`
- `nucleo/leitor_planilha.py`
- contrato operacional
- modelo matemático oficial
- README
- motor temporal
- ranking
- saída canônica
- console
- XLSX
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

---

## 6. Validações esperadas

- `python -m py_compile nucleo/carregador_config.py`
- `python -B aplicacao/principal.py`
- `git diff --check`
- `git status --short`

A execução principal deve continuar reconhecendo as cinco abas operacionais:

- `Carteira`
- `Salários`
- `Todos os Gastos`
- `Switching`
- `Inventário de Lotes`

---

## 7. Próxima etapa

Após validação e commit, iniciar a auditoria individual da Etapa 2 — Validação pré-execução — sem alterar ainda a canonização profunda da Etapa 3.
