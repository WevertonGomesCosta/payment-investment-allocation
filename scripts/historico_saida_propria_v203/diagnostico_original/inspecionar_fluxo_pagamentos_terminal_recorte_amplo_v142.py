from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import Counter
from pathlib import Path
import json

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import _comparar_fluxos, _config_sem_h1h3, _rodar_fluxo
from nucleo.identidade_baseline import caminho_saida_operacional

RAIZ_PATH = Path(RAIZ)
JSON_OUT = caminho_saida_operacional(RAIZ_PATH, 'fluxo_pagamentos_terminal_recorte_amplo_v142.json')
MD_OUT = RAIZ_PATH / 'relatorios' / 'atuais' / 'FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLO_V142.md'
ART_JSON = Path('/mnt/data/fluxo_pagamentos_terminal_recorte_amplo_v142.json')
ART_MD = Path('/mnt/data/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLO_V142.md')
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
MD_OUT.parent.mkdir(parents=True, exist_ok=True)

LIMITE_PAGAMENTOS = 20


def _fmt(valor: float | int | None) -> str:
    return f"{float(valor or 0.0):.2f}"


def main() -> int:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_PATH,
        instalar_automaticamente=False,
        incluir_switching_shadow=False,
        incluir_triagem=True,
        incluir_replay=True,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    fluxo_ativo = _rodar_fluxo(
        raiz_repositorio=RAIZ_PATH,
        limite_pagamentos=LIMITE_PAGAMENTOS,
        config_override=None,
        comparar_local_h1h3=False,
    )
    fluxo_neutro = _rodar_fluxo(
        raiz_repositorio=RAIZ_PATH,
        limite_pagamentos=LIMITE_PAGAMENTOS,
        config_override=_config_sem_h1h3(contexto.pacote_config.conteudo),
        comparar_local_h1h3=False,
    )
    comp_fluxo = _comparar_fluxos(
        fluxo_ativo.get('resultados_pagamento') or [],
        fluxo_neutro.get('resultados_pagamento') or [],
        fluxo_ativo.get('resumo') or {},
        fluxo_neutro.get('resumo') or {},
        fluxo_ativo.get('metrica_central') or {},
        fluxo_neutro.get('metrica_central') or {},
    )

    resultado = {
        'status': 'ok',
        'versao': 'V142',
        'limite_pagamentos': LIMITE_PAGAMENTOS,
        'fluxo_h1h3_ativo': fluxo_ativo,
        'fluxo_h1h3_neutro': fluxo_neutro,
        'comparacao_fluxo_completo': comp_fluxo,
        'observacao': 'A comparação foi feita em fluxo completo com H1–H3 ativas versus neutralizadas, usando recorte real maior e limite controlado de candidatos de switching por data para manter viabilidade computacional.',
    }
    texto_json = json.dumps(resultado, ensure_ascii=False, indent=2)
    JSON_OUT.write_text(texto_json, encoding='utf-8')
    ART_JSON.write_text(texto_json, encoding='utf-8')

    resumo_ativo = fluxo_ativo.get('resumo') or {}
    resumo_neutro = fluxo_neutro.get('resumo') or {}
    resultados_ativos = fluxo_ativo.get('resultados_pagamento') or []
    contagem_foco_ativa = Counter(
        item.get('fonte_principal_tipo') or 'sem_fonte_viavel'
        for item in resultados_ativos
        if item.get('fonte_principal_tipo') in {'lote_aportado', 'lote_nao_aportado', 'combinacao_minima_fontes', 'cenario_switching_elegivel'}
    )
    alterados = comp_fluxo.get('casos_alterados_no_fluxo') or []

    linhas = [
        '# FLUXO PAGAMENTOS TERMINAL RECORTE AMPLO V142',
        '',
        '- Objetivo: expandir a integração do `alocador_pagamentos_terminal_v1` para um recorte real maior de pagamentos e medir, em fluxo completo, como H1–H3 alteram as escolhas entre `lote_aportado`, `lote_nao_aportado`, `combinacao_minima_fontes` e `cenario_switching_elegivel`.',
        f'- Recorte auditado: **{LIMITE_PAGAMENTOS} pagamentos futuros reais**.',
        '- Observação operacional: para manter o recorte maior executável, a triagem de switching nesta auditoria foi rodada com teto controlado de candidatos por data na camada comparativa desta V142.',
        '',
        '## Resumo do recorte',
        '',
        f"- intervalo: `{resumo_ativo.get('data_inicio')}` → `{resumo_ativo.get('data_fim')}`",
        f"- pagamentos avaliados: **{resumo_ativo.get('quantidade_pagamentos')}**",
        f"- dias com pagamento: **{resumo_ativo.get('quantidade_dias_com_pagamento')}**",
        '',
        '## Fluxo com H1–H3 ativas',
        '',
        f"- patrimônio líquido terminal proxy: **R$ {_fmt(resumo_ativo.get('patrimonio_liquido_terminal_proxy'))}**",
        f"- perda terminal agregada: **R$ {_fmt(resumo_ativo.get('perda_patrimonio_liquido_terminal'))}**",
        f"- custo fiscal imediato total: **R$ {_fmt(resumo_ativo.get('custo_fiscal_imediato_total'))}**",
        f"- custo operacional total: **{_fmt(resumo_ativo.get('custo_operacional_total'))}**",
        f"- switching efetivamente escolhido: **{resumo_ativo.get('pagamentos_que_escolheram_switching')}** pagamentos",
        '',
        '## Fluxo com H1–H3 neutralizadas',
        '',
        f"- patrimônio líquido terminal proxy: **R$ {_fmt(resumo_neutro.get('patrimonio_liquido_terminal_proxy'))}**",
        f"- perda terminal agregada: **R$ {_fmt(resumo_neutro.get('perda_patrimonio_liquido_terminal'))}**",
        f"- custo fiscal imediato total: **R$ {_fmt(resumo_neutro.get('custo_fiscal_imediato_total'))}**",
        f"- custo operacional total: **{_fmt(resumo_neutro.get('custo_operacional_total'))}**",
        f"- switching efetivamente escolhido: **{resumo_neutro.get('pagamentos_que_escolheram_switching')}** pagamentos",
        '',
        '## Efeito agregado de H1–H3 no fluxo completo',
        '',
        f"- Δ patrimônio líquido terminal proxy: **R$ {_fmt(comp_fluxo.get('delta_patrimonio_liquido_terminal_proxy'))}**",
        f"- Δ perda terminal agregada: **R$ {_fmt(comp_fluxo.get('delta_perda_patrimonio_liquido_terminal'))}**",
        f"- Δ custo fiscal imediato: **R$ {_fmt(comp_fluxo.get('delta_custo_fiscal_imediato_total'))}**",
        f"- Δ custo operacional: **{_fmt(comp_fluxo.get('delta_custo_operacional_total'))}**",
        f"- Δ pagamentos que escolheram switching: **{comp_fluxo.get('delta_pagamentos_que_escolheram_switching')}**",
        f"- pagamentos com tipo/fonte alterados no fluxo: **{comp_fluxo.get('pagamentos_com_tipo_ou_fonte_alterados_no_fluxo')}**",
        '',
        '## Contagem das escolhas foco com H1–H3 ativas',
        '',
    ]
    for chave, valor in sorted(contagem_foco_ativa.items()):
        linhas.append(f'- `{chave}`: **{valor}**')
    linhas += [
        '',
        '## Casos alterados no fluxo completo',
        '',
    ]
    if alterados:
        for item in alterados[:10]:
            linhas.append(
                f"- `{item.get('data_pagamento')}` | `{item.get('pagamento_id')}` | `{item.get('transicao_fluxo_h1h3')}` | sem H1–H3: `{item.get('fonte_sem_h1h3_tipo')}` | com H1–H3: `{item.get('fonte_com_h1h3_tipo')}`"
            )
    else:
        linhas.append('- Nenhum pagamento mudou tipo/fonte principal no fluxo completo deste recorte.')

    linhas += [
        '',
        '## Leitura técnica',
        '',
        '- A comparação foi feita em fluxo completo com e sem H1–H3 no mesmo recorte real.',
        '- O foco permaneceu em patrimônio líquido terminal proxy, sem substituir a métrica terminal principal por score auxiliar.',
        '- Nesta rodada, o ganho relevante é observar se H1–H3 mudam a trajetória de fonte escolhida e se isso altera patrimônio terminal, custo fiscal e uso de switching em sequência real de pagamentos.',
    ]

    texto_md = '\n'.join(linhas) + '\n'
    MD_OUT.write_text(texto_md, encoding='utf-8')
    ART_MD.write_text(texto_md, encoding='utf-8')
    print(json.dumps({
        'status': 'ok',
        'limite_pagamentos': LIMITE_PAGAMENTOS,
        'delta_patrimonio_liquido_terminal_proxy': comp_fluxo.get('delta_patrimonio_liquido_terminal_proxy'),
        'pagamentos_com_tipo_ou_fonte_alterados_no_fluxo': comp_fluxo.get('pagamentos_com_tipo_ou_fonte_alterados_no_fluxo'),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
