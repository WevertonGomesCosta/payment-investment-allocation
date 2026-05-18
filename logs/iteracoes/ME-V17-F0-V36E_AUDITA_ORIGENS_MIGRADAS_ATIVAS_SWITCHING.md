# ME-V17-F0-V36E — Audita origens migradas ainda ativas

## 1. Identificacao

- MICROETAPA: ME-V17-F0-V36E
- VERSAO_CANDIDATA: V17-F0-V.3.6E
- TIPO: DIAGNOSTICO / AUDITORIA / SWITCHING
- CLASSE: AUDITA_ORIGENS_MIGRADAS_AINDA_ATIVAS
- STATUS: BLOQUEADA COMO DIAGNOSTICO DE CONSISTENCIA
- ALTERA_CODIGO: nao
- ALTERA_ETAPA_3: nao
- ALTERA_MOTOR: nao
- ALTERA_SAIDA_CANONICA: nao
- ALTERA_RENDERIZACAO: nao
- ALTERA_DADOS: nao

---

## 2. Condicao de entrada

A microetapa foi executada apos a V17-F0-V.3.6D.

Commit de entrada esperado:

- V17-F0-V.3.6D: desativa ponte passiva pos no main atual

A V3.6D corrigiu a duplicidade dos destinos POS na Situacao Atual ao desativar a ponte passiva POS quando os POS ja existem no inventario_canonico.

---

## 3. Objetivo

Auditar se as origens migradas por switching continuam aparecendo como ativos comuns apos a V3.6D.

Lotes de origem sob auditoria:

- Lote 3000 mar. B
- Lote 3000 mar. V
- Lote 8500 mar.

A V3.6E e estritamente diagnostica. Nenhum codigo foi alterado.

---

## 4. Resultado das validacoes

Validacoes executadas antes da geracao do log:

- python -m py_compile nucleo/saida_canonica.py: OK
- python -B aplicacao/principal.py: OK
- auditoria direcionada de origens migradas: executada
- auditoria do XLSX: executada
- arquivo XLSX auditado: saidas/oficial/relatorio_operacional_v225.xlsx

---

## 5. Estado da V3.6D preservado

A auditoria confirmou que os campos da V3.6D foram preservados:

- pos_canonico_ativo = True
- ponte_passiva_pos_desativada_por_pos_canonico = True
- destinos_pos_switching_passivos_para_situacao_total = 0
- destinos_pos_switching_passivos_preservados_auditoria_total = 4

Interpretacao:

- a ponte passiva POS foi corretamente desativada para a Situacao Atual;
- os destinos POS nao estao duplicados pela ponte passiva;
- a V3.6D nao deve ser reaberta nesta etapa.

---

## 6. Diagnostico corrigido da V3.6E

O diagnostico automatico inicial classificou incorretamente:

- DIAGNOSTICO=ORIGENS_MIGRADAS_NAO_APARECEM_COMO_ATIVOS_COMUNS

Essa conclusao foi considerada incorreta porque o criterio usado no script era restrito demais:

- risco_dupla_contagem = bool(em_ativos and em_exauridos)

O criterio correto para esta auditoria e:

- origem migrada aparece na auditoria de switching; e
- a mesma origem continua aparecendo em lotes_ativos.

Portanto, a origem nao precisa aparecer simultaneamente em lotes_exauridos para caracterizar o problema. Basta estar registrada como origem migrada e continuar carregando patrimonio em lotes_ativos.

---

## 7. Tabela das origens migradas

| lote_origem | aparece_em_auditoria_origens_migradas | aparece_em_lotes_ativos | patrimonio_liquido_ativo | diagnostico |
|---|---:|---:|---:|---|
| Lote 3000 mar. B | sim | 1 | 3149.58 | origem migrada ainda ativa |
| Lote 3000 mar. V | sim | 1 | 3152.71 | origem migrada ainda ativa |
| Lote 8500 mar. | sim | 1 | 3203.32 | origem migrada ainda ativa |

Conclusao: as tres origens migradas continuam aparecendo como ativos comuns.

---

## 8. Tabela dos destinos POS

| lote_destino_pos | aparece_em_lotes_ativos | aparece_em_lotes_exauridos | patrimonio_liquido | duplicado | diagnostico |
|---|---:|---:|---:|---:|---|
| Lote 3120 mai | 1 | 0 | 2823.62 | nao | OK |
| Lote 3000 mai Neon | 1 | 0 | 3126.69 | nao | OK |
| Lote 3000 mai Genial | 1 | 0 | 3008.78 | nao | OK |
| Lote 190 mai | 0 | 1 | 0.00 | nao | OK |

Conclusao: os destinos POS permanecem coerentes depois da V3.6D.

---

## 9. Diagnostico sobre risco de dupla contribuicao patrimonial

Ha risco de dupla contribuicao patrimonial porque:

1. os destinos POS existem corretamente como lotes pos-switching;
2. as origens migradas continuam aparecendo como ativos comuns;
3. essas origens carregam patrimonio liquido ativo;
4. o patrimonio total pode estar somando simultaneamente origem remanescente e destino pos-switching.

Esse problema nao e a duplicidade da ponte passiva POS corrigida pela V3.6D.

O problema remanescente esta associado a neutralizacao das origens migradas no estado temporal/replay ou na montagem da Situacao Atual.

---

## 10. Diagnostico sobre XLSX

O XLSX auditado foi:

- saidas/oficial/relatorio_operacional_v225.xlsx

A auditoria local encontrou ocorrencias dos alvos em abas como:

- Extrato Passado
- Extrato Futuro
- Switching
- Situacao Atual
- Saida Canonica
- Fontes Pagamento
- Multifonte Resgates
- Auditoria Fontes

Conclusao: o problema nao fica restrito ao console. A representacao observavel tambem deve ser considerada na proxima correcao.

---

## 11. Conclusao da V3.6E

STATUS:

- V3.6E bloqueada como diagnostico de consistencia.

Conclusao operacional:

- as tres origens migradas continuam em lotes_ativos;
- ha risco de dupla contribuicao patrimonial;
- a V3.6D permanece valida e nao deve ser reaberta;
- a proxima microetapa deve ser corretiva;
- nenhuma correcao foi executada nesta etapa.

Diagnostico final:

- DIAGNOSTICO=ORIGENS_MIGRADAS_CONTINUAM_COMO_ATIVOS_COMUNS
- V36E_REQUER_V36F_CORRETIVA=sim

---

## 12. Proxima microetapa recomendada

Abrir:

- V17-F0-V.3.6F — Corrige neutralizacao de origens migradas por switching ainda ativas

Diretriz inicial:

- investigar e corrigir o ponto correto entre replay/estado temporal e montagem da Situacao Atual;
- nao mexer novamente na ponte passiva POS ja corrigida pela V3.6D;
- preservar os destinos POS canonicos;
- preservar PacoteEntradaResolvida, gate, Etapa 3 e contrato;
- validar impacto no patrimonio liquido total, console e XLSX.

