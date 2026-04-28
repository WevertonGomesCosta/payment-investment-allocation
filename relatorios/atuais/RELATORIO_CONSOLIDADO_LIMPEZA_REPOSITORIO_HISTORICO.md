# Relatório consolidado — histórico de limpeza do repositório

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/limpeza_repositorio/` em um único relatório atual, permitindo avaliar a remoção da pasta granular.

- Arquivos consolidados: 6
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/limpeza_repositorio/CORRECAO_COMPATIBILIDADE_PANDAS_V199.md` | 36 | Correção de compatibilidade pandas 3.0 — V199 |
| `relatorios/historico/limpeza_repositorio/CORRECAO_SAIDA_OFICIAL_V192.md` | 34 | Correção operacional da saída oficial — V192 |
| `relatorios/historico/limpeza_repositorio/ETAPA5_LIMPEZA_LEGADO_DIAGNOSTICO_V187.md` | 27 | Etapa 5 — limpeza residual final do legado diagnóstico ativo (V187) |
| `relatorios/historico/limpeza_repositorio/MANIFESTO_REBAIXAMENTO_DOCUMENTAL_V201.md` | 10 | Manifesto de rebaixamento documental — V201 |
| `relatorios/historico/limpeza_repositorio/NORMALIZACAO_CAMINHOS_SAIDAS_SCRIPTS_V186.md` | 13 | Normalização final dos caminhos ativos de saída e scripts diagnósticos canônicos — V186 |
| `relatorios/historico/limpeza_repositorio/RESUMO_ATUALIZACAO_V190.md` | 27 | Atualização V190 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Normalização de caminhos | Histórico de ajustes em caminhos de scripts e saídas foi preservado. |
| Limpeza de legado diagnóstico | Registro de limpeza anterior foi preservado como referência, sem manter arquivos granulares. |
| Saída oficial | Correções relacionadas à saída oficial foram preservadas como trilha histórica. |
| Compatibilidade técnica | Correção relacionada a pandas/compatibilidade foi registrada. |
| Rebaixamento documental | A decisão de rebaixamento documental foi mantida como contexto histórico. |

## Detalhe consolidado por arquivo

### `relatorios/historico/limpeza_repositorio/CORRECAO_COMPATIBILIDADE_PANDAS_V199.md`

- Título: Correção de compatibilidade pandas 3.0 — V199
- Linhas originais: 36

<details>
<summary>Trecho inicial preservado</summary>

```text
# Correção de compatibilidade pandas 3.0 — V199
## Escopo
Correção de incompatibilidade com pandas 3.0 detectada na execução local, mantendo intactos
contrato mestre, modelo oficial, núcleo econômico e estrutura diária por pacotes.
## Problema
Em `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`, linha 580,
a coluna `mudou_vs_v103` era inicializada com valores string (lote_final_planejamento
como string via `.map(lambda ...)`), criando uma coluna `StringDtype`.
Nas linhas subsequentes (587–591), a mesma coluna recebia atribuições booleanas
via `.loc[mask, 'mudou_vs_v103'] = <Series booleana>`.
O pandas 3.0 passou a rejeitar atribuição de booleanos em coluna `StringDtype`,
lançando `TypeError: Invalid value for dtype 'str'. Value should be a string or missing value`.
## Correção
Substituição da inicialização via lambda string por `False` (booleano), alinhando o dtype
da coluna ao seu uso efetivo como flag booleana em todo o restante do código:
- `.sum()` para contagem de mudanças;
- comparação `== True` para filtragem.
A semântica é preservada: linhas sem pagamento_id correspondente no mapa v103
```

</details>

### `relatorios/historico/limpeza_repositorio/CORRECAO_SAIDA_OFICIAL_V192.md`

- Título: Correção operacional da saída oficial — V192
- Linhas originais: 34

<details>
<summary>Trecho inicial preservado</summary>

```text
# Correção operacional da saída oficial — V192
## Escopo
Correção apenas da camada observável, mantendo intactos contrato mestre, modelo oficial, núcleo econômico e estrutura diária por pacotes.
## Ajustes aplicados
- atualização do versionamento operacional para V192;
- correção da classificação de lotes na situação atual do console e do `.xlsx`:
  - lotes futuros não entram mais em `lotes exauridos` nem em `lotes ativos`;
  - lotes com `saldo_bruto`, `saldo_liquido` ou `saldo_rem` dentro do limiar são tratados como exauridos/resolvidos;
- redução de poluição nas tabelas da situação atual do console com limite de linhas exibidas;
- reescrita do bloco `SWITCHINGS CANDIDATOS / CLASSIFICADOS` do console para usar a priorização oficial do ranking vigente, independente de datas de pagamento;
- renomeação do relatório oficial para `relatorio_operacional_v192.xlsx`;
- simplificação da aba `Switching` do `.xlsx` para refletir primeiro os destinos priorizados pelo ranking oficial;
- remoção da aba legada `Melhores produtos` do relatório final.
## Validação local
- `compileall` passou;
- execução curta do console avançou até a situação atual sem novo traceback;
- o console passou a exibir:
  - destinos priorizados do ranking vigente no bloco de switching;
```

</details>

### `relatorios/historico/limpeza_repositorio/ETAPA5_LIMPEZA_LEGADO_DIAGNOSTICO_V187.md`

- Título: Etapa 5 — limpeza residual final do legado diagnóstico ativo (V187)
- Linhas originais: 27

<details>
<summary>Trecho inicial preservado</summary>

```text
# Etapa 5 — limpeza residual final do legado diagnóstico ativo (V187)
## Escopo aplicado
Limpeza restrita à camada de diagnóstico histórico ativo, com foco em:
- `saidas/diagnostico/`
- trilhas antigas superseded ainda competindo visualmente com a camada ativa
## O que foi feito
- todo o conteúdo legado de `saidas/diagnostico/`, exceto o `README.md`, foi rebaixado para `saidas/historico/diagnostico_legado/`;
- os arquivos foram organizados em subpastas por finalidade:
  - `auditorias/`
  - `grades/`
  - `motores_experimentais/`
  - `pagamentos_legado/`
  - `comparadores_legado/`
  - `probes/`
- `saidas/diagnostico/` foi mantido como caminho canônico apenas para diagnósticos correntes e temporários;
- `saidas/README.md` e `saidas/diagnostico/README.md` foram atualizados para refletir a nova navegação;
- resíduos efêmeros de `compileall` foram removidos antes da validação final.
## Resultado esperado
```

</details>

### `relatorios/historico/limpeza_repositorio/MANIFESTO_REBAIXAMENTO_DOCUMENTAL_V201.md`

- Título: Manifesto de rebaixamento documental — V201
- Linhas originais: 10

<details>
<summary>Trecho inicial preservado</summary>

```text
# Manifesto de rebaixamento documental — V201
Documentos versionados antigos que estavam na raiz foram movidos para este diretório na limpeza segura V201.
Eles ficam preservados para rastreabilidade, mas não possuem autoridade normativa ativa diante de `relatorios/atuais/`.
Arquivos rebaixados:
- `RESUMO_ATUALIZACAO_V190.md`
- `CORRECAO_SAIDA_OFICIAL_V192.md`
- `CORRECAO_COMPATIBILIDADE_PANDAS_V199.md`
```

</details>

### `relatorios/historico/limpeza_repositorio/NORMALIZACAO_CAMINHOS_SAIDAS_SCRIPTS_V186.md`

- Título: Normalização final dos caminhos ativos de saída e scripts diagnósticos canônicos — V186
- Linhas originais: 13

<details>
<summary>Trecho inicial preservado</summary>

```text
# Normalização final dos caminhos ativos de saída e scripts diagnósticos canônicos — V186
A V186 consolida:
- `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- `saidas/operacional/` como compatibilidade residual de caminho, sem novos artefatos oficiais;
- `saidas/historico/compatibilidade_operacional/` como destino dos artefatos operacionais duplicados rebaixados;
- `saidas/historico/raiz_rebaixada/` como destino dos artefatos antigos antes misturados na raiz de `saidas/`;
- `scripts/diagnostico/` como caminho canônico do tooling de release e inspeção;
- `scripts/historico_raiz/` como destino das cópias antigas movidas da raiz de `scripts/`;
- atualização do `README`, `LEIA-ME_OPERACIONAL`, `INDICE_RELATORIOS`, `saidas/README.md` e `scripts/README.md`;
- remoção de resíduos efêmeros (`__pycache__`, `.pyc`) do pacote.
Nenhuma alteração foi feita no contrato mestre, no modelo oficial, no núcleo econômico ou na estrutura diária por pacotes congelada.
```

</details>

### `relatorios/historico/limpeza_repositorio/RESUMO_ATUALIZACAO_V190.md`

- Título: Atualização V190
- Linhas originais: 27

<details>
<summary>Trecho inicial preservado</summary>

```text
# Atualização V190
## Ajustes aplicados
- atualização de `dados/cache_bcb.json` com o arquivo enviado pelo usuário;
- limpeza da saída do console, removendo blocos históricos/poluídos e promovendo apenas:
  - execução/base;
  - amostras operacionais de pagamentos;
  - ranqueamento oficial da carteira;
  - switchings candidatos/classificados;
  - situação atual;
- normalização do relatório operacional `.xlsx` para manter apenas as abas principais da trilha oficial e incorporar as abas do ranking estabilizado;
- tratamento mais conservador do lote residual baixo na situação atual, passando a zerar operacionalmente também quando `saldo_liquido` ou `saldo_rem` estiverem dentro do limiar.
## Estrutura alvo do `.xlsx`
- Extrato Passado
- Extrato Futuro
- Switching
- Carteira
- Situação Atual
- Ranking_Completo
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/limpeza_repositorio/` pode ser removida se a auditoria local confirmar que não há dependência operacional desses documentos granulares.
