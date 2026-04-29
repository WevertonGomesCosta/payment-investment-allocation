# Auditoria e remoção controlada de stubs V203 — lote 03 — V225

## Identificação

- Baseline operacional: V225
- Tipo: limpeza estrutural controlada
- Escopo: scripts diagnósticos bloqueados por governança V203 em `scripts/diagnostico/temporal_decisao/valoracao_decisao/`
- Classe: remoção física de stubs sem autoridade operacional
- Resultado: lote parcial

## Restrições respeitadas

Esta microetapa não alterou:

- código funcional do núcleo;
- `aplicacao/principal.py`;
- console;
- planilha operacional;
- config;
- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- identidade da baseline.

## Critério de seleção do lote

O lote 03 auditou três arquivos em `scripts/diagnostico/temporal_decisao/valoracao_decisao/` que atendiam aos critérios técnicos:

1. arquivo físico ainda existia no caminho antigo;
2. conteúdo era apenas stub de bloqueio V203;
3. o docstring declarava preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/valoracao_decisao/`;
4. a execução chamava apenas `scripts.diagnostico._governanca_saida.bloquear_script_legado(...)`;
5. não havia import operacional ativo nos resultados de busca;
6. referências remanescentes eram documentais/históricas em README, relatórios ou inventários.

## Arquivos auditados

```text
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_correcao_flattening_v148.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_chave_tau_v149.py
```

## Arquivo removido nesta microetapa

Foi removido com sucesso:

```text
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_correcao_flattening_v148.py
```

Consulta direta ao caminho no `main` retornou ausência do arquivo (`404`), confirmando a remoção física.

## Arquivos auditados, mas pendentes de remoção

As tentativas de remoção via conector foram bloqueadas para os seguintes arquivos:

```text
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_chave_tau_v149.py
```

Ambos permanecem classificados como stubs V203 puros e candidatos à remoção futura, mas não foram removidos nesta microetapa.

## Evidência de preservação histórica

Os três arquivos auditados declaravam que seu conteúdo original havia sido preservado em:

```text
scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/valoracao_decisao/<nome_do_script>.py
```

Portanto, a remoção física de stubs no caminho antigo não elimina a trilha histórica original quando executada.

## Evidência de ausência operacional

A busca por referências aos nomes dos três arquivos localizou referências documentais/históricas em:

- `scripts/diagnostico/temporal_decisao/README.md`;
- `relatorios/atuais/MAPA_SCRIPTS_V201.md`;
- `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md`;
- `relatorios/atuais/limpeza_scripts/auditoria_wrappers_temporal_decisao.csv`;
- `relatorios/atuais/limpeza_scripts/candidatos_remocao_scripts_diagnostico.csv`;
- demais inventários históricos.

Não foi localizada dependência operacional ativa em `aplicacao/principal.py`, `aplicacao/console/`, `scripts/operacional/` ou `nucleo/contexto_baseline.py`.

## Commits da microetapa

- `be30f1308ce23ddf5164710866194457b2af1a1f` — removeu `inspecionar_correcao_flattening_v148.py`
- este relatório — registra a auditoria e o resultado parcial do lote 03

## Validação local necessária

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

1. execução sem erro;
2. saída operacional em `saidas/oficial/relatorio_operacional_v225.xlsx`;
3. console sem alteração econômica observável;
4. nenhuma falha por ausência do stub removido.

## Decisão

O lote 03 foi concluído parcialmente. Um stub foi removido com segurança. Dois stubs foram auditados e classificados como removíveis, mas permaneceram no repositório porque a exclusão via conector foi bloqueada.

## Próxima microetapa recomendada

Após validação local, remover manualmente/localmente ou reabrir em nova microetapa os dois stubs pendentes:

```text
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py
scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_chave_tau_v149.py
```

Em seguida, validar novamente `python aplicacao/principal.py`.
