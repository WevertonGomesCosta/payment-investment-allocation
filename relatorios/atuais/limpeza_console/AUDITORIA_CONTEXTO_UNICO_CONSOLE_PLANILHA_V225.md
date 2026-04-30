# Auditoria de contexto único para console e planilha — V225

## Identificação

- Baseline: V225
- Data/hora local da auditoria: 2026-04-30T09:45:56
- Escopo:
  - `aplicacao/principal.py`
  - `aplicacao/console/principal.py`
  - `nucleo/gerar_planilha_operacional.py`

## Problema corrigido

A rota oficial não deve executar carregamentos independentes para console e planilha.

## Decisão aplicada

A rota oficial passa a ser:

```text
aplicacao/principal.py
├── carregar_contexto_baseline(...) uma única vez
├── construir_saida_canonica(...) uma única vez
├── render_console(contexto_baseline, saida_canonica)
└── gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

## Contrato resultante

- `nucleo/saida_observavel.py` permanece como fonte única dos dados observáveis compartilhados.
- `aplicacao/console/principal.py` passa a ser renderizador de console.
- `nucleo/gerar_planilha_operacional.py` passa a ser renderizador de planilha.
- `aplicacao/principal.py` passa a ser o orquestrador único de contexto e saída.

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline.

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/gerar_planilha_operacional.py nucleo/saida_observavel.py
python aplicacao/principal.py
```
