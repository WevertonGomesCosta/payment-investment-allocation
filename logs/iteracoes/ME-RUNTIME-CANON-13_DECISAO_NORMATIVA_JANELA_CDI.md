# ME-RUNTIME-CANON-13 — Decisão normativa da janela CDI canônica pré-replay

## Objetivo

Registrar decisão normativa documental sobre qual política de janela CDI deve orientar a rota canônica antes do replay, após a ME-RUNTIME-CANON-12 classificar a causa primária das divergências como diferença de materialização de `cache_cdi.serie_cdi`.

Esta microetapa não implementa alteração em cache, replay, saída canônica, motor, dados ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 8898093186135122c4e1de8e8b6b4538cf0c6360
ULTIMO_MERGE: PR #382 — ME-RUNTIME-CANON-12 classifica causa da divergência do cache CDI
```

## Auditoria pós-merge da ME-RUNTIME-CANON-12

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 9fb770d -> 8898093
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-13.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis após atualização local do cache:

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

A ME-RUNTIME-CANON-13 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Evidência consolidada

A ME-RUNTIME-CANON-11 detalhou:

```text
ContextoBaseline.cache_cdi.serie_cdi: 96 datas
ContextoOperacionalCanonico.cache_cdi.serie_cdi: 15 datas
qtd_ausentes_no_canonico: 81
qtd_ausentes_no_baseline: 0
qtd_valores_divergentes_amostrados: 0
```

A ME-RUNTIME-CANON-12 classificou a causa primária:

```text
CAUSA_PRIMARIA: divergência de política de janela CDI entre ContextoBaseline e ContextoOperacionalCanonico
TIPO: diferença de materialização de insumo temporal antes do replay
CAMADA: cache_cdi.serie_cdi
PRIMEIRO_COMPONENTE_DIVERGENTE: cache_cdi.serie_cdi
DIVERGÊNCIA_DE_VALORES_CDI_NAS_DATAS_COMUNS: não observada na amostra
DIVERGÊNCIA_DE_JANELA: sim
```

## Alternativas avaliadas

### A) Manter `janela_consulta_cdi` estreita no ContextoOperacionalCanonico

Descrição:

```text
Preservar a política atual do ContextoOperacionalCanonico, usando a JanelaConsultaCDI resolvida pela Etapa 1 mesmo quando ela produz janela mais curta que a exigida pelo replay passado.
```

Risco:

```text
replay_passado.log_passado continua divergente
lotes_apos_replay continuam divergentes
valoração de dias úteis/imposto/rendimento continua incompatível com ContextoBaseline
ContextoSaidaCanonicaCompat não pode ser promovido
```

Decisão:

```text
REJEITAR como política normativa suficiente para replay passado.
```

### B) Fazer ContextoBaseline também usar `janela_consulta_cdi`

Descrição:

```text
Reduzir a rota baseline para a janela CDI estreita usada pelo contexto canônico.
```

Risco:

```text
altera a rota oficial atualmente validada
reduz a série usada pelo replay histórico
pode reproduzir as perdas observadas em dias úteis, imposto e rendimento
não preserva a saída oficial
```

Decisão:

```text
REJEITAR para esta frente, pois altera a rota oficial validada.
```

### C) Fazer ContextoOperacionalCanonico usar a janela legada ampla

Descrição:

```text
Alinhar o ContextoOperacionalCanonico ao comportamento atualmente observado e validado do ContextoBaseline, usando a janela ampla derivada de dados operacionais quando a janela da Etapa 1 for insuficiente para o replay passado.
```

Vantagem:

```text
preserva semântica econômica da rota oficial
mantém compatibilidade com replay histórico
atua na primeira divergência causal
não corrige sintoma em saída canônica
```

Risco:

```text
reintroduzir cálculo legado sem amarra normativa explícita se implementado de forma direta e sem documentação
```

Decisão:

```text
APROVAR COMO DIREÇÃO NORMATIVA, desde que implementada como política canônica explícita de janela necessária ao replay, e não como fallback legado informal.
```

### D) Ampliar ou redefinir a JanelaConsultaCDI da Etapa 1 para cobrir toda necessidade histórica do replay

Descrição:

```text
Manter a rota canônica baseada em JanelaConsultaCDI, mas corrigir a definição da própria janela para que cubra todo o período necessário para replay passado, lotes históricos, pagamentos já realizados e data de referência.
```

Vantagem:

```text
preserva a arquitetura canônica da Etapa 1
remove a dependência de fallback legado por dados operacionais
faz a janela CDI ser artefato resolvido e auditável
mantém coerência com a limpeza das Etapas 1–4
```

Risco:

```text
exige microcorreção em camada de entrada/janela ou resolução estrutural
precisa provar equivalência com a janela ampla atual antes de promover
```

Decisão:

```text
APROVAR COMO POLÍTICA NORMATIVA PREFERENCIAL.
```

## Decisão normativa da ME-RUNTIME-CANON-13

A política normativa recomendada para a rota canônica pré-replay é:

```text
A JanelaConsultaCDI canônica deve cobrir a janela temporal completa necessária ao replay passado e à valoração auditável dos lotes, incluindo:

1. a menor data relevante de aplicação/recebimento/lote usada pelo replay;
2. as datas de pagamentos históricos já realizados;
3. as datas de switching histórico efetivo quando impactarem lotes de origem/destino;
4. a data de referência da execução;
5. dias úteis necessários ao fechamento por fallback encadeado quando o fator explícito do próprio dia de referência ainda não existir.
```

Portanto:

```text
A rota canônica não deve usar uma janela CDI menor que a janela necessária ao replay passado.
A janela CDI canônica deve ser resolvida antes do cache e passada de forma explícita ao ContextoOperacionalCanonico.
A equivalência com ContextoBaseline deve ser provada antes de qualquer promoção de ContextoSaidaCanonicaCompat.
```

## Decisão operacional

```text
STATUS: DECISAO_NORMATIVA_JANELA_CDI_PRE_REPLAY_REGISTRADA
POLITICA_PREFERENCIAL: ampliar/redefinir JanelaConsultaCDI canônica para cobrir toda necessidade histórica do replay
POLITICA_COMPATIVEL_SECUNDARIA: ContextoOperacionalCanonico pode usar janela ampla equivalente à baseline apenas como transição comprovada
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
ME-RUNTIME-CANON-14 — diagnóstico da origem de JanelaConsultaCDI e proposta de ampliação canônica
```

Objetivo futuro:

```text
Localizar onde a JanelaConsultaCDI é calculada na Etapa 1, medir por que ela resulta em 15 datas, comparar com a janela ampla de 96 datas e propor a menor alteração canônica capaz de cobrir o replay passado sem alterar ainda a regra econômica.
```

Critério de parada:

```text
Não alterar cache, replay, saída ou motor antes de localizar exatamente a regra de cálculo da JanelaConsultaCDI e provar qual data inicial/final ela deve conter.
```

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```
