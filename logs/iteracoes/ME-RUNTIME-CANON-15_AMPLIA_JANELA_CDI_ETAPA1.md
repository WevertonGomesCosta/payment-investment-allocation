# ME-RUNTIME-CANON-15 — Ampliação canônica mínima de JanelaConsultaCDI na Etapa 1

## Objetivo

Implementar a ampliação canônica mínima de `JanelaConsultaCDI` em `nucleo/leitor_planilha.py`, cobrindo datas operacionais necessárias ao replay passado, sem alterar replay, saída canônica, motor ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: da2c0f6bd01a8e46096ff80b67ec6dc62d5a173c
ULTIMO_MERGE: PR #384 — ME-RUNTIME-CANON-14 diagnostica origem da JanelaConsultaCDI
```

## Auditoria pós-merge da ME-RUNTIME-CANON-14

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 9e37798 -> da2c0f6
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-15.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis atuais, com cache local atualizado:

```text
relatorio_operacional_v225.xlsx: gerado
Patrimônio líquido atual: 79905.02
Rendimento líquido atual: 964.86
Rendimento líquido atual — reconciliado contra recebidos: 877.86
Ranking top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
Switchings reais: 4
```

Gate V4Z:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Escopo permitido

```text
nucleo/leitor_planilha.py
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/contexto_baseline.py
nucleo/cache_cdi_bcb.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
nucleo/construir_saida_canonica_v17_c7.py
scripts/diagnostico/*
dados/*
saidas/*
```

A ME-RUNTIME-CANON-15 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Alteração aplicada

A função `construir_janela_consulta_cdi(...)` foi ampliada de forma conservadora.

Foram adicionadas funções auxiliares internas em `nucleo/leitor_planilha.py`:

```text
_primeiro_dia_do_mes_janela_cdi(...)
_nome_temporal_para_janela_cdi(...)
_resolver_coluna_janela_cdi(...)
_datas_coluna_janela_cdi(...)
```

## Mudanças de comportamento da janela

### Antes

A janela era derivada apenas de campos resolvidos cujo nome estrutural continha:

```text
data
vencimento
```

A data inicial era exatamente a menor data identificada.

### Depois

A janela passa a:

```text
1. preservar a data de referência como limite mínimo superior;
2. usar campos resolvidos cujo nome ou coluna contém data/vencimento;
3. resolver corretamente coluna física ou coluna canonizada no quadro estrutural resolvido;
4. varrer colunas operacionais adicionais cujo nome contém data/vencimento;
5. ignorar datas futuras acima da data de referência para o replay passado;
6. definir data_inicial_consulta como o primeiro dia do mês da menor data identificada;
7. definir data_final_consulta como pelo menos a data de referência;
8. registrar metadados auditáveis sobre fontes, colunas não resolvidas e datas futuras ignoradas.
```

## Intenção técnica

A alteração corrige a causa classificada nas ME-RUNTIME-CANON-12/13/14:

```text
ContextoOperacionalCanonico usava uma JanelaConsultaCDI estreita, insuficiente para replay passado.
ContextoBaseline usava janela ampla derivada de dados operacionais.
A janela canônica agora deve carregar a cobertura temporal necessária ao replay sem remover o uso de JanelaConsultaCDI.
```

## O que esta microetapa não faz

```text
não altera contexto_baseline.py
não altera cache_cdi_bcb.py
não altera replay_passado
não altera saida_canonica.py
não altera saida_observavel.py
não altera motor
não altera regra econômica
não promove ContextoSaidaCanonicaCompat
não substitui ContextoBaseline
não commita dados/cache_bcb.json
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Validação diagnóstica recomendada:

```bash
python - <<'PY'
from pathlib import Path
from nucleo.contexto_baseline import carregar_contexto_baseline, carregar_contexto_operacional_canonico
from nucleo.comparacao_componentes_contextos import comparar_componentes_contextos, imprimir_resumo_comparacao_componentes

raiz = Path.cwd()
ctx_base = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
ctx_can = carregar_contexto_operacional_canonico(raiz_repositorio=raiz, instalar_automaticamente=False)
resultado = comparar_componentes_contextos(ctx_base, ctx_can, componentes=["cache_cdi.serie_cdi"])
imprimir_resumo_comparacao_componentes(resultado)
raise SystemExit(0 if resultado.ok else 1)
PY
```

Critério de sucesso:

```text
A divergência em cache_cdi.serie_cdi deve ser reduzida ou eliminada.
Se cache_cdi.serie_cdi passar a ser equivalente, as próximas divergências devem ser reavaliadas em replay_passado.log_passado e replay_passado.lotes_apos_replay.
```

## Decisão

```text
STATUS: AMPLIACAO_CANONICA_MINIMA_JANELA_CDI_IMPLEMENTADA
ALTERA_LEITOR_PLANILHA: true
ALTERA_CACHE_CDI_BCB: false
ALTERA_REPLAY: false
ALTERA_SAIDA_CANONICA: false
ALTERA_MOTOR: false
ALTERA_DADOS: false
ALTERA_REGRA_ECONOMICA: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
ETAPA_5_LIBERADA: false
```
