# Auditoria de cobertura — candidatos à consolidação ou remoção futura

## Objetivo

Auditar a cobertura documental dos 6 arquivos de `relatorios/atuais/` marcados como `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA`, comparando-os contra documentos vigentes, índices de rastreabilidade e relatórios consolidados. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- A auditoria mede cobertura textual/nominal; não substitui revisão humana antes de remoção.

## Resumo

| Classe de cobertura | Arquivos |
|---|---:|
| `COBERTURA_FORTE` | 1 |
| `COBERTURA_FRACA` | 2 |
| `SEM_COBERTURA_DETECTADA` | 3 |

## Resultado arquivo a arquivo

| Arquivo | Cobertura | Hits fortes | Fontes com hit | Decisão preliminar |
|---|---|---:|---:|---|
| `relatorios/atuais/PLANO_LIMPEZA_REPOSITORIO_POS_RD.md` | `SEM_COBERTURA_DETECTADA` | 0 | 0 | `MANTER_E_REVISAR_MANUALMENTE` |
| `relatorios/atuais/STATUS_LOCAL_IGNORADOS_POS_LIMPEZA.txt` | `SEM_COBERTURA_DETECTADA` | 0 | 0 | `MANTER_E_REVISAR_MANUALMENTE` |
| `relatorios/atuais/CORRECAO_CIRURGICA_V200.md` | `COBERTURA_FRACA` | 0 | 3 | `MANTER_ATE_COBERTURA_SER_REFORCADA` |
| `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md` | `COBERTURA_FORTE` | 1 | 2 | `CANDIDATO_REMOCAO_CONTROLADA_APOS_REVISAO_HUMANA` |
| `relatorios/atuais/HOTFIX_UTILITARIOS_SERIES_V207.md` | `SEM_COBERTURA_DETECTADA` | 0 | 0 | `MANTER_E_REVISAR_MANUALMENTE` |
| `relatorios/atuais/CORRECAO_SALDOS_FUTUROS_LOTES_V208.md` | `COBERTURA_FRACA` | 0 | 3 | `MANTER_ATE_COBERTURA_SER_REFORCADA` |

## Evidências de cobertura

### `relatorios/atuais/PLANO_LIMPEZA_REPOSITORIO_POS_RD.md`

- Título: Plano de limpeza do repositório pós-RD
- Linhas: 43
- Classe de cobertura: `SEM_COBERTURA_DETECTADA`
- Decisão preliminar: `MANTER_E_REVISAR_MANUALMENTE`
- Fontes com hit: 0
- Hits fortes: 0
- Hits em documentos vigentes: 0
- Hits em rastreabilidade consolidada: 0
- Hits em índices: 0

**Exemplos de cobertura:**

- Nenhuma cobertura textual/nominal detectada.

### `relatorios/atuais/STATUS_LOCAL_IGNORADOS_POS_LIMPEZA.txt`

- Título: STATUS_LOCAL_IGNORADOS_POS_LIMPEZA.txt
- Linhas: 44
- Classe de cobertura: `SEM_COBERTURA_DETECTADA`
- Decisão preliminar: `MANTER_E_REVISAR_MANUALMENTE`
- Fontes com hit: 0
- Hits fortes: 0
- Hits em documentos vigentes: 0
- Hits em rastreabilidade consolidada: 0
- Hits em índices: 0

**Exemplos de cobertura:**

- Nenhuma cobertura textual/nominal detectada.

### `relatorios/atuais/CORRECAO_CIRURGICA_V200.md`

- Título: Correção cirúrgica V200
- Linhas: 22
- Classe de cobertura: `COBERTURA_FRACA`
- Decisão preliminar: `MANTER_ATE_COBERTURA_SER_REFORCADA`
- Fontes com hit: 3
- Hits fortes: 0
- Hits em documentos vigentes: 0
- Hits em rastreabilidade consolidada: 2
- Hits em índices: 0

**Exemplos de cobertura:**

- relatorios/atuais/LEIA-ME_OPERACIONAL.md [REVISAO_MANUAL] termos=v200
- relatorios/atuais/RELATORIO_CONSOLIDADO_AUDITORIAS_ESPECIFICAS_RAIZ_HISTORICO.md [RASTREABILIDADE_CONSOLIDADA] termos=correcao cirurgica
- relatorios/atuais/RELATORIO_CONSOLIDADO_BASELINES_HISTORICAS_V031_V060.md [RASTREABILIDADE_CONSOLIDADA] termos=correcao cirurgica

### `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md`

- Título: HOTFIX_CONSOLE_IMPORTS_V205
- Linhas: 73
- Classe de cobertura: `COBERTURA_FORTE`
- Decisão preliminar: `CANDIDATO_REMOCAO_CONTROLADA_APOS_REVISAO_HUMANA`
- Fontes com hit: 2
- Hits fortes: 1
- Hits em documentos vigentes: 1
- Hits em rastreabilidade consolidada: 0
- Hits em índices: 0

**Exemplos de cobertura:**

- relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md [DOCUMENTO_VIGENTE_CANDIDATO] termos=v205
- relatorios/atuais/LEIA-ME_OPERACIONAL.md [REVISAO_MANUAL] termos=hotfix_console_imports_v205; hotfix_console_imports_v205.md; v205

### `relatorios/atuais/HOTFIX_UTILITARIOS_SERIES_V207.md`

- Título: HOTFIX_UTILITARIOS_SERIES_V207
- Linhas: 47
- Classe de cobertura: `SEM_COBERTURA_DETECTADA`
- Decisão preliminar: `MANTER_E_REVISAR_MANUALMENTE`
- Fontes com hit: 0
- Hits fortes: 0
- Hits em documentos vigentes: 0
- Hits em rastreabilidade consolidada: 0
- Hits em índices: 0

**Exemplos de cobertura:**

- Nenhuma cobertura textual/nominal detectada.

### `relatorios/atuais/CORRECAO_SALDOS_FUTUROS_LOTES_V208.md`

- Título: CORREÇÃO SALDOS FUTUROS DE LOTES — V208
- Linhas: 49
- Classe de cobertura: `COBERTURA_FRACA`
- Decisão preliminar: `MANTER_ATE_COBERTURA_SER_REFORCADA`
- Fontes com hit: 3
- Hits fortes: 0
- Hits em documentos vigentes: 1
- Hits em rastreabilidade consolidada: 0
- Hits em índices: 0

**Exemplos de cobertura:**

- relatorios/atuais/INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_V216.md [REVISAO_MANUAL] termos=v208
- relatorios/atuais/LEIA-ME_OPERACIONAL.md [REVISAO_MANUAL] termos=v208
- relatorios/atuais/VALIDACAO_LOCAL_V216.md [DOCUMENTO_VIGENTE_CANDIDATO] termos=v208

## Decisão desta etapa

Nenhum dos 6 arquivos deve ser removido automaticamente. Arquivos com `COBERTURA_FORTE` podem ser tratados como candidatos à remoção controlada em etapa posterior; arquivos com `COBERTURA_FRACA` ou `SEM_COBERTURA_DETECTADA` devem permanecer até reforço ou revisão manual da cobertura.
