# Eixo temático: decisão temporal

## Objetivo

Agrupar, em uma única fronteira semântica, os scripts ligados à decisão diária e às suas auditorias locais, antes da reorganização do `nucleo/simulador_central_eventos_v1.py`.

## Subgrupos

### `motor_diario/`
Scripts que auditam o motor diário, sua execução em janelas curtas e variantes diretamente ligadas ao runner temporal.

Arquivos canônicos:
- `inspecionar_motor_diario_conjunto_experimental_v143.py`
- `inspecionar_motor_diario_conjunto_experimental_v144.py`
- `inspecionar_motor_diario_pos_vencimento_v146.py`
- `run_v150_multi.py`

### `valoracao_decisao/`
Scripts que auditam a valoração local do pacote, flattening, pós-pagamento dos 3k mar e a chave `tau`.

Arquivos canônicos:
- `inspecionar_auditoria_3k_mar_pos_pagamento_v147.py`
- `inspecionar_correcao_flattening_v148.py`
- `inspecionar_chave_tau_v149.py`

### `bloco_critico/`
Scripts de microplanejamento e heurísticas locais do bloco crítico, anteriores à decisão diária consolidada.

Arquivos canônicos:
- `inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- `inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
- `inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`

## Contrato estrutural

- `scripts/diagnostico/temporal_decisao/` passa a ser a fronteira canônica para auditorias temporais locais.
- `scripts/diagnostico/*.py` preserva wrappers de compatibilidade para caminhos legados.
- `scripts/*.py` permanece como fachada plana de execução antiga.

## Regra de baixo risco

Nesta etapa, o agrupamento é semântico e reversível. Nenhuma regra funcional do motor diário ou do simulador central foi alterada.
