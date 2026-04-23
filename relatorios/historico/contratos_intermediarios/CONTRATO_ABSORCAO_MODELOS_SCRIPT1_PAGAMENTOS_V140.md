# Contrato de absorção dos modelos do Script 1 na camada de pagamentos — V140

## Objetivo

Formalizar quais partes do Script 1 entram primeiro no `alocador_pagamentos_terminal_v1` para melhorar a alocação de pagamentos com foco em **patrimônio líquido terminal**, sem reabrir o repositório ao acoplamento do legado inteiro.

## Escopo desta etapa

Esta etapa **não** implementa ainda os modelos do Script 1 dentro do fluxo oficial amplo.
Ela define:
- quais heurísticas entram primeiro;
- qual o papel de cada heurística;
- quais entradas e saídas elas devem consumir;
- o que fica fora do escopo imediato;
- como essas heurísticas serão absorvidas sem substituir a arquitetura canônica já validada.

## Princípio de absorção

O Script 1 não será migrado como bloco monolítico.
A absorção será:
1. **seletiva**;
2. **modular**;
3. **subordinada ao estado canônico atual**;
4. **orientada a patrimônio líquido terminal**;
5. **compatível com o switching já filtrado pelo comparador híbrido**.

## Camada alvo

A absorção deve ocorrer em:
- `nucleo/pagamentos/modelos_script1/`
- `nucleo/alocador_pagamentos_terminal_v1.py`

## Entradas canônicas obrigatórias

As heurísticas do Script 1 devem consumir apenas dados já canônicos do projeto, nunca leitura direta do legado:
- `pagamento`
- `estado_global`
- `config`
- `plano_switching_candidato` já filtrado pelo comparador híbrido
- snapshots de fontes elegíveis (`saldo`, `lote_nao_aportado`, `lote_aportado`, `combinação mínima`)

## Saída contratual mínima

Cada heurística absorvida deve retornar estrutura auditável do tipo:
- `score_modelo`
- `componentes_score`
- `justificativa`
- `promovivel_no_alocador`
- `metadados_modelo`

Essas saídas não substituem diretamente o comparador terminal principal; elas entram primeiro como:
- score auxiliar;
- filtro de triagem;
- desempate;
- ou seletor de modo individual vs combinado.

## Heurísticas que entram primeiro

### H1 — score multifator econômico por fonte (`score_hibrido_5p_fonte`)

Origem material:
- `resolver_hibrido_5p` absorvido em shadow

Função:
- calcular um custo/score econômico por fonte elegível incorporando:
  - IOF proxy;
  - IR proxy;
  - idade fiscal;
  - liquidez/fator líquido;
  - cliff tributário;
  - custo de oportunidade/VPL proxy.

Papel no alocador:
- primeira triagem entre `lote_aportado` e `lote_nao_aportado`;
- desempate entre fontes com cobertura e efeito terminal parecidos;
- ordenação interna das fontes antes de construir combinação mínima.

### H2 — penalidade de cliff e idade tributária (`penalidade_cliff_idade`)

Origem material:
- componente explícita do `resolver_hibrido_5p_shadow`

Função:
- evitar resgates em pontos fiscalmente ruins quando a diferença terminal entre alternativas é pequena.

Papel no alocador:
- desempate fino entre lotes aportados;
- penalização explícita quando o resgate destrói valor por antecipação de cliff.

### H3 — oportunidade VPL/terminal marginal (`oportunidade_vpl_marginal`)

Origem material:
- proxy de oportunidade do `resolver_hibrido_5p_shadow`

Função:
- estimar a perda marginal de manter ou sacrificar uma fonte até o horizonte relevante.

Papel no alocador:
- reforçar a comparação entre fonte localmente disponível e fonte economicamente estratégica;
- melhorar a distinção entre “cobertura fácil” e “cobertura economicamente correta”.

### H4 — seletor individual vs combinado (`seletor_modo_individual_ou_combinado`)

Origem material:
- benchmark shadow agrupado vs individual do Script 1

Função:
- decidir quando faz sentido abrir combinação mínima e quando a decisão individual já domina.

Papel no alocador:
- reduzir a geração desnecessária de combinações;
- abrir combinação mínima apenas quando houver ganho econômico plausível.

### H5 — triagem top-k de fontes para combinação (`triagem_topk_fontes_combinacao`)

Origem material:
- benchmark shadow do resolver híbrido com competição multifonte

Função:
- reduzir o custo combinatório da combinação mínima usando apenas as melhores fontes segundo H1+H3.

Papel no alocador:
- controlar custo computacional;
- manter auditabilidade sem abrir o solver pesado do legado.

## Ordem de absorção

### Fase 1 — absorção imediata
Entram primeiro:
- H1
- H2
- H3

Justificativa:
- melhoram diretamente a qualidade econômica da decisão por fonte sem exigir expansão combinatória pesada.

### Fase 2 — absorção operacional
Entram depois:
- H4
- H5

Justificativa:
- dependem da Fase 1 para ranquear fontes antes de abrir combinações.

## Fora do escopo imediato

Não entram nesta etapa:
- infraestrutura de treino do legado;
- `validacao_walk_forward`;
- wrappers de solver pesado;
- competição completa entre estratégias do Script 1;
- exportação e console legado.

## Regra de governança

Nenhuma heurística absorvida do Script 1 poderá:
- substituir o comparador terminal principal sem auditoria própria;
- promover switching não elegível pelo comparador híbrido;
- ler dados diretamente do legado textual;
- quebrar o contrato canônico atual do projeto.

## Critério de aceite da próxima implementação

A próxima integração será considerada correta se:
1. as heurísticas H1–H3 forem consumidas pelo `alocador_pagamentos_terminal_v1`;
2. o alocador continuar auditável por pagamento;
3. o switching continuar subordinado ao comparador híbrido;
4. houver melhora observável na escolha entre fontes em recorte real sem regressão de cobertura.
