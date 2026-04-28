"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path
import pandas as pd

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.common import imprimir_itens_severidade as _imprimir_itens_severidade, imprimir_linha_status as _imprimir_linha_status, imprimir_pares as _imprimir_pares, imprimir_tabela as _imprimir_tabela, imprimir_titulo as _imprimir_titulo, normalizar_lista as _normalizar_lista, severidade as _severidade
from aplicacao.console.secoes_canonicas import render_secao_canonicas
from aplicacao.console.secoes_execucao import render_secao_execucao
from aplicacao.console.secoes_financeiras import render_secao_amostras_pagamentos, render_secao_auditoria_temporal_pagamentos, render_secao_heuristica_conjunta_parcial, render_secao_metodo_pagamentos, render_secao_nucleo, render_secao_planejamento_conjunto_local, render_secao_reescolha_dinamica_pagamentos, render_secao_replay, render_secao_situacao_atual, render_secao_microplanejamento_conjunto_v2, render_secao_recomputacao_sequencial_central_v1, render_secao_motor_recomendacao_pagamentos_switching_v1
from aplicacao.console.secoes_triagem import render_secao_triagem
from nucleo.calendario_financeiro import contar_dias_rendimento
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha
from nucleo.contexto_baseline import carregar_contexto_baseline, obter_limiar_residuo_resolvido
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof
from nucleo.caixa_recebidos_auditaveis import auditar_comparativo_proxy_v2_v3
from nucleo.saida_canonica import construir_saida_canonica



def _classificar_status_residuo(valor, limiar):
    return 'resolvido por limiar' if float(valor or 0.0) <= float(limiar or 0.0) else 'pendente para validação'


def _preparar_auditoria_lotes_residuais(replay_passado, config):
    linhas = []
    limiar = obter_limiar_residuo_resolvido(config)
    estado = replay_passado.estado_lotes_passado.copy()
    log = replay_passado.log_passado.copy()
    if len(estado):
        estado = estado[(estado['Saldo Após Replay'] > 0.0) & (estado['Saldo Após Replay'] <= 5.0)]
        estado = estado.sort_values(by=['Saldo Após Replay', 'Lote ID'], ascending=[False, True], kind='stable')
        for _, row in estado.iterrows():
            lote_id = str(row.get('Lote ID') or '')
            sub = log[log['Lote'].astype(str) == lote_id].copy() if len(log) else log
            ultimo = sub.iloc[-1] if len(sub) else None
            vezes_usado = int(row.get('Vezes Usado no Replay') or 0)
            saldo = round(float(row.get('Saldo Após Replay') or 0.0), 2)
            data_txt = ''
            conta_txt = ''
            if ultimo is not None:
                data_ult = ultimo['Data']
                data_txt = data_ult.isoformat() if hasattr(data_ult, 'isoformat') else str(data_ult)
                conta_txt = str(ultimo.get('Conta') or '')
            linhas.append({
                'Tipo': 'micro-saldo',
                'Referência': lote_id,
                'Data': data_txt,
                'Conta': conta_txt,
                'Lote': lote_id,
                'Valor': saldo,
                'Status': _classificar_status_residuo(saldo, limiar),
                'Classe provável': 'resíduo de saque/arredondamento' if vezes_usado > 0 else 'remanescente residual sem evidência de convenção',
                'Leitura': f"vezes usado={vezes_usado}; saldo final pequeno em lote remanescente",
            })

    for item in (replay_passado.auditoria or {}).get('amostra_inconsistencias', []) or []:
        valor_restante = round(float(item.get('valor_restante') or 0.0), 2)
        if valor_restante <= 0.0:
            continue
        classe = 'resíduo de saque/arredondamento' if valor_restante <= 1.0 else 'resíduo material do replay histórico'
        lote_ref = item.get('lotes_informados') or item.get('lote_id') or ''
        linhas.append({
            'Tipo': 'conta parcial',
            'Referência': item.get('despesa_id') or item.get('descricao') or '',
            'Data': item.get('data') or '',
            'Conta': item.get('descricao') or '',
            'Lote': lote_ref,
            'Valor': valor_restante,
            'Status': _classificar_status_residuo(valor_restante, limiar),
            'Classe provável': classe,
            'Leitura': f"data={item.get('data')} | lotes={lote_ref}",
        })

    linhas.sort(key=lambda item: (0 if item.get('Status') == 'pendente para validação' else 1, 0 if item.get('Tipo') == 'conta parcial' else 1, -float(item.get('Valor') or 0.0), str(item.get('Referência') or '')))
    return linhas


def _preparar_auditoria_detalhada_residuos(replay_passado, config, data_referencia):
    limiar = obter_limiar_residuo_resolvido(config)
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    lotes_por_id = {l.id: l for l in replay_passado.lotes_apos_replay}
    estado = replay_passado.estado_lotes_passado.copy()
    log = replay_passado.log_passado.copy()
    linhas = []

    inconsistencias = ((replay_passado.auditoria or {}).get('amostra_inconsistencias') or [])
    for item in inconsistencias:
        valor_restante = round(float(item.get('valor_restante') or 0.0), 2)
        if valor_restante <= 0.0:
            continue
        despesa_id = str(item.get('despesa_id') or '').strip()
        sub = log[log['Despesa ID'].astype(str) == despesa_id].copy() if len(log) else log
        lote = str(sub.iloc[-1]['Lote']) if len(sub) else str(item.get('lotes_informados') or item.get('lote_id') or '')
        conta = str(sub.iloc[-1]['Conta']) if len(sub) else str(item.get('descricao') or '')
        data_evento = sub.iloc[-1]['Data'] if len(sub) else item.get('data')
        data_txt = data_evento.isoformat() if hasattr(data_evento, 'isoformat') else str(data_evento)
        liquido_coberto = round(float(sub['Liquido'].sum()), 2) if len(sub) else round(float(item.get('valor_conta') or 0.0) - valor_restante, 2)
        saldo_final_evento = round(float(sub.iloc[-1]['Saldo Remanescente']), 2) if len(sub) else None
        lote_zerado = saldo_final_evento is not None and saldo_final_evento <= 0.01
        origem = 'teto líquido do lote no esgotamento' if lote_zerado else 'déficit residual após saque parcial'
        evid = f"lote={lote} | coberto={liquido_coberto:.2f} | faltou={valor_restante:.2f}"
        if saldo_final_evento is not None:
            evid += f" | saldo pós-evento={saldo_final_evento:.2f}"
        leitura = 'não há evidência de convenção temporal remanescente; a falta aparece no próprio evento histórico de saque'
        linhas.append({
            'Tipo': 'conta parcial',
            'Referência': despesa_id,
            'Data': data_txt,
            'Conta': conta,
            'Lote': lote,
            'Valor': valor_restante,
            'Status': _classificar_status_residuo(valor_restante, limiar),
            'Origem provável': origem,
            'Evidência-chave': evid,
            'Leitura': leitura,
        })

    if len(estado):
        estado = estado[(estado['Saldo Após Replay'] > 0.0) & (estado['Saldo Após Replay'] <= 5.0)]
        estado = estado.sort_values(by=['Saldo Após Replay', 'Lote ID'], ascending=[False, True], kind='stable')
        for _, row in estado.iterrows():
            lote_id = str(row.get('Lote ID') or '')
            saldo = round(float(row.get('Saldo Após Replay') or 0.0), 2)
            situacao = str(row.get('Situacao Investimento') or '')
            vezes_usado = int(row.get('Vezes Usado no Replay') or 0)
            principal_rem = round(float(row.get('Principal Remanescente') or 0.0), 2)
            valor_inicial = round(float(row.get('Valor Inicial') or 0.0), 2)
            lote = lotes_por_id.get(lote_id)
            saldo_liquido_ref = None if lote is None else round(float(lote.valor_liquido_hoje(data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
            sub = log[log['Lote'].astype(str) == lote_id].copy() if len(log) else log
            ultimo = sub.iloc[-1] if len(sub) else None
            liquido_total = round(float(sub['Liquido'].sum()), 2) if len(sub) else 0.0
            bruto_total = round(float(sub['Bruto'].sum()), 2) if len(sub) else 0.0
            saldo_pos_ultimo = round(float(ultimo['Saldo Remanescente']), 2) if ultimo is not None else saldo
            data_txt = ''
            conta_txt = ''
            if ultimo is not None:
                data_ult = ultimo['Data']
                data_txt = data_ult.isoformat() if hasattr(data_ult, 'isoformat') else str(data_ult)
                conta_txt = str(ultimo.get('Conta') or '')
            if situacao == 'nao_aportado_exaurido':
                origem = 'remanescente por rendimento histórico'
                leitura = 'o lote histórico marcado como exaurido ainda acumulou rendimento até o último uso; o resíduo não nasce do fechamento temporal global'
            elif saldo <= 0.10:
                origem = 'micro-saldo centesimal pós-saques'
                leitura = 'o saldo final é muito pequeno e compatível com efeito acumulado de conversão líquido→bruto e arredondamento monetário'
            else:
                origem = 'saldo residual após saque líquido-alvo'
                leitura = 'os saques cobriram exatamente as contas históricas informadas, mas preservaram um pequeno saldo bruto remanescente no lote'
            evid = f"usos={vezes_usado} | bruto sacado={bruto_total:.2f} | líquido sacado={liquido_total:.2f} | principal rem={principal_rem:.2f}"
            if ultimo is not None:
                evid += f" | último saque={data_txt} | saldo pós-último={saldo_pos_ultimo:.2f}"
            if saldo_liquido_ref is not None:
                evid += f" | líquido ref={saldo_liquido_ref:.2f}"
            if abs(liquido_total - valor_inicial) <= 0.01:
                leitura += '; o líquido total sacado ficou praticamente igual ao valor inicial do lote'
            linhas.append({
                'Tipo': 'micro-saldo',
                'Referência': lote_id,
                'Data': data_txt,
                'Conta': conta_txt,
                'Lote': lote_id,
                'Valor': saldo,
                'Status': _classificar_status_residuo(saldo, limiar),
                'Origem provável': origem,
                'Evidência-chave': evid,
                'Leitura': leitura,
            })

    linhas.sort(key=lambda item: (0 if item.get('Status') == 'pendente para validação' else 1, 0 if item.get('Tipo') == 'conta parcial' else 1, -float(item.get('Valor') or 0.0), str(item.get('Referência') or '')))
    return linhas


def _preparar_resumo_auditoria_detalhada_residuos(auditoria_detalhada, limiar):
    if not auditoria_detalhada:
        return [('limiar operacional de resolução', limiar)]
    resumo_origem: dict[str, int] = {}
    for item in auditoria_detalhada:
        chave = str(item.get('Origem provável') or 'não classificado')
        resumo_origem[chave] = resumo_origem.get(chave, 0) + 1
    pares = [
        ('limiar operacional de resolução', limiar),
        ('resíduos auditados', len(auditoria_detalhada)),
        ('resolvidos por limiar', sum(1 for item in auditoria_detalhada if item.get('Status') == 'resolvido por limiar')),
        ('pendentes para validação', sum(1 for item in auditoria_detalhada if item.get('Status') == 'pendente para validação')),
        ('contas parciais auditadas', sum(1 for item in auditoria_detalhada if item.get('Tipo') == 'conta parcial')),
        ('micro-saldos auditados', sum(1 for item in auditoria_detalhada if item.get('Tipo') == 'micro-saldo')),
    ]
    for chave, valor in sorted(resumo_origem.items(), key=lambda kv: (-kv[1], kv[0])):
        pares.append((f"origem: {chave}", valor))
    return pares



def _preparar_auditoria_recebimento_vs_aplicacao(dados_operacionais, replay_passado):
    """Compatibilidade temporária da camada de console.

    A V190 ainda não consome essa auditoria em nenhuma seção renderizada,
    mas o ponto de montagem continua sendo chamado no fluxo principal.
    Mantemos um preparador neutro para evitar quebra do console enquanto a
    camada observável é consolidada.
    """
    return []


def _render_secao_ranking_oficial(contexto_baseline, saida_canonica=None):
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    if ranking is None:
        return
    _imprimir_titulo('RANQUEAMENTO OFICIAL DA CARTEIRA')
    _imprimir_pares([
        ('produtos totais', ranking.resumo.get('produtos_total')),
        ('produtos ativos ranqueados', ranking.resumo.get('produtos_ativos_ranqueados')),
        ('destinos elegíveis de switching', ranking.auditoria.get('qtd_destinos_switch')),
        ('destino top 1', ranking.auditoria.get('destino_top1')),
        ('método', ranking.auditoria.get('metodo')),
        ('origem da amostra', 'saida_canonica_v202'),
    ])
    linhas = list(getattr(saida_canonica, 'ranking_amostra', []) or [])
    print('- amostra do ranking relevante do dia:')
    _imprimir_tabela(['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.', 'Status'], linhas, limite=10)


def _render_secao_switchings_oficiais(contexto_baseline, saida_canonica=None):
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    destino_top1 = ranking.auditoria.get('destino_top1') if ranking is not None else None
    linhas = list(getattr(saida_canonica, 'switchings', []) or [])[:10]
    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    _imprimir_pares([
        ('lotes avaliados para switching', len(linhas)),
        ('destinos elegíveis de switching', len(ranking.quadro_destinos_switch) if ranking is not None and isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame) else 0),
        ('switchings promovidos/executados', len(linhas)),
        ('destino top 1 do ranking', destino_top1),
        ('origem da amostra', 'saida_canonica_v202'),
    ])
    print('- amostra de switchings reais da janela (independente de pagamentos):')
    _imprimir_tabela(['Data', 'Lote origem', 'Produto origem', 'Destino', 'Ganho estimado', 'Status'], linhas, limite=10)


def main() -> None:


    contexto_baseline = carregar_contexto_baseline(
        raiz_repositorio=RAIZ_REPOSITORIO,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    pacote_config = contexto_baseline.pacote_config
    contexto = contexto_baseline.execucao
    calendario_financeiro = contexto_baseline.calendario_financeiro
    pacote_planilha = contexto_baseline.pacote_planilha
    carteira_canonica = contexto_baseline.carteira_canonica
    dados_operacionais = contexto_baseline.dados_operacionais
    cache_cdi = contexto_baseline.cache_cdi
    switching_shadow = contexto_baseline.switching_shadow
    triagem_motor = contexto_baseline.triagem_motor
    nucleo_financeiro = contexto_baseline.nucleo_financeiro
    replay_passado = contexto_baseline.replay_passado
    saida_canonica = construir_saida_canonica(contexto_baseline, versao=VERSAO_BASELINE)

    resumo_planilha = construir_resumo_planilha(pacote_planilha)
    resumo_por_aba = {item['nome_aba']: item for item in resumo_planilha}
    abas_cfg = pacote_config.conteudo.get('abas', {}) if isinstance(pacote_config.conteudo.get('abas'), dict) else {}
    abas_primarias = [
        ('carteira', abas_cfg.get('carteira', 'Carteira')),
        ('lotes', abas_cfg.get('lotes', 'Inventário de Lotes')),
        ('despesas', abas_cfg.get('despesas', 'Todos os Gastos')),
    ]
    nome_aba_carteira_real = getattr(carteira_canonica, 'nome_aba', abas_cfg.get('carteira', 'Carteira'))
    abas_primarias_reais = [
        ('carteira', nome_aba_carteira_real),
        ('lotes', abas_cfg.get('lotes', 'Inventário de Lotes')),
        ('despesas', abas_cfg.get('despesas', 'Todos os Gastos')),
    ]
    abas_auxiliares = [nome for nome in pacote_planilha.nomes_abas if nome not in {aba for _, aba in abas_primarias_reais}]
    exemplo_inicio = contexto.data_referencia.replace(day=1)
    dias_rendimento_mes = contar_dias_rendimento(exemplo_inicio - timedelta(days=1), contexto.data_referencia, calendario_financeiro, serie_cdi=cache_cdi.serie_cdi, data_fechamento_referencia=contexto.data_referencia)

    validacao_carteira = carteira_canonica.validacao or {}
    resumo_inventario = dados_operacionais.auditoria_inventario.get('resumo', {})
    validacao_inventario = dados_operacionais.auditoria_inventario.get('validacao', {})
    resumo_gastos = dados_operacionais.auditoria_gastos.get('resumo', {})
    validacao_gastos = dados_operacionais.auditoria_gastos.get('validacao', {})
    resumo_lotes_shadow = switching_shadow.auditoria_lotes_shadow or {}
    auditoria_eventos_shadow = switching_shadow.auditoria_eventos_aporte or {}
    reconciliacao_shadow = switching_shadow.reconciliacao_aportes or {}
    auditoria_triagem = triagem_motor.auditoria or {}
    contexto_triagem = auditoria_triagem.get('contexto', {})
    auditoria_nucleo = nucleo_financeiro.auditoria or {}
    validacao_nucleo = nucleo_financeiro.validacao or {}
    auditoria_cache_cdi = cache_cdi.auditoria or {}
    validacao_cache_cdi = cache_cdi.validacao or {}
    data_ultimo_fator_cdi = max(cache_cdi.serie_cdi.keys()) if cache_cdi.serie_cdi else None
    auditoria_replay = replay_passado.auditoria or {}
    validacao_replay = replay_passado.validacao or {}
    limiar_residuo_resolvido = obter_limiar_residuo_resolvido(pacote_config.conteudo)
    auditoria_residual_lotes = _preparar_auditoria_lotes_residuais(replay_passado, pacote_config.conteudo)
    auditoria_detalhada_residuos = _preparar_auditoria_detalhada_residuos(replay_passado, pacote_config.conteudo, contexto.data_referencia)
    auditoria_recebimento_aplicacao = _preparar_auditoria_recebimento_vs_aplicacao(dados_operacionais, replay_passado)
    auditoria_residual_lotes_resolvidos = [item for item in auditoria_residual_lotes if item.get('Status') == 'resolvido por limiar']
    auditoria_residual_lotes_pendentes = [item for item in auditoria_residual_lotes if item.get('Status') != 'resolvido por limiar']
    auditoria_detalhada_residuos_pendentes = [item for item in auditoria_detalhada_residuos if item.get('Status') != 'resolvido por limiar']

    resumo_detalhado_residuos = _preparar_resumo_auditoria_detalhada_residuos(auditoria_detalhada_residuos, limiar_residuo_resolvido)

    severidade_carteira = _severidade(erros=validacao_carteira.get('erros'), avisos=validacao_carteira.get('avisos'), condicao_ok=bool(validacao_carteira.get('ok', True)))
    severidade_inventario = _severidade(erros=validacao_inventario.get('erros'), avisos=validacao_inventario.get('avisos'), condicao_ok=bool(validacao_inventario.get('ok', True)))
    severidade_gastos = _severidade(erros=validacao_gastos.get('erros'), avisos=validacao_gastos.get('avisos'), condicao_ok=bool(validacao_gastos.get('ok', True)))
    severidade_abas = _severidade(condicao_ok=all(nome_aba in pacote_planilha.nomes_abas for _, nome_aba in abas_primarias_reais))
    severidade_dependencias = _severidade(avisos=contexto.relatorio_dependencias.get('ausentes', []), condicao_ok=len(contexto.relatorio_dependencias.get('ausentes', [])) == 0)
    severidade_lotes_shadow = _severidade(erros=['lote_id_duplicado'] if resumo_lotes_shadow.get('qtd_ids_duplicados', 0) > 0 else None, avisos=['existem_produtos_nao_reconhecidos_no_shadow'] if resumo_lotes_shadow.get('qtd_produto_nao_reconhecido', 0) > 0 else None, condicao_ok=len(switching_shadow.lotes_shadow) > 0)
    severidade_eventos_shadow = _severidade(erros=['reconciliacao_aportes_divergente'] if not bool(reconciliacao_shadow.get('equivalentes_essenciais', False)) else None, condicao_ok=len(switching_shadow.eventos_financeiros_ordenados) > 0)
    severidade_triagem = _severidade(avisos=['existem_produtos_ativos_fora_da_selecao_v1'] if auditoria_triagem.get('qtd_candidatos_motor_v1', 0) < auditoria_triagem.get('qtd_elegiveis_brutos', 0) else None, condicao_ok=auditoria_triagem.get('qtd_candidatos_motor_v1', 0) > 0)
    severidade_nucleo = _severidade(erros=validacao_nucleo.get('erros'), avisos=validacao_nucleo.get('avisos'), condicao_ok=bool(validacao_nucleo.get('ok', True)))
    severidade_cache_cdi = _severidade(erros=validacao_cache_cdi.get('erros'), avisos=validacao_cache_cdi.get('avisos'), condicao_ok=bool(validacao_cache_cdi.get('ok', True)))
    severidade_replay = _severidade(erros=validacao_replay.get('erros'), avisos=validacao_replay.get('avisos'), condicao_ok=bool(validacao_replay.get('ok', True)))

    render_secao_execucao(
        versao=VERSAO_BASELINE,
        pacote_config=pacote_config,
        pacote_planilha=pacote_planilha,
        contexto=contexto,
        severidade_dependencias=severidade_dependencias,
        auditoria_cache_cdi=auditoria_cache_cdi,
        data_ultimo_fator_cdi=data_ultimo_fator_cdi,
        dias_rendimento_mes=dias_rendimento_mes,
        resumo_por_aba=resumo_por_aba,
        abas_primarias_reais=abas_primarias_reais,
        abas_auxiliares=abas_auxiliares,
    )

    render_secao_amostras_pagamentos(
        pagamentos_realizados=saida_canonica.pagamentos_realizados_console(limite=5),
        pagamentos_proximos=saida_canonica.pagamentos_proximos_console(limite=5),
    )
    _render_secao_ranking_oficial(contexto_baseline, saida_canonica)
    _render_secao_switchings_oficiais(contexto_baseline, saida_canonica)

    resumo_fechamento_bruto = {
        item.get('Métrica'): item.get('Valor')
        for item in saida_canonica.fechamento_atual
    }
    mapeamento_fechamento = {
        'Data de referência': 'data_referencia',
        'Status do fechamento econômico': 'status_fechamento',
        'Fonte do fechamento': 'fonte_fechamento',
        'Fechamentos com fallback CDI': 'qtd_fechamentos_fallback_cdi',
        'Último fator explícito CDI': 'data_ultimo_fator_explicito_cdi',
        'Data confirmada da série': 'data_fechamento_confirmado',
        'Leitura auditável': 'observacao',
    }
    resumo_fechamento_situacao_atual = {
        chave: valor
        for chave, valor in resumo_fechamento_bruto.items()
        if chave is not None
    }
    for rotulo_humano, chave_tecnica in mapeamento_fechamento.items():
        if chave_tecnica not in resumo_fechamento_situacao_atual and rotulo_humano in resumo_fechamento_bruto:
            resumo_fechamento_situacao_atual[chave_tecnica] = resumo_fechamento_bruto.get(rotulo_humano)
    resumo_recebidos_saida = {
        item.get('Métrica'): item.get('Valor')
        for item in saida_canonica.resumo_recebidos
    }
    render_secao_situacao_atual(
        lotes_ativos=saida_canonica.lotes_ativos,
        lotes_exauridos=saida_canonica.lotes_exauridos,
        recebidos_atuais=saida_canonica.recebidos_atuais,
        resumo_fechamento=resumo_fechamento_situacao_atual,
        resumo_recebidos=resumo_recebidos_saida,
    )


if __name__ == '__main__':
    main()
