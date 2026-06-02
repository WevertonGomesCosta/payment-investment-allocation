# ETAPA10-CONTRATO-01 — Formaliza Paridade da Renderização Oficial

## 1. Objetivo

Criar a frente documental da Etapa 10 do projeto `payment-investment-allocation`, formalizando a camada posterior à Etapa 9 responsável por validar paridade entre `PacoteSaidaObservavelOficial` e suas renderizações físicas/observáveis, especialmente console e XLSX.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `d16d972f9c55f422d23f387e01c0f3c9bbe25513`
- Marco incorporado: `ATUALIZACAO-DADOS-FINANCEIROS-01`
- Branch da frente: `etapa10-contrato-01`

## 3. Escopo executado

Arquivos criados ou alterados:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA10_PARIDADE_RENDERIZACAO_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/ETAPA10-CONTRATO-01_FORMALIZA_PARIDADE_RENDERIZACAO_OFICIAL.md
```

## 4. Síntese normativa

A Etapa 10 recebe como entrada formal obrigatória e exclusiva:

```text
PacoteSaidaObservavelOficial
```

A Etapa 10 produz como saída formal prevista:

```text
ResultadoParidadeRenderizacaoOficial
```

Console e XLSX são artefatos renderizados alvo de auditoria de paridade. Eles não são fontes decisórias, não corrigem decisão econômica e não substituem o pacote observável oficial.

## 5. Fronteira Etapa 9 -> Etapa 10

- Etapa 9 transforma `SaidaCanonicaOficial` em `PacoteSaidaObservavelOficial`.
- Etapa 10 valida se as renderizações físicas/observáveis preservam o pacote produzido pela Etapa 9.
- Etapa 10 não reabre Etapa 9.
- Divergências devem ser classificadas como renderização, serialização, normalização, ergonomia, lacuna ou divergência material.

## 6. Restrições preservadas

- Não altera `aplicacao/*`.
- Não altera `nucleo/*`.
- Não altera `dados/*`.
- Não altera `saidas/*`.
- Não altera `scripts/diagnostico/*`.
- Não altera contratos individuais das Etapas 1–9.
- Não altera contrato operacional mestre.
- Não altera modelo matemático-estatístico-financeiro oficial.
- Não altera console.
- Não altera XLSX.
- Não implementa `ResultadoParidadeRenderizacaoOficial`.
- Não integra runtime.
- Não executa motor, ledger ou gates.

## 7. Resumo do contrato criado

O contrato da Etapa 10:

- define `PacoteSaidaObservavelOficial` como entrada formal obrigatória e exclusiva;
- define `ResultadoParidadeRenderizacaoOficial` como saída formal prevista;
- posiciona a Etapa 10 depois da Etapa 9;
- trata console/XLSX como artefatos renderizados alvo;
- define classificação de divergências estruturais, headers, linhas, conteúdo, serialização, normalização numérica, data/datetime, ergonomia, lacunas e divergência material;
- inclui mapa funcional previsto em `nucleo/paridade_renderizacao_oficial.py`;
- inclui função pública prevista `validar_paridade_renderizacao_oficial(...)`;
- inclui fluxograma operacional-explicativo completo;
- prepara a futura frente `ETAPA10-FUNCIONAL-01`.

## 8. Validação esperada

A validação documental esperada é:

```bash
git status --short
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
```

O diff deve ficar restrito a:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA10_PARIDADE_RENDERIZACAO_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/ETAPA10-CONTRATO-01_FORMALIZA_PARIDADE_RENDERIZACAO_OFICIAL.md
```

## 9. Decisão operacional

```text
APROVAR a frente documental ETAPA10-CONTRATO-01 para PR, desde que a validação do diff confirme escopo restrito aos três documentos esperados.
```

## 10. Próxima frente recomendada

Após validação e merge desta frente:

```text
ETAPA10-FUNCIONAL-01 — Implementa ResultadoParidadeRenderizacaoOficial e auditor oficial de paridade entre PacoteSaidaObservavelOficial, console e XLSX.
```
