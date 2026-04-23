# Contrato V117 — motor conjunto temporal

## Objetivo da V117

A V117 introduz uma camada **documental/técnica mínima e executável** para o futuro motor conjunto temporal do projeto.

Esta versão **não** substitui a baseline central V108 e **não** promove a camada operacional por conta como motor final. O papel da V117 é formalizar os contratos mínimos de quatro módulos centrais:

- `planejador_switching_temporal_v1`
- `alocador_pagamentos_terminal_v1`
- `simulador_central_eventos_v1`
- `avaliador_cenarios_conjuntos_v1`

## Princípio metodológico

A V117 fixa que:

1. o switching é uma decisão **temporal autônoma**, não subordinada ao vencimento da conta;
2. a fonte de pagamento deve ser escolhida pelo **menor custo de oportunidade terminal**;
3. pagamentos, recebidos, aportes e switching devem operar sobre o **mesmo estado global auditável**;
4. a decisão correta não é a de menor custo local, e sim a de **menor perda de patrimônio líquido terminal** sob restrições operacionais.

## Estado global mínimo compartilhado

Os quatro módulos da V117 devem aceitar ou produzir estruturas compatíveis com um mesmo estado global, contendo no mínimo:

- `data_referencia`
- `data_evento_corrente`
- `saldo_disponivel_geral`
- `recebidos_nao_aportados_disponiveis`
- `recebidos_futuros`
- `lotes_aportados`
- `pagamentos_futuros`
- `eventos_switching_agendados`
- `eventos_aporte_agendados`
- `bases_fiscais_por_lote`
- `liquidez_por_lote`
- `carencia_por_lote`
- `historico_decisoes`
- `metricas_acumuladas_cenario`

## Contrato do `planejador_switching_temporal_v1`

### Entrada mínima

- `estado_global`
- `config`
- `horizonte_planejamento`
- `filtros_eventos`
- `limite_candidatos_por_data`

### Saída mínima

Coleção auditável de ações candidatas com, no mínimo:

- `id_acao`
- `tipo_acao`
- `data_acao`
- `lote_origem_id`
- `produto_origem`
- `produto_destino`
- `valor_bruto_origem`
- `valor_liquido_resgatavel`
- `custo_fiscal_estimado`
- `perda_liquidez_estimada`
- `ganho_terminal_proxy_estimado`
- `impacto_pagamentos_futuros_estimado`
- `justificativa`
- `elegivel`

### Regra mínima

A V117 exige uma ação neutra explícita de `manter` e não autoriza promover qualquer candidato de switching como decisão final nesta etapa.

## Contrato do `alocador_pagamentos_terminal_v1`

### Fontes candidatas obrigatórias

- `saldo_disponivel`
- `lote_nao_aportado`
- `lote_aportado`
- `combinacao_minima_fontes`
- `sem_fonte_viavel`

### Critério comparativo mínimo

Cada fonte deve ser comparada por um vetor lexicográfico auditável com os seguintes componentes:

1. violação de `PROTEGIDA`
2. déficit líquido total
3. falta de cobertura integral
4. perda de patrimônio líquido terminal
5. destruição estratégica de lote/fonte
6. deterioração de liquidez futura
7. custo fiscal imediato
8. custo operacional

## Contrato do `simulador_central_eventos_v1`

Nesta entrega, o simulador deve apenas:

- normalizar o estado de entrada;
- receber eventos candidatos;
- devolver trilha auditável mínima;
- preservar estado inicial e estado final estimado;
- explicitar que ainda se trata de um **esqueleto não econômico**.

## Contrato do `avaliador_cenarios_conjuntos_v1`

Nesta entrega, o avaliador deve:

- aceitar cenários já materializados;
- normalizar a métrica central mínima;
- produzir ranking determinístico por vetor lexicográfico;
- devolver o melhor cenário apenas como resultado **documental/técnico mínimo**.

## Relação com a baseline vigente

- **baseline central/contratual da frente principal:** V108
- **baseline operacional anterior:** V116
- **baseline do repositório entregue nesta etapa:** V117

A V117 introduz apenas a camada contratual/técnica mínima do futuro motor conjunto temporal. Não altera a lógica econômica vigente do fluxo principal.
