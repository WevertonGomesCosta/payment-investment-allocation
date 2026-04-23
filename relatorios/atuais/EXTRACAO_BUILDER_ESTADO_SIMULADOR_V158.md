# Extração do builder de estado do simulador central — V158

Baseline estrutural utilizada: V157.

## Escopo
Extração isolada de `construir_estado_global_recorte_curto_v117` para um módulo dedicado de builder, com wrapper de compatibilidade preservado em `nucleo/simulador_central_eventos_v1.py`.

## O que foi feito
- criado `nucleo/builders/`
- criado `nucleo/builders/simulador_central_estado_v117.py`
- `construir_estado_global_recorte_curto_v117` no simulador central agora delega para o módulo novo
- nenhuma outra função de switching, valoração terminal ou executor central foi movida

## Dependências mantidas
Para minimizar risco, o builder novo importa helpers já existentes do simulador central:
- `_coerce_date`
- `_mapa_produtos_proxy`
- `_proxy_fallback_lote`

Também preserva o uso de:
- `_pagamentos_futuros`
- `proximo_dia_util_bancario_em_ou_apos`

## Compatibilidade
- assinatura pública preservada
- nome antigo preservado
- import antigo continua válido

## Validação
- `compileall` em `nucleo/`, `aplicacao/` e `scripts/`
- import do wrapper antigo
- import do builder novo

## Próxima fronteira segura
A próxima extração de baixo risco deve mirar apenas transições simples de estado (por exemplo, política pós-vencimento/ativação de recebidos), sem tocar ainda em `_aplicar_switching_eventos`, `_valor_terminal_estimado_lote`, `_calcular_metrica` ou `_patrimonio_terminal_proxy`.


## Verificação adicional de contrato
O corpo do builder extraído foi ajustado para espelhar os campos e a estrutura exata da implementação original da V157, evitando enriquecimento acidental do estado inicial.
