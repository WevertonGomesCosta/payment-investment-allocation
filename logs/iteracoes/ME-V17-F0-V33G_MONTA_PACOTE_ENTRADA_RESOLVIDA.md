# ME-V17-F0-V33G — Monta PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3G
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / AGREGAÇÃO
- CLASSE: MONTA_PACOTE_ENTRADA_RESOLVIDA
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

Montar formalmente o artefato único `PacoteEntradaResolvida`, agregando os artefatos já produzidos na Etapa 1 sem alterar os produtores atuais.

---

## 3. Diagnóstico inicial

As microetapas anteriores criaram e validaram:

- `MapaAbasResolvidas`;
- `MapaColunasResolvidas`;
- `quadros_estruturais_resolvidos`;
- `JanelaConsultaCDI`;
- desacoplamento do cache CDI por janela.

Faltava uma função formal de agregação para montar o `PacoteEntradaResolvida` a partir desses objetos.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/entrada_resolvida.py`;
- `logs/iteracoes/ME-V17-F0-V33G_MONTA_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 5. Conteúdo implementado

### 5.1. Função montar_pacote_entrada_resolvida(...)

Foi criada a função:

```python
montar_pacote_entrada_resolvida(
    *,
    pacote_config=None,
    contexto_execucao=None,
    pacote_planilha=None,
    pacote_cache_cdi=None,
    metadados=None,
) -> PacoteEntradaResolvida
```

A função agrega:

- `pacote_config`;
- `contexto_execucao`;
- `pacote_planilha`;
- `mapa_abas_resolvidas`;
- `mapa_colunas_resolvidas`;
- `quadros_brutos`;
- `quadros_estruturais_resolvidos`;
- `janela_consulta_cdi`;
- `pacote_cache_cdi`;
- `auditoria_entrada_bruta`;
- `auditoria_resolucao_entrada`;
- `auditoria_cache_cdi`;
- `metadados`.

### 5.2. Auditorias formais auxiliares

Foram criadas funções auxiliares:

```python
montar_auditoria_entrada_bruta(...)
montar_auditoria_resolucao_entrada(...)
montar_auditoria_cache_cdi(...)
```

Essas funções apenas agregam informações já existentes nos pacotes informados.

### 5.3. Compatibilidade com quadros_canonicos

Se `quadros_estruturais_resolvidos` não existir no pacote de planilha, a função usa `quadros_canonicos` como fallback legado.

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

## 7. Validação necessária local

Executar validação local com:

- `python -m compileall nucleo`;
- import de `montar_pacote_entrada_resolvida`;
- teste com pacote de planilha simulado contendo mapas, quadros, janela e auditoria;
- teste com pacote de cache simulado;
- verificação de escopo restrita a `nucleo/entrada_resolvida.py` e este log.

---

## 8. Resultado esperado

A Etapa 1 passa a dispor de uma função formal para montar `PacoteEntradaResolvida`, ainda sem alterar o fluxo principal de execução.

---

## 9. Próxima microetapa recomendada

`V17-F0-V.3.3H — Auditar PacoteEntradaResolvida montado`

A próxima etapa deve validar o pacote montado e seus campos obrigatórios, ainda sem promover integração com Etapa 2, Etapa 3, motor ou saída.
