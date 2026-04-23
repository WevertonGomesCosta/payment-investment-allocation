# Validação local V126

Validações executadas:
- `python scripts/diagnostico/consolidar_grade_diaria_switching_v126.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

Observação: a auditoria diária foi consolidada em blocos de 5 dias para a janela inicial de 30 dias, preservando a lógica diária sem reduzir a análise a poucos horizontes fixos.
