# ESTRUTURA DO REPOSITÓRIO V103

## Nova camada adicionada

A V103 adiciona a camada `nucleo/heuristica_conjunta_parcial_bloco_critico.py`, acoplada ao `ContextoBaseline` sem alterar o motor principal.

## Novos pontos de integração

- `ContextoBaseline.heuristica_conjunta_parcial_bloco_critico`
- seção `PAGAMENTOS FUTUROS — HEURÍSTICA CONJUNTA PARCIAL (BLOCO CRÍTICO)` no console
- aba `Heurística conjunta` na planilha operacional
- script de diagnóstico `scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- wrapper de compatibilidade `scripts/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`

## Objetivo estrutural da V103

Criar uma ponte entre a recomputação local sequencial e futuras heurísticas mais globais, atuando apenas no bloco crítico 20/04/2026–20/05/2026 com preservação estratégica de lotes e trocas preventivas.
