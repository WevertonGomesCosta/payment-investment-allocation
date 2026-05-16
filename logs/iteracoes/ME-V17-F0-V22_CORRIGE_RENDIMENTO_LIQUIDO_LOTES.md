# ME-V17-F0-V22 — Corrige rendimento líquido observável de lotes ativos pós-switching

## 1. Identificação

- MICROETAPA: ME-V17-F0-V22
- VERSAO_CANDIDATA: V17-F0-V.2.2
- TIPO: CÓDIGO / RENDERIZAÇÃO OBSERVÁVEL / CORREÇÃO CIRÚRGICA
- CLASSE: CORRIGE_RENDIMENTO_LIQUIDO_OBSERVAVEL
- STATUS: CONCLUÍDA
- BRANCH: main
- ALTERA_CODIGO: sim
- ALTERA_MOTOR: não
- ALTERA_LEDGER: não
- ALTERA_MODELO_OFICIAL: não
- ALTERA_RUNNER_FINAL: não
- ALTERA_REGRA_ECONOMICA: não
- ALTERA_ETAPA_2: não

---

## 2. Problema

A saída operacional apresentava rendimento líquido negativo para o lote:

- `Lote 3120 mai`
- status: `ativo_pos_switching`
- rendimento líquido observado: `-11.57`

Esse valor é inconsistente como leitura observável de rendimento líquido de lote ativo pós-switching com saque parcial.

---

## 3. Diagnóstico

O problema estava restrito à camada observável em:

- `nucleo/saida_observavel.py`

A fórmula anterior calculava:

```text
rendimento_liquido = patrimonio_liquido - valor_original
```
