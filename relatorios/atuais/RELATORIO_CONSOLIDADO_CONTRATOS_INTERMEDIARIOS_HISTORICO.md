# Relatório consolidado — contratos intermediários históricos

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/contratos_intermediarios/` em um único relatório atual, preservando a trilha contratual intermediária sem manter arquivos granulares.

## Regra de autoridade documental

Os documentos consolidados aqui têm valor histórico e de rastreabilidade. Eles não substituem nem sobrepõem os documentos normativos atuais em `relatorios/atuais/`, especialmente contrato mestre, modelo matemático-estatístico-financeiro oficial, baseline funcional estável e documentação operacional vigente.

- Arquivos consolidados: 21
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Referências externas | Título |
|---|---:|---:|---|
| `relatorios/historico/contratos_intermediarios/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md` | 26 | 14 | ALOCADOR PAGAMENTOS TERMINAL V137 |
| `relatorios/historico/contratos_intermediarios/ALOCADOR_PAGAMENTOS_TERMINAL_V141.md` | 29 | 12 | Alocador pagamentos terminal — V141 |
| `relatorios/historico/contratos_intermediarios/BASELINE_FIXA_V139.md` | 9 | 0 | Baseline fixa V139 |
| `relatorios/historico/contratos_intermediarios/BASELINE_FIXA_V141.md` | 8 | 1 | Baseline fixa V141 |
| `relatorios/historico/contratos_intermediarios/COMPARADOR_HIBRIDO_SWITCHING_V132.md` | 52 | 12 | Comparador híbrido de switching — V132 |
| `relatorios/historico/contratos_intermediarios/CONTRATO_ABSORCAO_MODELOS_SCRIPT1_PAGAMENTOS_V140.md` | 168 | 0 | Contrato de absorção dos modelos do Script 1 na camada de pagamentos — V140 |
| `relatorios/historico/contratos_intermediarios/CONTRATO_RANKING_CARTEIRA_V123.md` | 17 | 0 | Contrato operacional do ranking Carteira-only — V123 |
| `relatorios/historico/contratos_intermediarios/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md` | 203 | 1 | Contrato-alvo V117 — `alocador_pagamentos_terminal_v1` + `planejador_switching_temporal_v1` |
| `relatorios/historico/contratos_intermediarios/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md` | 123 | 1 | Contrato V117 — motor conjunto temporal |
| `relatorios/historico/contratos_intermediarios/ESTRUTURA_REPOSITORIO_V139.md` | 12 | 0 | Estrutura do repositório — V139 |
| `relatorios/historico/contratos_intermediarios/ESTRUTURA_REPOSITORIO_V141.md` | 11 | 1 | Estrutura do repositório — V141 |
| `relatorios/historico/contratos_intermediarios/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md` | 178 | 0 | Frente F1 — contrato mínimo de caixa/recebidos auditáveis |
| `relatorios/historico/contratos_intermediarios/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLO_V142.md` | 57 | 14 | FLUXO PAGAMENTOS TERMINAL RECORTE AMPLO V142 |
| `relatorios/historico/contratos_intermediarios/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md` | 46 | 14 | FLUXO PAGAMENTOS TERMINAL RECORTE CURTO V138 |
| `relatorios/historico/contratos_intermediarios/GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md` | 116 | 0 | Grade diária oficial com comparador híbrido — V134 |
| `relatorios/historico/contratos_intermediarios/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md` | 85 | 0 | Mapa de absorção legado — Scripts 1 e 2 |
| `relatorios/historico/contratos_intermediarios/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md` | 36 | 1 | Mapa das heurísticas prioritárias do Script 1 para pagamentos — V140 |
| `relatorios/historico/contratos_intermediarios/METRICA_CANONICA_MINIMA_CENTRAL.md` | 95 | 0 | Métrica canônica mínima central |
| `relatorios/historico/contratos_intermediarios/MOTOR_DIARIO_CONJUNTO_EXPERIMENTAL_V143_2026-04-21_2026-05-06.md` | 68 | 0 | Motor diário conjunto experimental V143 |
| `relatorios/historico/contratos_intermediarios/MOTOR_DIARIO_CONJUNTO_POS_VENCIMENTO_V146_2026-05-03_2026-05-06.md` | 71 | 0 | Auditoria do motor diário com normalização pós-vencimento — V146 |
| `relatorios/historico/contratos_intermediarios/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md` | 19 | 0 | Recomputação sequencial central V108 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Contratos intermediários | Histórico de transição contratual preservado em forma consolidada. |
| Governança | Hierarquia entre documentos históricos e documentos atuais permanece explícita. |
| Modelo/motor | Registros intermediários foram preservados sem alterar motor, dados ou execução. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/contratos_intermediarios/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`

- Título: ALOCADOR PAGAMENTOS TERMINAL V137
- Linhas originais: 26
- Referências externas detectadas: 14

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md:23:- moved: `saidas/oficial/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md` → `saidas/historico/compatibilidade_operacional/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`
relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md:24:- moved: `saidas/oficial/alocador_pagamentos_terminal_v137.json` → `saidas/historico/compatibilidade_operacional/alocador_pagamentos_terminal_v137.json`
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:596:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:681:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v137.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:744:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v137.py
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:16:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py,LEGADO_BLOQUEADO_V203,mantido como bloqueio da V203
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:96:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v137.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:158:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v137.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:9:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py,BLOQUEADO_COM_STUB,DIAGNOSTICO_LEGADO_COM_SAIDA_PROPRIA,nao,nao_executa,scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v137.py,Execução bloqueada por governança; saída própria não pode competir com console/planilha canônicos.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:96:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v137.py,HISTORICO_READ_ONLY,,nao,nao,,Acervo histórico preservado sem autoridade operacional.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:158:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v137.py,HISTORICO_ORIGINAL_PRESERVADO,,nao,nao,,Original preservado de script bloqueado; acervo histórico.
relatorios/atuais/MAPA_SCRIPTS_V201.md:45:| `inspecionar_alocador_pagamentos_terminal_v137.py` | 2 |
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# ALOCADOR PAGAMENTOS TERMINAL V137
## Objetivo
Elevar o `alocador_pagamentos_terminal_v1` de esqueleto funcional mínimo para uma primeira versão realmente utilizável na integração com o motor de pagamentos.
## Escopo implementado
A V137 passa a comparar explicitamente, para cada pagamento:
- saldo disponível;
- lote não aportado já disponível na data;
- lote aportado resgatável na data, com custo fiscal estimado;
- combinação mínima funcional entre fontes;
- cenário com switching elegível já filtrado pelo comparador híbrido, desde que seja fornecido com estado pós-switching.
## Regras novas
1. Lote aportado com carência ativa na data do pagamento deixa de entrar como fonte elegível.
2. O custo fiscal estimado do resgate entra no score da fonte.
3. O cenário com switching só entra quando o plano chega já classificado como `vencedor_terminal` ou `vencedor_hibrido_aceitavel`.
4. Planos não promovíveis pelo comparador híbrido não entram como fonte candidata.
5. O retorno inclui metadados explícitos sobre a comparação com switching.
## Limite assumido nesta etapa
A V137 não substitui ainda a recomputação central nem decide sozinha o melhor plano temporal de switching. Ela prepara o núcleo de pagamento para consumir um cenário com switching já filtrado externamente.
```

</details>

### `relatorios/historico/contratos_intermediarios/ALOCADOR_PAGAMENTOS_TERMINAL_V141.md`

- Título: Alocador pagamentos terminal — V141
- Linhas originais: 29
- Referências externas detectadas: 12

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:597:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:682:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v141.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:745:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v141.py
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:17:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py,LEGADO_BLOQUEADO_V203,mantido como bloqueio da V203
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:97:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v141.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:159:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v141.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:10:scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py,BLOQUEADO_COM_STUB,DIAGNOSTICO_LEGADO_COM_SAIDA_PROPRIA,nao,nao_executa,scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v141.py,Execução bloqueada por governança; saída própria não pode competir com console/planilha canônicos.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:97:scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v141.py,HISTORICO_READ_ONLY,,nao,nao,,Acervo histórico preservado sem autoridade operacional.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:159:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_alocador_pagamentos_terminal_v141.py,HISTORICO_ORIGINAL_PRESERVADO,,nao,nao,,Original preservado de script bloqueado; acervo histórico.
relatorios/atuais/MAPA_SCRIPTS_V201.md:46:| `inspecionar_alocador_pagamentos_terminal_v141.py` | 2 |
relatorios/atuais/MAPA_SCRIPTS_V201.md:155:| `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 136 |
relatorios/atuais/MAPA_SCRIPTS_V201.md:235:| `scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v141.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Alocador pagamentos terminal — V141
## Escopo da etapa
A V141 implementa a **Fase 1 de absorção dos modelos do Script 1** no `alocador_pagamentos_terminal_v1`, incorporando:
- `score_hibrido_5p_fonte`
- `penalidade_cliff_idade`
- `oportunidade_vpl_marginal`
Essas heurísticas entram como:
- score auxiliar por fonte;
- desempate econômico;
- ordenação interna da combinação mínima.
## Regra de decisão da V141
A decisão principal continua subordinada à métrica terminal do alocador.
Depois disso, a ordenação fina entre candidatos passa a usar a chave:
1. `score_terminal_comparativo`
2. `score_hibrido_5p_fonte`
3. `penalidade_cliff_idade`
4. `oportunidade_vpl_marginal`
5. penalidades estratégicas e de liquidez já existentes
## Efeito esperado
- menor resgate de lote aportado próximo de cliff ruim;
- melhor distinção entre cobertura local e cobertura economicamente correta;
- menor uso cosmético de combinação mínima.
```

</details>

### `relatorios/historico/contratos_intermediarios/BASELINE_FIXA_V139.md`

- Título: Baseline fixa V139
- Linhas originais: 9
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V139
A V139 é a baseline de reorganização estrutural de baixo risco derivada da V138.
## Escopo
- limpeza de `relatorios/atuais`;
- separação entre documentação vigente e histórica;
- reorganização da trilha de saídas em `oficial/`, `diagnostico/` e `historico/`;
- preparação da base para a absorção futura dos modelos do Script 1 na camada de pagamentos.
```

</details>

### `relatorios/historico/contratos_intermediarios/BASELINE_FIXA_V141.md`

- Título: Baseline fixa V141
- Linhas originais: 8
- Referências externas detectadas: 1

<details>
<summary>Referências externas detectadas</summary>

```text
scripts/diagnostico/verificar_release_baseline.py:53:        'BASELINE_FIXA_V141.md',
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V141
A V141 mantém a V140 como baseline contratual da absorção dos modelos do Script 1 na camada de pagamentos e implementa a **Fase 1** no `alocador_pagamentos_terminal_v1`.
Nesta etapa:
- não há expansão do bloco real de pagamentos;
- não há reabertura da auditoria ampla de switching;
- o foco é incorporar H1–H3 como score auxiliar e desempate econômico por fonte.
```

</details>

### `relatorios/historico/contratos_intermediarios/COMPARADOR_HIBRIDO_SWITCHING_V132.md`

- Título: Comparador híbrido de switching — V132
- Linhas originais: 52
- Referências externas detectadas: 12

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:610:scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:694:scripts/historico_raiz/inspecionar_comparador_hibrido_switching_v132.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:753:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_comparador_hibrido_switching_v132.py
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:29:scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py,LEGADO_BLOQUEADO_V203,mantido como bloqueio da V203
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:109:scripts/historico_raiz/inspecionar_comparador_hibrido_switching_v132.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:167:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_comparador_hibrido_switching_v132.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:18:scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py,BLOQUEADO_COM_STUB,DIAGNOSTICO_LEGADO_COM_SAIDA_PROPRIA,nao,nao_executa,scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_comparador_hibrido_switching_v132.py,Execução bloqueada por governança; saída própria não pode competir com console/planilha canônicos.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:109:scripts/historico_raiz/inspecionar_comparador_hibrido_switching_v132.py,HISTORICO_READ_ONLY,,nao,nao,,Acervo histórico preservado sem autoridade operacional.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:167:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_comparador_hibrido_switching_v132.py,HISTORICO_ORIGINAL_PRESERVADO,,nao,nao,,Original preservado de script bloqueado; acervo histórico.
relatorios/atuais/MAPA_SCRIPTS_V201.md:58:| `inspecionar_comparador_hibrido_switching_v132.py` | 2 |
relatorios/atuais/MAPA_SCRIPTS_V201.md:167:| `scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 172 |
relatorios/atuais/MAPA_SCRIPTS_V201.md:247:| `scripts/historico_raiz/inspecionar_comparador_hibrido_switching_v132.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Comparador híbrido de switching — V132
## Objetivo
Classificar cada cenário diário como `vencedor operacional`, `vencedor terminal`, `vencedor híbrido aceitável` ou `dominado pelo baseline`, bloqueando a promoção automática de switchings que piorem patrimônio líquido terminal frente ao baseline.
## Contagem agregada das classes
- vencedor_operacional: 186
- vencedor_terminal: 25
- vencedor_hibrido_aceitavel: 0
- dominado_pelo_baseline: 171
- cenários bloqueados para promoção automática: 357
- dias em que o vencedor lexicográfico foi bloqueado: 21
- dias com promoção híbrida diferente do vencedor lexicográfico: 5
## Leitura principal
- `vencedor_operacional`: melhora a métrica central atual, mas piora materialmente o patrimônio terminal frente ao baseline; deve ficar bloqueado para promoção automática.
- `vencedor_terminal`: melhora materialmente o patrimônio terminal sem piora operacional material; é o candidato preferencial para promoção.
- `vencedor_hibrido_aceitavel`: vence ou permanece competitivo sem piora terminal material; é aceitável quando não existir vencedor terminal superior.
## Resumo diário
| Data | Vencedor lexicográfico | Classe | Bloqueado | Promoção híbrida | Classe promoção | Δ perda terminal promoção | Δ déficit promoção | Δ patrimônio promoção |
|---|---|---|---|---|---|---:|---:|---:|
| 2026-04-30 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -234.56 | -450.12 | 2167.56 |
| 2026-05-01 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -228.79 | -450.12 | 2156.02 |
| 2026-05-02 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -223.02 | -450.12 | 2144.48 |
| 2026-05-03 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -217.25 | -450.12 | 2132.94 |
```

</details>

### `relatorios/historico/contratos_intermediarios/CONTRATO_ABSORCAO_MODELOS_SCRIPT1_PAGAMENTOS_V140.md`

- Título: Contrato de absorção dos modelos do Script 1 na camada de pagamentos — V140
- Linhas originais: 168
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato de absorção dos modelos do Script 1 na camada de pagamentos — V140
## Objetivo
Formalizar quais partes do Script 1 entram primeiro no `alocador_pagamentos_terminal_v1` para melhorar a alocação de pagamentos com foco em **patrimônio líquido terminal**, sem reabrir o repositório ao acoplamento do legado inteiro.
## Escopo desta etapa
Esta etapa **não** implementa ainda os modelos do Script 1 dentro do fluxo oficial amplo.
Ela define:
- quais heurísticas entram primeiro;
- qual o papel de cada heurística;
- quais entradas e saídas elas devem consumir;
- o que fica fora do escopo imediato;
- como essas heurísticas serão absorvidas sem substituir a arquitetura canônica já validada.
## Princípio de absorção
O Script 1 não será migrado como bloco monolítico.
A absorção será:
1. **seletiva**;
2. **modular**;
3. **subordinada ao estado canônico atual**;
4. **orientada a patrimônio líquido terminal**;
5. **compatível com o switching já filtrado pelo comparador híbrido**.
## Camada alvo
A absorção deve ocorrer em:
- `nucleo/pagamentos/modelos_script1/`
```

</details>

### `relatorios/historico/contratos_intermediarios/CONTRATO_RANKING_CARTEIRA_V123.md`

- Título: Contrato operacional do ranking Carteira-only — V123
- Linhas originais: 17
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato operacional do ranking Carteira-only — V123
## Objetivo
Integrar ao projeto principal o método estabilizado de score/ranking da aba `Carteira`, sem mutar a planilha-fonte e sem reabrir a metodologia congelada.
## Escopo da V123
- entrada oficial: somente a aba `Carteira`;
- fonte contratual: `config/carteira_contract_v123.json`;
- parâmetros fixos: `config/fixed_parameters_ranking_carteira.json`;
- artefatos separados: ranking completo, top 30, destinos de switching e resumo de validação.
## Decisão de integração
O projeto passa a usar o ranking Carteira-only como fonte preferencial de destinos do `planejador_switching_temporal_v1`. A `triagem_motor` permanece como fallback e camada proxy, não como ranking principal de produtos.
## Implementação mínima desta versão
Nesta etapa, o núcleo do cálculo do ranking canônico é lido da própria aba `Carteira` já estabilizada e a penalização adicional de prazo no consolidado é recalculada internamente para produzir `SAOF_Final_Prazo`, `Rank_Consolidado_Prazo_Ativos` e `Delta_Rank`.
```

</details>

### `relatorios/historico/contratos_intermediarios/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`

- Título: Contrato-alvo V117 — `alocador_pagamentos_terminal_v1` + `planejador_switching_temporal_v1`
- Linhas originais: 203
- Referências externas detectadas: 1

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/RELATORIO_CONSOLIDADO_OBJETIVO_FINAL_HISTORICO.md:132:- `relatorios/atuais/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato-alvo V117 — `alocador_pagamentos_terminal_v1` + `planejador_switching_temporal_v1`
## 1. Status da V117
1. A V117 é uma **camada contratual/de desenho arquitetural** da próxima etapa central do projeto.
2. Ela **não** substitui a V108 como baseline central executável.
3. Ela **não** promove a V116 a motor final.
4. A V117 existe para congelar a interface mínima da próxima implementação, evitando que a frente central volte a derivar para recomendações locais por conta sem integração ao objetivo terminal.
---
## 2. Pergunta central que a V117 precisa responder
> Em cada data relevante da timeline, qual combinação de decisões entre manter, aportar, switchar, resgatar lote aportado, usar lote não aportado, usar saldo disponível ou combinar fontes preserva melhor o patrimônio líquido terminal do cenário, respeitando cobertura, liquidez, carência, tributação e governança operacional?
---
## 3. Princípio de modelagem
5. O projeto deixa de ser orientado exclusivamente por evento de pagamento e passa a ser orientado por **timeline global de eventos relevantes**.
6. O switching passa a ser tratado como **decisão temporal autônoma**, escolhida na melhor data econômica viável e não subordinada apenas ao vencimento da conta.
7. O pagamento passa a ser tratado como **decisão de financiamento da obrigação**, comparando fontes alternativas pela perda de patrimônio líquido terminal.
8. As duas decisões continuam acopladas e devem operar sobre o mesmo estado global do sistema.
---
## 4. Núcleos mínimos da V117
### 4.1 `planejador_switching_temporal_v1`
9. O `planejador_switching_temporal_v1` deve gerar, para cada lote elegível, um conjunto pequeno e auditável de transições candidatas no tempo.
10. Cada transição candidata deve especificar, no mínimo:
   - lote_origem;
   - tipo_origem (`aportado` ou `nao_aportado`);
```

</details>

### `relatorios/historico/contratos_intermediarios/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`

- Título: Contrato V117 — motor conjunto temporal
- Linhas originais: 123
- Referências externas detectadas: 1

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/RELATORIO_CONSOLIDADO_OBJETIVO_FINAL_HISTORICO.md:131:- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato V117 — motor conjunto temporal
## Objetivo da V117
A V117 introduz uma camada **documental/técnica mínima e executável** para o futuro motor conjunto temporal do projeto.
Esta versão **não** substitui a baseline central V108 e **não** promove a camada operacional por conta como motor final. O papel da V117 é formalizar os contratos mínimos de quatro módulos centrais:
- `planejador_switching_temporal_v1`
- `alocador_pagamentos_terminal_v1`
- `simulador_central_eventos_v1`
- `avaliador_cenarios_conjuntos_v1`
## Princípio metodológico
A V117 fixa que:
1. o switching é uma decisão **temporal autônoma**, não subordinada ao vencimento da conta;
2. a fonte de pagamento deve ser escolhida pelo **menor custo de oportunidade terminal**;
3. pagamentos, recebidos, aportes e switching devem operar sobre o **mesmo estado global auditável**;
4. a decisão correta não é a de menor custo local, e sim a de **menor perda de patrimônio líquido terminal** sob restrições operacionais.
## Estado global mínimo compartilhado
Os quatro módulos da V117 devem aceitar ou produzir estruturas compatíveis com um mesmo estado global, contendo no mínimo:
- `data_referencia`
- `data_evento_corrente`
- `saldo_disponivel_geral`
- `recebidos_nao_aportados_disponiveis`
- `recebidos_futuros`
- `lotes_aportados`
```

</details>

### `relatorios/historico/contratos_intermediarios/ESTRUTURA_REPOSITORIO_V139.md`

- Título: Estrutura do repositório — V139
- Linhas originais: 12
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório — V139
## Ajuste desta etapa
A V139 não altera ainda a localização dos módulos de negócio em `nucleo/`. Ela reorganiza primeiro a superfície documental e a trilha de saídas para reduzir ruído operacional antes da absorção dos modelos do Script 1.
## Trilhas vigentes após a V139
- `relatorios/atuais/` → apenas documentação realmente vigente
- `relatorios/historico/` → trilha histórica organizada
- `saidas/oficial/` → saídas operacionais correntes
- `saidas/diagnostico/` → artefatos técnicos intermediários
- `saidas/historico/` → artefatos antigos preservados
- `saidas/operacional/` → compatibilidade temporária
```

</details>

### `relatorios/historico/contratos_intermediarios/ESTRUTURA_REPOSITORIO_V141.md`

- Título: Estrutura do repositório — V141
- Linhas originais: 11
- Referências externas detectadas: 1

<details>
<summary>Referências externas detectadas</summary>

```text
scripts/diagnostico/verificar_release_baseline.py:55:        'ESTRUTURA_REPOSITORIO_V141.md',
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório — V141
A V141 mantém a reorganização da V139/V140 e adiciona a implementação funcional da Fase 1 em:
- `nucleo/pagamentos/modelos_script1/heuristicas_fase1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py`
Objetivo estrutural:
- permitir que o `alocador_pagamentos_terminal_v1` use H1–H3 sem acoplamento monolítico ao Script 1 legado;
- manter o switching subordinado ao comparador híbrido;
- preparar a próxima integração em recorte real ampliado.
```

</details>

### `relatorios/historico/contratos_intermediarios/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`

- Título: Frente F1 — contrato mínimo de caixa/recebidos auditáveis
- Linhas originais: 178
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Frente F1 — contrato mínimo de caixa/recebidos auditáveis
## Escopo desta etapa
A Etapa 8 da F1 preserva o **contrato mínimo canônico** da nova camada de caixa/recebidos auditáveis e mantém a quarta estrutura real materializada: `decisao_local_v1` escolhe, por pagamento, uma fonte prioritária observável sobre a matriz temporal completa (`fonte_elegivel_pagamento` + `saldo_disponivel_geral`) usando um `proxy econômico v3` auditável. Nesta etapa, o projeto **não** altera o motor financeiro, **não** abre solver ou switching e **não** integra ainda a decisão ao fluxo principal do console ou da planilha operacional.
## Objetivo
Criar uma base formal, estável e auditável para que as próximas etapas possam materializar:
- fontes elegíveis de pagamento por data e por pagamento;
- saldo disponível geral por pagamento sem duplicar as fontes explícitas já observáveis;
- recebidos auditáveis com destino explícito e vínculo histórico observável;
- decisão local v1 entre saldo disponível, caixa pré-aplicação, recebidos e resgate.
## Estruturas mínimas abertas nesta etapa
### 1. `fonte_elegivel_pagamento`
Representa qualquer fonte economicamente elegível para financiar um pagamento em uma data específica.
Campos mínimos:
- `fonte_pagamento_id`
- `fonte_id`
- `pagamento_id`
- `data_pagamento`
- `tipo_fonte`
- `data_evento`
- `lote_id`
- `recebido_id`
- `produto_key`
```

</details>

### `relatorios/historico/contratos_intermediarios/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLO_V142.md`

- Título: FLUXO PAGAMENTOS TERMINAL RECORTE AMPLO V142
- Linhas originais: 57
- Referências externas detectadas: 14

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md:27:- moved: `saidas/oficial/fluxo_pagamentos_terminal_recorte_amplo_v142.json` → `saidas/historico/compatibilidade_operacional/fluxo_pagamentos_terminal_recorte_amplo_v142.json`
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:64:nucleo/fluxo_pagamentos_terminal_recorte_amplo_v142.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:619:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:703:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:758:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:38:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,LEGADO_BLOQUEADO_V203,mantido como bloqueio da V203
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:118:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:172:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:23:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,BLOQUEADO_COM_STUB,DIAGNOSTICO_LEGADO_COM_SAIDA_PROPRIA,nao,nao_executa,scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,Execução bloqueada por governança; saída própria não pode competir com console/planilha canônicos.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:118:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,HISTORICO_READ_ONLY,,nao,nao,,Acervo histórico preservado sem autoridade operacional.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:172:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py,HISTORICO_ORIGINAL_PRESERVADO,,nao,nao,,Original preservado de script bloqueado; acervo histórico.
relatorios/atuais/MAPA_SCRIPTS_V201.md:67:| `inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py` | 2 |
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# FLUXO PAGAMENTOS TERMINAL RECORTE AMPLO V142
- Objetivo: expandir a integração do `alocador_pagamentos_terminal_v1` para um recorte real maior de pagamentos e medir, em fluxo completo, como H1–H3 alteram as escolhas entre `lote_aportado`, `lote_nao_aportado`, `combinacao_minima_fontes` e `cenario_switching_elegivel`.
- Baseline de origem: `V141`.
- Observação operacional: a auditoria comparativa V142 usou teto controlado de candidatos de switching por data para manter o recorte maior executável sem alterar o contrato central do alocador.
## Resumo do recorte
- intervalo: `2026-04-21` → `2026-06-10`
- pagamentos avaliados: **20**
- dias com pagamento: **13**
## Fluxo com H1–H3 ativas
- patrimônio líquido terminal proxy: **R$ 29933.35**
- perda terminal agregada: **R$ 0.00**
- custo fiscal imediato total: **R$ 65.79**
- custo operacional total: **20.00**
- switching efetivamente escolhido: **7** pagamentos
## Fluxo com H1–H3 neutralizadas
- patrimônio líquido terminal proxy: **R$ 29933.35**
- perda terminal agregada: **R$ 0.00**
- custo fiscal imediato total: **R$ 76.57**
- custo operacional total: **23.00**
- switching efetivamente escolhido: **7** pagamentos
## Efeito agregado de H1–H3 no fluxo completo
- Δ patrimônio líquido terminal proxy: **R$ 0.00**
```

</details>

### `relatorios/historico/contratos_intermediarios/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md`

- Título: FLUXO PAGAMENTOS TERMINAL RECORTE CURTO V138
- Linhas originais: 46
- Referências externas detectadas: 14

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md:25:- moved: `saidas/oficial/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md` → `saidas/historico/compatibilidade_operacional/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138_origem_oficial_1.md`
relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md:26:- moved: `saidas/oficial/fluxo_pagamentos_terminal_recorte_curto_v138.json` → `saidas/historico/compatibilidade_operacional/fluxo_pagamentos_terminal_recorte_curto_v138_origem_oficial_1.json`
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:620:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:704:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:759:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:39:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,LEGADO_BLOQUEADO_V203,mantido como bloqueio da V203
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:119:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_FINAL_SCRIPTS_V204.csv:173:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,HISTORICO_BLOQUEADO_V204,bloqueado; sem autoridade operacional
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:24:scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,BLOQUEADO_COM_STUB,DIAGNOSTICO_LEGADO_COM_SAIDA_PROPRIA,nao,nao_executa,scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,Execução bloqueada por governança; saída própria não pode competir com console/planilha canônicos.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:119:scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,HISTORICO_READ_ONLY,,nao,nao,,Acervo histórico preservado sem autoridade operacional.
relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv:173:scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py,HISTORICO_ORIGINAL_PRESERVADO,,nao,nao,,Original preservado de script bloqueado; acervo histórico.
relatorios/atuais/MAPA_SCRIPTS_V201.md:68:| `inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py` | 2 |
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# FLUXO PAGAMENTOS TERMINAL RECORTE CURTO V138
- Objetivo: integrar o `alocador_pagamentos_terminal_v1` ao fluxo oficial de um recorte curto real de pagamentos e validar, em dados do projeto, quando ele escolhe saldo disponível, lote não aportado, lote aportado ou cenário com switching elegível.
## Resumo do recorte
- intervalo: `2026-04-21` → `2026-05-21`
- pagamentos avaliados: **13**
- dias com pagamento: **9**
- pagamentos com switching elegível promovível disponível: **4**
- pagamentos que efetivamente escolheram switching: **2**
- pagamentos cobertos integralmente: **13**
- déficit total do recorte: **R$ 0.00**
## Contagem por fonte escolhida
- `cenario_switching_elegivel`: **2**
- `combinacao_minima_fontes`: **3**
- `lote_aportado`: **6**
- `lote_nao_aportado`: **2**
## Leitura técnica
- O fluxo já está usando o alocador em dados reais do projeto, comparando fontes contratuais de pagamento e cenário com switching elegível filtrado pelo comparador híbrido.
- Esta validação ainda é de recorte curto e integração funcional; ela não fecha o modelo final de pagamentos, mas já mostra quais fontes dominam no estado real da baseline.
## Exemplos auditados
- `2026-04-29` | `despesa_auto_00069` | `combinacao_minima_fontes` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-04` | `despesa_auto_00070` | `lote_nao_aportado` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-06` | `despesa_auto_00072` | `lote_nao_aportado` | cobertura `True` | déficit `R$ 0.00`
```

</details>

### `relatorios/historico/contratos_intermediarios/GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md`

- Título: Grade diária oficial com comparador híbrido — V134
- Linhas originais: 116
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Grade diária oficial com comparador híbrido — V134
- Objetivo: expandir o fluxo oficial híbrido além de 2026-05-20, promovendo apenas `vencedor_terminal`, `vencedor_hibrido_aceitavel` ou `baseline_sem_switching` no horizonte ampliado.
- Dias auditados: 90
- Resultados avaliados: 66
- Dias com vencedor lexicográfico bloqueado: 13
- Dias promovidos com switching: 0
- Dias promovidos com baseline: 90
- Dias em que a promoção oficial diferiu do vencedor lexicográfico: 0
## Contagem das classes oficiais promovidas
- nenhum switching promovido oficialmente
## Melhor cenário oficial por dia
| Data | Vencedor lexicográfico | Classe lex | Bloqueado | Melhor cenário oficial | Classe oficial | Origem | Δ perda terminal | Δ déficit | Δ patrimônio proxy |
|---|---|---|---|---|---|---|---:|---:|---:|
| 2026-05-21 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-22 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-23 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-24 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-25 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-26 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-27 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-28 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-29 | Lote 8500 mar. -> Combo PicPay 100-120 3m | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
```

</details>

### `relatorios/historico/contratos_intermediarios/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`

- Título: Mapa de absorção legado — Scripts 1 e 2
- Linhas originais: 85
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Mapa de absorção legado — Scripts 1 e 2
## Escopo
Este documento classifica os blocos relevantes de `Script 1.txt` e `Script 2.txt` em quatro grupos:
- **migrar já**;
- **migrar depois**;
- **não migrar**;
- **substituída pela baseline atual**.
> Correção de identidade vigente: o arquivo que havia sido tratado anteriormente como “Script 2” corresponde, na verdade, ao **Script 1**. O `Script 2.txt` correto passa a ser o runner legado de **switching + simulação futura + exportação final**.
A V92 usa este mapa como referência obrigatória antes de qualquer nova migração funcional do legado.
## Script 1 — otimização, validação e competição entre estratégias
### Migrar já
- `resolver_hibrido_5p(...)`
  - motivo: contém regra de decisão econômica ainda ausente na baseline atual, com pesos para IOF, IR, idade, liquidez, cliff e VPL.
  - forma recomendada de absorção: primeiro em modo **benchmark/diagnóstico shadow**, sem acoplamento direto ao fluxo principal.
- benchmark shadow do teste **agrupado vs. individual**
  - motivo: faz parte da governança da execução principal do Script 1 e já foi aberto como benchmark shadow, mantendo o modo `individual` como recomendação vigente.
### Migrar depois
- `carregar_parametros_hibrido_5p(...)`
- `carregar_parametros_hibrido_5p_passado(...)`
- `_escolher_modo_treino_por_objetivo(...)`
- `validacao_walk_forward(...)`
- competição final entre estratégias legadas em modo shadow
```

</details>

### `relatorios/historico/contratos_intermediarios/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md`

- Título: Mapa das heurísticas prioritárias do Script 1 para pagamentos — V140
- Linhas originais: 36
- Referências externas detectadas: 1

<details>
<summary>Referências externas detectadas</summary>

```text
relatorios/atuais/RELATORIO_CONSOLIDADO_OBJETIVO_FINAL_HISTORICO.md:133:- `relatorios/atuais/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md`
```

</details>

<details>
<summary>Trecho inicial preservado</summary>

```text
# Mapa das heurísticas prioritárias do Script 1 para pagamentos — V140
## Resumo executivo
A absorção do Script 1 deve começar por heurísticas que alteram a **qualidade da escolha da fonte de pagamento**, e não por blocos de treino, exportação ou solver completo.
## Heurísticas prioritárias
| Ordem | Heurística | Status V140 | Papel inicial no alocador |
|---|---|---:|---|
| 1 | `score_hibrido_5p_fonte` | contratada | score auxiliar por fonte |
| 2 | `penalidade_cliff_idade` | contratada | desempate tributário/fiscal |
| 3 | `oportunidade_vpl_marginal` | contratada | reforço terminal marginal |
| 4 | `seletor_modo_individual_ou_combinado` | contratada para fase 2 | decidir quando abrir combinação mínima |
| 5 | `triagem_topk_fontes_combinacao` | contratada para fase 2 | reduzir custo combinatório |
## O que entra primeiro no fluxo
### Bloco A — ranqueamento econômico das fontes
Usa H1 + H2 + H3 para produzir um score econômico auxiliar de cada fonte elegível.
### Bloco B — decisão local entre fontes simples
Usa o score auxiliar para priorizar:
- `saldo_disponivel`
- `lote_nao_aportado`
- `lote_aportado`
- `cenario_switching_elegivel`
### Bloco C — abertura controlada de combinação mínima
Só depois de H1–H3 estarem estáveis.
```

</details>

### `relatorios/historico/contratos_intermediarios/METRICA_CANONICA_MINIMA_CENTRAL.md`

- Título: Métrica canônica mínima central
- Linhas originais: 95
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Métrica canônica mínima central
Este documento formaliza a métrica mínima que deverá governar a futura `recomputacao_sequencial_central_v1`.
## Finalidade
A métrica canônica mínima central existe para impedir que o projeto volte a ser guiado por ganhos locais isolados — por exemplo, melhora de uma âncora específica — sem conexão explícita com o resultado conjunto do cenário.
## Princípio
A métrica central deve responder à pergunta:
> entre dois cenários auditáveis de pagamentos e uso de lotes, qual preserva melhor o objetivo econômico terminal do projeto, respeitando governança operacional mínima?
## Comparador hierárquico mínimo
Até nova decisão explícita, a comparação entre cenários deve seguir esta ordem de prioridade:
1. **Violações de pagamentos `PROTEGIDA`**
2. **Déficit líquido total dos pagamentos**
3. **Número de pagamentos sem cobertura integral**
4. **Patrimônio líquido terminal proxy do cenário**
5. **Destruição estratégica de lotes relevantes**
6. **Fragmentação residual e deterioração evitável da liquidez futura**
## Forma recomendada de implementação
### Comparador lexicográfico
A forma mínima recomendada é um comparador lexicográfico auditável:
\[
M_{central}(c) =
(
V_p,
```

</details>

### `relatorios/historico/contratos_intermediarios/MOTOR_DIARIO_CONJUNTO_EXPERIMENTAL_V143_2026-04-21_2026-05-06.md`

- Título: Motor diário conjunto experimental V143
- Linhas originais: 68
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Motor diário conjunto experimental V143
## Janela auditada
- Início: 2026-04-21
- Fim: 2026-05-06
- Limite de candidatos de switching por data: 24
- Cap de fontes por destino: 5
## Objetivo
Implementar um motor diário conjunto experimental tratando o dia como unidade de decisão e comparando, quando houver pagamento, `pay_only` versus `switch_then_pay`; e, quando não houver pagamento, `no_action` versus `switch_only`, sempre com foco em patrimônio líquido terminal proxy sob continuação neutra até o fim da janela.
## Resumo executivo
- Dias no horizonte: 16
- Dias com pagamento: 3
- Pagamentos no horizonte: 4
- Decisões `pay_only`: 3
- Decisões `switch_then_pay`: 0
- Decisões `no_action`: 13
- Decisões `switch_only`: 0
- Patrimônio líquido terminal proxy final: R$ 29586.91
- Fontes de pagamento escolhidas: {'combinacao_minima_fontes': 4}
## Leitura principal
- Nesta janela, nenhuma decisão diária promoveu `switch_then_pay` ou `switch_only`.
- O motor escolheu `pay_only` nos 3 dias com pagamento e `no_action` nos demais dias.
- Todos os 4 pagamentos foram cobertos por `combinacao_minima_fontes`, sem déficit e sem violação de pagamentos protegidos.
```

</details>

### `relatorios/historico/contratos_intermediarios/MOTOR_DIARIO_CONJUNTO_POS_VENCIMENTO_V146_2026-05-03_2026-05-06.md`

- Título: Auditoria do motor diário com normalização pós-vencimento — V146
- Linhas originais: 71
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria do motor diário com normalização pós-vencimento — V146
Janela: **2026-05-03** a **2026-05-06**.
## O que foi implementado
- inclusão de `prazo_dias_atual`, `regime_liquidez_atual` e `data_vencimento` na construção do estado dos lotes;
- normalização diária pós-vencimento no simulador e no motor diário, convertendo lote vencido em caixa líquido disponível segundo `politicas.pos_vencimento`;
- aplicação da normalização antes do planner diário, antes da execução do pacote do dia e dentro do simulador temporal.
## Resumo do motor corrigido
- decisões `pay_only`: **2**
- decisões `switch_then_pay`: **0**
- decisões `switch_only`: **0**
- decisões `no_action`: **2**
- pagamentos no horizonte: **3**
- patrimônio líquido terminal proxy final: **R$ 37.136,83**
- fontes finais de pagamento: **3 pagamentos por `combinacao_minima_fontes`**
## Decisões diárias do motor corrigido
### 2026-05-03
- pacote vencedor: **no_action**
- evento estrutural do dia: ativação de `Lote 7000 mai.`
- normalização pós-vencimento detectada: `Lote 6630,64 fev.` convertido para caixa disponível (**R$ 0,21**)
### 2026-05-04
- pacote vencedor: **pay_only**
- pagamentos do dia: **1** (`despesa_auto_00070`)
```

</details>

### `relatorios/historico/contratos_intermediarios/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`

- Título: Recomputação sequencial central V108
- Linhas originais: 19
- Referências externas detectadas: 0

<details>
<summary>Trecho inicial preservado</summary>

```text
# Recomputação sequencial central V108
A V108 recalibra a `recomputacao_sequencial_central_v1` da V107 com três mudanças estruturais mínimas na frente central:
1. penalidade explícita de escassez futura para pagamentos `PROTEGIDA`;
2. prioridade intraclasse operacional no mesmo dia;
3. fallback auditável de **sem fonte viável**.
## Objetivo da V108
Reduzir violações de `PROTEGIDA` e tornar a frente central mais fiel à métrica canônica mínima central, sem reabrir o solver global completo e sem voltar a uma lógica de otimização local do bloco crítico.
## Resultado esperado
A V108 deve ser lida como calibração da frente central, com foco em:
- preservar liquidez útil para `PROTEGIDA` futura;
- melhorar a ordenação de pagamentos protegidos no mesmo dia;
- evitar saídas enganosas quando não há mais fonte economicamente viável.
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/contratos_intermediarios/` pode ser removida se a validação local confirmar que os documentos granulares não possuem autoridade normativa ativa superior aos documentos atuais em `relatorios/atuais/`.
