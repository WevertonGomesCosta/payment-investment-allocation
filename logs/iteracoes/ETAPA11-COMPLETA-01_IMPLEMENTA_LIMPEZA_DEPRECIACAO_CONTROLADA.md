# ETAPA11-COMPLETA-01 — Implementa Limpeza e Depreciação Controlada

## Baseline de entrada

- Branch inicial observada: `work`.
- Commit de entrada observado: `4b0a42f Merge pull request #472 from WevertonGomesCosta/etapa11-contrato-01`.
- Diagnósticos iniciais executados:
  - `git status --short` sem alterações locais listadas.
  - `git log --oneline -n 8` confirmou o merge `4b0a42f` no topo local.
  - `git branch --show-current` retornou `work`.
- Branch criada para a frente: `etapa11-completa-01`.

## Objetivo

Implementar a Etapa 11 completa, com o artefato `ResultadoLimpezaDepreciacaoControlada` e a função pública `construir_resultado_limpeza_depreciacao_controlada(...)`, consumindo `ResultadoParidadeRenderizacaoOficial` como entrada formal de estado e permitindo evidências auxiliares apenas para classificação não decisória de limpeza/depreciação controlada.

## Arquivos alterados

- `nucleo/limpeza_depreciacao_controlada.py`
- `aplicacao/principal.py`
- `logs/iteracoes/ETAPA11-COMPLETA-01_IMPLEMENTA_LIMPEZA_DEPRECIACAO_CONTROLADA.md`

## Artefato implementado

Foi implementado `ResultadoLimpezaDepreciacaoControlada` com os campos contratuais diretos:

- `artefato`
- `etapa`
- `status`
- `ok`
- `entrada_formal`
- `origem_formal`
- `itens`
- `resumo`
- `auditoria`
- `metadados`
- `recomendacoes`
- `retorno_etapa1`

Também foram implementadas dataclasses explícitas para itens, resumo, auditoria e metadados.

## Função pública implementada

Foi implementada `construir_resultado_limpeza_depreciacao_controlada(resultado_paridade_renderizacao, evidencias_auxiliares=None)` aplicando os blocos funcionais contratados:

- `validar_entrada_limpeza_depreciacao(...)`
- `extrair_evidencias_paridade(...)`
- `verificar_status_paridade(...)`
- `incorporar_evidencias_auxiliares_nao_decisorias(...)`
- `classificar_ressalvas_nao_materiais(...)`
- `identificar_rotas_oficiais_preservadas(...)`
- `identificar_rotas_legadas_candidatas(...)`
- `classificar_itens_limpeza(...)`
- `classificar_bloqueios_depreciacao(...)`
- `montar_plano_retorno_etapa1(...)`
- `consolidar_resultado_limpeza_depreciacao(...)`
- `montar_metadados_limpeza_depreciacao(...)`

## Integração runtime

A Etapa 11 foi integrada em `aplicacao/principal.py` após a execução da Etapa 10 por `validar_paridade_renderizacao_oficial(...)`. A integração imprime a seção observável:

```text
=== LIMPEZA E DEPRECIAÇÃO CONTROLADA — ETAPA 11 ===
```

com artefato, entrada formal, status, ok, contagens resumidas, retorno à Etapa 1 e recomendações principais.

## Fronteiras preservadas

A implementação preserva sem alteração funcional:

- motor;
- ledger;
- gates;
- Etapa 9;
- Etapa 10;
- contrato mestre;
- modelo oficial;
- dados financeiros;
- cache BCB;
- console/XLSX econômico;
- lógica econômica;
- decisões de pagamento;
- ranking;
- switching;
- liquidez;
- rendimento;
- patrimônio terminal.

A Etapa 11 classifica e recomenda, mas não remove automaticamente arquivos, funções, rotas, logs, saídas ou artefatos.

## Correção pós-review P2 — dependência ativa

O PR recebeu comentário P2 solicitando que itens classificados como `bloqueado_dependencia_ativa` afetassem a decisão de status.

A correção aplicada em `nucleo/limpeza_depreciacao_controlada.py` faz com que:

- `consolidar_resultado_limpeza_depreciacao(...)` considere `bloqueios` no cálculo de `status`;
- qualquer bloqueio por dependência ativa rebaixe o resultado para, no mínimo, `aprovado_com_ressalva` quando não houver bloqueio material de paridade;
- divergência material de paridade continue produzindo `status='bloqueado'`;
- `montar_plano_retorno_etapa1(...)` registre `qtd_bloqueios_dependencia_ativa`, `bloqueado_por_dependencia_ativa`, `depreciacao_efetiva_permitida=False` e `remocao_automatica_autorizada=False`;
- `retorno_etapa1['permitido']` deixe de indicar permissão simples quando houver dependência ativa bloqueante;
- a recomendação passe a orientar resolver ou documentar dependências ativas antes de qualquer depreciação ou remoção efetiva.

A correção mantém a distinção entre retorno operacional controlado e autorização de remoção/depreciação efetiva.

## Correção pós-review P2 — evidência escalar e resumo de bloqueios

O PR recebeu comentários P2 adicionais sobre:

- perda de `status`, `categoria`, `tipo` ou `classificacao` quando `evidencias_auxiliares` é fornecido como mapping escalar simples, por exemplo `{"identificador": "rota_legacy", "status": "deprecated"}`;
- uso de `qtd_bloqueios_paridade` para contar bloqueios por dependência ativa, confundindo bloqueio de remoção/depreciação com falha da Etapa 10.

A correção aplicada faz com que:

- `_normalizar_evidencias_iteraveis(...)` trate mappings escalares com chaves como `identificador`, `nome`, `path`, `status`, `categoria`, `tipo` ou `classificacao` como uma única evidência auxiliar;
- `status`, `categoria`, `tipo` e `classificacao` sejam preservados para a classificação controlada;
- `ResumoLimpezaDepreciacaoControlada` passe a expor `qtd_bloqueios_dependencia_ativa`;
- `qtd_bloqueios_paridade` conte somente bloqueios originados de `paridade_material_bloqueante`;
- bloqueios por dependência ativa continuem rebaixando o status, mas sem sinalizar falsamente falha da Etapa 10.

Cenários esperados após a correção:

```python
evidencias_auxiliares={"identificador": "rota_legacy", "status": "deprecated"}
# classifica como legado_candidato_depreciacao

evidencias_auxiliares={"identificador": "rota_ativa", "status": "dependencia ativa"}
# classifica como bloqueado_dependencia_ativa, rebaixa status e mantém remocao_automatica_autorizada=False
```

## Correção pós-review P2 — marcador negativo de uso

O PR recebeu comentário P2 apontando que `status="sem uso"` poderia ser classificado indevidamente como `bloqueado_dependencia_ativa` por conter a substring `em uso`.

A correção aplicada faz com que:

- marcadores negativos como `sem uso`, `fora de uso`, `não usado`, `nao usado`, `unused` e `not used` sejam avaliados antes dos marcadores fracos de uso positivo;
- `dependencia ativa`, `dependência ativa` e `bloqueado` continuem sendo marcadores positivos fortes de bloqueio;
- `em uso` e `in use` só classifiquem como dependência ativa se não houver marcador negativo de uso;
- evidências como `{"identificador": "rota_sem_uso", "status": "sem uso", "tipo": "legado"}` não sejam bloqueadas por falso positivo de uso ativo e possam cair em classificação legada/depreciação ou avaliação posterior conforme os demais marcadores.

Cenário esperado após a correção:

```python
evidencias_auxiliares={"identificador": "rota_sem_uso", "status": "sem uso", "tipo": "legado"}
# não classifica como bloqueado_dependencia_ativa
```

## Correção pós-review P2 — inventário auxiliar vazio

O PR recebeu comentário P2 apontando que inventários auxiliares vazios, como `None`, `[]`, `{}` ou coleções sem itens normalizados, deveriam ser tratados como ausência efetiva de evidência auxiliar.

A correção aplicada faz com que:

- `construir_resultado_limpeza_depreciacao_controlada(...)` calcule `evidencias_auxiliares_fornecidas = bool(itens_auxiliares)`;
- inventários vazios mantenham o item conservador `inventario_auxiliar_ausente`;
- `classificacao_limitada_por_ausencia_inventario=True` seja preservado quando não houver itens auxiliares efetivos;
- o status permaneça `aprovado_com_ressalva` nesses casos conservadores;
- a recomendação de inventário estático auxiliar em frente posterior continue aparecendo.

Cenários esperados após a correção:

```python
evidencias_auxiliares=None
# inventario_auxiliar_ausente presente

evidencias_auxiliares=[]
# inventario_auxiliar_ausente presente

evidencias_auxiliares={}
# inventario_auxiliar_ausente presente
```

## Correção pós-review P2 — mapa compacto identificador/status

O PR recebeu comentário P2 apontando que mappings compactos no formato `identificador -> status`, por exemplo `{"rota_api": "dependencia ativa"}`, perdiam o valor escalar durante a normalização.

A correção aplicada faz com que:

- quando a chave do mapping for o identificador e o valor for escalar, esse valor seja preservado em `status` e `valor_original`;
- `{"rota_api": "dependencia ativa"}` seja normalizado como identificador `rota_api` com status `dependencia ativa`;
- `{"rota_legacy": "deprecated"}` seja normalizado como identificador `rota_legacy` com status `deprecated`;
- `{"rota_sem_uso": "sem uso"}` seja normalizado como identificador `rota_sem_uso` com status `sem uso`.

Cenários esperados após a correção:

```python
evidencias_auxiliares={"rota_api": "dependencia ativa"}
# classifica como bloqueado_dependencia_ativa

evidencias_auxiliares={"rota_legacy": "deprecated"}
# classifica como legado_candidato_depreciacao

evidencias_auxiliares={"rota_sem_uso": "sem uso"}
# não classifica como bloqueado_dependencia_ativa
```

## Validações executadas

- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py` — aprovado na validação inicial da frente.
- `python -B aplicacao/principal.py` — aprovado na validação inicial da frente, com seção observável da Etapa 11 emitida após a Etapa 10.
- Teste inline mínimo — aprovado na validação inicial para construção, ressalva não material, execução sem evidências auxiliares, execução com evidências auxiliares e ausência de remoção automática.
- Após a correção P2, a lógica de status foi ajustada para cobrir o cenário `evidencias_auxiliares=[{"status": "dependencia ativa"}]`.
- Após a segunda correção P2, a normalização de evidência escalar e a separação de bloqueios de paridade/dependência ativa foram ajustadas no código.
- Após a terceira correção P2, a classificação de marcadores negativos de uso foi ajustada para evitar falso bloqueio em `sem uso`.
- Após a quarta correção P2, inventários auxiliares vazios passaram a ser tratados como ausência efetiva de evidências auxiliares.
- Após a quinta correção P2, mappings compactos `identificador -> status` passaram a preservar valores escalares em `status` e `valor_original`.
- `git diff --check` — aprovado na validação inicial da frente.
- `git status --short` — executado para conferência de alterações.
- `git diff --name-only origin/main...HEAD` — não executável no ambiente inicial do Codex por ausência de `origin/main` local; validado posteriormente pelo usuário em checkout local com remote disponível.
- `git diff --stat origin/main...HEAD` — não executável no ambiente inicial do Codex por ausência de `origin/main` local; validado posteriormente pelo usuário em checkout local com remote disponível.

## Limitações encontradas

- A tentativa de download da planilha remota durante `python -B aplicacao/principal.py` falhou por restrição de proxy (`403 Forbidden`) no ambiente do Codex, mas o runtime continuou com `fallback_local` e cache BCB local.
- Em validação local posterior do usuário, o download remoto da planilha retornou `ok` e o runtime executou até o fim.
- `origin/main` não estava disponível no ambiente inicial do Codex, impedindo os comandos comparativos `origin/main...HEAD`; a conferência continuou com `git status --short`, `git diff --check` e diff local contra `HEAD`.
- Nenhuma evidência auxiliar de inventário estático foi fornecida ao runtime principal; a Etapa 11 operou no modo conservador previsto, classificando a ausência de inventário como limitação para frente posterior.

## Decisão final

Implementação concluída no escopo da Etapa 11, com ausência de alteração econômica, sem autorização de remoção automática e pronta para nova auditoria do PR após as correções P2.

## Correção pós-review P2 — marcador negativo de bloqueio

O PR recebeu comentário P2 apontando que `status="não bloqueado"` e `status="desbloqueado"` ainda eram classificados indevidamente como `bloqueado_dependencia_ativa` por conterem a substring `bloqueado`.

A correção aplicada faz com que:

- marcadores negativos como `não bloqueado`, `nao bloqueado`, `desbloqueado`, `sem bloqueio`, `unblocked` e `not blocked` sejam avaliados antes do marcador positivo `bloqueado`/`blocked`;
- `dependencia ativa` e `dependência ativa` continuem como marcadores positivos fortes;
- `bloqueado` e `blocked` só classifiquem como `bloqueado_dependencia_ativa` quando não houver marcador negativo de bloqueio;
- evidências como `{"status": "não bloqueado", "tipo": "legado"}` e `{"status": "desbloqueado", "tipo": "legado"}` não sejam bloqueadas por falso positivo.

Cenários esperados:

```python
{"status": "não bloqueado", "tipo": "legado"}
# não classifica como bloqueado_dependencia_ativa

{"status": "desbloqueado", "tipo": "legado"}
# não classifica como bloqueado_dependencia_ativa

{"status": "bloqueado", "tipo": "legado"}
# classifica como bloqueado_dependencia_ativa
