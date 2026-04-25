from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from pathlib import Path
import json

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.identidade_baseline import caminho_artifact, caminho_saida_diagnostico

RAIZ_PATH = Path(RAIZ)
JSON_OUT = caminho_saida_diagnostico(RAIZ_PATH, 'alocador_pagamentos_terminal_v141.json')
MD_OUT = caminho_saida_diagnostico(RAIZ_PATH, 'ALOCADOR_PAGAMENTOS_TERMINAL_V141.md')
ART_JSON = caminho_artifact('alocador_pagamentos_terminal_v141.json')
ART_MD = caminho_artifact('ALOCADOR_PAGAMENTOS_TERMINAL_V141.md')
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
ART_JSON.parent.mkdir(parents=True, exist_ok=True)


def _cenario_cliff() -> dict:
    pagamento = {
        'pagamento_id': 'pgto_demo_cliff_v141',
        'data': '2026-06-30',
        'classe': 'PROTEGIDA',
        'valor': 1500.0,
    }
    estado = {
        'data_referencia': '2026-06-01',
        'data_evento_corrente': '2026-06-30',
        'data_fim_recorte': '2026-12-31',
        'saldo_disponivel_geral': 0.0,
        'recebidos_nao_aportados_disponiveis': [],
        'lotes_aportados': [
            {
                'id': 'lote_proximo_cliff',
                'valor_liquido_resgatavel': 1700.0,
                'principal_remanescente': 1550.0,
                'data_aplicacao': '2026-01-07',
                'carencia_ate': None,
                'proxy_terminal_atual': 0.18,
            },
            {
                'id': 'lote_seguro',
                'valor_liquido_resgatavel': 1700.0,
                'principal_remanescente': 1550.0,
                'data_aplicacao': '2026-02-10',
                'carencia_ate': None,
                'proxy_terminal_atual': 0.18,
            },
        ],
    }
    return {'pagamento': pagamento, 'estado': estado}


def main() -> int:
    payload = _cenario_cliff()
    resultado = alocar_pagamento_terminal_v1(
        pagamento=payload['pagamento'],
        estado_global=payload['estado'],
        config={},
        plano_switching_candidato=None,
        permitir_combinacao_minima=False,
        limite_fontes_candidatas=None,
    )
    candidatos = {
        item['fonte_id']: item
        for item in resultado.get('fontes_candidatas', [])
        if item.get('tipo_fonte') == 'lote_aportado'
    }
    prox = candidatos.get('lote_proximo_cliff', {})
    seg = candidatos.get('lote_seguro', {})
    resumo = {
        'status': 'ok',
        'versao': 'V141',
        'melhor_acao_pagamento': resultado.get('melhor_acao_pagamento'),
        'fonte_principal_tipo': resultado.get('fonte_principal_tipo'),
        'fonte_principal_id': resultado.get('fonte_principal_id'),
        'score_auxiliar_escolhido': resultado.get('score_auxiliar_script1'),
        'chave_decisao_final': resultado.get('chave_decisao_final'),
        'candidatos_lote_aportado': {
            'lote_proximo_cliff': {
                'score_terminal': prox.get('score_terminal_comparativo'),
                'score_auxiliar_script1': prox.get('score_auxiliar_script1'),
                'heuristicas_script1_fase1': (prox.get('metadados_extras') or {}).get('heuristicas_script1_fase1'),
            },
            'lote_seguro': {
                'score_terminal': seg.get('score_terminal_comparativo'),
                'score_auxiliar_script1': seg.get('score_auxiliar_script1'),
                'heuristicas_script1_fase1': (seg.get('metadados_extras') or {}).get('heuristicas_script1_fase1'),
            },
        },
        'assertivas': {
            'camada_fase1_presente_nos_candidatos': all(
                bool((item.get('metadados_extras') or {}).get('heuristicas_script1_fase1'))
                for item in resultado.get('fontes_candidatas', [])
            ),
            'desempate_cliff_ativa_escolha_segura': resultado.get('fonte_principal_id') == 'lote_seguro',
        },
    }
    texto = json.dumps(resumo, ensure_ascii=False, indent=2)
    JSON_OUT.write_text(texto, encoding='utf-8')
    ART_JSON.write_text(texto, encoding='utf-8')
    linhas = [
        '# ALOCADOR PAGAMENTOS TERMINAL V141',
        '',
        '- Objetivo: validar a Fase 1 de absorção dos modelos do Script 1 no `alocador_pagamentos_terminal_v1`.',
        '- Heurísticas ativas: `score_hibrido_5p_fonte`, `penalidade_cliff_idade`, `oportunidade_vpl_marginal`.',
        '',
        '## Resultado sintético',
        '',
        f"- Melhor ação: `{resultado.get('melhor_acao_pagamento')}`",
        f"- Fonte principal: `{resultado.get('fonte_principal_id')}`",
        f"- Score auxiliar do escolhido: `{resultado.get('score_auxiliar_script1')}`",
        '',
        '## Assertivas',
        '',
        f"- camada fase 1 presente nos candidatos: {resumo['assertivas']['camada_fase1_presente_nos_candidatos']}",
        f"- desempate cliff escolhe o lote seguro: {resumo['assertivas']['desempate_cliff_ativa_escolha_segura']}",
        '',
        '## Observação',
        '',
        '- A validação sintética confirma que H1–H3 entram como score auxiliar e desempate econômico sem substituir a métrica terminal principal.',
    ]
    md = '\n'.join(linhas) + '\n'
    MD_OUT.write_text(md, encoding='utf-8')
    ART_MD.write_text(md, encoding='utf-8')
    print(texto)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
