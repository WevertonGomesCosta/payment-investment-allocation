# ME-V17-F0-V36C — Reconcilia rota POS/V3.2 com rota PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: ME-V17-F0-V36C
- VERSAO_CANDIDATA: V17-F0-V.3.6C
- TIPO: DIAGNÓSTICO / RECONCILIAÇÃO DE ROTA
- CLASSE: RECONCILIA_ROTA_POS_V32_COM_PACOTE_ENTRADA_RESOLVIDA
- STATUS: CONCLUÍDA COMO DIAGNÓSTICO DOCUMENTAL
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_RENDERIZACAO: não
- ALTERA_DADOS: não

---

## 2. Objetivo

Reconciliar a divergência entre duas rotas de trabalho recentes:

1. rota POS/V3.2, planejada para corrigir a duplicidade de lotes pós-switching na saída canônica após a V3.1;
2. rota PacoteEntradaResolvida, já avançada no `main` até V17-F0-V.3.6B.

O objetivo desta microetapa é decidir se a correção V3.2:

- já foi absorvida por outra frente;
- deve ser reaplicada sobre o `main` atual;
- ou deve ser retomada em branch separado a partir de `d181370`.

Esta microetapa é estritamente diagnóstica e documental. Não altera código.

---

## 3. Diagnóstico Git remoto

A inspeção foi feita no repositório remoto `WevertonGomesCosta/payment-investment-allocation`.

Não houve acesso ao worktree local `C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation` nesta execução.

Estado remoto observado:

```text
branch: main
HEAD remoto: 8f6b5a3aae1b63100b995f0879a0382e4d2cdc99
commit HEAD: V17-F0-V.3.6B: adiciona auditoria PacoteEntradaResolvida operacional
```

Comparação observada:

```text
base: d181370b9f7cab6c7550a8ffc87cf5b1e4c85914
base_commit: V17-F0-V.3.1: integra switching ao inventario canonico
head: main
status: ahead
ahead_by: 49
behind_by: 0
```

Conclusão: o `main` atual é descendente de `d181370`, mas avançou 49 commits por uma rota distinta, centrada em `PacoteEntradaResolvida`.

---

## 4. Verificação da V3.2 planejada

A V3.2 esperada era:

```text
V17-F0-V.3.2: desativa duplicidade pos canonico
```

Log esperado:

```text
logs/iteracoes/ME-V17-F0-V32_DESATIVA_DUPLICIDADE_POS_CANONICO.md
```

Resultado da verificação remota:

```text
commit V17-F0-V.3.2: desativa duplicidade pos canonico: não localizado
log ME-V17-F0-V32_DESATIVA_DUPLICIDADE_POS_CANONICO.md: não localizado em main
```

Também foi feita busca por `pos_canonico_ativo`, campo de auditoria previsto para a V3.2.

Resultado:

```text
pos_canonico_ativo: não localizado no repositório atual
```

Conclusão: a V3.2 planejada não foi aplicada no `main` atual.

---

## 5. Verificação se a V3.2 foi absorvida por outra frente

Foi inspecionado o estado atual de `nucleo/saida_canonica.py`.

Trecho relevante observado em `construir_saida_canonica(...)`:

```python
destinos_pos_switching_passivos = list(ledger_result.get('destinos_pos_switching_materializados_passivos', []))
vinculos_origem_destino_pos_switching = list(ledger_result.get('vinculos_origem_destino_pos_switching', []))
lotes_ativos, lotes_exauridos = _construir_lotes_situacao(contexto, destinos_pos_switching_passivos)
```

Interpretação:

- a lista `destinos_pos_switching_passivos` ainda é passada diretamente para `_construir_lotes_situacao(...)`;
- não existe lista separada `destinos_pos_switching_passivos_para_situacao`;
- não existe detecção explícita de `POS_CANONICO_ATIVO`;
- não existem os campos de auditoria planejados para a V3.2:
  - `pos_canonico_ativo`;
  - `ponte_passiva_pos_desativada_por_pos_canonico`;
  - `destinos_pos_switching_passivos_para_situacao_total`;
  - `destinos_pos_switching_passivos_preservados_auditoria_total`.

Conclusão: a V3.2 não foi absorvida por outra frente.

---

## 6. Relação com a rota PacoteEntradaResolvida

O `main` atual avançou em uma frente arquitetural diferente, com foco em:

- `PacoteEntradaResolvida`;
- gate da Etapa 2;
- promoção operacional no `ContextoBaseline`;
- auditorias de entrada resolvida;
- scripts diagnósticos correspondentes.

Arquivos relevantes observados no avanço posterior a `d181370` incluem, entre outros:

```text
nucleo/entrada_resolvida.py
nucleo/contexto_baseline.py
nucleo/leitor_planilha.py
nucleo/validacao_pre_execucao.py
nucleo/cache_cdi_bcb.py
scripts/diagnostico/auditar_pacote_entrada_resolvida_operacional_v36b.py
logs/iteracoes/ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md
logs/iteracoes/ME-V17-F0-V32B_FORMALIZA_ETAPA2_VALIDACAO_PACOTE_ENTRADA_RESOLVIDA.md
logs/iteracoes/ME-V17-F0-V32C_FORMALIZA_ETAPA3_CANONIZACAO_OPERACIONAL.md
...
logs/iteracoes/ME-V17-F0-V36A_PROMOVE_PACOTE_ENTRADA_RESOLVIDA_CONTEXTO_BASELINE.md
```

Essa rota não altera diretamente a lógica da ponte passiva POS em `nucleo/saida_canonica.py`.

Conclusão: a frente PacoteEntradaResolvida avançou o macrofluxo de entrada/gate, mas não substituiu a necessidade de correção da duplicidade POS na saída canônica.

---

## 7. Decisão de reconciliação

A decisão desta microetapa é:

```text
REAPLICAR_A_CORRECAO_POS_V32_SOBRE_MAIN_ATUAL
```

Justificativa:

1. A V3.2 planejada não existe no `main` atual.
2. O log obrigatório da V3.2 não existe.
3. A lógica de `nucleo/saida_canonica.py` ainda preserva a ponte antiga diretamente na construção da Situação Atual.
4. A frente PacoteEntradaResolvida não absorveu a correção POS.
5. O `main` atual é descendente de `d181370`, logo não há necessidade técnica imediata de retomar a partir de branch antigo apenas para preservar ancestralidade.
6. Retomar a partir de `d181370` em branch separado criaria risco de divergência com 49 commits já promovidos no `main`.
7. A ação mais segura é uma nova microetapa corretiva, aplicada sobre o `main` atual, com escopo restrito a `nucleo/saida_canonica.py` e novo log.

---

## 8. Condição para próxima microetapa

A próxima microetapa deve ser corretiva, não diagnóstica.

Nome recomendado:

```text
V17-F0-V.3.6D — Reaplica desativação da ponte passiva POS sobre main atual
```

Escopo recomendado:

Alterar somente:

```text
nucleo/saida_canonica.py
logs/iteracoes/ME-V17-F0-V36D_REAPLICA_DESATIVACAO_PONTE_PASSIVA_POS_MAIN_ATUAL.md
```

Não alterar:

```text
nucleo/dados_operacionais_canonicos.py
nucleo/inventario_lotes_expandido_pos_switching.py
nucleo/nucleo_financeiro_minimo.py
nucleo/validacao_pre_execucao.py
nucleo/leitor_planilha.py
nucleo/saida_observavel.py
nucleo/contexto_baseline.py
nucleo/entrada_resolvida.py
aplicacao/principal.py
relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md
relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md
dados/dados_financeiros.xlsx
dados/cache_bcb.json
```

A correção deve preservar a arquitetura da V3.1 e respeitar a frente PacoteEntradaResolvida já promovida.

---

## 9. Regra técnica para a próxima correção

A próxima microetapa deve aplicar a mesma lógica planejada originalmente para a V3.2, mas agora sobre o `main` atual:

1. detectar se o `inventario_canonico` já contém POS canônico:

```text
origem_registro == "lote_pos_switching_normalizado"
```

2. preservar `destinos_pos_switching_passivos` para auditoria;
3. usar lista separada para a Situação Atual:

```python
destinos_pos_switching_passivos_para_situacao = (
    [] if pos_canonico_ativo else destinos_pos_switching_passivos
)
```

4. chamar:

```python
lotes_ativos, lotes_exauridos = _construir_lotes_situacao(
    contexto,
    destinos_pos_switching_passivos_para_situacao,
)
```

5. registrar em auditoria:

```python
auditoria["pos_canonico_ativo"] = bool(pos_canonico_ativo)
auditoria["ponte_passiva_pos_desativada_por_pos_canonico"] = bool(pos_canonico_ativo and len(destinos_pos_switching_passivos) > 0)
auditoria["destinos_pos_switching_passivos_para_situacao_total"] = len(destinos_pos_switching_passivos_para_situacao)
auditoria["destinos_pos_switching_passivos_preservados_auditoria_total"] = len(destinos_pos_switching_passivos)
```

6. manter `_aplicar_consumo_pagamentos_passados_lotes_pos_switching(...)` ativo;
7. não alterar motor, Etapa 3, entrada resolvida, gate, XLSX ou renderização.

---

## 10. Status final

```text
V36C_RECONCILIACAO_ROTA_POS_V32_PACOTE_ENTRADA_RESOLVIDA=concluida
V32_POS_ORIGINAL_EXISTE_NO_MAIN=nao
V32_POS_ABSORVIDA_POR_OUTRA_FRENTE=nao
MAIN_ATUAL_DESCENDENTE_DE_D181370=sim
MAIN_ATUAL_HEAD=8f6b5a3aae1b63100b995f0879a0382e4d2cdc99
ROTA_PACOTE_ENTRADA_RESOLVIDA_PRESERVAR=sim
RECOMENDACAO=REAPLICAR_CORRECAO_POS_SOBRE_MAIN_ATUAL
PROXIMA_MICROETAPA_RECOMENDADA=V17-F0-V.3.6D
ALTEROU_CODIGO=nao
```
