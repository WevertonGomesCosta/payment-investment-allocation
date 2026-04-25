from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import Counter
from pathlib import Path
import json

from nucleo.fluxo_pagamentos_terminal_v138 import rodar_fluxo_pagamentos_terminal_recorte_curto_v138

BASE = Path(RAIZ) / 'saidas' / 'operacional'
BASE.mkdir(parents=True, exist_ok=True)
JSON_OUT = BASE / 'fluxo_pagamentos_terminal_recorte_curto_v138.json'
MD_OUT = BASE / 'FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md'


def main() -> int:
    resultado = rodar_fluxo_pagamentos_terminal_recorte_curto_v138(
        raiz_repositorio=Path(RAIZ),
        limite_pagamentos=15,
    )
    JSON_OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')

    pagamentos = resultado.get('resultados_pagamento') or []
    resumo = resultado.get('resumo') or {}
    por_fonte = Counter(item.get('fonte_principal_tipo') or 'sem_fonte_viavel' for item in pagamentos)
    com_switch_promovivel = [item for item in pagamentos if item.get('promovivel_switching')]
    com_switch_escolhido = [item for item in pagamentos if item.get('switching_aplicado_no_fluxo')]

    linhas = [
        '# FLUXO PAGAMENTOS TERMINAL RECORTE CURTO V138',
        '',
        '- Objetivo: integrar o `alocador_pagamentos_terminal_v1` ao fluxo oficial de um recorte curto real de pagamentos e validar, em dados do projeto, quando ele escolhe saldo disponível, lote não aportado, lote aportado ou cenário com switching elegível.',
        '',
        '## Resumo do recorte',
        '',
        f"- intervalo: `{resumo.get('data_inicio')}` → `{resumo.get('data_fim')}`",
        f"- pagamentos avaliados: **{resumo.get('quantidade_pagamentos')}**",
        f"- dias com pagamento: **{resumo.get('quantidade_dias_com_pagamento')}**",
        f"- pagamentos com switching elegível promovível disponível: **{resumo.get('pagamentos_com_switching_elegivel_promovivel')}**",
        f"- pagamentos que efetivamente escolheram switching: **{resumo.get('pagamentos_que_escolheram_switching')}**",
        f"- pagamentos cobertos integralmente: **{resumo.get('pagamentos_cobertos_integralmente')}**",
        f"- déficit total do recorte: **R$ {float(resumo.get('deficit_total') or 0.0):.2f}**",
        '',
        '## Contagem por fonte escolhida',
        '',
    ]
    for chave, valor in sorted(por_fonte.items()):
        linhas.append(f'- `{chave}`: **{valor}**')
    linhas += [
        '',
        '## Leitura técnica',
        '',
        '- O fluxo já está usando o alocador em dados reais do projeto, comparando fontes contratuais de pagamento e cenário com switching elegível filtrado pelo comparador híbrido.',
        '- Esta validação ainda é de recorte curto e integração funcional; ela não fecha o modelo final de pagamentos, mas já mostra quais fontes dominam no estado real da baseline.',
        '',
        '## Exemplos auditados',
        '',
    ]
    for item in pagamentos[:6]:
        linhas.append(
            f"- `{item.get('data_pagamento')}` | `{item.get('pagamento_id')}` | `{item.get('fonte_principal_tipo')}` | cobertura `{item.get('cobertura_integral')}` | déficit `R$ {float(item.get('valor_deficit') or 0.0):.2f}`"
        )
    if com_switch_promovivel:
        linhas += [
            '',
            '## Pagamentos com switching promovível disponível',
            '',
        ]
        for item in com_switch_promovivel[:5]:
            linhas.append(
                f"- `{item.get('data_pagamento')}` | `{item.get('pagamento_id')}` | cenário `{item.get('rotulo_cenario_switching')}` | fonte escolhida `{item.get('fonte_principal_tipo')}` | aplicado `{item.get('switching_aplicado_no_fluxo')}`"
            )
    if com_switch_escolhido:
        linhas += [
            '',
            '## Pagamentos que efetivamente acionaram switching',
            '',
        ]
        for item in com_switch_escolhido[:5]:
            linhas.append(
                f"- `{item.get('data_pagamento')}` | `{item.get('pagamento_id')}` | `{item.get('rotulo_cenario_switching')}`"
            )
    else:
        linhas += [
            '',
            '## Pagamentos que efetivamente acionaram switching',
            '',
            '- Nenhum pagamento do recorte curto escolheu cenário com switching elegível na baseline atual.',
        ]

    MD_OUT.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(json.dumps(resultado.get('resumo') or {}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
