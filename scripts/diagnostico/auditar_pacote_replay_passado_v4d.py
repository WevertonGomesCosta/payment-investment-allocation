from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_replay_passado import construir_pacote_replay_passado_shadow
from nucleo.saida_canonica import construir_saida_canonica


def _normalizar(obj: Any) -> Any:
    if isinstance(obj, pd.DataFrame):
        return [_normalizar(x) for x in obj.to_dict(orient="records")]
    if isinstance(obj, dict):
        return {str(k): _normalizar(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, list):
        return [_normalizar(v) for v in obj]
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


def _serializar(obj: Any) -> str:
    return json.dumps(_normalizar(obj), ensure_ascii=False, sort_keys=True, default=str)


def _iguais(a: Any, b: Any) -> bool:
    return _serializar(a) == _serializar(b)


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)
        linhas.append({"metrica": chave, "valor": valor})
    return linhas


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita PacoteReplayPassado shadow V4D.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    replay = getattr(contexto, "replay_passado", None)
    pacote = construir_pacote_replay_passado_shadow(replay, contexto=contexto)

    saida_antes = construir_saida_canonica(contexto)
    saida_depois = construir_saida_canonica(contexto)

    log_origem = getattr(replay, "log_passado", None)
    estado_origem = getattr(replay, "estado_lotes_passado", None)
    auditoria_origem = getattr(replay, "auditoria", {}) or {}
    validacao_origem = getattr(replay, "validacao", {}) or {}

    resultado = {
        "adaptador": "pacote_replay_passado_shadow",
        "versao": pacote.versao,
        "modo_execucao": pacote.modo_execucao,
        "data_referencia_presente": pacote.data_referencia not in (None, ""),
        "qtd_lotes_origem": len(getattr(replay, "lotes_apos_replay", []) or []),
        "qtd_lotes_pacote": len(pacote.lotes_apos_replay or []),
        "lotes_apos_replay_identicos": _iguais(getattr(replay, "lotes_apos_replay", []) or [], pacote.lotes_apos_replay or []),
        "log_passado_qtd_origem": int(len(log_origem)) if hasattr(log_origem, "__len__") else 0,
        "log_movimentos_passados_qtd_pacote": int(len(pacote.log_movimentos_passados)) if hasattr(pacote.log_movimentos_passados, "__len__") else 0,
        "log_movimentos_passados_identico": _iguais(log_origem, pacote.log_movimentos_passados),
        "estado_lotes_passado_qtd_origem": int(len(estado_origem)) if hasattr(estado_origem, "__len__") else 0,
        "estado_lotes_passado_qtd_pacote": int(len(pacote.estado_lotes_passado)) if hasattr(pacote.estado_lotes_passado, "__len__") else 0,
        "estado_lotes_passado_identico": _iguais(estado_origem, pacote.estado_lotes_passado),
        "auditoria_replay_presente": bool(pacote.auditoria_replay),
        "validacao_replay_presente": bool(pacote.validacao_replay),
        "metadados_origem_presente": bool(pacote.metadados_origem),
        "auditoria_base_preservada": all(k in pacote.auditoria_replay for k in auditoria_origem.keys()),
        "validacao_base_preservada": bool(pacote.validacao_replay.get("ok", True)) == bool(validacao_origem.get("ok", True)),
        "audit_trilha_pagamentos_passados_total": len(pacote.audit_trilha_pagamentos_passados or []),
        "nao_altera_replay_efetivo": bool(pacote.metadados_origem.get("nao_altera_replay_efetivo")),
        "nao_altera_saida_canonica": bool(pacote.metadados_origem.get("nao_altera_saida_canonica")),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
        "validacao_ok": bool(pacote.validacao_replay.get("ok")),
    }

    resultado["validacao_v4d_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["qtd_lotes_origem"] == resultado["qtd_lotes_pacote"],
        resultado["lotes_apos_replay_identicos"],
        resultado["log_movimentos_passados_identico"],
        resultado["estado_lotes_passado_identico"],
        resultado["auditoria_replay_presente"],
        resultado["validacao_replay_presente"],
        resultado["metadados_origem_presente"],
        resultado["auditoria_base_preservada"],
        resultado["validacao_base_preservada"],
        resultado["nao_altera_replay_efetivo"],
        resultado["nao_altera_saida_canonica"],
        resultado["saida_canonica_identica_dupla_execucao"],
        resultado["validacao_ok"],
    ])

    print("=== AUDITORIA PACOTE REPLAY PASSADO SHADOW V4D ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_pacote_replay_passado_v4d_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4d_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
