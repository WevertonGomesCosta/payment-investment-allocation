from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import Counter
from pathlib import Path
import json

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'AVALIACAO_DIARIA_PARAMETRIZADA_JANELA_V130.md'
JSON_OUT = Path(RAIZ) / 'saidas' / 'operacional' / 'grade_diaria_parametrizada_v130_consolidado.json'
BASE_OPERACIONAL = Path(RAIZ) / 'saidas' / 'operacional'


def consolidar() -> dict:
    chunks = sorted(BASE_OPERACIONAL.glob('grade_diaria_parametrizada_v130_offset_*.json'))
    if not chunks:
        raise FileNotFoundError('Nenhum chunk V130 encontrado em saidas/operacional.')
    resultados = []
    dias = []
    for chunk in chunks:
        payload = json.loads(chunk.read_text(encoding='utf-8'))
        resultados.extend(payload.get('resultados', []))
        dias.extend(payload.get('dias_auditados', []))
    dias = sorted({item['data']: item for item in dias}.values(), key=lambda x: x['data'])
    resultados = sorted(resultados, key=lambda x: (x['data_solicitada'], x['familia'], x['rotulo']))
    vencedores = [r for r in resultados if r.get('continua_vencedor_central')]

    def ordenacao(r: dict) -> tuple:
        return (
            0 if r.get('vitoria_material') else 1,
            tuple(r.get('vetor_lexicografico') or ()),
            -float(r.get('delta_patrimonio_proxy_vs_baseline') or 0.0),
            r.get('data_solicitada') or '',
            r.get('rotulo') or '',
        )

    vencedores_ordenados = sorted(vencedores, key=ordenacao)
    melhores_por_dia = []
    for dia in sorted({item['data_solicitada'] for item in vencedores_ordenados}):
        itens = sorted([x for x in vencedores_ordenados if x['data_solicitada'] == dia], key=ordenacao)
        if itens:
            melhores_por_dia.append(itens[0])

    agrupados = [x for x in vencedores_ordenados if str(x.get('familia') or '').startswith('agrupado')]
    agrupados_unicos = []
    vistos = set()
    for item in agrupados:
        chave = (item.get('rotulo'), item.get('produto_destino'))
        if chave in vistos:
            continue
        itens = [x for x in agrupados if (x.get('rotulo'), x.get('produto_destino')) == chave]
        agrupados_unicos.append({
            'rotulo': item.get('rotulo'),
            'produto_destino': item.get('produto_destino'),
            'primeira_data': min(x['data_solicitada'] for x in itens),
            'ultima_data': max(x['data_solicitada'] for x in itens),
            'dias_vencedores': len(itens),
            'melhor_delta_patrimonio_proxy': max(float(x.get('delta_patrimonio_proxy_vs_baseline') or 0.0) for x in itens),
            'melhor_delta_deficit': min(float(x.get('delta_deficit_vs_baseline') or 0.0) for x in itens),
        })
        vistos.add(chave)

    payload_final = {
        'janela_inicio': dias[0]['data'] if dias else '',
        'janela_fim': dias[-1]['data'] if dias else '',
        'dias_auditados': dias,
        'resultados': resultados,
        'vencedores': vencedores_ordenados,
        'melhores_por_dia': melhores_por_dia,
        'agrupados_unicos': agrupados_unicos,
        'contagem_destinos_vencedores': dict(Counter(x.get('produto_destino') for x in vencedores_ordenados)),
    }
    JSON_OUT.write_text(json.dumps(payload_final, ensure_ascii=False, indent=2), encoding='utf-8')

    linhas = [
        '# Avaliação diária parametrizada da janela crítica — V130',
        '',
        '- Objetivo: rerodar a janela `2026-04-30` a `2026-05-20` com parâmetros de produto corrigidos, eliminando falsos positivos de ticket mínimo e máximo.',
        f'- Dias auditados: {len(dias)}.',
        f'- Cenários parametrizados simulados: {len(resultados)}.',
        f'- Cenários vencedores no cenário conjunto: {len(vencedores)}.',
        '',
        '## Conclusões centrais',
        '',
        '- O bug do `CDB XP 150%` abaixo de R$ 10 mil deixa de contaminar a janela: os cenários individuais e agrupados abaixo do mínimo não entram mais na simulação.',
        '- O `CDB XP 150%` continua aparecendo apenas quando o agrupamento realmente ultrapassa o ticket mínimo do produto.',
        '- A janela vencedora permanece viva após a correção de parâmetros, mas sua composição muda: o curto prazo passa a favorecer mais `Mercado Pago Cofrinho 120% CDI (Meli+)`, `CDB BMG Escalonado - até 109% CDI - 5 anos`, `CDB Sofisa 105%` e os combos PicPay do que o Tesouro como destino dominante.',
        '',
        '## Resumo por dia',
        '',
        '| Data | Ações elegíveis do planejador | Cenários parametrizados |',
        '|---|---:|---:|',
    ]
    for item in dias:
        linhas.append(f"| {item['data']} | {item['quantidade_acoes_elegiveis_planejador']} | {item['quantidade_cenarios_parametrizados']} |")

    linhas += [
        '',
        '## Melhor cenário vencedor por dia',
        '',
        '| Data | Família | Cenário | Destino | Valor total alocado | Δ déficit | Δ patrimônio proxy |',
        '|---|---|---|---|---:|---:|---:|',
    ]
    for item in melhores_por_dia:
        linhas.append(
            f"| {item['data_solicitada']} | {item['familia']} | {item['rotulo']} | {item['produto_destino']} | {float(item.get('valor_total_alocado') or 0.0):.2f} | {float(item.get('delta_deficit_vs_baseline') or 0.0):.2f} | {float(item.get('delta_patrimonio_proxy_vs_baseline') or 0.0):.2f} |"
        )

    linhas += [
        '',
        '## Agrupamentos vencedores únicos',
        '',
        '| Cenário agrupado | Destino | 1ª data | Última data | Dias vencedores | Melhor Δ déficit | Melhor Δ patrimônio proxy |',
        '|---|---|---|---|---:|---:|---:|',
    ]
    for item in agrupados_unicos:
        linhas.append(
            f"| {item['rotulo']} | {item['produto_destino']} | {item['primeira_data']} | {item['ultima_data']} | {item['dias_vencedores']} | {item['melhor_delta_deficit']:.2f} | {item['melhor_delta_patrimonio_proxy']:.2f} |"
        )
    if not agrupados_unicos:
        linhas.append('| - | - | - | - | 0 | 0.00 | 0.00 |')

    linhas += [
        '',
        '## Leitura técnica',
        '',
        '- Os cenários só entram na simulação quando passam pela validação de aplicação mínima/máxima do produto de destino.',
        '- Ticket individual inválido deixa de gerar cenário; ticket agrupado só entra quando o valor total combinado atinge o mínimo do produto.',
        '- A leitura correta da janela agora é: vencedores reais da métrica central, já livres dos falsos positivos de ticket mínimo.',
        '',
    ]
    RELATORIO.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(str(JSON_OUT))
    print(str(RELATORIO))
    return payload_final


def main() -> int:
    consolidar()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
