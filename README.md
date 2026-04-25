# payment-investment-allocation

**Pacote operacional atual:** V205  
**Base funcional fixa de origem:** V200  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V203 deriva da V202 e aplica apenas governança de scripts legados. Ela bloqueia/rebaixa scripts diagnósticos com saída própria, preserva seus originais em histórico e converte os diagnósticos ainda úteis para leitura de `nucleo.saida_canonica`.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V203 consolida
- mantém `nucleo/saida_canonica.py` como camada única de saída observável;
- bloqueia 49 scripts legados com saída própria;
- preserva os originais bloqueados em `scripts/historico_saida_propria_v203/`;
- converte 2 diagnósticos úteis para wrappers canônicos;
- documenta a autoridade operacional dos scripts em `relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv`;
- não altera motor, contrato, modelo matemático-estatístico-financeiro nem recebidos/aportes futuros.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md`
- `relatorios/atuais/AUDITORIA_CAMADA_SAIDA_CANONICA_V202.md`
- `relatorios/atuais/GOVERNANCA_SCRIPTS_V203.md`
- `relatorios/atuais/MAPA_GOVERNANCA_SCRIPTS_V203.csv`

## Caminho operacional vigente
Para gerar a saída operacional:

```bash
python scripts/operacional/gerar_planilha_operacional.py
```

Para auditar a release:

```bash
python scripts/diagnostico/verificar_release_baseline.py
```

## Frente metodológica ainda preservada
Os aportes/recebidos futuros ainda não aportados em carteira permanecem como problema metodológico futuro. Essa frente deve ser aberta depois da estabilização da governança de scripts.


## Governança V204

A V204 aplica limpeza final de governança sem alteração econômica: código morto do console foi removido,
scripts históricos `.py` foram bloqueados, auditorias auxiliares foram separadas de saídas oficiais e
helpers utilitários de baixo risco foram centralizados em `nucleo/utilitarios_neutros.py`.

A camada oficial de saída permanece `nucleo.saida_canonica`.


## Hotfix V205

A V205 corrige regressão de importação no console introduzida na limpeza V204. A função de auditoria detalhada de resíduos voltou a importar explicitamente `construir_tabela_iof` e `construir_faixas_ir` de `nucleo.nucleo_financeiro_minimo`. Não há alteração no motor, contrato, modelo matemático-estatístico-financeiro nem na regra de recebidos/aportes futuros.
