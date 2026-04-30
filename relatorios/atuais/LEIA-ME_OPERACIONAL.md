# LEIA-ME operacional — V225

## Função deste documento

Este é o guia curto de navegação operacional do repositório `payment-investment-allocation`.

Use este arquivo para orientar leitura inicial, execução mínima e continuidade controlada a partir da baseline funcional estável V225.

## Estado vigente

- Pacote operacional atual: **V225**
- Baseline funcional estável: **BASELINE_FUNCIONAL_ESTAVEL_V225**
- Baseline contratual vigente: **V183**
- Modelo metodológico vinculante vigente: **V182**
- Entrada operacional principal: `aplicacao/principal.py`
- Configuração canônica: `dados/config_atualizado.json`
- Base financeira canônica: `dados/dados_financeiros.xlsx`

## Leitura obrigatória inicial

1. `README.md`
2. `AGENTS.md`
3. `relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md`
4. `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
5. `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
6. `relatorios/INDICE_RELATORIOS.md`

## Regra de leitura

1. Tratar a V225 como baseline funcional estável atual.
2. Tratar a V183 como contrato mestre vigente.
3. Tratar a V182 como modelo metodológico vinculante.
4. Tratar documentos V216–V224 como trilha de implementação e validação da frente de aportes planejados, gate econômico e release limpo.
5. Não usar documentos históricos como base normativa principal para novas implementações.
6. Consultar histórico, logs e relatórios de limpeza somente quando a tarefa exigir rastreabilidade específica.

## Estado funcional consolidado na V225

| Frente | Situação |
|---|---|
| Dias corridos/dias úteis dos lotes | centralizados e corrigidos |
| Idade fiscal | centralizada |
| Aportes planejados | disponíveis em modo diagnóstico |
| Gate econômico | ativo |
| Aportes economicamente inferiores | bloqueados |
| Cenário final validado | `sem_aportes_planejados` |
| Release limpo | validado |
| Baseline funcional | promovida formalmente |

## Execução operacional principal

```bash
python aplicacao/principal.py
```

Esse comando é a validação mínima padrão para alterações que possam afetar execução, console, planilha, dados, cache, pagamentos, rendimento, switching ou ranking.

## Abas de entrada autorizadas

A execução deve ler somente:

- `Carteira`;
- `Todos os Gastos`;
- `Inventário de Lotes`.

Qualquer estrutura derivada deve ser criada internamente pelo código.

## Camada única de saída

A saída observável oficial deve permanecer centralizada e auditável, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

Módulos centrais a consultar antes de alterar saídas:

- `nucleo/saida_canonica.py`
- `aplicacao/console/principal.py`
- `aplicacao/principal.py`

## Restrições de continuidade

Não reabrir automaticamente:

- cálculo de dias dos lotes;
- idade fiscal centralizada;
- regra do gate econômico;
- transição diagnóstica dos aportes planejados;
- scripts canônicos de auditoria;
- contratos matemáticos/econômicos;
- leitura das três abas autorizadas.

## Para uso com Codex

Codex deve priorizar:

1. leitura de `AGENTS.md`;
2. mudanças pequenas e localizadas;
3. validação explícita com `python aplicacao/principal.py`, quando aplicável;
4. preservação da baseline V225;
5. não leitura em massa de `relatorios/historico/**`, `logs/iteracoes/**` e relatórios de limpeza sem necessidade explícita.

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

