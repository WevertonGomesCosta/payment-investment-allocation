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

## O que pode virar helper local agora
Pode virar helper local, com risco baixo:
- despacho entre `aporte_nao_aportado` e `switching_simples` na hora de aplicar o efeito final;
- materialização do novo lote de destino no caso de aporte não aportado;
- despacho entre switching integral e parcial usando parâmetros já calculados.

## O que não deve virar helper nesta etapa
Permanece congelado nesta etapa:
- cálculo de `custo_fiscal`;
- cálculo de `valor_migrado`;
- cálculo de `valor_terminal_estimado`;
- `_valor_terminal_estimado_lote`;
- `_calcular_metrica`;
- `_patrimonio_terminal_proxy`;
- `simular_cenario_eventos_v1`.

## Implementação aplicada
Foi adicionado o helper local:
- `_aplicar_efeito_evento_switching(...)`

Papel do helper:
- aplicar o efeito final do evento no estado após a avaliação local já ter sido concluída;
- preservar `_aplicar_switching_eventos` como orquestrador local;
- reutilizar os helpers já existentes:
  - `_aplicar_switching_integral_no_lote`
  - `_aplicar_switching_parcial_no_lote`

## Escopo preservado
Nenhuma alteração pretendida em:
- contrato funcional;
- lógica econômica do switching;
- semântica do pós-vencimento;
- valoração terminal global;
- executor central.

## Validação executada
- `python -m compileall nucleo aplicacao`
- import de `nucleo.simulador_central_eventos_v1`
- checagem explícita da presença do helper novo

## Leitura arquitetural pós-etapa
Após a V163, `_aplicar_switching_eventos` fica mais claramente dividido em:
1. preparação do evento executável;
2. cálculo econômico-fiscal local;
3. aplicação final do efeito no estado;
4. registro/auditoria/acumulação.

Essa divisão melhora a legibilidade sem avançar prematuramente sobre a valoração terminal global ou sobre a função principal do simulador.
