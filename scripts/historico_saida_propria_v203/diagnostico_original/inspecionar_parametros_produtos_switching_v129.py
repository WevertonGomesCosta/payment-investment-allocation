from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path
import json

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _consumir_componentes,
    _coerce_date,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'AUDITORIA_PARAMETROS_PRODUTOS_SWITCHING_V129.md'
JSON_OUT = Path(RAIZ) / 'saidas' / 'operacional' / 'auditoria_parametros_produtos_switching_v129.json'
TOP_DESTINOS = 5
JANELA_INICIO = date(2026, 4, 30)
JANELA_FIM = date(2026, 5, 6)


def _carregar_estado_completo(contexto):
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=contexto.execucao.data_referencia)
    data_fim = max(pagamentos['data']) if len(pagamentos) else contexto.execucao.data_referencia
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=contexto.execucao.data_referencia,
        data_fim=data_fim,
        limite_pagamentos=max(len(pagamentos), 1),
    )
    return estado, data_fim, len(pagamentos)


def _gerar_snapshots_baseline(estado_inicial, config):
    estado = deepcopy(estado_inicial)
    pagamentos = sorted(
        [deepcopy(dict(item)) for item in estado.get('pagamentos_futuros', [])],
        key=lambda item: (
            _coerce_date(item.get('data')),
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )
    inicio = _coerce_date(estado.get('data_referencia'))
    fim = _coerce_date(estado.get('data_fim_recorte'))
    pagamentos_por_data = defaultdict(list)
    for pagamento in pagamentos:
        pagamentos_por_data[_coerce_date(pagamento.get('data'))].append(pagamento)
    snapshots = {}
    dia = inicio
    while dia <= fim:
        estado['data_evento_corrente'] = dia
        snapshots[dia.isoformat()] = deepcopy(estado)
        for pagamento in pagamentos_por_data.get(dia, []):
            estado_para_pagamento = deepcopy(estado)
            estado_para_pagamento['dias_horizonte_terminal'] = max((fim - dia).days, 0)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_pagamento,
                config=config,
                plano_switching_candidato=None,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            _consumir_componentes(estado, alocacao.get('componentes_escolhidos') or [])
        dia += timedelta(days=1)
    return snapshots


def _ticket_ok(valor_total: float, acao: dict, *, individual: bool) -> tuple[bool, str | None]:
    minimo = float(acao.get('aplicacao_minima_destino') or 0.0)
    maximo = float(acao.get('aplicacao_maxima_destino') or 0.0)
    somente_combo = bool(acao.get('somente_combo_destino') or False)
    if somente_combo:
        return False, 'somente_combo_nao_modelado'
    if individual and not bool(acao.get('atende_ticket_individual', True)):
        return False, str(acao.get('motivo_bloqueio_ticket_individual') or 'ticket_individual_invalido')
    if minimo > 0.0 and valor_total + 1e-9 < minimo:
        return False, 'abaixo_da_aplicacao_minima'
    if maximo > 0.0 and valor_total - 1e-9 > maximo:
        return False, 'acima_da_aplicacao_maxima'
    return True, None


def _acoes_top5(plano: dict) -> list[dict]:
    acoes = []
    for acao in plano.get('acoes_candidatas', []):
        if str(acao.get('tipo_acao') or '') not in {'switching_simples', 'aporte_nao_aportado'}:
            continue
        if int(acao.get('rank_destino_sugerido') or 999) > TOP_DESTINOS:
            continue
        if float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) <= 0.0:
            continue
        acoes.append(deepcopy(acao))
    return acoes


def _cenarios_parametrizados(acoes: list[dict]) -> list[dict]:
    cenarios = []
    # individuais
    for acao in acoes:
        valor_total = round(float(acao.get('valor_migrado_estimado') or acao.get('valor_liquido_resgatavel') or 0.0), 2)
        ok, motivo = _ticket_ok(valor_total, acao, individual=True)
        if not ok:
            continue
        evento = deepcopy(acao)
        evento['fracao_lote'] = 1.0
        cenarios.append({
            'familia': 'individual_integral_parametrizado',
            'rotulo': f"{acao.get('lote_origem_id')} -> {acao.get('produto_destino')}",
            'produto_destino': acao.get('produto_destino'),
            'valor_total_alocado': valor_total,
            'eventos': [evento],
        })
    # agrupados por destino
    por_destino = defaultdict(list)
    for acao in acoes:
        por_destino[str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')].append(deepcopy(acao))
    for _, grupo in por_destino.items():
        grupo = sorted(grupo, key=lambda a: float(a.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)
        if len(grupo) < 2:
            continue
        for tamanho in range(2, len(grupo) + 1):
            for combo in combinations(grupo, tamanho):
                valor_total = round(sum(float(a.get('valor_migrado_estimado') or a.get('valor_liquido_resgatavel') or 0.0) for a in combo), 2)
                ok, motivo = _ticket_ok(valor_total, combo[0], individual=False)
                if not ok:
                    continue
                eventos = []
                rotulos = []
                for acao in combo:
                    evento = deepcopy(acao)
                    evento['fracao_lote'] = 1.0
                    eventos.append(evento)
                    rotulos.append(str(acao.get('lote_origem_id') or ''))
                cenarios.append({
                    'familia': 'agrupado_integral_parametrizado',
                    'rotulo': f"{' + '.join(rotulos)} -> {combo[0].get('produto_destino')}",
                    'produto_destino': combo[0].get('produto_destino'),
                    'valor_total_alocado': valor_total,
                    'eventos': eventos,
                })
    return cenarios


def _comparar_com_baseline(sim: dict, baseline: dict) -> dict:
    metrica = sim.get('metrica_central') or {}
    base = baseline.get('metrica_central') or {}
    vetor = vetor_lexicografico_central(metrica)
    vetor_base = vetor_lexicografico_central(base)
    delta_perda = round(float(metrica.get('perda_patrimonio_liquido_terminal') or 0.0) - float(base.get('perda_patrimonio_liquido_terminal') or 0.0), 2)
    delta_deficit = round(float(metrica.get('deficit_liquido_total') or 0.0) - float(base.get('deficit_liquido_total') or 0.0), 2)
    delta_protegida = round(float(metrica.get('violacoes_protegida') or 0.0) - float(base.get('violacoes_protegida') or 0.0), 2)
    delta_pat = round(float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0) - float(baseline.get('patrimonio_liquido_terminal_proxy') or 0.0), 2)
    vencedor = vetor < vetor_base
    material = vencedor and (abs(delta_perda) >= 1.0 or abs(delta_deficit) >= 1.0 or abs(delta_protegida) >= 1.0 or abs(delta_pat) >= 1.0)
    return {
        'vetor_lexicografico': vetor,
        'vetor_baseline': vetor_base,
        'continua_vencedor_central': vencedor,
        'vitoria_material': material,
        'delta_perda_terminal_vs_baseline': delta_perda,
        'delta_deficit_vs_baseline': delta_deficit,
        'delta_violacoes_protegida_vs_baseline': delta_protegida,
        'delta_patrimonio_proxy_vs_baseline': delta_pat,
    }


def _resumir_top5(contexto) -> list[dict]:
    qd = contexto.ranking_carteira.quadro_destinos_switch.copy().head(TOP_DESTINOS)
    cols = ['rank_destino', 'nome', 'aplicacao_minima', 'aplicacao_maxima', 'retorno_anual_proxy', 'liquidez_dias', 'carencia_dias']
    return qd[cols].to_dict('records')


def _auditar_invalidos_xp(snapshot_0430: dict, config: dict, horizonte: dict) -> list[dict]:
    plano = planejar_switching_temporal_v1(
        estado_global=deepcopy(snapshot_0430),
        config=config,
        horizonte_planejamento=horizonte,
        filtros_eventos=None,
        limite_candidatos_por_data=300,
    )
    acoes = [a for a in plano.get('acoes_candidatas', []) if a.get('produto_destino') == 'CDB XP 150%']
    mapa = {str(a.get('lote_origem_id')): a for a in acoes}
    combos = [
        ['Lote 3000 mar. V'],
        ['Lote 3000 mar. B', 'Lote 3000 mar. V'],
        ['Lote 3000 mar. V', 'Lote 8500 mar.'],
    ]
    saida = []
    for combo in combos:
        subset = [mapa[c] for c in combo if c in mapa]
        total = round(sum(float(a.get('valor_migrado_estimado') or a.get('valor_liquido_resgatavel') or 0.0) for a in subset), 2)
        minimo = float(subset[0].get('aplicacao_minima_destino') or 0.0) if subset else 0.0
        saida.append({
            'rotulo': ' + '.join(combo),
            'destino': 'CDB XP 150%',
            'valor_total_migrado': total,
            'aplicacao_minima_destino': minimo,
            'ticket_valido': bool(total + 1e-9 >= minimo if minimo > 0 else True),
        })
    return saida


def executar():
    contexto = carregar_contexto_baseline(raiz_repositorio=Path(RAIZ), instalar_automaticamente=False)
    config = contexto.pacote_config.conteudo
    estado_base, data_fim, qtd_pagamentos = _carregar_estado_completo(contexto)
    horizonte = {'data_inicio': contexto.execucao.data_referencia.isoformat(), 'data_fim': data_fim.isoformat()}
    snapshots = _gerar_snapshots_baseline(estado_base, config)

    top5 = _resumir_top5(contexto)
    invalidos_xp = _auditar_invalidos_xp(snapshots['2026-04-30'], config, horizonte)

    resultados = []
    dia = JANELA_INICIO
    while dia <= JANELA_FIM:
        estado_dia = deepcopy(snapshots[dia.isoformat()])
        estado_dia['data_evento_corrente'] = dia
        baseline_dia = simular_cenario_eventos_v1(estado_inicial=estado_dia, eventos_candidatos=[], config=config, horizonte=horizonte)
        plano = planejar_switching_temporal_v1(
            estado_global=estado_dia,
            config=config,
            horizonte_planejamento=horizonte,
            filtros_eventos=None,
            limite_candidatos_por_data=300,
        )
        acoes = _acoes_top5(plano)
        cenarios = _cenarios_parametrizados(acoes)
        for cenario in cenarios:
            sim = simular_cenario_eventos_v1(estado_inicial=estado_dia, eventos_candidatos=cenario['eventos'], config=config, horizonte=horizonte)
            comp = _comparar_com_baseline(sim, baseline_dia)
            resultados.append({
                'data_solicitada': dia.isoformat(),
                'familia': cenario['familia'],
                'rotulo': cenario['rotulo'],
                'produto_destino': cenario['produto_destino'],
                'valor_total_alocado': cenario['valor_total_alocado'],
                'eventos': [
                    {
                        'lote_origem_id': e.get('lote_origem_id'),
                        'produto_destino': e.get('produto_destino'),
                        'rank_destino_sugerido': e.get('rank_destino_sugerido'),
                        'valor_migrado_estimado': e.get('valor_migrado_estimado'),
                        'aplicacao_minima_destino': e.get('aplicacao_minima_destino'),
                        'aplicacao_maxima_destino': e.get('aplicacao_maxima_destino'),
                    }
                    for e in cenario['eventos']
                ],
                'patrimonio_liquido_terminal_proxy': float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0),
                **comp,
            })
        dia += timedelta(days=1)

    vencedores = [r for r in resultados if r['continua_vencedor_central']]
    vencedores_ordenados = sorted(vencedores, key=lambda r: (0 if r['vitoria_material'] else 1, r['vetor_lexicografico'], -r['delta_patrimonio_proxy_vs_baseline']))
    payload = {
        'janela_inicio': JANELA_INICIO.isoformat(),
        'janela_fim': JANELA_FIM.isoformat(),
        'top5_destinos': top5,
        'invalidos_xp_v128': invalidos_xp,
        'resultados': resultados,
        'vencedores': vencedores_ordenados,
    }
    JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    linhas = [
        '# Auditoria de parâmetros de produtos no switching — V129',
        '',
        '- Objetivo: verificar se o switching diário está respeitando os parâmetros dos produtos de destino, com foco em ticket mínimo/máximo e nos 5 destinos mais bem ranqueados da Carteira.',
        f'- Janela auditada: {JANELA_INICIO.isoformat()} até {JANELA_FIM.isoformat()}.',
        '',
        '## Top 5 destinos ranqueados considerados',
        '',
        '| Rank | Produto | Aplicação mínima | Aplicação máxima | Retorno proxy aa | Liquidez | Carência |',
        '|---:|---|---:|---:|---:|---:|---:|',
    ]
    for item in top5:
        linhas.append(f"| {item['rank_destino']} | {item['nome']} | {item['aplicacao_minima']:.2f} | {item['aplicacao_maxima']:.2f} | {item['retorno_anual_proxy']:.2f} | {item['liquidez_dias']} | {item['carencia_dias']} |")
    linhas += [
        '',
        '## Evidência do bug material da V128 com `CDB XP 150%`',
        '',
        '| Cenário antigo recorrente | Valor migrado estimado | Mínimo do produto | Ticket válido? |',
        '|---|---:|---:|---|',
    ]
    for item in invalidos_xp:
        linhas.append(f"| {item['rotulo']} | {item['valor_total_migrado']:.2f} | {item['aplicacao_minima_destino']:.2f} | {'Sim' if item['ticket_valido'] else 'Não'} |")
    linhas += [
        '',
        '## Resultado da reavaliação parametrizada diária',
        '',
        f'- Cenários testados na janela: {len(resultados)}.',
        f'- Cenários vencedores no cenário conjunto: {len(vencedores)}.',
        '',
        '### Melhores vencedores após respeitar ticket e top 5',
        '',
        '| Data | Família | Cenário | Destino | Valor total | Vitória material? | Δ déficit | Δ patrimônio proxy |',
        '|---|---|---|---|---:|---|---:|---:|',
    ]
    for item in vencedores_ordenados[:15]:
        linhas.append(
            f"| {item['data_solicitada']} | {item['familia']} | {item['rotulo']} | {item['produto_destino']} | {float(item['valor_total_alocado'] or 0.0):.2f} | {'Sim' if item['vitoria_material'] else 'Não'} | {item['delta_deficit_vs_baseline']:.2f} | {item['delta_patrimonio_proxy_vs_baseline']:.2f} |"
        )
    if not vencedores_ordenados:
        linhas.append('| - | - | Nenhum cenário vencedor sobreviveu após a parametrização. | - | 0.00 | Não | 0.00 | 0.00 |')

    linhas += [
        '',
        '## Leitura técnica',
        '',
        '- O caso `CDB XP 150%` era materialmente inválido para parte relevante dos cenários vencedores da V128, porque o ticket mínimo de R$ 10.000,00 não estava sendo aplicado corretamente.',
        '- A origem do problema foi dupla: parsing monetário inconsistente na `Carteira` e geração de cenários sem validação final do valor total efetivamente alocado contra o ticket do destino.',
        '- Nesta auditoria, a avaliação diária foi restringida aos 5 melhores produtos ranqueados da `Carteira`, preservando o foco em patrimônio líquido terminal, mas respeitando parâmetros operacionais reais do destino.',
        '- O próximo passo correto é absorver essa filtragem parametrizada no fluxo principal da grade diária, para que nenhum vencedor estrutural seja promovido sem antes passar por ticket mínimo/máximo e demais restrições de produto.',
        '',
    ]
    RELATORIO.write_text('\n'.join(linhas), encoding='utf-8')
    print(f'OK resultados={len(resultados)} vencedores={len(vencedores)}')


if __name__ == '__main__':
    executar()
