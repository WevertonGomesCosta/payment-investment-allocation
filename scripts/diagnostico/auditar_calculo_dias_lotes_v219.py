"""Auditoria V219 do cálculo de dias dos lotes e idade fiscal centralizada.

A V219 não promove baseline. Ela mantém `calcular_dias_lote(...)` como fonte
única para campos visuais `Dias corridos`/`Dias úteis` e centraliza a idade
fiscal usada pelo alocador em `nucleo.fiscal_lotes`.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any
import json
import re

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from nucleo.ambiente import bootstrap_ambiente
from nucleo.calendario_financeiro import calcular_dias_lote, construir_calendario_financeiro
from nucleo.carregador_config import carregar_config
from nucleo.fiscal_lotes import aliquota_ir_regressiva_renda_fixa, calcular_idade_fiscal_lote
from nucleo.identidade_baseline import VERSAO_BASELINE, caminho_saida_diagnostico


def _salvar_csv(nome: str, linhas: list[dict[str, Any]] | pd.DataFrame) -> None:
    destino = caminho_saida_diagnostico(RAIZ, nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    df = linhas if isinstance(linhas, pd.DataFrame) else pd.DataFrame(linhas)
    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"CSV: {destino.relative_to(RAIZ).as_posix()}")


def _parse_data(valor: Any) -> date | None:
    try:
        if valor in (None, "") or pd.isna(valor):
            return None
    except Exception:
        if valor in (None, ""):
            return None
    if isinstance(valor, pd.Timestamp):
        if pd.isna(valor):
            return None
        return valor.date()
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        texto = str(valor).strip()
        if not texto or texto.lower() in {"nan", "nat", "none"}:
            return None
        return date.fromisoformat(texto[:10])
    except Exception:
        return None


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


def _carregar_serie_cdi() -> dict[date, float]:
    caminho = RAIZ / "dados" / "cache_bcb.json"
    if not caminho.exists():
        return {}
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    mapa = dados.get("mapa") if isinstance(dados, dict) else {}
    serie: dict[date, float] = {}
    if isinstance(mapa, dict):
        for k, v in mapa.items():
            try:
                serie[date.fromisoformat(str(k)[:10])] = float(v)
            except Exception:
                continue
    return serie


def _auditar_codigo_duplicado() -> pd.DataFrame:
    padroes = [
        ("uso_visual_canonico_calcular_dias_lote", re.compile(r"calcular_dias_lote\(")),
        ("uso_fiscal_canonico_v219", re.compile(r"calcular_idade_fiscal_lote\(")),
        ("aliquota_fiscal_canonica_v219", re.compile(r"aliquota_ir_regressiva_renda_fixa\(")),
        ("uso_date_today", re.compile(r"date\.today\(")),
        ("funcao_local_dias_uteis", re.compile(r"def _contar_dias_uteis")),
        ("idade_visual_por_recebimento", re.compile(r"Dias Corridos.+data_recebimento|data_recebimento\)\.days")),
        ("idade_visual_por_base_fiscal", re.compile(r"Dias Corridos.+data_base_fiscal|data_base_fiscal\)\.days")),
        ("faixa_ir_local_no_alocador", re.compile(r"if dias <= 180:\s+aliquota = 0\.225")),
    ]
    ignorar = {
        "scripts/diagnostico/auditar_calculo_dias_lotes_v218.py",
        "scripts/diagnostico/auditar_calculo_dias_lotes_v219.py",
        "nucleo/fiscal_lotes.py",
    }
    linhas: list[dict[str, Any]] = []
    for caminho in sorted(RAIZ.rglob("*.py")):
        rel = caminho.relative_to(RAIZ).as_posix()
        if rel in ignorar or "__pycache__" in rel:
            continue
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
        for nome, padrao in padroes:
            for match in padrao.finditer(texto):
                linha = texto.count("\n", 0, match.start()) + 1
                status = "OK" if nome in {
                    "uso_visual_canonico_calcular_dias_lote",
                    "uso_fiscal_canonico_v219",
                    "aliquota_fiscal_canonica_v219",
                } else "VERIFICAR"
                linhas.append({
                    "arquivo": rel,
                    "linha": linha,
                    "padrao": nome,
                    "status": status,
                    "trecho": texto[match.start(): match.start() + 180].replace("\n", " "),
                })
    return pd.DataFrame(linhas)


def main() -> int:
    pacote_config = carregar_config(raiz_repositorio=RAIZ)
    contexto_execucao = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=["financeiro"],
        instalar_automaticamente=False,
    )
    data_referencia = contexto_execucao.data_referencia
    calendario = construir_calendario_financeiro(pacote_config.conteudo, data_referencia=data_referencia)
    serie_cdi = _carregar_serie_cdi()

    planilha = RAIZ / "dados" / "dados_financeiros.xlsx"
    inventario = pd.read_excel(planilha, sheet_name="Inventário de Lotes")

    linhas_lotes: list[dict[str, Any]] = []
    linhas_fiscais: list[dict[str, Any]] = []

    for _, row in inventario.iterrows():
        lote_id = str(row.get("Lote (ID)") or "").strip()
        data_recebimento = _parse_data(row.get("Data Recebimento"))
        data_aplicacao = _parse_data(row.get("Data Aplicação"))
        investimento = "" if pd.isna(row.get("Investimento")) else str(row.get("Investimento") or "").strip()
        valor_original = _safe_float(row.get("Valor Original"))

        if not lote_id or data_recebimento is None or data_aplicacao is None:
            continue
        if data_aplicacao > data_referencia:
            continue

        status_operacional = "lote_aportado_ativo" if investimento and investimento != "-" else "nao_aportado_ou_exaurido"
        idade_visual = calcular_dias_lote(
            data_aplicacao,
            data_referencia,
            calendario,
            serie_cdi=serie_cdi,
            data_fechamento_referencia=data_referencia,
        )
        idade_fiscal = calcular_idade_fiscal_lote(data_aplicacao, data_referencia)
        aliquota = aliquota_ir_regressiva_renda_fixa(idade_fiscal)
        dias_recebimento_ate_aplicacao = max((data_aplicacao - data_recebimento).days, 0)

        linhas_lotes.append({
            "lote": lote_id,
            "status_operacional": status_operacional,
            "recebimento": data_recebimento.isoformat(),
            "aplicacao": data_aplicacao.isoformat(),
            "produto": investimento,
            "valor_original": round(valor_original, 2),
            "data_referencia_usada": data_referencia.isoformat(),
            "dias_corridos_v219": idade_visual["dias_corridos"],
            "dias_uteis_v219": idade_visual["dias_uteis"],
            "dias_recebimento_ate_aplicacao": dias_recebimento_ate_aplicacao,
            "corrigiu_uso_recebimento_como_idade": idade_visual["dias_corridos"] != dias_recebimento_ate_aplicacao,
        })
        linhas_fiscais.append({
            "lote": lote_id,
            "data_aplicacao": data_aplicacao.isoformat(),
            "data_referencia": data_referencia.isoformat(),
            "idade_fiscal_dias_corridos_v219": idade_fiscal,
            "aliquota_ir_estimativa_v219": aliquota,
            "fonte_funcao": "nucleo.fiscal_lotes.calcular_idade_fiscal_lote",
        })

    df_lotes = pd.DataFrame(linhas_lotes)
    df_lote_5680 = df_lotes[df_lotes["lote"].astype(str).str.contains("Lote 5680 abr.", regex=False, na=False)].copy()
    df_fiscal = pd.DataFrame(linhas_fiscais)
    duplicacoes = _auditar_codigo_duplicado()

    if len(duplicacoes):
        criticos = duplicacoes[
            (
                (duplicacoes["arquivo"] == "nucleo/saida_canonica.py")
                & duplicacoes["padrao"].isin(["idade_visual_por_recebimento", "idade_visual_por_base_fiscal", "funcao_local_dias_uteis"])
            )
            | (
                (duplicacoes["arquivo"] == "nucleo/replay_passado_controlado.py")
                & duplicacoes["padrao"].isin(["idade_visual_por_recebimento", "idade_visual_por_base_fiscal", "funcao_local_dias_uteis"])
            )
            | (
                (duplicacoes["arquivo"] == "scripts/auditoria/gerar_auditoria_diaria_lote.py")
                & duplicacoes["padrao"].isin(["funcao_local_dias_uteis"])
            )
            | (
                (duplicacoes["arquivo"] == "nucleo/alocador_pagamentos_terminal_v1.py")
                & duplicacoes["padrao"].isin(["uso_date_today", "faixa_ir_local_no_alocador"])
            )
        ]
    else:
        criticos = pd.DataFrame()

    _salvar_csv("auditoria_calculo_dias_lotes_v219_real.csv", df_lotes)
    _salvar_csv("auditoria_lote_5680_abr_v219_real.csv", df_lote_5680)
    _salvar_csv("auditoria_idade_fiscal_lotes_v219_real.csv", df_fiscal)
    _salvar_csv("auditoria_calculo_dias_duplicacoes_v219.csv", duplicacoes)

    print("=== AUDITORIA CALCULO DIAS LOTES V219 ===")
    print(f"versao: {VERSAO_BASELINE}")
    print(f"data_referencia: {data_referencia.isoformat()}")
    print(f"lotes_auditados: {len(df_lotes)}")
    print(f"lotes_com_idade_fiscal_auditada: {len(df_fiscal)}")
    print(f"lote_5680_abr_linhas: {len(df_lote_5680)}")
    if len(df_lote_5680):
        r = df_lote_5680.iloc[0]
        print(f"lote_5680_abr_dias_corridos_v219: {int(r['dias_corridos_v219'])}")
        print(f"lote_5680_abr_dias_uteis_v219: {int(r['dias_uteis_v219'])}")
        print(f"lote_5680_abr_dias_recebimento_ate_aplicacao: {int(r['dias_recebimento_ate_aplicacao'])}")
        print(f"lote_5680_abr_data_referencia_usada: {r['data_referencia_usada']}")
    print(f"duplicacoes_criticas: {len(criticos)}")
    status = "calculo_dias_e_idade_fiscal_canonico_v219_validado" if len(df_lote_5680) == 1 and len(criticos) == 0 else "revisar_calculo_dias_v219"
    print(f"status: {status}")
    return 0 if status == "calculo_dias_e_idade_fiscal_canonico_v219_validado" else 1


if __name__ == "__main__":
    raise SystemExit(main())
