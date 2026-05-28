# MACRO-ETAPA7-0 — Contrato individual da Etapa 7

## 1. Identificação

- MACROETAPA: MACRO-ETAPA7-0
- VERSÃO CANDIDATA: Etapa 7 — abertura documental
- BASELINE DE ENTRADA: `ecda2bdf79ea57fe977627b0ead69f5902573ed5`
- TIPO: DOCUMENTAL / CONTRATUAL
- CLASSE: CONTRATO_INDIVIDUAL_ETAPA7_GATES_VALIDACAO_NUCLEO
- BRANCH: `docs/macro-etapa7-0-contrato-gates-validacao-nucleo`
- ALTERA CÓDIGO FUNCIONAL: NÃO
- ALTERA MOTOR: NÃO
- ALTERA LEDGER FUNCIONAL: NÃO
- ALTERA DADOS: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- CRIA SCRIPT DIAGNÓSTICO: NÃO

## 2. Objetivo

Criar o contrato individual da **Etapa 7 — Gates de Validação de Núcleo**, sem implementar código funcional.

A macroetapa formaliza que a Etapa 7 deve consumir `LedgerTemporalCanonico`, estado temporal final e decisões finais já materializadas, quando formalmente disponíveis, para validar conservação de valor, pagamento integral, fonte materializada antes do uso, liquidez/carência, saldos/residuais, bloqueios, dupla contagem e consistência entre pagamentos e fontes.

## 3. Baseline confirmada

Baseline de entrada:

```text
main remota / merge da PR #421
ecda2bdf79ea57fe977627b0ead69f5902573ed5
```

A baseline contém a Etapa 6 funcionalmente integrada, com `LedgerTemporalCanonico` construído no runtime após `ResultadoMotorTemporalConjunto`.

A validação local pós-merge fornecida confirmou:

```text
HEAD == origin/main == ecda2bdf79ea57fe977627b0ead69f5902573ed5
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
git status --short
<limpo>
```

## 4. Escopo permitido

Arquivos permitidos nesta macroetapa:

- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `logs/iteracoes/MACRO-ETAPA7-0_CONTRATO_GATES_VALIDACAO_NUCLEO.md`

## 5. Arquivos alterados

Arquivos criados:

- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `logs/iteracoes/MACRO-ETAPA7-0_CONTRATO_GATES_VALIDACAO_NUCLEO.md`

Nenhum arquivo funcional foi alterado.

## 6. Conteúdo contratual formalizado

O contrato individual da Etapa 7 define:

- nome da etapa: Etapa 7 — Gates de Validação de Núcleo;
- entrada principal: `LedgerTemporalCanonico`;
- entradas auxiliares permitidas: estado temporal final, decisões finais, ranking oficial e auditorias compatíveis, apenas quando formalmente disponíveis no pipeline vivo;
- saída formal: `ResultadoGatesValidacaoNucleo`;
- gates mínimos obrigatórios;
- validação de conservação de valor;
- validação de pagamento integral e data correta;
- validação de fonte materializada antes do uso;
- validação de liquidez e carência;
- validação de saldos, consumo, imposto, líquido e residual;
- validação de dupla contagem;
- validação de switching materializado;
- validação de bloqueios e pendências;
- relação com Etapa 8 — Saída Canônica Validada;
- relação com Etapa 9 — Renderização Oficial Unificada;
- proibições da Etapa 7;
- estruturas funcionais previstas para macroetapa posterior;
- função pública prevista para macroetapa posterior;
- critérios de aceite da Etapa 7;
- fluxograma Mermaid da Etapa 7.

## 7. Proibições respeitadas

Esta macroetapa não realizou:

- alteração de `aplicacao/*`;
- alteração de `nucleo/*`;
- alteração de `dados/*`;
- alteração de console;
- alteração de XLSX;
- alteração de saída canônica;
- criação de gates funcionais;
- criação de schema funcional;
- criação de função pública de validação;
- criação de script diagnóstico;
- reintrodução de `ContextoBaseline`;
- reintrodução de `ContextoSaidaCanonicaCompat`;
- criação de fallback legado;
- criação de shadow;
- criação de wrapper transitório;
- criação de rota paralela;
- criação de sentinela.

## 8. Validações esperadas

Por se tratar de macroetapa documental pura, a validação esperada é:

```text
git diff --name-only origin/main...HEAD
logs/iteracoes/MACRO-ETAPA7-0_CONTRATO_GATES_VALIDACAO_NUCLEO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md

python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
<deve permanecer sem erro, pois não houve alteração funcional>

python -B aplicacao/principal.py
<deve preservar o runtime principal, pois não houve alteração funcional>

git status --short
<limpo após commit>
```

## 9. Decisão operacional

A MACRO-ETAPA7-0 fica definida como abertura documental pura da Etapa 7.

A Etapa 7 agora possui contrato individual próprio antes de qualquer implementação funcional.

A próxima macroetapa autorizável, após revisão e aprovação desta entrega, é:

```text
MACRO-ETAPA7-FULL — Implementa Gates de Validação de Núcleo
```

## 10. Condição de parada preservada

Não iniciar implementação funcional da Etapa 7 enquanto o contrato individual criado nesta macroetapa não for revisado e aprovado.

Qualquer necessidade de alterar runtime, console, XLSX, saída canônica, dados, scripts diagnósticos ou motor econômico deve ser tratada em macroetapa futura específica, nunca dentro da MACRO-ETAPA7-0.
