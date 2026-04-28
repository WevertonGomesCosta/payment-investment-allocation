# Decisão — CSVs diagnósticos V241 em saidas/diagnostico

## Objetivo

Decidir se os dois CSVs diagnósticos V241 devem continuar em `saidas/diagnostico/` ou se podem ser tratados como candidatos à remoção controlada futura após a criação do relatório consolidado em `relatorios/atuais/`.

## Arquivos avaliados

- `saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv`
- `saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv`

## Evidência já consolidada

A auditoria V241 foi consolidada em:

- `relatorios/atuais/RELATORIO_CONSOLIDADO_AUDITORIA_V241_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md`

O relatório consolidado preserva:

- síntese executiva;
- métricas agregadas;
- principais achados;
- interpretação operacional;
- amostra dos casos com divergência de lote motor-central;
- referência explícita aos dois CSVs originais.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa apenas define a decisão pós-consolidação.

## Decisão por arquivo

| Arquivo | Função | Decisão | Ação |
|---|---|---|---|
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv` | resumo diagnóstico bruto da V241 | `CANDIDATO_REMOCAO_CONTROLADA_FUTURA` | Manter por enquanto; pode ser removido somente em etapa posterior, com `git rm`, lista explícita e commit próprio. |
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv` | detalhe diagnóstico bruto da V241 por pagamento | `CANDIDATO_REMOCAO_CONTROLADA_FUTURA` | Manter por enquanto; pode ser removido somente em etapa posterior, com `git rm`, lista explícita e commit próprio. |

## Justificativa

Os dois CSVs já estão cobertos por um relatório consolidado em `relatorios/atuais/`, mas continuam sendo os arquivos-fonte brutos da auditoria V241.

Por isso, eles não devem ser removidos automaticamente nesta etapa. A decisão adequada é marcá-los como candidatos à remoção controlada futura, preservando-os até uma etapa específica de remoção com lista explícita.

## Decisão final desta etapa

Os dois CSVs V241 permanecem em `saidas/diagnostico/` por enquanto.

Eles ficam classificados como:

~~~text
CANDIDATO_REMOCAO_CONTROLADA_FUTURA
~~~

Qualquer remoção deve ocorrer apenas em etapa posterior, com comando explícito, validação de `git diff --cached --name-status`, commit próprio e `git status --short` limpo ao final.
