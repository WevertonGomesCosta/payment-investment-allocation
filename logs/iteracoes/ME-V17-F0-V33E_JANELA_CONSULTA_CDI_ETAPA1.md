# ME-V17-F0-V33E — Cria JanelaConsultaCDI na Etapa 1

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3E
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / DIAGNÓSTICA
- CLASSE: CRIA_JANELA_CONSULTA_CDI_ETAPA1
- ALTERA CACHE CDI/BCB: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Criar explicitamente `JanelaConsultaCDI` na Etapa 1, derivada das datas interpretáveis presentes nos quadros estruturais resolvidos e, quando informado, da data de referência.

---

## 3. Diagnóstico inicial

A Etapa 1 já expunha:

- `MapaAbasResolvidas`;
- `MapaColunasResolvidas`;
- `quadros_estruturais_resolvidos`.

A janela bruta de consulta CDI ainda não estava materializada como artefato formal retornado por `PacotePlanilha`.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/leitor_planilha.py`;
- `logs/iteracoes/ME-V17-F0-V33E_JANELA_CONSULTA_CDI_ETAPA1.md`.

---

## 5. Conteúdo implementado

### 5.1. Import estrutural

`nucleo/leitor_planilha.py` passa a importar:

```python
from nucleo.entrada_resolvida import JanelaConsultaCDI, MapaAbasResolvidas, MapaColunasResolvidas
```

### 5.2. Campo adicional em PacotePlanilha

Foi adicionado ao dataclass `PacotePlanilha` o campo opcional:

```python
janela_consulta_cdi: Optional[JanelaConsultaCDI] = None
```

### 5.3. Função construir_janela_consulta_cdi(...)

Foi criada a função:

```python
construir_janela_consulta_cdi(
    quadros_estruturais_resolvidos,
    mapa_abas_resolvidas,
    mapa_colunas_resolvidas,
    *,
    data_referencia=None,
) -> JanelaConsultaCDI
```

A função:

- identifica campos resolvidos cujo nome estrutural contém `data` ou `vencimento`;
- tenta interpretar valores como datas;
- inclui `data_referencia` quando fornecida;
- define `data_inicial_consulta` e `data_final_consulta`;
- registra metadados de auditoria;
- não consulta BCB;
- não carrega cache;
- não calcula rendimento;
- não altera DataFrames.

### 5.4. Integração em carregar_planilha(...)

`carregar_planilha(...)` passa a aceitar argumento opcional:

```python
data_referencia: Optional[date] = None
```

A compatibilidade é preservada porque o argumento tem valor padrão.

A função agora constrói:

```python
janela_consulta_cdi = construir_janela_consulta_cdi(
    quadros_estruturais_resolvidos,
    mapa_abas_resolvidas,
    mapa_colunas_resolvidas,
    data_referencia=data_referencia,
)
```

e retorna esse objeto no `PacotePlanilha`.

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/cache_cdi_bcb.py`;
- consulta BCB;
- carrega cache CDI;
- calcula rendimento;
- altera `canonizar_colunas(...)`;
- altera `resolver_coluna(...)`;
- altera `construir_mapa_abas_resolvidas(...)`;
- altera `construir_mapa_colunas_resolvidas(...)`;
- altera `nucleo/entrada_resolvida.py`;
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
- cria `PacoteValidacaoPreExecucao`;
- cria `PacoteDadosOperacionaisCanonicos`;
- executa replay;
- decide pagamentos;
- decide switching;
- cria inventário canônico.

---

## 7. Validação necessária local

Após pull local, executar:

```bash
python -m compileall nucleo
python - <<'PY'
from datetime import date
import pandas as pd
from nucleo.leitor_planilha import (
    construir_janela_consulta_cdi,
    construir_mapa_abas_resolvidas,
    construir_mapa_colunas_resolvidas,
)

config = {
    "abas": {"lotes": "Inventário de Lotes"},
    "colunas": {"lotes": {"data_aplicacao": ["Data Aplicação"], "vencimento": ["Vencimento"]}},
}
quadros = {"Inventário de Lotes": pd.DataFrame({"Data Aplicação": ["2026-01-10"], "Vencimento": ["2026-12-31"]})}
mapa_abas = construir_mapa_abas_resolvidas(["Inventário de Lotes"], config)
mapa_colunas = construir_mapa_colunas_resolvidas(quadros, mapa_abas, config)
janela = construir_janela_consulta_cdi(quadros, mapa_abas, mapa_colunas, data_referencia=date(2026, 5, 18))

assert janela.data_inicial_consulta == date(2026, 1, 10)
assert janela.data_final_consulta == date(2026, 12, 31)
assert janela.metadados["altera_cache_cdi"] is False
assert janela.metadados["altera_rendimento"] is False
assert janela.metadados["altera_fluxo_operacional"] is False
print("JANELA_CONSULTA_CDI_UNITARIO_OK")
PY
```

---

## 8. Resultado esperado

A Etapa 1 passa a expor explicitamente `JanelaConsultaCDI` dentro de `PacotePlanilha`, sem alterar cache CDI, rendimento, motor ou saída.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3F — Desacoplar cache CDI por janela`

A próxima etapa deve usar `JanelaConsultaCDI` como entrada estrutural para preparar a chamada ao cache CDI, ainda sem alterar motor, rendimento ou saída.
