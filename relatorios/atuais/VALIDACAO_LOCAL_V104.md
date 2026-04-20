# VALIDAÇÃO LOCAL V104

A V104 foi validada localmente com:

- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

Resultados esperados:

- console com nova seção do planejamento conjunto local do bloco crítico;
- `Extrato futuro` e nova aba `Planejamento conjunto` na planilha;
- release checker em `OK`.
