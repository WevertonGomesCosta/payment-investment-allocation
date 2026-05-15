from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

CSV = RAIZ / "saidas" / "diagnostico" / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ALERTAS_EXPLICITOS = {
    "saldo_temporal_insuficiente_cumulativo",
    "sem_saldo_temporal_auditavel",
    "sem_fonte_auditavel",
    "switch_then_pay_sem_materializacao",
    "fonte_pos_switching_nao_materializada",
}
SALDO_COLS = ["Saldo Remanescente", "Rem.", "Remanescente", "Saldo pós-pagamento", "saldo_remanescente", "saldo_pos_pagamento"]


def n(v):
    return str(v or "").strip().lower()


def parse_componentes(lote):
    return [x.strip() for x in str(lote or "").split("+") if x.strip()]


def to_float(v):
    if isinstance(v, (int, float)):
        return float(v)
    s0 = str(v).strip().replace("R$", "").replace(" ", "")
    if s0 == "" or s0.lower() == "nan":
        return 0.0
    if "," in s0 and "." in s0:
        s = s0.replace(".", "").replace(",", ".")
    elif "," in s0:
        s = s0.replace(",", ".")
    else:
        s = s0
    try:
        return float(s)
    except Exception:
        return 0.0


def detectar_alerta_explicito(r):
    campos = ["problema", "motivo", "Status recomendação", "Motivo bloqueio lote", "problema_operacional", "motivo_operacional"]
    txt = " | ".join(str(r.get(c, "")) for c in campos if str(r.get(c, "")).strip())
    txt_n = n(txt)
    for a in ALERTAS_EXPLICITOS:
        if a in txt_n:
            problema = "sem_saldo_temporal_auditavel" if "sem_saldo_temporal_auditavel" in txt_n else ("sem_fonte_auditavel" if "sem_fonte_auditavel" in txt_n else "estado_terminal_operacional")
            motivo = "saldo_temporal_insuficiente_cumulativo" if "saldo_temporal_insuficiente_cumulativo" in txt_n else a
            return True, problema, motivo, txt_n
    return False, "", "", txt_n


def extrair_saldo_pos(r, saldo_disp, valor):
    for c in SALDO_COLS:
        if c in r and str(r.get(c)).strip() != "":
            if c == "Saldo Remanescente":
                origem = "extrato_futuro_saldo_remanescente"
            elif c == "Rem.":
                origem = "extrato_futuro_rem"
            else:
                origem = "saida_canonica"
            return to_float(r.get(c)), origem
    if saldo_disp or valor:
        return saldo_disp - valor, "calculado_fallback"
    return 0.0, "nao_disponivel"


def main() -> int:
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao="V225")
    extrato = pd.DataFrame(saida.extrato_futuro)
    lotes = pd.concat([pd.DataFrame(saida.lotes_ativos), pd.DataFrame(saida.lotes_exauridos)], ignore_index=True, sort=False)
    idx_lotes = {n(r.get("Lote")): r for _, r in lotes.iterrows()} if "Lote" in lotes.columns else {}

    linhas = []
    q_aprov = q_aprov_multi = q_alert = q_sem_lote = q_bloq = q_saldo_insuf = 0
    q_alert_exp = q_alert_inf = q_sem_lote_sem_alerta_exp = 0
    q_saldo_insuf_exp = q_saldo_insuf_inf = 0
    q_estado_terminal_exp = q_sem_fonte_auditavel = q_switch_then_pay_sem_materializacao = q_fonte_pos_switching_nao_materializada = 0
    q_pay_pos = q_comp_pos = q_pay_multi = q_comp_multi = 0

    for _, r in extrato.iterrows():
        lote = str(r.get("Lote sugerido") or "").strip()
        status = str(r.get("Status recomendação") or "").strip()
        valor = to_float(r.get("Valor", 0))
        comps = parse_componentes(lote)

        if len(comps) > 1:
            q_pay_multi += 1
            q_comp_multi += len(comps)

        info_comps, saldos, pats, comp_pos_count = [], [], [], 0
        for c in comps:
            lr = idx_lotes.get(n(c), {})
            st_c = str(lr.get("Status", "nao_determinado"))
            sal = to_float(lr.get("Líquido", lr.get("Liq atual", lr.get("Líq. atual", r.get("saldo_liquido_disponivel", 0)))))
            patr = to_float(lr.get("Patr. líq", lr.get("Patrimonio líquido", lr.get("Líquido", 0))))
            if "ativo_pos_switching" in n(st_c):
                comp_pos_count += 1
            info_comps.append(f"{c}:{st_c}")
            saldos.append(sal)
            pats.append(f"{c}:{patr:.2f}")

        saldo_disp = sum(saldos) if saldos else to_float(r.get("saldo_liquido_disponivel", 0))
        saldo_pos, saldo_pos_origem = extrair_saldo_pos(r, saldo_disp, valor)

        usa_pos = comp_pos_count > 0
        if usa_pos:
            q_pay_pos += 1
            q_comp_pos += comp_pos_count

        alerta_exp, problema_op, motivo_op, txt_alerta = detectar_alerta_explicito(r)
        if alerta_exp:
            q_estado_terminal_exp += 1
            if "sem_fonte_auditavel" in txt_alerta:
                q_sem_fonte_auditavel += 1
            if "switch_then_pay_sem_materializacao" in txt_alerta:
                q_switch_then_pay_sem_materializacao += 1
            if "fonte_pos_switching_nao_materializada" in txt_alerta:
                q_fonte_pos_switching_nao_materializada += 1
        alerta_inf = (not alerta_exp) and (not lote) and (n(status) != "ok")
        tipo_alerta = "explicito" if alerta_exp else ("inferido" if alerta_inf else "sem_alerta")
        alerta_operacional = "sim" if (alerta_exp or alerta_inf) else "nao"

        if not lote:
            q_sem_lote += 1
            if alerta_exp:
                q_alert += 1
                q_alert_exp += 1
                status_op, acao = "alerta_operacional_justificado", "revisar_alerta_de_saldo_temporal"
            elif alerta_inf:
                q_alert += 1
                q_alert_inf += 1
                status_op, acao = "alerta_operacional_justificado", "aguardar_definicao_de_fonte"
            else:
                q_sem_lote_sem_alerta_exp += 1
                status_op, acao = "sem_lote_sugerido", "aguardar_definicao_de_fonte"
        elif alerta_exp:
            q_alert += 1
            q_alert_exp += 1
            status_op, acao = "alerta_operacional_justificado", "revisar_alerta_de_saldo_temporal"
        elif saldo_pos < 0:
            status_op, acao = "saldo_temporal_insuficiente", "revisar_alerta_de_saldo_temporal"
        elif len(comps) > 1:
            q_aprov_multi += 1
            status_op, acao = "aprovado_multifonte", "pagar_com_fontes_componentes"
        elif len(comps) == 1:
            q_aprov += 1
            status_op, acao = "aprovado_para_pagamento", "pagar_com_lote_sugerido"
        else:
            status_op, acao = "nao_determinado", "revisar_recomendacao"

        saldo_insuf_exp = alerta_exp and ("saldo_temporal_insuficiente_cumulativo" in n(motivo_op) or "sem_saldo_temporal_auditavel" in n(problema_op))
        saldo_insuf_inf = (not alerta_exp) and (status_op == "saldo_temporal_insuficiente")
        if saldo_insuf_exp or saldo_insuf_inf:
            q_saldo_insuf += 1
            if saldo_insuf_exp:
                q_saldo_insuf_exp += 1
            if saldo_insuf_inf:
                q_saldo_insuf_inf += 1

        linhas.append({
            "data": r.get("Data", ""),
            "conta": r.get("Conta", ""),
            "valor": valor,
            "lote_recomendado": lote,
            "fontes_componentes": " + ".join(comps),
            "qtd_fontes_componentes": len(comps),
            "fonte_principal": comps[0] if comps else "",
            "fonte_reserva": " + ".join(comps[1:]) if len(comps) > 1 else "",
            "status_recomendacao_original": status,
            "status_operacional": status_op,
            "acao_recomendada": acao,
            "motivo": " | ".join(info_comps) if info_comps else ("alerta_sem_fonte" if tipo_alerta != "sem_alerta" else "sem_fonte"),
            "saldo_liquido_disponivel": round(saldo_disp, 2),
            "valor_liquido_necessario": round(valor, 2),
            "saldo_pos_pagamento": round(saldo_pos, 2),
            "saldo_pos_pagamento_origem": saldo_pos_origem,
            "patrimonio_liquido_fonte": " | ".join(pats) if pats else "nao_determinado",
            "usa_lote_pos_switching": "sim" if usa_pos else "nao",
            "qtd_componentes_pos_switching": comp_pos_count,
            "alerta_operacional": alerta_operacional,
            "tipo_alerta_operacional": tipo_alerta,
            "problema_operacional": problema_op if alerta_exp else "",
            "motivo_operacional": motivo_op if alerta_exp else "",
            "saldo_temporal_insuficiente_tipo": "explicito" if saldo_insuf_exp else ("inferido" if saldo_insuf_inf else "nao_aplicavel"),
            "estado_terminal_bloqueante": "sim" if alerta_exp else "nao",
            "fonte_aprovada_para_pagamento": "sim" if status_op in {"aprovado_para_pagamento", "aprovado_multifonte"} else ("alerta_operacional" if tipo_alerta != "sem_alerta" else "nao"),
        })

    out = pd.DataFrame(linhas)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(CSV, index=False)

    print(f"qtd_pagamentos_operacionais_avaliados={len(out)}")
    print(f"qtd_pagamentos_aprovados_para_pagamento={q_aprov}")
    print(f"qtd_pagamentos_aprovados_multifonte={q_aprov_multi}")
    print(f"qtd_pagamentos_com_alerta_operacional_justificado={q_alert}")
    print(f"qtd_pagamentos_com_alerta_operacional_explicito={q_alert_exp}")
    print(f"qtd_pagamentos_com_alerta_operacional_inferido={q_alert_inf}")
    print(f"qtd_pagamentos_sem_lote_sugerido={q_sem_lote}")
    print(f"qtd_pagamentos_sem_lote_sugerido_sem_alerta_explicito={q_sem_lote_sem_alerta_exp}")
    print(f"qtd_pagamentos_com_fonte_bloqueada={q_bloq}")
    print(f"qtd_pagamentos_com_saldo_temporal_insuficiente={q_saldo_insuf}")
    print(f"qtd_pagamentos_com_saldo_temporal_insuficiente_explicito={q_saldo_insuf_exp}")
    print(f"qtd_pagamentos_com_saldo_temporal_insuficiente_inferido={q_saldo_insuf_inf}")
    print(f"qtd_pagamentos_com_estado_terminal_bloqueante_explicito={q_estado_terminal_exp}")
    print(f"qtd_pagamentos_sem_fonte_auditavel={q_sem_fonte_auditavel}")
    print(f"qtd_pagamentos_switch_then_pay_sem_materializacao={q_switch_then_pay_sem_materializacao}")
    print(f"qtd_pagamentos_fonte_pos_switching_nao_materializada={q_fonte_pos_switching_nao_materializada}")
    print(f"qtd_pagamentos_com_lote_pos_switching_valido={q_pay_pos}")
    print(f"qtd_componentes_lote_pos_switching_validos={q_comp_pos}")
    print(f"qtd_pagamentos_multifonte={q_pay_multi}")
    print(f"qtd_componentes_multifonte_total={q_comp_multi}")
    print("qtd_lotes_sugeridos_alterados=0")
    print("qtd_status_recomendacao_alterados=0")
    print(f"qtd_linhas_csv_s7g={len(out)}")
    print(f"csv_s7g={CSV.relative_to(RAIZ)}")
    st = "tabela_operacional_pagamentos_gerada" if len(out) == len(extrato) else "falha_tabela_operacional_pagamentos"
    print(f"status_geral_s7g={st}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
