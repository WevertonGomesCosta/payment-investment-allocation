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
- flags de rastreabilidade de origem do evento.

O que **não** devia ser extraído nesta etapa:

- qualquer recálculo econômico ou fiscal;
- qualquer uso novo de `_valor_terminal_estimado_lote`;
- qualquer alteração da semântica do pós-vencimento;
- qualquer mudança na valoração terminal global;
- qualquer mudança no executor central.

## Implementação aplicada

Foi criado o helper local:

- `_construir_payload_mutacao_switching_integral(...)`

E o helper existente:

- `_aplicar_switching_integral_no_lote(...)`

passou a apenas:

1. solicitar o payload neutro de mutação;
2. aplicar `lote.update(payload_mutacao)`.

## Ganho estrutural obtido

A mudança aproximou o ramo integral do padrão local já usado no parcial:

- separação entre **definição do novo estado do lote** e **mutação efetiva**;
- menor assimetria entre os ramos integral e parcial;
- redução de ruído dentro da aplicação do efeito do evento;
- melhor reversibilidade e auditabilidade da etapa.

## Risco residual

Baixo.

O ramo parcial continua mais sensível porque ainda precisa:

- recalcular o residual do lote de origem;
- recalcular `valor_terminal_estimado` do residual com `_valor_terminal_estimado_lote(...)`.

Por isso, nesta etapa, **não** foi promovida fusão entre integral e parcial em um único helper genérico.

## Validação executada

- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m compileall nucleo aplicacao`
- import mínimo do módulo `nucleo.simulador_central_eventos_v1`
- checagem da presença de `_construir_payload_mutacao_switching_integral`

## Resultado

A microextração foi considerada **segura, local, reversível e compatível** com as restrições estruturais congeladas da frente atual.
