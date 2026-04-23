# Mapa de absorção da execução principal do Script 2 (correto)

## Escopo

Este documento mapeia **apenas a orquestração principal do Script 2 correto** enviado pelo usuário, sem migrar o runner legado bruto para o fluxo principal atual.

> Observação de governança: o mapa aberto anteriormente para “Script 2” foi baseado em um arquivo identificado de forma incorreta. A partir da V92, este documento **substitui** aquela leitura e passa a refletir o runner correto de switching, simulação futura e exportação final.

A base desta classificação é o bloco `executar_runner_principal(...)` e suas funções imediatamente associadas no `Script 2.txt` correto, que contém:
- carregamento do snapshot inicial;
- alocação inicial de aportes;
- avaliação de switching e diagnósticos;
- aplicação do modo de execução futuro;
- `simular_futuro(...)`;
- exportação final do Excel.

## Classificação da execução principal do Script 2 correto

### Absorver já (em shadow/diagnóstico)

1. **Benchmark shadow do runner de simulação futura**
   - O núcleo real do Script 2 correto está em `simular_futuro(...)`, que processa contas futuras dia a dia, executa pagamentos, switches e consolida métricas.
   - Absorção recomendada: primeiro em **benchmark shadow reproduzível**, sem substituir o fluxo principal atual.

2. **Auditoria shadow do processamento por evento futuro**
   - O bloco `_processar_conta_futura(...)` e seus fallbacks (`rigido`, `hibrido`, `heuristico`) concentram regra de negócio real de pagamento no futuro.
   - Absorção recomendada: comparação diagnóstica por evento, sem acoplamento ao fluxo operacional vigente.

3. **Governança shadow dos modos de execução futura**
   - `_aplicar_modo_execucao_futuro_final(...)` e `_modo_execucao_futuro_requer_diag_datas()` mostram que o runner legado possuía uma régua explícita de modo futuro (`dinamico`, `rigido_*`).
   - Absorção recomendada: primeiro em camada de auditoria/governança, sem promover diretamente ao fluxo principal.

### Absorver depois

1. **Alocação inicial de aportes do runner legado**
   - `_alocar_aportes_iniciais(...)` pode trazer diferenças relevantes de consolidação por data e foco em rendimento.
   - Deve ser comparada com a baseline atual apenas depois do benchmark shadow do runner futuro estar estabilizado.

2. **Bootstrap legado do snapshot inicial**
   - `_carregar_snapshot_inicial(...)` e a combinação com `carregar_inventario_e_gastos(...)` podem ser úteis para confronto estrutural posterior, mas não são a primeira prioridade.

3. **Exportação final detalhada do runner legado**
   - `_exportar_resultados_excel(...)`, `_montar_relatorio_final_lotes(...)` e impressões consolidadas podem ser comparadas depois, sem migrar a interface antiga como está.

### Não absorver agora

1. **`executar_runner_principal(...)` como orquestrador principal da baseline**
   - O runner legado correto não deve substituir `aplicacao/principal.py` nem os comandos canônicos atuais.

2. **Console/prints do legado como interface principal**
   - A baseline atual já tem sua própria camada de saída organizada.

3. **Acoplamentos globais diretos do runner legado**
   - Globais de modo de execução, produtos globais de simulação e parâmetros auxiliares não devem entrar brutos no fluxo atual.

### Já substituído pela baseline atual

1. **Bootstrap controlado de dados e cache CDI**
   - A baseline atual já possui leitura canônica da planilha, fallback local, atualização do cache CDI e diagnóstico de origem dos dados.

2. **Geração operacional principal do Excel**
   - A baseline atual já gera seu próprio relatório operacional e suas próprias abas canônicas.

3. **Camadas shadow já abertas do legado**
   - `switching_economico_shadow`
- `resolver_hibrido_5p_shadow`
- benchmark shadow agrupado vs. individual do **Script 1**
- auditorias comparativas e residuais do `proxy v3` vigente

## Decisão operacional da V92

A V92 **não absorve funcionalmente** a execução principal do Script 2 correto. Ela apenas corrige o mapa dessa orquestração e redefine a prioridade real da futura migração.

## Prioridade pós-V92

1. **Prioridade aberta na V92:** benchmark shadow do runner de simulação futura do Script 2 correto (**aberto na V92**).
2. Em seguida: auditoria shadow do processamento por evento futuro e dos modos de execução futura.
3. Só depois avaliar se alguma parte do runner legado correto merece migração funcional.
