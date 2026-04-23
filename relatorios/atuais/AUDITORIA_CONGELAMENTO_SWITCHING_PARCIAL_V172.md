# Auditoria técnica V172 — congelamento local de `_aplicar_switching_parcial_no_lote(...)`

## Baseline auditada
- Baseline operacional: V171
- Arquivo auditado: `nucleo/simulador_central_eventos_v1.py`
- Fronteira avaliada: `_aplicar_switching_parcial_no_lote(...)`
- Escopo permitido: auditoria estrutural local sem tocar em `_valor_terminal_estimado_lote`, `_calcular_metrica`, `_patrimonio_terminal_proxy` ou `simular_cenario_eventos_v1`

## Pergunta da etapa
Verificar se `_aplicar_switching_parcial_no_lote(...)` já está modularizado o suficiente para congelar a frente local, ou se ainda vale uma última microextração apenas do `append`/persistência do novo lote destino no estado.

## Resultado da auditoria
**Conclusão:** a função já está modularizada o suficiente para congelamento local nesta frente.

## Motivos técnicos
Após as microextrações anteriores, a função ficou semanticamente organizada em três passos explícitos:

1. **Mutação do lote de origem residual**
   - delegada para `_aplicar_mutacao_origem_switching_parcial(...)`
2. **Construção do novo lote destino**
   - via `deepcopy(lote)` + campos específicos do novo lote + `_construir_campos_comuns_destino_evento_switching(...)`
3. **Persistência no estado**
   - `estado.setdefault('lotes_aportados', []).append(novo_lote)`

A etapa 3 é hoje uma operação terminal, de uma linha, sem regra econômica própria, sem derivação nova e sem reaproveitamento suficiente para justificar um helper dedicado.

## Avaliação da hipótese de microextração do append
### O que seria extraído
Algo como:
- `_persistir_lote_destino_switching(estado, novo_lote)`

### Benefícios esperados
- redução marginal de uma linha no corpo da função
- nome explícito para a persistência

### Custos/risco estrutural
- mais indireção para uma operação trivial
- piora potencial da legibilidade local, porque o leitor passaria a saltar para um helper que só encapsula `setdefault(...).append(...)`
- ganho arquitetural muito baixo em comparação com as microextrações anteriores, que isolaram fronteiras semânticas reais

## Critério de decisão
A microextração do `append` **não** foi promovida porque:
- não reduz acoplamento relevante;
- não cria uma nova fronteira semântica útil;
- não reduz risco funcional;
- não elimina duplicação material;
- tende a produzir abstração cosmética.

## Decisão final
**Congelar a frente local de `_aplicar_switching_parcial_no_lote(...)` na V172**, sem nova microextração de persistência.

## Estado arquitetural consolidado da função
A função deve permanecer com a seguinte responsabilidade local clara:
- aplicar a mutação do lote de origem residual;
- construir o novo lote destino parcial;
- persistir o novo lote no estado.

## Próxima frente recomendada
Avançar para auditoria do nível imediatamente acima:
- verificar se `_aplicar_efeito_evento_switching(...)` já está suficientemente estável como orquestrador local do switching ou se ainda há excesso de argumentos/ramificações que justifique uma reorganização de compatibilidade.

## Restrições preservadas
- contrato funcional preservado
- lógica econômica do switching preservada
- semântica do pós-vencimento preservada
- valoração terminal global intocada
- executor central intocado
