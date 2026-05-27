# ME-ETAPA5-00 — contrato mínimo da Etapa 5

## Data

2026-05-26

## Tipo

DOCUMENTAL / CONTRATUAL

## Classe

Abertura normativa mínima da Etapa 5 sem implementação funcional.

## Branch

`me-etapa5-00-contrato-minimo-etapa5`

## Baseline de entrada

`main` após merge da PR #401.

Commit de entrada confirmado:

`4712c0c8e40b1748ed79dca69af8963e0c947b1d`

## Confirmação prévia

A PR #401 estava mergeada antes da abertura desta microetapa.

A `main` estava idêntica ao merge commit da PR #401 no início desta frente.

## Objetivo

Criar o contrato específico mínimo da **Etapa 5 — Motor temporal conjunto**, preservando a separação entre `EstadoTemporalInicial`, motor temporal conjunto, ledger canônico, saída canônica, console e XLSX.

## Arquivos alterados

- `relatorios/principais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `logs/iteracoes/ME-ETAPA5-00_CONTRATO_MINIMO_ETAPA5.md`

## Arquivos não alterados

Não foram alterados:

- `aplicacao/*`
- `nucleo/*`
- `dados/*`
- `saidas/*`
- `scripts/diagnostico/*`
- motor temporal
- ledger
- console
- XLSX
- regras econômicas

## Contrato específico criado

Foi criado o contrato específico:

`relatorios/principais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`

## Entrada formal da Etapa 5

A entrada formal obrigatória da Etapa 5 ficou definida como:

`EstadoTemporalInicial`

A Etapa 5 deve consumir esse artefato diretamente.

## Componentes mínimos consumidos da entrada

O contrato específico registra como componentes mínimos consumidos:

- `pagamentos_temporais`;
- `recebidos_temporais`;
- `fontes_temporais`;
- `inventario_temporal`;
- `switching_temporal_realizado`;
- restrições temporais;
- elegibilidades temporais preliminares;
- auditoria temporal.

## Artefato mínimo de saída definido

A primeira implementação funcional futura da Etapa 5 deve produzir apenas:

`ResultadoMotorTemporalMinimo`

Esse artefato foi definido como estrutura preparatória, sem ledger oficial, sem saída canônica final e sem decisão econômica completa.

## Escopo permitido da primeira implementação funcional futura

A primeira implementação funcional poderá apenas:

- consumir diretamente o `EstadoTemporalInicial`;
- validar presença estrutural dos componentes mínimos de entrada;
- construir esqueleto temporal conjunto;
- organizar dias simuláveis;
- organizar obrigações temporais por data;
- organizar fontes temporais por disponibilidade preliminar;
- preservar switchings já realizados como eventos observados quando presentes na entrada;
- preservar rastreabilidade dos componentes consumidos;
- registrar bloqueios temporais básicos;
- retornar o `ResultadoMotorTemporalMinimo` como estrutura mínima auditável.

## Proibições registradas

A primeira implementação funcional não poderá:

- escolher fonte ótima final;
- executar pagamento;
- liquidar conta;
- escolher pacote vencedor do dia;
- decidir switching candidato;
- promover switching candidato;
- executar switching novo;
- materializar novo lote pós-switching;
- criar ledger oficial;
- criar saída canônica final;
- alterar console;
- alterar XLSX;
- alterar dados;
- alterar planilha operacional;
- alterar regras econômicas;
- usar saída observável como fonte de estado;
- usar log histórico como norma viva;
- usar diagnóstico como motor auxiliar;
- criar fallback legado;
- criar wrapper transitório;
- criar rota paralela;
- reintroduzir `ContextoBaseline`;
- reintroduzir `ContextoSaidaCanonicaCompat`.

## Separação preservada

A microetapa preserva separação explícita entre:

- `EstadoTemporalInicial`;
- motor temporal conjunto;
- ledger canônico;
- saída canônica;
- console;
- XLSX.

## Validação prevista

Por ser microetapa documental, a validação esperada é:

```bash
git diff --name-only
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
git status --short
```

## Resultado esperado do diff

O diff deve ficar restrito a:

- `relatorios/principais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `logs/iteracoes/ME-ETAPA5-00_CONTRATO_MINIMO_ETAPA5.md`

## Confirmações

- Não houve alteração de código funcional.
- Não houve alteração de dados.
- Não houve alteração de motor temporal.
- Não houve alteração de ledger.
- Não houve alteração de console.
- Não houve alteração de XLSX.
- Não houve criação de V4Z.
- Não houve criação de sentinelas.
- Não houve criação de scripts diagnósticos.
- Não houve abertura funcional da Etapa 5.
