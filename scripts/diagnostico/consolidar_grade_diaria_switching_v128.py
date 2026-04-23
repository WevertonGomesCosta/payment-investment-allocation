from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from scripts.diagnostico import inspecionar_grade_diaria_switching_v127 as grade

SAIDA_JSON = Path(RAIZ) / "saidas" / "operacional" / "grade_diaria_switching_v128_consolidado.json"
SAIDA_MD = Path(RAIZ) / "relatorios" / "atuais" / "AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V128.md"


def main() -> int:
    base = Path(RAIZ) / "saidas" / "operacional"
    chunks = sorted(base.glob("grade_diaria_switching_v127_chunk_*.json"), key=lambda p: int(re.search(r"_(\d+)\.json$", p.name).group(1)))
    if not chunks:
        print("nenhum_chunk_encontrado")
        return 1
    blocos = [json.loads(p.read_text(encoding="utf-8")) for p in chunks]
    meta = {k: v for k, v in blocos[0].items() if k != "resultados"}
    resultados = []
    for bloco in blocos:
        resultados.extend(bloco["resultados"])
    resultados.sort(key=lambda x: (x["data_solicitada"], x["familia"], x["rotulo"]))
    inicio = date.fromisoformat(meta["data_referencia"])
    fim_horizonte = date.fromisoformat(meta["data_fim"])
    fim_auditado = inicio
    for bloco in blocos:
        off = int(bloco.get("start_offset") or 0)
        max_dias = int(bloco.get("max_dias_executados") or 0)
        if max_dias > 0:
            candidato = inicio + timedelta(days=off + max_dias - 1)
            if candidato > fim_auditado:
                fim_auditado = candidato
    if fim_auditado > fim_horizonte:
        fim_auditado = fim_horizonte
    datas_auditadas = []
    d = inicio
    while d <= fim_auditado:
        datas_auditadas.append(d.isoformat())
        d += timedelta(days=1)
    datas_resultado = sorted({r["data_solicitada"] for r in resultados})
    vencedoras = sorted({r["data_solicitada"] for r in resultados if r["continua_vencedor_central"]})
    payload = {
        "data_referencia": meta["data_referencia"],
        "data_fim_horizonte": meta["data_fim"],
        "data_fim_auditada": fim_auditado.isoformat(),
        "quantidade_pagamentos": meta["quantidade_pagamentos"],
        "total_chunks": len(blocos),
        "dias_auditados_total": len(datas_auditadas),
        "dias_com_cenarios_gerados": len(datas_resultado),
        "dias_sem_cenarios_gerados": len(datas_auditadas) - len(datas_resultado),
        "primeira_data_com_cenario": datas_resultado[0] if datas_resultado else None,
        "ultima_data_com_cenario": datas_resultado[-1] if datas_resultado else None,
        "primeira_data_vencedora": vencedoras[0] if vencedoras else None,
        "ultima_data_vencedora": vencedoras[-1] if vencedoras else None,
        "datas_auditadas": datas_auditadas,
        "resultados": resultados,
    }
    SAIDA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    # o markdown detalhado é mantido pela rotina externa desta baseline
    print(f"consolidado_salvo_em={SAIDA_JSON}")
    print(f"dias_auditados_total={payload['dias_auditados_total']}")
    print(f"dias_com_cenarios={payload['dias_com_cenarios_gerados']}")
    print(f"ultima_data_vencedora={payload['ultima_data_vencedora']}")
    print(f"ultima_data_com_cenario={payload['ultima_data_com_cenario']}")
    print(f"relatorio_esperado_em={SAIDA_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
