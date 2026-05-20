# ME-V17-F0-V4A — Auditoria completa da Etapa 4: replay, ledger e estado temporal

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4A
- VERSAO_CANDIDATA: V17-F0-V.4A
- TIPO: DOCUMENTAL / AUDITORIA OPERACIONAL / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_ETAPA4_REPLAY_LEDGER_ESTADO_TEMPORAL
- BASELINE_DE_ENTRADA: V17-F0-V.3.7V
- BASELINE_COMMIT_ENTRADA: 30e979df85ea10c803bcd8fda20d7b5bfecd9ebe
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_ETAPA_4: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Mapear a Etapa 4 como camada própria, separando:

```text
replay passado
ledger temporal futuro
estado temporal por data
saldos por lote
vencimentos
fontes elegíveis
pagamentos futuros
resíduos de contexto amplo
responsabilidades ainda concentradas em saída canônica ou ledger legado
```

A V4A não implementa código. Ela identifica fronteiras, artefatos, resíduos e a sequência segura de microetapas posteriores.

---

## 3. Condição de entrada

A V3.7V reauditoria Etapas 1–3 concluiu:

```text
ETAPAS1_3_COERENTES_COM_PIPELINE_ATUAL=sim
ETAPA1_COM_RESIDUOS=sim
ETAPA2_COM_RESIDUOS=sim
ETAPA3_COM_RESIDUOS=sim
RESIDUO_CRITICO_SWITCHING_BRUTO_LEDGER_REMOVIDO_COMO_FONTE_PRIMARIA=sim
RESIDUOS_REMANESCENTES_BLOQUEIAM_V4A=nao
ABRIR_V4A_COM_RESIDUOS_CLASSIFICADOS=sim
```

Logo, a V4A parte de Etapas 1–3 funcionais, com resíduos classificados, e com `switching_canonico` já promovido como fonte primária interna do ledger.

---

## 4. Arquivos inspecionados

Foram inspecionados, sem alteração:

```text
nucleo/replay_passado_controlado.py
nucleo/ledger_temporal_conjunto.py
nucleo/pacote_ledger_temporal.py
nucleo/saida_canonica.py
logs/iteracoes/ME-V17-F0-V37V_REAUDITA_ETAPAS1_3_PIPELINE_ATUAL_PLANO_RESIDUOS.md
```

---

## 5. Definição operacional da Etapa 4

A Etapa 4 deve ser entendida como a camada temporal entre a canonização operacional e a saída canônica.

Ela deve receber os artefatos canônicos da Etapa 3 e produzir pacotes temporais auditáveis para consumo downstream.

Definição consolidada:

```text
Etapa 4 = replay passado + ledger temporal futuro + estado temporal + saldos + eventos temporais
```

Não pertencem conceitualmente à Etapa 4:

```text
leitura física da planilha
resolução de abas e colunas
validação pré-execução
canonização estrutural de inventário/gastos/salários/switching
renderização de console/XLSX
formatação final da saída observável
ranking visual de carteira
```

---

## 6. Subcamada 4.1 — Replay passado

### 6.1. Arquivo principal

```text
nucleo/replay_passado_controlado.py
```

### 6.2. Artefato atual

```text
PacoteReplayPassadoControlado
```

Campos atuais:

```text
lotes_apos_replay
log_passado
estado_lotes_passado
auditoria
validacao
```

### 6.3. Responsabilidade atual

O módulo declara como escopo:

```text
reprocessar contas pagas até a data de referência
consumir lotes explicitamente informados na despesa
materializar lotes históricos não aportados marcados com '-'
atualizar saldos e remanescentes por lote
gerar log técnico do replay e snapshot pós-passado
```

E declara fora do escopo:

```text
heurísticas/solvers para escolher lote
switching econômico
score econômico final
relatório financeiro atual
replay de despesas sem lote informado, salvo Lote usado = Saldo exclusivo
```

### 6.4. Entradas atuais

```text
PacoteDadosOperacionaisCanonicos
PacoteNucleoFinanceiroMinimo
PacoteCalendarioFinanceiro
config
data_referencia
serie_cdi opcional
```

### 6.5. Saídas atuais

```text
lotes_apos_replay
log_passado
estado_lotes_passado
auditoria
validacao
```

### 6.6. Resíduos / pontos de atenção

| Item | Classificação | Observação |
|---|---|---|
| `config` amplo | resíduo transversal | replay ainda consulta parâmetros de auditoria/replay diretamente |
| `PacoteNucleoFinanceiroMinimo` | dependência necessária atual | ainda é base material para lotes financeiros |
| alias de lotes históricos | heurística local | pertence ao replay, mas precisa contrato explícito |
| caixa operacional histórico `Saldo` | regra especial histórica | precisa virar campo contratual de replay |
| normalização de resíduos sub-limiar | regra de fechamento | precisa ficar explícita em contrato |
| `estado_lotes_passado` DataFrame | saída útil, mas schema não formalizado | candidato a contrato mínimo |

### 6.7. Decisão V4A para replay

```text
REPLAY_PASSADO_EXISTE_COM_PACOTE=sim
REPLAY_PASSADO_FUNCIONAL=sim
REPLAY_PASSADO_CONTRATO_MINIMO_AINDA_INCOMPLETO=sim
```

O replay é a parte da Etapa 4 mais próxima de um pacote formal, mas ainda precisa de contrato mínimo documentado e de separação mais clara entre regra temporal, auditoria e compatibilidade histórica.

---

## 7. Subcamada 4.2 — Ledger temporal futuro

### 7.1. Arquivo principal

```text
nucleo/ledger_temporal_conjunto.py
```

### 7.2. Função principal atual

```text
construir_ledger_temporal_conjunto(...)
```

### 7.3. Responsabilidade atual

O módulo declara:

```text
Ledger temporal conjunto mínimo para Extrato Futuro.
Consolida eventos canônicos (pagamento + switching) sem recalcular resgates, impostos ou saldos em camada de saída.
```

### 7.4. Estado após V3.7S

O ledger agora usa `switching_canonico` como fonte primária interna para mapa/eventos de switching:

```text
_mapa_switchings_canonico_compativel_ledger_v37s
_eventos_switching_canonico_compativel_ledger_v37s
```

O caminho legado bruto permanece apenas como fallback:

```text
_mapa_switchings_aba_operacional_legado_v37s
_eventos_switching_aba_operacional_legado_v37s
```

### 7.5. Entradas atuais

```text
quadro_futuro
mapa_central
contexto
```

Essas entradas ainda não formam um contrato puro. O `contexto` amplo ainda carrega replay, dados operacionais, config, pacote_planilha e módulos shadow.

### 7.6. Saídas atuais

O retorno legado é um dicionário, não um dataclass/pacote operacional formal.

Chaves relevantes já consumidas por saída e pacotes shadow:

```text
eventos
fifo_candidatos_avaliados
destinos_pos_switching_materializados_passivos
vinculos_origem_destino_pos_switching
metadados/auditorias diversas, conforme retorno legado
```

### 7.7. Resíduos / pontos de atenção

| Item | Classificação | Observação |
|---|---|---|
| retorno como dict amplo | resíduo contratual | precisa virar `PacoteLedgerTemporal` operacional |
| `contexto` amplo | resíduo arquitetural | ledger ainda depende de muitas fontes indiretas |
| `quadro_futuro` | entrada não formalizada da Etapa 4 | deve virar parte de pacote de pagamentos futuros |
| `mapa_central` | entrada derivada/ponte com saída | precisa contrato próprio |
| fallback bruto de Switching | fallback auditável | não é fonte primária, mas deve ser monitorado |
| estado temporal interno | não exposto formalmente | precisa schema próprio |
| fontes elegíveis por data | parcialmente inferidas/eventos | precisa pacote explícito |
| vencimentos | não formalizados como saída do ledger | mapear na V4B/V4C |

### 7.8. Decisão V4A para ledger

```text
LEDGER_TEMPORAL_FUNCIONAL=sim
LEDGER_TEMPORAL_SWITCHING_CANONICO_PRIMARIO=sim
LEDGER_TEMPORAL_CONTRATO_OPERACIONAL_INCOMPLETO=sim
```

O ledger já executa a função operacional necessária para a saída atual, mas ainda não é uma camada contratual limpa.

---

## 8. Subcamada 4.3 — PacoteLedgerTemporal

### 8.1. Arquivo principal

```text
nucleo/pacote_ledger_temporal.py
```

### 8.2. Artefato atual

```text
PacoteLedgerTemporal
```

Campos declarados:

```text
versao
modo_shadow
data_referencia
eventos_temporais
estado_temporal_por_data
saldos_por_lote
saldos_disponiveis_por_data
vencimentos_processados
pagamentos_futuros_processados
fontes_elegiveis_por_data
alertas_temporais
fifo_candidatos_avaliados
auditoria_ledger_temporal
validacao_ledger_temporal
metadados_origem
```

### 8.3. Natureza atual

O módulo declara que o pacote ainda é shadow e que não substitui o ledger legado.

### 8.4. Pontos positivos

O pacote já contém o esqueleto que a Etapa 4 precisa:

```text
eventos temporais
estado temporal por data
saldos por lote
vencimentos
pagamentos futuros
fontes elegíveis
alertas
FIFO
auditoria
validação
metadados
```

### 8.5. Pontos incompletos

O construtor atual ainda preenche vários campos a partir do retorno legado, com listas vazias quando o retorno não fornece a estrutura.

Também mantém marcadores herdados da fase shadow:

```text
usa_contexto_amplo=True
usa_planilha_bruta=True
usa_switching_shadow=True
usa_pos_injetado=True
uso_transitorio_de_contexto_amplo
uso_transitorio_de_planilha_bruta_pelo_ledger_legado
uso_transitorio_de_switching_shadow_pelo_ledger_legado
```

Após a V3.7S, esses marcadores precisam ser reinterpretados, porque `Switching` bruto deixou de ser fonte primária do ledger.

### 8.6. Decisão V4A para PacoteLedgerTemporal

```text
PACOTE_LEDGER_TEMPORAL_SHADOW_EXISTE=sim
PACOTE_LEDGER_TEMPORAL_EH_BASE_DO_CONTRATO_FUTURO=sim
PACOTE_LEDGER_TEMPORAL_AINDA_NAO_EH_OPERACIONAL_FINAL=sim
```

O pacote é a base certa para a Etapa 4, mas precisa ser promovido/normalizado em microetapa posterior.

---

## 9. Subcamada 4.4 — Estado temporal

### 9.1. Estado atual

O estado temporal existe de forma distribuída:

```text
lotes_apos_replay no replay passado
estado_lotes_passado no replay
estado_lotes interno do ledger
saldos_por_lote extraídos de eventos no PacoteLedgerTemporal shadow
campos de saldo usados pela saída canônica
```

### 9.2. Problema arquitetural

Ainda não existe um contrato explícito único para:

```text
estado_temporal_por_data
saldo bruto por lote por data
saldo líquido por lote por data
lote disponível/indisponível
lote migrado/exaurido
fonte elegível por pagamento
evento de vencimento
evento de switching
evento de pagamento
```

### 9.3. Consequência

Parte das regras de interpretação ainda aparece distribuída entre replay, ledger e saída canônica.

Classificação:

```text
ESTADO_TEMPORAL_EXISTE_IMPLÍCITO=sim
ESTADO_TEMPORAL_CONTRATO_FORMAL=nao
```

---

## 10. Subcamada 4.5 — Interface com a saída canônica

### 10.1. Arquivo principal consumidor

```text
nucleo/saida_canonica.py
```

### 10.2. Consumo atual do replay

A saída canônica monta o extrato passado a partir de:

```text
contexto.replay_passado.log_passado
```

e aplica regras adicionais de apresentação/ajuste, incluindo inclusão de pagamentos passados POS ausentes e ordenação final.

### 10.3. Consumo atual do ledger

A saída canônica monta o extrato futuro chamando diretamente:

```text
construir_ledger_temporal_conjunto(quadro, mapa_central, contexto)
```

Em seguida consome:

```text
eventos
fifo_candidatos_avaliados
```

### 10.4. Problema arquitetural

A saída canônica ainda é parcialmente orquestradora da Etapa 4, porque:

```text
escolhe quadro_futuro
monta mapa_central
chama ledger temporal
interpreta eventos do ledger
aplica filtros e regras visuais/operacionais
```

### 10.5. Decisão V4A para saída

```text
SAIDA_CANONICA_CONSUME_ETAPA4=sim
SAIDA_CANONICA_AINDA_ORQUESTRA_PARTE_DA_ETAPA4=sim
SAIDA_CANONICA_DEVE_DEIXAR_DE_CHAMAR_LEDGER_DIRETAMENTE_NO_FINAL=sim
```

A saída deve, no futuro, consumir pacotes da Etapa 4, não construir diretamente parte deles.

---

## 11. Fronteiras propostas da Etapa 4

### 11.1. Entrada formal desejada

A Etapa 4 deve receber, no mínimo:

```text
PacoteDadosOperacionaisCanonicos
PacoteNucleoFinanceiroMinimo
PacoteCalendarioFinanceiro
PacoteCarteiraCanonica
config operacional reduzida
data_referencia
serie_cdi/cache_cdi resolvido
```

### 11.2. Saídas formais desejadas

A Etapa 4 deve produzir:

```text
PacoteReplayPassado
PacoteLedgerTemporalOperacional
PacoteEstadoTemporal
PacoteFontesElegiveis
PacoteAuditoriaTemporal
```

### 11.3. Saída canônica desejada

A saída canônica deve consumir:

```text
PacoteReplayPassado
PacoteLedgerTemporalOperacional
PacoteEstadoTemporal / resumo temporal
```

sem chamar diretamente o ledger ou reconstruir regras temporais.

---

## 12. Resíduos principais da Etapa 4

| Resíduo | Local atual | Risco | Tratamento recomendado |
|---|---|---:|---|
| Retorno legado do ledger como dict | `ledger_temporal_conjunto.py` | médio | V4B/V4D |
| Saída canônica chama ledger diretamente | `saida_canonica.py` | médio/alto | V4D/V4E |
| Estado temporal implícito | replay/ledger/saída | alto | V4B/V4C |
| `PacoteLedgerTemporal` ainda shadow | `pacote_ledger_temporal.py` | médio | V4D |
| Metadados shadow antigos | `pacote_ledger_temporal.py` | baixo/médio | V4D |
| Fallback bruto de Switching | ledger fallback | baixo | manter até contratos V4 estabilizarem |
| `contexto` amplo | ledger/saída | médio | V4E |
| `mapa_central` derivado na saída | saída canônica | médio | V4C/V4D |
| `quadro_futuro` escolhido na saída | saída canônica | médio | V4C/V4D |
| Regras visuais misturadas a regras temporais | saída canônica | médio | V4E |

---

## 13. Decisão sobre implementação imediata

A V4A não recomenda refatoração imediata ampla.

Decisão:

```text
IMPLEMENTAR_REPLAY_NOVO_AGORA=nao
IMPLEMENTAR_LEDGER_NOVO_AGORA=nao
MOVER_CHAMADA_DO_LEDGER_PARA_FORA_DA_SAIDA_AGORA=nao
PROMOVER_PACOTE_LEDGER_TEMPORAL_AGORA=nao
```

Antes de qualquer implementação, é necessário especificar os contratos mínimos da Etapa 4.

---

## 14. Próximas microetapas recomendadas

### V4B — Especifica contratos mínimos da Etapa 4

Tipo:

```text
DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Definir PacoteReplayPassado mínimo, PacoteLedgerTemporalOperacional mínimo, PacoteEstadoTemporal e PacoteAuditoriaTemporal, com campos obrigatórios e fronteiras entre replay, ledger, estado e saída.
```

---

### V4C — Audita aderência do código atual aos contratos V4B

Tipo:

```text
DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Verificar quais campos já existem, quais estão implícitos, quais são calculados na saída e quais precisam ser materializados por adaptadores.
```

---

### V4D — Normaliza PacoteLedgerTemporal operacional em modo shadow

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Promover o envelope atual de PacoteLedgerTemporal para um pacote operacional shadow mais completo, corrigindo metadados obsoletos e materializando campos mínimos sem alterar saída.
```

---

### V4E — Conecta saída canônica a PacoteLedgerTemporal operacional shadow

Tipo:

```text
EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Permitir que a saída canônica compare seu caminho direto atual com o pacote temporal operacional shadow, sem trocar ainda a fonte efetiva.
```

---

### V4F — Substitui chamada direta do ledger na saída por pacote temporal validado

Tipo:

```text
EXECUTÁVEL / PROMOÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Remover gradualmente a orquestração da Etapa 4 de dentro da saída canônica, fazendo a saída consumir pacotes temporais validados.
```

---

## 15. Decisão final

```text
ETAPA4_EXISTE_FUNCIONALMENTE=sim
ETAPA4_CONTRATO_COMPLETO=nao
REPLAY_PASSADO_TEM_PACOTE=sim
LEDGER_TEMPORAL_TEM_RETORNO_FUNCIONAL=sim
PACOTE_LEDGER_TEMPORAL_SHADOW_EXISTE=sim
ESTADO_TEMPORAL_FORMALIZADO=nao
SAIDA_CANONICA_AINDA_ORQUESTRA_ETAPA4=sim
V4A_APROVADA_COMO_AUDITORIA=sim
PROXIMA_MICROETAPA=V17-F0-V.4B
```

---

## 16. Conclusão

A Etapa 4 já existe funcionalmente, mas ainda não está organizada como camada contratual completa.

O replay passado é a subcamada mais bem encapsulada. O ledger temporal funciona e já consome `switching_canonico` como fonte primária para switching, mas ainda retorna um dicionário legado. O `PacoteLedgerTemporal` existe como envelope shadow e deve ser a base do contrato operacional futuro. O estado temporal existe implicitamente, distribuído entre replay, ledger e saída. A saída canônica ainda orquestra parte da Etapa 4 e deve, futuramente, consumir pacotes temporais em vez de chamar o ledger diretamente.

A próxima etapa segura é especificar os contratos mínimos da Etapa 4 antes de qualquer refatoração executável.
