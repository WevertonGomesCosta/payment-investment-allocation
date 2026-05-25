# ME-GOV-01 — Ciclo de vida de diagnósticos e artefatos temporários

## Objetivo

Formalizar, como regra contratual, que scripts diagnósticos e artefatos temporários possuem ciclo de vida obrigatório.

## Motivação

A frente V17-F0 removeu resíduos `shadow`, `benchmark`, sentinelas e I/O diagnóstico do núcleo vivo das Etapas 1–4.

A frente V17-F0-DIAG1 removeu 61 scripts diagnósticos legados incompatíveis com a rota limpa e preservou apenas o gate permanente `scripts/diagnostico/auditar_nucleo_vivo_v4z.py`.

Os comentários de revisão da PR #361 evidenciaram que scripts diagnósticos históricos podem pressionar o núcleo vivo a reintroduzir aliases, kwargs, módulos ou stubs já removidos. Essa compatibilidade artificial é proibida por esta decisão de governança.

## Decisão contratual

Foi criado o adendo:

`relatorios/principais/ADENDO_GOV_01_CICLO_VIDA_DIAGNOSTICOS_ARTEFATOS_TEMPORARIOS.md`

O adendo estabelece que scripts diagnósticos são transitórios. Após validação e aplicação da correção no núcleo, devem ser removidos, arquivados fora da rota viva, substituídos por evidência estática ou promovidos explicitamente a gate permanente.

Na ausência de promoção explícita, o destino padrão é remoção.

## Escopo

Alteração documental. Esta microetapa não altera:

- `aplicacao/*`;
- `nucleo/*`;
- `dados/*`;
- motor;
- replay;
- ledger;
- ranking;
- saída canônica;
- regra econômica.

## Evidência preservada

- PR #361 — limpeza bruta das Etapas 1–4;
- PR #362 — limpeza de diagnósticos legados pós-limpeza bruta;
- log `ME-V17-F0-DIAG1_LIMPA_DIAGNOSTICOS_LEGADOS.md`;
- gate permanente `scripts/diagnostico/auditar_nucleo_vivo_v4z.py`.

## Validação esperada

- `git diff --stat` restrito a documentação;
- contrato/adendo criado;
- log da microetapa criado;
- nenhuma alteração em runtime;
- auditor V4Z segue disponível como gate permanente.
