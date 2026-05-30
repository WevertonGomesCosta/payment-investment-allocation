# Contrato macro — Etapa 8 — Saída pós-gates, adaptador, renderização e exportação

## 1. Identificação documental

- **Macrofrente:** MACRO-ETAPA8-SAIDA-01
- **Camada formal consolidada:** saída pós-gates e renderização/exportação
- **Entrada normativa primária:** `SaidaCanonicaOficial`
- **Artefato intermediário previsto:** `PacoteRenderizacaoSaidaCanonica`
- **Consumidores posteriores:** console e XLSX
- **Status:** contrato macro documental, sem alteração funcional nesta macrofrente

## 2. Decisão arquitetural

A Etapa 8 fica congelada como base válida. Sua saída formal é `SaidaCanonicaOficial`, derivada exclusivamente de `LedgerTemporalCanonico` validado e `ResultadoGatesValidacaoNucleo` aprovado.

A transição para console/XLSX não deve ocorrer por substituição direta de `saida_canonica` por `SaidaCanonicaOficial`. A transição deve ocorrer por camada intermediária explícita:

```text
LedgerTemporalCanonico validado
ResultadoGatesValidacaoNucleo aprovado
        -> SaidaCanonicaOficial
        -> PacoteRenderizacaoSaidaCanonica
        -> console/XLSX
```

## 3. Relação com o contrato operacional e modelo oficial

Esta camada é apenas renderização/exportação posterior. Ela não pertence ao motor decisório e não pode alterar o objetivo econômico do projeto.

O contrato operacional mestre e o modelo oficial determinam que as saídas sejam renderizações do ledger do pacote escolhido, não nova otimização, reconciliação ou correção decisória.

## 4. Entrada formal da camada pós-Etapa 8

A entrada formal é:

```text
SaidaCanonicaOficial
```

A entrada deve satisfazer:

```text
SaidaCanonicaOficial.ok=True
SaidaCanonicaOficial.preparada=True
```

Se a saída oficial estiver bloqueada, qualquer renderização/exportação oficial deve ser bloqueada.

## 5. Artefato intermediário previsto

O artefato intermediário previsto é:

```text
PacoteRenderizacaoSaidaCanonica
```

Esse pacote deve ser derivado exclusivamente de `SaidaCanonicaOficial` e deve conter componentes renderizáveis ou indisponibilidades explícitas para campos ainda não deriváveis.

## 6. Consumidores posteriores

Console e XLSX são consumidores posteriores do pacote renderizável. Eles não devem consultar diretamente:

- motor temporal;
- ledger;
- gates;
- contexto operacional como fonte econômica;
- dados brutos;
- planilha;
- logs diagnósticos;
- funções legadas de saída como fonte decisória nova.

## 7. Componentes mínimos do pacote renderizável

O pacote renderizável deve prever, no mínimo:

- `extrato_passado_renderizavel`;
- `extrato_futuro_renderizavel`;
- `switchings_renderizaveis`;
- `situacao_atual_renderizavel`;
- `auditoria_renderizavel`;
- `resumo_recebidos_renderizavel`;
- `fechamento_atual_renderizavel`;
- `ranking_renderizavel`, se houver origem formal válida;
- `metadados_renderizacao`;
- `bloqueios_renderizacao`;
- `avisos_renderizacao`.

Quando um componente não for derivável do schema atual de `SaidaCanonicaOficial`, a indisponibilidade deve ser explícita e auditável. Não é permitido consultar dados brutos para preencher lacunas.

## 8. O que a camada pós-Etapa 8 pode fazer

A camada pode:

- reorganizar conteúdo de `SaidaCanonicaOficial`;
- renomear campos para apresentação;
- construir tabelas renderizáveis em memória;
- declarar indisponibilidade de campos não deriváveis;
- preservar bloqueios, avisos e evidências;
- preparar pacote intermediário para posterior consumo por console/XLSX.

## 9. O que a camada pós-Etapa 8 não pode fazer

A camada não pode:

- reotimizar;
- revalorar;
- escolher fonte;
- trocar pacote vencedor;
- alterar obrigação coberta ou bloqueada;
- alterar switching;
- alterar saldo;
- consultar dados brutos;
- consultar planilha;
- executar motor temporal;
- executar ledger;
- executar gates;
- corrigir decisão econômica em camada de saída;
- substituir diretamente `saida_canonica` por `SaidaCanonicaOficial` em console/XLSX sem adaptador validado.

## 10. Decisão sobre a branch funcional existente

A branch `feat/micro-etapa8-adaptador-funcional-01` deve ser tratada como insumo técnico auditado, não como macroetapa concluída.

Ela pode ser aproveitada como base inicial do adaptador porque:

- consome apenas `SaidaCanonicaOficial`;
- define `PacoteRenderizacaoSaidaCanonica` mínimo;
- bloqueia saída oficial não preparada ou não aprovada;
- não altera runtime, console ou XLSX;
- não gera saída observável.

Ela ainda não resolve a transição de console/XLSX e não deve ser mergeada como solução final da camada pós-Etapa 8 sem macrovalidação posterior.

## 11. Critérios de aceite da macrofrente

A macrofrente é aceita se:

1. congelar a Etapa 8 como base válida;
2. manter `SaidaCanonicaOficial` como saída oficial pós-gates;
3. formalizar `PacoteRenderizacaoSaidaCanonica` como camada intermediária;
4. impedir substituição direta em console/XLSX;
5. preservar motor, ledger e gates;
6. proibir reotimização/revaloração;
7. consolidar decisão explícita sobre a branch funcional do adaptador;
8. não gerar nova saída operacional.

## 12. Condição de parada

Parar qualquer implementação posterior se a transição para renderização/exportação exigir:

- consulta a dados brutos;
- reconstrução da saída legada por contexto operacional;
- alteração de motor;
- alteração de ledger;
- alteração de gates;
- correção econômica em camada de saída;
- alteração de decisões de pagamento, switching, fontes ou saldos.

## 13. Fluxograma macro

```text
Etapa 7 gates aprovados
        |
        v
SaidaCanonicaOficial
        |
        v
PacoteRenderizacaoSaidaCanonica
        |
        +--> console posterior
        |
        +--> XLSX posterior
```

Se `SaidaCanonicaOficial.ok=False` ou `preparada=False`, o fluxo deve parar antes do pacote renderizável.
