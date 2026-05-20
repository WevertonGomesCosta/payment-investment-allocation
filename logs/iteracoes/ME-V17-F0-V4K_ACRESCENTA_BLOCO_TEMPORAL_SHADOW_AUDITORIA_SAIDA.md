# ME-V17-F0-V4K — Acrescenta bloco shadow temporal à auditoria da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4K
- VERSAO_CANDIDATA: V17-F0-V.4K
- TIPO: EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: ACRESCENTA_BLOCO_TEMPORAL_SHADOW_AUDITORIA_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4K0.1
- BASELINE_COMMIT_ENTRADA: 73f47e747f5caeae9e88dcd9d650699a0ba433e1
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA_EFETIVA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Adicionar bloco opcional de auditoria temporal shadow ao `PacoteSaidaCanonica.auditoria`, preservando integralmente as saídas observáveis.

---

## 3. Decisão de implementação

A integração foi implementada por rota opcional, em novo módulo, sem alterar diretamente o construtor efetivo:

```text
nucleo/saida_canonica.py
```

Motivo:

```text
saida_canonica.py é grande, central e sensível.
O agregador temporal importa funções auxiliares da saída.
Inserir import direto no construtor efetivo aumentaria risco de ciclo/importação circular.
A rota opcional permite validar a integração shadow antes de promoção controlada.
```

---

## 4. Arquivos criados

```text
nucleo/saida_canonica_temporal_shadow_v4k.py
scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py
logs/iteracoes/ME-V17-F0-V4K_ACRESCENTA_BLOCO_TEMPORAL_SHADOW_AUDITORIA_SAIDA.md
```

---

## 5. Implementação

### 5.1. Novo módulo opcional

Foi criado:

```text
nucleo/saida_canonica_temporal_shadow_v4k.py
```

com:

```text
CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K = "temporal_shadow_v4k"
construir_bloco_temporal_shadow_v4k(contexto, saida_base)
construir_saida_canonica_com_temporal_shadow_v4k(contexto, versao="V203")
```

A função opcional:

```text
1. chama construir_saida_canonica(contexto)
2. constrói pacotes temporais agregados shadow
3. monta bloco temporal_shadow_v4k
4. copia a auditoria existente
5. adiciona apenas a chave temporal_shadow_v4k
6. retorna novo PacoteSaidaCanonica via dataclasses.replace(...)
```

Não há mutação in-place do pacote base.

---

## 6. Bloco adicionado

Chave adicionada na auditoria shadow:

```text
temporal_shadow_v4k
```

Conteúdo principal:

```text
ok
versao_microetapa
versao_agregador
modo_shadow
data_referencia
pacote_replay_passado_presente
pacote_ledger_temporal_operacional_presente
pacote_estado_temporal_presente
pacote_auditoria_temporal_presente
validacao_agregador_ok
erros_bloqueantes_agregador_total
extrato_passado_qtd_saida
extrato_passado_qtd_pacote
extrato_passado_identico
extrato_futuro_qtd_saida
extrato_futuro_qtd_pacote
extrato_futuro_identico
lotes_saida_total
estado_lotes_final_qtd_original
estado_lotes_final_qtd_normalizado_base_observavel
lotes_normalizados_identicos
fechamento_atual_qtd_saida
auditoria_temporal_global_ok
fonte_primaria_switching_ledger
usa_planilha_bruta_como_fonte_primaria
usa_retorno_ledger_dict_legado
saida_chama_ledger_diretamente_fluxo_atual
auditoria_existente_preservada
auditoria_acrescida_apenas_bloco_temporal_shadow
sem_alteracao_observavel
```

---

## 7. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py
```

O script compara:

```text
saida_base = construir_saida_canonica(contexto)
saida_shadow = construir_saida_canonica_com_temporal_shadow_v4k(contexto)
```

Valida que a diferença está restrita a:

```text
saida_shadow.auditoria["temporal_shadow_v4k"]
```

---

## 8. Critérios de aprovação

A V4K só deve ser aprovada se:

```text
validacao_v4k_ok=True
bloco_temporal_shadow_presente=True
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
extrato_passado_identico=True
extrato_futuro_identico=True
switchings_identico=True
ranking_amostra_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
recebidos_atuais_identico=True
fechamento_atual_identico=True
resumo_recebidos_identico=True
versao_identica=True
data_referencia_identica=True
bloco_temporal_ok=True
bloco_validacao_agregador_ok=True
bloco_erros_bloqueantes_total=0
bloco_extrato_passado_identico=True
bloco_extrato_futuro_identico=True
bloco_lotes_normalizados_identicos=True
bloco_fonte_primaria_switching_ledger=switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria=False
sem_alteracao_observavel=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 9. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/saida_canonica_temporal_shadow_v4k.py
python -m py_compile scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py
python scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 10. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4K.1 — Registra equivalência runtime do bloco temporal shadow na auditoria da saída
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 11. Próxima etapa após V4K.1

A próxima etapa esperada é:

```text
V17-F0-V.4L — Promove bloco temporal shadow para caminho opcional controlado da saída canônica
```

ou, se a validação mostrar alguma divergência:

```text
V17-F0-V.4K.0a — Corrige integração opcional do bloco temporal shadow
```

---

## 12. Conclusão

A V4K acrescenta a integração shadow temporal por rota opcional e testável, sem alterar o construtor efetivo de `saida_canonica.py`. A saída observável só deve ser considerada preservada após validação runtime local.
