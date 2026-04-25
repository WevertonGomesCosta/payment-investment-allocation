# Governança de scripts — V203

## Status

- Baseline de origem: **V202**
- Baseline gerada: **V203**
- Escopo: governança de scripts e saídas legadas
- Motor principal: **não alterado**
- Contrato mestre: **não alterado**
- Modelo matemático-estatístico-financeiro: **não alterado**
- Regra de recebidos/aportes futuros: **não alterada**

## Objetivo

Impedir que scripts legados de diagnóstico, grade diária, switching shadow ou validações antigas gerem console/arquivos próprios capazes de competir com a saída oficial criada na V202.

A autoridade observável continua concentrada em:

```text
nucleo/saida_canonica.py
```

A geração operacional oficial continua em:

```text
scripts/operacional/gerar_planilha_operacional.py
```

## Ações aplicadas

| Ação | Quantidade |
|---|---:|
| Scripts legados bloqueados com stub | 49 |
| Diagnósticos úteis convertidos para wrapper canônico | 2 |
| Linhas classificadas no mapa de governança | 201 |
| Cópias originais preservadas em histórico V203 | 49 |

## Scripts bloqueados

Os scripts bloqueados permanecem no caminho antigo, mas agora retornam bloqueio intencional de governança, com marcador:

```text
BLOQUEADO_POR_GOVERNANCA_V203
```

O conteúdo original foi preservado em:

```text
scripts/historico_saida_propria_v203/
```

Esses scripts não têm autoridade operacional e não devem gerar arquivos oficiais, console oficial, nem relatórios atuais.

## Diagnósticos convertidos

Foram convertidos para leitura de `PacoteSaidaCanonica`:

```text
scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py
scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py
```

Esses scripts agora observam a mesma estrutura usada por console e planilha, sem recalcular visão própria.

## Scripts mantidos

Foram mantidos:

- wrappers de compatibilidade da raiz de `scripts/`;
- `scripts/operacional/gerar_planilha_operacional.py`;
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`, por ser auditoria específica;
- `scripts/diagnostico/verificar_release_baseline.py`;
- scripts ligados a recebidos/aportes futuros, porque essa frente foi explicitamente adiada.

## Regra operacional a partir da V203

Nenhum novo script pode gerar saída operacional própria sem passar pela camada:

```python
from nucleo.saida_canonica import construir_saida_canonica
```

Scripts diagnósticos podem imprimir amostras, mas devem declarar que não têm autoridade operacional, salvo o gerador oficial em `scripts/operacional/`.

## Frente preservada para depois

O problema dos recebidos/aportes futuros ainda não aportados em carteira permanece fora da V203. Essa correção será a próxima frente metodológica, depois da estabilização de governança e saída canônica.
