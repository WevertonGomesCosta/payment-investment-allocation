# Validação local V11

Esta validação foi executada no ambiente disponível antes da entrega da V11.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais observadas

- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- construção da carteira canônica;
- construção do inventário canônico;
- construção dos gastos canônicos;
- saída inicial de console organizada por blocos.

## Avisos estruturais observados

- `existem_taxas_base_nao_positivas`;
- `nenhum_produto_padrao_marcado`;
- `existem_lotes_aportados_sem_match_canonico_de_produto`;
- `existem_recebidos_futuros_nao_disponiveis_hoje`;
- `existem_lotes_nao_aportados_exauridos`;
- `existem_despesas_pagamento_historico`;
- `existem_despesas_futuras_ou_pendentes`.

Esses avisos não bloquearam a baseline nesta etapa porque a abertura do bloco foi restrita à camada canônica e estrutural.
