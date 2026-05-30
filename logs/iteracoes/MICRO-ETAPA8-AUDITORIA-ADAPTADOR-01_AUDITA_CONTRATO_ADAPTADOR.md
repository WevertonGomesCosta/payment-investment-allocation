# MICRO-ETAPA8-AUDITORIA-ADAPTADOR-01 — Audita contrato do adaptador contra diagnóstico de consumo console/XLSX

## Identificação

- **Microfrente:** MICRO-ETAPA8-AUDITORIA-ADAPTADOR-01
- **Tipo:** documental / auditoria contratual
- **Baseline de entrada:** `d0618be7bf747624d6eeb49487ca6969598ea599`
- **Branch:** `docs/micro-etapa8-auditoria-adaptador-01`
- **Contrato auditado:** `relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_ADAPTADOR_RENDERIZACAO_EXPORTACAO.md`
- **Diagnóstico-base:** `logs/iteracoes/MICRO-ETAPA8-DIAGNOSTICO-01_MAPEIA_CONSUMO_SAIDA_LEGADA_CONSOLE_XLSX.md`

## Objetivo

Auditar se o contrato complementar do adaptador resolve corretamente a lacuna identificada no diagnóstico de consumo da saída legada por console/XLSX contra `SaidaCanonicaOficial`.

## Resultado

```text
STATUS: APROVAR
```

## Evidência do diagnóstico-base

O diagnóstico `MICRO-ETAPA8-DIAGNOSTICO-01` concluiu que a substituição direta de `saida_canonica` por `SaidaCanonicaOficial` em console/XLSX não é recomendada, pois os consumidores atuais dependem de atributos, métodos e convenções da saída legada operacional.

Também recomendou criar camada adaptadora explícita:

```text
SaidaCanonicaOficial -> PacoteRenderizacaoSaidaCanonica -> console/XLSX
```

## Auditoria da entrada formal

O contrato do adaptador define como entrada formal obrigatória:

```text
SaidaCanonicaOficial
```

E exige:

```text
SaidaCanonicaOficial.preparada=True
SaidaCanonicaOficial.ok=True
```

**Resultado:** aprovado.

## Auditoria da saída prevista

O contrato define como saída prevista:

```text
PacoteRenderizacaoSaidaCanonica
```

Esse pacote é declarado como contratual e ainda não implementado.

**Resultado:** aprovado.

## Auditoria dos campos mínimos para console/XLSX

O contrato mapeia ou exige declaração de indisponibilidade para os blocos centrais exigidos pelo diagnóstico:

- amostras de pagamentos realizados;
- próximos pagamentos;
- valores por fonte;
- alertas operacionais;
- ranking relevante;
- switchings escolhidos;
- lotes ativos/exauridos;
- patrimônio total dos lotes;
- fechamento econômico;
- resumo de recebidos;
- `Extrato Passado`;
- `Extrato Futuro`;
- `Switching`;
- `Situação Atual`;
- `Saida Canonica`;
- `Auditoria Fontes`;
- `Auditoria FIFO`, se preservada.

**Resultado:** aprovado.

## Auditoria da proibição de substituição direta

O contrato declara explicitamente que não autoriza troca direta de `saida_canonica` por `SaidaCanonicaOficial` nos consumidores atuais.

A transição deve ocorrer por adaptador explícito e auditável.

**Resultado:** aprovado.

## Auditoria das restrições negativas

O contrato proíbe:

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

**Resultado:** aprovado.

## Auditoria de ausência de implementação funcional

A PR contratual do adaptador alterou apenas:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_ADAPTADOR_RENDERIZACAO_EXPORTACAO.md
logs/iteracoes/MICRO-ETAPA8-CONTRATO-ADAPTADOR-01_FORMALIZA_CONTRATO_ADAPTADOR_RENDERIZACAO.md
```

Não houve alteração em:

- `aplicacao/*`;
- `nucleo/*` funcional;
- console;
- XLSX;
- motor;
- ledger;
- gates;
- dados;
- saídas operacionais.

**Resultado:** aprovado.

## Ressalvas

Não há ressalvas bloqueantes.

Ressalva operacional futura: a implementação do adaptador deverá decidir como representar campos indisponíveis sem consultar contexto operacional ou reconstruir saída legada.

## Conclusão

O contrato do adaptador está aderente ao diagnóstico de consumo console/XLSX e preserva a separação entre:

```text
SaidaCanonicaOficial
PacoteRenderizacaoSaidaCanonica
console/XLSX
```

A implementação funcional do adaptador pode ser planejada em microfrente posterior, desde que não integre ainda console/XLSX diretamente.

## Próxima microfrente recomendada

```text
MICRO-ETAPA8-ADAPTADOR-FUNCIONAL-01 — Implementa PacoteRenderizacaoSaidaCanonica mínimo sem integrar console/XLSX
```

Escopo recomendado:

- criar módulo formal do adaptador em `nucleo/*`;
- definir `PacoteRenderizacaoSaidaCanonica`;
- consumir somente `SaidaCanonicaOficial`;
- bloquear se `ok=False` ou `preparada=False`;
- mapear campos disponíveis e declarar indisponíveis os não deriváveis;
- não alterar `aplicacao/principal.py`;
- não alterar console/XLSX;
- não gerar saída nova.
