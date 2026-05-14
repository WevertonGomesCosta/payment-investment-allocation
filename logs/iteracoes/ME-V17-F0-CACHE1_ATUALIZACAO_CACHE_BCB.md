# ME-V17-F0-CACHE.1 — Atualização controlada do cache BCB

## Identificação

- MICROETAPA: ME-V17-F0-CACHE.1
- TIPO: DADOS / CACHE
- CLASSE: VERSIONAMENTO CONTROLADO DE CACHE BCB
- BASELINE DE ENTRADA: dd70768
- ARQUIVO ALTERADO: `dados/cache_bcb.json`

## Objetivo

Versionar separadamente a atualização do cache BCB/CDI gerada durante execução diagnóstica, sem misturar essa alteração com Q.1.5-C, Q.4, motor, ledger, replay, switching, ranking ou saída canônica.

## Escopo

Alteração permitida nesta microetapa:

- `dados/cache_bcb.json`

Registro documental:

- `logs/iteracoes/ME-V17-F0-CACHE1_ATUALIZACAO_CACHE_BCB.md`

## Restrições preservadas

- Não alterar `nucleo/*`.
- Não alterar `scripts/diagnostico/*`.
- Não alterar `aplicacao/*`.
- Não alterar `dados/dados_financeiros.xlsx`.
- Não alterar planilhas geradas.
- Não alterar contrato/modelo.
- Não alterar auditor Q.1.
- Não abrir Q.4 nesta microetapa.

## Verificação esperada

A atualização deve corresponder apenas à atualização legítima da série/cache BCB/CDI, preservando JSON válido e estrutura compatível.

## Encaminhamento

Após esta microetapa, retomar a correção do auditor Q.1 em:

`V17-F0-Q.1.5-C — restaurar gate canônico e reconciliação do auditor Q.1 após PR #304`.
