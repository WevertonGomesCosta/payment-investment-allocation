# payment-investment-allocation

Motor financeiro em Python para alocação auditável de pagamentos, recebidos, lotes de investimento e switching, com foco em patrimônio líquido terminal e rastreabilidade por lote/fonte.

## Estado operacional atual

- **Baseline funcional estável:** `BASELINE_FUNCIONAL_ESTAVEL_V225`
- **Baseline funcional de origem da frente atual:** V208
- **Contrato mestre vigente:** V183
- **Modelo metodológico vinculante:** V182
- **Entrada operacional principal:** `aplicacao/principal.py`
- **Configuração canônica:** `dados/config_atualizado.json`
- **Base financeira canônica:** `dados/dados_financeiros.xlsx`

A V225 formaliza a promoção controlada da V224 sem alterar motor nem regra econômica. Ela consolida a frente V216–V224: aportes planejados em modo diagnóstico, gate econômico ativo, cálculo de dias/idade fiscal centralizados, validação de release limpa e cenário final validado como `sem_aportes_planejados`.

## Objetivo final do projeto

Construir um motor conjunto, diário, auditável e economicamente coerente para:

- pagamentos;
- recebidos;
- aportes planejados;
- switching;
- atualização e valoração de lotes;
- geração de saídas operacionais legíveis.

A decisão deve maximizar o **patrimônio líquido terminal líquido**, respeitando pagamento integral no vencimento, disponibilidade temporal, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## Leitura prioritária para Codex e agentes

Antes de modificar código, consultar nesta ordem:

1. `AGENTS.md`
2. `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
3. `relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md`
4. `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
5. `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
6. `relatorios/INDICE_RELATORIOS.md`

Consultar `relatorios/historico/**`, `logs/iteracoes/**`, relatórios de limpeza e auditorias antigas somente quando houver necessidade explícita de rastreabilidade.

## Instalação

```bash
python -m pip install -r requirements.txt
```

Dependências principais declaradas em `requirements.txt`: `pandas`, `numpy`, `openpyxl`, `python-dateutil`, `requests`, `pulp`, `workalendar` e `scipy`.

## Execução operacional

```bash
python aplicacao/principal.py
```

Esse é o comando principal para execução e validação mínima padrão.

## Entradas autorizadas

A execução deve ler somente as abas abaixo do arquivo financeiro canônico:

- `Carteira`
- `Todos os Gastos`
- `Inventário de Lotes`

Qualquer estrutura derivada deve ser criada internamente pelo código.

## Restrições para novas alterações

Não alterar sem solicitação explícita:

- motor econômico;
- replay passado;
- regra de pagamentos;
- switching;
- ranking da Carteira;
- cache CDI/BCB;
- identidade da baseline V225;
- contratos matemáticos/econômicos;
- `dados/config_atualizado.json`;
- `dados/dados_financeiros.xlsx`.

## Saídas e arquivos gerados

Arquivos gerados localmente devem permanecer fora do versionamento, salvo artefatos documentais explicitamente aprovados. A política principal de exclusão está em `.gitignore`.

Evitar versionar:

- `__pycache__/`;
- `.pyc`;
- logs temporários;
- planilhas geradas fora da base canônica;
- arquivos compactados;
- saídas operacionais locais.

## Validação antes de propor mudança

Quando a alteração afetar execução, console, planilha, dados, cache, pagamentos, rendimento, switching ou ranking:

```bash
python aplicacao/principal.py
```

Quando a alteração for apenas documental, registrar explicitamente que não houve alteração de motor nem regra econômica.

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

