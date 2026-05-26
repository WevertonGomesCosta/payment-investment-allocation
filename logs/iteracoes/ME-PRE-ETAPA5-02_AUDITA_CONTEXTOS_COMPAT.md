# ME-PRE-ETAPA5-02 - Audita dependencias de ContextoSaidaCanonicaCompat

## 1. Identificacao

- MICROETAPA: ME-PRE-ETAPA5-02
- TIPO: DIAGNOSTICO / DOCUMENTAL / SEM REMOCAO DE ARQUIVOS
- CLASSE: AUDITA_IMPORTS_DEPENDENCIAS_CONTEXTO_COMPAT
- BASELINE_DE_ENTRADA: e5175869f9b89027257adbc400b00230b3a256e9
- BRANCH: me-pre-etapa5-02-audita-contexto-compat
- ALTERA_CODIGO: nao
- ALTERA_RUNTIME: nao
- ALTERA_NUCLEO: nao
- REMOVE_ARQUIVOS: nao
- INICIA_ETAPA5_FUNCIONAL: nao

---

## 2. Objetivo

Auditar imports, referencias e dependencias reais associadas a `ContextoSaidaCanonicaCompat` antes de qualquer remocao fisica.

Esta microetapa nao remove arquivos, nao altera runtime, nao altera motor e nao muda regra economica. Ela registra apenas evidencia para decidir se a proxima microetapa podera remover ou arquivar artefatos compat transitorios.

---

## 3. Escopo permitido

Alterar somente este log:

- `logs/iteracoes/ME-PRE-ETAPA5-02_AUDITA_CONTEXTOS_COMPAT.md`

---

## 4. Escopo proibido

Nao alterar:

- `aplicacao/*`
- `nucleo/*`
- `dados/*`
- `scripts/diagnostico/*`
- `saidas/*`
- contrato mestre
- modelo oficial
- motor temporal
- replay
- saida canonica
- console
- XLSX
- regra economica

---

## 5. Artefatos auditados

Busca por `ContextoSaidaCanonicaCompat` identificou ocorrencias em:

- `nucleo/contexto_saida_canonica_compat.py`
- `nucleo/comparacao_saida_canonica_compat.py`
- logs historicos `ME-RUNTIME-CANON-*`

Busca por `contexto_saida_canonica_compat` identificou os mesmos dois modulos vivos em `nucleo/` e logs historicos.

Busca por `from nucleo.contexto_saida_canonica_compat` identificou import vivo apenas em:

- `nucleo/comparacao_saida_canonica_compat.py`

Busca por `from nucleo.comparacao_saida_canonica_compat` nao identificou import em codigo vivo; apareceram apenas logs historicos.

Busca por `comparar_saida_canonica_baseline_vs_compat` e `construir_saida_canonica_via_contexto_compat` identificou definicoes no proprio modulo comparador e referencias em logs historicos, sem evidencia de consumo pela rota oficial.

---

## 6. Leitura tecnica dos modulos compat

### 6.1. `nucleo/contexto_saida_canonica_compat.py`

O modulo define:

- `ComponentesTransicionaisSaidaCanonica`
- `ContextoSaidaCanonicaCompat`
- `construir_contexto_saida_canonica_compat(...)`
- `campos_contexto_saida_canonica_compat()`
- `validar_contexto_saida_canonica_compat(...)`

O proprio modulo declara em metadados que:

- `uso_runtime_principal=False`
- `substitui_contexto_baseline=False`
- `altera_motor=False`
- `altera_replay=False`
- `altera_ledger=False`
- `altera_ranking=False`
- `altera_saida_xlsx=False`

Conclusao: o modulo e artefato compat isolado, sem I/O proprio e sem promocao declarada de runtime.

### 6.2. `nucleo/comparacao_saida_canonica_compat.py`

O modulo comparador importa `ContextoSaidaCanonicaCompat` e constroi duas saidas em memoria:

1. saida via `ContextoBaseline`;
2. saida via contexto compat.

A funcao `comparar_saida_canonica_baseline_vs_compat(...)` retorna divergencias observaveis e declara nos metadados:

- `promove_rota_compat=False`
- `substitui_contexto_baseline=False`
- `altera_runtime_principal=False`
- `altera_xlsx_oficial=False`

Conclusao: o comparador e diagnostico de equivalencia observavel, nao rota oficial de runtime.

---

## 7. Diagnostico de dependencia real

Com base nas buscas realizadas:

- nao ha evidencia de import direto de `ContextoSaidaCanonicaCompat` por `aplicacao/principal.py`;
- nao ha evidencia de import direto de `ContextoSaidaCanonicaCompat` por console;
- nao ha evidencia de import direto de `ContextoSaidaCanonicaCompat` pela rota oficial de execucao;
- `nucleo/comparacao_saida_canonica_compat.py` e o unico consumidor vivo identificado de `nucleo/contexto_saida_canonica_compat.py`;
- o comparador nao foi identificado como dependencia importada por codigo vivo, aparecendo apenas como definicao e em logs historicos;
- os logs `ME-RUNTIME-CANON-*` sao historicos e nao constituem dependencia executavel.

---

## 8. Decisao da microetapa

`ContextoSaidaCanonicaCompat` e `comparacao_saida_canonica_compat` permanecem classificados como artefatos compat transitorios pos-equivalencia.

A ME-PRE-ETAPA5-02 nao remove arquivos. Ela apenas registra que a evidencia disponivel indica ausencia de consumo pela rota oficial e sugere remocao controlada em microetapa posterior, desde que uma validacao local por busca textual e execucao confirme o mesmo resultado.

---

## 9. Validacoes recomendadas antes da proxima remocao

Antes de remover fisicamente qualquer artefato compat, executar localmente:

```bash
git grep -n "ContextoSaidaCanonicaCompat\|contexto_saida_canonica_compat\|comparacao_saida_canonica_compat\|comparar_saida_canonica_baseline_vs_compat\|construir_saida_canonica_via_contexto_compat"
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

A remocao fisica so deve ocorrer se:

1. nao houver import pela rota oficial;
2. nao houver import por `aplicacao/*`;
3. nao houver import por console;
4. os unicos consumidores forem diagnosticos ou logs historicos;
5. a execucao principal e o gate V4Z permanecerem aprovados apos a remocao.

---

## 10. Proxima etapa recomendada

ME-PRE-ETAPA5-03 - remover fisicamente, de forma cirurgica e com validacao local, `nucleo/contexto_saida_canonica_compat.py` e `nucleo/comparacao_saida_canonica_compat.py`, se `git grep` confirmar ausencia de consumo pela rota oficial.

A ME-PRE-ETAPA5-03 deve manter logs historicos intactos e nao iniciar a Etapa 5 funcional.
