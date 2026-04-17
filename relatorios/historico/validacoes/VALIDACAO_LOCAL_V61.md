# Validação local V61

## Escopo validado

- identidade da baseline atualizada para V61;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel`;
- script diagnóstico de `recebido_auditavel` e wrapper de compatibilidade executáveis.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`
- `python scripts/inspecionar_contrato_f1.py`
- `python scripts/inspecionar_recebidos_auditaveis.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v61.xlsx`

## Atualização V61

- manutenção da nova fase sobre a baseline V60 limpa;
- manutenção da checagem de release como gate obrigatório;
- abertura da Etapa 2 da F1 por materialização de `recebido_auditavel`, sem tocar no motor financeiro.

## Evidências observáveis da V61

- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py` retorna `status_validacao: OK` e imprime o quadro materializado de recebidos;
- o release checker continua aprovando a baseline sem ruído estrutural;
- os comandos canônicos seguem executando sem regressão funcional.
