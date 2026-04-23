# Extração do runner do simulador central — V157

## Objetivo
Extrair apenas `rodar_integracao_funcional_minima_v117` de `nucleo/simulador_central_eventos_v1.py` para um módulo próprio de runner, preservando compatibilidade e sem mover builder de estado, switching ou valoração terminal.

## Mudanças aplicadas
- novo pacote `nucleo/runners/`
- novo módulo `nucleo/runners/simulador_central_runner_v117.py`
- novo `nucleo/runners/README.md`
- `nucleo/simulador_central_eventos_v1.py` agora mantém apenas um wrapper de compatibilidade para `rodar_integracao_funcional_minima_v117`

## Contrato preservado
- nome público preservado: `rodar_integracao_funcional_minima_v117`
- assinatura preservada
- retorno preservado
- builder de estado, switching, valoração terminal e `simular_cenario_eventos_v1` permanecem no simulador central

## Validação
- `compileall` em `nucleo/`, `aplicacao/` e `scripts/`
- import do wrapper antigo e do runner novo

## Observação de baseline
A baseline V156 não estava disponível em `.zip` no ambiente no momento desta execução. A extração foi aplicada sobre o código acessível da V155, mantendo a orientação estrutural definida na auditoria interna da V156 e sem alterar o contrato funcional observado.

## Próxima etapa recomendada
Extrair, em micro-etapa separada, apenas `construir_estado_global_recorte_curto_v117` para um módulo de builder de estado com wrapper de compatibilidade.
