MICROETAPA: V17-F0-S.7-C

1. Diagnóstico Git inicial
- git status --short --branch: ## work
- git log --oneline -10 topo: 8fec517 V17-F0-S.7-B.1: corrige leitura classes S6 matriz elegibilidade
- git rev-parse --short HEAD: 8fec517
- git branch --show-current: work
- git remote -v: indisponível no ambiente

2. Baseline observada
- Divergência da baseline esperada (fbdec1c) registrada; execução permitida por política da etapa.

3. Confirmação S.7-B.1 verde
- status_geral_s7b=matriz_elegibilidade_fontes_construida
- qtd_fontes_avaliadas=47
- qtd_salarios_previstos_bloqueados=29
- qtd_uso_pre_aplicacao_sem_vinculo_bloqueados=3
- qtd_lacunas_reais_bloqueadas=0
- sentinela_lote_190_nao_elegivel=sim
- sentinela_lote_3120_ativo_pos=sim

4. Arquivos alterados
- aplicacao/principal.py
- nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
- scripts/diagnostico/auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py
- logs/iteracoes/ME-V17-F0-S7C_INTEGRACAO_MATRIZ_ELEGIBILIDADE_RECOMENDADOR.md

5. Ponto exato do fluxo integrado
- aplicação oficial: `aplicacao/principal.py`
- após construir `saida_canonica_com_switching_v17_c7`, a execução passa a construir matriz S.7-B e aplicar bloqueio/preservação por matriz antes da geração de console/planilha.

6. Adaptador/função criada
- `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py`
- função pública: `aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz_elegibilidade)`

7. Consulta de fontes simples e compostas
- fonte simples: lookup por identificador normalizado (`strip`, `casefold`, colapso de espaços).
- fonte composta: decomposição por `+`.
- critério: todos os componentes devem existir na matriz e estar com `elegivel_para_pagamento=sim` e `pode_ser_lote_sugerido=sim`.
- componente ausente/bloqueado: ação S.7-C registra bloqueio e remove promoção para `Lote sugerido`.

8. Resultado auditor S.7-C
- qtd_pagamentos_avaliados=159
- qtd_fontes_promovidas_antes_matriz=49
- qtd_fontes_promovidas_pos_matriz=49
- qtd_fontes_bloqueadas_pela_matriz=0
- qtd_fontes_nao_encontradas_na_matriz=0
- qtd_fontes_compostas_avaliadas=16
- qtd_fontes_compostas_bloqueadas=0
- qtd_salario_previsto_futuro_bloqueado_no_fluxo=0
- qtd_uso_pre_aplicacao_sem_vinculo_bloqueado_no_fluxo=0
- qtd_lote_exaurido_bloqueado_no_fluxo=0
- qtd_lote_migrado_bloqueado_no_fluxo=0
- qtd_lote_pos_switching_materializado_preservado=12
- qtd_pagamentos_com_status_sem_saldo_temporal_preservado=110
- sentinela_lote_190_nao_promovido=sim
- sentinela_lote_3120_preservado_quando_elegivel=sim
- matriz_consultada_no_fluxo_oficial=sim
- status_geral_s7c=integracao_matriz_elegibilidade_recomendador_concluida

9. Sentinelas POS
- Lote 190 mai: não promovido.
- Lote 3120 mai: preservado quando elegível.

10. Regressões Q
- Q.0: switching_integrado_ok
- Q.1: sem_divergencia_observada
- Q.5-B/C/D/E: sem regressão

11. Hashes dados/cache
- dados_financeiros inicial/final: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4 / ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- cache_bcb inicial/final: 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525 / 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

12. Smoke
- python aplicacao/principal.py: exit 0

13. Confirmação de versionamento
- Nenhum arquivo em saidas/, dados, cache, XLSX oficial ou CSV diagnóstico foi incluído no commit.

14. Decisão
- S.7C_INTEGRACAO_APROVADA=sim
- Q_REABERTA=nao
- S.7D_LIBERADA=sim
