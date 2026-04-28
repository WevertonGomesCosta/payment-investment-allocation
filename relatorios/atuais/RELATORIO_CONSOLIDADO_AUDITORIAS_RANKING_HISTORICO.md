# Relatório consolidado — auditorias históricas de ranking

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/auditorias_especificas/ranking/` em um único relatório atual, preservando a trilha de ranking da Carteira, simulação central e testes de horizonte longo sem manter arquivos granulares.

- Arquivos consolidados: 4
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/auditorias_especificas/ranking/AUDITORIA_RANKING_CARTEIRA_V123.md` | 15 | Auditoria técnica do ranking da Carteira — V123 |
| `relatorios/historico/auditorias_especificas/ranking/SIMULACAO_CENTRAL_CONTROLADA_HORIZONTE_LONGO_V124.md` | 149 | Simulação central controlada em horizonte mais longo — V124 |
| `relatorios/historico/auditorias_especificas/ranking/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md` | 103 | Teste do planejador temporal multidestino em horizonte mais longo — V122 |
| `relatorios/historico/auditorias_especificas/ranking/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V123.md` | 103 | Teste do planejador temporal multidestino em horizonte mais longo — V122 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Ranking Carteira-only | Auditoria histórica da metodologia de ranking foi preservada. |
| Planejador de switching | Testes de horizonte longo ligados ao planejador foram preservados. |
| Simulação central | Registro histórico de simulação central controlada foi preservado. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/auditorias_especificas/ranking/AUDITORIA_RANKING_CARTEIRA_V123.md`

- Título: Auditoria técnica do ranking da Carteira — V123
- Linhas originais: 15

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria técnica do ranking da Carteira — V123
## Achado principal
O ranqueamento usado pelo `planejador_switching_temporal_v1` não vinha do método Carteira-only estabilizado. Os destinos eram ordenados pela `triagem_motor`, baseada em score proxy contextual, o que permitia superexposição de Tesouro como destino padrão.
## Correção aplicada
- criação do pacote `nucleo/ranking_carteira_estabilizado.py`;
- leitura da aba `Carteira` completa como entrada única do ranking;
- uso do contrato e dos parâmetros fixos externos;
- cálculo interno da penalização adicional de prazo no consolidado;
- adoção do ranking Carteira-only como fonte preferencial de destinos do switching temporal.
## Efeito esperado
Produtos com score final prazo superior ao Tesouro deixam de ser rebaixados por uma triagem proxy transitória antes da avaliação econômica de longo prazo.
```

</details>

### `relatorios/historico/auditorias_especificas/ranking/SIMULACAO_CENTRAL_CONTROLADA_HORIZONTE_LONGO_V124.md`

- Título: Simulação central controlada em horizonte mais longo — V124
- Linhas originais: 149

<details>
<summary>Trecho inicial preservado</summary>

```text
# Simulação central controlada em horizonte mais longo — V124
- Objetivo: rerodar a simulação central controlada em horizonte mais longo usando o ranking Carteira-only estabilizado como fonte de destinos do `planejador_switching_temporal_v1`.
- Escopo: comparar o baseline sem switching com os melhores candidatos positivos do planejador, um por lote, já no cenário conjunto com pagamentos.
- Fonte de destinos: `contexto_baseline.ranking_carteira.quadro_destinos_switch`.
## Síntese executiva
- Horizonte de **60 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).
- Horizonte de **90 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).
- Horizonte de **120 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).
Achado central: após a correção do ranqueamento, surgem destinos melhores que Tesouro no planejador, mas na simulação central longa apenas o switching do `Lote 6630,64 fev.` para `Mercado Pago Cofrinho 120% CDI (Meli+)` continua vencedor — e ainda assim de forma marginal, sem ganho material sobre o baseline.
## Resultados por horizonte
### Horizonte 60 dias
- Janela: 2026-04-20 → 2026-06-19
- Pagamentos no recorte: 25
- Destinos elegíveis considerados: 12
- Switchings elegíveis no planejador: 26
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Vetor do melhor cenário: `(6.0, 12009.59, 10.0, 874.12, 9876.43, 0.0, 0.0, 4.0)`
#### Candidatos controlados no cenário conjunto
```

</details>

### `relatorios/historico/auditorias_especificas/ranking/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md`

- Título: Teste do planejador temporal multidestino em horizonte mais longo — V122
- Linhas originais: 103

<details>
<summary>Trecho inicial preservado</summary>

```text
# Teste do planejador temporal multidestino em horizonte mais longo — V122
## Objetivo
- Verificar se algum switching passa a sobreviver economicamente quando o horizonte deixa de penalizar excessivamente o custo fiscal inicial.
- A análise desta etapa é do **planejador**; ela não reexecuta o simulador central completo em horizonte longo.
## Síntese geral
- O primeiro horizonte com switching economicamente sobrevivente foi **60 dias** com **32** candidatos elegíveis.
- O recorte curto de 30 dias continua sem sobreviventes econômicos, mas a partir da ampliação do horizonte o planejador passa a encontrar candidatos positivos.
## Comparativo por horizonte
### Horizonte de 30 dias
- Intervalo: 2026-04-20 até 2026-05-20
- Pagamentos considerados: 15
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 0
#### Melhor destino por lote
- Lote 5680 abr.: Tesouro Educa+ 2032 | ganho=-0.7 | elegível=False
- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=-2.07 | elegível=False
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=-8.9 | elegível=False
```

</details>

### `relatorios/historico/auditorias_especificas/ranking/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V123.md`

- Título: Teste do planejador temporal multidestino em horizonte mais longo — V122
- Linhas originais: 103

<details>
<summary>Trecho inicial preservado</summary>

```text
# Teste do planejador temporal multidestino em horizonte mais longo — V122
## Objetivo
- Verificar se algum switching passa a sobreviver economicamente quando o horizonte deixa de penalizar excessivamente o custo fiscal inicial.
- A análise desta etapa é do **planejador**; ela não reexecuta o simulador central completo em horizonte longo.
## Síntese geral
- O primeiro horizonte com switching economicamente sobrevivente foi **60 dias** com **32** candidatos elegíveis.
- O recorte curto de 30 dias continua sem sobreviventes econômicos, mas a partir da ampliação do horizonte o planejador passa a encontrar candidatos positivos.
## Comparativo por horizonte
### Horizonte de 30 dias
- Intervalo: 2026-04-20 até 2026-05-20
- Pagamentos considerados: 15
- Lotes considerados: 5
- Destinos elegíveis por lote: 12
- Switching elegível no planejador: 0
#### Melhor destino por lote
- Lote 5680 abr.: Tesouro Educa+ 2032 | ganho=-0.7 | elegível=False
- Lote 6630,64 fev.: Tesouro Educa+ 2027 | ganho=-2.07 | elegível=False
- Lote 3000 mar. B: Tesouro Educa+ 2027 | ganho=-8.9 | elegível=False
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/auditorias_especificas/ranking/` pode ser removida se os documentos granulares não tiverem autoridade ativa superior aos documentos atuais.
