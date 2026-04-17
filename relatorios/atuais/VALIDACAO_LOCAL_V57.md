# Validação local V57

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

- `saidas/operacional/relatorio_operacional_v57.xlsx`


## Atualização V57

- fallback encadeado do CDI para dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente quando o download do BCB falhar.
