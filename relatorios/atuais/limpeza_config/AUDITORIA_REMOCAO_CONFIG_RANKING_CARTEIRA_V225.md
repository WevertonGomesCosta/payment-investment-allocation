# Auditoria de remoção segura da pasta `config/` — ranking da Carteira — V225

## Identificação

- Baseline operacional: V225
- Tipo: microetapa estrutural/organizacional
- Escopo: decidir e executar a remoção dos arquivos físicos de ranking em `config/`
- Fonte canônica consolidada: `dados/config_atualizado.json::ranking_carteira`

## Objetivo

Remover os arquivos físicos abaixo somente após confirmar que o contrato e os parâmetros do ranking da Carteira passaram a ser lidos do config canônico:

- `config/carteira_contract_v123.json`
- `config/fixed_parameters_ranking_carteira.json`

## Estado antes da remoção

O contrato e os parâmetros já haviam sido migrados para:

```text
ranking_carteira.contract
ranking_carteira.fixed_parameters
```

no arquivo:

```text
dados/config_atualizado.json
```

O módulo `nucleo/ranking_carteira_estabilizado.py` ainda mantinha fallback físico para os arquivos em `config/`, o que impedia a remoção segura da pasta.

## Auditoria de referências

A busca por referências aos nomes físicos indicou que as referências operacionais estavam concentradas no próprio módulo de ranking. As demais ocorrências eram documentais/históricas, localizadas em relatórios e inventários.

Classificação:

| Referência | Classe | Decisão |
|---|---|---|
| `nucleo/ranking_carteira_estabilizado.py` | dependência operacional/fallback ativo | remover fallback físico antes de excluir arquivos |
| `relatorios/atuais/limpeza_config/INVENTARIO_USO_CONFIG_V225.md` | documentação/auditoria | preservar |
| `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md` | documentação/auditoria histórica | preservar |
| `relatorios/atuais/RELATORIO_CONSOLIDADO_CONTRATOS_INTERMEDIARIOS_HISTORICO.md` | documentação/auditoria histórica | preservar |
| `relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv` | inventário histórico | preservar |

## Alteração aplicada no código

`nucleo/ranking_carteira_estabilizado.py` foi alterado para exigir o bloco canônico:

```text
ranking_carteira.contract
ranking_carteira.fixed_parameters
```

A função `_resolver_contrato_e_parametros_ranking()` agora:

1. lê `ranking_carteira.contract` do config canônico;
2. lê `ranking_carteira.fixed_parameters` do config canônico;
3. lança erro explícito se algum dos dois blocos estiver ausente;
4. não tenta mais ler arquivos físicos da pasta `config/`.

Com isso, o config canônico passa a ser a fonte operacional única do ranking da Carteira.

## Arquivos removidos

Foram removidos os arquivos:

```text
config/carteira_contract_v123.json
config/fixed_parameters_ranking_carteira.json
```

Como o Git não versiona diretórios vazios, a pasta `config/` deixa de existir no repositório se não houver outros arquivos nela.

## Commits da microetapa

- `78cdd003261629b48703f1ca5e097201f9b4fedb` — remove fallback físico do ranking da Carteira
- `1f2a90d6e3c36210bc1966be865a932643f037cf` — remove `config/carteira_contract_v123.json`
- `93f7323de65b7d9585c0240271a874b65fc177ae` — remove `config/fixed_parameters_ranking_carteira.json`

## Restrições respeitadas

Esta microetapa não alterou:

- metodologia do ranking;
- cálculo financeiro;
- replay;
- pagamentos;
- switching;
- cabeçalhos da planilha;
- estilos da planilha;
- identidade da baseline.

## Validação necessária no ambiente local

Como a execução completa depende da planilha local/download e do ambiente do usuário, a validação final deve ser executada localmente:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios de aceite:

1. execução sem erro;
2. saída operacional gerada em `saidas/oficial/relatorio_operacional_v225.xlsx`;
3. ranking top 10 sem alteração observável;
4. console sem alteração econômica observável;
5. `ranking_carteira.auditoria` apontando para:
   - `dados/config_atualizado.json::ranking_carteira.contract`;
   - `dados/config_atualizado.json::ranking_carteira.fixed_parameters`.

## Plano de rollback

Se a execução local falhar por ausência do bloco `ranking_carteira` no config canônico:

1. restaurar os arquivos removidos a partir do histórico Git;
2. restaurar temporariamente o fallback físico no módulo de ranking;
3. corrigir `dados/config_atualizado.json`;
4. repetir a validação.

## Conclusão

A remoção dos arquivos físicos da pasta `config/` foi aplicada porque a dependência operacional foi eliminada antes da exclusão. A fonte operacional única do ranking da Carteira passa a ser `dados/config_atualizado.json::ranking_carteira`.
