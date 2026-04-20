# VALIDAÇÃO LOCAL V103

## Validação mínima executada

- `python scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Critérios de aceite desta etapa

- baseline carregando sem alterar o motor principal;
- heurística conjunta parcial restrita ao bloco crítico e sem solver global;
- console exibindo resumo, amostra de trocas preventivas e amostra do planejamento de reservas;
- `Extrato futuro` e aba `Heurística conjunta` gerados com colunas coerentes;
- release checker em `OK`.
