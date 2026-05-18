# ME-V17-F0-V33D — Produz quadros_estruturais_resolvidos na Etapa 1

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3D
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / COMPATIBILIDADE NOMINAL
- CLASSE: PRODUZ_QUADROS_ESTRUTURAIS_RESOLVIDOS_ETAPA1
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Produzir explicitamente `quadros_estruturais_resolvidos` na Etapa 1, sem remover nem alterar `quadros_canonicos`, preservando compatibilidade com os consumidores atuais.

---

## 3. Diagnóstico inicial

O código atual ainda usa o nome histórico `quadros_canonicos` para os DataFrames da planilha com colunas normalizadas estruturalmente.

Na arquitetura formalizada da Etapa 1, o nome normativo para esse artefato é:

```text
quadros_estruturais_resolvidos
```

Esses quadros ainda não são dados operacionais canônicos da Etapa 3.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/leitor_planilha.py`;
- `logs/iteracoes/ME-V17-F0-V33D_QUADROS_ESTRUTURAIS_RESOLVIDOS_ETAPA1.md`.

---

## 5. Conteúdo implementado

### 5.1. Campo adicional em PacotePlanilha

Foi adicionado ao dataclass `PacotePlanilha` o campo opcional:

```python
quadros_estruturais_resolvidos: Optional[dict[str, pd.DataFrame]] = None
```

A adição é compatível porque o campo tem valor padrão e o retorno de `PacotePlanilha` continua sendo feito por keywords.

### 5.2. Função materializar_quadros_estruturais_resolvidos(...)

Foi criada a função:

```python
materializar_quadros_estruturais_resolvidos(quadros_canonicos) -> dict[str, pd.DataFrame]
```

A função:

- materializa o nome normativo `quadros_estruturais_resolvidos`;
- preserva `quadros_canonicos` como nome legado de compatibilidade;
- não altera DataFrames;
- não faz cópia profunda de dados;
- não cria dados operacionais canônicos;
- não altera Etapa 2 ou Etapa 3.

### 5.3. Integração em carregar_planilha(...)

`carregar_planilha(...)` agora constrói:

```python
quadros_estruturais_resolvidos = materializar_quadros_estruturais_resolvidos(quadros_canonicos)
```

e retorna esse objeto no `PacotePlanilha`.

---

## 6. Limites preservados

Esta microetapa não:

- remove `quadros_canonicos`;
- altera `canonizar_colunas(...)`;
- altera `resolver_coluna(...)`;
- altera `construir_mapa_abas_resolvidas(...)`;
- altera `construir_mapa_colunas_resolvidas(...)`;
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
from nucleo.leitor_planilha import materializar_quadros_estruturais_resolvidos

quadros_canonicos = {"Carteira": pd.DataFrame({"nome": ["A"]})}
quadros = materializar_quadros_estruturais_resolvidos(quadros_canonicos)

assert quadros.keys() == quadros_canonicos.keys()
assert quadros["Carteira"] is quadros_canonicos["Carteira"]
print("QUADROS_ESTRUTURAIS_RESOLVIDOS_UNITARIO_OK")
PY
```

---

## 8. Resultado esperado

A Etapa 1 passa a expor explicitamente `quadros_estruturais_resolvidos` dentro de `PacotePlanilha`, mantendo `quadros_canonicos` para compatibilidade.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3E — Criar JanelaConsultaCDI`

A próxima etapa deve derivar a janela bruta de consulta CDI a partir dos quadros estruturais resolvidos e da data de referência, ainda sem alterar Etapa 2, Etapa 3, motor ou saída.
