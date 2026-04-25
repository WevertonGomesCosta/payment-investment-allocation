# payment-investment-allocation

**Pacote operacional atual:** V208  
**Base funcional fixa de origem:** V200  
**Baseline estrutural imediatamente anterior:** V206  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V208 deriva da V206 e aplica apenas um hotfix estrutural em `nucleo/utilitarios_neutros.py`: os helpers semânticos centralizados passam a aceitar tanto `dict` quanto `pandas.Series`, preservando a execução do console e sem alterar regras econômicas.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V208 consolida
- mantém `nucleo/saida_canonica.py` como camada única de saída observável;
- preserva a V205 como baseline pós-hotfix de console;
- mantém a governança de scripts V203/V204;
- move `saidas/oficial/relatorio_operacional_v202.xlsx` para `saidas/historico/relatorios_operacionais/`;
- centraliza `_rotulo_fonte`, `_fonte_id`, `_normalizar_proxy_terminal` e `_aliquota_ir_estimada`;
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
- `relatorios/atuais/GOVERNANCA_FINAL_SCRIPTS_V204.md`
- `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md`
- `relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md`

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
Os aportes/recebidos futuros ainda não aportados em carteira permanecem como problema metodológico futuro. Essa frente deve ser aberta depois da estabilização documental/estrutural da V208.
