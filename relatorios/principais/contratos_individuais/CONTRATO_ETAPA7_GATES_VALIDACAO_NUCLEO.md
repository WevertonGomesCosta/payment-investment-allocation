# Contrato Individual — Etapa 7 — Gates de Validação de Núcleo

## 1. Identificação documental

- **Etapa:** 7
- **Nome:** Gates de Validação de Núcleo
- **Entrada formal obrigatória e exclusiva:** `LedgerTemporalCanonico`
- **Saída formal:** `ResultadoGatesValidacaoNucleo`
- **Módulo funcional:** `nucleo/gates_validacao_nucleo.py`
- **Função pública implementada:** `validar_gates_nucleo(...)`

## 2. Status normativo

Este contrato reflete a implementação final mergeada na PR #426. Ele define a Etapa 7 como camada de validação do núcleo antes de qualquer progressão observável ou preparação de saída posterior.

## 3. Posição na cadeia macro

```text
Etapa 6 -> LedgerTemporalCanonico -> Etapa 7 -> ResultadoGatesValidacaoNucleo -> Etapa 8
```

A referência à Etapa 8 é apenas direcional. Este contrato não implementa a Etapa 8.

## 4. Função da etapa

A Etapa 7 valida o `LedgerTemporalCanonico` produzido pela Etapa 6 por meio de gates formais de núcleo. Ela preserva bloqueios e avisos, registra evidências, calcula prontidão para a próxima etapa e bloqueia progressão observável quando `pronto_para_etapa8=False`.

## 5. Entrada formal obrigatória e exclusiva

A entrada formal obrigatória e exclusiva da Etapa 7 é:

```text
LedgerTemporalCanonico
```

Referências contidas no ledger são apenas evidências internas, metadados, identificadores ou rastreabilidade já materializada. Elas não autorizam busca, reconstrução, importação ou consumo direto de artefatos anteriores.

## 6. Componentes consumíveis da entrada

A Etapa 7 pode consumir somente componentes materializados no `LedgerTemporalCanonico`, incluindo:

- metadados do ledger;
- auditoria do ledger;
- eventos;
- lançamentos por data;
- obrigações cobertas;
- obrigações bloqueadas;
- fontes utilizadas;
- fontes reservadas;
- saldos referenciais;
- switchings escolhidos;
- bloqueios preservados;
- avisos preservados;
- referências originais já embutidas no ledger.

## 7. Saída formal obrigatória

A saída formal obrigatória da Etapa 7 é:

```text
ResultadoGatesValidacaoNucleo
```

## 8. Componentes mínimos da saída

`ResultadoGatesValidacaoNucleo` deve conter, no mínimo:

- `ok`;
- `pronto_para_etapa8`;
- origem formal;
- lista de gates executados;
- bloqueios;
- avisos;
- evidências;
- resumo consolidado;
- metadados.

## 9. Processo interno da etapa

A Etapa 7 deve executar uma orquestração de validação em `validar_gates_nucleo(...)`. Essa orquestração consome exclusivamente `LedgerTemporalCanonico` e aplica gates independentes/transversais sobre coleções já materializadas no ledger.

A ordem documental abaixo descreve a sequência de chamada da função pública, mas não deve ser lida como dependência causal entre todos os gates. Os gates de origem, auditoria, obrigações, fontes, saldos, switchings e dupla contagem validam ramos do mesmo ledger. O `gate_bloqueios_prontidao` é o gate de fechamento e depende do próprio ledger e dos bloqueios/avisos/evidências produzidos pelos gates anteriores.

A Etapa 7 deve:

1. inicializar `ParametrosGatesValidacaoNucleo` quando parâmetros não forem informados;
2. verificar se a entrada formal é `LedgerTemporalCanonico`; se não for, emitir `ResultadoGatesValidacaoNucleo` reprovado sem consultar fontes externas;
3. executar `_gate_origem_exclusiva_ledger(...)` sobre metadados e origem declarada do ledger;
4. executar `_gate_auditoria_ledger(...)` sobre auditoria, bloqueios e avisos preservados no ledger;
5. executar `_gate_obrigacoes_cobertas(...)` sobre obrigações cobertas e fontes materializadas compatíveis;
6. executar `_gate_obrigacoes_bloqueadas(...)` sobre obrigações bloqueadas;
7. executar `_gate_fontes_utilizadas(...)` sobre fontes utilizadas, valores, saldos, liquidez/carência quando materializadas e sobreuso acumulado;
8. executar `_gate_fontes_reservadas(...)` sobre fontes reservadas, valores, saldos, liquidez/carência quando materializadas e sobre-reserva acumulada;
9. executar `_gate_saldos_residuais(...)` sobre saldos referenciais por data e movimentos de fonte;
10. executar `_gate_switchings(...)` sobre switchings escolhidos/materializados;
11. executar `_gate_dupla_contagem(...)` sobre obrigações, fontes e eventos para detectar duplicidades e incompatibilidades evidentes;
12. executar `_gate_bloqueios_prontidao(...)` usando o ledger e os gates anteriores;
13. registrar evidências por `_nova_evidencia(...)`;
14. registrar bloqueios e avisos por `_adicionar_bloqueio(...)` e `_adicionar_aviso(...)`;
15. finalizar gates por `_finalizar_gate(...)` ou `_finalizar_gate_sem_evidencia_minima(...)`;
16. consolidar gates, bloqueios, avisos e evidências;
17. montar `ResumoGatesValidacaoNucleo`;
18. calcular `pronto_para_etapa8` sem consultar fontes externas;
19. emitir `ResultadoGatesValidacaoNucleo`.

## 10. O que a etapa pode fazer

A Etapa 7 pode:

- validar origem exclusiva do ledger;
- validar auditoria do ledger;
- validar obrigações cobertas;
- validar obrigações bloqueadas;
- validar fontes utilizadas;
- validar fontes reservadas;
- validar saldos e residuais;
- validar switchings;
- validar dupla contagem;
- validar bloqueios e prontidão;
- preservar bloqueios e avisos;
- bloquear progressão observável quando `pronto_para_etapa8=False`;
- registrar evidências e metadados do próprio processo de validação.

## 11. O que a etapa não pode fazer

A Etapa 7 não pode:

- alterar o ledger;
- corrigir console;
- gerar XLSX;
- alterar saída canônica;
- renderizar saída observável;
- executar pagamento real;
- executar switching real;
- reotimizar;
- revalorar;
- trocar pacote vencedor;
- consultar `ResultadoMotorTemporalConjunto`;
- consultar `EstadoTemporalInicial`;
- consultar planilha;
- consultar logs ou diagnósticos como fonte de estado;
- criar scripts diagnósticos.

## 12. Relação com a etapa anterior

A Etapa 7 consome exclusivamente `LedgerTemporalCanonico` produzido pela Etapa 6. A Etapa 6 materializa as evidências que a Etapa 7 pode validar; a Etapa 7 não retorna ao motor temporal ou ao estado temporal inicial.

## 13. Relação com a etapa posterior

A Etapa 7 entrega `ResultadoGatesValidacaoNucleo` para orientar a Etapa 8 — Saída Canônica Validada. A progressão observável deve ser bloqueada quando `pronto_para_etapa8=False`. Este contrato não implementa a Etapa 8.

## 14. Schema/funções públicas previstas ou implementadas

Módulo funcional:

```text
nucleo/gates_validacao_nucleo.py
```

Função pública implementada:

```python
validar_gates_nucleo(
    ledger: LedgerTemporalCanonico,
    parametros: ParametrosGatesValidacaoNucleo | None = None,
) -> ResultadoGatesValidacaoNucleo
```

Artefatos formais implementados:

```python
ParametrosGatesValidacaoNucleo
EvidenciaGateNucleo
BloqueioGateNucleo
AvisoGateNucleo
GateValidacaoNucleo
ResumoGatesValidacaoNucleo
ResultadoGatesValidacaoNucleo
```

## 15. Auditoria esperada

A auditoria da Etapa 7 deve registrar:

- gates executados;
- gates aprovados, reprovados e não aplicáveis;
- bloqueios preservados do ledger;
- avisos preservados do ledger;
- bloqueios gerados pelos gates;
- avisos gerados pelos gates;
- contagens de obrigações cobertas e bloqueadas;
- contagens de fontes utilizadas e reservadas;
- contagens de switchings;
- estado final de `pronto_para_etapa8`.

## 16. Critérios de aceite

A Etapa 7 é aceita quando:

1. consome somente `LedgerTemporalCanonico`;
2. produz `ResultadoGatesValidacaoNucleo`;
3. executa os dez gates mínimos;
4. preserva bloqueios e avisos do ledger;
5. bloqueia progressão observável quando `pronto_para_etapa8=False`;
6. não altera ledger;
7. não altera console, XLSX ou saída canônica;
8. não consulta `ResultadoMotorTemporalConjunto`;
9. não consulta `EstadoTemporalInicial`;
10. não consulta planilha, logs ou diagnósticos como fonte de estado.

## 17. Fluxograma operacional-explicativo completo

```mermaid
flowchart TD
    IN["Entrada formal<br/>LedgerTemporalCanonico"] --> ORQ["nucleo/gates_validacao_nucleo.py<br/>validar_gates_nucleo(...)"]

    ORQ --> PARAM["ParametrosGatesValidacaoNucleo<br/>parâmetros padrão quando ausentes"]
    ORQ --> TIPO{"Entrada é LedgerTemporalCanonico?"}

    TIPO -->|não| ENAO["Resultado reprovado<br/>gate_origem_exclusiva_ledger<br/>entrada_nao_ledger_temporal_canonico"]
    ENAO --> OUT_FAIL["Saída formal<br/>ResultadoGatesValidacaoNucleo<br/>ok=False<br/>pronto_para_etapa8=False"]

    TIPO -->|sim| LEDGER["Consumir somente LedgerTemporalCanonico<br/>metadados, auditoria, eventos,<br/>obrigações, fontes, saldos,<br/>switchings, bloqueios e avisos"]
    PARAM --> LEDGER

    LEDGER --> G1["_gate_origem_exclusiva_ledger(...)"]
    LEDGER --> G2["_gate_auditoria_ledger(...)"]
    LEDGER --> G3["_gate_obrigacoes_cobertas(...)"]
    LEDGER --> G4["_gate_obrigacoes_bloqueadas(...)"]
    LEDGER --> G5["_gate_fontes_utilizadas(...)"]
    LEDGER --> G6["_gate_fontes_reservadas(...)"]
    LEDGER --> G7["_gate_saldos_residuais(...)"]
    LEDGER --> G8["_gate_switchings(...)"]
    LEDGER --> G9["_gate_dupla_contagem(...)"]

    G3 --> HREF["Helpers de reconciliação<br/>_fonte_compativel_com_obrigacao(...)<br/>_fonte_compativel_com_grupo(...)<br/>_total_fontes_sem_dupla_soma(...)"]
    G5 --> HLIQ["Helpers de fonte<br/>_validar_liquidez_carencia_materializada(...)<br/>_valor_materializado(...)<br/>_float_ou_none(...)"]
    G6 --> HLIQ
    G7 --> HSAL["Reconciliação de saldos<br/>movimentos de fontes utilizadas/reservadas<br/>saldos_referenciais_por_data"]
    G9 --> HDUP["Regras de dupla contagem<br/>obrigação coberta duplicada<br/>coberta e bloqueada<br/>uso/reserva incompatível<br/>evento duplicado"]

    G1 --> UTIL["Utilitários comuns<br/>_nova_evidencia(...)"]
    G2 --> UTIL
    G3 --> UTIL
    G4 --> UTIL
    G5 --> UTIL
    G6 --> UTIL
    G7 --> UTIL
    G8 --> UTIL
    G9 --> UTIL
    HREF --> UTIL
    HLIQ --> UTIL
    HSAL --> UTIL
    HDUP --> UTIL

    UTIL --> BLOQ["_adicionar_bloqueio(...)"]
    UTIL --> AVISO["_adicionar_aviso(...)"]
    BLOQ --> FING["_finalizar_gate(...)"]
    AVISO --> FING
    UTIL --> FING
    FING --> GATES["Gates 1–9 finalizados<br/>GateValidacaoNucleo[]"]

    GATES --> G10["_gate_bloqueios_prontidao(...)
    <br/>depende do LedgerTemporalCanonico<br/>e dos gates anteriores"]
    LEDGER --> G10
    G10 --> HTERM["_validar_aderencia_terminal_quando_materializada(...)"]
    HTERM --> UTIL10["_nova_evidencia(...)
    <br/>_adicionar_bloqueio(...)
    <br/>_adicionar_aviso(...)"]
    UTIL10 --> FING10["_finalizar_gate(...)"]

    FING10 --> CONS["Consolidar resultado<br/>bloqueios = todos os gates<br/>avisos = todos os gates<br/>evidências = todos os gates"]
    GATES --> CONS

    CONS --> RESUMO["ResumoGatesValidacaoNucleo<br/>contagens de gates, bloqueios,<br/>avisos, obrigações, fontes e switchings"]
    RESUMO --> PRONTO["Calcular pronto_para_etapa8<br/>not bloqueios and auditoria_ledger.ok"]
    PRONTO --> OUT["Saída formal<br/>ResultadoGatesValidacaoNucleo"]

    OUT --> DEC{pronto_para_etapa8?}
    DEC -->|False| BLOCK["aplicacao/principal.py<br/>bloqueia progressão observável<br/>console/XLSX oficiais não gerados"]
    DEC -->|True| E8["Destino<br/>Etapa 8 — Saída Canônica Validada<br/>contrato futuro"]
```

## 18. Condição de parada

A Etapa 7 deve bloquear progressão observável quando houver bloqueios impeditivos, quando a auditoria do ledger reprovar ou quando `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False`.

## 19. Adendos funcionais consolidados

A implementação mergeada consolidou:

- bloqueio de runtime antes de console/XLSX quando os gates reprovam;
- validação de fonte utilizada sem valor referencial;
- reconciliação conservadora de uso e reserva por fonte, data e pacote;
- bloqueio de switching sem data;
- validação de aderência terminal quando evidência estiver materializada;
- reconciliação agregada de obrigações cobertas por pacote/data;
- exigência de saldo residual para fonte movimentada.

Essas regras integram o corpo vivo deste contrato.
