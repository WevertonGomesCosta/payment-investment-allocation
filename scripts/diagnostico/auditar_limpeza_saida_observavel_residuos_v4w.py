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

    # invariantes de renderizacao final (sem fallback silencioso)
    try:
        from nucleo.contexto_baseline import carregar_contexto_baseline
        from nucleo.saida_canonica import construir_saida_canonica
        from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
        from nucleo.saida_observavel import construir_linhas_lotes_consolidados
        ctx = carregar_contexto_baseline(raiz_repositorio=ROOT, instalar_automaticamente=False, incluir_benchmark_agrupado_individual_shadow=False)
        saida_c = construir_saida_canonica(ctx)
        ativos_boot = construir_linhas_lotes_consolidados(ctx, saida_c, tipo="ativos", modo_bootstrap_pacote=True)
        ex_boot = construir_linhas_lotes_consolidados(ctx, saida_c, tipo="exauridos", modo_bootstrap_pacote=True)
        pacote = construir_pacote_saida_observavel_temporal(ctx, saida_c, lotes_ativos_observaveis=ativos_boot, lotes_exauridos_observaveis=ex_boot, pagamentos_realizados_observaveis=list(getattr(saida_c, "extrato_passado", []) or []))
        ativos_final = construir_linhas_lotes_consolidados(ctx, saida_c, tipo="ativos", pacote_saida_observavel_temporal=pacote)
        ex_final = construir_linhas_lotes_consolidados(ctx, saida_c, tipo="exauridos", pacote_saida_observavel_temporal=pacote)
        lote3120 = next((r for r in ativos_final if "3120" in str(r.get("Lote"))), {})
        r8500a = any("8500" in str(r.get("Lote")) for r in ativos_final)
        r8500e = any("8500" in str(r.get("Lote")) for r in ex_final)
        qtd_ex_saque_zero = sum(1 for r in ex_final if str(r.get("Status ciclo"))=="exaurido_por_saque" and float(r.get("Líq. sac.") or 0)==0)
        qtd_at_neg = sum(1 for r in ativos_final if float(r.get("Líq. atual") or 0)>0 and float(r.get("Orig.") or 0)>0 and float(r.get("Líq. sac.") or 0)==0 and float(r.get("Rend. líq.") or 0)<0)
        res.update({
            "lote_3120_mai_bruto_sacado": round(float(lote3120.get("Bruto sac.") or 0),2),
            "lote_3120_mai_liquido_sacado": round(float(lote3120.get("Líq. sac.") or 0),2),
            "lote_3120_mai_saldo_final": round(float(lote3120.get("Líq. atual") or 0),2),
            "qtd_lotes_exauridos_por_saque_com_saque_zero": qtd_ex_saque_zero,
            "qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado": qtd_at_neg,
            "duplicidade_ativo_exaurido_lote_8500": r8500a and r8500e,
        })
    except Exception:
        res.update({
            "invariantes_render_erro": "erro_interno",
            "lote_3120_mai_bruto_sacado": 0.0,
            "lote_3120_mai_liquido_sacado": 0.0,
            "lote_3120_mai_saldo_final": 0.0,
            "qtd_lotes_exauridos_por_saque_com_saque_zero": 999,
            "qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado": 999,
            "duplicidade_ativo_exaurido_lote_8500": True,
        })

    res["validacao_v4w_ok"] = all([
        gerar_planilha_operacional_consumindo_pacote,
        console_consumindo_pacote,
        saida_observavel_sem_fallback_silencioso_sem_pacote,
        funcoes_publicas_criticas_exigem_ou_recebem_pacote,
        sem_somar, sem_replay, sem_dict, sem_df_generic, helpers_legados_removidos, bootstrap_pacote_explicito,
        abs(res["lote_3120_mai_bruto_sacado"]-3093.76)<=0.01,
        abs(res["lote_3120_mai_liquido_sacado"]-3088.95)<=0.01,
        abs(res["lote_3120_mai_saldo_final"]-50.52)<=0.01,
        res["qtd_lotes_exauridos_por_saque_com_saque_zero"]==0,
        res["qtd_lotes_ativos_com_rendimento_negativo_por_saque_ignorado"]==0,
        res["duplicidade_ativo_exaurido_lote_8500"] is False,
    ])
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
