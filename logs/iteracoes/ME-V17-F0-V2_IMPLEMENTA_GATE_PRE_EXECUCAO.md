# ME-V17-F0-V2 — Implementa gate puro de validação pré-execução

## 1. Identificação

- MICROETAPA: ME-V17-F0-V2
- VERSAO_CANDIDATA: V17-F0-V.2
- TIPO: CÓDIGO / VALIDAÇÃO / ARQUITETURAL
- CLASSE: IMPLEMENTA_GATE_PURO_PRE_EXECUCAO
- STATUS: CONCLUÍDA
- BRANCH: main
- ALTERA_CODIGO: sim
- ALTERA_MOTOR: não
- ALTERA_MODELO_OFICIAL: não
- ALTERA_RUNNER_FINAL: não
- ALTERA_REGRA_ECONOMICA: não
- ALTERA_RENDERIZACAO: não

---

## 2. Objetivo

Implementar a Etapa 2 como gate puro de validação pré-execução, consumindo apenas artefatos já produzidos pela Etapa 1.

---

## 3. Arquivos alterados

- `nucleo/validacao_pre_execucao.py`
- `nucleo/contexto_baseline.py`
- `logs/iteracoes/ME-V17-F0-V2_IMPLEMENTA_GATE_PRE_EXECUCAO.md`

---

## 4. Arquivos explicitamente não alterados

- `aplicacao/principal.py`
- `nucleo/leitor_planilha.py`
- `nucleo/dados_operacionais_canonicos.py`
- motor
- saída canônica
- console
- XLSX
- contrato operacional
- modelo oficial
- README
- dados financeiros

---

## 5. Decisão implementada

Foi criado um módulo dedicado de validação pré-execução:

- `nucleo/validacao_pre_execucao.py`

A função principal é:

- `validar_pre_execucao(...)`

Ela recebe:

- `PacoteConfig`
- `ContextoExecucao`
- `PacotePlanilha`

E retorna:

- `PacoteValidacaoPreExecucao`

---

## 6. Proibições preservadas

O gate não executa:

- download;
- carregamento de planilha;
- abertura de workbook;
- resolução de colunas;
- canonização;
- transformação de dados;
- decisão econômica;
- renderização.

---

## 7. Integração mínima

`nucleo/contexto_baseline.py` passou a chamar `validar_pre_execucao(...)` imediatamente após `carregar_planilha(...)`.

Se o gate reprovar, a execução é bloqueada antes de avançar para:

- carteira canônica;
- dados operacionais canônicos;
- ranking;
- replay;
- motor;
- saída.

---

## 8. Validações esperadas

- `python -m py_compile nucleo/validacao_pre_execucao.py nucleo/contexto_baseline.py`
- `python -B aplicacao/principal.py`
- `git diff --check`
- `git status --short`

---

## 9. Próxima etapa

Após validação, iniciar a auditoria individual da Etapa 3 — Dados operacionais e universo econômico canônico.
