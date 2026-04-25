from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from pathlib import Path
import json

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1

BASE = Path(RAIZ) / 'saidas' / 'operacional'
BASE.mkdir(parents=True, exist_ok=True)
JSON_OUT = BASE / 'alocador_pagamentos_terminal_v137.json'
MD_OUT = BASE / 'ALOCADOR_PAGAMENTOS_TERMINAL_V137.md'


def _cenarios_base() -> dict:
    pagamento = {
        'pagamento_id': 'pgto_demo_001',
        'data': '2026-05-02',
        'classe': 'PROTEGIDA',
        'valor': 1500.0,
    }
    estado_baseline = {
        'data_referencia': '2026-04-30',
        'data_evento_corrente': '2026-05-02',
        'data_fim_recorte': '2026-06-30',
        'saldo_disponivel_geral': 200.0,
        'recebidos_nao_aportados_disponiveis': [
            {
                'id': 'na_1',
                'valor_disponivel': 900.0,
                'data_recebimento': '2026-05-01',
                'proxy_terminal_atual': 0.08,
            }
        ],
        'lotes_aportados': [
            {
                'id': 'lote_a',
                'valor_liquido_resgatavel': 1600.0,
                'principal_remanescente': 1450.0,
                'data_aplicacao': '2026-02-01',
                'carencia_ate': None,
                'proxy_terminal_atual': 0.24,
            }
        ],
    }
    estado_pos_switching = {
        'data_referencia': '2026-04-30',
        'data_evento_corrente': '2026-05-02',
        'data_fim_recorte': '2026-06-30',
        'saldo_disponivel_geral': 200.0,
        'recebidos_nao_aportados_disponiveis': [
            {
                'id': 'na_1',
                'valor_disponivel': 900.0,
                'data_recebimento': '2026-05-01',
                'proxy_terminal_atual': 0.08,
            }
        ],
        'lotes_aportados': [
            {
                'id': 'lote_a_sw',
                'valor_liquido_resgatavel': 1565.0,
                'principal_remanescente': 1565.0,
                'data_aplicacao': '2026-04-30',
                'carencia_ate': None,
                'proxy_terminal_atual': 0.05,
            }
        ],
    }
    plano_switch = {
        'id_acao': 'sw_demo_001',
        'rotulo': 'lote_a -> produto_melhor',
        'classe_comparador_hibrido': 'vencedor_terminal',
        'promovivel_hibrido': True,
        'estado_pos_switching': estado_pos_switching,
        'custo_fiscal_switching_total': 35.0,
        'perda_liquidez_switching_total': 0.0,
        'delta_perda_terminal_vs_baseline': -22.0,
        'motivo_comparador_hibrido': 'cenário sintético promotível para validação funcional do alocador',
    }
    return {'pagamento': pagamento, 'estado_baseline': estado_baseline, 'plano_switch': plano_switch}


def main() -> int:
    payload = _cenarios_base()
    sem_switch = alocar_pagamento_terminal_v1(
        pagamento=payload['pagamento'],
        estado_global=payload['estado_baseline'],
        config={},
        plano_switching_candidato=None,
        permitir_combinacao_minima=True,
        limite_fontes_candidatas=None,
    )
    com_switch = alocar_pagamento_terminal_v1(
        pagamento=payload['pagamento'],
        estado_global=payload['estado_baseline'],
        config={},
        plano_switching_candidato=payload['plano_switch'],
        permitir_combinacao_minima=True,
        limite_fontes_candidatas=None,
    )
    bloqueado = alocar_pagamento_terminal_v1(
        pagamento=payload['pagamento'],
        estado_global=payload['estado_baseline'],
        config={},
        plano_switching_candidato={**payload['plano_switch'], 'classe_comparador_hibrido': 'vencedor_operacional', 'promovivel_hibrido': False},
        permitir_combinacao_minima=True,
        limite_fontes_candidatas=None,
    )

    resumo = {
        'status': 'ok',
        'versao': 'V137',
        'sem_switching': {
            'melhor_acao_pagamento': sem_switch.get('melhor_acao_pagamento'),
            'fonte_principal_tipo': sem_switch.get('fonte_principal_tipo'),
            'score_terminal_comparativo': sem_switch.get('score_terminal_comparativo'),
        },
        'com_switching_elegivel': {
            'melhor_acao_pagamento': com_switch.get('melhor_acao_pagamento'),
            'fonte_principal_tipo': com_switch.get('fonte_principal_tipo'),
            'score_terminal_comparativo': com_switch.get('score_terminal_comparativo'),
            'resumo_comparacao_switching': com_switch.get('resumo_comparacao_switching'),
            'metadados_escolhidos': com_switch.get('metadados_escolhidos'),
        },
        'switching_bloqueado': {
            'melhor_acao_pagamento': bloqueado.get('melhor_acao_pagamento'),
            'fonte_principal_tipo': bloqueado.get('fonte_principal_tipo'),
            'resumo_comparacao_switching': bloqueado.get('resumo_comparacao_switching'),
        },
        'assertivas': {
            'considera_cenario_switching_promovivel': com_switch.get('resumo_comparacao_switching', {}).get('candidatos_switching_elegivel', 0) >= 1,
            'bloqueia_switching_nao_promovivel': bloqueado.get('resumo_comparacao_switching', {}).get('candidatos_switching_elegivel', 0) == 0,
        },
    }

    JSON_OUT.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding='utf-8')
    linhas = [
        '# ALOCADOR PAGAMENTOS TERMINAL V137',
        '',
        '- Objetivo: validar a primeira versão funcional do `alocador_pagamentos_terminal_v1` com comparação explícita entre saldo disponível, lote não aportado, lote aportado e cenário com switching elegível filtrado pelo comparador híbrido.',
        '',
        '## Resultado sintético',
        '',
        f"- Melhor sem switching: `{sem_switch.get('fonte_principal_tipo')}` ({sem_switch.get('melhor_acao_pagamento')})",
        f"- Melhor com switching elegível: `{com_switch.get('fonte_principal_tipo')}` ({com_switch.get('melhor_acao_pagamento')})",
        f"- Switching bloqueado: `{bloqueado.get('fonte_principal_tipo')}` ({bloqueado.get('melhor_acao_pagamento')})",
        '',
        '## Assertivas',
        '',
        f"- considera cenário com switching promovível: {resumo['assertivas']['considera_cenario_switching_promovivel']}",
        f"- bloqueia switching não promovível: {resumo['assertivas']['bloqueia_switching_nao_promovivel']}",
        '',
        '## Observação',
        '',
        '- Esta validação é sintética e estrutural; o objetivo aqui é confirmar o contrato funcional do alocador antes da integração plena com o fluxo central de pagamentos.',
    ]
    MD_OUT.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
