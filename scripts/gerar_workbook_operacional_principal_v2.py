
from __future__ import annotations

from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.exportacao_workbook_operacional_principal import build_operational_workbook

import pandas as pd




def _fmt_money(x: float) -> str:
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _clean_df_for_console(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = pd.to_datetime(out[col]).dt.strftime("%d/%m/%Y")
    return out.fillna("-")


def _print_console_table(title: str, df: pd.DataFrame) -> None:
    print(f"\n{title}")
    print("-" * 92)
    if df.empty:
        print("(sem registros)")
        return
    print(_clean_df_for_console(df).to_string(index=False))


def _short_switch_reason(x: str) -> str:
    if not isinstance(x, str) or not x.strip():
        return "-"
    return "Melhora riqueza terminal após reavaliar datas futuras."


def _print_console_summary(
    raw_path: Path,
    reference_path: Path,
    switchings_path: Path,
    resgates_path: Path,
    timeline_path: Path,
    output_workbook: Path,
) -> None:
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

    datas_deficit = 0
    primeira_data_critica = ""
    ultima_data_critica = ""
    if "deficit_sem_acao_centavos" in timeline.columns:
        timeline["data"] = pd.to_datetime(timeline["data"])
        crit = timeline[timeline["deficit_sem_acao_centavos"] > 0].copy()
        datas_deficit = int(len(crit))
        if len(crit):
            primeira_data_critica = crit["data"].min().strftime("%d/%m/%Y")
            ultima_data_critica = crit["data"].max().strftime("%d/%m/%Y")

    lote_to_carteira = lotes_raw.set_index("Lote ID")["Investimento"].to_dict()
    lotes_console = situacao[[
        "Lote ID", "Data Aplicação", "Dias Corridos até Hoje", "Dias Úteis até Hoje",
        "Valor Planejado Original (R$)", "Saldo Bruto Atual (R$)", "Saldo Líquido Atual (R$)",
        "Total Bruto Sacado (R$)", "Total Líquido Sacado (R$)", "Vezes Usado (Futuro)", "Esgotado no Passado"
    ]].copy()
    lotes_console["Carteira"] = lotes_console["Lote ID"].map(lote_to_carteira)
    lotes_console["Status"] = lotes_console["Esgotado no Passado"].map(lambda v: "ESGOTADO_NO_PASSADO" if bool(v) else "ATIVO/REMANESCENTE")
    lotes_console = lotes_console.rename(columns={
        "Lote ID": "Lote",
        "Data Aplicação": "Data_Aplicacao",
        "Dias Corridos até Hoje": "Dias_Corridos",
        "Dias Úteis até Hoje": "Dias_Uteis",
        "Valor Planejado Original (R$)": "Valor_Original_R$",
        "Saldo Bruto Atual (R$)": "Saldo_Bruto_R$",
        "Saldo Líquido Atual (R$)": "Saldo_Liquido_R$",
        "Total Bruto Sacado (R$)": "Total_Bruto_Sacado_R$",
        "Total Líquido Sacado (R$)": "Total_Liquido_Sacado_R$",
        "Vezes Usado (Futuro)": "Vezes_Usado_Futuro",
    }).sort_values(["Data_Aplicacao", "Lote"])

    lotes_ativos = lotes_console[lotes_console["Status"].eq("ATIVO/REMANESCENTE")].copy()
    lotes_hist = lotes_console[lotes_console["Status"].eq("ESGOTADO_NO_PASSADO")].copy()

    switchings_console = pd.DataFrame()
    switchings_group = pd.DataFrame()
    if len(switchings):
        switchings_console = switchings.copy()
        switchings_console["Carteira_Origem"] = switchings_console["id_lote_origem"].map(lote_to_carteira)
        switchings_console["Valor_Switching_R$"] = switchings_console["valor_switching_centavos"] / 100
        switchings_console["Ganho_vs_Base_R$"] = switchings_console["ganho_vs_base_centavos"] / 100
        switchings_console["Motivo_Resumo"] = switchings_console["motivo"].map(_short_switch_reason)
        switchings_console = switchings_console.rename(columns={
            "data_switching": "Data",
            "id_lote_origem": "Lote_Origem",
            "carteira_destino": "Carteira_Destino",
            "tipo_switching": "Tipo",
        })

        switchings_group = switchings_console.groupby(["Lote_Origem", "Carteira_Origem", "Carteira_Destino"], dropna=False).agg(
            Qtd_Eventos=("Data", "count"),
            Primeira_Data=("Data", "min"),
            Ultima_Data=("Data", "max"),
            Valor_Total_R=("Valor_Switching_R$", "sum"),
            Ganho_Total_R=("Ganho_vs_Base_R$", "sum"),
        ).reset_index().rename(columns={"Valor_Total_R": "Valor_Total_R$", "Ganho_Total_R": "Ganho_Total_R$"})
        dates = switchings_console.groupby(["Lote_Origem", "Carteira_Destino"])["Data"].apply(
            lambda s: ", ".join(pd.to_datetime(s).dt.strftime("%d/%m/%Y"))
        ).reset_index(name="Datas_Envolvidas")
        switchings_group = switchings_group.merge(dates, on=["Lote_Origem", "Carteira_Destino"], how="left")
        switchings_group["Motivo_Fragmentacao"] = switchings_group["Qtd_Eventos"].apply(
            lambda n: "Recalculado em novas datas críticas." if n > 1 else "Switching único."
        )

    print("\n" + "=" * 92)
    print("RESUMO DA EXECUÇÃO — WORKBOOK OPERACIONAL PRINCIPAL V2")
    print("=" * 92)
    print(f"Workbook gerado: {output_workbook}")
    print("Data de referência (Brasília): 13/04/2026")
    print("Fuso horário: America/Sao_Paulo")
    print(f"Pagamentos históricos: {len(gastos_hist)}")
    print(f"Pagamentos futuros: {len(gastos_fut)}")
    print(f"Datas críticas: {datas_deficit}")
    print(f"Switchings oficiais: {len(switchings)}")
    print(f"Resgates oficiais: {len(resgates)}")
    print(f"Primeira data crítica: {primeira_data_critica or '-'}")
    print(f"Última data crítica: {ultima_data_critica or '-'}")
    print(f"Riqueza terminal base: {_fmt_money(riqueza_base)}")
    print(f"Riqueza terminal oficial v2: {_fmt_money(riqueza_oficial)}")
    print(f"Ganho total vs base: {_fmt_money(ganho_total)}")
    print("=" * 92)

    _print_console_table(
        "LOTES / RECEBIDOS ATIVOS — IDENTIFICAÇÃO",
        lotes_ativos[["Lote", "Data_Aplicacao", "Carteira", "Status", "Dias_Corridos", "Dias_Uteis"]]
    )
    _print_console_table(
        "LOTES / RECEBIDOS ATIVOS — VALORES",
        lotes_ativos[["Lote", "Valor_Original_R$", "Saldo_Bruto_R$", "Saldo_Liquido_R$", "Total_Bruto_Sacado_R$", "Total_Liquido_Sacado_R$", "Vezes_Usado_Futuro"]]
    )

    _print_console_table(
        "LOTES / RECEBIDOS ESGOTADOS — IDENTIFICAÇÃO",
        lotes_hist[["Lote", "Data_Aplicacao", "Carteira", "Status", "Dias_Corridos", "Dias_Uteis"]]
    )
    _print_console_table(
        "LOTES / RECEBIDOS ESGOTADOS — VALORES",
        lotes_hist[["Lote", "Valor_Original_R$", "Saldo_Bruto_R$", "Saldo_Liquido_R$", "Total_Bruto_Sacado_R$", "Total_Liquido_Sacado_R$", "Vezes_Usado_Futuro"]]
    )

    if not switchings_console.empty:
        _print_console_table(
            "SWITCHINGS POR EVENTO — IDENTIFICAÇÃO",
            switchings_console[["Data", "Lote_Origem", "Carteira_Origem", "Carteira_Destino", "Tipo"]]
        )
        _print_console_table(
            "SWITCHINGS POR EVENTO — VALORES E MOTIVO",
            switchings_console[["Data", "Lote_Origem", "Valor_Switching_R$", "Ganho_vs_Base_R$", "Motivo_Resumo"]]
        )
        _print_console_table(
            "SWITCHINGS AGRUPADOS — IDENTIFICAÇÃO",
            switchings_group[["Lote_Origem", "Carteira_Origem", "Carteira_Destino", "Qtd_Eventos", "Primeira_Data", "Ultima_Data"]]
        )
        _print_console_table(
            "SWITCHINGS AGRUPADOS — VALORES E FRAGMENTAÇÃO",
            switchings_group[["Lote_Origem", "Valor_Total_R$", "Ganho_Total_R$", "Datas_Envolvidas", "Motivo_Fragmentacao"]]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description='Gera o workbook operacional principal da baseline v2.')
    parser.add_argument('--raw', default=str(ROOT / 'examples' / 'dados_financeiros.xlsx'))
    parser.add_argument('--reference', default=str(ROOT / 'examples' / 'resultado_economica_cliff_agrupado.xlsx'))
    parser.add_argument('--switchings', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_switchings.csv'))
    parser.add_argument('--resgates', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_resgates.csv'))
    parser.add_argument('--timeline', default=str(ROOT / 'examples' / 'full_end_to_end_confirmation_v2_timeline.csv'))
    parser.add_argument('--output', default=str(ROOT / 'outputs' / 'workbook_operacional_principal_v2.xlsx'))
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
    print(f'Workbook gerado em: {output_workbook}')
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
