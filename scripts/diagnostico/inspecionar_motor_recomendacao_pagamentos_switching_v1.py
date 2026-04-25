"""Inspeção canônica do motor de recomendações de pagamentos + switching.

V203: este diagnóstico não lê mais diretamente o dataframe interno do motor.
Ele materializa `nucleo.saida_canonica.PacoteSaidaCanonica` e imprime a visão
observável oficial usada por console e planilha.
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

    print("=== DIAGNOSTICO CANONICO: RECOMENDACOES FUTURAS + SWITCHING ===")
    print(f"versao_saida: {saida.versao}")
    print(f"origem: {saida.auditoria.get('origem')}")
    print(f"qtd_extrato_futuro: {saida.auditoria.get('qtd_extrato_futuro')}")
    print(f"qtd_futuro_sem_cobertura_integral: {saida.auditoria.get('qtd_futuro_sem_cobertura_integral')}")
    print(f"qtd_futuro_multifonte: {saida.auditoria.get('qtd_futuro_multifonte')}")
    print(f"qtd_switchings: {saida.auditoria.get('qtd_switchings')}")

    linhas_switching = [
        item for item in saida.extrato_futuro
        if str(item.get("Necessita switching") or "").strip().lower() == "sim"
    ]
    imprimir_tabela_dicts(
        "Amostra canônica de contas futuras com switching",
        linhas_switching,
        ["Data", "Conta", "Valor", "Lote sugerido", "Líquido", "Cobertura integral", "Estratégia"],
        limite=15,
    )

    imprimir_tabela_dicts(
        "Amostra canônica geral do extrato futuro",
        saida.extrato_futuro,
        ["Data", "Conta", "Valor", "Lote sugerido", "Líquido", "Cobertura integral", "Necessita switching"],
        limite=15,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
