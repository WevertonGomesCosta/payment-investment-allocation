from __future__ import annotations

from aplicacao.console.common import imprimir_itens_severidade, imprimir_linha_status, imprimir_pares, imprimir_tabela, imprimir_titulo


def render_secao_nucleo(*, auditoria_nucleo, validacao_nucleo, severidade_nucleo):
    imprimir_titulo('NÚCLEO FINANCEIRO MÍNIMO')
    imprimir_linha_status('Primitivas financeiras irreduzíveis do lote', severidade_nucleo, 'sem solver, sem replay, sem switching econômico e sem relatório financeiro atual')
    imprimir_pares([
        ('lotes financeiros', auditoria_nucleo.get('qtd_lotes_financeiros', 0)),
        ('lotes aportados', auditoria_nucleo.get('qtd_lotes_aportados', 0)),
        ('caixa disponível', auditoria_nucleo.get('qtd_caixa_disponivel', 0)),
        ('recebidos futuros', auditoria_nucleo.get('qtd_recebidos_futuros', 0)),
        ('lotes não disponíveis para aporte', auditoria_nucleo.get('qtd_lotes_nao_disponiveis_para_aporte', 0)),
        ('lotes com produto mapeado', auditoria_nucleo.get('qtd_lotes_produto_mapeado', 0)),
        ('lotes sem produto', auditoria_nucleo.get('qtd_lotes_sem_produto', 0)),
        ('lotes com taxa default', auditoria_nucleo.get('qtd_lotes_com_taxa_default', 0)),
        ('lotes com carência', auditoria_nucleo.get('qtd_lotes_com_carencia', 0)),
        ('lotes exauridos ignorados', auditoria_nucleo.get('qtd_lotes_ignorados_exauridos', 0)),
    ])
    imprimir_itens_severidade('erros de validação', validacao_nucleo.get('erros'), 'ERRO')
    imprimir_itens_severidade('avisos de validação', validacao_nucleo.get('avisos'), 'AVISO')

    imprimir_titulo('NÚCLEO FINANCEIRO MÍNIMO — VALUATION')
    imprimir_pares([
        ('data final valuation ref. completa', auditoria_nucleo.get('data_final_valuation_referencia')),
        ('fechamentos da referência com fallback CDI', auditoria_nucleo.get('qtd_fechamentos_referencia_com_fallback_cdi', 0)),
        ('saldo bruto ref. sem replay', auditoria_nucleo.get('saldo_bruto_total_referencia_sem_replay', 0.0)),
        ('saldo líquido ref. sem replay', auditoria_nucleo.get('saldo_liquido_total_referencia_sem_replay', 0.0)),
    ])

    imprimir_titulo('NÚCLEO FINANCEIRO MÍNIMO — AMOSTRAS')
    amostra_saque = auditoria_nucleo.get('amostra_movimento_saque') or {}
    if amostra_saque:
        print('- amostra de saque no núcleo mínimo (auditoria técnica):')
        print(f"  [OK] lote={amostra_saque.get('lote_id')} | bruto={amostra_saque.get('bruto')} | liquido={amostra_saque.get('liquido')} | imposto={amostra_saque.get('imposto')} | saldo_remanescente={amostra_saque.get('saldo_remanescente')}")
    amostra_fechamento_nucleo = auditoria_nucleo.get('amostra_fechamento_referencia') or {}
    if amostra_fechamento_nucleo:
        print('- amostra de fechamento da referência no núcleo mínimo:')
        print(f"  [OK] data_valuation={amostra_fechamento_nucleo.get('data_valuation')} | data_fator_utilizado={amostra_fechamento_nucleo.get('data_fator_utilizado')} | fonte={amostra_fechamento_nucleo.get('fonte')} | lotes_atualizados={amostra_fechamento_nucleo.get('qtd_lotes_atualizados')}")
    if not amostra_saque and not amostra_fechamento_nucleo:
        print('  [OK] nenhuma amostra disponível nesta execução')


def render_secao_replay(*, auditoria_replay, validacao_replay, severidade_replay, limiar_residuo_resolvido):
    imprimir_titulo('REPLAY CONTROLADO DO PASSADO')
    imprimir_linha_status('Reconciliacao de pagamentos historicos com lotes informados', severidade_replay, 'consome o nucleo financeiro minimo sem abrir switching economico, score final, solver ou relatorio financeiro atual')
    imprimir_pares([
        ('contas historicas', auditoria_replay.get('qtd_contas_historicas', 0)),
        ('contas com lote informado', auditoria_replay.get('qtd_contas_com_lote_informado', 0)),
        ('contas processadas', auditoria_replay.get('qtd_contas_processadas', 0)),
        ('cobertas integralmente', auditoria_replay.get('qtd_contas_cobertas_integralmente', 0)),
        ('parcialmente cobertas', auditoria_replay.get('qtd_contas_parcialmente_cobertas', 0)),
        ('nao cobertas', auditoria_replay.get('qtd_contas_nao_cobertas', 0)),
        ('contas sem lote informado', auditoria_replay.get('qtd_contas_sem_lote_informado', 0)),
        ('lotes historicos nao aportados materializados', auditoria_replay.get('qtd_lotes_historicos_nao_aportados_materializados', 0)),
        ('aliases historicos resolvidos', auditoria_replay.get('qtd_lotes_historicos_alias_resolvidos', 0)),
        ('lotes informados nao encontrados', auditoria_replay.get('qtd_lotes_informados_nao_encontrados', 0)),
        ('movimentos no log', auditoria_replay.get('qtd_movimentos_log', 0)),
        ('lotes remanescentes ativos', auditoria_replay.get('qtd_lotes_remanescentes_ativos', 0)),
        ('data final histórica do replay', auditoria_replay.get('data_final_historico_replay')),
        ('valor contas historicas', auditoria_replay.get('total_valor_contas_historicas', 0.0)),
        ('liquido coberto', auditoria_replay.get('total_liquido_coberto', 0.0)),
        ('saldo bruto pos replay', auditoria_replay.get('saldo_bruto_total_pos_replay', 0.0)),
        ('saldo liquido pos replay', auditoria_replay.get('saldo_liquido_total_pos_replay', 0.0)),
    ])

    imprimir_titulo('REPLAY CONTROLADO DO PASSADO — VALUATION')
    imprimir_pares([
        ('data final valuation ref. completa', auditoria_replay.get('data_final_valuation_referencia')),
        ('fechamentos da referência com fallback CDI', auditoria_replay.get('qtd_fechamentos_referencia_com_fallback_cdi', 0)),
    ])

    imprimir_titulo('REPLAY CONTROLADO DO PASSADO — AMOSTRAS')
    amostra_replay = auditoria_replay.get('amostra_log_passado') or {}
    if amostra_replay:
        print('- amostra do log de replay do passado:')
        print(f"  [OK] data={amostra_replay.get('Data')} | lote={amostra_replay.get('Lote')} | conta={amostra_replay.get('Conta')} | bruto={amostra_replay.get('Bruto')} | liquido={amostra_replay.get('Liquido')} | saldo_remanescente={amostra_replay.get('Saldo Remanescente')}")
    amostra_fechamento_replay = auditoria_replay.get('amostra_fechamento_referencia') or {}
    if amostra_fechamento_replay:
        print('- amostra de fechamento da referência no replay:')
        print(f"  [OK] data_valuation={amostra_fechamento_replay.get('data_valuation')} | data_fator_utilizado={amostra_fechamento_replay.get('data_fator_utilizado')} | fonte={amostra_fechamento_replay.get('fonte')} | lotes_atualizados={amostra_fechamento_replay.get('qtd_lotes_atualizados')}")
    amostras_alias_replay = auditoria_replay.get('amostra_alias_historicos_resolvidos') or []
    if amostras_alias_replay:
        print('- amostras de aliases historicos resolvidos no replay:')
        for item in amostras_alias_replay[:5]:
            print(f"  [OK] informado={item.get('lote_informado')} | resolvido={item.get('lote_resolvido')} | despesa={item.get('despesa_id')} | data={item.get('data_conta')}")
    amostra_inconsistencias_replay = auditoria_replay.get('amostra_inconsistencias_materiais') or []
    if amostra_inconsistencias_replay:
        print(f"- tabela de inconsistências materiais do replay controlado (> limiar {auditoria_replay.get('limiar_materialidade_replay', limiar_residuo_resolvido):.2f}):")
        colunas_inc = ['Data', 'Despesa', 'Despesa ID', 'Valor', 'Lotes informados', 'Motivo', 'Valor restante']
        linhas_inc = []
        for item in amostra_inconsistencias_replay[:10]:
            data = item.get('data')
            if hasattr(data, 'isoformat'):
                data = data.isoformat()
            linhas_inc.append({
                'Data': data,
                'Despesa': item.get('descricao') or '',
                'Despesa ID': item.get('despesa_id') or '',
                'Valor': item.get('valor_conta'),
                'Lotes informados': item.get('lotes_informados') or item.get('lote_id') or '',
                'Motivo': item.get('motivo') or '',
                'Valor restante': item.get('valor_restante'),
            })
        imprimir_tabela(colunas_inc, linhas_inc)
    if not amostra_replay and not amostra_fechamento_replay and not amostras_alias_replay and not amostra_inconsistencias_replay:
        print('  [OK] nenhuma amostra disponível nesta execução')
    imprimir_itens_severidade('erros de validação', validacao_replay.get('erros'), 'ERRO')
    imprimir_itens_severidade('avisos de validação', validacao_replay.get('avisos'), 'AVISO')





def render_secao_metodo_pagamentos(*, auditoria_metodo=None, amostra_mudancas_metodo=None):
    auditoria_metodo = auditoria_metodo or {}
    amostra_mudancas_metodo = amostra_mudancas_metodo or []

    imprimir_titulo('PAGAMENTOS FUTUROS — MÉTODO ATIVO E AUDITORIA')
    imprimir_pares([
        ('modelo governante atual', auditoria_metodo.get('modelo_governante') or ''),
        ('método auditável atual', auditoria_metodo.get('metodo_governante') or ''),
        ('proxy econômico ativo', auditoria_metodo.get('proxy_ativo') or ''),
        ('pagamentos auditados', auditoria_metodo.get('total_pagamentos_auditados', 0)),
        ('pagamentos cobertos pelo método atual', auditoria_metodo.get('pagamentos_cobertos_metodo_atual', 0)),
        ('pagamentos cobertos pelo proxy v2', auditoria_metodo.get('pagamentos_cobertos_proxy_v2', 0)),
        ('mudanças materiais v2→v3', auditoria_metodo.get('mudancas_materiais_v2_v3', 0)),
        ('casos em que v3 melhora o score comum v3', auditoria_metodo.get('casos_v3_melhor_score_comum_v3', 0)),
        ('cobertura integral do runner shadow', auditoria_metodo.get('pagamentos_cobertos_runner_shadow', 0)),
        ('pagamentos sem cobertura no runner shadow', auditoria_metodo.get('pagamentos_sem_cobertura_runner_shadow', 0)),
        ('recomendação operacional', auditoria_metodo.get('recomendacao_operacional') or ''),
    ])

    print('- parâmetros centrais do método governante:')
    print(f"  [OK] prioridade de fonte: {auditoria_metodo.get('prioridade_fontes') or ''}")
    print(f"  [OK] janela de excesso do proxy v3: {auditoria_metodo.get('janela_excesso_proxy_v3') or ''}")
    print(f"  [OK] componentes centrais do score: {auditoria_metodo.get('componentes_score_proxy_v3') or ''}")
    print(f"  [OK] leitura temporal da fonte: {auditoria_metodo.get('leitura_temporal_fonte') or ''}")
    print(f"  [OK] por que o método atual governa: {auditoria_metodo.get('justificativa_metodo_governante') or ''}")

    if amostra_mudancas_metodo:
        print('\n- amostra das mudanças materiais entre proxy v2 e v3:')
        imprimir_tabela(
            ['Data', 'Despesa ID', 'Descrição', 'Valor', 'Lote v2', 'Lote v3', 'Delta score comum v3'],
            amostra_mudancas_metodo,
            limite=5,
        )

def render_secao_amostras_pagamentos(*, pagamentos_realizados=None, pagamentos_proximos=None):
    imprimir_titulo('PAGAMENTOS — AMOSTRAS OPERACIONAIS')
    pagamentos_realizados = pagamentos_realizados or []
    pagamentos_proximos = pagamentos_proximos or []

    print('- últimos 5 pagamentos já realizados:')
    imprimir_tabela(
        ['Data', 'Descrição', 'Valor', 'Lotes usados', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente'],
        pagamentos_realizados,
        limite=5,
    )

    print('\n- próximos 5 pagamentos:')
    imprimir_tabela(
        ['Data', 'Descrição', 'Valor', 'Lote sugerido', 'Saldo Antes', 'Bruto', 'Imposto', 'Líquido', 'Saldo Remanescente', 'Score proxy', 'Status local'],
        pagamentos_proximos,
        limite=5,
    )



def render_secao_auditoria_temporal_pagamentos(*, auditoria_temporal=None, amostra_primeiras_quebras=None):
    auditoria_temporal = auditoria_temporal or {}
    amostra_primeiras_quebras = amostra_primeiras_quebras or []
    resumo = auditoria_temporal.get('resumo', {})
    imprimir_titulo('PAGAMENTOS FUTUROS — AUDITORIA TEMPORAL DA DECISÃO LOCAL')
    imprimir_pares([
        ('pagamentos auditados', resumo.get('total_pagamentos_auditados', 0)),
        ('integrais na decisão local', resumo.get('pagamentos_integral_local', 0)),
        ('integrais na sequência', resumo.get('pagamentos_integral_temporal', 0)),
        ('quebras temporais da sugestão local', resumo.get('pagamentos_com_quebra_temporal', 0)),
        ('pagamentos após quebra da fonte', resumo.get('pagamentos_apos_quebra_fonte', 0)),
        ('fontes auditadas', resumo.get('fontes_auditadas', 0)),
        ('fontes com quebra temporal', resumo.get('fontes_com_quebra_temporal', 0)),
        ('primeira quebra global', resumo.get('primeira_quebra_global_data')),
        ('pagamento da primeira quebra', resumo.get('primeira_quebra_global_pagamento')),
        ('lote/fonte da primeira quebra', resumo.get('primeira_quebra_global_lote')),
        ('valor da primeira quebra', resumo.get('primeira_quebra_global_valor')),
        ('sequência na fonte da primeira quebra', resumo.get('primeira_quebra_global_seq_fonte')),
    ])
    if amostra_primeiras_quebras:
        print('\n- amostra das primeiras quebras temporais por fonte sugerida:')
        imprimir_tabela(
            ['Data', 'Descrição', 'Valor', 'Lote sugerido', 'Seq. fonte', 'Saldo Antes temporal', 'Status temporal'],
            amostra_primeiras_quebras,
            limite=10,
        )



def render_secao_reescolha_dinamica_pagamentos(*, auditoria_reescolha=None, amostra_reescolhas=None, amostra_sem_cobertura=None):
    auditoria_reescolha = auditoria_reescolha or {}
    amostra_reescolhas = amostra_reescolhas or []
    amostra_sem_cobertura = amostra_sem_cobertura or []
    resumo = auditoria_reescolha.get('resumo', {})
    imprimir_titulo('PAGAMENTOS FUTUROS — REESCOLHA DINÂMICA PÓS-QUEBRA')
    imprimir_pares([
        ('pagamentos auditados', resumo.get('total_pagamentos_auditados', 0)),
        ('mantidos sem reescolha', resumo.get('pagamentos_mantidos_sem_reescolha', 0)),
        ('reescolhas acionadas', resumo.get('pagamentos_com_reescolha_acionada', 0)),
        ('mudanças efetivas de fonte', resumo.get('mudancas_efetivas_de_fonte', 0)),
        ('cobertos após reescolha', resumo.get('pagamentos_cobertos_pos_reescolha', 0)),
        ('sem cobertura após reescolha', resumo.get('pagamentos_sem_cobertura_pos_reescolha', 0)),
        ('pagamentos recuperados após reescolha', resumo.get('pagamentos_recuperados_pos_reescolha', 0)),
        ('primeira reescolha', resumo.get('primeira_reescolha_data')),
        ('pagamento da primeira reescolha', resumo.get('primeira_reescolha_pagamento')),
        ('lote original da primeira reescolha', resumo.get('primeira_reescolha_lote_original')),
        ('lote final da primeira reescolha', resumo.get('primeira_reescolha_lote_final')),
        ('primeira sem cobertura pós-reescolha', resumo.get('primeira_sem_cobertura_data')),
        ('pagamento da primeira sem cobertura', resumo.get('primeira_sem_cobertura_pagamento')),
        ('lote final da primeira sem cobertura', resumo.get('primeira_sem_cobertura_lote_final')),
    ])
    if amostra_reescolhas:
        print('\n- amostra das primeiras reescolhas dinâmicas:')
        imprimir_tabela(
            ['Data', 'Descrição', 'Valor', 'Lote original', 'Lote dinâmico', 'Status pós-reescolha', 'Score final'],
            amostra_reescolhas,
            limite=10,
        )
    if amostra_sem_cobertura:
        print('\n- amostra dos pagamentos ainda sem cobertura após a reescolha dinâmica:')
        imprimir_tabela(
            ['Data', 'Descrição', 'Valor', 'Lote dinâmico', 'Saldo Antes dinâmico', 'Status pós-reescolha'],
            amostra_sem_cobertura,
            limite=10,
        )

def render_secao_situacao_atual(*, lotes_ativos, lotes_exauridos=None, recebidos_atuais=None, resumo_fechamento=None, resumo_recebidos=None):
    imprimir_titulo('SITUAÇÃO ATUAL')
    resumo_fechamento = resumo_fechamento or {}
    resumo_recebidos = resumo_recebidos or {}
    lotes_exauridos = lotes_exauridos or []
    recebidos_atuais = recebidos_atuais or []
    if resumo_fechamento:
        imprimir_pares([
            ('data de referência', resumo_fechamento.get('data_referencia')),
            ('status do fechamento econômico', resumo_fechamento.get('status_fechamento')),
            ('fonte do fechamento', resumo_fechamento.get('fonte_fechamento')),
            ('fechamentos com fallback CDI', resumo_fechamento.get('qtd_fechamentos_fallback_cdi', 0)),
            ('último fator explícito CDI', resumo_fechamento.get('data_ultimo_fator_explicito_cdi')),
            ('data confirmada da série', resumo_fechamento.get('data_fechamento_confirmado')),
        ])
        observacao = resumo_fechamento.get('observacao')
        if observacao:
            print(f'- leitura auditável: {observacao}')
    print('\n- lotes exauridos:')
    if lotes_exauridos:
        print('  identificação e tempo:')
        imprimir_tabela(['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias corridos', 'Dias úteis'], lotes_exauridos)
        print('\n  valores atuais:')
        imprimir_tabela(['Lote', 'Valor original', 'Bruto', 'Líquido', 'Saldo rem'], lotes_exauridos)
    else:
        print('  [OK] sem lotes exauridos nesta execução')
    print('\n- lotes ativos:')
    if lotes_ativos:
        print('  identificação e tempo:')
        imprimir_tabela(['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Dias corridos', 'Dias úteis'], lotes_ativos)
        print('\n  valores atuais:')
        imprimir_tabela(['Lote', 'Valor original', 'Bruto', 'Líquido', 'Saldo rem'], lotes_ativos)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')
    print('\n- resumo dos recebidos auditáveis (inclui exauridos):')
    imprimir_pares([
        ('total de recebidos', resumo_recebidos.get('total_recebidos', len(recebidos_atuais))),
        ('valor total bruto', resumo_recebidos.get('valor_total_bruto', 0.0)),
        ('status recebido', resumo_recebidos.get('status_recebido', {})),
        ('destino potencial', resumo_recebidos.get('destino_potencial', {})),
        ('recebidos com pagamento vinculado', resumo_recebidos.get('recebidos_com_pagamento_vinculado', 0)),
        ('recebidos em janela pré-aplicação', resumo_recebidos.get('recebidos_em_janela_pre_aplicacao', 0)),
        ('recebidos usados antes da aplicação', resumo_recebidos.get('recebidos_usados_antes_da_aplicacao_observado', 0)),
    ])
    if not recebidos_atuais:
        print('  [OK] sem recebidos auditáveis materializados nesta execução')

