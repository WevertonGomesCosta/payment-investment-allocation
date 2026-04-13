
from __future__ import annotations

from pathlib import Path
import sys
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.exportacao_workbook_operacional_principal import build_operational_workbook

import pandas as pd
import numpy as np

BRASILIA_TZ = ZoneInfo("America/Sao_Paulo")


def _fmt_money(x: float) -> str:
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _business_days(start_date, end_date) -> int:
    if pd.isna(start_date):
        return 0
    s = pd.Timestamp(start_date).date()
    e = pd.Timestamp(end_date).date()
    if e < s:
        return 0
    return int(np.busday_count(s, e) + np.is_busday(s))


def _print_console_summary(
    raw_path: Path,
    reference_path: Path,
    switchings_path: Path,
    resgates_path: Path,
    timeline_path: Path,
    output_workbook: Path,
) -> None:
    ref_date = datetime.now(BRASILIA_TZ).date()

    gastos_raw = pd.read_excel(raw_path, sheet_name="Todos os Gastos", usecols=[0, 1, 2, 3, 4, 5])
    gastos_raw.columns = ["Data", "Descricao", "Valor", "Pago", "Lote_usado_1", "Lote_usado_2"]
    gastos_raw["Pago"] = gastos_raw["Pago"].fillna("").astype(str).str.strip().str.upper()

    lotes_raw = pd.read_excel(raw_path, sheet_name="Inventário de Lotes")
    lotes_raw.columns = ["Lote ID", "Data Aplicacao", "Valor Original", "Investimento"]

    situacao = pd.read_excel(reference_path, sheet_name="Situacao Atual")
    switchings = pd.read_csv(switchings_path)
    resgates = pd.read_csv(resgates_path)
    timeline = pd.read_csv(timeline_path)

    gastos_hist = gastos_raw[gastos_raw["Pago"].eq("OK")].copy()
    gastos_fut = gastos_raw[~gastos_raw["Pago"].eq("OK")].copy()

    switchings["data_switching"] = pd.to_datetime(switchings["data_switching"])
    riqueza_base = float(switchings["riqueza_terminal_base_centavos"].iloc[0] / 100) if len(switchings) else 10136.69
    riqueza_oficial = float(switchings["riqueza_terminal_switch_centavos"].max() / 100) if len(switchings) else riqueza_base
    ganho_total = round(float(switchings["ganho_vs_base_centavos"].sum() / 100), 2) if len(switchings) else 0.0

    timeline["data"] = pd.to_datetime(timeline["data"])
    crit = timeline[timeline["deficit_sem_acao_centavos"] > 0].copy() if "deficit_sem_acao_centavos" in timeline.columns else pd.DataFrame()
    primeira_data_critica = crit["data"].min().strftime("%d/%m/%Y") if len(crit) else "-"
    ultima_data_critica = crit["data"].max().strftime("%d/%m/%Y") if len(crit) else "-"

    lote_to_carteira = lotes_raw.set_index("Lote ID")["Investimento"].to_dict()

    lotes_console = lotes_raw.copy()
    lotes_console = lotes_console.merge(
        situacao[[
            "Lote ID", "Saldo Bruto Atual (R$)", "Saldo Líquido Atual (R$)",
            "Total Bruto Sacado (R$)", "Total Líquido Sacado (R$)",
            "Vezes Usado (Futuro)", "Esgotado no Passado"
        ]],
        on="Lote ID",
        how="left",
    )
    lotes_console["Data Aplicacao"] = pd.to_datetime(lotes_console["Data Aplicacao"], errors="coerce")
    lotes_console["Dias Corridos"] = lotes_console["Data Aplicacao"].apply(lambda d: max(0, (ref_date - d.date()).days) if pd.notna(d) else None)
    lotes_console["Dias Uteis"] = lotes_console["Data Aplicacao"].apply(lambda d: _business_days(d, ref_date) if pd.notna(d) else None)
    lotes_console["Carteira"] = lotes_console["Lote ID"].map(lote_to_carteira)
    lotes_console["Status"] = lotes_console["Esgotado no Passado"].map(lambda v: "ESGOTADO_NO_PASSADO" if bool(v) else "ATIVO/REMANESCENTE")
    lotes_console = lotes_console.rename(columns={
        "Lote ID": "Lote",
        "Data Aplicacao": "Data_Aplicacao",
        "Valor Original": "Valor_Original_R$",
        "Saldo Bruto Atual (R$)": "Saldo_Bruto_R$",
        "Saldo Líquido Atual (R$)": "Saldo_Liquido_R$",
        "Total Bruto Sacado (R$)": "Total_Bruto_Sacado_R$",
        "Total Líquido Sacado (R$)": "Total_Liquido_Sacado_R$",
        "Vezes Usado (Futuro)": "Vezes_Usado_Futuro",
    }).sort_values(["Status", "Data_Aplicacao", "Lote"])
    lotes_ativos = lotes_console[lotes_console["Status"] != "ESGOTADO_NO_PASSADO"].copy()
    lotes_historicos = lotes_console[lotes_console["Status"] == "ESGOTADO_NO_PASSADO"].copy()

    sw_console = pd.DataFrame()
    if len(switchings):
        sw_console = switchings.copy()
        sw_console["Carteira Origem"] = sw_console["id_lote_origem"].map(lote_to_carteira)
        sw_console["Valor_Switching_R$"] = sw_console["valor_switching_centavos"] / 100
        sw_console["Ganho_vs_Base_R$"] = sw_console["ganho_vs_base_centavos"] / 100
        sw_console = sw_console.rename(columns={
            "data_switching": "Data",
            "id_lote_origem": "Lote_Origem",
            "carteira_destino": "Carteira_Destino",
            "motivo": "Motivo",
            "tipo_switching": "Tipo",
        })[["Data", "Lote_Origem", "Carteira Origem", "Carteira_Destino", "Tipo", "Valor_Switching_R$", "Ganho_vs_Base_R$", "Motivo"]]

    sw_group = pd.DataFrame()
    if len(sw_console):
        sw_group = sw_console.groupby(["Lote_Origem", "Carteira Origem", "Carteira_Destino"], dropna=False).agg(
            Qtd_Eventos=("Data", "count"),
            Primeira_Data=("Data", "min"),
            Ultima_Data=("Data", "max"),
            Valor_Total_R=("Valor_Switching_R$", "sum"),
            Ganho_Total_R=("Ganho_vs_Base_R$", "sum"),
        ).reset_index().rename(columns={"Valor_Total_R": "Valor_Total_R$", "Ganho_Total_R": "Ganho_Total_R$"})
        dates = sw_console.groupby(["Lote_Origem", "Carteira_Destino"])["Data"].apply(
            lambda s: ", ".join(pd.to_datetime(s).dt.strftime("%d/%m/%Y"))
        ).reset_index(name="Datas_Envolvidas")
        sw_group = sw_group.merge(dates, on=["Lote_Origem", "Carteira_Destino"], how="left")
        sw_group["Motivo_Fragmentacao"] = sw_group["Qtd_Eventos"].apply(
            lambda n: "Mesmo lote/origem foi recalculado em várias datas críticas." if n > 1 else "Switching único."
        )

    print("\n" + "=" * 92)
    print("RESUMO DA EXECUÇÃO — WORKBOOK OPERACIONAL PRINCIPAL V2")
    print("=" * 92)
    print(f"Workbook gerado: {output_workbook}")
    print(f"Data de referência (Brasília): {ref_date.strftime('%d/%m/%Y')}")
    print("Fuso horário: America/Sao_Paulo")
    print(f"Pagamentos históricos: {len(gastos_hist)}")
    print(f"Pagamentos futuros: {len(gastos_fut)}")
    print(f"Datas críticas: {len(crit)}")
    print(f"Switchings oficiais: {len(switchings)}")
    print(f"Resgates oficiais: {len(resgates)}")
    print(f"Primeira data crítica: {primeira_data_critica}")
    print(f"Última data crítica: {ultima_data_critica}")
    print(f"Riqueza terminal base: {_fmt_money(riqueza_base)}")
    print(f"Riqueza terminal oficial v2: {_fmt_money(riqueza_oficial)}")
    print(f"Ganho total vs base: {_fmt_money(ganho_total)}")
    print("=" * 92)

    print("\nLOTES / RECEBIDOS ATIVOS")
    print("-" * 92)
    print(lotes_ativos.to_string(index=False))

    if len(lotes_historicos):
        print("\nLOTES / RECEBIDOS ESGOTADOS NO PASSADO")
        print("-" * 92)
        print(lotes_historicos.to_string(index=False))

    if len(sw_console):
        print("\nSWITCHINGS POR EVENTO")
        print("-" * 92)
        sw_console_print = sw_console.copy()
        sw_console_print["Data"] = pd.to_datetime(sw_console_print["Data"]).dt.strftime("%d/%m/%Y")
        print(sw_console_print.to_string(index=False))

        print("\nSWITCHINGS AGRUPADOS")
        print("-" * 92)
        sw_group_print = sw_group.copy()
        sw_group_print["Primeira_Data"] = pd.to_datetime(sw_group_print["Primeira_Data"]).dt.strftime("%d/%m/%Y")
        sw_group_print["Ultima_Data"] = pd.to_datetime(sw_group_print["Ultima_Data"]).dt.strftime("%d/%m/%Y")
        print(sw_group_print.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o workbook operacional principal da baseline v2.")
    parser.add_argument("--raw", default=str(ROOT / "examples" / "dados_financeiros.xlsx"))
    parser.add_argument("--reference", default=str(ROOT / "examples" / "resultado_economica_cliff_agrupado.xlsx"))
    parser.add_argument("--switchings", default=str(ROOT / "examples" / "full_end_to_end_confirmation_v2_switchings.csv"))
    parser.add_argument("--resgates", default=str(ROOT / "examples" / "full_end_to_end_confirmation_v2_resgates.csv"))
    parser.add_argument("--timeline", default=str(ROOT / "examples" / "full_end_to_end_confirmation_v2_timeline.csv"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "workbook_operacional_principal_v2.xlsx"))
    args = parser.parse_args()

    output_workbook = Path(args.output)
    output_workbook.parent.mkdir(parents=True, exist_ok=True)

    build_operational_workbook(
        raw_workbook_path=Path(args.raw),
        reference_workbook_path=Path(args.reference),
        official_switchings_csv=Path(args.switchings),
        official_resgates_csv=Path(args.resgates),
        official_timeline_csv=Path(args.timeline),
        output_path=output_workbook,
    )
    print(f"Workbook gerado em: {output_workbook}")
    _print_console_summary(
        raw_path=Path(args.raw),
        reference_path=Path(args.reference),
        switchings_path=Path(args.switchings),
        resgates_path=Path(args.resgates),
        timeline_path=Path(args.timeline),
        output_workbook=output_workbook,
    )


if __name__ == "__main__":
    main()
