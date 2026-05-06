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
destinos_oficiais = getattr(getattr(ctx, 'ranking_carteira', None), 'quadro_destinos_switch', pd.DataFrame()).copy()
rank_key = {}
rank_nome = {}
score_nome = {}
if isinstance(destinos_oficiais, pd.DataFrame) and len(destinos_oficiais):
    for _, rk in destinos_oficiais.iterrows():
        k = str(rk.get('produto_key') or '').strip().lower()
        n = str(rk.get('nome') or '').strip().lower()
        r = int(rk.get('rank_destino') or 999)
        s = float(rk.get('score_final') or 0.0)
        if k and k not in rank_key:
            rank_key[k] = r
        if n and n not in rank_nome:
            rank_nome[n] = r
            score_nome[n] = s
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
    dest_key = str(row.get('produto_destino_key', '') or '').strip().lower()
    dest_nome_shadow = str(row.get('produto_destino_nome', '') or '').strip().lower()
    rank_destino = int(row.get('rank_destino') or 999)
    rank_origem = int(row.get('rank_origem') or 999)
    valor_liq = float(row.get('valor_liquido_resgatavel') or 0.0)
    ganho = float(row.get('ganho_liquido_estimado') or 0.0)
    ganho_rel = ganho / max(valor_liq, 1.0)
    rank_oficial_key = int(rank_key.get(dest_key, 999))
    rank_oficial_nome = int(rank_nome.get(dest_nome_shadow, 999))
    ganho_excepcional_usado = max(gmin * 3.0, 0.40 * max(valor_liq, 1.0))
    delta_rank = rank_destino - rank_origem
    rank_muito_inferior = rank_destino >= 20
    origem_top1 = rank_origem == 1
    rank_pior = delta_rank > 0
    if rank_destino >= 20 and ganho_rel < 0.40:
        motivo_nao_bloqueio = 'gate_deveria_bloquear_mas_nao_bloqueou'
    elif rank_destino < 20:
        motivo_nao_bloqueio = 'rank_destino_nao_muito_inferior'
    elif ganho_rel >= 0.40:
        motivo_nao_bloqueio = 'ganho_classificado_como_excepcional'
    else:
        motivo_nao_bloqueio = 'gate_nao_aplicado_por_ordem_pipeline'
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
        'rank_origem': rank_origem,
        'rank_destino': rank_destino,
        'rank_destino_oficial_por_key': rank_oficial_key,
        'rank_destino_oficial_por_nome': rank_oficial_nome,
        'delta_rank': delta_rank,
        'score_destino_oficial': float(score_nome.get(dest_nome_shadow, 0.0)),
        'score_triagem_destino': row.get('score_triagem_destino', ''),
        'carencia_dias_origem': 0,
        'carencia_dias_destino': row.get('carencia_dias_destino', ''),
        'dias_carencia_incremental': row.get('dias_carencia_incremental', ''),
        'pagamentos_na_janela_carencia': row.get('pagamentos_na_janela_carencia', ''),
        'fontes_alternativas_suficientes': row.get('fontes_alternativas_suficientes', ''),
        'ganho_liquido_estimado': row.get('ganho_liquido_estimado', ''),
        'valor_liquido_resgatavel': valor_liq,
        'ganho_relativo': ganho_rel,
        'ganho_minimo': gmin,
        'ganho_excepcional_usado': ganho_excepcional_usado,
        'limiar_excepcional_rank': 0.40,
        'rank_muito_inferior_flag': rank_muito_inferior,
        'destino_fora_top_operacional_flag': rank_destino >= 10,
        'rank_pior_flag': rank_pior,
        'origem_top1_flag': origem_top1,
        'score_switch_shadow': row.get('score_switch_shadow', ''),
        'ranking_lote': row.get('ranking_lote', ''),
        'ranking_lote_antes_gate': row.get('ranking_lote', ''),
        'candidato_promovivel_pos_gate': row.get('candidato_promovivel_pos_gate', ''),
        'recomendado_shadow': row.get('recomendado_shadow', ''),
        'recomendado_shadow_antes_gate': row.get('recomendado_shadow_antes_gate', ''),
        'recomendado_shadow_depois_gate': row.get('recomendado_shadow_depois_gate', ''),
        'bloqueado_pos_gate': row.get('bloqueado_pos_gate', ''),
        'motivo_gate_switching': row.get('motivo_gate_switching', ''),
        'motivo_nao_bloqueio_gate': motivo_nao_bloqueio,
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
