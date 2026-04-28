# 03_decisao_continuidade.md — RD-2026-04-28-03

## Decisão de continuidade (classificação obrigatória)
**BLOQUEADO_POR_DEPENDENCIA_NAO_DECLARADA**

## Justificativa objetiva
1. O caminho de execução dos entrypoints oficiais passa por import de `nucleo.contexto_baseline`, que importa `nucleo.resolver_hibrido_5p_shadow` no topo do módulo.
2. `resolver_hibrido_5p_shadow` exige `scipy` via `from scipy.optimize import linprog`.
3. `requirements.txt` não declara `scipy`.
4. A evidência de RD-02 mostra que a falha ocorre no import, antes da execução econômica relevante (sem inferência de falha do motor).
5. A tentativa de instalação local também foi bloqueada por proxy/rede 403, reforçando o bloqueio operacional do ambiente.

## O que permanece aprovado
- RD-2026-04-28-01 permanece **GO** para escopo documental/estrutural.
- Não há evidência nesta rodada de quebra de regra econômica, função objetivo, pagamento, switching ou saída canônica.

## O que permanece bloqueado
- Reexecução numérica completa N2–N11 enquanto `scipy` não estiver disponível de forma reprodutível no ambiente e/ou manifesto de dependências.

## Ação mínima recomendada (próxima microetapa)
1. Garantir ambiente com `scipy` disponível (pré-instalado ou acesso liberado ao índice de pacotes).
2. Abrir microetapa específica para governança de dependência (sem alterar motor econômico).
3. Reexecutar rodada numérica de validação N2–N11 com evidências novas.
