# AUDITORIA_REPOSITORIO_V142

- Baseline auditada: `V141`.
- Escopo: organização do repositório, integridade do alocador terminal, viabilidade da expansão comparativa do fluxo de pagamentos e validação local mínima da nova camada V142.

## Achados principais

- A arquitetura da V141 está coerente com a reorganização documental recente: contratos, diagnósticos, wrappers de scripts e núcleo temporal permanecem separados de forma legível e auditável.
- O `alocador_pagamentos_terminal_v1` já estava funcional na V141, mas a validação operacional vigente ainda estava concentrada no recorte curto V138 e em cenários sintéticos/diagnósticos.
- O principal gargalo encontrado não foi erro estrutural do alocador, mas custo computacional da comparação expandida quando a auditoria ampla é executada com busca de switching muito larga; por isso a V142 comparativa usa teto controlado de candidatos por data apenas nesta camada de inspeção.
- Foi adicionada uma chave explícita para desabilitar H1–H3 (`desabilitar_modelos_script1_fase1`) em modo comparativo, permitindo auditoria controlada sem reabrir o contrato principal da V141.

## Validação local executada

- `python -m py_compile nucleo/alocador_pagamentos_terminal_v1.py`
- `python -m py_compile nucleo/fluxo_pagamentos_terminal_recorte_amplo_v142.py`
- execução real do fluxo ativo em 20 pagamentos futuros
- execução real do fluxo neutralizado em 20 pagamentos futuros
- comparação por pagamento entre as trajetórias ativa e neutralizada

## Riscos remanescentes

- A camada V142 ainda é comparativa/auditiva; ela não substitui o fluxo central principal.
- O teto de candidatos de switching por data foi reduzido apenas para manter a auditoria comparativa em recorte maior dentro de custo computacional controlado.
- Comparações ainda maiores (por exemplo, 30+ pagamentos com busca mais larga) exigirão nova calibração de custo de busca antes de promoção.

## Conclusão

- Não foi encontrado bloqueio contratual no núcleo que impeça a expansão.
- A V142 adiciona justamente a lacuna operacional identificada na auditoria: comparação real mais ampla entre fluxo com H1–H3 ativas versus neutralizadas, preservando o foco em patrimônio líquido terminal proxy.
