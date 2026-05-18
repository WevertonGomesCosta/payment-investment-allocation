# ME-V17-F0-V37A — Registra contenções V3.6D–V3.6F e retoma fronteira normativa da Etapa 3

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37A
- VERSAO_CANDIDATA: V17-F0-V.3.7A
- TIPO: DOCUMENTAL / ARQUITETURAL / GOVERNANÇA DE CAMADAS
- CLASSE: REGISTRA_CONTENCOES_TRANSITORIAS_E_RETOMA_FRONTEIRA_ETAPA3
- BASELINE_DE_ENTRADA: V17-F0-V.3.6F
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após a V17-F0-V.3.6F.

Commit de entrada esperado:

```text
3f3262c — V17-F0-V.3.6F: neutraliza origens migradas ainda ativas
```

A V3.6F corrigiu, na saída canônica, a permanência das origens migradas por switching como ativos comuns.

Arquivos alterados pela V3.6F:

- `nucleo/saida_canonica.py`;
- `logs/iteracoes/ME-V17-F0-V36F_CORRIGE_NEUTRALIZACAO_ORIGENS_MIGRADAS_SWITCHING.md`.

A presente V3.7A não altera código nem reabre a V3.6F.

---

## 3. Objetivo da V3.7A

Registrar formalmente que as microetapas V3.6D, V3.6E e V3.6F atuaram como contenções transitórias na camada de saída canônica, e não como implementação normativa da Etapa 3.

A partir desta microetapa, a rota principal volta a ser:

```text
Etapa 3 = canonização operacional do PacoteEntradaResolvida validado
```

A finalidade é reduzir correções sintomáticas em:

- `saida_canonica.py`;
- scripts diagnósticos isolados;
- renderizações de console/XLSX;
- adaptações pontuais fora da fronteira normativa.

---

## 4. Síntese das contenções V3.6D–V3.6F

### 4.1. V3.6D — desativação da ponte passiva POS

A V3.6D corrigiu a duplicidade dos destinos pós-switching na Situação Atual.

Regra estabilizada:

- se os POS já nascem no `inventario_canonico`, a ponte passiva POS não deve rematerializá-los para a Situação Atual;
- a lista passiva é preservada para auditoria, mas não alimenta novamente os lotes da Situação Atual.

Campos preservados:

- `pos_canonico_ativo`;
- `ponte_passiva_pos_desativada_por_pos_canonico`;
- `destinos_pos_switching_passivos_para_situacao_total`;
- `destinos_pos_switching_passivos_preservados_auditoria_total`.

Classificação arquitetural:

```text
contenção transitória em saida_canonica.py
```

Não foi implementação normativa da Etapa 3.

---

### 4.2. V3.6E — diagnóstico das origens migradas ainda ativas

A V3.6E diagnosticou que as origens migradas por switching continuavam em `lotes_ativos`:

| origem migrada | problema |
|---|---|
| Lote 3000 mar. B | origem migrada ainda ativa |
| Lote 3000 mar. V | origem migrada ainda ativa |
| Lote 8500 mar. | origem migrada ainda ativa |

Conclusão formal da V3.6E:

```text
DIAGNOSTICO=ORIGENS_MIGRADAS_CONTINUAM_COMO_ATIVOS_COMUNS
V36E_REQUER_V36F_CORRETIVA=sim
```

Classificação arquitetural:

```text
diagnóstico de consistência observável pós-contenção
```

Não foi implementação normativa da Etapa 3.

---

### 4.3. V3.6F — neutralização observável das origens migradas

A V3.6F neutralizou na camada ativa as origens migradas por switching:

| origem migrada | resultado após V3.6F |
|---|---|
| Lote 3000 mar. B | removido de `lotes_ativos` e registrado como `migrado_por_switching` |
| Lote 3000 mar. V | removido de `lotes_ativos` e registrado como `migrado_por_switching` |
| Lote 8500 mar. | removido de `lotes_ativos` e registrado como `migrado_por_switching` |

Campos de auditoria introduzidos:

- `origens_migradas_neutralizadas_situacao_total`;
- `origens_migradas_neutralizadas_situacao`;
- `patrimonio_liquido_ativo_neutralizado_origens_migradas`;
- `origens_migradas_ativas_remanescentes_total`;
- `origens_migradas_ativas_remanescentes`.

Validação observada:

```text
origens_migradas_neutralizadas_situacao_total = 3
patrimonio_liquido_ativo_neutralizado_origens_migradas = 9505.61
origens_migradas_ativas_remanescentes_total = 0
VALIDACAO_V36F_OK
```

Classificação arquitetural:

```text
contenção transitória em saida_canonica.py
```

Não foi implementação normativa da Etapa 3.

---

## 5. Decisão arquitetural da V3.7A

A V3.7A fixa a seguinte decisão:

```text
V3.6D–V3.6F estabilizam a saída observável, mas não substituem a implementação normativa da Etapa 3.
```

Portanto:

1. a V3.6D permanece válida;
2. a V3.6E permanece válida como diagnóstico;
3. a V3.6F permanece válida como contenção corretiva;
4. não se deve abrir uma sequência indefinida de correções em `saida_canonica.py`;
5. a próxima frente deve voltar para a fronteira normativa da Etapa 3.

---

## 6. Fronteira normativa da Etapa 3

A Etapa 3 foi formalizada como:

```text
Etapa 3 = canonização operacional do PacoteEntradaResolvida validado
```

A Etapa 3 deve receber:

- `PacoteEntradaResolvida` validado;
- `PacoteValidacaoPreExecucao`.

A Etapa 3 deve produzir:

- `PacoteDadosOperacionaisCanonicos`;
- `UniversoEconomicoCanonico`.

O `PacoteDadosOperacionaisCanonicos` deve conter, de forma normativa:

- `carteira_canonica`;
- `universo_economico_canonico`;
- `gastos_canonicos`;
- `salarios_canonicos`;
- `switching_canonico`;
- `inventario_canonico_base`;
- `inventario_canonico_completo`;
- auditorias;
- validações.

A saída canônica deve deixar de ser o local primário de correção patrimonial.

---

## 7. Regra de governança após V3.7A

Após a V3.7A, novas correções devem seguir esta ordem de classificação:

1. **Entrada resolvida** — problemas de leitura, abas, aliases, colunas, cache ou configuração.
2. **Validação pré-execução** — problemas de gate, campos obrigatórios, consistência mínima ou bloqueio antes da canonização.
3. **Etapa 3 / canonização operacional** — problemas de nascimento, normalização, status operacional, inventário canônico, switching canônico ou lotes pós-switching canônicos.
4. **Replay / ledger / estado temporal** — problemas de consumo temporal, pagamentos, saques, maturidade, rendimento, saldo ou eventos.
5. **Saída canônica / renderização** — apenas apresentação, auditoria observável ou contenção transitória explicitamente justificada.

Regra de parada:

```text
Se uma nova inconsistência patrimonial exigir mais do que filtragem/apresentação, não corrigir diretamente em saida_canonica.py sem antes classificar se a origem pertence à Etapa 3, replay, ledger ou motor.
```

---

## 8. Implicação para as próximas microetapas

A próxima microetapa não deve abrir uma nova correção sintomática em `saida_canonica.py`.

A próxima microetapa recomendada deve ser diagnóstica/arquitetural e deve mapear a fronteira real entre:

- `PacoteEntradaResolvida`;
- `PacoteValidacaoPreExecucao`;
- `PacoteDadosOperacionaisCanonicos`;
- `inventario_canonico_completo`;
- `switching_canonico`;
- replay passado;
- ledger temporal;
- saída canônica.

---

## 9. Próxima microetapa recomendada

Abrir:

```text
V17-F0-V.3.7B — Mapeia fronteira real entre Etapa 3, replay, ledger e saída canônica
```

Objetivo da V3.7B:

- identificar quais responsabilidades ainda estão indevidamente concentradas em `saida_canonica.py`;
- distinguir correções de nascimento canônico, estado temporal, replay e mera apresentação;
- definir a ordem segura de migração para a Etapa 3 normativa;
- reduzir a dependência de scripts diagnósticos e contenções manuais.

Escopo inicial recomendado para V3.7B:

- documental/diagnóstico;
- sem alteração de código;
- sem alteração de motor;
- sem alteração de replay;
- sem alteração de ledger;
- sem alteração da saída canônica.

---

## 10. Conclusão

A V3.7A encerra formalmente o ciclo de contenções V3.6D–V3.6F.

A decisão consolidada é:

```text
As contenções V3.6D–V3.6F são válidas para estabilizar a saída observável, mas a rota principal deve voltar à implementação normativa da Etapa 3 como canonização operacional do PacoteEntradaResolvida validado.
```

Esta microetapa não altera código e não promove nova regra econômica.
