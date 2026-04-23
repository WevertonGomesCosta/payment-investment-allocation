# EXTRAÇÃO DA MUTAÇÃO DO LOTE DE ORIGEM NO SWITCHING PARCIAL — V171

## Baseline
- Baseline operacional real considerada: V170
- Derivação gerada: V171

## Objetivo da microetapa
Auditar se a mutação do lote de origem no ramo de `switching_parcial` já podia ser isolada em um helper local próprio, sem tocar em:
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`

## Conclusão da auditoria
A fronteira foi considerada **segura para extração**.

### Motivo
O bloco do lote de origem no parcial já concentrava uma responsabilidade local coesa:
1. calcular `valor_residual`;
2. calcular `principal_residual`;
3. recomputar `valor_terminal_estimado` do lote residual usando a função já existente `_valor_terminal_estimado_lote(...)`.

Esse trecho não introduz regra econômica nova. Ele apenas aplica, de forma localizada, o efeito residual do resgate parcial sobre o lote de origem.

## Importante
A fronteira **não é puramente estrutural**, porque inclui a recomputação local de `valor_terminal_estimado` do lote residual. Ainda assim, a extração permanece segura porque:
- a fórmula não foi alterada;
- `_valor_terminal_estimado_lote(...)` não foi modificada;
- a recomputação continuou ocorrendo no mesmo ponto semântico do fluxo.

## Implementação aplicada
Foram criados dois helpers locais:
- `_construir_payload_mutacao_origem_switching_parcial(...)`
- `_aplicar_mutacao_origem_switching_parcial(...)`

### Papel de cada helper
- `_construir_payload_mutacao_origem_switching_parcial(...)`:
  - calcula os resíduos;
  - monta o payload final do lote residual;
  - recalcula o `valor_terminal_estimado` residual sem alterar a fórmula.

- `_aplicar_mutacao_origem_switching_parcial(...)`:
  - aplica o payload no lote original via `lote.update(...)`.

## O que permaneceu congelado
Nenhuma alteração foi feita em:
- valoração terminal global;
- executor central;
- `_calcular_metrica`;
- `_patrimonio_terminal_proxy`;
- `simular_cenario_eventos_v1`.

## Efeito arquitetural
A função `_aplicar_switching_parcial_no_lote(...)` agora ficou semanticamente separada em duas partes:
1. mutação do lote de origem residual;
2. criação do novo lote destino.

Isso reduz mistura de responsabilidades e aproxima a estrutura local do parcial do padrão já adotado no integral.

## Validação executada
- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m compileall nucleo aplicacao`
- import mínimo de `nucleo.simulador_central_eventos_v1`

## Risco residual
Baixo.

O principal ponto ainda aberto é que `_aplicar_switching_parcial_no_lote(...)` continua reunindo:
- mutação do lote de origem,
- construção do novo lote destino,
- append final no estado.

A mutação do lote de origem, porém, já está isolada e auditável.
