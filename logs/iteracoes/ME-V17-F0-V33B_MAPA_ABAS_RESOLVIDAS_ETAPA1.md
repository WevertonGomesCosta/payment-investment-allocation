# ME-V17-F0-V33B — Explicita MapaAbasResolvidas na Etapa 1

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3B
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / COMPATIBILIDADE
- CLASSE: EXPLICITA_MAPA_ABAS_RESOLVIDAS_ETAPA1
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Explicitar a produção de `MapaAbasResolvidas` na Etapa 1, sem alterar a leitura atual da planilha, sem alterar a canonização estrutural de colunas e sem modificar o consumo pelas etapas posteriores.

---

## 3. Diagnóstico inicial

O módulo `nucleo/leitor_planilha.py` já concentrava a leitura física da planilha e o retorno de `PacotePlanilha`.

Antes desta microetapa, o pacote retornava:

- caminho da planilha;
- nomes das abas;
- quadros brutos;
- quadros canonizados estruturalmente;
- auditoria;
- validação.

A correspondência entre bloco canônico e aba física era usada implicitamente a partir de `config["abas"]`, mas ainda não era exposta como artefato formal da Etapa 1.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/leitor_planilha.py`;
- `logs/iteracoes/ME-V17-F0-V33B_MAPA_ABAS_RESOLVIDAS_ETAPA1.md`.

---

## 5. Conteúdo implementado

### 5.1. Import estrutural

`nucleo/leitor_planilha.py` passa a importar:

```python
from nucleo.entrada_resolvida import MapaAbasResolvidas
```

Esse import é permitido porque pertence à Etapa 1 e não introduz dependência de motor, Etapa 2, Etapa 3, saída ou dados operacionais canônicos.

### 5.2. Campo adicional em PacotePlanilha

Foi adicionado ao dataclass `PacotePlanilha` o campo opcional:

```python
mapa_abas_resolvidas: Optional[MapaAbasResolvidas] = None
```

A adição é compatível porque o campo tem valor padrão e o retorno de `PacotePlanilha` continua sendo feito por keywords.

### 5.3. Função construir_mapa_abas_resolvidas(...)

Foi criada a função:

```python
construir_mapa_abas_resolvidas(nomes_abas, config) -> MapaAbasResolvidas
```

A função:

- lê `config["abas"]`;
- verifica correspondência exata entre aba configurada e abas presentes na planilha;
- monta `abas_por_bloco`;
- monta `metadados_por_bloco`;
- registra auditoria estrutural;
- não altera leitura da planilha;
- não resolve aliases de colunas;
- não cria dados operacionais canônicos.

### 5.4. Integração em carregar_planilha(...)

`carregar_planilha(...)` agora constrói:

```python
mapa_abas_resolvidas = construir_mapa_abas_resolvidas(excel.sheet_names, config)
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
from pathlib import Path
from nucleo.carregador_config import carregar_config, resolver_caminho_config
from nucleo.leitor_planilha import carregar_planilha, construir_mapa_abas_resolvidas

config = carregar_config(resolver_caminho_config())
pacote = carregar_planilha(config, raiz_repositorio=Path.cwd())

assert pacote.mapa_abas_resolvidas is not None
print(pacote.mapa_abas_resolvidas.abas_por_bloco)
print(pacote.mapa_abas_resolvidas.auditoria)
print('MAPA_ABAS_RESOLVIDAS_OK')
PY
```

---

## 8. Resultado esperado

A Etapa 1 passa a expor explicitamente `MapaAbasResolvidas` dentro de `PacotePlanilha`, sem alterar comportamento operacional.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3C — Explicitar MapaColunasResolvidas na Etapa 1`

A próxima etapa deve produzir explicitamente o mapa de colunas resolvidas, ainda sem alterar Etapa 2, Etapa 3, motor ou saída.
