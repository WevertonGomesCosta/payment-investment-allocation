"""ME-V241 — Auditoria diagnóstica motor versus central versus extrato futuro.

Este script é diagnóstico e não altera motor, recomputação central, saída
canônica, planilha operacional, dados financeiros, cache, regra econômica ou
fonte de verdade operacional.

Execução autorizada pela ME-V241:
    python scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py
"""
from __future__ import annotations

import csv
import math
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


VERSAO = "V241"
FONTE_DE_VERDADE_OPERACIONAL = "NAO_CONSOLIDADA"
PRECEDENCIA_ENTRE_CAMADAS = "NAO_DEFINIDA"


def localizar_raiz_repositorio() -> Path:
    atual = Path(__file__).resolve()
    for candidato in [atual.parent, *atual.parents]:
        if (candidato / "nucleo").is_dir() and (candidato / "scripts").is_dir():
            return candidato
    return atual.parents[2]


def valor_normalizado(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and math.isnan(valor):
        return ""
    texto = str(valor).strip()
    if texto.lower() in {"nan", "none", "nat"}:
        return ""
    return texto


def numero_normalizado(valor: Any) -> float | None:
    if valor is None:
        return None
    if isinstance(valor, str) and not valor.strip():
        return None
    try:
        numero = float(valor)
    except Exception:
        return None
    if math.isnan(numero):
        return None
    return round(numero, 2)


def bool_normalizado(valor: Any) -> str:
    if isinstance(valor, bool):
        return "sim" if valor else "não"
    texto = valor_normalizado(valor).lower()
    if texto in {"sim", "s", "true", "1", "yes"}:
        return "sim"
    if texto in {"não", "nao", "n", "false", "0", "no", ""}:
        return "não"
    return texto


def valores_iguais_texto(a: Any, b: Any) -> bool:
    return valor_normalizado(a) == valor_normalizado(b)


def valores_iguais_numero(a: Any, b: Any, tolerancia: float = 0.01) -> bool:
    na = numero_normalizado(a)
    nb = numero_normalizado(b)
    if na is None and nb is None:
        return True
    if na is None or nb is None:
        return False
    return abs(na - nb) <= tolerancia


def dataframe_por_pagamento(quadro: Any, coluna_id: str) -> pd.DataFrame:
    if not isinstance(quadro, pd.DataFrame) or len(quadro) == 0:
        return pd.DataFrame()
    df = quadro.copy()
    if coluna_id not in df.columns:
        return pd.DataFrame()
    df[coluna_id] = df[coluna_id].fillna("").astype(str).str.strip()
    df = df[df[coluna_id] != ""]
    if len(df) == 0:
        return pd.DataFrame()
    return df.drop_duplicates(subset=[coluna_id], keep="first").set_index(coluna_id, drop=False)


def construir_extrato_futuro(contexto: Any) -> pd.DataFrame:
    from nucleo.saida_canonica import construir_saida_canonica

    pacote_saida = construir_saida_canonica(contexto)
    extrato = getattr(pacote_saida, "extrato_futuro", []) or []
    df = pd.DataFrame(extrato)
    if len(df) == 0 or "Despesa ID" not in df.columns:
        return pd.DataFrame()
    df["Despesa ID"] = df["Despesa ID"].fillna("").astype(str).str.strip()
    df = df[df["Despesa ID"] != ""]
    return df.drop_duplicates(subset=["Despesa ID"], keep="first").set_index("Despesa ID", drop=False)


def linha_detalhe(pagamento_id: str, motor: dict[str, Any], central: dict[str, Any], extrato: dict[str, Any]) -> dict[str, Any]:
    lote_motor = motor.get("lote_recomendado")
    lote_central = central.get("lote_final_central") or central.get("lote_sugerido_original")
    lote_extrato = extrato.get("Lote sugerido")

    estrategia_motor = motor.get("estrategia_recomendada")
    estrategia_extrato = extrato.get("Estratégia")

    cobertura_motor = bool_normalizado(motor.get("cobertura_integral_recomendada"))
    cobertura_central = bool_normalizado(central.get("pagamento_totalmente_coberto_central"))
    cobertura_extrato = bool_normalizado(extrato.get("Cobertura integral"))

    saldo_motor = motor.get("saldo_residual_temporal_pos_recomendacao")
    saldo_central = central.get("saldo_remanescente_central")
    saldo_extrato = extrato.get("Saldo Remanescente")

    switching_motor = bool_normalizado(motor.get("necessidade_switching"))
    switching_extrato = bool_normalizado(extrato.get("Necessita switching"))

    divergencia_lote_motor_central = not valores_iguais_texto(lote_motor, lote_central)
    divergencia_lote_motor_extrato = not valores_iguais_texto(lote_motor, lote_extrato)
    divergencia_lote_central_extrato = not valores_iguais_texto(lote_central, lote_extrato)
    divergencia_estrategia = not valores_iguais_texto(estrategia_motor, estrategia_extrato)
    divergencia_cobertura_motor_central = cobertura_motor != cobertura_central
    divergencia_cobertura_motor_extrato = cobertura_motor != cobertura_extrato
    divergencia_cobertura_central_extrato = cobertura_central != cobertura_extrato
    divergencia_saldo_motor_central = not valores_iguais_numero(saldo_motor, saldo_central)
    divergencia_saldo_motor_extrato = not valores_iguais_numero(saldo_motor, saldo_extrato)
    divergencia_saldo_central_extrato = not valores_iguais_numero(saldo_central, saldo_extrato)
    divergencia_switching = switching_motor != switching_extrato

    origem_mista = False
    if valores_iguais_texto(estrategia_motor, estrategia_extrato) and valores_iguais_texto(lote_central, lote_extrato) and not valores_iguais_texto(lote_motor, lote_extrato):
        origem_mista = True
    if valores_iguais_numero(saldo_central, saldo_extrato) and not valores_iguais_numero(saldo_motor, saldo_extrato):
        origem_mista = True

    return {
        "pagamento_id": pagamento_id,
        "data_pagamento_motor": valor_normalizado(motor.get("data_pagamento")),
        "descricao_motor": valor_normalizado(motor.get("descricao_pagamento")),
        "valor_motor": numero_normalizado(motor.get("valor_pagamento")),
        "lote_recomendado_motor": valor_normalizado(lote_motor),
        "lote_final_central": valor_normalizado(lote_central),
        "lote_sugerido_extrato": valor_normalizado(lote_extrato),
        "estrategia_recomendada_motor": valor_normalizado(estrategia_motor),
        "estrategia_extrato": valor_normalizado(estrategia_extrato),
        "cobertura_integral_recomendada_motor": cobertura_motor,
        "pagamento_totalmente_coberto_central": cobertura_central,
        "cobertura_integral_extrato": cobertura_extrato,
        "saldo_residual_temporal_motor": numero_normalizado(saldo_motor),
        "saldo_remanescente_central": numero_normalizado(saldo_central),
        "saldo_remanescente_extrato": numero_normalizado(saldo_extrato),
        "necessidade_switching_motor": switching_motor,
        "necessita_switching_extrato": switching_extrato,
        "origem_mista_detectada": origem_mista,
        "divergencia_lote_motor_central": divergencia_lote_motor_central,
        "divergencia_lote_motor_extrato": divergencia_lote_motor_extrato,
        "divergencia_lote_central_extrato": divergencia_lote_central_extrato,
        "divergencia_estrategia_motor_extrato": divergencia_estrategia,
        "divergencia_cobertura_motor_central": divergencia_cobertura_motor_central,
        "divergencia_cobertura_motor_extrato": divergencia_cobertura_motor_extrato,
        "divergencia_cobertura_central_extrato": divergencia_cobertura_central_extrato,
        "divergencia_saldo_motor_central": divergencia_saldo_motor_central,
        "divergencia_saldo_motor_extrato": divergencia_saldo_motor_extrato,
        "divergencia_saldo_central_extrato": divergencia_saldo_central_extrato,
        "divergencia_switching_motor_extrato": divergencia_switching,
        "fonte_de_verdade_operacional": FONTE_DE_VERDADE_OPERACIONAL,
        "precedencia_entre_camadas": PRECEDENCIA_ENTRE_CAMADAS,
    }


def contar_verdadeiros(linhas: list[dict[str, Any]], campo: str) -> int:
    return sum(1 for linha in linhas if bool(linha.get(campo)))


def percentual(parte: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * parte / total, 2)


def construir_resumo(linhas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = len(linhas)
    metricas = [
        ("total_pagamentos_auditados", total),
        ("linhas_com_origem_mista_detectada", contar_verdadeiros(linhas, "origem_mista_detectada")),
        ("divergencia_lote_motor_central", contar_verdadeiros(linhas, "divergencia_lote_motor_central")),
        ("divergencia_lote_motor_extrato", contar_verdadeiros(linhas, "divergencia_lote_motor_extrato")),
        ("divergencia_lote_central_extrato", contar_verdadeiros(linhas, "divergencia_lote_central_extrato")),
        ("divergencia_estrategia_motor_extrato", contar_verdadeiros(linhas, "divergencia_estrategia_motor_extrato")),
        ("divergencia_cobertura_motor_central", contar_verdadeiros(linhas, "divergencia_cobertura_motor_central")),
        ("divergencia_cobertura_motor_extrato", contar_verdadeiros(linhas, "divergencia_cobertura_motor_extrato")),
        ("divergencia_cobertura_central_extrato", contar_verdadeiros(linhas, "divergencia_cobertura_central_extrato")),
        ("divergencia_saldo_motor_central", contar_verdadeiros(linhas, "divergencia_saldo_motor_central")),
        ("divergencia_saldo_motor_extrato", contar_verdadeiros(linhas, "divergencia_saldo_motor_extrato")),
        ("divergencia_saldo_central_extrato", contar_verdadeiros(linhas, "divergencia_saldo_central_extrato")),
        ("divergencia_switching_motor_extrato", contar_verdadeiros(linhas, "divergencia_switching_motor_extrato")),
    ]
    resumo = []
    for metrica, valor in metricas:
        resumo.append({
            "versao": VERSAO,
            "metrica": metrica,
            "valor": valor,
            "percentual_sobre_total": percentual(int(valor), total) if metrica != "total_pagamentos_auditados" else 100.0,
            "fonte_de_verdade_operacional": FONTE_DE_VERDADE_OPERACIONAL,
            "precedencia_entre_camadas": PRECEDENCIA_ENTRE_CAMADAS,
        })
    return resumo


def salvar_csv(caminho: Path, linhas: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not linhas:
        linhas = [{"status": "sem_linhas"}]
    campos = list(linhas[0].keys())
    with caminho.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for linha in linhas:
            writer.writerow(linha)


def executar_auditoria() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raiz = localizar_raiz_repositorio()
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

    from nucleo.contexto_baseline import carregar_contexto_baseline

    contexto = carregar_contexto_baseline(raiz_repositorio=raiz)

    motor = getattr(contexto, "motor_recomendacao_pagamentos_switching_v1", None)
    central = getattr(contexto, "recomputacao_sequencial_central_v1", None)
    quadro_motor = getattr(motor, "quadro_recomendacoes", None) if motor is not None else None
    quadro_central = getattr(central, "quadro_recomputacao_sequencial_central", None) if central is not None else None
    extrato = construir_extrato_futuro(contexto)

    df_motor = dataframe_por_pagamento(quadro_motor, "pagamento_id")
    df_central = dataframe_por_pagamento(quadro_central, "pagamento_id")

    ids = sorted(set(df_motor.index.astype(str)) | set(df_central.index.astype(str)) | set(extrato.index.astype(str)))
    detalhes: list[dict[str, Any]] = []
    for pagamento_id in ids:
        motor_row = df_motor.loc[pagamento_id].to_dict() if pagamento_id in df_motor.index else {}
        central_row = df_central.loc[pagamento_id].to_dict() if pagamento_id in df_central.index else {}
        extrato_row = extrato.loc[pagamento_id].to_dict() if pagamento_id in extrato.index else {}
        detalhes.append(linha_detalhe(pagamento_id, motor_row, central_row, extrato_row))

    return construir_resumo(detalhes), detalhes


def main() -> int:
    raiz = localizar_raiz_repositorio()
    resumo_path = raiz / "saidas" / "diagnostico" / "divergencias_motor_central_extrato_v241_resumo.csv"
    detalhe_path = raiz / "saidas" / "diagnostico" / "divergencias_motor_central_extrato_v241_detalhe.csv"

    try:
        resumo, detalhes = executar_auditoria()
        salvar_csv(resumo_path, resumo)
        salvar_csv(detalhe_path, detalhes)
        total = len(detalhes)
        print("=== ME-V241 AUDITORIA DIVERGENCIAS MOTOR x CENTRAL x EXTRATO ===")
        print(f"status: ok")
        print(f"total_pagamentos_auditados: {total}")
        print(f"CSV resumo: {resumo_path}")
        print(f"CSV detalhe: {detalhe_path}")
        print(f"fonte_de_verdade_operacional: {FONTE_DE_VERDADE_OPERACIONAL}")
        print(f"precedencia_entre_camadas: {PRECEDENCIA_ENTRE_CAMADAS}")
        return 0
    except Exception as exc:
        resumo = [{
            "versao": VERSAO,
            "metrica": "erro_execucao_auditoria_v241",
            "valor": valor_normalizado(exc),
            "percentual_sobre_total": 0.0,
            "fonte_de_verdade_operacional": FONTE_DE_VERDADE_OPERACIONAL,
            "precedencia_entre_camadas": PRECEDENCIA_ENTRE_CAMADAS,
        }]
        detalhe = [{
            "status": "erro_execucao_auditoria_v241",
            "erro": valor_normalizado(exc),
            "traceback": traceback.format_exc(),
            "fonte_de_verdade_operacional": FONTE_DE_VERDADE_OPERACIONAL,
            "precedencia_entre_camadas": PRECEDENCIA_ENTRE_CAMADAS,
        }]
        salvar_csv(resumo_path, resumo)
        salvar_csv(detalhe_path, detalhe)
        print("=== ME-V241 AUDITORIA DIVERGENCIAS MOTOR x CENTRAL x EXTRATO ===")
        print("status: erro")
        print(f"erro: {exc}")
        print(f"CSV resumo: {resumo_path}")
        print(f"CSV detalhe: {detalhe_path}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
