# Auditoria temática dos scripts temporais — V155

## Escopo

Auditoria temática sobre os scripts relacionados a motor diário, pós-vencimento, `tau` e bloco crítico, tomando a V154 como baseline estrutural.

## Achados centrais

1. O conjunto auditado possui **10 scripts** que tratam do mesmo eixo semântico: decisão temporal local.
2. Esse eixo estava espalhado no diretório plano `scripts/diagnostico/`, misturando:
   - runners do motor diário;
   - auditorias de valoração e flattening;
   - microplanejamento e heurísticas do bloco crítico.
3. A separação temática mais coerente, antes de tocar no simulador central, é:
   - `motor_diario/`
   - `valoracao_decisao/`
   - `bloco_critico/`

## Scripts auditados

### Grupo `motor_diario/`
- `inspecionar_motor_diario_conjunto_experimental_v143.py`
- `inspecionar_motor_diario_conjunto_experimental_v144.py`
- `inspecionar_motor_diario_pos_vencimento_v146.py`
- `run_v150_multi.py`

### Grupo `valoracao_decisao/`
- `inspecionar_auditoria_3k_mar_pos_pagamento_v147.py`
- `inspecionar_correcao_flattening_v148.py`
- `inspecionar_chave_tau_v149.py`

### Grupo `bloco_critico/`
- `inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- `inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
- `inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`

## Critério usado para o agrupamento

O agrupamento foi definido por responsabilidade real:
- **motor diário**: scripts que executam ou reexecutam o runner temporal diário;
- **valoração/decisão**: scripts que auditam a ponte entre ação, pacote, patrimônio terminal, pós-pagamento e chave `tau`;
- **bloco crítico**: scripts de planejamento local anterior ao runner consolidado.

## Consolidação aplicada

A implementação canônica desses 10 scripts foi movida para `scripts/diagnostico/temporal_decisao/`, preservando wrappers nos caminhos antigos.

## Risco funcional

Baixo.

- imports antigos continuam válidos por wrapper;
- nenhuma função de negócio do `nucleo/` foi alterada;
- o objetivo foi apenas reduzir ruído estrutural antes de reorganizar `simulador_central_eventos_v1.py`.

## Próxima etapa recomendada

Antes de reorganizar o simulador central, abrir uma auditoria interna do próprio `nucleo/simulador_central_eventos_v1.py` para separar:
- construção/normalização de estado;
- aplicação de eventos;
- valoração terminal;
- replay/continuação neutra.
