from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import caminho_saida_operacional, nome_auditoria_casos_criticos_runner_futuro_shadow

ARQUIVO_XLSX = nome_auditoria_casos_criticos_runner_futuro_shadow('xlsx')
ARQUIVO_CSV = nome_auditoria_casos_criticos_runner_futuro_shadow('csv')


def _quadro_resumo(resumo: dict[str, object]) -> pd.DataFrame:
    registros = []
    for chave, valor in resumo.items():
        if isinstance(valor, dict):
            for subchave, subvalor in valor.items():
                registros.append({'grupo': chave, 'item': str(subchave), 'valor': subvalor})
        else:
            registros.append({'grupo': 'geral', 'item': chave, 'valor': valor})
    return pd.DataFrame(registros)


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    pacote = contexto.auditoria_runner_futuro_shadow
    resumo = pacote.auditoria['resumo']
    sem_cob = pacote.quadro_sem_cobertura.copy()
    multifonte = pacote.quadro_multifonte.copy()
    datas = pacote.quadro_datas_criticas.copy()

    print('=== AUDITORIA DOS CASOS CRÍTICOS DO RUNNER FUTURO SHADOW ===')
    for chave in [
        'data_referencia',
        'total_pagamentos_benchmark',
        'pagamentos_sem_cobertura_integral_shadow',
        'datas_criticas_com_sem_cobertura',
        'primeira_data_sem_cobertura',
        'valor_total_descoberto_shadow',
        'pagamentos_multifonte_shadow',
        'multifonte_totalmente_cobertos',
        'multifonte_sem_cobertura',
        'recomendacao_auditoria',
        'justificativa_recomendacao',
    ]:
        print(f"{chave}: {resumo.get(chave)}")
    print('\n--- MOTIVOS DE SEM COBERTURA ---')
    print(resumo.get('motivos_sem_cobertura'))
    print('\n--- AMOSTRA SEM COBERTURA ---')
    print(sem_cob.head(25).to_string(index=False) if len(sem_cob) else 'sem dados')
    print('\n--- SUBBLOCO MULTIFONTE ---')
    print(multifonte.to_string(index=False) if len(multifonte) else 'sem dados')

    caminho_xlsx = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_XLSX)
    caminho_csv = caminho_saida_operacional(RAIZ_REPOSITORIO, ARQUIVO_CSV)
    caminho_xlsx.parent.mkdir(parents=True, exist_ok=True)
    sem_cob.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
    with pd.ExcelWriter(caminho_xlsx, engine='openpyxl') as writer:
        _quadro_resumo(resumo).to_excel(writer, sheet_name='Resumo', index=False)
        sem_cob.to_excel(writer, sheet_name='Sem_Cobertura', index=False)
        datas.to_excel(writer, sheet_name='Datas_Criticas', index=False)
        multifonte.to_excel(writer, sheet_name='Subbloco_Multifonte', index=False)
    print(f"xlsx: {caminho_xlsx}")
    print(f"csv: {caminho_csv}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
