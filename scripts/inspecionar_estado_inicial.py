from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from motor_precificacao import precificar_lote_investido_na_data
from pipeline_fase1 import executar_pipeline_inicial


def main() -> None:
    config_path = ROOT / "config" / "config_minimo_v1.json"
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)

    resumo = {
        "data_corte_modelo": str(estado.data_corte_modelo.date()),
        "data_referencia": str(estado.data_referencia.date()),
        "horizonte_final": str(estado.horizonte_final.date()),
        "qtd_gastos_historicos": int(len(estado.gastos_historicos)),
        "qtd_gastos_futuros": int(len(estado.gastos_futuros)),
        "qtd_lotes_historicos": int(len(estado.lotes_historicos)),
        "qtd_lotes_ativos": int(len(estado.lotes_ativos)),
        "qtd_lotes_futuros": int(len(estado.lotes_futuros)),
        "caixa_livre_centavos": int(estado.caixa_livre_centavos),
        "status_lotes": {
            str(k): int(v)
            for k, v in estado.lotes["status_lote"].value_counts(dropna=False).to_dict().items()
        },
        "carteiras_investidas_nao_encontradas": sorted(
            estado.lotes.loc[
                (estado.lotes["status_lote"] == "INVESTIDO_ATUAL")
                & (~estado.lotes["flag_carteira_encontrada"]),
                "carteira_atual",
            ].astype(str).unique().tolist()
        ),
    }

    amostras_precificacao = []
    investidos = estado.lotes[estado.lotes["status_lote"] == "INVESTIDO_ATUAL"].head(5)
    for _, lote in investidos.iterrows():
        carteira = estado.carteiras[estado.carteiras["id_carteira"] == lote["id_carteira_atual"]]
        if carteira.empty:
            continue
        resultado = precificar_lote_investido_na_data(
            lote=lote,
            carteira=carteira.iloc[0],
            data_referencia=estado.data_referencia,
            config=estado.config,
        )
        amostras_precificacao.append({
            "id_lote": resultado.id_lote,
            "valor_bruto_centavos": resultado.valor_bruto_centavos,
            "valor_liquido_centavos": resultado.valor_liquido_centavos,
            "elegivel_resgate": resultado.elegivel_resgate,
            "elegivel_switching": resultado.elegivel_switching,
        })

    payload = {
        "resumo_estado": resumo,
        "amostras_precificacao": amostras_precificacao,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
