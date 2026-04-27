# INTEGRAÇÃO FUNCIONAL DE APORTES FUTUROS — V216

## 1. Status

`V216_INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_NO_MOTOR`

A V216 usa a V208 como baseline funcional real e usa os artefatos V209–V215 apenas como especificação. Diferentemente da reconstrução V209–V215, esta versão altera módulos centrais do motor para que os aportes planejados possam ser criados e consumidos durante a simulação temporal.

## 2. Escopo implementado

A V216 implementa:

1. remoção prática dos stubs V209–V215 como fonte funcional;
2. módulo funcional `nucleo/aportes_futuros_planejados.py`;
3. transição controlada `recebido_futuro → caixa/reserva → aporte_planejado`;
4. integração do invariante V212 ao estado temporal;
5. bloqueio real de dupla contagem por `recebido_id_origem`;
6. auditoria de liquidez e carência do produto destino;
7. comparação operacional com/sem aporte planejado;
8. criação de lotes planejados apenas após validação;
9. consumo dos lotes planejados pelo alocador como `lote_aportado`.

## 3. Regra de precedência intradiária

A materialização do aporte planejado ocorre **depois** dos pagamentos do próprio dia.

Ordem no simulador:

```text
ativar recebidos futuros do dia
aplicar switching elegível do dia
processar pagamentos do dia
consumir componentes usados nos pagamentos
materializar aporte planejado apenas com o excedente remanescente
```

Essa ordem evita transformar em investimento um valor que deveria primeiro cobrir pagamentos do mesmo dia.

## 4. Invariante operacional

A cada recebido materializado, o motor valida:

```text
valor_recebido = valor_pago_com_recebido + valor_aportado + saldo_caixa_remanescente
```

Campos gravados na auditoria:

- `valor_recebido`;
- `valor_pago_com_recebido`;
- `valor_aportado`;
- `saldo_caixa_remanescente`;
- `diferenca_invariante`;
- `invariante_v216_valida`.

## 5. Bloqueio de dupla contagem

A V216 impede que o mesmo recebido seja tratado simultaneamente como caixa integral e como lote planejado.

Mecanismo:

- cada lote planejado recebe `recebido_id_origem`;
- o recebido original tem o valor aportado debitado de `valor_disponivel`;
- o recebido recebe `aporte_planejado_materializado_v216 = True`;
- se houver nova tentativa para o mesmo recebido, o status passa a `BLOQUEADO_DUPLA_CONTAGEM_V216`.

## 6. Auditoria de liquidez e carência

O produto destino é aceito apenas se:

- respeitar aplicação mínima;
- respeitar aplicação máxima, quando informada;
- não for produto somente combo, exceto se autorizado em config;
- tiver liquidez dentro do limite V216;
- tiver carência dentro do limite V216.

O lote planejado recebe:

- `liquidez_dias_atual`;
- `carencia_dias_atual`;
- `liquidez_ate`;
- `carencia_ate`.

O alocador passou a respeitar também `liquidez_ate`, além de `carencia_ate`.

## 7. Comparação com/sem aporte

Antes da promoção, a V216 calcula:

- `valor_terminal_sem_aporte`;
- `valor_terminal_com_aporte`;
- `ganho_liquido_estimado`.

Se o ganho não for positivo e a política exigir ganho positivo, o status passa a:

```text
BLOQUEADO_COMPARACAO_SEM_APORTE_V216
```

## 8. Módulos alterados

- `nucleo/aportes_futuros_planejados.py` — novo módulo funcional.
- `nucleo/simulador_central_eventos_v1.py` — integração temporal e auditoria.
- `nucleo/alocador_pagamentos_terminal_v1.py` — consumo de lotes planejados e bloqueio por liquidez.
- `nucleo/builders/simulador_central_estado_v117.py` — inicialização dos campos de invariante.
- `scripts/diagnostico/inspecionar_aportes_planejados_v216.py` — diagnóstico específico.
- `scripts/diagnostico/verificar_release_baseline.py` — validações V216.
- `nucleo/identidade_baseline.py` — versão V216.
- `README.md` e `relatorios/INDICE_RELATORIOS.md`.

## 9. Status de baseline

A V216 é uma **versão funcional candidata**, mas não deve ser promovida automaticamente para baseline estável sem validação operacional em uso real.

Critérios mínimos para promoção futura:

- release checker sem erros;
- ausência de `__pycache__` e `.pyc`;
- diagnóstico V216 executando;
- evidência de lotes planejados consumidos pelos pagamentos futuros quando houver cenário compatível;
- comparação observável contra cenário sem aporte.
