# ME-V17-F0-V37K — Implementa PacoteLedgerTemporal shadow sem alterar saída canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37K
- VERSAO_CANDIDATA: V17-F0-V.3.7K
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO DE SAÍDA
- CLASSE: IMPLEMENTA_PACOTE_LEDGER_TEMPORAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7J
- ALTERA_CODIGO: sim
- ALTERA_LEDGER_LEGADO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após:

```text
44aef47 — V17-F0-V.3.7J: especifica pacote ledger temporal shadow
```

A V3.7J determinou que a primeira etapa executável deveria criar um envelope shadow para o retorno atual de:

```text
construir_ledger_temporal_conjunto(...)
```

sem alterar saída canônica, replay, Etapa 3, motor, console, XLSX, dados ou cache.

---

## 3. Objetivo

Implementar um adaptador shadow que:

1. crie `PacoteLedgerTemporal`;
2. embrulhe o retorno legado do ledger atual;
3. preserve eventos e candidatos FIFO;
4. derive campos mínimos auditáveis quando possível;
5. preencha campos ainda inexistentes com listas vazias auditadas;
6. permita diagnóstico de equivalência sem modificar a saída canônica.

---

## 4. Arquivos adicionados

```text
nucleo/pacote_ledger_temporal.py
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
logs/iteracoes/ME-V17-F0-V37K_IMPLEMENTA_PACOTE_LEDGER_TEMPORAL_SHADOW.md
```

---

## 5. Arquivos deliberadamente preservados

Não foram alterados:

```text
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
nucleo/replay_passado_controlado.py
nucleo/dados_operacionais_canonicos.py
aplicacao/principal.py
aplicacao/console/principal.py
dados/
cache/
saidas/
```

---

## 6. Implementação realizada

### 6.1. Novo módulo

Arquivo:

```text
nucleo/pacote_ledger_temporal.py
```

Elementos criados:

```text
PacoteLedgerTemporal
construir_pacote_ledger_temporal_shadow(...)
VERSAO_PACOTE_LEDGER_TEMPORAL_SHADOW
```

O módulo importa `construir_ledger_temporal_conjunto(...)` apenas dentro do adaptador, para evitar acoplamento de importação antecipada.

---

### 6.2. Dataclass `PacoteLedgerTemporal`

Campos implementados:

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

Também foi criado o método:

```text
como_dict(...)
```

---

### 6.3. Adaptador shadow

Função criada:

```text
construir_pacote_ledger_temporal_shadow(
    quadro_futuro,
    mapa_central,
    contexto,
    *,
    modo_shadow=True,
    retorno_legado=None,
) -> PacoteLedgerTemporal
```

Comportamento:

- se `retorno_legado` não for fornecido, executa o ledger atual;
- se `retorno_legado` for fornecido, apenas embrulha o retorno já calculado;
- preserva `eventos` como `eventos_temporais`;
- preserva `fifo_candidatos_avaliados`;
- deriva `pagamentos_futuros_processados` dos eventos;
- deriva `saldos_por_lote` dos eventos;
- extrai alertas/bloqueios estruturais quando houver listas associadas a chaves de alerta/bloqueio;
- preenche campos ainda não materializados com listas vazias auditadas;
- registra auditoria e validação do pacote shadow.

---

## 7. Script diagnóstico

Arquivo:

```text
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

O script:

1. carrega `ContextoBaseline`;
2. obtém `quadro_futuro` por `_quadro_futuro_preferencial(contexto)`;
3. obtém `mapa_central` por `_mapa_pagamentos_central(contexto)`;
4. executa `construir_ledger_temporal_conjunto(...)`;
5. executa `construir_pacote_ledger_temporal_shadow(...)` usando o retorno legado já calculado;
6. compara eventos, candidatos FIFO, `pagamento_id`, status, motivo de bloqueio e saldos/consumos;
7. imprime resumo no console;
8. opcionalmente grava CSVs diagnósticos em `saidas/diagnostico/`.

Comando previsto:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

Para rodar sem gravar CSV:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py --sem-csv
```

---

## 8. Garantias de não alteração de saída

A V3.7K não alterou:

```text
nucleo/saida_canonica.py
nucleo/saida_observavel.py
aplicacao/principal.py
aplicacao/console/principal.py
```

Portanto:

- a saída canônica continua chamando o ledger legado diretamente;
- o adaptador shadow não é usado pela saída canônica;
- nenhuma ponte histórica foi removida;
- nenhum cálculo econômico foi alterado;
- nenhum extrato foi modificado;
- nenhum console/XLSX foi modificado.

---

## 9. Critérios de validação da V3.7K

A V3.7K é aprovada se:

- o novo módulo importa sem erro;
- `PacoteLedgerTemporal` existe;
- `construir_pacote_ledger_temporal_shadow(...)` existe;
- o script diagnóstico existe;
- nenhum arquivo de saída foi alterado;
- nenhum módulo legado foi alterado;
- o adaptador preserva contagem de eventos e FIFO;
- o script identifica divergências sem alterar comportamento.

---

## 10. Critérios de promoção futura

O adaptador shadow ainda não deve ser promovido como entrada obrigatória da saída canônica.

Antes de promoção, será necessário:

```text
rodar auditoria shadow
comparar saída atual vs saída via pacote shadow
confirmar equivalência de extrato passado
confirmar equivalência de extrato futuro
confirmar equivalência de situação atual
confirmar equivalência de console/XLSX
```

---

## 11. Próxima microetapa recomendada

```text
V17-F0-V.3.7L — Audita execução do PacoteLedgerTemporal shadow e equivalência contra ledger legado
```

Tipo:

```text
EXECUTÁVEL / DIAGNÓSTICO / SEM ALTERAÇÃO DE SAÍDA
```

Objetivo:

```text
Executar o script diagnóstico da V3.7K, registrar evidências de equivalência entre retorno legado e PacoteLedgerTemporal shadow e decidir se o pacote pode ser conectado à saída canônica em modo shadow opcional.
```

---

## 12. Conclusão

A V3.7K implementa a primeira peça executável de desacoplamento entre ledger e saída canônica, preservando integralmente o comportamento atual.

O projeto agora possui um envelope shadow para o ledger temporal, mas ele ainda não interfere na saída canônica.
