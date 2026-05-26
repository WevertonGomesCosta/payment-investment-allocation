from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.contexto_saida_canonica_compat import (
    ComponentesTransicionaisSaidaCanonica,
    construir_contexto_saida_canonica_compat,
)
from nucleo.identidade_baseline import VERSAO_BASELINE


@dataclass(frozen=True)
class ResultadoComparacaoSaidaCanonicaCompat:
    """Resultado observável da comparação controlada de saída canônica."""

    ok: bool
    resumo_baseline: dict[str, Any]
    resumo_compat: dict[str, Any]
    divergencias: list[dict[str, Any]]
    metadados: dict[str, Any]


def _normalizar_json(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {str(k): _normalizar_json(v) for k, v in sorted(valor.items(), key=lambda item: str(item[0]))}
    if isinstance(valor, (list, tuple)):
        return [_normalizar_json(v) for v in valor]
    if isinstance(valor, set):
        return sorted(_normalizar_json(v) for v in valor)
    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat()
        except Exception:
            return str(valor)
    if isinstance(valor, Decimal):
        return str(valor)
    return valor


def _hash_registros(registros: Any) -> str:
    serializado = json.dumps(_normalizar_json(registros or []), ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _como_decimal(valor: Any) -> Decimal | None:
    if valor is None or valor == "":
        return None
    try:
        return Decimal(str(valor).replace("R$", "").replace(".", "").replace(",", ".").strip())
    except (InvalidOperation, ValueError):
        try:
            return Decimal(str(float(valor)))
        except Exception:
            return None


def _valor_metrica(fechamento: list[dict[str, Any]], nome_metrica: str) -> str:
    alvo = nome_metrica.strip().lower()
    for linha in fechamento or []:
        nome = str(linha.get("Métrica") or linha.get("Metrica") or linha.get("metrica") or "").strip().lower()
        if nome == alvo:
            return str(linha.get("Valor") or linha.get("valor") or "")
    return ""


def _valor_metrica_decimal(fechamento: list[dict[str, Any]], nome_metrica: str) -> str:
    valor = _como_decimal(_valor_metrica(fechamento, nome_metrica))
    if valor is None:
        return ""
    return str(valor.quantize(Decimal("0.01")))


def _ranking_top1(saida: Any) -> str:
    ranking = getattr(saida, "ranking_amostra", None) or []
    if not ranking:
        return ""
    primeira = ranking[0]
    return str(primeira.get("Produto") or primeira.get("produto") or "")


def _resumir_saida(saida: Any) -> dict[str, Any]:
    fechamento = getattr(saida, "fechamento_atual", None) or []
    extrato_passado = getattr(saida, "extrato_passado", None) or []
    extrato_futuro = getattr(saida, "extrato_futuro", None) or []
    lotes_ativos = getattr(saida, "lotes_ativos", None) or []
    lotes_exauridos = getattr(saida, "lotes_exauridos", None) or []
    switchings = getattr(saida, "switchings", None) or []

    return {
        "versao": str(getattr(saida, "versao", "")),
        "data_referencia": str(getattr(saida, "data_referencia", "")),
        "patrimonio_liquido_atual": _valor_metrica_decimal(fechamento, "Patrimônio líquido atual"),
        "rendimento_liquido_atual": _valor_metrica_decimal(fechamento, "Rendimento líquido atual"),
        "rendimento_liquido_reconciliado_recebidos": _valor_metrica_decimal(
            fechamento,
            "Rendimento líquido atual — reconciliado contra recebidos",
        ),
        "ranking_top1": _ranking_top1(saida),
        "qtd_switchings_reais": len(switchings),
        "qtd_lotes_ativos": len(lotes_ativos),
        "qtd_lotes_exauridos": len(lotes_exauridos),
        "qtd_extrato_passado": len(extrato_passado),
        "qtd_extrato_futuro": len(extrato_futuro),
        "hash_lotes_ativos": _hash_registros(lotes_ativos),
        "hash_lotes_exauridos": _hash_registros(lotes_exauridos),
        "hash_extrato_passado": _hash_registros(extrato_passado),
        "hash_extrato_futuro": _hash_registros(extrato_futuro),
        "hash_situacao_atual": _hash_registros(fechamento),
        "hash_switchings": _hash_registros(switchings),
    }


def _comparar_resumos(resumo_baseline: dict[str, Any], resumo_compat: dict[str, Any]) -> list[dict[str, Any]]:
    chaves = sorted(set(resumo_baseline) | set(resumo_compat))
    divergencias = []
    for chave in chaves:
        valor_baseline = resumo_baseline.get(chave)
        valor_compat = resumo_compat.get(chave)
        if valor_baseline != valor_compat:
            divergencias.append(
                {
                    "campo": chave,
                    "baseline": valor_baseline,
                    "compat": valor_compat,
                }
            )
    return divergencias


def construir_saida_canonica_via_contexto_compat(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
    *,
    versao: str = VERSAO_BASELINE,
):
    """Constrói saída em memória usando ContextoSaidaCanonicaCompat.

    A função não altera a rota principal e não escreve XLSX. Os componentes
    transicionais são retirados explicitamente do ContextoBaseline já carregado.
    """

    componentes = ComponentesTransicionaisSaidaCanonica(
        decisao_local_v1=getattr(contexto_baseline, "decisao_local_v1"),
        recomputacao_sequencial_central_v1=getattr(
            contexto_baseline,
            "recomputacao_sequencial_central_v1",
        ),
    )
    contexto_compat = construir_contexto_saida_canonica_compat(
        contexto_operacional_canonico,
        componentes,
    )
    return construir_saida_canonica_com_switching_v17_c7(contexto_compat, versao=versao)


def comparar_saida_canonica_baseline_vs_compat(
    contexto_baseline: Any,
    contexto_operacional_canonico: Any,
    *,
    versao: str = VERSAO_BASELINE,
) -> ResultadoComparacaoSaidaCanonicaCompat:
    """Compara saída atual por ContextoBaseline contra saída via adaptador compatível.

    A comparação é controlada e isolada. Ela constrói duas saídas em memória,
    calcula resumos observáveis e retorna divergências sem promover a rota
    compatível e sem substituir ContextoBaseline.
    """

    saida_baseline = construir_saida_canonica_com_switching_v17_c7(contexto_baseline, versao=versao)
    saida_compat = construir_saida_canonica_via_contexto_compat(
        contexto_baseline,
        contexto_operacional_canonico,
        versao=versao,
    )

    resumo_baseline = _resumir_saida(saida_baseline)
    resumo_compat = _resumir_saida(saida_compat)
    divergencias = _comparar_resumos(resumo_baseline, resumo_compat)

    return ResultadoComparacaoSaidaCanonicaCompat(
        ok=not divergencias,
        resumo_baseline=resumo_baseline,
        resumo_compat=resumo_compat,
        divergencias=divergencias,
        metadados={
            "artefato": "ResultadoComparacaoSaidaCanonicaCompat",
            "microetapa": "ME-RUNTIME-CANON-08",
            "promove_rota_compat": False,
            "substitui_contexto_baseline": False,
            "altera_runtime_principal": False,
            "altera_xlsx_oficial": False,
            "versao": versao,
        },
    )


def imprimir_resumo_comparacao(resultado: ResultadoComparacaoSaidaCanonicaCompat) -> None:
    """Imprime resumo textual curto da comparação isolada."""

    print("=== COMPARAÇÃO OBSERVÁVEL CONTROLADA — CONTEXTO COMPAT ===")
    print(f"ok={resultado.ok}")
    print(f"divergencias={len(resultado.divergencias)}")
    for chave in (
        "patrimonio_liquido_atual",
        "rendimento_liquido_atual",
        "rendimento_liquido_reconciliado_recebidos",
        "ranking_top1",
        "qtd_switchings_reais",
        "qtd_lotes_ativos",
        "qtd_lotes_exauridos",
        "qtd_extrato_passado",
        "qtd_extrato_futuro",
    ):
        print(
            f"{chave}: baseline={resultado.resumo_baseline.get(chave)} | "
            f"compat={resultado.resumo_compat.get(chave)}"
        )
    if resultado.divergencias:
        print("--- divergências ---")
        for divergencia in resultado.divergencias:
            print(
                f"{divergencia['campo']}: baseline={divergencia['baseline']} | "
                f"compat={divergencia['compat']}"
            )
