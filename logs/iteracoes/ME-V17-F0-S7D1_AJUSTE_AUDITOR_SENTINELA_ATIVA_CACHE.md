# ME-V17-F0-S7D1_AJUSTE_AUDITOR_SENTINELA_ATIVA_CACHE

## 1) Identificação

- MICROETAPA=V17-F0-S.7-D.1
- TIPO=MICROCORRECAO_DIAGNOSTICA
- OBJETIVO=tornar o auditor S.7-D robusto a data de referencia/cache para lote ativo_pos_switching
- BASELINE_ENTRADA=66b790e
- Q_REABERTA=nao

## 2) Problema observado

A S.7-E foi bloqueada porque o auditor S.7-D ainda usava valores fixos para o Lote 3120 mai:

- Liquido atual
- Patrimonio liquido
- Rendimento liquido
- Saldo remanescente

Esses campos variam quando a data de referencia e o cache CDI avancam, pois o lote permanece ativo_pos_switching.

## 3) Decisao tecnica

- Manter validacao fixa para Lote 190 mai, pois esta exaurido.
- Tornar dinamica a validacao do Lote 3120 mai, pois esta ativo_pos_switching.
- Validar formulas e invariantes, nao valores fixos obsoletos.

## 4) Invariantes preservados

Para Lote 3120 mai, exigir:

- Status ciclo=ativo_pos_switching
- Liquido sacado >= 24.00
- Liquido atual > 0
- Patrimonio liquido = Liquido sacado + Liquido atual
- Rendimento liquido = Patrimonio liquido - Orig.
- Rendimento liquido > 0
- Linha correspondente no Extrato Passado presente
- Saldo remanescente no Extrato Passado > 0

## 5) Escopo

Arquivos alterados:

- scripts/diagnostico/auditar_patrimonio_rendimento_lotes_consumidos_v17_f0_s7d.py
- logs/iteracoes/ME-V17-F0-S7D1_AJUSTE_AUDITOR_SENTINELA_ATIVA_CACHE.md

Nao altera:

- motor economico
- saida_observavel.py
- principal.py
- matriz S.7
- switching
- ranking
- Q
- dados/cache

## 6) Validacao esperada

- sentinela_lote_190_ok=sim
- sentinela_lote_3120_formula_patr_ok=sim
- sentinela_lote_3120_formula_rend_ok=sim
- sentinela_lote_3120_ok=sim
- qtd_lotes_sugeridos_alterados=0
- qtd_status_recomendacao_alterados=0
- qtd_lotes_com_patr_liq_diferente_de_liq_sac_mais_liq_atual=0
- qtd_lotes_com_rend_liq_diferente_de_patr_liq_menos_orig=0
- status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido

## 7) Decisao

- S7D1_AJUSTE_AUDITOR_APROVADO=pendente
- S7E_LIBERADA_APOS_VALIDACAO=pendente
- Q_REABERTA=nao
