# Auditoria técnica V173 — `_aplicar_efeito_evento_switching(...)`

## Objetivo
Auditar se `_aplicar_efeito_evento_switching(...)` já podia ser tratado como orquestrador local estável e congelável, ou se ainda havia uma microredução segura de assinatura/ramificação.

## Conclusão
A função **ainda não estava no melhor ponto de congelamento** na V172, porque mantinha um ramo inline relevante para `aporte_nao_aportado`, enquanto `switching_integral` e `switching_parcial` já estavam delegados para helpers dedicados.

Foi aplicada uma **última microredução segura de ramificação**, sem alterar contrato funcional, lógica econômica, semântica do pós-vencimento, valoração terminal global ou executor central.

## Mudança implementada
Foram extraídos dois helpers locais:

- `_construir_lote_destino_aporte_nao_aportado(...)`
- `_aplicar_aporte_nao_aportado_no_estado(...)`

Com isso, `_aplicar_efeito_evento_switching(...)` passou a operar como orquestrador local mais uniforme:

1. valida o tipo/objeto preparado;
2. delega `aporte_nao_aportado`;
3. delega `switching_integral`;
4. delega `switching_parcial`.

## O que não foi alterado
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`
- fórmulas econômicas/fiscais
- semântica do pós-vencimento
- executor central

## Justificativa arquitetural
A redução foi considerada segura porque o ramo extraído:

- não recalculava imposto;
- não recalculava valor migrado;
- não recalculava proxy terminal global;
- apenas consumia valores já fechados e persistia o novo lote destino de aporte.

## Validação executada
- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m compileall nucleo aplicacao`
- import mínimo de `nucleo.simulador_central_eventos_v1`

## Decisão recomendada após a V173
Após essa microredução, `_aplicar_efeito_evento_switching(...)` **já pode ser tratado como orquestrador local estável e congelável** nesta frente.

Seguir fragmentando a função agora tenderia a gerar indireção excessiva com baixo ganho estrutural.
