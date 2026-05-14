MICROETAPA: V17-F0-S.7-C.2-FECHAMENTO

Diagnóstico Git inicial
- branch: work
- head: 26711ae
- diff restrito aos 4 arquivos de código esperados da S.7-C.2.
- git diff --check: sem inconsistências de whitespace.

Classificação do diff
- nucleo/matriz_elegibilidade_fontes_s7b.py: mudanca_funcional_s7c2_prevista (recomposição S.2/S.4/S.6 + vínculo S.6).
- nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py: mudanca_funcional_s7c2_prevista (enforcement/telemetria S.6 no fluxo).
- scripts/diagnostico/auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py: instrumentacao_de_validacao.
- scripts/diagnostico/auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py: instrumentacao_de_validacao.
- sem alteração fora do escopo (ranking/switching/motor/Q/rendimento/patrimônio).

Validações curtas
- py_compile dos 4 arquivos: ok.
- testes isolados:
  - CSV S.6 ausente + scripts ausentes -> RuntimeError erro_recomposicao_cadeia_s6_indisponivel.
  - recomposição determinística por stubs S.2→S.4→S.6 -> ok; s6_origem=recomposta.
  - adaptador S.7-C decompõe fonte composta e bloqueia componente inelegível -> ok.
  - qtd_fonte_id_sintetico_usado_para_lookup = 0 em cenário isolado.

Validações longas (timeout controlado)
- auditar_lacuna_integracao_temporal_v17_f0_s2.py: timeout.
- auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py: timeout.
- auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py: timeout.
- demais auditores longos/Q/principal.py: não reconfirmados nesta rodada para evitar travamento cumulativo.

Evidência alternativa por artefato/inspeção
- CSV S.6 ausente no momento da validação longa; a função agora recompõe ou falha explicitamente.
- schema e vínculo S.6 avaliados por testes isolados com stubs e pelo código:
  - s6_origem
  - classe_politica_s6
  - linkavel_ao_fluxo / motivo_nao_linkavel
  - chave_operacional_s6 / fonte_id_real
- integração S.7-C mede exposição operacional e enforcement:
  - qtd_componentes_fluxo_nao_lote
  - s7c_enforcement_s6_classes
  - qtd_fonte_id_sintetico_usado_para_lookup

Hashes dados/cache
- dados/dados_financeiros.xlsx antes/depois: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- dados/cache_bcb.json antes/depois: 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

Decisão de fechamento
- S.7C2_VALIDACAO_COMPLETA=nao
- S.7C2_CORRECAO_CONTROLADA_APLICADA=sim
- S.7C2_GATE_S6_REPRODUTIVEL_APROVADO=sim
- S.7C2_VINCULO_S6_FLUXO_APROVADO=parcial_justificado_sem_exposicao_operacional
- Q_REABERTA=nao
- S.7D_LIBERADA=nao
