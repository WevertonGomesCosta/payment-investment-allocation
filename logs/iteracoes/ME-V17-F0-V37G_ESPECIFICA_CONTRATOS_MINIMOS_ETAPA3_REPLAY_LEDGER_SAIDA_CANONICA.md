# ME-V17-F0-V37G — Especifica contratos mínimos entre Etapa 3, replay, ledger e saída canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37G
- VERSAO_CANDIDATA: V17-F0-V.3.7G
- TIPO: DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: ESPECIFICA_CONTRATOS_MINIMOS_ETAPA3_REPLAY_LEDGER_SAIDA_CANONICA
- BASELINE_DE_ENTRADA: V17-F0-V.3.7F.1
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
2693ea7 — V17-F0-V.3.7F.1: atualiza documento etapa3 fluxograma normativo
```

A V3.7F.1 atualizou a versão documental da Etapa 3 para explicitar a canonização operacional final, o `PacoteAuditoriaCanonizacaoOperacional` e o fluxograma Mermaid normativo.

A presente V3.7G não implementa esses contratos em código. Ela especifica os contratos mínimos que devem orientar as próximas microetapas de migração arquitetural.

---

## 3. Objetivo

Especificar os contratos mínimos entre:

1. Etapa 3 — Canonização operacional;
2. Replay passado;
3. Ledger temporal;
4. Saída canônica;
5. Saída observável / console / XLSX.

O objetivo é impedir que uma camada produza, corrija ou reinterprete estado que pertence a outra camada.

---

## 4. Cadeia contratual mínima

```text
PacoteEntradaResolvida validado
        |
        v
PacoteValidacaoPreExecucao aprovado
        |
        v
Etapa 3 — Canonização operacional
        |
        +--> PacoteDadosOperacionaisCanonicos
        +--> UniversoEconomicoCanonico
        +--> PacoteAuditoriaCanonizacaoOperacional
        |
        v
Replay passado
        |
        +--> PacoteReplayPassado
        |
        v
Ledger temporal
        |
        +--> PacoteLedgerTemporal
        |
        v
Saída canônica
        |
        +--> PacoteSaidaCanonica
        |
        v
Saída observável / console / XLSX
```

---

## 5. Contrato mínimo — PacoteDadosOperacionaisCanonicos

### 5.1. Produtor

```text
Etapa 3 — Canonização operacional
```

### 5.2. Consumidores

```text
Replay passado
Ledger temporal
Saída canônica
motores posteriores
scripts de auditoria canônica
```

### 5.3. Entradas normativas

```text
PacoteEntradaResolvida validado
PacoteValidacaoPreExecucao aprovado
```

### 5.4. Campos mínimos obrigatórios

```text
carteira_canonica
universo_economico_canonico
gastos_canonicos
salarios_canonicos
recebidos_canonicos
switching_canonico
inventario_canonico_base
inventario_canonico_completo
auditoria_carteira
auditoria_gastos
auditoria_recebidos
auditoria_switching
auditoria_inventario_base
auditoria_inventario_completo
auditoria_canonizacao_operacional
validacoes_canonicas
```

### 5.5. Regras mínimas de inventário

O `inventario_canonico_base` contém apenas lotes derivados diretamente da entrada estrutural de lotes.

O `inventario_canonico_completo` contém:

- lotes do inventário canônico base;
- lotes POS derivados de switchings já realizados;
- classificação das origens migradas por switching;
- vínculos origem-destino quando houver switching declarado.

O artefato `lotes_pos_switching_normalizados` pode existir internamente, mas não deve ser tratado como fonte operacional paralela.

### 5.6. Campos mínimos de lote canônico

Cada lote canônico deve conter, quando aplicável:

```text
lote_id
origem_registro
status_lote_canonico
data_recebimento
data_aplicacao
data_base_fiscal
valor_original
produto_key
produto_nome_canonico
produto_encontrado
aportado
nao_aportado_disponivel
nao_aportado_exaurido
recebido_futuro_nao_disponivel
ativo_pos_switching
migrado_por_switching
lote_origem_switching
lote_destino_switching
switching_id
```

### 5.7. Campos mínimos de switching canônico

Cada switching já realizado deve conter, quando aplicável:

```text
switching_id
lote_origem
lote_destino
produto_origem
produto_destino
data_recebimento
data_aplicacao
data_switching
valor_liquido_origem
ganho_estimado
status
vinculo_origem_destino_valido
```

### 5.8. Responsabilidades proibidas

O `PacoteDadosOperacionaisCanonicos` não deve conter:

- replay de pagamentos passados;
- consumo histórico de lotes;
- rendimento acumulado;
- saldo temporal após saque;
- decisão de pagamento futuro;
- switching candidato do motor;
- ledger temporal;
- formatação de console ou XLSX.

---

## 6. Contrato mínimo — UniversoEconomicoCanonico

### 6.1. Produtor

```text
Etapa 3 — Canonização operacional
```

### 6.2. Consumidores

```text
motores econômicos posteriores
replay
ledger
saída canônica
auditorias de consistência econômica
```

### 6.3. Campos mínimos obrigatórios

```text
produtos_canonicos
mapa_produtos
carteira_canonica
ranking_carteira
elegibilidade_basica_produtos
fontes_canonicas
lotes_canonicos
eventos_estruturais
relacoes_origem_destino_switching
auditoria_universo_economico
```

### 6.4. Responsabilidades permitidas

O universo econômico canônico pode:

- consolidar produtos e chaves canônicas;
- resolver produto de lote contra carteira canônica;
- expor ranking estrutural de carteira;
- registrar elegibilidade básica estrutural;
- registrar relações origem-destino de switching já realizado.

### 6.5. Responsabilidades proibidas

O universo econômico canônico não pode:

- calcular rendimento terminal;
- decidir melhor produto;
- recomendar switching candidato;
- liquidar pagamento;
- gerar carteira futura;
- aplicar gates econômicos;
- simular cenários.

---

## 7. Contrato mínimo — PacoteAuditoriaCanonizacaoOperacional

### 7.1. Produtor

```text
Etapa 3 — Canonização operacional
```

### 7.2. Consumidores

```text
auditorias de transição
replay passado
ledger temporal
saída canônica
release checker futuro
```

### 7.3. Campos mínimos obrigatórios

```text
ok
erros_bloqueantes
avisos
evidencias
resumo_shapes
resumo_ids
resumo_datas
resumo_valores
resumo_pos_switching
resumo_origens_migradas
resumo_inventario_base_vs_completo
```

### 7.4. Validações mínimas

O pacote deve validar:

- presença de todos os artefatos canônicos obrigatórios;
- ausência de duplicidade bloqueante de `lote_id` em inventário completo;
- presença de IDs obrigatórios;
- parseabilidade e consistência de datas;
- valores monetários não negativos quando aplicável;
- relação entre origem migrada e destino POS;
- não exposição de POS como fonte paralela fora do inventário completo;
- consistência entre switching canônico e inventário completo.

---

## 8. Contrato mínimo — PacoteReplayPassado

### 8.1. Produtor

```text
Replay passado
```

### 8.2. Consumidores

```text
Ledger temporal
Saída canônica
auditorias de reconciliação histórica
motores posteriores que dependam do estado pós-replay
```

### 8.3. Entradas normativas

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional aprovado
PacoteCacheCDIDiario
calendario_financeiro
data_referencia
config operacional mínima de replay
```

### 8.4. Saídas mínimas obrigatórias

```text
eventos_passados
pagamentos_passados_processados
saques_por_lote
lotes_exauridos_por_saque
saldos_pos_replay_por_lote
bloqueios_replay
auditoria_replay_passado
```

### 8.5. Responsabilidades permitidas

O replay pode:

- consumir pagamentos passados declarados;
- aplicar saques históricos aos lotes informados;
- calcular saldo pós-replay por lote;
- classificar exaustão por saque;
- registrar bloqueios por cadastro, carência, lote futuro, lote inexistente ou fonte ausente;
- produzir auditoria histórica.

### 8.6. Responsabilidades proibidas

O replay não pode:

- criar lote canônico novo;
- criar POS canônico novo;
- alterar carteira canônica;
- alterar switching canônico;
- decidir pagamento futuro;
- decidir switching candidato;
- gerar ledger futuro;
- formatar saída final;
- corrigir dados de entrada sem registro de bloqueio.

---

## 9. Contrato mínimo — PacoteLedgerTemporal

### 9.1. Produtor

```text
Ledger temporal
```

### 9.2. Consumidores

```text
Saída canônica
motores temporais futuros
auditorias econômicas
console/XLSX por meio da saída canônica
```

### 9.3. Entradas normativas

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteReplayPassado
PacoteCacheCDIDiario
calendario_financeiro
data_referencia
config temporal mínima
```

### 9.4. Saídas mínimas obrigatórias

```text
eventos_temporais
estado_temporal_por_data
saldos_por_lote
saldos_disponiveis_por_data
vencimentos_processados
pagamentos_futuros_processados
fontes_elegiveis_por_data
alertas_temporais
auditoria_ledger_temporal
```

### 9.5. Responsabilidades permitidas

O ledger pode:

- consolidar estado temporal por data;
- carregar o estado pós-replay como ponto inicial;
- processar vencimentos como transição temporal;
- registrar disponibilidade por data;
- registrar pagamentos futuros processados quando o motor temporal os definir;
- consolidar saldos por lote e por fonte.

### 9.6. Responsabilidades proibidas

O ledger não pode:

- resolver planilha;
- canonizar entrada;
- criar produto canônico;
- criar lote canônico de Etapa 3;
- alterar replay passado já fechado;
- renderizar console ou XLSX;
- recalcular saída canônica por regra própria.

---

## 10. Contrato mínimo — PacoteSaidaCanonica

### 10.1. Produtor

```text
Saída canônica
```

### 10.2. Consumidores

```text
Saída observável
console
XLSX
scripts de auditoria de apresentação
```

### 10.3. Entradas normativas

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional
PacoteReplayPassado
PacoteLedgerTemporal
contexto_execucao
config de saída
```

### 10.4. Saídas mínimas obrigatórias

```text
situacao_atual_canonica
extrato_passado_canonico
extrato_futuro_canonico
switching_canonico_saida
carteira_canonica_saida
resumos_patrimoniais_canonicos
auditoria_saida_canonica
```

### 10.5. Responsabilidades permitidas

A saída canônica pode:

- agregar artefatos já produzidos;
- montar tabelas canônicas finais;
- expor extratos e resumos a partir de replay e ledger;
- registrar auditoria de montagem da saída;
- preparar dados para saída observável.

### 10.6. Responsabilidades proibidas

A saída canônica não pode:

- executar replay;
- disparar ledger;
- neutralizar origem migrada por regra própria;
- criar POS canônico;
- corrigir inventário canônico;
- consumir pagamentos passados diretamente;
- recalcular estado patrimonial independente do ledger;
- decidir pagamento ou switching.

---

## 11. Contrato mínimo — Saída observável / console / XLSX

### 11.1. Produtor

```text
Camada de apresentação
```

### 11.2. Entrada normativa

```text
PacoteSaidaCanonica
```

### 11.3. Saídas permitidas

```text
console operacional
arquivo XLSX operacional
visões resumidas
visões de auditoria
```

### 11.4. Responsabilidades permitidas

A camada observável pode:

- selecionar colunas;
- ordenar linhas;
- renomear cabeçalhos de apresentação;
- aplicar filtros estritamente visuais;
- formatar valores monetários, datas e percentuais;
- separar abas do XLSX.

### 11.5. Responsabilidades proibidas

A camada observável não pode:

- alterar totais canônicos;
- alterar status de lote;
- remover duplicidade patrimonial por regra econômica;
- criar ou consumir pagamentos;
- alterar replay;
- alterar ledger;
- alterar switching;
- alterar saldos.

---

## 12. Regras de passagem entre camadas

### 12.1. Etapa 3 para replay

Replay só pode iniciar se:

```text
PacoteDadosOperacionaisCanonicos.ok conceitual = verdadeiro
PacoteAuditoriaCanonizacaoOperacional sem erros bloqueantes
inventario_canonico_completo presente
switching_canonico presente
relacoes origem-destino auditadas
```

### 12.2. Replay para ledger

Ledger só pode iniciar se:

```text
PacoteReplayPassado disponível
bloqueios_replay classificados
saldos_pos_replay_por_lote presentes
lotes_exauridos_por_saque classificados
```

### 12.3. Ledger para saída canônica

Saída canônica só pode iniciar se:

```text
PacoteLedgerTemporal disponível
estado_temporal_por_data presente
saldos_por_lote presentes
alertas_temporais registrados
```

### 12.4. Saída canônica para saída observável

Saída observável só pode iniciar se:

```text
PacoteSaidaCanonica disponível
auditoria_saida_canonica presente
resumos_patrimoniais_canonicos presentes
extratos canônicos presentes
```

---

## 13. Critérios de migração futura

A migração futura deve seguir a ordem:

1. encapsular a Etapa 3 normativa como produtora de `PacoteDadosOperacionaisCanonicos`, `UniversoEconomicoCanonico` e `PacoteAuditoriaCanonizacaoOperacional`;
2. mover consumo de pagamentos passados para `PacoteReplayPassado`;
3. mover estado temporal para `PacoteLedgerTemporal`;
4. reduzir `saida_canonica.py` a agregador de pacotes já produzidos;
5. limitar `saida_observavel.py`, console e XLSX à apresentação.

Nenhuma microetapa futura deve expandir responsabilidades transitórias de `saida_canonica.py`.

---

## 14. Critérios de validação documental desta V3.7G

A V3.7G é aprovada se:

- especifica contratos mínimos das cinco camadas;
- não altera código;
- não altera dados;
- não cria scripts;
- não altera saída;
- registra campos mínimos obrigatórios;
- registra responsabilidades proibidas;
- registra regras de passagem;
- preserva a Etapa 3 como produtora de artefatos canônicos;
- preserva replay, ledger e saída como camadas consumidoras.

---

## 15. Conclusão

A V3.7G formaliza os contratos mínimos necessários para iniciar migrações futuras sem misturar canonização, replay, ledger e saída.

A próxima microetapa deve ser escolhida entre:

1. criar auditoria documental dos contratos mínimos;
2. criar script diagnóstico que verifique se o código atual viola os contratos;
3. iniciar a primeira migração controlada, começando pela Etapa 3 como produtora explícita dos pacotes finais.
