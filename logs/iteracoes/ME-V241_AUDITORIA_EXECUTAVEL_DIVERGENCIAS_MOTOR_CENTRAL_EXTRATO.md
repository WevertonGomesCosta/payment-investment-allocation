# ME-V241 — Auditoria executável das divergências motor versus central versus extrato futuro

```text
STATUS_DO_REGISTRO: IMPLEMENTACAO_PARCIAL_COM_LIMITACAO_OPERACIONAL
MICROETAPA: ME-V241
VERSAO_CANDIDATA: V241
BASELINE_DE_ENTRADA: V240
TIPO: DIAGNOSTICO / AUDITORIA EXECUTAVEL CONTROLADA
CLASSE_SEMANTICA: AUDITA_DIVERGENCIAS_SAIDA_PAGAMENTOS_SWITCHING_SEM_ALTERAR_REGRA
```

---

## 1. Estado carregado

```text
BASELINE_DE_ENTRADA: V240
VERSAO_CANDIDATA: V241
FONTE_DE_VERDADE_OPERACIONAL: NAO_CONSOLIDADA
PRECEDENCIA_ENTRE_CAMADAS: NAO_DEFINIDA
ME_V242: NAO_INICIADA
```

A ME-V241 foi aberta para criar e executar um artefato diagnóstico isolado capaz de comparar, pagamento a pagamento, divergências entre:

```text
- quadro_recomendacoes do motor_recomendacao_pagamentos_switching_v1;
- quadro_recomputacao_sequencial_central;
- extrato_futuro da saida_canonica.
```

---

## 2. Arquivos criados/gerados dentro do escopo aprovado

```text
scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv
saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv
logs/iteracoes/ME-V241_AUDITORIA_EXECUTAVEL_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md
```

Nenhum arquivo fora do escopo aprovado foi criado por esta implementação.

---

## 3. Script diagnóstico criado

Arquivo:

```text
scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
```

Função do script:

```text
- carregar o contexto funcional da baseline;
- acessar motor_recomendacao_pagamentos_switching_v1;
- acessar recomputacao_sequencial_central_v1;
- construir extrato_futuro pela saida_canonica existente;
- comparar campos por pagamento_id;
- gerar CSV de resumo;
- gerar CSV de detalhe;
- preservar FONTE_DE_VERDADE_OPERACIONAL = NAO_CONSOLIDADA;
- preservar PRECEDENCIA_ENTRE_CAMADAS = NAO_DEFINIDA;
- não corrigir divergências;
- não alterar módulos produtivos.
```

Comparações implementadas no script:

```text
1. lote_recomendado do motor versus lote_final_central versus Lote sugerido do extrato_futuro.
2. estrategia_recomendada versus Estratégia exibida.
3. cobertura_integral_recomendada versus pagamento_totalmente_coberto_central versus Cobertura integral exibida.
4. saldo_residual_temporal_pos_recomendacao versus saldo_remanescente_central versus Saldo Remanescente exibido.
5. necessidade_switching versus Necessita switching exibido.
6. Identificação de linhas com origem mista.
7. Quantificação de divergências sem correção.
8. Registro de totais e percentuais no CSV de resumo.
9. Registro de detalhe por pagamento no CSV detalhado.
```

---

## 4. Comando autorizado

```bash
python scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
```

---

## 5. Resultado operacional da execução nesta sessão

```text
EXECUCAO_REMOTA_PELO_CORE: NAO_REALIZADA
MOTIVO: o conector GitHub disponível nesta sessão permite leitura/escrita de arquivos, mas não oferece execução remota de processos Python no repositório principal.
EXECUCAO_LOCAL_RECOMENDADA: SIM
EXECUCAO_CI_RECOMENDADA: SIM, se houver runner configurado em microetapa própria ou por ação manual do mantenedor.
```

Declaração de integridade:

```text
O CORE não declara execução que não ocorreu. Os CSVs criados nesta implementação registram explicitamente que a execução quantitativa não foi realizada nesta sessão por limitação operacional do conector GitHub.
```

---

## 6. Conteúdo dos CSVs gerados nesta implementação

### 6.1 Resumo

Arquivo:

```text
saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv
```

Conteúdo gerado:

```text
versao,metrica,valor,percentual_sobre_total,fonte_de_verdade_operacional,precedencia_entre_camadas
V241,status_execucao_core,NAO_EXECUTADO_POR_LIMITACAO_DO_CONECTOR_GITHUB,0.0,NAO_CONSOLIDADA,NAO_DEFINIDA
V241,script_diagnostico_criado,SIM,100.0,NAO_CONSOLIDADA,NAO_DEFINIDA
V241,comando_autorizado,python scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py,0.0,NAO_CONSOLIDADA,NAO_DEFINIDA
V241,total_pagamentos_auditados,NAO_APURADO_SEM_EXECUCAO,0.0,NAO_CONSOLIDADA,NAO_DEFINIDA
V241,divergencias_quantificadas,NAO_APURADO_SEM_EXECUCAO,0.0,NAO_CONSOLIDADA,NAO_DEFINIDA
```

### 6.2 Detalhe

Arquivo:

```text
saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv
```

Conteúdo gerado:

```text
status,erro,traceback,fonte_de_verdade_operacional,precedencia_entre_camadas
NAO_EXECUTADO_POR_LIMITACAO_DO_CONECTOR_GITHUB,Conector GitHub disponível nesta sessão não executa processos remotos; script criado e comando autorizado registrado; execução deve ocorrer em ambiente local ou CI.,,NAO_CONSOLIDADA,NAO_DEFINIDA
```

---

## 7. Travas preservadas

```text
FONTE_DE_VERDADE_OPERACIONAL: NAO_CONSOLIDADA
PRECEDENCIA_ENTRE_CAMADAS: NAO_DEFINIDA
DIVERGENCIA_CORRIGIDA: NAO
REGRA_ECONOMICA_ALTERADA: NAO
CONTRATO_DE_CAMPOS_EM_CODIGO_ALTERADO: NAO
```

---

## 8. Registros de não alteração

```text
CONTRATO_MESTRE: NAO_ALTERADO
MMEF_OFICIAL: NAO_ALTERADO
FRAMEWORK: NAO_ALTERADO
CHECKLIST: NAO_ALTERADO
TEMPLATE: NAO_ALTERADO
PROMPTS: NAO_ALTERADOS
REGISTROS_ANTERIORES: NAO_ALTERADOS
README: NAO_ALTERADO
INDICE_RELATORIOS: NAO_ALTERADO
RELATORIOS_ATUAIS_OU_HISTORICOS: NAO_ALTERADOS
RELEASE_CHECKER: NAO_ALTERADO
RELEASE_CHECKER_EXECUTADO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUTADO: NAO
SCRIPT_PRODUTIVO_EXECUTADO: NAO
SCRIPT_OPERACIONAL_EXECUTADO: NAO
CODIGO_ECONOMICO: NAO_ALTERADO
MOTORES: NAO_ALTERADOS
RECOMPUTACAO_CENTRAL: NAO_ALTERADA
SIMULADOR_CENTRAL: NAO_ALTERADO
SAIDA_CANONICA: NAO_ALTERADA
PLANILHA_OPERACIONAL: NAO_ALTERADA
DADOS_FINANCEIROS: NAO_ALTERADOS
CACHE_BCB_CDI: NAO_ALTERADO
SAIDAS_OFICIAIS_EXISTENTES: NAO_ALTERADAS
PLANILHAS_DE_DADOS: NAO_ALTERADAS
ARQUIVOS_DE_RESULTADO_EXISTENTES_FORA_DOS_CSVS_AUTORIZADOS: NAO_ALTERADOS
SIMULACAO_ECONOMICA_AMPLA_EXECUTADA: NAO
CODEX: NAO_ACIONADO
V184: NAO_USADA_COMO_VERSAO_OFICIAL
ME_V242: NAO_INICIADA
```

---

## 9. Validação de escopo

```text
ESCOPO_AUTORIZADO:
1. scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
2. logs/iteracoes/ME-V241_AUDITORIA_EXECUTAVEL_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md
3. saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv
4. saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv

ESCOPO_CRIADO_GERADO:
1. scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
2. logs/iteracoes/ME-V241_AUDITORIA_EXECUTAVEL_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md
3. saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv
4. saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv

ESCOPO_FORA_DA_LISTA: NAO_IDENTIFICADO
```

---

## 10. Estado final da ME-V241 nesta implementação

```text
SCRIPT_DIAGNOSTICO_CRIADO: SIM
CSV_RESUMO_CRIADO: SIM, COM STATUS_EXPLICITO_DE_EXECUCAO_NAO_REALIZADA
CSV_DETALHE_CRIADO: SIM, COM STATUS_EXPLICITO_DE_EXECUCAO_NAO_REALIZADA
COMANDO_EXECUTADO_PELO_CORE: NAO
MOTIVO_NAO_EXECUCAO: LIMITACAO_DO_CONECTOR_GITHUB
RESULTADO_QUANTITATIVO_REAL: NAO_APURADO
PROMOCAO_V241: NAO_REALIZADA
AUDITORIA_POS_IMPLEMENTACAO_DA_ME_V241: PENDENTE
```

---

## 11. Próxima ação recomendada

```text
ACAO_RECOMENDADA: retornar para auditoria pos-implementacao com ressalva operacional.
MOTIVO: script e arquivos autorizados foram criados, mas a execução quantitativa exigida não pôde ser realizada pelo CORE nesta sessão por limitação objetiva do conector GitHub.
```
