# V170 — Extração de camada comum neutra entre parcial e integral

## Objetivo
Auditar se a montagem do payload do lote destino no switching parcial e a montagem do payload de mutação no switching integral já podiam compartilhar uma camada local ainda mais neutra de campos comuns, sem tocar em `_valor_terminal_estimado_lote`, `_calcular_metrica`, `_patrimonio_terminal_proxy` ou `simular_cenario_eventos_v1`.

## Conclusão
A fronteira foi considerada segura.

O núcleo compartilhável encontrado é estritamente estrutural:
- identificação do produto destino
- campos de valor do lote destino já calculados
- proxy/retorno/liquidez/carência do destino
- datas locais de aplicação e valuation já definidas antes
- custo fiscal acumulado incremental já fechado antes
- flags de rastreabilidade do evento

## Implementação aplicada
Foi criado o helper local:
- `_construir_campos_comuns_destino_evento_switching(...)`

Ele passou a ser usado em:
- `_construir_payload_mutacao_switching_integral(...)`
- `_aplicar_switching_parcial_no_lote(...)`

## O que permaneceu fora da camada comum
- `id` do novo lote parcial
- `valor_inicial` do novo lote parcial
- mutação residual do lote de origem no parcial
- `lote.update(...)` no integral
- qualquer recálculo econômico/fiscal/terminal

## Segurança da mudança
A extração não alterou:
- contrato funcional esperado
- lógica econômica do switching
- semântica de pós-vencimento
- valoração terminal global
- executor central

## Validação executada
- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m compileall nucleo aplicacao`
- import mínimo de `nucleo.simulador_central_eventos_v1`
