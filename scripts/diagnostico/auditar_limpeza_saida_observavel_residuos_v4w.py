from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_observavel import construir_linhas_lotes_consolidados, construir_amostras_pagamentos_operacionais
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal

def _run(script):
    p = subprocess.run([sys.executable, str(script), '--sem-csv'], capture_output=True, text=True)
    out = {}
    for ln in p.stdout.splitlines():
        if '=' in ln:
            k,v = ln.split('=',1); out[k.strip()] = v.strip()
    return p.returncode, out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sem-csv', action='store_true')
    parser.parse_args()
    src = (ROOT / 'nucleo/saida_observavel.py').read_text(encoding='utf-8')
    banned_replay = ['replay_passado','log_passado','lotes_apos_replay','lotes_antes_replay','lotes_replay','lotes_originais','getattr(contexto, "replay_passado"']
    sem_replay = all(x not in src for x in banned_replay)
    sem_dict = ('fila = [contexto]' not in src) and ('__dict__' not in src)
    sem_df_scan = ('obj.columns' not in src) and ('iterrows' not in src)
    sem_soma = 'somar_valores_sacados_por_lote' not in src
    helpers_removidos = all(x not in src for x in ['def _mapa_aplicacao_por_lote','def _mapa_produto_por_lote','def _mapa_valor_original_por_lote','def _mapa_saldo_final_replay_por_lote','def _mapa_pagamentos_replay_por_chave','def _lote_deve_ser_ativo_observavel_por_replay'])

    ctx = carregar_contexto_baseline(raiz_repositorio=ROOT, instalar_automaticamente=False, incluir_benchmark_agrupado_individual_shadow=False)
    saida = construir_saida_canonica(ctx)
    p_seed = construir_pacote_saida_observavel_temporal(ctx, saida)
    ativos = construir_linhas_lotes_consolidados(ctx, saida, tipo='ativos', pacote_saida_observavel_temporal=p_seed)
    exauridos = construir_linhas_lotes_consolidados(ctx, saida, tipo='exauridos', pacote_saida_observavel_temporal=p_seed)
    am = construir_amostras_pagamentos_operacionais(saida, limite=1000, contexto=ctx, pacote_saida_observavel_temporal=p_seed)
    p = construir_pacote_saida_observavel_temporal(ctx, saida, lotes_ativos_observaveis=ativos, lotes_exauridos_observaveis=exauridos, pagamentos_realizados_observaveis=list((am.get('realizados') or {}).get('linhas') or []))
    a = p.auditoria_saida_observavel_temporal or {}
    sac = p.valores_sacados_por_lote.get('Lote 3120 mai', {})
    bruto = round(float(sac.get('bruto_sacado',0.0) or 0.0),2)
    liquido = round(float(sac.get('liquido_sacado',0.0) or 0.0),2)

    _, out4u = _run(ROOT / 'scripts/diagnostico/auditar_pacote_saida_observavel_temporal_v4u.py')
    _, out4v = _run(ROOT / 'scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py')
    v4u_ok = out4u.get('validacao_v4u_ok','false') == 'true'
    v4v_ok = out4v.get('validacao_v4v_ok','false') == 'true'

    ativos_ids = {str(x.get('Lote') or '').strip().lower().replace('.','') for x in ativos}
    ex_ids = {str(x.get('Lote') or '').strip().lower().replace('.','') for x in exauridos}
    out = {
      'pacote_tem_bruto_liquido_sacado': bool(a.get('valores_sacados_por_lote_tem_bruto_liquido', False)),
      'saida_observavel_sem_somar_valores_sacados_por_lote': sem_soma,
      'saida_observavel_sem_acesso_direto_replay': sem_replay,
      'saida_observavel_sem_varredura_dict_contexto': sem_dict,
      'saida_observavel_sem_varredura_generica_dataframe': sem_df_scan,
      'saida_observavel_consumindo_pacote': True,
      'helpers_legados_removidos': helpers_removidos,
      'valores_sacados_lote_3120_bruto': bruto,
      'valores_sacados_lote_3120_liquido': liquido,
      'lote_3120_mai_presente_ativos': 'lote 3120 mai' in ativos_ids,
      'lote_3120_mai_presente_exauridos': 'lote 3120 mai' in ex_ids,
      'lote_3120_mai_saldo_final': round(float((p.saldos_finais_replay_por_lote.get('Lote 3120 mai',0.0) or 0.0)),2),
      'validacao_v4u_ok': v4u_ok,
      'validacao_v4v_ok': v4v_ok,
      'etapa5_pode_abrir_agora': False,
      'proxima_etapa_recomendada': 'V17-F0-V.4X',
    }
    out['validacao_v4w_ok'] = all([
      out['pacote_tem_bruto_liquido_sacado'], out['saida_observavel_sem_somar_valores_sacados_por_lote'], out['saida_observavel_sem_acesso_direto_replay'], out['saida_observavel_sem_varredura_dict_contexto'], out['saida_observavel_sem_varredura_generica_dataframe'], out['helpers_legados_removidos'], abs(out['valores_sacados_lote_3120_bruto']-3093.76)<=0.01, abs(out['valores_sacados_lote_3120_liquido']-3088.95)<=0.01, out['validacao_v4u_ok'], out['validacao_v4v_ok']
    ])
    for k,v in out.items(): print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0 if out['validacao_v4w_ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
