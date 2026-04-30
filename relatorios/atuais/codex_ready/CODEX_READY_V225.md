# CODEX-ready V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T11:31:19
- Tipo: preparação estrutural para uso posterior no Codex
- Escopo: documentação operacional, instruções para agente e inventário de legado
- Alteração de motor econômico: não
- Alteração de replay: não
- Alteração de pagamentos: não
- Alteração de switching: não
- Alteração de ranking: não
- Alteração de cache: não

## Estado auditado

| Item | Status |
|---|---:|
| `aplicacao/principal.py` existe | SIM |
| `dados/config_atualizado.json` existe | SIM |
| Entrada oficial carrega contexto único | SIM |
| Entrada oficial constrói `saida_canonica` uma única vez | SIM |
| Console recebe `contexto_baseline` e `saida_canonica` | SIM |
| Planilha recebe `contexto_baseline` e `saida_canonica` | SIM |
| Console usa `nucleo/saida_observavel.py` | SIM |
| Console usa amostras observáveis centralizadas | NÃO |
| Console usa Situação Atual centralizada | SIM |
| Planilha usa blocos da Situação Atual de `saida_observavel` | SIM |
| Planilha não cria aba `Validacao` | SIM |
| `secoes_financeiras.py` sem uso operacional na rota oficial | NÃO |
| `render_secao_situacao_atual` neutralizada | SIM |
| Estado mínimo Codex-ready | NÃO |

## Rota oficial

```text
aplicacao/principal.py
├── carregar_contexto_baseline(...) uma única vez
├── construir_saida_canonica(...) uma única vez
├── render_console(contexto_baseline, saida_canonica)
└── gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

## Arquivos centrais para o Codex

| Arquivo | Papel |
|---|---|
| `AGENTS.md` | instruções operacionais para agentes |
| `aplicacao/principal.py` | entrada oficial única |
| `nucleo/contexto_baseline.py` | carregamento da baseline |
| `nucleo/saida_canonica.py` | saída canônica estruturada |
| `nucleo/saida_observavel.py` | fonte única da apresentação compartilhada |
| `aplicacao/console/principal.py` | renderizador do console |
| `nucleo/gerar_planilha_operacional.py` | renderizador da planilha |
| `dados/config_atualizado.json` | configuração canônica |

## Comandos oficiais

### Validação mínima

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
python aplicacao/principal.py
```

### Saída esperada

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

## Restrições preservadas

Não houve alteração em:

- cálculo econômico;
- replay;
- regra de pagamentos;
- switching;
- ranking;
- cache CDI/BCB;
- identidade da baseline V225;
- arquivos legados.

## Decisão

O repositório fica preparado para uso posterior no Codex desde que a validação local seja concluída com sucesso.

Se a validação falhar, corrigir apenas a causa da falha sem reabrir motor econômico.
