from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica


PACOTES = [
    "no_action",
    "switch_only",
    "pay_only",
    "switch_then_pay",
    "pay_then_switch",
]

PACOTES_SWITCHING = {
    "switch_only",
    "switch_then_pay",
    "pay_then_switch",
}

VALORES_NULOS_TEXTO = {
    "",
    "n/d",
    "nd",
    "nan",
    "none",
    "-",
    "null",
}


def _norm(v) -> str:
    return str(v or "").strip().lower()


def _serie(df: pd.DataFrame, coluna: str, default="", dtype=object) -> pd.Series:
    if coluna in df.columns:
        return df[coluna]
    return pd.Series([default] * len(df), index=df.index, dtype=dtype)


def _pacote_normalizado(v) -> str:
    p = _norm(v)
    return p if p in PACOTES else ""


def contar_fontes_lote_sugerido(valor) -> int:
    texto = str(valor or "").strip()
    if _norm(texto) in VALORES_NULOS_TEXTO:
        return 0

    partes = [
        parte.strip()
        for parte in texto.split("+")
        if _norm(parte) not in VALORES_NULOS_TEXTO
    ]
    return len(partes)


def calcular_fontes_pagamento(dia: pd.DataFrame) -> tuple[int, int, int]:
    if len(dia) == 0:
        return 0, 0, 0

    lotes = _serie(dia, "Lote sugerido", default="", dtype=object).fillna("").astype(str)
    fontes_por_pagamento = lotes.apply(contar_fontes_lote_sugerido)

    qtd_fontes_pagamento = int(fontes_por_pagamento.sum())
    qtd_pagamentos_multifonte = int((fontes_por_pagamento > 1).sum())
    usa_multifonte = int(qtd_pagamentos_multifonte > 0)

    return usa_multifonte, qtd_fontes_pagamento, qtd_pagamentos_multifonte


def obter_pacotes_materializados(dia: pd.DataFrame) -> list[str]:
    if len(dia) == 0:
        return []

    pacotes = (
        _serie(dia, "Pacote do dia", default="", dtype=object)
        .fillna("")
        .astype(str)
        .map(_pacote_normalizado)
    )
    pacotes_validos = sorted({p for p in pacotes if p})
    return pacotes_validos


def inferir_pacote_vencedor_observado(
    pacotes_materializados: list[str],
    pagamentos: int,
) -> str:
    if len(pacotes_materializados) == 0:
        return "no_action" if pagamentos == 0 else "indeterminado_por_saida"

    if len(pacotes_materializados) == 1:
        return pacotes_materializados[0]

    return "misto"


def motivo_infactibilidade_pacote(pacote: str, has_pay: bool, factivel: bool) -> str:
    if factivel:
        return "n/d"

    if pacote == "pay_only" and not has_pay:
        return "sem_pagamento_no_dia"

    if pacote == "no_action" and has_pay:
        return "pagamento_obrigatorio_no_dia"

    if pacote in PACOTES_SWITCHING:
        return "pacote_nao_implementado"

    return "n/d"


def main() -> int:
    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )

    saida = construir_saida_canonica(ctx)

    extrato = pd.DataFrame(saida.extrato_futuro)
    if len(extrato) == 0:
        raise SystemExit("extrato futuro vazio")

    extrato["data"] = pd.to_datetime(extrato.get("Data"), errors="coerce").dt.date
    extrato = extrato[extrato["data"].notna()].copy()

    aud_fontes = pd.DataFrame((saida.auditoria or {}).get("alocacao_fontes_auditoria", []))
    if len(aud_fontes):
        col_data = (
            aud_fontes["Data"]
            if "Data" in aud_fontes.columns
            else pd.Series([None] * len(aud_fontes), index=aud_fontes.index)
        )
        aud_fontes["data"] = pd.to_datetime(col_data, errors="coerce").dt.date

    datas = sorted(extrato["data"].unique())

    plano_shadow = getattr(
        getattr(ctx, "switching_economico_shadow", None),
        "plano_shadow",
        pd.DataFrame(),
    )
    qtd_plano_shadow = int(len(plano_shadow)) if isinstance(plano_shadow, pd.DataFrame) else 0

    ranking_carteira = getattr(ctx, "ranking_carteira", None)
    quadro_destinos = getattr(ranking_carteira, "quadro_destinos_switch", pd.DataFrame())
    destinos_ranking_elegiveis = int(len(quadro_destinos)) if isinstance(quadro_destinos, pd.DataFrame) else 0

    rows = []
    estado_id = 0

    for d in datas:
        estado_id += 1

        dia = extrato[extrato["data"].eq(d)].copy()
        ad = aud_fontes[aud_fontes["data"].eq(d)].copy() if len(aud_fontes) else pd.DataFrame()

        pagamentos = int(len(dia))
        has_pay = pagamentos > 0

        total_pag = float(
            pd.to_numeric(
                _serie(dia, "Valor", default=0.0, dtype=float),
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        cand_sw_disp = (
            int(
                _serie(ad, "evento_switching_id", default="", dtype=object)
                .fillna("")
                .astype(str)
                .str.strip()
                .ne("")
                .sum()
            )
            if len(ad)
            else 0
        )

        cand_sw_bloq = (
            int(
                _serie(ad, "motivo_descarte_fonte", default="", dtype=object)
                .fillna("")
                .astype(str)
                .str.contains("gate", case=False, na=False)
                .sum()
            )
            if len(ad)
            else 0
        )

        cand_sw_prom = 0 if qtd_plano_shadow == 0 else cand_sw_disp

        pacotes_materializados_lista = obter_pacotes_materializados(dia)
        pacotes_materializados_set = set(pacotes_materializados_lista)
        pacote_vencedor = inferir_pacote_vencedor_observado(
            pacotes_materializados=pacotes_materializados_lista,
            pagamentos=pagamentos,
        )

        usa_multifonte, qtd_fontes_pagamento, qtd_pagamentos_multifonte = calcular_fontes_pagamento(dia)

        status_ledger = str(
            _serie(dia, "Status recomendação", default="", dtype=object).iloc[0]
            if len(dia)
            else ""
        )
        motivo_ledger = str(
            _serie(dia, "Motivo bloqueio lote", default="", dtype=object).iloc[0]
            if len(dia)
            else ""
        )

        recebidos_disponiveis_inicio_dia = (
            int(
                _serie(ad, "tipo_fonte_candidata", default="", dtype=object)
                .fillna("")
                .astype(str)
                .str.contains("recebido|caixa_pre_aplicacao", case=False, regex=True)
                .sum()
            )
            if len(ad)
            else 0
        )

        lotes_ativos_inicio_dia = (
            int(
                _serie(ad, "fonte_candidata_id", default="", dtype=object)
                .fillna("")
                .astype(str)
                .str.contains("lote", case=False, na=False)
                .sum()
            )
            if len(ad)
            else 0
        )

        fontes_disponiveis_inicio_dia = (
            int(
                _serie(ad, "fonte_candidata_id", default="", dtype=object)
                .fillna("")
                .astype(str)
                .str.strip()
                .ne("")
                .sum()
            )
            if len(ad)
            else 0
        )

        for p in PACOTES:
            constru = p == "pay_only" and has_pay
            aval = constru

            fact = (p == "pay_only" and has_pay) or (p == "no_action" and not has_pay)
            mat = p in pacotes_materializados_set

            origem = "motor_nativo" if constru else "ausente_no_motor"

            motivo_aus = "n/d"
            if not constru:
                if p in PACOTES_SWITCHING:
                    motivo_aus = "pacote_nao_implementado"
                elif p == "pay_only" and not has_pay:
                    motivo_aus = "sem_pagamento_no_dia"
                elif p == "no_action" and has_pay:
                    motivo_aus = "pagamento_obrigatorio_no_dia"
                else:
                    motivo_aus = "ausente_no_motor"

            motivo_infactibilidade = motivo_infactibilidade_pacote(
                pacote=p,
                has_pay=has_pay,
                factivel=fact,
            )

            motivo_nao_construido = motivo_aus if not constru else "n/d"
            motivo_nao_avaliado = "comparador_de_pacotes_ausente" if not aval else "n/d"

            if not mat and constru:
                motivo_nao_materializado = "ledger_nao_materializa_pacote"
            elif not mat:
                motivo_nao_materializado = motivo_aus
            else:
                motivo_nao_materializado = "n/d"

            motivo_descarte = "comparador_de_pacotes_ausente" if not mat else "n/d"

            rows.append(
                {
                    "data": d.isoformat(),
                    "pacote": p,
                    "origem_registro": origem,
                    "estado_inicial_id": f"estado_{estado_id:04d}",
                    "pagamentos_do_dia": pagamentos,
                    "valor_total_pagamentos_dia": round(total_pag, 2),
                    "recebidos_disponiveis_inicio_dia": recebidos_disponiveis_inicio_dia,
                    "recebidos_ativados_no_dia": 0,
                    "lotes_ativos_inicio_dia": lotes_ativos_inicio_dia,
                    "lotes_vencidos_normalizados_no_dia": 0,
                    "lotes_exauridos_inicio_dia": 0,
                    "fontes_disponiveis_inicio_dia": fontes_disponiveis_inicio_dia,
                    "destinos_ranking_elegiveis": destinos_ranking_elegiveis,
                    "candidatos_switching_disponiveis": cand_sw_disp,
                    "candidatos_switching_bloqueados_gate": cand_sw_bloq,
                    "candidatos_switching_promoviveis": cand_sw_prom,
                    "pacote_construido_no_motor": int(constru),
                    "pacote_avaliado_no_motor": int(aval),
                    "pacote_factivel_no_estado": int(fact),
                    "pacote_materializado_no_fluxo_atual": int(mat),
                    "pacote_vencedor_observado": pacote_vencedor,
                    "pacotes_materializados_observados": " | ".join(pacotes_materializados_lista)
                    if pacotes_materializados_lista
                    else "",
                    "motivo_nao_construido": motivo_nao_construido,
                    "motivo_nao_avaliado": motivo_nao_avaliado,
                    "motivo_infactibilidade": motivo_infactibilidade,
                    "motivo_descarte": motivo_descarte,
                    "motivo_nao_materializado": motivo_nao_materializado,
                    "valor_objetivo_ou_proxy_terminal": "",
                    "delta_vs_no_action": "",
                    "delta_vs_pay_only": "",
                    "status_ledger_resultante": status_ledger,
                    "motivo_ledger_resultante": motivo_ledger,
                    "usa_multifonte": usa_multifonte,
                    "qtd_fontes_pagamento": qtd_fontes_pagamento,
                    "qtd_pagamentos_multifonte": qtd_pagamentos_multifonte,
                    "observacao_auditoria": "instrumentacao_observacional_sem_mudanca_decisoria",
                }
            )

    df = pd.DataFrame(rows)

    out = RAIZ / "saidas/diagnostico/auditoria_matriz_pacotes_motor.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    resumo = {
        "total_dias": int(df["data"].nunique()),
        "total_pacotes_conceituais": int(len(df)),
        "total_pacotes_construidos_no_motor": int(df["pacote_construido_no_motor"].sum()),
        "total_pacotes_avaliados_no_motor": int(df["pacote_avaliado_no_motor"].sum()),
        "total_switch_only_construidos": int(
            df[df["pacote"].eq("switch_only")]["pacote_construido_no_motor"].sum()
        ),
        "total_switch_then_pay_construidos": int(
            df[df["pacote"].eq("switch_then_pay")]["pacote_construido_no_motor"].sum()
        ),
        "total_pay_then_switch_construidos": int(
            df[df["pacote"].eq("pay_then_switch")]["pacote_construido_no_motor"].sum()
        ),
        "total_candidatos_switching_disponiveis": int(df["candidatos_switching_disponiveis"].sum()),
        "total_candidatos_switching_bloqueados_gate": int(df["candidatos_switching_bloqueados_gate"].sum()),
        "total_candidatos_switching_promoviveis": int(df["candidatos_switching_promoviveis"].sum()),
        "total_pacotes_switching_materializados": int(
            df[df["pacote"].isin(list(PACOTES_SWITCHING))]["pacote_materializado_no_fluxo_atual"].sum()
        ),
        "causa_principal_switching_zero": "pacote_switching_nao_implementado",
    }

    print(out)
    print(resumo)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
