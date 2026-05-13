from __future__ import annotations
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

BASELINE_ENTRADA = "1625655"
CSV_DETALHE = RAIZ / "saidas" / "diagnostico" / "auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.csv"
CSV_RESUMO = RAIZ / "saidas" / "diagnostico" / "auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1_resumo.csv"

TIPOS_DIVERGENCIA = {
    "baixa_pos_switching_confirmada", "baixa_pos_switching_ausente_confirmada", "baixa_pos_switching_sem_evidencia_observavel",
    "baixa_pos_switching_parcial_ou_inconsistente", "pagamento_ok_pos_switching_ausente_extrato_passado",
    "baixa_passada_pos_switching_nao_refletida_situacao_atual", "saldo_pos_switching_exibido_sem_consumo",
    "extrato_futuro_sem_reflexo_da_baixa", "console_sem_reflexo_da_baixa", "origem_migrada_usada_apos_switching",
    "sem_divergencia_observada", "sem_pagamento_pos_switching_para_auditar"
}
CAMADAS = {"console", "extrato_passado", "extrato_futuro", "situacao_atual", "saida_canonica", "saida_observavel", "estado_temporal_ledger", "replay_passado", "decisao_pagamento", "nao_determinado", "sem_falha_observada"}
STATUS_GERAL = {"sem_pagamentos_pos_switching_para_auditar", "baixa_pos_switching_confirmada", "baixa_pos_switching_sem_evidencia_observavel", "baixa_pos_switching_inconsistente", "baixa_pos_switching_ausente_confirmada", "baixa_passada_pos_switching_nao_refletida", "pagamento_ok_pos_switching_ausente_extrato_passado", "origem_migrada_usada_indevidamente", "falha_diagnostico_q1"}


def _n(v: Any) -> str: return str(v or "").strip().lower()
def _num(v: Any):
    try: return float(v)
    except Exception: return None

def _d(v: Any):
    try: return pd.to_datetime(v, dayfirst=True, errors="coerce").date()
    except Exception: return None

def _contains_lote(texto: Any, lote_norm: str) -> bool:
    return lote_norm and lote_norm in _n(texto)

def _pick_status(r: dict[str, Any]) -> str:
    for k in ["Status recomendação", "status_ledger", "Status", "status"]:
        if str(r.get(k) or "").strip(): return str(r.get(k))
    return ""

def _switch_maps(switchings: list[dict[str, Any]]):
    destinos = {}
    origem_data = {}
    for s in switchings:
        origem = _n(s.get("lote_origem"))
        destino = _n(s.get("lote_destino") or s.get("lote_pos_switching"))
        data_sw = _d(s.get("data_switching"))
        if destino:
            destinos[destino] = {"origem": origem, "destino": destino, "data_switching": data_sw}
        if origem:
            origem_data[origem] = data_sw
    return destinos, origem_data


def _linhas_passado(saida) -> tuple[list[dict[str, Any]], str]:
    extrato_passado = [dict(x) for x in (getattr(saida, "extrato_passado", []) or []) if isinstance(x, dict)]
    return extrato_passado, ("saida_canonica" if extrato_passado else "nao_localizada")


def main():
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO_BASELINE)

    extrato_futuro = [dict(x) for x in (saida.extrato_futuro or []) if isinstance(x, dict)]
    extrato_passado, fonte_passados = _linhas_passado(saida)
    switchings = [dict(x) for x in (saida.switchings or []) if isinstance(x, dict)]
    lotes_pos = [dict(x) for x in (getattr(saida, "lotes_sinteticos_pos_switching_console", lambda **_: [])(limite=500) or [])]
    situacao_raw = getattr(saida, "estado_pos_switching_lotes_console", lambda **_: [])
    situacao_atual = [dict(x) for x in ((situacao_raw(limite=500) if callable(situacao_raw) else (situacao_raw or [])) or []) if isinstance(x, dict)]

    destinos, origem_data = _switch_maps(switchings)
    nomes_lotes_pos = set(destinos.keys())

    detalhe = []

    def montar_linha(base: dict[str, Any], origem_pagamento: str):
        data = _d(base.get("Data"))
        conta = str(base.get("Conta") or "")
        valor = _num(base.get("Valor"))
        lote_sugerido = str(base.get("Lote sugerido") or "")
        lote_usado = str(base.get("Lote usado") or lote_sugerido)
        partes = [_n(x.strip()) for x in lote_sugerido.split("+") if x.strip()]
        lote_pos_encontrado = next((p for p in partes if p in nomes_lotes_pos), "")
        info_sw = destinos.get(lote_pos_encontrado, {})
        origem_sw = info_sw.get("origem", "")
        data_sw = info_sw.get("data_switching")

        origem_migrada_indevida = any(origem_data.get(p) and data and data >= origem_data.get(p) for p in partes if p in origem_data)
        presente_passado = origem_pagamento == "pagamentos_passados"
        presente_futuro = origem_pagamento == "pagamentos_futuros"

        linha_sit = next((x for x in situacao_atual if _contains_lote(x.get("Lote") or x.get("lote"), lote_pos_encontrado)), {})
        bruto_sacado = _num(linha_sit.get("Bruto sac.") or linha_sit.get("bruto_sacado"))
        liquido_sacado = _num(linha_sit.get("Líq. sac.") or linha_sit.get("liq_sacado") or linha_sit.get("liquido_sacado"))
        saldo_exibido = _num(linha_sit.get("Líq. disp.") or linha_sit.get("saldo"))
        bruto_pos = _num(linha_sit.get("Bruto") or linha_sit.get("bruto"))
        liquido_pos = _num(linha_sit.get("Líquido") or linha_sit.get("liquido"))
        ativo_integral = bool((_n(linha_sit.get("status")) == "ativo_pos_switching") and (bruto_sacado in (0, None)) and (liquido_sacado in (0, None)))

        tipo = "sem_divergencia_observada"
        camada = "sem_falha_observada"
        evid = []

        fonte_eh_pos = bool(lote_pos_encontrado)
        if not fonte_eh_pos:
            tipo = "sem_pagamento_pos_switching_para_auditar"
            camada = "nao_determinado"
        else:
            if origem_migrada_indevida:
                tipo = "origem_migrada_usada_apos_switching"
                camada = "decisao_pagamento"
                evid.append("origem migrada usada apos data_switching")
            elif origem_pagamento == "pagamentos_passados" and not presente_passado:
                tipo = "pagamento_ok_pos_switching_ausente_extrato_passado"
                camada = "extrato_passado"
            elif origem_pagamento == "pagamentos_passados" and ativo_integral:
                tipo = "baixa_passada_pos_switching_nao_refletida_situacao_atual"
                camada = "situacao_atual"
                evid.append("lote ativo_pos_switching com bruto/liquido sacados zerados")
            elif origem_pagamento == "pagamentos_futuros":
                tipo = "baixa_pos_switching_sem_evidencia_observavel"
                camada = "saida_observavel"
            else:
                tipo = "baixa_pos_switching_confirmada"
                camada = "sem_falha_observada"

        if tipo not in TIPOS_DIVERGENCIA: tipo = "baixa_pos_switching_sem_evidencia_observavel"
        if camada not in CAMADAS: camada = "nao_determinado"

        return {
            "origem_pagamento": origem_pagamento,
            "fonte_pagamentos_passados": fonte_passados,
            "pagamento_id": base.get("Despesa ID") or f"{origem_pagamento}_{conta}_{base.get('Data')}",
            "data_pagamento": base.get("Data"),
            "conta": conta,
            "valor_pagamento": base.get("Valor"),
            "pagamento_ok_na_planilha": "sim" if origem_pagamento == "pagamentos_passados" else "nao",
            "presente_no_extrato_passado": "sim" if presente_passado else "nao",
            "presente_no_extrato_futuro": "sim" if presente_futuro else "nao",
            "pacote_do_dia": _n(base.get("Pacote do dia") or base.get("pacote_do_dia_ledger")),
            "status_recomendacao": _pick_status(base),
            "lote_sugerido": lote_sugerido,
            "lote_usado_planilha": lote_usado,
            "lote_pos_switching_renderizado": lote_pos_encontrado,
            "fonte_pos_switching": "sim" if fonte_eh_pos else "nao",
            "pos_sw_flag": "sim" if fonte_eh_pos else "nao",
            "origem_switching": origem_sw,
            "destino_switching": lote_pos_encontrado,
            "data_switching": data_sw,
            "lote_pos_switching_elegivel_na_data": "sim" if data_sw and data and data >= data_sw else "nao",
            "fonte_eh_lote_pos_switching": "sim" if fonte_eh_pos else "nao",
            "origem_migrada_usada_indevidamente": "sim" if origem_migrada_indevida else "nao",
            "saldo_pos_switching_exibido": saldo_exibido,
            "saldo_temporal_antes": None,
            "consumo_temporal": None,
            "saldo_temporal_depois": None,
            "saldo_remanescente_extrato": None,
            "bruto_pos": bruto_pos,
            "liquido_pos": liquido_pos,
            "bruto_sacado_situacao_atual": bruto_sacado,
            "liquido_sacado_situacao_atual": liquido_sacado,
            "baixa_refletida_situacao_atual": "sim" if (bruto_sacado not in (None, 0) or liquido_sacado not in (None, 0)) else "nao",
            "lote_pos_switching_permanece_ativo_integral": "sim" if ativo_integral else "nao",
            "valor_pagamento_abateu_saldo_pos_switching": "nao_determinado",
            "saldo_pos_switching_esperado_apos_pagamento": None,
            "divergencia_baixa_pos_switching": "sim" if tipo not in {"sem_divergencia_observada", "baixa_pos_switching_confirmada", "sem_pagamento_pos_switching_para_auditar"} else "nao",
            "tipo_divergencia_q1": tipo,
            "tipo_falha_replay_passado": "sem_evidencia_direta_ledger" if tipo in {"baixa_pos_switching_sem_evidencia_observavel", "baixa_passada_pos_switching_nao_refletida_situacao_atual"} else "n/a",
            "camada_onde_falha": camada,
            "evidencia_q1": " | ".join(evid) if evid else "sem_evidencia_direta_adicional",
            "recomendacao_q1": "V17-F0-Q.2" if tipo != "baixa_pos_switching_confirmada" else "V17-F0-S.7",
        }

    for r in extrato_futuro:
        detalhe.append(montar_linha(r, "pagamentos_futuros"))
    for r in extrato_passado:
        detalhe.append(montar_linha(r, "pagamentos_passados"))

    df = pd.DataFrame(detalhe)
    # auditoria explícita dos dois casos informados
    casos = [
        (pd.Timestamp("2026-05-13").date(), "aluguel", 192.89, "lote 190 mai"),
        (pd.Timestamp("2026-05-13").date(), "pelada", 24.00, "lote 3120 mai"),
    ]
    for dt, conta, valor, lote in casos:
        existe = ((pd.to_datetime(df["data_pagamento"], errors="coerce", dayfirst=True).dt.date == dt) & (df["conta"].astype(str).str.lower() == conta) & (pd.to_numeric(df["valor_pagamento"], errors="coerce").round(2) == round(valor, 2))).any() if not df.empty else False
        if not existe:
            detalhe.append({c: None for c in df.columns} if not df.empty else {})

    df = pd.DataFrame(detalhe)
    df_pos = df[df["fonte_eh_lote_pos_switching"] == "sim"] if not df.empty else pd.DataFrame()
    df_fut = df[df["origem_pagamento"] == "pagamentos_futuros"] if not df.empty else pd.DataFrame()
    df_pass = df[(df["origem_pagamento"] == "pagamentos_passados") & (df["pagamento_ok_na_planilha"] == "sim") & (df["fonte_eh_lote_pos_switching"] == "sim")] if not df.empty else pd.DataFrame()

    q0 = pd.read_csv(RAIZ / "saidas" / "diagnostico" / "auditar_integracao_switching_pagamentos_v17_f0_q0.csv") if (RAIZ / "saidas" / "diagnostico" / "auditar_integracao_switching_pagamentos_v17_f0_q0.csv").exists() else pd.DataFrame()
    q0r = q0[q0.get("tipo_linha", "") == "resumo"].head(1).to_dict("records") if not q0.empty else []
    q0r = q0r[0] if q0r else {}

    alinhado = (
        int(len(df_fut)) == int(q0r.get("total_pagamentos_futuros", -1)) and
        int((df_fut["fonte_eh_lote_pos_switching"] == "sim").sum()) == int(q0r.get("pagamentos_usando_lote_pos_switching", -1)) and
        int(len(lotes_pos)) == int(q0r.get("lotes_pos_switching_total", -1)) and
        int((df["origem_migrada_usada_indevidamente"] == "sim").sum()) == int(q0r.get("origens_migradas_usadas_indevidamente_total", -1))
    ) if q0r else False

    cont_tipo = df_pos["tipo_divergencia_q1"].value_counts() if not df_pos.empty else pd.Series(dtype=int)
    if len(df_pos) == 0:
        status = "sem_pagamentos_pos_switching_para_auditar"
    elif int(cont_tipo.get("origem_migrada_usada_apos_switching", 0)) > 0:
        status = "origem_migrada_usada_indevidamente"
    elif int(cont_tipo.get("pagamento_ok_pos_switching_ausente_extrato_passado", 0)) > 0:
        status = "pagamento_ok_pos_switching_ausente_extrato_passado"
    elif int(cont_tipo.get("baixa_passada_pos_switching_nao_refletida_situacao_atual", 0)) > 0:
        status = "baixa_passada_pos_switching_nao_refletida"
    elif int(cont_tipo.get("baixa_pos_switching_ausente_confirmada", 0)) > 0:
        status = "baixa_pos_switching_ausente_confirmada"
    elif int(cont_tipo.get("baixa_pos_switching_parcial_ou_inconsistente", 0)) > 0:
        status = "baixa_pos_switching_inconsistente"
    elif int(cont_tipo.get("baixa_pos_switching_sem_evidencia_observavel", 0)) > 0:
        status = "baixa_pos_switching_sem_evidencia_observavel"
    else:
        status = "baixa_pos_switching_confirmada"
    if status not in STATUS_GERAL: status = "falha_diagnostico_q1"

    diverg = int((df_pos["divergencia_baixa_pos_switching"] == "sim").sum()) if not df_pos.empty else 0
    camada_dom = (df_pos[df_pos["divergencia_baixa_pos_switching"] == "sim"]["camada_onde_falha"].value_counts().index[0] if diverg > 0 else "sem_falha_observada")

    resumo = {
        "baseline_entrada": BASELINE_ENTRADA,
        "qtd_pagamentos_futuros": int(len(df_fut)),
        "qtd_pagamentos_futuros_usando_lote_pos_switching": int((df_fut["fonte_eh_lote_pos_switching"] == "sim").sum()) if not df_fut.empty else 0,
        "fonte_pagamentos_passados": fonte_passados,
        "qtd_pagamentos_passados_ok_usando_lote_pos_switching": int(len(df_pass)),
        "qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado": int(cont_tipo.get("pagamento_ok_pos_switching_ausente_extrato_passado", 0)),
        "qtd_baixas_passadas_pos_switching_nao_refletidas_situacao_atual": int(cont_tipo.get("baixa_passada_pos_switching_nao_refletida_situacao_atual", 0)),
        "qtd_lotes_pos_switching_total": int(len(lotes_pos)),
        "qtd_lotes_pos_switching_elegiveis_em_alguma_data": int((df_fut["lote_pos_switching_elegivel_na_data"] == "sim").sum()) if not df_fut.empty else 0,
        "qtd_pagamentos_pos_switching_com_baixa_confirmada": int(cont_tipo.get("baixa_pos_switching_confirmada", 0)),
        "qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada": int(cont_tipo.get("baixa_pos_switching_ausente_confirmada", 0)),
        "qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa": int(cont_tipo.get("baixa_pos_switching_sem_evidencia_observavel", 0)),
        "qtd_pagamentos_pos_switching_com_baixa_inconsistente": int(cont_tipo.get("baixa_pos_switching_parcial_ou_inconsistente", 0)),
        "qtd_origens_migradas_usadas_indevidamente": int((df["origem_migrada_usada_indevidamente"] == "sim").sum()) if not df.empty else 0,
        "qtd_divergencias_baixa_pos_switching": diverg,
        "camada_falha_dominante": camada_dom,
        "status_geral_q1": status,
        "q1_alinhado_com_q0": "sim" if alinhado else "nao",
    }

    CSV_DETALHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_DETALHE, index=False)
    pd.DataFrame([resumo]).to_csv(CSV_RESUMO, index=False)

    print("=== AUDITORIA V17-F0-Q.1.1 — BAIXA CONTABIL LOTES POS-SWITCHING EM PAGAMENTOS PASSADOS E FUTUROS ===")
    for k in ["baseline_entrada","qtd_pagamentos_futuros","qtd_pagamentos_futuros_usando_lote_pos_switching","fonte_pagamentos_passados","qtd_pagamentos_passados_ok_usando_lote_pos_switching","qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado","qtd_baixas_passadas_pos_switching_nao_refletidas_situacao_atual","qtd_lotes_pos_switching_total","qtd_lotes_pos_switching_elegiveis_em_alguma_data","qtd_pagamentos_pos_switching_com_baixa_confirmada","qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada","qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa","qtd_pagamentos_pos_switching_com_baixa_inconsistente","qtd_origens_migradas_usadas_indevidamente","qtd_divergencias_baixa_pos_switching","camada_falha_dominante","status_geral_q1","q1_alinhado_com_q0"]:
        print(f"{k}={resumo[k]}")
    print(f"csv_detalhe={CSV_DETALHE}")
    print(f"csv_resumo={CSV_RESUMO}")

if __name__ == "__main__":
    main()
