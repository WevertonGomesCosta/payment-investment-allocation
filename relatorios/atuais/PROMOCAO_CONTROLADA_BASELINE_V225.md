# PROMOÇÃO CONTROLADA DE BASELINE — V225

## Status formal

```text
BASELINE_FUNCIONAL_ESTAVEL_V225
```

A V225 formaliza a promoção controlada da V224 como baseline funcional estável da frente de aportes planejados, gate econômico, cálculo de dias e higiene de release.

## Decisão

A V224 foi validada localmente com:

```text
V224_VALIDADA_LOCALMENTE
GATE_ECONOMICO_VALIDADO
RELEASE_LIMPO_VALIDADO
CANDIDATA_APTA_A_PROMOCAO_CONTROLADA
```

A V225 apenas registra a promoção formal. Ela **não altera motor**, não altera regra econômica, não altera cálculo de dias e não altera idade fiscal.

## Escopo aprovado

A baseline V225 consolida:

1. cálculo de dias corridos e dias úteis centralizado para campos visuais de lotes;
2. idade fiscal centralizada em módulo fiscal próprio;
3. transição de recebidos futuros para aportes planejados em modo diagnóstico;
4. comparação operacional entre cenários com e sem aportes planejados;
5. gate econômico bloqueando aportes planejados quando o cenário com aporte piora o objetivo econômico;
6. scripts canônicos de impacto e gate preservados;
7. auditoria final pré-baseline;
8. limpeza pré-release e release checker limpo.

## Resultado econômico preservado

A regra do gate econômico permanece:

```text
bloquear aportes planejados se:
delta_patrimonio_terminal_proxy < 0
ou delta_perda_terminal_total > 0
ou delta_penalidade_estrategica_total > 0
ou delta_deficit_total > 0
```

Na validação que motivou a promoção, o gate manteve:

```text
status_gate_economico_v220: BLOQUEADO_GATE_ECONOMICO_V220
cenario_final_v220: sem_aportes_planejados
```

## Escopo negativo obrigatório

A V225:

- não altera motor;
- não altera regra econômica;
- não altera cálculo de dias;
- não altera idade fiscal;
- não altera seleção de lotes;
- não altera a decisão do gate;
- não promove aportes planejados bloqueados;
- não reabre o contrato mestre.

## Comandos canônicos

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v223.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v223.py --real
python scripts/diagnostico/auditoria_final_pre_baseline_v223.py
python scripts/diagnostico/verificar_release_limpo.py
```

## Decisão final

```text
PROMOVER_V225_COMO_BASELINE_FUNCIONAL_ESTAVEL
MANTER_GATE_ECONOMICO_ATIVO
MANTER_APORTES_PLANEJADOS_BLOQUEADOS_QUANDO_INFERIORES_AO_CENARIO_SEM_APORTE
```
