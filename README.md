# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts financeiros:

- um otimizador de pagamentos e resgates;
- um motor de switching para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo é evoluir esta baseline para um projeto único, auditável e modular de
alocação conjunta de recebidos entre pagamentos, investimentos e decisões de switching,
maximizando o patrimônio líquido final sob regras financeiramente corretas.

## Estado Atual do Repositório

Este repositório é a baseline oficial controlada do esforço de unificação modular.

**Versão atual da baseline:** V2 revisada

Nesta etapa, o repositório contém:

- a planilha canônica e o arquivo de configuração em `data/`;
- os primeiros módulos Python compartilhados extraídos dos dois scripts originais;
- um ponto de entrada mínimo para inspeção da baseline;
- diretórios de apoio para as próximas etapas controladas da modularização.

## Entradas Canônicas

A baseline atual utiliza como entradas principais:

- `data/config_atualizado.json`
- `data/dados_financeiros.xlsx`

Esses arquivos permanecem como ponto de partida canônico para as primeiras etapas da migração estrutural.

## O que foi adicionado na V2

A V2 criou a primeira camada modular sem alterar ainda o núcleo financeiro profundo.

### Módulos compartilhados iniciais

- `core/ambiente.py`
  - tratamento seletivo de avisos de rede;
  - detecção do ambiente de execução;
  - verificação e instalação opcional de dependências;
  - contexto de timezone e bootstrap.

- `core/config_loader.py`
  - descoberta da raiz do repositório;
  - resolução do caminho do config canônico;
  - carregamento do JSON de configuração;
  - acesso seguro a chaves aninhadas.

- `core/io_planilha.py`
  - resolução do caminho da planilha canônica;
  - carregamento do workbook;
  - leitura inicial das abas;
  - canonização inicial de colunas com base nos aliases definidos no config.

### Ponto de entrada mínimo

- `app/main.py`

Esse ponto de entrada apenas inspeciona a baseline e imprime um resumo estruturado do config e da planilha.
Ele **ainda não** executa otimização de pagamentos, switching, simulação ou reconciliação financeira.

## Estrutura Atual do Repositório

```text
.
├── .editorconfig
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── payment-investment-allocation.Rproj
├── requirements.txt
├── app/
│   └── main.py
├── core/
│   ├── __init__.py
│   ├── ambiente.py
│   ├── config_loader.py
│   └── io_planilha.py
├── motores/
│   └── __init__.py
├── estrategias/
│   └── __init__.py
├── adapters/
│   └── __init__.py
├── scripts/
│   └── inspecionar_baseline.py
├── tests/
│   └── .gitkeep
├── data/
│   ├── config_atualizado.json
│   ├── dados_financeiros.xlsx
│   ├── raw/
│   │   └── .gitkeep
│   ├── interim/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── outputs/
│   └── .gitkeep
└── reports/
    └── .gitkeep
```

## Uso Mínimo

Crie ou ative seu ambiente Python e instale as dependências atuais:

```bash
pip install -r requirements.txt
```

Execute a inspeção da baseline a partir da raiz do repositório:

```bash
python app/main.py
```

ou:

```bash
python scripts/inspecionar_baseline.py
```

O comando imprime:

- raiz do repositório resolvida;
- caminho do config resolvido;
- caminho da planilha resolvido;
- relatório de dependências;
- nomes das abas da planilha;
- resumo inicial da baseline.

## Princípios de Projeto Mantidos

Este repositório continua seguindo a política de migração controlada:

- config canônico único;
- interpretação canônica única da planilha;
- modularização incremental;
- auditabilidade futura em nível de lote;
- nenhuma correção estrutural profunda antes que a unificação do núcleo esteja estável;
- entrega do repositório completo em `.zip` a cada versão.

## O que a V2 ainda não altera

A V2 deliberadamente **não** implementa nem reescreve:

- cálculos do núcleo financeiro;
- lógica tributária;
- reconciliação de IOF e IR;
- ranking de pagamento;
- ranking de switching;
- avaliação conjunta de cenários;
- reconstrução histórica de lotes.

Essas camadas deverão ser migradas em versões controladas posteriores.

## Recomendação antes da V3

Antes de expandir a base modular para contratos de entidades e validações mais profundas, a recomendação é auditar mais blocos equivalentes dos dois scripts-base. Isso reduz o risco de criar funções ou estruturas duplicadas que já existam nos scripts originais, preserva a identificação correta das responsabilidades e melhora a qualidade da unificação.

A prioridade recomendada para os próximos blocos é:

1. leitura do config e resolução de caminhos;
2. carga da planilha e interpretação das abas;
3. normalização/canonização de colunas;
4. construção inicial das estruturas de lotes, despesas e produtos;
5. validações operacionais mínimas;
6. só depois disso, migração controlada do núcleo de pagamento e switching.

## Próximo passo sugerido

O próximo passo mais seguro é continuar a auditoria comparativa dos scripts-base antes de ampliar demais a V2. A V3 deve nascer apenas depois que os próximos blocos equivalentes forem comparados e classificados em:

- manter;
- unificar;
- excluir;
- reescrever posteriormente.
