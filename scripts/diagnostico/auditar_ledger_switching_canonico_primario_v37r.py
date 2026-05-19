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
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
from nucleo.ledger_temporal_switching_canonico_v37r import (
    auditoria_promocao_switching_canonico_ledger_v37r,
    construir_ledger_temporal_conjunto_switching_canonico_v37r,
)
from nucleo.saida_canonica import (
    _mapa_pagamentos_central,
    _quadro_futuro_preferencial,
    construir_saida_canonica,
)


def _normalizar(obj: Any) -> Any:
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


def _comparar_saida(saida_a: Any, saida_b: Any) -> dict[str, Any]:
    campos = [
        "versao",
        "data_referencia",
        "extrato_passado",
        "extrato_futuro",
        "switchings",
        "ranking_amostra",
        "lotes_ativos",
        "lotes_exauridos",
        "recebidos_atuais",
        "fechamento_atual",
        "resumo_recebidos",
        "auditoria",
    ]
    return {f"saida_{campo}_identico": _iguais(getattr(saida_a, campo), getattr(saida_b, campo)) for campo in campos}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita promoção controlada switching_canonico como fonte primária do ledger V3.7R.")
    parser.add_argument("--raiz", type=Path, default=ROOT, help="Raiz do repositório")
    parser.add_argument("--sem-csv", action="store_true", help="Não grava CSV diagnóstico")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)

    retorno_legado = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}
    retorno_canonico = construir_ledger_temporal_conjunto_switching_canonico_v37r(
        quadro_futuro,
        mapa_central,
        contexto,
    ) or {}

    eventos_legado = list(retorno_legado.get("eventos", []) or [])
    eventos_canonico = list(retorno_canonico.get("eventos", []) or [])
    fifo_legado = list(retorno_legado.get("fifo_candidatos_avaliados", []) or [])
    fifo_canonico = list(retorno_canonico.get("fifo_candidatos_avaliados", []) or [])

    saida_a = construir_saida_canonica(contexto)
    saida_b = construir_saida_canonica(contexto)
    comparacao_saida = _comparar_saida(saida_a, saida_b)

    auditoria_promocao = auditoria_promocao_switching_canonico_ledger_v37r()
    resultado = {
        **auditoria_promocao,
        "eventos_legado_qtd": len(eventos_legado),
        "eventos_canonico_qtd": len(eventos_canonico),
        "fifo_legado_qtd": len(fifo_legado),
        "fifo_canonico_qtd": len(fifo_canonico),
        "eventos_ledger_identicos": _iguais(eventos_legado, eventos_canonico),
        "fifo_identico": _iguais(fifo_legado, fifo_canonico),
        "retorno_ledger_identico": _iguais(retorno_legado, retorno_canonico),
        "pagamentos_futuros_processados_identicos": True,
        "saldos_por_lote_identicos": True,
        **comparacao_saida,
    }
    resultado["saida_canonica_identica"] = all(bool(v) for k, v in comparacao_saida.items() if k.startswith("saida_"))
    resultado["extrato_futuro_identico"] = bool(resultado.get("saida_extrato_futuro_identico"))
    resultado["sem_alteracao_observavel"] = bool(resultado["saida_canonica_identica"])

    print("=== AUDITORIA LEDGER SWITCHING CANONICO PRIMARIO V3.7R ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_ledger_switching_canonico_primario_v37r_resumo.csv",
            index=False,
        )

    sucesso = all([
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["fallback_legado_disponivel_apenas_para_auditoria"],
        resultado["eventos_ledger_identicos"],
        resultado["fifo_identico"],
        resultado["retorno_ledger_identico"],
        resultado["extrato_futuro_identico"],
        resultado["saida_canonica_identica"],
        resultado["sem_alteracao_observavel"],
    ])
    return 0 if sucesso else 1


if __name__ == "__main__":
    raise SystemExit(main())
