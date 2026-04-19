# Benchmark shadow do runner de simulação futura do Script 2

## Escopo

Este benchmark reproduz, em modo shadow e auditável, o núcleo da execução futura do **Script 2 correto** enviado pelo usuário, inspirado principalmente no bloco `simular_futuro(...)` e na sua lógica de processamento dia a dia.

Nesta baseline, a absorção ocorre sem migrar o runner legado bruto para o fluxo principal.

## Resultado observado na baseline atual

- pagamentos futuros avaliados: **152**
- pagamentos totalmente cobertos no runner shadow: **15**
- pagamentos totalmente cobertos na decisão vigente: **152**
- pagamentos com multifonte no runner shadow: **3**
- pagamentos com mudança de lote principal vs. decisão vigente: **150**
- recomendação do benchmark: **vigente**

## Leitura técnica

1. O runner futuro shadow é muito mais agressivo do que a baseline vigente e altera o lote principal em quase todo o universo analisado.
2. Embora ele reduza excesso de forma quase sistemática, perde cobertura integral em uma parte substancial dos pagamentos futuros.
3. O uso de multifonte aparece, mas ainda em subconjunto pequeno.
4. Nesta etapa, a informação útil é diagnóstica: o runner legado correto não pode ser promovido ao fluxo principal sem auditorias adicionais por evento e por modo de execução futura.

## Decisão operacional

A baseline mantém a decisão vigente como referência operacional.
O runner futuro do Script 2 correto permanece apenas como benchmark shadow externo.

## Situação na V92

A V92 abre essa régua shadow como primeira absorção útil da execução principal correta do Script 2, mantendo o runner legado bruto fora do fluxo principal.
