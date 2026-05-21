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
from nucleo.saida_canonica import construir_saida_canonica
from nucleo.saida_canonica_controlada_v4l import construir_saida_canonica_controlada_v4l
from nucleo.saida_canonica_temporal_shadow_v4k import CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K


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
    parser = argparse.ArgumentParser(description="Audita caminho controlado V4L da saída com temporal shadow opcional.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    saida_padrao = construir_saida_canonica(contexto)
    saida_controlada_desligada = construir_saida_canonica_controlada_v4l(contexto, incluir_temporal_shadow=False)
    saida_controlada_ligada = construir_saida_canonica_controlada_v4l(contexto, incluir_temporal_shadow=True)

    auditoria_padrao = dict(saida_padrao.auditoria or {})
    auditoria_ligada_sem_bloco = _auditoria_sem_bloco_temporal(saida_controlada_ligada.auditoria or {})
    bloco = (saida_controlada_ligada.auditoria or {}).get(CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K, {})

    resultado = {
        "adaptador": "saida_canonica_controlada_v4l",
        "saida_padrao_identica": _iguais(saida_padrao, saida_controlada_desligada),
        "saida_com_shadow_temporal_tem_bloco": CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K in (saida_controlada_ligada.auditoria or {}),
        "auditoria_existente_preservada": _iguais(auditoria_padrao, auditoria_ligada_sem_bloco),
        "auditoria_acrescida_apenas_bloco_temporal_shadow": len(saida_controlada_ligada.auditoria or {}) == len(auditoria_padrao) + 1,
        "extrato_passado_identico": _iguais(saida_padrao.extrato_passado, saida_controlada_ligada.extrato_passado),
        "extrato_futuro_identico": _iguais(saida_padrao.extrato_futuro, saida_controlada_ligada.extrato_futuro),
        "switchings_identico": _iguais(saida_padrao.switchings, saida_controlada_ligada.switchings),
        "ranking_amostra_identico": _iguais(saida_padrao.ranking_amostra, saida_controlada_ligada.ranking_amostra),
        "lotes_ativos_identico": _iguais(saida_padrao.lotes_ativos, saida_controlada_ligada.lotes_ativos),
        "lotes_exauridos_identico": _iguais(saida_padrao.lotes_exauridos, saida_controlada_ligada.lotes_exauridos),
        "recebidos_atuais_identico": _iguais(saida_padrao.recebidos_atuais, saida_controlada_ligada.recebidos_atuais),
        "fechamento_atual_identico": _iguais(saida_padrao.fechamento_atual, saida_controlada_ligada.fechamento_atual),
        "resumo_recebidos_identico": _iguais(saida_padrao.resumo_recebidos, saida_controlada_ligada.resumo_recebidos),
        "versao_identica": saida_padrao.versao == saida_controlada_ligada.versao,
        "data_referencia_identica": saida_padrao.data_referencia == saida_controlada_ligada.data_referencia,
        "bloco_temporal_ok": bool(bloco.get("ok")),
        "bloco_validacao_agregador_ok": bool(bloco.get("validacao_agregador_ok")),
        "bloco_erros_bloqueantes_total": int(bloco.get("erros_bloqueantes_agregador_total") or 0),
        "bloco_extrato_passado_identico": bool(bloco.get("extrato_passado_identico")),
        "bloco_extrato_futuro_identico": bool(bloco.get("extrato_futuro_identico")),
        "bloco_lotes_normalizados_identicos": bool(bloco.get("lotes_normalizados_identicos")),
        "bloco_fonte_primaria_switching_ledger": bloco.get("fonte_primaria_switching_ledger"),
        "bloco_usa_planilha_bruta_como_fonte_primaria": bloco.get("usa_planilha_bruta_como_fonte_primaria"),
        "sem_alteracao_observavel_padrao": _iguais(saida_padrao, saida_controlada_desligada),
    }

    resultado["validacao_v4l_ok"] = all([
        resultado["saida_padrao_identica"],
        resultado["saida_com_shadow_temporal_tem_bloco"],
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
        resultado["sem_alteracao_observavel_padrao"],
    ])

    print("=== AUDITORIA SAIDA CANONICA CONTROLADA TEMPORAL SHADOW V4L ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_saida_controlada_temporal_shadow_v4l_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4l_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
