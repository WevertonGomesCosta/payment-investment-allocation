# Relatório consolidado — validações históricas V061–V090

## Objetivo

Consolidar a faixa `V061_V090` das validações históricas, preservando validações da Frente F1, recebidos auditáveis, fontes elegíveis, saldo disponível, decisão local, proxy econômico v2/v3, absorção legado, switching econômico shadow, comparações proxy/híbrido, auditoria estrutural e correção de execução local, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações consolidadas nesta faixa: 28
- Faixa: V061–V090
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das validações

| Versão | Linhas | Título |
|---:|---:|---|
| V61 | 41 | Validação local V61 |
| V62 | 44 | Validação local V62 |
| V63 | 46 | Validação local V63 |
| V64 | 46 | Validação local V64 |
| V65 | 49 | Validação local V65 |
| V66 | 55 | Validação local V66 |
| V67 | 52 | Validação local V67 |
| V68 | 49 | Validação local V68 |
| V69 | 50 | Validação local V69 |
| V71 | 53 | Validação local V71 |
| V72 | 53 | Validação local V72 |
| V73 | 34 | Validação local V73 |
| V74 | 30 | Validação local V74 |
| V75 | 30 | Validação local V75 |
| V76 | 30 | Validação local V76 |
| V77 | 38 | Validação local V77 |
| V78 | 45 | Validação local V78 |
| V79 | 51 | Validação local V79 |
| V80 | 16 | Validação local V80 |
| V82 | 16 | Validação local V82 |
| V83 | 16 | Validação local V83 |
| V84 | 18 | Validação local V84 |
| V85 | 25 | Validação local V85 |
| V86 | 27 | Validação local V86 |
| V87 | 18 | Validação local V88 |
| V88 | 18 | Validação local V88 |
| V89 | 25 | Validação local V89 |
| V90 | 15 | Validação local V90 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Frente F1 | Validações de recebidos auditáveis, fontes elegíveis e saldo disponível foram preservadas. |
| Decisão local | Validações da `decisao_local_v1` e proxies econômicos v2/v3 foram consolidadas. |
| Shadow/legado | Absorção legado, switching econômico shadow e comparações proxy/híbrido foram registradas. |
| Auditoria estrutural | Validações de redundância, mapa Script 2 e execução local foram preservadas. |
| Release e operação | Execuções de console, planilha operacional e release checker foram consolidadas. |

## Detalhe por validação

### V61 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V61.md`

- Linhas originais: 41
- Título: Validação local V61

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V61
## Escopo validado
- identidade da baseline atualizada para V61;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel`;
- script diagnóstico de `recebido_auditavel` e wrapper de compatibilidade executáveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
```

</details>

### V62 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V62.md`

- Linhas originais: 44
- Título: Validação local V62

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V62
## Escopo validado
- identidade da baseline atualizada para V62;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` aberta;
- script diagnóstico de `fonte_elegivel_pagamento` e wrapper de compatibilidade executáveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
```

</details>

### V63 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V63.md`

- Linhas originais: 46
- Título: Validação local V63

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V63
## Escopo validado
- identidade da baseline atualizada para V63;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- atualização do cache BCB/CDI em `dados/cache_bcb.json`;
- script diagnóstico de `fonte_elegivel_pagamento` e wrapper de compatibilidade executáveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
```

</details>

### V64 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V64.md`

- Linhas originais: 46
- Título: Validação local V64

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V64
## Escopo validado
- identidade da baseline atualizada para V64;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- atualização do cache BCB/CDI em `dados/cache_bcb.json`;
- script diagnóstico de `fonte_elegivel_pagamento` e wrapper de compatibilidade executáveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
```

</details>

### V65 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V65.md`

- Linhas originais: 49
- Título: Validação local V65

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V65
## Escopo validado
- identidade da baseline atualizada para V65;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- reorganização da seção `Situação atual` no console para separar lotes exauridos e lotes ativos;
- reorganização da aba `Situação atual` da planilha com quatro tabelas de lotes;
- recebidos auditáveis preservados na mesma aba/seção.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
```

</details>

### V66 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V66.md`

- Linhas originais: 55
- Título: Validação local V66

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V66
## Escopo validado
- identidade da baseline atualizada para V66;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- remoção da tabela detalhada de recebidos da seção `Situação atual` no console;
- remoção da tabela detalhada de recebidos da aba `Situação atual` da planilha;
- criação da aba `Fechamento econômico atual` na planilha;
- normalização pós-replay de resíduos sub-limiar validada;
- correção observável do `Lote 4124,75 fev.` na situação atual.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V67 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V67.md`

- Linhas originais: 52
- Título: Validação local V67

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V67
## Escopo validado
- identidade da baseline atualizada para V67;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- remoção da tabela detalhada de recebidos da seção `Situação atual` no console;
- remoção da tabela detalhada de recebidos da aba `Situação atual` da planilha;
- criação da aba `Fechamento econômico atual` na planilha;
- normalização pós-replay de resíduos sub-limiar validada;
- correção observável do `Lote 4124,75 fev.` na situação atual.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
```

</details>

### V68 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V68.md`

- Linhas originais: 49
- Título: Validação local V68

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V68
## Escopo validado
- identidade da baseline atualizada para V68;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 4;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` refinada por `pagamento_id` e `data_pagamento`;
- diagnóstico de `fonte_elegivel_pagamento` atualizado para mostrar elegibilidade temporal, bloqueios e método de leitura do valor disponível;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
```

</details>

### V69 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V69.md`

- Linhas originais: 50
- Título: Validação local V69

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V69
## Escopo validado
- identidade da baseline atualizada para V69;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 5;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada por `pagamento_id` e `data_pagamento`;
- materialização executável de `saldo_disponivel_geral` por pagamento;
- diagnóstico de `saldo_disponivel_geral` atualizado para mostrar origem, status, duplicidade e método de agregação;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `python aplicacao/console/principal.py`
```

</details>

### V71 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V71.md`

- Linhas originais: 53
- Título: Validação local V71

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V71
## Escopo validado
- identidade da baseline atualizada para V71;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 7;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada por `pagamento_id` e `data_pagamento`;
- materialização executável de `saldo_disponivel_geral` preservada;
- materialização executável de `decisao_local_v1` com proxy econômico v2 por pagamento sobre a matriz temporal completa;
- diagnóstico de `decisao_local_v1` atualizado para mostrar critério, proxy econômico v2, fonte escolhida, cobertura e status da origem;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
```

</details>

### V72 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V72.md`

- Linhas originais: 53
- Título: Validação local V72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V72
## Escopo validado
- identidade da baseline atualizada para V72;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 8;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada por `pagamento_id` e `data_pagamento`;
- materialização executável de `saldo_disponivel_geral` preservada;
- materialização executável de `decisao_local_v1` com proxy econômico v3 por pagamento sobre a matriz temporal completa;
- diagnóstico de `decisao_local_v1` atualizado para mostrar critério, proxy econômico v3, fonte escolhida, cobertura e status da origem;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.
## Execução validada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
```

</details>

### V73 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V73.md`

- Linhas originais: 34
- Título: Validação local V73

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V73
## Escopo validado
- identidade da baseline atualizada para V73;
- manutenção da `decisao_local_v1` com proxy econômico v3 como baseline vigente;
- recalculo reproduzível da decisão local com proxy v2 e v3 na mesma base;
- auditoria comparativa `v2 vs v3` com exportação de `.xlsx` e `.csv`;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py
python scripts/diagnostico/inspecionar_decisao_local_v1.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V73
```

</details>

### V74 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V74.md`

- Linhas originais: 30
- Título: Validação local V74

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V74
## Escopo validado
- identidade da baseline atualizada para V74;
- sincronização documental de `README`, contrato operacional, backlog e relatórios vigentes;
- manutenção da `decisao_local_v1` com `proxy econômico v3` congelado como baseline vigente;
- geração do artefato operacional com o novo versionamento da baseline;
- comandos canônicos e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V74
- o `README` passa a apontar para a baseline **V74**;
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md` deixa de descrever a V69 e passa a refletir a baseline vigente;
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md` deixa de listar `decisao_local_v1` como etapa futura já aberta;
```

</details>

### V75 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V75.md`

- Linhas originais: 30
- Título: Validação local V75

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V75
## Escopo validado
- identidade da baseline atualizada para V75;
- criação do mapa de absorção legado para os Scripts 1 e 2;
- criação do diagnóstico `inspecionar_mapa_absorcao_legado.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_absorcao_legado.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V75
- o mapa vigente classifica os blocos dos Scripts 1 e 2 em `migrar já`, `migrar depois`, `não migrar` e `substituída pela baseline`;
- o diagnóstico do mapa imprime prioridades imediatas de absorção legado sem alterar o fluxo principal;
```

</details>

### V76 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V76.md`

- Linhas originais: 30
- Título: Validação local V76

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V76
## Escopo validado
- identidade da baseline atualizada para V76;
- criação da camada `switching_economico_shadow`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V76
- a baseline agora materializa uma camada shadow de switching econômico legado desacoplada do fluxo principal;
```

</details>

### V77 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V77.md`

- Linhas originais: 38
- Título: Validação local V77

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V77
## Escopo validado
- identidade da baseline atualizada para V77;
- criação da camada `switching_economico_shadow`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V77
- a baseline agora materializa uma camada shadow de switching econômico legado desacoplada do fluxo principal;
```

</details>

### V78 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V78.md`

- Linhas originais: 45
- Título: Validação local V78

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V78
## Escopo validado
- identidade da baseline atualizada para V78;
- criação da camada `switching_economico_shadow`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V78
- a baseline agora materializa uma camada shadow de switching econômico legado desacoplada do fluxo principal;
```

</details>

### V79 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V79.md`

- Linhas originais: 51
- Título: Validação local V79

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V79
## Escopo validado
- identidade da baseline atualizada para V79;
- criação da camada `switching_economico_shadow`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.
## Comandos executados
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Evidências observáveis da V79
- a baseline agora materializa uma camada shadow de switching econômico legado desacoplada do fluxo principal;
```

</details>

### V80 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V80.md`

- Linhas originais: 16
- Título: Validação local V80

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V80
## Bateria executada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V80 compilando e executando;
- auditoria cirúrgica dos 42 casos reaproveitáveis gerada com sucesso;
- `release checker` aprovado em estado limpo;
- sem alteração do fluxo principal, do motor financeiro e do `proxy v3` congelado.
```

</details>

### V82 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V82.md`

- Linhas originais: 16
- Título: Validação local V82

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V82
## Bateria executada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V82 compilando e executando;
- auditoria fina da transição dominante gerada com sucesso;
- `release checker` aprovado em estado limpo;
- sem alteração do fluxo principal, do motor financeiro e do `proxy v3` congelado.
```

</details>

### V83 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V83.md`

- Linhas originais: 16
- Título: Validação local V83

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V83
## Bateria executada
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V83 compilando e executando;
- auditoria fina da transição dominante gerada com sucesso;
- `release checker` aprovado em estado limpo;
- sem alteração do fluxo principal, do motor financeiro e do `proxy v3` congelado.
```

</details>

### V84 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V84.md`

- Linhas originais: 18
- Título: Validação local V84

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V84
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V84 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico da auditoria estrutural executando;
- release checker fechando em `OK` no pacote final limpo.
```

</details>

### V85 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V85.md`

- Linhas originais: 25
- Título: Validação local V85

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V85
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V85 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico da auditoria estrutural executando;
- release checker fechando em `OK` no pacote final limpo.
- wrappers raiz previamente quebrados executando diretamente;
- `python scripts/verificar_release_baseline.py` executando corretamente;
- `python scripts/inspecionar_switching_economico_shadow.py` executando corretamente;
- `python scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` executando corretamente;
```

</details>

### V86 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V86.md`

- Linhas originais: 27
- Título: Validação local V86

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V86
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V86 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico da auditoria estrutural executando;
- release checker fechando em `OK` no pacote final limpo.
- wrappers raiz previamente quebrados executando diretamente;
- `python scripts/verificar_release_baseline.py` executando corretamente;
- `python scripts/inspecionar_switching_economico_shadow.py` executando corretamente;
- `python scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` executando corretamente;
```

</details>

### V87 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V87.md`

- Linhas originais: 18
- Título: Validação local V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V88
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V88 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico do mapa da execução principal do Script 2 executando;
- release checker fechando em `OK` no pacote final limpo.
```

</details>

### V88 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V88.md`

- Linhas originais: 18
- Título: Validação local V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V88
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V88 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico do mapa da execução principal do Script 2 executando;
- release checker fechando em `OK` no pacote final limpo.
```

</details>

### V89 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V89.md`

- Linhas originais: 25
- Título: Validação local V89

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V89
## Bateria executada
```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```
## Resultado
- baseline V89 compilando e executando com os dados atualizados;
- relatório operacional vigente gerado;
- diagnóstico do mapa da execução principal do Script 2 executando;
- release checker fechando em `OK` no pacote final limpo.
## Validação adicional da V89
- atualização dos dados canônicos `dados/dados_financeiros.xlsx` e `dados/cache_bcb.json`;
- rerun do benchmark shadow agrupado vs individual com dados atualizados;
- release checker aprovado em estado limpo.
```

</details>

### V90 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V90.md`

- Linhas originais: 15
- Título: Validação local V90

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V90
## Escopo validado
- compilação do repositório;
- geração da planilha operacional;
- execução do script principal;
- checagem mínima de release.
## Resultado
- baseline V90 compilando e executando;
- script principal gerando a saída operacional;
- `release checker` aprovado em estado limpo;
- rotina de download preparada para não manter o arquivo temporário bloqueado após a validação do `.xlsx`.
```

</details>

## Decisão desta etapa

A faixa V061–V090 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de validações sejam consolidadas e um índice-mestre final seja criado.
