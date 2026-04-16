# Baseline fixa V44

## Escopo
A V44 preserva a baseline saneada da V43 e adiciona uma frente funcional situacional/prospectiva mínima, sem abrir solver, switching econômico ou engine completa.

## Ajustes desta versão
- manutenção da base canônica atual em `dados/dados_financeiros.xlsx`;
- inclusão de um painel mínimo de cobertura futura no console;
- enriquecimento da aba `Extrato futuro` da planilha operacional com acumulado, liquidez atual, folga e status;
- atualização da geração operacional corrente para `saidas/relatorio_operacional_v44.xlsx`;
- promoção da V44 como documentação vigente em `relatorios/atuais/`.

## Regra operacional desta versão
A V44 introduz uma leitura conservadora da cobertura futura: as despesas futuras passam a ser confrontadas com a liquidez atual pós-replay, sem consumo sequencial de lotes e sem projeção econômica adicional além da posição já auditada. O objetivo é fornecer um diagnóstico operacional preliminar da suficiência de cobertura, e não uma alocação final otimizada.
