# ME-V17-F0-V34B — Implementa validação paralela por PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4B
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / MODO PARALELO
- CLASSE: VALIDACAO_PRE_EXECUCAO_PACOTE_ENTRADA_RESOLVIDA_PARALELA
- ALTERA CÓDIGO: SIM
- ALTERA `nucleo/validacao_pre_execucao.py`: SIM
- ALTERA CONTEXTO BASELINE: NÃO
- ALTERA ENTRADA RESOLVIDA: NÃO
- ALTERA CACHE CDI/BCB: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO

---

## 2. Objetivo

Implementar, em modo paralelo, a função:

```python
validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
) -> PacoteValidacaoPreExecucao
```

A função valida a entrada resolvida produzida pela Etapa 1 sem substituir ainda a função legada:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

---

## 3. Escopo implementado

A implementação adicionou validações específicas para:

- estrutura do `PacoteEntradaResolvida`;
- `PacoteConfig` extraído do pacote;
- `ContextoExecucao` extraído do pacote;
- `PacotePlanilha` em modo básico, sem redescobrir aliases;
- `MapaAbasResolvidas`;
- `MapaColunasResolvidas`;
- `quadros_estruturais_resolvidos`;
- interpretabilidade mínima de datas e números usando mapas já resolvidos;
- `JanelaConsultaCDI`;
- `PacoteCacheCDIDiario`;
- auditorias da Etapa 1.

---

## 4. Funções adicionadas

Foram adicionadas funções auxiliares de validação:

```text
_validar_pacote_planilha_basico_sem_alias(...)
_validar_pacote_entrada_resolvida_estrutura(...)
_validar_mapa_abas_resolvidas(...)
_validar_mapa_colunas_resolvidas(...)
_resolver_coluna_no_quadro_estrutural(...)
_validar_quadros_estruturais_resolvidos(...)
_validar_janela_consulta_cdi(...)
_validar_pacote_cache_cdi(...)
_validar_auditorias_etapa1(...)
```

A função legada `_mapear_colunas_por_alias(...)` foi preservada para a validação antiga, mas não é usada pela nova função por `PacoteEntradaResolvida`.

---

## 5. Compatibilidade preservada

A função atual foi preservada:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

O `ContextoBaseline` atual continua chamando a validação legada.

A nova função é paralela e ainda não é integrada ao fluxo principal.

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/contexto_baseline.py`;
- altera `nucleo/entrada_resolvida.py`;
- altera `nucleo/leitor_planilha.py`;
- altera `nucleo/cache_cdi_bcb.py`;
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
- altera cache;
- altera Etapa 3.

---

## 7. Observações técnicas

A validação por pacote aceita `quadros_estruturais_resolvidos` tanto quando os quadros estão indexados por nome da aba física quanto quando estão indexados por bloco.

Também aceita que os campos nos quadros estruturais apareçam como:

- nome canônico do campo; ou
- coluna física resolvida no `MapaColunasResolvidas`.

Isso evita redescoberta de aliases e preserva a fronteira entre Etapa 1 e Etapa 2.

---

## 8. Validação local necessária

Executar:

```bash
python -m compileall nucleo
```

Executar teste local confirmando:

- import de `validar_pre_execucao_pacote_entrada_resolvida`;
- carregamento do `ContextoBaseline` com shadows pesados desativados;
- execução da validação legada atual;
- execução da validação paralela por `PacoteEntradaResolvida`;
- confirmação de que ambas retornam `PacoteValidacaoPreExecucao`;
- confirmação de que a validação paralela não altera o contexto nem substitui a legada.

---

## 9. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa recomendada é:

```text
V17-F0-V.3.4C — Criar script diagnóstico comparando validação legada vs validação por PacoteEntradaResolvida
```

Essa etapa deve criar um script em `scripts/diagnostico/`, sem alterar pipeline principal, para comparar os resultados das duas validações.