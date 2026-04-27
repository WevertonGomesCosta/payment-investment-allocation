# VALIDAÇÃO LOCAL — V216

## 1. Status

`V216_CANDIDATA_FUNCIONAL_VALIDADA_MINIMAMENTE`

A V216 foi criada a partir da V208 como baseline funcional real. Os artefatos V209–V215 foram usados apenas como especificação metodológica.

## 2. Validações executadas

### 2.1 Validação sintática

Arquivos verificados por `ast.parse`:

- `nucleo/aportes_futuros_planejados.py`
- `nucleo/simulador_central_eventos_v1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/builders/simulador_central_estado_v117.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_aportes_planejados_v216.py`

Resultado: **OK**.

### 2.2 Release checker

Comando:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

Resultado:

```text
OK - release baseline validado para V216
```

Observação: o ambiente de execução exibiu aviso externo de warmup do runtime de planilhas (`Spreadsheet runtime warmup failed...`). Esse aviso não é gerado pelo repositório e não impediu o retorno `rc=0` do release checker.

### 2.3 Diagnóstico funcional sintético

Comando:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/inspecionar_aportes_planejados_v216.py
```

Resultado:

```text
eventos_auditoria: 3
lotes_planejados_promovidos: 1
pagamentos_consumindo_lotes_planejados: 1
pagamentos_processados: 3
status_simulador: integracao_integral_multidestino_v216
```

## 3. Evidência funcional do cenário sintético

O cenário sintético validou a cadeia:

```text
recebido futuro de R$ 5.000,00
→ pagamento intradiário de R$ 1.000,00
→ reserva D+7 de R$ 300,00
→ aporte planejado de R$ 3.700,00
→ lote planejado promovido
→ pagamento futuro consumindo o lote planejado
```

Invariante validado:

```text
5000 = 1000 + 3700 + 300
```

## 4. Artefatos diagnósticos gerados

- `saidas/diagnostico/auditoria_aportes_planejados_v216_sintetico.csv`
- `saidas/diagnostico/historico_aportes_planejados_v216_sintetico.csv`
- `saidas/diagnostico/lotes_planejados_promovidos_v216_sintetico.csv`
- `saidas/diagnostico/pagamentos_consumindo_lotes_planejados_v216_sintetico.csv`

## 5. Higiene de release

- `__pycache__`: ausente.
- `.pyc`: ausente.
- stubs reconstruídos V209–V215: ausentes.
- pacote final: sem pasta raiz interna no `.zip`.

## 6. Limite da validação

A validação real contra a planilha completa não foi promovida como gate obrigatório nesta entrega porque pode ser mais pesada no ambiente do chat. O script `inspecionar_aportes_planejados_v216.py --real` ficou disponível para execução local quando necessário.

## 7. Decisão

A V216 está pronta como **versão funcional candidata**. Ainda não deve ser tratada como baseline estável sem teste real local sobre o fluxo operacional completo.
