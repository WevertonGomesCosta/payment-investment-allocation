# ME-V17-F0-V33E-fix — Corrige parsing de datas da JanelaConsultaCDI

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3E-fix
- TIPO: MICROCORREÇÃO CIRÚRGICA
- CLASSE: CORRIGE_PARSING_DATAS_JANELA_CDI
- ALTERA CACHE CDI/BCB: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Motivo da correção

A validação local da V17-F0-V.3.3E reprovou o teste unitário da janela CDI porque a string ISO `2026-01-10` foi interpretada como `2026-10-01`.

A causa foi o uso de parsing com `dayfirst=True` sem tratar previamente o formato ISO `YYYY-MM-DD`.

---

## 3. Arquivos alterados

Alterados nesta microcorreção:

- `nucleo/leitor_planilha.py`;
- `logs/iteracoes/ME-V17-F0-V33E_FIX_PARSING_DATAS_JANELA_CDI.md`.

---

## 4. Conteúdo corrigido

### 4.1. Detecção explícita de ISO

Foi criada a função interna:

```python
_string_iso_yyyy_mm_dd(valor: str) -> bool
```

Ela identifica strings no formato `YYYY-MM-DD` antes do parsing com `dayfirst=True`.

### 4.2. Correção de `_normalizar_data_para_janela_cdi(...)`

A função agora:

- retorna diretamente objetos `date`;
- ignora nulos;
- detecta strings ISO `YYYY-MM-DD` e usa `format="%Y-%m-%d"`;
- preserva suporte a datas brasileiras via `dayfirst=True` para demais strings;
- mantém fallback para objetos de data/datetime/pandas.

### 4.3. Correção do parsing em colunas

O parsing vetorizado:

```python
pd.to_datetime(..., dayfirst=True)
```

foi substituído por normalização escalar usando `_normalizar_data_para_janela_cdi(...)` para cada valor da coluna.

---

## 5. Limites preservados

Esta microcorreção não:

- altera `nucleo/cache_cdi_bcb.py`;
- consulta BCB;
- carrega cache CDI;
- calcula rendimento;
- altera Etapa 2;
- altera Etapa 3;
- altera motor;
- altera ledger;
- altera console;
- altera XLSX;
- altera saída canônica;
- altera contrato mestre;
- altera modelo matemático.

---

## 6. Validação necessária local

Executar a validação da V3.3E novamente, com teste unitário cobrindo:

- ISO `2026-01-10`;
- brasileiro `10/01/2026`;
- data de referência `2026-05-18`;
- flags `altera_cache_cdi=False`, `altera_rendimento=False`, `altera_fluxo_operacional=False`.

Resultado esperado:

```text
VALIDACAO_LOCAL_V33E_FIX_OK
```

---

## 7. Condição para avançar

A V17-F0-V.3.3F só deve ser iniciada após validação local aprovada desta microcorreção.
