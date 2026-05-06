from pathlib import Path
import sys, pandas as pd
RAIZ=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(RAIZ))
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.config_utils import obter_config
ctx=carregar_contexto_baseline(raiz_repositorio=RAIZ,instalar_automaticamente=False,incluir_benchmark_agrupado_individual_shadow=False,incluir_benchmark_runner_futuro_shadow=False,incluir_auditoria_primeira_quebra_runner_futuro_shadow=False)
saida=construir_saida_canonica(ctx); shadow=ctx.switching_economico_shadow
p=shadow.plano_shadow.copy(); q=shadow.quadro_oportunidades.copy(); rk=getattr(ctx.ranking_carteira,'quadro_destinos_switch',pd.DataFrame()).copy()
rank_key={str(r.get('produto_key') or '').strip().lower():int(r.get('rank_destino') or 999) for _,r in rk.iterrows()}
rank_nome={str(r.get('nome') or '').strip().lower():int(r.get('rank_destino') or 999) for _,r in rk.iterrows()}
gmin=float(obter_config(ctx.pacote_config.conteudo,'switching_shadow','ganho_minimo_absoluto',padrao=5.0) or 5.0)
linhas=[]
for it in saida.switchings:
 lote=str(it.get('Lote origem') or '')
 f=p[p['lote_id'].astype(str)==lote]
 r=f.iloc[0] if len(f) else {}
 dk=str(r.get('produto_destino_key') or '').strip().lower(); dn=str(r.get('produto_destino_nome') or '').strip().lower()
 vr=float(r.get('valor_liquido_resgatavel') or 0.0); g=float(r.get('ganho_liquido_estimado') or 0.0); gr=g/max(vr,1.0)
 linhas.append({'lote_id':lote,'produto_origem_nome':r.get('produto_origem_nome',''),'produto_origem_key':r.get('produto_origem_key',''),'produto_destino_nome':r.get('produto_destino_nome',''),'produto_destino_key':r.get('produto_destino_key',''),'produto_destino_nome_saida':it.get('Destino',''),'produto_destino_nome_shadow':r.get('produto_destino_nome',''),'rank_origem':r.get('rank_origem',''),'rank_destino':r.get('rank_destino',''),'rank_destino_oficial_por_key':rank_key.get(dk,999),'rank_destino_oficial_por_nome':rank_nome.get(dn,999),'score_destino_oficial':r.get('score_destino_oficial',''),'score_triagem_destino':r.get('score_triagem_destino',''),'valor_liquido_resgatavel':vr,'riqueza_manter_horizonte':r.get('riqueza_manter_horizonte',''),'riqueza_switch_horizonte':r.get('riqueza_switch_horizonte',''),'ganho_liquido_estimado':g,'ganho_relativo':gr,'ganho_minimo':gmin,'limiar_excepcional_rank':0.80,'motivo_nao_bloqueio_gate':'ganho_classificado_como_excepcional' if gr>=0.80 else 'gate_deveria_bloquear_mas_nao_bloqueou','taxa_base_cdi_destino':r.get('taxa_base_cdi',''),'taxa_bonus_cdi_destino':r.get('taxa_bonus_cdi',''),'dias_bonus_destino':r.get('dias_bonus',''),'semantica_taxa_base_destino':r.get('semantica_taxa_base_destino',''),'tipo_produto_destino':r.get('tipo_produto_destino',''),'indexador_destino':r.get('indexador_destino',''),'prazo_dias_destino':r.get('prazo_dias_destino',''),'carencia_dias_destino':r.get('carencia_dias_destino',''),'regime_taxa_destino':r.get('regime_taxa_destino',''),'fgc_destino':r.get('fgc_destino',''),'origem_parametros_destino':r.get('origem_parametros_destino',''),'data_referencia':r.get('data_referencia',''),'data_horizonte':r.get('data_horizonte',''),'candidato_promovivel_pos_gate':r.get('candidato_promovivel_pos_gate',''),'recomendado_shadow':r.get('recomendado_shadow',''),'bloqueado_pos_gate':r.get('bloqueado_pos_gate',''),'motivo_gate_switching':r.get('motivo_gate_switching','')})
out=RAIZ/'saidas/diagnostico/auditoria_origem_switchings_promovidos.csv'; out.parent.mkdir(parents=True,exist_ok=True)
pd.DataFrame(linhas).to_csv(out,index=False)
if len(p)==0:
    cols=['lote_id','produto_origem_nome','produto_destino_nome','produto_destino_key','rank_origem','rank_destino','score_destino_oficial','semantica_taxa_base_destino','tipo_produto_destino','elegivel_shadow','motivo_bloqueio_shadow','bloqueado_pos_gate','motivo_gate_switching','candidato_promovivel_pos_gate','recomendado_shadow','ganho_liquido_estimado','score_switch_shadow']
    bloqueados=q.copy()
    for c in cols:
        if c not in bloqueados.columns:
            bloqueados[c]=''
    bloqueados=bloqueados[cols]
    bloqueados.to_csv(RAIZ/'saidas/diagnostico/auditoria_switchings_bloqueados.csv',index=False)
print(f'plano_shadow_linhas={len(p)}'); print(f'saida_switchings_linhas={len(saida.switchings)}'); print(f'arquivo={out}')
