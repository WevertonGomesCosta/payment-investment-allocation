# Auditoria e remoção controlada de stubs V203 — lote 04 — V225

## Identificação

- Baseline operacional: V225
- Tipo: limpeza estrutural controlada
- Escopo: scripts diagnósticos bloqueados por governança V203 em `scripts/diagnostico/temporal_decisao/bloco_critico/`
- Classe: remoção física de stubs sem autoridade operacional
- Resultado: lote concluído

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

O lote 04 foi restrito a arquivos que atendiam simultaneamente aos critérios:

1. arquivo físico ainda existia em `scripts/diagnostico/temporal_decisao/bloco_critico/`;
2. conteúdo era apenas stub de bloqueio V203;
3. o docstring declarava preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/bloco_critico/`;
4. a execução chamava apenas `scripts.diagnostico._governanca_saida.bloquear_script_legado(...)`;
5. não havia import operacional ativo nos resultados de busca;
6. referências remanescentes eram documentais/históricas em README, relatórios ou inventários.

## Arquivos removidos

Foram removidos os três stubs do lote 04:

```text
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py
scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py
```

## Evidência de preservação histórica

Os três arquivos removidos declaravam que seu conteúdo original havia sido preservado em:

```text
scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/bloco_critico/<nome_do_script>.py
```

Portanto, a remoção física dos stubs no caminho antigo não elimina a trilha histórica original.

## Evidência de ausência operacional

A busca por referências aos nomes dos três arquivos localizou referências documentais/históricas em:

- `scripts/diagnostico/temporal_decisao/README.md`;
- `relatorios/atuais/MAPA_SCRIPTS_V201.md`;
- `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md`;
- `relatorios/atuais/RELATORIO_CONSOLIDADO_ESTRUTURAS_HISTORICAS_V091_V120.md`;
- `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V091_V120.md`;
- `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv`;
- demais inventários históricos.

Não foi localizada dependência operacional ativa em `aplicacao/principal.py`, `aplicacao/console/`, `scripts/operacional/` ou `nucleo/contexto_baseline.py`.

## Estado após remoção

Consulta direta aos três caminhos no `main` retornou ausência do arquivo (`404`), confirmando a remoção física completa do lote 04.

## Commits da microetapa

- `b97a443f826f9652834ce814187b9037c2608bb3` — removeu `inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- `1845cd7a16b6fbd4249280b754d59ccf2771a853` — removeu `inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`
- `dcf6ce1c5b822fe72842c8f9af0287022321b9f5` — removeu `inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
- este relatório — registra a auditoria e conclusão do lote 04

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
4. nenhuma falha por ausência dos três scripts removidos.

## Decisão

O lote 04 está concluído.

A remoção é considerada segura porque:

1. os três arquivos removidos eram apenas stubs V203;
2. não havia lógica funcional própria nos caminhos atuais;
3. o conteúdo original permaneceu preservado no histórico V203;
4. não havia dependência operacional ativa;
5. a remoção ficou limitada a um lote pequeno e auditável.

## Próxima microetapa recomendada

Após validação local, a próxima limpeza pode continuar em lote pequeno com outros stubs V203 ainda existentes, ou abrir auditoria para atualizar inventários de scripts após os lotes 01–04.
