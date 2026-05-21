from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import construir_saida_canonica


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-csv", action="store_true")
    parser.parse_args()

    ctx = carregar_contexto_baseline(
        raiz_repositorio=ROOT,
        instalar_automaticamente=False,
        incluir_benchmark_agrupado_individual_shadow=False,
    )
    saida = construir_saida_canonica(ctx)
    pacotes = construir_pacotes_temporais_agregados_saida_shadow(ctx)
    pacote = construir_pacote_saida_observavel_temporal(ctx, saida, pacotes_temporais=pacotes)

    aud = pacote.auditoria_saida_observavel_temporal
    val = pacote.validacao_saida_observavel_temporal

    out = {
        "pacote_saida_observavel_temporal_criado": pacote is not None,
        "usa_pacotes_temporais_agregados": aud.get("usa_pacotes_temporais_agregados", False),
        "usa_saida_apenas_como_snapshot_observavel": aud.get("usa_saida_apenas_como_snapshot_observavel", False),
        "nao_importa_saida_observavel": aud.get("nao_importa_saida_observavel", False),
        "nao_altera_saida_canonica": aud.get("nao_altera_saida_canonica", False),
        "nao_altera_saida_observavel": aud.get("nao_altera_saida_observavel", False),
        "nao_altera_replay_efetivo": aud.get("nao_altera_replay_efetivo", False),
        "nao_altera_ledger_efetivo": aud.get("nao_altera_ledger_efetivo", False),
        "lote_3120_mai_presente_ativos": aud.get("lote_3120_mai_presente_ativos_snapshot", False),
        "lote_3120_mai_presente_exauridos": aud.get("lote_3120_mai_presente_exauridos_snapshot", False),
        "lote_3120_mai_saldo_final": aud.get("lote_3120_mai_saldo_final", 0.0),
        "sem_duplicidade_ativos_exauridos": "lotes_duplicados_ativos_exauridos" not in val.get("erros_bloqueantes", []),
        "mapas_substitutivos_criados": all([
            len(pacote.saldos_finais_replay_por_lote) > 0,
            len(pacote.pagamentos_replay_por_chave) > 0,
            len(pacote.aplicacoes_por_lote) > 0,
            len(pacote.produtos_por_lote) > 0,
            len(pacote.valores_originais_por_lote) > 0,
            len(pacote.valores_sacados_por_lote) > 0,
        ]),
        "pacote_pronto_para_migracao_v4v": bool(val.get("ok")),
        "helpers_legados_ainda_existentes": True,
        "etapa5_pode_abrir_agora": False,
        "proxima_etapa_recomendada": "V17-F0-V.4V",
        "validacao_v4u_ok": bool(val.get("ok")),
        "qtd_saldos_finais_replay_por_lote": len(pacote.saldos_finais_replay_por_lote),
        "qtd_pagamentos_replay_por_chave": len(pacote.pagamentos_replay_por_chave),
        "qtd_aplicacoes_por_lote": len(pacote.aplicacoes_por_lote),
        "qtd_produtos_por_lote": len(pacote.produtos_por_lote),
        "qtd_valores_originais_por_lote": len(pacote.valores_originais_por_lote),
        "qtd_valores_sacados_por_lote": len(pacote.valores_sacados_por_lote),
        "qtd_lotes_ativos_observaveis": len(pacote.lotes_ativos_observaveis),
        "qtd_lotes_exauridos_observaveis": len(pacote.lotes_exauridos_observaveis),
        "qtd_pagamentos_realizados_observaveis": len(pacote.pagamentos_realizados_observaveis),
    }
    for k, v in out.items():
        print(f"{k}={json.dumps(v, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
