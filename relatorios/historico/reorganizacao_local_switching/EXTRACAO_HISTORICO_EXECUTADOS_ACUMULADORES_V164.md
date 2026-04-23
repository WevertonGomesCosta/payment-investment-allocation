# V164 — extração local de histórico, executados e acumuladores no simulador central

## Baseline
- baseline operacional real: V162
- derivação imediata aplicada sobre a V163

## Escopo desta microextração
Auditar e, sendo seguro, extrair a instrumentação pós-execução dentro de `_aplicar_switching_eventos`, cobrindo apenas:
- registro em `historico`
- registro em `executados`
- atualização de acumuladores (`ganho_total`, `perda_liquidez`, `custo_fiscal_total`)

## Conclusão da auditoria
A fronteira foi considerada segura porque essa camada já operava apenas com valores previamente calculados e não recalcula nenhuma regra econômica do switching.

## Novo helper local
- `_registrar_pos_execucao_evento_switching(...)`

Responsabilidade do helper:
- receber valores já fechados do evento
- registrar o payload histórico
- registrar o payload de execução
- devolver acumuladores atualizados

## O que permaneceu congelado
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`
- valoração terminal global
- lógica econômica do switching
- semântica de pós-vencimento

## Risco residual
Baixo. A extração é local, reversível e não altera a sequência macro do fluxo. O principal risco seria erro de montagem de payload, mitigado por reaproveitar os mesmos campos já usados na V163.

## Validação mínima
- `python -m compileall nucleo aplicacao`
- import mínimo de `nucleo.simulador_central_eventos_v1`
