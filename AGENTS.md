# AGENTS.md — payment-investment-allocation

## Escopo

Este arquivo orienta agentes de código, incluindo Codex, em todo o repositório.

Objetivo: reduzir leitura desnecessária, evitar reabertura de decisões já estabilizadas e preservar a baseline funcional atual.

## Estado vigente

- Baseline funcional estável: `BASELINE_FUNCIONAL_ESTAVEL_V225`
- Contrato mestre vigente: `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
- Modelo metodológico vinculante: `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- Guia operacional curto: `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- Entrada operacional principal: `aplicacao/principal.py`
- Configuração canônica: `dados/config_atualizado.json`
- Base financeira canônica: `dados/dados_financeiros.xlsx`

## Rota obrigatória de leitura

Antes de modificar código, ler nesta ordem:

1. `README.md`
2. `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
3. `relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md`
4. `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
5. `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`

Consultar histórico, auditorias antigas, relatórios de limpeza ou logs de iteração somente quando a tarefa pedir rastreabilidade específica.

## Instalação e execução

Instalar dependências, se necessário:

```bash
python -m pip install -r requirements.txt
```

Comando operacional principal:

```bash
python aplicacao/principal.py
```

Esse comando também é a validação mínima padrão para alterações que possam afetar execução, console, planilha, leitura de dados, cache, pagamento, rendimento, switching ou ranking.

## Restrições fortes

Não alterar sem pedido explícito:

- motor econômico;
- replay passado;
- regra de pagamentos;
- switching;
- ranking da Carteira;
- cache CDI/BCB;
- identidade da baseline V225;
- contratos matemáticos/econômicos;
- `dados/config_atualizado.json`;
- `dados/dados_financeiros.xlsx`;
- estrutura de leitura das abas de entrada.

## Abas de entrada autorizadas

A execução deve ler somente:

- `Carteira`;
- `Todos os Gastos`;
- `Inventário de Lotes`.

Qualquer estrutura derivada deve ser criada internamente pelo código.

## Diretriz para mudanças

Preferir alterações pequenas, auditáveis e localizadas.

Para cada mudança, registrar claramente:

- arquivo alterado;
- motivo;
- impacto esperado;
- comando de validação executado;
- se houve ou não alteração de regra econômica.

## Higiene de contexto

Evitar abrir em massa, salvo necessidade explícita:

- `relatorios/historico/**`;
- `relatorios/atuais/limpeza_*/**`;
- `relatorios/atuais/auditoria_estrutura_repositorio/**`;
- `relatorios/atuais/codex_ready/*.csv`;
- `logs/iteracoes/**`;
- `saidas/**`;
- arquivos `.csv`, `.xlsx`, `.zip`, `.tar`, `.gz` gerados localmente.

Para entender o estado atual, usar primeiro os documentos vigentes listados na rota obrigatória de leitura.

## Antes de finalizar uma alteração

Executar, quando aplicável:

```bash
python aplicacao/principal.py
git status
```

Se o comando não puder ser executado por falta de dependência, dado privado, permissão ou ambiente, registrar o impedimento de forma explícita no resumo final.

<!-- CODEX_MODO_ENXUTO_INICIO -->
## Regra operacional para Codex — modo enxuto

Por padrão, o Codex não deve executar validações locais, testes, scripts diagnósticos ou `python aplicacao/principal.py`.

A validação será feita pelo usuário no ambiente local.

O Codex deve focar em alterações funcionais mínimas e responder apenas com:

- Summary
- Changed files
- Testing
- Risk
- Next

Na seção Testing, quando não houver pedido explícito para executar comandos, usar:

> Não executado por regra do fluxo; validação local será feita pelo usuário.

Codex não deve criar, alterar ou incluir arquivos em:

- relatorios/
- scripts/diagnostico/
- logs/
- docs/
- prompts/

Também não deve criar CSV, inventário, relatório, auditoria, validação auxiliar ou nova documentação, salvo pedido explícito do usuário.

Se a tarefa for funcional, alterar apenas os arquivos de código estritamente necessários.

O corpo do PR deve ser escrito do zero com base apenas no diff final. Não mencionar arquivos que não foram alterados no PR atual.
<!-- CODEX_MODO_ENXUTO_FIM -->

