from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_primeira_quebra_runner_futuro_shadow

ARQUIVO_XLSX = nome_auditoria_primeira_quebra_runner_futuro_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_primeira_quebra_runner_futuro_shadow('csv')


def _quadro_resumo(resumo: dict[str, object]) -> pd.DataFrame:
    registros=[]
    for k,v in resumo.items():
        registros.append({'item':k,'valor':v})
    return pd.DataFrame(registros)


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.auditoria_primeira_quebra_runner_futuro_shadow
    resumo = pacote.auditoria['resumo']
    q_pag = pacote.quadro_pagamentos_primeira_quebra.copy()
    q_lotes = pacote.quadro_lotes_primeira_quebra.copy()
    q_consumo = pacote.quadro_consumo_lote_critico.copy()
    q_traj = pacote.quadro_trajetoria_liquidez.copy()

    print('=== AUDITORIA DA PRIMEIRA QUEBRA DO RUNNER FUTURO SHADOW ===')
    for chave in [
        'data_referencia','primeira_data_quebra','pagamentos_na_primeira_quebra','lote_critico_identificado',
        'eventos_previos_com_consumo_lote_critico','liquidez_disponivel_na_primeira_quebra',
        'liquidez_bloqueada_na_primeira_quebra','primeiro_pagamento_critico',
        'valor_primeiro_pagamento_critico','valor_descoberto_no_primeiro_dia','causa_raiz_resumida','recomendacao_auditoria'
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- PAGAMENTOS DA PRIMEIRA QUEBRA ---')
    print(q_pag.to_string(index=False) if len(q_pag) else 'sem dados')
    print('\n--- LOTES NA PRIMEIRA QUEBRA ---')
    print(q_lotes.to_string(index=False) if len(q_lotes) else 'sem dados')
    print('\n--- CONSUMO DO LOTE CRITICO ANTES DA QUEBRA ---')
    print(q_consumo.to_string(index=False) if len(q_consumo) else 'sem dados')

    caminho_xlsx = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    q_pag.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        q_pag.to_excel(writer, sheet_name='Primeira_Quebra', index=False)
        q_lotes.to_excel(writer, sheet_name='Lotes_No_Dia', index=False)
        q_consumo.to_excel(writer, sheet_name='Consumo_Lote_Critico', index=False)
        q_traj.to_excel(writer, sheet_name='Trajetoria_Liquidez', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
