# Validação local V18

Esta validação foi executada no ambiente disponível antes da entrega da V18.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais observadas

- a nova base fixa foi incorporada ao repositório;
- a aba `Carteira` passou a carregar o universo completo de produtos;
- a aba auxiliar `Todas as Carteiras` deixou de ser necessária no arquivo canônico da baseline;
- o matching de produtos aportados no inventário ficou completo no universo canônico atual;
- a triagem programática v1 do motor (triagem preliminar proxy) foi executada sem abrir replay, núcleo financeiro completo, switching econômico ou otimização profunda;
- a baseline preservou as camadas já abertas: carteira canônica, dados operacionais canônicos, calendário financeiro/taxas base e reconciliação shadow.

## Sinais relevantes da triagem v1

- produtos totais no universo: 178
- elegíveis brutos: 167
- candidatos do motor v1: 49
- recursos disponíveis para aporte: 5680.00
- despesas futuras em 30 dias: 13163.09
- cobertura de caixa em 30 dias: 0.4315

## Observação

A triagem v1 é uma camada auditável de redução do universo de candidatos. Ela ainda não substitui o motor conjunto final e não deve ser interpretada como decisão econômica definitiva.
