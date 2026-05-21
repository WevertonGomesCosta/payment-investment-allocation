from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

def _resolver_raiz_repositorio() -> Path:
    atual = Path(__file__).resolve()
    for pai in atual.parents:
        if (pai / "nucleo").is_dir() and (pai / "scripts").is_dir():
            return pai
    raise RuntimeError("raiz_repositorio_nao_encontrada")


ROOT = _resolver_raiz_repositorio()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
from nucleo.pacote_estado_temporal import construir_pacote_estado_temporal_shadow
from nucleo.pacote_ledger_temporal import construir_pacote_ledger_temporal_shadow
from nucleo.pacote_ledger_temporal_operacional import construir_pacote_ledger_temporal_operacional_shadow
from nucleo.pacote_replay_passado import construir_pacote_replay_passado_shadow
from nucleo.saida_canonica import _mapa_pagamentos_central, _quadro_futuro_preferencial, construir_saida_canonica


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
    parser = argparse.ArgumentParser(description="Audita PacoteEstadoTemporal shadow V4F.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    pacote_replay = construir_pacote_replay_passado_shadow(getattr(contexto, "replay_passado", None), contexto=contexto)
    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    retorno_legado = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}
    pacote_ledger_shadow = construir_pacote_ledger_temporal_shadow(
        quadro_futuro,
        mapa_central,
        contexto,
        retorno_legado=retorno_legado,
    )
    pacote_ledger_operacional = construir_pacote_ledger_temporal_operacional_shadow(
        retorno_legado,
        pacote_ledger_shadow,
        contexto=contexto,
    )
    pacote_estado = construir_pacote_estado_temporal_shadow(
        pacote_replay,
        pacote_ledger_operacional,
        contexto=contexto,
    )

    saida_antes = construir_saida_canonica(contexto)
    saida_depois = construir_saida_canonica(contexto)

    auditoria = pacote_estado.auditoria_estado_temporal or {}
    validacao = pacote_estado.validacao_estado_temporal or {}

    resultado = {
        "adaptador": "pacote_estado_temporal_shadow",
        "versao": pacote_estado.versao,
        "modo_execucao": pacote_estado.modo_execucao,
        "data_referencia_presente": pacote_estado.data_referencia not in (None, ""),
        "estado_lotes_por_data_total": len(pacote_estado.estado_lotes_por_data or []),
        "estado_lotes_final_total": len(pacote_estado.estado_lotes_final or []),
        "saldos_por_lote_total": len(pacote_estado.saldos_por_lote or []),
        "saldos_disponiveis_por_data_total": len(pacote_estado.saldos_disponiveis_por_data or []),
        "fontes_disponiveis_por_data_total": len(pacote_estado.fontes_disponiveis_por_data or []),
        "vencimentos_por_data_total": len(pacote_estado.vencimentos_por_data or []),
        "migracoes_por_data_total": len(pacote_estado.migracoes_por_data or []),
        "campos_vazios_auditados": auditoria.get("campos_vazios_auditados"),
        "usa_pacote_replay_passado_shadow": auditoria.get("usa_pacote_replay_passado_shadow"),
        "usa_pacote_ledger_temporal_operacional_shadow": auditoria.get("usa_pacote_ledger_temporal_operacional_shadow"),
        "nao_altera_replay_efetivo": auditoria.get("nao_altera_replay_efetivo"),
        "nao_altera_ledger_efetivo": auditoria.get("nao_altera_ledger_efetivo"),
        "nao_altera_saida_canonica": auditoria.get("nao_altera_saida_canonica"),
        "validacao_ok": bool(validacao.get("ok")),
        "erros_bloqueantes_total": len(validacao.get("erros_bloqueantes", []) or []),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
    }

    resultado["validacao_v4f_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["estado_lotes_por_data_total"] > 0,
        resultado["estado_lotes_final_total"] > 0,
        resultado["saldos_por_lote_total"] > 0,
        resultado["fontes_disponiveis_por_data_total"] > 0,
        resultado["usa_pacote_replay_passado_shadow"] is True,
        resultado["usa_pacote_ledger_temporal_operacional_shadow"] is True,
        resultado["nao_altera_replay_efetivo"] is True,
        resultado["nao_altera_ledger_efetivo"] is True,
        resultado["nao_altera_saida_canonica"] is True,
        resultado["validacao_ok"],
        resultado["erros_bloqueantes_total"] == 0,
        resultado["saida_canonica_identica_dupla_execucao"],
    ])

    print("=== AUDITORIA PACOTE ESTADO TEMPORAL SHADOW V4F ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_pacote_estado_temporal_v4f_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4f_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
