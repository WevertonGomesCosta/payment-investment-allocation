from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_PATH = Path(__file__).resolve().parents[2]
if str(RAIZ_PATH) not in sys.path:
    sys.path.insert(0, str(RAIZ_PATH))

from nucleo.fluxo_pagamentos_terminal_v142 import comparar_fluxo_pagamentos_terminal_fase1_v142
from nucleo.identidade_baseline import caminho_saida_diagnostico, caminho_artifact

JSON_OUT = caminho_saida_diagnostico(RAIZ_PATH, 'fluxo_pagamentos_terminal_recorte_ampliado_v142.json')
MD_OUT = caminho_saida_diagnostico(RAIZ_PATH, 'FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLIADO_V142.md')
ART_JSON = caminho_artifact('fluxo_pagamentos_terminal_recorte_ampliado_v142.json')
ART_MD = caminho_artifact('FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLIADO_V142.md')

def main() -> int:
    resultado = comparar_fluxo_pagamentos_terminal_fase1_v142(raiz_repositorio=RAIZ_PATH)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')

    resumo = resultado['resumo']
    mudancas = resultado['mudancas_pagamento']
    linhas = [
        '# Fluxo pagamentos terminal — recorte ampliado V142',
        '',
        f"- Janela: **{resumo['data_inicio']} → {resumo['data_fim']}**",
        f"- Pagamentos avaliados: **{resumo['pagamentos_avaliados']}**",
        f"- Dias com pagamento: **{resumo['dias_com_pagamento']}**",
        f"- Mudanças de fonte com H1–H3: **{resumo['pagamentos_com_mudanca_fonte']}**",
        f"- Mudanças de tipo de fonte: **{resumo['pagamentos_com_mudanca_tipo']}**",
        f"- Switching escolhido sem H1–H3: **{resumo['pagamentos_com_switching_escolhido_sem_h1_h3']}**",
        f"- Switching escolhido com H1–H3: **{resumo['pagamentos_com_switching_escolhido_com_h1_h3']}**",
        '',
        '## Contagem de fontes sem H1–H3',
        '',
    ]
    for k, v in (resumo['contagem_fontes_sem_h1_h3'] or {}).items():
        linhas.append(f'- {k}: **{v}**')
    linhas.extend(['', '## Contagem de fontes com H1–H3', ''])
    for k, v in (resumo['contagem_fontes_com_h1_h3'] or {}).items():
        linhas.append(f'- {k}: **{v}**')
    linhas.extend(['', '## Pagamentos com mudança de escolha', ''])
    if not mudancas:
        linhas.append('- Nenhuma mudança de escolha observada no recorte ampliado.')
    else:
        for item in mudancas[:20]:
            linhas.append(
                f"- {item['data_pagamento']} | {item['descricao']} | "
                f"{item['antes_fonte_tipo']} → {item['depois_fonte_tipo']} | "
                f"{item['antes_fonte_id']} → {item['depois_fonte_id']}"
            )
    MD_OUT.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(json.dumps({'json': str(ART_JSON), 'md': str(ART_MD)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
