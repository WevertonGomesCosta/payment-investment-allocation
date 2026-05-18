# ME-V17-F0-V33F — Desacopla cache CDI por janela

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3F
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / COMPATIBILIDADE
- CLASSE: DESACOPLA_CACHE_CDI_POR_JANELA
- ALTERA MOTOR: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Permitir que o cache CDI use a `JanelaConsultaCDI` produzida pela Etapa 1 como fonte opcional da janela de consulta, preservando o comportamento legado quando a janela não for informada ou estiver incompleta.

---

## 3. Diagnóstico inicial

Antes desta microetapa, `carregar_cache_cdi_diario(...)` calculava internamente a janela de consulta a partir de `dados_operacionais` por meio de `_datas_relevantes(...)`.

Após a V17-F0-V.3.3E e a microcorreção V17-F0-V.3.3E-fix, a Etapa 1 passou a expor `JanelaConsultaCDI` com datas de início e fim já resolvidas estruturalmente.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/cache_cdi_bcb.py`;
- `logs/iteracoes/ME-V17-F0-V33F_DESACOPLA_CACHE_CDI_POR_JANELA.md`.

---

## 5. Conteúdo implementado

### 5.1. Import estrutural

`nucleo/cache_cdi_bcb.py` passa a importar:

```python
from nucleo.entrada_resolvida import JanelaConsultaCDI
```

### 5.2. Função auxiliar de tradução de janela

Foi criada a função:

```python
_datas_relevantes_por_janela_cdi(janela_consulta_cdi, data_referencia)
```

A função:

- recebe `JanelaConsultaCDI` opcional;
- retorna `None` se a janela estiver ausente ou incompleta;
- usa o primeiro dia do mês da data inicial da janela;
- usa o máximo entre `data_final_consulta` e `data_referencia`;
- não consulta BCB;
- não lê cache;
- não calcula rendimento.

### 5.3. Parâmetro opcional em carregar_cache_cdi_diario(...)

A função `carregar_cache_cdi_diario(...)` passa a aceitar:

```python
janela_consulta_cdi: Optional[JanelaConsultaCDI] = None
```

A compatibilidade é preservada porque o argumento é opcional.

### 5.4. Fallback legado preservado

Se `janela_consulta_cdi` não for informada ou estiver incompleta, o código permanece usando:

```python
_datas_relevantes(dados_operacionais, data_referencia)
```

### 5.5. Auditoria acrescida

A auditoria do cache passa a registrar:

```python
origem_janela_consulta
janela_consulta_cdi_informada
```

Isso permite distinguir quando a janela veio da Etapa 1 e quando veio do comportamento legado.

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/leitor_planilha.py`;
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
- altera saída oficial;
- altera regra de rendimento;
- altera parsing de datas da Etapa 1.

---

## 7. Validação necessária local

Executar validação local com:

- `python -m compileall nucleo`;
- teste unitário da função `_datas_relevantes_por_janela_cdi(...)`;
- teste de fallback com janela ausente;
- verificação de escopo restrita a `nucleo/cache_cdi_bcb.py` e este log.

---

## 8. Resultado esperado

O cache CDI passa a aceitar janela estrutural da Etapa 1, mas mantém comportamento legado quando a janela não é fornecida.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3G — Montar PacoteEntradaResolvida`

A próxima etapa deve reunir, sem ainda alterar Etapa 2 ou Etapa 3, os artefatos formais da Etapa 1 em `PacoteEntradaResolvida`.
