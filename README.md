# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts
financeiros: um de otimização de pagamentos e resgates, e outro de switching
para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo é evoluir esta base para um projeto único, auditável
 e modular de alocação conjunta de recebidos entre pagamentos, investimentos e
decisões de switching, maximizando o patrimônio líquido final com matemática
financeira correta.

## Estado atual do repositório

**Versão atual da baseline:** V9

A V9 preserva a baseline fixa da V7 e aplica apenas ajustes neutros derivados da auditoria do bloco 02, sem abrir domínio financeiro, fiscal ou de otimização:

- função central de data de referência;
- resolução semântica de colunas por alias configurado;
- endurecimento do contrato de chaves obrigatórias do config;
- correção documental da versão exibida e nova validação local.

A regra de trabalho do projeto continua sendo:

> a estrutura física dos módulos dos scripts-base não é tratada como fronteira
> semântica confiável; as decisões de migração e unificação devem seguir a
> responsabilidade real das funções.

## Estrutura atual do repositório

```text
.
├── .editorconfig
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── payment-investment-allocation.Rproj
├── requirements.txt
├── aplicacao/
│   └── principal.py
├── nucleo/
│   ├── __init__.py
│   ├── ambiente.py
│   ├── carregador_config.py
│   └── leitor_planilha.py
├── scripts/
│   └── inspecionar_base.py
├── dados/
│   ├── config_atualizado.json
│   ├── dados_financeiros.xlsx
│   ├── bruto/
│   │   └── .gitkeep
│   ├── intermediario/
│   │   └── .gitkeep
│   └── processado/
│       └── .gitkeep
├── saidas/
│   └── .gitkeep
├── relatorios/
│   ├── .gitkeep
│   ├── AUDITORIA_ARQUITETURAL_V3.md
│   └── CONTRATO_OPERACIONAL_PROJETO.md
└── testes/
    └── .gitkeep
```

## Documento-base oficial

O arquivo oficial de regras da fase atual é:

- `relatorios/CONTRATO_OPERACIONAL_PROJETO.md`

Esse documento deve ser tratado como a referência principal para:
- reavaliação da baseline;
- auditoria dos scripts-base;
- validação de novas regras;
- futuras alterações organizadas do projeto.

A validação local executada antes desta entrega está registrada em:
- `relatorios/VALIDACAO_LOCAL_V9.md`

## Entradas canônicas atuais

A baseline atual utiliza como entradas principais:

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`

A convenção oficial da baseline reconstruída permanece sendo a pasta `dados/`.

## Núcleo compartilhado inicial

### `nucleo/ambiente.py`
Responsável por:
- detecção da raiz do repositório;
- warnings seletivos de rede;
- verificação e instalação opcional de dependências por import real;
- contexto mínimo de timezone.

### `nucleo/carregador_config.py`
Responsável por:
- descoberta do config canônico;
- leitura do JSON de configuração;
- suporte a lista ordenada de configs candidatos;
- suporte a variável de ambiente;
- helpers seguros para leitura de chaves aninhadas.

### `nucleo/leitor_planilha.py`
Responsável por:
- descoberta da planilha canônica;
- carregamento estrutural das abas;
- leitura inicial da planilha;
- canonização inicial de colunas com base nos aliases do config.

## O que esta baseline ainda não implementa

Esta baseline ainda não implementa:
- contratos finais de entidades de domínio;
- motores de pagamento;
- motores de switching;
- adaptadores remotos;
- reconstrução histórica profunda de lotes;
- regras profundas de IR/IOF;
- avaliação conjunta final de cenários.

Essas camadas só devem ser abertas depois de novas auditorias comparativas dos
scripts-base.

## Uso mínimo

Instale as dependências atuais:

```bash
pip install -r requirements.txt
```

Execute a inspeção mínima da baseline:

```bash
python aplicacao/principal.py
```

ou:

```bash
python scripts/inspecionar_base.py
```

A saída atual do console foi organizada em blocos curtos para facilitar a
validação incremental da baseline. Nesta V9, a execução local mínima foi
realizada antes da entrega. Ela deve mostrar, no mínimo:
- caminhos principais resolvidos;
- contexto de ambiente;
- relatório de dependências;
- abas encontradas;
- abas primárias do contrato;
- resumo estrutural da planilha.

## Princípios mantidos nesta baseline

- config canônico único;
- interpretação canônica única da planilha;
- modularização incremental;
- auditoria por responsabilidade real;
- reauditoria da base antes de cada nova migração;
- nenhuma correção estrutural profunda no núcleo financeiro antes da hora;
- entrega do repositório completo em `.zip` a cada versão.

## Próximo passo recomendado

O próximo passo mais seguro continua sendo a auditoria comparativa dos
scripts-base antes da criação de entidades finais, validadores semânticos
profundos ou módulos de negócio mais específicos.
