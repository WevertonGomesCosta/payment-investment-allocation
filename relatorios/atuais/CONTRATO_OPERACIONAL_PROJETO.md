# Contrato operacional executável do projeto `payment-investment-allocation`

Este documento define **apenas** as regras e o escopo que já podem ser cobrados da baseline atual.
Ele não deve misturar backlog estratégico, changelog histórico ou metas futuras com o comportamento operacional vigente do repositório.

## 1. Escopo e status da baseline atual

1. A baseline atual é a **V81**.
2. A V81 preserva integralmente a base funcional da V80 e abre apenas a auditoria fina da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.` entre o `proxy econômico v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal.
3. O contrato executável deve descrever somente o que já está implementado ou parcialmente implementado de forma observável na baseline.
4. Regras futuras, metas estratégicas e camadas ainda não abertas ficam fora deste documento e passam a constar em `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`.

## 2. Governança do projeto

5. O repositório-base oficial é `payment-investment-allocation`.
6. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial (`v1`, `v2`, `v3`, ...).
7. O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas do repositório diretamente na raiz.
8. Todo o projeto deve permanecer em português.
9. Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.
10. A checagem de release em `scripts/diagnostico/verificar_release_baseline.py` é gate obrigatório antes das entregas.
11. O mapa vigente de absorção legado dos Scripts 1 e 2 deve ser consultado antes de qualquer migração de regra de negócio ainda ausente.
12. A camada `switching_economico_shadow` é diagnóstica e auditável; ela não executa switches no fluxo principal nem altera o replay/valuation vigentes.
13. A camada `resolver_hibrido_5p_shadow` é diagnóstica e auditável; ela não substitui a decisão local v1 do fluxo principal nem reabre o `proxy econômico v3` congelado.
14. O pacote final não deve incluir artefatos temporários como `__pycache__`, `.pyc`, logs brutos auxiliares, caches efêmeros não oficiais ou saídas redundantes de versões antigas.

## 3. Regra metodológica principal de auditoria

14. A divisão física dos módulos dos scripts-base não deve ser tratada como fronteira semântica confiável.
15. A unidade oficial de análise continua sendo a **responsabilidade real da função**, e não o módulo onde ela aparece.
16. Antes de criar, mover, consolidar ou excluir funções, a baseline deve ser auditada por responsabilidade real, comparando equivalências, duplicações e divergências entre os blocos herdados.

## 4. Entradas canônicas e contrato de dados

15. O script deve ler somente as três abas primárias: `Carteira`, `Todos os Gastos` e `Inventário de Lotes`.
16. Estruturas auxiliares devem ser derivadas internamente pelo script, e não tratadas como novas entradas primárias.
17. A aba `Carteira` é o universo único de produtos do projeto.
18. A filtragem de candidatos deve ser feita programaticamente no script.
19. O `config` em `dados/config_atualizado.json` é a fonte central e obrigatória de parametrização da baseline.
20. A planilha canônica atual da baseline é `dados/dados_financeiros.xlsx`.
21. O cache CDI vigente da baseline é `dados/cache_bcb.json`.
22. Para os dados operacionais financeiros, a baseline deve primeiro tentar o download da planilha canônica configurada e, se isso não for possível, usar o fallback local em `dados/dados_financeiros.xlsx`.
23. Para o CDI do BCB, a baseline deve primeiro tentar o download online da série necessária e, se isso não for possível, usar o fallback local em `dados/cache_bcb.json`.
24. Quando o download do BCB falhar e o cache local não contiver o próprio dia corrente, a baseline deve usar fallback encadeado com o valor da data útil mais próxima anterior disponível na série, desde que a data corrente seja um dia útil bancário.
25. O fallback encadeado deve poder cobrir dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente.
26. A ausência de download novo não deve interromper a execução quando o fallback local estiver disponível e validado.

## 5. Regras executáveis sobre lotes e temporalidade

27. O projeto deve distinguir, no mínimo, lotes aportados ativos, aportados parcialmente resgatados, lotes exauridos, lotes não aportados disponíveis e lotes não aportados exauridos.
28. A semântica formal do campo `Investimento` em `Inventário de Lotes` permanece:
    - com nome de produto = lote aportado/associado;
    - em branco = lote não aportado disponível somente se a data relevante já ocorreu;
    - em branco com data futura = recebido futuro ainda não disponível;
    - `Investimento = "-"` = lote não aportado já consumido/exaurido.
29. Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas.
30. Na janela de caixa pré-aplicação, o lote já pode ser usado para pagamentos, mas ainda:
    - não rende;
    - não sofre tributação de investimento;
    - não obedece à carência do produto.
31. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.
32. O cálculo de rendimento dos lotes deve considerar explicitamente os resgates realizados para pagamentos, fazendo o saldo remanescente continuar rendendo a partir do valor residual.
33. O cálculo de rendimento continua sendo tratado como hipótese operacional auditável e não como verdade fechada; a auditabilidade corrente deve priorizar evidência interna da baseline e da série CDI carregada, sem manter auditoria comparativa contra app no fluxo executável.

## 6. Regra de referência temporal da baseline

34. A baseline opera com **data de referência corrente** da execução.
35. Quando a série CDI diária não contiver o próprio dia corrente, a baseline pode usar fechamento econômico coerente com o último fator disponível, sem extrapolar indevidamente um novo dia útil já representado pela série.
36. A idade em dias corridos pode continuar referenciada à data corrente, mas o fechamento econômico deve respeitar a última data útil efetivamente observada na série.

## 7. Camadas efetivamente abertas na baseline

37. Estão efetivamente abertas e executáveis na baseline atual:
    - leitura canônica da planilha;
    - carteira canônica;
    - inventário canônico;
    - gastos canônicos;
    - shadow/reconciliação canônica;
    - calendário financeiro e taxas base;
    - cache CDI diário com fallback controlado;
    - núcleo financeiro mínimo;
    - replay controlado do passado;
    - triagem preliminar proxy do motor (`score v1`);
    - geração da planilha operacional;
    - contrato mínimo da F1 e seus diagnósticos.
38. Essas camadas devem permanecer auditáveis por console, artefatos e relatórios vigentes.

## 8. Saídas executáveis da baseline atual

39. A saída do console deve permanecer organizada, legível e centrada no que está ativo e útil para a etapa corrente.
40. Auditorias já concluídas podem ser resumidas, ocultadas ou retiradas da saída principal, desde que exista caminho documental para reabrir a trilha quando necessário.
41. A planilha operacional vigente deve conter, no mínimo, as abas:
    - `Extrato passado`;
    - `Extrato futuro`;
    - `Melhores produtos`;
    - `Situação atual`;
    - `Fechamento econômico atual`.
42. A aba `Situação atual` deve exibir os lotes em dois blocos explícitos: `lotes exauridos` e `lotes ativos`.
43. Cada bloco de lotes da `Situação atual`, no console e na planilha, deve expor duas tabelas: uma de identificação/tempo (`Lote | Recebimento | Aplicação | Produto | Dias corridos | Dias úteis`) e outra de valores atuais (`Lote | Valor original | Bruto | Líquido | Saldo rem`).
44. A seção `Situação atual` do console e da planilha não deve exibir a tabela detalhada de todos os recebidos quando essa camada estiver desativada na baseline corrente.
45. A aba `Fechamento econômico atual` deve permanecer separada da aba `Situação atual`.
46. A seção de top produtos deve permanecer separada da situação atual dos lotes e recebidos.

## 9. Itens parcialmente implementados e observáveis na F1

47. A F1 está parcialmente aberta na forma de **contrato mínimo canônico observável** e de **quatro estruturas reais** derivadas dos dados canônicos.
48. O contrato mínimo da F1 deve permanecer centralizado em `nucleo/caixa_recebidos_auditaveis.py` e documentado em `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`.
49. Nesta etapa, a F1 disponibiliza as estruturas canônicas:
    - `fonte_elegivel_pagamento` (contratual + materializado);
    - `recebido_auditavel` (contratual + materializado);
    - `saldo_disponivel_geral` (contratual + materializado);
    - `decisao_local_v1` (contratual + materializado, com `proxy econômico v3` congelado como baseline vigente).
50. A inspeção dessa camada deve ser possível por:
    - `scripts/diagnostico/inspecionar_contrato_f1.py`;
    - `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`;
    - `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`;
    - `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`;
    - `scripts/diagnostico/inspecionar_decisao_local_v1.py`;
    - `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`.
51. A materialização atual de `recebido_auditavel` deve usar, no mínimo, o inventário canônico, a data de referência corrente e os vínculos históricos explícitos da aba de gastos.
52. A materialização atual de `fonte_elegivel_pagamento` deve usar, no mínimo, o inventário canônico, a data de referência corrente, os pagamentos futuros/pendentes, `recebido_auditavel` e o estado mínimo observável do replay, refinando a leitura por `pagamento_id` e `data_pagamento`.
53. A materialização atual de `saldo_disponivel_geral` deve agregar somente fontes explícitas de caixa já observáveis na F1, preservando a restrição de não duplicidade com as linhas componentes.
54. A materialização atual de `decisao_local_v1` deve permanecer monofonte, auditável e desacoplada do fluxo principal, usando o `proxy econômico v3` como critério vigente até nova evidência concreta.
55. A abertura da F1 nesta etapa não implica integração ao fluxo principal, nem decisão econômica final, nem alteração do replay, nem abertura de switching.

## 10. O que continua fora do contrato executável

56. Ainda não fazem parte do contrato executável:
    - switching econômico;
    - decisão conjunta completa de pagamentos + aportes + switching;
    - solver ou busca pesada;
    - recomendação final por cenário integrado;
    - integração da F1 ao console principal e ao `.xlsx` operacional;
    - decisão multifonte para um mesmo pagamento;
    - projeção financeira das fontes até cada `data_pagamento`.
57. Esses itens só podem ser abertos por etapa posterior explicitamente auditada e documentada.

## 11. Hierarquia documental oficial

58. A documentação vigente deve ficar concentrada em `relatorios/atuais/`.
59. Relatórios de versões anteriores devem permanecer preservados em `relatorios/historico/`, organizados por tipo documental.
60. O arquivo `relatorios/INDICE_RELATORIOS.md` deve ser tratado como mapa oficial de navegação documental.


## 12. Mapeamento legado vigente

91. A baseline V79 mantém e usa um mapa de absorção legado específico para os `Script 1.txt` e `Script 2.txt`.
92. Esse mapa classifica funções e blocos em: `migrar já`, `migrar depois`, `não migrar` e `substituída pela baseline atual`.
93. Nenhuma migração funcional dos Scripts 1 e 2 deve ser feita de forma bruta; a absorção deve seguir esse mapa e ocorrer primeiro em modo shadow/diagnóstico quando a regra ainda estiver ausente.

## 13. Camadas shadow e diagnósticas atualmente abertas

64. A baseline mantém três camadas shadow/distintas: `switching_shadow_reconciliacao`, `switching_economico_shadow` e `resolver_hibrido_5p_shadow`.
65. `switching_shadow_reconciliacao` permanece limitada à reconciliação técnica dos lotes/eventos.
66. `switching_economico_shadow` avalia lotes ativos pós-replay, compara `manter` vs `switch agora e carregar até o horizonte` e produz apenas ranking/plano shadow auditável.
67. `resolver_hibrido_5p_shadow` avalia, por pagamento, um benchmark multifonte de resgate entre lotes elegíveis usando pesos legados de IOF, IR, idade, liquidez, cliff e VPL, sem substituir a decisão local v1 vigente.
68. Nenhuma dessas camadas altera o fluxo principal da baseline atual.


## 14. Auditoria comparativa vigente do benchmark híbrido

94. A baseline V81 mantém uma auditoria comparativa reproduzível entre a `decisao_local_v1` vigente (proxy v3) e o `resolver_hibrido_5p_shadow`.
95. Essa auditoria usa métricas comuns e não compara diretamente scores brutos de escalas diferentes.
96. A baseline V81 também mantém uma auditoria residual específica dos casos de divergência material entre essas duas réguas.
97. O benchmark híbrido permanece diagnóstico; divergência em relação ao proxy v3 não implica substituição automática da decisão vigente.
98. A auditoria residual atual mostra que o benchmark reduz excesso sistematicamente, mas que a maioria das divergências materiais não melhora a métrica comum do `proxy v3`.


## 15. Auditoria cirúrgica vigente dos casos reaproveitáveis

99. A baseline V81 mantém uma auditoria cirúrgica específica apenas sobre os 42 casos já classificados como `potencial_reaproveitamento_proxy_v3`.
100. Essa auditoria não reabre o `proxy v3`; ela apenas organiza transições dominantes, buckets e prioridades cirúrgicas para eventual auditoria fina futura.
101. Enquanto não houver evidência nova, o benchmark híbrido continua shadow e o `proxy v3` permanece a decisão monofonte vigente.


## 16. Auditoria fina vigente da transição dominante

102. A baseline V81 mantém uma auditoria fina específica apenas da transição `Lote 3000 mar. B -> Lote 8500 mar.`.
103. Essa auditoria fina permanece diagnóstica e externa ao fluxo principal; ela não altera o `proxy v3` nem substitui a decisão local vigente.
104. Qualquer ajuste futuro no `proxy v3` só pode ser considerado se essa auditoria fina mostrar padrão estável e localizado em pagamentos pequenos ou médios no horizonte entre 91 e 365 dias.
