# Validação local V114

Validações executadas:

- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado esperado

- contexto carrega normalmente;
- console exibe seção do motor operacional de pagamentos + switching;
- planilha operacional contém aba `Rec. pgto+switch` e colunas de recomendação no `Extrato futuro`;
- release checker em OK.
