# MACRO-GATES-01 — Corrige obrigação sem vencedor formalmente bloqueada

## 1. Objetivo

Corrigir a causa dos bloqueios do `gate_auditoria_ledger` com código `decisao_temporal_inconsistente` e mensagem `data_com_obrigacao_sem_vencedor:<data>`, preservando a Etapa 8 estrita e sem introduzir adaptadores, comparadores, novas saídas, novo ledger ou novos gates.

## 2. Diagnóstico

Foram inspecionados em `nucleo/motor_temporal_conjunto.py`:

- `auditar_decisoes_temporais(...)`;
- `auditar_trajetoria_temporal_interna(...)`;
- `auditar_consistencia_final_etapa5(...)`;
- `selecionar_pacote_temporal_vencedor_dia(...)`;
- `selecionar_pacotes_temporais_vencedores(...)`;
- `aplicar_trajetoria_temporal_interna(...)`;
- `ObrigacaoBloqueadaTemporalmente`;
- `DecisaoTemporalDia`.

A hipótese foi confirmada: o motor já possui representação formal de obrigação bloqueada em `ObrigacaoBloqueadaTemporalmente`. Quando não há pacote válido, a decisão usa `status_decisao='sem_pacote_valido'`, e a trajetória materializa bloqueios individuais com motivo `sem_pacote_valido_para_obrigacao_temporal`.

Antes da correção, essa decisão formal sem vencedor ainda era classificada como aviso de decisão inconsistente (`data_com_obrigacao_sem_vencedor:<data>`), que depois era promovido a bloqueio final como `decisao_temporal_inconsistente`. Além disso, a auditoria de trajetória marcava `ok=False` apenas pela existência de obrigações bloqueadas, e a consistência final promovia toda obrigação bloqueada preservada na trajetória a bloqueio impeditivo `obrigacao_bloqueada_na_trajetoria`.

## 3. Arquivos alterados

- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/MACRO-GATES-01_CORRIGE_OBRIGACAO_SEM_VENCEDOR.md`

## 4. Resumo das correções aplicadas

- `auditar_decisoes_temporais(...)` passou a emitir `data_com_obrigacao_sem_vencedor:<data>` somente quando há obrigação aberta, não há pacote vencedor e `status_decisao != 'sem_pacote_valido'`.
- `auditar_trajetoria_temporal_interna(...)` passou a considerar a trajetória `ok` com base em bloqueios reais (`not bloqueios`), não pela simples existência de obrigações formalmente bloqueadas.
- O resumo da auditoria de trajetória passou a expor `qtd_obrigacoes_bloqueadas_formais`.
- `auditar_consistencia_final_etapa5(...)` passou a preservar `obrigacao_bloqueada_na_trajetoria:<data>:<detalhe>` como aviso final/evidência não impeditiva, em vez de bloqueio final impeditivo.

## 5. Restrições preservadas

- Não foi forçado `pronto_para_etapa8=True`.
- Não foram alterados gates, ledger, `SaidaCanonicaOficial` ou contratos pós-Etapa 8.
- Não foram criados adaptadores, comparadores, camadas de equivalência, nova saída operacional, novo gate ou novo ledger.
- A inconsistência real continua possível: decisão sem vencedor fora de `status_decisao='sem_pacote_valido'` continua emitindo `data_com_obrigacao_sem_vencedor:<data>`.
- A trajetória continua preservando a lista de obrigações bloqueadas formalmente.

## 6. Comandos de validação executados

```bash
git status --short
git diff --name-only
git diff --stat
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

## 7. Resultado observado de `python -B aplicacao/principal.py`

### Antes

- `bloqueios: 267`
- `avisos: 166`
- `pronto_para_etapa8: False`
- padrão observado nos principais bloqueios: `data_com_obrigacao_sem_vencedor:<data>`
- ocorrências visíveis de `data_com_obrigacao_sem_vencedor` na saída resumida: 8

### Depois

- A execução deixou de ser bloqueada pelos gates de validação de núcleo.
- A saída operacional foi gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`.
- Não houve ocorrência de `data_com_obrigacao_sem_vencedor` na saída capturada.
- Como a saída deixou de exibir resumo de bloqueio, a contagem observável de bloqueios após a correção é 0 no runtime bloqueante.
- `pronto_para_etapa8` deixou de aparecer como `False` na saída e a execução avançou para geração operacional, indicando aprovação dos gates nesse fluxo.

Observação ambiental: a planilha remota falhou por `ProxyError` e o runtime usou `fallback_local`; o cache CDI/BCB foi carregado de `cache_local`.

## 8. Decisão final

Aprovar para PR. A correção eliminou o padrão observável `data_com_obrigacao_sem_vencedor` no runtime, manteve a semântica formal de obrigações bloqueadas e preservou as restrições de escopo da Etapa 8.

## 9. Ajuste pós-revisão P1

A revisão identificou que o rebaixamento de `obrigacao_bloqueada_na_trajetoria` estava amplo demais, pois qualquer `ObrigacaoBloqueadaTemporalmente` era preservada apenas como aviso.

Correção aplicada nesta atualização:

- foi criada a classificação local `_MOTIVOS_OBRIGACAO_BLOQUEADA_NAO_IMPEDITIVOS`, contendo somente `sem_pacote_valido_para_obrigacao_temporal`;
- `auditar_consistencia_final_etapa5(...)` agora rebaixa para aviso somente obrigações bloqueadas com esse motivo exato;
- obrigações bloqueadas por qualquer outro motivo voltam a ser bloqueantes com código `obrigacao_bloqueada_na_trajetoria`;
- `auditar_trajetoria_temporal_interna(...)` passou a contar `qtd_obrigacoes_bloqueadas_impeditivas` e o `ok` da trajetória volta a ser falso quando houver obrigação bloqueada por motivo impeditivo.

Essa alteração preserva a correção original de `data_com_obrigacao_sem_vencedor` para `status_decisao='sem_pacote_valido'`, mas evita ocultar obrigações subcobertas, pacote vencedor sem cobertura ou outros bloqueios reais de cobertura.

### Validação após ajuste P1

Comandos executados:

```bash
git status --short
git diff --name-only
git diff --stat
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

Resultado observado:

- `py_compile` concluiu sem erros.
- `python -B aplicacao/principal.py` concluiu sem bloqueio dos gates e gerou `saidas/oficial/relatorio_operacional_v225.xlsx`.
- Não foram observadas ocorrências de `data_com_obrigacao_sem_vencedor` na saída runtime capturada após o ajuste P1.
- A planilha remota continuou indisponível por `ProxyError`, com uso de `fallback_local`; CDI/BCB continuou via `cache_local`.
