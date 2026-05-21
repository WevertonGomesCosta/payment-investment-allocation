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
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
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
    parser = argparse.ArgumentParser(description="Audita pacotes temporais agregados shadow V4I.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    agregados = construir_pacotes_temporais_agregados_saida_shadow(contexto)
    saida_antes = construir_saida_canonica(contexto)
    saida_depois = construir_saida_canonica(contexto)

    replay = agregados.pacote_replay_passado
    ledger = agregados.pacote_ledger_temporal_operacional
    estado = agregados.pacote_estado_temporal
    auditoria = agregados.pacote_auditoria_temporal
    aud_agregador = agregados.auditoria_agregador_temporal or {}
    val_agregador = agregados.validacao_agregador_temporal or {}

    resultado = {
        "adaptador": "pacotes_temporais_agregados_saida_shadow",
        "versao": agregados.versao,
        "modo_execucao": agregados.modo_execucao,
        "data_referencia_presente": agregados.data_referencia not in (None, ""),
        "pacote_replay_passado_presente": replay is not None,
        "pacote_ledger_temporal_operacional_presente": ledger is not None,
        "pacote_estado_temporal_presente": estado is not None,
        "pacote_auditoria_temporal_presente": auditoria is not None,
        "validacao_replay_ok": bool((replay.validacao_replay or {}).get("ok")),
        "validacao_ledger_ok": bool((ledger.validacao_ledger_temporal or {}).get("ok")),
        "validacao_estado_ok": bool((estado.validacao_estado_temporal or {}).get("ok")),
        "validacao_auditoria_temporal_ok": bool((auditoria.validacao_temporal_global or {}).get("ok")),
        "validacao_agregador_ok": bool(val_agregador.get("ok")),
        "erros_bloqueantes_total": len(val_agregador.get("erros_bloqueantes", []) or []),
        "avisos_total": len(val_agregador.get("avisos", []) or []),
        "qtd_lotes_replay": aud_agregador.get("qtd_lotes_replay"),
        "qtd_log_movimentos_passados": aud_agregador.get("qtd_log_movimentos_passados"),
        "qtd_eventos_retorno_legado": aud_agregador.get("qtd_eventos_retorno_legado"),
        "qtd_eventos_ledger_operacional": aud_agregador.get("qtd_eventos_ledger_operacional"),
        "qtd_fifo_retorno_legado": aud_agregador.get("qtd_fifo_retorno_legado"),
        "qtd_fifo_ledger_operacional": aud_agregador.get("qtd_fifo_ledger_operacional"),
        "qtd_estado_lotes_por_data": aud_agregador.get("qtd_estado_lotes_por_data"),
        "qtd_estado_lotes_final": aud_agregador.get("qtd_estado_lotes_final"),
        "fonte_primaria_switching_ledger": aud_agregador.get("fonte_primaria_switching_ledger"),
        "usa_planilha_bruta_como_fonte_primaria": aud_agregador.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_retorno_ledger_dict_legado": aud_agregador.get("usa_retorno_ledger_dict_legado"),
        "saida_chama_ledger_diretamente_fluxo_atual": aud_agregador.get("saida_chama_ledger_diretamente_fluxo_atual"),
        "nao_altera_replay_efetivo": aud_agregador.get("nao_altera_replay_efetivo"),
        "nao_altera_ledger_efetivo": aud_agregador.get("nao_altera_ledger_efetivo"),
        "nao_altera_estado_temporal_efetivo": aud_agregador.get("nao_altera_estado_temporal_efetivo"),
        "nao_altera_saida_canonica": aud_agregador.get("nao_altera_saida_canonica"),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
    }

    resultado["eventos_ledger_qtd_equivalente"] = resultado["qtd_eventos_retorno_legado"] == resultado["qtd_eventos_ledger_operacional"]
    resultado["fifo_ledger_qtd_equivalente"] = resultado["qtd_fifo_retorno_legado"] == resultado["qtd_fifo_ledger_operacional"]

    resultado["validacao_v4i_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["pacote_replay_passado_presente"],
        resultado["pacote_ledger_temporal_operacional_presente"],
        resultado["pacote_estado_temporal_presente"],
        resultado["pacote_auditoria_temporal_presente"],
        resultado["validacao_replay_ok"],
        resultado["validacao_ledger_ok"],
        resultado["validacao_estado_ok"],
        resultado["validacao_auditoria_temporal_ok"],
        resultado["validacao_agregador_ok"],
        resultado["erros_bloqueantes_total"] == 0,
        resultado["eventos_ledger_qtd_equivalente"],
        resultado["fifo_ledger_qtd_equivalente"],
        int(resultado["qtd_estado_lotes_por_data"] or 0) > 0,
        int(resultado["qtd_estado_lotes_final"] or 0) > 0,
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["nao_altera_replay_efetivo"] is True,
        resultado["nao_altera_ledger_efetivo"] is True,
        resultado["nao_altera_estado_temporal_efetivo"] is True,
        resultado["nao_altera_saida_canonica"] is True,
        resultado["saida_canonica_identica_dupla_execucao"],
    ])

    print("=== AUDITORIA PACOTES TEMPORAIS AGREGADOS SAIDA SHADOW V4I ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_pacotes_temporais_agregados_saida_v4i_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4i_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
