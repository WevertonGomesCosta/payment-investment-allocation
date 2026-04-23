from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execucao direta
    from _bootstrap import RAIZ

from pathlib import Path

from nucleo.simulador_central_eventos_v1 import rodar_integracao_funcional_minima_v117

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md'


def _formatar_bloco(resultados: dict) -> str:
    avaliacao = resultados['avaliacao_cenarios']
    melhor = avaliacao.get('melhor_cenario') or {}
    linhas = [
        '# Integração funcional mínima V117/V118 — recorte curto',
        '',
        f"- Data de referência: {resultados.get('contexto_data_referencia')}",
        f"- Horizonte: {resultados.get('horizonte')}",
        f"- Melhor cenário atual: {melhor.get('cenario_id')}",
        f"- Vetor lexicográfico: {melhor.get('vetor_lexicografico')}",
        '',
        '## Cenários avaliados',
        '',
    ]
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
