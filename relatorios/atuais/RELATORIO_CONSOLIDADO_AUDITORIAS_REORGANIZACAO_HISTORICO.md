# Relatório consolidado — auditorias históricas de reorganização

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/auditorias_especificas/reorganizacao/` em um único relatório atual, preservando a trilha de reorganização, saneamento contratual, compatibilidade e consolidação de helpers sem manter arquivos granulares.

- Arquivos consolidados: 4
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/auditorias_especificas/reorganizacao/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md` | 60 | Auditoria estrutural de redundância e compatibilidade |
| `relatorios/historico/auditorias_especificas/reorganizacao/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md` | 39 | Consolidação de helpers duplicados de baixo risco |
| `relatorios/historico/auditorias_especificas/reorganizacao/REORGANIZACAO_REPOSITORIO_V115.md` | 29 | Reorganização do repositório V115 |
| `relatorios/historico/auditorias_especificas/reorganizacao/SANEAMENTO_CONTRATUAL_V106.md` | 51 | Saneamento contratual V106 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Reorganização estrutural | Auditorias históricas de reorganização foram preservadas em forma consolidada. |
| Saneamento contratual | Registros de saneamento e compatibilidade permanecem rastreáveis. |
| Helpers e redundâncias | Histórico de consolidação de helpers duplicados foi preservado. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/auditorias_especificas/reorganizacao/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`

- Título: Auditoria estrutural de redundância e compatibilidade
- Linhas originais: 60

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria estrutural de redundância e compatibilidade
## Escopo
Auditoria leve e diagnóstica originalmente aberta na V84 e atualizada na V86 focada em três frentes:
1. wrappers de compatibilidade em `scripts/`;
2. helpers duplicados em módulos do núcleo e da apresentação;
3. crescimento da superfície diagnóstica e sua carga de manutenção.
## Achados principais
### 1. Wrappers de compatibilidade
- existem **17 scripts raiz** em `scripts/` além de `__init__.py`;
- existe espelhamento entre scripts raiz e implementações reais em `scripts/diagnostico/`, `scripts/auditoria/` e `scripts/operacional`;
- há **pelo menos 4 wrappers raiz com falha confirmada de execução direta** por ausência de bootstrap de `sys.path`:
  - `scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/verificar_release_baseline.py`;
- há **1 wrapper raiz com bootstrap inconsistente** e falha confirmada de execução direta:
  - `scripts/inspecionar_switching_economico_shadow.py`.
### 2. Helpers duplicados
```

</details>

### `relatorios/historico/auditorias_especificas/reorganizacao/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md`

- Título: Consolidação de helpers duplicados de baixo risco
- Linhas originais: 39

<details>
<summary>Trecho inicial preservado</summary>

```text
# Consolidação de helpers duplicados de baixo risco
## Escopo
Esta etapa consolida apenas helpers pequenos e neutros previamente mapeados na auditoria estrutural, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow como regras decisórias.
## Consolidações aplicadas
1. **Normalização de valores exauridos na situação atual**
   - fonte única: `nucleo.utilitarios_neutros.normalizar_valores_situacao_atual_exaurida`
   - consumidores atualizados:
     - `aplicacao/console/principal.py`
     - `scripts/operacional/gerar_planilha_operacional.py`
2. **Leitura simples de configuração**
   - fonte única material: `nucleo.config_utils.obter_config`
   - consumidores atualizados:
     - `nucleo.triagem_motor`
     - `nucleo.resolver_hibrido_5p_shadow`
     - `nucleo.switching_economico_shadow`
   - `nucleo.carregador_config.obter_config` foi preservado apenas como compatibilidade delegando para a fonte única.
3. **Iteração de datas e simulação de lote em camadas shadow**
   - fonte única: `nucleo.helpers_shadow_compartilhados`
```

</details>

### `relatorios/historico/auditorias_especificas/reorganizacao/REORGANIZACAO_REPOSITORIO_V115.md`

- Título: Reorganização do repositório V115
- Linhas originais: 29

<details>
<summary>Trecho inicial preservado</summary>

```text
# Reorganização do repositório V115
## Objetivo
Recolocar o repositório em direção explícita ao objetivo final do projeto, reduzindo ruído estrutural e documental sem alterar a regra econômica vigente da frente central.
## Ajustes aplicados
1. **Recentralização documental**
   - README reescrito para destacar o objetivo final conjunto do projeto.
   - índice oficial reestruturado separando frente central, camada operacional por conta e reorganização estrutural.
   - contrato atualizado para distinguir baseline central V108 de camadas auxiliares posteriores.
2. **Limpeza de histórico fora do lugar**
   - documentos antigos de baseline, validação e estrutura que ainda estavam em `relatorios/atuais/` foram movidos para `relatorios/historico/`.
3. **Limpeza de saídas redundantes**
   - saídas operacionais antigas e não referenciadas foram removidas de `saidas/operacional/`.
4. **Deduplicação leve de código**
   - scripts diagnósticos passaram a compartilhar um bootstrap único em `scripts/diagnostico/_bootstrap.py`.
   - wrappers raiz em `scripts/` foram preservados apenas como compatibilidade.
## Resultado esperado
- menos ruído para a próxima retomada da frente central;
- menor risco de drift documental;
```

</details>

### `relatorios/historico/auditorias_especificas/reorganizacao/SANEAMENTO_CONTRATUAL_V106.md`

- Título: Saneamento contratual V106
- Linhas originais: 51

<details>
<summary>Trecho inicial preservado</summary>

```text
# Saneamento contratual V106
## Objetivo
A V106 executa um saneamento contratual do repositório para corrigir o drift entre:
- baseline vigente;
- README;
- índice de relatórios;
- contrato operacional;
- e direção metodológica real do projeto.
## Problema corrigido
Até a V105, o repositório já possuía uma linha experimental local do bloco crítico (`V103`–`V105`) suficientemente detalhada para começar a competir com a frente principal do projeto na prática, mesmo sem ter sido formalmente promovida.
Isso criava ambiguidade em três níveis:
1. o objetivo final do projeto ficava menos nítido;
2. melhoras locais podiam ser confundidas com avanço do motor principal;
3. a documentação contratual não acompanhava integralmente a baseline vigente.
## Correções aplicadas
### 1. Separação formal das trilhas
A V106 separa explicitamente:
- **frente central do projeto**;
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/auditorias_especificas/reorganizacao/` pode ser removida se os documentos granulares não tiverem autoridade ativa superior aos documentos atuais.
