
from __future__ import annotations

import json
from pathlib import Path
import sys
import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_SLUG


def _saida_dir(raiz: Path) -> Path:
    out = raiz / 'saidas' / 'ranking_carteira'
    out.mkdir(parents=True, exist_ok=True)
    return out


def main() -> dict[str, str]:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO)
    ranking = contexto.ranking_carteira
    out_dir = _saida_dir(RAIZ_REPOSITORIO)
    xlsx_path = out_dir / f'ranking_carteira_estabilizado_{VERSAO_SLUG}.xlsx'
    csv_top30 = out_dir / f'top30_carteira_estabilizado_{VERSAO_SLUG}.csv'
    json_resumo = out_dir / f'resumo_ranking_carteira_estabilizado_{VERSAO_SLUG}.json'

    quadro = ranking.quadro_ranking.copy()
    top30 = ranking.top30.copy()
    destinos = ranking.quadro_destinos_switch.copy()

    resumo_df = pd.DataFrame([
        {'indicador': 'produtos_total', 'valor': ranking.resumo.get('produtos_total')},
        {'indicador': 'produtos_ativos_ranqueados', 'valor': ranking.resumo.get('produtos_ativos_ranqueados')},
        {'indicador': 'qtd_destinos_switch', 'valor': ranking.auditoria.get('qtd_destinos_switch')},
        {'indicador': 'destino_top1', 'valor': ranking.auditoria.get('destino_top1')},
        {'indicador': 'qtd_diffs_materiais_nucleo', 'valor': ranking.validacao.get('qtd_diffs_materiais_nucleo')},
        {'indicador': 'aceite_nucleo', 'valor': ranking.validacao.get('aceite_nucleo')},
    ])
    valid_df = pd.DataFrame([ranking.validacao | {'metodo': ranking.auditoria.get('metodo')}])

    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        quadro.to_excel(writer, sheet_name='Ranking_Completo', index=False)
        top30.to_excel(writer, sheet_name='Top30', index=False)
        destinos.to_excel(writer, sheet_name='Destinos_Switch', index=False)
        resumo_df.to_excel(writer, sheet_name='Resumo', index=False)
        valid_df.to_excel(writer, sheet_name='Validacao', index=False)

    top30.to_csv(csv_top30, index=False, encoding='utf-8-sig')
    json_resumo.write_text(json.dumps({'resumo': ranking.resumo, 'validacao': ranking.validacao, 'auditoria': ranking.auditoria}, ensure_ascii=False, indent=2), encoding='utf-8')

    print('ranking carteira estabilizado')
    print(resumo_df.to_string(index=False))
    print('\ntop 10 do ranking prazo')
    print(top30[['Rank_Consolidado_Prazo_Ativos', 'Nome', 'Bucket_SAOF', 'Score Final Prazo']].head(10).to_string(index=False))
    return {'xlsx': str(xlsx_path), 'csv_top30': str(csv_top30), 'json_resumo': str(json_resumo)}


if __name__ == '__main__':
    main()
