# ME-V17-F0-V4L — Promove bloco temporal shadow para caminho opcional controlado da saída canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4L
- VERSAO_CANDIDATA: V17-F0-V.4L
- TIPO: EXECUTÁVEL / INTEGRAÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL POR PADRÃO
- CLASSE: PROMOVE_BLOCO_TEMPORAL_SHADOW_CAMINHO_OPCIONAL_CONTROLADO_SAIDA_CANONICA
- BASELINE_DE_ENTRADA: V17-F0-V.4K.1
- BASELINE_COMMIT_ENTRADA: 2889e1e4b3c8c6f2471070d76ab72ce4e2f85ac9
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA_PADRAO: não
- ALTERA_SAIDA_OBSERVAVEL_PADRAO: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Expor o bloco temporal shadow por um caminho opcional controlado da saída canônica, mantendo o comportamento padrão da saída inalterado e permitindo ativação explícita por parâmetro.

---

## 3. Decisão de implementação

A V4L não altera `nucleo/saida_canonica.py` diretamente.

Foi criado um módulo de controle:

```text
nucleo/saida_canonica_controlada_v4l.py
```

Motivo:

```text
Preservar o comportamento padrão sem risco de regressão em saida_canonica.py.
Expor a rota temporal shadow por parâmetro explícito.
Permitir validação comparativa antes de qualquer promoção futura dentro do construtor oficial.
```

---

## 4. Arquivos criados

```text
nucleo/saida_canonica_controlada_v4l.py
scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py
logs/iteracoes/ME-V17-F0-V4L_PROMOVE_BLOCO_TEMPORAL_SHADOW_CAMINHO_OPCIONAL_CONTROLADO.md
```

---

## 5. Implementação

### 5.1. Função controlada

Foi criada:

```text
construir_saida_canonica_controlada_v4l(
    contexto,
    *,
    versao="V203",
    incluir_temporal_shadow=False,
)
```

Comportamento:

```text
incluir_temporal_shadow=False -> chama construir_saida_canonica(contexto, versao=versao)
incluir_temporal_shadow=True  -> chama construir_saida_canonica_com_temporal_shadow_v4k(contexto, versao=versao)
```

### 5.2. Garantia de padrão inalterado

A rota padrão da função controlada deve ser idêntica ao construtor oficial atual:

```text
construir_saida_canonica_controlada_v4l(..., incluir_temporal_shadow=False)
==
construir_saida_canonica(...)
```

---

## 6. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py
```

O script compara:

```text
saida_padrao = construir_saida_canonica(contexto)
saida_controlada_desligada = construir_saida_canonica_controlada_v4l(contexto, incluir_temporal_shadow=False)
saida_controlada_ligada = construir_saida_canonica_controlada_v4l(contexto, incluir_temporal_shadow=True)
```

Valida:

```text
saida_padrao_identica=True
saida_com_shadow_temporal_tem_bloco=True
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
extrato_passado_identico=True
extrato_futuro_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
fechamento_atual_identico=True
sem_alteracao_observavel_padrao=True
```

---

## 7. Critérios de aprovação

A V4L só deve ser aprovada se:

```text
validacao_v4l_ok=True
saida_padrao_identica=True
saida_com_shadow_temporal_tem_bloco=True
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
sem_alteracao_observavel_padrao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 8. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/saida_canonica_controlada_v4l.py
python -m py_compile scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py
python scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 9. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4L.1 — Registra equivalência runtime do caminho controlado temporal shadow da saída
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 10. Próxima etapa após V4L.1

A próxima etapa arquitetural recomendada é:

```text
V17-F0-V.4M — Audita elegibilidade para promoção do caminho controlado no construtor oficial da saída
```

Tipo sugerido:

```text
DOCUMENTAL / DIAGNÓSTICO ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Decidir se a assinatura oficial de construir_saida_canonica pode receber parâmetro opcional incluir_temporal_shadow=False sem risco de regressão, ou se a rota controlada deve permanecer externa por mais uma rodada.
```

---

## 11. Conclusão

A V4L promove a integração shadow temporal para um caminho opcional controlado, mantendo o construtor oficial e o comportamento padrão inalterados. A aprovação depende da validação runtime local.
