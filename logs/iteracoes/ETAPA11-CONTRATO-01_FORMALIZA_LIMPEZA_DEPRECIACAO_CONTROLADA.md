# ETAPA11-CONTRATO-01 — Formaliza Limpeza e Depreciação Controlada

## 1. Objetivo

Formalizar documentalmente a Etapa 11 como `Limpeza e Depreciação Controlada`, em aderência ao contrato operacional mestre, que define a etapa posterior à validação de paridade da renderização como limpeza/depreciação controlada com retorno à Etapa 1.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `8a0c7fabd62138bdba4387968dc21874a9dfb8dc`
- Marco incorporado: `FECHAMENTO-ETAPA10-01`
- Branch da frente: `etapa11-contrato-01`

## 3. Auditoria normativa realizada

A frente foi iniciada após auditoria do contrato operacional mestre, modelo matemático-estatístico-financeiro oficial, README dos contratos individuais e contrato da Etapa 10.

A auditoria confirmou:

- a Etapa 11 já existe no contrato macro;
- a função macro da Etapa 11 é `limpeza e depreciação controlada, com retorno à etapa 1`;
- a Etapa 11 não deve ser redefinida como governança de lacunas de decisão futura;
- a saída formal da Etapa 10, `ResultadoParidadeRenderizacaoOficial`, deve ser a entrada formal da Etapa 11;
- a Etapa 11 não deve consumir `PacoteSaidaObservavelOficial` como entrada formal paralela;
- a Etapa 11 não deve reabrir motor, ledger, gates, Etapa 9 ou Etapa 10.

## 4. Arquivos alterados

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA11_LIMPEZA_DEPRECIACAO_CONTROLADA.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/ETAPA11-CONTRATO-01_FORMALIZA_LIMPEZA_DEPRECIACAO_CONTROLADA.md
```

## 5. Contrato criado

O contrato individual da Etapa 11 define:

- entrada formal obrigatória e exclusiva: `ResultadoParidadeRenderizacaoOficial`;
- saída formal prevista: `ResultadoLimpezaDepreciacaoControlada`;
- módulo funcional previsto: `nucleo/limpeza_depreciacao_controlada.py`;
- função pública prevista: `construir_resultado_limpeza_depreciacao_controlada(...)`;
- escopo: classificar rotas legadas, resíduos de renderização, formatos substituídos, artefatos depreciáveis e retorno controlado à Etapa 1.

## 6. Refinamento pré-PR

Após auditoria do contrato e do fluxograma, a função pública prevista foi refinada de:

```text
executar_limpeza_depreciacao_controlada(...)
```

para:

```text
construir_resultado_limpeza_depreciacao_controlada(...)
```

Motivo: evitar interpretação indevida de que a Etapa 11 executa remoção efetiva de arquivos, funções ou rotas.

A Etapa 11 classifica e recomenda limpeza/depreciação controlada, mas não remove automaticamente arquivos, funções, rotas, logs, saídas ou artefatos. Qualquer remoção efetiva deve ocorrer somente em frente posterior específica, com escopo próprio e validação própria.

## 7. Fronteira preservada

A Etapa 11 foi formalizada sem alterar:

```text
código funcional
runtime
contrato operacional mestre
modelo matemático-estatístico-financeiro oficial
contratos das Etapas 1–10
motor temporal
ledger temporal
gates de validação
Etapa 9
Etapa 10
dados financeiros
cache BCB
console
XLSX
lógica econômica
```

## 8. Decisão operacional

```text
ETAPA11-CONTRATO-01 formaliza a Etapa 11 como Limpeza e Depreciação Controlada, não como governança de lacunas de decisão futura.
```

Pendências de próximos pagamentos sem fonte decidida não são a função contratual da Etapa 11. Elas devem ser tratadas em auditoria específica ou correção upstream, sem contaminar o contrato da Etapa 11.

## 9. Validação esperada

Antes de abrir PR, validar:

```bash
git status --short
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
```

O diff esperado deve ficar restrito aos três arquivos desta frente documental.

## 10. Próxima frente recomendada

Após merge da Etapa 11 contratual:

```text
ETAPA11-FUNCIONAL-01 — Implementa ResultadoLimpezaDepreciacaoControlada e construir_resultado_limpeza_depreciacao_controlada(...), consumindo exclusivamente ResultadoParidadeRenderizacaoOficial, sem alterar motor, ledger, gates, Etapa 9, Etapa 10, contrato, modelo, dados, cache ou lógica econômica.
```
