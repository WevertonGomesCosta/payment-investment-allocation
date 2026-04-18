# Mapa de absorção da execução principal do Script 2

## Escopo

Este documento mapeia **apenas a orquestração principal** do Script 2 legado enviado pelo usuário, sem migrar o runner legado bruto para o fluxo principal atual.

A base desta classificação é o bloco `if __name__ == "__main__":` do Script 2 original, que contém bootstrap de dados, escolha interativa de treino, teste agrupado vs. individual, competição final entre estratégias, exportação por estratégia e exibição da situação atual da melhor estratégia.

## Classificação da execução principal do Script 2

### Absorver já (em shadow/diagnóstico)

1. **Teste agrupado vs. individual como benchmark de governança**
   - No legado, `GENETICA_5P` é executada em `dados_contas_agr` e `dados_contas_ind`, e o resultado define o `modo_analise_forcado`.
   - Absorção recomendada: benchmark reproduzível e desacoplado, sem substituir automaticamente o modo vigente da baseline.

2. **Competição final entre estratégias legadas em modo shadow**
   - O legado compara `PENALIDADE_5P`, `HIBRIDO_5P`, `ECONOMICA_VPL`, `ECONOMICA_CLIFF`, `HEURISTICA` e `GENETICA_5P`.
   - Absorção recomendada: comparação shadow da régua legada, sem acoplamento ao fluxo principal atual.

3. **Comparativo entre melhor estratégia legada e baseline atual**
   - O legado fecha selecionando a melhor estratégia e exibindo sua situação atual.
   - Absorção recomendada: auditoria comparativa controlada contra a baseline vigente, sem promover automaticamente o vencedor para o fluxo principal.

### Absorver depois

1. **Exportação detalhada por estratégia**
   - O legado salva extrato, auditoria do extrato, carteira final, resumo, situação atual e abas específicas de switching para cada estratégia.
   - Isso pode ser útil no futuro, mas só depois que a comparação shadow estiver estabilizada.

2. **Validação walk-forward integrada ao runner**
   - O legado usa `validacao_walk_forward(...)` para compor o score final das estratégias.
   - Absorção recomendada apenas depois da camada comparativa shadow estar madura.

3. **Leitura de parâmetros salvos para perfis legados**
   - O runner carrega e salva parâmetros para 5p e refinamento.
   - Absorção adiada enquanto a baseline não reabrir treino ou seleção de parâmetros.

### Não absorver agora

1. **Interatividade por `input()`**
   - O runner legado depende de escolhas manuais de modo de treino e perfil.
   - Não deve entrar no fluxo principal atual.

2. **Treino profundo/refinamento pesado como caminho principal**
   - O legado permite treinamento demorado e refinamento de parâmetros.
   - Isso não é o gargalo atual da baseline.

3. **Runner legado bruto como orquestrador principal**
   - Não deve substituir `aplicacao/principal.py` nem os comandos canônicos atuais.

### Já substituído pela baseline atual

1. **Bootstrap controlado de dados**
   - A baseline atual já possui leitura canônica, cache CDI, fallback local e geração operacional própria.

2. **Saída operacional principal**
   - A baseline atual já gera `relatorio_operacional_v87.xlsx` e suas próprias seções/abas canônicas.

3. **Camadas shadow específicas já abertas**
   - `switching_economico_shadow`
   - `resolver_hibrido_5p_shadow`
   - auditorias comparativas do `proxy v3` vigente

## Decisão operacional da V87

A V87 **não absorve funcionalmente** a execução principal do Script 2. Ela apenas registra o mapa de absorção dessa orquestração e define a prioridade correta de futura migração.

## Prioridade pós-V87

1. Abrir, se necessário, um **benchmark shadow do teste agrupado vs. individual**.
2. Depois, abrir uma **competição final shadow entre estratégias legadas**.
3. Só então avaliar se alguma parte do runner legado merece migração funcional.
