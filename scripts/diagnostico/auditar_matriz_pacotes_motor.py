from __future__ import annotations
from pathlib import Path
from datetime import date
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica

PACOTES = ['no_action','switch_only','pay_only','switch_then_pay','pay_then_switch']


def _norm(v)->str:
    return str(v or '').strip().lower()


def main()->int:
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
        raise SystemExit('extrato futuro vazio')
    extrato['data'] = pd.to_datetime(extrato.get('Data'), errors='coerce').dt.date
    extrato = extrato[extrato['data'].notna()].copy()

    aud_fontes = pd.DataFrame((saida.auditoria or {}).get('alocacao_fontes_auditoria', []))
    if len(aud_fontes):
        col_data = aud_fontes['Data'] if 'Data' in aud_fontes.columns else pd.Series([None]*len(aud_fontes), index=aud_fontes.index)
        aud_fontes['data'] = pd.to_datetime(col_data, errors='coerce').dt.date

    datas = sorted(extrato['data'].unique())
    estado_id = 0
    rows = []
    plano_shadow = getattr(getattr(ctx, 'switching_economico_shadow', None), 'plano_shadow', pd.DataFrame())
    qtd_plano_shadow = int(len(plano_shadow)) if isinstance(plano_shadow, pd.DataFrame) else 0

    for d in datas:
        estado_id += 1
        dia = extrato[extrato['data'].eq(d)].copy()
        ad = aud_fontes[aud_fontes['data'].eq(d)].copy() if len(aud_fontes) else pd.DataFrame()
        pagamentos = int(len(dia))
        total_pag = float(pd.to_numeric(dia.get('Valor', pd.Series([],dtype=float)), errors='coerce').fillna(0).sum())
        cand_sw_disp = int(ad.get('evento_switching_id', pd.Series([],dtype=object)).fillna('').astype(str).str.strip().ne('').sum()) if len(ad) else 0
        cand_sw_bloq = int(ad.get('motivo_descarte_fonte', pd.Series([],dtype=object)).fillna('').astype(str).str.contains('gate',case=False,na=False).sum()) if len(ad) else 0
        cand_sw_prom = 0 if qtd_plano_shadow == 0 else cand_sw_disp
        pacotes_materializados = set(dia.get('Pacote do dia', pd.Series('',index=dia.index)).fillna('').astype(str).str.strip().str.lower())
        pacote_vencedor = next(iter(pacotes_materializados), 'no_action' if pagamentos == 0 else 'pay_only')

        for p in PACOTES:
            has_pay = pagamentos > 0
            constru = (p == 'pay_only' and has_pay)
            aval = constru
            fact = (p == 'pay_only' and has_pay) or (p == 'no_action' and not has_pay)
            mat = p in pacotes_materializados
            origem = 'motor_nativo' if constru else 'ausente_no_motor'
            motivo_aus = 'n/d'
            if not constru:
                if p in ('switch_only','switch_then_pay','pay_then_switch'):
                    motivo_aus = 'pacote_nao_implementado'
                elif p == 'pay_only' and not has_pay:
                    motivo_aus = 'sem_pagamento_no_dia'
                elif p == 'no_action' and has_pay:
                    motivo_aus = 'pagamento_obrigatorio_no_dia'
                else:
                    motivo_aus = 'ausente_no_motor'
            status_ledger = str(dia.get('Status recomendação', pd.Series('',index=dia.index)).iloc[0] if len(dia) else '')
            motivo_ledger = str(dia.get('Motivo bloqueio lote', pd.Series('',index=dia.index)).iloc[0] if len(dia) else '')

            rows.append({
                'data': d.isoformat(), 'pacote': p, 'origem_registro': origem,
                'estado_inicial_id': f'estado_{estado_id:04d}', 'pagamentos_do_dia': pagamentos,
                'valor_total_pagamentos_dia': round(total_pag,2), 'recebidos_disponiveis_inicio_dia': int(ad.get('tipo_fonte_candidata', pd.Series([],dtype=object)).fillna('').astype(str).str.contains('recebido|caixa_pre_aplicacao',case=False,regex=True).sum()) if len(ad) else 0,
                'recebidos_ativados_no_dia': 0, 'lotes_ativos_inicio_dia': int(ad.get('fonte_candidata_id', pd.Series([],dtype=object)).fillna('').astype(str).str.contains('lote',case=False,na=False).sum()) if len(ad) else 0,
                'lotes_vencidos_normalizados_no_dia': 0, 'lotes_exauridos_inicio_dia': 0, 'fontes_disponiveis_inicio_dia': int(ad.get('fonte_candidata_id', pd.Series([],dtype=object)).fillna('').astype(str).str.strip().ne('').sum()) if len(ad) else 0,
                'destinos_ranking_elegiveis': len(getattr(getattr(ctx,'ranking_carteira',None),'quadro_destinos_switch',pd.DataFrame())),
                'candidatos_switching_disponiveis': cand_sw_disp,
                'candidatos_switching_bloqueados_gate': cand_sw_bloq,
                'candidatos_switching_promoviveis': cand_sw_prom,
                'pacote_construido_no_motor': int(constru), 'pacote_avaliado_no_motor': int(aval), 'pacote_factivel_no_estado': int(fact),
                'pacote_materializado_no_fluxo_atual': int(mat), 'pacote_vencedor_observado': pacote_vencedor,
                'motivo_nao_construido': motivo_aus if not constru else 'n/d', 'motivo_nao_avaliado': 'comparador_de_pacotes_ausente' if not aval else 'n/d',
                'motivo_infactibilidade': ('sem_pagamento_no_dia' if p=='pay_only' and not has_pay else ('pagamento_obrigatorio_no_dia' if p=='no_action' and has_pay else ('pacote_nao_implementado' if p.startswith('switch') and p!='switch_only' or p=='switch_only' else 'n/d'))) if not fact else 'n/d',
                'motivo_descarte': 'comparador_de_pacotes_ausente' if not mat else 'n/d', 'motivo_nao_materializado': 'ledger_nao_materializa_pacote' if not mat and constru else motivo_aus,
                'valor_objetivo_ou_proxy_terminal': '', 'delta_vs_no_action': '', 'delta_vs_pay_only': '',
                'status_ledger_resultante': status_ledger, 'motivo_ledger_resultante': motivo_ledger,
                'usa_multifonte': int(dia.get('Lote sugerido', pd.Series('',index=dia.index)).fillna('').astype(str).str.contains('+',regex=False).any()) if len(dia) else 0,
                'qtd_fontes_pagamento': int(dia.get('Lote sugerido', pd.Series('',index=dia.index)).fillna('').astype(str).str.count('\\+').add(1).sum()) if len(dia) else 0,
                'observacao_auditoria': 'instrumentacao_observacional_sem_mudanca_decisoria'
            })

    df = pd.DataFrame(rows)
    out = RAIZ / 'saidas/diagnostico/auditoria_matriz_pacotes_motor.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    resumo = {
        'total_dias': df['data'].nunique(),
        'total_pacotes_conceituais': len(df),
        'total_pacotes_construidos_no_motor': int(df['pacote_construido_no_motor'].sum()),
        'total_pacotes_avaliados_no_motor': int(df['pacote_avaliado_no_motor'].sum()),
        'total_switch_only_construidos': int(df[df['pacote'].eq('switch_only')]['pacote_construido_no_motor'].sum()),
        'total_switch_then_pay_construidos': int(df[df['pacote'].eq('switch_then_pay')]['pacote_construido_no_motor'].sum()),
        'total_pay_then_switch_construidos': int(df[df['pacote'].eq('pay_then_switch')]['pacote_construido_no_motor'].sum()),
        'total_candidatos_switching_disponiveis': int(df['candidatos_switching_disponiveis'].sum()),
        'total_candidatos_switching_bloqueados_gate': int(df['candidatos_switching_bloqueados_gate'].sum()),
        'total_candidatos_switching_promoviveis': int(df['candidatos_switching_promoviveis'].sum()),
        'total_pacotes_switching_materializados': int(df[df['pacote'].isin(['switch_only','switch_then_pay','pay_then_switch'])]['pacote_materializado_no_fluxo_atual'].sum()),
        'causa_principal_switching_zero': 'pacote_switching_nao_implementado',
    }
    print(out)
    print(resumo)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
