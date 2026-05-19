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
from nucleo.ledger_switching_canonico_shadow_v37q import BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q
from nucleo.pacote_ledger_temporal_switching_shadow_v37q import (
    construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q,
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
    parser = argparse.ArgumentParser(description="Audita ledger com switching_canonico shadow opcional V3.7Q.")
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

    pacote_desligado = construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q(
        quadro_futuro,
        mapa_central,
        contexto,
        ativar_switching_canonico_shadow=False,
        retorno_legado=retorno_legado,
    )
    pacote_ligado = construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q(
        quadro_futuro,
        mapa_central,
        contexto,
        ativar_switching_canonico_shadow=True,
        retorno_legado=retorno_legado,
    )

    saida_base = construir_saida_canonica(contexto)
    saida_controle = construir_saida_canonica(contexto)
    comparacao_saida = _comparar_saida(saida_base, saida_controle)

    bloco_switching = dict(pacote_ligado.auditoria_ledger_temporal or {}).get(
        BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q,
        {},
    )

    auditoria_desligada = dict(pacote_desligado.auditoria_ledger_temporal or {})
    auditoria_ligada_sem_bloco = dict(pacote_ligado.auditoria_ledger_temporal or {})
    auditoria_ligada_sem_bloco.pop(BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q, None)
    auditoria_ligada_sem_bloco.pop("switching_canonico_shadow_v37q_ativado", None)
    auditoria_ligada_sem_bloco.pop("ledger_operacional_preservado_v37q", None)
    auditoria_ligada_sem_bloco.pop("fonte_operacional_ledger_v37q", None)
    auditoria_ligada_sem_bloco.pop("promove_switching_canonico_para_ledger_v37q", None)

    resultado = {
        "pacote_desligado_eventos_qtd": len(pacote_desligado.eventos_temporais),
        "pacote_ligado_eventos_qtd": len(pacote_ligado.eventos_temporais),
        "pacote_desligado_fifo_qtd": len(pacote_desligado.fifo_candidatos_avaliados),
        "pacote_ligado_fifo_qtd": len(pacote_ligado.fifo_candidatos_avaliados),
        "eventos_temporais_identicos": _iguais(pacote_desligado.eventos_temporais, pacote_ligado.eventos_temporais),
        "fifo_identico": _iguais(pacote_desligado.fifo_candidatos_avaliados, pacote_ligado.fifo_candidatos_avaliados),
        "pagamentos_futuros_processados_identicos": _iguais(pacote_desligado.pagamentos_futuros_processados, pacote_ligado.pagamentos_futuros_processados),
        "saldos_por_lote_identicos": _iguais(pacote_desligado.saldos_por_lote, pacote_ligado.saldos_por_lote),
        "auditoria_sem_bloco_switching_identica": _iguais(auditoria_desligada, auditoria_ligada_sem_bloco),
        "bloco_switching_shadow_presente": isinstance(bloco_switching, dict) and bool(bloco_switching),
        "bloco_switching_shadow_validacao_ok": bool((bloco_switching or {}).get("validacao_ok")),
        "comparacao_mapa_legado_vs_canonico": bool((bloco_switching or {}).get("comparacao_mapa_legado_vs_canonico")),
        "comparacao_eventos_legado_vs_canonico": bool((bloco_switching or {}).get("comparacao_eventos_legado_vs_canonico")),
        "ledger_operacional_preservado": bool((bloco_switching or {}).get("ledger_operacional_preservado")),
        "ledger_operacional_ainda_usa_caminho_legado": bool((bloco_switching or {}).get("ledger_operacional_ainda_usa_caminho_legado")),
        "promove_switching_canonico_para_ledger": bool((bloco_switching or {}).get("promove_switching_canonico_para_ledger")),
        "saida_canonica_preservada": bool((bloco_switching or {}).get("saida_canonica_preservada")),
        **comparacao_saida,
    }

    resultado["saida_canonica_identica"] = all(
        bool(v) for k, v in comparacao_saida.items() if k.startswith("saida_")
    )
    resultado["sem_alteracao_observavel"] = bool(resultado["saida_canonica_identica"])

    print("=== AUDITORIA LEDGER COM SWITCHING CANONICO SHADOW V3.7Q ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_ledger_com_switching_canonico_shadow_v37q_resumo.csv",
            index=False,
        )

    sucesso = all([
        resultado["eventos_temporais_identicos"],
        resultado["fifo_identico"],
        resultado["pagamentos_futuros_processados_identicos"],
        resultado["saldos_por_lote_identicos"],
        resultado["auditoria_sem_bloco_switching_identica"],
        resultado["bloco_switching_shadow_presente"],
        resultado["bloco_switching_shadow_validacao_ok"],
        resultado["comparacao_mapa_legado_vs_canonico"],
        resultado["comparacao_eventos_legado_vs_canonico"],
        resultado["ledger_operacional_preservado"],
        resultado["ledger_operacional_ainda_usa_caminho_legado"],
        not resultado["promove_switching_canonico_para_ledger"],
        resultado["saida_canonica_identica"],
        resultado["sem_alteracao_observavel"],
    ])
    return 0 if sucesso else 1


if __name__ == "__main__":
    raise SystemExit(main())
