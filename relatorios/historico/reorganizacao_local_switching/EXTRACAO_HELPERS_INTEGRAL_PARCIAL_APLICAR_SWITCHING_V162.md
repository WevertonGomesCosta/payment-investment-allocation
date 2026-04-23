# Extração local entre switching integral e parcial no simulador central — V162

## Observação de baseline
O arquivo .zip da V161 não estava disponível no ambiente desta execução.
Para não bloquear a etapa, a alteração foi aplicada sobre a baseline estrutural acessível mais próxima (**V158**), reconstruindo localmente as microextrações intermediárias necessárias no mesmo módulo e executando apenas a separação pedida nesta etapa.

## Escopo da etapa
Microextração local dentro de `nucleo/simulador_central_eventos_v1.py`, sem mover a função principal `_aplicar_switching_eventos` e sem alterar o cálculo fiscal, a valoração do destino, a valoração terminal ou o executor central.

## Helpers locais adicionados
- `_preparar_evento_executavel_no_dia`
- `_registrar_historico_evento`
- `_registrar_execucao_evento`
- `_acumular_resultados_execucao`
- `_aplicar_switching_integral_no_lote`
- `_aplicar_switching_parcial_no_lote`

## O que mudou
A função principal `_aplicar_switching_eventos` continua no mesmo arquivo e com a mesma assinatura, mas agora delega:
- a preparação do evento do dia;
- o registro de histórico/executados/acumuladores;
- a mutação do estado específica de switching integral;
- a mutação do estado específica de switching parcial.

## O que foi preservado
Sem alteração pretendida em:
- cálculo fiscal (`_aliquota_ir_estimada`, `_estimar_imposto_resgate`);
- valoração do destino (`_valor_terminal_estimado_lote`);
- métricas terminais;
- executor central `simular_cenario_eventos_v1`.

## Validação executada
- `compileall` em `nucleo/`, `aplicacao/` e `scripts/`;
- import do módulo `nucleo.simulador_central_eventos_v1`;
- verificação da presença dos helpers locais novos.

## Leitura arquitetural
Esta etapa melhora a legibilidade e prepara uma futura extração controlada do bloco de switching sem tocar ainda no núcleo econômico-fiscal.
A próxima separação segura continua sendo interna ao mesmo módulo, antes de qualquer movimento para outro pacote.
