# ME-V17-F0-V33H — Audita PacoteEntradaResolvida montado

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3H
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / AUDITORIA INTERNA
- CLASSE: AUDITA_PACOTE_ENTRADA_RESOLVIDA_MONTADO
- ALTERA LEITURA DA PLANILHA: NÃO
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

Criar uma auditoria estrutural interna para o `PacoteEntradaResolvida` já montado, ainda dentro da Etapa 1, sem substituir a validação pré-execução da Etapa 2.

---

## 3. Diagnóstico inicial

A V17-F0-V.3.3G criou `montar_pacote_entrada_resolvida(...)` e validou a montagem estrutural do artefato agregador da Etapa 1.

Faltava uma função formal para auditar se o pacote montado contém os componentes estruturais esperados, flags de não alteração e evidências mínimas de integridade.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/entrada_resolvida.py`;
- `logs/iteracoes/ME-V17-F0-V33H_AUDITA_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 5. Conteúdo implementado

### 5.1. Dataclass AuditoriaPacoteEntradaResolvida

Foi criada a dataclass:

```python
AuditoriaPacoteEntradaResolvida
```

Campos:

- `ok`;
- `erros`;
- `avisos`;
- `evidencias`;
- `detalhes`.

### 5.2. Função auditar_pacote_entrada_resolvida(...)

Foi criada a função:

```python
auditar_pacote_entrada_resolvida(
    pacote,
    *,
    exigir_cache_cdi=False,
) -> AuditoriaPacoteEntradaResolvida
```

A função verifica:

- se o objeto é `PacoteEntradaResolvida`;
- presença de `pacote_planilha`;
- presença de `MapaAbasResolvidas`;
- presença de `MapaColunasResolvidas`;
- presença de `quadros_brutos`;
- presença de `quadros_estruturais_resolvidos`;
- presença de `JanelaConsultaCDI`;
- presença de `AuditoriaEntradaBruta`;
- presença de `AuditoriaResolucaoEntrada`;
- validade opcional do cache CDI;
- se os quadros são DataFrames;
- coerência temporal básica da `JanelaConsultaCDI`;
- flags de não alteração do fluxo, motor, saída e dados canônicos.

### 5.3. Cache CDI opcional

O parâmetro `exigir_cache_cdi=False` preserva a regra da Etapa 1 de que o cache CDI pode ser auditado como componente opcional durante a montagem estrutural.

Quando `exigir_cache_cdi=True`, a auditoria exige `pacote_cache_cdi` e `AuditoriaCacheCDI`.

---

## 6. Limites preservados

Esta microetapa não:

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
- lê planilha;
- consulta BCB;
- carrega cache CDI;
- calcula rendimento;
- cria `PacoteValidacaoPreExecucao`;
- cria `PacoteDadosOperacionaisCanonicos`.

---

## 7. Distinção com Etapa 2

Esta auditoria não é a validação pré-execução da Etapa 2.

Ela apenas audita a montagem estrutural do pacote produzido pela Etapa 1.

A Etapa 2 continuará responsável por validar o `PacoteEntradaResolvida` antes da canonização operacional.

---

## 8. Validação necessária local

Executar validação local com:

- `python -m compileall nucleo`;
- import de `auditar_pacote_entrada_resolvida`;
- teste de pacote válido sem cache exigido;
- teste de pacote válido com cache exigido;
- teste de pacote inválido;
- verificação de escopo restrita a `nucleo/entrada_resolvida.py` e este log.

---

## 9. Resultado esperado

A Etapa 1 passa a dispor de uma auditoria estrutural do `PacoteEntradaResolvida` montado, sem alterar o fluxo principal de execução.

---

## 10. Próxima microetapa recomendada

Após validação local aprovada, a próxima ação deve ser uma auditoria de fechamento da série V3.3A–V3.3H antes de decidir se a próxima implementação será integração controlada do pacote ao contexto baseline ou ajuste documental adicional.
