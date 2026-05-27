# ME-ETAPA5-04 — audita ResultadoMotorTemporalConjunto

## Data

2026-05-27

## Tipo

FUNCIONAL / AUDITORIA INTERNA ESTRUTURAL

## Classe

Auditoria interna do `ResultadoMotorTemporalConjunto` construído pela Etapa 5, sem alteração de console, XLSX, saída canônica, ledger ou scripts diagnósticos.

## Branch

`me-etapa5-04-audita-resultado-motor-temporal-conjunto`

## Baseline de entrada

`main` após merge da PR #407.

Merge commit de entrada:

`8840687c321f2b00e68567b7a33d1965d8042989`

## Objetivo

Adicionar auditoria interna ao artefato canônico da Etapa 5:

`ResultadoMotorTemporalConjunto`

A auditoria verifica integridade estrutural de:

- interface do `EstadoTemporalInicial`;
- horizonte do motor;
- janela temporal;
- índice temporal;
- eventos temporais base;
- auditoria de consumo direto do `EstadoTemporalInicial`.

## Arquivos alterados

- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/ME-ETAPA5-04_AUDITA_RESULTADO_MOTOR_TEMPORAL_CONJUNTO.md`

## Estruturas adicionadas

- `AuditoriaIntegridadeResultadoMotorTemporalConjunto`

## Funções adicionadas

- `auditar_integridade_resultado_motor_temporal_conjunto(...)`

## Integração no artefato

`ResultadoMotorTemporalConjunto` passa a conter o campo:

```python
auditoria_integridade_resultado: AuditoriaIntegridadeResultadoMotorTemporalConjunto | None = None
```

A função `construir_resultado_motor_temporal_conjunto(...)` passa a preencher esse campo antes de retornar o artefato.

## Escopo da auditoria

A auditoria verifica:

- se a interface do `EstadoTemporalInicial` está válida;
- se `data_referencia` do resultado coincide com a do horizonte;
- se `data_inicio <= data_fim`;
- se `janela_temporal_motor` coincide com `horizonte.datas_temporais`;
- se o horizonte possui datas temporais;
- se datas do índice estão dentro do horizonte;
- se contagens indexadas não excedem os eventos base;
- se eventos temporais base não estão simultaneamente vazios;
- se a auditoria de consumo confirma consumo direto de `EstadoTemporalInicial`.

## Escopo não implementado

Esta microetapa não implementa:

- decisão econômica completa;
- escolha de fonte ótima;
- seleção de lote;
- execução de pagamento;
- promoção de switching;
- execução de switching novo;
- materialização de lote pós-switching;
- ledger oficial;
- saída canônica final;
- alteração de console;
- alteração de XLSX;
- alteração de dados;
- alteração de regras econômicas;
- script diagnóstico;
- sentinela;
- V4Z;
- rota paralela.

## Validação esperada

Validar localmente:

```bash
git diff --name-only origin/main...HEAD
python -m py_compile nucleo/motor_temporal_conjunto.py
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
git status --short
```

Resultado esperado:

- diff restrito a `nucleo/motor_temporal_conjunto.py` e este log;
- `py_compile` sem erro;
- runtime principal sem regressão;
- árvore limpa, salvo eventual atualização esperada de `dados/cache_bcb.json` por BCB online, a ser tratada separadamente.

## Confirmações

- Não houve alteração de `aplicacao/principal.py`.
- Não houve alteração de console.
- Não houve alteração de XLSX.
- Não houve alteração de dados.
- Não houve alteração de saída canônica.
- Não houve criação de ledger.
- Não houve criação de script diagnóstico.
- Não houve criação de sentinela.
- Não houve criação de V4Z.
- Não houve reintrodução de `ContextoBaseline`.
- Não houve reintrodução de `ContextoSaidaCanonicaCompat`.
