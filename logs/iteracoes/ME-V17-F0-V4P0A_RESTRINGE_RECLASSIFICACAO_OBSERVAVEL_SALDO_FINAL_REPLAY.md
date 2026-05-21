# ME-V17-F0-V4P.0a — Restringe reclassificação observável por saldo final real do replay

A V4P local anterior foi reprovada porque usava último saldo positivo intermediário e reclassificava lotes exauridos indevidamente.

Esta microetapa altera a regra para usar o saldo final real do replay por lote, incluindo zeros, e bloqueia reclassificação de lotes migrados por switching.

Validação esperada:
- somente Lote 3120 mai reclassificado;
- nenhum lote migrado reclassificado;
- nenhum lote simultaneamente em ativos e exauridos;
- principal.py executa sem erro.
