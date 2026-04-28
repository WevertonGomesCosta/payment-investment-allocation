# Relatório consolidado — auditorias históricas de shadow legacy

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/auditorias_especificas/shadow_legacy/` em um único relatório atual, preservando a trilha de benchmarks shadow, runner futuro, Script 2 legado e casos críticos sem manter arquivos granulares.

- Arquivos consolidados: 5
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/auditorias_especificas/shadow_legacy/AUDITORIA_CASOS_CRITICOS_RUNNER_FUTURO_SHADOW.md` | 15 | Auditoria dos casos críticos do runner futuro shadow |
| `relatorios/historico/auditorias_especificas/shadow_legacy/AUDITORIA_PRIMEIRA_QUEBRA_RUNNER_FUTURO_SHADOW.md` | 16 | Auditoria da primeira quebra do runner futuro shadow |
| `relatorios/historico/auditorias_especificas/shadow_legacy/BENCHMARK_SHADOW_AGRUPADO_VS_INDIVIDUAL_SCRIPT1.md` | 32 | Benchmark shadow do teste agrupado vs individual do Script 1 |
| `relatorios/historico/auditorias_especificas/shadow_legacy/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md` | 32 | Benchmark shadow do runner de simulação futura do Script 2 |
| `relatorios/historico/auditorias_especificas/shadow_legacy/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md` | 78 | Mapa de absorção da execução principal do Script 2 (correto) |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Shadow legacy | Evidências históricas de comparação shadow foram preservadas. |
| Runner futuro | Auditorias do runner de simulação futura legado permanecem rastreáveis. |
| Script 2 legado | Mapa de absorção da execução principal do Script 2 foi preservado. |
| Casos críticos | Achados sobre quebras e cobertura parcial foram preservados em forma consolidada. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/auditorias_especificas/shadow_legacy/AUDITORIA_CASOS_CRITICOS_RUNNER_FUTURO_SHADOW.md`

- Título: Auditoria dos casos críticos do runner futuro shadow
- Linhas originais: 15

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria dos casos críticos do runner futuro shadow
## Objetivo
Esta auditoria explica os casos sem cobertura integral do benchmark shadow do runner de simulação futura do Script 2 correto e mantém, ao final, um subbloco específico dos casos multifonte.
## Resultado central
1. O problema dominante do runner shadow é a perda de cobertura integral, não os poucos casos multifonte.
2. A maior parte dos casos críticos ocorre por **ausência total de liquidez no dia**, depois da primeira quebra de cobertura.
3. Os 3 casos multifonte devem ser lidos como subbloco final da auditoria e não como frente principal de absorção.
## Decisão operacional
A baseline V93 mantém o runner futuro apenas como benchmark shadow e prioriza a leitura causal dos casos sem cobertura integral antes de qualquer nova absorção do Script 2 legado.
```

</details>

### `relatorios/historico/auditorias_especificas/shadow_legacy/AUDITORIA_PRIMEIRA_QUEBRA_RUNNER_FUTURO_SHADOW.md`

- Título: Auditoria da primeira quebra do runner futuro shadow
- Linhas originais: 16

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria da primeira quebra do runner futuro shadow
## Escopo
Esta auditoria isola a primeira quebra de cobertura integral do benchmark shadow do runner de simulação futura do Script 2 correto.
## Hipótese auditada
A primeira quebra não decorre do multifonte em si, mas da exaustão prévia do lote crítico combinada com liquidez bloqueada por carência no dia da quebra.
## Critério de leitura
- usar a data da primeira quebra como marco causal;
- reconstruir a trajetória de liquidez até essa data;
- listar o consumo prévio do lote crítico;
- listar os pagamentos do próprio dia da quebra e os lotes disponíveis/bloqueados.
## Resultado esperado
Separar agressividade estrutural do runner shadow de qualquer sinal realmente reaproveitável para a baseline vigente.
```

</details>

### `relatorios/historico/auditorias_especificas/shadow_legacy/BENCHMARK_SHADOW_AGRUPADO_VS_INDIVIDUAL_SCRIPT1.md`

- Título: Benchmark shadow do teste agrupado vs individual do Script 1
- Linhas originais: 32

<details>
<summary>Trecho inicial preservado</summary>

```text
# Benchmark shadow do teste agrupado vs individual do Script 1
## Escopo
Este benchmark reproduz, em modo shadow e auditável, a camada de governança do **Script 1** legado que comparava execução **agrupada por dia** versus **individual**.
> Correção de identidade vigente: este benchmark havia sido inicialmente atribuído ao Script 2 por causa de um arquivo enviado com identificação incorreta. A partir da V91, ele deve ser lido como benchmark da execução principal do **Script 1**.
Nesta baseline, a absorção ocorre sobre a decisão local vigente com `proxy v3`, sem migrar a competição final entre estratégias nem o runner legado bruto.
## Resultado observado na baseline atual
- pagamentos individuais avaliados: **152**
- datas agrupadas avaliadas: **97**
- datas com mudança de lote dominante: **9**
- modo recomendado no benchmark shadow: **individual**
## Leitura técnica
1. O modo **individual** mantém cobertura integral em **152/152** pagamentos.
2. O modo **agrupado** reduz excesso em várias datas, mas perde cobertura integral em uma delas.
3. A recomendação agrupado vs individual é apenas uma régua de governança inspirada no **Script 1** legado.
4. Ela não substitui o fluxo principal nem reabre o `proxy v3` congelado.
## Decisão operacional
A baseline mantém o **modo individual** como recomendação shadow vigente.
O modo agrupado permanece apenas como benchmark comparativo, útil para auditoria fina das datas em que há mudança de lote dominante.
```

</details>

### `relatorios/historico/auditorias_especificas/shadow_legacy/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md`

- Título: Benchmark shadow do runner de simulação futura do Script 2
- Linhas originais: 32

<details>
<summary>Trecho inicial preservado</summary>

```text
# Benchmark shadow do runner de simulação futura do Script 2
## Escopo
Este benchmark reproduz, em modo shadow e auditável, o núcleo da execução futura do **Script 2 correto** enviado pelo usuário, inspirado principalmente no bloco `simular_futuro(...)` e na sua lógica de processamento dia a dia.
Nesta baseline, a absorção ocorre sem migrar o runner legado bruto para o fluxo principal.
## Resultado observado na baseline atual
- pagamentos futuros avaliados: **152**
- pagamentos totalmente cobertos no runner shadow: **15**
- pagamentos totalmente cobertos na decisão vigente: **152**
- pagamentos com multifonte no runner shadow: **3**
- pagamentos com mudança de lote principal vs. decisão vigente: **150**
- recomendação do benchmark: **vigente**
## Leitura técnica
1. O runner futuro shadow é muito mais agressivo do que a baseline vigente e altera o lote principal em quase todo o universo analisado.
2. Embora ele reduza excesso de forma quase sistemática, perde cobertura integral em uma parte substancial dos pagamentos futuros.
3. O uso de multifonte aparece, mas ainda em subconjunto pequeno.
4. Nesta etapa, a informação útil é diagnóstica: o runner legado correto não pode ser promovido ao fluxo principal sem auditorias adicionais por evento e por modo de execução futura.
## Decisão operacional
A baseline mantém a decisão vigente como referência operacional.
```

</details>

### `relatorios/historico/auditorias_especificas/shadow_legacy/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`

- Título: Mapa de absorção da execução principal do Script 2 (correto)
- Linhas originais: 78

<details>
<summary>Trecho inicial preservado</summary>

```text
# Mapa de absorção da execução principal do Script 2 (correto)
## Escopo
Este documento mapeia **apenas a orquestração principal do Script 2 correto** enviado pelo usuário, sem migrar o runner legado bruto para o fluxo principal atual.
> Observação de governança: o mapa aberto anteriormente para “Script 2” foi baseado em um arquivo identificado de forma incorreta. A partir da V92, este documento **substitui** aquela leitura e passa a refletir o runner correto de switching, simulação futura e exportação final.
A base desta classificação é o bloco `executar_runner_principal(...)` e suas funções imediatamente associadas no `Script 2.txt` correto, que contém:
- carregamento do snapshot inicial;
- alocação inicial de aportes;
- avaliação de switching e diagnósticos;
- aplicação do modo de execução futuro;
- `simular_futuro(...)`;
- exportação final do Excel.
## Classificação da execução principal do Script 2 correto
### Absorver já (em shadow/diagnóstico)
1. **Benchmark shadow do runner de simulação futura**
   - O núcleo real do Script 2 correto está em `simular_futuro(...)`, que processa contas futuras dia a dia, executa pagamentos, switches e consolida métricas.
   - Absorção recomendada: primeiro em **benchmark shadow reproduzível**, sem substituir o fluxo principal atual.
2. **Auditoria shadow do processamento por evento futuro**
   - O bloco `_processar_conta_futura(...)` e seus fallbacks (`rigido`, `hibrido`, `heuristico`) concentram regra de negócio real de pagamento no futuro.
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/auditorias_especificas/shadow_legacy/` pode ser removida se os documentos granulares não tiverem autoridade ativa superior aos documentos atuais.
