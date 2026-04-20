# BASELINE FIXA V103

A V103 preserva a baseline funcional imediatamente anterior e adiciona uma **heurística conjunta parcial** focada no bloco crítico entre **20/04/2026** e **20/05/2026**. A nova camada continua sem solver global, usa a `decisao_local_v1` com `proxy v3` como base e introduz planejamento de reservas estratégicas por fonte para testar se a primeira grande quebra estrutural pode ser adiada.

## O que a V103 adiciona

- nova camada `heuristica_conjunta_parcial_bloco_critico`;
- planejamento heurístico de reservas por fonte para o bloco crítico;
- trocas preventivas de lote por preservação estratégica;
- comparação da primeira sem cobertura da heurística com a primeira quebra temporal e com a primeira sem cobertura pós-reescolha;
- nova seção dedicada no console principal;
- novas colunas no `Extrato futuro` e nova aba `Heurística conjunta` na planilha operacional.
