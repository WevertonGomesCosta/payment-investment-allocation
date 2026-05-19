# ME-V17-F0-V37B — Mapeia fronteira real entre Etapa 3, replay, ledger e saída canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37B
- VERSAO_CANDIDATA: V17-F0-V.3.7B
- TIPO: DOCUMENTAL / DIAGNÓSTICO / ARQUITETURAL
- CLASSE: MAPEIA_FRONTEIRA_REAL_ENTRE_ETAPA3_REPLAY_LEDGER_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.3.7A
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após a V17-F0-V.3.7A.

Commit de entrada esperado:

```text
a2d9cd9 — V17-F0-V.3.7A: registra contencoes e fronteira etapa 3
```

A V3.7A estabeleceu que:

```text
V3.6D–V3.6F estabilizam a saída observável, mas não substituem a implementação normativa da Etapa 3.
```

A V3.7B não altera código. Seu objetivo é mapear responsabilidades e definir a ordem segura de migração para a Etapa 3 normativa.

---

## 3. Objetivo da V3.7B

Mapear a fronteira real atual entre:

- Etapa 3 / canonização operacional;
- replay passado;
- ledger temporal;
- saída canônica;
- console/XLSX.

A finalidade é identificar responsabilidades ainda concentradas indevidamente em `nucleo/saida_canonica.py` e definir uma rota de migração para reduzir correções sintomáticas.

---

## 4. Evidência arquitetural de entrada

A Etapa 3 foi formalizada como:

```text
Etapa 3 = canonização operacional do PacoteEntradaResolvida validado
```

A Etapa 3 deve receber:

- `PacoteEntradaResolvida` validado;
- `PacoteValidacaoPreExecucao`.

A Etapa 3 deve produzir:

- `PacoteDadosOperacionaisCanonicos`;
- `UniversoEconomicoCanonico`.

O pacote operacional canônico deve conter:

- `carteira_canonica`;
- `universo_economico_canonico`;
- `gastos_canonicos`;
- `salarios_canonicos`;
- `switching_canonico`;
- `inventario_canonico_base`;
- `inventario_canonico_completo`;
- auditorias;
- validações.

Consequência:

```text
A saída canônica não deve ser a camada primária de nascimento, normalização ou correção patrimonial.
```

---

## 5. Diagnóstico da concentração atual em `saida_canonica.py`

A inspeção da V3.7B identificou que `construir_saida_canonica(...)` ainda acumula responsabilidades de múltiplas camadas.

### 5.1. Responsabilidades de saída observável legítimas

São responsabilidades compatíveis com `saida_canonica.py`:

- montar `extrato_passado` observável;
- montar `extrato_futuro` observável;
- montar amostra de ranking;
- montar blocos de auditoria para console/XLSX;
- agregar resultados já calculados por camadas anteriores;
- expor campos de auditoria sem alterar regra econômica.

Essas responsabilidades podem permanecer provisoriamente na saída canônica.

---

### 5.2. Responsabilidades de ledger/estado temporal ainda acionadas pela saída

`construir_saida_canonica(...)` chama diretamente:

```python
ledger_result = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}
```

Diagnóstico:

- a saída canônica ainda dispara a construção do ledger temporal;
- isso mistura montagem observável com produção de estado temporal;
- a médio prazo, o ledger deveria ser produzido antes da saída, como artefato do fluxo operacional, e apenas consumido pela saída.

Classificação correta:

```text
responsabilidade de replay/ledger, não de saída canônica
```

Risco:

- novas correções podem ser aplicadas em `saida_canonica.py` apenas porque o ledger nasce dentro dela;
- isso dificulta testes unitários, rastreabilidade e governança por etapas.

---

### 5.3. Responsabilidades de Etapa 3 ainda tratadas pela saída

A saída canônica ainda executa lógica de detecção ou contenção relacionada ao nascimento canônico dos POS:

- `_pos_canonico_ativo(contexto)`;
- `destinos_pos_switching_passivos_para_situacao`;
- desativação da ponte passiva POS quando os POS já nascem em `inventario_canonico`.

Diagnóstico:

- a decisão sobre o nascimento canônico de POS pertence à Etapa 3;
- a saída pode auditar se os POS nasceram canonicamente;
- mas a saída não deveria decidir, no longo prazo, se deve materializar, rematerializar ou bloquear artefatos operacionais.

Classificação correta:

```text
responsabilidade de Etapa 3 / canonização operacional, atualmente contida na saída
```

---

### 5.4. Responsabilidades de replay/histórico ainda corrigidas pela saída

A V3.6F introduziu neutralização observável de origens migradas:

- `_valor_monetario_situacao(...)`;
- `_neutralizar_origens_migradas_situacao(...)`.

A função remove da camada ativa origens já migradas por switching, preservando auditoria, histórico e destinos POS.

Diagnóstico:

- a contenção é válida para estabilizar a saída;
- porém, a decisão de que uma origem migrada não é mais ativo operacional deveria nascer antes, no estado temporal ou no inventário canônico completo;
- a saída deveria consumir o status final, não inferir e neutralizar ativos.

Classificação correta:

```text
responsabilidade de estado temporal/replay ou Etapa 3, atualmente contida na saída
```

---

### 5.5. Responsabilidades de pagamento/consumo ainda aplicadas pela saída

`construir_saida_canonica(...)` ainda aplica:

```python
_aplicar_consumo_pagamentos_passados_lotes_pos_switching(...)
```

Diagnóstico:

- consumo de pagamentos passados é regra temporal;
- se o consumo altera lotes ativos/exauridos, sua fonte normativa deve ser replay/ledger;
- a saída pode apresentar a consequência, mas não deveria ser o ponto primário de aplicação de consumo.

Classificação correta:

```text
responsabilidade de replay passado / ledger temporal, atualmente aplicada na saída
```

---

## 6. Mapa de fronteiras normativas

### 6.1. Etapa 1 — Entrada resolvida

Responsabilidades:

- resolver caminho de planilha;
- resolver abas;
- resolver colunas;
- resolver cache CDI;
- preservar quadros brutos e estruturais resolvidos;
- produzir `PacoteEntradaResolvida`.

Não deve:

- aplicar decisão econômica;
- simular pagamento;
- criar lote pós-switching;
- neutralizar origem migrada;
- materializar saída.

---

### 6.2. Etapa 2 — Validação pré-execução

Responsabilidades:

- validar existência de abas e colunas obrigatórias;
- validar tipos mínimos;
- validar consistência estrutural;
- bloquear execução se entrada resolvida for inválida;
- produzir `PacoteValidacaoPreExecucao`.

Não deve:

- corrigir dados;
- criar artefatos canônicos;
- executar replay;
- montar saída.

---

### 6.3. Etapa 3 — Canonização operacional

Responsabilidades normativas:

- produzir `carteira_canonica`;
- produzir `universo_economico_canonico`;
- produzir `gastos_canonicos`;
- produzir `salarios_canonicos`;
- produzir `switching_canonico`;
- produzir `inventario_canonico_base`;
- produzir `inventario_canonico_completo`;
- classificar lotes POS como canônicos;
- registrar vínculo origem/destino de switching;
- classificar origens migradas como estado operacional não ativo, quando essa classificação for determinística a partir do switching realizado;
- emitir auditorias canônicas.

Não deve:

- executar pagamentos futuros;
- decidir switching candidato futuro;
- calcular ledger diário completo;
- renderizar console/XLSX.

---

### 6.4. Replay passado

Responsabilidades:

- aplicar pagamentos passados;
- consumir saldos por lote;
- registrar saques reais;
- marcar exauridos por saque;
- preservar histórico de consumo;
- lidar com carência, data, saldo, rendimento e status temporal observado.

Não deve:

- nascer artefatos canônicos de entrada;
- decidir estrutura da Etapa 3;
- renderizar saída final.

---

### 6.5. Ledger temporal

Responsabilidades:

- produzir estado temporal auditável;
- consolidar eventos por data;
- representar saldos disponíveis;
- representar vencimentos;
- representar pagamentos futuros;
- representar consumo futuro planejado;
- expor artefatos para saída e auditoria.

Não deve:

- resolver planilha;
- alterar contrato;
- renderizar console/XLSX.

---

### 6.6. Saída canônica

Responsabilidades normativas finais:

- consumir artefatos já produzidos;
- montar `PacoteSaidaCanonica`;
- expor blocos observáveis;
- agregar auditorias;
- não criar estado patrimonial novo;
- não corrigir origem de inconsistência temporal ou canônica;
- conter apenas filtros/apresentações transitórias explicitamente registradas.

---

## 7. Responsabilidades hoje indevidamente concentradas em `saida_canonica.py`

| Responsabilidade atual em `saida_canonica.py` | Fronteira correta | Prioridade de migração |
|---|---|---:|
| Chamar `construir_ledger_temporal_conjunto(...)` | Ledger temporal produzido antes da saída | Alta |
| Detectar POS canônico ativo | Etapa 3 / auditoria canônica | Média |
| Bloquear ponte passiva POS | Etapa 3 / compatibilidade transitória | Média |
| Aplicar consumo de pagamentos passados em POS | Replay passado / ledger | Alta |
| Construir/reconciliar origens migradas por switching | Etapa 3 + replay/ledger | Alta |
| Neutralizar origens migradas ainda ativas | Etapa 3 ou estado temporal | Alta |
| Agregar dezenas de chaves internas do ledger na auditoria | Interface formal do ledger | Média |
| Gerar saída observável final | Saída canônica | Correta |

---

## 8. Ordem segura de migração

### Fase 1 — Diagnosticar contratos de artefatos

Criar uma microetapa documental para especificar os artefatos formais entre camadas:

- `PacoteDadosOperacionaisCanonicos`;
- `PacoteReplayPassado`;
- `PacoteLedgerTemporal`;
- `PacoteSaidaCanonica`.

Objetivo:

- definir quais campos cada pacote produz;
- impedir que a saída consuma estruturas soltas e dicionários extensos sem contrato.

---

### Fase 2 — Isolar ledger como artefato pré-saída

Mover gradualmente a chamada de `construir_ledger_temporal_conjunto(...)` para uma etapa anterior ao `construir_saida_canonica(...)`.

A saída deve receber o resultado do ledger já pronto.

Critério de parada:

- `saida_canonica.py` não deve disparar motor temporal;
- deve apenas consumir `ledger_result` ou pacote equivalente.

---

### Fase 3 — Reclassificar POS e origens migradas na Etapa 3

A Etapa 3 deve produzir uma estrutura canônica em que:

- POS já nascem como lotes canônicos com origem `lote_pos_switching_normalizado`;
- origens migradas já nascem classificadas como não ativas operacionalmente;
- vínculos origem/destino são explícitos;
- não há necessidade de ponte passiva POS para Situação Atual.

---

### Fase 4 — Reposicionar consumo passado no replay/ledger

Consumo de pagamentos passados em lotes POS deve sair da saída e passar para o replay/ledger.

Critério:

- a Situação Atual deve refletir saldos já consumidos sem aplicar consumo dentro da camada de saída.

---

### Fase 5 — Reduzir `saida_canonica.py` a agregador observável

Após as migrações, `saida_canonica.py` deve:

- receber artefatos formais;
- montar tabelas finais;
- preservar auditorias;
- não corrigir patrimônio;
- não alterar status operacional;
- não executar ledger.

---

## 9. Recomendações de microetapas seguintes

A próxima microetapa não deve alterar código ainda.

Recomendação imediata:

```text
V17-F0-V.3.7C — Especifica contratos mínimos entre Etapa 3, replay, ledger e saída canônica
```

Tipo:

```text
DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

- definir campos obrigatórios e responsabilidades de cada pacote;
- impedir novas correções sintomáticas em `saida_canonica.py`;
- preparar uma futura implementação controlada com microetapas pequenas.

---

## 10. Critério para futuras correções

A partir desta V3.7B, qualquer nova inconsistência patrimonial deve ser classificada antes de correção:

```text
1. entrada resolvida?
2. validação pré-execução?
3. Etapa 3 / canonização?
4. replay passado?
5. ledger temporal?
6. saída observável?
```

Se a causa estiver em 3, 4 ou 5, é proibido corrigir diretamente em `saida_canonica.py`, salvo contenção transitória explicitamente registrada e aprovada.

---

## 11. Conclusão

A V3.7B confirma que `saida_canonica.py` ainda concentra responsabilidades de múltiplas camadas.

A correção arquitetural não deve começar por uma nova alteração de código.

A próxima ação deve ser especificar contratos mínimos entre Etapa 3, replay, ledger e saída, para que futuras microetapas movam responsabilidades gradualmente e com validação.
