# Relatório consolidado — estruturas históricas V061–V090

## Objetivo

Consolidar a faixa `V061_V090` das estruturas históricas do repositório, preservando a evolução da Frente F1, recebidos auditáveis, fontes elegíveis, saldo disponível, decisão local, proxy econômico, benchmarks shadow, absorção legado e governança documental, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 28
- Faixa: V061–V090
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das estruturas

| Versão | Tipo | Linhas | Título |
|---:|---|---:|---|
| V61 | `estrutura_repositorio` | 59 | Estrutura oficial do repositório V61 |
| V62 | `estrutura_repositorio` | 61 | Estrutura oficial do repositório V62 |
| V63 | `estrutura_repositorio` | 61 | Estrutura oficial do repositório V63 |
| V64 | `estrutura_repositorio` | 61 | Estrutura oficial do repositório V64 |
| V65 | `estrutura_repositorio` | 62 | Estrutura oficial do repositório V65 |
| V66 | `estrutura_repositorio` | 63 | Estrutura oficial do repositório V66 |
| V67 | `estrutura_repositorio` | 63 | Estrutura oficial do repositório V67 |
| V68 | `estrutura_repositorio` | 63 | Estrutura oficial do repositório V68 |
| V69 | `estrutura_repositorio` | 65 | Estrutura oficial do repositório V69 |
| V71 | `estrutura_repositorio` | 67 | Estrutura oficial do repositório V71 |
| V72 | `estrutura_repositorio` | 67 | Estrutura oficial do repositório V72 |
| V73 | `estrutura_repositorio` | 33 | Estrutura oficial do repositório V73 |
| V74 | `estrutura_repositorio` | 34 | Estrutura oficial do repositório V74 |
| V75 | `estrutura_repositorio` | 45 | Estrutura do repositório V75 |
| V76 | `estrutura_repositorio` | 47 | Estrutura do repositório V76 |
| V77 | `estrutura_repositorio` | 54 | Estrutura do repositório V77 |
| V78 | `estrutura_repositorio` | 60 | Estrutura do repositório V78 |
| V79 | `estrutura_repositorio` | 67 | Estrutura do repositório V79 |
| V80 | `estrutura_repositorio` | 19 | Estrutura do repositório V80 |
| V82 | `estrutura_repositorio` | 20 | Estrutura do repositório V82 |
| V83 | `estrutura_repositorio` | 20 | Estrutura do repositório V83 |
| V84 | `estrutura_repositorio` | 16 | Estrutura do repositório V84 |
| V85 | `estrutura_repositorio` | 16 | Estrutura do repositório V85 |
| V86 | `estrutura_repositorio` | 16 | Estrutura do repositório V86 |
| V87 | `estrutura_repositorio` | 13 | Estrutura do repositório V88 |
| V88 | `estrutura_repositorio` | 13 | Estrutura do repositório V88 |
| V89 | `estrutura_repositorio` | 19 | Estrutura do repositório V89 |
| V90 | `estrutura_repositorio` | 9 | Estrutura do repositório V90 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Frente F1 | Estruturas de recebidos auditáveis, fontes elegíveis e saldo disponível foram preservadas. |
| Decisão local | Estruturação de `decisao_local_v1` e proxies econômicos v2/v3 foi consolidada. |
| Benchmarks shadow | Estruturas de switching econômico, resolver híbrido e auditorias shadow foram preservadas. |
| Absorção legado | Mapeamentos de Script 1/Script 2 e trilhas de compatibilidade foram registrados. |
| Governança documental | Estruturas de sincronização documental e organização da baseline foram preservadas. |

## Detalhe por estrutura

### V61 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V61.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 59
- Título: Estrutura oficial do repositório V61

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V61
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/*.py` → wrappers de compatibilidade
```

</details>

### V62 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V62.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 61
- Título: Estrutura oficial do repositório V62

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V62
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V63 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V63.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 61
- Título: Estrutura oficial do repositório V63

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V63
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V64 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V64.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 61
- Título: Estrutura oficial do repositório V64

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V64
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V65 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V65.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 62
- Título: Estrutura oficial do repositório V65

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V65
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V66 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V66.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 63
- Título: Estrutura oficial do repositório V66

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V66
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V67 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V67.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 63
- Título: Estrutura oficial do repositório V67

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V67
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V68 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V68.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 63
- Título: Estrutura oficial do repositório V68

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V68
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis` e `fontes_elegiveis_pagamento`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V69 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V69.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 65
- Título: Estrutura oficial do repositório V69

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V69
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento` e `saldo_disponivel_geral`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V71 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V71.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 67
- Título: Estrutura oficial do repositório V71

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V71
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento` e `saldo_disponivel_geral e decisao_local_v1 com proxy econômico v2`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V72 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V72.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 67
- Título: Estrutura oficial do repositório V72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V72
## Orquestração canônica
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento` e `saldo_disponivel_geral e decisao_local_v1 com proxy econômico v3`
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config
## Console
- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade
## Scripts
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V73 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V73.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 33
- Título: Estrutura oficial do repositório V73

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V73
## Núcleo
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1`;
- `nucleo/identidade_baseline.py` → identidade da baseline e nomes canônicos de artefatos;
- `nucleo/caixa_recebidos_auditaveis.py` → contrato mínimo da F1 + materialização de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral`, `decisao_local_v1` e auditoria comparativa `proxy v2 vs v3`.
## Aplicação e wrappers
- `aplicacao/console/principal.py`
- `aplicacao/principal.py`
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- wrappers compatíveis em `scripts/*.py`
## Diagnósticos vigentes
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
```

</details>

### V74 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V74.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 34
- Título: Estrutura oficial do repositório V74

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura oficial do repositório V74
## Núcleo
- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1`;
- `nucleo/identidade_baseline.py` → identidade da baseline e nomes canônicos de artefatos;
- `nucleo/caixa_recebidos_auditaveis.py` → contrato mínimo da F1 + materialização de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral`, `decisao_local_v1` e auditoria comparativa `proxy v2 vs v3`.
## Aplicação e wrappers
- `aplicacao/console/principal.py`
- `aplicacao/principal.py`
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- wrappers compatíveis em `scripts/*.py`
## Diagnósticos vigentes
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
```

</details>

### V75 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V75.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 45
- Título: Estrutura do repositório V75

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V75
## Núcleo da baseline
- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V75 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow de switching vigente
## Aplicação
- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade
## Scripts
### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
```

</details>

### V76 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V76.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 47
- Título: Estrutura do repositório V76

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V76
## Núcleo da baseline
- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V76 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow reconciliatória de switching
- `nucleo/switching_economico_shadow.py` — camada shadow de switching econômico legado
## Aplicação
- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade
## Scripts
### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
```

</details>

### V77 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V77.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 54
- Título: Estrutura do repositório V77

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V77
## Núcleo da baseline
- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V77 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow reconciliatória de switching
- `nucleo/switching_economico_shadow.py` — camada shadow de switching econômico legado
## Aplicação
- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade
## Scripts
### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
```

</details>

### V78 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V78.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 60
- Título: Estrutura do repositório V78

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V78
## Núcleo da baseline
- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V78 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow reconciliatória de switching
- `nucleo/switching_economico_shadow.py` — camada shadow de switching econômico legado
## Aplicação
- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade
## Scripts
### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
```

</details>

### V79 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V79.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 67
- Título: Estrutura do repositório V79

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V79
## Núcleo da baseline
- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V79 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow reconciliatória de switching
- `nucleo/switching_economico_shadow.py` — camada shadow de switching econômico legado
## Aplicação
- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade
## Scripts
### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
```

</details>

### V80 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V80.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 19
- Título: Estrutura do repositório V80

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V80
## Camadas novas da V80
- `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`
## Camadas preservadas
- `nucleo/caixa_recebidos_auditaveis.py`
- `nucleo/switching_economico_shadow.py`
- `nucleo/resolver_hibrido_5p_shadow.py`
- `scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
## Papel da V80
A V80 não adiciona nova camada funcional ao motor. Ela só aprofunda, de forma cirúrgica, os 42 casos já classificados como reaproveitáveis, preservando a baseline decisória vigente e mantendo o benchmark híbrido como régua externa de auditoria.
```

</details>

### V82 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V82.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 20
- Título: Estrutura do repositório V82

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V82
## Camadas novas da V82
- `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`
## Camadas preservadas
- `nucleo/caixa_recebidos_auditaveis.py`
- `nucleo/switching_economico_shadow.py`
- `nucleo/resolver_hibrido_5p_shadow.py`
- `scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
## Papel da V82
A V82 não adiciona nova camada funcional ao motor. Ela só aprofunda, de forma fina e localizada, a transição dominante identificada na V81, preservando a baseline decisória vigente e mantendo o benchmark híbrido como régua externa de auditoria.
```

</details>

### V83 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V83.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 20
- Título: Estrutura do repositório V83

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V83
## Camadas novas da V83
- `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`
## Camadas preservadas
- `nucleo/caixa_recebidos_auditaveis.py`
- `nucleo/switching_economico_shadow.py`
- `nucleo/resolver_hibrido_5p_shadow.py`
- `scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
## Papel da V83
A V83 não adiciona nova camada funcional ao motor. Ela só aprofunda, de forma fina e localizada, a transição dominante identificada na V81, preservando a baseline decisória vigente e mantendo o benchmark híbrido como régua externa de auditoria.
```

</details>

### V84 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V84.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 16
- Título: Estrutura do repositório V84

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V84
## Camada nova da V84
- `scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py`;
- `scripts/inspecionar_auditoria_estrutural_redundancia.py`;
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`.
## Papel da V84
A V84 adiciona apenas uma camada diagnóstica/documental focada em:
- wrappers de compatibilidade;
- helpers duplicados;
- crescimento da superfície diagnóstica.
Nenhum módulo funcional do motor foi alterado.
```

</details>

### V85 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V85.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 16
- Título: Estrutura do repositório V85

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V85
## Camada nova da V85
- `scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py`;
- `scripts/inspecionar_auditoria_estrutural_redundancia.py`;
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`.
## Papel da V85
A V85 adiciona apenas uma camada diagnóstica/documental focada em:
- wrappers de compatibilidade;
- helpers duplicados;
- crescimento da superfície diagnóstica.
Nenhum módulo funcional do motor foi alterado.
```

</details>

### V86 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V86.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 16
- Título: Estrutura do repositório V86

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V86
## Camada nova da V86
- `scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py`;
- `scripts/inspecionar_auditoria_estrutural_redundancia.py`;
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`.
## Papel da V86
A V86 adiciona apenas uma camada diagnóstica/documental focada em:
- wrappers de compatibilidade;
- helpers duplicados;
- crescimento da superfície diagnóstica.
Nenhum módulo funcional do motor foi alterado.
```

</details>

### V87 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V87.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 13
- Título: Estrutura do repositório V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V88
## Camada nova da V88
- `scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py`;
- `scripts/inspecionar_mapa_execucao_principal_script2.py`;
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`.
## Papel da V88
A V88 adiciona apenas uma camada diagnóstica/documental focada em classificar a orquestração principal do Script 2 legado.
Nenhum módulo funcional do motor foi alterado.
```

</details>

### V88 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V88.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 13
- Título: Estrutura do repositório V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V88
## Camada nova da V88
- `scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py`;
- `scripts/inspecionar_mapa_execucao_principal_script2.py`;
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`.
## Papel da V88
A V88 adiciona apenas uma camada diagnóstica/documental focada em classificar a orquestração principal do Script 2 legado.
Nenhum módulo funcional do motor foi alterado.
```

</details>

### V89 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V89.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 19
- Título: Estrutura do repositório V89

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V89
## Camada nova da V89
- `scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py`;
- `scripts/inspecionar_mapa_execucao_principal_script2.py`;
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`.
## Papel da V89
A V89 não abre nova camada funcional; ela atualiza os arquivos canônicos de dados, ajusta o `.gitignore` e revalida a camada diagnóstica já existente do benchmark shadow agrupado vs individual.
Nenhum módulo funcional do motor foi alterado.
## Ajustes incrementais da V89
- atualização dos arquivos canônicos de dados;
- ampliação do `.gitignore` para evitar versionamento acidental de `Script 1.txt`, `Script 2.txt` e `code/`.
```

</details>

### V90 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V90.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V90

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V90
## Camada nova da V90
A V90 não abre nova camada funcional. Ela realiza apenas uma correção de execução local na leitura/download da planilha financeira.
## Papel da V90
A baseline elimina uma fragilidade de Windows na promoção do arquivo temporário validado para `dados/dados_financeiros.xlsx`, preservando o restante da arquitetura da V89.
```

</details>

## Decisão desta etapa

A faixa V061–V090 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de estruturas sejam consolidadas e um índice-mestre final seja criado.
