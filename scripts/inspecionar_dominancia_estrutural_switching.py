from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from diagnostico_futuro import obter_datas_criticas_sem_resgate  # noqa: E402
from motor_switching import (  # noqa: E402
    gerar_candidatos_switching_por_data,
    listar_destinos_elegiveis_switching,
    listar_lotes_elegiveis_switching,
    obter_carteira_origem_do_lote,
    validar_contrato_switching,
)
from pipeline_fase1 import executar_pipeline_inicial  # noqa: E402


def main() -> None:
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")
    lote_id = sys.argv[2] if len(sys.argv) > 2 else "Lote 3000 mar. B"
    output_json = Path(sys.argv[3]) if len(sys.argv) > 3 else REPO_ROOT / "outputs" / "origin_dominance_inspection.json"
    output_csv = Path(sys.argv[4]) if len(sys.argv) > 4 else REPO_ROOT / "outputs" / "origin_dominance_destinos.csv"

    _, estado = executar_pipeline_inicial(REPO_ROOT / "config" / "config_minimo_v1.json", workbook_path=workbook_path)
    criticas = obter_datas_criticas_sem_resgate(estado)
    primeira_data = pd.Timestamp(criticas.iloc[0]["data"]).normalize()
    deficit = int(criticas.iloc[0]["deficit_sem_resgate_centavos"])

    lotes = listar_lotes_elegiveis_switching(estado, primeira_data)
    lote = lotes.loc[lotes["id_lote"].astype(str) == str(lote_id)].iloc[0]
    carteira_origem = obter_carteira_origem_do_lote(lote, estado)
    destinos = listar_destinos_elegiveis_switching(
        estado, lote, int(lote.get("valor_liquido_resgatavel_centavos", 0))
    )

    rows = []
    for _, destino in destinos.iterrows():
        report = validar_contrato_switching(
            lote=lote,
            carteira_origem=carteira_origem,
            carteira_destino=destino,
            data_switching=primeira_data,
            valor_transferido_centavos=int(lote.get("valor_liquido_resgatavel_centavos", 0)),
            config=estado.config,
        )
        rows.append({
            "destino": str(destino["nome_carteira"]),
            "destino_id": str(destino["id_carteira"]),
            "ok": bool(report.ok),
            "codes": [x.code for x in report.issues],
        })

    candidatos = gerar_candidatos_switching_por_data(estado, primeira_data, deficit)
    payload = {
        "data_critica_inspecionada": primeira_data.isoformat(),
        "lote_inspecionado": str(lote_id),
        "carteira_origem": str(carteira_origem["nome_carteira"]) if carteira_origem is not None else None,
        "bloquear_switch_se_origem_domina_destino": bool(estado.config.politicas_modelo.bloquear_switch_se_origem_domina_destino),
        "qtd_destinos_validos_antes_da_dominancia": int(len(destinos)),
        "qtd_destinos_bloqueados_por_dominancia_estrutural": int(sum("SW_ORIGEM_DOMINA_DESTINO_ESTRUTURALMENTE" in r["codes"] for r in rows)),
        "qtd_destinos_ainda_validos": int(sum(r["ok"] for r in rows)),
        "lote_aparece_como_candidato_valido_na_primeira_data": bool((candidatos["id_lote_origem"].astype(str) == str(lote_id)).any()) if not candidatos.empty else False,
        "amostra_destinos": rows[:15],
    }
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
