# payment-investment-allocation

Repositório controlado para a unificação incremental de dois scripts financeiros: um de otimização de pagamentos e resgates, e outro de switching para lotes já investidos e lotes disponíveis.

O objetivo de longo prazo continua sendo evoluir esta base para um projeto único, auditável e modular de alocação conjunta de recebidos entre pagamentos, investimentos e decisões de switching.

## Estado atual do repositório

**Versão atual da baseline:** V54

A V54 preserva a base funcional vigente e formaliza a regra de aquisição de dados com download primeiro e fallback controlado depois.

## Estrutura canônica da V54

### Execução principal
- `aplicacao/console/principal.py` → caminho canônico do console
- `aplicacao/principal.py` → wrapper de compatibilidade

### Scripts auxiliares
- `scripts/operacional/gerar_planilha_operacional.py` → geração da planilha operacional
- `scripts/auditoria/gerar_auditoria_diaria_lote.py` → auditoria diária de lote
- `scripts/diagnostico/inspecionar_base.py` → inspeção rápida da baseline
- `scripts/*.py` → wrappers de compatibilidade para os comandos antigos

### Dados canônicos
- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

### Saídas
- `saidas/operacional/` → artefatos gerados da baseline atual

### Documentação vigente
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V54.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V54.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V54.md`

## Comandos canônicos

```bash
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/diagnostico/inspecionar_base.py
```

## Comandos antigos preservados

```bash
python aplicacao/principal.py
python scripts/gerar_planilha_operacional.py
python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/inspecionar_base.py
```

## Regra canônica ativa da baseline

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.
