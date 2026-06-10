from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.principal import render_console
from nucleo.contexto_operacional_canonico import carregar_contexto_operacional_canonico
from nucleo.gerar_planilha_operacional import main as gerar_planilha_operacional
from nucleo.estado_temporal_inicial import construir_estado_temporal_inicial
from nucleo.motor_temporal_conjunto import construir_resultado_motor_temporal_conjunto
from nucleo.ledger_temporal_canonico import construir_ledger_temporal_canonico
from nucleo.gates_validacao_nucleo import validar_gates_nucleo
from nucleo.saida_canonica_oficial import construir_saida_canonica_oficial
from nucleo.saida_observavel_oficial import construir_pacote_saida_observavel_oficial
from nucleo.paridade_renderizacao_oficial import validar_paridade_renderizacao_oficial
from nucleo.limpeza_depreciacao_controlada import construir_resultado_limpeza_depreciacao_controlada
from nucleo.inventario_legado_pipeline import construir_inventario_legado_pipeline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b
from nucleo.integracao_matriz_elegibilidade_pagamentos_s7c import aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c
from nucleo.pacote_saida_observavel_temporal import construir_pacote_saida_observavel_temporal
from nucleo.saida_observavel import construir_blocos_situacao_atual, construir_linhas_lotes_consolidados


def _valor(objeto, campo, padrao=None):
    if isinstance(objeto, dict):
        return objeto.get(campo, padrao)
    return getattr(objeto, campo, padrao)


def _formatar_item_gate(item, indice):
    gate_id = _valor(item, 'gate_id', 'gate_indefinido')
    codigo = _valor(item, 'codigo', 'codigo_indefinido')
    mensagem = _valor(item, 'mensagem', '')
    data_referencia = _valor(item, 'data_referencia')
    entidade_tipo = _valor(item, 'entidade_tipo')
    entidade_id = _valor(item, 'entidade_id')

    partes = [f"{indice}. gate={gate_id}", f"codigo={codigo}"]

    if data_referencia is not None:
        partes.append(f"data={data_referencia}")
    if entidade_tipo is not None:
        partes.append(f"entidade={entidade_tipo}")
    if entidade_id is not None:
        partes.append(f"id={entidade_id}")
    if mensagem:
        partes.append(f"mensagem={mensagem}")

    return " | ".join(partes)


def _render_resumo_gates_bloqueados(resultado_gates_validacao_nucleo, limite_itens=8):
    resumo = _valor(resultado_gates_validacao_nucleo, 'resumo')
    bloqueios = list(_valor(resultado_gates_validacao_nucleo, 'bloqueios', []) or [])
    avisos = list(_valor(resultado_gates_validacao_nucleo, 'avisos', []) or [])

    print("\nResumo dos gates de validação de núcleo:")
    print(f"- gates executados: {_valor(resumo, 'qtd_gates_executados', 'NA')}/{_valor(resumo, 'qtd_gates', 'NA')}")
    print(f"- gates aprovados: {_valor(resumo, 'qtd_gates_aprovados', 'NA')}")
    print(f"- gates reprovados: {_valor(resumo, 'qtd_gates_reprovados', 'NA')}")
    print(f"- bloqueios: {_valor(resumo, 'qtd_bloqueios', len(bloqueios))}")
    print(f"- avisos: {_valor(resumo, 'qtd_avisos', len(avisos))}")
    print(f"- pronto_para_etapa8: {_valor(resumo, 'pronto_para_etapa8', resultado_gates_validacao_nucleo.pronto_para_etapa8)}")

    if bloqueios:
        print("\nPrincipais bloqueios:")
        for indice, bloqueio in enumerate(bloqueios[:limite_itens], start=1):
            print("- " + _formatar_item_gate(bloqueio, indice))
        if len(bloqueios) > limite_itens:
            print(f"- ... {len(bloqueios) - limite_itens} bloqueio(s) adicional(is) omitido(s).")

    if avisos:
        print("\nPrincipais avisos:")
        for indice, aviso in enumerate(avisos[:limite_itens], start=1):
            print("- " + _formatar_item_gate(aviso, indice))
        if len(avisos) > limite_itens:
            print(f"- ... {len(avisos) - limite_itens} aviso(s) adicional(is) omitido(s).")

    print("\nPróxima ação objetiva: corrigir os bloqueios acima antes de esperar console/XLSX oficiais.")


def _render_resultado_paridade_renderizacao(resultado_paridade) -> None:
    if resultado_paridade is None:
        return

    resumo = getattr(resultado_paridade, 'resumo', None)
    auditoria_xlsx = getattr(resultado_paridade, 'auditoria_xlsx', None)
    auditoria_console = getattr(resultado_paridade, 'auditoria_console', None)
    divergencias = list(getattr(resultado_paridade, 'divergencias', []) or [])

    print("\n=== PARIDADE DA RENDERIZAÇÃO OFICIAL — ETAPA 10 ===")
    print(f"- artefato: {getattr(resultado_paridade, 'artefato', None)}")
    print(f"- entrada formal: {getattr(resultado_paridade, 'entrada_formal', None)}")
    print(f"- status: {getattr(resultado_paridade, 'status', None)}")
    print(f"- ok: {getattr(resultado_paridade, 'ok', None)}")
    print(f"- xlsx auditado: {getattr(auditoria_xlsx, 'auditado', None)}")
    print(f"- xlsx status: {getattr(auditoria_xlsx, 'status', None)}")
    print(f"- console auditado: {getattr(auditoria_console, 'auditado', None)}")
    print(f"- console status: {getattr(auditoria_console, 'status', None)}")
    print(f"- divergências: {getattr(resumo, 'qtd_divergencias', len(divergencias))}")
    print(f"- divergências materiais: {getattr(resumo, 'qtd_divergencias_materiais', None)}")
    print(f"- ressalvas: {getattr(resumo, 'qtd_ressalvas', None)}")

    if divergencias:
        print("- primeiras divergências/ressalvas:")
        for divergencia in divergencias[:5]:
            categoria = getattr(divergencia, 'categoria', None)
            alvo = getattr(divergencia, 'alvo', None)
            material = getattr(divergencia, 'material', None)
            mensagem = getattr(divergencia, 'mensagem', None)
            print(f"  - categoria={categoria} | alvo={alvo} | material={material} | mensagem={mensagem}")
        if len(divergencias) > 5:
            print(f"  - ... {len(divergencias) - 5} divergência(s)/ressalva(s) adicional(is) omitida(s).")


def _itens_limpeza_por_classificacao(resultado_limpeza, *classificacoes: str):
    return [
        item
        for item in list(getattr(resultado_limpeza, 'artefatos_avaliados', []) or [])
        if getattr(item, 'classificacao', None) in classificacoes
    ]


def _render_itens_limpeza(titulo: str, itens: list, limite: int = 6) -> None:
    print(f"- {titulo}: {len(itens)}")
    for item in itens[:limite]:
        referencias = getattr(item, 'referencias', {}) or {}
        arquivo = referencias.get('arquivo') or 'arquivo_nao_informado'
        simbolo = referencias.get('simbolo_funcao_classe') or referencias.get('simbolo') or 'simbolo_nao_informado'
        decisao = referencias.get('decisao_recomendada') or getattr(item, 'motivo', '')
        print(f"  - {getattr(item, 'identificador', None)} | {arquivo} | {simbolo} | {decisao}")
    if len(itens) > limite:
        print(f"  - ... {len(itens) - limite} item(ns) adicional(is) omitido(s).")


def _render_resultado_limpeza_depreciacao(resultado_limpeza) -> None:
    if resultado_limpeza is None:
        return

    resumo = getattr(resultado_limpeza, 'resumo', None)
    auditoria = getattr(resultado_limpeza, 'auditoria', None)
    oficiais = _itens_limpeza_por_classificacao(resultado_limpeza, 'rota_oficial_preservada')
    candidatos = _itens_limpeza_por_classificacao(resultado_limpeza, 'legado_candidato_depreciacao')
    bloqueados = list(getattr(resultado_limpeza, 'rotas_legadas_bloqueadas_remocao', []) or [])
    historicos_diagnosticos = _itens_limpeza_por_classificacao(
        resultado_limpeza,
        'historico_preservado',
        'diagnostico_preservado_fora_pipeline',
    )
    fallbacks = _itens_limpeza_por_classificacao(resultado_limpeza, 'fallback_temporario_bloqueado_para_remocao')

    print("\n=== LIMPEZA E DEPRECIAÇÃO CONTROLADA — ETAPA 11 ===")
    print(f"- artefato: {getattr(resultado_limpeza, 'artefato', None)}")
    print(f"- entrada formal: {getattr(resultado_limpeza, 'entrada_formal', None)}")
    print(f"- origem formal: {getattr(resultado_limpeza, 'origem_formal', None)}")
    print(f"- status: {getattr(resultado_limpeza, 'status', None)}")
    print(f"- ok: {getattr(resultado_limpeza, 'ok', None)}")
    print(f"- inventario_auxiliar_fornecido: {getattr(auditoria, 'inventario_auxiliar_fornecido', None)}")
    print(f"- artefatos avaliados: {getattr(resumo, 'qtd_artefatos_avaliados', None)}")
    print(f"- rotas oficiais preservadas: {getattr(resumo, 'qtd_rotas_oficiais_preservadas', len(oficiais))}")
    print(f"- legados candidatos à depreciação: {getattr(resumo, 'qtd_rotas_legadas_candidatas_depreciacao', None)}")
    print(f"- legados bloqueados para remoção: {getattr(resumo, 'qtd_rotas_legadas_bloqueadas', None)}")
    print(f"- históricos/diagnósticos preservados: {getattr(resumo, 'qtd_historicos_diagnosticos_preservados', len(historicos_diagnosticos))}")
    print(f"- fallbacks temporários bloqueados para remoção: {getattr(resumo, 'qtd_fallbacks_temporarios_bloqueados', len(fallbacks))}")
    print(f"- remoção automática autorizada: {getattr(resumo, 'remocao_automatica_autorizada', None)}")
    print(
        "- classificação limitada por ausência de inventário: "
        f"{getattr(auditoria, 'classificacao_limitada_por_ausencia_inventario', None)}"
    )

    print("- classificação explícita do inventário:")
    _render_itens_limpeza('rotas oficiais preservadas', oficiais)
    _render_itens_limpeza('legados candidatos à depreciação', candidatos)
    _render_itens_limpeza('legados bloqueados por dependência ativa', bloqueados)
    _render_itens_limpeza('históricos/diagnósticos preservados', historicos_diagnosticos)
    _render_itens_limpeza('fallbacks temporários bloqueados para remoção nesta etapa', fallbacks)

    bloqueios = list(getattr(resultado_limpeza, 'bloqueios_limpeza', []) or [])
    if bloqueios:
        print("- bloqueios/ressalvas de limpeza:")
        for bloqueio in bloqueios[:5]:
            print(f"  - {bloqueio}")
        if len(bloqueios) > 5:
            print(f"  - ... {len(bloqueios) - 5} bloqueio(s)/ressalva(s) adicional(is) omitido(s).")


def carregar_contexto_e_saida():
    """Carrega as Etapas 1-8 e só prepara saídas posteriores quando os gates aprovam."""
    contexto_operacional_canonico = carregar_contexto_operacional_canonico(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
    )
    estado_temporal_inicial = construir_estado_temporal_inicial(contexto_operacional_canonico)
    resultado_motor_temporal_conjunto = construir_resultado_motor_temporal_conjunto(estado_temporal_inicial)
    ledger_temporal_canonico = construir_ledger_temporal_canonico(resultado_motor_temporal_conjunto)
    resultado_gates_validacao_nucleo = validar_gates_nucleo(ledger_temporal_canonico)

    if not resultado_gates_validacao_nucleo.pronto_para_etapa8:
        return (
            contexto_operacional_canonico,
            estado_temporal_inicial,
            resultado_motor_temporal_conjunto,
            ledger_temporal_canonico,
            resultado_gates_validacao_nucleo,
            None,
            None,
            None,
        )

    saida_canonica = construir_saida_canonica_com_switching_v17_c7(contexto_operacional_canonico, versao=VERSAO_BASELINE)
    matriz = construir_matriz_elegibilidade_fontes_s7b(
        contexto_operacional_canonico,
        data_referencia=saida_canonica.data_referencia,
        saida_canonica_preconstruida=saida_canonica,
    )
    saida_canonica, _ = aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz)

    lotes_ativos_observaveis = construir_linhas_lotes_consolidados(
        contexto_operacional_canonico,
        saida_canonica,
        tipo='ativos',
        modo_bootstrap_pacote=True,
    )
    pacote_temporal_semente = construir_pacote_saida_observavel_temporal(
        contexto_operacional_canonico,
        saida_canonica,
        lotes_ativos_observaveis=lotes_ativos_observaveis,
    )
    lotes_exauridos_observaveis = construir_linhas_lotes_consolidados(
        contexto_operacional_canonico,
        saida_canonica,
        tipo='exauridos',
        pacote_saida_observavel_temporal=pacote_temporal_semente,
    )
    pacote_temporal_situacao_atual = construir_pacote_saida_observavel_temporal(
        contexto_operacional_canonico,
        saida_canonica,
        lotes_ativos_observaveis=lotes_ativos_observaveis,
        lotes_exauridos_observaveis=lotes_exauridos_observaveis,
        pagamentos_realizados_observaveis=list(getattr(saida_canonica, 'extrato_passado', []) or []),
    )
    blocos_situacao_atual = construir_blocos_situacao_atual(
        contexto_operacional_canonico,
        saida_canonica,
        pacote_saida_observavel_temporal=pacote_temporal_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
    )
    situacao_atual_origem = SimpleNamespace(
        fechamento_atual=list(getattr(saida_canonica, 'fechamento_atual', []) or []),
        resumo_recebidos=list(getattr(saida_canonica, 'resumo_recebidos', []) or []),
        recebidos_atuais=list(getattr(saida_canonica, 'recebidos_atuais', []) or []),
        situacao_atual_blocos=blocos_situacao_atual,
    )

    saida_canonica_oficial = construir_saida_canonica_oficial(
        ledger=ledger_temporal_canonico,
        gates=resultado_gates_validacao_nucleo,
        ranking_carteira=getattr(contexto_operacional_canonico, 'ranking_carteira', None),
        situacao_atual_origem=situacao_atual_origem,
    )
    pacote_saida_observavel_oficial = construir_pacote_saida_observavel_oficial(saida_canonica_oficial)
    return (
        contexto_operacional_canonico,
        estado_temporal_inicial,
        resultado_motor_temporal_conjunto,
        ledger_temporal_canonico,
        resultado_gates_validacao_nucleo,
        saida_canonica,
        saida_canonica_oficial,
        pacote_saida_observavel_oficial,
    )


def main():
    (
        contexto_operacional_canonico,
        estado_temporal_inicial,
        resultado_motor_temporal_conjunto,
        ledger_temporal_canonico,
        resultado_gates_validacao_nucleo,
        saida_canonica,
        saida_canonica_oficial,
        pacote_saida_observavel_oficial,
    ) = carregar_contexto_e_saida()

    _ = resultado_motor_temporal_conjunto
    _ = ledger_temporal_canonico
    _ = saida_canonica_oficial

    if not resultado_gates_validacao_nucleo.pronto_para_etapa8:
        print(
            "Execução bloqueada pelos gates de validação de núcleo: "
            "ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False. "
            "Console e XLSX oficiais não foram gerados."
        )
        _render_resumo_gates_bloqueados(resultado_gates_validacao_nucleo)
        return None

    console_auditavel = render_console(
        contexto_operacional_canonico,
        saida_canonica,
        estado_temporal_inicial=estado_temporal_inicial,
        pacote_saida_observavel_oficial=pacote_saida_observavel_oficial,
    )

    caminho_saida = gerar_planilha_operacional(
        contexto=contexto_operacional_canonico,
        saida=saida_canonica,
        estado_temporal_inicial=estado_temporal_inicial,
        pacote_saida_observavel_oficial=pacote_saida_observavel_oficial,
    )

    print(f"Saída operacional gerada em: {caminho_saida}")

    resultado_paridade_renderizacao = validar_paridade_renderizacao_oficial(
        pacote_saida_observavel=pacote_saida_observavel_oficial,
        caminho_xlsx=caminho_saida,
        console_renderizado=console_auditavel,
    )
    _render_resultado_paridade_renderizacao(resultado_paridade_renderizacao)

    inventario_legado_pipeline = construir_inventario_legado_pipeline()
    resultado_limpeza_depreciacao = construir_resultado_limpeza_depreciacao_controlada(
        resultado_paridade_renderizacao,
        evidencias_auxiliares=inventario_legado_pipeline,
    )
    _render_resultado_limpeza_depreciacao(resultado_limpeza_depreciacao)

    return caminho_saida


if __name__ == "__main__":
    main()
