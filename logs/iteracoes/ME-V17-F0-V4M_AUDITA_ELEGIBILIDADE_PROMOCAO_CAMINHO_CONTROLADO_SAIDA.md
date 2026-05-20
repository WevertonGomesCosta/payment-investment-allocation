# ME-V17-F0-V4M — Audita elegibilidade para promoção do caminho controlado no construtor oficial da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4M
- VERSAO_CANDIDATA: V17-F0-V.4M
- TIPO: DOCUMENTAL / DIAGNÓSTICO ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_ELEGIBILIDADE_PROMOCAO_CAMINHO_CONTROLADO_CONSTRUTOR_OFICIAL_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4L.1
- BASELINE_COMMIT_ENTRADA: b8731ec3bea9a4fe6b30d8181b267f6e54d3555d
- ALTERA_CODIGO: não
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

Decidir se a assinatura oficial de `construir_saida_canonica(...)` pode receber um parâmetro opcional `incluir_temporal_shadow=False` sem risco de regressão, ou se a rota controlada deve permanecer externa por mais uma rodada.

---

## 3. Condição de entrada

A V4L.1 validou o caminho controlado temporal shadow com:

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
principal_py_executou_sem_erro=True
worktree_limpa=True
```

---

## 4. Arquivos inspecionados

Foram inspecionados, sem alteração:

```text
nucleo/saida_canonica.py
nucleo/saida_canonica_controlada_v4l.py
logs/iteracoes/ME-V17-F0-V4L1_REGISTRA_EQUIVALENCIA_RUNTIME_CAMINHO_CONTROLADO_TEMPORAL_SHADOW_SAIDA.md
```

---

## 5. Estado atual da saída oficial

A função oficial continua com assinatura:

```text
construir_saida_canonica(contexto: Any, *, versao: str = 'V203') -> PacoteSaidaCanonica
```

Ela ainda concentra em um único fluxo:

```text
1. construção do extrato passado
2. construção do extrato futuro
3. construção de switchings
4. ranking de carteira
5. chamada direta ao ledger temporal conjunto
6. montagem de lotes ativos/exauridos
7. neutralização de origens migradas
8. fechamento atual
9. resumo de recebidos
10. montagem da auditoria da saída
```

Esse acoplamento torna a função central e sensível para alterações diretas.

---

## 6. Estado atual do caminho controlado

A V4L criou:

```text
nucleo/saida_canonica_controlada_v4l.py
```

com:

```text
construir_saida_canonica_controlada_v4l(
    contexto,
    *,
    versao="V203",
    incluir_temporal_shadow=False,
)
```

Comportamento validado:

```text
incluir_temporal_shadow=False -> saída padrão idêntica
incluir_temporal_shadow=True  -> saída com bloco temporal_shadow_v4k na auditoria
```

---

## 7. Critérios de elegibilidade

### 7.1. Critério 1 — comportamento padrão preservado

Resultado V4L.1:

```text
saida_padrao_identica=True
sem_alteracao_observavel_padrao=True
```

Status:

```text
APROVADO
```

---

### 7.2. Critério 2 — bloco shadow isolado

Resultado V4L.1:

```text
saida_com_shadow_temporal_tem_bloco=True
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
```

Status:

```text
APROVADO
```

---

### 7.3. Critério 3 — blocos observáveis preservados

Resultado V4L.1:

```text
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
```

Status:

```text
APROVADO
```

---

### 7.4. Critério 4 — conteúdo temporal validado

Resultado V4L.1:

```text
bloco_temporal_ok=True
bloco_validacao_agregador_ok=True
bloco_erros_bloqueantes_total=0
bloco_extrato_passado_identico=True
bloco_extrato_futuro_identico=True
bloco_lotes_normalizados_identicos=True
bloco_fonte_primaria_switching_ledger=switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria=False
```

Status:

```text
APROVADO
```

---

### 7.5. Critério 5 — risco de alteração direta do construtor oficial

Fatores de risco:

```text
saida_canonica.py é arquivo central e extenso
construir_saida_canonica ainda chama ledger diretamente
construir_saida_canonica ainda reconstrói estado observável
construir_saida_canonica ainda agrega auditorias temporais e observáveis
pacotes temporais ainda são shadow
```

Status:

```text
RISCO_MODERADO
```

---

## 8. Decisão arquitetural

A promoção é tecnicamente elegível, mas deve ser feita em microetapa executável própria e mínima.

Decisão:

```text
ELEGIVEL_PARA_ASSINATURA_OFICIAL=sim
PROMOVER_NA_V4M=nao
MANTER_V4M_DOCUMENTAL=sim
PROXIMA_ETAPA_EXECUTAVEL_MINIMA=sim
```

Motivo:

```text
A V4L já provou que o comportamento padrão é idêntico e que o bloco temporal é isolado.
Porém, alterar a assinatura oficial de construir_saida_canonica deve ser uma etapa executável própria, com auditoria runtime imediatamente associada.
```

---

## 9. Promoção recomendada

A próxima etapa deve alterar apenas `nucleo/saida_canonica.py`, com a menor alteração possível:

```text
construir_saida_canonica(
    contexto: Any,
    *,
    versao: str = 'V203',
    incluir_temporal_shadow: bool = False,
) -> PacoteSaidaCanonica
```

Comportamento esperado:

```text
incluir_temporal_shadow=False
    -> comportamento atual idêntico

incluir_temporal_shadow=True
    -> acrescenta apenas auditoria['temporal_shadow_v4k']
```

---

## 10. Restrições para a próxima etapa executável

Escopo permitido:

```text
nucleo/saida_canonica.py
scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py
logs/iteracoes/ME-V17-F0-V4N_PROMOVE_PARAMETRO_TEMPORAL_SHADOW_CONSTRUTOR_OFICIAL_SAIDA.md
```

Escopo proibido:

```text
alterar replay
alterar ledger
alterar PacoteEstadoTemporal
alterar PacoteAuditoriaTemporal
alterar console
alterar XLSX
alterar dados
alterar cache
alterar comportamento padrão da saída
```

---

## 11. Risco principal da próxima etapa

A próxima etapa pode introduzir dependência circular se `saida_canonica.py` importar diretamente módulos que importam a própria saída.

Mitigação obrigatória:

```text
usar import local dentro do ramo incluir_temporal_shadow=True
ou criar helper local sem import top-level
não importar pacotes_temporais_agregados_saida no topo de saida_canonica.py
```

---

## 12. Critérios mínimos da próxima etapa executável

A próxima etapa só deve ser aprovada se:

```text
saida_padrao_identica=True
saida_parametro_false_identica=True
saida_parametro_true_tem_bloco=True
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
console_xlsx_identicos=True
sem_alteracao_observavel_padrao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 13. Decisão sobre manter rota controlada externa

A rota externa `construir_saida_canonica_controlada_v4l(...)` deve ser preservada temporariamente mesmo após a promoção do parâmetro oficial.

Motivo:

```text
Ela fornece comparação independente entre wrapper controlado e assinatura oficial promovida.
Só deve ser removida ou depreciada depois de uma etapa posterior confirmar redundância segura.
```

---

## 14. Decisão final

```text
V4M_STATUS=AUDITORIA_ARQUITETURAL_CONCLUIDA
PROMOCAO_OFICIAL_ELEGIVEL=sim
PROMOCAO_OFICIAL_IMEDIATA_NA_V4M=nao
MANTER_ROTA_CONTROLADA_EXTERNA=sim
PROXIMA_MICROETAPA=V17-F0-V.4N
```

---

## 15. Próxima microetapa recomendada

```text
V17-F0-V.4N — Promove parâmetro opcional temporal shadow no construtor oficial da saída
```

Tipo sugerido:

```text
EXECUTÁVEL / INTEGRAÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL POR PADRÃO
```

Objetivo:

```text
Adicionar incluir_temporal_shadow=False à assinatura oficial de construir_saida_canonica, preservando comportamento padrão e permitindo ativação explícita do bloco temporal shadow.
```

---

## 16. Conclusão

A V4M conclui que a promoção do caminho controlado para a assinatura oficial é tecnicamente elegível, mas não deve ser feita dentro da própria V4M. A próxima etapa deve ser uma microetapa executável mínima, focada apenas na assinatura oficial e acompanhada de diagnóstico runtime específico.
