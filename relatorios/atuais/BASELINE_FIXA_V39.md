# BASELINE FIXA V39

## Escopo desta derivação

Esta derivação consolida uma limpeza documental mais ampla do repositório, sem abrir nova frente econômica nem alterar a lógica financeira já estabilizada na V38.

## Objetivos da limpeza documental

- separar de forma explícita a documentação **vigente** da documentação **histórica**;
- reduzir ruído no diretório `relatorios/`;
- manter a trilha de evolução documental sem perder rastreabilidade;
- alinhar o `README.md`, o contrato operacional e o índice de relatórios à estrutura atual;
- remover artefatos temporários proibidos do pacote final.

## Estrutura documental oficial a partir da V39

- `relatorios/atuais/`
  - documentos vigentes da baseline atual;
  - contrato operacional vigente;
  - validação local mais recente.
- `relatorios/historico/baselines/`
  - versões anteriores de baseline fixa.
- `relatorios/historico/validacoes/`
  - validações locais de versões anteriores.
- `relatorios/historico/auditorias_especificas/`
  - auditorias e validações focadas por lote ou por frente específica.
- `relatorios/INDICE_RELATORIOS.md`
  - mapa oficial da documentação.

## Regra documental ativa

A documentação principal do projeto deve apontar apenas para os artefatos vigentes da baseline atual. A documentação histórica deve permanecer preservada, mas fora do caminho principal de navegação.

## Regra canônica mantida da baseline

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.

## Observação operacional

A V39 não substitui a trilha histórica anterior; ela apenas reorganiza essa trilha para tornar a baseline atual mais legível, auditável e fácil de manter.
