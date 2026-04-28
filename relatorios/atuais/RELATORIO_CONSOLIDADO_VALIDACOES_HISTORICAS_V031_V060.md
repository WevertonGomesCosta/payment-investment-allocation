# Relatório consolidado — validações históricas V031–V060

## Objetivo

Consolidar a faixa `V031_V060` das validações históricas, preservando validações de compileall, inspeções da base, planilha operacional, convenção de valuation, CDI/cache, fallback de dados, organização arquitetural, release checker e contrato mínimo da Frente F1, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações consolidadas nesta faixa: 21
- Faixa: V031–V060
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das validações

| Versão | Linhas | Título |
|---:|---:|---|
| V31 | 23 | VALIDACAO LOCAL V31 |
| V32 | 30 | VALIDACAO LOCAL V32 |
| V33 | 41 | VALIDACAO LOCAL V33 |
| V34 | 41 | VALIDACAO LOCAL V34 |
| V35 | 56 | VALIDACAO LOCAL V35 |
| V36 | 38 | VALIDAÇÃO LOCAL V36 |
| V37 | 40 | VALIDAÇÃO LOCAL V37 |
| V38 | 15 | VALIDAÇÃO LOCAL V38 |
| V39 | 33 | VALIDAÇÃO LOCAL V39 |
| V40 | 26 | VALIDAÇÃO LOCAL V40 |
| V41 | 22 | Validação local V41 |
| V42 | 30 | Validação local V42 |
| V45 | 26 | Validação local V45 |
| V48 | 23 | VALIDAÇÃO LOCAL V47 |
| V50 | 17 | Validação local V50 |
| V51 | 22 | Validação local V51 |
| V52 | 27 | Validação local V52 |
| V55 | 9 | Validação local V55 |
| V58 | 37 | Validação local V58 |
| V59 | 39 | Validação local V59 |
| V60 | 39 | Validação local V60 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Execução e compilação | Validações de `compileall`, console e scripts operacionais foram preservadas. |
| Valuation/CDI/cache | Testes de data de referência, fallback e cache BCB foram consolidados. |
| Planilha operacional | Geração de planilha e artefatos operacionais foi registrada. |
| Organização arquitetural | Centralização de contexto, console modular e identidade da baseline foram preservadas. |
| Frente F1 | Validação do contrato mínimo da F1 e release checker foi registrada. |

## Detalhe por validação

### V31 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V31.md`

- Linhas originais: 23
- Título: VALIDACAO LOCAL V31

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V31
Validação local executada com sucesso na baseline derivada da V30.
## Comandos executados
- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`
## Evidências principais
- fechamento da referência em `2026-04-15` aplicado no núcleo e no replay;
- fallback CDI controlado registrado com `data_valuation=2026-04-15` e `data_fator_utilizado=2026-04-14`;
- replay estendido até a data de referência completa;
- deltas críticos vs. app reduzidos para a faixa aproximada de `R$ 0,01` a `R$ 0,21` no líquido e `R$ 0,02` a `R$ 0,11` no bruto;
- resíduos remanescentes concentrados em:
  - duas contas parcialmente cobertas de `R$ 0,68` e `R$ 0,71`;
  - micro-saldos pós-replay de `R$ 3,19`, `R$ 0,49`, `R$ 0,38`, `R$ 0,09` e `R$ 0,04`.
## Observação do teste de -1 dia
O teste de `-1 dia de rendimento` ficou limpo para `Lote 3000 mar. V`, `Lote 3000 mar. B` e `Lote 8500 mar.`. Para `Lote 6630,64 fev.`, o console marca corretamente que houve saque em `15/04/2026`, então a comparação `ref` vs. `ref-1d` não isola apenas rendimento.
```

</details>

### V32 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V32.md`

- Linhas originais: 30
- Título: VALIDACAO LOCAL V32

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V32
Validação local executada com sucesso na derivação V32.
## Comandos executados
- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`
## Evidências principais
- `data_referencia_simulacao` fixada em `2026-04-15` no config para manter a execução alinhada à auditoria dos apps;
- nova seção no console: `AUDITORIA DETALHADA DOS RESÍDUOS DE SAQUE/ARREDONDAMENTO`;
- classificação causal dos 7 resíduos remanescentes:
  - 2 casos de `teto líquido do lote no esgotamento`;
  - 2 casos de `remanescente por rendimento histórico`;
  - 2 casos de `saldo residual após saque líquido-alvo`;
  - 1 caso de `micro-saldo centesimal pós-saques`.
## Deltas críticos vs. app em 15/04/2026
- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
```

</details>

### V33 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V33.md`

- Linhas originais: 41
- Título: VALIDACAO LOCAL V33

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V33
Validação local executada com sucesso na derivação V33.
## Comandos executados
- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`
## Evidências principais
- limiar operacional de resolução fixado em `R$ 0,20` no config;
- resíduos `<= R$ 0,20` passaram a ser classificados como `resolvido por limiar`;
- nova organização da auditoria:
  - tabela de itens resolvidos por limiar;
  - tabela de itens pendentes `> limiar` com `data`, `conta` e `lote`;
  - tabela causal detalhada apenas dos pendentes.
## Resultado da classificação dos resíduos
- `2` resíduos resolvidos por limiar:
  - `Lote 7800 abr.` → `R$ 0,09`
  - `Lote 2063,11 fev.` → `R$ 0,04`
- `5` resíduos pendentes para validação:
```

</details>

### V34 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V34.md`

- Linhas originais: 41
- Título: VALIDACAO LOCAL V34

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V34
Validação local executada com sucesso na derivação V34.
## Comandos executados
- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`
## Evidências principais
- a criação de lotes passou a preservar `taxa_base_cdi = 0.0` quando essa taxa é explicitamente informada;
- os lotes históricos `nao_aportado_exaurido` deixaram de render indevidamente no replay;
- a auditoria residual foi revalidada após a correção, sem alterar os deltas críticos contra os apps.
## Resultado da reauditoria residual
### Casos removidos pela correção estrutural
- `Lote 3600 abr.`
- `Lote 7800 abr.`
### Resíduo resolvido por limiar
- `Lote 2063,11 fev.` → `R$ 0,04`
### Resíduos pendentes para validação
- `despesa_auto_00037` → `R$ 0,71`
```

</details>

### V35 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V35.md`

- Linhas originais: 56
- Título: VALIDACAO LOCAL V35

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V35
Validação local executada com sucesso na derivação V35.
## Comandos executados
- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`
## Evidências principais
- a transição de bônus passou a respeitar o primeiro dia útil de rendimento quando o fim da janela corrida cai em dia sem rendimento bancário;
- o `Lote 5400 fev.` foi reprocessado e seu evento final de `2026-03-20` saiu de um desvio material para um resíduo de `R$ 0,09`;
- o imposto do evento final do `Lote 5400 fev.` passou a bater exatamente com o app: `R$ 19,74`.
## Revalidação do `Lote 5400 fev.`
### Evento 1 — `2026-03-13` — `Escola`
- bruto modelo V35: `R$ 810,20`
- imposto modelo V35: `R$ 3,00`
- líquido modelo V35: `R$ 807,20`
### Evento 2 — `2026-03-16` — `Internet`
- bruto modelo V35: `R$ 132,91`
- imposto modelo V35: `R$ 0,51`
```

</details>

### V36 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V36.md`

- Linhas originais: 38
- Título: VALIDAÇÃO LOCAL V36

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V36
## Ambiente e execução
Base usada na validação:
- repositório derivado da V35;
- nova planilha substituindo `dados/dados_financeiros.xlsx`;
- cache CDI mantido em `dados/cache_bcb.json`;
- data de referência da execução: `2026-04-15`.
## Comandos executados
```bash
python -m compileall aplicacao nucleo
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado
- execução local concluída com sucesso;
- leitura da nova planilha estabilizada após o tratamento de `NaT`;
- auditoria crítica dos lotes vs. app permaneceu estável para os lotes de referência em `15/04/2026`;
- reauditoria residual reduziu os casos pendentes acima do limiar para dois itens novos ligados ao `Lote 5680 abr.`, fora do bloco atual dos lotes criticamente auditados.
```

</details>

### V37 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V37.md`

- Linhas originais: 40
- Título: VALIDAÇÃO LOCAL V37

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V37
## Ambiente
- data de referência da execução: `2026-04-16`
- cache CDI: último fator disponível em `2026-04-15`
- fechamento da referência em `2026-04-16`: fallback controlado para o último fator disponível
## Comandos executados
```bash
python -m compileall aplicacao nucleo
python scripts/inspecionar_base.py
python aplicacao/principal.py
```
## Resultados principais
### Replay controlado do passado
- contas históricas: `62`
- cobertas integralmente: `61`
- parcialmente cobertas: `1`
- não cobertas: `0`
- inconsistência remanescente: apenas `despesa_auto_00037` (`Lote 5400 fev.`) com `R$ 0,09`, já dentro do limiar
```

</details>

### V38 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V38.md`

- Linhas originais: 15
- Título: VALIDAÇÃO LOCAL V38

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V38
## Escopo
Esta versão contém atualização documental da baseline, sem alteração adicional de lógica operacional além do que já havia sido consolidado na V37.
## Arquivos atualizados
- `README.md`
- `relatorios/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/BASELINE_FIXA_V38.md`
## Regra formalizada
Foi consolidado em texto canônico curto o tratamento de lotes com `Data Recebimento` e `Data Aplicação` distintas, para uso uniforme em relatórios e no README operacional.
```

</details>

### V39 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V39.md`

- Linhas originais: 33
- Título: VALIDAÇÃO LOCAL V39

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V39
## Escopo
Esta versão consolida uma limpeza documental ampliada do repositório e a remoção de artefatos temporários proibidos do pacote final.
## Alterações executadas
- criação da estrutura `relatorios/atuais/`;
- criação da estrutura `relatorios/historico/` com subpastas por tipo documental;
- migração organizada de baselines, validações locais e auditorias específicas para essa nova estrutura;
- atualização do `README.md` para apontar apenas para documentos vigentes e para o índice documental;
- atualização do `CONTRATO_OPERACIONAL_PROJETO.md` com a hierarquia documental oficial da V39;
- remoção de `__pycache__` e `.pyc` do pacote final.
## Arquivos vigentes da baseline após a limpeza
- `README.md`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BASELINE_FIXA_V39.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V39.md`
## Validação operacional executada
- inspeção da estrutura documental reorganizada;
```

</details>

### V40 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V40.md`

- Linhas originais: 26
- Título: VALIDAÇÃO LOCAL V40

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V40
## Execuções realizadas
```bash
python -m compileall aplicacao nucleo scripts
python aplicacao/principal.py
python scripts/gerar_planilha_operacional.py
```
## Resultado validado
- o console passou a omitir as auditorias já encerradas solicitadas;
- a tabela de inconsistências do replay passou a usar apenas inconsistências materiais acima do limiar;
- os `Top produtos selecionados` ficaram em seção própria;
- o `RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS` foi reposicionado logo após a leitura das abas;
- a tabela final de lotes ativos passou a ser exibida na saída principal;
- a planilha operacional foi gerada com as abas:
  - `Extrato passado`
  - `Extrato futuro`
  - `Melhores produtos`
  - `Situação atual`
```

</details>

### V41 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V41.md`

- Linhas originais: 22
- Título: Validação local V41

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V41
## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
## Resultado auditado
Na reexecução local da V41, o lote `Lote 6630,64 fev.` foi reproduzido com os seguintes valores na seção `Situação atual — lotes ativos`:
- Recebimento: `2026-02-04`
- Aplicação: `2026-02-04`
- Produto: `CDB Turbinado`
- Valor original: `R$ 6.630,64`
- Dias corridos: `71`
- Dias úteis: `47`
- Bruto: `R$ 2.852,48`
- Líquido: `R$ 2.833,92`
- Saldo rem.: `R$ 2.770,00`
## Observação
A discrepância maior (`R$ 2.854,13` / `R$ 2.835,21`) não foi reproduzida na V40 entregue. Ainda assim, a V41 força a tabela e a planilha a usarem o mesmo caminho explícito de cálculo para evitar divergências futuras entre exibição e estado interno do lote.
```

</details>

### V42 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V42.md`

- Linhas originais: 30
- Título: Validação local V42

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V42
## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
## Resultado reproduzido com o cache atual do repositório
Na execução local com a série CDI atualmente salva no repositório, a linha do `Lote 6630,64 fev.` na seção `Situação atual — lotes ativos` ficou em:
- Valor original: `R$ 6.630,64`
- Dias corridos: `71`
- Dias úteis: `47`
- Bruto: `R$ 2.852,48`
- Líquido: `R$ 2.833,92`
- Saldo rem.: `R$ 2.770,00`
## Resultado validado para o cenário da divergência reportada
A correção também foi validada contra o cenário em que a série CDI já contém `2026-04-15`, reproduzindo o padrão reportado pelo usuário (`48 dias úteis`, `R$ 2.854,13 / R$ 2.835,21`) antes da correção.
Após a V42, nesse mesmo cenário, a linha passa para:
- Dias corridos: `71`
- Dias úteis: `47`
```

</details>

### V45 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V45.md`

- Linhas originais: 26
- Título: Validação local V45

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V45
## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
## Resultado da execução local
A baseline executou sem erro após a revisão documental e a atualização da versão para `V45`.
Resumo observado no console:
- versão reportada: `V45`
- data de referência: `2026-04-16`
- abas primárias lidas com sucesso: `Carteira`, `Inventário de Lotes`, `Todos os Gastos`
- carteira canônica: `91` produtos
- inventário canônico: `15` lotes
- gastos canônicos: `214` despesas
- triagem preliminar: `70` candidatos
- núcleo financeiro mínimo: `10` lotes financeiros
- planilha operacional gerada: `saidas/relatorio_operacional_v45.xlsx`
## Critérios validados
```

</details>

### V48 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V48.md`

- Linhas originais: 23
- Título: VALIDAÇÃO LOCAL V47

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V47
## Execução realizada
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
## Resultado
A baseline executou sem erro após a substituição do `cache_bcb.json`.
## Auditoria do cache
- `data_atualizacao`: `2026-04-16`
- `meta.data_final`: `2026-04-16`
- última data com fator disponível no mapa: `2026-04-15`
- `taxa_projecao`: `0.0`
- mudança de fator observada a partir de `2026-03-19`: de `1.00055131` para `1.00054266`
## Situação atual dos lotes ativos validada
- `Lote 6630,64 fev.`: bruto `2854.13`, líquido `2835.21`, saldo rem. `2770.06`
- `Lote 3000 mar. V`: bruto `3119.00`, líquido `3092.22`, saldo rem. `3000.00`
- `Lote 3000 mar. B`: bruto `3115.05`, líquido `3089.16`, saldo rem. `3000.00`
- `Lote 8500 mar.`: bruto `8725.69`, líquido `8694.49`, saldo rem. `8587.00`
```

</details>

### V50 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V50.md`

- Linhas originais: 17
- Título: Validação local V50

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V50
Validações executadas nesta versão:
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
Resultado esperado da V50:
- o dia da aplicação não entra como dia de rendimento do lote;
- o primeiro dia útil subsequente à aplicação já pode render;
- a regra passa a ficar explícita no núcleo financeiro, não apenas implícita na evolução monetária do saldo.
Validação adicional V50:
- `python scripts/gerar_auditoria_diaria_lote.py`
```

</details>

### V51 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V51.md`

- Linhas originais: 22
- Título: Validação local V51

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V51
Validações executadas nesta versão:
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
Resultado esperado da V51:
- o dia da aplicação não entra como dia de rendimento do lote;
- o primeiro dia útil subsequente à aplicação já pode render;
- a regra passa a ficar explícita no núcleo financeiro, não apenas implícita na evolução monetária do saldo.
Validação adicional V51:
- `python scripts/gerar_auditoria_diaria_lote.py`
Validação adicional V51:
- python aplicacao/principal.py
- conferência visual das novas seções do console.
```

</details>

### V52 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V52.md`

- Linhas originais: 27
- Título: Validação local V52

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V52
Validações executadas nesta versão:
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
Resultado esperado da V52:
- o dia da aplicação não entra como dia de rendimento do lote;
- o primeiro dia útil subsequente à aplicação já pode render;
- a regra passa a ficar explícita no núcleo financeiro, não apenas implícita na evolução monetária do saldo.
Validação adicional V52:
- `python scripts/gerar_auditoria_diaria_lote.py`
Validação adicional V52:
- python aplicacao/principal.py
- conferência visual das novas seções do console.
## Ajuste V52
A seção `Situação atual — lotes ativos` foi dividida em duas tabelas: uma para identificação/tempo e outra para valores atuais.
```

</details>

### V55 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V55.md`

- Linhas originais: 9
- Título: Validação local V55

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V55
- código e contrato alinhados à regra de aquisição de dados com download primeiro e fallback depois;
- `nucleo/cache_cdi_bcb.py` atualizado para tentar fetch online antes do cache local;
- `nucleo/leitor_planilha.py` atualizado para tentar download da planilha antes do fallback local;
- contrato executável atualizado com a nova regra.
- `python aplicacao/console/principal.py` executou com a nova regra de aquisição de dados;
- `python scripts/operacional/gerar_planilha_operacional.py` gerou `saidas/operacional/relatorio_operacional_v55.xlsx`.
```

</details>

### V58 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V58.md`

- Linhas originais: 37
- Título: Validação local V58

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V58
## Escopo validado
- contexto canônico da baseline centralizado em `nucleo/contexto_baseline.py`;
- console modularizado por seções;
- identidade de versão e nomes de artefatos centralizados;
- wrappers antigos preservados.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
## Artefatos gerados
- `saidas/operacional/relatorio_operacional_v58.xlsx`
## Atualização V58
- fallback encadeado do CDI para dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente quando o download do BCB falhar.
```

</details>

### V59 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V59.md`

- Linhas originais: 39
- Título: Validação local V59

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V59
## Escopo validado
- identidade da baseline atualizada para V59;
- remoção do ramo residual `menos_1_dia`;
- consistência do índice documental vigente;
- checagem mínima automática de release;
- wrappers antigos preservados.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`
## Artefatos gerados
```

</details>

### V60 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V60.md`

- Linhas originais: 39
- Título: Validação local V60

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V60
## Escopo validado
- identidade da baseline atualizada para V60;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 documentado e validado;
- script diagnóstico da F1 e wrapper de compatibilidade executáveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`
- `python scripts/inspecionar_contrato_f1.py`
```

</details>

## Decisão desta etapa

A faixa V031–V060 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de validações sejam consolidadas e um índice-mestre final seja criado.
