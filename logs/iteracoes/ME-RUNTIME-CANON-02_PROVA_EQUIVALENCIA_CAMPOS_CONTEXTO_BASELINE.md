# ME-RUNTIME-CANON-02 — Prova de equivalência dos campos consumidos de ContextoBaseline

## Objetivo

Inventariar os campos efetivamente consumidos de `ContextoBaseline` pela rota runtime atual e avaliar a equivalência com `ContextoOperacionalCanonico`, sem migrar runtime.

A etapa cobre:

```text
aplicacao/principal.py
aplicacao/console/*
nucleo/gerar_planilha_operacional.py
nucleo/construir_saida_canonica_v17_c7.py
nucleo/matriz_elegibilidade_fontes_s7b.py
nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
```

## Baseline de entrada

```text
BASELINE: main
HEAD: dfa401f575ae5bebb27432b847a02697fbff7bbb
ULTIMO_MERGE: PR #371 — ME-RUNTIME-CANON-01 auditoria da rota runtime versionada
```

## Escopo permitido

```text
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
scripts/diagnostico/*
saidas/*
```

Esta microetapa não altera motor, replay, ledger, ranking, saída canônica, XLSX, console ou regra econômica.

## Auditoria de entrada informada

Validação local em `main` antes da abertura:

```text
git checkout main: aprovado
git pull --ff-only: atualizado
status --short: vazio
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Resultado V4Z informado:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Campos declarados em `ContextoBaseline`

`ContextoBaseline` contém 26 campos:

```text
pacote_config
execucao
calendario_financeiro
pacote_planilha
validacao_pre_execucao
carteira_canonica
dados_operacionais
recebidos_auditaveis
fontes_elegiveis_pagamento
saldo_disponivel_geral
decisao_local_v1
cache_cdi
pacote_entrada_resolvida
auditoria_pacote_entrada_resolvida
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
recomputacao_sequencial_central_v1
triagem_motor
ranking_carteira
nucleo_financeiro
replay_passado
tabela_iof
faixas_ir
```

`ContextoOperacionalCanonico` contém 20 campos:

```text
pacote_config
execucao
calendario_financeiro
pacote_planilha
pacote_entrada_resolvida
auditoria_pacote_entrada_resolvida
validacao_pre_execucao
carteira_canonica
dados_operacionais
recebidos_auditaveis
fontes_elegiveis_pagamento
saldo_disponivel_geral
cache_cdi
nucleo_financeiro
replay_passado
ranking_carteira
tabela_iof
faixas_ir
metadados
```

## Interseção estrutural

Campos de `ContextoBaseline` também existentes em `ContextoOperacionalCanonico`:

```text
pacote_config
execucao
calendario_financeiro
pacote_planilha
validacao_pre_execucao
carteira_canonica
dados_operacionais
recebidos_auditaveis
fontes_elegiveis_pagamento
saldo_disponivel_geral
cache_cdi
pacote_entrada_resolvida
auditoria_pacote_entrada_resolvida
ranking_carteira
nucleo_financeiro
replay_passado
tabela_iof
faixas_ir
```

Campos exclusivos de `ContextoBaseline`:

```text
decisao_local_v1
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
recomputacao_sequencial_central_v1
triagem_motor
```

Campo exclusivo de `ContextoOperacionalCanonico`:

```text
metadados
```

## Consumo direto por `aplicacao/principal.py`

`aplicacao/principal.py` não acessa campos internos por atributo. Ele consome o objeto inteiro em três pontos:

```text
construir_saida_canonica_com_switching_v17_c7(contexto_baseline, versao=VERSAO_BASELINE)
construir_matriz_elegibilidade_fontes_s7b(contexto_baseline, data_referencia=saida_canonica.data_referencia)
render_console(contexto_baseline, saida_canonica)
gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

Classificação:

```text
CONSUMO_DIRETO_ATRIBUTO: não
CONSUMO_INDIRETO_OBJETO_COMPLETO: sim
RISCO_SUBSTITUICAO_DIRETA: alto
```

## Consumo por `aplicacao/console/principal.py`

Campos diretamente acessados pelo console:

```text
pacote_config
execucao
pacote_planilha
carteira_canonica
cache_cdi
dados_operacionais
ranking_carteira
```

Todos esses campos existem também em `ContextoOperacionalCanonico`.

Porém, o console passa o contexto inteiro para funções observáveis:

```text
construir_amostras_pagamentos_operacionais(..., contexto=contexto_baseline)
construir_switchings_observaveis(contexto_baseline, saida_canonica, ...)
construir_linhas_lotes_consolidados(contexto_baseline, saida_canonica, ...)
construir_linhas_lotes_id_curta(contexto_baseline, saida_canonica, ...)
construir_linhas_lotes_valores_curta(contexto_baseline, saida_canonica, ...)
construir_resumo_patrimonio_total_lotes(contexto_baseline, saida_canonica, ...)
construir_pacote_saida_observavel_temporal(contexto_baseline, saida_canonica, ...)
```

Classificação:

```text
CAMPOS_DIRETOS_EQUIVALENTES: sim
CONSUMO_INDIRETO_EXIGE_INVENTARIO: sim
RISCO_SUBSTITUICAO_CONSOLE_ISOLADO: médio-alto
```

## Consumo por `nucleo/gerar_planilha_operacional.py`

Campos diretamente acessados na geração XLSX:

```text
pacote_config
ranking_carteira
```

Além disso, a planilha passa o contexto inteiro para funções observáveis e de situação atual:

```text
construir_linhas_lotes_consolidados(contexto, saida, ...)
construir_pacote_saida_observavel_temporal(contexto, saida, ...)
construir_switchings_observaveis(contexto, saida, ...)
construir_blocos_situacao_atual(contexto, saida, ...)
```

Campos diretamente acessados aqui também existem em `ContextoOperacionalCanonico`, mas o consumo indireto pela camada observável ainda impede substituição direta.

Classificação:

```text
CAMPOS_DIRETOS_EQUIVALENTES: sim
CONSUMO_INDIRETO_EXIGE_INVENTARIO: sim
RISCO_SUBSTITUICAO_XLSX_ISOLADO: médio-alto
```

## Consumo por `nucleo/construir_saida_canonica_v17_c7.py`

O wrapper `construir_saida_canonica_v17_c7.py` não acessa campos diretamente. Ele repassa o contexto para:

```text
nucleo.saida_canonica.construir_saida_canonica(contexto, versao=versao)
nucleo.saida_canonica_switching_v17_c7.integrar_switchings_materializados_saida_canonica_v17_f0_p1(saida_base, contexto)
```

Classificação:

```text
CONSUMO_DIRETO_ATRIBUTO: não
CONSUMO_INDIRETO_OBJETO_COMPLETO: sim
RISCO_SUBSTITUICAO_DIRETA: alto
```

## Consumo por `nucleo/matriz_elegibilidade_fontes_s7b.py`

O módulo S7B consome o contexto inteiro indiretamente ao reconstruir internamente a saída canônica:

```text
saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
```

Depois consome `saida.lotes_ativos`, `saida.lotes_exauridos` e `saida.data_referencia`.

Classificação:

```text
CONSUMO_DIRETO_ATRIBUTO_CONTEXTO: não observado
CONSUMO_INDIRETO_VIA_RECONSTRUCAO_SAIDA: sim
RISCO_SUBSTITUICAO_DIRETA: alto
ACHADO_PRINCIPAL: S7B não precisa semanticamente do contexto se receber saida_canonica_preconstruida
```

## Consumo por `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py`

O módulo S7C não consome `ContextoBaseline`. Ele consome:

```text
saida_canonica
matriz_elegibilidade
```

E altera `saida_canonica.extrato_futuro` in-place.

Classificação:

```text
CONSUME_CONTEXT_BASELINE: não
DEPENDE_DA_SAIDA_CANONICA: sim
RISCO_SUBSTITUICAO_CONTEXTO: baixo
RISCO_ORDEM_APLICACAO: alto
```

## Campos mínimos de ContextoBaseline necessários para rota atual

### Necessários diretamente por console/XLSX

```text
pacote_config
execucao
pacote_planilha
carteira_canonica
cache_cdi
dados_operacionais
ranking_carteira
```

### Necessários indiretamente por saída canônica e observável

```text
calendario_financeiro
fontes_elegiveis_pagamento
saldo_disponivel_geral
nucleo_financeiro
replay_passado
tabela_iof
faixas_ir
carteira_canonica
ranking_carteira
cache_cdi
pacote_config
execucao
```

### Campos exclusivos de ContextoBaseline ainda não provados como dispensáveis

```text
decisao_local_v1
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
recomputacao_sequencial_central_v1
triagem_motor
```

Estes campos não estão em `ContextoOperacionalCanonico` e devem ser tratados antes de qualquer substituição de contexto.

## Resultado da prova de equivalência

| Bloco | Campos diretos equivalentes? | Campos indiretos equivalentes? | Pode substituir agora? |
|---|---:|---:|---:|
| `aplicacao/principal.py` | não aplicável | não provado | não |
| `aplicacao/console/principal.py` | sim | não provado | não |
| `nucleo/gerar_planilha_operacional.py` | sim | não provado | não |
| `nucleo/construir_saida_canonica_v17_c7.py` | não aplicável | não provado | não |
| `nucleo/matriz_elegibilidade_fontes_s7b.py` | não aplicável | pode ser eliminado via parâmetro `saida_canonica_preconstruida` | não nesta etapa |
| `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py` | não consome contexto | sim | não aplicável |

## Decisão

```text
STATUS: PROVA_EQUIVALENCIA_DOCUMENTAL_REGISTRADA
TROCAR_CONTEXT_BASELINE_AGORA: false
CRIAR_ADAPTADOR_AGORA: false
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
```

## Sequência segura revisada

1. `ME-RUNTIME-CANON-03` — Corrigir S7B para aceitar opcionalmente `saida_canonica_preconstruida`, eliminando a dupla construção de saída sem alterar saída observável.
2. `ME-RUNTIME-CANON-04` — Remover `VERSAO_BASELINE = "V225"` local da S7B e usar `nucleo.identidade_baseline.VERSAO_BASELINE` ou argumento explícito.
3. `ME-RUNTIME-CANON-05` — Auditar consumo indireto dos campos exclusivos de `ContextoBaseline` em `saida_canonica.py` e `saida_observavel.py`.
4. `ME-RUNTIME-CANON-06` — Criar adaptador canônico compatível, se necessário, sem substituir runtime principal.
5. `ME-RUNTIME-CANON-07` — Só então avaliar substituição de `carregar_contexto_baseline()`.

## Validação esperada

Como a ME-RUNTIME-CANON-02 é documental, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```
