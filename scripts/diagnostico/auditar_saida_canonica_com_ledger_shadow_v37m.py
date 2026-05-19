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
from nucleo.saida_canonica_ledger_shadow import (
    BLOCO_AUDITORIA_LEDGER_SHADOW_V37M,
    construir_saida_canonica_com_ledger_shadow_opcional,
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


def _comparar_saida(saida_base: Any, saida_shadow: Any) -> dict[str, Any]:
    campos_observaveis = [
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
    ]
    comparacao = {}
    for campo in campos_observaveis:
        comparacao[f"{campo}_identico"] = _iguais(getattr(saida_base, campo), getattr(saida_shadow, campo))
        valor = getattr(saida_base, campo)
        if isinstance(valor, list):
            comparacao[f"{campo}_qtd_base"] = len(valor)
            comparacao[f"{campo}_qtd_shadow"] = len(getattr(saida_shadow, campo))

    aud_base = dict(getattr(saida_base, "auditoria", {}) or {})
    aud_shadow = dict(getattr(saida_shadow, "auditoria", {}) or {})
    bloco_shadow = aud_shadow.pop(BLOCO_AUDITORIA_LEDGER_SHADOW_V37M, None)
    comparacao["auditoria_sem_bloco_shadow_identica"] = _iguais(aud_base, aud_shadow)
    comparacao["bloco_shadow_presente"] = isinstance(bloco_shadow, dict)
    comparacao["bloco_shadow_validacao_ok"] = bool((bloco_shadow or {}).get("validacao_ok"))
    comparacao["bloco_shadow_equivalente_eventos"] = bool((bloco_shadow or {}).get("equivalente_qtd_eventos_saida_vs_shadow"))
    comparacao["bloco_shadow_equivalente_fifo"] = bool((bloco_shadow or {}).get("equivalente_qtd_fifo_saida_vs_shadow"))
    comparacao["qtd_eventos_temporais_shadow"] = (bloco_shadow or {}).get("qtd_eventos_temporais_shadow")
    comparacao["qtd_fifo_candidatos_shadow"] = (bloco_shadow or {}).get("qtd_fifo_candidatos_shadow")
    comparacao["usa_contexto_amplo"] = (bloco_shadow or {}).get("usa_contexto_amplo")
    comparacao["usa_planilha_bruta"] = (bloco_shadow or {}).get("usa_planilha_bruta")
    comparacao["usa_switching_shadow"] = (bloco_shadow or {}).get("usa_switching_shadow")
    comparacao["usa_pos_injetado"] = (bloco_shadow or {}).get("usa_pos_injetado")
    return comparacao


def _linhas_resumo(comparacao: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"metrica": k, "valor": v} for k, v in comparacao.items()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita saída canônica com ledger shadow opcional V3.7M.")
    parser.add_argument("--raiz", type=Path, default=ROOT, help="Raiz do repositório")
    parser.add_argument("--sem-csv", action="store_true", help="Não grava CSV diagnóstico")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    saida_base = construir_saida_canonica(contexto)
    saida_shadow_desligado = construir_saida_canonica_com_ledger_shadow_opcional(
        contexto,
        ativar_ledger_shadow=False,
    )
    saida_shadow_ligado = construir_saida_canonica_com_ledger_shadow_opcional(
        contexto,
        ativar_ledger_shadow=True,
    )

    comparacao_desligado = _comparar_saida(saida_base, saida_shadow_desligado)
    comparacao_ligado = _comparar_saida(saida_base, saida_shadow_ligado)

    resumo = {f"desligado_{k}": v for k, v in comparacao_desligado.items()}
    resumo.update({f"ligado_{k}": v for k, v in comparacao_ligado.items()})

    print("=== AUDITORIA SAIDA CANONICA COM LEDGER SHADOW V3.7M ===")
    for linha in _linhas_resumo(resumo):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resumo)).to_csv(
            saida_dir / "auditoria_saida_canonica_com_ledger_shadow_v37m_resumo.csv",
            index=False,
        )

    campos_observaveis = [
        "versao_identico",
        "data_referencia_identico",
        "extrato_passado_identico",
        "extrato_futuro_identico",
        "switchings_identico",
        "ranking_amostra_identico",
        "lotes_ativos_identico",
        "lotes_exauridos_identico",
        "recebidos_atuais_identico",
        "fechamento_atual_identico",
        "resumo_recebidos_identico",
    ]
    sucesso_desligado = all(bool(comparacao_desligado.get(c)) for c in campos_observaveis)
    sucesso_ligado = all(bool(comparacao_ligado.get(c)) for c in campos_observaveis)
    sucesso_ligado = sucesso_ligado and bool(comparacao_ligado.get("auditoria_sem_bloco_shadow_identica"))
    sucesso_ligado = sucesso_ligado and bool(comparacao_ligado.get("bloco_shadow_presente"))
    sucesso_ligado = sucesso_ligado and bool(comparacao_ligado.get("bloco_shadow_validacao_ok"))
    sucesso_ligado = sucesso_ligado and bool(comparacao_ligado.get("bloco_shadow_equivalente_eventos"))
    sucesso_ligado = sucesso_ligado and bool(comparacao_ligado.get("bloco_shadow_equivalente_fifo"))

    return 0 if (sucesso_desligado and sucesso_ligado) else 1


if __name__ == "__main__":
    raise SystemExit(main())
