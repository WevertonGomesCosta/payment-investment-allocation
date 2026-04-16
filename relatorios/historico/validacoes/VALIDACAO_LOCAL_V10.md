# Validação local V10

Esta validação foi executada no ambiente disponível antes da entrega da V10.

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
- exibição da data de referência no console;
- construção da carteira canônica inicial;
- geração de `produto_key` para todos os produtos da aba `Carteira`;
- validação estrutural da aba `Carteira` sem erro fatal.

## Avisos observados na validação estrutural da aba `Carteira`

- `existem_taxas_base_nao_positivas`;
- `nenhum_produto_padrao_marcado`.

Esses avisos foram mantidos como sinalização estrutural para as próximas auditorias, sem abrir ainda domínio financeiro ou de produto além do escopo desta etapa.
