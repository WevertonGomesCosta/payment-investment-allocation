# Validação local V79

## Escopo validado

- identidade da baseline atualizada para V79;
- criação da camada `switching_economico_shadow`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- preservação do motor financeiro, da F1 materializada e do `proxy econômico v3` congelado;
- comandos canônicos, wrappers e release checker.

## Comandos executados

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Evidências observáveis da V79

- a baseline agora materializa uma camada shadow de switching econômico legado desacoplada do fluxo principal;
- o diagnóstico de switching shadow imprime resumo de lotes avaliados, bloqueios, melhores oportunidades e plano shadow recomendado;
- o repositório continua executável e o release checker continua aprovando o pacote final em estado limpo.

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v76.xlsx`


## Validação adicional da V79

- diagnóstico `inspecionar_resolver_hibrido_5p_shadow.py` executado com sucesso;
- `aplicacao/console/principal.py` executado com sucesso;
- `scripts/operacional/gerar_planilha_operacional.py` executado com sucesso;
- `release checker` executado com sucesso em estado limpo final.


## Validação adicional da V79

- diagnóstico `inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py` executado com sucesso;
- auditoria comparativa gerando `.xlsx` e `.csv` em `saidas/operacional`;
- release checker final aprovado em estado limpo.


## Validação adicional V79

- `python scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
