# VALIDAÇÃO LOCAL — V224

## Comandos recomendados

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v223.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v223.py --real
python scripts/diagnostico/auditoria_final_pre_baseline_v223.py
python scripts/diagnostico/verificar_release_limpo.py
```

## Resultado esperado

O release limpo deve remover `__pycache__`/`.pyc` e então validar a V224.


## Validação estática nesta geração

- script_limpeza_presente: OK
- script_release_limpo_presente: OK
- limpeza_remove_pycache: OK
- limpeza_remove_pyc: OK
- wrapper_chama_release: OK
- sem_pycache: OK
- sem_pyc: OK