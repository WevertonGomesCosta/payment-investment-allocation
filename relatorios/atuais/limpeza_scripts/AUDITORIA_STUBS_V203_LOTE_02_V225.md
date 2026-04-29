# Auditoria e remoção controlada de stubs V203 — lote 02 — V225

## Identificação

- Baseline operacional: V225
- Tipo: limpeza estrutural controlada
- Escopo: scripts diagnósticos bloqueados por governança V203 em `scripts/diagnostico/temporal_decisao/`
- Classe: remoção física de stubs sem autoridade operacional

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

O lote 02 foi restrito a arquivos que atendiam simultaneamente aos critérios:

1. arquivo físico ainda existia em `scripts/diagnostico/temporal_decisao/motor_diario/`;
2. conteúdo era apenas stub de bloqueio V203;
3. o docstring declarava preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/motor_diario/`;
4. a execução chamava apenas `scripts.diagnostico._governanca_saida.bloquear_script_legado(...)`;
5. não havia import operacional ativo nos resultados de busca;
6. referências remanescentes eram documentais/históricas em relatórios, README ou inventários.

## Arquivos removidos

Foram removidos os seguintes stubs:

```text
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v143.py
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v144.py
scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_pos_vencimento_v146.py
```

## Evidência de preservação histórica

Cada arquivo removido declarava que seu conteúdo original havia sido preservado em:

```text
scripts/historico_saida_propria_v203/diagnostico_original/temporal_decisao/motor_diario/<nome_do_script>.py
```

Portanto, a remoção física do stub no caminho antigo não elimina a trilha histórica original.

## Evidência de ausência operacional

A busca por referências aos nomes dos três arquivos localizou apenas referências documentais/históricas em:

- `scripts/diagnostico/temporal_decisao/README.md`;
- `relatorios/atuais/MAPA_SCRIPTS_V201.md`;
- `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md`;
- `relatorios/atuais/limpeza_scripts/candidatos_remocao_scripts_diagnostico.csv`;
- `relatorios/atuais/limpeza_scripts/auditoria_wrappers_temporal_decisao.csv`;
- `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv`;
- demais inventários históricos.

Não foi localizada dependência operacional ativa em `aplicacao/principal.py`, `aplicacao/console/`, `scripts/operacional/` ou `nucleo/contexto_baseline.py`.

## Estado após remoção

Consulta direta aos três caminhos no `main` retornou ausência do arquivo (`404`), confirmando a remoção física dos stubs.

## Commits da microetapa

- `db30aa8cc392cb56af8ca37adb4e5c15cdf51324` — removeu `inspecionar_motor_diario_conjunto_experimental_v143.py`
- commit intermediário de limpeza — removeu `inspecionar_motor_diario_conjunto_experimental_v144.py`
- `a25f4aacbc77aac98ff17f880b372e6a512f9b45` — removeu `inspecionar_motor_diario_pos_vencimento_v146.py`

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

A remoção do lote 02 é considerada segura, porque os arquivos removidos eram apenas bloqueios preventivos, sem lógica funcional própria no caminho atual e com conteúdo original preservado no histórico V203.

## Próxima microetapa recomendada

A próxima limpeza deve repetir o padrão com outro lote pequeno, preferencialmente em `scripts/diagnostico/temporal_decisao/valoracao_decisao/`, removendo apenas stubs puros com histórico preservado e sem referência operacional ativa.
