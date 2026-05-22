from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQ_GERAR = ROOT / 'nucleo' / 'gerar_planilha_operacional.py'
ARQ_SAIDA = ROOT / 'nucleo' / 'saida_observavel.py'


def main() -> None:
    gerar = ARQ_GERAR.read_text(encoding='utf-8')
    saida = ARQ_SAIDA.read_text(encoding='utf-8')
    res = {
        'gerar_planilha_operacional_consumindo_pacote': 'pacote_consolidado' in gerar and 'construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal=pacote_consolidado)' in gerar,
        'saida_observavel_sem_fallback_silencioso_sem_pacote': 'saida_observavel_requer_pacote_saida_observavel_temporal_na_V4W' in saida,
        'funcoes_publicas_criticas_exigem_ou_recebem_pacote': 'def construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal' in saida and 'def construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal' in saida,
    }
    res['validacao_v4w_ok'] = all(res.values())
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
