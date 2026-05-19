# ME-V17-F0-V37O — Especifica substituição do consumo bruto de Switching no ledger por switching_canonico

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37O
- VERSAO_CANDIDATA: V17-F0-V.3.7O
- TIPO: DOCUMENTAL / CONTRATO DE MIGRAÇÃO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: ESPECIFICA_SUBSTITUICAO_SWITCHING_BRUTO_LEDGER_POR_SWITCHING_CANONICO
- BASELINE_DE_ENTRADA: V17-F0-V.3.7N
- BASELINE_COMMIT_ENTRADA: f6d974fc444c3f32e568d9691e094e0e3a70889a
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_PACOTE_LEDGER_TEMPORAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Definir o contrato de migração para substituir, no ledger temporal, o consumo direto da aba bruta `Switching` por consumo canônico de:

```text
contexto.dados_operacionais.switching_canonico
```

A migração deve preservar equivalência runtime com o caminho legado antes de qualquer promoção operacional.

---

## 3. Condição de entrada

A V3.7N concluiu:

```text
ETAPA1_FUNCIONAL=sim
ETAPA1_COM_RESIDUO_LEGADO=sim
RESIDUO_ETAPA1_CONSUMIDO_APOS_ETAPA3=sim
ETAPA2_FUNCIONAL=sim
ETAPA3_FUNCIONAL=sim
ETAPA3_COERENTE_PARA_ETAPA4_ATUAL=sim
ETAPA3_SUFICIENTE_PARA_ETAPA4_ARQUITETURALMENTE_PURA=nao
SAIDA_CANONICA_ESTAVEL_APOS_V37M=sim
MICROCORRECAO_IMEDIATA_OBRIGATORIA=nao
MIGRACAO_ARQUITETURAL_FUTURA_NECESSARIA=sim
```

O resíduo crítico identificado foi:

```text
contexto.pacote_planilha.quadros_brutos['Switching']
pd.read_excel(..., sheet_name='Switching')
```

sendo consumido por `nucleo/ledger_temporal_conjunto.py` após a Etapa 3.

---

## 4. Problema arquitetural a resolver

O ledger temporal atualmente ainda depende de entrada bruta/legada para materializar informações de switching.

Padrão legado observado:

```text
contexto -> pacote_planilha -> quadros_brutos -> aba Switching
```

Fallback legado observado:

```text
pd.read_excel(caminho_planilha, sheet_name='Switching')
```

Esse comportamento viola a cadeia contratual definida na V3.7G:

```text
PacoteEntradaResolvida validado
        |
        v
PacoteValidacaoPreExecucao aprovado
        |
        v
Etapa 3 — Canonização operacional
        |
        v
Replay / Ledger / Saída
```

Depois da Etapa 3, consumidores posteriores não devem reabrir planilha nem consultar quadros brutos da Etapa 1.

---

## 5. Funções-alvo no ledger legado

A migração futura deve mirar, inicialmente, as funções que extraem switching a partir da aba bruta:

```text
_mapa_switchings_aba_operacional(contexto)
_eventos_switching_aba_operacional(contexto)
```

Essas funções devem ser substituídas por equivalentes baseadas em:

```text
contexto.dados_operacionais.switching_canonico
```

Sem alteração imediata do comportamento operacional.

---

## 6. Fonte canônica obrigatória

A fonte canônica para switching, a partir da Etapa 3, é:

```text
PacoteDadosOperacionaisCanonicos.switching_canonico
```

A fonte deve ser acessada por:

```text
dados_operacionais = contexto.dados_operacionais
switching_canonico = dados_operacionais.switching_canonico
```

É proibido que o adaptador futuro acesse diretamente:

```text
contexto.pacote_planilha.quadros_brutos
pd.read_excel(...)
```

exceto em auditoria comparativa shadow especificamente destinada a provar equivalência com o caminho legado.

---

## 7. Campos canônicos esperados de switching_canonico

A Etapa 3 já produz, quando disponível, colunas com semântica operacional:

```text
switching_id
ordem_planilha_switching
origem_registro
data_recebimento
data_aplicacao
data_switching
lote_origem
lote_destino
produto_origem
produto_destino
ganho_estimado
valor_liquido_origem
status
```

A migração do ledger deve consumir esses campos, não nomes físicos da aba original como:

```text
Lote (ID) Antes
Lote (ID) Depois
Valor Líquido Migrado
Data Aplicação
Investimento
```

---

## 8. Contrato de equivalência — mapa de switchings

O adaptador canônico futuro deve produzir estrutura equivalente à estrutura atualmente devolvida por:

```text
_mapa_switchings_aba_operacional(contexto)
```

Formato mínimo esperado por lote de origem:

```text
lote_origem
lote_pos_switching
data_switching
produto_destino
valor_liquido_origem
status_switching
origem_mapa_migracao
```

Regras mínimas:

1. `lote_origem` deve vir de `switching_canonico['lote_origem']`.
2. `lote_pos_switching` deve vir de `switching_canonico['lote_destino']`.
3. `data_switching` deve priorizar `data_switching`; se ausente, usar `data_aplicacao`; se ainda ausente, usar `data_recebimento` apenas como fallback canônico auditável.
4. `produto_destino` deve vir de `produto_destino`.
5. `valor_liquido_origem` deve vir de `valor_liquido_origem`.
6. `status_switching` deve preservar `status` quando informado; se ausente, usar marcador canônico controlado, por exemplo `classificado_promovido`.
7. `origem_mapa_migracao` deve passar a indicar fonte canônica, por exemplo `switching_canonico_etapa3`.

---

## 9. Contrato de equivalência — eventos de switching

O adaptador canônico futuro deve produzir estrutura equivalente à estrutura atualmente devolvida por:

```text
_eventos_switching_aba_operacional(contexto)
```

Campos mínimos esperados por evento:

```text
evento_switching_id
lote_origem
lote_pos_switching
data_switching
produto_destino
valor_liquido_origem
status_materializacao_passiva
origem_mapa_migracao
```

Regras mínimas:

1. `evento_switching_id` deve preferir `switching_id` quando existente.
2. Caso `switching_id` esteja ausente, o identificador sintético deve ser determinístico e baseado em `data_switching`, `lote_origem`, `lote_destino` e ordem canônica.
3. `status_materializacao_passiva` deve preservar o marcador legado esperado pelo ledger enquanto a equivalência estiver sendo testada.
4. `origem_mapa_migracao` deve ser `switching_canonico_etapa3` ou marcador equivalente auditável.

---

## 10. Regras de precedência e conflito

Quando houver múltiplos registros para o mesmo `lote_origem`, o adaptador canônico deve reproduzir a precedência observada no caminho legado:

```text
manter o switching com maior data_switching comparável
```

Empates devem ser resolvidos de forma determinística, preferencialmente por:

```text
data_switching
ordem_planilha_switching
switching_id
```

A regra de empate deve ser auditável e registrada no script diagnóstico da próxima microetapa executável.

---

## 11. Escopo proibido na implementação futura

A microetapa executável posterior não deve:

- alterar a decisão econômica;
- alterar o replay passado;
- alterar a saída canônica efetiva;
- alterar console;
- alterar XLSX;
- alterar dados ou cache;
- remover imediatamente o caminho legado;
- tornar `switching_canonico` fonte única sem comparação shadow;
- remover contenções POS existentes;
- reabrir planilha fora do bloco comparativo legado.

---

## 12. Estratégia de migração obrigatória

A migração deve ocorrer em três fases.

### 12.1. Fase 1 — Adaptador shadow

Criar adaptador puro, sem alterar ledger efetivo:

```text
switching_canonico_para_mapa_ledger_shadow(...)
switching_canonico_para_eventos_ledger_shadow(...)
```

O adaptador deve consumir apenas:

```text
contexto.dados_operacionais.switching_canonico
```

### 12.2. Fase 2 — Auditoria de equivalência

Criar script diagnóstico para comparar:

```text
mapa legado baseado em aba Switching bruta
vs
mapa shadow baseado em switching_canonico
```

e:

```text
eventos legados baseados em aba Switching bruta
vs
eventos shadow baseados em switching_canonico
```

Critérios mínimos:

```text
qtd_lotes_origem_identica
lotes_origem_identicos
lote_pos_switching_identico
data_switching_identica
produto_destino_identico
valor_liquido_origem_identico
status_equivalente
eventos_switching_qtd_identica
eventos_switching_ids_equivalentes
```

### 12.3. Fase 3 — Integração shadow no ledger

Somente após equivalência da Fase 2, conectar o adaptador ao ledger em modo shadow, preservando o caminho legado como fonte operacional efetiva.

Critérios mínimos:

```text
eventos ledger idênticos
fifo idêntico
extrato futuro idêntico
saída canônica idêntica
auditoria acrescida apenas com bloco shadow
```

---

## 13. Critérios de aprovação da V3.7P futura

A próxima microetapa executável sugerida deve ser:

```text
V17-F0-V.3.7P — Implementa adaptador switching_canonico_para_ledger_shadow
```

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Escopo seguro sugerido:

```text
nucleo/switching_canonico_ledger_shadow.py
scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py
logs/iteracoes/ME-V17-F0-V37P_IMPLEMENTA_ADAPTADOR_SWITCHING_CANONICO_LEDGER_SHADOW.md
```

Critérios de aprovação:

```text
codigo_nao_altera_ledger_operacional=True
codigo_nao_altera_saida_canonica=True
adaptador_nao_le_pacote_planilha=True
adaptador_nao_reabre_excel=True
comparacao_mapa_legado_vs_canonico=True
comparacao_eventos_legado_vs_canonico=True
sem_alteracao_observavel=True
```

---

## 14. Condição de parada

A execução da V3.7P deve parar sem promoção se qualquer uma das condições ocorrer:

```text
switching_canonico ausente ou vazio quando aba Switching bruta possui registros
lotes_origem divergentes
lote_destino divergente
valor_liquido_origem divergente acima de tolerância monetária mínima
data_switching divergente sem regra documentada
qtd_eventos divergente
identificador sintético não determinístico
alteração em extrato futuro
alteração em saída canônica
alteração em console ou XLSX
```

---

## 15. Relação com a auditoria completa da Etapa 4

A auditoria/refatoração completa da Etapa 4 deve ocorrer somente depois que o ledger deixar de depender, mesmo em modo shadow, da aba bruta `Switching` como fonte operacional.

Antes disso, uma auditoria completa da Etapa 4 misturaria:

```text
resíduo de entrada bruta
contrato da Etapa 3
estado temporal do ledger
saída canônica
pontes POS observáveis
```

Portanto, esta V3.7O define como prioridade:

```text
fechar a fronteira Etapa 3 -> ledger para switching canônico
```

antes de abrir uma V4 ampla.

---

## 16. Decisão

```text
CONTRATO_MIGRACAO_SWITCHING_BRUTO_PARA_SWITCHING_CANONICO=definido
ALTERA_LEDGER_AGORA=nao
ALTERA_SAIDA_AGORA=nao
PROXIMA_MICROETAPA_EXECUTAVEL=V17-F0-V.3.7P
AUDITORIA_COMPLETA_ETAPA4=adiada_ate_equivalencia_switching_canonico_ledger
```

---

## 17. Conclusão

A V3.7O estabelece que a próxima migração deve substituir o consumo bruto de `Switching` no ledger por um adaptador canônico baseado em `switching_canonico` da Etapa 3.

A substituição deve ocorrer primeiro em modo shadow, com comparação explícita contra o caminho legado, sem alterar ledger operacional nem saída observável.

Somente depois de equivalência comprovada será seguro promover `switching_canonico` como fonte primária do ledger e, posteriormente, abrir a auditoria/refatoração completa da Etapa 4.
