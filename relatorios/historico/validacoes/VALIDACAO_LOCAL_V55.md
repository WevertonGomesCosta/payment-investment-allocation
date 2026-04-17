# Validação local V55

- código e contrato alinhados à regra de aquisição de dados com download primeiro e fallback depois;
- `nucleo/cache_cdi_bcb.py` atualizado para tentar fetch online antes do cache local;
- `nucleo/leitor_planilha.py` atualizado para tentar download da planilha antes do fallback local;
- contrato executável atualizado com a nova regra.

- `python aplicacao/console/principal.py` executou com a nova regra de aquisição de dados;
- `python scripts/operacional/gerar_planilha_operacional.py` gerou `saidas/operacional/relatorio_operacional_v55.xlsx`.
