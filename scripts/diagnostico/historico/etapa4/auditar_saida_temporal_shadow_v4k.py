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
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_canonica_temporal_shadow_v4k import (
    CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K,
    construir_saida_canonica_com_temporal_shadow_v4k,
)


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


def _auditoria_sem_bloco_temporal(auditoria: dict[str, Any]) -> dict[str, Any]:
    saida = dict(auditoria or {})
    saida.pop(CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K, None)
    return saida


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)
        linhas.append({"metrica": chave, "valor": valor})
    return linhas


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita bloco temporal shadow V4K na auditoria da saída.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    saida_base = construir_saida_canonica(contexto)
    saida_shadow = construir_saida_canonica_com_temporal_shadow_v4k(contexto)
    bloco = (saida_shadow.auditoria or {}).get(CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K, {})

    auditoria_base = dict(saida_base.auditoria or {})
    auditoria_shadow_sem_bloco = _auditoria_sem_bloco_temporal(saida_shadow.auditoria or {})

    resultado = {
        "adaptador": "saida_canonica_temporal_shadow_v4k",
        "bloco_temporal_shadow_presente": CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K in (saida_shadow.auditoria or {}),
        "auditoria_existente_preservada": _iguais(auditoria_base, auditoria_shadow_sem_bloco),
        "auditoria_acrescida_apenas_bloco_temporal_shadow": len(saida_shadow.auditoria or {}) == len(auditoria_base) + 1,
        "extrato_passado_identico": _iguais(saida_base.extrato_passado, saida_shadow.extrato_passado),
        "extrato_futuro_identico": _iguais(saida_base.extrato_futuro, saida_shadow.extrato_futuro),
        "switchings_identico": _iguais(saida_base.switchings, saida_shadow.switchings),
        "ranking_amostra_identico": _iguais(saida_base.ranking_amostra, saida_shadow.ranking_amostra),
        "lotes_ativos_identico": _iguais(saida_base.lotes_ativos, saida_shadow.lotes_ativos),
        "lotes_exauridos_identico": _iguais(saida_base.lotes_exauridos, saida_shadow.lotes_exauridos),
        "recebidos_atuais_identico": _iguais(saida_base.recebidos_atuais, saida_shadow.recebidos_atuais),
        "fechamento_atual_identico": _iguais(saida_base.fechamento_atual, saida_shadow.fechamento_atual),
        "resumo_recebidos_identico": _iguais(saida_base.resumo_recebidos, saida_shadow.resumo_recebidos),
        "versao_identica": saida_base.versao == saida_shadow.versao,
        "data_referencia_identica": saida_base.data_referencia == saida_shadow.data_referencia,
        "bloco_temporal_ok": bool(bloco.get("ok")),
        "bloco_validacao_agregador_ok": bool(bloco.get("validacao_agregador_ok")),
        "bloco_erros_bloqueantes_total": int(bloco.get("erros_bloqueantes_agregador_total") or 0),
        "bloco_extrato_passado_identico": bool(bloco.get("extrato_passado_identico")),
        "bloco_extrato_futuro_identico": bool(bloco.get("extrato_futuro_identico")),
        "bloco_lotes_normalizados_identicos": bool(bloco.get("lotes_normalizados_identicos")),
        "bloco_fonte_primaria_switching_ledger": bloco.get("fonte_primaria_switching_ledger"),
        "bloco_usa_planilha_bruta_como_fonte_primaria": bloco.get("usa_planilha_bruta_como_fonte_primaria"),
        "sem_alteracao_observavel": bool(bloco.get("sem_alteracao_observavel")),
    }

    resultado["validacao_v4k_ok"] = all([
        resultado["bloco_temporal_shadow_presente"],
        resultado["auditoria_existente_preservada"],
        resultado["auditoria_acrescida_apenas_bloco_temporal_shadow"],
        resultado["extrato_passado_identico"],
        resultado["extrato_futuro_identico"],
        resultado["switchings_identico"],
        resultado["ranking_amostra_identico"],
        resultado["lotes_ativos_identico"],
        resultado["lotes_exauridos_identico"],
        resultado["recebidos_atuais_identico"],
        resultado["fechamento_atual_identico"],
        resultado["resumo_recebidos_identico"],
        resultado["versao_identica"],
        resultado["data_referencia_identica"],
        resultado["bloco_temporal_ok"],
        resultado["bloco_validacao_agregador_ok"],
        resultado["bloco_erros_bloqueantes_total"] == 0,
        resultado["bloco_extrato_passado_identico"],
        resultado["bloco_extrato_futuro_identico"],
        resultado["bloco_lotes_normalizados_identicos"],
        resultado["bloco_fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["bloco_usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["sem_alteracao_observavel"],
    ])

    print("=== AUDITORIA SAIDA CANONICA TEMPORAL SHADOW V4K ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_saida_temporal_shadow_v4k_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4k_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
