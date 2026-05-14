from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

DADOS = RAIZ / "dados/dados_financeiros.xlsx"
CSV_DETALHE = RAIZ / "saidas/diagnostico/auditoria_reflexo_pos_switching_situacao_atual_v17_f0_q4.csv"
CSV_RESUMO = RAIZ / "saidas/diagnostico/auditoria_reflexo_pos_switching_situacao_atual_v17_f0_q4_resumo.csv"

LOTES_ALVO = [
    {"lote_alvo": "Lote 190 mai", "data_pagamento": "2026-05-13", "conta": "Aluguel", "valor_pagamento": 192.89},
    {"lote_alvo": "Lote 3120 mai", "data_pagamento": "2026-05-13", "conta": "Pelada", "valor_pagamento": 24.00},
]


def _hash_arquivo(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _n(v: Any) -> str:
    t = str(v or "").lower().replace(".", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _num(v: Any) -> float | None:
    if v is None:
        return None
    s = str(v).strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _iter_rows(nome: str, obj: Any) -> list[dict[str, Any]]:
    try:
        if isinstance(obj, pd.DataFrame):
            return [dict(x) for x in obj.head(2000).to_dict(orient="records")]
        if isinstance(obj, list):
            out = []
            for x in obj[:2000]:
                if isinstance(x, dict):
                    out.append(dict(x))
                else:
                    out.append({"_valor": x})
            return out
        if isinstance(obj, tuple):
            return _iter_rows(nome, list(obj))
    except Exception:
        return []
    return []


def _row_has_lote(row: dict[str, Any], lote_norm: str) -> bool:
    for v in row.values():
        if isinstance(v, str) and _n(v) == lote_norm:
            return True
        if isinstance(v, str):
            toks = [_n(p) for p in str(v).split("+") if _n(p)]
            if lote_norm in toks:
                return True
    return False


def _extract_metric(rows: list[dict[str, Any]], lote_norm: str, keys: list[str]) -> Any:
    for row in rows:
        if not _row_has_lote(row, lote_norm):
            continue
        for k in keys:
            for rk, rv in row.items():
                if _n(rk) == _n(k):
                    return rv
    return None


def _classificar(presente_passado: bool, pres_ativos: bool, pres_exauridos: bool, pres_sit: bool, saldo_rem: float | None, valor_pg: float) -> tuple[str, str, str]:
    if not presente_passado:
        return (
            "pagamento_nao_localizado_extrato_passado",
            "pagamento esperado nao encontrado no extrato passado",
            "validar cadeia Q.2/Q.3 antes de concluir reflexo",
        )
    if pres_exauridos or (saldo_rem is not None and abs(saldo_rem) <= 1e-9):
        return (
            "pagamento_presente_e_lote_exaurido",
            "lote aparece exaurido ou com saldo remanescente zero",
            "sem acao corretiva no motor (diagnostico ok)",
        )
    if pres_ativos and saldo_rem is not None and saldo_rem < max(valor_pg, 0.0):
        return (
            "pagamento_presente_e_lote_ativo_com_saldo_menor",
            "lote ativo com saldo menor compativel com consumo parcial",
            "monitorar em execucoes seguintes",
        )
    if pres_ativos or pres_sit:
        return (
            "possivel_baixa_nao_refletida_situacao_atual",
            "lote ainda observavel como ativo/situacao atual sem evidencia forte de baixa",
            "investigar reflexo entre extrato passado e situacao atual",
        )
    if presente_passado and not (pres_ativos or pres_exauridos or pres_sit):
        return (
            "pagamento_presente_sem_lote_na_situacao_atual",
            "pagamento esta no extrato passado, mas lote nao apareceu nas estruturas atuais",
            "validar se lote saiu da visao atual por regra legitima de consolidacao",
        )
    return (
        "diagnostico_inconclusivo",
        "estruturas disponiveis nao permitiram fechar conclusao",
        "reexecutar com mais telemetria de saida observavel",
    )


def main() -> None:
    h0 = _hash_arquivo(DADOS)
    baseline = "79b46fa_ou_snapshot_local_validado"
    status_geral_q4 = "diagnostico_inconclusivo"

    try:
        ctx = carregar_contexto_baseline(
            raiz_repositorio=RAIZ,
            instalar_automaticamente=False,
            incluir_resolver_hibrido_5p_shadow=False,
            incluir_benchmark_agrupado_individual_shadow=False,
            incluir_benchmark_runner_futuro_shadow=False,
            incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
        )
        saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO_BASELINE)

        extrato_passado = _iter_rows("extrato_passado", getattr(saida, "extrato_passado", []))
        extrato_futuro = _iter_rows("extrato_futuro", getattr(saida, "extrato_futuro", []))
        lotes_ativos = _iter_rows("lotes_ativos", getattr(saida, "lotes_ativos", []))
        lotes_exauridos = _iter_rows("lotes_exauridos", getattr(saida, "lotes_exauridos", []))
        fechamento_atual = _iter_rows("fechamento_atual", getattr(saida, "fechamento_atual", []))
        situacao_atual = _iter_rows("situacao_atual", getattr(saida, "situacao_atual", []))
        estado_console = _iter_rows(
            "estado_pos_switching_lotes_console",
            getattr(saida, "estado_pos_switching_lotes_console", lambda **_: [])(limite=500)
            if callable(getattr(saida, "estado_pos_switching_lotes_console", None)) else [],
        )

        estruturas_genericas: dict[str, list[dict[str, Any]]] = {}
        for nm in [x for x in dir(saida) if not x.startswith("_")]:
            if nm in {
                "extrato_passado", "extrato_futuro", "lotes_ativos", "lotes_exauridos", "fechamento_atual", "situacao_atual", "estado_pos_switching_lotes_console"
            }:
                continue
            try:
                val = getattr(saida, nm)
                if callable(val):
                    continue
                rows = _iter_rows(nm, val)
                if not rows or len(rows) > 2000:
                    continue
                header = " ".join(_n(k) for k in rows[0].keys()) if rows else ""
                if any(k in header for k in ["lote", "saldo", "situacao", "status", "bruto", "liquido"]):
                    estruturas_genericas[nm] = rows
            except Exception:
                continue

        linhas = []
        for alvo in LOTES_ALVO:
            lote = alvo["lote_alvo"]
            lote_n = _n(lote)
            valor_pg = float(alvo["valor_pagamento"])

            pres_passado = any(_row_has_lote(r, lote_n) for r in extrato_passado)
            pres_futuro = any(_row_has_lote(r, lote_n) for r in extrato_futuro)
            pres_ativos = any(_row_has_lote(r, lote_n) for r in lotes_ativos)
            pres_exauridos = any(_row_has_lote(r, lote_n) for r in lotes_exauridos)
            pres_sit = any(_row_has_lote(r, lote_n) for r in situacao_atual)
            pres_fech = any(_row_has_lote(r, lote_n) for r in fechamento_atual)
            pres_estado = any(_row_has_lote(r, lote_n) for r in estado_console)

            estruturas_hit = []
            for nm, rows in estruturas_genericas.items():
                if any(_row_has_lote(r, lote_n) for r in rows):
                    estruturas_hit.append(nm)

            pool = extrato_passado + extrato_futuro + lotes_ativos + lotes_exauridos + situacao_atual + fechamento_atual + estado_console
            for nm in estruturas_hit:
                pool += estruturas_genericas.get(nm, [])

            saldo_orig = _extract_metric(pool, lote_n, ["valor aplicado", "valor original", "saldo original", "aplicado", "valor"])
            bruto = _extract_metric(pool, lote_n, ["bruto atual", "bruto", "saldo bruto"])
            liquido = _extract_metric(pool, lote_n, ["liquido atual", "liquido", "saldo liquido"])
            saldo_rem = _extract_metric(pool, lote_n, ["saldo remanescente", "remanescente", "saldo", "saldo depois", "saldo_final"])
            status_ciclo = _extract_metric(pool, lote_n, ["status", "situacao", "status ciclo", "ciclo"])
            saldo_rem_num = _num(saldo_rem)

            cls, evid, rec = _classificar(pres_passado, pres_ativos, pres_exauridos, pres_sit, saldo_rem_num, valor_pg)
            estruturas_obs = [
                "extrato_passado" if pres_passado else None,
                "extrato_futuro" if pres_futuro else None,
                "lotes_ativos" if pres_ativos else None,
                "lotes_exauridos" if pres_exauridos else None,
                "situacao_atual" if pres_sit else None,
                "fechamento_atual" if pres_fech else None,
                "estado_pos_switching_lotes_console" if pres_estado else None,
            ] + estruturas_hit
            estruturas_obs = [x for x in estruturas_obs if x]

            linhas.append(
                {
                    "lote_alvo": lote,
                    "pagamento_esperado": "sim",
                    "data_pagamento": alvo["data_pagamento"],
                    "conta": alvo["conta"],
                    "valor_pagamento": valor_pg,
                    "presente_no_extrato_passado": "sim" if pres_passado else "nao",
                    "presente_no_extrato_futuro": "sim" if pres_futuro else "nao",
                    "presente_em_lotes_ativos": "sim" if pres_ativos else "nao",
                    "presente_em_lotes_exauridos": "sim" if pres_exauridos else "nao",
                    "presente_em_situacao_atual": "sim" if pres_sit else "nao",
                    "presente_em_fechamento_atual": "sim" if pres_fech else "nao",
                    "presente_em_estado_pos_switching_console": "sim" if pres_estado else "nao",
                    "estruturas_observadas": "|".join(estruturas_obs) if estruturas_obs else "nao_disponivel",
                    "saldo_original_ou_aplicado": saldo_orig if saldo_orig is not None else "nao_disponivel",
                    "bruto_atual": bruto if bruto is not None else "nao_disponivel",
                    "liquido_atual": liquido if liquido is not None else "nao_disponivel",
                    "saldo_remanescente_observado": saldo_rem if saldo_rem is not None else "nao_disponivel",
                    "status_ciclo_observado": status_ciclo if status_ciclo is not None else "nao_disponivel",
                    "classificacao_q4": cls,
                    "evidencia_q4": evid,
                    "recomendacao_q4": rec,
                }
            )

        df = pd.DataFrame(linhas)
        CSV_DETALHE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CSV_DETALHE, index=False)

        resumo = {
            "baseline_entrada": baseline,
            "qtd_lotes_alvo": len(LOTES_ALVO),
            "qtd_presentes_extrato_passado": int((df["presente_no_extrato_passado"] == "sim").sum()),
            "qtd_presentes_situacao_atual": int((df["presente_em_situacao_atual"] == "sim").sum()),
            "qtd_presentes_lotes_ativos": int((df["presente_em_lotes_ativos"] == "sim").sum()),
            "qtd_presentes_lotes_exauridos": int((df["presente_em_lotes_exauridos"] == "sim").sum()),
            "qtd_possivel_baixa_nao_refletida_situacao_atual": int((df["classificacao_q4"] == "possivel_baixa_nao_refletida_situacao_atual").sum()),
            "qtd_pagamento_presente_e_lote_exaurido": int((df["classificacao_q4"] == "pagamento_presente_e_lote_exaurido").sum()),
            "qtd_pagamento_presente_e_lote_ativo_com_saldo_menor": int((df["classificacao_q4"] == "pagamento_presente_e_lote_ativo_com_saldo_menor").sum()),
            "qtd_pagamento_presente_sem_lote_na_situacao_atual": int((df["classificacao_q4"] == "pagamento_presente_sem_lote_na_situacao_atual").sum()),
            "qtd_diagnostico_inconclusivo": int((df["classificacao_q4"] == "diagnostico_inconclusivo").sum()),
        }

        if resumo["qtd_possivel_baixa_nao_refletida_situacao_atual"] > 0:
            status_geral_q4 = "possivel_baixa_nao_refletida_situacao_atual"
        elif resumo["qtd_diagnostico_inconclusivo"] > 0:
            status_geral_q4 = "diagnostico_inconclusivo"
        else:
            status_geral_q4 = "sem_indicio_observavel_de_baixa_pendente"

        resumo["status_geral_q4"] = status_geral_q4

        h1 = _hash_arquivo(DADOS)
        resumo["dados_financeiros_modificado_apos_execucao"] = "sim" if h0 != h1 else "nao"
        if resumo["dados_financeiros_modificado_apos_execucao"] == "sim":
            resumo["status_geral_q4"] = "falha_diagnostico_q4"

        pd.DataFrame([resumo]).to_csv(CSV_RESUMO, index=False)

        for k, v in resumo.items():
            print(f"{k}={v}")
        print(f"csv_detalhe={CSV_DETALHE}")
        print(f"csv_resumo={CSV_RESUMO}")

    except Exception as exc:
        h1 = _hash_arquivo(DADOS)
        mod = "sim" if h0 != h1 else "nao"
        print(f"baseline_entrada={baseline}")
        print("qtd_lotes_alvo=2")
        print("status_geral_q4=falha_diagnostico_q4")
        print(f"dados_financeiros_modificado_apos_execucao={mod}")
        print(f"erro_q4={type(exc).__name__}:{exc}")
        raise


if __name__ == "__main__":
    main()
