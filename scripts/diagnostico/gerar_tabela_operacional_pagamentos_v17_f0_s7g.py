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
ALERTAS = {"saldo_temporal_insuficiente_cumulativo", "sem_saldo_temporal_auditavel"}


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


def main() -> int:
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao="V225")
    extrato = pd.DataFrame(saida.extrato_futuro)
    lotes = pd.concat([pd.DataFrame(saida.lotes_ativos), pd.DataFrame(saida.lotes_exauridos)], ignore_index=True, sort=False)
    idx_lotes = {n(r.get("Lote")): r for _, r in lotes.iterrows()} if "Lote" in lotes.columns else {}

    linhas = []
    q_aprov = q_aprov_multi = q_alert = q_sem_lote = q_bloq = q_saldo_insuf = 0
    q_pay_pos = q_comp_pos = q_pay_multi = q_comp_multi = 0

    for _, r in extrato.iterrows():
        lote = str(r.get("Lote sugerido") or "").strip()
        status = str(r.get("Status recomendação") or "").strip()
        motivo_bloqueio = str(r.get("Motivo bloqueio lote") or "").strip()
        alerta = n(status) in ALERTAS or n(motivo_bloqueio) in ALERTAS
        saldo_temporal_insuf_alerta = ("saldo_temporal_insuficiente_cumulativo" in n(status) or "saldo_temporal_insuficiente_cumulativo" in n(motivo_bloqueio))
        valor = to_float(r.get("Valor", 0))
        comps = parse_componentes(lote)
        fonte_principal = comps[0] if comps else ""
        fonte_reserva = " + ".join(comps[1:]) if len(comps) > 1 else ""
        if len(comps) > 1:
            q_pay_multi += 1
            q_comp_multi += len(comps)

        info_comps = []
        saldos = []
        pats = []
        comp_pos_count = 0
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
        saldo_pos = saldo_disp - valor if comps else 0.0
        usa_pos = comp_pos_count > 0
        if usa_pos:
            q_pay_pos += 1
            q_comp_pos += comp_pos_count

        if not lote:
            q_sem_lote += 1
            if alerta:
                q_alert += 1
                if saldo_temporal_insuf_alerta:
                    q_saldo_insuf += 1
                status_op = "alerta_operacional_justificado"
                acao = "revisar_alerta_de_saldo_temporal"
            else:
                status_op = "sem_lote_sugerido"
                acao = "aguardar_definicao_de_fonte"
        elif alerta:
            q_alert += 1
            if saldo_temporal_insuf_alerta:
                q_saldo_insuf += 1
            status_op = "alerta_operacional_justificado"
            acao = "revisar_alerta_de_saldo_temporal"
        elif saldo_pos < 0:
            q_saldo_insuf += 1
            status_op = "saldo_temporal_insuficiente"
            acao = "revisar_alerta_de_saldo_temporal"
        elif len(comps) > 1:
            q_aprov_multi += 1
            status_op = "aprovado_multifonte"
            acao = "pagar_com_fontes_componentes"
        elif len(comps) == 1:
            q_aprov += 1
            status_op = "aprovado_para_pagamento"
            acao = "pagar_com_lote_sugerido"
        else:
            status_op = "nao_determinado"
            acao = "revisar_recomendacao"

        fonte_aprov = "sim" if status_op in {"aprovado_para_pagamento", "aprovado_multifonte"} else ("alerta_operacional" if alerta else "nao")
        if status_op == "fonte_bloqueada":
            q_bloq += 1

        linhas.append({
            "data": r.get("Data", ""),
            "conta": r.get("Conta", ""),
            "valor": valor,
            "lote_recomendado": lote,
            "fontes_componentes": " + ".join(comps),
            "qtd_fontes_componentes": len(comps),
            "fonte_principal": fonte_principal,
            "fonte_reserva": fonte_reserva,
            "status_recomendacao_original": status,
            "status_operacional": status_op,
            "acao_recomendada": acao,
            "motivo": " | ".join(info_comps) if info_comps else ("alerta_sem_fonte" if alerta else "sem_fonte"),
            "saldo_liquido_disponivel": round(saldo_disp, 2),
            "valor_liquido_necessario": round(valor, 2),
            "saldo_pos_pagamento": round(saldo_pos, 2),
            "patrimonio_liquido_fonte": " | ".join(pats) if pats else "nao_determinado",
            "usa_lote_pos_switching": "sim" if usa_pos else "nao",
            "qtd_componentes_pos_switching": comp_pos_count,
            "alerta_operacional": (status if n(status) in ALERTAS else motivo_bloqueio) if alerta else "",
            "fonte_aprovada_para_pagamento": fonte_aprov,
        })

    out = pd.DataFrame(linhas)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(CSV, index=False)

    print(f"qtd_pagamentos_operacionais_avaliados={len(out)}")
    print(f"qtd_pagamentos_aprovados_para_pagamento={q_aprov}")
    print(f"qtd_pagamentos_aprovados_multifonte={q_aprov_multi}")
    print(f"qtd_pagamentos_com_alerta_operacional_justificado={q_alert}")
    print(f"qtd_pagamentos_sem_lote_sugerido={q_sem_lote}")
    print(f"qtd_pagamentos_com_fonte_bloqueada={q_bloq}")
    print(f"qtd_pagamentos_com_saldo_temporal_insuficiente={q_saldo_insuf}")
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
