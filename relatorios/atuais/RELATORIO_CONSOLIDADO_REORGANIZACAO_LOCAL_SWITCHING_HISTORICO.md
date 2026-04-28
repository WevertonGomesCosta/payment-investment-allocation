# Relatório consolidado — histórico de reorganização local e switching

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/reorganizacao_local_switching/` em um único relatório atual, preservando a trilha de reorganização local, planejamento conjunto, decisão local e switching sem manter arquivos granulares.

- Arquivos consolidados: 11
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/reorganizacao_local_switching/AUDITORIA_CONGELAMENTO_APLICAR_SWITCHING_EVENTOS_V174.md` | 90 | Auditoria de congelamento estrutural de `_aplicar_switching_eventos(...)` — V174 |
| `relatorios/historico/reorganizacao_local_switching/AUDITORIA_CONGELAMENTO_SWITCHING_PARCIAL_V172.md` | 67 | Auditoria técnica V172 — congelamento local de `_aplicar_switching_parcial_no_lote(...)` |
| `relatorios/historico/reorganizacao_local_switching/AUDITORIA_ORQUESTRADOR_LOCAL_SWITCHING_V173.md` | 49 | Auditoria técnica V173 — `_aplicar_efeito_evento_switching(...)` |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_APLICACAO_EFEITO_EVENTO_SWITCHING_V163.md` | 72 | Auditoria e microextração local da aplicação final do efeito do evento — V163 |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_BUILDER_ESTADO_SIMULADOR_V158.md` | 39 | Extração do builder de estado do simulador central — V158 |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_CAMADA_COMUM_DESTINO_SWITCHING_V170.md` | 43 | V170 — Extração de camada comum neutra entre parcial e integral |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_HELPERS_INTEGRAL_PARCIAL_APLICAR_SWITCHING_V162.md` | 39 | Extração local entre switching integral e parcial no simulador central — V162 |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_HISTORICO_EXECUTADOS_ACUMULADORES_V164.md` | 39 | V164 — extração local de histórico, executados e acumuladores no simulador central |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_MUTACAO_LOTE_ORIGEM_SWITCHING_PARCIAL_V171.md` | 73 | EXTRAÇÃO DA MUTAÇÃO DO LOTE DE ORIGEM NO SWITCHING PARCIAL — V171 |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_PAYLOAD_MUTACAO_SWITCHING_INTEGRAL_V169.md` | 82 | Extração local do payload de mutação do ramo `switching_integral` — V169 |
| `relatorios/historico/reorganizacao_local_switching/EXTRACAO_RUNNER_SIMULADOR_CENTRAL_V157.md` | 26 | Extração do runner do simulador central — V157 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Reorganização local | Histórico de reorganização da camada local preservado em forma consolidada. |
| Switching | Registros relacionados a decisões e integração de switching permanecem rastreáveis. |
| Planejamento conjunto | Evidências históricas sobre planejamento conjunto/local foram preservadas. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/reorganizacao_local_switching/AUDITORIA_CONGELAMENTO_APLICAR_SWITCHING_EVENTOS_V174.md`

- Título: Auditoria de congelamento estrutural de `_aplicar_switching_eventos(...)` — V174
- Linhas originais: 90

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria de congelamento estrutural de `_aplicar_switching_eventos(...)` — V174
## Baseline auditada
- Baseline operacional real considerada: **V162**
- Derivação imediatamente auditada: **V173**
- Escopo desta auditoria: decidir se `_aplicar_switching_eventos(...)` já atingiu ponto de **congelamento estrutural** nesta rodada, antes de qualquer discussão sobre camadas mais sensíveis.
## Conclusão objetiva
**Sim. `_aplicar_switching_eventos(...)` já pode ser congelada estruturalmente nesta rodada.**
A função ainda possui algum espalhamento de assinatura e duplicação de coordenação entre os ramos de `aporte_nao_aportado` e `switching`, mas o ganho restante **já não é de microextração local neutra**. O próximo passo para reduzi-la exigiria uma reorganização de coordenação mais ampla, com risco maior de encostar no contrato funcional do motor.
## Estado arquitetural observado na V173
Após as microextrações anteriores, `_aplicar_switching_eventos(...)` já opera, na prática, como um orquestrador de nível imediatamente acima da aplicação local do evento:
1. prepara o evento executável do dia;
2. fecha os escalares econômicos mínimos do ramo;
3. delega a aplicação do efeito do evento;
4. registra histórico/executados/acumuladores.
As fronteiras locais de menor risco já foram exploradas:
- aplicação do efeito do evento;
- registro pós-execução;
- camada comum de campos de destino;
```

</details>

### `relatorios/historico/reorganizacao_local_switching/AUDITORIA_CONGELAMENTO_SWITCHING_PARCIAL_V172.md`

- Título: Auditoria técnica V172 — congelamento local de `_aplicar_switching_parcial_no_lote(...)`
- Linhas originais: 67

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria técnica V172 — congelamento local de `_aplicar_switching_parcial_no_lote(...)`
## Baseline auditada
- Baseline operacional: V171
- Arquivo auditado: `nucleo/simulador_central_eventos_v1.py`
- Fronteira avaliada: `_aplicar_switching_parcial_no_lote(...)`
- Escopo permitido: auditoria estrutural local sem tocar em `_valor_terminal_estimado_lote`, `_calcular_metrica`, `_patrimonio_terminal_proxy` ou `simular_cenario_eventos_v1`
## Pergunta da etapa
Verificar se `_aplicar_switching_parcial_no_lote(...)` já está modularizado o suficiente para congelar a frente local, ou se ainda vale uma última microextração apenas do `append`/persistência do novo lote destino no estado.
## Resultado da auditoria
**Conclusão:** a função já está modularizada o suficiente para congelamento local nesta frente.
## Motivos técnicos
Após as microextrações anteriores, a função ficou semanticamente organizada em três passos explícitos:
1. **Mutação do lote de origem residual**
   - delegada para `_aplicar_mutacao_origem_switching_parcial(...)`
2. **Construção do novo lote destino**
   - via `deepcopy(lote)` + campos específicos do novo lote + `_construir_campos_comuns_destino_evento_switching(...)`
3. **Persistência no estado**
   - `estado.setdefault('lotes_aportados', []).append(novo_lote)`
```

</details>

### `relatorios/historico/reorganizacao_local_switching/AUDITORIA_ORQUESTRADOR_LOCAL_SWITCHING_V173.md`

- Título: Auditoria técnica V173 — `_aplicar_efeito_evento_switching(...)`
- Linhas originais: 49

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria técnica V173 — `_aplicar_efeito_evento_switching(...)`
## Objetivo
Auditar se `_aplicar_efeito_evento_switching(...)` já podia ser tratado como orquestrador local estável e congelável, ou se ainda havia uma microredução segura de assinatura/ramificação.
## Conclusão
A função **ainda não estava no melhor ponto de congelamento** na V172, porque mantinha um ramo inline relevante para `aporte_nao_aportado`, enquanto `switching_integral` e `switching_parcial` já estavam delegados para helpers dedicados.
Foi aplicada uma **última microredução segura de ramificação**, sem alterar contrato funcional, lógica econômica, semântica do pós-vencimento, valoração terminal global ou executor central.
## Mudança implementada
Foram extraídos dois helpers locais:
- `_construir_lote_destino_aporte_nao_aportado(...)`
- `_aplicar_aporte_nao_aportado_no_estado(...)`
Com isso, `_aplicar_efeito_evento_switching(...)` passou a operar como orquestrador local mais uniforme:
1. valida o tipo/objeto preparado;
2. delega `aporte_nao_aportado`;
3. delega `switching_integral`;
4. delega `switching_parcial`.
## O que não foi alterado
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_APLICACAO_EFEITO_EVENTO_SWITCHING_V163.md`

- Título: Auditoria e microextração local da aplicação final do efeito do evento — V163
- Linhas originais: 72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria e microextração local da aplicação final do efeito do evento — V163
## Baseline operacional
- Base utilizada: **V162**
- Arquivo-alvo: `nucleo/simulador_central_eventos_v1.py`
- Objetivo: reduzir acoplamento local dentro de `_aplicar_switching_eventos` sem alterar o contrato funcional do motor.
## Auditoria técnica objetiva
A mutação final do lote/estado dentro de `_aplicar_switching_eventos` mostrou uma fronteira semântica suficientemente estável para uma microextração local segura, porque:
1. **Os insumos econômicos já chegam resolvidos antes da mutação**:
   - `valor_disponivel`
   - `fracao_lote`
   - `valor_liquido_origem`
   - `principal`
   - `custo_fiscal`
   - `valor_migrado`
   - `valor_terminal_estimado`
   - metadados de destino (`retorno`, `liquidez`, `carencia`)
2. **A mutação final não decide a economia do evento**; ela apenas aplica no estado um efeito já calculado.
3. **A distinção integral/parcial já estava encapsulada em helpers locais**, o que permite criar um wrapper-orquestrador pequeno sem tocar na regra econômica.
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_BUILDER_ESTADO_SIMULADOR_V158.md`

- Título: Extração do builder de estado do simulador central — V158
- Linhas originais: 39

<details>
<summary>Trecho inicial preservado</summary>

```text
# Extração do builder de estado do simulador central — V158
Baseline estrutural utilizada: V157.
## Escopo
Extração isolada de `construir_estado_global_recorte_curto_v117` para um módulo dedicado de builder, com wrapper de compatibilidade preservado em `nucleo/simulador_central_eventos_v1.py`.
## O que foi feito
- criado `nucleo/builders/`
- criado `nucleo/builders/simulador_central_estado_v117.py`
- `construir_estado_global_recorte_curto_v117` no simulador central agora delega para o módulo novo
- nenhuma outra função de switching, valoração terminal ou executor central foi movida
## Dependências mantidas
Para minimizar risco, o builder novo importa helpers já existentes do simulador central:
- `_coerce_date`
- `_mapa_produtos_proxy`
- `_proxy_fallback_lote`
Também preserva o uso de:
- `_pagamentos_futuros`
- `proximo_dia_util_bancario_em_ou_apos`
## Compatibilidade
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_CAMADA_COMUM_DESTINO_SWITCHING_V170.md`

- Título: V170 — Extração de camada comum neutra entre parcial e integral
- Linhas originais: 43

<details>
<summary>Trecho inicial preservado</summary>

```text
# V170 — Extração de camada comum neutra entre parcial e integral
## Objetivo
Auditar se a montagem do payload do lote destino no switching parcial e a montagem do payload de mutação no switching integral já podiam compartilhar uma camada local ainda mais neutra de campos comuns, sem tocar em `_valor_terminal_estimado_lote`, `_calcular_metrica`, `_patrimonio_terminal_proxy` ou `simular_cenario_eventos_v1`.
## Conclusão
A fronteira foi considerada segura.
O núcleo compartilhável encontrado é estritamente estrutural:
- identificação do produto destino
- campos de valor do lote destino já calculados
- proxy/retorno/liquidez/carência do destino
- datas locais de aplicação e valuation já definidas antes
- custo fiscal acumulado incremental já fechado antes
- flags de rastreabilidade do evento
## Implementação aplicada
Foi criado o helper local:
- `_construir_campos_comuns_destino_evento_switching(...)`
Ele passou a ser usado em:
- `_construir_payload_mutacao_switching_integral(...)`
- `_aplicar_switching_parcial_no_lote(...)`
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_HELPERS_INTEGRAL_PARCIAL_APLICAR_SWITCHING_V162.md`

- Título: Extração local entre switching integral e parcial no simulador central — V162
- Linhas originais: 39

<details>
<summary>Trecho inicial preservado</summary>

```text
# Extração local entre switching integral e parcial no simulador central — V162
## Observação de baseline
O arquivo .zip da V161 não estava disponível no ambiente desta execução.
Para não bloquear a etapa, a alteração foi aplicada sobre a baseline estrutural acessível mais próxima (**V158**), reconstruindo localmente as microextrações intermediárias necessárias no mesmo módulo e executando apenas a separação pedida nesta etapa.
## Escopo da etapa
Microextração local dentro de `nucleo/simulador_central_eventos_v1.py`, sem mover a função principal `_aplicar_switching_eventos` e sem alterar o cálculo fiscal, a valoração do destino, a valoração terminal ou o executor central.
## Helpers locais adicionados
- `_preparar_evento_executavel_no_dia`
- `_registrar_historico_evento`
- `_registrar_execucao_evento`
- `_acumular_resultados_execucao`
- `_aplicar_switching_integral_no_lote`
- `_aplicar_switching_parcial_no_lote`
## O que mudou
A função principal `_aplicar_switching_eventos` continua no mesmo arquivo e com a mesma assinatura, mas agora delega:
- a preparação do evento do dia;
- o registro de histórico/executados/acumuladores;
- a mutação do estado específica de switching integral;
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_HISTORICO_EXECUTADOS_ACUMULADORES_V164.md`

- Título: V164 — extração local de histórico, executados e acumuladores no simulador central
- Linhas originais: 39

<details>
<summary>Trecho inicial preservado</summary>

```text
# V164 — extração local de histórico, executados e acumuladores no simulador central
## Baseline
- baseline operacional real: V162
- derivação imediata aplicada sobre a V163
## Escopo desta microextração
Auditar e, sendo seguro, extrair a instrumentação pós-execução dentro de `_aplicar_switching_eventos`, cobrindo apenas:
- registro em `historico`
- registro em `executados`
- atualização de acumuladores (`ganho_total`, `perda_liquidez`, `custo_fiscal_total`)
## Conclusão da auditoria
A fronteira foi considerada segura porque essa camada já operava apenas com valores previamente calculados e não recalcula nenhuma regra econômica do switching.
## Novo helper local
- `_registrar_pos_execucao_evento_switching(...)`
Responsabilidade do helper:
- receber valores já fechados do evento
- registrar o payload histórico
- registrar o payload de execução
- devolver acumuladores atualizados
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_MUTACAO_LOTE_ORIGEM_SWITCHING_PARCIAL_V171.md`

- Título: EXTRAÇÃO DA MUTAÇÃO DO LOTE DE ORIGEM NO SWITCHING PARCIAL — V171
- Linhas originais: 73

<details>
<summary>Trecho inicial preservado</summary>

```text
# EXTRAÇÃO DA MUTAÇÃO DO LOTE DE ORIGEM NO SWITCHING PARCIAL — V171
## Baseline
- Baseline operacional real considerada: V170
- Derivação gerada: V171
## Objetivo da microetapa
Auditar se a mutação do lote de origem no ramo de `switching_parcial` já podia ser isolada em um helper local próprio, sem tocar em:
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`
## Conclusão da auditoria
A fronteira foi considerada **segura para extração**.
### Motivo
O bloco do lote de origem no parcial já concentrava uma responsabilidade local coesa:
1. calcular `valor_residual`;
2. calcular `principal_residual`;
3. recomputar `valor_terminal_estimado` do lote residual usando a função já existente `_valor_terminal_estimado_lote(...)`.
Esse trecho não introduz regra econômica nova. Ele apenas aplica, de forma localizada, o efeito residual do resgate parcial sobre o lote de origem.
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_PAYLOAD_MUTACAO_SWITCHING_INTEGRAL_V169.md`

- Título: Extração local do payload de mutação do ramo `switching_integral` — V169
- Linhas originais: 82

<details>
<summary>Trecho inicial preservado</summary>

```text
# Extração local do payload de mutação do ramo `switching_integral` — V169
## Baseline operacional usada nesta entrega
No ambiente local desta conversa, o último pacote efetivamente acessível para edição foi a derivação visível do simulador central já contendo as microextrações anteriores registradas até a V164.
A auditoria e a microextração desta entrega foram aplicadas cirurgicamente sobre esse código visível do módulo `nucleo/simulador_central_eventos_v1.py`, preservando o mesmo objetivo estrutural que vinha sendo seguido na trilha incremental da V162 em diante.
## Objetivo desta microetapa
Auditar se o ramo `switching_integral` já podia ser aproximado da mesma estrutura local de aplicação usada no parcial, **sem** tocar em:
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`
## Conclusão da auditoria
Sim. A fronteira local segura identificada foi a **montagem do payload final de mutação do lote integral**.
O que estava seguro para extração:
- troca de produto destino e chaves associadas;
- atualização do valor líquido resgatável e principal remanescente;
- atualização de proxy/retorno/liquidez/carência do destino;
- atualização de `carencia_ate`, `data_aplicacao` e custo fiscal acumulado;
- atualização dos campos locais de valuation já calculados fora do helper;
```

</details>

### `relatorios/historico/reorganizacao_local_switching/EXTRACAO_RUNNER_SIMULADOR_CENTRAL_V157.md`

- Título: Extração do runner do simulador central — V157
- Linhas originais: 26

<details>
<summary>Trecho inicial preservado</summary>

```text
# Extração do runner do simulador central — V157
## Objetivo
Extrair apenas `rodar_integracao_funcional_minima_v117` de `nucleo/simulador_central_eventos_v1.py` para um módulo próprio de runner, preservando compatibilidade e sem mover builder de estado, switching ou valoração terminal.
## Mudanças aplicadas
- novo pacote `nucleo/runners/`
- novo módulo `nucleo/runners/simulador_central_runner_v117.py`
- novo `nucleo/runners/README.md`
- `nucleo/simulador_central_eventos_v1.py` agora mantém apenas um wrapper de compatibilidade para `rodar_integracao_funcional_minima_v117`
## Contrato preservado
- nome público preservado: `rodar_integracao_funcional_minima_v117`
- assinatura preservada
- retorno preservado
- builder de estado, switching, valoração terminal e `simular_cenario_eventos_v1` permanecem no simulador central
## Validação
- `compileall` em `nucleo/`, `aplicacao/` e `scripts/`
- import do wrapper antigo e do runner novo
## Observação de baseline
A baseline V156 não estava disponível em `.zip` no ambiente no momento desta execução. A extração foi aplicada sobre o código acessível da V155, mantendo a orientação estrutural definida na auditoria interna da V156 e sem alterar o contrato funcional observado.
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/reorganizacao_local_switching/` pode ser removida se os documentos granulares não tiverem autoridade normativa ativa superior aos documentos atuais.
