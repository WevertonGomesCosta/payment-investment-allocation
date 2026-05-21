from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

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


def _as_list_dict(valor: Any) -> list[dict[str, Any]]:
    if valor is None:
        return []
    if isinstance(valor, list):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, tuple):
        return [dict(x) for x in valor if isinstance(x, Mapping)]
    if isinstance(valor, pd.DataFrame):
        return list(valor.to_dict(orient="records"))
    return []


def _as_dict(valor: Any) -> dict[str, Any]:
    if isinstance(valor, dict):
        return dict(valor)
    if isinstance(valor, Mapping):
        return dict(valor.items())
    return {}


def _primeiro(row: Mapping[str, Any], *chaves: str) -> Any:
    for chave in chaves:
        if chave in row and row.get(chave) not in (None, ""):
            return row.get(chave)
    return ""


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _boolish(valor: Any) -> bool:
    texto = _txt(valor).lower()
    return texto in {"true", "1", "sim", "yes", "y", "migrado", "ativo_pos_switching"}


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)
        linhas.append({"metrica": chave, "valor": valor})
    return linhas


def _conjunto_lotes(rows: list[dict[str, Any]]) -> set[str]:
    lotes: set[str] = set()
    for row in rows:
        lote = _txt(_primeiro(row, "Lote", "lote_id", "Lote ID", "lote"))
        if lote:
            lotes.add(lote)
    return lotes


def _mapa_estado_por_lote(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapa: dict[str, dict[str, Any]] = {}
    for row in rows:
        lote = _txt(_primeiro(row, "lote_id", "Lote", "Lote ID"))
        if lote:
            mapa[lote] = dict(row)
    return mapa


def _historico_estado_lote(estado_lotes_por_data: list[dict[str, Any]], lote_id: str) -> list[dict[str, Any]]:
    return [row for row in estado_lotes_por_data if _txt(_primeiro(row, "lote_id", "Lote", "Lote ID")) == lote_id]


def _classificar_lote_extra(row: Mapping[str, Any], historico: list[dict[str, Any]]) -> dict[str, Any]:
    lote_id = _txt(_primeiro(row, "lote_id", "Lote", "Lote ID"))
    origem = _txt(_primeiro(row, "origem_estado_final", "origem_estado"))
    status = _txt(_primeiro(row, "status_final", "status_temporal", "status"))
    migrado = _boolish(_primeiro(row, "migrado"))
    lote_pos = _txt(_primeiro(row, "lote_pos_switching"))

    origens_historico = sorted({_txt(_primeiro(h, "origem_estado", "origem_estado_final")) for h in historico if _txt(_primeiro(h, "origem_estado", "origem_estado_final"))})
    status_historico = sorted({_txt(_primeiro(h, "status_temporal", "status_final", "status")) for h in historico if _txt(_primeiro(h, "status_temporal", "status_final", "status"))})

    if origem == "pacote_ledger_temporal_operacional.saldos_por_lote":
        motivo = "saldo_temporal_ledger_sem_lote_observavel_saida"
    elif migrado or lote_pos:
        motivo = "registro_migracao_temporal_preservado_no_estado"
    elif "pos_switching" in status.lower() or "switch" in lote_id.lower():
        motivo = "registro_pos_switching_temporal_sem_linha_observavel_saida"
    elif origem:
        motivo = "registro_estado_temporal_nao_observavel_na_saida"
    else:
        motivo = "motivo_indeterminado"

    return {
        "lote_id": lote_id,
        "motivo": motivo,
        "classe_normalizacao": "excluir_da_base_observavel_shadow" if motivo != "motivo_indeterminado" else "revisar_manual",
        "observavel_na_saida": False,
        "origem_estado_final": origem,
        "status_final": status,
        "migrado": migrado,
        "lote_pos_switching": lote_pos,
        "qtd_registros_historico_estado": len(historico),
        "origens_historico": origens_historico,
        "status_historico": status_historico,
    }


def _normalizar_estado_para_base_observavel(
    estado_final: list[dict[str, Any]],
    lotes_observaveis_saida: set[str],
) -> list[dict[str, Any]]:
    normalizado: list[dict[str, Any]] = []
    for row in estado_final:
        lote = _txt(_primeiro(row, "lote_id", "Lote", "Lote ID"))
        if lote in lotes_observaveis_saida:
            normalizado.append(dict(row))
    return normalizado


def main() -> int:
    parser = argparse.ArgumentParser(description="Normaliza comparação shadow de lotes/estado temporal V4K0.")
    parser.add_argument("--raiz", type=Path, default=ROOT)
    parser.add_argument("--sem-csv", action="store_true")
    args = parser.parse_args()

    contexto = carregar_contexto_baseline(
        raiz_repositorio=args.raiz,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )

    saida_antes = construir_saida_canonica(contexto)
    agregados = construir_pacotes_temporais_agregados_saida_shadow(contexto)
    saida_depois = construir_saida_canonica(contexto)

    ativos = _as_list_dict(getattr(saida_antes, "lotes_ativos", []))
    exauridos = _as_list_dict(getattr(saida_antes, "lotes_exauridos", []))
    lotes_saida = _conjunto_lotes(ativos + exauridos)

    estado = agregados.pacote_estado_temporal
    estado_final = _as_list_dict(getattr(estado, "estado_lotes_final", []))
    estado_lotes_por_data = _as_list_dict(getattr(estado, "estado_lotes_por_data", []))
    mapa_estado = _mapa_estado_por_lote(estado_final)
    lotes_estado = set(mapa_estado.keys())

    lotes_apenas_estado = sorted(lotes_estado - lotes_saida)
    lotes_apenas_saida = sorted(lotes_saida - lotes_estado)
    classificados = [
        _classificar_lote_extra(
            mapa_estado[lote],
            _historico_estado_lote(estado_lotes_por_data, lote),
        )
        for lote in lotes_apenas_estado
    ]

    estado_final_normalizado = _normalizar_estado_para_base_observavel(estado_final, lotes_saida)
    lotes_estado_normalizado = _conjunto_lotes(estado_final_normalizado)

    motivos_classificados = all(item.get("motivo") != "motivo_indeterminado" for item in classificados)
    todos_excluiveis = all(item.get("classe_normalizacao") == "excluir_da_base_observavel_shadow" for item in classificados)
    comparacao_lotes_normalizada = lotes_estado_normalizado == lotes_saida and len(estado_final_normalizado) == len(lotes_saida)
    saida_preservada = _iguais(saida_antes, saida_depois)

    validacao_agregador = _as_dict(getattr(agregados, "validacao_agregador_temporal", {}))
    auditoria_agregador = _as_dict(getattr(agregados, "auditoria_agregador_temporal", {}))

    resultado = {
        "adaptador": "normalizacao_lotes_estado_temporal_v4k0",
        "versao_agregador": getattr(agregados, "versao", ""),
        "data_referencia_presente": getattr(agregados, "data_referencia", None) not in (None, ""),
        "validacao_agregador_ok": bool(validacao_agregador.get("ok")),
        "erros_bloqueantes_agregador_total": len(validacao_agregador.get("erros_bloqueantes", []) or []),
        "saida_canonica_identica_dupla_execucao": saida_preservada,
        "lotes_saida_total": len(lotes_saida),
        "lotes_ativos_qtd_saida": len(ativos),
        "lotes_exauridos_qtd_saida": len(exauridos),
        "estado_lotes_final_qtd_original": len(estado_final),
        "estado_lotes_final_qtd_normalizado": len(estado_final_normalizado),
        "lotes_apenas_estado_qtd": len(lotes_apenas_estado),
        "lotes_apenas_estado": lotes_apenas_estado,
        "lotes_apenas_saida_qtd": len(lotes_apenas_saida),
        "lotes_apenas_saida": lotes_apenas_saida,
        "lotes_apenas_estado_identificados": len(lotes_apenas_estado) > 0,
        "motivo_lotes_apenas_estado_classificado": motivos_classificados,
        "lotes_apenas_estado_excluiveis_base_observavel": todos_excluiveis,
        "comparacao_lotes_normalizada": comparacao_lotes_normalizada,
        "lotes_normalizados_intersecao": len(lotes_estado_normalizado & lotes_saida),
        "lotes_normalizados_apenas_estado": sorted(lotes_estado_normalizado - lotes_saida),
        "lotes_normalizados_apenas_saida": sorted(lotes_saida - lotes_estado_normalizado),
        "fonte_primaria_switching_ledger": auditoria_agregador.get("fonte_primaria_switching_ledger"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_agregador.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_retorno_ledger_dict_legado": auditoria_agregador.get("usa_retorno_ledger_dict_legado"),
        "saida_chama_ledger_diretamente_fluxo_atual": auditoria_agregador.get("saida_chama_ledger_diretamente_fluxo_atual"),
        "lotes_apenas_estado_classificados": classificados,
        "sem_alteracao_observavel": saida_preservada,
    }

    resultado["validacao_v4k0_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["validacao_agregador_ok"],
        resultado["erros_bloqueantes_agregador_total"] == 0,
        resultado["saida_canonica_identica_dupla_execucao"],
        resultado["lotes_apenas_estado_identificados"],
        resultado["motivo_lotes_apenas_estado_classificado"],
        resultado["lotes_apenas_estado_excluiveis_base_observavel"],
        resultado["comparacao_lotes_normalizada"],
        resultado["lotes_apenas_saida_qtd"] == 0,
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["sem_alteracao_observavel"],
    ])

    print("=== AUDITORIA NORMALIZACAO LOTES ESTADO TEMPORAL SHADOW V4K0 ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_normalizacao_lotes_estado_temporal_v4k0_resumo.csv",
            index=False,
        )
        pd.DataFrame(classificados).to_csv(
            saida_dir / "auditoria_normalizacao_lotes_estado_temporal_v4k0_lotes_apenas_estado.csv",
            index=False,
        )
        pd.DataFrame(estado_final_normalizado).to_csv(
            saida_dir / "auditoria_normalizacao_lotes_estado_temporal_v4k0_estado_normalizado.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4k0_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
