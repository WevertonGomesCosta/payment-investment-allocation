from __future__ import annotations

from aplicacao.console.common import imprimir_itens_severidade, imprimir_linha_status, imprimir_pares, imprimir_titulo


def render_secao_canonicas(*, carteira_canonica, dados_operacionais, switching_shadow, severidade_carteira, severidade_inventario, severidade_gastos, severidade_lotes_shadow, severidade_eventos_shadow, severidade_triagem, severidade_nucleo, resumo_inventario, resumo_gastos, validacao_carteira, validacao_inventario, validacao_gastos, resumo_lotes_shadow, auditoria_eventos_shadow, reconciliacao_shadow, auditoria_triagem, auditoria_nucleo):
    imprimir_titulo('RESUMO CONSOLIDADO DAS CAMADAS CANÔNICAS')
    imprimir_linha_status('Carteira canônica', severidade_carteira, f"{len(carteira_canonica.quadro_canonico)} produtos")
    imprimir_linha_status('Inventário canônico', severidade_inventario, f"{len(dados_operacionais.inventario_canonico)} lotes")
    imprimir_linha_status('Gastos canônicos', severidade_gastos, f"{len(dados_operacionais.gastos_canonicos)} despesas")
    imprimir_linha_status('Lotes shadow', severidade_lotes_shadow, f"{len(switching_shadow.lotes_shadow)} lotes técnicos")
    imprimir_linha_status('Trilha técnica de eventos', severidade_eventos_shadow, f"{len(switching_shadow.eventos_financeiros_ordenados)} eventos ordenados")
    imprimir_linha_status('Triagem programática do motor', severidade_triagem, f"{auditoria_triagem.get('qtd_candidatos_motor_v1', 0)} candidatos")
    imprimir_linha_status('Núcleo financeiro mínimo', severidade_nucleo, f"{auditoria_nucleo.get('qtd_lotes_financeiros', 0)} lotes financeiros")

    imprimir_titulo('CARTEIRA CANÔNICA')
    imprimir_linha_status('Validação estrutural da carteira', severidade_carteira)
    imprimir_pares([
        ('aba', carteira_canonica.nome_aba),
        ('produtos canônicos', len(carteira_canonica.quadro_canonico)),
        ('produto_key únicos', len(carteira_canonica.mapa_produtos.get('by_key', {}))),
        ('nomes normalizados únicos', len(carteira_canonica.mapa_produtos.get('by_nome_norm', {}))),
        ('famílias de produto', len(carteira_canonica.auditoria.get('resumo_familia_produto', {}))),
        ('regimes de taxa', len(carteira_canonica.auditoria.get('resumo_regime_taxa', {}))),
        ('papéis de produto', len(carteira_canonica.auditoria.get('resumo_papel_produto', {}))),
        ('linhas sem produto_id explícito', carteira_canonica.auditoria.get('sem_produto_id', 0)),
        ('erros de validação', len(validacao_carteira.get('erros') or [])),
        ('avisos de validação', len(validacao_carteira.get('avisos') or [])),
    ])
    print('- colunas resolvidas:')
    for chave, valor in carteira_canonica.auditoria.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    imprimir_itens_severidade('erros de validação', validacao_carteira.get('erros'), 'ERRO')
    imprimir_itens_severidade('avisos de validação', validacao_carteira.get('avisos'), 'AVISO')

    imprimir_titulo('CARTEIRA CANÔNICA — OBSERVAÇÕES')
    print('- observação estrutural: metadados derivados da carteira atuam como ponte transitória até maior estruturação explícita da planilha.')
    print(f"- campos estruturais ainda sem coluna resolvida: {carteira_canonica.auditoria.get('qtd_campos_estruturais_sem_coluna_resolvida', 0)}")
    if carteira_canonica.auditoria.get('campos_estruturais_sem_coluna_resolvida'):
        print(f"  [AVISO] pendentes na planilha: {', '.join(carteira_canonica.auditoria.get('campos_estruturais_sem_coluna_resolvida', []))}")
    print('- fontes dos metadados estruturais:')
    for campo, resumo in carteira_canonica.auditoria.get('resumo_fontes_metadados', {}).items():
        cobertura_planilha = carteira_canonica.auditoria.get('resumo_cobertura_metadados_planilha', {}).get(campo, 0)
        cobertura_derivada = carteira_canonica.auditoria.get('resumo_cobertura_metadados_derivados', {}).get(campo, 0)
        print(f"  [OK] {campo}: {resumo} | planilha={cobertura_planilha} | derivado={cobertura_derivada}")

    imprimir_titulo('INVENTÁRIO CANÔNICO')
    imprimir_linha_status('Validação estrutural do inventário', severidade_inventario)
    imprimir_pares([
        ('aba', dados_operacionais.nome_aba_lotes),
        ('lotes canônicos', len(dados_operacionais.inventario_canonico)),
        ('aportados', resumo_inventario.get('aportados', 0)),
        ('não aportados disponíveis', resumo_inventario.get('nao_aportados_disponiveis', 0)),
        ('não aportados exauridos', resumo_inventario.get('nao_aportados_exauridos', 0)),
        ('recebidos futuros', resumo_inventario.get('recebidos_futuros', 0)),
        ('aportados com match', resumo_inventario.get('aportados_com_match', 0)),
        ('aportados sem match', resumo_inventario.get('aportados_sem_match', 0)),
        ('erros de validação', len(validacao_inventario.get('erros') or [])),
        ('avisos de validação', len(validacao_inventario.get('avisos') or [])),
    ])
    print('- colunas resolvidas:')
    for chave, valor in dados_operacionais.auditoria_inventario.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    imprimir_itens_severidade('erros de validação', validacao_inventario.get('erros'), 'ERRO')
    imprimir_itens_severidade('avisos de validação', validacao_inventario.get('avisos'), 'AVISO')

    imprimir_titulo('GASTOS CANÔNICOS')
    imprimir_linha_status('Validação estrutural dos gastos', severidade_gastos)
    imprimir_pares([
        ('aba', dados_operacionais.nome_aba_despesas),
        ('despesas canônicas', len(dados_operacionais.gastos_canonicos)),
        ('pagas até data de referência', resumo_gastos.get('pagas_ate_data_referencia', 0)),
        ('futuras ou pendentes', resumo_gastos.get('futuras_ou_pendentes', 0)),
        ('com lote informado', resumo_gastos.get('com_lote_informado', 0)),
        ('erros de validação', len(validacao_gastos.get('erros') or [])),
        ('avisos de validação', len(validacao_gastos.get('avisos') or [])),
    ])
    print('- colunas resolvidas:')
    for chave, valor in dados_operacionais.auditoria_gastos.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    imprimir_itens_severidade('erros de validação', validacao_gastos.get('erros'), 'ERRO')
    imprimir_itens_severidade('avisos de validação', validacao_gastos.get('avisos'), 'AVISO')

    imprimir_titulo('SWITCHING SHADOW E RECONCILIAÇÃO')
    imprimir_linha_status('Normalização shadow dos lotes', severidade_lotes_shadow)
    imprimir_pares([
        ('lotes shadow', len(switching_shadow.lotes_shadow)),
        ('produto reconhecido', resumo_lotes_shadow.get('qtd_produto_reconhecido', 0)),
        ('produto não reconhecido', resumo_lotes_shadow.get('qtd_produto_nao_reconhecido', 0)),
        ('fração produto reconhecido', resumo_lotes_shadow.get('fracao_produto_reconhecido', 0.0)),
        ('caixa disponível', resumo_lotes_shadow.get('qtd_caixa_disponivel', 0)),
        ('caixa futuro', resumo_lotes_shadow.get('qtd_caixa_futuro', 0)),
        ('caixa exaurido', resumo_lotes_shadow.get('qtd_caixa_exaurido', 0)),
        ('eventos aporte shadow', auditoria_eventos_shadow.get('qtd_eventos_aporte', 0)),
        ('reconciliação equivalente', 'sim' if reconciliacao_shadow.get('equivalentes_essenciais') else 'não'),
        ('ids somente shadow', len(reconciliacao_shadow.get('ids_somente_shadow', []))),
        ('ids somente observado', len(reconciliacao_shadow.get('ids_somente_observado', []))),
        ('cobertura ids observado', reconciliacao_shadow.get('fracao_ids_observado_cobertos', 0.0)),
        ('cobertura ids shadow', reconciliacao_shadow.get('fracao_ids_shadow_cobertos', 0.0)),
    ])
    if resumo_lotes_shadow.get('resumo_tipos_match_produto'):
        print('- tipos de match de produto no shadow:')
        for chave, valor in resumo_lotes_shadow.get('resumo_tipos_match_produto', {}).items():
            print(f"  [OK] {chave}: {valor}")
