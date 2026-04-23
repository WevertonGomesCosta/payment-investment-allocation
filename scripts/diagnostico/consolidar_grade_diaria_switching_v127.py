from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

import json
from pathlib import Path

from scripts.diagnostico import inspecionar_grade_diaria_switching_v127 as grade

SAIDA_JSON = Path(RAIZ) / 'saidas' / 'operacional' / 'grade_diaria_switching_v127_consolidado.json'
SAIDA_MD = Path(RAIZ) / 'relatorios' / 'atuais' / 'AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V127.md'


def main() -> int:
    base = Path(RAIZ) / 'saidas' / 'operacional'
    chunks = sorted(base.glob('grade_diaria_switching_v127_chunk_*.json'))
    if not chunks:
        print('nenhum_chunk_encontrado')
        return 1
    dados = []
    for p in chunks:
        dados.append(json.loads(p.read_text(encoding='utf-8')))
    meta = {k: v for k, v in dados[0].items() if k != 'resultados'}
    meta['resultados'] = []
    for bloco in dados:
        meta['resultados'].extend(bloco['resultados'])
    meta['resultados'].sort(key=lambda x: (x['data_solicitada'], x['familia'], x['rotulo']))
    SAIDA_JSON.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    SAIDA_MD.write_text(grade._formatar_relatorio(meta), encoding='utf-8')
    print(f'consolidado_salvo_em={SAIDA_JSON}')
    print(f'relatorio_salvo_em={SAIDA_MD}')
    print(f'dias_consolidados={len({x["data_solicitada"] for x in meta["resultados"]})}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
