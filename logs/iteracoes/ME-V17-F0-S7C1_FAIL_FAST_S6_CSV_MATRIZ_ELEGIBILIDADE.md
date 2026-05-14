MICROETAPA: V17-F0-S.7-C.1

1. Diagnóstico Git inicial
- git status --short --branch: ## work
- git log --oneline -10 topo: 59c85ad V17-F0-S.7-C: integra matriz de elegibilidade ao recomendador
- git rev-parse --short HEAD: 59c85ad
- git branch --show-current: work
- git remote -v: indisponível no ambiente

2. Referência ao P1 do @codex (PR #314)
- Fail fast quando CSV S.6 estiver ausente/indisponível/vazio, sem retorno silencioso de DataFrame vazio.

3. Arquivos alterados
- nucleo/matriz_elegibilidade_fontes_s7b.py
- scripts/diagnostico/auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py
- scripts/diagnostico/auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py
- logs/iteracoes/ME-V17-F0-S7C1_FAIL_FAST_S6_CSV_MATRIZ_ELEGIBILIDADE.md

4. Descrição da correção fail-fast
- execução S.6 automática com `check=True` quando CSV S.6 ausente e script S.6 presente;
- erro explícito se script S.6 ausente: `erro_csv_s6_indisponivel_para_matriz_elegibilidade`;
- erro explícito se script falhar ou CSV não for produzido: `erro_s6_csv_nao_produzido`;
- erro explícito se CSV S.6 vazio ou sem linhas úteis: `erro_csv_s6_vazio_para_matriz_elegibilidade`;
- proibido retorno silencioso de `pd.DataFrame()` vazio na ausência/vazio de S.6.

5. Resultado do teste normal S.7-B
- status_geral_s7b=matriz_elegibilidade_fontes_construida
- qtd_fontes_avaliadas=47
- qtd_salarios_previstos_bloqueados=29
- qtd_uso_pre_aplicacao_sem_vinculo_bloqueados=3
- qtd_lacunas_reais_bloqueadas=0

6. Resultado do teste normal S.7-C
- matriz_consultada_no_fluxo_oficial=sim
- status_geral_s7c=integracao_matriz_elegibilidade_recomendador_concluida

7. Resultado do teste negativo
- monkeypatch controlado com CSV_S6 e SCRIPT_S6 inexistentes.
- resultado: RuntimeError
- mensagem: erro_csv_s6_indisponivel_para_matriz_elegibilidade
- confirmação: não houve retorno de DataFrame vazio.

8. Sentinelas POS
- S.7-B: sentinela_lote_190_nao_elegivel=sim; sentinela_lote_3120_ativo_pos=sim
- S.7-C: sentinela_lote_190_nao_promovido=sim; sentinela_lote_3120_preservado_quando_elegivel=sim

9. Regressões Q
- Q.0: switching_integrado_ok
- Q.1: sem_divergencia_observada
- Q.5-B/C/D/E: sem regressão observada

10. Hashes dados/cache
- dados_financeiros inicial/final: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4 / ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- cache_bcb inicial/final: 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525 / 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

11. Smoke
- python aplicacao/principal.py: exit 0

12. Confirmação de versionamento
- Nenhum arquivo em saidas/, dados, cache, XLSX, CSV diagnóstico ou temporário foi commitado.

13. Decisão
- S.7C1_FAIL_FAST_APROVADO=sim
- Q_REABERTA=nao
- S.7D_LIBERADA=sim
