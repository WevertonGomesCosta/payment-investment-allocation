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

## Validações executadas

- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py` — aprovado na validação inicial da frente.
- `python -B aplicacao/principal.py` — aprovado na validação inicial da frente, com seção observável da Etapa 11 emitida após a Etapa 10.
- Teste inline mínimo — aprovado na validação inicial para construção, ressalva não material, execução sem evidências auxiliares, execução com evidências auxiliares e ausência de remoção automática.
- Após a correção P2, a lógica de status foi ajustada para cobrir o cenário `evidencias_auxiliares=[{"status": "dependencia ativa"}]`.
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

Implementação concluída no escopo da Etapa 11, com ausência de alteração econômica, sem autorização de remoção automática e pronta para nova auditoria do PR após a correção P2.
