# Inventário pós-lotes 01–05 de limpeza de stubs V203 — V225

## Identificação

- Baseline operacional: V225
- Tipo: inventário documental pós-limpeza
- Escopo: estado atual da limpeza de scripts diagnósticos bloqueados por governança V203
- Restrições: não remover arquivos; não alterar código funcional; não alterar config; não alterar cálculo, replay, pagamentos, switching, ranking ou identidade da baseline.

## Objetivo

Consolidar o estado da limpeza após os lotes 01–05, separando:

1. lotes de stubs já removidos;
2. arquivos que agora aparecem apenas em inventários/documentação histórica;
3. stubs V203 que ainda existem fisicamente no repositório;
4. candidatos seguros a remoção futura.

## Rota operacional preservada

A rota operacional da V225 permanece fora da frente de scripts diagnósticos removidos:

```text
aplicacao/principal.py
├── aplicacao.console.principal.main
└── scripts.operacional.gerar_planilha_operacional.main
```

Os lotes 01–05 não alteraram código funcional, nem a rota principal.

## Lotes já removidos

### Lote 01 — raiz de `scripts/diagnostico/`

Arquivos removidos:

```text
scripts/diagnostico/inspecionar_mapa_absorcao_legado.py
scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
scripts/diagnostico/inspecionar_contrato_f1.py
scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
```

Status: removido e auditado.

Relatório: `relatorios/atuais/limpeza_scripts/AUDITORIA_STUBS_V203_LOTE_01_V225.md`

### Lote 02 — `temporal_decisao/motor_diario/`

Arquivos removidos:

```text
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v143.py
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v144.py
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_pos_vencimento_v146.py
```

Status: removido e auditado.

Relatório: `relatorios/atuais/limpeza_scripts/AUDITORIA_STUBS_V203_LOTE_02_V225.md`

### Lote 03 — `temporal_decisao/valoracao_decisao/`

Arquivos removidos:

```text
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_correcao_flattening_v148.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_chave_tau_v149.py
```

Status: removido e auditado. Dois arquivos foram removidos localmente após bloqueio inicial do conector, e a auditoria foi atualizada como concluída integralmente.

Relatório: `relatorios/atuais/limpeza_scripts/AUDITORIA_STUBS_V203_LOTE_03_V225.md`

### Lote 04 — `temporal_decisao/bloco_critico/`

Arquivos removidos:

```text
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py
```

Status: removido e auditado.

Relatório: `relatorios/atuais/limpeza_scripts/AUDITORIA_STUBS_V203_LOTE_04_V225.md`

### Lote 05 — consolidação documental da mesma frente `bloco_critico/`

O lote 05 registrou novamente a ausência dos mesmos arquivos de `bloco_critico/`. A checagem confirmou `404` para os caminhos já removidos.

Status: documental; não introduziu nova alteração funcional.

Relatório: `relatorios/atuais/limpeza_scripts/AUDITORIA_STUBS_V203_LOTE_05_V225.md`

## Arquivos que agora aparecem apenas em inventários/documentação histórica

Os nomes removidos nos lotes 01–05 ainda podem aparecer em:

```text
relatorios/atuais/MAPA_SCRIPTS_V201.md
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md
relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv
relatorios/atuais/limpeza_scripts/candidatos_remocao_scripts_diagnostico.csv
relatorios/atuais/limpeza_scripts/auditoria_wrappers_temporal_decisao.csv
relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv
scripts/diagnostico/temporal_decisao/README.md
```

Classificação: documentação histórica / inventário antigo. Não indica, isoladamente, existência física atual do arquivo.

## Stubs V203 ainda existentes fisicamente — amostra verificada

A auditoria confirmou a existência física de stubs V203 ainda presentes no `main`. Todos os arquivos abaixo foram verificados por leitura direta e seguem o mesmo padrão:

- docstring de bloqueio V203;
- indicação de preservação do original em `scripts/historico_saida_propria_v203/diagnostico_original/`;
- import de `scripts.diagnostico._governanca_saida.bloquear_script_legado`;
- função `main()` que apenas chama `bloquear_script_legado(...)`.

### Candidatos em `scripts/diagnostico/`

```text
scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py
scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_validacao_diaria_operacional_v176.py
scripts/diagnostico/inspecionar_validacao_diaria_operacional_v177.py
scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py
scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py
scripts/diagnostico/inspecionar_benchmark_agrupado_individual_shadow.py
scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py
```

### Candidato em `scripts/diagnostico/temporal_decisao/motor_diario/`

```text
scripts/diagnostico/temporal_decisao/motor_diario/run_v150_multi.py
```

## Leitura sobre `temporal_decisao/`

Após os lotes 02–05, a frente `temporal_decisao/` está majoritariamente limpa nos blocos tratados:

- `motor_diario`: os stubs V143, V144 e V146 foram removidos; `run_v150_multi.py` ainda existe fisicamente e é candidato a lote futuro.
- `valoracao_decisao`: V147, V148 e V149 foram removidos.
- `bloco_critico`: os três stubs auditados foram removidos.

## Candidatos seguros a remoção futura

A próxima remoção deve ser em lote pequeno e preferencialmente começar por uma das duas opções:

### Opção A — lote 06 focado no remanescente de `temporal_decisao/motor_diario/`

```text
scripts/diagnostico/temporal_decisao/motor_diario/run_v150_multi.py
```

Vantagem: fecha melhor a frente `temporal_decisao/motor_diario/`.

### Opção B — lote 06 com scripts da raiz de `scripts/diagnostico/` ligados a validação/runner shadow

Sugestão de lote pequeno:

```text
scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py
scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py
```

Vantagem: agrupa por tema e reduz stubs de runner/shadow que já foram bloqueados pela governança V203.

## Decisão desta microetapa

Nenhum arquivo foi removido nesta microetapa.

O estado pós-lotes 01–05 é considerado consistente:

1. os lotes removidos foram documentados;
2. as validações locais reportadas confirmaram `python aplicacao/principal.py` sem erro;
3. a saída oficial permaneceu em `saidas/oficial/relatorio_operacional_v225.xlsx`;
4. referências antigas em inventários não devem ser confundidas com existência física atual;
5. ainda há stubs físicos V203 candidatos a remoção futura, mas devem ser removidos somente em lotes pequenos e auditados.

## Próxima microetapa recomendada

Abrir lote 06 com foco no arquivo remanescente de `temporal_decisao/motor_diario/run_v150_multi.py`, ou, alternativamente, em três stubs da raiz relacionados a runner futuro shadow. Em qualquer caso, repetir o protocolo:

1. confirmar stub puro;
2. confirmar histórico preservado;
3. buscar referências operacionais;
4. remover lote pequeno;
5. validar `python aplicacao/principal.py`.
