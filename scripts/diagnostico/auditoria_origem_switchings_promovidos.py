from pathlib import Path
import sys
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.config_utils import obter_config

ctx = carregar_contexto_baseline(
    raiz_repositorio=RAIZ,
    instalar_automaticamente=False,
    incluir_benchmark_agrupado_individual_shadow=False,
    incluir_benchmark_runner_futuro_shadow=False,
    incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
)
saida = construir_saida_canonica(ctx)
shadow = ctx.switching_economico_shadow
q = shadow.quadro_oportunidades.copy()
m = shadow.quadro_melhores_oportunidades.copy()
p = shadow.plano_shadow.copy()
gmin = float(obter_config(ctx.pacote_config.conteudo, 'switching_shadow', 'ganho_minimo_absoluto', padrao=5.0) or 5.0)
linhas = []
for item in saida.switchings:
    lote = str(item.get('Lote origem') or '')
    destino_saida = str(item.get('Produto destino switching') or item.get('Destino') or '')
    sub_p = p[p['lote_id'].astype(str) == lote]
    sub_m = m[m['lote_id'].astype(str) == lote]
    sub_q = q[q['lote_id'].astype(str) == lote]
    if len(sub_p):
        origem_df, fonte = 'plano_shadow', sub_p
    elif len(sub_m):
        origem_df, fonte = 'quadro_melhores_oportunidades', sub_m
    else:
        origem_df, fonte = 'quadro_oportunidades', sub_q
    row = fonte.iloc[0] if len(fonte) else {}
    linhas.append({
        'origem_exata_da_linha': 'saida_canonica.switchings',
        'dataframe_origem': origem_df,
        'indice_origem': int(fonte.index[0]) if len(fonte) else -1,
        'lote_id': lote,
        'produto_origem_nome': row.get('produto_origem_nome', ''),
        'produto_origem_key': row.get('produto_origem_key', ''),
        'produto_destino_nome_shadow': row.get('produto_destino_nome', ''),
        'produto_destino_nome_saida': destino_saida,
        'produto_destino_key': row.get('produto_destino_key', ''),
        'rank_origem_oficial': row.get('rank_origem', ''),
        'rank_destino_oficial': row.get('rank_destino', ''),
        'carencia_dias_origem': 0,
        'carencia_dias_destino': row.get('carencia_dias_destino', ''),
        'dias_carencia_incremental': row.get('dias_carencia_incremental', ''),
        'pagamentos_na_janela_carencia': row.get('pagamentos_na_janela_carencia', ''),
        'fontes_alternativas_suficientes': row.get('fontes_alternativas_suficientes', ''),
        'ganho_liquido_estimado': row.get('ganho_liquido_estimado', ''),
        'ganho_minimo': gmin,
        'score_switch_shadow': row.get('score_switch_shadow', ''),
        'ranking_lote': row.get('ranking_lote', ''),
        'recomendado_shadow': row.get('recomendado_shadow', ''),
        'recomendado_shadow_antes_gate': row.get('recomendado_shadow_antes_gate', ''),
        'recomendado_shadow_depois_gate': row.get('recomendado_shadow_depois_gate', ''),
        'bloqueado_pos_gate': row.get('bloqueado_pos_gate', ''),
        'motivo_gate_switching': row.get('motivo_gate_switching', ''),
        'status_exportado_para_saida_canonica': item.get('Status', ''),
        'status_exportado_para_planilha': item.get('Status', ''),
    })

df = pd.DataFrame(linhas)
out = RAIZ / 'saidas' / 'diagnostico' / 'auditoria_origem_switchings_promovidos.csv'
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f'plano_shadow_linhas={len(p)}')
print(f'saida_switchings_linhas={len(saida.switchings)}')
print(f'arquivo={out}')
print(df[['lote_id','dataframe_origem','produto_destino_nome_shadow','produto_destino_nome_saida','bloqueado_pos_gate','motivo_gate_switching','recomendado_shadow']].to_string(index=False))
