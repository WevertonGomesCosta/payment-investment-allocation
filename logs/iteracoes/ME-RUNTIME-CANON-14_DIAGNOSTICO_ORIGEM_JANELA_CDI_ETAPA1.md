# ME-RUNTIME-CANON-14 — Diagnóstico da origem da JanelaConsultaCDI na Etapa 1

## Objetivo

Diagnosticar onde a `JanelaConsultaCDI` é calculada na Etapa 1, por que a rota canônica atual resulta em janela estreita equivalente a 15 datas de CDI, como compará-la à janela ampla de 96 datas usada pela rota baseline e qual menor alteração canônica deve ser proposta.

Esta microetapa é documental/diagnóstica. Não implementa alteração em cache, replay, saída canônica, motor, dados ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 9e377981886597f74e7ad8d9ff0fbad7becc6aca
ULTIMO_MERGE: PR #383 — ME-RUNTIME-CANON-13 decide janela CDI canônica pré-replay
```

## Auditoria pós-merge da ME-RUNTIME-CANON-13

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: already up to date após merge da PR #383
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-14.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis atuais, com cache local atualizado:

```text
relatorio_operacional_v225.xlsx: gerado
Patrimônio líquido atual: 79905.02
Rendimento líquido atual: 964.86
Rendimento líquido atual — reconciliado contra recebidos: 877.86
Ranking top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
Switchings reais: 4
```

Gate V4Z:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
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

A ME-RUNTIME-CANON-14 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Onde a JanelaConsultaCDI nasce

A estrutura formal da Etapa 1 está em `nucleo/entrada_resolvida.py`:

```text
JanelaConsultaCDI:
  data_inicial_consulta
  data_final_consulta
  metadados

PacoteEntradaResolvida:
  janela_consulta_cdi
```

A montagem do pacote de entrada resolvida apenas propaga `pacote_planilha.janela_consulta_cdi` para `PacoteEntradaResolvida.janela_consulta_cdi`.

Portanto, a janela não nasce em `entrada_resolvida.py`; ela nasce antes, no produtor do `PacotePlanilha`.

## Onde a janela é calculada

A janela é calculada em `nucleo/leitor_planilha.py`, pela função:

```text
construir_janela_consulta_cdi(...)
```

Essa função:

```text
1. inicia a lista de datas com a data de referência, quando fornecida;
2. percorre os blocos e abas resolvidos pelo mapa de abas da Etapa 1;
3. usa apenas colunas resolvidas cujo nome estrutural contém "data" ou "vencimento";
4. normaliza datas interpretáveis;
5. define data_inicial_consulta = min(datas);
6. define data_final_consulta = max(datas).
```

A função `carregar_planilha(...)` chama `construir_janela_consulta_cdi(...)` depois de resolver:

```text
mapa_abas_resolvidas
mapa_colunas_resolvidas
quadros_estruturais_resolvidos
```

e armazena o resultado em:

```text
PacotePlanilha.janela_consulta_cdi
```

## Por que a janela resulta em 15 datas

A janela da Etapa 1 é estreita porque o critério atual depende exclusivamente de:

```text
campos resolvidos cujo nome contém "data" ou "vencimento"
```

Esse critério é estrutural e genérico, mas não garante cobertura do replay passado. Em particular, ele pode deixar de incluir datas economicamente necessárias quando:

```text
1. campos relevantes para replay não estão mapeados em mapa_colunas_resolvidas;
2. datas de lotes históricos, pagamentos ou switching não entram como campos resolvidos com nome contendo "data" ou "vencimento";
3. quadros canonizados têm colunas renomeadas de modo que o campo estrutural usado no mapa não capture toda a necessidade temporal;
4. a menor data necessária ao replay vem de dados operacionais já canonizados, não diretamente da janela estrutural de planilha;
5. datas necessárias à idade fiscal/econômica de lotes exauridos dependem de estado pós-replay e não apenas da entrada bruta.
```

O efeito observado foi:

```text
ContextoBaseline.cache_cdi.serie_cdi: 96 datas
ContextoOperacionalCanonico.cache_cdi.serie_cdi: 15 datas
```

A série de 15 datas vem da janela estreita produzida pela Etapa 1. A série de 96 datas vem da janela ampla legada derivada dos dados operacionais.

## Como a janela estreita chega ao cache

Em `nucleo/contexto_baseline.py`, `carregar_contexto_operacional_canonico(...)` passa explicitamente:

```text
janela_consulta_cdi=getattr(pacote_planilha, 'janela_consulta_cdi', None)
```

para:

```text
carregar_cache_cdi_diario(...)
```

Em `nucleo/cache_cdi_bcb.py`, `carregar_cache_cdi_diario(...)` aplica a seguinte decisão:

```text
se janela_consulta_cdi estiver completa:
    usa _datas_relevantes_por_janela_cdi(...)
    origem_janela_consulta = 'janela_consulta_cdi'
senão:
    usa _datas_relevantes(dados_operacionais, data_referencia)
    origem_janela_consulta = 'dados_operacionais_legado'
```

Logo, quando `ContextoOperacionalCanonico` passa a janela estreita, o cache filtra a série para essa janela e gera apenas 15 datas.

## Como a janela ampla de 96 datas é obtida

A janela ampla é obtida pela rota legada `_datas_relevantes(dados_operacionais, data_referencia)` em `cache_cdi_bcb.py`.

Essa função:

```text
1. coleta datas de aplicação do inventário canônico;
2. coleta datas de gastos canônicos;
3. usa a menor dessas datas;
4. ajusta a data inicial para o primeiro dia do mês da menor data;
5. usa a data de referência como data final.
```

Essa política cobre o replay passado porque deriva de dados operacionais canônicos efetivamente consumidos pelo replay.

## Comparação conceitual

```text
JanelaConsultaCDI atual da Etapa 1:
  origem: campos estruturais resolvidos de planilha
  critério: nomes de campos contendo data/vencimento
  vantagem: canônica, auditável, anterior ao cache
  problema: insuficiente para replay passado observado

Janela legada ampla:
  origem: dados_operacionais.inventario_canonico + dados_operacionais.gastos_canonicos
  critério: menor data operacional relevante arredondada ao primeiro dia do mês até data de referência
  vantagem: cobre replay passado atual
  problema: está acoplada ao pós-canonização operacional, não à Etapa 1
```

## Menor alteração canônica proposta

A menor alteração canônica a ser proposta em etapa posterior é ampliar `construir_janela_consulta_cdi(...)` para produzir uma janela CDI que seja, no mínimo, equivalente à necessidade temporal do replay passado.

Direção preferencial:

```text
Adicionar à JanelaConsultaCDI da Etapa 1 um critério explícito de cobertura de replay histórico, incorporando datas das abas/blocos operacionais que alimentam:

1. inventário de lotes;
2. todos os gastos/pagamentos;
3. switching histórico;
4. data de referência;
5. fechamento por fallback encadeado.
```

Regra de segurança proposta:

```text
A data_inicial_consulta deve ser o primeiro dia do mês da menor data economicamente relevante observada nas entradas operacionais canônicas necessárias ao replay.
A data_final_consulta deve ser pelo menos a data de referência.
```

Essa proposta mantém a arquitetura canônica porque a janela continua sendo artefato explícito da Etapa 1, mas passa a carregar a necessidade real do replay.

## Alteração que NÃO deve ser feita agora

Não corrigir por:

```text
1. remover o uso de janela_consulta_cdi no ContextoOperacionalCanonico;
2. fazer ContextoBaseline usar a janela estreita;
3. corrigir saida_canonica.py;
4. corrigir replay passado;
5. forçar cache amplo sem registrar a janela canônica;
6. commitar dados/cache_bcb.json nesta microetapa.
```

## Decisão da ME-RUNTIME-CANON-14

```text
STATUS: ORIGEM_JANELA_CDI_ETAPA1_DIAGNOSTICADA
ORIGEM_FORMAL: PacotePlanilha.janela_consulta_cdi
PRODUTOR: nucleo/leitor_planilha.py::construir_janela_consulta_cdi(...)
CRITERIO_ATUAL: campos resolvidos com nome contendo data/vencimento
EFEITO_ATUAL: janela estreita insuficiente para replay passado
JANELA_AMPLA_REFERENCIA: _datas_relevantes(dados_operacionais, data_referencia)
MENOR_ALTERACAO_CANONICA_PROPOSTA: ampliar construir_janela_consulta_cdi(...) para cobrir datas operacionais necessárias ao replay
CORRIGE_CACHE_CDI: false
CORRIGE_REPLAY: false
CORRIGE_SAIDA_CANONICA: false
ALTERA_CONTEXTOS: false
ALTERA_DADOS: false
ALTERA_REGRA_ECONOMICA: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
ETAPA_5_LIBERADA: false
```

## Próxima ação segura

A próxima microetapa recomendada é:

```text
ME-RUNTIME-CANON-15 — implementar ampliação canônica mínima de JanelaConsultaCDI na Etapa 1
```

Escopo futuro proposto:

```text
nucleo/leitor_planilha.py
logs/iteracoes/*
```

Objetivo futuro:

```text
Ajustar construir_janela_consulta_cdi(...) para incluir explicitamente datas operacionais necessárias ao replay passado, preservando data inicial como primeiro dia do mês da menor data econômica relevante e data final pelo menos igual à data de referência.
```

Critérios de validação futuros:

```text
1. py_compile aprovado;
2. aplicacao/principal.py aprovado;
3. auditar_nucleo_vivo_v4z.py --sem-arquivos aprovado;
4. ContextoOperacionalCanonico.cache_cdi.serie_cdi passa a ter cobertura equivalente à rota baseline;
5. comparação de componentes internos deve reduzir ou eliminar divergência em cache_cdi.serie_cdi;
6. não alterar saída canônica diretamente;
7. não commitar dados/cache_bcb.json junto com a alteração funcional.
```

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```
