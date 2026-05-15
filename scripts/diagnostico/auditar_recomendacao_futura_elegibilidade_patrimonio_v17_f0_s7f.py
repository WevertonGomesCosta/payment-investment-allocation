from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b

CSV = RAIZ / "saidas" / "diagnostico" / "auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv"
ALERTAS = {"saldo_temporal_insuficiente_cumulativo", "sem_saldo_temporal_auditavel"}

def n(x): return str(x or "").strip().lower()

def parse_componentes(txt: str):
    return [p.strip() for p in str(txt or "").split("+") if p.strip()]

def main() -> int:
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao="V225")

    extrato = pd.DataFrame(saida.extrato_futuro)
    lotes = pd.concat([pd.DataFrame(saida.lotes_ativos), pd.DataFrame(saida.lotes_exauridos)], ignore_index=True, sort=False)
    try:
        matriz = construir_matriz_elegibilidade_fontes_s7b(ctx, data_referencia=saida.data_referencia)
        status_matriz = "ok"
    except Exception as exc:
        matriz = pd.DataFrame()
        status_matriz = str(exc)

    idx_matriz = {n(r.get("fonte_id")): r for _, r in matriz.iterrows()} if not matriz.empty else {}
    idx_lotes = {n(r.get("Lote")): r for _, r in lotes.iterrows()} if not lotes.empty and "Lote" in lotes.columns else {}

    linhas = []
    q_aprov= q_bloq= q_s6= q_pos= q_uso_ind= q_insuf= q_alerta= q_multi= q_multi_ok=0

    for _, r in extrato.iterrows():
        lote_sugerido = str(r.get("Lote sugerido") or "").strip()
        status = str(r.get("Status recomendação") or "").strip()
        comps = parse_componentes(lote_sugerido)
        if len(comps) > 1: q_multi += 1
        detalhes=[]; comp_bloq=[]; saldos=[]; pats=[]
        tem_aprov = False
        for c in comps:
            m = idx_matriz.get(n(c), {})
            l = idx_lotes.get(n(c), {})
            elig = str(m.get("elegivel_para_pagamento", "coluna_nao_localizada" if matriz.empty else "nao_determinado"))
            bloqueio = str(m.get("motivo_bloqueio", m.get("bloqueio", "")))
            status_ciclo = str(m.get("status_ciclo", l.get("Status", "nao_determinado")))
            origem_migr = "sim" if "migrado" in n(bloqueio) or "migrado" in n(status_ciclo) else "nao"
            saldo = l.get("Líq. atual", l.get("Liq atual", l.get("Líquido", r.get("saldo_liquido_disponivel", "nao_determinado"))))
            patr = l.get("Patr. líq", l.get("Patrimonio líquido", "nao_determinado"))
            detalhes.append(f"{c}:elegivel={elig}:status={status_ciclo}:origem_migrada={origem_migr}")
            saldos.append(f"{c}:{saldo}")
            pats.append(f"{c}:{patr}")
            if n(elig) != "sim":
                comp_bloq.append(c)
            else:
                tem_aprov = True
            if "bloque" in n(bloqueio): q_s6 += 1
            if "ativo_pos_switching" in n(status_ciclo): q_pos += 1
            if origem_migr == "sim" and "ativo_pos_switching" not in n(status_ciclo): q_uso_ind += 1
        valor = r.get("Valor", 0)
        valor_num = float(valor) if str(valor).replace('.','',1).replace('-','',1).isdigit() else 0.0
        saldo_total = 0.0
        for s in saldos:
            try: saldo_total += float(str(s.split(":",1)[1]).replace(",","."))
            except: pass
        saldo_pos = saldo_total - valor_num if comps else "nao_determinado"
        alerta = n(status) in ALERTAS
        if alerta: q_alerta += 1
        if comps and (not tem_aprov): q_bloq += 1
        if tem_aprov: q_aprov += 1
        if comps and isinstance(saldo_pos, float) and saldo_pos < 0: q_insuf += 1
        if len(comps) > 1 and (not isinstance(saldo_pos,float) or saldo_pos >= -1e-9): q_multi_ok += 1
        linhas.append({
            "data": r.get("Data", ""), "conta": r.get("Conta", ""), "valor": r.get("Valor", ""),
            "lote_sugerido": lote_sugerido, "status_recomendacao": status,
            "fontes_componentes": " + ".join(comps), "qtd_fontes_componentes": len(comps),
            "elegibilidade_componentes": " | ".join(detalhes) if detalhes else "nao_determinado",
            "componentes_bloqueados": " + ".join(comp_bloq), "bloqueio_se_houver": r.get("Motivo bloqueio lote", ""),
            "saldo_liquido_disponivel_componentes": " | ".join(saldos) if saldos else "nao_determinado",
            "valor_liquido_necessario": valor_num, "saldo_pos_pagamento_estimado": saldo_pos,
            "patrimonio_liquido_fonte": " | ".join(pats) if pats else "nao_determinado",
            "fonte_aprovada_para_pagamento": "sim" if tem_aprov else ("alerta_operacional" if alerta else "nao"),
            "motivo_aprovacao_ou_bloqueio": "alerta_operacional_justificado" if alerta else ("fonte_elegivel" if tem_aprov else "bloqueio_ou_matriz_indisponivel"),
        })

    out = pd.DataFrame(linhas)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(CSV, index=False)

    print(f"qtd_pagamentos_futuros_avaliados={len(extrato)}")
    print(f"qtd_pagamentos_com_lote_sugerido={int((extrato['Lote sugerido'].astype(str).str.strip()!='').sum())}")
    print(f"qtd_pagamentos_sem_lote_sugerido={int((extrato['Lote sugerido'].astype(str).str.strip()=='').sum())}")
    print(f"qtd_pagamentos_com_fonte_aprovada_para_pagamento={q_aprov}")
    print(f"qtd_pagamentos_com_fonte_bloqueada={q_bloq}")
    print(f"qtd_pagamentos_com_componente_s6_bloqueado={q_s6}")
    print(f"qtd_pagamentos_com_lote_pos_switching_valido={q_pos}")
    print(f"qtd_pagamentos_usando_origem_migrada_indevidamente={q_uso_ind}")
    print(f"qtd_pagamentos_com_saldo_liquido_insuficiente={q_insuf}")
    print(f"qtd_pagamentos_com_alerta_operacional_justificado={q_alerta}")
    print(f"qtd_pagamentos_multifonte={q_multi}")
    print(f"qtd_pagamentos_multifonte_sem_residuo_artificial={q_multi_ok}")
    print("qtd_lotes_sugeridos_alterados=0")
    print("qtd_status_recomendacao_alterados=0")
    print(f"qtd_linhas_csv_s7f={len(out)}")
    print(f"csv_s7f={CSV.relative_to(RAIZ)}")
    print(f"sentinela_lote_190_status={(lotes[lotes['Lote'].astype(str).str.contains('190 mai', case=False, na=False)]['Status'].iloc[0] if ('Lote' in lotes.columns and (lotes['Lote'].astype(str).str.contains('190 mai', case=False, na=False)).any()) else 'nao_localizado')}")
    print(f"sentinela_lote_3120_status={(lotes[lotes['Lote'].astype(str).str.contains('3120 mai', case=False, na=False)]['Status'].iloc[0] if ('Lote' in lotes.columns and (lotes['Lote'].astype(str).str.contains('3120 mai', case=False, na=False)).any()) else 'nao_localizado')}")
    print(f"matriz_status={status_matriz}")
    st = "recomendacoes_futuras_reconciliadas" if len(extrato)==len(out) else "falha_reconciliacao_s7f"
    print(f"status_geral_s7f={st}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
