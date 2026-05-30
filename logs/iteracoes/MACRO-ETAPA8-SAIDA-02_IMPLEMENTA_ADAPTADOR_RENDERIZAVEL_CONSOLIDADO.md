# MACRO-ETAPA8-SAIDA-02 — Implementa adaptador renderizável consolidado sem integrar console/XLSX

## 1. Identificação

- **Macrofrente:** MACRO-ETAPA8-SAIDA-02
- **Tipo:** funcional consolidada
- **Baseline de entrada:** `fbc0a0b8574e3d7f8d7037aec9d8d72e65b69bd1`
- **Branch:** `feat/macro-etapa8-saida-02`

## 2. Objetivo

Implementar o adaptador renderizável consolidado entre `SaidaCanonicaOficial` e a futura camada de renderização/exportação, sem integrar console/XLSX e sem gerar saída observável.

## 3. Arquivos alterados

```text
nucleo/adaptador_renderizacao_saida_canonica.py
logs/iteracoes/MACRO-ETAPA8-SAIDA-02_IMPLEMENTA_ADAPTADOR_RENDERIZAVEL_CONSOLIDADO.md
```

## 4. Implementação

O novo módulo define:

```python
BloqueioRenderizacaoSaidaCanonica
ComponenteRenderizacaoSaidaCanonica
PacoteRenderizacaoSaidaCanonica
construir_pacote_renderizacao_saida_canonica(...)
```

A função pública consome exclusivamente:

```text
SaidaCanonicaOficial
```

## 5. Componentes renderizáveis disponíveis

O pacote consolidado monta, quando possível:

- `situacao_atual_renderizavel`;
- `auditoria_renderizavel`;
- `switchings_renderizaveis`;
- `obrigacoes_cobertas_renderizaveis`;
- `obrigacoes_bloqueadas_renderizaveis`;
- `fontes_utilizadas_renderizaveis`;
- `fontes_reservadas_renderizaveis`;
- `saldos_referenciais_renderizaveis`;
- `bloqueios_renderizaveis`;
- `avisos_renderizaveis`;
- `evidencias_gates_renderizaveis`.

## 6. Componentes declarados indisponíveis

Continuam explicitamente indisponíveis, por ainda não serem deriváveis diretamente do schema atual de `SaidaCanonicaOficial`:

- `extrato_passado_renderizavel`;
- `extrato_futuro_renderizavel`;
- `resumo_recebidos_renderizavel`;
- `fechamento_atual_renderizavel`;
- `ranking_renderizavel`.

A indisponibilidade é registrada no próprio componente, sem consulta a dados brutos e sem reconstrução da saída legada.

## 7. Bloqueios implementados

A função bloqueia quando:

- a entrada não é `SaidaCanonicaOficial`;
- `SaidaCanonicaOficial.preparada=False`;
- `SaidaCanonicaOficial.ok=False`.

## 8. Restrições preservadas

Esta macrofrente não altera:

- `aplicacao/principal.py`;
- console;
- XLSX;
- motor temporal;
- ledger;
- gates;
- contratos;
- dados;
- saídas operacionais;
- ranking;
- score;
- regras econômicas.

Também não executa:

- reotimização;
- revaloração;
- nova escolha de fonte;
- alteração de obrigação;
- alteração de switching;
- alteração de saldo;
- geração de console;
- geração de XLSX.

## 9. Relação com a branch protótipo anterior

A branch `feat/micro-etapa8-adaptador-funcional-01` foi tratada como insumo técnico, não como solução final.

A presente macrofrente implementa versão consolidada mais ampla e alinhada ao contrato macro `CONTRATO_ETAPA8_SAIDA_POS_GATES_RENDERIZACAO.md`.

## 10. Validação esperada

```bash
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

O runtime deve preservar o bloqueio atual quando `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False`, sem gerar console/XLSX oficiais.

## 11. Próxima frente recomendada

```text
MACRO-ETAPA8-SAIDA-03 — Audita adaptador renderizável consolidado contra contrato macro e saída oficial
```

Escopo recomendado:

- auditar o módulo consolidado;
- validar ausência de importações proibidas;
- confirmar bloqueios;
- confirmar componentes disponíveis/indisponíveis;
- ainda não integrar `aplicacao/principal.py`, console ou XLSX.
