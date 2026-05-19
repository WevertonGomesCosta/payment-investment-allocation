# ME-V17-F0-V37R — Promove switching_canonico como fonte primária shadow-controlada do ledger

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37R
- VERSAO_CANDIDATA: V17-F0-V.3.7R
- TIPO: EXECUTÁVEL / PROMOÇÃO CONTROLADA / COM FALLBACK LEGADO AUDITÁVEL / SEM ALTERAÇÃO OBSERVÁVEL ESPERADA
- CLASSE: PROMOVE_SWITCHING_CANONICO_LEDGER_FONTE_PRIMARIA_CONTROLADA
- BASELINE_DE_ENTRADA: V17-F0-V.3.7Q.1
- BASELINE_COMMIT_ENTRADA: fc3a181af800395e739b98a3cd214df50b1056bd
- ALTERA_CODIGO: sim
- ALTERA_LEDGER_LEGADO_DIRETAMENTE: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Promover `switching_canonico` como fonte primária controlada do ledger, mantendo o caminho legado da aba bruta `Switching` apenas como fallback/auditoria comparativa.

A promoção é feita sem edição invasiva de `nucleo/ledger_temporal_conjunto.py`.

---

## 3. Estratégia adotada

A V3.7R cria um construtor controlado:

```text
construir_ledger_temporal_conjunto_switching_canonico_v37r(...)
```

Esse construtor executa o ledger legado sob substituição temporária das funções globais usadas para obter mapa/eventos de switching:

```text
_mapa_switchings_aba_operacional
_eventos_switching_aba_operacional
```

Durante a execução controlada, essas funções passam a consultar:

```text
contexto.dados_operacionais.switching_canonico
```

por meio dos adaptadores já validados na V3.7P e conectados ao shadow do ledger na V3.7Q.

Ao final da chamada, as funções originais do ledger são restauradas.

---

## 4. Arquivos criados

```text
nucleo/ledger_temporal_switching_canonico_v37r.py
scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py
logs/iteracoes/ME-V17-F0-V37R_PROMOVE_SWITCHING_CANONICO_LEDGER_FONTE_PRIMARIA_CONTROLADA.md
```

---

## 5. Arquivos deliberadamente não alterados

```text
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
nucleo/saida_canonica_ledger_shadow.py
aplicacao/principal.py
aplicacao/console/principal.py
nucleo/gerar_planilha_operacional.py
dados/cache_bcb.json
```

---

## 6. Módulo de promoção controlada

Arquivo:

```text
nucleo/ledger_temporal_switching_canonico_v37r.py
```

Função principal:

```text
construir_ledger_temporal_conjunto_switching_canonico_v37r(
    quadro_futuro,
    mapa_central,
    contexto,
)
```

Auditoria declarada:

```text
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_disponivel_apenas_para_auditoria=True
promocao_controlada_v37r=True
edita_ledger_legado_diretamente=False
preserva_schema_operacional_legado=True
```

---

## 7. Preservação de schema operacional

Embora a fonte primária seja canônica, o construtor V3.7R preserva o schema operacional esperado pelo ledger:

```text
origem_mapa_migracao=aba_switching_operacional
status_switching=classificado_promovido
status_materializacao_passiva=materializado_passivo
```

Essa decisão é intencional para testar a promoção da fonte de dados sem alterar simultaneamente os rótulos observáveis e a semântica downstream.

---

## 8. Script diagnóstico

Arquivo:

```text
scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py
```

Comando recomendado:

```bash
python scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py --sem-csv
```

Com CSV:

```bash
python scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py
```

CSV esperado:

```text
saidas/diagnostico/auditoria_ledger_switching_canonico_primario_v37r_resumo.csv
```

---

## 9. Critérios avaliados pelo diagnóstico

O script compara:

```text
ledger legado baseado na aba Switching bruta
vs
ledger com switching_canonico como fonte primária controlada
```

Critérios mínimos:

```text
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_disponivel_apenas_para_auditoria=True
eventos_ledger_identicos=True
fifo_identico=True
retorno_ledger_identico=True
extrato_futuro_identico=True
saida_canonica_identica=True
sem_alteracao_observavel=True
```

---

## 10. Condição de parada

A V3.7R não deve ser promovida se qualquer critério abaixo falhar:

```text
eventos_ledger_identicos=False
fifo_identico=False
retorno_ledger_identico=False
extrato_futuro_identico=False
saida_canonica_identica=False
sem_alteracao_observavel=False
```

Se houver divergência, deve-se abrir microcorreção específica, sem editar diretamente o ledger legado, salvo decisão arquitetural explícita em microetapa posterior.

---

## 11. Limitação controlada

A V3.7R ainda não substitui diretamente as chamadas internas do ledger legado. Ela cria um caminho promovido controlado, auditável e reversível.

A alteração direta do ledger legado só deve ocorrer depois da aprovação runtime desta etapa.

---

## 12. Decisão

```text
SWITCHING_CANONICO_PROMOVIDO_COMO_FONTE_PRIMARIA_CONTROLADA=sim
FALLBACK_LEGADO_DISPONIVEL_APENAS_PARA_AUDITORIA=sim
LEDGER_LEGADO_EDITADO_DIRETAMENTE=nao
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
VALIDACAO_RUNTIME=pendente_de_execucao_local
```

---

## 13. Próxima ação

Executar localmente:

```bash
git pull origin main
python scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py --sem-csv
```

Se passar, registrar:

```text
V17-F0-V.3.7R.1 — Registra equivalência runtime da promoção controlada switching_canonico no ledger
```

---

## 14. Conclusão

A V3.7R implementa a promoção controlada de `switching_canonico` como fonte primária do ledger, mas sem edição direta do ledger legado e sem alteração esperada na saída.

A aprovação depende de prova runtime de identidade entre o ledger legado e o ledger executado com fonte primária canônica.
