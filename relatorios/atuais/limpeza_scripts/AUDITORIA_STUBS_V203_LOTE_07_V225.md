# Auditoria de limpeza de stubs V203 — lote 07 — V225

## Identificação

- Baseline: V225
- Escopo: stubs V203 relacionados a runner/shadow na raiz de `scripts/diagnostico/`
- Resultado: lote concluído

## Arquivos auditados e removidos

```text
scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py
```

## Critério aplicado

Os três arquivos foram selecionados porque:

1. eram stubs V203 sem lógica operacional própria no caminho atual;
2. indicavam preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/`;
3. a busca por referências localizou apenas registros documentais/históricos;
4. não havia dependência ativa na rota `aplicacao/principal.py`.

## Evidência pós-limpeza

A consulta direta aos três caminhos no `main` retornou ausência dos arquivos (`404`).

## Commits da microetapa

```text
aa3487e359f041b48f1d733f12add4f0b1494f6d
ce7fca6f894525868d9b50c98bfcca465719a645
6216ffc31cce72c2210197cbc12cb521ffc96665
```

## Restrições respeitadas

Não houve alteração em:

- código funcional;
- config;
- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- identidade da baseline.

## Validação local necessária

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

- execução sem erro;
- saída em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- sem alteração econômica observável.

## Próxima etapa sugerida

Após validação local, auditar novo lote pequeno de stubs V203 ainda físicos na raiz de `scripts/diagnostico/`, priorizando validação diária ou proxy/híbrido shadow, ou atualizar o inventário pós-lotes 01–07.
