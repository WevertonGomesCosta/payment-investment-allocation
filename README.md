# payment-investment-allocation

**Pacote operacional atual:** V186  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V186 é uma normalização final dos caminhos ativos de saída e do tooling diagnóstico/release. Ela **não altera** o núcleo econômico, o contrato mestre, o modelo oficial nem a estrutura diária por pacotes já congelados.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V186 consolida
- normaliza `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- rebaixa artefatos residuais de `saidas/operacional/` e da raiz de `saidas/` para histórico;
- reforça `saidas/diagnostico/` como caminho ativo de apoio, sem competir com `saidas/oficial/`;
- canoniza `scripts/diagnostico/` como caminho principal do tooling de release e inspeção;
- rebaixa scripts antigos da raiz para `scripts/historico_raiz/`;
- remove resíduos efêmeros (`__pycache__`, `.pyc`) do pacote.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

## Próxima frente após a V186
Abrir a limpeza residual final do legado histórico ainda presente em `saidas/diagnostico/` e trilhas auxiliares antigas, sem reabrir contrato, modelo ou núcleo econômico.
