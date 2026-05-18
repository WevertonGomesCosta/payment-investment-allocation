# ME-V17-F0-V33K-fix — Corrige import path da auditoria comparativa do contexto shadow

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3K-fix
- TIPO: MICROCORREÇÃO CIRÚRGICA
- CLASSE: CORRIGE_IMPORT_PATH_AUDITORIA_CONTEXTO_SHADOW
- ALTERA CONTEXTO BASELINE: NÃO
- ALTERA ENTRADA RESOLVIDA: NÃO
- ALTERA CACHE CDI/BCB: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Motivo da correção

A validação local da V17-F0-V.3.3K reprovou a execução do script diagnóstico com:

```text
ModuleNotFoundError: No module named 'nucleo'
```

A causa foi a execução do script por caminho:

```bash
python -B scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py
```

Nesse modo, o Python inclui `scripts/diagnostico` no `sys.path`, mas não necessariamente a raiz do repositório, impedindo o import de `nucleo`.

---

## 3. Arquivos alterados

Alterados nesta microcorreção:

- `scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py`;
- `logs/iteracoes/ME-V17-F0-V33K_FIX_IMPORT_PATH_AUDITORIA_CONTEXTO_SHADOW.md`.

---

## 4. Conteúdo corrigido

O script passou a importar `sys` e a inserir a raiz do repositório no `sys.path` antes dos imports de `nucleo`:

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

Os imports de `nucleo.contexto_baseline` e `nucleo.entrada_resolvida` foram mantidos depois dessa configuração.

---

## 5. Limites preservados

Esta microcorreção não:

- altera `nucleo/contexto_baseline.py`;
- altera `nucleo/entrada_resolvida.py`;
- altera `nucleo/leitor_planilha.py`;
- altera `nucleo/cache_cdi_bcb.py`;
- altera `nucleo/validacao_pre_execucao.py`;
- altera `nucleo/dados_operacionais_canonicos.py`;
- altera `nucleo/carteira_canonica.py`;
- altera `nucleo/inventario_lotes_expandido_pos_switching.py`;
- altera `nucleo/nucleo_financeiro_minimo.py`;
- altera `nucleo/saida_canonica.py`;
- altera `nucleo/saida_observavel.py`;
- altera `aplicacao/principal.py`;
- altera contrato mestre;
- altera modelo matemático;
- altera motor;
- altera ledger;
- altera console;
- altera XLSX;
- altera saída oficial;
- altera dados;
- altera cache.

---

## 6. Validação local necessária

Executar novamente a validação da V3.3K, com foco em:

```bash
python -m compileall nucleo scripts/diagnostico
python -B scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py
```

Resultado esperado:

```text
AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW_V33K_OK
VALIDACAO_LOCAL_V33K_OK
```

---

## 7. Próxima etapa

A próxima microetapa só deve avançar após a validação local aprovada desta microcorreção.