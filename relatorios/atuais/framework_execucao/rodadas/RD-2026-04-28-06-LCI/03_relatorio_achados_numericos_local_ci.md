# 03_relatorio_achados_numericos_local_ci.md — RD-2026-04-28-06-LCI

## Resumo executivo
- Escopo: validação numérica local/CI baseada em evidências fornecidas.
- Controles avaliados: N2–N11.
- PASS: 6
- NA: 4
- FAIL: 0

## Achados observacionais
### ACH-01 (observacional)
- Evidência: `evidencias/planilha_execucao.txt`
- Descrição: lote `Lote 6630,64 fev.` reportado como exaurido (`Bruto=0.00`, `Líquido=0.00`, `Saldo rem=0.00`).
- Leitura: compatível com exaustão completa de lote; sem indício de saldo material remanescente.

### ACH-02 (observacional)
- Evidência: `evidencias/console_execucao.txt`
- Descrição: seção `SITUAÇÃO ATUAL` com metadados `None` em campos de fechamento/data.
- Leitura: achado de observabilidade/apresentação; não caracteriza falha de motor econômico sem investigação adicional de origem do metadado.

## Risco e impacto
- Não há falha crítica comprovada nos logs locais fornecidos.
- Há restrição de evidência para N4/N6/N7/N8 (insuficiência de detalhe explícito), classificada como NA justificado.
