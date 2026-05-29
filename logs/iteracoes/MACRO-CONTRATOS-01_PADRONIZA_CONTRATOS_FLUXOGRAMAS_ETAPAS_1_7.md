# MACRO-CONTRATOS-01 — Padroniza contratos e fluxogramas das Etapas 1–7

## 1. Identificação

- **Tipo:** DOCUMENTAL / CONTRATUAL
- **Classe:** PADRONIZA_CONTRATOS_INDIVIDUAIS_E_FLUXOGRAMAS
- **Baseline de entrada:** `446bbab7e611ff169a2b7a4ac81643334edb4ae9`
- **Branch:** `docs/macro-contratos-01-padroniza-contratos-fluxogramas-v2`
- **Altera código funcional:** não
- **Altera runtime:** não
- **Altera dados/cache:** não
- **Altera console/XLSX/saída canônica:** não
- **Cria script diagnóstico:** não

## 2. Objetivo

Padronizar os contratos individuais e os fluxogramas das Etapas 1–7, preservando o padrão operacional-explicativo completo das Etapas 1–3 e alinhando as Etapas 4–7 à cadeia funcional consolidada:

```text
Etapa 1 -> PacoteEntradaResolvida
Etapa 2 -> PacoteValidacaoPreExecucao
Etapa 3 -> PacoteDadosOperacionaisCanonicos / UniversoEconomicoCanonico
Etapa 4 -> EstadoTemporalInicial
Etapa 5 -> ResultadoMotorTemporalConjunto
Etapa 6 -> LedgerTemporalCanonico
Etapa 7 -> ResultadoGatesValidacaoNucleo
```

## 3. Arquivos alterados

Foram alterados apenas arquivos documentais permitidos:

- `relatorios/principais/contratos_individuais/README.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `logs/iteracoes/MACRO-CONTRATOS-01_PADRONIZA_CONTRATOS_FLUXOGRAMAS_ETAPAS_1_7.md`

## 4. Contratos preservados

As Etapas 1–3 foram preservadas como padrão documental e operacional-explicativo. Seus fluxogramas já continham módulos, funções e blocos internos completos, servindo como referência para padronização das Etapas 4–7.

## 5. Contratos revisados

### Etapa 4 — Estado Temporal Inicial

O contrato foi reescrito para refletir a cadeia atual:

- entrada formal da Etapa 3;
- saída formal `EstadoTemporalInicial`;
- remoção de replay, ledger, saída canônica, console e XLSX como norma viva da Etapa 4;
- explicitação do módulo `nucleo/estado_temporal_inicial.py`;
- explicitação da função `construir_estado_temporal_inicial(...)`;
- fluxograma operacional-explicativo completo até a Etapa 5.

### Etapa 5 — Motor Temporal Conjunto

O contrato foi consolidado para incorporar o fechamento funcional:

- entrada formal exclusiva `EstadoTemporalInicial`;
- saída formal exclusiva `ResultadoMotorTemporalConjunto`;
- processo interno com horizonte, estrutura diária, pacotes candidatos, valoração, pacote vencedor, trajetória, obrigações, fontes, reservas, switchings e auditoria final;
- explicitação do módulo `nucleo/motor_temporal_conjunto.py`;
- explicitação da função `construir_resultado_motor_temporal_conjunto(...)`;
- fluxograma operacional-explicativo completo até a Etapa 6.

### Etapa 6 — Ledger Temporal Canônico

O contrato foi ajustado para:

- manter entrada exclusiva `ResultadoMotorTemporalConjunto`;
- manter saída exclusiva `LedgerTemporalCanonico`;
- preservar proibição de reotimização, revaloração, nova escolha de pacote/fonte, console, XLSX e saída canônica;
- apontar explicitamente para a Etapa 7;
- explicitar `nucleo/ledger_temporal_canonico.py`;
- explicitar `construir_ledger_temporal_canonico(...)` no fluxograma.

### Etapa 7 — Gates de Validação de Núcleo

O contrato foi revisado para refletir a implementação final mergeada na PR #426:

- entrada formal exclusiva `LedgerTemporalCanonico`;
- saída formal `ResultadoGatesValidacaoNucleo`;
- função pública `validar_gates_nucleo(...)`;
- dez gates mínimos;
- proibição de consumo direto de `ResultadoMotorTemporalConjunto`, `EstadoTemporalInicial`, planilha, logs e diagnósticos;
- bloqueio de progressão observável em `aplicacao/principal.py` quando `pronto_para_etapa8=False`;
- fluxograma com decisão de prontidão antes da futura Etapa 8.

## 6. Confirmação de ausência de alteração funcional

Esta macrofrente não alterou:

- `aplicacao/*`;
- `nucleo/*`;
- `dados/*`;
- `saidas/*`;
- `scripts/diagnostico/*`;
- console;
- XLSX;
- saída canônica;
- runtime;
- motor econômico;
- ledger funcional;
- gates funcionais.

A atualização de `dados/cache_bcb.json` observada durante validações operacionais anteriores foi preservada fora desta frente documental e deve ser tratada separadamente, se necessário.

## 7. Validações esperadas

Validações recomendadas para a PR documental:

```bash
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
git status --short
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
```

Não é obrigatório executar `python -B aplicacao/principal.py` nesta frente documental, para evitar efeitos operacionais desnecessários. Se executado, o runtime deve bloquear progressão observável pelos gates da Etapa 7 enquanto `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False`.

## 8. Critérios de aceite

A frente é aceitável quando:

1. o diff fica restrito aos seis arquivos documentais permitidos;
2. o README lista Etapas 1–7;
3. Etapas 1–3 permanecem preservadas;
4. Etapa 4 está alinhada a `EstadoTemporalInicial`;
5. Etapa 5 está consolidada em `ResultadoMotorTemporalConjunto`;
6. Etapa 6 aponta explicitamente para a Etapa 7;
7. Etapa 7 reflete a implementação final da PR #426;
8. os fluxogramas das Etapas 4–7 incluem módulos/funções centrais no corpo do Mermaid;
9. nenhum arquivo funcional, dado, saída, console, XLSX ou script diagnóstico é alterado.
