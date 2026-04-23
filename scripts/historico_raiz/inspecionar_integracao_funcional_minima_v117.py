from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execucao direta
    from _bootstrap import RAIZ

from collections import defaultdict
from pathlib import Path

from nucleo.simulador_central_eventos_v1 import rodar_integracao_funcional_minima_v117

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md'


def _melhores_por_lote(acoes: list[dict]) -> list[dict]:
    melhores: dict[str, dict] = {}
    for acao in acoes:
        lote = str(acao.get('lote_origem_id') or '')
        if not lote:
            continue
        atual = melhores.get(lote)
        if atual is None or float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) > float(atual.get('ganho_terminal_economico_minimo_estimado') or 0.0):
            melhores[lote] = acao
    return sorted(
        melhores.values(),
        key=lambda item: float(item.get('ganho_terminal_economico_minimo_estimado') or 0.0),
        reverse=True,
    )


def _formatar_bloco(resultados: dict) -> str:
    avaliacao = resultados['avaliacao_cenarios']
    melhor = avaliacao.get('melhor_cenario') or {}
    plano = resultados.get('plano_switching_temporal') or {}
    acoes = [x for x in plano.get('acoes_candidatas', []) if x.get('tipo_acao') == 'switching_simples']
    elegiveis = [x for x in acoes if x.get('elegivel')]
    melhores_por_lote = _melhores_por_lote(acoes)
    linhas = [
        '# Integração funcional mínima V117/V121 — recorte curto',
        '',
        f"- Data de referência: {resultados.get('contexto_data_referencia')}",
        f"- Horizonte: {resultados.get('horizonte')}",
        f"- Critério do planejador temporal: {plano.get('criterio_ranqueamento')}",
        f"- Destinos elegíveis considerados por lote: {plano.get('quantidade_destinos_elegiveis_considerados')}",
        f"- Candidatos elegíveis de switching: {plano.get('quantidade_candidatos_elegiveis_switching')}",
        f"- Melhor cenário atual: {melhor.get('cenario_id')}",
        f"- Vetor lexicográfico: {melhor.get('vetor_lexicografico')}",
        '',
        '## Melhor destino por lote',
        '',
    ]
    if not melhores_por_lote:
        linhas.append('- Nenhum lote com destino candidato disponível no recorte.')
        linhas.append('')
    else:
        for acao in melhores_por_lote:
            linhas.extend([
                f"### {acao.get('lote_origem_id')}",
                f"- Melhor destino no recorte: {acao.get('produto_destino')}",
                f"- Rank do destino: {acao.get('rank_destino_sugerido')}",
                f"- Elegível: {acao.get('elegivel')}",
                f"- Ganho terminal econômico mínimo estimado: {acao.get('ganho_terminal_economico_minimo_estimado')}",
                f"- Patrimônio terminal origem estimado: {acao.get('patrimonio_terminal_origem_estimado')}",
                f"- Patrimônio terminal destino estimado: {acao.get('patrimonio_terminal_destino_estimado')}",
                f"- Custo fiscal estimado: {acao.get('custo_fiscal_estimado')}",
                f"- Penalidade carência reprojetada: {acao.get('penalidade_carencia_reprojetada')}",
                '',
            ])
    linhas.extend([
        '## Top candidatos do planejador temporal',
        '',
    ])
    for acao in acoes[:8]:
        linhas.extend([
            f"### {acao.get('id_acao')}",
            f"- Lote: {acao.get('lote_origem_id')}",
            f"- Data: {acao.get('data_acao')}",
            f"- Produto destino: {acao.get('produto_destino')}",
            f"- Rank do destino: {acao.get('rank_destino_sugerido')}",
            f"- Elegível: {acao.get('elegivel')}",
            f"- Ganho terminal econômico mínimo estimado: {acao.get('ganho_terminal_economico_minimo_estimado')}",
            '',
        ])
    linhas.extend([
        '## Cenários avaliados',
        '',
    ])
    for item in avaliacao.get('ranking_cenarios', []):
        sim = resultados['simulacoes'].get(item['cenario_id'], {})
        linhas.extend([
            f"### {item['cenario_id']}",
            f"- Descrição: {item.get('descricao')}",
            f"- Vetor: {item.get('vetor_lexicografico')}",
            f"- Patrimônio líquido terminal proxy: {sim.get('patrimonio_liquido_terminal_proxy')}",
            f"- Ganho switching total: {sim.get('ganho_switching_total')}",
            f"- Pagamentos cobertos: {len(sim.get('pagamentos_cobertos', []))}",
            f"- Pagamentos sem cobertura: {len(sim.get('pagamentos_sem_cobertura', []))}",
            '',
        ])
    linhas.extend([
        '## Síntese',
        '',
        f"- Destinos alternativos economicamente sobreviventes: {len(elegiveis)}.",
        '- Quando esse total é zero, o destino padrão falhou e nenhum destino alternativo melhorou suficientemente o cenário no recorte.',
        '',
    ])
    return '\n'.join(linhas).strip() + '\n'


def main() -> int:
    resultados = rodar_integracao_funcional_minima_v117(raiz_repositorio=Path(RAIZ), limite_pagamentos=15)
    texto = _formatar_bloco(resultados)
    RELATORIO.write_text(texto, encoding='utf-8')
    print(texto)
    print(f'relatorio_salvo_em={RELATORIO}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
