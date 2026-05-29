# MACRO-CONTRATOS-01 — Padroniza contratos e fluxogramas das Etapas 1–7

## Baseline

- Baseline solicitada: `main` limpa após merge da PR #426 em `446bbab7e611ff169a2b7a4ac81643334edb4ae9`.
- Baseline disponível no workspace: branch `work`, HEAD `664129661bddbc5dbe151472e4cdbdc93bb45c96`.
- Limitação do ambiente: não havia branch local `main` nem remoto `origin` configurado para executar `git checkout main`, `git fetch origin` e `git pull --ff-only origin main`. A execução foi iniciada apenas com `git status --short` limpo e escopo documental restrito.

## Branch

- Branch de trabalho local: `work`.

## Objetivo

Padronizar os contratos individuais e os fluxogramas das Etapas 1–7, alinhando Etapas 4–7 à cadeia funcional consolidada:

```text
Etapa 1 -> PacoteEntradaResolvida
Etapa 2 -> PacoteValidacaoPreExecucao
Etapa 3 -> PacoteDadosOperacionaisCanonicos / UniversoEconomicoCanonico
Etapa 4 -> EstadoTemporalInicial
Etapa 5 -> ResultadoMotorTemporalConjunto
Etapa 6 -> LedgerTemporalCanonico
Etapa 7 -> ResultadoGatesValidacaoNucleo
```

## Escopo documental

Alterações restritas a contratos e log de iteração:

- `relatorios/principais/contratos_individuais/README.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `logs/iteracoes/MACRO-CONTRATOS-01_PADRONIZA_CONTRATOS_FLUXOGRAMAS_ETAPAS_1_7.md`

## Contratos preservados

- `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md` preservado sem alteração.
- `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md` preservado sem alteração.
- `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md` preservado sem alteração.

## Contratos revisados

- README dos contratos individuais atualizado para listar Etapas 1–7 e registrar histórico consolidado.
- Etapa 4 reescrita para `EstadoTemporalInicial`.
- Etapa 5 consolidada para `ResultadoMotorTemporalConjunto`.
- Etapa 6 ajustada para apontar explicitamente à Etapa 7.
- Etapa 7 revisada para refletir a implementação final dos gates de validação de núcleo.

## Principais alterações por etapa

### Etapas 1–3

Preservadas como padrão documental e operacional-explicativo.

### Etapa 4

Contrato alinhado a:

```text
PacoteDadosOperacionaisCanonicos / UniversoEconomicoCanonico / auditoria de canonização operacional -> EstadoTemporalInicial -> Etapa 5
```

Foram removidas do corpo vivo referências normativas antigas e incompatíveis com a cadeia atual.

### Etapa 5

Contrato consolidado com entrada formal exclusiva `EstadoTemporalInicial` e saída formal exclusiva `ResultadoMotorTemporalConjunto`, declarando diretamente a montagem diária, geração/valoração de pacotes, escolha de pacote vencedor, trajetória temporal, fontes, obrigações, switchings, auditoria final e `pronto_para_etapa6`.

### Etapa 6

Contrato ajustado para entrada formal exclusiva `ResultadoMotorTemporalConjunto`, saída formal exclusiva `LedgerTemporalCanonico` e ponte explícita para `Etapa 7 — Gates de Validação de Núcleo`.

### Etapa 7

Contrato revisado para registrar `validar_gates_nucleo(...)`, os dez gates mínimos, `ResultadoGatesValidacaoNucleo`, bloqueio de progressão observável quando `pronto_para_etapa8=False` e proibições de consulta direta a artefatos anteriores ou fontes externas.

## Confirmação de ausência de alteração funcional

Não houve alteração funcional. Nenhum código de runtime, núcleo, console, motor econômico, ledger ou gates foi modificado nesta frente documental.

## Confirmação de escopo proibido

Não foram alterados:

- `aplicacao/*`;
- `nucleo/*`;
- `dados/*`;
- `saidas/*`;
- `scripts/diagnostico/*`;
- console;
- XLSX;
- saída canônica;
- comportamento do runtime.

## Validações executadas

- `git diff --name-only origin/main...HEAD`
- `git diff --stat origin/main...HEAD`
- `git status --short`
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py`

## Limitações

- O workspace não disponibilizava branch local `main`, remoto `origin` ou o objeto do HEAD esperado `446bbab7e611ff169a2b7a4ac81643334edb4ae9`; por isso a baseline foi registrada conforme ambiente local disponível, sem executar atualização remota.
- `python -B aplicacao/principal.py` não foi executado por se tratar de PR documental e para evitar efeitos operacionais desnecessários.
