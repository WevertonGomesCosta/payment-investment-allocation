# Governança estrutural V206

## Status

```text
V206_DOCUMENTAL_E_ESTRUTURAL
SEM_ALTERACAO_ECONOMICA
```

## Escopo aplicado

A V206 foi aberta a partir da V205 para executar apenas ajustes documentais e estruturais de baixo risco:

1. Atualizar `README.md`, `relatorios/atuais/LEIA-ME_OPERACIONAL.md` e `saidas/README.md` para refletirem a V205 como baseline pós-hotfix e a V206 como camada documental/estrutural vigente.
2. Remover `relatorio_operacional_v202.xlsx` de `saidas/oficial/` e preservá-lo em `saidas/historico/relatorios_operacionais/`.
3. Centralizar helpers semânticos ainda duplicados de fonte, proxy terminal e IR em `nucleo/utilitarios_neutros.py`.

## Helpers centralizados

- `_rotulo_fonte`
- `_fonte_id`
- `_normalizar_proxy_terminal`
- `_aliquota_ir_estimada`

A centralização substitui definições locais por imports do utilitário neutro. Não houve mudança intencional de regra econômica.

## Fora de escopo

Não foram alterados:

- contrato mestre;
- modelo matemático-estatístico-financeiro;
- motor econômico;
- regra de pagamentos;
- regra de switching;
- regra de recebidos/aportes futuros.

## Decisão sobre `relatorio_operacional_v202.xlsx`

O relatório V202 deixou de ser artefato oficial ativo e passou a ser histórico congelado em:

```text
saidas/historico/relatorios_operacionais/relatorio_operacional_v202.xlsx
```

Justificativa: `saidas/oficial/` deve conter apenas saídas oficiais ativas ou README de orientação, sem misturar relatórios antigos preservados.
