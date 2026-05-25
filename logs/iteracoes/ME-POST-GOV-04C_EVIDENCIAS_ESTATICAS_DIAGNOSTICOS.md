# ME-POST-GOV-04C — Evidências estáticas para diagnósticos remanescentes

## Objetivo

Tratar exclusivamente os 11 scripts classificados como `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` no `scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md` após o merge da PR #367.

Esta microetapa **não remove fisicamente** esses scripts. Ela cria a evidência estática substitutiva mínima para cada diagnóstico, permitindo que uma microetapa futura decida a remoção física com rastreabilidade.

## Baseline de entrada

```text
BASELINE: main
HEAD: 21ba9cf48eb4efdf43d9e7e457aa23146c0372f9
ULTIMO_MERGE: PR #367 — ME-POST-GOV-04B arquiva diagnósticos fora da rota viva
```

## Escopo permitido

```text
scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
saidas/*
```

A ME-POST-GOV-04C não altera motor, replay, ledger, ranking, saída canônica, contrato mestre, modelo oficial ou regra econômica.

## Critério de evidência estática

Para cada script remanescente, a evidência estática substitutiva deve registrar:

1. o tema operacional coberto;
2. a decisão de governança;
3. o destino futuro permitido;
4. a condição de remoção física;
5. a restrição contra uso como insumo runtime.

## Evidências estáticas por script

| Script | Tema coberto | Evidência estática criada/apontada | Decisão futura permitida |
|---|---|---|---|
| `scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py` | consistência entre exportações auxiliares U4/U3 | Esta linha preserva a evidência de que a comparação U4/U3 é histórico de exportação auxiliar e não gate vivo. | remover após confirmar que não é referenciado no índice nem em runtime |
| `scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py` | governança de promoção de saída auxiliar | Esta linha preserva a evidência de que a promoção de saída auxiliar foi decisão documental, não dependência executável. | remover após confirmar que o log da microetapa substitui o diagnóstico |
| `scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py` | regras operacionais de uso de recebidos | Esta linha preserva a evidência de que regras de recebidos devem estar em contrato/log, não em script diagnóstico vivo. | remover após confirmar que as regras relevantes seguem no contrato/modelo/log |
| `scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py` | separação entre previsão e materialização | Esta linha preserva a evidência de que a separação previsão/materialização é decisão de arquitetura, não gate executável ativo. | remover após confirmar que a regra está documentada e não consumida por runtime |
| `scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py` | matriz histórica de correção | Esta linha preserva a evidência de que a matriz de correção é artefato consumado e não insumo operacional. | remover após confirmar que a matriz não é necessária para execução principal |
| `scripts/diagnostico/consolidar_plano_migracao_v17_b0.py` | plano histórico de migração | Esta linha preserva a evidência de que o plano de migração é documentação histórica, não script ativo. | remover após confirmar que a migração já foi absorvida por logs/índice |
| `scripts/diagnostico/construir_taxonomia_v17_a2.py` | taxonomia diagnóstica V17 | Esta linha preserva a evidência de que a taxonomia pertence ao histórico de diagnóstico e não à rota viva. | remover após confirmar que não há consumo por runtime nem gate |
| `scripts/diagnostico/desenhar_pacote_orquestrado_pre_saida_v17_b2.py` | desenho de pacote orquestrado pré-saída | Esta linha preserva a evidência de que o desenho de pacote é especificação histórica, não implementação viva. | remover após confirmar que não é dependência de saída canônica |
| `scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py` | explicitação de valores de resgate multifonte | Esta linha preserva a evidência de que os valores multifonte pertencem à auditoria histórica e não à decisão econômica atual. | remover após confirmar que a regra econômica oficial não depende do script |
| `scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py` | critérios de elegibilidade para pagamento | Esta linha preserva a evidência de que critérios de elegibilidade devem estar formalizados no contrato/modelo/log, não em script transitório. | remover após confirmar que critérios necessários estão cobertos normativamente |
| `scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py` | ledger diagnóstico de recebidos | Esta linha preserva a evidência de que ledger diagnóstico é histórico e não ledger oficial/runtime. | remover após confirmar que não há consumo em saída oficial |

## Restrições preservadas

- Nenhum script foi removido nesta microetapa.
- Nenhum script foi promovido a gate permanente.
- `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` permanece como único gate permanente.
- Os 11 scripts acima permanecem presentes apenas até microetapa futura de remoção física.
- Os 11 scripts acima seguem proibidos como insumo operacional, norma superior ou compatibilidade artificial.

## Decisão da microetapa

```text
STATUS: EVIDENCIAS_ESTATICAS_REGISTRADAS
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
REMOVE_SCRIPTS: false
PROXIMA_ACAO: VALIDAR_PR_E_EXECUTAR_GATES
```

## Validação esperada

Após checkout da branch ou após merge, rodar:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```
