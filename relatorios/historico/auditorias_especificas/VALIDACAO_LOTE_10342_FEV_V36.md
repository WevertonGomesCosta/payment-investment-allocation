# VALIDAÇÃO DO LOTE 10342 FEV. — V36

## Contexto

O usuário informou duas discrepâncias principais para o `Lote 10342 fev.`:

1. o resgate agregado de `12/02/2026`, correspondente à soma de `Aluguel` + `IPVA`;
2. o resgate de `13/03/2026`, correspondente à conta `Escola`.

Além disso, a nova planilha corrigiu:

- `IPVA` de `12/02/2026` em `-R$ 0,02`;
- `Internet` de `16/02/2026` em `-R$ 1,00`.

## Correções relevantes desta versão

1. a nova planilha substituiu a base anterior;
2. a tabela do IOF passou a ser indexada corretamente por dia de vida (`dias - 1`);
3. a leitura de `NaT` no inventário foi robustecida para a nova base.

## Comparação contra o app

### 12/02/2026 — Aluguel + IPVA (resgate agregado no app)

#### App
- líquido: `R$ 2.389,58`
- bruto: `R$ 2.396,54`
- IR: `R$ 0,46`
- IOF: `R$ 6,50`
- imposto total: `R$ 6,96`

#### Modelo V36 (somando os dois eventos do mesmo dia)
- líquido: `R$ 2.389,58`
- bruto: `R$ 2.396,56`
- imposto total: `R$ 6,98`

#### Delta V36 vs. app
- líquido: `R$ 0,00`
- bruto: `+R$ 0,02`
- imposto total: `+R$ 0,02`

#### Leitura
Esse bloco ficou materialmente aderente ao app. A diferença remanescente de `R$ 0,02` é compatível com arredondamento centesimal, especialmente porque o app consolida a movimentação do dia em um único comprovante, enquanto o replay mantém dois eventos históricos distintos.

### 13/03/2026 — Escola

#### App
- líquido: `R$ 1.368,12`
- bruto: `R$ 1.373,20`
- IR: `R$ 5,08`

#### Modelo V36
- líquido: `R$ 1.368,13`
- bruto: `R$ 1.373,22`
- imposto: `R$ 5,09`

#### Delta V36 vs. app
- líquido: `+R$ 0,01`
- bruto: `+R$ 0,02`
- imposto: `+R$ 0,01`

#### Leitura
A discrepância remanescente caiu para a faixa centesimal. Não há mais evidência de resíduo material de convenção ou de cálculo para este evento.

## Trilha por evento do lote na V36

| Data | Conta | Despesa ID | Valor conta | Saldo antes | Bruto | Imposto | Líquido | Saldo remanescente |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-02-09 | Cartão Azul | despesa_auto_00009 | 6014,06 | 10356,83 | 6021,75 | 7,69 | 6014,06 | 4335,08 |
| 2026-02-12 | Aluguel | despesa_auto_00010 | 981,95 | 4344,41 | 984,82 | 2,87 | 981,95 | 3359,59 |
| 2026-02-12 | IPVA | despesa_auto_00011 | 1407,63 | 3359,59 | 1411,74 | 4,11 | 1407,63 | 1947,85 |
| 2026-02-16 | Internet | despesa_auto_00012 | 131,40 | 1949,25 | 131,80 | 0,40 | 131,40 | 1817,45 |
| 2026-02-19 | Material | despesa_auto_00013 | 460,00 | 1820,05 | 461,68 | 1,68 | 460,00 | 1358,37 |
| 2026-03-13 | Escola | despesa_auto_00014 | 1368,12 | 1373,22 | 1373,22 | 5,09 | 1368,13 | 0,00 |

## Conclusão

Para o `Lote 10342 fev.` na V36:

- o resíduo material foi eliminado;
- os dois pontos antes discrepantes ficaram em faixa centesimal;
- o lote deve ser considerado **resolvido por arredondamento/limiar**, sem necessidade de nova microcorreção de lógica nesta etapa.
