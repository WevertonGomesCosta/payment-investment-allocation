# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts financeiros: um de otimização de pagamentos e resgates, e outro de switching para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo é evoluir esta base para um projeto único, auditável e modular de alocação conjunta de recebidos entre pagamentos, investimentos e decisões de switching, maximizando o patrimônio líquido final com matemática financeira correta.

## Estado atual do repositório

**Versão atual da baseline:** V43

A baseline atual consolida:

- leitura canônica das abas `Carteira`, `Inventário de Lotes` e `Todos os Gastos`;
- coluna `Data Recebimento` integrada ao contrato operacional dos lotes;
- cache diário de CDI com fallback controlado;
- núcleo financeiro mínimo e replay controlado do passado;
- regra geral de transição entre `Data Recebimento` e `Data Aplicação`;
- documentação vigente concentrada em `relatorios/atuais/`;
- pacote final limpo, sem resíduos temporários de versões anteriores;
- geração da planilha operacional atual em `saidas/relatorio_operacional_v43.xlsx`.

## Regra canônica ativa da baseline

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.

A regra de trabalho do projeto continua sendo:

> a estrutura física dos módulos dos scripts-base não é tratada como fronteira semântica confiável; as decisões de migração e unificação devem seguir a responsabilidade real das funções.

## Documentação oficial

Documentos vigentes da baseline atual:

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BASELINE_FIXA_V43.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V43.md`

Mapa da documentação:

- `relatorios/INDICE_RELATORIOS.md`

## Entradas canônicas atuais

A baseline atual utiliza como entradas principais:

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Uso mínimo

Instale as dependências atuais:

```bash
pip install -r requirements.txt
```

Execute a inspeção mínima da baseline:

```bash
python aplicacao/principal.py
```

Gere a planilha operacional atual:

```bash
python scripts/gerar_planilha_operacional.py
```

## Princípios mantidos nesta baseline

- config canônico único;
- interpretação canônica única da planilha;
- modularização incremental;
- auditoria por responsabilidade real;
- reauditoria da base antes de cada nova migração;
- entrega do repositório completo em `.zip` a cada versão.
