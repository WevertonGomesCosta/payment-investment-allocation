# Validação local V75

## Escopo validado

- identidade da baseline atualizada para V75;
- criação do mapa de absorção legado para os Scripts 1 e 2;
- criação do diagnóstico `inspecionar_mapa_absorcao_legado.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.

## Comandos executados

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_absorcao_legado.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Evidências observáveis da V75

- o mapa vigente classifica os blocos dos Scripts 1 e 2 em `migrar já`, `migrar depois`, `não migrar` e `substituída pela baseline`;
- o diagnóstico do mapa imprime prioridades imediatas de absorção legado sem alterar o fluxo principal;
- a baseline continua executável e o release checker continua aprovando o pacote final em estado limpo.


## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v75.xlsx`
