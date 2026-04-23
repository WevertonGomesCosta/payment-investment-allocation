from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from copy import deepcopy

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ
from nucleo.motor_diario_conjunto_experimental_v143 import rodar_motor_diario_conjunto_experimental_v143
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import _safe_float

DATA_INICIO=date(2026,5,4)
DATA_FIM=date(2026,5,12)
TAU=10.0
LIMITE=24
CAP=5

def norm(x):
    return str(x or '')

def mapd(p):
    return {str(i.get('data')): i for i in (p.get('decisoes_diarias') or [])}

def switch_summary(dec):
    cands=list(dec.get('candidatos') or [])
    sw=[c for c in cands if norm(c.get('tipo_pacote')) in {'switch_only','switch_then_pay'}]
    sw=sorted(sw,key=lambda c:(tuple(c.get('vetor_total_estimado') or ()), -_safe_float(c.get('patrimonio_terminal_proxy_estimado'))))
    best=sw[0] if sw else None
    return {
        'quantidade_candidatos_switching': len(sw),
        'melhor_switching': None if best is None else {
            'tipo_pacote': best.get('tipo_pacote'),
            'rotulo_switching': best.get('rotulo_switching'),
            'classe_switching': best.get('classe_switching'),
            'eventos_switching': best.get('eventos_switching'),
            'vetor_total_estimado': list(best.get('vetor_total_estimado') or ()),
            'patrimonio_terminal_proxy_estimado': round(_safe_float(best.get('patrimonio_terminal_proxy_estimado')),2),
        }
    }

raiz=RAIZ
atual=rodar_motor_diario_conjunto_experimental_v143(
    raiz_repositorio=raiz,data_inicio=DATA_INICIO,data_fim=DATA_FIM,
    limite_candidatos_por_data=LIMITE,cap_fontes_destino=CAP,tau_custo_operacional=None,
)
tau=rodar_motor_diario_conjunto_experimental_v143(
    raiz_repositorio=raiz,data_inicio=DATA_INICIO,data_fim=DATA_FIM,
    limite_candidatos_por_data=LIMITE,cap_fontes_destino=CAP,tau_custo_operacional=TAU,
)
dec_a=mapd(atual); dec_t=mapd(tau)
dias=sorted(set(dec_a)|set(dec_t))
compar=[]; add=0; changed=0
for dia in dias:
    a=dec_a[dia]; t=dec_t[dia]
    va=norm(a.get('pacote_vencedor')); vt=norm(t.get('pacote_vencedor'))
    mudou=va!=vt
    if mudou:
        changed+=1
    adicional=va in {'pay_only','no_action'} and vt in {'switch_then_pay','switch_only'}
    if adicional:
        add+=1
    compar.append({
        'data': dia,
        'mudou_pacote_vencedor': mudou,
        'switching_adicional_promovido': adicional,
        'vencedor_regra_atual': va,
        'vencedor_tau_10_0': vt,
        'patrimonio_regra_atual': round(_safe_float(a.get('patrimonio_terminal_proxy_estimado_vencedor')),2),
        'patrimonio_tau_10_0': round(_safe_float(t.get('patrimonio_terminal_proxy_estimado_vencedor')),2),
        'vetor_regra_atual': list(a.get('vetor_total_estimado_vencedor') or ()),
        'vetor_tau_10_0': list(t.get('vetor_total_estimado_vencedor') or ()),
        'justificativa_atual': a.get('justificativa_vencedor'),
        'justificativa_tau': t.get('justificativa_vencedor'),
        'melhor_switching_regra_atual': switch_summary(a),
        'melhor_switching_tau': switch_summary(t),
    })
res_a=deepcopy(atual.get('resumo') or {})
res_t=deepcopy(tau.get('resumo') or {})
pa=_safe_float(res_a.get('patrimonio_liquido_terminal_proxy_final'))
pt=_safe_float(res_t.get('patrimonio_liquido_terminal_proxy_final'))
payload={
    'status':'ok',
    'baseline_operacional':'V149',
    'versao_auditoria':'V150',
    'janela':{'data_inicio':DATA_INICIO.isoformat(),'data_fim':DATA_FIM.isoformat()},
    'parametros':{'tau_custo_operacional':TAU,'limite_candidatos_por_data':LIMITE,'cap_fontes_destino':CAP},
    'resumo_comparativo':{
        'switching_adicionais_promovidos_por_tau':add,
        'dias_com_pacote_vencedor_alterado':changed,
        'decisoes_switch_then_pay_regra_atual':int(res_a.get('decisoes_switch_then_pay') or 0),
        'decisoes_switch_only_regra_atual':int(res_a.get('decisoes_switch_only') or 0),
        'decisoes_switch_then_pay_tau_10_0':int(res_t.get('decisoes_switch_then_pay') or 0),
        'decisoes_switch_only_tau_10_0':int(res_t.get('decisoes_switch_only') or 0),
        'patrimonio_terminal_proxy_final_regra_atual':round(pa,2),
        'patrimonio_terminal_proxy_final_tau_10_0':round(pt,2),
        'delta_patrimonio_terminal_proxy_final':round(pt-pa,2)
    },
    'regra_atual':atual,
    'tau_10_0':tau,
    'comparativo_dias':compar,
}
path=raiz/'saidas'/'auditoria_janela_tau_v150_2026-05-04_2026-05-12.json'
path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(payload['resumo_comparativo'],ensure_ascii=False,indent=2))
