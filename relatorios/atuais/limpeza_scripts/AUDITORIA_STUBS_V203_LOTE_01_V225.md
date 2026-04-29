# Auditoria e remoção controlada de stubs V203 — lote 01 — V225

## Identificação

- Baseline operacional: V225
- Tipo: limpeza estrutural controlada
- Escopo: scripts diagnósticos bloqueados por governança V203
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

O lote 01 foi restrito a arquivos que atendiam simultaneamente aos critérios:

1. arquivo físico ainda existia em `scripts/diagnostico/`;
2. conteúdo era apenas stub de bloqueio V203;
3. o docstring declarava preservação do conteúdo original em `scripts/historico_saida_propria_v203/diagnostico_original/`;
4. a execução chamava apenas `scripts.diagnostico._governanca_saida.bloquear_script_legado(...)`;
5. não havia import operacional ativo nos resultados de busca;
6. referências remanescentes eram documentais/históricas em relatórios ou inventários.

## Arquivos removidos

Foram removidos os seguintes stubs:

```text
scripts/diagnostico/inspecionar_mapa_absorcao_legado.py
scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
scripts/diagnostico/inspecionar_contrato_f1.py
scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
```

## Evidência de preservação histórica

Cada arquivo removido declarava que seu conteúdo original havia sido preservado em:

```text
scripts/historico_saida_propria_v203/diagnostico_original/<nome_do_script>.py
```

Portanto, a remoção física do stub no caminho antigo não elimina a trilha histórica original.

## Evidência de ausência operacional

A busca por referências aos nomes dos quatro arquivos localizou apenas referências em relatórios, inventários e documentos históricos, como:

- `relatorios/atuais/MAPA_SCRIPTS_V201.md`
- `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md`
- `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv`
- `relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv`

Não foi localizada dependência operacional ativa em `aplicacao/principal.py`, `aplicacao/console/`, `scripts/operacional/` ou `nucleo/contexto_baseline.py`.

## Estado após remoção

Consulta direta aos quatro caminhos no `main` retornou ausência do arquivo (`404`), confirmando a remoção física dos stubs.

## Commits da microetapa

- `c6910701d434ffbe959c58a7c176ab4c99cfb696` — removeu `inspecionar_mapa_absorcao_legado.py`
- `c7833c37925bf00ea707ba9d110a2395eebe93c0` — removeu `inspecionar_mapa_execucao_principal_script2.py`
- commit intermediário de limpeza 03 — removeu `inspecionar_contrato_f1.py`
- `fd156e5f1baf5dd90c5aeda4bd450bffde57be52` — removeu `inspecionar_auditoria_estrutural_redundancia.py`

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
4. nenhuma falha por ausência dos quatro scripts removidos.

## Decisão

A remoção do lote 01 é considerada segura, porque os arquivos removidos eram apenas bloqueios preventivos, sem lógica funcional própria no caminho atual e com conteúdo original preservado no histórico V203.

## Próxima microetapa recomendada

A próxima limpeza deve repetir o mesmo padrão com outro lote pequeno de stubs V203, priorizando arquivos ainda existentes em subpastas de `scripts/diagnostico/temporal_decisao/` que tenham conteúdo de 7 a 40 linhas e apenas redirecionamento/bloqueio, sempre com busca de referências antes da remoção.
