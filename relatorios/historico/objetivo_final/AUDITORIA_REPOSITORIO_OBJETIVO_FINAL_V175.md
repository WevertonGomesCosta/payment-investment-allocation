# Auditoria do repositório focada no objetivo final — V175

## Referências contratuais revisadas
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `relatorios/atuais/CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`
- `relatorios/atuais/MAPA_HEURISTICAS_PRIORITARIAS_SCRIPT1_V140.md`
- `relatorios/atuais/AUDITORIA_POS_VENCIMENTO_V145.md`

## Síntese executiva
A V175 já contém peças importantes do motor conjunto, mas ainda não atende integralmente o objetivo final do projeto. O desvio atual não é apenas um bug de saída; é um desalinhamento entre:

1. o **contrato final do projeto** (motor conjunto temporal, auditável, orientado a patrimônio terminal);
2. a **camada executável atual** (ainda fortemente monofonte/local no pagamento e restritiva no switching);
3. a **saída de validação** (insuficiente para auditoria por lote/dia/cenário).

## O que já está coerente com a metodologia
- A decisão por pagamento não está modelada como “aportar por aportar”; o alocador tenta ranquear fontes por perda terminal, custo fiscal, liquidez e penalidade estratégica.
- Há previsão contratual e estrutural para timeline global, switching temporal autônomo e recomputação sequencial central.
- A normalização pós-vencimento já foi aberta no simulador central e no runner diário.
- O comparador híbrido já distingue cenários terminalmente aceitáveis de cenários apenas operacionalmente bons.

## Onde a implementação ainda diverge do objetivo final

### 1. Saída operacional ainda não é auditável por lote/fonte no nível exigido
O runner diário V175 resume pagamentos em campos agregados e perde a decomposição real da fonte vencedora.

Consequências observáveis:
- descrição de pagamento vazia em parte da saída;
- valor do pagamento aparecendo como `0.0` em pontos críticos;
- fonte vencedora reduzida a `combinacao_minima_controlada` sem detalhar os lotes componentes;
- ausência da trilha diária dos switchings avaliados, promovidos e bloqueados.

Impacto:
- inviabiliza validar manualmente se o lote escolhido para pagamento foi economicamente correto;
- viola o requisito de auditabilidade por lote/data/fonte do contrato final.

### 2. O alocador já tenta minimizar custo terminal, mas a leitura operacional do resultado ficou encoberta
No `alocador_pagamentos_terminal_v1`, a escolha final compara candidatos por vetor lexicográfico que inclui:
- déficit e cobertura;
- perda terminal estimada;
- penalidade estratégica do lote;
- penalidade de liquidez;
- custo fiscal;
- heurísticas H1–H3 do Script 1.

Portanto, a regra correta não é “sempre pegar o lote com menor taxa nominal”.
A regra correta é:
- escolher a fonte com **menor custo de oportunidade terminal**, respeitando a hierarquia central.

Na prática, isso frequentemente tende a usar primeiro:
- saldo disponível;
- caixa/não aportado com menor custo de oportunidade;
- lote aportado com menor proxy terminal, menor destruição estratégica e menor custo fiscal;
mas **não** como regra fixa de “menor rendimento sempre”.

Desvio atual:
- quando o vencedor é `combinacao_minima_controlada`, a saída não mostra os componentes da combinação, então a otimização existe parcialmente no código, mas não fica auditável na interface de validação.

### 3. O switching ainda está abaixo do contrato final
O contrato final exige switching:
- temporal autônomo;
- fora dos dias de pagamento;
- individual por lote;
- agrupado;
- integral;
- parcial quando permitido.

Na V175:
- o runner diário já avalia switching em dias sem pagamento;
- porém o planejador ainda gera principalmente `switching_simples` e `aporte_nao_aportado`;
- as famílias efetivamente observadas na validação ficaram limitadas a `individual_integral_parametrizado` e `agrupado_integral_parametrizado`;
- a trilha executável ainda não entrega “todas as combinações possíveis” nem switching parcial promovível de forma contratual.

Impacto:
- o espaço de busca de switching ainda está estreito demais para o objetivo final do repositório.

### 4. O pós-vencimento crítico dos lotes 3k mar continua sendo a prova de fogo metodológica
A auditoria documental do próprio repositório já havia identificado que o caso dos lotes:
- `Lote 3000 mar. V`
- `Lote 3000 mar. B`

exige tratamento operacional explícito de rollover no vencimento.

Na V175 houve avanço com a normalização pós-vencimento no estado diário, mas ainda faltam dois pontos para fechar o contrato final:
1. o lote vencido precisa entrar de forma auditável como caixa disponível do dia;
2. o motor precisa competir esse caixa contra switching individual, agrupado e integral em janela curta, com saída rastreável.

Ou seja:
- a semântica do vencimento começou a ser tratada;
- mas a exploração econômica posterior ainda está incompleta.

### 5. Há desalinhamento entre “contrato executável vigente” e “objetivo final do projeto”
O repositório separa explicitamente:
- o que já é executável hoje na frente central;
- e o objetivo final do motor conjunto.

Hoje, parte do comportamento observado na V175 ainda reflete a camada executável mais limitada:
- F1 monofonte/local;
- combinação mínima controlada;
- switching filtrado por promoção híbrida antes de competir no fluxo.

Isso não é ilegítimo como etapa, mas não pode mais ser tratado como suficiente para validar o objetivo final.

## Diagnóstico principal desta auditoria
A V175 já serve como base técnica de continuação, mas **não pode ser considerada ainda uma validação adequada do objetivo final do projeto**.

O principal problema atual não é mais só “bug temporal”.
Os problemas agora estão em três níveis:

1. **auditabilidade insuficiente da saída**;
2. **espaço de busca de switching incompleto**;
3. **integração ainda incompleta entre decisão diária e otimização terminal por lote**.

## Ordem correta das próximas frentes

### Frente 1 — obrigatória e imediata
Reformar a saída do runner diário para devolver, por dia:
- pagamentos do dia;
- lote(s) efetivamente escolhidos;
- valor usado por lote;
- saldo residual por lote após pagamento;
- switchings candidatos do dia;
- classe do comparador híbrido;
- motivo do bloqueio/promoção;
- melhor cenário individual;
- melhor cenário agrupado;
- melhor cenário integral.

### Frente 2 — obrigatória e central
Expandir a geração/competição de switching para contemplar explicitamente:
- individual por lote;
- agrupado controlado com combinações relevantes;
- integral;
- parcial quando permitido.

### Frente 3 — crítica para o caso 3k mar
Materializar uma auditoria operacional curta específica da janela:
- 2026-05-03
- 2026-05-04
- 2026-05-05
- 2026-05-06

com foco em:
- transformação dos 3k mar em caixa disponível no vencimento;
- competição entre rollover imediato e uso em pagamentos;
- comparação contra alternativas agrupadas viáveis.

### Frente 4 — só depois
Reabrir a promoção de switching no fluxo oficial diário, já com saída auditável e espaço de busca ampliado.

## Conclusão
Para seguir fielmente a metodologia já definida no projeto, a próxima etapa não deve ser “rodar de novo o mesmo teste”.
Deve ser:

1. auditar e reformar a **saída operacional diária**;
2. abrir o **espaço de busca de switching** no nível exigido pelo contrato final;
3. usar a janela crítica dos lotes `3k mar` como teste de prova do modelo.
