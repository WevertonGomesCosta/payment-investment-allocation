# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts
financeiros: um de otimização de pagamentos e resgates, e outro de switching
para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo é evoluir esta base para um projeto único, auditável
 e modular de alocação conjunta de recebidos entre pagamentos, investimentos e
 decisões de switching, maximizando o patrimônio líquido final com matemática
financeira correta.

## Estado atual do repositório

**Versão atual da baseline:** V3

A V3 não representa ainda uma expansão funcional do projeto. Ela é uma
**reconstrução controlada da baseline** para deixá-la coerente com a regra de
trabalho adotada no projeto:

> a estrutura física dos módulos dos scripts-base não é tratada como fronteira
> semântica confiável; as decisões de migração e unificação devem seguir a
> responsabilidade real das funções.

## O que mudou na V3

A V2 revisada foi reavaliada e reconstruída para remover compromissos
arquiteturais prematuros.

As principais mudanças foram:

- simplificação da árvore do repositório para uma base mais neutra;
- tradução do núcleo inicial para português;
- remoção de diretórios futuros que ainda poderiam induzir modularização antes
  da hora;
- fortalecimento do carregamento do config com base no bloco já auditado do
  Script 1;
- manutenção do leitor de planilha em escopo estritamente estrutural.

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
│   └── AUDITORIA_ARQUITETURAL_V3.md
└── testes/
    └── .gitkeep
```

## Entradas canônicas atuais

A baseline atual utiliza como entradas principais:

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`

O carregamento foi mantido com compatibilidade para caminhos antigos quando
necessário, mas a convenção oficial da baseline reconstruída passa a ser a
pasta `dados/`.

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
- carregamento das abas;
- leitura estrutural inicial;
- canonização inicial de colunas com base nos aliases do config.

## O que esta versão deliberadamente não implementa

Esta versão ainda não implementa:

- contratos finais de entidades de domínio;
- motores de pagamento;
- motores de switching;
- adaptadores remotos;
- reconstrução histórica de lotes;
- regras profundas de IR/IOF;
- avaliação conjunta de cenários.

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

O comando imprime:

- raiz do repositório resolvida;
- caminho do config;
- caminho da planilha;
- relatório de dependências;
- nomes das abas;
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

O próximo passo mais seguro é continuar a auditoria comparativa dos scripts-base
antes de criar entidades finais, validadores semânticos profundos ou módulos de
negócio mais específicos.
