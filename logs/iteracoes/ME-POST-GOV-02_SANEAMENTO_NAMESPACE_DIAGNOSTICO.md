# ME-POST-GOV-02 — Saneamento final do namespace diagnóstico pós-GOV

## Objetivo

Abrir uma microetapa restrita ao saneamento de `scripts/diagnostico/*` após a formalização do GOV-01.

A finalidade é eliminar o índice diagnóstico obsoleto, registrar a classificação inicial dos scripts remanescentes e impedir que diagnósticos transitórios sejam tratados como gates permanentes ou como fonte normativa operacional.

## Baseline de entrada

```text
BASELINE: main
HEAD: 693a730b7997d6dba5d0a380d7a0b4d2902f2749
ULTIMO_MERGE: PR #363 — ME-GOV-01 ciclo de vida de diagnósticos
```

## Escopo permitido

```text
scripts/diagnostico/*
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
relatorios/principais/*
saidas/*
```

A ME-POST-GOV-02 não altera motor, replay, ledger, ranking, saída canônica, regra econômica, contrato mestre ou modelo oficial.

## Auditoria de entrada executada pelo usuário

### Estado Git

```text
git checkout main: aprovado
git pull --ff-only: aprovado
git status --short: vazio
git log --oneline -8: HEAD em 693a730, merge da PR #363
```

### Gates executáveis

```text
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Resultado V4Z reportado:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Achado motivador

O arquivo `scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md` ainda estava na versão V17-F0-V.4T e referenciava diagnósticos removidos ou não mais pertencentes à rota viva.

Esse estado conflita com o GOV-01 porque scripts diagnósticos só podem permanecer como gates permanentes mediante classificação explícita, estável e compatível com a rota canônica vigente.

## Alteração inicial da microetapa

O índice diagnóstico foi saneado para:

1. declarar explicitamente `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` como o único gate permanente já preservado;
2. classificar os demais scripts remanescentes como `TRANSITORIO_PENDENTE`;
3. proibir uso desses diagnósticos como norma superior, fonte operacional ou gate permanente sem promoção formal;
4. registrar que o destino padrão de diagnóstico não promovido é remoção ou arquivamento fora da rota viva.

## Decisão da abertura

```text
STATUS: MICROETAPA_ABERTA
TIPO: GOVERNANCA_DIAGNOSTICA
CLASSE: SANEAMENTO_NAMESPACE_DIAGNOSTICO
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
```

## Próxima ação dentro da ME-POST-GOV-02

A próxima ação deve ser uma classificação decisória dos scripts `TRANSITORIO_PENDENTE`, separando:

1. remover imediatamente;
2. arquivar fora da rota viva;
3. substituir por evidência estática;
4. promover formalmente a gate permanente, apenas se cumprir GOV-01.

Não iniciar canonização da rota runtime versionada enquanto essa classificação não estiver fechada.
