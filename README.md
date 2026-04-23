# payment-investment-allocation

Baseline atual: **V125**.

Esta derivação amplia a auditoria temporal do cenário conjunto com uma grade multihorizonte mais rica, para medir quando o switching realmente sobrevive economicamente e quando o baseline sem switching volta a dominar.

# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, recebidos, aportes e switching** com base única, `config` central e rastreabilidade por lote.

**Baseline entregue do repositório:** V125  
**Baseline central/contratual da frente principal:** V108

A V125 preserva a V117 como contrato do motor conjunto temporal, mantém o ranking Carteira-only estabilizado da V123, a simulação central controlada longa da V124 e acrescenta uma **auditoria multihorizonte do cenário conjunto**, para evitar decisões baseadas em poucos recortes temporais isolados.

## Objetivo final do projeto

Construir um **motor conjunto, auditável e economicamente coerente** para:

- pagamentos;
- recebidos;
- aportes;
- futuras decisões de switching.

A decisão final deve buscar **maximizar o patrimônio líquido terminal**, respeitando:

- cobertura dos pagamentos;
- liquidez e carência;
- tributação;
- precedência intradiária parametrizada;
- preservação de pagamentos protegidos;
- auditabilidade completa por lote/fonte.

O projeto **não** tem como objetivo final otimizar isoladamente um único pagamento ou uma janela local sem reconexão com o cenário conjunto.

## O que a V122 faz

- preserva o `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md` como referência do desenho da nova camada central;
- integra minimamente:
  - `planejador_switching_temporal_v1`;
  - `alocador_pagamentos_terminal_v1`;
  - `simulador_central_eventos_v1`;
  - `avaliador_cenarios_conjuntos_v1`;
- executa um recorte curto real de datas críticas com vetor terminal auditável;
- recalibra a triagem do `planejador_switching_temporal_v1` por custo fiscal + reprojeção terminal + carência incremental;
- expande o planejador para múltiplos destinos elegíveis por lote com o mesmo critério econômico mínimo real;
- mantém a baseline central V108 e a camada operacional V116 sem reabrir a lógica econômica principal.

## Camadas vigentes

### Frente central
- `caixa_recebidos_auditaveis`
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v1`

### Camada temporal mínima integrada
- `planejador_switching_temporal_v1`
- `alocador_pagamentos_terminal_v1`
- `simulador_central_eventos_v1`
- `avaliador_cenarios_conjuntos_v1`

### Camada operacional por conta
- `motor_recomendacao_pagamentos_switching_v1`

### Trilha experimental local
- `heuristica_conjunta_parcial_bloco_critico`
- `planejamento_conjunto_local_bloco_critico_v1`
- `microplanejamento_conjunto_bloco_critico_v2`

## Documentos ativos

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `relatorios/atuais/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md`
- `relatorios/atuais/BASELINE_FIXA_V128.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V128.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V128.md`
- `relatorios/atuais/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md`
- `relatorios/atuais/EXPANSAO_MULTIDESTINO_PLANEJADOR_SWITCHING_TEMPORAL_V121.md`
- `relatorios/atuais/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md`
- `relatorios/atuais/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`
- `relatorios/INDICE_RELATORIOS.md`


Documento novo desta derivação: `relatorios/atuais/AUDITORIA_MULTIHORIZONTE_CENARIOS_TEMPO_V125.md`.


## V130

A V130 reroda a janela crítica `2026-04-30` a `2026-05-20` com validação parametrizada de aplicação mínima/máxima do produto de destino, eliminando falsos positivos de ticket no switching diário.

## V129

- adiciona grade diária de data ótima de switching com estado condicional por dia;
- suporta switching isolado e agrupado em modo integral e parcial 50%;
- prepara execução em blocos e consolidação para janelas longas quando o ambiente interativo ficar pesado.


## V131

A V131 adiciona uma auditoria cirúrgica do bloco `2026-05-13` a `2026-05-20` e mostra que o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` não é superior em patrimônio líquido terminal ao baseline. Ele vence a métrica central apenas porque reduz déficit líquido sem piorar `PROTEGIDA` ou cobertura.


## Atualização V132

A V132 introduz um comparador híbrido para classificar cenários diários em vencedor operacional, vencedor terminal ou vencedor híbrido aceitável, bloqueando promoção automática de switchings que piorem patrimônio líquido terminal frente ao baseline.
