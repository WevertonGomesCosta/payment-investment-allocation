"""Inspeciona a alocação intradiária por pacote v1."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline

COLUNAS_EXIBICAO = [
    'data_pagamento', 'descricao_pagamento', 'valor_pagamento', 'classe_pagamento_operacional',
    'politica_pacote_id', 'ordem_no_pacote', 'lote_final_central_v108', 'lote_final_pacote',
    'status_pacote', 'deficit_liquido_total_pacote', 'mudou_vs_central_v108',
]


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.alocacao_intradiaria_pacote_v1
    quadro = pacote.quadro_alocacao_intradiaria_pacote
    resumo_pacotes = pacote.quadro_resumo_pacotes
    auditoria = pacote.auditoria
    resumo = auditoria.get('resumo', {})

    print('=== ALOCAÇÃO INTRADIÁRIA POR PACOTE V1 ===')
    print(f"data_referencia: {contexto.execucao.data_referencia}")
    print(f"total_pagamentos_auditados: {resumo.get('total_pagamentos_auditados', 0)}")
    print(f"datas_com_pacote: {resumo.get('datas_com_pacote', 0)}")
    print(f"politicas_avaliadas_total: {resumo.get('politicas_avaliadas_total', 0)}")
    print(f"pagamentos_cobertos_integral_pacote: {resumo.get('pagamentos_cobertos_integral_pacote', 0)}")
    print(f"pagamentos_sem_cobertura_integral_pacote: {resumo.get('pagamentos_sem_cobertura_integral_pacote', 0)}")
    print(f"violacoes_pagamentos_protegida_pacote: {resumo.get('violacoes_pagamentos_protegida_pacote', 0)}")
    print(f"deficit_liquido_total_pacote: {resumo.get('deficit_liquido_total_pacote', 0.0)}")
    print(f"mudancas_vs_central_v108: {resumo.get('mudancas_vs_central_v108', 0)}")
    print(f"primeira_sem_cobertura: {resumo.get('primeira_sem_cobertura_data')} | {resumo.get('primeira_sem_cobertura_pagamento')}")
    print(f"primeira_violacao_protegida: {resumo.get('primeira_violation_protegida_data')} | {resumo.get('primeira_violation_protegida_pagamento')}")

    print('\n--- RESUMO DOS PACOTES ---')
    if len(resumo_pacotes):
        print(resumo_pacotes.head(20).to_string(index=False))

    print('\n--- QUADRO DO PACOTE (AMOSTRA) ---')
    if len(quadro):
        print(quadro[COLUNAS_EXIBICAO].head(40).to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
