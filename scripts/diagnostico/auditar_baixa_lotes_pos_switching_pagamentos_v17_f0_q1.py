from __future__ import annotations
import hashlib
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

BASELINE_ENTRADA = "c7ef001"
CSV_DETALHE = RAIZ / "saidas/diagnostico/auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.csv"
CSV_RESUMO = RAIZ / "saidas/diagnostico/auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1_resumo.csv"
DADOS = RAIZ / "dados/dados_financeiros.xlsx"

def _n(v: Any) -> str: return str(v or "").strip().lower()
def _num(v: Any):
    try: return float(str(v).replace('.', '').replace(',', '.') if isinstance(v, str) and ',' in str(v) and str(v).count(',')==1 and str(v).count('.')>=1 else v)
    except Exception:
        try: return float(v)
        except Exception: return None
def _d(v: Any):
    try: return pd.to_datetime(v, errors='coerce').date()
    except Exception: return None

def _hash_arquivo(p: Path) -> str:
    if not p.exists(): return "nao_existe"
    h = hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda: f.read(8192), b''): h.update(c)
    return h.hexdigest()

def _norm_lote(v: Any) -> str:
    return _n(str(v).replace('.', '').replace(',', '.'))

def _row_base(origem_pagamento: str, fonte_base: str, fonte_passados: str):
    return {k: None for k in [
        "origem_pagamento","fonte_base_operacional_gastos","fonte_pagamentos_passados","pagamento_id","data_pagamento","conta","valor_pagamento","pagamento_ok_na_planilha","presente_no_extrato_passado","presente_no_extrato_futuro","pacote_do_dia","status_recomendacao","lote_sugerido","lote_usado_planilha","lote_pos_switching_renderizado","fonte_pos_switching","pos_sw_flag","origem_switching","destino_switching","data_switching","lote_pos_switching_elegivel_na_data","fonte_eh_lote_pos_switching","origem_migrada_usada_indevidamente","saldo_pos_switching_exibido","saldo_temporal_antes","consumo_temporal","saldo_temporal_depois","saldo_remanescente_extrato","bruto_pos","liquido_pos","bruto_sacado_situacao_atual","liquido_sacado_situacao_atual","baixa_refletida_situacao_atual","lote_pos_switching_permanece_ativo_integral","valor_pagamento_abateu_saldo_pos_switching","saldo_pos_switching_esperado_apos_pagamento","divergencia_baixa_pos_switching","tipo_divergencia_q1","tipo_falha_replay_passado","camada_onde_falha","evidencia_q1","recomendacao_q1"]} | {"origem_pagamento": origem_pagamento, "fonte_base_operacional_gastos": fonte_base, "fonte_pagamentos_passados": fonte_passados}

def main():
    hash_antes = _hash_arquivo(DADOS)
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO_BASELINE)

    extrato_futuro = [dict(x) for x in (saida.extrato_futuro or []) if isinstance(x, dict)]
    extrato_passado = [dict(x) for x in (saida.extrato_passado or []) if isinstance(x, dict)]
    switchings = [dict(x) for x in (saida.switchings or []) if isinstance(x, dict)]
    lotes_pos = [dict(x) for x in (getattr(saida, 'lotes_sinteticos_pos_switching_console', lambda **_: [])(limite=500) or [])]
    situacao_atual = [dict(x) for x in (getattr(saida, 'estado_pos_switching_lotes_console', lambda **_: [])(limite=500) or [])]

    fonte_base_operacional_gastos = "nao_localizada"
    base_pag_ok = []
    prc = getattr(saida, 'pagamentos_realizados_console', None)
    if callable(prc):
        prc = prc(limite=5000)
    if isinstance(prc, list) and prc:
        fonte_base_operacional_gastos = "saida.pagamentos_realizados_console"
        for r in prc:
            if not isinstance(r, dict):
                continue
            lote = str(r.get('Lotes usados') or r.get('Lote') or '')
            if not lote: continue
            base_pag_ok.append({"Data": r.get('Data'), "Conta": r.get('Descrição') or r.get('Conta'), "Valor": r.get('Valor'), "Lote usado": lote, "Pagamento OK": "sim"})

    destinos = {_norm_lote(s.get('lote_destino') or s.get('lote_pos_switching')): s for s in switchings if _norm_lote(s.get('lote_destino') or s.get('lote_pos_switching'))}
    lotes_pos_nomes = {_norm_lote(x.get('Lote') or x.get('lote') or x.get('Novo lote') or x.get('lote_destino') or x.get('lote_pos_switching')) for x in lotes_pos}
    lotes_pos_nomes = {x for x in lotes_pos_nomes if x}

    detalhes = []
    # futuros
    for i, r in enumerate(extrato_futuro, 1):
        row = _row_base("pagamentos_futuros", fonte_base_operacional_gastos, "saida_canonica")
        lote_sug = str(r.get('Lote sugerido') or r.get('Lote') or '')
        parts = [_norm_lote(p.strip()) for p in lote_sug.split('+') if p.strip()]
        lote_pos = next((p for p in parts if p in lotes_pos_nomes or p in destinos), '')
        row.update({"pagamento_id": r.get('Despesa ID') or f"fut_{i}", "data_pagamento": r.get('Data'), "conta": r.get('Conta'), "valor_pagamento": r.get('Valor'), "pagamento_ok_na_planilha": "nao", "presente_no_extrato_passado": "nao", "presente_no_extrato_futuro": "sim", "pacote_do_dia": r.get('Pacote do dia') or r.get('pacote_do_dia_ledger'), "status_recomendacao": r.get('Status recomendação') or r.get('status_ledger'), "lote_sugerido": lote_sug, "lote_usado_planilha": lote_sug, "lote_pos_switching_renderizado": lote_pos, "fonte_pos_switching": "sim" if lote_pos else "nao", "pos_sw_flag": "sim" if lote_pos else "nao", "fonte_eh_lote_pos_switching": "sim" if lote_pos else "nao", "origem_migrada_usada_indevidamente": "nao"})
        if lote_pos:
            sw = destinos.get(lote_pos, {})
            row["origem_switching"] = sw.get('lote_origem')
            row["destino_switching"] = sw.get('lote_destino') or sw.get('lote_pos_switching')
            row["data_switching"] = sw.get('data_switching')
            row["lote_pos_switching_elegivel_na_data"] = "sim"
            row["divergencia_baixa_pos_switching"] = "sim"
            row["tipo_divergencia_q1"] = "baixa_pos_switching_sem_evidencia_observavel"
            row["camada_onde_falha"] = "saida_observavel"
            row["evidencia_q1"] = "pagamento futuro com lote pos-switching sem campo de baixa observavel"
            row["recomendacao_q1"] = "V17-F0-Q.2"
        else:
            row["tipo_divergencia_q1"] = "sem_pagamento_pos_switching_para_auditar"
            row["camada_onde_falha"] = "nao_determinado"
            row["divergencia_baixa_pos_switching"] = "nao"
            row["evidencia_q1"] = "sem lote pos-switching"
            row["recomendacao_q1"] = "continuar_diagnostico"
        detalhes.append(row)

    # passados candidatos a partir da base operacional
    explicitos = [(pd.Timestamp('2026-05-13').date(), 'aluguel', 192.89, 'lote 190 mai'), (pd.Timestamp('2026-05-13').date(), 'pelada', 24.00, 'lote 3120 mai')]
    casos_encontrados = 0
    casos_ausentes_extrato = 0
    passados_pos = []
    if fonte_base_operacional_gastos != "nao_localizada":
        for r in base_pag_ok:
            lote = _norm_lote(r.get('Lote usado'))
            if any(lp in lote for lp in lotes_pos_nomes) or lote in lotes_pos_nomes:
                passados_pos.append(r)
        for i, r in enumerate(passados_pos, 1):
            dt = _d(r.get('Data')); conta = str(r.get('Conta') or ''); val = _num(r.get('Valor')); lote = str(r.get('Lote usado') or '')
            lote_n = _norm_lote(lote)
            presente_extrato = any(_d(x.get('Data'))==dt and _n(x.get('Conta'))==_n(conta) and round(_num(x.get('Líquido') or x.get('Valor') or 0) or 0,2)==round(val or 0,2) for x in extrato_passado)
            row = _row_base("pagamentos_passados_base_operacional", fonte_base_operacional_gastos, "saida_canonica")
            row.update({"pagamento_id": f"pas_{i}","data_pagamento": r.get('Data'),"conta": conta,"valor_pagamento": val,"pagamento_ok_na_planilha": "sim","presente_no_extrato_passado": "sim" if presente_extrato else "nao","presente_no_extrato_futuro": "nao","lote_usado_planilha": lote,"lote_sugerido": lote,"lote_pos_switching_renderizado": lote_n,"fonte_pos_switching":"sim","pos_sw_flag":"sim","fonte_eh_lote_pos_switching":"sim","lote_pos_switching_elegivel_na_data":"sim","origem_migrada_usada_indevidamente":"nao"})
            sit = next((s for s in situacao_atual if lote_n in _norm_lote(s.get('Novo lote') or s.get('Lote') or '')), {})
            bruto_sac = _num(sit.get('Bruto sac.') or sit.get('bruto_sacado') or 0)
            liq_sac = _num(sit.get('Líq. sac.') or sit.get('liquido_sacado') or 0)
            status_novo = _n(sit.get('Status novo') or sit.get('status') or '')
            row.update({"bruto_sacado_situacao_atual": bruto_sac,"liquido_sacado_situacao_atual": liq_sac,"baixa_refletida_situacao_atual": "sim" if (bruto_sac or liq_sac) else "nao","lote_pos_switching_permanece_ativo_integral": "sim" if status_novo=='ativo_pos_switching' and (bruto_sac or 0)==0 and (liq_sac or 0)==0 else "nao"})
            if not presente_extrato:
                row["tipo_divergencia_q1"] = "pagamento_ok_pos_switching_ausente_extrato_passado"
                row["camada_onde_falha"] = "extrato_passado"
                row["divergencia_baixa_pos_switching"] = "sim"
                row["recomendacao_q1"] = "V17-F0-Q.2"
                row["evidencia_q1"] = "pagamento OK pos-switching localizado na base operacional e ausente no extrato passado"
                casos_ausentes_extrato += 1
                if row["lote_pos_switching_permanece_ativo_integral"] == "sim":
                    row["tipo_falha_replay_passado"] = "baixa_passada_pos_switching_nao_refletida_situacao_atual"
            else:
                row["tipo_divergencia_q1"] = "sem_divergencia_observada"
                row["camada_onde_falha"] = "sem_falha_observada"
                row["divergencia_baixa_pos_switching"] = "nao"
                row["recomendacao_q1"] = "continuar_diagnostico"
                row["evidencia_q1"] = "pagamento presente no extrato passado"
            detalhes.append(row)

    # casos explícitos preenchidos
    for dt, conta, valor, lote in explicitos:
        found = any(_d(r.get('Data'))==dt and _n(r.get('Conta'))==conta and round(_num(r.get('Valor')) or 0,2)==round(valor,2) and lote in _n(r.get('Lote usado')) for r in base_pag_ok)
        if found: casos_encontrados += 1
        already = any(_d(d.get('data_pagamento'))==dt and _n(d.get('conta'))==conta and round(_num(d.get('valor_pagamento')) or 0,2)==round(valor,2) for d in detalhes)
        if not already:
            row = _row_base("caso_explicitamente_auditado", fonte_base_operacional_gastos, "saida_canonica")
            row.update({"pagamento_id": f"caso_{conta}","data_pagamento": str(dt),"conta": conta.title(),"valor_pagamento": valor,"lote_usado_planilha": lote,"lote_sugerido": lote,"presente_no_extrato_passado":"nao","presente_no_extrato_futuro":"nao","fonte_eh_lote_pos_switching":"sim","fonte_pos_switching":"sim","pos_sw_flag":"sim","lote_pos_switching_renderizado":lote,"divergencia_baixa_pos_switching":"sim"})
            if fonte_base_operacional_gastos == "nao_localizada":
                row.update({"pagamento_ok_na_planilha":"indeterminado","tipo_divergencia_q1":"base_operacional_gastos_nao_localizada","camada_onde_falha":"base_operacional_gastos","evidencia_q1":"base operacional nao localizada; caso explicitamente auditado sem verificacao estrutural","recomendacao_q1":"investigar_base_operacional_gastos"})
            elif found:
                row.update({"pagamento_ok_na_planilha":"sim","tipo_divergencia_q1":"pagamento_ok_pos_switching_ausente_extrato_passado","camada_onde_falha":"extrato_passado","evidencia_q1":"caso explicito encontrado na base operacional e ausente no extrato passado","recomendacao_q1":"V17-F0-Q.2"})
                casos_ausentes_extrato += 1
            else:
                row.update({"pagamento_ok_na_planilha":"nao","tipo_divergencia_q1":"caso_explicito_nao_localizado_na_base_operacional","camada_onde_falha":"base_operacional_gastos","evidencia_q1":"base operacional localizada mas caso explicito nao encontrado","recomendacao_q1":"continuar_diagnostico"})
            detalhes.append(row)

    df = pd.DataFrame(detalhes)
    q0_path = RAIZ / "saidas/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.csv"
    q0r = {}
    if q0_path.exists():
        q0 = pd.read_csv(q0_path)
        r = q0[q0.get('tipo_linha','')=='resumo']
        if not r.empty: q0r = r.iloc[0].to_dict()

    fut = df[df['origem_pagamento']=='pagamentos_futuros'] if not df.empty else pd.DataFrame()
    pos = df[df['fonte_eh_lote_pos_switching']=='sim'] if not df.empty else pd.DataFrame()

    if fonte_base_operacional_gastos == 'nao_localizada':
        qtd_pass_ok = qtd_pass_aus = qtd_pass_sit = 'nao_determinado'
        status = 'base_operacional_gastos_nao_localizada'
        camada = 'base_operacional_gastos'
    else:
        qtd_pass_ok = int((df['origem_pagamento']=='pagamentos_passados_base_operacional').sum())
        qtd_pass_aus = int((df['tipo_divergencia_q1']=='pagamento_ok_pos_switching_ausente_extrato_passado').sum())
        qtd_pass_sit = int((df['tipo_falha_replay_passado']=='baixa_passada_pos_switching_nao_refletida_situacao_atual').sum()) if 'tipo_falha_replay_passado' in df.columns else 0
        status = 'pagamento_ok_pos_switching_ausente_extrato_passado' if qtd_pass_aus>0 else ('baixa_pos_switching_sem_evidencia_observavel' if int((pos['tipo_divergencia_q1']=='baixa_pos_switching_sem_evidencia_observavel').sum())>0 else 'sem_pagamentos_pos_switching_para_auditar')
        camada = 'extrato_passado' if qtd_pass_aus>0 else ('saida_observavel' if status=='baixa_pos_switching_sem_evidencia_observavel' else 'sem_falha_observada')

    hash_depois = _hash_arquivo(DADOS)
    modificado = 'sim' if hash_antes != hash_depois else 'nao'
    if modificado == 'sim':
        status = 'falha_diagnostico_q1'

    alinhado = 'nao'
    if q0r:
        ok_match = (int(len(fut))==int(q0r.get('total_pagamentos_futuros',-1)) and int((fut['fonte_eh_lote_pos_switching']=='sim').sum())==int(q0r.get('pagamentos_usando_lote_pos_switching',-1)) and int(len(lotes_pos))==int(q0r.get('lotes_pos_switching_total',-1)) and int((df['origem_migrada_usada_indevidamente']=='sim').sum())==int(q0r.get('origens_migradas_usadas_indevidamente_total',-1)))
        alinhado = 'sim' if ok_match else 'nao'

    resumo = {
        'baseline_entrada': BASELINE_ENTRADA,
        'fonte_base_operacional_gastos': fonte_base_operacional_gastos,
        'fonte_pagamentos_passados': 'saida_canonica',
        'qtd_pagamentos_futuros': int(len(fut)),
        'qtd_pagamentos_futuros_usando_lote_pos_switching': int((fut['fonte_eh_lote_pos_switching']=='sim').sum()) if not fut.empty else 0,
        'qtd_pagamentos_passados_ok_usando_lote_pos_switching': qtd_pass_ok,
        'qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado': qtd_pass_aus,
        'qtd_baixas_passadas_pos_switching_nao_refletidas_situacao_atual': qtd_pass_sit,
        'qtd_casos_explicitos_auditados': 2,
        'qtd_casos_explicitos_encontrados_base_operacional': casos_encontrados if fonte_base_operacional_gastos != 'nao_localizada' else 'nao_determinado',
        'qtd_casos_explicitos_ausentes_extrato_passado': casos_ausentes_extrato if fonte_base_operacional_gastos != 'nao_localizada' else 'nao_determinado',
        'qtd_lotes_pos_switching_total': int(len(lotes_pos)),
        'qtd_lotes_pos_switching_elegiveis_em_alguma_data': int((fut['lote_pos_switching_elegivel_na_data']=='sim').sum()) if not fut.empty else 0,
        'qtd_pagamentos_pos_switching_com_baixa_confirmada': int((pos['tipo_divergencia_q1']=='baixa_pos_switching_confirmada').sum()) if not pos.empty else 0,
        'qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada': int((pos['tipo_divergencia_q1']=='baixa_pos_switching_ausente_confirmada').sum()) if not pos.empty else 0,
        'qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa': int((pos['tipo_divergencia_q1']=='baixa_pos_switching_sem_evidencia_observavel').sum()) if not pos.empty else 0,
        'qtd_pagamentos_pos_switching_com_baixa_inconsistente': int((pos['tipo_divergencia_q1']=='baixa_pos_switching_parcial_ou_inconsistente').sum()) if not pos.empty else 0,
        'qtd_origens_migradas_usadas_indevidamente': int((df['origem_migrada_usada_indevidamente']=='sim').sum()) if not df.empty else 0,
        'qtd_divergencias_baixa_pos_switching': int((df['divergencia_baixa_pos_switching']=='sim').sum()) if not df.empty else 0,
        'camada_falha_dominante': camada,
        'status_geral_q1': status,
        'q1_alinhado_com_q0': alinhado,
        'dados_financeiros_modificado_apos_execucao': modificado,
    }

    CSV_DETALHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_DETALHE, index=False)
    pd.DataFrame([resumo]).to_csv(CSV_RESUMO, index=False)

    print('=== AUDITORIA V17-F0-Q.1.2 — PAGAMENTOS PASSADOS POS-SWITCHING AUSENTES DO EXTRATO ===')
    for k,v in resumo.items(): print(f'{k}={v}')
    if modificado == 'sim':
        print('motivo_falha=dados_financeiros_modificado_por_execucao_diagnostica')
    print(f'csv_detalhe={CSV_DETALHE}')
    print(f'csv_resumo={CSV_RESUMO}')

if __name__ == '__main__':
    main()
