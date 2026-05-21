# ME-V17-F0-V4S — Auditoria estática de resíduos funcionais pós-Etapa 4

## Objetivo
Implementar a microetapa V4S com auditoria estática via AST para inventariar resíduos funcionais em `nucleo/saida_observavel.py`, sem bloquear entrega por presença de resíduos.

## Entregáveis
- Script criado: `scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py`
- Log da microetapa: este arquivo.
- Log V4S1 prematuro: **substituído/removido**.

## Escopo auditado
O script V4S inventaria:
- funções que acessam contexto/replay;
- funções com uso amplo de `getattr`;
- funções que percorrem `__dict__`;
- funções que percorrem DataFrames genericamente (`iterrows`/`itertuples`/`to_dict`);
- funções com heurística de correção/reconstrução observável com replay;
- duplicidades potenciais em:
  - valor original,
  - produto/carteira,
  - aplicação/base fiscal,
  - saldo/sacado/remanescente;
- caminhos shadow ainda presentes em `nucleo/*.py`;
- diagnósticos V4 em `scripts/diagnostico/*v4*.py` e classificação por categoria.

## Contrato operacional do script
- Saída em formato `chave=valor`.
- `exit code 0` quando o inventário é emitido com sucesso, mesmo se houver resíduos, duplicidades ou recomendações de adiamento de Etapa 5.
- `--sem-csv` aceito por compatibilidade operacional.

## Execução dos comandos informativos (não bloqueantes)

### 1) `python -m py_compile scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py`
- Exit code: **0**
- Resultado: compilação OK.

### 2) `python scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py --sem-csv`
- Exit code: **0**
- Resultado: inventário emitido em `chave=valor`, incluindo `inventario_emitido=true`.

### 3) `python -B aplicacao/principal.py`
- Exit code: **1**
- Resultado: `RuntimeError: erro_csv_s6_ausente_sem_recomposicao_segura`.
- Causa provável: ausência de insumo CSV S6 no ambiente de execução.
- Tratamento: falha **informativa** e **não bloqueante** para V4S.

### 4) `git diff --check`
- Exit code: **0**
- Resultado: sem apontamentos.

### 5) `git status -sb`
- Exit code: **0**
- Resultado: branch `work`.

## Inventário consolidado (resumo)
- Foram identificadas funções com acesso a contexto/replay, uso de `getattr`, iteração DataFrame genérica e pontos de reconstrução observável com replay.
- Foram classificados potenciais focos de duplicidade funcional nas famílias solicitadas.
- Foram listados caminhos shadow ainda presentes no núcleo.
- Foram listados e classificados diagnósticos V4 atualmente existentes.

## Governança
- Não houve alteração de código funcional.
- Não houve abertura de Etapa 5.
- Falhas de validação/execução foram tratadas como informativas e sem efeito de bloqueio da entrega da microetapa V4S.
