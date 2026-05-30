# Contrato complementar — Etapa 8 — Adaptador de Renderização/Exportação

## 1. Identificação documental

- **Microfrente:** MICRO-ETAPA8-CONTRATO-ADAPTADOR-01
- **Camada:** Adaptador posterior à `SaidaCanonicaOficial`
- **Entrada formal prevista:** `SaidaCanonicaOficial`
- **Saída formal prevista:** `PacoteRenderizacaoSaidaCanonica`
- **Status:** contrato documental complementar, sem implementação funcional nesta microfrente

## 2. Função da camada adaptadora

A camada adaptadora deve transformar a `SaidaCanonicaOficial` em um pacote de renderização/exportação apto a ser consumido por console e XLSX.

Essa camada não pertence ao motor econômico, não substitui os gates, não altera o ledger e não reabre decisões da Etapa 8. Sua função é exclusivamente preparar estruturas observáveis derivadas da saída oficial.

## 3. Entrada formal obrigatória

A entrada formal obrigatória é:

```text
SaidaCanonicaOficial
```

A entrada deve estar preparada e aprovada:

```text
SaidaCanonicaOficial.preparada=True
SaidaCanonicaOficial.ok=True
```

Se a saída oficial estiver bloqueada, o adaptador deve bloquear a renderização/exportação.

## 4. Saída formal prevista

A saída formal prevista é:

```text
PacoteRenderizacaoSaidaCanonica
```

Esse pacote é contratual e ainda não implementado nesta microfrente.

## 5. Componentes mínimos previstos

`PacoteRenderizacaoSaidaCanonica` deve prever, no mínimo, componentes compatíveis com os consumidores atuais:

- `extrato_passado_renderizavel`;
- `extrato_futuro_renderizavel`;
- `switchings_renderizaveis`;
- `situacao_atual_renderizavel`;
- `auditoria_renderizavel`;
- `resumo_recebidos_renderizavel`;
- `fechamento_atual_renderizavel`;
- `ranking_renderizavel`, se a origem formal estiver disponível;
- `metadados_renderizacao`;
- `bloqueios_renderizacao`;
- `avisos_renderizacao`.

## 6. Campos mínimos para console

A camada deve mapear ou declarar indisponibilidade explícita para:

- amostras de pagamentos realizados;
- próximos pagamentos;
- valores por fonte;
- alertas operacionais;
- ranking relevante;
- switchings escolhidos;
- lotes ativos/exauridos;
- patrimônio total dos lotes;
- fechamento econômico;
- resumo de recebidos.

## 7. Campos mínimos para XLSX

A camada deve mapear ou declarar indisponibilidade explícita para:

- `Extrato Passado`;
- `Extrato Futuro`;
- `Switching`;
- `Situação Atual`;
- `Saida Canonica`;
- `Auditoria Fontes`;
- `Auditoria FIFO`, se contratualmente preservada;
- abas diagnósticas opcionais, se autorizadas por configuração.

## 8. O que a camada pode fazer

A camada adaptadora pode:

- reorganizar dados já presentes em `SaidaCanonicaOficial`;
- derivar tabelas observáveis a partir de snapshots da saída oficial;
- renomear campos para renderização;
- preencher metadados de indisponibilidade quando um campo legado não existir;
- produzir estruturas intermediárias em memória para console/XLSX;
- preservar bloqueios, avisos e evidências.

## 9. O que a camada não pode fazer

A camada adaptadora não pode:

- reotimizar;
- revalorar;
- escolher fonte;
- alterar obrigação coberta ou bloqueada;
- alterar switching;
- alterar saldo;
- consultar dados brutos;
- consultar planilha;
- consultar cache BCB como fonte decisória;
- consultar `ContextoOperacionalCanonico` como fonte econômica;
- reconstruir saída legada a partir de contexto operacional;
- executar motor temporal;
- executar ledger;
- executar gates;
- gerar console diretamente;
- gerar XLSX diretamente.

## 10. Relação com console/XLSX

Console e XLSX devem consumir o `PacoteRenderizacaoSaidaCanonica` somente em microfrente posterior específica.

Este contrato não autoriza troca direta de `saida_canonica` por `SaidaCanonicaOficial` nos consumidores atuais. A transição deve ser feita por adaptador explícito e auditável.

## 11. Critérios de aceite futuro

A futura implementação do adaptador será aceita somente se:

1. consumir exclusivamente `SaidaCanonicaOficial`;
2. bloquear quando `SaidaCanonicaOficial.ok=False` ou `preparada=False`;
3. produzir `PacoteRenderizacaoSaidaCanonica`;
4. mapear campos mínimos de console/XLSX ou declarar indisponibilidade;
5. não consultar dados brutos, planilha, contexto operacional como fonte econômica ou funções legadas de saída;
6. não gerar console ou XLSX;
7. não alterar decisão econômica.

## 12. Condição de parada

A camada deve parar se:

- a entrada não for `SaidaCanonicaOficial`;
- a saída oficial estiver bloqueada;
- algum campo requerido exigir consulta externa ou reprocessamento econômico;
- a adaptação exigir alteração de ledger, gates, motor ou decisão econômica.

## 13. Próxima microfrente recomendada

Após aprovação deste contrato documental:

```text
MICRO-ETAPA8-AUDITORIA-ADAPTADOR-01 — Audita contrato do adaptador contra diagnóstico de consumo console/XLSX
```

A implementação funcional do adaptador deve ocorrer somente depois dessa auditoria documental.
