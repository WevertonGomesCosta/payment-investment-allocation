# ME-V17-F0-V0 — Mapa da arquitetura operacional canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V0
- VERSAO_CANDIDATA: V17-F0-V.0
- TIPO: DOCUMENTAL / ARQUITETURAL
- CLASSE: FORMALIZA_FLUXOGRAMA_MACRO_PIPELINE_OPERACIONAL
- STATUS: CONCLUÍDA
- BRANCH: main
- BASELINE_DE_ENTRADA: main pós-U.7, pós-README V.0 e pós-atualização de dados
- BASELINE_DE_SAÍDA: main após alinhamento da seção 7-E do contrato operacional
- ESCOPO: README.md e relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md
- ALTERA_CODIGO: não
- ALTERA_MOTOR: não
- ALTERA_MODELO_OFICIAL: não
- ALTERA_REGRA_ECONOMICA: não
- ALTERA_DADOS: não nesta microetapa documental
- ALTERA_RENDERIZACAO: não

---

## 2. Objetivo

Formalizar o fluxograma macro do pipeline operacional do projeto `payment-investment-allocation`, alinhando a leitura arquitetural do README e da seção 7-E do contrato operacional mestre.

A microetapa consolida a arquitetura macro em camadas, sem abrir subetapas internas no fluxograma principal, preservando o detalhamento individual para auditorias posteriores de cada camada.

---

## 3. Decisões formalizadas

### 3.1. Fluxograma macro limpo

O fluxograma macro passa a conter apenas etapas principais, sem detalhar subetapas internas de dados canônicos, motor, ledger, gates ou renderização.

A estrutura oficial documentada é:

1. Entrada bruta e configuração.
2. Validação pré-execução.
3. Dados operacionais e universo econômico canônico.
4. Estado temporal inicial.
5. Motor temporal conjunto.
6. Ledger canônico do pacote escolhido.
7. Gates de validação de núcleo.
8. Saída canônica validada.
9. Renderização oficial unificada.
10. Validação de paridade da renderização.
11. Limpeza e depreciação controlada, com retorno à etapa 1.

---

### 3.2. Dados operacionais e universo econômico canônico

A etapa 3 passa a concentrar a preparação canônica dos dados operacionais e do universo econômico.

Essa etapa deve produzir, quando aplicável:

- pagamentos canônicos;
- recebidos ou salários canônicos;
- switchings canônicos;
- produtos canônicos;
- ranking da Carteira;
- universo de produtos elegíveis;
- inventário completo de lotes.

O inventário completo de lotes deve ser construído a partir da combinação entre:

- aba `Inventário de Lotes`;
- aba `Switching`;
- lotes destino derivados ou materializáveis por switching;
- reconciliação entre lotes destino já existentes e lotes derivados de switching;
- prevenção de dupla contagem.

---

### 3.3. Ranking e motor

O ranking da `Carteira` pertence ao universo econômico canônico.

A etapa de estado temporal inicial não depende diretamente do ranking para existir.

A dependência direta do ranking ocorre principalmente no motor temporal conjunto, especialmente para recomendações e avaliação de switchings.

---

### 3.4. Pagamentos e switchings

Pagamentos e switchings devem ser tratados como decisões dependentes dentro do motor temporal conjunto.

É vedado calcular pagamentos e switchings em trilhas independentes e reconciliá-los posteriormente em console, planilha, relatório ou CSV diagnóstico.

A dependência entre pagamentos e switchings deve ser resolvida dentro da construção das trajetórias candidatas do motor e antes da comparação terminal dos pacotes.

---

### 3.5. FIFO

FIFO pode ser usado inicialmente como candidato interno simples e auditável para seleção de fontes de pagamento.

FIFO não deve ser tratado como:

- etapa autônoma;
- regra final exclusiva;
- promoção direta de diagnóstico;
- substituto da comparação terminal dos pacotes.

---

### 3.6. Renderização oficial

Console e XLSX são renderizações da mesma saída canônica validada.

A renderização oficial unificada deve gerar, no mínimo:

- console;
- XLSX.

A validação de paridade deve ocorrer depois da renderização e deve verificar se console e XLSX representam a mesma saída canônica validada.

---

### 3.7. Ciclo contínuo

A limpeza e depreciação controlada não encerra o pipeline.

Após qualquer remoção, depreciação, normalização ou substituição estrutural, o processo deve retornar à etapa 1, exigindo nova execução integral do pipeline.

---

## 4. Arquivos alterados nesta frente documental

### 4.1. README.md

Alterações principais:

- inclusão das cinco abas operacionais mínimas:
  - `Carteira`;
  - `Todos os Gastos`;
  - `Inventário de Lotes`;
  - `Salários`;
  - `Switching`;
- inclusão do fluxograma macro do pipeline operacional;
- registro de que console e XLSX são renderizações sincronizadas;
- registro de que a limpeza/depreciação retorna à etapa 1.

### 4.2. relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md

Alterações principais:

- substituição da antiga seção 7-E por uma seção de arquitetura macro obrigatória;
- formalização das 11 etapas do pipeline;
- inclusão do fluxograma macro oficial;
- formalização do inventário completo de lotes dentro da etapa de dados operacionais e universo econômico canônico;
- formalização da dependência do motor em relação ao ranking para avaliação de switchings;
- reforço da vedação a trilhas independentes de pagamentos e switchings;
- inclusão da limpeza/depreciação controlada como etapa cíclica.

---

## 5. Itens explicitamente não alterados

Esta microetapa não alterou:

- código do motor;
- funções de cálculo;
- scripts de renderização;
- modelo matemático-estatístico-financeiro oficial;
- regra econômica;
- regras de pagamento;
- regras de switching;
- estrutura da planilha oficial;
- saídas canônicas;
- dados financeiros no escopo documental da V.0.

---

## 6. Validações realizadas

Foram realizadas validações operacionais após as alterações documentais:

- `git diff --check`;
- execução de `python -B aplicacao/principal.py`;
- geração de `saidas/oficial/relatorio_operacional_v225.xlsx`;
- verificação de que as cinco abas operacionais canônicas foram reconhecidas:
  - `Carteira`;
  - `Salários`;
  - `Todos os Gastos`;
  - `Switching`;
  - `Inventário de Lotes`;
- confirmação de repositório limpo após push:
  - `git status -sb`
  - resultado esperado: `## main...origin/main`.

---

## 7. Observações não bloqueantes

O console ainda contém formulações herdadas, como amostra de switchings independentes de pagamentos.

Isso é compatível com o estado atual do código, mas deverá ser tratado em etapa futura de alinhamento do motor e da renderização ao macrofluxo oficial.

Também permanecem alertas operacionais de saldo temporal insuficiente em pagamentos futuros. Esses alertas pertencem à evolução futura do motor temporal conjunto, não à V.0 documental.

---

## 8. Decisão final

A V17-F0-V.0 documental fica formalmente concluída quanto ao fluxograma macro do pipeline operacional.

Estado final:

- README alinhado;
- contrato operacional alinhado na seção 7-E;
- motor preservado;
- modelo oficial preservado;
- repositório limpo;
- main local sincronizada com origin/main.

---

## 9. Próxima etapa recomendada

Iniciar a auditoria individual da etapa 3:

`Dados operacionais e universo econômico canônico`

Objetivo da próxima etapa:

- mapear scripts e funções que constroem dados operacionais canônicos;
- auditar a construção do inventário completo de lotes;
- verificar dependências entre `Inventário de Lotes`, `Switching`, `Carteira`, `Salários` e `Todos os Gastos`;
- identificar funções existentes antes de criar novas funções;
- evitar criação desnecessária de scripts ou funções paralelas.
