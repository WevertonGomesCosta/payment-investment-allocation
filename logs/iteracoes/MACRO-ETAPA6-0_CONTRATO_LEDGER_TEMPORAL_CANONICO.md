# MACRO-ETAPA6-0 — Contrato individual da Etapa 6

## 1. Identificação

- MACROETAPA: MACRO-ETAPA6-0
- VERSÃO CANDIDATA: Etapa 6 — abertura documental
- BASELINE DE ENTRADA: `5a8033c`
- TIPO: DOCUMENTAL / CONTRATUAL
- CLASSE: CONTRATO_INDIVIDUAL_ETAPA6_LEDGER_TEMPORAL_CANONICO
- BRANCH: `docs/macro-etapa6-0-contrato-ledger-temporal-canonico`
- ALTERA CÓDIGO FUNCIONAL: NÃO
- ALTERA MOTOR: NÃO
- ALTERA LEDGER FUNCIONAL: NÃO
- ALTERA DADOS: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- CRIA SCRIPT DIAGNÓSTICO: NÃO

## 2. Objetivo

Criar o contrato individual da **Etapa 6 — Ledger Temporal Canônico**, sem implementar código funcional.

A macroetapa formaliza que a Etapa 6 deve consumir exclusivamente `ResultadoMotorTemporalConjunto` e produzir `LedgerTemporalCanonico` como materialização contábil-canônica, temporal, sequencial, rastreável e auditável das decisões já fechadas pela Etapa 5.

## 3. Baseline confirmada

Baseline informada e confirmada antes da edição:

```text
git branch --show-current
main

git fetch origin

git status --short
<limpo>

git rev-parse HEAD
5a8033cafa3f676f700f20064d4e14048fcc2779

git rev-parse origin/main
5a8033cafa3f676f700f20064d4e14048fcc2779

git log --oneline -5
5a8033c (HEAD -> main, origin/main, origin/HEAD) Merge pull request #419 from WevertonGomesCosta/me-etapa5-doc-final-atualiza-contrato-final
29464c0 ME-ETAPA5-DOC-FINAL: atualiza contrato final da etapa 5
14da2ca Merge pull request #418 from WevertonGomesCosta/codex/implementar-macro-etapa5-c-para-aplicacao-de-trajetoria-cyvsl5
32458f0 MACRO-ETAPA5-D: promove bloqueios internos para auditoria final
671bd40 Merge branch 'main' into codex/implementar-macro-etapa5-c-para-aplicacao-de-trajetoria-cyvsl5
```

A branch documental foi criada a partir de `5a8033cafa3f676f700f20064d4e14048fcc2779`.

## 4. Escopo permitido

Arquivos permitidos nesta macroetapa:

- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `logs/iteracoes/MACRO-ETAPA6-0_CONTRATO_LEDGER_TEMPORAL_CANONICO.md`

## 5. Arquivos alterados

Arquivos criados:

- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `logs/iteracoes/MACRO-ETAPA6-0_CONTRATO_LEDGER_TEMPORAL_CANONICO.md`

Nenhum arquivo funcional foi alterado.

## 6. Conteúdo contratual formalizado

O contrato individual da Etapa 6 define:

- nome da etapa: Etapa 6 — Ledger Temporal Canônico;
- entrada exclusiva: `ResultadoMotorTemporalConjunto`;
- saída exclusiva: `LedgerTemporalCanonico`;
- blocos de `ResultadoMotorTemporalConjunto` que podem ser consumidos;
- definição conceitual do ledger;
- limites negativos da Etapa 6;
- tratamento de `pronto_para_etapa6=True`;
- tratamento de `pronto_para_etapa6=False`;
- representação de obrigações cobertas;
- representação de obrigações bloqueadas;
- representação de reservas de fontes;
- representação de uso referencial de fontes;
- representação de switchings escolhidos;
- relação entre ledger, saída canônica, console e XLSX;
- auditoria interna esperada;
- critérios de aceite da Etapa 6;
- fluxograma Mermaid da Etapa 6.

## 7. Proibições respeitadas

Esta macroetapa não realizou:

- alteração de `aplicacao/*`;
- alteração de `nucleo/*`;
- alteração de `dados/*`;
- alteração de console;
- alteração de XLSX;
- alteração de saída canônica;
- criação de ledger funcional;
- criação de schema funcional;
- criação de função pública do ledger;
- criação de script diagnóstico;
- reintrodução de `ContextoBaseline`;
- reintrodução de `ContextoSaidaCanonicaCompat`;
- criação de fallback legado;
- criação de shadow;
- criação de wrapper transitório;
- criação de rota paralela;
- criação de sentinela.

## 8. Validações executadas antes da edição

Validações fornecidas antes da edição documental:

```text
git diff --name-only origin/main...HEAD
<sem diferenças>

python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
<sem erro>

python -B aplicacao/principal.py
<execução concluída; baseline V225; planilha carregada; relatório operacional gerado>

git status --short
<limpo>
```

## 9. Validações esperadas após a edição

Após a criação dos dois arquivos documentais, a validação esperada é:

```text
git diff --name-only origin/main...HEAD
logs/iteracoes/MACRO-ETAPA6-0_CONTRATO_LEDGER_TEMPORAL_CANONICO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md

python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
<deve permanecer sem erro, pois não houve alteração funcional>

python -B aplicacao/principal.py
<deve preservar o runtime principal, pois não houve alteração funcional>

git status --short
<limpo após commit>
```

## 10. Decisão operacional

A MACRO-ETAPA6-0 fica definida como abertura documental pura da Etapa 6.

A Etapa 6 agora possui contrato individual próprio antes de qualquer implementação funcional.

A próxima macroetapa autorizável, após revisão e aprovação desta entrega, é:

```text
MACRO-ETAPA6-A — Schema canônico do LedgerTemporalCanonico
```

## 11. Condição de parada preservada

Não iniciar implementação funcional da Etapa 6 enquanto o contrato individual criado nesta macroetapa não for revisado e aprovado.

Qualquer necessidade de alterar runtime, console, XLSX, saída canônica, dados, scripts diagnósticos ou motor econômico deve ser tratada em macroetapa futura específica, nunca dentro da MACRO-ETAPA6-0.
