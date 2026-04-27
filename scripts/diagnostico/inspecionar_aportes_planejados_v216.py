"""Diagnóstico funcional da integração V216 de aportes futuros planejados.

Por padrão executa um cenário sintético mínimo para validar, de forma rápida,
a cadeia funcional:
recebido_futuro -> pagamento intradiário -> reserva -> aporte planejado -> lote consumido por pagamento futuro.

Use `--real` para rodar contra a planilha real, quando a execução pesada for desejada.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta

import pandas as pd

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.builders.simulador_central_estado_v117 import construir_estado_global_recorte_curto_v117
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE, caminho_saida_diagnostico
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1


def _salvar_csv(nome: str, linhas: list[dict]) -> None:
    destino = caminho_saida_diagnostico(RAIZ, nome)
    destino.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(linhas).to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"CSV: {destino.relative_to(RAIZ).as_posix()}")


def _estado_sintetico_v216() -> dict:
    return {
        "data_referencia": date(2026, 4, 27),
        "data_evento_corrente": date(2026, 4, 27),
        "data_fim_recorte": date(2026, 6, 1),
        "saldo_disponivel_geral": 0.0,
        "recebidos_nao_aportados_disponiveis": [],
        "recebidos_nao_aportados_futuros": [
            {
                "id": "recebido_sintetico_v216",
                "valor_disponivel": 5000.0,
                "valor_recebido_original_v216": 5000.0,
                "valor_pago_com_recebido_v216": 0.0,
                "valor_aportado_planejado_v216": 0.0,
                "saldo_caixa_remanescente_v216": 5000.0,
                "proxy_terminal_atual": 0.0,
                "data_recebimento": date(2026, 4, 28),
            }
        ],
        "lotes_aportados": [],
        "pagamentos_futuros": [
            {
                "pagamento_id": "pagamento_mesmo_dia_v216",
                "despesa_id": "pagamento_mesmo_dia_v216",
                "data": date(2026, 4, 28),
                "descricao": "pagamento intradiario v216",
                "valor": 1000.0,
                "classe_pagamento": "FLEXIVEL",
                "subclasse_pagamento": "FLEXIVEL",
                "prioridade_classe": 2,
                "prioridade_intraclasse": 20,
            },
            {
                "pagamento_id": "pagamento_reserva_7d_v216",
                "despesa_id": "pagamento_reserva_7d_v216",
                "data": date(2026, 5, 2),
                "descricao": "pagamento reserva v216",
                "valor": 300.0,
                "classe_pagamento": "FLEXIVEL",
                "subclasse_pagamento": "FLEXIVEL",
                "prioridade_classe": 2,
                "prioridade_intraclasse": 20,
            },
            {
                "pagamento_id": "pagamento_consumo_lote_planejado_v216",
                "despesa_id": "pagamento_consumo_lote_planejado_v216",
                "data": date(2026, 5, 15),
                "descricao": "pagamento futuro com lote planejado v216",
                "valor": 1000.0,
                "classe_pagamento": "FLEXIVEL",
                "subclasse_pagamento": "FLEXIVEL",
                "prioridade_classe": 2,
                "prioridade_intraclasse": 20,
            },
        ],
        "produto_destino_padrao": {
            "produto_key": "produto_sintetico_liquidez_diaria_v216",
            "nome": "Produto Sintetico Liquidez Diaria V216",
            "score_final": 0.99,
            "proxy_terminal_destino": 0.99,
            "retorno_anual_proxy": 0.10,
            "liquidez_dias": 0,
            "carencia_dias": 0,
            "aplicacao_minima": 1.0,
            "aplicacao_maxima": 0.0,
            "somente_combo": False,
        },
        "produtos_destino_elegiveis": [
            {
                "produto_key": "produto_sintetico_liquidez_diaria_v216",
                "nome": "Produto Sintetico Liquidez Diaria V216",
                "score_final": 0.99,
                "proxy_terminal_destino": 0.99,
                "retorno_anual_proxy": 0.10,
                "liquidez_dias": 0,
                "carencia_dias": 0,
                "aplicacao_minima": 1.0,
                "aplicacao_maxima": 0.0,
                "somente_combo": False,
            }
        ],
    }


def _rodar_sintetico() -> dict:
    return simular_cenario_eventos_v1(
        _estado_sintetico_v216(),
        eventos_candidatos=[],
        config={
            "aportes_futuros_v216": {
                "habilitado": True,
                "reserva_dias": 7,
                "liquidez_max_dias": 7,
                "carencia_max_dias": 7,
                "exigir_ganho_positivo": True,
            },
            "desabilitar_modelos_script1_fase1": True,
        },
        horizonte={"diagnostico": "sintetico_aportes_planejados_v216"},
    )


def _rodar_real() -> dict:
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
        limite_pagamentos=30,
    )
    return simular_cenario_eventos_v1(
        estado,
        eventos_candidatos=[],
        config=contexto.pacote_config.conteudo,
        horizonte={"diagnostico": "real_aportes_planejados_v216", "data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat()},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Executa contra a planilha real; pode ser mais lento.")
    args = parser.parse_args()

    resultado = _rodar_real() if args.real else _rodar_sintetico()

    auditoria = list(resultado.get("auditoria_aportes_planejados_v216") or [])
    historico = [
        item for item in list(resultado.get("historico_eventos") or [])
        if str(item.get("tipo_evento") or "") == "aporte_planejado_v216"
    ]
    lotes_planejados = [
        item for item in list((resultado.get("estado_final_estimado") or {}).get("lotes_aportados") or [])
        if bool(item.get("origem_aporte_planejado_v216"))
    ]
    pagamentos_com_lote_planejado = [
        item for item in list(resultado.get("resultados_pagamento") or [])
        if bool((item.get("metadados_escolhidos") or {}).get("origem_aporte_planejado_v216"))
        or any(bool((comp or {}).get("origem_aporte_planejado_v216")) for comp in list(item.get("componentes_escolhidos") or []))
        or any("ap_planejado_v216" in str((comp or {}).get("fonte_id") or "") for comp in list(item.get("componentes_escolhidos") or []))
    ]

    sufixo = "real" if args.real else "sintetico"
    _salvar_csv(f"auditoria_aportes_planejados_{VERSAO_BASELINE.lower()}_{sufixo}.csv", auditoria)
    _salvar_csv(f"historico_aportes_planejados_{VERSAO_BASELINE.lower()}_{sufixo}.csv", historico)
    _salvar_csv(f"lotes_planejados_promovidos_{VERSAO_BASELINE.lower()}_{sufixo}.csv", lotes_planejados)
    _salvar_csv(f"pagamentos_consumindo_lotes_planejados_{VERSAO_BASELINE.lower()}_{sufixo}.csv", pagamentos_com_lote_planejado)

    print("=== DIAGNOSTICO FUNCIONAL: APORTES PLANEJADOS V216 ===")
    print(f"versao: {VERSAO_BASELINE}")
    print(f"modo: {sufixo}")
    print(f"eventos_auditoria: {len(auditoria)}")
    print(f"lotes_planejados_promovidos: {len(lotes_planejados)}")
    print(f"pagamentos_consumindo_lotes_planejados: {len(pagamentos_com_lote_planejado)}")
    print(f"pagamentos_processados: {len(resultado.get('resultados_pagamento') or [])}")
    print(f"patrimonio_terminal_proxy: {resultado.get('patrimonio_liquido_terminal_proxy')}")
    print(f"status_simulador: {resultado.get('status')}")

    if resultado.get("status") != "integracao_integral_multidestino_v216":
        raise SystemExit("simulador_nao_esta_na_versao_v216")
    if not auditoria:
        raise SystemExit("auditoria_aportes_planejados_v216_vazia")
    if not lotes_planejados:
        raise SystemExit("nenhum_lote_planejado_promovido_v216")
    if not pagamentos_com_lote_planejado:
        raise SystemExit("nenhum_pagamento_consumiu_lote_planejado_v216")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
