# 01_correcao_dependencia_scipy.md — RD-2026-04-28-04

## Identificação
- **Rodada:** RD-2026-04-28-04
- **Data:** 2026-04-28
- **Objetivo:** corrigir governança de dependência, declarando `scipy` no manifesto principal para preparar reexecução numérica futura.

## Escopo e restrições aplicadas
- Alteração **somente** em `requirements.txt`.
- Sem mudança em motor econômico, pagamentos, switching, função objetivo, dados oficiais, cache BCB/CDI, saída canônica ou contrato/modelo.

## Cadeia confirmada de dependência
1. `nucleo/resolver_hibrido_5p_shadow.py` importa `from scipy.optimize import linprog`.
2. `nucleo/contexto_baseline.py` importa `resolver_hibrido_5p_shadow` no topo de módulo.
3. Entry points operacionais passam por `contexto_baseline`.
4. Sem `scipy` instalado, a execução quebra antes da validação numérica.

## Correção aplicada
- Arquivo alterado: `requirements.txt`
- Inclusão de linha: `scipy`
- Padrão adotado: dependências sem pin de versão (consistente com o restante do manifesto).

## Resultado técnico da microetapa
- Governança de dependência corrigida no repositório (manifesto atualizado).
- Ambiente atual permanece bloqueado para instalação por proxy/rede (403), impedindo import local de `scipy` nesta infraestrutura.
