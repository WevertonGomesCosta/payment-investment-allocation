from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQ_GERAR = ROOT / "nucleo" / "gerar_planilha_operacional.py"
ARQ_SAIDA = ROOT / "nucleo" / "saida_observavel.py"
ARQ_CONSOLE = ROOT / "aplicacao" / "console" / "principal.py"


def _all_in(txt: str, termos: list[str]) -> bool:
    return all(t in txt for t in termos)


def main() -> None:
    gerar = ARQ_GERAR.read_text(encoding="utf-8")
    saida = ARQ_SAIDA.read_text(encoding="utf-8")
    console = ARQ_CONSOLE.read_text(encoding="utf-8")

    gerar_planilha_operacional_consumindo_pacote = _all_in(
        gerar,
        [
            "def _adicionar_situacao_atual(wb, contexto, saida, pacote_saida_observavel_temporal)",
            "construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
            "_adicionar_situacao_atual(wb, contexto, saida, pacote_consolidado)",
            "construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal=pacote_consolidado)",
        ],
    )

    console_consumindo_pacote = _all_in(
        console,
        [
            "def _render_situacao_atual_operacional(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos, pacote_saida_observavel_temporal=None)",
            "construir_resumo_patrimonio_total_lotes(",
            "pacote_saida_observavel_temporal=pacote_saida_observavel_temporal",
            "construir_switchings_observaveis(contexto_baseline, saida_canonica, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
            "_render_amostras_pagamentos_operacionais(contexto_baseline, saida_canonica, pacote_saida_observavel_temporal)",
        ],
    )

    saida_observavel_sem_fallback_silencioso_sem_pacote = "saida_observavel_requer_pacote_saida_observavel_temporal_na_V4W" in saida

    funcoes_publicas_criticas_exigem_ou_recebem_pacote = _all_in(
        saida,
        [
            "def construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "def construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "def construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "_exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)",
        ],
    )

    res = {
        "gerar_planilha_operacional_consumindo_pacote": gerar_planilha_operacional_consumindo_pacote,
        "console_consumindo_pacote": console_consumindo_pacote,
        "saida_observavel_sem_fallback_silencioso_sem_pacote": saida_observavel_sem_fallback_silencioso_sem_pacote,
        "funcoes_publicas_criticas_exigem_ou_recebem_pacote": funcoes_publicas_criticas_exigem_ou_recebem_pacote,
    }
    res["validacao_v4w_ok"] = all(res.values())
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
