# Relatório consolidado — auditorias específicas históricas da raiz

## Objetivo

Consolidar os documentos históricos remanescentes diretamente em `relatorios/historico/auditorias_especificas/`, preservando auditorias antigas de lotes, arquitetura, scripts, ativação de futuros, pós-vencimento, tau, flattening, validações locais, recalibração e recomputação sem manter arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui documentos vigentes em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saída oficial.

- Arquivos consolidados: 20
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Tema classificado | Linhas | Título |
|---|---|---:|---|
| `relatorios/historico/auditorias_especificas/AUDITORIA_ARQUITETURAL_V3.md` | arquitetura_repositorio_scripts | 49 | Auditoria arquitetural da V3 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md` | ativacao_futuros_pos_vencimento | 53 | Auditoria da ativação dos lotes futuros e expansão da grade oficial híbrida — V136 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md` | ativacao_futuros_pos_vencimento | 35 | Auditoria da ativação de lotes não aportados futuros — V136 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_CHAVE_TAU_V149_2026-05-04.md` | tau_flattening | 26 | Auditoria da chave experimental com tau em 2026-05-04 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_CORRECAO_FLATTENING_V148_2026-05-04.md` | tau_flattening | 62 | Auditoria experimental da correção de flattening em 2026-05-04 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_DUPLICACAO_SCRIPTS_V154.md` | arquitetura_repositorio_scripts | 71 | Auditoria de duplicação entre `scripts/` e `scripts/diagnostico/` |
| `relatorios/historico/auditorias_especificas/AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md` | auditoria_geral | 101 | Auditoria de fechamento da frente temporal — V135 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_JANELA_TAU_SEM_GATE_V151_2026-05-04_2026-05-12.md` | tau_flattening | 94 | Auditoria da janela 2026-05-04 a 2026-05-12 sem pré-gate |
| `relatorios/historico/auditorias_especificas/AUDITORIA_JANELA_TAU_V150_2026-05-04_2026-05-12.md` | tau_flattening | 78 | Auditoria multi-dia com tau = 10,0 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_LOTE_5680_ABR_V37.md` | auditorias_lotes | 30 | AUDITORIA ESPECÍFICA — LOTE 5680 ABR. — V37 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_POS_VENCIMENTO_V145.md` | ativacao_futuros_pos_vencimento | 132 | AUDITORIA POS-VENCIMENTO V145 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_REPOSITORIO_V142.md` | arquitetura_repositorio_scripts | 30 | AUDITORIA_REPOSITORIO_V142 |
| `relatorios/historico/auditorias_especificas/AUDITORIA_TEMATICA_SCRIPTS_TEMPORAIS_V155.md` | arquitetura_repositorio_scripts | 62 | Auditoria temática dos scripts temporais — V155 |
| `relatorios/historico/auditorias_especificas/RECALIBRACAO_PLANEJADOR_SWITCHING_TEMPORAL_V120.md` | recalibracao_recomputacao | 28 | Recalibração do planejador temporal de switching — V120 |
| `relatorios/historico/auditorias_especificas/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V107.md` | recalibracao_recomputacao | 26 | Recomputação sequencial central V107 |
| `relatorios/historico/auditorias_especificas/REORGANIZACAO_ESTRUTURAL_V153.md` | arquitetura_repositorio_scripts | 113 | Reorganização estrutural V153 |
| `relatorios/historico/auditorias_especificas/VALIDACAO_LOCAL_V139.md` | validacoes_locais | 7 | Validação local V139 |
| `relatorios/historico/auditorias_especificas/VALIDACAO_LOCAL_V141.md` | validacoes_locais | 12 | Validação local V141 |
| `relatorios/historico/auditorias_especificas/VALIDACAO_LOTE_10342_FEV_V36.md` | auditorias_lotes | 82 | VALIDAÇÃO DO LOTE 10342 FEV. — V36 |
| `relatorios/historico/auditorias_especificas/VALIDACAO_LOTE_5400_FEV_V35.md` | auditorias_lotes | 25 | VALIDACAO LOTE 5400 FEV - V35 |

## Interpretação consolidada por tema

| Tema | Informação preservada |
|---|---|
| Auditorias de lotes | Validações históricas de lotes específicos foram preservadas em forma consolidada. |
| Arquitetura/repositório/scripts | Auditorias de arquitetura, repositório, duplicação e organização de scripts foram preservadas. |
| Ativação/futuros/pós-vencimento | Evidências históricas sobre lotes futuros, ativação e pós-vencimento foram preservadas. |
| Tau/flattening | Auditorias técnicas de tau e correção de flattening foram preservadas. |
| Validações locais | Registros de validação local foram preservados. |
| Recalibração/recomputação | Histórico de recalibração do planejador e recomputação sequencial foi preservado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/auditorias_especificas/AUDITORIA_ARQUITETURAL_V3.md`

- Tema classificado: `arquitetura_repositorio_scripts`
- Título: Auditoria arquitetural da V3
- Linhas originais: 49

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria arquitetural da V3
## Objetivo desta reconstrução
Esta versão não amplia o domínio financeiro do projeto. Ela apenas reconstrói a
baseline para deixá-la mais coerente com a regra de auditoria por
**responsabilidade real**, e não por módulo físico herdado dos scripts-base.
## Problemas identificados na V2 revisada
1. A estrutura já sugeria diretórios futuros como `motores/`, `estrategias/` e
   `adapters/` antes de termos mapeado suficientemente as responsabilidades
   reais nos scripts-base.
2. Parte importante da base ainda estava nomeada em inglês, o que contrariava a
   diretriz de manter o projeto em português.
3. O carregador de config estava funcional, mas ainda subrepresentava a lógica
   auditada do Script 1 para descoberta e priorização de arquivos de config.
4. A base ainda precisava ficar mais neutra, para evitar que a própria árvore
   do repositório induzisse modularização prematura.
## Decisões aplicadas nesta reconstrução
- A árvore do projeto foi reduzida a uma base mais neutra e menor.
- Os módulos iniciais foram renomeados para português.
- O repositório passou a usar `dados/`, `saidas/`, `relatorios/` e `testes/`.
- O núcleo inicial ficou restrito a:
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md`

- Tema classificado: `ativacao_futuros_pos_vencimento`
- Título: Auditoria da ativação dos lotes futuros e expansão da grade oficial híbrida — V136
- Linhas originais: 53

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da ativação dos lotes futuros e expansão da grade oficial híbrida — V136
## Resultado da auditoria de ativação
- lotes futuros não aportados auditados: **24**
- ativações corretas na própria data de recebimento: **24**
- ativações incorretas: **0**
Isso confirma que, a partir desta versão, os lotes futuros não aportados entram como fontes elegíveis exatamente na data de recebimento.
## Evidência de ativação ao longo do horizonte
Exemplos confirmados:
- `Lote 7000 mai.` entra em `2026-05-03`
- `Lote 7000 set.` entra em `2026-09-01`
- `Lote 7000 mar.` entra em `2027-03-03`
- `Lote 5680 mar.` entra em `2027-03-06`
## Expansão da grade oficial híbrida até 2027-03-31
A expansão completa com combinações agrupadas no horizonte inteiro ficou computacionalmente pesada neste ambiente interativo depois da entrada dos lotes futuros. O bloqueio não é mais estrutural da base, e sim combinatório:
- em `2026-09-01`, já com os futuros ativados, o planejador reduzido por fonte/destino gerou **95 ações**;
- mesmo após capar para **3 fontes por destino** apenas para fins de prova de execução tardia, ainda restaram **58 cenários** num único dia;
- com cap **6**, um único dia já sobe para **513 cenários**.
Por isso, nesta entrega a expansão ficou preparada no script até `2027-03-31`, mas a validação executada no ambiente foi feita por **provas tardias representativas**, não por varredura diária completa do horizonte inteiro.
## Provas tardias executadas
### 2026-09-01
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md`

- Tema classificado: `ativacao_futuros_pos_vencimento`
- Título: Auditoria da ativação de lotes não aportados futuros — V136
- Linhas originais: 35

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da ativação de lotes não aportados futuros — V136
- Data de referência: 2026-04-21
- Lotes futuros auditados: 24
- Ativações corretas na data de recebimento: 24
- Ativações incorretas: 0
## Registros auditados
| Lote | Data recebimento | Valor | Elegível antes | Elegível no dia | Ativação correta |
|---|---|---:|---|---|---|
| Lote 7000 mai. | 2026-05-03 | 7000.00 | Não | Sim | Sim |
| Lote 3600 mai. | 2026-05-06 | 3600.00 | Não | Sim | Sim |
| Lote 5680 mai. | 2026-05-06 | 5680.00 | Não | Sim | Sim |
| Lote 7000 jun. | 2026-06-02 | 7000.00 | Não | Sim | Sim |
| Lote 1800 jun. | 2026-06-05 | 1800.00 | Não | Sim | Sim |
| Lote 5680 jun. | 2026-06-05 | 5680.00 | Não | Sim | Sim |
| Lote 7000 jul. | 2026-07-02 | 7000.00 | Não | Sim | Sim |
| Lote 5680 jul. | 2026-07-05 | 5680.00 | Não | Sim | Sim |
| Lote 7000 ago. | 2026-08-01 | 7000.00 | Não | Sim | Sim |
| Lote 5680 ago. | 2026-08-04 | 5680.00 | Não | Sim | Sim |
| Lote 7000 set. | 2026-09-01 | 7000.00 | Não | Sim | Sim |
| Lote 5680 set. | 2026-09-04 | 5680.00 | Não | Sim | Sim |
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_CHAVE_TAU_V149_2026-05-04.md`

- Tema classificado: `tau_flattening`
- Título: Auditoria da chave experimental com tau em 2026-05-04
- Linhas originais: 26

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da chave experimental com tau em 2026-05-04
Baseline: V148
Versão experimental: V149
## Contrato experimental
Mantém os 7 primeiros critérios canônicos intactos e, no empate, compara patrimônio_terminal_proxy - tau * custo_operacional.
## Base
- Patrimônio terminal proxy do `pay_only`: **R$ 25.456,76**
- Custo operacional do `pay_only`: **9.0**
## Regra atual
- Vencedor: **pay_only** | rotulo `` | fontes — | patrimônio **R$ 25.456,76** | custo operacional **9.0**
## Tau = 9,5
- Vencedor: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | fontes Lote 7000 mai., Lote 3000 mar. V | patrimônio **R$ 25.499,07** | custo operacional **11.0**
- Quantidade de switching promovidos vs base: **33**
- Melhor 3k-only promovido: `Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)` | fontes Lote 3000 mar. V | delta patrimônio **R$ 10,58** | delta custo operacional **1.0** | ganho/op **10.580000**
- Caso `Lote 7000 mai. -> MP 120%` promovido: sim | delta patrimônio **R$ 23,87** | delta custo operacional **1.0** | ganho/op **23.870000**
## Tau = 10,0
- Vencedor: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | fontes Lote 7000 mai., Lote 3000 mar. V | patrimônio **R$ 25.499,07** | custo operacional **11.0**
- Quantidade de switching promovidos vs base: **28**
- Melhor 3k-only promovido: `Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)` | fontes Lote 3000 mar. V | delta patrimônio **R$ 10,58** | delta custo operacional **1.0** | ganho/op **10.580000**
- Caso `Lote 7000 mai. -> MP 120%` promovido: sim | delta patrimônio **R$ 23,87** | delta custo operacional **1.0** | ganho/op **23.870000**
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_CORRECAO_FLATTENING_V148_2026-05-04.md`

- Tema classificado: `tau_flattening`
- Título: Auditoria experimental da correção de flattening em 2026-05-04
- Linhas originais: 62

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria experimental da correção de flattening em 2026-05-04
Baseline: V147
Versão experimental: V148
## Resumo
- Lotes normalizados no dia: Lote 3000 mar. V=R$ 3.104,32, Lote 3000 mar. B=R$ 2.571,24
- Patrimônio terminal proxy do pacote base (`pay_only`): **R$ 25.456,76**
- Patrimônio terminal proxy do pacote `switch_then_pay` 3k-only: **R$ 25.476,11**
- Delta de patrimônio terminal proxy: **R$ 19,35**
- `switch_then_pay` 3k-only vence o base: **False**
- Fontes do switching: Lote 3000 mar. V, Lote 3000 mar. B
- Destinos do switching: prod::mercado pago cofrinho 120% cdi meli+, prod::mercado pago cofrinho 120% cdi meli+
## Melhor cenário 3k-only sem gate
{
  "rotulo": "Lote 3000 mar. V + Lote 3000 mar. B -> Mercado Pago Cofrinho 120% CDI (Meli+)",
  "fontes": [
    "Lote 3000 mar. V",
    "Lote 3000 mar. B"
  ],
  "destinos": [
    "prod::mercado pago cofrinho 120% cdi meli+",
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_DUPLICACAO_SCRIPTS_V154.md`

- Tema classificado: `arquitetura_repositorio_scripts`
- Título: Auditoria de duplicação entre `scripts/` e `scripts/diagnostico/`
- Linhas originais: 71

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria de duplicação entre `scripts/` e `scripts/diagnostico/`
Baseline de entrada: **V153**
Baseline de saída: **V154**
## Resumo objetivo
- arquivos Python no `scripts/` raiz (sem subpastas): **65**
- arquivos Python canônicos em `scripts/diagnostico/` (sem `__init__`/`_bootstrap`): **62**
- nomes espelhados entre raiz e diagnóstico: **62**
- arquivos somente na raiz: **3**
- arquivos somente em `scripts/diagnostico/`: **0**
## Diagnóstico estrutural
A maior parte da “duplicação” entre `scripts/` e `scripts/diagnostico/` não é duplicação lógica, e sim **duplicação de entrada de execução**: a implementação vive em `scripts/diagnostico/` e a raiz mantém um ponto de entrada legado.
O risco estrutural real estava em três pontos:
1. **wrappers heterogêneos** na raiz (`import main`, `runpy.run_path`, ajustes manuais de `sys.path`);
2. **scripts diagnósticos novos** vivendo apenas na raiz, sem canonicidade temática;
3. **três scripts canônicos apenas em `scripts/diagnostico/`**, sem wrapper plano correspondente.
## Consolidação de baixo risco aplicada
### 1. Helper único de compatibilidade
Foi criado `scripts/_compat.py` para unificar a execução de wrappers via `run_module_entrypoint(...)`.
### 2. Canonicidade formal
- `scripts/diagnostico/` passa a ser a localização canônica dos inspeccionadores e consolidadores diagnósticos.
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md`

- Tema classificado: `auditoria_geral`
- Título: Auditoria de fechamento da frente temporal — V135
- Linhas originais: 101

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria de fechamento da frente temporal — V135
## Pergunta de decisão
Decidir se a evidência atual já permite encerrar a frente temporal com a única subjanela vencedora oficial `2026-04-30` a `2026-05-04`, ou se ainda existe justificativa técnica para estender a grade diária oficial híbrida até `2027-03-31`.
## Evidência já consolidada no fluxo oficial híbrido
### Subjanela oficialmente vencedora já confirmada
- `2026-04-30` a `2026-05-04`
- promoção oficial: `vencedor_terminal`
- cenário promovido: `Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150%`
### Período ampliado já auditado
- `2026-05-21` a `2026-08-18`
- dias auditados: `90`
- dias promovidos com switching: `0`
- dias promovidos com baseline: `90`
- a partir de `2026-06-03`, a origem oficial passa majoritariamente para `sem_cenarios_gerados`
## Evidência estrutural da base que impede encerrar a frente agora
A planilha-base ainda contém um bloco grande de **lotes futuros não aportados** e um volume material de **pagamentos futuros após `2026-08-18`**.
### Lotes futuros não aportados ainda fora do trecho auditado
- quantidade: `24`
- valor total: `R$ 144.880,00`
- distribuição mensal de recebidos não aportados:
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_JANELA_TAU_SEM_GATE_V151_2026-05-04_2026-05-12.md`

- Tema classificado: `tau_flattening`
- Título: Auditoria da janela 2026-05-04 a 2026-05-12 sem pré-gate
- Linhas originais: 94

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da janela 2026-05-04 a 2026-05-12 sem pré-gate
Baseline operacional: V150.
## Contrato auditado
- tau = **10,0**
- sem depender de `_melhor_plano_switching_diario_v143`
- em cada dia, o pacote base foi comparado apenas contra o **melhor switching bruto do dia**
## Resumo comparativo contra a V150 (gate + tau)
- Switching promovidos sem gate: **1**
- Dias com vencedor alterado vs V150: **1**
- Patrimônio final V150 (gate + tau): **R$ 25,993.97**
- Patrimônio final sem gate: **R$ 26,036.28**
- Delta agregado vs V150: **R$ 42.31**
- switch_then_pay V150: **0**
- switch_only V150: **0**
- switch_then_pay sem gate: **1**
- switch_only sem gate: **0**
## Decisões por dia
### 2026-05-04
- Pagamentos do dia: **1**
- IDs: despesa_auto_00070
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_JANELA_TAU_V150_2026-05-04_2026-05-12.md`

- Tema classificado: `tau_flattening`
- Título: Auditoria multi-dia com tau = 10,0
- Linhas originais: 78

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria multi-dia com tau = 10,0
Janela: **2026-05-04 a 2026-05-12**
## Resumo comparativo
- Switching adicionais promovidos por tau: **0**
- Dias com pacote vencedor alterado: **0**
- `switch_then_pay` na regra atual: **0**
- `switch_only` na regra atual: **0**
- `switch_then_pay` com tau=10,0: **0**
- `switch_only` com tau=10,0: **0**
- Patrimônio terminal proxy final, regra atual: **R$ 25.993,97**
- Patrimônio terminal proxy final, tau=10,0: **R$ 25.993,97**
- Delta patrimônio terminal proxy final: **R$ 0,00**
## Comparativo por dia
### 2026-05-04
- Vencedor, regra atual: **pay_only**
- Vencedor, tau=10,0: **pay_only**
- Mudou pacote vencedor: **False**
- Patrimônio vencedor, regra atual: **R$ 25.993,97**
- Patrimônio vencedor, tau=10,0: **R$ 25.993,97**
### 2026-05-05
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_LOTE_5680_ABR_V37.md`

- Tema classificado: `auditorias_lotes`
- Título: AUDITORIA ESPECÍFICA — LOTE 5680 ABR. — V37
- Linhas originais: 30

<details>
<summary>Trecho inicial preservado</summary>

```text
# AUDITORIA ESPECÍFICA — LOTE 5680 ABR. — V37
## Cadastro do lote
- lote: `Lote 5680 abr.`
- data de recebimento: `2026-04-06`
- data de aplicação: `2026-04-14`
- valor original: `R$ 5.680,00`
- produto: `CDB Neon Planejado 150% CDI - 60 dias`
## Regra aplicada
Entre `2026-04-06` e `2026-04-14` inclusive, o lote é tratado como **caixa pré-aplicação**:
- disponível para pagamentos;
- sem rendimento;
- sem IR/IOF de investimento;
- sem bloqueio por carência.
## Eventos históricos auditados
| Data | Conta | Fase | Bruto | Líquido | Saldo remanescente |
|---|---|---:|---:|---:|---:|
| 2026-04-08 | Pelada e churrasco | caixa_pre_aplicacao | 70,00 | 70,00 | 5.610,00 |
| 2026-04-10 | Concerto Carro | caixa_pre_aplicacao | 434,75 | 434,75 | 5.175,25 |
| 2026-04-14 | Escola | caixa_pre_aplicacao | 151,71 | 151,71 | 5.023,54 |
| 2026-04-14 | Escola | caixa_pre_aplicacao | 206,80 | 206,80 | 4.816,74 |
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_POS_VENCIMENTO_V145.md`

- Tema classificado: `ativacao_futuros_pos_vencimento`
- Título: AUDITORIA POS-VENCIMENTO V145
- Linhas originais: 132

<details>
<summary>Trecho inicial preservado</summary>

```text
# AUDITORIA POS-VENCIMENTO V145
## Escopo
Baseline usada: **V144**.
Janela crítica auditada: **2026-05-03 a 2026-05-06**.
Objetivo: verificar se o gate atual do motor diário está escondendo um caso realmente vencedor de `switch_then_pay` quando os lotes **Lote 3000 mar. V** e **Lote 3000 mar. B** entram em vencimento em **2026-05-04**, com rollover obrigatório no próprio dia ou, no máximo, em **2026-05-05**.
## Achado estrutural principal
A política operacional já existe no config:
- `politicas.pos_vencimento.rendimento = "parar"`
- `politicas.pos_vencimento.acao = "disponivel_para_resgate"`
Mas essa política **não está implementada no planejador temporal nem no motor diário experimental** nesta baseline. Na auditoria do código, não há uso de `pos_vencimento` em:
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/motor_diario_conjunto_experimental_v143.py`
Além disso, o planejador atual avalia lotes aportados como se ainda fossem fontes normais de switching, descontando custo fiscal na migração e projetando continuidade econômica do produto de origem após a data da ação. Os pontos centrais estão em `nucleo/planejador_switching_temporal_v1.py`:
- linhas **230-232**: estima imposto e subtrai custo fiscal do valor migrado
- linhas **237-243**: projeta o patrimônio terminal da origem a partir do retorno do produto atual
- linhas **303-309**: só promove candidato se o ganho econômico líquido for positivo frente a esse baseline
Isso cria um viés exatamente no caso dos lotes 3k mar: no pós-vencimento, o correto é tratar o lote como **caixa líquido disponível**, não como produto que ainda continua rendendo no estado de origem.
## Evidência a partir da V144 já auditada
No diagnóstico existente da V144 para a janela maior 2026-05-03 a 2026-05-12:
- em **2026-05-04**, o motor registra:
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_REPOSITORIO_V142.md`

- Tema classificado: `arquitetura_repositorio_scripts`
- Título: AUDITORIA_REPOSITORIO_V142
- Linhas originais: 30

<details>
<summary>Trecho inicial preservado</summary>

```text
# AUDITORIA_REPOSITORIO_V142
- Baseline auditada: `V141`.
- Escopo: organização do repositório, integridade do alocador terminal, viabilidade da expansão comparativa do fluxo de pagamentos e validação local mínima da nova camada V142.
## Achados principais
- A arquitetura da V141 está coerente com a reorganização documental recente: contratos, diagnósticos, wrappers de scripts e núcleo temporal permanecem separados de forma legível e auditável.
- O `alocador_pagamentos_terminal_v1` já estava funcional na V141, mas a validação operacional vigente ainda estava concentrada no recorte curto V138 e em cenários sintéticos/diagnósticos.
- O principal gargalo encontrado não foi erro estrutural do alocador, mas custo computacional da comparação expandida quando a auditoria ampla é executada com busca de switching muito larga; por isso a V142 comparativa usa teto controlado de candidatos por data apenas nesta camada de inspeção.
- Foi adicionada uma chave explícita para desabilitar H1–H3 (`desabilitar_modelos_script1_fase1`) em modo comparativo, permitindo auditoria controlada sem reabrir o contrato principal da V141.
## Validação local executada
- `python -m py_compile nucleo/alocador_pagamentos_terminal_v1.py`
- `python -m py_compile nucleo/fluxo_pagamentos_terminal_recorte_amplo_v142.py`
- execução real do fluxo ativo em 20 pagamentos futuros
- execução real do fluxo neutralizado em 20 pagamentos futuros
- comparação por pagamento entre as trajetórias ativa e neutralizada
## Riscos remanescentes
- A camada V142 ainda é comparativa/auditiva; ela não substitui o fluxo central principal.
- O teto de candidatos de switching por data foi reduzido apenas para manter a auditoria comparativa em recorte maior dentro de custo computacional controlado.
- Comparações ainda maiores (por exemplo, 30+ pagamentos com busca mais larga) exigirão nova calibração de custo de busca antes de promoção.
## Conclusão
- Não foi encontrado bloqueio contratual no núcleo que impeça a expansão.
```

</details>

### `relatorios/historico/auditorias_especificas/AUDITORIA_TEMATICA_SCRIPTS_TEMPORAIS_V155.md`

- Tema classificado: `arquitetura_repositorio_scripts`
- Título: Auditoria temática dos scripts temporais — V155
- Linhas originais: 62

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria temática dos scripts temporais — V155
## Escopo
Auditoria temática sobre os scripts relacionados a motor diário, pós-vencimento, `tau` e bloco crítico, tomando a V154 como baseline estrutural.
## Achados centrais
1. O conjunto auditado possui **10 scripts** que tratam do mesmo eixo semântico: decisão temporal local.
2. Esse eixo estava espalhado no diretório plano `scripts/diagnostico/`, misturando:
   - runners do motor diário;
   - auditorias de valoração e flattening;
   - microplanejamento e heurísticas do bloco crítico.
3. A separação temática mais coerente, antes de tocar no simulador central, é:
   - `motor_diario/`
   - `valoracao_decisao/`
   - `bloco_critico/`
## Scripts auditados
### Grupo `motor_diario/`
- `inspecionar_motor_diario_conjunto_experimental_v143.py`
- `inspecionar_motor_diario_conjunto_experimental_v144.py`
- `inspecionar_motor_diario_pos_vencimento_v146.py`
- `run_v150_multi.py`
### Grupo `valoracao_decisao/`
```

</details>

### `relatorios/historico/auditorias_especificas/RECALIBRACAO_PLANEJADOR_SWITCHING_TEMPORAL_V120.md`

- Tema classificado: `recalibracao_recomputacao`
- Título: Recalibração do planejador temporal de switching — V120
- Linhas originais: 28

<details>
<summary>Trecho inicial preservado</summary>

```text
# Recalibração do planejador temporal de switching — V120
## Objetivo
Substituir o ranqueamento por ganho proxy simples por um ranqueamento por **ganho terminal econômico mínimo real estimado**.
## Componentes incorporados
- custo fiscal estimado do resgate;
- patrimônio terminal reprojetado da origem até o fim do recorte;
- patrimônio terminal reprojetado do destino após reinvestimento líquido;
- penalidade incremental de carência/liquidez baseada na janela adicional de indisponibilidade;
- score final de ranqueamento econômico.
## Resultado no recorte curto
No recorte até 2026-05-20, nenhum candidato de switching permaneceu elegível após a recalibração.
Os principais candidatos ficaram com ganho terminal econômico mínimo estimado negativo, incluindo:
- `Lote 6630,64 fev.`: `-2.59`;
- `Lote 3000 mar. B`: `-9.47`;
- `Lote 3000 mar. V`: `-10.34`;
- `Lote 8500 mar.`: `-84.58`;
- `Lote 5680 abr.`: `-0.70`.
## Interpretação
A V120 evita que o simulador central gaste capacidade com switchings que parecem bons por proxy, mas já chegam economicamente dominados no próprio planejador temporal.
```

</details>

### `relatorios/historico/auditorias_especificas/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V107.md`

- Tema classificado: `recalibracao_recomputacao`
- Título: Recomputação sequencial central V107
- Linhas originais: 26

<details>
<summary>Trecho inicial preservado</summary>

```text
# Recomputação sequencial central V107
A V107 implementa a `recomputacao_sequencial_central_v1` como primeira camada executável da frente central após o saneamento contratual da V106.
## Escopo
- recalcular a fonte a cada pagamento futuro;
- usar saldos residuais atualizados;
- comparar alternativas pela métrica canônica mínima central;
- manter rastreabilidade por lote e por fonte;
- não abrir solver global completo.
## Comparador mínimo
A ordem de prioridade aplicada continua sendo:
1. violações de pagamentos `PROTEGIDA`;
2. déficit líquido total;
3. pagamentos sem cobertura integral;
4. patrimônio terminal proxy do cenário;
5. destruição estratégica de lotes;
6. fragmentação residual e piora evitável de liquidez futura.
## Papel da V107
A V107 não resolve o problema conjunto final, mas recoloca a evolução do projeto na frente central, deixando V103–V105 explicitamente como trilha experimental local.
```

</details>

### `relatorios/historico/auditorias_especificas/REORGANIZACAO_ESTRUTURAL_V153.md`

- Tema classificado: `arquitetura_repositorio_scripts`
- Título: Reorganização estrutural V153
- Linhas originais: 113

<details>
<summary>Trecho inicial preservado</summary>

```text
# Reorganização estrutural V153
## Objetivo
Executar uma primeira reorganização arquitetural **sem alterar o contrato funcional**, começando pelo mapeamento de responsabilidades reais e depois pela redistribuição de funções de menor risco.
## Limitação de baseline no ambiente
O artefato zip rotulado como V152 não estava disponível no ambiente de execução no momento desta etapa. A reorganização foi aplicada sobre a baseline acessível mais recente (`payment-investment-allocation_v151.zip`), preservando o contrato funcional observável do motor diário e sem introduzir mudanças de regra de negócio.
## Mapa de responsabilidades reais
### 1. Aplicação e console
- `aplicacao/principal.py`: ponto de entrada operacional.
- `aplicacao/console/*`: formatação e seções do console.
### 2. Configuração e dados
- `config/*`: contratos de carteira e parâmetros de heurísticas.
- `dados/*`: entrada bruta, cache CDI e planilha operacional.
### 3. Núcleo financeiro canônico
- `nucleo/nucleo_financeiro_minimo.py`: primitivas financeiras centrais.
- `nucleo/calendario_financeiro.py`: calendário e regras de dia útil.
- `nucleo/cache_cdi_bcb.py`: cache e fallback CDI.
- `nucleo/caixa_recebidos_auditaveis.py`: contrato detalhado de recebidos.
### 4. Estado operacional e leitura da base
- `nucleo/leitor_planilha.py`
- `nucleo/dados_operacionais_canonicos.py`
```

</details>

### `relatorios/historico/auditorias_especificas/VALIDACAO_LOCAL_V139.md`

- Tema classificado: `validacoes_locais`
- Título: Validação local V139
- Linhas originais: 7

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V139
## Verificações executadas
- `python scripts/diagnostico/verificar_release_baseline.py`
## Objetivo da validação
Confirmar que a reorganização documental/operacional da V139 preserva a baseline íntegra, sem artefatos efêmeros e com índice documental coerente.
```

</details>

### `relatorios/historico/auditorias_especificas/VALIDACAO_LOCAL_V141.md`

- Tema classificado: `validacoes_locais`
- Título: Validação local V141
- Linhas originais: 12

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V141
Validações executadas nesta etapa:
- compilação de `nucleo/alocador_pagamentos_terminal_v1.py`;
- compilação de `nucleo/pagamentos/modelos_script1/heuristicas_fase1.py`;
- execução de `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py`;
- `python scripts/diagnostico/verificar_release_baseline.py`.
Resultado esperado:
- baseline V141 íntegra;
- Fase 1 do Script 1 ativa no alocador;
- score auxiliar e desempate econômico materializados em estrutura auditável.
```

</details>

### `relatorios/historico/auditorias_especificas/VALIDACAO_LOTE_10342_FEV_V36.md`

- Tema classificado: `auditorias_lotes`
- Título: VALIDAÇÃO DO LOTE 10342 FEV. — V36
- Linhas originais: 82

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO DO LOTE 10342 FEV. — V36
## Contexto
O usuário informou duas discrepâncias principais para o `Lote 10342 fev.`:
1. o resgate agregado de `12/02/2026`, correspondente à soma de `Aluguel` + `IPVA`;
2. o resgate de `13/03/2026`, correspondente à conta `Escola`.
Além disso, a nova planilha corrigiu:
- `IPVA` de `12/02/2026` em `-R$ 0,02`;
- `Internet` de `16/02/2026` em `-R$ 1,00`.
## Correções relevantes desta versão
1. a nova planilha substituiu a base anterior;
2. a tabela do IOF passou a ser indexada corretamente por dia de vida (`dias - 1`);
3. a leitura de `NaT` no inventário foi robustecida para a nova base.
## Comparação contra o app
### 12/02/2026 — Aluguel + IPVA (resgate agregado no app)
#### App
- líquido: `R$ 2.389,58`
- bruto: `R$ 2.396,54`
- IR: `R$ 0,46`
- IOF: `R$ 6,50`
- imposto total: `R$ 6,96`
```

</details>

### `relatorios/historico/auditorias_especificas/VALIDACAO_LOTE_5400_FEV_V35.md`

- Tema classificado: `auditorias_lotes`
- Título: VALIDACAO LOTE 5400 FEV - V35
- Linhas originais: 25

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOTE 5400 FEV - V35
## Hipótese aplicada
Quando `data_base_fiscal + dias_bonus` cair em dia sem rendimento bancário, a taxa bônus deve permanecer válida no primeiro dia útil de rendimento subsequente.
## Traço do replay após a correção
| Data | Conta | Despesa ID | Valor da conta | Saldo antes | Bruto | Imposto | Líquido | Saldo remanescente |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-03-13 | Escola | despesa_auto_00035 | 807,20 | 5.490,39 | 810,20 | 3,00 | 807,20 | 4.680,19 |
| 2026-03-16 | Internet | despesa_auto_00036 | 132,40 | 4.682,85 | 132,91 | 0,51 | 132,40 | 4.549,94 |
| 2026-03-20 | Cartão Azul | despesa_auto_00037 | 4.540,55 | 4.560,20 | 4.560,20 | 19,74 | 4.540,46 | 0,00 |
## Comparação explícita do evento 3 contra o app
| Métrica | App | Modelo V34 | Modelo V35 | Delta V35 vs. app |
|---|---:|---:|---:|---:|
| Bruto | 4.560,29 | 4.559,42 | 4.560,20 | -0,09 |
| Imposto | 19,74 | 19,58 | 19,74 | 0,00 |
| Líquido | 4.540,55 | 4.539,84 | 4.540,46 | -0,09 |
## Conclusão
A correção cirúrgica removeu o erro estrutural principal do evento 3 do `Lote 5400 fev.`. O desvio remanescente caiu para `R$ 0,09`, abaixo do limiar operacional aprovado.
```

</details>

## Decisão sugerida

Após esta consolidação, os arquivos granulares restantes da raiz de `relatorios/historico/auditorias_especificas/` podem ser removidos se o relatório consolidado preservar os achados principais.
