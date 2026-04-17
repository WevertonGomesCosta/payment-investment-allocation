# Estrutura oficial do repositório V60

## Orquestração canônica

- `nucleo/contexto_baseline.py` → montagem central da baseline
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config

## Console

- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade

## Scripts

- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/*.py` → wrappers de compatibilidade

## Camada contratual mínima da F1

- `nucleo/caixa_recebidos_auditaveis.py` → estruturas canônicas mínimas de caixa/recebidos auditáveis
- `scripts/diagnostico/inspecionar_contrato_f1.py` → leitura observável do contrato mínimo da F1

## Auditabilidade de fechamento

- `nucleo/rotulagem_fechamento.py` → resumo auditável do fechamento econômico da situação atual

## Governança mínima de release

- `scripts/diagnostico/verificar_release_baseline.py` → checagem automática mínima de higiene da baseline

## Dados

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Saídas

- `saidas/operacional/` → artefatos vigentes da baseline atual

## Documentação

- `relatorios/atuais/` → documentos vigentes
- `relatorios/historico/` → trilha preservada por categoria documental

## Atualização V60

- abertura parcial da F1 por contrato mínimo executável/diagnóstico;
- manutenção da baseline limpa da V59 como base funcional;
- preservação do motor financeiro e do fluxo principal.
