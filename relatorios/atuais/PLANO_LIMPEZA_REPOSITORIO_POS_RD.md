# Plano de limpeza do repositório pós-RD

## Objetivo

Reduzir o repositório ao conjunto operacional necessário para continuidade do projeto, preservando motor, dados oficiais, configuração, saída oficial, documentação mestre e baseline.

## Princípios

1. Não remover código do motor sem verificar importação/uso.
2. Não remover dados oficiais.
3. Não remover contrato mestre, modelo oficial ou baseline.
4. Remover artefatos temporários, duplicados, históricos redundantes e saídas diagnósticas antigas.
5. Fazer a limpeza em commits pequenos e reversíveis.

## Etapas

| Etapa | Escopo | Ação |
|---|---|---|
| L1 | Inventário rastreado | Gerar lista com `git ls-files` |
| L2 | Histórico duplicado | Remover `scripts/historico_raiz/` após preservar o único script exclusivo |
| L3 | Scripts diagnósticos | Separar scripts necessários de temporários |
| L4 | Relatórios antigos | Manter apenas documentos mestres e relatório consolidado |
| L5 | Saídas antigas | Manter apenas saída oficial e READMEs |
| L6 | Validação final | Rodar console/planilha e `git status --short` |

## Arquivos e pastas a preservar

- `aplicacao/`
- `nucleo/`
- `scripts/operacional/`
- `scripts/diagnostico/validar_janela_diaria_operacional_v175.py`
- `dados/dados_financeiros.xlsx`
- `dados/config_atualizado.json`
- `dados/cache_bcb.json`
- `config/`
- `requirements.txt`
- `README.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md`
- `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_RD_2026_04_28.md`
- `saidas/oficial/relatorio_operacional_v225.xlsx`
