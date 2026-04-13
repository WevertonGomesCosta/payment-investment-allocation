from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from diagnostico_futuro import obter_datas_criticas_sem_resgate  # noqa: E402
from motor_switching import gerar_candidatos_switching_datas_criticas, listar_lotes_elegiveis_switching  # noqa: E402
from pipeline_fase1 import executar_pipeline_inicial  # noqa: E402


def main() -> None:
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO_ROOT / "outputs" / "origin_dominance_inspection.json"

    _, estado = executar_pipeline_inicial(REPO_ROOT / "config" / "config_minimo_v1.json", workbook_path=workbook_path)
    criticas = obter_datas_criticas_sem_resgate(estado)
    candidatos = gerar_candidatos_switching_datas_criticas(estado=estado)

    primeira_data = None
    elegiveis_primeira = []
    if not criticas.empty:
        primeira_data = criticas.iloc[0]["data"]
        elegiveis_primeira = listar_lotes_elegiveis_switching(estado, primeira_data)["id_lote"].astype(str).tolist()

    payload = {
        "bloquear_switch_se_origem_domina_destino": bool(estado.config.politicas_modelo.bloquear_switch_se_origem_domina_destino),
        "spread_minimo_dominancia_estrutural": float(estado.config.politicas_modelo.spread_minimo_dominancia_estrutural),
        "janela_minima_dominancia_dias": int(estado.config.politicas_modelo.janela_minima_dominancia_dias),
        "primeira_data_critica": primeira_data.isoformat() if hasattr(primeira_data, "isoformat") else None,
        "lotes_elegiveis_primeira_data": elegiveis_primeira,
        "qtd_candidatos_total": int(len(candidatos)),
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
