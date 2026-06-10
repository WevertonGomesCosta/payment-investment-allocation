from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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
from nucleo.situacao_atual_oficial import construir_situacao_atual_oficial


def _valor(objeto, campo, padrao=None):
    if isinstance(objeto, dict):
        return objeto.get(campo, padrao)
    return getattr(objeto, campo, padrao)


def _como_dict(objeto: Any) -> dict[str, Any]:
    if objeto is None:
        return {}
    if isinstance(objeto, dict):
        return dict(objeto)
    try:
        from dataclasses import asdict, is_dataclass

        if is_dataclass(objeto):
            return asdict(objeto)
    except Exception:
        pass
    return {
        chave: getattr(objeto, chave)
        for chave in dir(objeto)
        if not chave.startswith('_') and not callable(getattr(objeto, chave, None))
    }


def _fontes_consulta(item: dict[str, Any]) -> list[dict[str, Any]]:
    fontes = [item]
    for chave in ('referencia_original', 'referencia_recebido_temporal', 'referencia_switching_temporal', 'metadados'):
        valor = item.get(chave)
        if isinstance(valor, dict):
            fontes.append(valor)
    return fontes


def _primeiro(item: dict[str, Any], *campos: str, padrao: Any = None) -> Any:
    for fonte in _fontes_consulta(item):
        for campo in campos:
            valor = fonte.get(campo)
            if valor not in (None, ''):
                return valor
    return padrao


def _float(valor: Any, padrao: float = 0.0) -> float:
    try:
        if valor in (None, ''):
            return padrao
        return float(valor)
    except Exception:
        return padrao


def _fmt_lote(valor: Any) -> str:
    return str(valor or '').strip()


def _materializar_extrato_passado_oficial(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for item_bruto in list(getattr(saida_canonica_oficial, 'pagamentos_historicos_realizados', []) or []):
        item = _como_dict(item_bruto)
        lote = _primeiro(
            item,
            'Lote',
            'Lotes usados',
            'lote',
            'lote_usado',
            'lote_id_operacional',
            'fonte_resolvida_historica',
            padrao='',
        )
        linhas.append(
            {
                'Data': _primeiro(item, 'Data', 'data', 'data_pagamento'),
                'Conta': _primeiro(item, 'Conta', 'Descrição', 'Descricao', 'conta', 'fonte_informada', padrao=''),
                'Despesa ID': _primeiro(item, 'Despesa ID', 'despesa_id', 'pagamento_id', 'obrigacao_id', 'id', padrao=''),
                'Lote': lote,
                'Lotes usados': lote,
                'Saldo Antes': _primeiro(item, 'Saldo Antes', 'saldo_antes', 'saldo_antes_fonte', padrao=''),
                'Bruto': _primeiro(item, 'Bruto', 'valor_bruto_resgate', 'valor_bruto', 'valor', padrao=0.0),
                'Imposto': _primeiro(item, 'Imposto', 'imposto_resgate', 'imposto', padrao=0.0),
                'Líquido': _primeiro(item, 'Líquido', 'Liquido', 'valor_liquido_resgate', 'valor_liquido', 'valor', padrao=0.0),
                'Saldo Remanescente': _primeiro(
                    item,
                    'Saldo Remanescente',
                    'Saldo remanescente',
                    'saldo_remanescente',
                    'saldo_remanescente_fonte',
                    padrao=0.0,
                ),
            }
        )
    return linhas


def _linha_lote_ativo_de_saldo(saldo_bruto: Any, data_referencia: Any) -> dict[str, Any] | None:
    saldo = _como_dict(saldo_bruto)
    lote = _fmt_lote(
        _primeiro(
            saldo,
            'lote_id_operacional',
            'lote_id',
            'Lote',
            'fonte_id',
            'fonte_id_tecnico',
            padrao='',
        )
    )
    if not lote:
        return None
    liquido = _float(_primeiro(saldo, 'valor_disponivel_referencial', 'valor_liquido_atual', 'Líquido', 'Liquido', padrao=0.0))
    if round(liquido, 2) <= 0.20:
        return None
    valor_original = _float(
        _primeiro(
            saldo,
            'valor_original',
            'Valor original',
            'valor_bruto_original',
            'valor_aplicado',
            padrao=liquido,
        ),
        padrao=liquido,
    )
    return {
        'Lote': lote,
        'Produto': _primeiro(saldo, 'produto', 'Produto', 'carteira', 'Carteira', 'investimento', padrao=lote),
        'Aplicação': _primeiro(saldo, 'data_aplicacao', 'Aplicação', 'Aplicacao', 'data_recebimento', padrao=data_referencia),
        'Base fiscal': _primeiro(saldo, 'data_base_fiscal', 'Base fiscal', 'data_aplicacao', padrao=data_referencia),
        'Valor original': round(valor_original, 2),
        'Bruto': round(_float(_primeiro(saldo, 'valor_bruto_atual', 'Bruto', padrao=liquido)), 2),
        'Líquido': round(liquido, 2),
        'Status ciclo': _primeiro(saldo, 'status_temporal', 'status', padrao='ativo'),
    }


def _materializar_lotes_ativos_oficiais(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    data_referencia = getattr(saida_canonica_oficial, 'data_referencia', None)
    saldos_por_data = dict(getattr(saida_canonica_oficial, 'saldos_referenciais_por_data', {}) or {})
    saldos_referencia = []
    if saldos_por_data:
        data_saldo = data_referencia if data_referencia in saldos_por_data else max(saldos_por_data)
        saldos_referencia = list(saldos_por_data.get(data_saldo, []) or [])

    linhas: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for saldo in saldos_referencia:
        linha = _linha_lote_ativo_de_saldo(saldo, data_referencia)
        if not linha:
            continue
        lote = _fmt_lote(linha.get('Lote'))
        if lote in vistos:
            continue
        vistos.add(lote)
        linhas.append(linha)

    for item_bruto in list(getattr(saida_canonica_oficial, 'lotes_pos_switching_materializados', []) or []):
        item = _como_dict(item_bruto)
        lote = _fmt_lote(_primeiro(item, 'lote_id_operacional', 'lote_id', 'lote_destino', 'Lote', padrao=''))
        if not lote or lote in vistos:
            continue
        valor = _float(_primeiro(item, 'valor_liquido_migrado', 'valor_liquido_migrado_referencial', 'valor', padrao=0.0))
        if round(valor, 2) <= 0.20:
            continue
        vistos.add(lote)
        linhas.append(
            {
                'Lote': lote,
                'Produto': _primeiro(item, 'produto_destino', 'produto', 'Produto', padrao=lote),
                'Aplicação': _primeiro(item, 'data_aplicacao', 'data_switching', padrao=data_referencia),
                'Base fiscal': _primeiro(item, 'data_aplicacao', 'data_switching', padrao=data_referencia),
                'Valor original': round(valor, 2),
                'Bruto': round(valor, 2),
                'Líquido': round(valor, 2),
                'Status ciclo': 'ativo_pos_switching',
            }
        )
    return linhas


def _materializar_lotes_exauridos_oficiais(extrato_passado: list[dict[str, Any]], lotes_ativos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ativos = {_fmt_lote(item.get('Lote')) for item in lotes_ativos}
    acumulado: dict[str, dict[str, Any]] = {}
    for linha in extrato_passado:
        lote = _fmt_lote(linha.get('Lotes usados') or linha.get('Lote'))
        if not lote or lote in ativos:
            continue
        atual = acumulado.setdefault(
            lote,
            {
                'Lote': lote,
                'Produto': lote,
                'Aplicação': linha.get('Data'),
                'Base fiscal': linha.get('Data'),
                'Valor original': 0.0,
                'Bruto': 0.0,
                'Líquido': 0.0,
                'Saldo Remanescente': 0.0,
                'Status ciclo': 'exaurido_por_saque',
            },
        )
        atual['Valor original'] = round(_float(atual.get('Valor original')) + abs(_float(linha.get('Bruto'))), 2)
        atual['Bruto'] = 0.0
        atual['Líquido'] = 0.0
        atual['Saldo Remanescente'] = linha.get('Saldo Remanescente')
    return [item for item in acumulado.values() if round(_float(item.get('Saldo Remanescente')), 2) <= 0.20]


def _materializar_switchings_oficiais(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for item_bruto in list(getattr(saida_canonica_oficial, 'switchings_realizados_operacionais', []) or []):
        item = _como_dict(item_bruto)
        linhas.append(
            {
                'Data': _primeiro(item, 'data', 'data_switching', 'data_aplicacao'),
                'Lote origem': _primeiro(item, 'lote_origem_id', 'lote_origem', padrao=''),
                'Lote destino': _primeiro(item, 'lote_destino_id', 'lote_destino', padrao=''),
                'Produto origem': _primeiro(item, 'produto_origem', 'Produto origem', padrao=''),
                'Produto destino': _primeiro(item, 'produto_destino', 'Produto destino', padrao=''),
                'Valor líquido origem': _primeiro(item, 'valor_liquido_migrado_referencial', 'valor_liquido_migrado', padrao=0.0),
                'Status': _primeiro(item, 'status', 'status_observavel', padrao='switching_operacional_preservado'),
            }
        )
    return linhas


def _materializar_recebidos_oficiais(saida_canonica_oficial: Any) -> list[dict[str, Any]]:
    recebidos: list[dict[str, Any]] = []
    for item_bruto in list(getattr(saida_canonica_oficial, 'destinos_sobras_recebidos', []) or []):
        item = _como_dict(item_bruto)
        valor_bruto = _float(_primeiro(item, 'valor_bruto', 'valor_recebido', 'Valor bruto', 'valor', padrao=0.0))
        valor_liquido = _float(_primeiro(item, 'valor_liquido', 'Valor líquido', 'valor_liquido_aplicado', padrao=valor_bruto))
        recebidos.append(
            {
                'Recebido': _primeiro(item, 'recebido_id', 'Recebido', 'lote_origem', 'lote_id_operacional', padrao='recebido_sem_id'),
                'Lote origem': _primeiro(item, 'lote_origem', 'lote_id_operacional', 'fonte_id_tecnico', padrao=''),
                'Recebimento': _primeiro(item, 'data_recebimento', 'Recebimento', 'data', padrao=''),
                'Aplicação': _primeiro(item, 'data_aplicacao', 'Aplicação', padrao=''),
                'Valor bruto': round(valor_bruto, 2),
                'Valor líquido': round(valor_liquido, 2),
                'Status': _primeiro(item, 'status_materializacao', 'status', padrao='materializado_oficial'),
                'Destino': _primeiro(item, 'destino_explicito', 'investimento_destino', 'carteira_destino', 'Destino', padrao=''),
                'Pagamentos vinculados': len(list(_primeiro(item, 'pagamentos_vinculados', padrao=[]) or [])),
                'Valor vinculado': _primeiro(item, 'valor_vinculado', 'Valor vinculado', padrao=0.0),
                'Residual aplicação': _primeiro(item, 'valor_residual_aplicacao', 'Residual aplicação', padrao=0.0),
                'Disponível ref': _primeiro(item, 'valor_disponivel_referencial', 'Disponível ref', padrao=valor_liquido),
                'Observação': _primeiro(item, 'origem', 'observacao', padrao='SaidaCanonicaOficial'),
            }
        )
    return recebidos


def _resumo_recebidos_oficiais(recebidos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {'Métrica': 'Total de recebidos', 'Valor': len(recebidos)},
        {'Métrica': 'Valor bruto total dos recebidos', 'Valor': round(sum(_float(item.get('Valor bruto')) for item in recebidos), 2)},
        {'Métrica': 'Valor líquido total dos recebidos', 'Valor': round(sum(_float(item.get('Valor líquido')) for item in recebidos), 2)},
        {'Métrica': 'Origem', 'Valor': 'SaidaCanonicaOficial'},
    ]


def _fonte_situacao_atual_da_saida_oficial(saida_canonica_oficial: Any) -> SimpleNamespace:
    extrato_passado = _materializar_extrato_passado_oficial(saida_canonica_oficial)
    lotes_ativos = _materializar_lotes_ativos_oficiais(saida_canonica_oficial)
    lotes_exauridos = _materializar_lotes_exauridos_oficiais(extrato_passado, lotes_ativos)
    recebidos_atuais = _materializar_recebidos_oficiais(saida_canonica_oficial)
    switchings = _materializar_switchings_oficiais(saida_canonica_oficial)
    return SimpleNamespace(
        data_referencia=getattr(saida_canonica_oficial, 'data_referencia', None),
        extrato_passado=extrato_passado,
        lotes_ativos=lotes_ativos,
        lotes_exauridos=lotes_exauridos,
        switchings=switchings,
        recebidos_atuais=recebidos_atuais,
        fechamento_atual=[
            {'Métrica': 'Data de referência', 'Valor': getattr(saida_canonica_oficial, 'data_referencia', None)},
            {'Métrica': 'Status do fechamento econômico', 'Valor': getattr(saida_canonica_oficial, 'status', None)},
            {'Métrica': 'Fonte do fechamento', 'Valor': 'SaidaCanonicaOficial'},
            {'Métrica': 'Fechamentos com fallback CDI', 'Valor': 0},
        ],
        resumo_recebidos=_resumo_recebidos_oficiais(recebidos_atuais),
        auditoria={
            'origem_formal': 'SaidaCanonicaOficial',
            'adaptacao_observavel_situacao_atual': True,
            'sem_consumo_saida_canonica_transitoria': True,
            'sem_consumo_matriz_elegibilidade_transitoria': True,
            'qtd_lotes_ativos': len(lotes_ativos),
            'qtd_lotes_exauridos': len(lotes_exauridos),
            'qtd_switchings': len(switchings),
            'qtd_recebidos': len(recebidos_atuais),
        },
    )


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

    saida_canonica_oficial_preliminar = construir_saida_canonica_oficial(
        ledger=ledger_temporal_canonico,
        gates=resultado_gates_validacao_nucleo,
        ranking_carteira=getattr(contexto_operacional_canonico, 'ranking_carteira', None),
    )
    fonte_situacao_atual = _fonte_situacao_atual_da_saida_oficial(saida_canonica_oficial_preliminar)
    situacao_atual_origem = construir_situacao_atual_oficial(
        contexto_operacional_canonico,
        fonte_situacao_atual,
        estado_temporal_inicial=estado_temporal_inicial,
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
        saida_canonica_oficial,
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
