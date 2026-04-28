# 03_relatorio_achados_numericos.md — RD-2026-04-28-02

## Resumo executivo
- **Escopo da rodada:** validação numérica complementar controlada.
- **Itens N1..N12:** 12
- **PASS:** 3
- **FAIL:** 2
- **NA:** 7
- **Classificação da rodada:** **NO_GO**

## Achados principais

### ACH-01 (crítico)
- **Controle:** N2
- **Descrição:** `python aplicacao/principal.py` falha com `ModuleNotFoundError: No module named 'scipy'`.
- **Evidência:** `evidencias/console_execucao.txt`.
- **Impacto:** impede execução do console principal e qualquer validação numérica consequente.

### ACH-02 (crítico)
- **Controle:** N3
- **Descrição:** `python scripts/operacional/gerar_planilha_operacional.py` falha com `ModuleNotFoundError: No module named 'scipy'`.
- **Evidência:** `evidencias/planilha_execucao.txt`.
- **Impacto:** impede geração de planilha/saída oficial para conferência numérica.

### ACH-03 (restrição de ambiente)
- **Descrição:** tentativa de `pip install scipy` falhou por bloqueio de rede/proxy (403 Forbidden).
- **Evidência:** `evidencias/pip_install_scipy.txt`.
- **Impacto:** bloqueio externo impede remediação local na própria rodada.

## Conclusão técnica
A rodada confirmou rastreabilidade documental dos comandos e preservação estrutural da camada canônica, mas **não conseguiu executar numericamente** os cenários por bloqueio crítico de dependência+ambiente.

## Proposta de microetapa seguinte
Abrir microetapa de infraestrutura para viabilizar dependência (`scipy`) em ambiente com rede/liberação apropriada; reexecutar integralmente N2–N11 sem alterar motor econômico.
