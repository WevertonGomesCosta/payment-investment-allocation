# Relatório consolidado — validações históricas V001–V030

## Objetivo

Consolidar a faixa `V001_V030` das validações históricas, preservando as execuções locais iniciais, testes de `aplicacao/principal.py`, inspeções de base, cache CDI/BCB, primeiros contratos e validações de lotes, sem remover ainda os arquivos granulares de `relatorios/historico/validacoes/`.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações consolidadas nesta faixa: 24
- Faixa: V001–V030
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das validações

| Versão | Linhas | Título |
|---:|---:|---|
| V6 | 33 | Validação local da V6 |
| V7 | 27 | Validação local V7 |
| V8 | 27 | Validação local V8 |
| V9 | 14 | Validação local V9 |
| V10 | 32 | Validação local V10 |
| V11 | 37 | Validação local V11 |
| V12 | 30 | Validação local V12 |
| V13 | 21 | Validação local V13 |
| V14 | 28 | Validação local V14 |
| V15 | 35 | Validação local V15 |
| V16 | 24 | Validação local V16 |
| V18 | 37 | Validação local V18 |
| V19 | 3 | Validação local V19 |
| V20 | 10 | Validação local V20 |
| V21 | 23 | Validação local V21 |
| V22 | 23 | Validação local V22 |
| V23 | 17 | Validação local V23 |
| V24 | 17 | Validação local V24 |
| V25 | 14 | VALIDAÇÃO LOCAL V25 |
| V26 | 1 | VALIDACAO_LOCAL_V26.md |
| V27 | 5 | VALIDAÇÃO LOCAL V27 |
| V28 | 1 | VALIDACAO_LOCAL_V28.md |
| V29 | 1 | VALIDACAO_LOCAL_V29.md |
| V30 | 3 | VALIDACAO LOCAL V30 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Execução inicial | Validações de `aplicacao/principal.py` e inspeções básicas foram preservadas. |
| Base e inconsistências | Inspeções iniciais da base financeira e inconsistências de lotes foram consolidadas. |
| CDI/cache | Validações do fallback local do cache CDI/BCB foram preservadas. |
| Lotes e resíduos | Correções iniciais de datas, resíduos, bônus e lotes históricos foram registradas. |
| Governança | A faixa permanece histórica e não reabre decisões antigas. |

## Detalhe por validação

### V6 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V6.md`

- Linhas originais: 33
- Título: Validação local da V6

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local da V6
Esta validação foi executada localmente antes da entrega da versão V6, em conformidade
com a regra operacional de testar e corrigir o que for possível antes do envio do
repositório.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado observado
- Execução concluída sem erro fatal nos dois comandos.
- `config_atualizado.json` foi localizado corretamente em `dados/`.
- `dados_financeiros.xlsx` foi localizado corretamente em `dados/`.
- As abas primárias `Carteira`, `Inventário de Lotes` e `Todos os Gastos` foram lidas com sucesso.
- As abas auxiliares `Resumo Mensal` e `Todas as Carteiras` foram identificadas e separadas como não operacionais na inspeção atual.
- A saída do console permaneceu organizada em blocos legíveis.
## Achados relevantes desta validação
- O ambiente atual executou a baseline mesmo com `pulp` e `workalendar` ausentes, porque a
```

</details>

### V7 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V7.md`

- Linhas originais: 27
- Título: Validação local V7

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V7
Esta validação foi executada no ambiente disponível antes da entrega da V7.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- saída inicial de console organizada por blocos.
## Observação
Dependências não críticas para esta etapa mínima podem continuar ausentes no ambiente,
desde que não impeçam a validação básica da baseline.
```

</details>

### V8 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V8.md`

- Linhas originais: 27
- Título: Validação local V8

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V8
Esta validação foi executada no ambiente disponível antes da entrega da V8.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- resolução central da data de referência;
- saída inicial de console organizada por blocos.
## Observação
Dependências não críticas para esta etapa mínima podem continuar ausentes no ambiente, desde que não impeçam a validação básica da baseline.
```

</details>

### V9 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V9.md`

- Linhas originais: 14
- Título: Validação local V9

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V9
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado
- Ambos os comandos executaram com retorno 0 no ambiente disponível.
- A baseline foi validada após a limpeza dos artefatos de execução local.
- O pacote final desta versão não inclui `__pycache__`, `.pyc` nem logs brutos auxiliares.
```

</details>

### V10 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V10.md`

- Linhas originais: 32
- Título: Validação local V10

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V10
Esta validação foi executada no ambiente disponível antes da entrega da V10.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- exibição da data de referência no console;
- construção da carteira canônica inicial;
- geração de `produto_key` para todos os produtos da aba `Carteira`;
- validação estrutural da aba `Carteira` sem erro fatal.
```

</details>

### V11 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V11.md`

- Linhas originais: 37
- Título: Validação local V11

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V11
Esta validação foi executada no ambiente disponível antes da entrega da V11.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- construção da carteira canônica;
- construção do inventário canônico;
- construção dos gastos canônicos;
- saída inicial de console organizada por blocos.
```

</details>

### V12 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V12.md`

- Linhas originais: 30
- Título: Validação local V12

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V12
Esta validação foi executada no ambiente disponível antes da entrega da V12.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- construção da carteira canônica;
- construção do inventário canônico;
- construção dos gastos canônicos;
- construção da camada neutra de calendário financeiro e taxas/CDI base;
- saída inicial de console organizada por blocos.
```

</details>

### V13 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V13.md`

- Linhas originais: 21
- Título: Validação local V13

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V13
Esta validação foi executada no ambiente disponível antes da entrega da V13.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- saída do console com severidade explícita (`OK`, `AVISO`, `ERRO`);
- resumo consolidado das camadas canônicas;
- carregamento correto de config, planilha, carteira, inventário, gastos e calendário/taxas base.
```

</details>

### V14 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V14.md`

- Linhas originais: 28
- Título: Validação local V14

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V14
Esta validação foi executada no ambiente disponível antes da entrega da V14.
## Escopo da derivação
Centralização de utilitários neutros transversais em módulo próprio, sem abertura de replay do passado, núcleo financeiro, switching ou CDI operacional.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- baseline carregada corretamente como V14;
- `config_atualizado.json` localizado corretamente;
- `dados_financeiros.xlsx` localizado corretamente;
- carteira canônica, inventário canônico, gastos canônicos e calendário financeiro/taxas base carregados com sucesso;
- console permaneceu organizado e auditável após a refatoração;
```

</details>

### V15 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V15.md`

- Linhas originais: 35
- Título: Validação local V15

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V15
Esta validação foi executada no ambiente disponível antes da entrega da V15.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- leitura correta das três abas primárias do contrato;
- manutenção da carteira canônica, inventário canônico, gastos canônicos e calendário/taxas base;
- construção de lotes shadow normalizados;
- derivação de eventos brutos de aporte histórico;
- reconciliação observado vs shadow marcada como equivalente;
- trilha técnica de eventos ordenada de forma determinística;
```

</details>

### V16 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V16.md`

- Linhas originais: 24
- Título: Validação local V16

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V16
Esta validação foi executada no ambiente disponível antes da entrega da V16.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- matching canônico reforçado dos produtos aportados;
- resumo shadow mais consolidado no console;
- ausência de erro fatal na baseline.
```

</details>

### V18 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V18.md`

- Linhas originais: 37
- Título: Validação local V18

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V18
Esta validação foi executada no ambiente disponível antes da entrega da V18.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- a nova base fixa foi incorporada ao repositório;
- a aba `Carteira` passou a carregar o universo completo de produtos;
- a aba auxiliar `Todas as Carteiras` deixou de ser necessária no arquivo canônico da baseline;
- o matching de produtos aportados no inventário ficou completo no universo canônico atual;
- a triagem programática v1 do motor (triagem preliminar proxy) foi executada sem abrir replay, núcleo financeiro completo, switching econômico ou otimização profunda;
- a baseline preservou as camadas já abertas: carteira canônica, dados operacionais canônicos, calendário financeiro/taxas base e reconciliação shadow.
## Sinais relevantes da triagem v1
```

</details>

### V19 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V19.md`

- Linhas originais: 3
- Título: Validação local V19

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V19
Esta versão foi validada localmente após a remoção do fallback nominal específico e após o enquadramento explícito do score v1 como triagem preliminar proxy.
```

</details>

### V20 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V20.md`

- Linhas originais: 10
- Título: Validação local V20

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V20
Comandos executados antes da entrega:
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
Objetivo: confirmar que a baseline segue íntegra após os ajustes finos de auditabilidade e calibração conservadora da triagem.
```

</details>

### V21 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V21.md`

- Linhas originais: 23
- Título: Validação local V21

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V21
Esta validação foi executada antes da entrega da V21.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- leitura das abas primárias da planilha;
- carteira canônica carregada e auditada;
- triagem v1 exibida como proxy preliminar com calibração cautelosa;
- auditoria de matching canônico e resumo shadow reforçados.
```

</details>

### V22 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V22.md`

- Linhas originais: 23
- Título: Validação local V22

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V22
Esta validação foi executada no ambiente disponível antes da entrega da V22.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado resumido
- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0
## Evidências principais observadas
- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- carregamento do núcleo financeiro mínimo com lotes financeiros, fator líquido e amostra de saque;
- ausência de abertura de solver, replay, switching econômico e relatório financeiro atual.
```

</details>

### V23 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V23.md`

- Linhas originais: 17
- Título: Validação local V23

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V23
Esta validação foi executada no ambiente disponível antes da entrega da V23.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado
- ambos retornaram `0`;
- o replay controlado do passado foi carregado sobre o núcleo financeiro mínimo;
- o console passou a exibir resumo do replay histórico, incluindo cobertura de contas e saldo pós-replay;
- não foram abertos switching econômico, score econômico final, solver ou relatório financeiro atual.
```

</details>

### V24 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V24.md`

- Linhas originais: 17
- Título: Validação local V24

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V24
Esta validação foi executada no ambiente disponível antes da entrega da V24.
## Comandos executados
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
## Resultado
- ambos retornaram `0`;
- o replay controlado do passado passou a materializar lotes históricos `Investimento='-'`;
- aliases históricos auditáveis foram resolvidos;
- a cobertura de contas históricas passou a 59/59.
```

</details>

### V25 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V25.md`

- Linhas originais: 14
- Título: VALIDAÇÃO LOCAL V25

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V25
Comandos executados:
```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```
Resultado:
- ambos retornaram 0;
- o replay controlado do passado permaneceu cobrindo 59/59 contas históricas;
- o cache diário do CDI do BCB foi integrado à baseline, mas na validação local o fetch não pôde ser concluído por indisponibilidade de rede/resolução de nome, então o sistema fez fallback controlado para a taxa de modelo;
- a baseline permaneceu estável sem abrir novas camadas econômicas.
```

</details>

### V26 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V26.md`

- Linhas originais: 1
- Título: VALIDACAO_LOCAL_V26.md

<details>
<summary>Trecho inicial preservado</summary>

```text
Validação local da V28 com fallback local do cache CDI em dados/cache_bcb.json.
```

</details>

### V27 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V27.md`

- Linhas originais: 5
- Título: VALIDAÇÃO LOCAL V27

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V27
Comandos executados:
- python aplicacao/principal.py
- python scripts/inspecionar_base.py
```

</details>

### V28 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V28.md`

- Linhas originais: 1
- Título: VALIDACAO_LOCAL_V28.md

<details>
<summary>Trecho inicial preservado</summary>

```text
Validação local da V28: leitura do fallback local em dados/cache_bcb.json e teste controlado da conversão/parse do cache do BCB.
```

</details>

### V29 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V29.md`

- Linhas originais: 1
- Título: VALIDACAO_LOCAL_V29.md

<details>
<summary>Trecho inicial preservado</summary>

```text
Validação local da V29: python aplicacao/principal.py e python scripts/inspecionar_base.py executados com sucesso; tabela de inconsistências e auditoria comparativa dos lotes exibidas no console.
```

</details>

### V30 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V30.md`

- Linhas originais: 3
- Título: VALIDACAO LOCAL V30

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDACAO LOCAL V30
Versão recriada a partir da V29 para materializar o estado lógico da V30.
```

</details>

## Decisão desta etapa

A faixa V001–V030 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de validações sejam consolidadas e um índice-mestre final seja criado.
