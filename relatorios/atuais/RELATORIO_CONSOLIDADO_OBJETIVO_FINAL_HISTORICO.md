# Relatório consolidado — histórico de objetivo final

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/objetivo_final/` em um único relatório atual, preservando a trilha conceitual sobre objetivo final, critérios de decisão, função objetivo e direção estratégica do motor.

- Arquivos consolidados: 4
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/objetivo_final/ATUALIZACAO_CACHE_DADOS_E_REEXECUCAO_V178.md` | 72 | Atualização de cache/dados e reexecução da análise — V178 |
| `relatorios/historico/objetivo_final/AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md` | 37 | Auditoria de alinhamento entre contrato vigente e objetivo final — V176 |
| `relatorios/historico/objetivo_final/AUDITORIA_REEXECUCAO_CACHE_DADOS_V178.md` | 18 | Auditoria da reexecução com cache BCB atualizado — V178 |
| `relatorios/historico/objetivo_final/AUDITORIA_REPOSITORIO_OBJETIVO_FINAL_V175.md` | 158 | Auditoria do repositório focada no objetivo final — V175 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Objetivo final | Preservação da direção estratégica do projeto e da função econômica central. |
| Critérios de decisão | Registro histórico de critérios usados para orientar recomendações, alocações e comparações. |
| Motor final | Contexto histórico preservado para futuras implementações sem manter arquivos granulares. |
| Rastreabilidade | Conteúdo original permanece resumido e com trechos iniciais preservados neste relatório. |

## Detalhe consolidado por arquivo

### `relatorios/historico/objetivo_final/ATUALIZACAO_CACHE_DADOS_E_REEXECUCAO_V178.md`

- Título: Atualização de cache/dados e reexecução da análise — V178
- Linhas originais: 72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Atualização de cache/dados e reexecução da análise — V178
## Escopo
- baseline operacional: V177
- repositório atualizado com o novo `dados/cache_bcb.json` e com a nova `dados/dados_financeiros.xlsx` enviada pelo usuário
- reexecução da validação diária: 2026-04-23 até 2026-05-23
- runner utilizado: `nucleo/runner_validacao_diaria_operacional_v177.py`
## Verificação dos insumos
- cache antigo: `data_final=2026-04-18`, `data_atualizacao=2026-04-18`
- cache novo: `data_final=2026-04-23`, `data_atualizacao=2026-04-23`
- novas datas efetivamente incorporadas ao cache: `2026-04-17`, `2026-04-20`, `2026-04-22`
- workbook enviado: idêntico byte a byte ao workbook já presente na V177
## Resultado global da reexecução
- data_inicio: 2026-04-23
- data_fim: 2026-05-23
- dias_no_horizonte: 31
- dias_com_pagamento: 9
- dias_sem_pagamento: 22
- dias_com_acoes_candidatas_switching: 31
```

</details>

### `relatorios/historico/objetivo_final/AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md`

- Título: Auditoria de alinhamento entre contrato vigente e objetivo final — V176
- Linhas originais: 37

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria de alinhamento entre contrato vigente e objetivo final — V176
## Conclusão executiva
A baseline V175 corrigiu a elegibilidade temporal operacional, mas ainda não entregava uma trilha diária suficientemente auditável para validar o objetivo final do projeto.
A V176 fecha duas lacunas prioritárias:
1. deixa explícito, em documentação oficial, que a validação diária user-facing deve ser lida contra o objetivo final do projeto;
2. reforma o runner diário para expor, por dia, os componentes reais do pagamento vencedor e o quadro de switching candidato/classificado.
## Divergências que precisavam ficar explícitas no projeto
### 1. Saída resumida demais para pagamentos
- Problema anterior: o runner retornava rótulos como `combinacao_minima_controlada`, sem mostrar a decomposição real por fonte/lote.
- Correção de governança na V176: o runner agora deve expor `componentes_reais_pagamento` e `fontes_candidatas_ordenadas`.
### 2. Saída resumida demais para switching
- Problema anterior: o runner retornava apenas contagens agregadas e o pacote vencedor do dia.
- Correção de governança na V176: o runner agora deve expor `acoes_candidatas`, `cenarios_classificados` e `melhor_cenario_promovivel`.
### 3. Critério de promovibilidade mal refletido no runner V175
- Problema anterior: o runner V175 checava `promovivel`, enquanto o comparador híbrido marca `promovivel_hibrido`.
- Efeito: risco de contar ou selecionar cenários de forma incorreta no runner de validação.
- Correção operacional na V176: seleção e contagem passam a usar `escolher_melhor_cenario_promovivel(...)` e `promovivel_hibrido`.
### 4. Lotes monitorados pouco visíveis
```

</details>

### `relatorios/historico/objetivo_final/AUDITORIA_REEXECUCAO_CACHE_DADOS_V178.md`

- Título: Auditoria da reexecução com cache BCB atualizado — V178
- Linhas originais: 18

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da reexecução com cache BCB atualizado — V178
## Síntese executiva
- somente o cache BCB/CDI mudou materialmente; a planilha enviada é idêntica à já embutida na V177.
- a atualização acrescentou fatores diários para 2026-04-17, 2026-04-20 e 2026-04-22.
- a política do motor não mudou com a reexecução: mesmos contadores globais, mesmas escolhas estruturais e mesmos gargalos metodológicos.
## Evidência objetiva
- resumo anterior: {'data_inicio': '2026-04-23', 'data_fim': '2026-05-23', 'dias_no_horizonte': 31, 'dias_com_pagamento': 9, 'dias_sem_pagamento': 22, 'dias_com_acoes_candidatas_switching': 31, 'dias_com_cenarios_promoviveis': 12, 'dias_com_switching_executado': 7, 'dias_com_normalizacao_pos_vencimento': 2, 'pagamentos_no_horizonte': 13, 'pagamentos_com_switching_no_fluxo': 0, 'inconsistencias_temporais_no_estado': 0, 'familias_cenarios_switching_avaliadas': {'individual_integral_parametrizado': 78, 'agrupado_integral_parametrizado': 22}, 'classes_cenarios_hibridos_avaliados': {'vencedor_terminal': 75, 'vencedor_operacional': 7, 'vencedor_hibrido_aceitavel': 1, 'dominado_pelo_baseline': 17}}
- resumo reexecutado: {'data_inicio': '2026-04-23', 'data_fim': '2026-05-23', 'dias_no_horizonte': 31, 'dias_com_pagamento': 9, 'dias_sem_pagamento': 22, 'dias_com_acoes_candidatas_switching': 31, 'dias_com_cenarios_promoviveis': 12, 'dias_com_switching_executado': 7, 'dias_com_normalizacao_pos_vencimento': 2, 'pagamentos_no_horizonte': 13, 'pagamentos_com_switching_no_fluxo': 0, 'inconsistencias_temporais_no_estado': 0, 'familias_cenarios_switching_avaliadas': {'individual_integral_parametrizado': 78, 'agrupado_integral_parametrizado': 22}, 'classes_cenarios_hibridos_avaliados': {'vencedor_terminal': 75, 'vencedor_operacional': 7, 'vencedor_hibrido_aceitavel': 1, 'dominado_pelo_baseline': 17}}
## Efeito numérico principal
- 2026-04-23, lote 3000 mar. V: 3076.18 -> 3074.03
- 2026-04-23, lote 3000 mar. B: 3074.0 -> 3071.85
## Decisão de auditoria
- a V178 deve ser lida como atualização de insumos + reexecução, não como mudança de política do motor.
- os próximos ajustes devem continuar focados no comparador integrado de dias com pagamento.
```

</details>

### `relatorios/historico/objetivo_final/AUDITORIA_REPOSITORIO_OBJETIVO_FINAL_V175.md`

- Título: Auditoria do repositório focada no objetivo final — V175
- Linhas originais: 158

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria do repositório focada no objetivo final — V175
## Referências contratuais revisadas
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `relatorios/atuais/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`
- `relatorios/atuais/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md`
- `relatorios/atuais/AUDITORIA_POS_VENCIMENTO_V145.md`
## Síntese executiva
A V175 já contém peças importantes do motor conjunto, mas ainda não atende integralmente o objetivo final do projeto. O desvio atual não é apenas um bug de saída; é um desalinhamento entre:
1. o **contrato final do projeto** (motor conjunto temporal, auditável, orientado a patrimônio terminal);
2. a **camada executável atual** (ainda fortemente monofonte/local no pagamento e restritiva no switching);
3. a **saída de validação** (insuficiente para auditoria por lote/dia/cenário).
## O que já está coerente com a metodologia
- A decisão por pagamento não está modelada como “aportar por aportar”; o alocador tenta ranquear fontes por perda terminal, custo fiscal, liquidez e penalidade estratégica.
- Há previsão contratual e estrutural para timeline global, switching temporal autônomo e recomputação sequencial central.
- A normalização pós-vencimento já foi aberta no simulador central e no runner diário.
- O comparador híbrido já distingue cenários terminalmente aceitáveis de cenários apenas operacionalmente bons.
## Onde a implementação ainda diverge do objetivo final
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/objetivo_final/` pode ser removida se a auditoria local confirmar que os documentos granulares não possuem autoridade normativa ativa superior aos documentos atuais do projeto.
