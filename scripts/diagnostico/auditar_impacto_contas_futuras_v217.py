"""Auditoria V217 do impacto dos aportes planejados sobre contas futuras reais.

A V217 não promove baseline. Ela compara o mesmo recorte real em dois cenários:

1. sem aportes planejados: `aportes_futuros_v216.habilitado = False`;
2. com aportes planejados: configuração funcional da V216 habilitada.

Objetivo: auditar se a integração funcional da V216 melhora ou preserva a cobertura
das contas futuras reais sem criar déficit, dupla contagem operacional ou piora não
justificada no recorte avaliado.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import timedelta
from typing import Any
import ast

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from nucleo.builders.simulador_central_estado_v117 import construir_estado_global_recorte_curto_v117
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE, caminho_saida_diagnostico
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1


def _salvar_csv(nome: str, linhas: list[dict[str, Any]] | pd.DataFrame) -> None:
    destino = caminho_saida_diagnostico(RAIZ, nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df = linhas if isinstance(linhas, pd.DataFrame) else pd.DataFrame(linhas)
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"CSV: {destino.relative_to(RAIZ).as_posix()}")


def _safe_float(valor: Any) -> float:
    try:
        if valor is None or pd.isna(valor):
            return 0.0
    except Exception:
        if valor is None:
            return 0.0
    try:
        return float(valor)
    except Exception:
        return 0.0


def _lista(obj: Any) -> list[Any]:
    if isinstance(obj, list):
        return obj
    if isinstance(obj, str):
        try:
            parsed = ast.literal_eval(obj)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


def _usa_lote_planejado(resultado_pagamento: dict[str, Any]) -> bool:
    metadados = resultado_pagamento.get("metadados_escolhidos") or {}
    if bool(metadados.get("origem_aporte_planejado_v216")):
        return True
    for comp in _lista(resultado_pagamento.get("componentes_escolhidos")):
        if not isinstance(comp, dict):
            continue
        if bool(comp.get("origem_aporte_planejado_v216")):
            return True
        if "ap_planejado_v216" in str(comp.get("fonte_id") or ""):
            return True
    return False


def _ids_lotes_planejados_usados(resultado_pagamento: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for comp in _lista(resultado_pagamento.get("componentes_escolhidos")):
        if not isinstance(comp, dict):
            continue
        fonte_id = str(comp.get("fonte_id") or "")
        if "ap_planejado_v216" in fonte_id:
            ids.append(fonte_id)
    return ids


def _resumir_pagamento(item: dict[str, Any], cenario: str) -> dict[str, Any]:
    return {
        "cenario": cenario,
        "pagamento_id": item.get("pagamento_id") or item.get("despesa_id"),
        "data_pagamento": item.get("data_pagamento"),
        "melhor_acao_pagamento": item.get("melhor_acao_pagamento"),
        "fonte_principal_tipo": item.get("fonte_principal_tipo"),
        "fonte_principal_id": item.get("fonte_principal_id"),
        "valor_coberto": round(_safe_float(item.get("valor_coberto")), 2),
        "valor_deficit": round(_safe_float(item.get("valor_deficit")), 2),
        "cobertura_integral": bool(item.get("cobertura_integral")),
        "custo_fiscal_imediato": round(_safe_float(item.get("custo_fiscal_imediato")), 2),
        "perda_retorno_terminal_estimada": round(_safe_float(item.get("perda_retorno_terminal_estimada")), 2),
        "penalidade_liquidez_futura": round(_safe_float(item.get("penalidade_liquidez_futura")), 2),
        "penalidade_estrategica_lote": round(_safe_float(item.get("penalidade_estrategica_lote")), 2),
        "usa_lote_planejado_v216": _usa_lote_planejado(item),
        "lotes_planejados_usados": " | ".join(_ids_lotes_planejados_usados(item)),
    }


def _rodar_real(habilitar_aportes: bool, limite_pagamentos: int) -> dict[str, Any]:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
    )
    data_inicio = contexto.execucao.data_referencia
    data_fim = data_inicio + timedelta(days=60)
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite_pagamentos=limite_pagamentos,
    )
    config = deepcopy(contexto.pacote_config.conteudo)
    config.setdefault("aportes_futuros_v216", {})
    config["aportes_futuros_v216"]["habilitado"] = bool(habilitar_aportes)
    config.setdefault("desabilitar_modelos_script1_fase1", True)
    return simular_cenario_eventos_v1(
        estado,
        eventos_candidatos=[],
        config=config,
        horizonte={
            "diagnostico": "impacto_contas_futuras_v217",
            "cenario_aportes_planejados": "com_aportes_planejados" if habilitar_aportes else "sem_aportes_planejados",
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
        },
    )


def _resumo_resultado(resultado: dict[str, Any], cenario: str) -> dict[str, Any]:
    pagamentos = list(resultado.get("resultados_pagamento") or [])
    lotes_planejados = [
        item for item in list((resultado.get("estado_final_estimado") or {}).get("lotes_aportados") or [])
        if bool(item.get("origem_aporte_planejado_v216"))
    ]
    auditoria = list(resultado.get("auditoria_aportes_planejados_v216") or [])
    pagamentos_com_planejado = [p for p in pagamentos if _usa_lote_planejado(p)]
    return {
        "cenario": cenario,
        "status_simulador": resultado.get("status"),
        "pagamentos_processados": len(pagamentos),
        "pagamentos_cobertura_integral": sum(1 for p in pagamentos if bool(p.get("cobertura_integral"))),
        "pagamentos_com_deficit": sum(1 for p in pagamentos if _safe_float(p.get("valor_deficit")) > 0.01),
        "deficit_total": round(sum(_safe_float(p.get("valor_deficit")) for p in pagamentos), 2),
        "valor_coberto_total": round(sum(_safe_float(p.get("valor_coberto")) for p in pagamentos), 2),
        "custo_fiscal_total": round(sum(_safe_float(p.get("custo_fiscal_imediato")) for p in pagamentos), 2),
        "perda_terminal_total": round(sum(_safe_float(p.get("perda_retorno_terminal_estimada")) for p in pagamentos), 2),
        "penalidade_liquidez_total": round(sum(_safe_float(p.get("penalidade_liquidez_futura")) for p in pagamentos), 2),
        "penalidade_estrategica_total": round(sum(_safe_float(p.get("penalidade_estrategica_lote")) for p in pagamentos), 2),
        "patrimonio_terminal_proxy": resultado.get("patrimonio_liquido_terminal_proxy"),
        "eventos_auditoria_aportes": len(auditoria),
        "lotes_planejados_promovidos": len(lotes_planejados),
        "pagamentos_usando_lote_planejado": len(pagamentos_com_planejado),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Executa contra a planilha real.")
    parser.add_argument("--limite-pagamentos", type=int, default=30)
    args = parser.parse_args()

    if not args.real:
        raise SystemExit("Use --real para a auditoria V217. Esta etapa é definida para contas futuras reais.")

    sem = _rodar_real(False, args.limite_pagamentos)
    com = _rodar_real(True, args.limite_pagamentos)

    pagamentos_sem = [_resumir_pagamento(p, "sem_aportes_planejados") for p in list(sem.get("resultados_pagamento") or [])]
    pagamentos_com = [_resumir_pagamento(p, "com_aportes_planejados") for p in list(com.get("resultados_pagamento") or [])]
    df_sem = pd.DataFrame(pagamentos_sem)
    df_com = pd.DataFrame(pagamentos_com)

    chave = ["pagamento_id"]
    comparativo = df_sem.merge(
        df_com,
        on=chave,
        how="outer",
        suffixes=("_sem_aporte", "_com_aporte"),
    )
    for col in [
        "valor_coberto", "valor_deficit", "custo_fiscal_imediato",
        "perda_retorno_terminal_estimada", "penalidade_liquidez_futura", "penalidade_estrategica_lote"
    ]:
        comparativo[f"delta_{col}_com_menos_sem"] = (
            comparativo[f"{col}_com_aporte"].fillna(0.0) - comparativo[f"{col}_sem_aporte"].fillna(0.0)
        ).round(2)

    comparativo["mudou_acao"] = (
        comparativo["melhor_acao_pagamento_sem_aporte"].astype(str)
        != comparativo["melhor_acao_pagamento_com_aporte"].astype(str)
    )
    comparativo["mudou_fonte_principal"] = (
        comparativo["fonte_principal_id_sem_aporte"].astype(str)
        != comparativo["fonte_principal_id_com_aporte"].astype(str)
    )
    comparativo["usa_lote_planejado_v216_com_aporte"] = comparativo["usa_lote_planejado_v216_com_aporte"].fillna(False)

    resumo = pd.DataFrame([
        _resumo_resultado(sem, "sem_aportes_planejados"),
        _resumo_resultado(com, "com_aportes_planejados"),
    ])
    resumo_delta = {
        "cenario": "delta_com_menos_sem",
        "status_simulador": "comparativo_v217",
    }
    for col in [
        "pagamentos_processados", "pagamentos_cobertura_integral", "pagamentos_com_deficit",
        "deficit_total", "valor_coberto_total", "custo_fiscal_total", "perda_terminal_total",
        "penalidade_liquidez_total", "penalidade_estrategica_total", "eventos_auditoria_aportes",
        "lotes_planejados_promovidos", "pagamentos_usando_lote_planejado"
    ]:
        resumo_delta[col] = round(float(resumo.loc[resumo["cenario"].eq("com_aportes_planejados"), col].iloc[0]) - float(resumo.loc[resumo["cenario"].eq("sem_aportes_planejados"), col].iloc[0]), 2)
    try:
        resumo_delta["patrimonio_terminal_proxy"] = round(float(resumo.loc[resumo["cenario"].eq("com_aportes_planejados"), "patrimonio_terminal_proxy"].iloc[0]) - float(resumo.loc[resumo["cenario"].eq("sem_aportes_planejados"), "patrimonio_terminal_proxy"].iloc[0]), 2)
    except Exception:
        resumo_delta["patrimonio_terminal_proxy"] = ""
    resumo = pd.concat([resumo, pd.DataFrame([resumo_delta])], ignore_index=True)

    lotes_planejados = [
        item for item in list((com.get("estado_final_estimado") or {}).get("lotes_aportados") or [])
        if bool(item.get("origem_aporte_planejado_v216"))
    ]

    alertas: list[dict[str, Any]] = []
    for _, row in comparativo.iterrows():
        if _safe_float(row.get("delta_valor_deficit_com_menos_sem")) > 0.01:
            alertas.append({"tipo_alerta": "aumento_deficit", "pagamento_id": row.get("pagamento_id"), "detalhe": row.get("delta_valor_deficit_com_menos_sem")})
        if bool(row.get("usa_lote_planejado_v216_com_aporte")) and not bool(row.get("cobertura_integral_com_aporte")):
            alertas.append({"tipo_alerta": "lote_planejado_usado_sem_cobertura_integral", "pagamento_id": row.get("pagamento_id"), "detalhe": row.get("valor_deficit_com_aporte")})
    for item in list(com.get("auditoria_aportes_planejados_v216") or []):
        if str(item.get("status_integracao_v216") or "") == "PROMOVIDO_CONTROLADO_V216" and not bool(item.get("invariante_v216_valida")):
            alertas.append({"tipo_alerta": "invariante_promovido_invalido", "pagamento_id": "", "detalhe": item.get("recebido_id")})

    _salvar_csv(f"impacto_contas_futuras_{VERSAO_BASELINE.lower()}_resumo_real.csv", resumo)
    _salvar_csv(f"impacto_contas_futuras_{VERSAO_BASELINE.lower()}_comparativo_pagamentos_real.csv", comparativo)
    _salvar_csv(f"impacto_contas_futuras_{VERSAO_BASELINE.lower()}_lotes_planejados_real.csv", lotes_planejados)
    _salvar_csv(f"impacto_contas_futuras_{VERSAO_BASELINE.lower()}_alertas_real.csv", alertas)

    print("=== AUDITORIA DE IMPACTO SOBRE CONTAS FUTURAS V217 ===")
    print(f"versao: {VERSAO_BASELINE}")
    print("modo: real")
    print(f"pagamentos_processados_sem_aporte: {len(pagamentos_sem)}")
    print(f"pagamentos_processados_com_aporte: {len(pagamentos_com)}")
    print(f"lotes_planejados_promovidos: {len(lotes_planejados)}")
    print(f"pagamentos_usando_lote_planejado: {int(resumo.loc[resumo['cenario'].eq('com_aportes_planejados'), 'pagamentos_usando_lote_planejado'].iloc[0])}")
    print(f"alertas: {len(alertas)}")
    print(f"status_sem_aporte: {sem.get('status')}")
    print(f"status_com_aporte: {com.get('status')}")

    if alertas:
        raise SystemExit("auditoria_impacto_v217_com_alertas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
