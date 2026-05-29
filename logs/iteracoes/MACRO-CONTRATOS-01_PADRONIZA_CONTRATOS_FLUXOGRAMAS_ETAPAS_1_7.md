# MACRO-CONTRATOS-01 — Padroniza contratos e fluxogramas das Etapas 1–7

## Baseline

- Baseline solicitada: `main` limpa após merge da PR #426 em `446bbab7e611ff169a2b7a4ac81643334edb4ae9`.
- Baseline operacional local: branch `main` reconstruída no workspace a partir da PR #426 disponível localmente, com `origin/main` apontado para essa baseline local antes da aplicação documental.
- Limitação do ambiente: o `git fetch origin main` não pôde ser concluído porque o acesso ao remoto retornou `CONNECT tunnel failed, response 403`; o objeto do HEAD esperado `446bbab7e611ff169a2b7a4ac81643334edb4ae9` não estava presente no clone local. A frente foi recriada em branch limpa local sem carregar alterações funcionais no diff documental.

## Branch

- Branch de trabalho local: `docs/macro-contratos-01-padroniza-contratos-fluxogramas`.

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

Foram removidas do corpo vivo referências normativas antigas e incompatíveis com a cadeia atual. O fluxograma passou a distinguir a interface formal contratual da entrada física atual e cita `nucleo/estado_temporal_inicial.py` e `construir_estado_temporal_inicial(...)`.

### Etapa 5

Contrato consolidado com entrada formal exclusiva `EstadoTemporalInicial` e saída formal exclusiva `ResultadoMotorTemporalConjunto`, declarando diretamente a montagem diária, geração/valoração de pacotes, escolha de pacote vencedor, trajetória temporal, fontes, obrigações, switchings, auditoria final e `pronto_para_etapa6`. O fluxograma cita `nucleo/motor_temporal_conjunto.py` e `construir_resultado_motor_temporal_conjunto(...)`.

### Etapa 6

Contrato ajustado para entrada formal exclusiva `ResultadoMotorTemporalConjunto`, saída formal exclusiva `LedgerTemporalCanonico` e ponte explícita para `Etapa 7 — Gates de Validação de Núcleo`. O fluxograma cita `nucleo/ledger_temporal_canonico.py` e `construir_ledger_temporal_canonico(...)`.

### Etapa 7

Contrato revisado para registrar `nucleo/gates_validacao_nucleo.py`, `validar_gates_nucleo(...)`, os dez gates mínimos, `ResultadoGatesValidacaoNucleo`, bloqueio por `aplicacao/principal.py` quando `pronto_para_etapa8=False`, não geração de console/XLSX oficiais nesse caso e proibições de consulta direta a artefatos anteriores ou fontes externas.

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

- O acesso ao remoto GitHub via `git fetch origin main` retornou `CONNECT tunnel failed, response 403`; por isso a validação do hash remoto exato `446bbab7e611ff169a2b7a4ac81643334edb4ae9` não pôde ser feita dentro deste ambiente.
- `python -B aplicacao/principal.py` não foi executado por se tratar de PR documental e para evitar efeitos operacionais desnecessários.
