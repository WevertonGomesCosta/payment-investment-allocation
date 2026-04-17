# Contrato operacional executável do projeto `payment-investment-allocation`

Este documento define **apenas** as regras e o escopo que já podem ser cobrados da baseline atual.
Ele não deve misturar backlog estratégico, changelog histórico ou metas futuras com o comportamento operacional vigente do repositório.

## 1. Escopo e status da baseline atual

1. A baseline atual é a **V60**.
2. A V60 preserva a linha funcional consolidada até a V59 e abre apenas a **Etapa 1 da Frente F1**, formalizando o contrato mínimo da camada de caixa/recebidos auditáveis sem alterar o motor financeiro.
3. O contrato executável deve descrever somente o que já está implementado ou parcialmente implementado de forma observável na baseline.
4. Regras futuras, metas estratégicas e camadas ainda não abertas ficam fora deste documento e passam a constar em `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`.

## 2. Governança do projeto

5. O repositório-base oficial é `payment-investment-allocation`.
6. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial (`v1`, `v2`, `v3`, ...).
7. O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas do repositório diretamente na raiz.
8. Todo o projeto deve permanecer em português.
9. Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.
10. A checagem de release em `scripts/diagnostico/verificar_release_baseline.py` passa a ser gate obrigatório antes das próximas entregas.
11. O pacote final não deve incluir artefatos temporários como `__pycache__`, `.pyc`, logs brutos auxiliares, caches efêmeros não oficiais ou saídas redundantes de versões antigas.

## 3. Regra metodológica principal de auditoria

12. A divisão física dos módulos dos scripts-base não deve ser tratada como fronteira semântica confiável.
13. A unidade oficial de análise continua sendo a **responsabilidade real da função**, e não o módulo onde ela aparece.
14. Antes de criar, mover, consolidar ou excluir funções, a baseline deve ser auditada por responsabilidade real, comparando equivalências, duplicações e divergências entre os blocos herdados.

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
    - geração da planilha operacional.
38. Essas camadas devem permanecer auditáveis por console, artefatos e relatórios vigentes.

## 8. Saídas executáveis da baseline atual

39. A saída do console deve permanecer organizada, legível e centrada no que está ativo e útil para a etapa corrente.
40. Auditorias já concluídas podem ser resumidas, ocultadas ou retiradas da saída principal, desde que exista caminho documental para reabrir a trilha quando necessário.
41. A planilha operacional vigente deve conter, no mínimo, as abas:
    - `Extrato passado`;
    - `Extrato futuro`;
    - `Melhores produtos`;
    - `Situação atual`.
42. A aba `Situação atual` deve exibir os lotes ainda ativos com colunas auditáveis, incluindo pelo menos recebimento, aplicação, produto, valor original, dias corridos, dias úteis, bruto, líquido e saldo remanescente.
43. A seção de top produtos deve permanecer separada da situação atual dos lotes.

## 9. Itens parcialmente implementados e observáveis na F1

44. A F1 está parcialmente aberta apenas na forma de **contrato mínimo canônico observável**.
45. O contrato mínimo da F1 deve permanecer centralizado em `nucleo/caixa_recebidos_auditaveis.py` e documentado em `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`.
46. Nesta etapa, a F1 deve disponibilizar, no mínimo, as estruturas canônicas:
    - `fonte_elegivel_pagamento`;
    - `recebido_auditavel`;
    - `decisao_local_v1`.
47. A inspeção dessa camada deve ser possível por `scripts/diagnostico/inspecionar_contrato_f1.py`, sem tocar no motor financeiro.
48. A abertura da F1 nesta etapa não implica integração ao fluxo principal, nem decisão econômica real, nem alteração do replay, nem abertura de switching.

## 10. O que continua fora do contrato executável

49. Ainda não fazem parte do contrato executável:
    - switching econômico;
    - decisão conjunta completa de pagamentos + aportes + switching;
    - solver ou busca pesada;
    - recomendação final por cenário integrado;
    - decisão econômica real entre saldo disponível e resgate.
50. Esses itens só podem ser abertos por etapa posterior explicitamente auditada e documentada.

## 11. Hierarquia documental oficial

51. A documentação vigente deve ficar concentrada em `relatorios/atuais/`.
52. Relatórios de versões anteriores devem permanecer preservados em `relatorios/historico/`, organizados por tipo documental.
53. O arquivo `relatorios/INDICE_RELATORIOS.md` deve ser tratado como mapa oficial de navegação documental.
54. O `README.md` deve apontar apenas para os documentos vigentes e para o índice documental.

## 12. Regra de evolução a partir desta revisão contratual

55. Toda nova etapa deve informar claramente se altera:
    - o contrato executável vigente;
    - o backlog contratual futuro;
    - ambos.
56. Alterações futuras no contrato executável devem refletir apenas comportamento já validado na baseline.
57. Metas futuras, ampliações de escopo e camadas ainda não abertas devem ser registradas no backlog contratual e não neste contrato.
58. A montagem da baseline executável deve ser centralizada em `nucleo/contexto_baseline.py` para evitar duplicação de orquestração entre console, planilha operacional e auditorias específicas.
59. A identidade da versão e os nomes-base dos artefatos operacionais devem ser centralizados em `nucleo/identidade_baseline.py`.
60. O console deve permanecer modularizado por seções, com o orquestrador em `aplicacao/console/principal.py` e a renderização distribuída em módulos específicos de seção.
61. Wrappers de compatibilidade antigos podem permanecer, desde que não substituam os caminhos canônicos da baseline.
62. A seção e a aba `Situação atual` devem rotular explicitamente se o fechamento econômico foi confirmado pela série CDI ou estimado por fallback.
63. A checagem mínima automática de release deve permanecer fora do motor financeiro, atuando apenas sobre governança, estrutura e consistência operacional da entrega.
