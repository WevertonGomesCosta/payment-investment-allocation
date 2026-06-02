# ETAPA10-RUNTIME-01 — Integra paridade da renderização ao runtime

## 1. Objetivo

Integrar a Etapa 10 ao fluxo operacional principal, chamando `validar_paridade_renderizacao_oficial(...)` após a geração do XLSX operacional e emitindo no console um resumo observável de `ResultadoParidadeRenderizacaoOficial`.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `77be9c3b019738bae09f154b0d4c232d73780e58`
- Marco incorporado: `ETAPA10-FUNCIONAL-01` mergeada pelo PR #469
- Branch da frente: `etapa10-runtime-01`

## 3. Arquivos alterados

```text
aplicacao/principal.py
logs/iteracoes/ETAPA10-RUNTIME-01_INTEGRA_PARIDADE_RENDERIZACAO_RUNTIME.md
```

## 4. Escopo implementado

- Importa `validar_paridade_renderizacao_oficial` em `aplicacao/principal.py`.
- Após `gerar_planilha_operacional(...)`, chama a validação da Etapa 10 usando:
  - `pacote_saida_observavel_oficial` como referência formal de verdade;
  - `caminho_saida` como XLSX renderizado alvo da auditoria.
- Adiciona `_render_resultado_paridade_renderizacao(...)` para imprimir seção curta no console:
  - artefato;
  - entrada formal;
  - status;
  - ok;
  - auditoria XLSX;
  - auditoria console;
  - quantidade de divergências;
  - divergências materiais;
  - ressalvas;
  - primeiras divergências/ressalvas, quando existirem.

## 5. Fronteira preservada

A integração preserva a fronteira contratual:

- Etapa 9 continua produzindo `PacoteSaidaObservavelOficial`.
- Etapa 10 apenas audita a renderização após o XLSX existir.
- O XLSX e o console permanecem artefatos renderizados alvo, não fontes decisórias.
- `PacoteSaidaObservavelOficial` permanece referência de verdade para a paridade.

## 6. Ausência de alteração econômica

Não houve alteração em:

```text
motor temporal
ledger temporal
gates de validação
Etapa 9
contratos
modelo matemático-estatístico-financeiro oficial
dados financeiros
cache BCB
regras de ranking
regras de switching
liquidez
rendimento
regras fiscais
patrimônio líquido terminal
```

## 7. Validação esperada

Executar localmente:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
git status --short
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
```

Critérios esperados:

- `py_compile` sem erro;
- execução do runtime sem erro;
- console imprime a seção `PARIDADE DA RENDERIZAÇÃO OFICIAL — ETAPA 10` após `Saída operacional gerada em: ...`;
- `ResultadoParidadeRenderizacaoOficial` retorna status observável;
- diff restrito a `aplicacao/principal.py` e este log;
- sem alteração em dados, cache, saída gerada ou lógica econômica.

## 8. Próxima frente recomendada

Após validação e merge desta frente:

```text
POS-ETAPA10-VALIDACAO-RUNTIME-01 — Auditar saída real do console e XLSX após integração runtime da Etapa 10, classificando eventual divergência como paridade, serialização, normalização, colisão de nomes de abas ou lacuna upstream.
```
