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


BLOCOS_SAIDA = [
    "extrato_passado",
    "extrato_futuro",
    "lotes_ativos",
    "lotes_exauridos",
    "fechamento_atual",
    "auditoria",
]


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


def _qtd(valor: Any) -> int:
    try:
        if valor is None:
            return 0
        if isinstance(valor, pd.DataFrame):
            return int(len(valor))
        if hasattr(valor, "__len__"):
            return int(len(valor))
    except Exception:
        return 0
    return 0


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


def _linhas_resumo(resultado: dict[str, Any]) -> list[dict[str, Any]]:
    linhas = []
    for chave, valor in resultado.items():
        if isinstance(valor, (dict, list)):
            valor = json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)
        linhas.append({"metrica": chave, "valor": valor})
    return linhas


def _conjunto_chaves_pagamentos(rows: list[dict[str, Any]], *, origem: str) -> set[str]:
    chaves: set[str] = set()
    for row in rows:
        if origem == "saida_passado":
            chave = "|".join([
                _txt(_primeiro(row, "Despesa ID", "pagamento_id")),
                _txt(_primeiro(row, "Data", "data_movimento", "data_pagamento")),
                _txt(_primeiro(row, "Conta", "Descrição", "descricao_pagamento")),
            ])
        elif origem == "saida_futuro":
            chave = "|".join([
                _txt(_primeiro(row, "pagamento_id", "Despesa ID")),
                _txt(_primeiro(row, "Data", "data_pagamento")),
                _txt(_primeiro(row, "Conta", "Descrição", "descricao_pagamento")),
            ])
        else:
            chave = "|".join([
                _txt(_primeiro(row, "pagamento_id", "Despesa ID")),
                _txt(_primeiro(row, "data_pagamento", "data_movimento", "Data")),
                _txt(_primeiro(row, "descricao_pagamento", "Conta", "Descrição")),
            ])
        if chave.strip("|"):
            chaves.add(chave)
    return chaves


def _conjunto_lotes(rows: list[dict[str, Any]]) -> set[str]:
    lotes: set[str] = set()
    for row in rows:
        lote = _txt(_primeiro(row, "Lote", "lote_id", "Lote ID", "lote"))
        if lote:
            lotes.add(lote)
    return lotes


def _metricas_fechamento(fechamento: list[dict[str, Any]]) -> dict[str, Any]:
    metricas: dict[str, Any] = {}
    for row in fechamento:
        chave = _txt(_primeiro(row, "Métrica", "Metrica", "metrica"))
        valor = _primeiro(row, "Valor", "valor")
        if chave:
            metricas[chave] = valor
    return metricas


def _comparar_extrato_passado(saida: Any, agregados: Any) -> dict[str, Any]:
    extrato = _as_list_dict(getattr(saida, "extrato_passado", []))
    replay = agregados.pacote_replay_passado
    log = _as_list_dict(getattr(replay, "log_movimentos_passados", []))
    chaves_saida = _conjunto_chaves_pagamentos(extrato, origem="saida_passado")
    chaves_log = _conjunto_chaves_pagamentos(log, origem="pacote")
    return {
        "qtd_saida": len(extrato),
        "qtd_pacote": len(log),
        "qtd_identica": len(extrato) == len(log),
        "chaves_intersecao": len(chaves_saida & chaves_log),
        "chaves_apenas_saida": len(chaves_saida - chaves_log),
        "chaves_apenas_pacote": len(chaves_log - chaves_saida),
        "comparavel": True,
        "status": "identico" if len(extrato) == len(log) and not (chaves_saida - chaves_log) and not (chaves_log - chaves_saida) else "shadow_gap",
    }


def _comparar_extrato_futuro(saida: Any, agregados: Any) -> dict[str, Any]:
    extrato = _as_list_dict(getattr(saida, "extrato_futuro", []))
    ledger = agregados.pacote_ledger_temporal_operacional
    eventos = _as_list_dict(getattr(ledger, "eventos_temporais", []))
    pagamentos = _as_list_dict(getattr(ledger, "pagamentos_futuros_processados", []))
    chaves_saida = _conjunto_chaves_pagamentos(extrato, origem="saida_futuro")
    chaves_pag = _conjunto_chaves_pagamentos(pagamentos, origem="pacote")
    return {
        "qtd_saida": len(extrato),
        "qtd_eventos_pacote": len(eventos),
        "qtd_pagamentos_pacote": len(pagamentos),
        "qtd_identica_eventos": len(extrato) == len(eventos),
        "qtd_identica_pagamentos": len(extrato) == len(pagamentos),
        "chaves_intersecao_pagamentos": len(chaves_saida & chaves_pag),
        "chaves_apenas_saida": len(chaves_saida - chaves_pag),
        "chaves_apenas_pacote": len(chaves_pag - chaves_saida),
        "comparavel": True,
        "status": "identico" if len(extrato) == len(eventos) else "shadow_gap",
    }


def _comparar_lotes(saida: Any, agregados: Any) -> dict[str, Any]:
    ativos = _as_list_dict(getattr(saida, "lotes_ativos", []))
    exauridos = _as_list_dict(getattr(saida, "lotes_exauridos", []))
    estado = agregados.pacote_estado_temporal
    estado_final = _as_list_dict(getattr(estado, "estado_lotes_final", []))
    saldos = _as_list_dict(getattr(estado, "saldos_por_lote", []))
    lotes_saida = _conjunto_lotes(ativos + exauridos)
    lotes_estado = _conjunto_lotes(estado_final)
    return {
        "qtd_lotes_ativos_saida": len(ativos),
        "qtd_lotes_exauridos_saida": len(exauridos),
        "qtd_lotes_saida_total": len(ativos) + len(exauridos),
        "qtd_estado_lotes_final": len(estado_final),
        "qtd_saldos_por_lote_pacote": len(saldos),
        "qtd_lotes_distintos_saida": len(lotes_saida),
        "qtd_lotes_distintos_estado": len(lotes_estado),
        "lotes_intersecao": len(lotes_saida & lotes_estado),
        "lotes_apenas_saida": len(lotes_saida - lotes_estado),
        "lotes_apenas_estado": len(lotes_estado - lotes_saida),
        "qtd_identica_estado_final": len(ativos) + len(exauridos) == len(estado_final),
        "comparavel": True,
        "status": "identico" if lotes_saida == lotes_estado and len(ativos) + len(exauridos) == len(estado_final) else "shadow_gap",
    }


def _comparar_resumo_patrimonial(saida: Any, agregados: Any) -> dict[str, Any]:
    fechamento = _as_list_dict(getattr(saida, "fechamento_atual", []))
    metricas = _metricas_fechamento(fechamento)
    estado = agregados.pacote_estado_temporal
    estado_final = _as_list_dict(getattr(estado, "estado_lotes_final", []))
    tem_metricas_saida = len(metricas) > 0
    tem_estado_final = len(estado_final) > 0
    return {
        "qtd_metricas_saida": len(metricas),
        "qtd_estado_lotes_final": len(estado_final),
        "tem_valor_original_total": "Valor original total" in metricas,
        "tem_patrimonio_liquido_atual": "Patrimônio líquido atual" in metricas,
        "tem_rendimento_liquido_atual": "Rendimento líquido atual" in metricas,
        "comparavel": tem_metricas_saida and tem_estado_final,
        "status": "parcial_comparavel" if tem_metricas_saida and tem_estado_final else "nao_comparavel",
    }


def _comparar_auditoria(saida: Any, agregados: Any) -> dict[str, Any]:
    auditoria_saida = _as_dict(getattr(saida, "auditoria", {}))
    auditoria_temporal = agregados.pacote_auditoria_temporal
    validacao_temporal = _as_dict(getattr(auditoria_temporal, "validacao_temporal_global", {}))
    aud_residuos = _as_dict(getattr(auditoria_temporal, "auditoria_residuos_legados", {}))
    return {
        "auditoria_saida_presente": bool(auditoria_saida),
        "auditoria_temporal_presente": bool(auditoria_temporal),
        "validacao_temporal_global_ok": bool(validacao_temporal.get("ok")),
        "saida_chama_ledger_diretamente": aud_residuos.get("saida_chama_ledger_diretamente"),
        "usa_retorno_ledger_dict_legado": aud_residuos.get("usa_retorno_ledger_dict_legado"),
        "qtd_chaves_auditoria_saida": len(auditoria_saida),
        "comparavel": bool(auditoria_saida) and bool(auditoria_temporal),
        "status": "parcial_comparavel" if bool(auditoria_saida) and bool(auditoria_temporal) else "nao_comparavel",
    }


def _classificar_divergencias(*comparacoes: dict[str, Any]) -> dict[str, Any]:
    blocos_identicos = 0
    blocos_shadow_gap = 0
    blocos_parciais = 0
    blocos_nao_comparaveis = 0
    for comp in comparacoes:
        status = comp.get("status")
        if status == "identico":
            blocos_identicos += 1
        elif status == "shadow_gap":
            blocos_shadow_gap += 1
        elif status == "parcial_comparavel":
            blocos_parciais += 1
        else:
            blocos_nao_comparaveis += 1
    return {
        "blocos_identicos": blocos_identicos,
        "blocos_com_shadow_gap": blocos_shadow_gap,
        "blocos_parcialmente_comparaveis": blocos_parciais,
        "blocos_nao_comparaveis": blocos_nao_comparaveis,
        "divergencias_classificadas": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita saída canônica contra pacotes temporais agregados shadow V4J.")
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

    comparacao_extrato_passado = _comparar_extrato_passado(saida_antes, agregados)
    comparacao_extrato_futuro = _comparar_extrato_futuro(saida_antes, agregados)
    comparacao_lotes = _comparar_lotes(saida_antes, agregados)
    comparacao_resumo = _comparar_resumo_patrimonial(saida_antes, agregados)
    comparacao_auditoria = _comparar_auditoria(saida_antes, agregados)
    classificacao = _classificar_divergencias(
        comparacao_extrato_passado,
        comparacao_extrato_futuro,
        comparacao_lotes,
        comparacao_resumo,
        comparacao_auditoria,
    )

    validacao_agregador = _as_dict(getattr(agregados, "validacao_agregador_temporal", {}))
    auditoria_agregador = _as_dict(getattr(agregados, "auditoria_agregador_temporal", {}))

    resultado = {
        "adaptador": "saida_canonica_vs_pacotes_temporais_agregados_shadow",
        "versao_agregador": getattr(agregados, "versao", ""),
        "data_referencia_presente": getattr(agregados, "data_referencia", None) not in (None, ""),
        "saida_canonica_identica_dupla_execucao": _iguais(saida_antes, saida_depois),
        "validacao_agregador_ok": bool(validacao_agregador.get("ok")),
        "erros_bloqueantes_agregador_total": len(validacao_agregador.get("erros_bloqueantes", []) or []),
        "extrato_passado_qtd_saida": comparacao_extrato_passado["qtd_saida"],
        "extrato_passado_qtd_pacote": comparacao_extrato_passado["qtd_pacote"],
        "extrato_passado_qtd_identica": comparacao_extrato_passado["qtd_identica"],
        "extrato_passado_status": comparacao_extrato_passado["status"],
        "extrato_futuro_qtd_saida": comparacao_extrato_futuro["qtd_saida"],
        "extrato_futuro_qtd_eventos_pacote": comparacao_extrato_futuro["qtd_eventos_pacote"],
        "extrato_futuro_qtd_pagamentos_pacote": comparacao_extrato_futuro["qtd_pagamentos_pacote"],
        "extrato_futuro_qtd_identica_eventos": comparacao_extrato_futuro["qtd_identica_eventos"],
        "extrato_futuro_status": comparacao_extrato_futuro["status"],
        "lotes_ativos_qtd_saida": comparacao_lotes["qtd_lotes_ativos_saida"],
        "lotes_exauridos_qtd_saida": comparacao_lotes["qtd_lotes_exauridos_saida"],
        "lotes_saida_total": comparacao_lotes["qtd_lotes_saida_total"],
        "estado_lotes_final_qtd_pacote": comparacao_lotes["qtd_estado_lotes_final"],
        "lotes_status": comparacao_lotes["status"],
        "resumo_patrimonial_status": comparacao_resumo["status"],
        "auditoria_status": comparacao_auditoria["status"],
        "fonte_primaria_switching_ledger": auditoria_agregador.get("fonte_primaria_switching_ledger"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_agregador.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_retorno_ledger_dict_legado": auditoria_agregador.get("usa_retorno_ledger_dict_legado"),
        "saida_chama_ledger_diretamente_fluxo_atual": auditoria_agregador.get("saida_chama_ledger_diretamente_fluxo_atual"),
        "blocos_identicos": classificacao["blocos_identicos"],
        "blocos_com_shadow_gap": classificacao["blocos_com_shadow_gap"],
        "blocos_parcialmente_comparaveis": classificacao["blocos_parcialmente_comparaveis"],
        "blocos_nao_comparaveis": classificacao["blocos_nao_comparaveis"],
        "divergencias_classificadas": classificacao["divergencias_classificadas"],
        "comparacao_extrato_passado": comparacao_extrato_passado,
        "comparacao_extrato_futuro": comparacao_extrato_futuro,
        "comparacao_lotes": comparacao_lotes,
        "comparacao_resumo_patrimonial": comparacao_resumo,
        "comparacao_auditoria": comparacao_auditoria,
    }

    resultado["validacao_v4j_ok"] = all([
        resultado["data_referencia_presente"],
        resultado["saida_canonica_identica_dupla_execucao"],
        resultado["validacao_agregador_ok"],
        resultado["erros_bloqueantes_agregador_total"] == 0,
        resultado["fonte_primaria_switching_ledger"] == "switching_canonico",
        resultado["usa_planilha_bruta_como_fonte_primaria"] is False,
        resultado["divergencias_classificadas"],
        resultado["extrato_passado_qtd_saida"] > 0,
        resultado["extrato_futuro_qtd_saida"] > 0,
        resultado["estado_lotes_final_qtd_pacote"] > 0,
    ])

    print("=== AUDITORIA SAIDA CANONICA VS PACOTES TEMPORAIS AGREGADOS SHADOW V4J ===")
    for linha in _linhas_resumo(resultado):
        print(f"{linha['metrica']}: {linha['valor']}")

    if not args.sem_csv:
        saida_dir = args.raiz / "saidas" / "diagnostico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(_linhas_resumo(resultado)).to_csv(
            saida_dir / "auditoria_saida_canonica_vs_pacotes_temporais_v4j_resumo.csv",
            index=False,
        )
        pd.DataFrame([comparacao_extrato_passado]).to_csv(
            saida_dir / "auditoria_saida_canonica_vs_pacotes_temporais_v4j_extrato_passado.csv",
            index=False,
        )
        pd.DataFrame([comparacao_extrato_futuro]).to_csv(
            saida_dir / "auditoria_saida_canonica_vs_pacotes_temporais_v4j_extrato_futuro.csv",
            index=False,
        )
        pd.DataFrame([comparacao_lotes]).to_csv(
            saida_dir / "auditoria_saida_canonica_vs_pacotes_temporais_v4j_lotes.csv",
            index=False,
        )

    return 0 if resultado["validacao_v4j_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
