# Benchmark shadow do teste agrupado vs individual do Script 1

## Escopo

Este benchmark reproduz, em modo shadow e auditável, a camada de governança do **Script 1** legado que comparava execução **agrupada por dia** versus **individual**.

> Correção de identidade vigente: este benchmark havia sido inicialmente atribuído ao Script 2 por causa de um arquivo enviado com identificação incorreta. A partir da V91, ele deve ser lido como benchmark da execução principal do **Script 1**.

Nesta baseline, a absorção ocorre sobre a decisão local vigente com `proxy v3`, sem migrar a competição final entre estratégias nem o runner legado bruto.

## Resultado observado na baseline atual

- pagamentos individuais avaliados: **152**
- datas agrupadas avaliadas: **97**
- datas com mudança de lote dominante: **9**
- modo recomendado no benchmark shadow: **individual**

## Leitura técnica

1. O modo **individual** mantém cobertura integral em **152/152** pagamentos.
2. O modo **agrupado** reduz excesso em várias datas, mas perde cobertura integral em uma delas.
3. A recomendação agrupado vs individual é apenas uma régua de governança inspirada no **Script 1** legado.
4. Ela não substitui o fluxo principal nem reabre o `proxy v3` congelado.

## Decisão operacional

A baseline mantém o **modo individual** como recomendação shadow vigente.
O modo agrupado permanece apenas como benchmark comparativo, útil para auditoria fina das datas em que há mudança de lote dominante.

## Situação na V91

A V91 preserva este benchmark shadow, mas corrige sua vinculação documental: ele passa a ser explicitamente tratado como parte da execução principal do **Script 1**, e não do Script 2.
