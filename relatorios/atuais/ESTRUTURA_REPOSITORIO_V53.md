# Estrutura oficial do repositório V53

## Código-fonte e execução

- `aplicacao/console/` → ponto de entrada canônico do console
- `aplicacao/principal.py` → wrapper de compatibilidade
- `nucleo/` → motor e camadas centrais

## Scripts auxiliares

- `scripts/operacional/` → geração de artefatos operacionais
- `scripts/auditoria/` → auditorias específicas
- `scripts/diagnostico/` → inspeções e diagnósticos da baseline
- `scripts/*.py` → wrappers de compatibilidade

## Dados canônicos

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Saídas

- `saidas/operacional/` → artefatos gerados da baseline atual

## Documentação

- `relatorios/atuais/` → documentos vigentes
- `relatorios/historico/` → trilha preservada por tipo documental
