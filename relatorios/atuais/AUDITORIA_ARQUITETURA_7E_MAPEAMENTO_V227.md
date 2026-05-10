# AUDITORIA ARQUITETURA 7-E — MAPEAMENTO DE ETAPAS, ARQUIVOS E DUPLICIDADES (V227)

## 1) Objetivo
Mapear, etapa por etapa da arquitetura **7-E**, os arquivos/scripts/funções envolvidos, identificar sobreposições de responsabilidade e listar candidatos objetivos para consolidação/remoção de código morto.

## 2) Escopo analisado
- Entrada principal: `aplicacao/principal.py`.
- Núcleo econômico/temporal: módulos em `nucleo/`.
- Camada de diagnóstico: scripts em `scripts/diagnostico/`.
- Legado e duplicidades históricas: `code/`.

## 3) Mapeamento por etapa (7-E)

### Etapa 1 — Configuração e planilha bruta
**Arquivos principais**
- `nucleo/carregador_config.py`
- `nucleo/config_utils.py`
- `nucleo/leitor_planilha.py`
- `nucleo/contexto_baseline.py`

**Função no pipeline**
- Carregar configurações e entrada bruta da planilha, com resolução de aliases de colunas e parâmetros de execução.

---

### Etapa 2 — Validação pré-execução
**Arquivos principais**
- `scripts/diagnostico/validar_canonizacao_v17_a1.py`
- `scripts/diagnostico/auditar_semantica_dados_v17_a3.py`
- `scripts/diagnostico/auditar_aderencia_v17_a0_1.py`

**Função no pipeline**
- Validar estrutura mínima e coerência semântica antes de qualquer decisão econômica.

---

### Etapa 3 — Dados operacionais canônicos
**Arquivos principais**
- `nucleo/dados_operacionais_canonicos.py`
- `nucleo/carteira_canonica.py`
- `nucleo/caixa_recebidos_auditaveis.py`

**Função no pipeline**
- Canonização de entidades, tipos, datas, valores e identificadores usados pelo motor.

---

### Etapa 4 — Ranking e definição do universo de produtos
**Arquivos principais**
- `nucleo/ranking_carteira_estabilizado.py`
- `nucleo/triagem_motor.py`

**Função no pipeline**
- Priorização/eligibilidade de destinos sem aplicar efeitos econômicos no estado temporal.

---

### Etapa 5 — Estado inicial temporal
**Arquivos principais**
- `nucleo/contexto_baseline.py`
- `nucleo/matriz_pacotes_diarios.py`
- `nucleo/pacote_orquestrado_pre_saida.py`

**Função no pipeline**
- Construção do estado temporal pré-motor (lotes, saldos, recebidos, pagamentos e restrições).

---

### Etapa 6 — Motor temporal conjunto
**Arquivos principais**
- `nucleo/motor_recomendacao_pagamentos_switching_v1.py`
- `nucleo/ledger_temporal_conjunto.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/fluxo_pagamentos_terminal_v138.py`
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/microplanejamento_conjunto_bloco_critico_v2.py`
- `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`

**Função no pipeline**
- Decisão e aplicação dos eventos econômicos (pagamento/aporte/resgate/switching), incluindo materialização e migração auditável.

---

### Etapa 7 — Ledger canônico, estado final e decisões finais
**Arquivos principais**
- `nucleo/ledger_temporal_conjunto.py`
- `nucleo/saida_observavel.py`

**Função no pipeline**
- Persistir a trilha canônica de eventos e estado final para consumo por camadas posteriores.

---

### Etapa 8 — Validação do estado temporal
**Arquivos principais**
- `scripts/diagnostico/auditar_transicao_temporal_switching_v17_d0.py`
- `scripts/diagnostico/validar_invariantes_extrato_futuro.py`
- `scripts/diagnostico/auditar_matriz_pacotes_motor.py`

**Função no pipeline**
- Aplicar gates de consistência temporal sobre ledger/estado final (não sobre renderização).

---

### Etapa 9 — Construção da saída canônica
**Arquivos principais**
- `nucleo/construir_saida_canonica_v17_c7.py`
- `nucleo/saida_canonica.py`
- `nucleo/saida_canonica_switching_v17_c7.py`

**Função no pipeline**
- Construir estrutura canônica final a partir do estado/ledger, sem recalcular decisão econômica.

---

### Etapa 10 — Saída canônica única
**Arquivos principais**
- `nucleo/construir_saida_canonica_v17_c7.py`

**Função no pipeline**
- Consolidar objeto único de saída consumido por console e planilha.

---

### Etapa 11 — Validação da saída canônica
**Arquivos principais**
- `scripts/diagnostico/auditar_saida_canonica_v17_a4.py`
- `scripts/diagnostico/definir_fonte_verdade_saida_v17_b1.py`

**Função no pipeline**
- Validar aderência da saída canônica ao ledger e ao estado final.

---

### Etapa 12 — Renderização de console e planilha operacional
**Arquivos principais**
- `aplicacao/console/principal.py`
- `aplicacao/console/secoes_execucao.py`
- `nucleo/gerar_planilha_operacional.py`
- `nucleo/ponte_renderizacao_switching_v17_c6.py`

**Função no pipeline**
- Somente apresentação/organização visual e operacional da saída canônica.

---

### Etapa 13 — Validação de renderização
**Arquivos principais**
- `scripts/diagnostico/validar_ponte_renderizacao_switching_v17_c6.py`
- `scripts/diagnostico/comparar_pacote_pre_saida_saida_canonica_v17_c3.py`

**Função no pipeline**
- Confirmar fidelidade dos artefatos renderizados à saída canônica.

---

### Etapa 14 — Artefatos finais
**Arquivos principais**
- Saídas em `saidas/`
- Relatórios em `relatorios/`

**Função no pipeline**
- Registro final auditável de execução/diagnóstico.

## 4) Achados de duplicidade (prioridade alta)

### 4.1 Núcleo funcional duplicado em `code/` x `nucleo/`
Foram encontrados blocos de funções com mesmo nome e papel em:
- `code/otimizacao_gastos.py`
- `code/otimizacao_swtiching.py`
- `code/otimizacao_unificado_gastos_swtiching.py`
- `nucleo/nucleo_financeiro_minimo.py`
- `nucleo/calendario_financeiro.py`
- `nucleo/leitor_planilha.py`

Exemplos recorrentes:
- `resolver_coluna`
- `contar_dias_rendimento`
- `gerar_dias_sem_rendimento_bancario`
- `is_dia_rendimento`
- `get_fator_liquido`
- `sacar`
- `criar_lote_de_aporte`
- `executar_saque_lote`

**Leitura técnica:** há forte indício de legado paralelo ainda coexistindo com o núcleo estabilizado.

### 4.2 Utilitários de diagnóstico repetidos
Há alta repetição de helpers em `scripts/diagnostico/`, especialmente:
- `_gravar_csv`
- `gravar`
- `_ler_csv`
- `_norm`
- `_txt`

**Leitura técnica:** parte dos scripts de diagnóstico poderia ser consolidada em um módulo comum (ex.: `scripts/diagnostico/common_io.py`) para reduzir divergência comportamental.

## 5) Candidatos a reorganização por onda

### Onda A — Congelamento de fonte oficial
1. Declarar `nucleo/` + `aplicacao/` como trilha oficial de runtime.
2. Marcar `code/` como legado experimental/documental.

### Onda B — Extração de utilitários compartilhados
1. Criar utilitários comuns de diagnóstico (`ler/gravar CSV`, normalização, parsing numérico/data).
2. Migrar scripts gradualmente para o módulo comum.

### Onda C — Gate arquitetural automatizado
1. Criar validação CI simples para impedir novas regras econômicas em camadas de renderização.
2. Criar checklist de PR por etapa 7-E (origem da mudança + camada afetada).

## 6) Riscos atuais
- **Risco de duplicidade semântica:** mesma função com múltiplas cópias evoluindo separadamente.
- **Risco de regressão silenciosa:** ajustes em `code/` não refletidos em `nucleo/` (ou vice-versa).
- **Risco de quebra da 7-E:** scripts de diagnóstico/renderização absorvendo regra econômica por conveniência local.

## 7) Próxima ação recomendada
Executar uma auditoria técnica por lotes, iniciando pelos 10 nomes de função mais duplicados com impacto econômico, vinculando cada função a uma única implementação oficial e convertendo as demais em wrappers de compatibilidade (ou remoção planejada).
