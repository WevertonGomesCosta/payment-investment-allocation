# Integração funcional mínima V117/V121 — recorte curto

- Data de referência: 2026-04-21
- Horizonte: {'data_inicio': '2026-04-21', 'data_fim': '2026-05-21'}
- Critério do planejador temporal: ganho_terminal_economico_minimo_estimado
- Destinos elegíveis considerados por lote: 12
- Candidatos elegíveis de switching: 20
- Melhor cenário atual: switching_temporal_top2
- Vetor lexicográfico: (0.0, 0.0, 0.0, 48.99, 9699.45, 0.0, 29.41, 5.0)

## Melhor destino por lote

### Lote 3000 mar. B
- Melhor destino no recorte: CDB XP 150%
- Rank do destino: 8
- Elegível: True
- Ganho terminal econômico mínimo estimado: 19.08
- Patrimônio terminal origem estimado: 3099.09
- Patrimônio terminal destino estimado: 3118.17
- Custo fiscal estimado: 28.52
- Penalidade carência reprojetada: 0.0

### Lote 3000 mar. V
- Melhor destino no recorte: CDB XP 150%
- Rank do destino: 8
- Elegível: True
- Ganho terminal econômico mínimo estimado: 18.23
- Patrimônio terminal origem estimado: 3102.16
- Patrimônio terminal destino estimado: 3120.39
- Custo fiscal estimado: 29.41
- Penalidade carência reprojetada: 0.0

## Top candidatos do planejador temporal

### switching_candidato_3_8
- Lote: Lote 3000 mar. B
- Data: 2026-04-21
- Produto destino: CDB XP 150%
- Rank do destino: 8
- Elegível: True
- Ganho terminal econômico mínimo estimado: 19.08

### switching_candidato_2_8
- Lote: Lote 3000 mar. V
- Data: 2026-04-21
- Produto destino: CDB XP 150%
- Rank do destino: 8
- Elegível: True
- Ganho terminal econômico mínimo estimado: 18.23

### switching_candidato_3_1
- Lote: Lote 3000 mar. B
- Data: 2026-04-21
- Produto destino: Mercado Pago Cofrinho 120% CDI (Meli+)
- Rank do destino: 1
- Elegível: True
- Ganho terminal econômico mínimo estimado: 10.04

### switching_candidato_3_4
- Lote: Lote 3000 mar. B
- Data: 2026-04-21
- Produto destino: Combo PicPay 100-120 3m
- Rank do destino: 4
- Elegível: True
- Ganho terminal econômico mínimo estimado: 10.04

### switching_candidato_3_5
- Lote: Lote 3000 mar. B
- Data: 2026-04-21
- Produto destino: Combo PicPay 100-120 6m
- Rank do destino: 5
- Elegível: True
- Ganho terminal econômico mínimo estimado: 10.04

### switching_candidato_2_1
- Lote: Lote 3000 mar. V
- Data: 2026-04-21
- Produto destino: Mercado Pago Cofrinho 120% CDI (Meli+)
- Rank do destino: 1
- Elegível: True
- Ganho terminal econômico mínimo estimado: 9.18

### switching_candidato_2_4
- Lote: Lote 3000 mar. V
- Data: 2026-04-21
- Produto destino: Combo PicPay 100-120 3m
- Rank do destino: 4
- Elegível: True
- Ganho terminal econômico mínimo estimado: 9.18

### switching_candidato_2_5
- Lote: Lote 3000 mar. V
- Data: 2026-04-21
- Produto destino: Combo PicPay 100-120 6m
- Rank do destino: 5
- Elegível: True
- Ganho terminal econômico mínimo estimado: 9.18

## Cenários avaliados

### switching_temporal_top2
- Descrição: Recorte curto com Lote 3000 mar. V -> CDB XP 150% em 2026-04-21
- Vetor: (0.0, 0.0, 0.0, 48.99, 9699.45, 0.0, 29.41, 5.0)
- Patrimônio líquido terminal proxy: 1738.28
- Ganho switching total: 94.76
- Pagamentos cobertos: 13
- Pagamentos sem cobertura: 0

### switching_temporal_top1
- Descrição: Recorte curto com Lote 3000 mar. B -> CDB XP 150% em 2026-04-21
- Vetor: (0.0, 0.0, 0.0, 49.01, 9698.24, 0.0, 28.52, 5.0)
- Patrimônio líquido terminal proxy: 1739.08
- Ganho switching total: 94.69
- Pagamentos cobertos: 13
- Pagamentos sem cobertura: 0

### baseline_sem_switching
- Descrição: Recorte curto sem switching temporal.
- Vetor: (0.0, 0.0, 0.0, 113.82, 8533.71, 0.0, 0.0, 3.0)
- Patrimônio líquido terminal proxy: 1608.11
- Ganho switching total: 0.0
- Pagamentos cobertos: 13
- Pagamentos sem cobertura: 0

## Síntese

- Destinos alternativos economicamente sobreviventes: 20.
- Quando esse total é zero, o destino padrão falhou e nenhum destino alternativo melhorou suficientemente o cenário no recorte.
