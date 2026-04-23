# VALIDAÇÃO LOCAL V137

Comandos executados localmente nesta entrega:

- `python -m py_compile nucleo/alocador_pagamentos_terminal_v1.py`
- `python -m py_compile scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py`
- `python scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

Critério de aceite desta etapa:
- o alocador deve gerar candidatos reais para as quatro famílias principais de fonte;
- o cenário com switching elegível só pode entrar quando já vier promovível pelo comparador híbrido;
- o release checker deve fechar em OK para a baseline V137.
