# Atualização de cache/dados e reexecução da análise — V178

## Escopo
- baseline operacional: V177
- repositório atualizado com o novo `dados/cache_bcb.json` e com a nova `dados/dados_financeiros.xlsx` enviada pelo usuário
- reexecução da validação diária: 2026-04-23 até 2026-05-23
- runner utilizado: `nucleo/runner_validacao_diaria_operacional_v177.py`

## Verificação dos insumos
- cache antigo: `data_final=2026-04-18`, `data_atualizacao=2026-04-18`
- cache novo: `data_final=2026-04-23`, `data_atualizacao=2026-04-23`
- novas datas efetivamente incorporadas ao cache: `2026-04-17`, `2026-04-20`, `2026-04-22`
- workbook enviado: idêntico byte a byte ao workbook já presente na V177

## Resultado global da reexecução
- data_inicio: 2026-04-23
- data_fim: 2026-05-23
- dias_no_horizonte: 31
- dias_com_pagamento: 9
- dias_sem_pagamento: 22
- dias_com_acoes_candidatas_switching: 31
- dias_com_cenarios_promoviveis: 12
- dias_com_switching_executado: 7
- dias_com_normalizacao_pos_vencimento: 2
- pagamentos_no_horizonte: 13
- pagamentos_com_switching_no_fluxo: 0
- inconsistencias_temporais_no_estado: 0
- familias_cenarios_switching_avaliadas: {'individual_integral_parametrizado': 78, 'agrupado_integral_parametrizado': 22}
- classes_cenarios_hibridos_avaliados: {'vencedor_terminal': 75, 'vencedor_operacional': 7, 'vencedor_hibrido_aceitavel': 1, 'dominado_pelo_baseline': 17}

## Auditoria comparativa V177 anterior × V178 reexecutada
- não houve mudança de política no resultado agregado
- os contadores globais permaneceram idênticos entre a V177 anterior e a reexecução com os novos insumos
- a diferença ficou concentrada em valores econômicos marginais dos lotes monitorados e dos cenários de switching, compatível com a atualização do cache CDI/BCB

## Dias críticos auditados

### 2026-04-23
- pacote vencedor: `switch_only`
- switching executado: `True`
- gate: `override_promovivel_sem_pagamento`
- lote 3000 mar. V monitorado: 3074.03
- lote 3000 mar. B monitorado: 3071.85
- melhor cenário promovível: `Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)`
- delta patrimônio proxy vs baseline: 211.64
- leitura: o override em dia sem pagamento continuou metodologicamente ativo e o efeito numérico mudou apenas de forma marginal com o novo cache.

### 2026-05-04
- pacote vencedor: `pay_only`
- switching executado: `False`
- gate: `selecao_pacote`
- lote 3000 mar. V pós-vencimento disponível: 1574.03
- lote 3000 mar. B pós-vencimento disponível: 3071.85
- pagamento Cartão NU componentes reais: [('Lote 3000 mar. V', 1500.0)]
- melhor cenário promovível do dia: `Lote 3000 mar. V + Lote 3000 mar. B -> Mercado Pago Cofrinho 120% CDI (Meli+)`
- delta patrimônio proxy vs baseline: 346.13
- leitura: a auditabilidade pós-vencimento permaneceu correta; o ponto metodológico pendente segue sendo a integração explícita entre `pay_only`, `switch_then_pay` e `pay_then_switch` em dias com pagamento.

### 2026-05-20
- pacote vencedor: `pay_only`
- switching executado: `False`
- melhor cenário promovível: ``
- componentes reais Cartão Azul: [('Lote 7000 mai._ap_2026-05-03', 6867.6), ('Lote 5680 mai._ap_2026-05-07', 332.4)]
- componentes reais Condomínio: [('Lote 3600 mai._ap_2026-05-09', 113.31)]
- leitura: a decisão do dia permaneceu `pay_only`, sem mudança material com a atualização do cache.

## Conclusão da auditoria
- a atualização do cache foi absorvida corretamente e eliminou o risco de trabalhar com CDI/BCB defasado até 2026-04-18
- a planilha enviada não alterou a base operacional porque estava idêntica à planilha já presente no repositório
- a reexecução confirma estabilidade da política da V177 sob os novos insumos
- o gargalo principal não está mais nos dados/cache; permanece na política de decisão em dias com pagamento
- próxima correção metodológica continua sendo integrar explicitamente `pay_only` × `switch_then_pay` × `pay_then_switch` no runner diário antes de expandir o espaço de busca