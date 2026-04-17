# Baseline fixa V62

## Objetivo desta versão

Derivar a V61 de forma cirúrgica para abrir a **Etapa 3 da Frente F1**, materializando a segunda estrutura real de caixa/recebidos auditáveis: `fonte_elegivel_pagamento`, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- ampliação de `nucleo/caixa_recebidos_auditaveis.py` para materializar `fonte_elegivel_pagamento` a partir do inventário canônico, da data de referência corrente, dos recebidos auditáveis e do estado mínimo observável do replay;
- inclusão de `fontes_elegiveis_pagamento` em `nucleo/contexto_baseline.py` como camada derivada não invasiva;
- criação do script `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py` e do wrapper `scripts/inspecionar_fontes_elegiveis_pagamento.py`;
- atualização da documentação vigente para registrar a Etapa 3 da F1.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V62. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.

## Critério desta baseline

A V62 preserva a baseline limpa da V61 e abre somente a segunda estrutura real da F1. O objetivo é criar a base estável para que as próximas etapas possam refinar `fonte_elegivel_pagamento`, abrir uma camada robusta de `saldo_disponivel` e, depois, materializar a decisão local v1 entre saldo disponível e resgate.

## Atualização V62

- manutenção da V61 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- materialização executável de `fonte_elegivel_pagamento`;
- preservação do motor financeiro e do fluxo principal.
