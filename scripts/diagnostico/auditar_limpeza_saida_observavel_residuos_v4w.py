from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARQ_GERAR = ROOT / "nucleo" / "gerar_planilha_operacional.py"
ARQ_SAIDA = ROOT / "nucleo" / "saida_observavel.py"
ARQ_CONSOLE = ROOT / "aplicacao" / "console" / "principal.py"


def _all_in(txt: str, termos: list[str]) -> bool:
    return all(t in txt for t in termos)


def _none_in(txt: str, termos: list[str]) -> bool:
    return all(t not in txt for t in termos)


def main() -> None:
    gerar = ARQ_GERAR.read_text(encoding="utf-8")
    saida = ARQ_SAIDA.read_text(encoding="utf-8")
    console = ARQ_CONSOLE.read_text(encoding="utf-8")

    gerar_planilha_operacional_consumindo_pacote = _all_in(gerar, [
        "construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
        "construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal=pacote_consolidado)",
    ])

    console_consumindo_pacote = _all_in(console, [
        "construir_resumo_patrimonio_total_lotes(",
        "pacote_saida_observavel_temporal=pacote_saida_observavel_temporal",
        "construir_switchings_observaveis(contexto_baseline, saida_canonica, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
    ])

    saida_observavel_sem_fallback_silencioso_sem_pacote = "saida_observavel_requer_pacote_saida_observavel_temporal_na_V4W" in saida

    funcoes_publicas_criticas_exigem_ou_recebem_pacote = _all_in(saida, [
        "def construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
        "def construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
        "def construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
        "_exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)",
    ])

    sem_somar = "somar_valores_sacados_por_lote" not in saida
    sem_replay = _none_in(saida, ["replay_passado", "log_passado", "lotes_apos_replay", "lotes_antes_replay", "lotes_replay", "lotes_originais"])
    sem_dict = _none_in(saida, ["__dict__", "fila = [contexto]"])
    sem_df_generic = _none_in(saida, ["iterrows", ".columns"])
    bootstrap_pacote_explicito = "modo_bootstrap_pacote: bool = False" in saida
    helpers_legados_removidos = _none_in(saida, [
        "somar_valores_sacados_por_lote", "_mapa_aplicacao_por_lote", "_mapa_produto_por_lote", "_mapa_valor_original_por_lote", "_mapa_saldo_final_replay_por_lote", "_mapa_pagamentos_replay_por_chave", "_lote_deve_ser_ativo_observavel_por_replay"
    ])

    res = {
        "gerar_planilha_operacional_consumindo_pacote": gerar_planilha_operacional_consumindo_pacote,
        "console_consumindo_pacote": console_consumindo_pacote,
        "saida_observavel_sem_fallback_silencioso_sem_pacote": saida_observavel_sem_fallback_silencioso_sem_pacote,
        "funcoes_publicas_criticas_exigem_ou_recebem_pacote": funcoes_publicas_criticas_exigem_ou_recebem_pacote,
        "saida_observavel_sem_somar_valores_sacados_por_lote": sem_somar,
        "saida_observavel_sem_acesso_direto_replay": sem_replay,
        "saida_observavel_sem_varredura_dict_contexto": sem_dict,
        "saida_observavel_sem_varredura_generica_dataframe": sem_df_generic,
        "helpers_legados_removidos": helpers_legados_removidos,
        "bootstrap_pacote_explicito": bootstrap_pacote_explicito,
    }
    res["validacao_v4w_ok"] = all(res.values())
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
