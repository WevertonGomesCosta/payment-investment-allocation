# ME-V17-F0-V2 — Decisão sobre gate puro de validação pré-execução

## 1. Identificação

- MICROETAPA: ME-V17-F0-V2
- VERSAO_CANDIDATA: V17-F0-V.2
- TIPO: DOCUMENTAL / DECISÃO ARQUITETURAL
- CLASSE: FORMALIZA_GATE_PURO_PRE_EXECUCAO
- STATUS: DECISÃO FORMALIZADA
- BRANCH: main
- ALTERA_CODIGO: não
- ALTERA_MOTOR: não
- ALTERA_MODELO_OFICIAL: não
- ALTERA_RUNNER_FINAL: não
- ALTERA_REGRA_ECONOMICA: não
- ALTERA_RENDERIZACAO: não

---

## 2. Decisão

A Etapa 2 — Validação pré-execução — deve ser estruturada como gate puro sobre os artefatos produzidos pela Etapa 1.

A Etapa 2 não deve produzir entrada nova, baixar planilha, carregar planilha, resolver caminho, abrir workbook, resolver colunas, canonizar colunas ou transformar dados.

---

## 3. Fronteira entre etapas

### Etapa 1 — Entrada bruta e configuração

Responsável por produzir os artefatos brutos e metadados mínimos, incluindo:

- `PacoteConfig`;
- `ContextoExecucao`;
- `PacotePlanilha`;
- origem da planilha;
- status de download ou fallback;
- nomes de abas;
- quadros brutos.

Validações técnicas locais necessárias à produção desses artefatos podem permanecer na Etapa 1.

### Etapa 2 — Validação pré-execução

Responsável apenas por validar os artefatos já produzidos pela Etapa 1.

Deve retornar:

- status de validação;
- erros bloqueantes;
- avisos não bloqueantes;
- evidências de conformidade;
- decisão de avanço ou bloqueio para a Etapa 3.

### Etapa 3 — Dados operacionais e universo econômico canônico

Responsável por:

- resolver aliases;
- resolver colunas;
- canonizar colunas;
- criar dados operacionais canônicos;
- construir inventário completo de lotes;
- estruturar universo econômico canônico.

---

## 4. Decisão sobre `aplicacao/principal.py`

`aplicacao/principal.py` não pertence à Etapa 1 nem à Etapa 2.

Ele deve ser tratado como runner final externo ao macrofluxo interno.

A função `carregar_contexto_e_saida()` permanece como pendência arquitetural controlada e deve ser migrada futuramente para módulo próprio de pipeline, com destino provisório:

- `nucleo/pipeline_operacional.py`

Essa migração não será feita na V17-F0-V.2.

---

## 5. Decisão sobre implementação da V.2

A microcorreção da V17-F0-V.2 deve:

Criar:

- `nucleo/validacao_pre_execucao.py`

Alterar minimamente:

- `nucleo/contexto_baseline.py`

Não alterar:

- `aplicacao/principal.py`;
- `nucleo/dados_operacionais_canonicos.py`;
- motor;
- saída canônica;
- console;
- XLSX;
- modelo oficial;
- contrato operacional;
- README;
- dados financeiros.

---

## 6. Objetivo da futura microcorreção

Criar um gate explícito entre a Etapa 1 e a Etapa 3.

O fluxo futuro esperado é:

1. carregar configuração;
2. resolver ambiente;
3. carregar planilha bruta;
4. validar pré-execução;
5. somente se aprovado, avançar para carteira canônica e dados operacionais canônicos.

---

## 7. Critério de aprovação futuro

A V17-F0-V.2 será aprovada se:

- a execução principal continuar funcionando;
- a validação pré-execução bloquear artefatos obrigatórios ausentes;
- o gate não baixar, carregar ou transformar dados;
- `aplicacao/principal.py` permanecer inalterado;
- `nucleo/dados_operacionais_canonicos.py` permanecer inalterado;
- o macrofluxo permanecer preservado.
