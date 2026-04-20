# Alocação intradiária por pacote V113

A V113 adiciona a camada experimental `alocacao_intradiaria_pacote_v1` sobre a **V108**, sem alterar a regra de que a **baseline principal da frente central permanece V108**.

## Objetivo

Resolver conjuntamente os pagamentos de uma mesma data para reduzir artefatos de ordem (`despesa_id`) e melhorar a alocação intradiária das mesmas fontes concorrentes.

## Escopo

- não abre solver global completo;
- não reativa a trilha local do bloco crítico;
- usa a mesma hierarquia central por classe (`PROTEGIDA`, `SEMIPROTEGIDA`, `FLEXIVEL`);
- compara poucas políticas candidatas por data e escolhe a melhor por comparador lexicográfico diário.

## Políticas avaliadas por pacote

- `padrao_classe`
- `valor_desc_intraclasse`
- `valor_asc_intraclasse`
- `protegida_maior_valor`
- `semiprotegida_maior_valor`

## Saídas auditáveis

- quadro completo por pagamento na aba `Aloc. intradiaria v1`;
- resumo por data/pacote com política escolhida;
- amostra das mudanças vs `recomputacao_sequencial_central_v1` da V108.

## Interpretação

A V113 deve ser lida como **experimento central intradiário**. Sua promoção depende de auditoria explícita contra a V108.
