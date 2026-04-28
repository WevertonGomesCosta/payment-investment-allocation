# 01_hotfix_rastreabilidade_comandos.md — RD-2026-04-28-04A

## Objetivo
Corrigir exclusivamente a reprodutibilidade/rastreabilidade dos comandos registrados nos artefatos CSV do framework, conforme comentários do Codex Review.

## Escopo aplicado
- Arquivos corrigidos:
  - `relatorios/atuais/framework_execucao/rodadas/RD-2026-04-28-01/02_matriz_checklist.csv`
  - `relatorios/atuais/framework_execucao/rodadas/RD-2026-04-28-02/02_matriz_validacao_numerica.csv`
- Verificação de templates/base:
  - `relatorios/atuais/framework_execucao/02_matriz_checklist.csv` (sem comandos preenchidos; nenhum hotfix necessário)

## Problemas corrigidos
1. Alternância com `|` sem escape/aspas no shell (potencial pipeline acidental).
2. Padrões literais multi-palavra sem aspas em `rg -e`.
3. Placeholder não executável `.../evidencias/...` em comandos de RD-02.

## Estratégia de correção
- Padronização para `rg -n -e "padrao1" -e "padrao2" arquivo`.
- Para literal multi-palavra, uso de `rg -n -F -e "padrão" arquivo`.
- Substituição de placeholders por caminhos relativos completos do repositório.

## Validação mínima executada
- Reexecução dos comandos corrigidos em RD-01 (itens alterados), com retorno de evidências em arquivos-alvo.
- Reexecução dos comandos corrigidos de RD-02 N2/N3 com caminhos reais, reproduzindo o mesmo erro esperado por ausência de `scipy`.

## Restrições preservadas
- Sem alteração em motor econômico, lógica de pagamentos/switching, função objetivo, dados oficiais, cache, saída canônica, contrato e manifesto de dependências.
