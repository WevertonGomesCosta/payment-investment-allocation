# ME-V17-F0-V37J — Especifica PacoteLedgerTemporal mínimo e adaptador shadow do ledger atual

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37J
- VERSAO_CANDIDATA: V17-F0-V.3.7J
- TIPO: DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: ESPECIFICA_PACOTE_LEDGER_TEMPORAL_E_ADAPTADOR_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7I
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após:

```text
57bec25 — V17-F0-V.3.7I: diagnostica dependencias ledger saida
```

A V3.7I identificou que a saída canônica ainda chama `construir_ledger_temporal_conjunto(...)` diretamente e que o ledger atual ainda depende de contexto amplo, planilha bruta, switching shadow e injeção local de POS.

A V3.7I também definiu que nenhuma ponte deve ser removida antes da criação de um envelope formal para o ledger.

---

## 3. Objetivo

Especificar:

1. o contrato mínimo de `PacoteLedgerTemporal`;
2. o contrato do adaptador shadow do ledger atual;
3. as entradas e saídas mínimas do adaptador;
4. as garantias de equivalência exigidas antes de qualquer promoção;
5. as restrições para impedir alteração de saída, motor, replay ou dados nesta fase.

A V3.7J é exclusivamente documental.

---

## 4. Decisão arquitetural

A próxima migração executável deve criar um envelope formal:

```text
PacoteLedgerTemporal
```

Esse pacote deve embrulhar, inicialmente em modo shadow, o retorno atual de:

```text
construir_ledger_temporal_conjunto(...)
```

sem alterar o comportamento observável da saída canônica.

A saída canônica ainda não deve ser modificada para depender obrigatoriamente do novo pacote. A primeira implementação futura deve apenas construir o pacote shadow e compará-lo contra o retorno legado.

---

## 5. Papel do PacoteLedgerTemporal

O `PacoteLedgerTemporal` é o contrato entre:

```text
Replay passado / artefatos canônicos / eventos temporais
        |
        v
Ledger temporal
        |
        v
Saída canônica
```

Ele deve representar o estado temporal já processado, pronto para consumo por saída canônica, motores futuros ou auditorias.

Ele não deve resolver planilha, não deve canonizar entrada, não deve executar replay e não deve formatar console ou XLSX.

---

## 6. Entradas normativas futuras do PacoteLedgerTemporal

As entradas normativas finais são:

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteReplayPassado
PacoteCacheCDIDiario
calendario_financeiro
data_referencia
config temporal mínima
eventos ou decisões temporais promovidas
```

Entretanto, na primeira implementação shadow, o adaptador pode receber também os mesmos insumos usados pelo ledger atual, desde que isso seja declarado como transição controlada.

---

## 7. Entrada transitória permitida para o adaptador shadow

A primeira implementação futura poderá receber:

```text
quadro_futuro
mapa_central
contexto
```

Esses são os insumos atuais de `construir_ledger_temporal_conjunto(...)`.

Essa permissão é transitória e serve apenas para preservar equivalência durante a criação do envelope.

O adaptador shadow não deve ampliar dependências nem criar novas leituras de planilha, contexto ou saída.

---

## 8. Interface documental do adaptador shadow

Nome normativo sugerido:

```text
construir_pacote_ledger_temporal_shadow(...)
```

Assinatura conceitual transitória:

```text
construir_pacote_ledger_temporal_shadow(
    quadro_futuro,
    mapa_central,
    contexto,
    *,
    modo_shadow=True,
) -> PacoteLedgerTemporal
```

Essa assinatura não é implementação obrigatória nesta microetapa documental. Ela define o contrato da futura microetapa executável.

---

## 9. Campos mínimos do PacoteLedgerTemporal

O pacote deve conter, no mínimo:

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

---

## 10. Mapeamento mínimo do retorno atual do ledger

O retorno atual de `construir_ledger_temporal_conjunto(...)` deve ser embrulhado sem perda de informação.

Mapeamento inicial recomendado:

| Retorno atual | Campo no PacoteLedgerTemporal | Observação |
|---|---|---|
| `eventos` | `eventos_temporais` | Campo central para extrato futuro |
| `fifo_candidatos_avaliados` | `fifo_candidatos_avaliados` | Preservar para auditorias FIFO |
| auditorias internas POS/recebidos, se presentes | `auditoria_ledger_temporal` | Consolidar sem renomear semanticamente |
| alertas ou bloqueios operacionais, se presentes | `alertas_temporais` | Preservar classificação original |
| dados de saldo por evento | `saldos_por_lote` / `saldos_disponiveis_por_data` | Pode ser derivado inicialmente dos eventos |
| pagamentos processados no futuro | `pagamentos_futuros_processados` | Derivado dos eventos por pagamento_id |

Quando algum campo mínimo ainda não existir no retorno atual, o adaptador deve preenchê-lo com estrutura vazia auditável, não com inferência econômica nova.

---

## 11. Contrato de `eventos_temporais`

Cada evento temporal deve conter, quando aplicável:

```text
evento_id
pagamento_id
data_evento
tipo_evento
lote_id
fonte_id
status
motivo_bloqueio
cobertura_integral
saldo_antes
bruto
imposto
liquido
consumo
saldo_depois
fonte_temporal
status_funcional
lote_origem_switching
lote_pos_switching
produto_destino
evento_switching_id
origem_evento_temporal
```

Eventos derivados do ledger atual devem manter nomes e valores compatíveis com a saída atual para permitir comparação determinística.

---

## 12. Contrato de `estado_temporal_por_data`

O campo `estado_temporal_por_data` deve representar, no mínimo:

```text
data
saldo_total_disponivel
qtd_lotes_ativos
qtd_lotes_exauridos
qtd_fontes_disponiveis
qtd_pagamentos_processados
qtd_alertas
```

Na primeira versão shadow, esse campo pode ser derivado dos eventos existentes ou permanecer vazio com auditoria explícita:

```text
estado_temporal_por_data_shadow_nao_materializado=True
```

Não é permitido criar novo cálculo econômico apenas para preencher esse campo.

---

## 13. Contrato de `saldos_por_lote`

O campo `saldos_por_lote` deve conter, quando disponível:

```text
lote_id
data_referencia_temporal
saldo_antes
saldo_depois
saldo_liquido
saldo_bruto
status_funcional
fonte_temporal
migrado_em
lote_origem_switching
lote_pos_switching
```

Na primeira versão shadow, pode ser derivado de eventos do ledger atual, desde que sem alterar decisão, consumo ou saldos usados pela saída.

---

## 14. Contrato de `pagamentos_futuros_processados`

O campo `pagamentos_futuros_processados` deve conter, quando aplicável:

```text
pagamento_id
data_pagamento
valor_pagamento
lote_sugerido_operacional
status
motivo_bloqueio
cobertura_integral
pacote_dia
necessita_switching
switching_antes_pagamento
switching_depois_pagamento
```

Esse campo deve ser derivado de `eventos_temporais` na versão shadow.

---

## 15. Contrato de `fontes_elegiveis_por_data`

O campo `fontes_elegiveis_por_data` deve conter, quando materializado:

```text
data
fonte_id
tipo_fonte
lote_id
saldo_disponivel
elegivel
motivo_inelegibilidade
```

Na versão shadow inicial, esse campo pode permanecer vazio com auditoria explícita, pois o objetivo é encapsular o retorno atual do ledger, não expandir sua capacidade.

---

## 16. Contrato de `alertas_temporais`

O campo `alertas_temporais` deve conter:

```text
alerta_id
classe_alerta
severidade
data_evento
pagamento_id
lote_id
mensagem
origem_alerta
```

Alertas já existentes no retorno atual devem ser preservados.

Alertas novos só podem ser estruturais, isto é, sobre ausência de campos, inconsistência de pacote ou divergência de equivalência. Não podem alterar decisão econômica.

---

## 17. Contrato de `auditoria_ledger_temporal`

A auditoria deve conter, no mínimo:

```text
ok
modo_shadow
origem_execucao
qtd_eventos_temporais
qtd_pagamentos_futuros_processados
qtd_fifo_candidatos_avaliados
qtd_alertas_temporais
campos_ausentes_preenchidos_vazios
usa_contexto_amplo
usa_planilha_bruta
usa_switching_shadow
usa_pos_injetado
compatibilidade_retorno_legado
```

Na primeira versão shadow, os campos abaixo devem registrar a realidade atual, não ocultá-la:

```text
usa_contexto_amplo=True
usa_planilha_bruta=True ou False conforme inspeção/execução
usa_switching_shadow=True ou False conforme inspeção/execução
usa_pos_injetado=True ou False conforme inspeção/execução
```

---

## 18. Contrato de `validacao_ledger_temporal`

A validação deve conter:

```text
ok
erros_bloqueantes
avisos
evidencias
```

Erros bloqueantes mínimos:

```text
eventos_temporais_ausente_sem_justificativa
pagamento_id_ausente_em_evento_de_pagamento
status_ausente_em_evento_processado
saldo_depois_invalido_quando_cobertura_integral_sim
pacote_ledger_temporal_inconsistente_com_retorno_legado
```

Avisos mínimos:

```text
estado_temporal_por_data_nao_materializado
fontes_elegiveis_por_data_nao_materializado
saldos_por_lote_derivado_dos_eventos
uso_transitorio_de_contexto_amplo
uso_transitorio_de_planilha_bruta
uso_transitorio_de_switching_shadow
```

---

## 19. Garantia de equivalência shadow

A primeira implementação executável deve provar equivalência entre:

```text
retorno_legado = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto)
pacote_shadow = construir_pacote_ledger_temporal_shadow(quadro_futuro, mapa_central, contexto)
```

Critérios mínimos:

```text
len(retorno_legado['eventos']) == len(pacote_shadow.eventos_temporais)
len(retorno_legado['fifo_candidatos_avaliados']) == len(pacote_shadow.fifo_candidatos_avaliados)
mesmos pagamento_id nos eventos
mesmos status por pagamento_id
mesmos motivos de bloqueio por pagamento_id
mesmos saldos e consumos quando presentes
sem alteração de extrato futuro
sem alteração de extrato passado
sem alteração de situação atual
sem alteração de console
sem alteração de XLSX
```

---

## 20. Proibições da futura implementação shadow

A futura microetapa executável não poderá:

- remover chamada atual de `construir_ledger_temporal_conjunto(...)` em `saida_canonica.py`;
- alterar `saida_canonica.py` para consumir obrigatoriamente o pacote novo;
- remover contenções POS;
- remover complemento de pagamentos passados POS;
- alterar `ledger_temporal_conjunto.py` além do mínimo necessário para expor o adaptador, caso essa seja a estratégia escolhida;
- alterar motor econômico;
- alterar replay;
- alterar Etapa 3;
- alterar saída observável;
- alterar console;
- alterar XLSX;
- alterar dados ou cache.

---

## 21. Localização recomendada para a futura implementação

Duas opções são aceitáveis:

### Opção A — novo módulo dedicado

```text
nucleo/pacote_ledger_temporal.py
```

Vantagem:

```text
separa contrato novo do ledger legado
```

### Opção B — mesmo módulo do ledger atual

```text
nucleo/ledger_temporal_conjunto.py
```

Vantagem:

```text
menor dispersão inicial
```

Decisão recomendada:

```text
Opção A — novo módulo dedicado
```

Motivo:

A V3.7I mostrou que `ledger_temporal_conjunto.py` já possui acoplamentos transitórios. Um módulo dedicado permite criar o envelope sem aumentar a complexidade do arquivo legado.

---

## 22. Script diagnóstico futuro recomendado

A primeira implementação shadow deve vir acompanhada de script diagnóstico:

```text
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

Esse script deve:

```text
carregar contexto baseline
executar ledger legado
executar adaptador shadow
comparar contagens
comparar pagamento_id
comparar status
comparar motivo_bloqueio
comparar saldos/consumos quando presentes
confirmar que saída canônica não mudou
emitir CSV/console diagnóstico, se necessário
```

---

## 23. Critérios de promoção futura

O `PacoteLedgerTemporal` só poderá substituir a chamada direta ao ledger na saída canônica depois que:

```text
adaptador shadow existir
script diagnóstico passar
saída atual vs saída shadow forem equivalentes
extrato passado permanecer idêntico
extrato futuro permanecer idêntico
situação atual permanecer idêntica
console permanecer idêntico ou com diferenças documentadas apenas de auditoria
XLSX permanecer idêntico ou com diferenças documentadas apenas de auditoria
```

---

## 24. Próxima microetapa recomendada

A próxima microetapa deve ser executável, mas ainda sem alterar saída:

```text
V17-F0-V.3.7K — Implementa PacoteLedgerTemporal shadow sem alterar saída canônica
```

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO DE SAÍDA
```

Escopo permitido sugerido:

```text
nucleo/pacote_ledger_temporal.py
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
logs/iteracoes/ME-V17-F0-V37K_IMPLEMENTA_PACOTE_LEDGER_TEMPORAL_SHADOW.md
```

Escopo proibido sugerido:

```text
nucleo/saida_canonica.py, salvo import ou chamada shadow opcional se estritamente necessário e sem alterar saída
nucleo/saida_observavel.py
aplicacao/principal.py
dados/
cache/
saidas/
motor econômico
replay
Etapa 3
```

---

## 25. Critérios de aprovação desta V3.7J

A V3.7J é aprovada se:

- não altera código;
- não altera dados;
- não altera saída;
- não altera ledger;
- especifica `PacoteLedgerTemporal` mínimo;
- especifica o adaptador shadow;
- define campos mínimos;
- define mapeamento do retorno legado;
- define validação e auditoria;
- define equivalência shadow;
- define proibições para a implementação futura;
- preserva a rota V3.7G e o diagnóstico V3.7I.

---

## 26. Conclusão

A V3.7J fecha o contrato mínimo necessário para iniciar a primeira microetapa executável de desacoplamento entre ledger e saída canônica.

A estratégia aprovada é criar primeiro um envelope shadow, sem remoção de ponte histórica e sem alteração observável.
