# payment-investment-allocation

**Pacote operacional atual:** V216  
**Baseline funcional real de origem:** V208  
**Artefatos V209–V215:** usados apenas como especificação metodológica, não como baseline funcional  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V216 deriva diretamente da V208 e implementa de forma funcional, no motor temporal, a frente de recebidos/aportes futuros que havia ficado apenas documentada entre V209 e V215.

## Objetivo final do projeto

Construir um motor conjunto, auditável e economicamente coerente para:

- pagamentos;
- recebidos;
- aportes planejados;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V216 implementa

- cria `nucleo/aportes_futuros_planejados.py` como módulo funcional, não stub;
- integra a transição `recebido_futuro → caixa/reserva → aporte_planejado` ao simulador central;
- materializa aportes planejados somente após os pagamentos do próprio dia;
- valida o invariante:

```text
valor_recebido = valor_pago_com_recebido + valor_aportado + saldo_caixa_remanescente
```

- bloqueia dupla contagem por `recebido_id_origem`;
- audita liquidez e carência do produto destino;
- compara o cenário com aporte contra o cenário sem aporte;
- cria lotes planejados como `lote_aportado` somente quando todos os critérios passam;
- torna os lotes planejados consumíveis pelos módulos centrais de pagamento;
- atualiza o release checker para V216 e bloqueia `__pycache__`/`.pyc`.

## Evidência de integração funcional

Os pontos centrais de consumo são:

- `nucleo/simulador_central_eventos_v1.py`
  - chama `materializar_aportes_planejados_v216(...)` após os pagamentos do dia;
  - grava `auditoria_aportes_planejados_v216`;
  - adiciona lotes planejados em `estado['lotes_aportados']`.

- `nucleo/alocador_pagamentos_terminal_v1.py`
  - consome lotes planejados como `lote_aportado`;
  - respeita `carencia_ate` e `liquidez_ate`;
  - preserva metadados `origem_aporte_planejado_v216` e `recebido_id_origem_v216`.

- `nucleo/builders/simulador_central_estado_v117.py`
  - inicializa os recebidos com campos de invariante V216.

## Documentos operacionais prioritários

Consulte primeiro:

- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_V216.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

## Caminho operacional vigente

Para gerar a saída operacional:

```bash
python scripts/operacional/gerar_planilha_operacional.py
```

Para auditar a release:

```bash
python scripts/diagnostico/verificar_release_baseline.py
```

Para auditar especificamente a V216:

```bash
python scripts/diagnostico/inspecionar_aportes_planejados_v216.py
```
