"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from typing import Iterable, Sequence

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from aplicacao.console.common import imprimir_itens_severidade as _imprimir_itens_severidade, imprimir_linha_status as _imprimir_linha_status, imprimir_pares as _imprimir_pares, imprimir_tabela as _imprimir_tabela, imprimir_titulo as _imprimir_titulo, normalizar_lista as _normalizar_lista, severidade as _severidade
from aplicacao.console.secoes_canonicas import render_secao_canonicas
from aplicacao.console.secoes_execucao import render_secao_execucao
from aplicacao.console.secoes_financeiras import render_secao_amostras_pagamentos, render_secao_nucleo, render_secao_replay, render_secao_situacao_atual
from aplicacao.console.secoes_triagem import render_secao_triagem
from nucleo.calendario_financeiro import contar_dias_rendimento
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha
from nucleo.contexto_baseline import carregar_contexto_baseline, obter_limiar_residuo_resolvido
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof
from nucleo.rotulagem_fechamento import resumir_fechamento_situacao_atual
from nucleo.utilitarios_neutros import normalizar_valores_situacao_atual_exaurida



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



def _preparar_tabela_lotes_situacao_atual(replay_passado, calendario_financeiro, config, data_referencia, *, serie_cdi=None):
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    limiar = obter_limiar_residuo_resolvido(config)
    lotes_ativos = []
    lotes_exauridos = []
    data_economica = data_referencia
    for lote in sorted(replay_passado.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        saldo_bruto = round(float(lote.valor_bruto_em_data(
            data_economica,
            calendario_financeiro,
            serie_cdi=serie_cdi,
            data_base_referencia=data_referencia,
        ) or 0.0), 2)
        saldo_liquido = round(float(lote.valor_liquido_em_data(
            data_economica,
            calendario_financeiro,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            serie_cdi=serie_cdi,
            data_base_referencia=data_referencia,
        ) or 0.0), 2)
        saldo_rem = round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2)
        dias_corridos = max((data_referencia - lote.data_recebimento).days, 0)
        dias_uteis = 0 if data_economica < lote.data_aplicacao else contar_dias_rendimento(
            lote.data_base_fiscal,
            data_economica,
            calendario_financeiro,
            serie_cdi=serie_cdi,
            data_fechamento_referencia=data_economica,
        )
        lote_exaurido_na_situacao = bool(lote.esgotado or saldo_bruto <= limiar)
        saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao = normalizar_valores_situacao_atual_exaurida(
            saldo_bruto=saldo_bruto,
            saldo_liquido=saldo_liquido,
            saldo_rem=saldo_rem,
            exaurido=lote_exaurido_na_situacao,
        )
        linha = {
            'Recebimento': lote.data_recebimento.isoformat() if hasattr(lote.data_recebimento, 'isoformat') else str(lote.data_recebimento),
            'Aplicação': lote.data_aplicacao.isoformat() if hasattr(lote.data_aplicacao, 'isoformat') else str(lote.data_aplicacao),
            'Produto': lote.investimento,
            'Valor original': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Bruto': saldo_bruto_exibicao,
            'Líquido': saldo_liquido_exibicao,
            'Saldo rem': saldo_rem_exibicao,
            'Lote': lote.id,
        }
        if lote_exaurido_na_situacao:
            lotes_exauridos.append(linha)
        else:
            lotes_ativos.append(linha)
    return lotes_ativos, lotes_exauridos


def _preparar_tabela_recebidos_situacao_atual(recebidos_auditaveis):
    quadro = recebidos_auditaveis.quadro_recebidos_auditaveis.copy()
    if len(quadro) == 0:
        return []
    quadro = quadro.sort_values(by=['data_recebimento', 'lote_id_origem', 'recebido_id'], kind='stable').reset_index(drop=True)
    linhas = []
    for _, row in quadro.iterrows():
        linhas.append({
            'Recebido': row.get('recebido_id'),
            'Lote origem': row.get('lote_id_origem'),
            'Recebimento': row.get('data_recebimento').isoformat() if hasattr(row.get('data_recebimento'), 'isoformat') else str(row.get('data_recebimento') or ''),
            'Aplicação': row.get('data_aplicacao').isoformat() if hasattr(row.get('data_aplicacao'), 'isoformat') else str(row.get('data_aplicacao') or ''),
            'Valor bruto': round(float(row.get('valor_bruto') or 0.0), 2),
            'Valor líquido': round(float(row.get('valor_liquido') or 0.0), 2),
            'Status': row.get('status_recebido'),
            'Destino': row.get('destino_potencial'),
            'Pagamentos vinculados': int(row.get('qtd_pagamentos_vinculados') or 0),
            'Valor vinculado': round(float(row.get('valor_total_vinculado') or 0.0), 2),
            'Residual aplicação': round(float(row.get('valor_residual_para_aplicacao_origem') or 0.0), 2),
            'Disponível ref': 'sim' if bool(row.get('disponivel_na_data_referencia', False)) else 'não',
            'Observação': row.get('observacao_auditavel') or '',
        })
    return linhas


def main() -> None:
    contexto_baseline = carregar_contexto_baseline(raiz_repositorio=RAIZ_REPOSITORIO, instalar_automaticamente=False)
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

    render_secao_canonicas(
        carteira_canonica=carteira_canonica,
        dados_operacionais=dados_operacionais,
        switching_shadow=switching_shadow,
        severidade_carteira=severidade_carteira,
        severidade_inventario=severidade_inventario,
        severidade_gastos=severidade_gastos,
        severidade_lotes_shadow=severidade_lotes_shadow,
        severidade_eventos_shadow=severidade_eventos_shadow,
        severidade_triagem=severidade_triagem,
        severidade_nucleo=severidade_nucleo,
        resumo_inventario=resumo_inventario,
        resumo_gastos=resumo_gastos,
        validacao_carteira=validacao_carteira,
        validacao_inventario=validacao_inventario,
        validacao_gastos=validacao_gastos,
        resumo_lotes_shadow=resumo_lotes_shadow,
        auditoria_eventos_shadow=auditoria_eventos_shadow,
        reconciliacao_shadow=reconciliacao_shadow,
        auditoria_triagem=auditoria_triagem,
        auditoria_nucleo=auditoria_nucleo,
    )

    render_secao_nucleo(
        auditoria_nucleo=auditoria_nucleo,
        validacao_nucleo=validacao_nucleo,
        severidade_nucleo=severidade_nucleo,
    )

    render_secao_replay(
        auditoria_replay=auditoria_replay,
        validacao_replay=validacao_replay,
        severidade_replay=severidade_replay,
        limiar_residuo_resolvido=limiar_residuo_resolvido,
    )

    render_secao_triagem(
        auditoria_triagem=auditoria_triagem,
        contexto_triagem=contexto_triagem,
        severidade_triagem=severidade_triagem,
    )

    pagamentos_realizados_console, pagamentos_proximos_console = _preparar_amostras_pagamentos_console(dados_operacionais, replay_passado, limite=5)
    render_secao_amostras_pagamentos(
        pagamentos_realizados=pagamentos_realizados_console,
        pagamentos_proximos=pagamentos_proximos_console,
    )

    lotes_ativos, lotes_exauridos = _preparar_tabela_lotes_situacao_atual(replay_passado, calendario_financeiro, pacote_config.conteudo, contexto.data_referencia, serie_cdi=cache_cdi.serie_cdi)
    recebidos_situacao_atual = _preparar_tabela_recebidos_situacao_atual(contexto_baseline.recebidos_auditaveis)
    resumo_fechamento_situacao_atual = resumir_fechamento_situacao_atual(
        data_referencia=contexto.data_referencia,
        calendario_financeiro=calendario_financeiro,
        serie_cdi=cache_cdi.serie_cdi,
    )
    render_secao_situacao_atual(
        lotes_ativos=lotes_ativos,
        lotes_exauridos=lotes_exauridos,
        recebidos_atuais=recebidos_situacao_atual,
        resumo_fechamento=resumo_fechamento_situacao_atual,
        resumo_recebidos=contexto_baseline.recebidos_auditaveis.auditoria.get('resumo', {}),
    )




def _preparar_amostras_pagamentos_console(dados_operacionais, replay_passado, *, limite=5):
    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(gastos) == 0:
        return [], []

    gastos['data'] = pd.to_datetime(gastos['data'], errors='coerce').dt.date

    log = replay_passado.log_passado.copy()
    agregados_replay = {}
    if len(log):
        log['Data'] = pd.to_datetime(log['Data'], errors='coerce').dt.date
        for despesa_id, grupo in log.groupby('Despesa ID', sort=False):
            lotes = [str(v).strip() for v in grupo['Lote'].tolist() if str(v).strip()]
            lotes_unicos = []
            vistos = set()
            for lote in lotes:
                if lote not in vistos:
                    vistos.add(lote)
                    lotes_unicos.append(lote)
            data_pagamento = grupo['Data'].dropna().max() if 'Data' in grupo.columns else None
            descricao = str(grupo.iloc[-1].get('Conta') or '').strip()
            valor_pagamento = round(float(grupo['Valor Conta'].dropna().iloc[-1]), 2) if grupo['Valor Conta'].dropna().shape[0] else None
            liquido_coberto = round(float(grupo['Liquido'].fillna(0.0).sum()), 2)
            agregados_replay[str(despesa_id)] = {
                'Data': data_pagamento.isoformat() if hasattr(data_pagamento, 'isoformat') else (str(data_pagamento) if data_pagamento is not None else ''),
                'Despesa ID': str(despesa_id),
                'Descrição': descricao,
                'Valor': valor_pagamento,
                'Líquido coberto': liquido_coberto,
                'Lotes usados': ' | '.join(lotes_unicos),
            }

    realizados = gastos.loc[gastos['passado_pago_ate_data_referencia'].fillna(False)].copy()
    realizados = realizados.sort_values(['data', 'despesa_id'], ascending=[False, False], kind='stable')
    linhas_realizados = []
    for _, row in realizados.iterrows():
        despesa_id = str(row.get('despesa_id') or '').strip()
        base = agregados_replay.get(despesa_id, {})
        lotes_informados = [str(row.get('lote_usado_1') or '').strip(), str(row.get('lote_usado_2') or '').strip()]
        lotes_informados = [item for item in lotes_informados if item]
        linhas_realizados.append({
            'Data': base.get('Data') or (row['data'].isoformat() if hasattr(row['data'], 'isoformat') else str(row.get('data') or '')),
            'Despesa ID': despesa_id,
            'Descrição': base.get('Descrição') or str(row.get('descricao') or ''),
            'Valor': base.get('Valor') if base.get('Valor') is not None else round(float(row.get('valor') or 0.0), 2),
            'Líquido coberto': base.get('Líquido coberto') if base.get('Líquido coberto') is not None else '',
            'Lotes usados': base.get('Lotes usados') or (' | '.join(lotes_informados)),
        })
        if len(linhas_realizados) >= limite:
            break

    proximos = gastos.loc[gastos['futuro_ou_pendente_na_data_referencia'].fillna(False)].copy()
    proximos = proximos.sort_values(['data', 'despesa_id'], ascending=[True, True], kind='stable')
    linhas_proximos = []
    for _, row in proximos.iterrows():
        lotes_informados = [str(row.get('lote_usado_1') or '').strip(), str(row.get('lote_usado_2') or '').strip()]
        lotes_informados = [item for item in lotes_informados if item]
        linhas_proximos.append({
            'Data': row['data'].isoformat() if hasattr(row['data'], 'isoformat') else str(row.get('data') or ''),
            'Despesa ID': str(row.get('despesa_id') or ''),
            'Descrição': str(row.get('descricao') or ''),
            'Valor': round(float(row.get('valor') or 0.0), 2),
            'Lotes informados': ' | '.join(lotes_informados),
        })
        if len(linhas_proximos) >= limite:
            break

    return linhas_realizados, linhas_proximos

def _preparar_auditoria_recebimento_vs_aplicacao(dados_operacionais, replay_passado):
    inventario = dados_operacionais.inventario_canonico.copy()
    if len(inventario) == 0:
        return []
    janela = inventario[inventario['data_recebimento'] < inventario['data_aplicacao']].copy()
    if len(janela) == 0:
        return []
    log = replay_passado.log_passado.copy()
    inconsistencias = pd.DataFrame((replay_passado.auditoria or {}).get('amostra_inconsistencias') or [])
    linhas = []
    for _, row in janela.sort_values(by=['data_recebimento', 'lote_id'], kind='stable').iterrows():
        lote_id = str(row.get('lote_id') or '')
        sub = log[log['Lote'].astype(str) == lote_id].copy() if len(log) else log
        for _, mov in sub.iterrows():
            data_evt = mov.get('Data')
            fase = 'caixa_pre_aplicacao' if row['data_recebimento'] <= data_evt <= row['data_aplicacao'] else 'aplicado'
            linhas.append({
                'Lote': lote_id,
                'Recebimento': row['data_recebimento'].isoformat() if hasattr(row['data_recebimento'], 'isoformat') else str(row['data_recebimento']),
                'Aplicação': row['data_aplicacao'].isoformat() if hasattr(row['data_aplicacao'], 'isoformat') else str(row['data_aplicacao']),
                'Data evento': data_evt.isoformat() if hasattr(data_evt, 'isoformat') else str(data_evt),
                'Conta': mov.get('Conta') or '',
                'Fase': fase,
                'Bruto': mov.get('Bruto'),
                'Líquido': mov.get('Liquido'),
                'Saldo rem.': mov.get('Saldo Remanescente'),
                'Leitura': 'caixa sem rendimento' if fase == 'caixa_pre_aplicacao' else 'lote aplicado com rendimento',
            })
        if len(inconsistencias):
            sub_inc = inconsistencias[inconsistencias['lotes_informados'].astype(str).str.contains(lote_id, na=False, regex=False)] if 'lotes_informados' in inconsistencias.columns else inconsistencias.iloc[0:0]
            for _, inc in sub_inc.iterrows():
                data_inc = inc.get('data')
                if hasattr(data_inc, 'isoformat'):
                    data_inc = data_inc.isoformat()
                linhas.append({
                    'Lote': lote_id,
                    'Recebimento': row['data_recebimento'].isoformat() if hasattr(row['data_recebimento'], 'isoformat') else str(row['data_recebimento']),
                    'Aplicação': row['data_aplicacao'].isoformat() if hasattr(row['data_aplicacao'], 'isoformat') else str(row['data_aplicacao']),
                    'Data evento': data_inc,
                    'Conta': inc.get('descricao') or '',
                    'Fase': 'inconsistência',
                    'Bruto': '',
                    'Líquido': inc.get('valor_restante'),
                    'Saldo rem.': '',
                    'Leitura': inc.get('motivo') or '',
                })
    return linhas

if __name__ == '__main__':
    main()
