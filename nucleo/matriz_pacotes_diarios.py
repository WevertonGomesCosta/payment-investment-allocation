from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

PACOTES = ["no_action", "switch_only", "pay_only", "switch_then_pay", "pay_then_switch"]
PACOTES_SWITCHING = {"switch_only", "switch_then_pay", "pay_then_switch"}
VALORES_NULOS_TEXTO = {"", "n/d", "nd", "nan", "none", "-", "null"}


def _norm(v: Any) -> str:
    return str(v or "").strip().lower()


def _serie(df: pd.DataFrame, coluna: str, default="", dtype=object) -> pd.Series:
    if coluna in df.columns:
        return df[coluna]
    return pd.Series([default] * len(df), index=df.index, dtype=dtype)


def _pacote_normalizado(v: Any) -> str:
    p = _norm(v)
    return p if p in PACOTES else ""


def _contar_fontes_lote_sugerido(valor: Any) -> int:
    texto = str(valor or "").strip()
    if _norm(texto) in VALORES_NULOS_TEXTO:
        return 0
    partes = [p.strip() for p in texto.split("+") if _norm(p) not in VALORES_NULOS_TEXTO]
    return len(partes)


def _inferir_pacote_vencedor_observado(pacotes_materializados: list[str], pagamentos: int) -> str:
    if len(pacotes_materializados) == 0:
        return "no_action" if pagamentos == 0 else "indeterminado_por_saida"
    if len(pacotes_materializados) == 1:
        return pacotes_materializados[0]
    return "misto"


@dataclass
class _SnapshotDia:
    data: date
    dia: pd.DataFrame
    ad: pd.DataFrame
    estado_id: int
    destinos_ranking_elegiveis: int


def construir_matriz_pacotes_diarios(contexto, saida_canonica, modo_observacional: bool = True) -> pd.DataFrame:
    extrato = pd.DataFrame(saida_canonica.extrato_futuro)
    if len(extrato) == 0:
        raise ValueError("extrato futuro vazio")

    extrato["data"] = pd.to_datetime(extrato.get("Data"), errors="coerce").dt.date
    extrato = extrato[extrato["data"].notna()].copy()

    aud_fontes = pd.DataFrame((saida_canonica.auditoria or {}).get("alocacao_fontes_auditoria", []))
    if len(aud_fontes):
        col_data = aud_fontes["Data"] if "Data" in aud_fontes.columns else pd.Series([None] * len(aud_fontes), index=aud_fontes.index)
        aud_fontes["data"] = pd.to_datetime(col_data, errors="coerce").dt.date

    ranking_carteira = getattr(contexto, "ranking_carteira", None)
    quadro_destinos = getattr(ranking_carteira, "quadro_destinos_switch", pd.DataFrame())
    destinos_ranking_elegiveis = int(len(quadro_destinos)) if isinstance(quadro_destinos, pd.DataFrame) else 0

    snapshots = []
    for i, d in enumerate(sorted(extrato["data"].unique()), start=1):
        dia = extrato[extrato["data"].eq(d)].copy()
        ad = aud_fontes[aud_fontes["data"].eq(d)].copy() if len(aud_fontes) else pd.DataFrame()
        snapshots.append(_SnapshotDia(d, dia, ad, i, destinos_ranking_elegiveis))

    rows: list[dict[str, Any]] = []
    for s in snapshots:
        pagamentos = int(len(s.dia))
        has_pay = pagamentos > 0
        total_pag = float(pd.to_numeric(_serie(s.dia, "Valor", default=0.0, dtype=float), errors="coerce").fillna(0).sum())

        cand_sw_disp = int(_serie(s.ad, "evento_switching_id", default="", dtype=object).fillna("").astype(str).str.strip().ne("").sum()) if len(s.ad) else 0
        cand_sw_bloq = int(_serie(s.ad, "motivo_descarte_fonte", default="", dtype=object).fillna("").astype(str).str.contains("gate", case=False, na=False).sum()) if len(s.ad) else 0
        cand_sw_prom = max(cand_sw_disp - cand_sw_bloq, 0)

        pacotes_materializados = sorted({p for p in _serie(s.dia, "Pacote do dia", default="", dtype=object).fillna("").astype(str).map(_pacote_normalizado) if p})
        mat_set = set(pacotes_materializados)
        pacote_vencedor = _inferir_pacote_vencedor_observado(pacotes_materializados, pagamentos)

        lotes = _serie(s.dia, "Lote sugerido", default="", dtype=object).fillna("").astype(str)
        fontes_por_pagamento = lotes.apply(_contar_fontes_lote_sugerido)
        qtd_fontes_pagamento = int(fontes_por_pagamento.sum())
        qtd_pagamentos_multifonte = int((fontes_por_pagamento > 1).sum())
        usa_multifonte = int(qtd_pagamentos_multifonte > 0)

        status_ledger = str(_serie(s.dia, "Status recomendação", default="", dtype=object).iloc[0] if len(s.dia) else "")
        motivo_ledger = str(_serie(s.dia, "Motivo bloqueio lote", default="", dtype=object).iloc[0] if len(s.dia) else "")

        recebidos_disponiveis_inicio_dia = int(_serie(s.ad, "tipo_fonte_candidata", default="", dtype=object).fillna("").astype(str).str.contains("recebido|caixa_pre_aplicacao", case=False, regex=True).sum()) if len(s.ad) else 0
        lotes_ativos_inicio_dia = int(_serie(s.ad, "fonte_candidata_id", default="", dtype=object).fillna("").astype(str).str.contains("lote", case=False, na=False).sum()) if len(s.ad) else 0
        fontes_disponiveis_inicio_dia = int(_serie(s.ad, "fonte_candidata_id", default="", dtype=object).fillna("").astype(str).str.strip().ne("").sum()) if len(s.ad) else 0

        for p in PACOTES:
            exige_pay = p in {"pay_only", "switch_then_pay", "pay_then_switch"}
            exige_sem_pay = p in {"no_action", "switch_only"}
            gate_temporal = (has_pay and exige_pay) or ((not has_pay) and exige_sem_pay)

            motivo_nao_construido = "n/d"
            constru = gate_temporal
            if not constru:
                motivo_nao_construido = "sem_pagamento_no_dia" if exige_pay else "pagamento_obrigatorio_no_dia"

            aval = int(constru and modo_observacional)
            motivo_nao_avaliado = "n/d" if aval else "comparador_de_pacotes_ainda_nao_decisorio"

            if p in PACOTES_SWITCHING:
                if not gate_temporal:
                    fact = 0
                    motivo_infact = "sem_pagamento_no_dia" if exige_pay else "pagamento_obrigatorio_no_dia"
                elif cand_sw_disp == 0:
                    fact = 0; motivo_infact = "sem_candidato_switching"
                elif cand_sw_bloq > 0 and cand_sw_prom == 0:
                    fact = 0; motivo_infact = "bloqueado_por_gate"
                else:
                    fact = 1; motivo_infact = "n/d"
            else:
                fact = int(gate_temporal)
                motivo_infact = "n/d" if fact else ("sem_pagamento_no_dia" if exige_pay else "pagamento_obrigatorio_no_dia")

            mat = int(p in mat_set)
            if mat:
                motivo_nao_mat = "n/d"
            elif p in PACOTES_SWITCHING and gate_temporal:
                if cand_sw_disp == 0:
                    motivo_nao_mat = "sem_candidato_switching"
                elif cand_sw_bloq > 0 and cand_sw_prom == 0:
                    motivo_nao_mat = "bloqueado_por_gate"
                else:
                    motivo_nao_mat = "candidato_switching_promovivel_nao_materializado"
            else:
                motivo_nao_mat = "pacote_nao_materializado_por_restricao_da_etapa"

            rows.append({
                "data": s.data.isoformat(), "pacote": p, "origem_registro": "motor_nativo_dry_run" if constru else "fora_janela_do_dia",
                "estado_inicial_id": f"estado_{s.estado_id:04d}", "pagamentos_do_dia": pagamentos,
                "valor_total_pagamentos_dia": round(total_pag, 2), "recebidos_disponiveis_inicio_dia": recebidos_disponiveis_inicio_dia,
                "recebidos_ativados_no_dia": 0, "lotes_ativos_inicio_dia": lotes_ativos_inicio_dia,
                "lotes_vencidos_normalizados_no_dia": 0, "lotes_exauridos_inicio_dia": 0, "fontes_disponiveis_inicio_dia": fontes_disponiveis_inicio_dia,
                "destinos_ranking_elegiveis": s.destinos_ranking_elegiveis, "candidatos_switching_disponiveis": cand_sw_disp,
                "candidatos_switching_bloqueados_gate": cand_sw_bloq, "candidatos_switching_promoviveis": cand_sw_prom,
                "pacote_construido_no_motor": int(constru), "pacote_avaliado_no_motor": int(aval), "pacote_factivel_no_estado": int(fact),
                "pacote_materializado_no_fluxo_atual": mat, "pacote_vencedor_observado": pacote_vencedor,
                "pacotes_materializados_observados": " | ".join(pacotes_materializados) if pacotes_materializados else "",
                "motivo_nao_construido": motivo_nao_construido, "motivo_nao_avaliado": motivo_nao_avaliado,
                "motivo_infactibilidade": motivo_infact, "motivo_descarte": "comparador_de_pacotes_ainda_nao_decisorio" if not mat else "n/d",
                "motivo_nao_materializado": motivo_nao_mat, "valor_objetivo_ou_proxy_terminal": "", "delta_vs_no_action": "", "delta_vs_pay_only": "",
                "status_ledger_resultante": status_ledger, "motivo_ledger_resultante": motivo_ledger,
                "usa_multifonte": usa_multifonte, "qtd_fontes_pagamento": qtd_fontes_pagamento, "qtd_pagamentos_multifonte": qtd_pagamentos_multifonte,
                "observacao_auditoria": "construido_dry_run_nao_decisorio" if constru else "n/d", "pacote_candidato_nao_decisorio": int(constru),
                "dry_run_sem_materializacao": int(p in PACOTES_SWITCHING),
            })

    return pd.DataFrame(rows)
