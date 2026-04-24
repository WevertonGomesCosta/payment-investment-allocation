# Correção de compatibilidade pandas 3.0 — V199

## Escopo
Correção de incompatibilidade com pandas 3.0 detectada na execução local, mantendo intactos
contrato mestre, modelo oficial, núcleo econômico e estrutura diária por pacotes.

## Problema
Em `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`, linha 580,
a coluna `mudou_vs_v103` era inicializada com valores string (lote_final_planejamento
como string via `.map(lambda ...)`), criando uma coluna `StringDtype`.

Nas linhas subsequentes (587–591), a mesma coluna recebia atribuições booleanas
via `.loc[mask, 'mudou_vs_v103'] = <Series booleana>`.

O pandas 3.0 passou a rejeitar atribuição de booleanos em coluna `StringDtype`,
lançando `TypeError: Invalid value for dtype 'str'. Value should be a string or missing value`.

## Correção
Substituição da inicialização via lambda string por `False` (booleano), alinhando o dtype
da coluna ao seu uso efetivo como flag booleana em todo o restante do código:
- `.sum()` para contagem de mudanças;
- comparação `== True` para filtragem.

A semântica é preservada: linhas sem pagamento_id correspondente no mapa v103
permanecem `False` (sem mudança detectável vs v103), que era o comportamento implícito
anterior quando pandas aceitava booleano em coluna mista.

## Correção de artefatos efêmeros
Remoção de `nucleo/__pycache__` e `.pyc` que haviam sido incluídos acidentalmente
no pacote V198, em violação à cláusula 20.7 do contrato mestre.

## Validação
- `compileall` passou sem erros;
- checagem de release passou (OK - release baseline validado para V199);
- aplicação iniciou sem traceback;
- console exibiu corretamente: baseline, ambiente, dados, pagamentos, ranking e situação atual.
