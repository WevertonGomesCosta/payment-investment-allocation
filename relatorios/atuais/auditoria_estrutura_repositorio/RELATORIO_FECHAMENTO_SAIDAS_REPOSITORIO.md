# Relatório de fechamento — pasta saidas

## Objetivo

Encerrar a auditoria estrutural da pasta `saidas/`, registrando a decisão final sobre os arquivos atualmente rastreados nessa pasta.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa apenas documenta o fechamento da pasta `saidas/`.

## Arquivos avaliados

A auditoria inicial de `saidas/` identificou 4 arquivos rastreados:

| Arquivo | Classe | Decisão final |
|---|---|---|
| `saidas/.gitkeep` | `METADADO_ESTRUTURAL_MANTER` | manter |
| `saidas/operacional/README.md` | `METADADO_ESTRUTURAL_MANTER` | manter |
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv` | `SAIDA_DIAGNOSTICO_AUDITAR` | manter até próxima limpeza |
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv` | `SAIDA_DIAGNOSTICO_AUDITAR` | manter até próxima limpeza |

## Consolidação executada

Os 2 CSVs diagnósticos V241 foram consolidados em:

- `relatorios/atuais/RELATORIO_CONSOLIDADO_AUDITORIA_V241_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md`

Esse relatório consolidado preserva:

- síntese executiva;
- métricas agregadas;
- principais achados;
- interpretação operacional;
- amostra dos casos com divergência de lote motor-central;
- referência explícita aos dois CSVs originais.

## Decisão sobre os CSVs V241

Os dois CSVs V241 permanecem em `saidas/diagnostico/` por enquanto.

Decisão registrada:

~~~text
CANDIDATO_REMOCAO_CONTROLADA_FUTURA
~~~

Interpretação:

- os arquivos já possuem síntese consolidada em `relatorios/atuais/`;
- ainda são evidência bruta útil da auditoria V241;
- não serão removidos nesta frente;
- poderão ser reavaliados em uma limpeza futura específica.

## Decisão final da pasta saidas

A pasta `saidas/` fica encerrada nesta frente com a seguinte decisão:

1. `saidas/.gitkeep` permanece;
2. `saidas/operacional/README.md` permanece;
3. os 2 CSVs V241 permanecem em `saidas/diagnostico/`;
4. nenhuma remoção ou movimentação foi executada;
5. os CSVs V241 só podem ser removidos futuramente mediante nova etapa explícita, com lista de arquivos, `git rm`, conferência de diff, commit próprio e `git status --short` limpo.

## Próxima pasta sugerida

Com `saidas/` encerrada, a próxima pasta a auditar deve ser `scripts/`, separando:

- scripts canônicos;
- scripts operacionais;
- scripts diagnósticos;
- wrappers;
- legados;
- candidatos a reorganização futura.
