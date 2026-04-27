# VALIDAÇÃO LOCAL — V223

## Comandos preferenciais

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v223.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v223.py --real
python scripts/diagnostico/auditoria_final_pre_baseline_v223.py
python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado esperado

- Impacto gera CSVs `impacto_contas_futuras_v223_*`.
- Alertas do impacto têm cabeçalho mesmo quando vazios.
- Gate gera CSVs `gate_economico_aportes_v223_*`.
- Auditoria final retorna `falhas: 0`.


## Validação estática nesta geração

- script_impacto_v223_presente: OK
- script_gate_v223_presente: OK
- auditoria_final_v223_presente: OK
- colunas_alertas_impacto_presente: OK
- impacto_alertas_real_referenciado: OK
- gate_fallback_v223_presente: OK
- gate_fallbacks_antigos_preservados: OK
- regra_economica_preservada: OK
- sem_pycache: OK
- sem_pyc: OK