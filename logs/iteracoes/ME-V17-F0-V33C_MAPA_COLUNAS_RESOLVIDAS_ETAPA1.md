# ME-V17-F0-V33C — Explicita MapaColunasResolvidas na Etapa 1

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3C
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / COMPATIBILIDADE
- CLASSE: EXPLICITA_MAPA_COLUNAS_RESOLVIDAS_ETAPA1
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Explicitar a produção de `MapaColunasResolvidas` na Etapa 1, sem alterar a leitura atual da planilha, sem alterar a canonização estrutural já existente e sem modificar o consumo pelas etapas posteriores.

---

## 3. Diagnóstico inicial

A V17-F0-V.3.3B já havia criado `MapaAbasResolvidas` e exposto esse artefato no `PacotePlanilha`.

Antes desta microetapa, a resolução estrutural de colunas ainda ocorria de modo implícito por meio de `canonizar_colunas(...)`, `construir_mapa_alias(...)` e `resolver_coluna(...)`, mas o mapa de campos canônicos para colunas físicas ainda não era retornado como artefato explícito da Etapa 1.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/leitor_planilha.py`;
- `logs/iteracoes/ME-V17-F0-V33C_MAPA_COLUNAS_RESOLVIDAS_ETAPA1.md`.

---

## 5. Conteúdo implementado

### 5.1. Import estrutural

`nucleo/leitor_planilha.py` passa a importar:

```python
from nucleo.entrada_resolvida import MapaAbasResolvidas, MapaColunasResolvidas
```

Esse import é permitido porque pertence à Etapa 1 e não introduz dependência de motor, Etapa 2, Etapa 3, saída ou dados operacionais canônicos.

### 5.2. Campo adicional em PacotePlanilha

Foi adicionado ao dataclass `PacotePlanilha` o campo opcional:

```python
mapa_colunas_resolvidas: Optional[MapaColunasResolvidas] = None
```

A adição é compatível porque o campo tem valor padrão e o retorno de `PacotePlanilha` continua sendo feito por keywords.

### 5.3. Função construir_mapa_colunas_resolvidas(...)

Foi criada a função:

```python
construir_mapa_colunas_resolvidas(
    quadros_brutos,
    mapa_abas_resolvidas,
    config,
) -> MapaColunasResolvidas
```

A função:

- lê `config["colunas"]`;
- usa os blocos presentes em `MapaAbasResolvidas`;
- verifica correspondência entre aliases configurados e colunas físicas encontradas;
- monta `colunas_por_bloco`;
- monta `metadados_por_bloco`;
- registra campos ausentes por bloco;
- registra auditoria estrutural;
- não altera os DataFrames;
- não cria dados operacionais canônicos;
- não executa validação pré-execução.

### 5.4. Integração em carregar_planilha(...)

`carregar_planilha(...)` agora constrói:

```python
mapa_colunas_resolvidas = construir_mapa_colunas_resolvidas(
    quadros_brutos,
    mapa_abas_resolvidas,
    config,
)
```

e retorna esse objeto no `PacotePlanilha`.

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/entrada_resolvida.py`;
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
- cria `PacoteValidacaoPreExecucao`;
- cria `PacoteDadosOperacionaisCanonicos`;
- calcula rendimento;
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
import pandas as pd
from nucleo.leitor_planilha import construir_mapa_abas_resolvidas, construir_mapa_colunas_resolvidas

config = {
    "abas": {"carteira": "Carteira"},
    "colunas": {
        "carteira": {
            "nome": ["Nome", "Produto"],
            "taxa_base": ["Taxa_Base_CDI"],
        }
    },
}
quadros = {"Carteira": pd.DataFrame(columns=["Nome", "Taxa_Base_CDI"])}
mapa_abas = construir_mapa_abas_resolvidas(["Carteira"], config)
mapa_colunas = construir_mapa_colunas_resolvidas(quadros, mapa_abas, config)

assert mapa_colunas.colunas_por_bloco["carteira"]["nome"] == "Nome"
assert mapa_colunas.colunas_por_bloco["carteira"]["taxa_base"] == "Taxa_Base_CDI"
assert mapa_colunas.auditoria["altera_colunas_dataframe"] is False
assert mapa_colunas.auditoria["altera_leitura_planilha"] is False
assert mapa_colunas.auditoria["altera_fluxo_operacional"] is False
print("MAPA_COLUNAS_RESOLVIDAS_UNITARIO_OK")
PY
```

---

## 8. Resultado esperado

A Etapa 1 passa a expor explicitamente `MapaColunasResolvidas` dentro de `PacotePlanilha`, sem alterar comportamento operacional.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3D — Produzir quadros_estruturais_resolvidos`

A próxima etapa deve alinhar o nome conceitual `quadros_estruturais_resolvidos` ao artefato atualmente chamado `quadros_canonicos`, ainda sem alterar Etapa 2, Etapa 3, motor ou saída.
