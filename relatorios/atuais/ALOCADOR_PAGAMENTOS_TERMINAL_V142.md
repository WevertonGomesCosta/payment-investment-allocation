# Alocador pagamentos terminal — V142

A V142 mantém a Fase 1 de absorção dos modelos do Script 1 e amplia a validação para um **recorte real maior de pagamentos**, comparando duas execuções:

- sem H1–H3
- com H1–H3

Objetivo:
- medir onde `score_hibrido_5p_fonte`, `penalidade_cliff_idade` e `oportunidade_vpl_marginal` alteram a escolha entre:
  - `lote_aportado`
  - `lote_nao_aportado`
  - `combinacao_minima_fontes`
  - `cenario_switching_elegivel`

A lógica principal do comparador terminal permanece a mesma. A Fase 1 atua como:
- score auxiliar;
- desempate econômico;
- reordenação fina da combinação mínima.
