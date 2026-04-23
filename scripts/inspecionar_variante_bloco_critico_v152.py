from __future__ import annotations

from datetime import date
from pathlib import Path
import json

from nucleo.motor_diario_conjunto_experimental_v143 import rodar_motor_diario_conjunto_experimental_v143

DATA_INICIO = date(2026, 5, 4)
DATA_FIM = date(2026, 5, 12)
TAU = 10.0
LIMITE = 24
CAP = 5

raiz = Path(__file__).resolve().parents[1]
resultado = rodar_motor_diario_conjunto_experimental_v143(
    raiz_repositorio=raiz,
    data_inicio=DATA_INICIO,
    data_fim=DATA_FIM,
    limite_candidatos_por_data=LIMITE,
    cap_fontes_destino=CAP,
    tau_custo_operacional=TAU,
    usar_melhor_switching_bruto_no_bloco_critico=True,
    data_inicio_bloco_critico=DATA_INICIO,
    data_fim_bloco_critico=DATA_FIM,
)
print(json.dumps(resultado.get('resumo') or {}, ensure_ascii=False, indent=2))
