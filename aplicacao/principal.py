"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
from typing import Iterable

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.ambiente import bootstrap_ambiente
from nucleo.calendario_financeiro import construir_calendario_financeiro, contar_dias_rendimento
from nucleo.carregador_config import carregar_config
from nucleo.carteira_canonica import carregar_carteira_canonica
from nucleo.dados_operacionais_canonicos import carregar_dados_operacionais_canonicos
from nucleo.leitor_planilha import carregar_planilha, construir_resumo_planilha


def _imprimir_titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


def _imprimir_pares(pares: Iterable[tuple[str, object]]) -> None:
    for chave, valor in pares:
        print(f"- {chave}: {valor}")


def _normalizar_lista(itens: Iterable[object] | None) -> list[str]:
    if not itens:
        return []
    return [str(item) for item in itens]


def _severidade(*, erros: Iterable[object] | None = None, avisos: Iterable[object] | None = None, condicao_ok: bool = True) -> str:
    erros_norm = _normalizar_lista(erros)
    avisos_norm = _normalizar_lista(avisos)
    if erros_norm:
        return "ERRO"
    if avisos_norm or not condicao_ok:
        return "AVISO"
    return "OK"


def _imprimir_linha_status(rotulo: str, severidade: str, detalhe: str = "") -> None:
    sufixo = f" — {detalhe}" if detalhe else ""
    print(f"[{severidade}] {rotulo}{sufixo}")


def _imprimir_itens_severidade(rotulo: str, itens: Iterable[object] | None, severidade: str) -> None:
    itens_norm = _normalizar_lista(itens)
    if not itens_norm:
        return
    print(f"- {rotulo}:")
    for item in itens_norm:
        print(f"  [{severidade}] {item}")


def main() -> None:
    pacote_config = carregar_config(raiz_repositorio=RAIZ_REPOSITORIO)
    contexto = bootstrap_ambiente(
        pacote_config.conteudo,
        grupos_extras=["financeiro"],
        instalar_automaticamente=False,
    )
    calendario_financeiro = construir_calendario_financeiro(
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
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

    exemplo_inicio = contexto.data_referencia.replace(day=1)
    dias_rendimento_mes = contar_dias_rendimento(
        exemplo_inicio - timedelta(days=1),
        contexto.data_referencia,
        calendario_financeiro,
    )

    validacao_carteira = carteira_canonica.validacao or {}
    resumo_inventario = dados_operacionais.auditoria_inventario.get("resumo", {})
    validacao_inventario = dados_operacionais.auditoria_inventario.get("validacao", {})
    resumo_gastos = dados_operacionais.auditoria_gastos.get("resumo", {})
    validacao_gastos = dados_operacionais.auditoria_gastos.get("validacao", {})

    severidade_carteira = _severidade(
        erros=validacao_carteira.get("erros"),
        avisos=validacao_carteira.get("avisos"),
        condicao_ok=bool(validacao_carteira.get("ok", True)),
    )
    severidade_inventario = _severidade(
        erros=validacao_inventario.get("erros"),
        avisos=validacao_inventario.get("avisos"),
        condicao_ok=bool(validacao_inventario.get("ok", True)),
    )
    severidade_gastos = _severidade(
        erros=validacao_gastos.get("erros"),
        avisos=validacao_gastos.get("avisos"),
        condicao_ok=bool(validacao_gastos.get("ok", True)),
    )
    severidade_abas = _severidade(condicao_ok=all(nome_aba in pacote_planilha.nomes_abas for _, nome_aba in abas_primarias))
    severidade_dependencias = _severidade(
        avisos=contexto.relatorio_dependencias.get("ausentes", []),
        condicao_ok=len(contexto.relatorio_dependencias.get("ausentes", [])) == 0,
    )

    _imprimir_titulo("BASELINE")
    _imprimir_pares([
        ("versão", "V13"),
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
    _imprimir_linha_status("Dependências essenciais da baseline", severidade_dependencias, "baseline mínima e auditoria estrutural")
    _imprimir_pares([
        ("instaladas", ", ".join(contexto.relatorio_dependencias.get("instaladas", [])) or "nenhuma"),
        ("ausentes", ", ".join(contexto.relatorio_dependencias.get("ausentes", [])) or "nenhuma"),
    ])

    _imprimir_titulo("CALENDÁRIO FINANCEIRO E TAXAS BASE")
    _imprimir_linha_status("Camada neutra de calendário e taxas base", "OK", "sem fetch do BCB e sem aplicação econômica aos lotes")
    _imprimir_pares([
        ("CDI anual do modelo", f"{calendario_financeiro.cdi_anual_modelo:.6f}"),
        ("convenção dias/ano CDI", calendario_financeiro.convencao_dias_ano_cdi),
        ("taxa diária base", f"{calendario_financeiro.taxa_dia_base:.12f}"),
        ("anos dias sem rendimento", f"{calendario_financeiro.ano_inicio_dias_sem_rendimento}-{calendario_financeiro.ano_fim_dias_sem_rendimento}"),
        ("dias sem rendimento mapeados", len(calendario_financeiro.dias_sem_rendimento_bancario)),
        ("workalendar disponível", "sim" if calendario_financeiro.workalendar_disponivel else "não"),
        ("calendário Brasil disponível", "sim" if calendario_financeiro.calendario_brasil_disponivel else "não"),
        ("dias de rendimento no mês até a data de referência", dias_rendimento_mes),
    ])

    _imprimir_titulo("ABAS ENCONTRADAS")
    for indice, nome_aba in enumerate(pacote_planilha.nomes_abas, start=1):
        print(f"- [{indice}] {nome_aba}")

    _imprimir_titulo("ABAS PRIMÁRIAS DO CONTRATO")
    _imprimir_linha_status("Abas primárias do contrato", severidade_abas, f"{len(abas_primarias)} blocos esperados")
    for chave, nome_aba in abas_primarias:
        presente = nome_aba in pacote_planilha.nomes_abas
        info = resumo_por_aba.get(nome_aba)
        linhas = info["n_linhas"] if info else "-"
        colunas = info["n_colunas"] if info else "-"
        sev = "OK" if presente else "ERRO"
        _imprimir_linha_status(f"Bloco {chave}", sev, nome_aba)
        _imprimir_pares([
            ("presente", "sim" if presente else "não"),
            ("linhas", linhas),
            ("colunas", colunas),
        ])
        print("")

    if abas_auxiliares:
        _imprimir_titulo("ABAS AUXILIARES / NÃO OPERACIONAIS")
        _imprimir_linha_status("Abas auxiliares identificadas", "OK", f"{len(abas_auxiliares)} abas fora do contrato operacional")
        for nome_aba in abas_auxiliares:
            info = resumo_por_aba.get(nome_aba)
            linhas = info["n_linhas"] if info else "-"
            colunas = info["n_colunas"] if info else "-"
            print(f"- {nome_aba}: {linhas} linhas, {colunas} colunas")

    _imprimir_titulo("RESUMO CONSOLIDADO DAS CAMADAS CANÔNICAS")
    _imprimir_linha_status("Carteira canônica", severidade_carteira, f"{len(carteira_canonica.quadro_canonico)} produtos")
    _imprimir_linha_status("Inventário canônico", severidade_inventario, f"{len(dados_operacionais.inventario_canonico)} lotes")
    _imprimir_linha_status("Gastos canônicos", severidade_gastos, f"{len(dados_operacionais.gastos_canonicos)} despesas")
    _imprimir_pares([
        ("produtos canônicos", len(carteira_canonica.quadro_canonico)),
        ("produto_key únicos", len(carteira_canonica.mapa_produtos.get("by_key", {}))),
        ("lotes aportados", resumo_inventario.get("aportados", 0)),
        ("lotes não aportados disponíveis", resumo_inventario.get("nao_aportados_disponiveis", 0)),
        ("lotes não aportados exauridos", resumo_inventario.get("nao_aportados_exauridos", 0)),
        ("recebidos futuros não disponíveis hoje", resumo_inventario.get("recebidos_futuros", 0)),
        ("despesas pagas até a data de referência", resumo_gastos.get("pagas_ate_data_referencia", 0)),
        ("despesas futuras ou pendentes", resumo_gastos.get("futuras_ou_pendentes", 0)),
        ("despesas com lote informado", resumo_gastos.get("com_lote_informado", 0)),
    ])

    _imprimir_titulo("CARTEIRA CANÔNICA")
    _imprimir_linha_status("Validação estrutural da aba Carteira", severidade_carteira)
    _imprimir_pares([
        ("aba", carteira_canonica.nome_aba),
        ("produtos canônicos", len(carteira_canonica.quadro_canonico)),
        ("produto_key únicos", len(carteira_canonica.mapa_produtos.get("by_key", {}))),
        ("nomes normalizados únicos", len(carteira_canonica.mapa_produtos.get("by_nome_norm", {}))),
        ("linhas sem produto_id explícito", carteira_canonica.auditoria.get("sem_produto_id", 0)),
        ("erros de validação", len(_normalizar_lista(validacao_carteira.get("erros")))),
        ("avisos de validação", len(_normalizar_lista(validacao_carteira.get("avisos")))),
    ])
    print("- colunas resolvidas:")
    for chave, valor in carteira_canonica.auditoria.get("colunas_resolvidas", {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    _imprimir_itens_severidade("erros de validação", validacao_carteira.get("erros"), "ERRO")
    _imprimir_itens_severidade("avisos de validação", validacao_carteira.get("avisos"), "AVISO")

    _imprimir_titulo("INVENTÁRIO CANÔNICO")
    _imprimir_linha_status("Validação estrutural do inventário", severidade_inventario)
    _imprimir_pares([
        ("aba", dados_operacionais.nome_aba_lotes),
        ("lotes canônicos", len(dados_operacionais.inventario_canonico)),
        ("aportados", resumo_inventario.get("aportados", 0)),
        ("não aportados disponíveis", resumo_inventario.get("nao_aportados_disponiveis", 0)),
        ("não aportados exauridos", resumo_inventario.get("nao_aportados_exauridos", 0)),
        ("recebidos futuros", resumo_inventario.get("recebidos_futuros", 0)),
        ("erros de validação", len(_normalizar_lista(validacao_inventario.get("erros")))),
        ("avisos de validação", len(_normalizar_lista(validacao_inventario.get("avisos")))),
    ])
    print("- colunas resolvidas:")
    for chave, valor in dados_operacionais.auditoria_inventario.get("colunas_resolvidas", {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    _imprimir_itens_severidade("erros de validação", validacao_inventario.get("erros"), "ERRO")
    _imprimir_itens_severidade("avisos de validação", validacao_inventario.get("avisos"), "AVISO")

    _imprimir_titulo("GASTOS CANÔNICOS")
    _imprimir_linha_status("Validação estrutural dos gastos", severidade_gastos)
    _imprimir_pares([
        ("aba", dados_operacionais.nome_aba_despesas),
        ("despesas canônicas", len(dados_operacionais.gastos_canonicos)),
        ("pagas até data de referência", resumo_gastos.get("pagas_ate_data_referencia", 0)),
        ("futuras ou pendentes", resumo_gastos.get("futuras_ou_pendentes", 0)),
        ("com lote informado", resumo_gastos.get("com_lote_informado", 0)),
        ("erros de validação", len(_normalizar_lista(validacao_gastos.get("erros")))),
        ("avisos de validação", len(_normalizar_lista(validacao_gastos.get("avisos")))),
    ])
    print("- colunas resolvidas:")
    for chave, valor in dados_operacionais.auditoria_gastos.get("colunas_resolvidas", {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    _imprimir_itens_severidade("erros de validação", validacao_gastos.get("erros"), "ERRO")
    _imprimir_itens_severidade("avisos de validação", validacao_gastos.get("avisos"), "AVISO")

    _imprimir_titulo("RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS")
    for _, nome_aba in abas_primarias:
        info = resumo_por_aba.get(nome_aba)
        if not info:
            _imprimir_linha_status(nome_aba, "ERRO", "aba ausente")
            continue
        _imprimir_linha_status(nome_aba, "OK", f"{info['n_linhas']} linhas, {info['n_colunas']} colunas")
        colunas = info.get("colunas", [])
        if colunas:
            print(f"  colunas (primeiras 8): {', '.join(colunas[:8])}")


if __name__ == "__main__":
    main()
