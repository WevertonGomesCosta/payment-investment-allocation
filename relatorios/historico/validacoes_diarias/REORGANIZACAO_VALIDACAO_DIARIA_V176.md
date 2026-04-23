# Reorganização do projeto e reforma do runner diário — V176

## Objetivo da V176

A V176 reorganiza a camada documental e a validação diária para evitar regressões entre:
- o contrato executável mínimo da baseline vigente;
- e o objetivo final do projeto, que continua sendo a referência correta para validar pagamentos e switching.

## O que foi feito

1. Foi adicionado o contrato suplementar `CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`.
2. Foi adicionada a auditoria `AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md`.
3. O `README.md`, o `LEIA-ME_OPERACIONAL.md` e o `INDICE_RELATORIOS.md` foram atualizados para destacar essa leitura obrigatória.
4. Foi criado o runner `nucleo/runner_validacao_diaria_operacional_v176.py`.
5. Foi criado o script `scripts/diagnostico/inspecionar_validacao_diaria_operacional_v176.py`.

## Correções materiais do runner em relação à V175

1. A promovibilidade dos cenários passou a usar `promovivel_hibrido` e `escolher_melhor_cenario_promovivel(...)`.
2. O runner agora expõe, por dia:
   - componentes reais do pagamento vencedor;
   - fontes candidatas ordenadas do pagamento;
   - ações candidatas de switching;
   - cenários classificados;
   - melhor cenário promovível;
   - lotes monitorados no estado diário.
3. A saída ficou apta para validar manualmente pagamentos e lotes críticos, como os 3k de março.

## Limite desta etapa

A V176 melhora auditabilidade e governança. Ela não expande, por si só, o espaço de busca do switching para todas as combinações finais desejadas pelo contrato completo do projeto.
