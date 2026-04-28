# 03_decisao_hotfix_review.md — RD-2026-04-28-04A

## Classificação final
**HOTFIX_RASTREABILIDADE_APROVADO**

## Justificativa
1. Comandos frágeis com `|` sem aspas foram substituídos por múltiplos `-e` no `rg`.
2. Padrões multi-palavra foram convertidos para literais com aspas e `-F` quando aplicável.
3. Placeholders `.../evidencias/...` foram substituídos por caminhos relativos completos reexecutáveis.
4. Reexecução mínima dos comandos alterados confirmou reprodutibilidade dos PASS de RD-01 e reprodução controlada da falha esperada por `scipy` em RD-02.

## Restrições
Nenhuma regra econômica, lógica de pagamento/switching, função objetivo, dados oficiais, cache, saída canônica ou `requirements.txt` foi alterada nesta microetapa.
