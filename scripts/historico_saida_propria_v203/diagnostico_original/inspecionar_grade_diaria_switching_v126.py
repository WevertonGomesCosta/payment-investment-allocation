from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import defaultdict
import os
from copy import deepcopy
from datetime import timedelta
from itertools import combinations
from pathlib import Path

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

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V126.md'
DADOS_JSON = Path(RAIZ) / 'saidas' / 'operacional' / 'grade_diaria_switching_v126.json'
FAMILIAS_FRACAO = ((1.0, 'integral'), (0.5, 'parcial_50'))
TOP_LOTES_GRUPO = 3


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
    if inicio is None or fim is None:
        return {}
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


def _melhores_por_lote(acoes):
    melhores = {}
    for acao in acoes:
        if acao.get('tipo_acao') != 'switching_simples' or not acao.get('elegivel'):
            continue
        lote = str(acao.get('lote_origem_id') or '')
        if not lote:
            continue
        atual = melhores.get(lote)
        score = float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0)
        if atual is None or score > float(atual.get('ganho_terminal_economico_minimo_estimado') or 0.0):
            melhores[lote] = acao
    return sorted(melhores.values(), key=lambda x: float(x.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)


def _forcar_fracao(acao, fracao):
    novo = deepcopy(acao)
    novo['fracao_lote'] = fracao
    novo['id_acao'] = f"{acao.get('id_acao')}_f{int(fracao*100)}"
    return novo


def _gerar_cenarios_do_dia(data_iso, acoes_lote):
    cenarios = []
    top = [acao for acao in acoes_lote[:TOP_LOTES_GRUPO] if float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) > 0.0]
    todos = [acao for acao in acoes_lote if float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) > 0.0]
    for acao in acoes_lote:
        for fracao, tag_frac in FAMILIAS_FRACAO:
            evento = _forcar_fracao(acao, fracao)
            cenarios.append({
                'familia': f'isolado_{tag_frac}',
                'rotulo': str(acao.get('lote_origem_id') or ''),
                'data_solicitada': data_iso,
                'eventos': [evento],
            })
    for fracao, tag_frac in FAMILIAS_FRACAO:
        for a, b in combinations(top, 2):
            cenarios.append({
                'familia': f'par_{tag_frac}',
                'rotulo': f"{a.get('lote_origem_id')} + {b.get('lote_origem_id')}",
                'data_solicitada': data_iso,
                'eventos': [_forcar_fracao(a, fracao), _forcar_fracao(b, fracao)],
            })
        if len(todos) >= 2:
            cenarios.append({
                'familia': f'grupo_total_{tag_frac}',
                'rotulo': ' + '.join(str(x.get('lote_origem_id') or '') for x in todos),
                'data_solicitada': data_iso,
                'eventos': [_forcar_fracao(x, fracao) for x in todos],
            })
    return cenarios


def _comparar_com_baseline(sim, baseline):
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


def _executar_grade(raiz: Path):
    contexto = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
    config = contexto.pacote_config.conteudo
    estado_base, data_fim, qtd_pagamentos = _carregar_estado_completo(contexto)
    horizonte = {'data_inicio': contexto.execucao.data_referencia.isoformat(), 'data_fim': data_fim.isoformat()}
    snapshots = _gerar_snapshots_baseline(estado_base, config)

    resultados = []
    max_dias = int(os.getenv('V126_MAX_DIAS', '0') or 0)
    start_offset = int(os.getenv('V126_START_OFFSET', '0') or 0)
    dia = contexto.execucao.data_referencia + timedelta(days=start_offset)
    limite_data = data_fim if max_dias <= 0 else min(data_fim, dia + timedelta(days=max_dias - 1))
    while dia <= limite_data:
        estado_dia = deepcopy(snapshots[dia.isoformat()])
        estado_dia['data_evento_corrente'] = dia
        baseline_dia = simular_cenario_eventos_v1(estado_inicial=estado_dia, eventos_candidatos=[], config=config, horizonte=horizonte)
        plano = planejar_switching_temporal_v1(
            estado_global=estado_dia,
            config=config,
            horizonte_planejamento=horizonte,
            filtros_eventos=None,
            limite_candidatos_por_data=200,
        )
        melhores = _melhores_por_lote(plano.get('acoes_candidatas', []))
        cenarios = _gerar_cenarios_do_dia(dia.isoformat(), melhores)
        for cenario in cenarios:
            sim = simular_cenario_eventos_v1(
                estado_inicial=estado_dia,
                eventos_candidatos=cenario['eventos'],
                config=config,
                horizonte=horizonte,
            )
            comp = _comparar_com_baseline(sim, baseline_dia)
            resultados.append({
                'data_solicitada': dia.isoformat(),
                'familia': cenario['familia'],
                'rotulo': cenario['rotulo'],
                'eventos': [
                    {
                        'lote_origem_id': e.get('lote_origem_id'),
                        'produto_destino': e.get('produto_destino'),
                        'data_acao': e.get('data_acao'),
                        'fracao_lote': e.get('fracao_lote', 1.0),
                        'ganho_planejador': float(e.get('ganho_terminal_economico_minimo_estimado') or 0.0),
                    }
                    for e in cenario['eventos']
                ],
                'patrimonio_liquido_terminal_proxy': float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0),
                **comp,
            })
        dia += timedelta(days=1)
    return {
        'data_referencia': contexto.execucao.data_referencia.isoformat(),
        'start_offset': int(os.getenv('V126_START_OFFSET', '0') or 0),
        'max_dias_executados': max_dias if 'max_dias' in locals() else 0,
        'data_fim': data_fim.isoformat(),
        'quantidade_pagamentos': qtd_pagamentos,
        'baseline_inicial': {
            'descricao': 'baseline do dia zero sem switching, apenas para referência global do horizonte completo',
        },
        'resultados': resultados,
    }


def _melhor_por_chave(resultados, *, familia=None):
    melhores = {}
    for item in resultados:
        if familia and item['familia'] != familia:
            continue
        chave = (item['familia'], item['rotulo'])
        atual = melhores.get(chave)
        score = (
            0 if item['continua_vencedor_central'] else 1,
            0 if item['vitoria_material'] else 1,
            item['vetor_lexicografico'],
            -item['delta_patrimonio_proxy_vs_baseline'],
        )
        if atual is None or score < atual['_score']:
            novo = dict(item)
            novo['_score'] = score
            melhores[chave] = novo
    return sorted((v for v in melhores.values()), key=lambda x: x['_score'])


def _top_globais(resultados, limite=12):
    itens = sorted(
        resultados,
        key=lambda item: (
            0 if item['continua_vencedor_central'] else 1,
            0 if item['vitoria_material'] else 1,
            item['vetor_lexicografico'],
            -item['delta_patrimonio_proxy_vs_baseline'],
        ),
    )
    return itens[:limite]


def _formatar_relatorio(dados):
    resultados = dados['resultados']
    melhores = _melhor_por_chave(resultados)
    top = _top_globais(resultados)
    datas = sorted({item['data_solicitada'] for item in resultados})
    primeira_data = datas[0] if datas else dados['data_referencia']
    ultima_data = datas[-1] if datas else dados['data_fim']
    linhas = [
        '# Avaliação diária da data ótima de switching — V126',
        '',
        '- Objetivo: testar diariamente, desde D0 até o fim do horizonte, qual é a melhor data de switching por lote e por agrupamento, mantendo a análise conjunta até o fim do período.',
        '- Escopo: lotes já investidos, com comparação entre cenários isolados e agrupados, em modo integral e parcial 50%.',
        '- Observação: esta primeira grade cobre isolado, pares entre os 3 lotes mais promissores do dia e grupo total dos candidatos positivos do dia; não faz busca exaustiva de todos os subconjuntos possíveis.',
        '- Execução pesada: o código foi preparado para rodar em blocos e consolidar a grade diária por partes quando o ambiente interativo não suporta o horizonte completo em uma única passagem.',
        '',
        '## Janela auditada',
        '',
        f"- Data de referência: {dados['data_referencia']}",
        f"- Janela total teórica do horizonte: {dados['data_referencia']} → {dados['data_fim']}",
        f"- Janela efetivamente consolidada nesta auditoria: {primeira_data} → {ultima_data}",
        f"- Quantidade de dias consolidados: {len(datas)}",
        f"- Quantidade de pagamentos futuros no horizonte: {dados['quantidade_pagamentos']}",
        '- Comparação principal: em cada data, o switching é comparado contra o baseline condicional daquela própria data, após a trajetória sem switching até esse ponto.',
        '',
        '## Top global de datas/cenários',
        '',
    ]
    for item in top:
        linhas.extend([
            f"- {item['data_solicitada']} | {item['familia']} | {item['rotulo']}",
            f"  - vencedor central = {item['continua_vencedor_central']}",
            f"  - vitória material = {item['vitoria_material']}",
            f"  - vetor = {item['vetor_lexicografico']}",
            f"  - Δ perda terminal = {item['delta_perda_terminal_vs_baseline']}",
            f"  - Δ déficit = {item['delta_deficit_vs_baseline']}",
            f"  - Δ protegida = {item['delta_violacoes_protegida_vs_baseline']}",
            f"  - Δ patrimônio proxy = {item['delta_patrimonio_proxy_vs_baseline']}",
            f"  - eventos = {item['eventos']}",
        ])
    linhas.extend(['', '## Melhor data por lote ou agrupamento', ''])
    for item in melhores:
        linhas.extend([
            f"### {item['familia']} | {item['rotulo']}",
            f"- melhor data solicitada: {item['data_solicitada']}",
            f"- vencedor central: {item['continua_vencedor_central']}",
            f"- vitória material: {item['vitoria_material']}",
            f"- vetor: {item['vetor_lexicografico']}",
            f"- Δ perda terminal: {item['delta_perda_terminal_vs_baseline']}",
            f"- Δ déficit: {item['delta_deficit_vs_baseline']}",
            f"- Δ protegida: {item['delta_violacoes_protegida_vs_baseline']}",
            f"- Δ patrimônio proxy: {item['delta_patrimonio_proxy_vs_baseline']}",
            f"- eventos: {item['eventos']}",
            '',
        ])
    vencedores_d0 = [x for x in resultados if x['data_solicitada'] == dados['data_referencia'] and x['continua_vencedor_central']]
    vencedores_d1 = [x for x in resultados if x['data_solicitada'] == (_coerce_date(dados['data_referencia']) + timedelta(days=1)).isoformat() and x['continua_vencedor_central']]
    linhas.extend([
        '## Leitura operacional',
        '',
        f"- Quantidade de cenários diários vencedores em D0: {len(vencedores_d0)}",
        f"- Quantidade de cenários diários vencedores em D+1: {len(vencedores_d1)}",
        '- A decisão correta deixa de ser um único horizonte e passa a ser uma grade diária de datas possíveis, mantendo a trajetória conjunta após o switching.',
        '- O simulador continua após a data escolhida até o fim do horizonte, já com o switching realizado e impactando pagamentos futuros.',
        '- Cada delta do relatório é calculado contra o baseline condicional do mesmo dia, e não contra um único baseline fixo de D0.',
        '',
    ])
    return '\n'.join(linhas).strip() + '\n'


def main() -> int:
    import json

    raiz = Path(RAIZ)
    dados = _executar_grade(raiz)
    texto = _formatar_relatorio(dados)
    RELATORIO.write_text(texto, encoding='utf-8')
    DADOS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(texto)
    print(f'relatorio_salvo_em={RELATORIO}')
    print(f'dados_salvos_em={DADOS_JSON}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
