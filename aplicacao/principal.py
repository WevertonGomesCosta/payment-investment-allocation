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
from nucleo.carteira_canonica import carregar_carteira_canonica
from nucleo.dados_operacionais_canonicos import carregar_dados_operacionais_canonicos


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

    carteira_canonica = carregar_carteira_canonica(pacote_planilha, pacote_config.conteudo)
    dados_operacionais = carregar_dados_operacionais_canonicos(
        pacote_planilha,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
        carteira_canonica=carteira_canonica,
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
        ("versão", "V11"),
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

    _imprimir_titulo("CARTEIRA CANÔNICA")
    _imprimir_pares([
        ("aba", carteira_canonica.nome_aba),
        ("produtos canônicos", len(carteira_canonica.quadro_canonico)),
        ("produto_key únicos", len(carteira_canonica.mapa_produtos.get("by_key", {}))),
        ("nomes normalizados únicos", len(carteira_canonica.mapa_produtos.get("by_nome_norm", {}))),
        ("linhas sem produto_id explícito", carteira_canonica.auditoria.get("sem_produto_id", 0)),
        ("validação estrutural", "ok" if carteira_canonica.validacao.get("ok") else "com pendências"),
    ])

    colunas_resolvidas = carteira_canonica.auditoria.get("colunas_resolvidas", {})
    print("- colunas resolvidas:")
    for chave, valor in colunas_resolvidas.items():
        if valor:
            print(f"  - {chave}: {valor}")

    erros = carteira_canonica.validacao.get("erros", [])
    avisos = carteira_canonica.validacao.get("avisos", [])
    if erros:
        print("- erros de validação:")
        for erro in erros:
            print(f"  - {erro}")
    if avisos:
        print("- avisos de validação:")
        for aviso in avisos:
            print(f"  - {aviso}")


    _imprimir_titulo("INVENTÁRIO CANÔNICO")
    resumo_inventario = dados_operacionais.auditoria_inventario.get("resumo", {})
    validacao_inventario = dados_operacionais.auditoria_inventario.get("validacao", {})
    _imprimir_pares([
        ("aba", dados_operacionais.nome_aba_lotes),
        ("lotes canônicos", len(dados_operacionais.inventario_canonico)),
        ("aportados", resumo_inventario.get("aportados", 0)),
        ("não aportados disponíveis", resumo_inventario.get("nao_aportados_disponiveis", 0)),
        ("não aportados exauridos", resumo_inventario.get("nao_aportados_exauridos", 0)),
        ("recebidos futuros", resumo_inventario.get("recebidos_futuros", 0)),
        ("validação estrutural", "ok" if validacao_inventario.get("ok") else "com pendências"),
    ])
    print("- colunas resolvidas:")
    for chave, valor in dados_operacionais.auditoria_inventario.get("colunas_resolvidas", {}).items():
        if valor:
            print(f"  - {chave}: {valor}")
    if validacao_inventario.get("erros"):
        print("- erros de validação:")
        for erro in validacao_inventario.get("erros", []):
            print(f"  - {erro}")
    if validacao_inventario.get("avisos"):
        print("- avisos de validação:")
        for aviso in validacao_inventario.get("avisos", []):
            print(f"  - {aviso}")

    _imprimir_titulo("GASTOS CANÔNICOS")
    resumo_gastos = dados_operacionais.auditoria_gastos.get("resumo", {})
    validacao_gastos = dados_operacionais.auditoria_gastos.get("validacao", {})
    _imprimir_pares([
        ("aba", dados_operacionais.nome_aba_despesas),
        ("despesas canônicas", len(dados_operacionais.gastos_canonicos)),
        ("pagas até data de referência", resumo_gastos.get("pagas_ate_data_referencia", 0)),
        ("futuras ou pendentes", resumo_gastos.get("futuras_ou_pendentes", 0)),
        ("com lote informado", resumo_gastos.get("com_lote_informado", 0)),
        ("validação estrutural", "ok" if validacao_gastos.get("ok") else "com pendências"),
    ])
    print("- colunas resolvidas:")
    for chave, valor in dados_operacionais.auditoria_gastos.get("colunas_resolvidas", {}).items():
        if valor:
            print(f"  - {chave}: {valor}")
    if validacao_gastos.get("erros"):
        print("- erros de validação:")
        for erro in validacao_gastos.get("erros", []):
            print(f"  - {erro}")
    if validacao_gastos.get("avisos"):
        print("- avisos de validação:")
        for aviso in validacao_gastos.get("avisos", []):
            print(f"  - {aviso}")

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
