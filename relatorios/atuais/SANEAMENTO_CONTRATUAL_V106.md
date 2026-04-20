# Saneamento contratual V106

## Objetivo

A V106 executa um saneamento contratual do repositório para corrigir o drift entre:

- baseline vigente;
- README;
- índice de relatórios;
- contrato operacional;
- e direção metodológica real do projeto.

## Problema corrigido

Até a V105, o repositório já possuía uma linha experimental local do bloco crítico (`V103`–`V105`) suficientemente detalhada para começar a competir com a frente principal do projeto na prática, mesmo sem ter sido formalmente promovida.

Isso criava ambiguidade em três níveis:

1. o objetivo final do projeto ficava menos nítido;
2. melhoras locais podiam ser confundidas com avanço do motor principal;
3. a documentação contratual não acompanhava integralmente a baseline vigente.

## Correções aplicadas

### 1. Separação formal das trilhas
A V106 separa explicitamente:

- **frente central do projeto**;
- **trilha experimental local do bloco crítico**.

### 2. Rebaixamento formal da V105
A V105 passa a ser tratada como **baseline experimental local**, e não como direção principal do repositório.

### 3. Definição da métrica canônica mínima central
A V106 cria o documento `METRICA_CANONICA_MINIMA_CENTRAL.md`, que passa a governar a futura `recomputacao_sequencial_central_v1`.

### 4. Recentragem do objetivo principal
A V106 explicita que o objetivo final do projeto é o motor conjunto e auditável de pagamentos, aportes e switching orientado por resultado econômico terminal, e não a otimização local de uma âncora isolada.

## Efeito prático da V106

A partir da V106:

- a linha local do bloco crítico permanece disponível para auditoria e reaproveitamento;
- a frente central volta a ser o eixo principal de evolução do projeto;
- novas camadas centrais devem ser avaliadas pela métrica canônica mínima central;
- políticas experimentais locais deixam de poder ser promovidas por ganho local isolado.

## Próximo passo esperado

A próxima camada principal do projeto deve ser uma `recomputacao_sequencial_central_v1` guiada pela métrica canônica mínima central e desacoplada da lógica de otimização local da âncora do bloco crítico.
