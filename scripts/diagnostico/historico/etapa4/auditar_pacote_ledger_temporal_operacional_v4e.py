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
from nucleo.pacote_ledger_temporal import construir_pacote_ledger_temporal_shadow
from nucleo.pacote_ledger_temporal_operacional import construir_pacote_ledger_temporal_operacional_shadow
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
    parser = argparse.ArgumentParser(description="Audita PacoteLedgerTemporalOperacional shadow V4E.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    retorno_legado = construir_ledger_temporal_conjunto(quadro_futuro, mapa_central, contexto) or {}

    pacote_shadow = construir_pacote_ledger_temporal_shadow(
        quadro_futuro,
        mapa_central,
        contexto,
        retorno_legado=retorno_legado,
    )
    pacote_operacional = construir_pacote_ledger_temporal_operacional_shadow(
        retorno_legado,
        pacote_shadow,
        contexto=contexto,
    )

    saida_antes = construir_saida_canonica(contexto)
    saida_depois = construir_saida_canonica(contexto)

    eventos_legado = list(retorno_legado.get("eventos", []) or [])
    fifo_legado = list(retorno_legado.get("fifo_candidatos_avaliados", []) or [])
    eventos_shadow = list(getattr(pacote_shadow, "eventos_temporais", []) or [])
    fifo_shadow = list(getattr(pacote_shadow, "fifo_candidatos_avaliados", []) or [])
    eventos_operacional = list(getattr(pacote_operacional, "eventos_temporais", []) or [])
    fifo_operacional = list(getattr(pacote_operacional, "fifo_candidatos_avaliados", []) or [])
    auditoria = pacote_operacional.auditoria_ledger_temporal or {}
    validacao = pacote_operacional.validacao_ledger_temporal or {}

    resultado = {
        "adaptador": "pacote_ledger_temporal_operacional_shadow",
        "versao": pacote_operacional.versao,
        "modo_execucao": pacote_operacional.modo_execucao,
        "data_referencia_presente": pacote_operacional.data_referencia not in (None, ""),
        "eventos_legado_qtd": len(eventos_legado),
        "eventos_shadow_qtd": len(eventos_shadow),
        "eventos_operacional_qtd": len(eventos_operacional),
        "fifo_legado_qtd": len(fifo_legado),
        "fifo_shadow_qtd": len(fifo_shadow),
        "fifo_operacional_qtd": len(fifo_operacional),
        "eventos_operacional_mesma_qtd_legado": len(eventos_operacional) == len(eventos_legado),
        "fifo_operacional_identico_shadow": _iguais(fifo_operacional, fifo_shadow),
        "pagamentos_futuros_processados_total": len(pacote_operacional.pagamentos_futuros_processados or []),
        "fontes_elegiveis_por_pagamento_total": len(pacote_operacional.fontes_elegiveis_por_pagamento or []),
        "saldos_por_lote_total": len(pacote_operacional.saldos_por_lote or []),
        "saldos_disponiveis_por_data_total": len(pacote_operacional.saldos_disponiveis_por_data or []),
        "campos_vazios_auditados": auditoria.get("campos_vazios_auditados"),
        "fonte_primaria_switching_ledger": auditoria.get("fonte_primaria_switching_ledger"),
        "fallback_legado_switching_auditavel": auditoria.get("fallback_legado_switching_auditavel"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_planilha_bruta_apenas_fallback": auditoria.get("usa_planilha_bruta_apenas_fallback"),
        "usa_switching_canonico_como_fonte_primaria": auditoria.get("usa_switching_canonico_como_fonte_primaria"),
        "retorno_dict_legado_usado_como_origem": auditoria.get("retorno_dict_legado_usado_como_origem"),
        "pacote_shadow_v37k_usado_como_origem": auditoria.get("pacote_shadow_v37k_usado_como_origem"),
        "nao_altera_ledger_efetivo": auditoria.get("nao_altera_ledger_efetivo"),
        "nao_altera_saida_canonica": auditoria.get("nao_altera_saida_canonica"),
        "validacao_ok": bool(validacao.get("ok")),
        "erros_bloqueantes_total": len(validacao.get("erros_bloqueantes", []) or []),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
    }

    resultado["validacao_v4e_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["eventos_operacional_mesma_qtd_legado"],
        resultado["fifo_operacional_identico_shadow"],
        resultado["pagamentos_futuros_processados_total"] > 0,
        resultado["fontes_elegiveis_por_pagamento_total"] > 0,
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["fallback_legado_switching_auditavel"] is True,
        resultado["usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["usa_planilha_bruta_apenas_fallback"] is True,
        resultado["usa_switching_canonico_como_fonte_primaria"] is True,
        resultado["nao_altera_ledger_efetivo"] is True,
        resultado["nao_altera_saida_canonica"] is True,
        resultado["validacao_ok"],
        resultado["erros_bloqueantes_total"] == 0,
        resultado["saida_canonica_identica_dupla_execucao"],
    ])

    print("=== AUDITORIA PACOTE LEDGER TEMPORAL OPERACIONAL SHADOW V4E ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_pacote_ledger_temporal_operacional_v4e_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4e_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
