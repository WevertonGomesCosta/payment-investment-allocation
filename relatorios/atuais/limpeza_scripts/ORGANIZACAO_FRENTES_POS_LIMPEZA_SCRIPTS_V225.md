# Organização das frentes após limpeza estrutural de scripts — V225

## Identificação

- Baseline operacional: V225
- Tipo: relatório documental de organização pós-limpeza
- Escopo: definição da próxima frente do projeto após remoção de scripts/pastas não utilizados pela rota principal
- Restrições: não alterar código funcional; não alterar config; não alterar cálculo; não alterar replay; não alterar pagamentos; não alterar switching; não alterar ranking; não alterar identidade da baseline.

## Estado validado pelo usuário

Após a remoção manual/local de pastas e scripts que não eram utilizados por `aplicacao/principal.py`, o usuário validou:

- `python aplicacao/principal.py` executa sem erro;
- saída operacional preservada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável.

## Rota operacional atual

A rota principal atual é:

```text
aplicacao/principal.py
├── aplicacao.console.principal.main
└── nucleo.gerar_planilha_operacional.main
```

Observação importante: a geração da planilha operacional agora está em `nucleo/gerar_planilha_operacional.py`, e não mais em `scripts/operacional/gerar_planilha_operacional.py`.

## Ponto central de integração

O módulo `nucleo/contexto_baseline.py` é hoje o principal agregador operacional da baseline. Ele carrega e materializa:

- config;
- ambiente e data de referência;
- calendário financeiro;
- planilha e dados operacionais;
- carteira canônica;
- recebidos auditáveis;
- cache CDI;
- replay passado;
- ranking da Carteira;
- triagem;
- fontes elegíveis;
- saldo disponível;
- decisão local;
- switching econômico shadow;
- recomputação sequencial central;
- motor de recomendação de pagamentos com switching;
- módulos shadow/benchmark opcionais.

Portanto, qualquer nova frente deve respeitar `carregar_contexto_baseline(...)` como fronteira operacional.

## Camada observável oficial

`nucleo/saida_canonica.py` declara explicitamente que console, planilha e futuras saídas JSON/CSV/Markdown devem consumir o pacote canônico em vez de recalcular saldos, resgates, switchings ou amostras em paralelo.

Essa decisão deve permanecer como contrato central da próxima fase.

## Situação atual dos componentes principais

### 1. `aplicacao/principal.py`

Função atual:

- orquestra console;
- gera planilha operacional;
- imprime o caminho da saída.

Decisão: manter simples. Não deve receber lógica econômica nem montagem de relatórios.

### 2. `aplicacao/console/principal.py`

Função atual:

- renderiza o console oficial;
- consome `carregar_contexto_baseline(...)`;
- constrói `saida_canonica`;
- ainda mantém funções locais para auditorias residuais e preparação de alguns blocos.

Risco futuro:

- o console pode voltar a recalcular parte da camada observável que deveria vir da saída canônica.

Decisão: próxima frente candidata é auditar o console para separar renderização de cálculo/preparação de dados.

### 3. `nucleo/gerar_planilha_operacional.py`

Função atual:

- gera a planilha operacional;
- consome contexto e saída canônica;
- resolve nomes de abas e arquivo via config;
- escreve tabelas e estilos;
- contém contratos locais de cabeçalhos e seções.

Risco futuro:

- mistura configuração, mapeamento de colunas, formatação visual e escrita XLSX no mesmo arquivo.

Decisão: não mexer agora se a próxima frente for econômica. Só reorganizar se houver foco em arquitetura de saída.

### 4. `nucleo/contexto_baseline.py`

Função atual:

- materializa praticamente todo o grafo operacional;
- inclui módulos oficiais e módulos shadow/experimentais por flags.

Risco futuro:

- virar um arquivo agregador grande demais;
- dificultar identificar quais módulos são canônicos, auxiliares, shadow ou experimentais.

Decisão: próxima frente organizacional importante é documentar o grafo de dependências do contexto, sem alterar código.

### 5. `nucleo/saida_canonica.py`

Função atual:

- concentra a saída observável oficial;
- produz extrato passado, extrato futuro, switchings, ranking, situação atual e auditorias.

Risco futuro:

- crescer demais com lógica de cálculo/valoração que deveria ficar no motor econômico.

Decisão: manter como fronteira de apresentação, não como motor econômico primário.

## Próxima frente recomendada

A próxima frente deve ser:

```text
FRENTE: estabilizar e auditar a rota operacional canônica pós-limpeza
```

Objetivo: identificar quais módulos do `nucleo/` são realmente canônicos na execução atual, quais são auxiliares de saída e quais ainda são shadow/experimentais.

Essa frente deve vir antes de novas mudanças econômicas profundas, porque a limpeza de scripts reduziu ruído externo, mas o grafo interno do `nucleo/contexto_baseline.py` ainda está denso.

## Ordem recomendada das próximas microetapas

### Microetapa 1 — mapa da rota operacional real

Objetivo:

- mapear todos os imports e carregadores chamados por `aplicacao/principal.py` indiretamente via `aplicacao.console.principal`, `nucleo.gerar_planilha_operacional` e `nucleo.contexto_baseline`.

Produto:

- relatório com módulos classificados como:
  - entrada/config;
  - domínio financeiro;
  - replay;
  - decisão/pagamentos;
  - switching;
  - ranking;
  - saída canônica;
  - console/planilha;
  - shadow/benchmark;
  - legado ainda importado.

Não alterar código.

### Microetapa 2 — classificar módulos do `nucleo/` por autoridade

Objetivo:

- definir quais arquivos do `nucleo/` são canônicos e quais são auxiliares/diagnósticos/experimentais.

Classes sugeridas:

```text
CANONICO_OPERACIONAL
CANONICO_SAIDA
AUXILIAR_CONFIG_DADOS
AUXILIAR_FINANCEIRO
SHADOW_COMPARATIVO
EXPERIMENTAL_MANTIDO
LEGADO_IMPORTADO
CANDIDATO_REORGANIZACAO
```

Não remover arquivos nessa etapa.

### Microetapa 3 — auditar console versus saída canônica

Objetivo:

- identificar funções em `aplicacao/console/principal.py` que ainda preparam dados próprios;
- decidir se devem migrar para `nucleo/saida_canonica.py` ou permanecer como renderização local.

Foco inicial:

```text
_preparar_auditoria_lotes_residuais
_preparar_auditoria_detalhada_residuos
_preparar_resumo_auditoria_detalhada_residuos
_preparar_auditoria_recebimento_vs_aplicacao
```

Não alterar cálculo.

### Microetapa 4 — auditar planilha operacional pós-migração para `nucleo/`

Objetivo:

- avaliar se `nucleo/gerar_planilha_operacional.py` deve permanecer no `nucleo/` ou se deveria existir uma camada `aplicacao/saida/` ou `aplicacao/planilha/`.

Decisão provável:

- manter temporariamente onde está para não abrir nova reorganização física;
- documentar que ele é camada de saída, não motor econômico.

### Microetapa 5 — retomar evolução econômica com base na rota estabilizada

Depois da auditoria estrutural, a frente econômica mais importante passa a ser:

```text
motor_recomendacao_pagamentos_switching_v1
+ recomputacao_sequencial_central_v1
+ saida_canonica.extrato_futuro
```

Pergunta operacional central:

```text
Para cada conta futura, qual fonte/lote/switching deve ser usado, com cobertura integral, auditabilidade e melhor resultado econômico sem degradar o terminal líquido?
```

## Decisão estratégica

A limpeza de scripts deve parar temporariamente. A próxima fase não deve continuar removendo arquivos por inércia.

A prioridade agora é organizar o núcleo em torno da execução real:

```text
principal → contexto_baseline → motores canônicos → saída canônica → console/planilha
```

Somente depois disso faz sentido voltar a desenvolver o motor econômico.

## Prompt recomendado para a próxima microetapa

```text
Use a V225 após a limpeza estrutural de scripts e a validação de que aplicacao/principal.py executa sem erro e sem alteração econômica observável. Abra uma microetapa apenas para mapear a rota operacional real da execução atual: aplicacao/principal.py, aplicacao/console/principal.py, nucleo/gerar_planilha_operacional.py, nucleo/contexto_baseline.py e nucleo/saida_canonica.py. Classifique todos os módulos carregados indiretamente por contexto_baseline em canônico operacional, canônico de saída, auxiliar de config/dados, auxiliar financeiro, ranking, replay, decisão/pagamentos, switching, shadow/benchmark, experimental mantido ou candidato a reorganização. Não alterar código funcional, config, cálculo, replay, pagamentos, switching, ranking nem identidade da baseline. Gerar apenas relatório documental com a próxima frente recomendada.
```
