# MACRO-ETAPA7-0A — Ajuste de exclusividade de entrada da Etapa 7

## 1. Identificação

- MACROETAPA: MACRO-ETAPA7-0A
- TIPO: DOCUMENTAL / CONTRATUAL
- CLASSE: AJUSTE_EXCLUSIVIDADE_ENTRADA_ETAPA7
- BASELINE DE ENTRADA: `0fcf3543531941a2137f15892da1585c223718c5`
- BRANCH: `docs/macro-etapa7-0a-exclusividade-ledger`
- ALTERA CÓDIGO FUNCIONAL: NÃO
- ALTERA MOTOR: NÃO
- ALTERA LEDGER FUNCIONAL: NÃO
- ALTERA DADOS: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- CRIA SCRIPT DIAGNÓSTICO: NÃO

## 2. Objetivo

Ajustar documentalmente o contrato individual da **Etapa 7 — Gates de Validação de Núcleo** para declarar `LedgerTemporalCanonico` como entrada formal obrigatória e exclusiva da etapa.

O ajuste remove a ambiguidade de entradas auxiliares paralelas como estado temporal final ou decisões finais independentes.

## 3. Motivação

Após a correção da Etapa 5 congelada em `0fcf3543531941a2137f15892da1585c223718c5`, a sequência contratual viva passa por:

```text
Etapa 5 -> ResultadoMotorTemporalConjunto
Etapa 6 -> LedgerTemporalCanonico
Etapa 7 -> ResultadoGatesValidacaoNucleo
```

Para preservar encadeamento estrito, a Etapa 7 não deve consumir diretamente `ResultadoMotorTemporalConjunto`, `EstadoTemporalInicial` ou objetos anteriores.

Informações sobre estado temporal final, decisões finais, ranking e auditorias só podem ser usadas se estiverem materializadas ou explicitamente referenciadas no próprio `LedgerTemporalCanonico`.

## 4. Arquivos alterados

- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `logs/iteracoes/MACRO-ETAPA7-0A_EXCLUSIVIDADE_LEDGER.md`

## 5. Alterações documentais aplicadas

O contrato da Etapa 7 foi ajustado para explicitar que:

- `LedgerTemporalCanonico` é entrada formal obrigatória e exclusiva;
- informações sobre estado temporal final, decisões econômicas finais, ranking oficial utilizado e auditorias compatíveis não são entradas paralelas;
- tais informações só podem ser usadas quando materializadas ou referenciadas no ledger;
- a Etapa 7 não pode consumir diretamente `ResultadoMotorTemporalConjunto`;
- a Etapa 7 não pode consumir diretamente `EstadoTemporalInicial`;
- a função prevista `validar_gates_nucleo(...)` deve receber apenas `LedgerTemporalCanonico` e parâmetros opcionais;
- o fluxograma da Etapa 7 não contém mais entrada auxiliar paralela.

## 6. Proibições respeitadas

Esta macroetapa não realizou:

- alteração de `aplicacao/*`;
- alteração de `nucleo/*`;
- alteração de `dados/*`;
- alteração de console;
- alteração de XLSX;
- alteração de saída canônica;
- alteração de motor econômico;
- alteração do ledger funcional;
- criação de script diagnóstico;
- criação de fallback legado, shadow, wrapper transitório, rota paralela ou sentinela.

## 7. Validações esperadas

Por ser ajuste documental puro, a validação esperada é:

```text
git diff --name-only origin/main...HEAD
logs/iteracoes/MACRO-ETAPA7-0A_EXCLUSIVIDADE_LEDGER.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md

git status --short
<limpo após commit>
```

`py_compile` e `python -B aplicacao/principal.py` devem permanecer idênticos à baseline, pois não houve alteração funcional.

## 8. Próxima macroetapa autorizável

Após revisão e aprovação deste ajuste documental, a próxima macroetapa autorizável é:

```text
MACRO-ETAPA7-FULL — Implementa Gates de Validação de Núcleo
```

Essa macroetapa funcional deverá consumir exclusivamente `LedgerTemporalCanonico` como entrada de estado.
