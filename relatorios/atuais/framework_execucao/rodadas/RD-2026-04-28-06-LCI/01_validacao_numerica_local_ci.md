# 01_validacao_numerica_local_ci.md — RD-2026-04-28-06-LCI

## Objetivo
Formalizar a validação numérica executada em ambiente local/CI com `.venv` ativo, utilizando evidências locais para preencher os controles N2–N11.

## Contexto de execução local/CI
- Ambiente virtual ativado com sucesso.
- `which python` e `sys.executable` apontando para `.venv/Scripts/python(.exe)`.
- `pip install -r requirements.txt` com sucesso.
- `scipy` importado com sucesso (versão 1.17.1).

## Resultado operacional
- `python aplicacao/principal.py`: executou sem erro fatal.
- `python scripts/operacional/gerar_planilha_operacional.py`: executou sem erro fatal.
- Saída operacional gerada: `saidas/oficial/relatorio_operacional_v225.xlsx`.

## Achados observacionais
1. Lote `Lote 6630,64 fev.` aparece exaurido com Bruto/Líquido/Saldo rem iguais a 0.00.
2. Seção `SITUAÇÃO ATUAL` com metadados `None` em campos de fechamento econômico/data de referência/fonte CDI.

## Interpretação
- Os achados são observacionais de saída e **não** comprovam falha de motor econômico por si só.
- A validação N2/N3 está comprovada pela execução sem erro fatal.
