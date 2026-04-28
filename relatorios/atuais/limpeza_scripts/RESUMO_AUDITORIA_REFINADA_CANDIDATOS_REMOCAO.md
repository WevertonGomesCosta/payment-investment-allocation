# Auditoria refinada dos candidatos à remoção em `scripts/diagnostico/`

## Objetivo

Separar referências operacionais reais de referências documentais, históricas e wrappers diagnósticos.

## Resumo

| Classe refinada | Ação refinada | Qtde |
|---|---|---:|
| AVALIAR_REFERENCIA_DIAGNOSTICA_WRAPPER | avaliar_wrapper_antes_de_remover | 8 |
| SEM_REFERENCIA_OPERACIONAL_REAL | candidato_remocao_refinada | 25 |

## Interpretação

- `PRESERVAR_REFERENCIA_OPERACIONAL`: possui referência em código operacional/núcleo/README operacional; não remover.
- `AVALIAR_REFERENCIA_DIAGNOSTICA_WRAPPER`: só aparece em wrappers/README de diagnóstico; avaliar se pode remover em bloco.
- `SEM_REFERENCIA_OPERACIONAL_REAL`: não apresentou uso operacional após exclusão de ruídos documentais/históricos; candidato à remoção refinada.

## Arquivo detalhado

- `relatorios\atuais\limpeza_scripts\auditoria_refinada_referencias_candidatos_remocao.csv`
