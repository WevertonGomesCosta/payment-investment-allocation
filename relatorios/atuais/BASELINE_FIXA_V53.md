# Baseline fixa V53

## Objetivo desta versão

Reorganizar estruturalmente todo o repositório sem alterar a base funcional vigente.

## Reorganização aplicada

- separação do ponto de entrada principal em `aplicacao/console/`;
- separação dos scripts por responsabilidade em:
  - `scripts/operacional/`
  - `scripts/auditoria/`
  - `scripts/diagnostico/`
- manutenção de wrappers de compatibilidade nos caminhos antigos:
  - `aplicacao/principal.py`
  - `scripts/gerar_planilha_operacional.py`
  - `scripts/gerar_auditoria_diaria_lote.py`
  - `scripts/inspecionar_base.py`
- centralização das saídas operacionais em `saidas/operacional/`;
- limpeza da documentação vigente em `relatorios/atuais/`, mantendo no diretório atual apenas:
  - contrato operacional executável
  - backlog contratual futuro
  - baseline fixa corrente
  - validação local corrente
  - estrutura oficial do repositório

## Garantia de compatibilidade

Os comandos antigos continuam válidos, mas os caminhos canônicos da baseline passam a ser os novos caminhos organizados.
