# ME-PRE-ETAPA5-03 - Remove artefatos compatitorios transitorios

## 1. Identificacao

- MICROETAPA: ME-PRE-ETAPA5-03
- TIPO: REMOCAO CIRURGICA / HIGIENE ARQUITETURAL / SEM ALTERACAO FUNCIONAL PRETENDIDA
- CLASSE: REMOVE_ARTEFATOS_COMPAT_POS_EQUIVALENCIA
- BASELINE_DE_ENTRADA: 31ff3ac738418b2a8493cd6434c74155d083d2c5
- BRANCH: me-pre-etapa5-03-remove-contexto-compat
- ALTERA_APLICACAO: nao
- ALTERA_DADOS: nao
- ALTERA_SCRIPTS_DIAGNOSTICO: nao
- ALTERA_SAIDAS: nao
- ALTERA_CONTRATO_MESTRE: nao
- ALTERA_MODELO_OFICIAL: nao
- INICIA_ETAPA5_FUNCIONAL: nao

---

## 2. Objetivo

Remover fisicamente, de forma cirurgica, os artefatos compat transitorios associados a `ContextoSaidaCanonicaCompat`, apos a ME-PRE-ETAPA5-01 ter classificado esse contexto como artefato diagnostico concluido e a ME-PRE-ETAPA5-02 ter auditado imports e dependencias reais.

A remocao nao promove a Etapa 5 funcional, nao altera regra economica, nao altera motor, nao altera replay e nao altera saida canonica.

---

## 3. Arquivos removidos

Foram removidos somente:

- `nucleo/contexto_saida_canonica_compat.py`
- `nucleo/comparacao_saida_canonica_compat.py`

---

## 4. Arquivos preservados

Foram preservados:

- logs historicos `ME-RUNTIME-CANON-*`;
- contrato mestre;
- modelo oficial;
- `aplicacao/*`;
- demais arquivos de `nucleo/*`;
- `dados/*`;
- `scripts/diagnostico/*`;
- `saidas/*`.

Logs historicos que mencionam os artefatos compat permanecem como rastreabilidade, nao como dependencia executavel.

---

## 5. Evidencia pre-remocao

A validacao local informada apos merge da ME-PRE-ETAPA5-02 executou:

```bash
git grep -n "ContextoSaidaCanonicaCompat\|contexto_saida_canonica_compat\|comparacao_saida_canonica_compat\|comparar_saida_canonica_baseline_vs_compat\|construir_saida_canonica_via_contexto_compat"
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

O `git grep` mostrou que as unicas ocorrencias em codigo vivo estavam nos dois modulos removidos. As demais ocorrencias estavam em logs historicos e no contrato mestre.

A execucao local informou:

- `py_compile` aprovado;
- `python -B aplicacao/principal.py` aprovado;
- `auditar_nucleo_vivo_v4z.py --sem-arquivos` aprovado;
- `entrada_limpa_etapa5_ok=True`.

---

## 6. Racional tecnico

`nucleo/contexto_saida_canonica_compat.py` era o artefato que definia `ContextoSaidaCanonicaCompat` e helpers associados.

`nucleo/comparacao_saida_canonica_compat.py` era o comparador diagnostico que consumia esse contexto compat para comparar saida baseline versus saida compat em memoria.

Como a ME-PRE-ETAPA5-01 invalidou a promocao do contexto compat como arquitetura viva e a ME-PRE-ETAPA5-02 nao encontrou consumo pela rota oficial, a remocao dos dois modulos reduz ambiguidade antes da Etapa 5.

---

## 7. Validacoes obrigatorias pos-remocao

Antes de merge desta microetapa, executar localmente:

```bash
git grep -n "ContextoSaidaCanonicaCompat\|contexto_saida_canonica_compat\|comparacao_saida_canonica_compat\|comparar_saida_canonica_baseline_vs_compat\|construir_saida_canonica_via_contexto_compat"
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Resultado esperado do `git grep` apos a remocao:

- ocorrencias apenas em logs historicos e contrato mestre;
- nenhuma ocorrencia em `aplicacao/*`;
- nenhuma ocorrencia em modulo vivo de `nucleo/*`.

Resultado esperado das execucoes:

- `py_compile` aprovado;
- `aplicacao/principal.py` aprovado;
- `auditar_nucleo_vivo_v4z.py --sem-arquivos` aprovado;
- `entrada_limpa_etapa5_ok=True`.

---

## 8. Criterio de rejeicao

Rejeitar ou reverter esta microetapa se:

1. qualquer import quebrado aparecer em `aplicacao/*`;
2. qualquer import quebrado aparecer em modulo vivo de `nucleo/*`;
3. `py_compile` falhar;
4. `aplicacao/principal.py` falhar;
5. `auditar_nucleo_vivo_v4z.py --sem-arquivos` falhar;
6. a remocao alterar saida, motor, replay, console, XLSX ou regra economica.

---

## 9. Proxima etapa recomendada

Se a ME-PRE-ETAPA5-03 for validada e mergeada, a proxima microetapa recomendada e preparar a abertura funcional da Etapa 5 apenas apos confirmar que nao restaram pontes compat vivas em `nucleo/*` e que o contrato mestre permanece coerente com `ContextoOperacionalCanonico` como alvo canonico das Etapas 1-4.
