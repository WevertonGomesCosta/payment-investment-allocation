# GOVERNANÇA FINAL DE SCRIPTS — V204

Status: `V204_LIMPEZA_FINAL_GOVERNANCA`

## Escopo aplicado

A V204 foi criada a partir da V203 como limpeza final de governança, sem alterar motor,
contrato mestre, modelo matemático-estatístico-financeiro nem a regra de recebidos/aportes futuros.

## Ações executadas

1. Remoção de código morto do console que duplicava a camada `nucleo.saida_canonica`.
2. Conversão do diagnóstico de ranking estabilizado em wrapper read-only da saída canônica.
3. Redirecionamento da auditoria diária de lote para `saidas/diagnostico/`, deixando de escrever em saída oficial/operacional.
4. Bloqueio físico dos scripts históricos `.py` em `scripts/historico_raiz/` e `scripts/historico_saida_propria_v203/`.
5. Centralização dos helpers utilitários de baixo risco em `nucleo/utilitarios_neutros.py`:
   - `_safe_float`
   - `_coerce_date`
   - `_split_fontes_compostas`

## Decisão operacional

A saída operacional oficial deve continuar vindo de:

```text
nucleo.saida_canonica.construir_saida_canonica(...)
```

Scripts históricos e diagnósticos legados não têm autoridade operacional.

## Pontos explicitamente não alterados

- motor principal;
- alocação/recomendação de pagamentos;
- switching econômico;
- contrato mestre;
- modelo matemático-estatístico-financeiro;
- regra de recebidos/aportes futuros ainda não aportados em carteira.

## Gatilho da próxima frente

A próxima frente deve ser aberta apenas para tratar a regra econômica de recebidos/aportes futuros,
já com a governança de saídas e scripts estabilizada.
