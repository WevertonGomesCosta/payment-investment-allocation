# Relatório consolidado — estruturas históricas V121–V150

## Objetivo

Consolidar a faixa `V121_V150` das estruturas históricas do repositório, preservando a evolução do planejador temporal, ranking Carteira-only, simulação central, grade diária de switching, comparador híbrido, alocador terminal, fluxo de pagamentos terminal e preparação dos modelos do Script 1, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 20
- Faixa: V121–V150
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das estruturas

| Versão | Tipo | Linhas | Título |
|---:|---|---:|---|
| V121 | `estrutura_repositorio` | 20 | Estrutura repositório V121 |
| V122 | `estrutura_repositorio` | 18 | Estrutura repositório V122 |
| V123 | `estrutura_repositorio` | 3 | Estrutura V123 |
| V124 | `estrutura_repositorio` | 9 | Estrutura V124 |
| V125 | `estrutura_repositorio` | 7 | Estrutura V125 |
| V126 | `estrutura_repositorio` | 11 | Estrutura do repositório V126 |
| V127 | `estrutura_repositorio` | 8 | Estrutura do repositório V127 |
| V128 | `estrutura_repositorio` | 8 | Estrutura do repositório V128 |
| V129 | `estrutura_repositorio` | 3 | Estrutura do repositório V129 |
| V130 | `estrutura_repositorio` | 3 | Estrutura do repositório V130 |
| V131 | `estrutura_repositorio` | 9 | Estrutura do repositório — V131 |
| V132 | `estrutura_repositorio` | 10 | Estrutura do repositório V132 |
| V133 | `estrutura_repositorio` | 7 | Estrutura do repositório V133 |
| V134 | `estrutura_repositorio` | 3 | Estrutura do repositório V134 |
| V135 | `estrutura_repositorio` | 8 | Estrutura do repositório V135 |
| V136 | `estrutura_repositorio` | 9 | Estrutura do repositório V136 |
| V137 | `estrutura_repositorio` | 11 | ESTRUTURA REPOSITÓRIO V137 |
| V138 | `estrutura_repositorio` | 6 | ESTRUTURA REPOSITORIO V138 |
| V139 | `subpasta_etapa_modelos_script1` | 21 | Preparação para absorção dos modelos do Script 1 — V139 |
| V140 | `estrutura_repositorio` | 14 | Estrutura do repositório — V140 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Planejador temporal | Estruturas de switching temporal, multidestino e multihorizonte foram preservadas. |
| Ranking e simulação | Ranking Carteira-only e simulação central controlada foram consolidados. |
| Grade diária e comparador híbrido | Avaliações diárias, parametrização e comparador híbrido foram preservados. |
| Alocador terminal | Estruturas do alocador e fluxo de pagamentos terminal foram registradas. |
| Script 1 | Preparação estrutural para absorção dos modelos do Script 1 foi preservada. |

## Detalhe por estrutura

### V121 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V121.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 20
- Título: Estrutura repositório V121

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V121
## Arquivos centrais alterados na V121
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/simulador_central_eventos_v1.py`
- `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `scripts/inspecionar_integracao_funcional_minima_v117.py`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `README.md`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/BASELINE_FIXA_V121.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V121.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V121.md`
- `relatorios/atuais/EXPANSAO_MULTIDESTINO_PLANEJADOR_SWITCHING_TEMPORAL_V121.md`
## Síntese estrutural
A V121 preserva a integração curta existente, mantém a triagem econômica mínima da V120 e expande o `planejador_switching_temporal_v1` para múltiplos destinos elegíveis por lote antes da simulação central.
```

</details>

### V122 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V122.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 18
- Título: Estrutura repositório V122

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V122
## Arquivos centrais alterados na V122
- `README.md`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`
- `scripts/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/BASELINE_FIXA_V122.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V122.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V122.md`
- `relatorios/atuais/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md`
## Resumo estrutural
A V122 não muda a fórmula do planejador. Ela adiciona uma camada diagnóstica multihorizonte para testar se a sobrevivência econômica do switching depende da janela temporal usada no ranking.
```

</details>

### V123 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V123.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 3
- Título: Estrutura V123

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura V123
Adicionados `config/`, `nucleo/ranking_carteira_estabilizado.py` e scripts diagnósticos do ranking Carteira-only.
```

</details>

### V124 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V124.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura V124

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura V124
Arquivos centrais adicionados nesta derivação:
- `scripts/diagnostico/inspecionar_simulacao_central_controlada_horizonte_longo_v124.py`
- `scripts/inspecionar_simulacao_central_controlada_horizonte_longo_v124.py`
- `relatorios/atuais/SIMULACAO_CENTRAL_CONTROLADA_HORIZONTE_LONGO_V124.md`
A V124 não altera o ranking Carteira-only nem o comparador do planejador. Ela adiciona a rerodagem da simulação central controlada em horizontes mais longos para testar se os candidatos positivos do planejador continuam vencedores quando entram no cenário conjunto com pagamentos.
```

</details>

### V125 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V125.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 7
- Título: Estrutura V125

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura V125
Arquivos centrais adicionados nesta derivação:
- `relatorios/atuais/AUDITORIA_MULTIHORIZONTE_CENARIOS_TEMPO_V125.md`
A V125 não altera o ranking Carteira-only nem o simulador central. Ela amplia a auditoria do cenário conjunto para uma grade multihorizonte mais rica, reduzindo o risco de inferir política de switching a partir de poucos recortes de tempo.
```

</details>

### V126 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V126.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 11
- Título: Estrutura do repositório V126

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V126
Adições centrais:
- `scripts/diagnostico/inspecionar_grade_diaria_switching_v126.py`
- `scripts/diagnostico/consolidar_grade_diaria_switching_v126.py`
- `scripts/inspecionar_grade_diaria_switching_v126.py`
- `scripts/consolidar_grade_diaria_switching_v126.py`
- `relatorios/atuais/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V126.md`
Mudanças centrais:
- `nucleo/simulador_central_eventos_v1.py` agora suporta switching parcial por fração do lote, preservando o saldo remanescente e criando novo lote migrado.
```

</details>

### V127 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V127.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 8
- Título: Estrutura do repositório V127

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V127
Mudanças centrais da V127:
- `nucleo/planejador_switching_temporal_v1.py`: inclui fontes não aportadas disponíveis e mantém apenas ações integrais;
- `nucleo/simulador_central_eventos_v1.py`: suporta aporte de não aportado como evento temporal integral;
- `scripts/diagnostico/inspecionar_grade_diaria_switching_v127.py`: avalia grade diária integral individual e agrupada com todas as combinações entre as melhores fontes do dia;
- `scripts/diagnostico/consolidar_grade_diaria_switching_v127.py`: consolida blocos da grade diária.
```

</details>

### V128 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V128.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 8
- Título: Estrutura do repositório V128

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V128
Mudanças centrais da V128:
- continuação dos chunks da grade diária integral `V127` até 120 dias auditados;
- criação de `scripts/diagnostico/consolidar_grade_diaria_switching_v128.py` para consolidar a janela ampliada com dias sem cenários;
- criação de `relatorios/atuais/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V128.md`;
- criação de `saidas/operacional/grade_diaria_switching_v128_consolidado.json`.
```

</details>

### V129 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V129.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 3
- Título: Estrutura do repositório V129

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V129
A V129 adiciona a auditoria `AUDITORIA_PARAMETROS_PRODUTOS_SWITCHING_V129.md` e propaga metadados de aplicação mínima/máxima do ranking Carteira-only para o fluxo temporal.
```

</details>

### V130 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V130.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 3
- Título: Estrutura do repositório V130

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V130
A V130 adiciona os diagnósticos `inspecionar_grade_diaria_parametrizada_v130.py` e `consolidar_grade_diaria_parametrizada_v130.py`, além do relatório `AVALIACAO_DIARIA_PARAMETRIZADA_JANELA_V130.md`.
```

</details>

### V131 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V131.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório — V131

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório — V131
A V131 adiciona:
- `relatorios/atuais/AUDITORIA_CIRURGICA_BLOCO_8500_PICPAY_V131.md`
- `scripts/diagnostico/inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py`
- `saidas/operacional/auditoria_cirurgica_bloco_8500_picpay_v131.json`
Sem alterar a lógica central de cálculo da V130.
```

</details>

### V132 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V132.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 10
- Título: Estrutura do repositório V132

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V132
Novos artefatos principais:
- `nucleo/comparador_hibrido_switching_v1.py`
- `scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py`
- `relatorios/atuais/COMPARADOR_HIBRIDO_SWITCHING_V132.md`
- `saidas/operacional/comparador_hibrido_switching_v132.json`
A V132 não reabre ranking nem planejador; ela recalibra a camada de promoção/aceite dos cenários diários.
```

</details>

### V133 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V133.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 7
- Título: Estrutura do repositório V133

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V133
Arquivos novos principais:
- `nucleo/comparador_hibrido_switching_v1.py` já existente e agora integrado ao fluxo oficial;
- `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v133.py`;
- `scripts/diagnostico/consolidar_grade_diaria_hibrida_v133.py`;
- `relatorios/atuais/GRADE_DIARIA_OFICIAL_HIBRIDA_V133.md`.
```

</details>

### V134 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V134.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 3
- Título: Estrutura do repositório V134

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V134
A V134 mantém a estrutura da V133 e adiciona os scripts/artefatos da expansão do fluxo oficial híbrido para o horizonte após 2026-05-20.
```

</details>

### V135 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V135.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 8
- Título: Estrutura do repositório V135

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V135
A V135 mantém a estrutura funcional da V134 e adiciona apenas a camada documental de fechamento da frente temporal:
- `relatorios/atuais/AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md`
- `saidas/operacional/auditoria_fechamento_frente_temporal_v135.json`
Não há mudança de lógica econômica nesta versão.
```

</details>

### V136 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V136.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V136

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V136
Artefatos centrais adicionados na V136:
- `scripts/diagnostico/inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py`
- `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v136.py`
- `scripts/diagnostico/consolidar_grade_diaria_hibrida_v136.py`
- `relatorios/atuais/AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md`
- `relatorios/atuais/AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md`
```

</details>

### V137 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V137.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 11
- Título: ESTRUTURA REPOSITÓRIO V137

<details>
<summary>Trecho inicial preservado</summary>

```text
# ESTRUTURA REPOSITÓRIO V137
Arquivos centrais alterados nesta versão:
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py`
- `scripts/inspecionar_alocador_pagamentos_terminal_v137.py`
- `relatorios/atuais/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`
- `relatorios/atuais/BASELINE_FIXA_V137.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V137.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V137.md`
```

</details>

### V138 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V138.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 6
- Título: ESTRUTURA REPOSITORIO V138

<details>
<summary>Trecho inicial preservado</summary>

```text
# ESTRUTURA REPOSITORIO V138
- `nucleo/fluxo_pagamentos_terminal_v138.py`
- `scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py`
- `scripts/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py`
- `relatorios/atuais/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md`
```

</details>

### V139 — `relatorios\historico\estruturas\etapa_modelos_script1\PREPARACAO_MODELOS_SCRIPT1_PAGAMENTOS_V139.md`

- Tipo: `subpasta_etapa_modelos_script1`
- Linhas originais: 21
- Título: Preparação para absorção dos modelos do Script 1 — V139

<details>
<summary>Trecho inicial preservado</summary>

```text
# Preparação para absorção dos modelos do Script 1 — V139
Esta etapa não reimplementa ainda os modelos do Script 1. Ela apenas prepara a base do repositório para recebê-los na próxima frente sem aumentar acoplamento estrutural.
## Decisão
Os modelos do Script 1 devem entrar **depois** da reorganização documental/operacional da V139 e **antes** da expansão do fluxo real de pagamentos para blocos maiores.
## Camada alvo
A absorção futura deve ocorrer na trilha:
- `nucleo/pagamentos/`
- `nucleo/pagamentos/modelos_script1/`
## Escopo sugerido da próxima frente
1. formalizar o contrato dos modelos do Script 1 ainda úteis para alocação de pagamentos;
2. criar adapters para o estado canônico atual;
3. integrar essas heurísticas ao `alocador_pagamentos_terminal_v1`.
## O que não fazer nesta etapa
- não reabrir auditoria ampla de switching;
- não mover ainda módulos de negócio entre diretórios;
- não expandir o bloco de pagamentos antes de absorver os modelos úteis do Script 1.
```

</details>

### V140 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V140.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 14
- Título: Estrutura do repositório — V140

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório — V140
A V140 mantém a reorganização da V139 e adiciona uma formalização explícita da trilha:
- `nucleo/pagamentos/modelos_script1/`
Arquivos novos desta etapa:
- `nucleo/pagamentos/modelos_script1/contrato_modelos_script1.py`
- `nucleo/pagamentos/modelos_script1/registro_modelos_script1.py`
- `config/modelos_script1_pagamentos_v140.json`
- `relatorios/atuais/CONTRATO_ABSORCAO_MODELOS_SCRIPT1_PAGAMENTOS_V140.md`
- `relatorios/atuais/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md`
Objetivo estrutural:
- permitir que a próxima integração das heurísticas do Script 1 aconteça sem ambiguidade sobre escopo e prioridade.
```

</details>

## Decisão desta etapa

A faixa V121–V150 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que o índice-mestre final das estruturas históricas seja criado.
