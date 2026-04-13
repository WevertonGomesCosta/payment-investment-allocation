from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from pipeline_fase1 import executar_pipeline_inicial  # noqa: E402
from motor_precificacao import calcular_dias_bonus_restantes  # noqa: E402
from motor_switching import obter_carteira_origem_do_lote  # noqa: E402


def main() -> None:
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")
    config_path = REPO_ROOT / "config" / "config_minimo_v1.json"
    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)

    rows = []
    for _, lote in estado.lotes_ativos.iterrows():
        carteira = obter_carteira_origem_do_lote(lote, estado)
        if carteira is None:
            continue
        dias_restantes = calcular_dias_bonus_restantes(lote["data_entrada_lote"], estado.data_referencia, carteira)
        if dias_restantes > 0:
            rows.append({
                "id_lote": str(lote["id_lote"]),
                "carteira_origem": str(lote.get("carteira_atual", "")),
                "dias_bonus_restantes": int(dias_restantes),
            })

    payload = {
        "data_referencia": str(estado.data_referencia.date()),
        "qtd_lotes_com_bonus_remanescente": len(rows),
        "lotes": rows,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
