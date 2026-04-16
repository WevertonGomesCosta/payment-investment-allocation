# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts financeiros: um de otimização de pagamentos e resgates, e outro de switching para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo é evoluir esta base para um projeto único, auditável e modular de alocação conjunta de recebidos entre pagamentos, investimentos e decisões de switching, maximizando o patrimônio líquido final com matemática financeira correta.

## Estado atual do repositório

**Versão atual da baseline:** V40

A baseline atual já consolidou:

- leitura canônica das abas `Carteira`, `Inventário de Lotes` e `Todos os Gastos`;
- cache diário de CDI com fallback controlado;
- núcleo financeiro mínimo e replay controlado do passado;
- regra geral de transição entre `Data Recebimento` e `Data Aplicação`;
- limpeza documental ampla com separação entre documentação vigente e histórica;
- saída operacional simplificada com tabela final de lotes ativos e planilha operacional consolidada.

## Regra canônica ativa da baseline

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.

A regra de trabalho do projeto continua sendo:

> a estrutura física dos módulos dos scripts-base não é tratada como fronteira semântica confiável; as decisões de migração e unificação devem seguir a responsabilidade real das funções.

## Documentação oficial

Documentos vigentes da baseline atual:

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BASELINE_FIXA_V40.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V40.md`

Mapa completo da documentação:

- `relatorios/INDICE_RELATORIOS.md`

## Entradas canônicas atuais

A baseline atual utiliza como entradas principais:

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`

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

## Princípios mantidos nesta baseline

- config canônico único;
- interpretação canônica única da planilha;
- modularização incremental;
- auditoria por responsabilidade real;
- reauditoria da base antes de cada nova migração;
- entrega do repositório completo em `.zip` a cada versão.
