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
from nucleo.pacote_auditoria_temporal import construir_pacote_auditoria_temporal_shadow
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
    parser = argparse.ArgumentParser(description="Audita PacoteAuditoriaTemporal shadow V4G.")
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
    pacote_auditoria = construir_pacote_auditoria_temporal_shadow(
        pacote_replay,
        pacote_ledger_operacional,
        pacote_estado,
        contexto=contexto,
    )

    saida_antes = construir_saida_canonica(contexto)
    saida_depois = construir_saida_canonica(contexto)

    validacao = pacote_auditoria.validacao_temporal_global or {}
    auditoria_switching = pacote_auditoria.auditoria_switching_temporal or {}
    auditoria_fontes = pacote_auditoria.auditoria_fontes_elegiveis or {}
    auditoria_invariantes = pacote_auditoria.auditoria_invariantes or {}
    auditoria_residuos = pacote_auditoria.auditoria_residuos_legados or {}

    resultado = {
        "adaptador": "pacote_auditoria_temporal_shadow",
        "versao": pacote_auditoria.versao,
        "modo_execucao": pacote_auditoria.modo_execucao,
        "data_referencia_presente": pacote_auditoria.data_referencia not in (None, ""),
        "auditoria_replay_presente": bool(pacote_auditoria.auditoria_replay),
        "auditoria_ledger_presente": bool(pacote_auditoria.auditoria_ledger),
        "auditoria_estado_temporal_presente": bool(pacote_auditoria.auditoria_estado_temporal),
        "auditoria_fontes_elegiveis_ok": auditoria_fontes.get("ok"),
        "auditoria_switching_temporal_ok": auditoria_switching.get("ok"),
        "auditoria_invariantes_ok": auditoria_invariantes.get("ok"),
        "auditoria_residuos_legados_presente": bool(auditoria_residuos),
        "validacao_temporal_global_ok": bool(validacao.get("ok")),
        "erros_bloqueantes_total": len(validacao.get("erros_bloqueantes", []) or []),
        "avisos_total": len(validacao.get("avisos", []) or []),
        "fonte_primaria_switching_ledger": auditoria_switching.get("fonte_primaria_switching_ledger"),
        "fallback_legado_switching_auditavel": auditoria_switching.get("fallback_legado_switching_auditavel"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_switching.get("usa_planilha_bruta_como_fonte_primaria"),
        "qtd_fontes_elegiveis_por_pagamento": auditoria_fontes.get("qtd_fontes_elegiveis_por_pagamento"),
        "qtd_fontes_disponiveis_por_data": auditoria_fontes.get("qtd_fontes_disponiveis_por_data"),
        "qtd_fifo_candidatos_avaliados": auditoria_fontes.get("qtd_fifo_candidatos_avaliados"),
        "estado_lotes_por_data_materializado": auditoria_invariantes.get("estado_lotes_por_data_materializado"),
        "estado_lotes_final_materializado": auditoria_invariantes.get("estado_lotes_final_materializado"),
        "usa_retorno_ledger_dict_legado": auditoria_residuos.get("usa_retorno_ledger_dict_legado"),
        "saida_chama_ledger_diretamente": auditoria_residuos.get("saida_chama_ledger_diretamente"),
        "campos_vazios_auditados": auditoria_residuos.get("campos_vazios_auditados"),
        "nao_altera_replay_efetivo": pacote_auditoria.metadados_origem.get("nao_altera_replay_efetivo"),
        "nao_altera_ledger_efetivo": pacote_auditoria.metadados_origem.get("nao_altera_ledger_efetivo"),
        "nao_altera_estado_temporal_efetivo": pacote_auditoria.metadados_origem.get("nao_altera_estado_temporal_efetivo"),
        "nao_altera_saida_canonica": pacote_auditoria.metadados_origem.get("nao_altera_saida_canonica"),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
    }

    resultado["validacao_v4g_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["auditoria_replay_presente"],
        resultado["auditoria_ledger_presente"],
        resultado["auditoria_estado_temporal_presente"],
        resultado["auditoria_fontes_elegiveis_ok"] is True,
        resultado["auditoria_switching_temporal_ok"] is True,
        resultado["auditoria_invariantes_ok"] is True,
        resultado["auditoria_residuos_legados_presente"],
        resultado["validacao_temporal_global_ok"],
        resultado["erros_bloqueantes_total"] == 0,
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["estado_lotes_por_data_materializado"] is True,
        resultado["estado_lotes_final_materializado"] is True,
        resultado["nao_altera_replay_efetivo"] is True,
        resultado["nao_altera_ledger_efetivo"] is True,
        resultado["nao_altera_estado_temporal_efetivo"] is True,
        resultado["nao_altera_saida_canonica"] is True,
        resultado["saida_canonica_identica_dupla_execucao"],
    ])

    print("=== AUDITORIA PACOTE AUDITORIA TEMPORAL SHADOW V4G ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_pacote_auditoria_temporal_v4g_resumo.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4g_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
