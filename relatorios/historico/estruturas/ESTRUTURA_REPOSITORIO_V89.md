# Estrutura do repositório V89

## Camada nova da V89

- `scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py`;
- `scripts/inspecionar_mapa_execucao_principal_script2.py`;
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`.

## Papel da V89

A V89 não abre nova camada funcional; ela atualiza os arquivos canônicos de dados, ajusta o `.gitignore` e revalida a camada diagnóstica já existente do benchmark shadow agrupado vs individual.

Nenhum módulo funcional do motor foi alterado.


## Ajustes incrementais da V89

- atualização dos arquivos canônicos de dados;
- ampliação do `.gitignore` para evitar versionamento acidental de `Script 1.txt`, `Script 2.txt` e `code/`.
