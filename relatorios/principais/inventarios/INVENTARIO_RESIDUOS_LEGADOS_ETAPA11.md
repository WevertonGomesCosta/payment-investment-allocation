# INVENTARIO-RESIDUOS-LEGADOS-ETAPA11-01

## 1. Identificação

- **Frente:** `INVENTARIO-RESIDUOS-LEGADOS-ETAPA11-01`
- **Natureza:** inventário documental não executivo
- **Objetivo:** registrar resíduos legados remanescentes após os PRs #491 e #492 para subsidiar a Etapa 11 — Limpeza e Depreciação Controlada.
- **Escopo:** classificação documental de rotas, módulos, funções e artefatos legados ou transitórios.
- **Fora do escopo:** remoção de código, alteração de runtime, reativação de rotas legadas, mudança de contratos, alteração de dados/cache, alteração de console, alteração de XLSX.

Este inventário não autoriza remoção automática. Ele registra evidências e condições de preservação/depreciação para que a Etapa 11 deixe de depender de classificação limitada por ausência de inventário auxiliar.

---

## 2. Vocabulário de classificação

| Classe operacional | Significado | Remoção automática autorizada? |
|---|---|---:|
| `dependencia_viva` | Elemento ainda necessário para a rota oficial ou para execução standalone ainda existente. | Não |
| `compatibilidade_transitoria` | Elemento não desejado como arquitetura final, mas ainda necessário para transição, fallback explícito, console standalone ou blocos não materializados oficialmente. | Não |
| `diagnostico_preservado` | Elemento diagnóstico, histórico ou auditável, mantido fora do produto oficial padrão. | Não |
| `candidato_futuro_depreciacao` | Elemento que poderá ser removido somente depois que não houver dependência viva e houver frente específica de depreciação. | Não |
| `rota_oficial_preservada` | Elemento da cadeia oficial atual que deve ser mantido. | Não |

Mapeamento sugerido para a Etapa 11:

| Classe operacional | Classe interna sugerida da Etapa 11 |
|---|---|
| `rota_oficial_preservada` | `rota_oficial_preservada` |
| `dependencia_viva` | `bloqueado_dependencia_ativa` |
| `compatibilidade_transitoria` | `avaliacao_remocao_futura` com dependência ativa |
| `diagnostico_preservado` | `historico_preservado` ou `legado_candidato_depreciacao` sem remoção automática |
| `candidato_futuro_depreciacao` | `legado_candidato_depreciacao` sem remoção automática |

---

## 3. Inventário de resíduos e rotas relacionadas

| ID | Local | Tipo | Classe operacional | Evidência/uso atual | Condição de preservação | Condição futura para depreciação | Remoção automática |
|---|---|---|---|---|---|---|---:|
| `OFICIAL-PRINCIPAL-01` | `aplicacao/principal.py` | rota principal | `rota_oficial_preservada` | Executa cadeia Etapas 5–11 e gera console/XLSX via `PacoteSaidaObservavelOficial`. | Sempre preservar enquanto for ponto de entrada oficial. | Não se aplica. | Não |
| `CONSOLE-STANDALONE-V17-S7-01` | `aplicacao/console/principal.py` | fallback/standalone | `dependencia_viva` | Quando executado sem `pacote_saida_observavel_oficial`, ainda constrói saída V17/S7 e aplica matriz S7C. | Preservar até existir console standalone oficial baseado em Etapas 5–9. | Migrar `main()` standalone para rota oficial ou desativar execução standalone antiga. | Não |
| `CONSOLE-IMPORTS-LEGADOS-01` | `aplicacao/console/principal.py` | importações | `compatibilidade_transitoria` | Importa `construir_saida_canonica_v17_c7`, `matriz_elegibilidade_fontes_s7b`, `integracao_matriz_elegibilidade_pagamentos_s7c`, `pacote_saida_observavel_temporal` e `saida_observavel`. | Preservar enquanto console standalone depender desses módulos. | Remover importações após migração do console standalone e Situação Atual rica. | Não |
| `CONSOLE-OFICIAL-RETURN-01` | `aplicacao/console/principal.py` | proteção oficial | `rota_oficial_preservada` | Quando recebe pacote oficial sem saída legada, renderiza seções oficiais e retorna antes de seções antigas. | Preservar como barreira contra fallback legado no produto oficial. | Não se aplica. | Não |
| `CONSOLE-SITUACAO-ANTIGA-01` | `aplicacao/console/principal.py` | helpers antigos | `compatibilidade_transitoria` | `_render_situacao_atual_operacional` ainda depende de helpers antigos de lotes, patrimônio e recebidos. | Preservar até Situação Atual rica nascer canonicamente nas Etapas corretas. | Depreciar após formalizar e implementar Situação Atual rica em Etapas 5/6/8/9. | Não |
| `XLSX-DIAGNOSTICO-U7-FIFO-01` | `nucleo/gerar_planilha_operacional.py` | funções diagnósticas | `diagnostico_preservado` | Define abas e CSVs diagnósticos U7/FIFO, mas a rota oficial usa `incluir_abas_diagnosticas=False`. | Preservar enquanto diagnósticos forem úteis e bloqueados fora do modo oficial. | Remover somente após confirmação de ausência de uso e registro histórico suficiente. | Não |
| `XLSX-FALLBACK-BLOQUEADO-01` | `nucleo/gerar_planilha_operacional.py` | proteção oficial | `rota_oficial_preservada` | Bloqueia fallback silencioso V17/S7 quando não há `pacote_saida_observavel_oficial`. | Preservar. | Não se aplica. | Não |
| `XLSX-COMPAT-TEMPORAL-01` | `nucleo/gerar_planilha_operacional.py` | compatibilidade | `compatibilidade_transitoria` | `usar_compatibilidade_temporal` ainda monta pacote temporal se `saida.extrato_futuro` existir. | Preservar enquanto houver consumidores de `PacoteSaidaCanonica` antigo. | Remover após eliminação de consumidores do pacote antigo e migração de Situação Atual. | Não |
| `PACOTE-OBS-TEMPORAL-01` | `nucleo/pacote_saida_observavel_temporal.py` | pacote transitório | `compatibilidade_transitoria` | Mantém versão `V17-F0-V.4U`, saldos de replay, valores sacados, lotes ativos/exauridos e auditorias de migração. | Preservar até lotes/patrimônio/rendimento com saques nascerem na cadeia oficial. | Depreciar após Etapas 5/6/8/9 materializarem esses blocos. | Não |
| `SAIDA-OBSERVAVEL-ANTIGA-01` | `nucleo/saida_observavel.py` | helpers observáveis antigos | `compatibilidade_transitoria` | Contém helpers de lotes, patrimônio, recebidos, switching e fallback observável. | Preservar enquanto Situação Atual rica e patrimônio não forem oficiais. | Migrar campos úteis para Etapas oficiais e depois depreciar. | Não |
| `SAIDA-CANONICA-V17-C7-01` | `nucleo/construir_saida_canonica_v17_c7.py` | wrapper legado | `candidato_futuro_depreciacao` | Constrói `PacoteSaidaCanonica` antigo e integra switchings materializados V17. Ainda é usado pelo console standalone/S7. | Preservar enquanto houver dependência standalone ativa. | Remover após console standalone e S7 não dependerem dele. | Não |
| `SAIDA-CANONICA-ANTIGA-01` | `nucleo/saida_canonica.py` | pacote antigo | `candidato_futuro_depreciacao` | Define `PacoteSaidaCanonica`, métodos antigos de console e campos extensos de switching/pós-switching/saldo temporal. | Preservar por alto risco de dependência transitória. | Remover apenas após inventário confirmar ausência total de consumidores vivos. | Não |
| `MATRIZ-S7B-01` | `nucleo/matriz_elegibilidade_fontes_s7b.py` | matriz legada/transitória | `compatibilidade_transitoria` | Pode construir saída V17 se não receber saída pré-construída; ainda atende console standalone. | Preservar até decisão formal sobre S7B. | Depreciar após substituição por estrutura oficial ou preservação histórica. | Não |
| `INTEGRACAO-S7C-01` | `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py` | integração legada/transitória | `compatibilidade_transitoria` | Aplicada pelo console standalone para fluxo de pagamentos S7C. | Preservar enquanto console standalone usar S7C. | Depreciar junto da migração do console standalone. | Não |
| `CSV-U7-DIAG-01` | `saidas/diagnostico/saida_operacional_pagamentos_v17_f0_u3_*.csv` | artefatos diagnósticos esperados | `diagnostico_preservado` | Exportador possui leitura condicional desses CSVs para abas diagnósticas. | Preservar apenas como diagnóstico, nunca como fonte oficial. | Remover referência após inventário histórico e eliminação das abas diagnósticas U7. | Não |
| `LOGS-ITERACOES-LEGADOS-01` | `logs/iteracoes/*.md` | histórico | `diagnostico_preservado` | Logs preservam decisões e auditorias de microetapas V17/S7/U7/FIFO. | Preservar como histórico documental. | Não remover salvo política documental específica. | Não |
| `ETAPA11-INVENTARIO-01` | `nucleo/limpeza_depreciacao_controlada.py` | governança | `rota_oficial_preservada` | A Etapa 11 já aceita evidências auxiliares, mas antes desta frente a classificação ficava limitada por inventário ausente. | Preservar e alimentar com inventário explícito em frente futura de integração. | Não se aplica. | Não |

---

## 4. Regras de uso deste inventário

1. Este inventário é evidência auxiliar não decisória.
2. Nenhum item deste inventário autoriza remoção automática.
3. Qualquer remoção deve ocorrer em frente própria, com PR específico e validação de ausência de dependência viva.
4. Itens classificados como `dependencia_viva` ou `compatibilidade_transitoria` bloqueiam depreciação automática.
5. Itens classificados como `diagnostico_preservado` podem permanecer fora do produto oficial padrão.
6. Itens classificados como `candidato_futuro_depreciacao` requerem auditoria adicional antes de qualquer remoção.
7. O produto oficial padrão deve continuar usando `aplicacao/principal.py`, `PacoteSaidaObservavelOficial` e `incluir_abas_diagnosticas=False`.

---

## 5. Pendências para transformar inventário documental em entrada operacional da Etapa 11

Este arquivo fecha o inventário documental inicial. Para que a Etapa 11 deixe de emitir `inventario_auxiliar_ausente` em runtime, ainda é necessária uma frente posterior específica, por exemplo:

```text
INTEGRA-INVENTARIO-RESIDUOS-ETAPA11-01
```

Essa frente posterior deve decidir se a Etapa 11 consumirá:

- este Markdown como evidência documental;
- uma versão estruturada em JSON/YAML;
- ou um objeto `evidencias_auxiliares` montado pela rota principal.

Até essa integração, este inventário deve ser tratado como fonte documental de auditoria, não como input runtime.

---

## 6. Decisão de fechamento da frente

A frente `INVENTARIO-RESIDUOS-LEGADOS-ETAPA11-01` cria o inventário formal mínimo dos resíduos legados identificados após os PRs #491 e #492.

Resultado esperado:

- código inalterado;
- runtime inalterado;
- dados/cache inalterados;
- contratos inalterados;
- rotas legadas não reativadas;
- resíduos classificados;
- remoção automática não autorizada;
- próxima frente de integração da Etapa 11 explicitada.
