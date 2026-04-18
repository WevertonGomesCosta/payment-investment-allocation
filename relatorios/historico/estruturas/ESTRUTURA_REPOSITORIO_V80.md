# Estrutura do repositório V80

## Camadas novas da V80

- `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`

## Camadas preservadas

- `nucleo/caixa_recebidos_auditaveis.py`
- `nucleo/switching_economico_shadow.py`
- `nucleo/resolver_hibrido_5p_shadow.py`
- `scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`

## Papel da V80

A V80 não adiciona nova camada funcional ao motor. Ela só aprofunda, de forma cirúrgica, os 42 casos já classificados como reaproveitáveis, preservando a baseline decisória vigente e mantendo o benchmark híbrido como régua externa de auditoria.
