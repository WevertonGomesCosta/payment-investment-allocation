from __future__ import annotations

import json
from datetime import date
from pathlib import Path

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from nucleo.runner_validacao_diaria_operacional_v176 import rodar_validacao_diaria_operacional_v176


def main() -> None:
    raiz = Path(RAIZ)
    data_inicio = date(2026, 4, 23)
    data_fim = date(2026, 5, 23)
    resultado = rodar_validacao_diaria_operacional_v176(
        raiz_repositorio=raiz,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_candidatos_por_data=8,
        cap_fontes_destino=3,
    )

    saidas = raiz / 'saidas'
    relatorios = raiz / 'relatorios' / 'atuais'
    saidas.mkdir(parents=True, exist_ok=True)
    relatorios.mkdir(parents=True, exist_ok=True)

    nome_base = f'validacao_diaria_operacional_v176_{data_inicio.isoformat()}_{data_fim.isoformat()}'
    arquivo_json = saidas / f'{nome_base}.json'
    arquivo_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    resumo = resultado.get('resumo') or {}
    linhas = [
        '# Validação diária operacional V176',
        '',
        f'- Janela: {resumo.get("data_inicio")} até {resumo.get("data_fim")}',
        f'- Dias no horizonte: {resumo.get("dias_no_horizonte")}',
        f'- Dias com pagamento: {resumo.get("dias_com_pagamento")}',
        f'- Dias com ações candidatas de switching: {resumo.get("dias_com_acoes_candidatas_switching")}',
        f'- Dias com cenários promovíveis: {resumo.get("dias_com_cenarios_promoviveis")}',
        f'- Dias com switching executado: {resumo.get("dias_com_switching_executado")}',
        f'- Pagamentos no horizonte: {resumo.get("pagamentos_no_horizonte")}',
        f'- Inconsistências temporais no estado: {resumo.get("inconsistencias_temporais_no_estado")}',
        '',
        '## Famílias avaliadas',
    ]
    for familia, qtd in sorted((resumo.get('familias_cenarios_switching_avaliadas') or {}).items()):
        linhas.append(f'- {familia}: {qtd}')
    linhas.extend(['', '## Classes híbridas avaliadas'])
    for classe, qtd in sorted((resumo.get('classes_cenarios_hibridos_avaliados') or {}).items()):
        linhas.append(f'- {classe}: {qtd}')
    linhas.extend(['', f'JSON detalhado: `saidas/{arquivo_json.name}`'])

    arquivo_md = relatorios / f'VALIDACAO_DIARIA_OPERACIONAL_V176_{data_inicio.isoformat()}_{data_fim.isoformat()}.md'
    arquivo_md.write_text('\n'.join(linhas) + '\n', encoding='utf-8')

    print(str(arquivo_json))
    print(str(arquivo_md))


if __name__ == '__main__':
    main()
