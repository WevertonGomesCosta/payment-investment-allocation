# Baseline fixa V75

## Objetivo desta versão

Derivar a V74 de forma cirúrgica para executar um **mapeamento de absorção legado** dos `Script 1.txt` e `Script 2.txt`, alinhando README, contrato, backlog e relatórios vigentes ao estado real do repositório, sem alterar o motor financeiro, sem reabrir o `proxy econômico v3` congelado e sem abrir `multifonte v1`.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do relatório vigente `MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_mapa_absorcao_legado.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog e do índice documental com a realidade da V75;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V75. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na identidade da baseline, na documentação vigente, no diagnóstico do mapa legado e nos nomes de artefatos.

## Critério desta baseline

A V75 não abre nova frente funcional. Ela consolida um mapa de absorção legado para os Scripts 1 e 2, separando o que deve migrar já, o que deve migrar depois, o que não deve migrar e o que já foi substituído pela baseline.
