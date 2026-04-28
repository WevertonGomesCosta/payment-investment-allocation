# Relatório consolidado — validações históricas V121–V150

## Objetivo

Consolidar a faixa `V121_V150` das validações históricas, preservando validações do planejador temporal, ranking Carteira-only, simulação central, auditorias multihorizonte, grade diária de switching, comparador híbrido, ativação de lotes futuros, alocador terminal, fluxo de pagamentos terminal e preparação dos modelos do Script 1, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações consolidadas nesta faixa: 19
- Faixa: V121–V150
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das validações

| Versão | Linhas | Título |
|---:|---:|---|
| V121 | 17 | Validação local V121 |
| V122 | 14 | Validação local V122 |
| V123 | 6 | Validação local V123 |
| V124 | 8 | Validação local V124 |
| V125 | 8 | Validação local V125 |
| V126 | 8 | Validação local V126 |
| V127 | 9 | Validação local V127 |
| V128 | 9 | Validação local V128 |
| V129 | 6 | Validação local V129 |
| V130 | 8 | Validação local V130 |
| V131 | 10 | Validação local — V131 |
| V132 | 10 | Validação local V132 |
| V133 | 8 | Validação local V133 |
| V134 | 8 | Validação local V134 |
| V135 | 10 | Validação local V135 |
| V136 | 9 | Validação local V136 |
| V137 | 14 | VALIDAÇÃO LOCAL V137 |
| V138 | 6 | VALIDACAO LOCAL V138 |
| V140 | 11 | Validação local V140 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Planejador temporal | Validações de multidestino, horizonte longo e integração mínima foram preservadas. |
| Ranking e simulação | Ranking Carteira-only, simulação central e auditorias multihorizonte foram consolidados. |
| Grade diária | Execuções segmentadas e consolidações da grade diária de switching foram registradas. |
| Comparador híbrido | Validações do comparador híbrido e da grade oficial híbrida foram preservadas. |
| Alocador terminal e Script 1 | Validações do alocador, fluxo terminal e preparação dos modelos do Script 1 foram consolidadas. |

## Detalhe por validação

### V121 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V121.md`

- Linhas originais: 17
- Título: Validação local V121

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V121
## Rotinas executadas
- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado observado
- o planejador temporal passou a comparar múltiplos destinos elegíveis por lote;
- no recorte curto, foram considerados 12 destinos elegíveis por lote;
- nenhum destino alternativo permaneceu elegível após custo fiscal + reprojeção terminal + penalidade incremental de carência/liquidez;
- o cenário vencedor permaneceu o `baseline_sem_switching`;
- a baseline V121 permaneceu íntegra no release checker.
```

</details>

### V122 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V122.md`

- Linhas originais: 14
- Título: Validação local V122

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V122
## Execuções mínimas realizadas
- `python scripts/diagnostico/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado esperado
- o relatório multihorizonte deve ser gerado em `relatorios/atuais/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md`;
- a baseline V122 deve permanecer íntegra no release checker;
- a planilha operacional V122 deve ser gerada normalmente.
```

</details>

### V123 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V123.md`

- Linhas originais: 6
- Título: Validação local V123

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V123
- ranking Carteira estabilizado executado
- console principal executado
- planilha operacional executada
- release checker executado
```

</details>

### V124 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V124.md`

- Linhas originais: 8
- Título: Validação local V124

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V124
Validações mínimas desta derivação:
- `python scripts/diagnostico/inspecionar_simulacao_central_controlada_horizonte_longo_v124.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
```

</details>

### V125 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V125.md`

- Linhas originais: 8
- Título: Validação local V125

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V125
Validações mínimas desta derivação:
- auditoria multihorizonte consolidada a partir de execuções locais segmentadas dos horizontes 30, 45, 60, 75, 90, 120, 150, 180, 210, 240, 270 e 360 dias;
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
```

</details>

### V126 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V126.md`

- Linhas originais: 8
- Título: Validação local V126

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V126
Validações executadas:
- `python scripts/diagnostico/consolidar_grade_diaria_switching_v126.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
Observação: a auditoria diária foi consolidada em blocos de 5 dias para a janela inicial de 30 dias, preservando a lógica diária sem reduzir a análise a poucos horizontes fixos.
```

</details>

### V127 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V127.md`

- Linhas originais: 9
- Título: Validação local V127

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V127
Validações executadas nesta entrega:
- compilação dos módulos alterados da camada temporal;
- execução segmentada da grade diária em blocos de 3 dias;
- consolidação local de 30 dias da janela diária (`2026-04-21` a `2026-05-20`);
- geração do relatório operacional da baseline;
- release checker da baseline.
```

</details>

### V128 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V128.md`

- Linhas originais: 9
- Título: Validação local V128

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V128
Validações executadas nesta entrega:
- continuação da grade diária integral em blocos de 3 dias após `2026-05-20`;
- consolidação da auditoria diária ampliada até `2026-08-18`;
- geração do JSON consolidado V128;
- geração do relatório operacional da baseline;
- release checker da baseline.
```

</details>

### V129 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V129.md`

- Linhas originais: 6
- Título: Validação local V129

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V129
Validações executadas:
- carga do contexto baseline com parâmetros corrigidos da Carteira;
- auditoria do ticket mínimo do `CDB XP 150%`;
- reavaliação focal da janela 2026-04-30 a 2026-05-02 com os 5 melhores destinos da Carteira.
```

</details>

### V130 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V130.md`

- Linhas originais: 8
- Título: Validação local V130

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V130
Validações executadas na V130:
- execução segmentada da janela `2026-04-30` a `2026-05-20` em blocos de 3 dias via `inspecionar_grade_diaria_parametrizada_v130.py`;
- consolidação final via `consolidar_grade_diaria_parametrizada_v130.py`;
- geração da planilha operacional;
- release checker da baseline.
```

</details>

### V131 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V131.md`

- Linhas originais: 10
- Título: Validação local — V131

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local — V131
Validações executadas nesta derivação:
- `python scripts/diagnostico/inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
Resultado: baseline íntegra e auditoria cirúrgica gerada com sucesso.
```

</details>

### V132 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V132.md`

- Linhas originais: 10
- Título: Validação local V132

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V132
Validações executadas nesta versão:
- `python scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
Status esperado: release checker OK, relatório operacional V132 gerado e comparador híbrido consolidado.
```

</details>

### V133 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V133.md`

- Linhas originais: 8
- Título: Validação local V133

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V133
Validações executadas:
- execução em blocos da grade diária híbrida V133 para a janela `2026-04-30` a `2026-05-20`;
- consolidação oficial híbrida V133;
- `python aplicacao/console/principal.py`;
- `python scripts/operacional/gerar_planilha_operacional.py`;
- `python scripts/diagnostico/verificar_release_baseline.py`.
```

</details>

### V134 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V134.md`

- Linhas originais: 8
- Título: Validação local V134

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V134
Validações executadas nesta derivação:
- execução da grade diária híbrida V134 para 2026-05-21 a 2026-08-18;
- consolidação oficial híbrida V134;
- geração da planilha operacional V134;
- release checker V134.
```

</details>

### V135 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V135.md`

- Linhas originais: 10
- Título: Validação local V135

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V135
Validações executadas na V135:
- leitura e auditoria dos relatórios oficiais híbridos V133 e V134;
- auditoria da base `dados_financeiros.xlsx` para quantificar lotes futuros não aportados e pagamentos após `2026-08-18`;
- geração do relatório de fechamento `AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md`;
- geração do artefato JSON `auditoria_fechamento_frente_temporal_v135.json`;
- geração da planilha operacional V135;
- release checker V135.
```

</details>

### V136 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V136.md`

- Linhas originais: 9
- Título: Validação local V136

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V136
Validações executadas na V136:
- auditoria de ativação dos 24 lotes futuros não aportados;
- prova tardia oficial híbrida em `2026-09-01`;
- prova tardia oficial híbrida em `2027-03-03`;
- geração dos relatórios V136;
- release checker V136.
```

</details>

### V137 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V137.md`

- Linhas originais: 14
- Título: VALIDAÇÃO LOCAL V137

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V137
Comandos executados localmente nesta entrega:
- `python -m py_compile nucleo/alocador_pagamentos_terminal_v1.py`
- `python -m py_compile scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py`
- `python scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
Critério de aceite desta etapa:
- o alocador deve gerar candidatos reais para as quatro famílias principais de fonte;
- o cenário com switching elegível só pode entrar quando já vier promovível pelo comparador híbrido;
- o release checker deve fechar em OK para a baseline V137.
```

</details>

### V138 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V138.md`

- Linhas originais: 6
- Título: VALIDACAO LOCAL V138

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V138
- `python -m py_compile nucleo/fluxo_pagamentos_terminal_v138.py`
- `python -m py_compile scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py`
- `python scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
```

</details>

### V140 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V140.md`

- Linhas originais: 11
- Título: Validação local V140

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V140
Validações executadas nesta etapa:
- atualização do contrato documental da camada de pagamentos;
- criação do registro técnico das heurísticas prioritárias do Script 1;
- criação do registro Python das heurísticas contratadas;
- `python scripts/diagnostico/verificar_release_baseline.py`
Resultado esperado:
- baseline V140 íntegra;
- documentação ativa consistente com a próxima frente de implementação.
```

</details>

## Decisão desta etapa

A faixa V121–V150 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que o índice-mestre final das validações históricas seja criado.
