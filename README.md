# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V59

A V59 preserva a base funcional vigente, mantém a arquitetura reorganizada da baseline e fecha a higiene operacional/documental da release com uma checagem mínima automática.

## Estrutura canônica da V59

### Orquestração da baseline
- `nucleo/contexto_baseline.py` → montagem central da baseline
- `nucleo/identidade_baseline.py` → versão e nomes-base de artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config

### Execução principal
- `aplicacao/console/principal.py` → caminho canônico do console
- `aplicacao/principal.py` → wrapper de compatibilidade

### Scripts auxiliares
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/*.py` → wrappers de compatibilidade

### Dados canônicos
- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

### Saídas
- `saidas/operacional/` → artefatos vigentes da baseline atual

### Documentação vigente
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V59.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V59.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V59.md`

## Comandos canônicos

```bash
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/diagnostico/inspecionar_base.py
python scripts/diagnostico/verificar_release_baseline.py
```

## Comandos antigos preservados

```bash
python aplicacao/principal.py
python scripts/gerar_planilha_operacional.py
python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/inspecionar_base.py
python scripts/verificar_release_baseline.py
```


## Atualização V59

- limpeza de artefatos efêmeros (`__pycache__` e `.pyc`) da entrega;
- atualização da documentação vigente para a baseline atual;
- remoção do ramo residual `menos_1_dia`;
- adição de uma checagem mínima automática de release.