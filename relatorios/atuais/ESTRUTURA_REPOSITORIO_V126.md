# Estrutura do repositório V126

Adições centrais:
- `scripts/diagnostico/inspecionar_grade_diaria_switching_v126.py`
- `scripts/diagnostico/consolidar_grade_diaria_switching_v126.py`
- `scripts/inspecionar_grade_diaria_switching_v126.py`
- `scripts/consolidar_grade_diaria_switching_v126.py`
- `relatorios/atuais/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V126.md`

Mudanças centrais:
- `nucleo/simulador_central_eventos_v1.py` agora suporta switching parcial por fração do lote, preservando o saldo remanescente e criando novo lote migrado.
