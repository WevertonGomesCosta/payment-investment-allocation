from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from nucleo.comparador_hibrido_switching_v1 import (
    PRIORIDADE_CLASSE,
    ToleranciasComparadorHibrido,
    chave_promocao_hibrida,
    classificar_cenario_diario,
    escolher_melhor_cenario_promovivel,
)


JSON_FONTES = [
    Path('/mnt/data/grade_diaria_parametrizada_v130_consolidado.json'),
    REPO_ROOT / 'saidas' / 'operacional' / 'grade_diaria_parametrizada_v130_consolidado.json',
]

SAIDA_JSON = REPO_ROOT / 'saidas' / 'operacional' / 'comparador_hibrido_switching_v132.json'
SAIDA_MD = REPO_ROOT / 'relatorios' / 'atuais' / 'COMPARADOR_HIBRIDO_SWITCHING_V132.md'


def _carregar_grade() -> dict:
    for caminho in JSON_FONTES:
        if caminho.exists():
            return json.loads(caminho.read_text(encoding='utf-8'))
    raise FileNotFoundError('grade_diaria_parametrizada_v130_consolidado.json não encontrada')


def _anotar_resultados(resultados: list[dict]) -> list[dict]:
    anotados: list[dict] = []
    for item in resultados:
        novo = dict(item)
        novo.update(classificar_cenario_diario(novo, ToleranciasComparadorHibrido()))
        anotados.append(novo)
    return anotados


def _resumo_por_dia(resultados: list[dict]) -> list[dict]:
    saida: list[dict] = []
    por_dia: dict[str, list[dict]] = {}
    for item in resultados:
        por_dia.setdefault(str(item.get('data_solicitada')), []).append(item)

    for data, itens in sorted(por_dia.items()):
        vencedor_lexicografico = sorted(itens, key=lambda x: (tuple(x.get('vetor_lexicografico') or []), str(x.get('rotulo') or '')))[0]
        vencedor_hibrido = escolher_melhor_cenario_promovivel(itens)
        saida.append({
            'data_solicitada': data,
            'vencedor_lexicografico': {
                'rotulo': vencedor_lexicografico.get('rotulo'),
                'classe_comparador_hibrido': vencedor_lexicografico.get('classe_comparador_hibrido'),
                'delta_perda_terminal_vs_baseline': vencedor_lexicografico.get('delta_perda_terminal_vs_baseline'),
                'delta_deficit_vs_baseline': vencedor_lexicografico.get('delta_deficit_vs_baseline'),
                'delta_patrimonio_proxy_vs_baseline': vencedor_lexicografico.get('delta_patrimonio_proxy_vs_baseline'),
                'bloqueado_promocao_automatica': vencedor_lexicografico.get('bloqueado_promocao_automatica'),
            },
            'promocao_hibrida': None if vencedor_hibrido is None else {
                'rotulo': vencedor_hibrido.get('rotulo'),
                'classe_comparador_hibrido': vencedor_hibrido.get('classe_comparador_hibrido'),
                'delta_perda_terminal_vs_baseline': vencedor_hibrido.get('delta_perda_terminal_vs_baseline'),
                'delta_deficit_vs_baseline': vencedor_hibrido.get('delta_deficit_vs_baseline'),
                'delta_patrimonio_proxy_vs_baseline': vencedor_hibrido.get('delta_patrimonio_proxy_vs_baseline'),
            },
        })
    return saida


def _gerar_relatorio(payload: dict) -> str:
    contagem = payload['contagem_classes']
    dias = payload['dias_resumidos']
    linhas = [
        '# Comparador híbrido de switching — V132',
        '',
        '## Objetivo',
        '',
        'Classificar cada cenário diário como `vencedor operacional`, `vencedor terminal`, `vencedor híbrido aceitável` ou `dominado pelo baseline`, bloqueando a promoção automática de switchings que piorem patrimônio líquido terminal frente ao baseline.',
        '',
        '## Contagem agregada das classes',
        '',
        f"- vencedor_operacional: {contagem.get('vencedor_operacional', 0)}",
        f"- vencedor_terminal: {contagem.get('vencedor_terminal', 0)}",
        f"- vencedor_hibrido_aceitavel: {contagem.get('vencedor_hibrido_aceitavel', 0)}",
        f"- dominado_pelo_baseline: {contagem.get('dominado_pelo_baseline', 0)}",
        '',
        f"- cenários bloqueados para promoção automática: {payload['cenarios_bloqueados_promocao_automatica']}",
        f"- dias em que o vencedor lexicográfico foi bloqueado: {payload['dias_com_vencedor_lexicografico_bloqueado']}",
        f"- dias com promoção híbrida diferente do vencedor lexicográfico: {payload['dias_com_promocao_hibrida_diferente']}",
        '',
        '## Leitura principal',
        '',
        '- `vencedor_operacional`: melhora a métrica central atual, mas piora materialmente o patrimônio terminal frente ao baseline; deve ficar bloqueado para promoção automática.',
        '- `vencedor_terminal`: melhora materialmente o patrimônio terminal sem piora operacional material; é o candidato preferencial para promoção.',
        '- `vencedor_hibrido_aceitavel`: vence ou permanece competitivo sem piora terminal material; é aceitável quando não existir vencedor terminal superior.',
        '',
        '## Resumo diário',
        '',
        '| Data | Vencedor lexicográfico | Classe | Bloqueado | Promoção híbrida | Classe promoção | Δ perda terminal promoção | Δ déficit promoção | Δ patrimônio promoção |',
        '|---|---|---|---|---|---|---:|---:|---:|',
    ]

    for dia in dias:
        lex = dia['vencedor_lexicografico']
        pro = dia['promocao_hibrida']
        linhas.append(
            '| {data} | {lex_rotulo} | {lex_classe} | {lex_bloq} | {pro_rotulo} | {pro_classe} | {pro_dp:.2f} | {pro_dd:.2f} | {pro_dpat:.2f} |'.format(
                data=dia['data_solicitada'],
                lex_rotulo=lex.get('rotulo') or 'baseline',
                lex_classe=lex.get('classe_comparador_hibrido') or '-',
                lex_bloq='Sim' if lex.get('bloqueado_promocao_automatica') else 'Não',
                pro_rotulo=(pro or {}).get('rotulo') or 'baseline_sem_switching',
                pro_classe=(pro or {}).get('classe_comparador_hibrido') or 'baseline',
                pro_dp=float((pro or {}).get('delta_perda_terminal_vs_baseline') or 0.0),
                pro_dd=float((pro or {}).get('delta_deficit_vs_baseline') or 0.0),
                pro_dpat=float((pro or {}).get('delta_patrimonio_proxy_vs_baseline') or 0.0),
            )
        )

    linhas.extend([
        '',
        '## Caso crítico já conhecido',
        '',
        '- O cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` permanece classificado como `vencedor_operacional` no bloco 2026-05-13 a 2026-05-20, portanto fica bloqueado para promoção automática no comparador híbrido.',
    ])
    return '\n'.join(linhas) + '\n'


def main() -> int:
    bruto = _carregar_grade()
    resultados = _anotar_resultados(list(bruto['resultados']))
    df = pd.DataFrame(resultados)
    contagem_classes = {k: int(v) for k, v in df['classe_comparador_hibrido'].value_counts().to_dict().items()}

    dias_resumidos = _resumo_por_dia(resultados)
    dias_com_vencedor_lexicografico_bloqueado = sum(1 for item in dias_resumidos if bool(item['vencedor_lexicografico']['bloqueado_promocao_automatica']))
    dias_com_promocao_hibrida_diferente = sum(
        1
        for item in dias_resumidos
        if item['promocao_hibrida'] is not None and item['promocao_hibrida']['rotulo'] != item['vencedor_lexicografico']['rotulo']
    )

    payload = {
        'janela_inicio': bruto.get('janela_inicio'),
        'janela_fim': bruto.get('janela_fim'),
        'tolerancias': ToleranciasComparadorHibrido().__dict__,
        'contagem_classes': contagem_classes,
        'cenarios_bloqueados_promocao_automatica': int(df['bloqueado_promocao_automatica'].sum()),
        'dias_com_vencedor_lexicografico_bloqueado': int(dias_com_vencedor_lexicografico_bloqueado),
        'dias_com_promocao_hibrida_diferente': int(dias_com_promocao_hibrida_diferente),
        'dias_resumidos': dias_resumidos,
        'resultados_anotados': resultados,
    }

    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    SAIDA_MD.write_text(_gerar_relatorio(payload), encoding='utf-8')

    print(f"OK cenarios={len(resultados)} bloqueados={payload['cenarios_bloqueados_promocao_automatica']} dias_bloqueados={payload['dias_com_vencedor_lexicografico_bloqueado']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
