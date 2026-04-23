# Estrutura do repositório — V141

A V141 mantém a reorganização da V139/V140 e adiciona a implementação funcional da Fase 1 em:
- `nucleo/pagamentos/modelos_script1/heuristicas_fase1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py`

Objetivo estrutural:
- permitir que o `alocador_pagamentos_terminal_v1` use H1–H3 sem acoplamento monolítico ao Script 1 legado;
- manter o switching subordinado ao comparador híbrido;
- preparar a próxima integração em recorte real ampliado.
