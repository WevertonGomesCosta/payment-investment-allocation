# ME-V17-F0-V30 — Auditoria da Etapa 3 e decisão sobre integração de Switching ao inventario_canonico

## 1. Identificação

- MICROETAPA: ME-V17-F0-V30
- VERSAO_CANDIDATA: V17-F0-V.3.0
- TIPO: DOCUMENTAL / AUDITORIA / DECISÃO
- CLASSE: AUDITA_ETAPA3_E_FORMALIZA_INTEGRACAO_SWITCHING_INVENTARIO_CANONICO
- STATUS: CONCLUÍDA
- ALTERA_CODIGO: não
- ALTERA_MOTOR: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_RENDERIZACAO: não
- ALTERA_DADOS: não

---

## 2. Objetivo

Auditar o estado atual da Etapa 3 do macrofluxo operacional e formalizar a decisão arquitetural de integrar os registros da aba `Switching` ao `inventario_canonico` operacional.

A decisão registrada nesta microetapa é que a próxima implementação deve fazer o `inventario_canonico` nascer completo, incorporando os lotes derivados de switching, em vez de criar um novo artefato operacional dominante que exigiria refatoração ampla dos consumidores downstream.

---

## 3. Escopo auditado

Foram considerados os seguintes módulos e funções:

### Etapa 2

- `nucleo/validacao_pre_execucao.py`
  - `validar_pre_execucao(...)`
  - `_validar_pacote_config(...)`
  - `_validar_contexto_execucao(...)`
  - `_validar_pacote_planilha(...)`
  - `_mapear_colunas_por_alias(...)`
  - `_validar_datas_minimas(...)`
  - `_validar_numeros_minimos(...)`

### Etapa 3

- `nucleo/dados_operacionais_canonicos.py`
  - `carregar_dados_operacionais_canonicos(...)`
  - `carregar_inventario_canonico(...)`
  - `carregar_gastos_canonicos(...)`
  - `carregar_salarios_canonicos(...)`
  - `carregar_switching_canonico(...)`
  - `_resolver_produto_canonico(...)`
  - `_classificar_investimento(...)`

- `nucleo/inventario_lotes_expandido_pos_switching.py`
  - `normalizar_lotes_pos_switching_para_schema_inventario(...)`
  - `construir_inventario_lotes_expandido(...)`
  - `_resolver_produto_canonico_local(...)`

### Suporte de leitura

- `nucleo/leitor_planilha.py`
  - `carregar_planilha(...)`
  - `resolver_coluna(...)`
  - `aliases_coluna(...)`
  - `canonizar_colunas(...)`
  - `construir_mapa_alias(...)`

---

## 4. Evidências observadas

### 4.1. A aba Switching contém as informações necessárias

A aba `Switching` possui as colunas:

```text
Lote (ID) Antes
Lote (ID) Depois
Data Recebimento
Data Aplicação
Valor Líquido Migrado
Investimento
````

Exemplo observado:

```text
Lote (ID) Antes: Lote 3000 mar. V
Lote (ID) Depois: Lote 3120 mai
Data Recebimento: 2026-05-04
Data Aplicação: 2026-05-05
Valor Líquido Migrado: 3122.53
Investimento: Mercado Pago Cofrinho 120% CDI (Meli+)
```

Portanto, a falha não está na ausência de informação na planilha.

---

### 4.2. A Etapa 3 não resolve corretamente as datas do Switching

A auditoria de `ctx.dados_operacionais.auditoria_switching` retornou:

```text
'data_switching': None
'lote_origem': 'Lote (ID) Antes'
'lote_destino': 'Lote (ID) Depois'
'produto_destino': 'Investimento'
'valor_liquido_origem': 'Valor Líquido Migrado'
```

A validação retornou:

```text
avisos: ['existem_switchings_sem_data']
```

Conclusão: `carregar_switching_canonico(...)` lê lote origem, lote destino, produto destino e valor migrado, mas não reconhece `Data Recebimento` e `Data Aplicação`.

---

### 4.3. O produto destino está corretamente resolvido na Carteira

Para `Mercado Pago Cofrinho 120% CDI (Meli+)`, a Carteira canônica retorna:

```text
taxa_base_cdi = 1.2
taxa_bonus_cdi = 0.0
dias_bonus = 0
isento_ir = False
regra_iof = nao_incide
semantica_taxa_base = percentual_cdi
```

Logo, a falha não está nos metadados fiscais ou econômicos do produto.

---

### 4.4. O lote pós-switching existe fora do inventario_canonico

O `Lote 3120 mai` aparece em `lotes_pos_switching_normalizados`, mas com datas nulas:

```text
data_recebimento = None
data_aplicacao = None
data_base_fiscal = None
```

E não aparece em `inventario_canonico`, que retorna `Empty DataFrame` ao filtrar por `Lote 3120 mai`.

Conclusão: o lote pós-switching não está no artefato operacional consumido pelo restante do fluxo.

---

## 5. Diagnóstico da Etapa 3 atual

A Etapa 3 está parcialmente implementada:

```text
Inventário de Lotes bruto
    -> inventario_canonico

Switching bruto
    -> switching_canonico
    -> lotes_pos_switching_normalizados
    -> inventario_lotes_expandido
```

Porém, o artefato dominante consumido pelo restante do projeto continua sendo `inventario_canonico`, e ele não contém os lotes pós-switching.

A consequência prática é que o núcleo financeiro e os módulos posteriores não tratam `Lote 3120 mai` como lote financeiro regular desde o nascimento canônico.

---

## 6. Redundâncias avaliadas

### 6.1. Redundância aceitável entre Etapa 2 e Etapa 3

A Etapa 2 valida aliases e interpretabilidade mínima, mas não deve produzir mapeamento operacional.

A Etapa 3 resolve colunas e transforma dados.

Portanto, a existência de mecanismos separados de validação e resolução é aceitável, desde que a Etapa 2 continue sendo gate puro.

---

### 6.2. Redundância problemática na Etapa 3

Há dois resolvedores de produto:

```text
nucleo/dados_operacionais_canonicos.py
_resolver_produto_canonico(...)

nucleo/inventario_lotes_expandido_pos_switching.py
_resolver_produto_canonico_local(...)
```

A redundância é real, mas não deve ser refatorada nesta microetapa. A correção atual deve preservar escopo restrito.

Refatoração futura possível: extrair resolvedor comum para módulo neutro.

---

### 6.3. Redundância operacional entre inventario_canonico e inventario_lotes_expandido

O problema mais importante é que existem dois artefatos:

```text
inventario_canonico
inventario_lotes_expandido
```

mas apenas `inventario_canonico` é consumido como base operacional corrente.

Decisão: não criar novo artefato dominante. O `inventario_canonico` deve passar a nascer completo.

---

## 7. Decisão formal

A próxima implementação deve fazer:

```text
inventario_canonico =
inventario_canonico_base
+
lotes_pos_switching_normalizados
```

O artefato `inventario_lotes_expandido` pode continuar existindo como alias, espelho ou auditoria, mas não deve ser o único local onde os lotes pós-switching aparecem.

---

## 8. Próxima microetapa

A próxima microetapa será:

```text
V17-F0-V.3.1 — Integra Switching ao inventario_canonico operacional
```

Objetivo:

```text
1. Corrigir a leitura temporal do Switching:
   - Data Recebimento -> data_recebimento
   - Data Aplicação -> data_aplicacao
   - data_switching mantida por compatibilidade, preferencialmente igual a data_aplicacao.

2. Transformar cada switching válido em linha compatível com o schema do inventario_canonico.

3. Retornar inventario_canonico já expandido operacionalmente.

4. Manter inventario_lotes_expandido como espelho/auditoria compatível.

5. Registrar risco de dupla contagem dos lotes origem migrados, sem neutralização temporal agressiva nesta etapa.
```

---

## 9. Restrições para V3.1

A implementação da V3.1 deve alterar somente:

```text
nucleo/dados_operacionais_canonicos.py
nucleo/inventario_lotes_expandido_pos_switching.py
logs/iteracoes/ME-V17-F0-V31_INTEGRA_SWITCHING_INVENTARIO_CANONICO.md
```

Não deve alterar:

```text
nucleo/validacao_pre_execucao.py
nucleo/leitor_planilha.py
nucleo/nucleo_financeiro_minimo.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
aplicacao/principal.py
contrato operacional
modelo oficial
README
dados financeiros
cache BCB
```

---

## 10. Critérios de aceite da V3.1

Após a V3.1, devem ser verdadeiras as seguintes verificações:

```text
1. switching_canonico deve conter data_recebimento e data_aplicacao preenchidas.
2. lotes_pos_switching_normalizados deve conter Lote 3120 mai com:
   - data_recebimento = 2026-05-04
   - data_aplicacao = 2026-05-05
   - data_base_fiscal = 2026-05-05
   - valor_original = 3122.53
   - produto_key resolvido
   - regra_iof herdável pelo núcleo financeiro via produto_key.

3. inventario_canonico deve conter Lote 3120 mai.
4. inventario_lotes_expandido deve ser igual ou compatível com inventario_canonico operacional.
5. O núcleo financeiro deve conseguir enxergar o Lote 3120 mai sem alteração em nucleo_financeiro_minimo.py.
```

---

## 11. Status final

```text
AUDITORIA_ETAPA_3=concluida
IMPLEMENTACAO_V3_1=autorizada
ROTA=expandir_inventario_canonico_existente
NOVO_ARTEFATO_DOMINANTE=nao
RISCO_PRINCIPAL_A_CONTROLAR=dupla_contagem_de_lote_origem_migrado
```

