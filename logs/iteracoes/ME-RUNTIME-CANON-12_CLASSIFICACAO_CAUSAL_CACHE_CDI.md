# ME-RUNTIME-CANON-12 — Classificação causal primária da divergência em cache_cdi.serie_cdi

## Objetivo

Classificar causalmente a divergência primária detectada pela ME-RUNTIME-CANON-11 em `cache_cdi.serie_cdi`, investigando por que `ContextoBaseline` materializa 96 datas e `ContextoOperacionalCanonico` materializa 15 datas.

Esta microetapa é documental/diagnóstica. Não corrige replay, saída canônica, motor, cache, dados ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 9fb770d5bef68a0171420bbb2206564202787232
ULTIMO_MERGE: PR #381 — ME-RUNTIME-CANON-11 detalha divergências internas dos contextos
```

## Auditoria pós-merge da ME-RUNTIME-CANON-11

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 618390e -> 9fb770d
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação importante:

```text
dados/cache_bcb.json foi modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-11 nem à ME-RUNTIME-CANON-12.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis após atualização do cache local:

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

A ME-RUNTIME-CANON-12 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Evidência da ME-RUNTIME-CANON-11

O detalhamento completo retornou:

```text
ok=False
componentes=3
componentes_com_divergencia=3
```

Para `cache_cdi.serie_cdi`:

```text
qtd_baseline: 96
qtd_canonico: 15
qtd_ausentes_no_canonico: 81
qtd_ausentes_no_baseline: 0
qtd_valores_divergentes_amostrados: 0
```

Classificação da evidência:

```text
O conjunto canônico é subconjunto do conjunto baseline.
Não há divergência de valores nas datas comuns amostradas.
A diferença primária é de janela/materialização, não de fator CDI divergente.
```

## Análise causal no código

A divergência é explicada pela diferença explícita de chamada em `nucleo/contexto_baseline.py`.

### ContextoOperacionalCanonico

`carregar_contexto_operacional_canonico(...)` chama:

```python
cache_cdi = carregar_cache_cdi_diario(
    dados_operacionais,
    pacote_config.conteudo,
    data_referencia=contexto_execucao.data_referencia,
    raiz_repositorio=pacote_config.raiz_repositorio,
    janela_consulta_cdi=getattr(pacote_planilha, 'janela_consulta_cdi', None),
)
```

Isto força `carregar_cache_cdi_diario(...)` a usar a janela resolvida da Etapa 1 quando disponível.

### ContextoBaseline

`carregar_contexto_baseline(...)` chama:

```python
cache_cdi = carregar_cache_cdi_diario(
    dados_operacionais,
    pacote_config.conteudo,
    data_referencia=contexto_execucao.data_referencia,
    raiz_repositorio=pacote_config.raiz_repositorio,
)
```

Como não passa `janela_consulta_cdi`, `carregar_cache_cdi_diario(...)` cai no cálculo legado por dados operacionais.

## Mecanismo causal em `cache_cdi_bcb.py`

`carregar_cache_cdi_diario(...)` resolve a janela em duas rotas:

```text
1. Se janela_consulta_cdi for informada e completa:
   origem_janela_consulta = 'janela_consulta_cdi'
   data_ini/data_fim vêm de _datas_relevantes_por_janela_cdi(...)

2. Caso contrário:
   origem_janela_consulta = 'dados_operacionais_legado'
   data_ini/data_fim vêm de _datas_relevantes(...)
```

Portanto:

```text
ContextoOperacionalCanonico: janela_consulta_cdi -> 15 datas
ContextoBaseline: dados_operacionais_legado -> 96 datas
```

## Classificação causal primária

```text
CAUSA_PRIMARIA: divergência de política de janela CDI entre ContextoBaseline e ContextoOperacionalCanonico
TIPO: diferença de materialização de insumo temporal antes do replay
CAMADA: cache_cdi.serie_cdi
PRIMEIRO_COMPONENTE_DIVERGENTE: cache_cdi.serie_cdi
DIVERGÊNCIA_DE_VALORES_CDI_NAS_DATAS_COMUNS: não observada na amostra
DIVERGÊNCIA_DE_JANELA: sim
EFEITO_A_JUSANTE: replay_passado.log_passado e replay_passado.lotes_apos_replay divergem em dias úteis, fator_acumulado, imposto, bruto e líquido
```

## Interpretação operacional

A divergência não deve ser corrigida em:

```text
saida_canonica.py
saida_observavel.py
construir_saida_canonica_v17_c7.py
replay_passado_controlado.py
motor
ledger
ranking
```

Antes de qualquer correção funcional, é necessário decidir qual política de janela CDI é normativa para a rota canônica:

```text
A) manter janela_consulta_cdi da Etapa 1 no ContextoOperacionalCanonico;
B) fazer ContextoBaseline também usar janela_consulta_cdi;
C) fazer ContextoOperacionalCanonico usar a janela legada ampla;
D) ampliar ou redefinir a JanelaConsultaCDI da Etapa 1 para cobrir toda a necessidade histórica do replay.
```

## Decisão da ME-RUNTIME-CANON-12

```text
STATUS: CAUSA_PRIMARIA_CLASSIFICADA
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
ME-RUNTIME-CANON-13 — decisão normativa da janela CDI canônica pré-replay
```

Objetivo futuro:

```text
Definir, sem implementar inicialmente, qual política de janela CDI deve ser normativa para o ContextoOperacionalCanonico antes do replay.
```

Critério de parada:

```text
Não alterar cache, replay ou saída antes de decidir a política normativa de janela CDI.
```

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```
