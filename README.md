# payment-investment-allocation

Projeto em Python para apoio à decisão financeira envolvendo pagamentos, recebidos, lotes de investimento e switching entre produtos financeiros.

O objetivo do projeto é construir uma simulação diária, auditável e economicamente coerente para apoiar decisões como:

- quais fontes ou lotes usar para pagar contas;
- quando manter uma posição financeira;
- quando avaliar switching entre produtos;
- como preservar rastreabilidade por data, conta, lote, fonte, produto e saldo;
- como gerar saídas operacionais legíveis para conferência humana.

## Documentos oficiais

A interpretação do projeto deve ser baseada exclusivamente nos documentos oficiais abaixo:

- `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md`

Este README é apenas um documento informativo de entrada no repositório. Em caso de divergência, prevalecem o contrato operacional e o modelo matemático-estatístico-financeiro oficiais.

## Ideia central

O projeto deve tratar pagamentos e switchings como partes de uma mesma decisão temporal.

Em termos operacionais, isso significa que:

- pagamentos não devem ser avaliados de forma isolada dos switchings;
- switchings não devem ser avaliados de forma isolada dos pagamentos;
- fontes, lotes, saldos, eventos e saídas devem derivar de uma fonte única de verdade temporal;
- console, planilhas e relatórios devem apenas apresentar resultados da simulação, não reconstruir decisões.

## Entrada operacional

A entrada principal de execução é:

```bash
python aplicacao/principal.py
```

## Dados de entrada

A base financeira principal fica em:

```text
dados/dados_financeiros.xlsx
```

As abas operacionais usadas pelo projeto são:

- `Carteira`
- `Todos os Gastos`
- `Inventário de Lotes`

A configuração principal fica em:

```text
dados/config_atualizado.json
```

## Saídas esperadas

As execuções oficiais podem gerar saídas para auditoria e conferência, incluindo planilhas operacionais e mensagens de console.

As saídas devem permitir verificar, no mínimo:

- pagamentos futuros e passados;
- fonte ou lote usado;
- cobertura integral ou bloqueio;
- saldo antes e saldo depois;
- eventos de switching;
- situação atual dos lotes e fontes;
- coerência entre console e planilha.

## Estrutura geral do repositório

```text
aplicacao/               Entrada de execução e camada de console
nucleo/                  Núcleo de cálculo, simulação e regras financeiras
dados/                   Base financeira e configuração
relatorios/principais/   Contrato operacional e modelo oficial
relatorios/              Relatórios, auditorias e materiais de rastreabilidade
scripts/                 Scripts auxiliares e diagnósticos controlados
saidas/                  Saídas locais geradas pela execução
```

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Execução

```bash
python aplicacao/principal.py
```

## Observação

Este repositório está em desenvolvimento incremental. Alterações funcionais devem preservar a coerência com o contrato operacional e com o modelo matemático-estatístico-financeiro oficiais.
