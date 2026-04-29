# Auditoria de remoção do wrapper da planilha operacional — V225

## Identificação

- Baseline operacional: V225
- Tipo: microetapa estrutural/organizacional
- Classe: remoção segura de wrapper obsoleto
- Arquivo removido: `scripts/operacional/gerar_planilha_operacional_configurada.py`

## Objetivo

Auditar referências restantes ao wrapper `gerar_planilha_operacional_configurada.py` após a fusão progressiva da lógica configurável no gerador base `scripts/operacional/gerar_planilha_operacional.py`.

Se não houvesse dependência operacional real, remover o wrapper e registrar que o gerador base passou a ser a fonte única da planilha operacional.

## Evidência 1 — rota operacional atual

O entrypoint principal `aplicacao/principal.py` importa diretamente o gerador base:

```python
from scripts.operacional.gerar_planilha_operacional import main as main_planilha
```

A cadeia operacional passa a ser:

```text
aplicacao/principal.py
→ scripts/operacional/gerar_planilha_operacional.py
```

Portanto, `gerar_planilha_operacional_configurada.py` não está mais na rota principal.

## Evidência 2 — referências restantes

As buscas por `gerar_planilha_operacional_configurada` localizaram referências apenas em relatórios/documentos históricos da própria limpeza estrutural, especialmente:

- `AUDITORIA_POS_PUSH_PLANILHA_OPERACIONAL_CONFIGURAVEL_V225.md`
- `AUDITORIA_HARDCODED_PLANILHA_OPERACIONAL_V225.md`

Não foi localizada dependência operacional ativa em código.

## Decisão

Remover o arquivo:

```text
scripts/operacional/gerar_planilha_operacional_configurada.py
```

O arquivo era apenas compatibilidade temporária e já havia sido validado após a fusão. Como o `principal.py` chama diretamente o gerador base, sua remoção não deve afetar a execução operacional.

## Commits relacionados

- `43a2119815a4ad7c554566bdb9d04684e6353309` — fundiu a lógica configurável no gerador base
- `00a8ddcb894baa03a2bb4f06c59cb886fe35d5b0` — transformou o wrapper em delegador temporário
- `0c2f670b3c68d1af19d9dbc39858201d7b84433a` — corrigiu a execução direta do wrapper durante a fase de compatibilidade
- `21e227c8563ca5b5336bb0f1492a82677c4cd76c` — removeu o wrapper obsoleto

## Restrições respeitadas

Esta microetapa não alterou:

- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- estilos;
- cabeçalhos;
- config;
- identidade da baseline.

## Validação local recomendada

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

1. execução sem erro;
2. saída operacional em `saidas/oficial/relatorio_operacional_v225.xlsx`;
3. abas e cabeçalhos preservados;
4. aba `Situação Atual` preservada;
5. console sem alteração econômica observável.

## Conclusão

O wrapper `gerar_planilha_operacional_configurada.py` foi removido com segurança. O gerador base `gerar_planilha_operacional.py` passa a ser a fonte única da planilha operacional.
