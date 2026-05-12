from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any
import pandas as pd
RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path: sys.path.insert(0, str(RAIZ_REPOSITORIO))
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2
from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida
from nucleo.ponte_renderizacao_switching_v17_c6 import renderizar_switchings_compativeis_saida
ARQUIVO_DIAGNOSTICO = RAIZ_REPOSITORIO / 'saidas' / 'diagnostico' / 'gate_remocao_ponte_v17_f0_p0.csv'

def _txt(v: Any) -> str:
    if v is None: return ''
    try:
        if pd.isna(v): return ''
    except Exception: pass
    return str(v).strip()

def _norm(v: Any) -> str: return ' '.join(_txt(v).lower().split())

def _pick(d: dict[str, Any], nomes: list[str]) -> Any:
    mapa = {_norm(k): k for k in d}
    for n in nomes:
        c = mapa.get(_norm(n))
        if c is not None and _txt(d.get(c)): return d.get(c)
    return ''

def _num(v: Any) -> float:
    t = _txt(v)
    if not t: return 0.0
    try: return round(float(v), 2)
    except Exception: pass
    l = t.replace('R$', '').strip()
    if ',' in l: l = l.replace('.', '').replace(',', '.')
    return round(float(l), 2)

def _data(v: Any) -> str:
    if not _txt(v): return ''
    for d in (False, True):
        try:
            dt = pd.to_datetime(v, errors='raise', dayfirst=d)
            if not pd.isna(dt): return dt.date().isoformat()
        except Exception: pass
    return _txt(v)[:10]

def _canon(regs: list[dict[str, Any]], fonte: str) -> list[dict[str, Any]]:
    out = []
    for r in regs:
        data = _data(_pick(r, ['Data', 'data_switching', 'Data sugerida']))
        lo = _txt(_pick(r, ['Lote origem', 'lote_origem']))
        ld = _txt(_pick(r, ['Lote destino', 'lote_destino', 'lote_pos_switching']))
        pdst = _txt(_pick(r, ['Produto destino switching', 'Produto destino', 'Destino', 'produto_destino']))
        vl = _num(_pick(r, ['Valor líquido origem', 'valor_liquido_origem', 'valor_liquido_migrado']))
        out.append({'fonte': fonte, 'data': data, 'lote_origem': lo, 'lote_destino': ld, 'produto_destino': pdst, 'valor_liquido': f'{vl:.2f}', 'chave': '|'.join([data, lo, ld, pdst, f'{vl:.2f}']), 'json': json.dumps(r, ensure_ascii=False, default=str, sort_keys=True)})
    return sorted(out, key=lambda x: (x['data'], x['lote_origem'], x['lote_destino'], x['produto_destino'], x['valor_liquido']))

def _comparar(a: list[dict[str, Any]], b: list[dict[str, Any]], nome_a: str, nome_b: str) -> list[dict[str, Any]]:
    ma, mb = {x['chave']: x for x in a}, {x['chave']: x for x in b}
    divs = []
    for ch in sorted(set(ma) | set(mb)):
        if ch in ma and ch in mb: continue
        base = ma.get(ch) or mb.get(ch) or {}
        divs.append({'tipo_linha': 'divergencia_switching', 'comparacao': f'{nome_a}_vs_{nome_b}', 'data': base.get('data', ''), 'lote_origem': base.get('lote_origem', ''), 'lote_destino': base.get('lote_destino', ''), 'produto_destino': base.get('produto_destino', ''), 'valor_liquido': base.get('valor_liquido', ''), f'em_{nome_a}': 'sim' if ch in ma else 'nao', f'em_{nome_b}': 'sim' if ch in mb else 'nao', f'json_{nome_a}': ma.get(ch, {}).get('json', ''), f'json_{nome_b}': mb.get(ch, {}).get('json', '')})
    return divs

def _metricas(saida: Any, q_ledger: int) -> dict[str, Any]:
    def vm(lista,ch):
        for i in (lista or []):
            if isinstance(i,dict) and any(c in _norm(i.get('Métrica','')) for c in ch): return _num(i.get('Valor',''))
        return 0.0
    return {'valor_liquido_migrado_destinos_pos_switching': vm(saida.fechamento_atual,['valor líquido migrado para destinos pós-switching']), 'patrimonio_liquido_atual': vm(saida.fechamento_atual,['patrimônio líquido atual']), 'patrimonio_liquido_reconciliado_origens_migradas': vm(saida.fechamento_atual,['patrimônio líquido reconciliado com origens migradas']), 'rendimento_liquido_atual': vm(saida.resumo_recebidos,['rendimento líquido atual']), 'rendimento_liquido_reconciliado_contra_recebidos': vm(saida.resumo_recebidos,['rendimento líquido reconciliado contra recebidos']), 'qtd_extrato_futuro': len(getattr(saida,'extrato_futuro',[]) or []), 'qtd_eventos_ledger': q_ledger}

def main() -> None:
    ctx = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO, instalar_automaticamente=False, incluir_resolver_hibrido_5p_shadow=False, incluir_benchmark_agrupado_individual_shadow=False, incluir_benchmark_runner_futuro_shadow=False, incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
    saida_oficial = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO_BASELINE)
    ponte = renderizar_switchings_compativeis_saida(montar_pacote_orquestrado_pre_saida(ctx))
    eventos = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(ctx)
    sw_oficial = _canon(list(getattr(saida_oficial,'switchings',[]) or []), 'saida_oficial_sem_ponte')
    sw_ponte = _canon(list(getattr(ponte,'switchings_compativeis_saida',[]) or []), 'ponte_legada_diagnostica')
    sw_ledger = _canon([dict(e) for e in eventos if isinstance(e, dict)], 'ledger_materializado')
    d_op = _comparar(sw_oficial, sw_ponte, 'oficial', 'ponte_legada')
    d_ol = _comparar(sw_oficial, sw_ledger, 'oficial', 'ledger')
    d_pl = _comparar(sw_ponte, sw_ledger, 'ponte_legada', 'ledger')
    m_oficial = _metricas(saida_oficial, len(eventos))
    d_metricas = []
    resumo = {'tipo_linha':'resumo','ponte_removivel':'sim' if not (d_op or d_ol or d_pl) else 'nao','switchings_saida_oficial':len(sw_oficial),'switchings_ponte_legada':len(sw_ponte),'switchings_ledger_materializados':len(sw_ledger),'divergencias_oficial_vs_ponte_legada':len(d_op),'divergencias_oficial_vs_ledger':len(d_ol),'divergencias_ponte_legada_vs_ledger':len(d_pl),'divergencias_metricas':0,'semantica_metricas':'invariantes_saida_oficial_sem_fonte_independente_para_comparacao','switchings_com_ponte':len(sw_ponte),'switchings_sem_ponte_simulada':len(sw_ledger),'divergencias_switching':len(d_ol),**m_oficial}
    ARQUIVO_DIAGNOSTICO.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([resumo]+d_op+d_ol+d_pl).to_csv(ARQUIVO_DIAGNOSTICO,index=False)
    print('=== GATE V17-F0-P.0 — REMOCAO PREVENTIVA DA PONTE V17-C7 ===')
    print(f'versao_baseline={VERSAO_BASELINE}')
    for k in ['ponte_removivel','switchings_saida_oficial','switchings_ponte_legada','switchings_ledger_materializados','divergencias_oficial_vs_ponte_legada','divergencias_oficial_vs_ledger','divergencias_ponte_legada_vs_ledger','divergencias_metricas','semantica_metricas','switchings_com_ponte','switchings_sem_ponte_simulada','divergencias_switching','qtd_eventos_ledger','qtd_extrato_futuro']:
        print(f'{k}={resumo[k]}')
    print(f'csv={ARQUIVO_DIAGNOSTICO}')

if __name__ == '__main__':
    main()
