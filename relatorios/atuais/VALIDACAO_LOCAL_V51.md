# Validação local V51

Validações executadas nesta versão:

- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

Resultado esperado da V51:

- o dia da aplicação não entra como dia de rendimento do lote;
- o primeiro dia útil subsequente à aplicação já pode render;
- a regra passa a ficar explícita no núcleo financeiro, não apenas implícita na evolução monetária do saldo.


Validação adicional V51:
- `python scripts/gerar_auditoria_diaria_lote.py`


Validação adicional V51:
- python aplicacao/principal.py
- conferência visual das novas seções do console.
