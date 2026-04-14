"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.ambiente import bootstrap_ambiente
from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha, construir_resumo_planilha


def _imprimir_titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


def _imprimir_pares(pares: Iterable[tuple[str, object]]) -> None:
    for chave, valor in pares:
        print(f"- {chave}: {valor}")


def main() -> None:
    pacote_config = carregar_config(raiz_repositorio=RAIZ_REPOSITORIO)
    contexto = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=["financeiro"],
        instalar_automaticamente=False,
    )
    pacote_planilha = carregar_planilha(
        pacote_config.conteudo,
        raiz_repositorio=pacote_config.raiz_repositorio,
    )

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item["nome_aba"]: item for item in resumo_planilha}
    abas_config = pacote_config.conteudo.get("abas", {}) if isinstance(pacote_config.conteudo.get("abas"), dict) else {}
    abas_primarias = [
        ("carteira", abas_config.get("carteira", "Carteira")),
        ("lotes", abas_config.get("lotes", "Inventário de Lotes")),
        ("despesas", abas_config.get("despesas", "Todos os Gastos")),
    ]
    abas_auxiliares = [nome for nome in pacote_planilha.nomes_abas if nome not in {aba for _, aba in abas_primarias}]

    _imprimir_titulo("BASELINE")
    _imprimir_pares([
        ("versão", "V8"),
        ("raiz do repositório", pacote_config.raiz_repositorio),
        ("config carregado", pacote_config.caminho),
        ("planilha carregada", pacote_planilha.caminho),
    ])

    _imprimir_titulo("AMBIENTE")
    _imprimir_pares([
        ("timezone", contexto.timezone_nome),
        ("data de referência", contexto.data_referencia.isoformat()),
        ("colab", "sim" if contexto.em_colab else "não"),
        ("warnings de rede configurados", "sim" if contexto.warnings_configurados else "não"),
    ])

    _imprimir_titulo("DEPENDÊNCIAS")
    _imprimir_pares([
        ("instaladas", ", ".join(contexto.relatorio_dependencias.get("instaladas", [])) or "nenhuma"),
        ("ausentes", ", ".join(contexto.relatorio_dependencias.get("ausentes", [])) or "nenhuma"),
    ])

    _imprimir_titulo("ABAS ENCONTRADAS")
    for indice, nome_aba in enumerate(pacote_planilha.nomes_abas, start=1):
        print(f"- [{indice}] {nome_aba}")

    _imprimir_titulo("ABAS PRIMÁRIAS DO CONTRATO")
    for chave, nome_aba in abas_primarias:
        presente = "sim" if nome_aba in pacote_planilha.nomes_abas else "não"
        info = resumo_por_aba.get(nome_aba)
        linhas = info["n_linhas"] if info else "-"
        colunas = info["n_colunas"] if info else "-"
        _imprimir_pares([
            ("bloco", chave),
            ("aba", nome_aba),
            ("presente", presente),
            ("linhas", linhas),
            ("colunas", colunas),
        ])
        print("")

    if abas_auxiliares:
        _imprimir_titulo("ABAS AUXILIARES / NÃO OPERACIONAIS")
        for nome_aba in abas_auxiliares:
            info = resumo_por_aba.get(nome_aba)
            linhas = info["n_linhas"] if info else "-"
            colunas = info["n_colunas"] if info else "-"
            print(f"- {nome_aba}: {linhas} linhas, {colunas} colunas")

    _imprimir_titulo("RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS")
    for _, nome_aba in abas_primarias:
        info = resumo_por_aba.get(nome_aba)
        if not info:
            print(f"- {nome_aba}: aba ausente")
            continue
        print(f"- {nome_aba}: {info['n_linhas']} linhas, {info['n_colunas']} colunas")
        colunas = info.get("colunas", [])
        if colunas:
            print(f"  colunas (primeiras 8): {', '.join(colunas[:8])}")


if __name__ == "__main__":
    main()
