from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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

    res = {
        "gerar_planilha_operacional_consumindo_pacote": _all_in(gerar, [
            "construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
            "construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal=pacote_consolidado)",
        ]),
        "console_consumindo_pacote": _all_in(console, [
            "construir_resumo_patrimonio_total_lotes(",
            "pacote_saida_observavel_temporal=pacote_saida_observavel_temporal",
            "construir_switchings_observaveis(contexto_baseline, saida_canonica, pacote_saida_observavel_temporal=pacote_saida_observavel_temporal)",
        ]),
        "saida_observavel_sem_fallback_silencioso_sem_pacote": "saida_observavel_requer_pacote_saida_observavel_temporal_na_V4W" in saida,
        "funcoes_publicas_criticas_exigem_ou_recebem_pacote": _all_in(saida, [
            "def construir_blocos_situacao_atual(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "def construir_resumo_patrimonio_total_lotes(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "def construir_switchings_observaveis(contexto, saida, pacote_saida_observavel_temporal: Any | None = None)",
            "_exigir_pacote_saida_observavel_temporal(pacote_saida_observavel_temporal)",
        ]),
        "saida_observavel_sem_somar_valores_sacados_por_lote": "somar_valores_sacados_por_lote" not in saida,
        "saida_observavel_sem_acesso_direto_replay": _none_in(saida, ["replay_passado", "log_passado", "lotes_apos_replay", "lotes_antes_replay", "lotes_replay", "lotes_originais"]),
        "saida_observavel_sem_varredura_dict_contexto": _none_in(saida, ["__dict__", "fila = [contexto]"]),
        "saida_observavel_sem_varredura_generica_dataframe": _none_in(saida, ["iterrows", ".columns"]),
        "helpers_legados_removidos": _none_in(saida, [
            "somar_valores_sacados_por_lote", "_mapa_aplicacao_por_lote", "_mapa_produto_por_lote", "_mapa_valor_original_por_lote", "_mapa_saldo_final_replay_por_lote", "_mapa_pagamentos_replay_por_chave", "_lote_deve_ser_ativo_observavel_por_replay"
        ]),
        "bootstrap_pacote_explicito": "modo_bootstrap_pacote: bool = False" in saida,
    }

    res.update({
        "invariantes_render_ok": False,
        "invariantes_render_erro": "",
        "qtd_lotes_exauridos_por_saque_com_saque_zero": 0,
        "qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado": 0,
        "duplicidade_ativo_exaurido_lote_8500": False,
        "lote_3120_mai_bruto_sacado_renderizado": 0.0,
        "lote_3120_mai_liquido_sacado_renderizado": 0.0,
        "lote_3120_mai_patrimonio_liquido_renderizado": 0.0,
        "lote_3120_mai_rendimento_liquido_renderizado": 0.0,
        "lote_3120_mai_saldo_final": 0.0,
    })

    try:
        from nucleo.contexto_baseline import carregar_contexto_baseline
        from nucleo.saida_canonica import construir_saida_canonica
        from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
        from nucleo.saida_observavel import construir_linhas_lotes_consolidados

        ctx = carregar_contexto_baseline(raiz_repositorio=ROOT, instalar_automaticamente=False, incluir_benchmark_agrupado_individual_shadow=False)
        s0 = construir_saida_canonica(ctx)
        ativos_boot = construir_linhas_lotes_consolidados(ctx, s0, tipo="ativos", modo_bootstrap_pacote=True)
        ex_boot = construir_linhas_lotes_consolidados(ctx, s0, tipo="exauridos", modo_bootstrap_pacote=True)
        pacote = construir_pacote_saida_observavel_temporal(ctx, s0, lotes_ativos_observaveis=ativos_boot, lotes_exauridos_observaveis=ex_boot, pagamentos_realizados_observaveis=list(getattr(s0, "extrato_passado", []) or []))
        ativos = construir_linhas_lotes_consolidados(ctx, s0, tipo="ativos", pacote_saida_observavel_temporal=pacote)
        exauridos = construir_linhas_lotes_consolidados(ctx, s0, tipo="exauridos", pacote_saida_observavel_temporal=pacote)

        lote3120 = next((r for r in ativos if "3120" in str(r.get("Lote"))), {})
        res["lote_3120_mai_bruto_sacado_renderizado"] = round(float(lote3120.get("Bruto sac.") or 0), 2)
        res["lote_3120_mai_liquido_sacado_renderizado"] = round(float(lote3120.get("Líq. sac.") or 0), 2)
        res["lote_3120_mai_saldo_final"] = round(float(lote3120.get("Líq. atual") or 0), 2)
        res["lote_3120_mai_patrimonio_liquido_renderizado"] = round(float(lote3120.get("Patr. líq.") or 0), 2)
        res["lote_3120_mai_rendimento_liquido_renderizado"] = round(float(lote3120.get("Rend. líq.") or 0), 2)
        res["qtd_lotes_exauridos_por_saque_com_saque_zero"] = sum(1 for r in exauridos if str(r.get("Status ciclo")) == "exaurido_por_saque" and float(r.get("Líq. sac.") or 0) == 0)
        res["qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado"] = sum(1 for r in ativos if float(r.get("Líq. atual") or 0) > 0 and float(r.get("Orig.") or 0) > 0 and float(r.get("Líq. sac.") or 0) == 0 and float(r.get("Rend. líq.") or 0) < 0)
        res["duplicidade_ativo_exaurido_lote_8500"] = any("8500" in str(r.get("Lote")) for r in ativos) and any("8500" in str(r.get("Lote")) for r in exauridos)
        res["invariantes_render_ok"] = True
    except Exception as exc:
        res["invariantes_render_ok"] = False
        res["invariantes_render_erro"] = str(exc)

    res["validacao_v4w_ok"] = all([
        res["gerar_planilha_operacional_consumindo_pacote"],
        res["console_consumindo_pacote"],
        res["saida_observavel_sem_fallback_silencioso_sem_pacote"],
        res["funcoes_publicas_criticas_exigem_ou_recebem_pacote"],
        res["saida_observavel_sem_somar_valores_sacados_por_lote"],
        res["saida_observavel_sem_acesso_direto_replay"],
        res["saida_observavel_sem_varredura_dict_contexto"],
        res["saida_observavel_sem_varredura_generica_dataframe"],
        res["helpers_legados_removidos"],
        res["bootstrap_pacote_explicito"],
        res["invariantes_render_ok"],
        abs(res["lote_3120_mai_bruto_sacado_renderizado"] - 3093.76) <= 0.01,
        abs(res["lote_3120_mai_liquido_sacado_renderizado"] - 3088.95) <= 0.01,
        abs(res["lote_3120_mai_saldo_final"] - 50.52) <= 0.01,
        abs(res["lote_3120_mai_patrimonio_liquido_renderizado"] - 3139.47) <= 0.01,
        abs(res["lote_3120_mai_rendimento_liquido_renderizado"] - 16.94) <= 0.01,
        res["qtd_lotes_exauridos_por_saque_com_saque_zero"] == 0,
        res["qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado"] == 0,
        res["duplicidade_ativo_exaurido_lote_8500"] is False,
    ])
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
