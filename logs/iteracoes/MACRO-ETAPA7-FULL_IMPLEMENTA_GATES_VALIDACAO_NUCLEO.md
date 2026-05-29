# MACRO-ETAPA7-FULL — Implementa Gates de Validação de Núcleo

## Baseline

- Repositório: `WevertonGomesCosta/payment-investment-allocation`.
- Branch de trabalho: `work`.
- HEAD inicial observado: `e87a26e900ccc17b02c6f0a62ebb3cb06ed3db7c`.
- `origin/main` local usado como referência de baseline: `e87a26e900ccc17b02c6f0a62ebb3cb06ed3db7c`.
- O ambiente não possuía remoto `origin` configurado nem branch local `main`; por isso `git checkout main`/`git fetch origin`/`git pull --ff-only origin main` não puderam ser completados neste workspace. A implementação só foi iniciada após confirmar que o HEAD limpo do workspace coincidia com o hash obrigatório e que o arquivo legado `code/03_modelos_machine_learning_arroz.R` não estava versionado.
- `git status --short` inicial: vazio.
- `git ls-files code/03_modelos_machine_learning_arroz.R`: sem retorno.

## Arquivos alterados

- `nucleo/gates_validacao_nucleo.py` — novo módulo formal da Etapa 7.
- `aplicacao/principal.py` — integração mínima para construir o resultado de gates logo após o ledger.
- `logs/iteracoes/MACRO-ETAPA7-FULL_IMPLEMENTA_GATES_VALIDACAO_NUCLEO.md` — registro desta execução.

## Estrutura criada

O módulo `nucleo/gates_validacao_nucleo.py` define as dataclasses com `slots=True`:

- `ParametrosGatesValidacaoNucleo`.
- `EvidenciaGateNucleo`.
- `BloqueioGateNucleo`.
- `AvisoGateNucleo`.
- `GateValidacaoNucleo`.
- `ResumoGatesValidacaoNucleo`.
- `ResultadoGatesValidacaoNucleo`.

Também foi criada a função pública:

```python
validar_gates_nucleo(ledger: LedgerTemporalCanonico, parametros: ParametrosGatesValidacaoNucleo | None = None) -> ResultadoGatesValidacaoNucleo
```

## Gates implementados

1. `gate_origem_exclusiva_ledger` — valida entrada formal como `LedgerTemporalCanonico`, origem formal da Etapa 7 e metadados de origem histórica da Etapa 6 materializados no ledger.
2. `gate_auditoria_ledger` — valida existência/estado de `ledger.auditoria`, preserva bloqueios e avisos materializados no ledger.
3. `gate_obrigacoes_cobertas` — valida data, identificador mínimo, valores não negativos, compatibilidade entre obrigação/cobertura e associação de fonte quando evidenciada no ledger.
4. `gate_obrigacoes_bloqueadas` — valida motivo explícito, referência temporal mínima e valor de obrigação quando disponível.
5. `gate_fontes_utilizadas` — valida identificador, data de uso, valores referenciais não negativos/coerentes e associação operacional quando evidenciada.
6. `gate_fontes_reservadas` — valida fonte, data, valor reservado não negativo, saldos antes/depois e incompatibilidade identificável com obrigação bloqueada.
7. `gate_saldos_residuais` — valida saldos referenciais por data quando disponibilizados e bloqueia inconsistências materiais negativas além da tolerância residual.
8. `gate_switchings` — valida origem/destino quando disponíveis, valor migrado não negativo, status materializado e origem/destino distintos.
9. `gate_dupla_contagem` — valida dupla contagem evidente de obrigações, fontes e eventos exclusivamente a partir do ledger.
10. `gate_bloqueios_prontidao` — consolida bloqueios impeditivos e calcula `pronto_para_etapa8`.

## Entrada exclusiva e ausência de consumo proibido

- A Etapa 7 consome exclusivamente `LedgerTemporalCanonico` como entrada formal de estado.
- `nucleo/gates_validacao_nucleo.py` importa apenas o ledger e estruturas genéricas de biblioteca padrão; não importa nem consulta artefatos das etapas anteriores.
- A validação de origem histórica da Etapa 6 é feita somente pelos metadados já materializados dentro do ledger.
- Não há consumo direto de `ResultadoMotorTemporalConjunto` pela Etapa 7.
- Não há consumo direto de `EstadoTemporalInicial` pela Etapa 7.
- Em `aplicacao/principal.py`, chamadas já existentes às etapas anteriores permanecem no pipeline para construir os artefatos anteriores; a nova função `validar_gates_nucleo(...)` recebe somente `ledger_temporal_canonico`.

## Integração no runtime

- `resultado_gates_validacao_nucleo = validar_gates_nucleo(ledger_temporal_canonico)` foi construído imediatamente após `ledger_temporal_canonico = construir_ledger_temporal_canonico(...)`.
- `carregar_contexto_e_saida()` passou a retornar 6 itens, colocando `ResultadoGatesValidacaoNucleo` logo após o ledger e antes da saída canônica.
- `main()` foi ajustada somente para desempacotar e manter o artefato interno sem renderização.
- O resultado de gates não é renderizado no console, não é exportado para XLSX e não altera a saída canônica.

## Auditoria inline

Comando executado:

```bash
python - <<'PY'
from aplicacao.principal import carregar_contexto_e_saida

ret = carregar_contexto_e_saida()
print("qtd_retornos:", len(ret))

for obj in ret:
    print(type(obj).__name__)

gates = None
for obj in ret:
    if type(obj).__name__ == "ResultadoGatesValidacaoNucleo":
        gates = obj

print("gates_encontrado:", gates is not None)
if gates is not None:
    print("ok:", gates.ok)
    print("pronto_para_etapa8:", gates.pronto_para_etapa8)
    print("origem_formal:", gates.origem_formal)
    print("qtd_gates:", gates.resumo.qtd_gates)
    print("qtd_bloqueios:", gates.resumo.qtd_bloqueios)
    print("qtd_avisos:", gates.resumo.qtd_avisos)
    print("qtd_obrigacoes_cobertas:", gates.resumo.qtd_obrigacoes_cobertas)
    print("qtd_obrigacoes_bloqueadas:", gates.resumo.qtd_obrigacoes_bloqueadas)
    print("gate_ids:", [g.gate_id for g in gates.gates])
PY
```

Resultado resumido:

- `qtd_retornos: 6`.
- Objetos retornados: `ContextoOperacionalCanonico`, `EstadoTemporalInicial`, `ResultadoMotorTemporalConjunto`, `LedgerTemporalCanonico`, `ResultadoGatesValidacaoNucleo`, `PacoteSaidaCanonica`.
- `gates_encontrado: True`.
- `ok: False`.
- `pronto_para_etapa8: False`.
- `origem_formal: LedgerTemporalCanonico`.
- `qtd_gates: 10`.
- `qtd_bloqueios: 267`.
- `qtd_avisos: 165`.
- `qtd_obrigacoes_cobertas: 2`.
- `qtd_obrigacoes_bloqueadas: 154`.
- Gates retornados: todos os 10 gates obrigatórios listados acima.

## Validações executadas

- `rg -n "ResultadoMotorTemporalConjunto|EstadoTemporalInicial|scripts/diagnostico|ContextoBaseline|ContextoSaidaCanonicaCompat" nucleo/gates_validacao_nucleo.py aplicacao/principal.py || true` — sem ocorrências literais nos arquivos alterados.
- `git diff --name-only origin/main...HEAD` — sem saída antes do commit porque as alterações ainda não estavam commitadas.
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py` — sucesso.
- `python -B aplicacao/principal.py` — sucesso, gerando a saída operacional já existente em `saidas/oficial/relatorio_operacional_v225.xlsx` sem resíduo versionado.
- `git status --short` após validações — apenas os arquivos funcionais/log ainda não commitados.

## Limitações

- O workspace não possuía remoto `origin` configurado nem branch local `main`; a referência `origin/main` local foi alinhada ao hash obrigatório apenas para permitir comparação de diff neste ambiente.
- A execução de `python -B aplicacao/principal.py` reportou falha de download da planilha por proxy e usou `fallback_local`, comportamento operacional preexistente do runtime.
- A Etapa 7 reportou bloqueios/avisos porque preserva e valida a incompletude já materializada no ledger; não tenta recomputar, corrigir ou consultar fontes externas.

## Confirmações de escopo

- Console não foi alterado.
- XLSX não foi alterado por design e não houve resíduo versionado em `saidas/`.
- Dados não foram alterados.
- Saída canônica não foi alterada.
- Scripts diagnósticos não foram criados nem alterados.
- Ledger não foi alterado.
- Motor temporal conjunto não foi alterado.
- Estado temporal inicial não foi alterado.
- Não houve renderização nova.
- Não houve execução real de pagamento ou switching.

## Correção pós-auditoria PR #426 — comentários P2

Correção aplicada sobre a PR #426 para endereçar os seis comentários P2 ainda procedentes:

1. `gate_dupla_contagem` deixou de usar deduplicação por `dict comprehension` em obrigações cobertas; agora itera com `seen set` e bloqueia duplicidade de `(obrigacao_id, data)` antes de manter a chave para comparações com obrigações bloqueadas.
2. Foi criado helper interno para finalizar gates sem evidência mínima. Quando `ParametrosGatesValidacaoNucleo.bloquear_sem_evidencia_minima=True`, ausência de evidência mínima em obrigações cobertas, obrigações bloqueadas, fontes utilizadas, fontes reservadas, saldos residuais e switchings gera bloqueio em vez de apenas `nao_aplicavel`.
3. `gate_obrigacoes_cobertas` agora compara `obrigacao.data` com datas preservadas em `referencia_original` (`data_pagamento`, `data_vencimento`, `Data`, `data`, `vencimento`) e bloqueia divergência material usando somente dados materializados no ledger.
4. `gate_fontes_reservadas` agora valida liquidez/carência quando a evidência existe no próprio item, em `referencia_original` ou em metadados do lançamento: `elegivel_na_data_pagamento=False`, `elegivel=False`, `liquido=False` e `carencia_ate_origem`/`carencia_ate` posterior à data da reserva geram bloqueio.
5. `gate_obrigacoes_cobertas` agora exige que cada `fonte_id` em `fontes_referenciadas` exista em `ledger.fontes_utilizadas` ou `ledger.fontes_reservadas` com compatibilidade mínima de data, pacote e obrigação quando esses campos estiverem disponíveis.
6. `gate_fontes_reservadas` agora acumula reservas por `(fonte_id, data)` e bloqueia sobre-reserva quando a soma reservada excede o saldo disponível antes máximo preservado no ledger além de `tolerancia_residual`.

As correções continuam consumindo exclusivamente `LedgerTemporalCanonico` como entrada formal de estado. Não houve consulta direta a `ResultadoMotorTemporalConjunto`, `EstadoTemporalInicial`, planilha, console, XLSX, dados brutos, logs externos, diagnósticos ou saída observável pela Etapa 7.

Confirmação de escopo pós-correção: console, XLSX, dados, saída canônica e scripts diagnósticos não foram alterados.
