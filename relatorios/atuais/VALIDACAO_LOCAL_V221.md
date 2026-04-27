# VALIDAÇÃO LOCAL — V221

## Comandos

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado esperado

O gate não deve mais retornar `CSV V217 ausente`.


## Validação estática nesta geração

- resolver_csv_impacto_presente: OK
- fallback_versao_corrente_presente: OK
- fallback_v220_presente: OK
- fallback_v217_presente: OK
- mensagem_antiga_removida: OK

## Py compile

- scripts/diagnostico/auditar_gate_economico_aportes_v220.py: OK
- scripts/diagnostico/auditar_impacto_contas_futuras_v217.py: OK
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
