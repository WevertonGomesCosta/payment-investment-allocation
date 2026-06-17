from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from aplicacao.principal import carregar_contexto_e_saida


OUT_DIR = RAIZ / "saidas" / "diagnostico"
OUT_CSV = OUT_DIR / "auditoria_rendimento_motor_calibrado_me531.csv"
OUT_MD = OUT_DIR / "auditoria_rendimento_motor_calibrado_me531.md"

COLUNAS_OBRIGATORIAS = {
    "Rend. líq.",
    "Rend. líq. motor",
    "Dif. rend.",
    "Rend. motor teórico",
    "Dif. teórica",
}


def valor_numerico(valor: Any) -> bool:
    if valor is None or valor == "":
        return False
    try:
        float(valor)
        return True
    except Exception:
        return False


def fnum(valor: Any) -> float:
    if not valor_numerico(valor):
        return 0.0
    return round(float(valor), 2)


def classe_materialidade(valor: Any) -> str:
    if not valor_numerico(valor):
        return "n/d"
    abs_val = abs(float(valor))
    if abs_val <= 0.20:
        return "dentro_tolerancia_020"
    if abs_val <= 0.50:
        return "residuo_pequeno"
    return "fora_tolerancia_material"


def linhas_situacao_atual(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for grupo, attr in [
        ("exauridos", "situacao_atual_lotes_exauridos_valores"),
        ("ativos", "situacao_atual_lotes_ativos_valores"),
    ]:
        for row in list(getattr(saida_canonica_oficial, attr, []) or []):
            item = dict(row)
            item["grupo_publicado"] = grupo
            linhas.append(item)
    return linhas


def montar_linhas_auditoria(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    saida: list[dict[str, Any]] = []
    for row in linhas_situacao_atual(saida_canonica_oficial):
        faltantes = sorted(col for col in COLUNAS_OBRIGATORIAS if col not in row)
        dif_calibrada = row.get("Dif. rend.")
        dif_teorica = row.get("Dif. teórica")
        saida.append(
            {
                "grupo_publicado": row.get("grupo_publicado"),
                "lote": row.get("Lote"),
                "rendimento_observado": row.get("Rend. líq."),
                "rendimento_motor_calibrado": row.get("Rend. líq. motor"),
                "dif_calibrada": dif_calibrada,
                "classe_dif_calibrada": classe_materialidade(dif_calibrada),
                "rendimento_motor_teorico": row.get("Rend. motor teórico"),
                "dif_teorica": dif_teorica,
                "classe_dif_teorica": classe_materialidade(dif_teorica),
                "colunas_obrigatorias_presentes": len(faltantes) == 0,
                "colunas_faltantes": " | ".join(faltantes),
            }
        )
    return saida


def escrever_csv(rows: list[dict[str, Any]]) -> None:
    campos = list(rows[0].keys()) if rows else []
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(rows)


def escrever_md(rows: list[dict[str, Any]], auditoria_me531: dict[str, Any]) -> None:
    faltantes = [r for r in rows if not r["colunas_obrigatorias_presentes"]]
    fora = [r for r in rows if r["classe_dif_calibrada"] == "fora_tolerancia_material"]
    dentro = [r for r in rows if r["classe_dif_calibrada"] == "dentro_tolerancia_020"]
    teoricos = [r for r in rows if valor_numerico(r["rendimento_motor_teorico"])]
    evidencia_publicada = bool(rows) and not faltantes and len(teoricos) > 0

    md: list[str] = []
    md.append("# ME-531 — Auditoria do rendimento motor calibrado\n\n")
    md.append("## Resumo\n\n")
    md.append(f"- lotes auditados: {len(rows)}\n")
    md.append(f"- linhas com colunas obrigatórias ausentes: {len(faltantes)}\n")
    md.append(f"- linhas com diferença calibrada dentro de 0,20: {len(dentro)}\n")
    md.append(f"- linhas com diferença calibrada material fora de 0,50: {len(fora)}\n")
    md.append(f"- linhas com motor teórico preservado: {len(teoricos)}\n")
    md.append(f"- evidência ME-531 publicada nas colunas: {evidencia_publicada}\n")
    md.append(f"- auditoria ME-531 preservada em metadado, se disponível: {bool(auditoria_me531)}\n")
    md.append(f"- versão ME-531: {auditoria_me531.get('versao', 'n/d') if auditoria_me531 else 'n/d'}\n")

    md.append("\n## Evidência de arquitetura\n\n")
    for chave in [
        "fonte_primaria",
        "nao_usa_saida_renderizada_como_fonte_primaria",
        "preserva_motor_teorico",
        "qtd_lotes_pre_replay",
        "qtd_lotes_pos_replay",
        "qtd_lotes_com_movimentos_replay",
        "qtd_origens_switching_calibraveis",
        "qtd_linhas_fallback_teorico",
    ]:
        md.append(f"- {chave}: {auditoria_me531.get(chave, 'n/d') if auditoria_me531 else 'n/d'}\n")

    md.append("\n## Maiores diferenças calibradas\n\n")
    for row in sorted(rows, key=lambda r: abs(fnum(r["dif_calibrada"])), reverse=True)[:12]:
        md.append(
            f"- {row['lote']} | grupo={row['grupo_publicado']} | "
            f"obs={fnum(row['rendimento_observado']):.2f} | "
            f"calib={fnum(row['rendimento_motor_calibrado']):.2f} | "
            f"dif_calib={fnum(row['dif_calibrada']):.2f} | "
            f"teorico={fnum(row['rendimento_motor_teorico']):.2f} | "
            f"dif_teorica={fnum(row['dif_teorica']):.2f}\n"
        )

    md.append("\n## Decisão da auditoria\n\n")
    if faltantes:
        md.append("- status: reprovado_colunas_obrigatorias_ausentes\n")
    elif fora:
        md.append("- status: aprovado_com_ressalva_diferenca_calibrada_material\n")
    else:
        md.append("- status: aprovado\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (
        contexto,
        estado_temporal_inicial,
        resultado_motor_temporal_conjunto,
        ledger_temporal_canonico,
        resultado_gates_validacao_nucleo,
        saida_canonica,
        saida_canonica_oficial,
        pacote_saida_observavel_oficial,
    ) = carregar_contexto_e_saida()

    _ = contexto
    _ = estado_temporal_inicial
    _ = resultado_motor_temporal_conjunto
    _ = ledger_temporal_canonico
    _ = saida_canonica
    _ = pacote_saida_observavel_oficial

    if not getattr(resultado_gates_validacao_nucleo, "pronto_para_etapa8", False):
        raise RuntimeError("gates_nao_aprovados_para_auditoria_me531")

    rows = montar_linhas_auditoria(saida_canonica_oficial)
    auditoria_situacao = dict(getattr(saida_canonica_oficial, "auditoria_situacao_atual_oficial", {}) or {})
    metadados = dict(getattr(saida_canonica_oficial, "metadados", {}) or {})
    auditoria_me531 = dict(
        auditoria_situacao.get("me531_rendimento_motor_calibrado")
        or metadados.get("me531_rendimento_motor_calibrado")
        or {}
    )

    escrever_csv(rows)
    escrever_md(rows, auditoria_me531)

    faltantes = [r for r in rows if not r["colunas_obrigatorias_presentes"]]
    fora = [r for r in rows if r["classe_dif_calibrada"] == "fora_tolerancia_material"]

    print(f"[OK] CSV: {OUT_CSV}")
    print(f"[OK] MD:  {OUT_MD}")
    print(f"[OK] lotes auditados: {len(rows)}")
    print(f"[OK] evidência ME-531 publicada nas colunas: {bool(rows) and not faltantes}")
    print(f"[OK] auditoria ME-531 em metadado, se disponível: {bool(auditoria_me531)}")
    print(f"[OK] colunas obrigatórias ausentes: {len(faltantes)}")
    print(f"[OK] dif calibrada material fora de 0,50: {len(fora)}")


if __name__ == "__main__":
    main()
