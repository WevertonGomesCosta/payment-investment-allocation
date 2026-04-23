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
- mutação integral;
- mutação parcial do lote de origem;
- criação do lote destino no parcial;
- aplicação de aporte não aportado.

## O que ainda resta dentro de `_aplicar_switching_eventos(...)`
O que sobra hoje é principalmente:
- coordenação dos dois ramos (`aporte_nao_aportado` vs `switching`);
- extração dos escalares econômicos mínimos por ramo;
- chamada ao registrador com muitos argumentos explícitos.

Isso significa que o resíduo estrutural deixou de ser uma fronteira local clara e passou a ser uma questão de **modelo de coordenação**.

## Por que a função pode ser congelada agora
Ela pode ser congelada agora porque o ganho remanescente exigiria uma das seguintes mudanças, todas mais invasivas do que as microextrações já aprovadas:

### 1. Introduzir um objeto/contexto fechado real por evento
Isso reduziria bastante a assinatura da função e do registrador, mas mudaria a forma como os dados circulam no orquestrador e elevaria o risco de regressão sem ganho funcional imediato.

### 2. Unificar o fechamento dos ramos em um pipeline comum
Isso reduziria a duplicação entre `aporte_nao_aportado` e `switching`, mas exigiria reescrever parte da coordenação local e dos payloads de registro.

### 3. Reestruturar o registrador para consumir payloads já montados
Também reduziria assinatura, porém deslocaria o desenho da fronteira entre preparação, aplicação e instrumentação.

Nenhuma dessas três frentes é mais “microextração local de baixo risco”.

## O que NÃO compensa fazer nesta rodada
Não compensa, agora, fazer nenhuma destas mudanças apenas por limpeza estrutural:
- criar helper só para calcular os escalares mínimos do ramo de aporte;
- criar helper só para calcular os escalares mínimos do ramo de switching;
- criar helper só para chamar `_registrar_pos_execucao_evento_switching(...)`;
- introduzir wrappers cosméticos em torno de 1–2 linhas.

Essas mudanças aumentariam a indireção e a dispersão da leitura sem ganho proporcional de segurança.

## Fronteira de congelamento recomendada
A recomendação é considerar **congelada** a frente estrutural local que envolve:
- `_aplicar_switching_eventos(...)`
- `_aplicar_efeito_evento_switching(...)`
- `_aplicar_switching_integral_no_lote(...)`
- `_aplicar_switching_parcial_no_lote(...)`
- `_aplicar_aporte_nao_aportado_no_estado(...)`
- `_registrar_pos_execucao_evento_switching(...)`

## Camadas que continuam fora de escopo
Permanece correto **não tocar agora** em:
- `_valor_terminal_estimado_lote`
- `_calcular_metrica`
- `_patrimonio_terminal_proxy`
- `simular_cenario_eventos_v1`
- valoração terminal global
- executor central

## Decisão operacional desta versão
- **Sem alteração de código**
- **Congelamento estrutural recomendado para `_aplicar_switching_eventos(...)` nesta rodada**
- Próxima frente, se aberta, já deve ser tratada como reorganização de coordenação acima do nível de microextração local

## Validação executada
- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m compileall nucleo aplicacao`
- checagem estrutural manual do fluxo completo de `_aplicar_switching_eventos(...)`

## Síntese final
A função ainda não é mínima, mas já está **estável, legível e suficientemente segmentada** para encerrarmos esta rodada local com baixo risco. Continuar quebrando agora aumentaria a abstração antes de gerar ganho arquitetural real.
