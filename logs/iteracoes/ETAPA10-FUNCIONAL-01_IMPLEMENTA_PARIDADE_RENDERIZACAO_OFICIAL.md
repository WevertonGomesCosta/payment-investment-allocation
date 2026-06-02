# ETAPA10-FUNCIONAL-01 — Implementa paridade da renderização oficial

## Baseline de entrada

- Repositório local: `/workspace/payment-investment-allocation`.
- Branch criada: `etapa10-funcional-01`.
- Commit de entrada: `2c6eba7`.
- Baseline confirmado no log local: `2c6eba7 Merge pull request #468 from WevertonGomesCosta/atualizacao-cache-bcb-01`.
- Contrato da Etapa 10 confirmado: `relatorios/principais/contratos_individuais/CONTRATO_ETAPA10_PARIDADE_RENDERIZACAO_OFICIAL.md`.
- Limitação de ambiente registrada: o remote `origin` não está configurado neste clone local; por isso `git fetch origin`, `git checkout main` e `git pull --ff-only origin main` não puderam ser concluídos. A execução continuou a partir do commit local esperado `2c6eba7`.

## Objetivo

Implementar o módulo funcional oficial `nucleo/paridade_renderizacao_oficial.py` para consumir `PacoteSaidaObservavelOficial` como referência de verdade e emitir `ResultadoParidadeRenderizacaoOficial`, auditando a paridade entre a saída observável oficial em memória e artefatos renderizados de XLSX/console, sem alterar runtime, console, XLSX, motor, ledger, gates, Etapa 9, dados financeiros ou lógica econômica.

## Arquivos alterados

- Criado: `nucleo/paridade_renderizacao_oficial.py`.
- Criado: `logs/iteracoes/ETAPA10-FUNCIONAL-01_IMPLEMENTA_PARIDADE_RENDERIZACAO_OFICIAL.md`.

## Módulo criado

- `nucleo/paridade_renderizacao_oficial.py`.

## Função pública criada

- `validar_paridade_renderizacao_oficial(pacote_saida_observavel, caminho_xlsx=None, console_renderizado=None)`.

## Artefato formal criado

- `ResultadoParidadeRenderizacaoOficial`.

## Dataclasses formais implementadas

- `DivergenciaParidadeRenderizacao`.
- `ResumoParidadeRenderizacaoOficial`.
- `AuditoriaParidadeXLSX`.
- `AuditoriaParidadeConsole`.
- `MetadadosParidadeRenderizacao`.
- `ResultadoParidadeRenderizacaoOficial`.

## Funções auxiliares implementadas

- `validar_entrada_paridade_renderizacao(...)`.
- `extrair_blocos_esperados_do_pacote(...)`.
- `ler_renderizacao_xlsx(...)`.
- `ler_renderizacao_console(...)`.
- `normalizar_valores_para_paridade(...)`.
- `comparar_presenca_estrutura(...)`.
- `comparar_headers(...)`.
- `comparar_quantidade_linhas(...)`.
- `comparar_conteudo_normalizado(...)`.
- `classificar_divergencias(...)`.
- `auditar_paridade_xlsx(...)`.
- `auditar_paridade_console(...)`.
- `consolidar_resultado_paridade(...)`.
- `montar_metadados_paridade(...)`.

## Regras de normalização implementadas

- `date` é normalizado para ISO `yyyy-mm-dd`.
- `datetime` à meia-noite é normalizado para ISO `yyyy-mm-dd`.
- `datetime` com horário real é normalizado para ISO datetime com segundos.
- Strings ISO inequívocas `yyyy-mm-dd` e `yyyy-mm-ddT00:00:00` são normalizadas para data ISO.
- Números `int`, `float` e `Decimal` são comparados por equivalência decimal, com tolerância absoluta `<= 0.005` e quantização a 2 casas decimais.
- Booleanos são preservados como booleanos.
- `None` é preservado como `None`.
- Strings comuns são preservadas; listas/dicionários serializados pelo exportador observável são mantidos como strings para não inventar estrutura decisória.

## Categorias de divergência implementadas

- `PARIDADE_OK`.
- `ARTEFATO_RENDERIZADO_AUSENTE`.
- `ABA_XLSX_AUSENTE`.
- `ABA_XLSX_EXTRA`.
- `DIVERGENCIA_ESTRUTURAL`.
- `DIVERGENCIA_HEADERS`.
- `DIVERGENCIA_QTD_LINHAS`.
- `DIVERGENCIA_CONTEUDO`.
- `DIVERGENCIA_SERIALIZACAO`.
- `DIVERGENCIA_NORMALIZACAO_NUMERICA`.
- `DIVERGENCIA_DATA_DATETIME`.
- `DIVERGENCIA_MATERIAL`.
- `CONSOLE_NAO_AUDITADO`.
- `CONSOLE_AUDITADO_COM_RESSALVA`.
- `MELHORIA_ERGONOMICA`.

## Auditoria XLSX

- A referência de verdade é `PacoteSaidaObservavelOficial.bloco_xlsx.abas`.
- O módulo reproduz localmente a lógica de nomeação das abas observáveis com prefixo `Obs ` e a normalização de linhas observáveis usada pelo exportador, evitando dependência em funções privadas de `nucleo/gerar_planilha_operacional.py`.
- A leitura de XLSX usa `openpyxl` quando o arquivo existe e a dependência está disponível.
- São comparadas abas observáveis esperadas/exportadas, headers, quantidade de linhas e conteúdo normalizado.
- Abas faltantes, abas extras e divergências materiais reprovam a paridade XLSX.

## Auditoria Console

- A referência de verdade é `PacoteSaidaObservavelOficial.bloco_console`.
- Quando `console_renderizado` é `None`, a auditoria de console é registrada como não executada com `CONSOLE_NAO_AUDITADO`, sem reprovar automaticamente o XLSX.
- Quando `console_renderizado` é fornecido como texto ou captura estruturada, o módulo compara presença mínima de seções/campos esperados.
- O console não é capturado automaticamente nesta frente e nenhum arquivo de `aplicacao/console/*` foi alterado.

## Validações executadas

### Baseline solicitado

```text
fatal: 'origin' does not appear to be a git repository
fatal: Could not read from remote repository.
error: pathspec 'main' did not match any file(s) known to git
fatal: 'origin' does not appear to be a git repository
fatal: Could not read from remote repository.
2c6eba7 Merge pull request #468 from WevertonGomesCosta/atualizacao-cache-bcb-01
5b5ec4a ATUALIZACAO-CACHE-BCB-01: atualiza cache BCB
7c165d8 Merge pull request #467 from WevertonGomesCosta/etapa10-contrato-01
5d85f59 ETAPA10-CONTRATO-01: alinha mapa funcional ao fluxograma
364df2f ETAPA10-CONTRATO-01: registra formalizacao paridade renderizacao
654da27 ETAPA10-CONTRATO-01: atualiza README contratos individuais
6fdc726 ETAPA10-CONTRATO-01: cria contrato paridade renderizacao oficial
d16d972 Merge pull request #466 from WevertonGomesCosta/atualizacao-dados-financeiros-01
CONTRATO_ETAPA10_EXISTE
Switched to a new branch 'etapa10-funcional-01'
```

### Compilação obrigatória

Comando executado:

```bash
python -m py_compile nucleo/paridade_renderizacao_oficial.py nucleo/saida_observavel_oficial.py nucleo/gerar_planilha_operacional.py
```

Resultado: aprovado, sem saída de erro.

### Validação inline obrigatória

Comando executado conforme especificação, sem executar `python -B aplicacao/principal.py`.

Resultado observado:

```text
artefato: ResultadoParidadeRenderizacaoOficial
status: bloqueado
ok: False
qtd_divergencias: 2
console_auditado: False
xlsx_auditado: False
```

Classificação objetiva das divergências na validação inline:

```text
ARTEFATO_RENDERIZADO_AUSENTE True XLSX informado para auditoria não existe ou não está acessível.
CONSOLE_NAO_AUDITADO False Console renderizado não foi fornecido; auditoria de console não executada nesta frente.
```

### Validação adicional de sanidade com XLSX temporário

Foi executada uma validação adicional em `/tmp`, criando um XLSX temporário derivado exclusivamente dos blocos esperados do próprio `PacoteSaidaObservavelOficial`, sem alterar arquivos do repositório.

Resultado observado:

```text
status: aprovado_com_ressalva
xlsx_auditado: True
console_auditado: False
divergencias: [('CONSOLE_NAO_AUDITADO', False)]
```

## Limitações encontradas

- Remote `origin` ausente no clone local; não foi possível buscar/puxar `main` remoto, mas o commit local esperado `2c6eba7` estava presente.
- Branch `main` não existe localmente neste clone; a branch funcional foi criada a partir do baseline local disponível.
- `saidas/oficial/relatorio_operacional_v225.xlsx` não existe no ambiente local. A validação de conteúdo do XLSX oficial depende de execução prévia do runtime (`python -B aplicacao/principal.py`), que não foi executado nesta frente por escopo.
- Console renderizado não foi fornecido; a auditoria de console ficou registrada como ressalva não material.

## Confirmação de ausência de alteração econômica

- Não houve alteração em `dados/*`, `saidas/*`, contratos, modelo matemático, `aplicacao/principal.py`, `aplicacao/console/*`, `nucleo/gerar_planilha_operacional.py`, `nucleo/saida_observavel_oficial.py`, motor, ledger, gates, ranking, switching, liquidez, rendimento, regras de pagamento, regras fiscais ou patrimônio líquido terminal.
- A Etapa 10 implementada é exclusivamente auditora de renderização e não consulta motor, ledger ou gates para corrigir ou redecidir conteúdo econômico.

## Próxima frente recomendada

- Integrar a Etapa 10 ao fluxo operacional somente em frente posterior, após geração/captura formal de XLSX e console, mantendo esta implementação como auditor oficial isolado.

## Refinamento pós-revisão — PR #469

- Ajustada a auditoria textual de console para verificar rótulo e valor esperado separadamente em cada campo de `resumo_operacional`.
- Quando o rótulo textual está presente, mas o valor esperado está ausente ou divergente, o módulo passa a registrar `CONSOLE_AUDITADO_COM_RESSALVA` com referências objetivas `rotulo_presente` e `valor_presente`.
- Validações reexecutadas: `python -m py_compile nucleo/paridade_renderizacao_oficial.py nucleo/saida_observavel_oficial.py nucleo/gerar_planilha_operacional.py` e script mínimo com XLSX temporário + console textual contendo valor correto e valor divergente.
- Confirmação mantida: sem alteração em motor, ledger, gates, Etapa 9, contrato, modelo, dados financeiros, cache BCB, runtime, console ou XLSX.
