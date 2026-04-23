# Auditoria residual das divergências materiais — proxy v3 vs benchmark híbrido shadow

## Escopo

Esta auditoria residual aprofunda apenas os casos de **divergência material** já identificados na comparação entre a `decisao_local_v1` vigente com `proxy econômico v3` e o benchmark shadow do `resolver_hibrido_5p`.

Ela **não** altera o fluxo principal e **não** substitui automaticamente o `proxy v3`.

## Resultado consolidado da V79

- pagamentos comparados: **152**
- divergências materiais: **113**
- casos classificados como **potencial_reaproveitamento_proxy_v3**: **42**
- casos classificados como **divergência estrutural do benchmark híbrido**: **71**
- casos multifonte no benchmark dentro das divergências materiais: **2**

## Leitura metodológica

A auditoria residual confirma que o benchmark híbrido reduz excesso quase sistematicamente, mas que isso não se traduz, na maioria das divergências materiais, em melhora da métrica comum do `proxy v3`.

Portanto, a divergência do benchmark híbrido deve ser lida principalmente como:

1. **régua externa de auditoria**, útil para mostrar trade-offs de excesso;
2. **fonte de possíveis padrões reaproveitáveis**, mas apenas nos casos em que também melhora a métrica comum do `proxy v3`;
3. **não** como evidência suficiente para substituir a decisão monofonte vigente.

## Padrões residuais principais

### 1. Potencial reaproveitamento no proxy v3

Os casos reaproveitáveis concentram-se onde o benchmark muda o lote principal **e** melhora simultaneamente a métrica comum do `proxy v3` e o excesso líquido.

Na V79, esses casos aparecem sobretudo em transições do tipo:
- `Lote 3000 mar. B -> Lote 8500 mar.`

### 2. Divergência estrutural do benchmark híbrido

Os casos estruturais concentram-se onde o benchmark reduz excesso, mas piora a métrica comum do `proxy v3`.

Na V79, isso aparece principalmente em transições do tipo:
- `Lote 3000 mar. B -> Lote 6630,64 fev.`
- `Lote 6630,64 fev. -> Lote 8500 mar.`

## Conclusão operacional

A V79 **não** reabre o `proxy v3`.
A leitura atual é:

- manter o `proxy v3` congelado como decisão vigente;
- manter o benchmark híbrido como camada shadow externa;
- só considerar refino do proxy local se os **42 casos reaproveitáveis** mostrarem um padrão realmente consistente em uma próxima etapa cirúrgica.
