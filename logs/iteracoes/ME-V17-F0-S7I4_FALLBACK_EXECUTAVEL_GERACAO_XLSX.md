# ME-V17-F0-S7I4 — Fallback seguro de geração/garantia do XLSX no auditor S.7-I

## Identificação

- MICROETAPA: V17-F0-S.7-I.4
- TIPO: MICROCORREÇÃO DIAGNÓSTICA CURTA
- BASELINE_DE_ENTRADA_ESPERADA: 51cb619
- BASELINE_OPERACIONAL_CONGELADA: 5d401e1
- Q_REABERTA: não

## Objetivo

Tornar seguro e controlado o fallback de geração/garantia do XLSX no auditor S.7-I, removendo a chamada direta a entrypoint inseguro do núcleo.

## Comentário Codex tratado

- P1: o auditor S.7-I continha fallback direto para `nucleo/gerar_planilha_operacional.py`.
- Risco: falso bloqueio do gate S.7-I quando `aplicacao/principal.py` falhasse e o fallback secundário tentasse executar um entrypoint não seguro como script.

## Diagnóstico

- fallback_atual_detectado: sim
- fallback_direto_nucleo_detectado: sim
- entrada_importavel_segura_detectada: não usada
- estrategia_fallback_escolhida: remover fallback direto inseguro e registrar fallback secundário indisponível/controlado quando necessário

## Correção aplicada

A função `_garantir_xlsx()` foi ajustada para:

1. não executar nada se o XLSX oficial já existir;
2. tentar apenas `aplicacao/principal.py` se o XLSX estiver ausente;
3. se `aplicacao/principal.py` falhar, registrar fallback secundário indisponível de forma controlada;
4. nunca executar diretamente `nucleo/gerar_planilha_operacional.py` como script;
5. emitir `fallback_direto_nucleo_removido=sim`.

## Resultado normal observado

- tentativa_geracao_xlsx_principal: nao_necessaria
- tentativa_geracao_xlsx_principal_status: nao_executada
- tentativa_geracao_xlsx_fallback: nao_necessaria
- tentativa_geracao_xlsx_fallback_status: nao_executada
- fallback_xlsx_secundario: nao_necessario
- fallback_xlsx_secundario_motivo: xlsx_oficial_ja_existente
- fallback_direto_nucleo_removido: sim
- status_geral_s7i: tabela_operacional_integrada_xlsx
- qtd_linhas_aba_tabela_operacional: 159
- qtd_linhas_csv_s7g: 159
- comparacao_csv_s7g_xlsx: sim
- qtd_linhas_divergentes_csv_xlsx: 0
- qtd_valores_saldo_pos_divergentes_csv_xlsx: 0
- qtd_status_operacional_divergentes_csv_xlsx: 0

## Testes negativos preservados

- teste_negativo_coluna_removida: status_operacional
- teste_negativo_keyerror: nao
- teste_negativo_coluna_ausente_detectada: sim
- teste_negativo_status_controlado: falha_integracao_tabela_operacional_xlsx
- teste_negativo_rowcount_original: 159
- teste_negativo_rowcount_truncado: 158
- teste_negativo_rowcount_detectado: sim
- teste_negativo_rowcount_status_controlado: falha_integracao_tabela_operacional_xlsx

## Regressões

A preencher após execução local:

- S.7-J.1:
- S.7-H:
- S.7-G:
- S.7-F:
- S.7-D:
- Q.0:
- Q.1:
- Q.5:
- Q.5-B/C/D/E:

## Decisão

A preencher após regressões:

- S7I4_CORRECAO_APROVADA: sim
- S7I_AUDITOR_ROBUSTO_FALLBACK: sim
- S7J_AUDITORIA_APROVADA: sim
- USO_OPERACIONAL_TABELA_PAGAMENTOS_VALIDADO: sim
- Q_REABERTA: não
- S7K_LIBERADA: sim