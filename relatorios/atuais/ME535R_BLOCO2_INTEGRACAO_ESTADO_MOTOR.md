# ME-535R — Bloco 2: integração do estado econômico com a fronteira do novo motor

## 1. Objetivo

Esta entrega incorpora a fundação do Bloco 2 ao fluxo principal, constrói o
`EstadoEconomicoCanonico` e materializa uma interface econômica exclusiva para
o futuro motor decisório.

A integração é bloqueante: falha de proveniência, insuficiência CDI, reprovação
do estado econômico ou inconsistência da interface interrompe a execução antes
do motor temporal legado.

## 2. Ordem formal implementada

```text
ContextoOperacionalCanonico
→ EstadoTemporalInicial, apenas como adaptador de construção já existente
→ FundacaoEntradaBloco2
→ EstadoEconomicoCanonico
→ EntradaEconomicaMotorCanonico
→ motor temporal legado preservado nesta etapa
```

O `EstadoTemporalInicial` não é aceito como entrada do novo motor. Ele permanece
apenas como fonte transitória para construir o estado econômico canônico até a
substituição completa da arquitetura anterior.

## 3. Interface exclusiva

`EntradaEconomicaMotorCanonico` aceita exclusivamente:

- `EstadoEconomicoCanonico` aprovado;
- `FundacaoEntradaBloco2` aprovada;
- mesma data de referência nos dois artefatos.

São recusados sem coerção:

- `ContextoOperacionalCanonico`;
- `EstadoTemporalInicial`;
- listas;
- dicionários;
- outros objetos legados.

## 4. Partição econômica transportada

Todas as unidades do estado são particionadas uma única vez em:

1. fontes disponíveis, com saldo líquido positivo;
2. unidades bloqueadas, com saldo atual não disponível;
3. unidades encerradas, obrigatoriamente com saldo zero.

A interface preserva:

- `unidade_id`;
- identidade de origem;
- tipo da unidade;
- estado de ciclo;
- saldo líquido atual;
- produto;
- datas de origem, aplicação e disponibilidade de resgate.

Também registra o hash semântico do estado e o hash semântico do cache JSON.

## 5. Integração no principal

`aplicacao/principal.py` executa a integração imediatamente após construir o
`EstadoTemporalInicial` e antes de chamar
`construir_resultado_motor_temporal_conjunto`.

O artefato de integração ainda não substitui a entrada do motor legado. Nesta
entrega ele funciona como gate e contrato da futura implementação.

## 6. Limites preservados

Esta entrega não:

- gera pacotes econômicos;
- executa `argmax`;
- altera a decisão temporal atual;
- altera o ledger;
- altera o console;
- altera o XLSX;
- corrige o download automático da planilha.

## 7. Testes

Os testes cobrem:

- transporte de fontes disponíveis;
- transporte de unidades bloqueadas;
- transporte de unidades encerradas;
- rejeição de `ContextoOperacionalCanonico`;
- rejeição de `EstadoTemporalInicial`;
- rejeição de listas e dicionários;
- fundação reprovada;
- divergência de data de referência;
- unidade encerrada com saldo;
- ausência de mutação dos objetos de origem;
- ordem da integração antes do motor legado;
- cache versionado e cache localmente modificado.

## 8. Validação local

```bash
python -m unittest -v \
  tests.test_proveniencia_portatil \
  tests.test_suficiencia_temporal_cdi \
  tests.test_estado_economico_canonico \
  tests.test_estado_economico_canonico_fechamento \
  tests.test_fundacao_entrada_bloco2 \
  tests.test_entrada_economica_motor_canonico

python -B scripts/validacao/validar_bloco2_fundacao_entrada.py
python -B scripts/validacao/validar_bloco2_integracao_estado_motor.py
python aplicacao/principal.py

git status --short
```

## 9. Critérios de aprovação

```text
FundacaoEntradaBloco2.ok = true
EstadoEconomicoCanonico.auditoria.ok = true
EntradaEconomicaMotorCanonico.auditoria.ok = true
valor_total_disponivel da interface = valor_total_disponivel_canonico
unidades encerradas com saldo = 0
objetos legados rejeitados
principal mantém ledger, console e XLSX anteriores
```

## 10. Próxima entrega

A próxima alteração poderá implementar a geração de pacotes factíveis consumindo
exclusivamente `EntradaEconomicaMotorCanonico`. A reconstrução de saldos a partir
de contexto, estado temporal ou listas legadas deverá permanecer proibida.
