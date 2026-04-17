# Validação local V60

## Escopo validado

- identidade da baseline atualizada para V60;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 documentado e validado;
- script diagnóstico da F1 e wrapper de compatibilidade executáveis.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`
- `python scripts/inspecionar_contrato_f1.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v60.xlsx`

## Atualização V60

- formalização da nova fase sobre a baseline V59 limpa;
- manutenção da checagem de release como gate obrigatório;
- abertura parcial da F1 por contrato mínimo, sem tocar no motor financeiro.

## Evidências observáveis da V60

- a documentação vigente passa a registrar explicitamente a F1 como frente parcialmente aberta;
- o script diagnóstico da F1 retorna `status: OK` e imprime o contrato mínimo canônico;
- o release checker continua aprovando a baseline sem ruído estrutural;
- os comandos canônicos seguem executando sem regressão funcional.
