from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execucao direta
    from _bootstrap import RAIZ

from datetime import timedelta
from pathlib import Path

from nucleo.avaliador_cenarios_conjuntos_v1 import avaliar_cenarios_conjuntos_v1
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import construir_estado_global_recorte_curto_v117, simular_cenario_eventos_v1

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'SIMULACAO_CENTRAL_CONTROLADA_HORIZONTE_LONGO_V124.md'
HORIZONTES = (
    {'dias': 60, 'limite_pagamentos': 25},
    {'dias': 90, 'limite_pagamentos': 35},
    {'dias': 120, 'limite_pagamentos': 50},
)


def _melhores_por_lote(acoes: list[dict]) -> list[dict]:
    melhores: dict[str, dict] = {}
    for acao in acoes:
        if acao.get('tipo_acao') != 'switching_simples' or not acao.get('elegivel'):
            continue
        lote = str(acao.get('lote_origem_id') or '')
        if not lote:
            continue
        atual = melhores.get(lote)
        if atual is None or float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) > float(atual.get('ganho_terminal_economico_minimo_estimado') or 0.0):
            melhores[lote] = acao
    return sorted(melhores.values(), key=lambda x: float(x.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)


def _rodar_horizonte(*, dias: int, limite_pagamentos: int, raiz: Path) -> dict:
    contexto = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
    data_inicio = contexto.execucao.data_referencia
    data_fim = data_inicio + timedelta(days=dias)
    config = contexto.pacote_config.conteudo
    estado = construir_estado_global_recorte_curto_v117(contexto, data_inicio=data_inicio, data_fim=data_fim, limite_pagamentos=limite_pagamentos)
    horizonte = {'data_inicio': data_inicio.isoformat(), 'data_fim': data_fim.isoformat()}
    plano = planejar_switching_temporal_v1(estado_global=estado, config=config, horizonte_planejamento=horizonte, filtros_eventos=None, limite_candidatos_por_data=200)
    candidatos = _melhores_por_lote(plano.get('acoes_candidatas', []))
    cenarios = [{'cenario_id': 'baseline_sem_switching', 'descricao': 'Sem switching temporal no cenário conjunto.', 'eventos': [], 'acao_referencia': {}}]
    for idx, acao in enumerate(candidatos[:6], start=1):
        cenarios.append({'cenario_id': f'switching_controlado_top{idx}', 'descricao': f"{acao.get('lote_origem_id')} -> {acao.get('produto_destino')}", 'eventos': [acao], 'acao_referencia': acao})
    simulacoes = {}
    cenarios_avaliados = []
    for cenario in cenarios:
        simulacao = simular_cenario_eventos_v1(estado_inicial=estado, eventos_candidatos=cenario['eventos'], config=config, horizonte=horizonte)
        simulacoes[cenario['cenario_id']] = simulacao
        cenarios_avaliados.append({'cenario_id': cenario['cenario_id'], 'descricao': cenario['descricao'], 'status': simulacao.get('status'), 'metrica_central': simulacao.get('metrica_central') or {}, 'patrimonio_liquido_terminal_proxy': simulacao.get('patrimonio_liquido_terminal_proxy'), 'ganho_switching_total': simulacao.get('ganho_switching_total')})
    avaliacao = avaliar_cenarios_conjuntos_v1(cenarios_avaliados, config=config)
    ranking = avaliacao.get('ranking_cenarios') or []
    baseline = simulacoes['baseline_sem_switching']
    controlados = []
    for item in ranking:
        if item['cenario_id'] == 'baseline_sem_switching':
            continue
        simulacao = simulacoes[item['cenario_id']]
        acao = next((c.get('acao_referencia') for c in cenarios if c['cenario_id'] == item['cenario_id']), {}) or {}
        metrica = simulacao.get('metrica_central') or {}
        base = baseline.get('metrica_central') or {}
        delta_perda = round(float(metrica.get('perda_patrimonio_liquido_terminal') or 0.0) - float(base.get('perda_patrimonio_liquido_terminal') or 0.0), 2)
        delta_deficit = round(float(metrica.get('deficit_liquido_total') or 0.0) - float(base.get('deficit_liquido_total') or 0.0), 2)
        delta_protegida = round(float(metrica.get('violacoes_protegida') or 0.0) - float(base.get('violacoes_protegida') or 0.0), 2)
        delta_pat = round(float(simulacao.get('patrimonio_liquido_terminal_proxy') or 0.0) - float(baseline.get('patrimonio_liquido_terminal_proxy') or 0.0), 2)
        vencedor = item == (avaliacao.get('melhor_cenario') or {})
        material = vencedor and (abs(delta_perda) >= 1.0 or abs(delta_deficit) >= 1.0 or abs(delta_protegida) >= 1.0 or abs(delta_pat) >= 1.0)
        controlados.append({'cenario_id': item['cenario_id'], 'descricao': item['descricao'], 'vetor_lexicografico': item['vetor_lexicografico'], 'lote_origem_id': acao.get('lote_origem_id'), 'produto_destino': acao.get('produto_destino'), 'ganho_planejador': float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0), 'delta_perda_terminal_vs_baseline': delta_perda, 'delta_deficit_vs_baseline': delta_deficit, 'delta_violacoes_protegida_vs_baseline': delta_protegida, 'delta_patrimonio_proxy_vs_baseline': delta_pat, 'continua_vencedor_central': vencedor, 'vitoria_material': material, 'patrimonio_liquido_terminal_proxy': simulacao.get('patrimonio_liquido_terminal_proxy')})
    return {'dias': dias, 'data_inicio': data_inicio.isoformat(), 'data_fim': data_fim.isoformat(), 'limite_pagamentos': limite_pagamentos, 'quantidade_pagamentos_no_recorte': len(estado.get('pagamentos_futuros') or []), 'quantidade_destinos_elegiveis': plano.get('quantidade_destinos_elegiveis_considerados'), 'quantidade_switchings_elegiveis_no_planejador': plano.get('quantidade_candidatos_elegiveis_switching'), 'melhores_candidatos_planejador': candidatos, 'simulacoes': simulacoes, 'avaliacao': avaliacao, 'cenarios_controlados': controlados}


def _formatar_relatorio(blocos: list[dict]) -> str:
    linhas = ['# Simulação central controlada em horizonte mais longo — V124', '', '- Objetivo: rerodar a simulação central controlada em horizonte mais longo usando o ranking Carteira-only estabilizado como fonte de destinos do `planejador_switching_temporal_v1`.', '- Escopo: comparação individual entre baseline sem switching e o melhor destino positivo de cada lote no planejador, sem abrir combinações amplas.', '- Fonte de destinos: `contexto_baseline.ranking_carteira.quadro_destinos_switch`.', '', '## Síntese executiva', '']
    for bloco in blocos:
        melhor = bloco.get('avaliacao', {}).get('melhor_cenario') or {}
        linhas.append(f"- Horizonte de **{bloco['dias']} dias**: melhor cenário = **{melhor.get('cenario_id')}** ({melhor.get('descricao')}).")
    linhas.extend(['', '## Resultados por horizonte', ''])
    for bloco in blocos:
        melhor = bloco.get('avaliacao', {}).get('melhor_cenario') or {}
        ranking = bloco.get('avaliacao', {}).get('ranking_cenarios') or []
        linhas.extend([f"### Horizonte {bloco['dias']} dias", f"- Janela: {bloco['data_inicio']} → {bloco['data_fim']}", f"- Pagamentos no recorte: {bloco['quantidade_pagamentos_no_recorte']}", f"- Destinos elegíveis considerados: {bloco['quantidade_destinos_elegiveis']}", f"- Switchings elegíveis no planejador: {bloco['quantidade_switchings_elegiveis_no_planejador']}", f"- Melhor cenário central: {melhor.get('cenario_id')} ({melhor.get('descricao')})", f"- Vetor do melhor cenário: {melhor.get('vetor_lexicografico')}", '', '#### Melhores candidatos do planejador (um por lote)', ''])
        candidatos = bloco.get('melhores_candidatos_planejador') or []
        if not candidatos:
            linhas.extend(['- Nenhum candidato positivo no planejador para este horizonte.', ''])
        else:
            for acao in candidatos[:6]:
                linhas.append(f"- {acao.get('lote_origem_id')} → {acao.get('produto_destino')}: ganho planejador = {acao.get('ganho_terminal_economico_minimo_estimado')}")
            linhas.append('')
        linhas.extend(['#### Ranking da simulação central controlada', ''])
        for item in ranking:
            simulacao = bloco['simulacoes'][item['cenario_id']]
            linhas.extend([f"- {item['cenario_id']}: {item['descricao']}", f"  - vetor = {item['vetor_lexicografico']}", f"  - patrimônio líquido terminal proxy = {simulacao.get('patrimonio_liquido_terminal_proxy')}", f"  - pagamentos cobertos = {len(simulacao.get('pagamentos_cobertos', []))}", f"  - pagamentos sem cobertura = {len(simulacao.get('pagamentos_sem_cobertura', []))}"])
        linhas.extend(['', '#### Leitura dos switchings controlados', ''])
        for item in bloco.get('cenarios_controlados', []):
            linhas.extend([f"- {item['lote_origem_id']} → {item['produto_destino']}", f"  - continua vencedor central = {item['continua_vencedor_central']}", f"  - vitória material = {item['vitoria_material']}", f"  - ganho no planejador = {item['ganho_planejador']}", f"  - Δ perda terminal vs baseline = {item['delta_perda_terminal_vs_baseline']}", f"  - Δ déficit vs baseline = {item['delta_deficit_vs_baseline']}", f"  - Δ violações protegida vs baseline = {item['delta_violacoes_protegida_vs_baseline']}", f"  - Δ patrimônio proxy vs baseline = {item['delta_patrimonio_proxy_vs_baseline']}"])
        linhas.append('')
    linhas.extend(['## Conclusões', '', '- Após a correção do ranqueamento, os destinos vencedores do planejador deixam de ser Tesouro e passam a ser principalmente `CDB XP 150%` e `Mercado Pago Cofrinho 120% CDI (Meli+)` no teste controlado.', '- Porém, ganho positivo no planejador não implica vitória no cenário conjunto.', '- O teste correto desta etapa é identificar quais switchings ainda vencem quando pagamentos, déficit e violação de PROTEGIDA entram simultaneamente na métrica central.', '- Quando a vitória central ocorre apenas por centésimos e sem ganho material nas métricas prioritárias, ela deve ser tratada como marginal.', ''])
    return '\n'.join(linhas).strip() + '\n'


def main() -> int:
    raiz = Path(RAIZ)
    blocos = [_rodar_horizonte(raiz=raiz, **cfg) for cfg in HORIZONTES]
    texto = _formatar_relatorio(blocos)
    RELATORIO.write_text(texto, encoding='utf-8')
    print(texto)
    print(f'relatorio_salvo_em={RELATORIO}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
