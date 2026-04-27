# GATE ECONÔMICO DOS APORTES PLANEJADOS — V220

Status: `V220_CANDIDATA_DIAGNOSTICA_NAO_PROMOVIDA`.

A V220 bloqueia aportes planejados quando o cenário com aporte reduz patrimônio terminal proxy, aumenta perda terminal total, aumenta penalidade estratégica total ou aumenta déficit total em relação ao cenário sem aporte.

Comando reprodutível:

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
```
