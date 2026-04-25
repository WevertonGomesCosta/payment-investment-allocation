"""Inspeção canônica da recomputação sequencial central.

V203: este diagnóstico não recalcula nem lê diretamente a saída interna da
recomputação. Ele usa `nucleo.saida_canonica.PacoteSaidaCanonica`, que é a
camada observável comum a console e planilha.
"""
from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.saida_canonica import construir_saida_canonica
from scripts.diagnostico._governanca_saida import imprimir_tabela_dicts


def main() -> int:
    contexto = carregar_contexto_baseline(raiz_repositorio=RAIZ, instalar_automaticamente=False)
    saida = construir_saida_canonica(contexto, versao=VERSAO_BASELINE)

    total = len(saida.extrato_futuro)
    sem_cobertura = [item for item in saida.extrato_futuro if item.get("Cobertura integral") != "sim"]
    multifonte = [item for item in saida.extrato_futuro if "+" in str(item.get("Lote sugerido") or "")]

    print("=== DIAGNOSTICO CANONICO: RECOMPUTACAO SEQUENCIAL CENTRAL ===")
    print(f"versao_saida: {saida.versao}")
    print(f"origem: {saida.auditoria.get('origem')}")
    print(f"total_pagamentos_futuros_observaveis: {total}")
    print(f"pagamentos_sem_cobertura_integral: {len(sem_cobertura)}")
    print(f"pagamentos_multifonte: {len(multifonte)}")
    print(f"validacao_observavel_ok: {len(sem_cobertura) == 0}")

    imprimir_tabela_dicts(
        "Amostra canônica multifonte",
        multifonte,
        ["Data", "Conta", "Valor", "Lote sugerido", "Líquido", "Cobertura integral", "Estratégia"],
        limite=15,
    )

    if sem_cobertura:
        imprimir_tabela_dicts(
            "Amostra canônica sem cobertura integral",
            sem_cobertura,
            ["Data", "Conta", "Valor", "Lote sugerido", "Líquido", "Cobertura integral", "Estratégia"],
            limite=15,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
