
from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import Counter
from pathlib import Path
import json

from nucleo.comparador_hibrido_switching_v1 import escolher_melhor_cenario_promovivel

import os

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md'
JSON_OUT = Path(RAIZ) / 'saidas' / 'operacional' / 'grade_diaria_oficial_hibrida_v134_consolidado.json'
BASE_OPERACIONAL = Path(RAIZ) / 'saidas' / 'operacional'

def _date_env(var: str, default: str) -> str:
    return os.getenv(var, default) or default

JANELA_INICIO = _date_env('V134_JANELA_INICIO', '2026-05-21')
JANELA_FIM = _date_env('V134_JANELA_FIM', '2026-08-18')


def _baseline_oficial(data: str) -> dict:
    return {
        'data_solicitada': data,
        'rotulo': 'baseline_sem_switching',
        'classe_comparador_hibrido': 'baseline',
        'promovivel_hibrido': True,
        'origem_promocao_oficial': 'baseline',
        'delta_perda_terminal_vs_baseline': 0.0,
        'delta_deficit_vs_baseline': 0.0,
        'delta_patrimonio_proxy_vs_baseline': 0.0,
        'familia': 'baseline',
        'produto_destino': None,
        'valor_total_alocado': 0.0,
        'bloqueado_promocao_automatica': False,
    }


def consolidar() -> dict:
    chunks = sorted(BASE_OPERACIONAL.glob(f'grade_diaria_hibrida_v134_{JANELA_INICIO}_{JANELA_FIM}_offset_*.json'))
    if not chunks:
        raise FileNotFoundError('Nenhum chunk V134 encontrado em saidas/operacional.')
    resultados = []
    dias = []
    for chunk in chunks:
        payload = json.loads(chunk.read_text(encoding='utf-8'))
        resultados.extend(payload.get('resultados', []))
        dias.extend(payload.get('dias_auditados', []))
    dias = sorted({item['data']: item for item in dias}.values(), key=lambda x: x['data'])
    resultados = sorted(resultados, key=lambda x: (x['data_solicitada'], x['familia'], x['rotulo']))

    por_dia = {}
    for item in resultados:
        por_dia.setdefault(item['data_solicitada'], []).append(item)

    melhores_lex = []
    melhores_oficiais = []
    dias_bloqueados = 0
    dias_promovidos_switching = 0
    dias_baseline = 0
    dias_promocao_diferente = 0
    contagem_classes_oficiais = Counter()

    datas_auditadas = [item['data'] for item in dias]
    for data in sorted(datas_auditadas):
        itens = por_dia.get(data, [])
        if itens:
            vencedor_lex = sorted(itens, key=lambda x: (tuple(x.get('vetor_lexicografico') or ()), str(x.get('rotulo') or '')))[0]
            melhores_lex.append(vencedor_lex)
            if vencedor_lex.get('bloqueado_promocao_automatica'):
                dias_bloqueados += 1
            promovivel = escolher_melhor_cenario_promovivel(itens)
        else:
            vencedor_lex = _baseline_oficial(data)
            vencedor_lex['origem_promocao_oficial'] = 'sem_cenarios_gerados'
            melhores_lex.append(vencedor_lex)
            promovivel = None
        if promovivel is None:
            oficial = _baseline_oficial(data)
            oficial['origem_promocao_oficial'] = 'baseline' if itens else 'sem_cenarios_gerados'
            dias_baseline += 1
        else:
            oficial = dict(promovivel)
            oficial['origem_promocao_oficial'] = 'comparador_hibrido'
            dias_promovidos_switching += 1
            if oficial.get('rotulo') != vencedor_lex.get('rotulo'):
                dias_promocao_diferente += 1
            contagem_classes_oficiais[str(oficial.get('classe_comparador_hibrido') or 'desconhecido')] += 1
        melhores_oficiais.append(oficial)

    payload_final = {
        'janela_inicio': dias[0]['data'] if dias else '',
        'janela_fim': dias[-1]['data'] if dias else '',
        'dias_auditados': dias,
        'resultados': resultados,
        'melhores_lexicograficos_por_dia': melhores_lex,
        'melhores_oficiais_por_dia': melhores_oficiais,
        'dias_com_vencedor_lexicografico_bloqueado': dias_bloqueados,
        'dias_promovidos_com_switching': dias_promovidos_switching,
        'dias_promovidos_com_baseline': dias_baseline,
        'dias_em_que_promocao_oficial_diferiu_do_lexicografico': dias_promocao_diferente,
        'contagem_classes_oficiais': dict(contagem_classes_oficiais),
        'contagem_destinos_oficiais': dict(Counter(item.get('produto_destino') or 'baseline_sem_switching' for item in melhores_oficiais)),
    }
    JSON_OUT.write_text(json.dumps(payload_final, ensure_ascii=False, indent=2), encoding='utf-8')

    linhas = [
        '# Grade diária oficial com comparador híbrido — V134',
        '',
        '- Objetivo: expandir o fluxo oficial híbrido além de 2026-05-20, promovendo apenas `vencedor_terminal`, `vencedor_hibrido_aceitavel` ou `baseline_sem_switching` no horizonte ampliado.',
        '',
        f"- Dias auditados: {len(dias)}",
        f"- Resultados avaliados: {len(resultados)}",
        f"- Dias com vencedor lexicográfico bloqueado: {dias_bloqueados}",
        f"- Dias promovidos com switching: {dias_promovidos_switching}",
        f"- Dias promovidos com baseline: {dias_baseline}",
        f"- Dias em que a promoção oficial diferiu do vencedor lexicográfico: {dias_promocao_diferente}",
        '',
        '## Contagem das classes oficiais promovidas',
        '',
    ]
    if contagem_classes_oficiais:
        for chave, valor in sorted(contagem_classes_oficiais.items()):
            linhas.append(f"- {chave}: {valor}")
    else:
        linhas.append('- nenhum switching promovido oficialmente')
    linhas += [
        '',
        '## Melhor cenário oficial por dia',
        '',
        '| Data | Vencedor lexicográfico | Classe lex | Bloqueado | Melhor cenário oficial | Classe oficial | Origem | Δ perda terminal | Δ déficit | Δ patrimônio proxy |',
        '|---|---|---|---|---|---|---|---:|---:|---:|',
    ]
    por_data_oficial = {item['data_solicitada']: item for item in melhores_oficiais}
    for lex in melhores_lex:
        oficial = por_data_oficial[lex['data_solicitada']]
        linhas.append(
            '| {data} | {lex_rotulo} | {lex_classe} | {bloq} | {of_rotulo} | {of_classe} | {origem} | {dp:.2f} | {dd:.2f} | {dpat:.2f} |'.format(
                data=lex['data_solicitada'],
                lex_rotulo=lex.get('rotulo') or 'baseline',
                lex_classe=lex.get('classe_comparador_hibrido') or '-',
                bloq='Sim' if lex.get('bloqueado_promocao_automatica') else 'Não',
                of_rotulo=oficial.get('rotulo') or 'baseline_sem_switching',
                of_classe=oficial.get('classe_comparador_hibrido') or 'baseline',
                origem=oficial.get('origem_promocao_oficial') or '-',
                dp=float(oficial.get('delta_perda_terminal_vs_baseline') or 0.0),
                dd=float(oficial.get('delta_deficit_vs_baseline') or 0.0),
                dpat=float(oficial.get('delta_patrimonio_proxy_vs_baseline') or 0.0),
            )
        )
    linhas += [
        '',
        '## Leitura técnica',
        '',
        '- O vencedor lexicográfico continua sendo registrado para auditoria, mas não define mais a promoção oficial do dia quando cai como `vencedor_operacional`.',
        '- Se existir cenário `vencedor_terminal` ou `vencedor_hibrido_aceitavel`, ele passa a ser o melhor cenário oficial do dia.',
        '- Se não existir cenário promovível, o consolidado oficial passa a emitir explicitamente `baseline_sem_switching` como melhor cenário do dia.',
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
