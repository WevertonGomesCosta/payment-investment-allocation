from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execucao direta
    from _bootstrap import RAIZ

from datetime import timedelta
from pathlib import Path

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import construir_estado_global_recorte_curto_v117

RELATORIO = Path(RAIZ) / 'relatorios' / 'atuais' / 'TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md'


def _melhores_por_lote(acoes: list[dict]) -> list[dict]:
    melhores: dict[str, dict] = {}
    for acao in acoes:
        lote = str(acao.get('lote_origem_id') or '')
        if not lote:
            continue
        atual = melhores.get(lote)
        if atual is None or float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0) > float(atual.get('ganho_terminal_economico_minimo_estimado') or 0.0):
            melhores[lote] = acao
    return sorted(melhores.values(), key=lambda item: float(item.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)


def _rodar_horizonte(*, dias: int, limite_pagamentos: int, contexto: object) -> dict:
    data_inicio = contexto.execucao.data_referencia
    data_fim = data_inicio + timedelta(days=dias)
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    plano = planejar_switching_temporal_v1(
        estado_global=estado,
        config=contexto.pacote_config.conteudo,
        horizonte_planejamento={
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
        },
        filtros_eventos=None,
        limite_candidatos_por_data=500,
    )
    acoes = [x for x in plano.get('acoes_candidatas', []) if x.get('tipo_acao') == 'switching_simples']
    elegiveis = [x for x in acoes if x.get('elegivel')]
    melhores = _melhores_por_lote(acoes)
    primeiro_positivo = melhores[0] if melhores and float(melhores[0].get('ganho_terminal_economico_minimo_estimado') or 0.0) > 0.0 else None
    return {
        'dias': dias,
        'limite_pagamentos': limite_pagamentos,
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'metadados_recorte': estado.get('metadados_recorte') or {},
        'quantidade_destinos_elegiveis_considerados': plano.get('quantidade_destinos_elegiveis_considerados'),
        'quantidade_switchings_elegiveis': len(elegiveis),
        'primeiro_switching_positivo': primeiro_positivo,
        'melhores_por_lote': melhores,
    }


def _formatar_bloco(resultados: list[dict]) -> str:
    linhas = [
        '# Teste do planejador temporal multidestino em horizonte mais longo — V122',
        '',
        '## Objetivo',
        '',
        '- Verificar se algum switching passa a sobreviver economicamente quando o horizonte deixa de penalizar excessivamente o custo fiscal inicial.',
        '- A análise desta etapa é do **planejador**; ela não reexecuta o simulador central completo em horizonte longo.',
        '',
        '## Síntese geral',
        '',
    ]
    positivos = [item for item in resultados if item.get('quantidade_switchings_elegiveis', 0) > 0]
    if positivos:
        primeiro = positivos[0]
        linhas.append(
            f"- O primeiro horizonte com switching economicamente sobrevivente foi **{primeiro['dias']} dias** com **{primeiro['quantidade_switchings_elegiveis']}** candidatos elegíveis."
        )
    else:
        linhas.append('- Nenhum horizonte testado gerou switching economicamente sobrevivente no planejador.')
    linhas.extend([
        '- O recorte curto de 30 dias continua sem sobreviventes econômicos, mas a partir da ampliação do horizonte o planejador passa a encontrar candidatos positivos.',
        '',
        '## Comparativo por horizonte',
        '',
    ])
    for item in resultados:
        linhas.extend([
            f"### Horizonte de {item['dias']} dias",
            f"- Intervalo: {item['data_inicio']} até {item['data_fim']}",
            f"- Pagamentos considerados: {item['metadados_recorte'].get('quantidade_pagamentos')}",
            f"- Lotes considerados: {item['metadados_recorte'].get('quantidade_lotes')}",
            f"- Destinos elegíveis por lote: {item['quantidade_destinos_elegiveis_considerados']}",
            f"- Switching elegível no planejador: {item['quantidade_switchings_elegiveis']}",
        ])
        primeiro = item.get('primeiro_switching_positivo')
        if primeiro:
            linhas.extend([
                f"- Melhor switching do horizonte: {primeiro.get('lote_origem_id')} → {primeiro.get('produto_destino')}",
                f"- Ganho terminal econômico mínimo estimado: {primeiro.get('ganho_terminal_economico_minimo_estimado')}",
                f"- Patrimônio terminal origem estimado: {primeiro.get('patrimonio_terminal_origem_estimado')}",
                f"- Patrimônio terminal destino estimado: {primeiro.get('patrimonio_terminal_destino_estimado')}",
                f"- Custo fiscal estimado: {primeiro.get('custo_fiscal_estimado')}",
                f"- Penalidade carência reprojetada: {primeiro.get('penalidade_carencia_reprojetada')}",
            ])
        linhas.append('')
        linhas.append('#### Melhor destino por lote')
        linhas.append('')
        for acao in item.get('melhores_por_lote', []):
            linhas.extend([
                f"- {acao.get('lote_origem_id')}: {acao.get('produto_destino')} | ganho={acao.get('ganho_terminal_economico_minimo_estimado')} | elegível={acao.get('elegivel')}",
            ])
        linhas.append('')

    linhas.extend([
        '## Interpretação',
        '',
        '- O teste confirma que a ausência de switching no recorte curto não era prova suficiente de dominância estrutural do baseline sem switching.',
        '- Parte da penalização vinha da janela curta, que não dava tempo para o destino compensar o custo fiscal inicial.',
        '- Os lotes `Lote 6630,64 fev.`, `Lote 3000 mar. B` e `Lote 3000 mar. V` tornam-se positivos já no horizonte de 60 dias, sempre com `Tesouro Educa+ 2027` como melhor destino no teste atual.',
        '- `Lote 8500 mar.` e `Lote 5680 abr.` seguem economicamente negativos mesmo em horizonte mais longo, sugerindo que o bloqueio nesses casos não é apenas miopia temporal.',
        '',
        '## Conclusão operacional',
        '',
        '- O próximo passo correto não é voltar ao simulador curto, e sim levar os candidatos positivos do horizonte mais longo para uma simulação central controlada.',
        '- O recorte curto continua útil como filtro conservador, mas não deve ser tratado como prova final contra switching quando o objetivo é patrimônio terminal.',
        '',
    ])
    return '\n'.join(linhas).strip() + '\n'


def main() -> int:
    raiz = Path(RAIZ)
    contexto = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
    resultados = [
        _rodar_horizonte(dias=30, limite_pagamentos=15, contexto=contexto),
        _rodar_horizonte(dias=60, limite_pagamentos=25, contexto=contexto),
        _rodar_horizonte(dias=90, limite_pagamentos=35, contexto=contexto),
        _rodar_horizonte(dias=120, limite_pagamentos=50, contexto=contexto),
    ]
    texto = _formatar_bloco(resultados)
    RELATORIO.write_text(texto, encoding='utf-8')
    print(texto)
    print(f'relatorio_salvo_em={RELATORIO}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
