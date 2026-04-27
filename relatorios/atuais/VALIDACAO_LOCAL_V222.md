# VALIDAÇÃO LOCAL — V222

## Comandos

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado esperado

O segundo comando deve usar `impacto_contas_futuras_v222_*` ou `v221_*` sem retornar erro de CSV ausente.


## Validação estática nesta geração

- usa_carregar_csvs_impacto: OK
- resolver_presente: OK
- fallback_v222_presente: OK
- fallback_v221_presente: OK
- fallback_v220_presente: OK
- fallback_v217_presente: OK
- caminho_rigido_v217_removido: OK

## Py compile

- scripts/diagnostico/auditar_gate_economico_aportes_v220.py: OK
- scripts/diagnostico/verificar_release_baseline.py: OK

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py", line 35986, in hydrate_crdt_from_proto
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py", line 747, in __call__
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py", line 150, in call
presentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/generated/interface/models.py", line 35986, in hydrate_crdt_from_proto
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/remote.py", line 747, in __call__
  File "/tmp/tmp.vJDWZqkmKn/artifact_tool_v2-2.6.11/presentation_artifact_tool/rpc/client.py", line 150, in call
presentation_artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.

```
