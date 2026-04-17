# Contrato operacional executável do projeto `payment-investment-allocation`

Este documento define **apenas** as regras e o escopo que já podem ser cobrados da baseline atual.
Ele não deve misturar backlog estratégico, changelog histórico ou metas futuras com o comportamento operacional vigente do repositório.

## 1. Escopo e status da baseline atual

1. A baseline atual é a **V55**.
2. A V55 preserva a linha funcional consolidada e incorpora a regra operacional de aquisição de dados com tentativa de download primeiro e fallback controlado depois, sem abertura de solver, switching econômico, score econômico final ou engine conjunta completa.
3. O contrato executável deve descrever somente o que já está implementado ou parcialmente implementado de forma observável na baseline.
4. Regras futuras, metas estratégicas e camadas ainda não abertas ficam fora deste documento e passam a constar em `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`.

## 2. Governança do projeto

5. O repositório-base oficial é `payment-investment-allocation`.
6. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial (`v1`, `v2`, `v3`, ...).
7. O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas do repositório diretamente na raiz.
8. Todo o projeto deve permanecer em português.
9. Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.
10. O pacote final não deve incluir artefatos temporários como `__pycache__`, `.pyc`, logs brutos auxiliares, caches efêmeros não oficiais ou saídas redundantes de versões antigas.

## 3. Regra metodológica principal de auditoria

11. A divisão física dos módulos dos scripts-base não deve ser tratada como fronteira semântica confiável.
12. A unidade oficial de análise continua sendo a **responsabilidade real da função**, e não o módulo onde ela aparece.
13. Antes de criar, mover, consolidar ou excluir funções, a baseline deve ser auditada por responsabilidade real, comparando equivalências, duplicações e divergências entre os blocos herdados.

## 4. Entradas canônicas e contrato de dados

14. O script deve ler somente as três abas primárias: `Carteira`, `Todos os Gastos` e `Inventário de Lotes`.
15. Estruturas auxiliares devem ser derivadas internamente pelo script, e não tratadas como novas entradas primárias.
16. A aba `Carteira` é o universo único de produtos do projeto.
17. A filtragem de candidatos deve ser feita programaticamente no script.
18. O `config` em `dados/config_atualizado.json` é a fonte central e obrigatória de parametrização da baseline.
19. A planilha canônica atual da baseline é `dados/dados_financeiros.xlsx`.
20. O cache CDI vigente da baseline é `dados/cache_bcb.json`.
21. Para os dados operacionais financeiros, a baseline deve primeiro tentar o download da planilha canônica configurada e, se isso não for possível, usar o fallback local em `dados/dados_financeiros.xlsx`.
22. Para o CDI do BCB, a baseline deve primeiro tentar o download online da série necessária e, se isso não for possível, usar o fallback local em `dados/cache_bcb.json`.
23. Quando o download do BCB falhar e o cache local não contiver o próprio dia corrente, a baseline deve usar o valor da data útil mais próxima anterior disponível na série, desde que a data corrente seja um dia útil bancário.
24. A ausência de download novo não deve interromper a execução quando o fallback local estiver disponível e validado.

## 5. Regras executáveis sobre lotes e temporalidade

25. O projeto deve distinguir, no mínimo, lotes aportados ativos, aportados parcialmente resgatados, lotes exauridos, lotes não aportados disponíveis e lotes não aportados exauridos.
26. A semântica formal do campo `Investimento` em `Inventário de Lotes` permanece:
    - com nome de produto = lote aportado/associado;
    - em branco = lote não aportado disponível somente se a data relevante já ocorreu;
    - em branco com data futura = recebido futuro ainda não disponível;
    - `Investimento = "-"` = lote não aportado já consumido/exaurido.
27. Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas.
28. Na janela de caixa pré-aplicação, o lote já pode ser usado para pagamentos, mas ainda:
    - não rende;
    - não sofre tributação de investimento;
    - não obedece à carência do produto.
29. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.
30. O cálculo de rendimento dos lotes deve considerar explicitamente os resgates realizados para pagamentos, fazendo o saldo remanescente continuar rendendo a partir do valor residual.
31. O cálculo de rendimento continua sendo tratado como hipótese operacional auditável e não como verdade fechada; portanto, diferenças relevantes com apps devem continuar podendo abrir auditoria específica.

## 6. Regra de referência temporal da baseline

32. A baseline opera com **data de referência corrente** da execução.
33. Quando a série CDI diária não contiver o próprio dia corrente, a baseline pode usar fechamento econômico coerente com o último fator disponível, sem extrapolar indevidamente um novo dia útil já representado pela série.
34. A idade em dias corridos pode continuar referenciada à data corrente, mas o fechamento econômico deve respeitar a última data útil efetivamente observada na série.

## 7. Camadas efetivamente abertas na baseline

35. Estão efetivamente abertas e executáveis na baseline atual:
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
36. Essas camadas devem permanecer auditáveis por console, artefatos e relatórios vigentes.

## 8. Saídas executáveis da baseline atual

37. A saída do console deve permanecer organizada, legível e centrada no que está ativo e útil para a etapa corrente.
38. Auditorias já concluídas podem ser resumidas, ocultadas ou retiradas da saída principal, desde que exista caminho documental para reabrir a trilha quando necessário.
39. A planilha operacional vigente deve conter, no mínimo, as abas:
    - `Extrato passado`;
    - `Extrato futuro`;
    - `Melhores produtos`;
    - `Situação atual`.
40. A aba `Situação atual` deve exibir os lotes ainda ativos com colunas auditáveis, incluindo pelo menos recebimento, aplicação, produto, valor original, dias corridos, dias úteis, bruto, líquido e saldo remanescente.
41. A seção de top produtos deve permanecer separada da situação atual dos lotes.

## 9. Itens parcialmente implementados, mas já reconhecidos pela baseline

42. A triagem do motor por `score v1` é apenas uma camada preliminar proxy e não deve ser tratada como decisão econômica final.
43. O replay controlado do passado já reconcilia pagamentos históricos com lotes informados, mas ainda não representa a engine conjunta completa do projeto.
44. A utilização de recebidos futuros e de saldo disponível em decisões econômicas completas continua apenas parcialmente representada pela baseline atual.

## 10. Itens explicitamente fora do escopo atual da baseline

45. Não fazem parte do escopo executável atual:
    - solver;
    - switching econômico aberto;
    - score econômico final;
    - recomendação final por cenário integrado;
    - engine conjunta completa de pagamentos + aportes + switching.
46. Esses itens só podem ser abertos por etapa posterior explicitamente auditada e documentada.

## 11. Hierarquia documental oficial

47. A documentação vigente deve ficar concentrada em `relatorios/atuais/`.
48. Relatórios de versões anteriores devem permanecer preservados em `relatorios/historico/`, organizados por tipo documental.
49. O arquivo `relatorios/INDICE_RELATORIOS.md` deve ser tratado como mapa oficial de navegação documental.
50. O `README.md` deve apontar apenas para os documentos vigentes e para o índice documental.

## 12. Regra de evolução a partir desta revisão contratual

51. Toda nova etapa deve informar claramente se altera:
    - o contrato executável vigente;
    - o backlog contratual futuro;
    - ambos.
52. Alterações futuras no contrato executável devem refletir apenas comportamento já validado na baseline.
53. Metas futuras, ampliações de escopo e camadas ainda não abertas devem ser registradas no backlog contratual e não neste contrato.
