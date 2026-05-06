from pathlib import Path
import sys
import pandas as pd
RAIZ=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.config_utils import obter_config

ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
saida=construir_saida_canonica(ctx)
shadow=ctx.switching_economico_shadow
p=shadow.plano_shadow.copy();q=shadow.quadro_oportunidades.copy();m=shadow.quadro_melhores_oportunidades.copy()
dest=getattr(ctx.ranking_carteira,'quadro_destinos_switch',pd.DataFrame()).copy()
rank_key={str(r.get('produto_key') or '').lower(): int(r.get('rank_destino') or 999) for _,r in dest.iterrows()} if len(dest) else {}
rank_nome={str(r.get('nome') or '').lower(): int(r.get('rank_destino') or 999) for _,r in dest.iterrows()} if len(dest) else {}
score_nome={str(r.get('nome') or '').lower(): float(r.get('score_final') or 0.0) for _,r in dest.iterrows()} if len(dest) else {}
gmin=float(obter_config(ctx.pacote_config.conteudo,'switching_shadow','ganho_minimo_absoluto',padrao=5.0) or 5.0)
rows=[]
for s in saida.switchings:
 lote=str(s.get('Lote origem') or '')
 fonte=p[p['lote_id'].astype(str)==lote]
 if len(fonte)==0: fonte=m[m['lote_id'].astype(str)==lote]
 if len(fonte)==0: fonte=q[q['lote_id'].astype(str)==lote]
 r=fonte.iloc[0] if len(fonte) else {}
 rank_dest=int(r.get('rank_destino') or 999); rank_ori=int(r.get('rank_origem') or 999)
 ganho=float(r.get('ganho_liquido_estimado') or 0.0); vl=float(r.get('valor_liquido_resgatavel') or 0.0)
 gr=ganho/max(vl,1.0)
 limiar=0.40
 motivo='ganho_classificado_como_excepcional' if gr>=limiar else 'gate_deveria_bloquear_mas_nao_bloqueou'
 rows.append({
 'lote_id':lote,'produto_origem_nome':r.get('produto_origem_nome',''),'produto_origem_key':r.get('produto_origem_key',''),'produto_destino_nome':r.get('produto_destino_nome',''),'produto_destino_key':r.get('produto_destino_key',''),'produto_destino_nome_saida':s.get('Destino',''),'produto_destino_nome_shadow':r.get('produto_destino_nome',''),'rank_origem':rank_ori,'rank_destino':rank_dest,'rank_destino_oficial_por_key':rank_key.get(str(r.get('produto_destino_key') or '').lower(),999),'rank_destino_oficial_por_nome':rank_nome.get(str(r.get('produto_destino_nome') or '').lower(),999),'score_destino_oficial':score_nome.get(str(r.get('produto_destino_nome') or '').lower(),0.0),'score_triagem_destino':r.get('score_triagem_destino',''),'valor_liquido_resgatavel':vl,'riqueza_manter_horizonte':r.get('riqueza_manter_horizonte',''),'riqueza_switch_horizonte':r.get('riqueza_switch_horizonte',''),'ganho_liquido_estimado':ganho,'ganho_relativo':gr,'ganho_minimo':gmin,'limiar_excepcional_rank':limiar,'motivo_nao_bloqueio_gate':motivo,'taxa_base_cdi_destino':r.get('taxa_base_cdi',''),'taxa_bonus_cdi_destino':r.get('taxa_bonus_cdi',''),'dias_bonus_destino':r.get('dias_bonus',''),'semantica_taxa_base_destino':r.get('semantica_taxa_base',''),'tipo_produto_destino':r.get('tipo_produto',''),'indexador_destino':r.get('indexador',''),'prazo_dias_destino':r.get('prazo_dias_destino',''),'carencia_dias_destino':r.get('carencia_dias_destino',''),'regime_taxa_destino':r.get('regime_taxa_destino',''),'isento_ir_destino':r.get('isento_ir_destino',''),'fgc_destino':r.get('fgc_destino',''),'taxa_dia_modelo_usada':getattr(ctx.calendario_financeiro,'taxa_dia_base',''),'data_referencia':r.get('data_referencia',''),'data_horizonte':r.get('data_horizonte',''),'candidato_promovivel_pos_gate':r.get('candidato_promovivel_pos_gate',''),'recomendado_shadow':r.get('recomendado_shadow',''),'bloqueado_pos_gate':r.get('bloqueado_pos_gate',''),'motivo_gate_switching':r.get('motivo_gate_switching','')
 })

df=pd.DataFrame(rows)
out=RAIZ/'saidas'/'diagnostico'/'auditoria_origem_switchings_promovidos.csv'
out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(out,index=False)
print('plano_shadow_linhas=',len(p))
print('saida_switchings_linhas=',len(saida.switchings))
print('arquivo=',out)
print(df[['lote_id','rank_destino','ganho_relativo','semantica_taxa_base_destino','tipo_produto_destino','indexador_destino','motivo_nao_bloqueio_gate']].to_string(index=False) if len(df) else 'sem_linhas_promovidas')
