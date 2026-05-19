# ME-V17-F0-V37C — Diagnostica duplicidade residual de origens migradas em lotes_exauridos

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37C
- VERSAO_CANDIDATA: V17-F0-V.3.7C
- TIPO: DOCUMENTAL / DIAGNÓSTICO / FRONTEIRA DE RESPONSABILIDADE
- CLASSE: DIAGNOSTICA_DUPLICIDADE_RESIDUAL_ORIGENS_MIGRADAS_EXAURIDOS
- BASELINE_DE_ENTRADA: V17-F0-V.3.7B
- ALTERA_CODIGO: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_APLICACAO_PRINCIPAL: não
- ALTERA_DADOS: não

---

## 2. Condição de entrada

A microetapa foi aberta após:

```text
50ddaef — V17-F0-V.3.7B: mapeia fronteira etapa3 replay ledger saida
```

A V3.7B estabeleceu que novas inconsistências patrimoniais devem ser classificadas antes de qualquer correção em `saida_canonica.py`.

---

## 3. Problema diagnosticado

A saída de `python aplicacao/principal.py` mostra duplicidade residual em `lotes_exauridos` para origens migradas por switching.

Os lotes afetados são:

- `Lote 3000 mar. B`;
- `Lote 3000 mar. V`;
- `Lote 8500 mar.`.

Cada um aparece simultaneamente como:

- `exaurido_por_saque`;
- `migrado_por_switching`.

Essa duplicidade é diferente dos problemas já tratados nas V3.6D e V3.6F.

---

## 4. Relação com microetapas anteriores

A V3.6D corrigiu a duplicidade dos destinos POS causada pela ponte passiva.

A V3.6F removeu as origens migradas de `lotes_ativos`.

O problema atual é residual e está restrito ao bloco observável de `lotes_exauridos`.

Classificação:

```text
duplicidade observável/histórica em lotes_exauridos
```

---

## 5. Hipóteses de origem

### Hipótese A — `saida_canonica.py`

A duplicidade pode já existir em `saida.lotes_exauridos`, antes da renderização.

Se confirmada, a correção cirúrgica deve consolidar `lotes_exauridos` em `saida_canonica.py`.

### Hipótese B — `saida_observavel.py`

A duplicidade pode existir apenas na renderização do console/XLSX.

Se confirmada, a correção deve ser em `saida_observavel.py`.

### Hipótese C — replay/ledger

A duplicidade pode nascer como dois eventos temporais independentes.

Se confirmada, a V3.7D não deve corrigir código de saída; deve abrir microetapa própria de replay/ledger.

---

## 6. Regra candidata para correção

Regra a validar na V3.7D:

```text
Se um lote é origem migrada por switching, ele não deve aparecer duas vezes no bloco principal de lotes_exauridos.
```

Preferência operacional:

- preservar status `migrado_por_switching` como encerramento operacional principal;
- preservar valores de saque histórico em auditoria própria, quando existirem;
- não duplicar `Patr. líq.` no bloco principal;
- não alterar destinos POS;
- não alterar lotes ativos;
- não alterar replay/ledger sem diagnóstico específico.

---

## 7. Auditoria obrigatória para V3.7D

A V3.7D deve começar com auditoria executável local para responder:

1. A duplicidade existe em `saida.lotes_exauridos` antes da renderização?
2. A duplicidade existe apenas no console de `aplicacao/principal.py`?
3. A duplicidade aparece também no XLSX?
4. Quais status e valores aparecem por lote?
5. O patrimônio total soma as linhas duplicadas ou usa reconciliação separada?
6. A correção mínima pertence a `saida_canonica.py`, `saida_observavel.py` ou replay/ledger?

---

## 8. Próxima microetapa recomendada

Abrir:

```text
V17-F0-V.3.7D — Corrige duplicidade residual de origens migradas em lotes_exauridos
```

Tipo:

```text
DIAGNÓSTICO EXECUTÁVEL + CORREÇÃO CIRÚRGICA CONDICIONAL
```

Condição:

- corrigir em `saida_canonica.py` se a duplicidade já existir em `saida.lotes_exauridos`;
- corrigir em `saida_observavel.py` se a duplicidade existir apenas na renderização;
- parar e abrir microetapa própria se a duplicidade nascer em replay/ledger.

---

## 9. Conclusão

A V3.7C confirma que existe duplicidade residual de origens migradas em `lotes_exauridos`.

A sequência ajustada passa a ser:

```text
V3.7C — diagnosticar duplicidade residual em lotes_exauridos
V3.7D — corrigir cirurgicamente se a origem for saída canônica/observável
V3.7E — especificar contratos mínimos entre Etapa 3, replay, ledger e saída
```
