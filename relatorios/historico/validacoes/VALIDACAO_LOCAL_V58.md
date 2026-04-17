# Validação local V58

## Escopo validado

- contexto canônico da baseline centralizado em `nucleo/contexto_baseline.py`;
- console modularizado por seções;
- identidade de versão e nomes de artefatos centralizados;
- wrappers antigos preservados.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v58.xlsx`


## Atualização V58

- fallback encadeado do CDI para dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente quando o download do BCB falhar.

- remoção do ramo de auditoria contra app do fluxo executável da baseline;
- remoção do teste de `-1 dia` do fluxo principal;
- rotulagem auditável do fallback CDI na situação atual do console e do `.xlsx`.

## Evidências observáveis da V58

- o console principal exibe, na seção `Situação atual`, o status do fechamento econômico, a fonte usada, a quantidade de fechamentos com fallback CDI, a última data explícita da série e a data confirmada da série;
- a aba `Situação atual` do `.xlsx` começa com um bloco de cabeçalho auditável do fechamento econômico antes das tabelas de identificação/tempo e valores;
- o ramo de auditoria contra app e o teste de `-1 dia` deixam de participar do fluxo executável principal e saem da configuração ativa.
