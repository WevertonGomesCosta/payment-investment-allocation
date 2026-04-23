# Auditoria de duplicação entre `scripts/` e `scripts/diagnostico/`

Baseline de entrada: **V153**  
Baseline de saída: **V154**

## Resumo objetivo

- arquivos Python no `scripts/` raiz (sem subpastas): **65**
- arquivos Python canônicos em `scripts/diagnostico/` (sem `__init__`/`_bootstrap`): **62**
- nomes espelhados entre raiz e diagnóstico: **62**
- arquivos somente na raiz: **3**
- arquivos somente em `scripts/diagnostico/`: **0**

## Diagnóstico estrutural

A maior parte da “duplicação” entre `scripts/` e `scripts/diagnostico/` não é duplicação lógica, e sim **duplicação de entrada de execução**: a implementação vive em `scripts/diagnostico/` e a raiz mantém um ponto de entrada legado.

O risco estrutural real estava em três pontos:

1. **wrappers heterogêneos** na raiz (`import main`, `runpy.run_path`, ajustes manuais de `sys.path`);
2. **scripts diagnósticos novos** vivendo apenas na raiz, sem canonicidade temática;
3. **três scripts canônicos apenas em `scripts/diagnostico/`**, sem wrapper plano correspondente.

## Consolidação de baixo risco aplicada

### 1. Helper único de compatibilidade

Foi criado `scripts/_compat.py` para unificar a execução de wrappers via `run_module_entrypoint(...)`.

### 2. Canonicidade formal

- `scripts/diagnostico/` passa a ser a localização canônica dos inspeccionadores e consolidadores diagnósticos.
- `scripts/` passa a ser tratado prioritariamente como camada de **compatibilidade de execução**.

### 3. Scripts movidos da raiz para `scripts/diagnostico/`

- `inspecionar_auditoria_3k_mar_pos_pagamento_v147.py`
- `inspecionar_chave_tau_v149.py`
- `inspecionar_correcao_flattening_v148.py`
- `inspecionar_motor_diario_conjunto_experimental_v143.py`
- `inspecionar_motor_diario_conjunto_experimental_v144.py`
- `inspecionar_motor_diario_pos_vencimento_v146.py`
- `run_v150_multi.py`

Na raiz, cada um desses arquivos foi substituído por um wrapper fino.

### 4. Wrappers adicionados na raiz para cobrir lacunas

- `consolidar_grade_diaria_parametrizada_v130.py`
- `consolidar_grade_diaria_switching_v128.py`
- `inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py`

### 5. Wrappers normalizados

Os wrappers abaixo, que ainda usavam `runpy.run_path` manual, foram normalizados para o helper comum:

- `inspecionar_decisao_local_v1.py`
- `inspecionar_saldo_disponivel_geral.py`

## Decisão arquitetural recomendada

Antes de reorganizar `nucleo/simulador_central_eventos_v1.py`, o contrato mais seguro para `scripts/` é:

- preservar nomes históricos no diretório raiz;
- manter implementação canônica nas subpastas temáticas;
- evitar mover novamente scripts canônicos entre camadas sem necessidade;
- continuar tratando a raiz como fachada de compatibilidade.

## Próximo passo estrutural de baixo risco

A próxima micro-etapa recomendada é consolidar a **nomenclatura e agrupamento dos scripts de diagnóstico temporal/motor diário**, sem tocar ainda no simulador central.
