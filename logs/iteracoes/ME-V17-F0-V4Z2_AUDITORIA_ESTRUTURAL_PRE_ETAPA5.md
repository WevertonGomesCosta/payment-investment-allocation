# ME-V17-F0-V4Z2 — Auditoria estrutural pré-Etapa 5

```text
MICROETAPA: ME-V17-F0-V4Z2
VERSAO_CANDIDATA: V17-F0-V.4Z2
TIPO: DOCUMENTAL / DIAGNOSTICO
CLASSE: INVENTARIO_FUNCOES_ENTRADAS_SAIDAS_CONSUMIDORES_RESIDUOS
ESCOPO:
  - aplicacao/principal.py
  - aplicacao/console/*.py
  - nucleo/*.py
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ALTERA_RANKING: false
ALTERA_XLSX: false
ALTERA_CONTEXT_BASELINE: false
ALTERA_DADOS: false
```

## Motivação

A V4Z1 criou `ContextoOperacionalCanonico`, mas não encerrou o saneamento pré-Etapa 5. Ainda há resíduos observáveis no núcleo e a rota `aplicacao/principal.py` permanece como runtime principal a validar.

Antes de abrir a Etapa 5, é necessário inventariar mecanicamente funções, entradas, saídas, consumidores e resíduos da rota operacional e do núcleo vivo.

## Evidência de runtime local recebida

Foi executado localmente:

```bash
python -B aplicacao/principal.py
python -m py_compile aplicacao/principal.py nucleo/contexto_baseline.py scripts/diagnostico/auditar_nucleo_vivo_v4z.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

A execução de `principal.py` gerou `saidas/oficial/relatorio_operacional_v225.xlsx` sem traceback e confirmou origem de dados por download e CDI/BCB online. A auditoria V4Z1 em `main` retornou `entrada_limpa_etapa5_ok=True` para o contexto limpo.

## Arquivo criado

```text
scripts/diagnostico/auditar_estrutura_pre_etapa5_v4z2.py
```

## Saídas esperadas do auditor

Ao rodar sem `--sem-arquivos`, o auditor grava:

```text
relatorios/atuais/auditoria_pre_etapa5_v4z2/inventario_estrutura_pre_etapa5_v4z2.json
relatorios/atuais/auditoria_pre_etapa5_v4z2/inventario_modulos_pre_etapa5_v4z2.csv
relatorios/atuais/auditoria_pre_etapa5_v4z2/inventario_funcoes_pre_etapa5_v4z2.csv
relatorios/atuais/auditoria_pre_etapa5_v4z2/residuos_modulos_pre_etapa5_v4z2.csv
relatorios/atuais/auditoria_pre_etapa5_v4z2/resumo_auditoria_pre_etapa5_v4z2.md
```

## Critério de uso

A V4Z2 é apenas diagnóstica. Ela não autoriza abertura da Etapa 5. O inventário produzido deve ser analisado para decidir quais módulos serão mantidos, canonizados, isolados, arquivados ou corrigidos antes da Etapa 5.

## Comandos de validação

```bash
python -m py_compile scripts/diagnostico/auditar_estrutura_pre_etapa5_v4z2.py
python scripts/diagnostico/auditar_estrutura_pre_etapa5_v4z2.py --sem-arquivos
python scripts/diagnostico/auditar_estrutura_pre_etapa5_v4z2.py
```
