"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from copy import deepcopy
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
from aplicacao.console.secoes_financeiras import render_secao_amostras_pagamentos, render_secao_auditoria_temporal_pagamentos, render_secao_heuristica_conjunta_parcial, render_secao_metodo_pagamentos, render_secao_nucleo, render_secao_planejamento_conjunto_local, render_secao_reescolha_dinamica_pagamentos, render_secao_replay, render_secao_situacao_atual, render_secao_microplanejamento_conjunto_v2, render_secao_recomputacao_sequencial_central_v1, render_secao_motor_recomendacao_pagamentos_switching_v1
from aplicacao.console.secoes_triagem import render_secao_triagem
from nucleo.calendario_financeiro import contar_dias_rendimento, proximo_dia_util_bancario_em_ou_apos
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.leitor_planilha import construir_resumo_planilha
from nucleo.contexto_baseline import carregar_contexto_baseline, obter_limiar_residuo_resolvido
from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof, executar_saque_lote
from nucleo.rotulagem_fechamento import resumir_fechamento_situacao_atual
from nucleo.caixa_recebidos_auditaveis import auditar_comparativo_proxy_v2_v3
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
    log = getattr(replay_passado, 'log_passado', None)

    def _ultimo_uso_lote(lote_id):
        if not isinstance(log, pd.DataFrame) or len(log) == 0 or 'Lote' not in log.columns:
            return ''
        sub = log[log['Lote'].fillna('').astype(str) == str(lote_id)]
        if len(sub) == 0:
            return ''
        data_ult = sub['Data'].max() if 'Data' in sub.columns else None
        return data_ult.isoformat() if hasattr(data_ult, 'isoformat') else str(data_ult or '')

    for lote in sorted(replay_passado.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        if lote.data_recebimento > data_referencia or lote.data_aplicacao > data_referencia:
            continue
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
        ultimo_uso_txt = _ultimo_uso_lote(lote.id)
        data_base_tempo = data_referencia
        if ultimo_uso_txt:
            try:
                data_base_tempo = date.fromisoformat(str(ultimo_uso_txt))
            except Exception:
                data_base_tempo = data_referencia
        dias_corridos = max((data_base_tempo - lote.data_recebimento).days, 0)
        dias_uteis = 0 if data_base_tempo < lote.data_aplicacao else contar_dias_rendimento(
            lote.data_base_fiscal,
            data_base_tempo,
            calendario_financeiro,
            serie_cdi=serie_cdi,
            data_fechamento_referencia=min(data_economica, data_base_tempo),
        )
        lote_exaurido_na_situacao = bool(
            lote.esgotado
            or saldo_bruto <= limiar
            or saldo_liquido <= limiar
            or saldo_rem <= limiar
        )
        saldo_bruto_exibicao, saldo_liquido_exibicao, saldo_rem_exibicao = normalizar_valores_situacao_atual_exaurida(
            saldo_bruto=saldo_bruto,
            saldo_liquido=saldo_liquido,
            saldo_rem=saldo_rem,
            exaurido=lote_exaurido_na_situacao,
        )
        linha = {
            'Lote': lote.id,
            'Recebimento': lote.data_recebimento.isoformat() if hasattr(lote.data_recebimento, 'isoformat') else str(lote.data_recebimento),
            'Aplicação': lote.data_aplicacao.isoformat() if hasattr(lote.data_aplicacao, 'isoformat') else str(lote.data_aplicacao),
            'Último uso': ultimo_uso_txt,
            'Produto': lote.investimento,
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Valor original': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'Bruto': saldo_bruto_exibicao,
            'Líquido': saldo_liquido_exibicao,
            'Saldo rem': saldo_rem_exibicao,
        }
        if lote_exaurido_na_situacao:
            lotes_exauridos.append(linha)
        else:
            lotes_ativos.append(linha)
    lotes_exauridos.sort(key=lambda item: (str(item.get('Último uso') or ''), str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
    lotes_ativos.sort(key=lambda item: (str(item.get('Aplicação') or ''), str(item.get('Lote') or '')), reverse=True)
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





def _preparar_auditoria_recebimento_vs_aplicacao(dados_operacionais, replay_passado):
    """Compatibilidade temporária da camada de console.

    A V190 ainda não consome essa auditoria em nenhuma seção renderizada,
    mas o ponto de montagem continua sendo chamado no fluxo principal.
    Mantemos um preparador neutro para evitar quebra do console enquanto a
    camada observável é consolidada.
    """
    return []


def _valor_monetario_preferencial(*valores):
    for v in valores:
        if v is None or v == '':
            continue
        try:
            return round(float(v), 2)
        except Exception:
            continue
    return ''


def _mapa_pagamentos_central(contexto_baseline):
    mapa = {}
    pacote = getattr(contexto_baseline, 'recomputacao_sequencial_central_v1', None)
    quadro = getattr(pacote, 'quadro_recomputacao_sequencial_central', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _ultimo_fator_cache_cdi(contexto_baseline):
    serie = getattr(getattr(contexto_baseline, 'cache_cdi', None), 'serie_cdi', {}) or {}
    if not serie:
        return 1.0, None
    try:
        data_ult = max(serie.keys())
        fator = float(serie.get(data_ult) or 1.0)
        return fator if fator > 0 else 1.0, data_ult
    except Exception:
        return 1.0, None


def _mapa_saldo_disponivel(contexto_baseline):
    mapa = {}
    pacote = getattr(contexto_baseline, 'saldo_disponivel_geral', None)
    quadro = getattr(pacote, 'quadro_saldo_disponivel', None) if pacote is not None else None
    if isinstance(quadro, pd.DataFrame) and len(quadro):
        for _, row in quadro.iterrows():
            mapa[str(row.get('pagamento_id') or '').strip()] = row.to_dict()
    return mapa


def _mapa_saldos_correntes_lotes(contexto_baseline):
    replay = getattr(contexto_baseline, 'replay_passado', None)
    lotes = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    ctx = contexto_baseline.execucao
    cal = contexto_baseline.calendario_financeiro
    serie = getattr(getattr(contexto_baseline, 'cache_cdi', None), 'serie_cdi', None)
    tabela_iof = contexto_baseline.tabela_iof
    faixas_ir = contexto_baseline.faixas_ir
    mapa = {}
    for lote in lotes:
        try:
            bruto = round(float(lote.valor_bruto_em_data(ctx.data_referencia, cal, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_em_data(ctx.data_referencia, cal, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie, data_base_referencia=ctx.data_referencia) or 0.0), 2)
        except Exception:
            bruto = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            liquido = round(float(lote.valor_liquido_hoje(ctx.data_referencia, tabela_iof=tabela_iof, faixas_ir=faixas_ir) or 0.0), 2)
        mapa[str(lote.id)] = {'bruto': bruto, 'liquido': liquido, 'saldo_rem': round(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 2)}
    return mapa


def _avancar_lote_para_data(lote, data_origem, data_alvo, contexto_baseline):
    if data_alvo is None or data_origem is None or data_alvo <= data_origem:
        return
    fator_dia, _ = _ultimo_fator_cache_cdi(contexto_baseline)
    taxa_diaria = max(float(fator_dia) - 1.0, 0.0)
    data_cursor = data_origem
    while data_cursor < data_alvo:
        data_cursor = data_cursor + timedelta(days=1)
        lote.atualizar_juros(
            data_cursor,
            taxa_diaria,
            contexto_baseline.calendario_financeiro,
            serie_cdi=None,
            data_fechamento_referencia=data_cursor,
        )


def _mapa_resumos_futuros_operacionais(contexto_baseline, quadro_futuro):
    if not isinstance(quadro_futuro, pd.DataFrame) or len(quadro_futuro) == 0:
        return {}
    tabela_iof = contexto_baseline.tabela_iof
    faixas_ir = contexto_baseline.faixas_ir
    replay = getattr(contexto_baseline, 'replay_passado', None)
    lotes_orig = getattr(replay, 'lotes_apos_replay', []) if replay is not None else []
    lotes_estado = {str(l.id): deepcopy(l) for l in lotes_orig}
    lotes_data = {str(l.id): contexto_baseline.execucao.data_referencia for l in lotes_orig}
    saldo_map = _mapa_saldo_disponivel(contexto_baseline)
    saldos_correntes = _mapa_saldos_correntes_lotes(contexto_baseline)
    consumo_saldo = 0.0
    resumos = {}
    quadro = quadro_futuro.copy().sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    for _, row in quadro.iterrows():
        pagamento_id = str(row.get('pagamento_id') or '').strip()
        data_pag = row.get('data_pagamento')
        valor = round(float(row.get('valor_pagamento') or 0.0), 2)
        lote_sug = str(row.get('lote_recomendado') or row.get('lote_id_escolhido') or row.get('fonte_base_escolhida') or row.get('tipo_fonte_escolhida') or '')
        resumo = {'Lote sugerido': lote_sug, 'Saldo Antes': '', 'Bruto': '', 'Imposto': '', 'Líquido': '', 'Saldo Remanescente': ''}
        if lote_sug in lotes_estado and data_pag is not None:
            lote = lotes_estado[lote_sug]
            corrente = saldos_correntes.get(lote_sug, {})
            saldo_corrente_bruto = round(float(corrente.get('bruto') or 0.0), 2)
            fator_atual = max(float(getattr(lote, 'fator_acumulado', 1.0) or 1.0), 1.0)
            principal = max(float(getattr(lote, 'principal_remanescente', 0.0) or 0.0), 0.0)
            if saldo_corrente_bruto > 0:
                lote.saldo_bruto = saldo_corrente_bruto
                if principal > 0:
                    lote.fator_acumulado = max(saldo_corrente_bruto / principal, fator_atual)
            _avancar_lote_para_data(lote, lotes_data.get(lote_sug, contexto_baseline.execucao.data_referencia), data_pag, contexto_baseline)
            lotes_data[lote_sug] = data_pag
            saldo_antes = round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0), 2)
            mov = executar_saque_lote(lote, valor, data_pag, tabela_iof=tabela_iof, faixas_ir=faixas_ir)
            if mov is not None:
                saldo_rem = round(float(mov.get('saldo_remanescente') or 0.0), 2)
                if saldo_rem <= obter_limiar_residuo_resolvido(contexto_baseline.pacote_config.conteudo):
                    saldo_rem = 0.0
                resumo = {
                    'Lote sugerido': lote_sug,
                    'Saldo Antes': round(float(mov.get('saldo_antes') or saldo_antes), 2),
                    'Bruto': round(float(mov.get('bruto') or 0.0), 2),
                    'Imposto': round(float(mov.get('imposto') or 0.0), 2),
                    'Líquido': round(float(mov.get('liquido') or 0.0), 2),
                    'Saldo Remanescente': saldo_rem,
                }
        elif lote_sug == 'saldo_disponivel_geral':
            base = saldo_map.get(pagamento_id, {})
            saldo_base = round(float(base.get('saldo_disponivel_bruto') or base.get('saldo_disponivel_liquido') or 0.0), 2)
            saldo_antes = max(round(saldo_base - consumo_saldo, 2), 0.0)
            bruto = min(valor, saldo_antes)
            imposto = 0.0
            liquido = bruto
            saldo_rem = max(round(saldo_antes - liquido, 2), 0.0)
            consumo_saldo = round(consumo_saldo + liquido, 2)
            resumo = {
                'Lote sugerido': lote_sug,
                'Saldo Antes': saldo_antes,
                'Bruto': bruto,
                'Imposto': imposto,
                'Líquido': liquido,
                'Saldo Remanescente': saldo_rem,
            }
        resumos[pagamento_id] = resumo
    return resumos


def _resumo_financeiro_futuro_console(contexto_baseline, pagamento_id, decisao_row, mapa_resumos=None):
    mapa_resumos = mapa_resumos or {}
    resumo = mapa_resumos.get(str(pagamento_id or '').strip())
    if resumo:
        return resumo
    central = _mapa_pagamentos_central(contexto_baseline).get(str(pagamento_id or '').strip(), {})
    if central:
        return {
            'Saldo Antes': _valor_monetario_preferencial(central.get('saldo_antes_central')),
            'Bruto': _valor_monetario_preferencial(central.get('bruto_central')),
            'Imposto': _valor_monetario_preferencial(central.get('imposto_central')),
            'Líquido': _valor_monetario_preferencial(central.get('liquido_central')),
            'Saldo Remanescente': _valor_monetario_preferencial(central.get('saldo_remanescente_central')),
            'Lote sugerido': central.get('lote_final_central') or central.get('lote_sugerido_original') or '',
        }
    return {
        'Saldo Antes': '',
        'Bruto': '',
        'Imposto': '',
        'Líquido': '',
        'Saldo Remanescente': '',
        'Lote sugerido': decisao_row.get('lote_recomendado') or decisao_row.get('lote_id_escolhido') or decisao_row.get('fonte_base_escolhida') or decisao_row.get('tipo_fonte_escolhida') or '',
    }


def _ranking_destino_para_lote(contexto_baseline, lote):
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    if ranking is None or not isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame):
        return None
    destinos = ranking.quadro_destinos_switch.copy()
    if len(destinos) == 0:
        return None
    origem_key = str(getattr(lote, 'produto_key', '') or '').strip()
    if 'produto_key' in destinos.columns:
        destinos = destinos[destinos['produto_key'].fillna('').astype(str).str.strip() != origem_key]
    status_col = 'Status_Confirmação' if 'Status_Confirmação' in destinos.columns else ('status_confirmacao' if 'status_confirmacao' in destinos.columns else None)
    if status_col is not None:
        destinos = destinos[destinos[status_col].fillna('').astype(str).isin(['', 'Confirmado', 'confirmado', 'Fortemente sustentado'])]
    if 'elegivel_switch_in' in destinos.columns:
        destinos = destinos[destinos['elegivel_switch_in'].fillna(False).astype(bool)]
    valor_liquido = round(float(lote.valor_liquido_hoje(contexto_baseline.execucao.data_referencia, tabela_iof=contexto_baseline.tabela_iof, faixas_ir=contexto_baseline.faixas_ir) or 0.0), 2)
    if 'aplicacao_minima' in destinos.columns:
        elegiveis = destinos[destinos['aplicacao_minima'].fillna(0.0).astype(float) <= valor_liquido + 1e-9]
        if len(elegiveis):
            destinos = elegiveis
    if len(destinos) == 0:
        return None
    if 'rank_destino' in destinos.columns:
        destinos = destinos.sort_values(['rank_destino', 'score_final', 'nome'], ascending=[True, False, True], kind='stable')
    else:
        destinos = destinos.sort_values(['score_final', 'nome'], ascending=[False, True], kind='stable')
    return destinos.iloc[0].to_dict()


def _data_sugerida_switching_lote(contexto_baseline, lote):
    carteira = getattr(contexto_baseline, 'carteira_canonica', None)
    mapa = getattr(carteira, 'mapa_produtos', {}) if carteira is not None else {}
    meta = ((mapa.get('by_key') or {}).get(getattr(lote, 'produto_key', None)) or {}) if isinstance(mapa, dict) else {}
    prazo = int(meta.get('prazo_dias') or 0)
    data_base = getattr(lote, 'carencia_ate', None) or contexto_baseline.execucao.data_referencia
    if prazo > 0:
        base = lote.data_aplicacao + timedelta(days=prazo)
        try:
            return proximo_dia_util_bancario_em_ou_apos(base, contexto_baseline.calendario_financeiro)
        except Exception:
            return base
    return data_base


def _montar_switchings_oficiais(contexto_baseline, limite=10):
    shadow = getattr(contexto_baseline, 'switching_economico_shadow', None)
    plano = getattr(shadow, 'plano_shadow', None) if shadow is not None else None
    linhas = []
    lotes_by_id = {str(l.id): l for l in (getattr(getattr(contexto_baseline, 'replay_passado', None), 'lotes_apos_replay', []) or [])}
    if isinstance(plano, pd.DataFrame) and len(plano):
        plano_f = plano.copy()
        if 'recomendado_shadow' in plano_f.columns:
            plano_f = plano_f[plano_f['recomendado_shadow'].fillna(False)]
        plano_f = plano_f.sort_values(['ganho_liquido_estimado','score_switch_shadow','lote_id'], ascending=[False,False,True], kind='stable')
        usados = set()
        for _, row in plano_f.iterrows():
            lote_id = str(row.get('lote_id') or '')
            if not lote_id or lote_id in usados:
                continue
            lote = lotes_by_id.get(lote_id)
            if lote is None:
                continue
            destino_rank = _ranking_destino_para_lote(contexto_baseline, lote) or {}
            data_sug = _data_sugerida_switching_lote(contexto_baseline, lote) if lote is not None else contexto_baseline.execucao.data_referencia
            destino_nome = destino_rank.get('nome') or ''
            ganho = row.get('ganho_liquido_estimado')
            try:
                ganho = round(float(ganho), 2)
            except Exception:
                ganho = round(float(destino_rank.get('proxy_terminal_destino') or 0.0), 2)
            linhas.append({
                'Data': data_sug.isoformat() if hasattr(data_sug, 'isoformat') else data_sug,
                'Lote origem': lote_id,
                'Produto origem': getattr(lote, 'investimento', '') if lote is not None else row.get('produto_origem_nome') or '',
                'Destino': destino_nome,
                'Ganho estimado': ganho,
                'Status': 'destino ranqueado elegível',
            })
            usados.add(lote_id)
            if len(linhas) >= limite:
                break
    return linhas


def _preparar_amostras_pagamentos_console(dados_operacionais, replay_passado, decisao_local_v1, contexto_baseline, limite=5):
    import pandas as pd

    pagamentos_realizados = []
    pagamentos_proximos = []

    log = getattr(replay_passado, 'log_passado', None)
    if isinstance(log, pd.DataFrame) and len(log):
        quadro = log.copy()
        chave = 'Despesa ID' if 'Despesa ID' in quadro.columns else None
        if chave is not None:
            quadro['_ordem'] = range(len(quadro))
            agreg = (
                quadro.sort_values(['Data', '_ordem'], kind='stable')
                .groupby(chave, dropna=False, sort=False)
                .agg({
                    'Data': 'last',
                    'Conta': 'last' if 'Conta' in quadro.columns else 'first',
                    'Liquido': 'sum' if 'Liquido' in quadro.columns else 'first',
                    'Bruto': 'sum' if 'Bruto' in quadro.columns else 'first',
                    'Imposto': 'sum' if 'Imposto' in quadro.columns else 'first',
                    'Saldo Antes': 'first' if 'Saldo Antes' in quadro.columns else 'last',
                    'Saldo Remanescente': 'last' if 'Saldo Remanescente' in quadro.columns else 'first',
                    'Lote': lambda s: ' + '.join(dict.fromkeys([str(x) for x in s if str(x).strip()])) if 'Lote' in quadro.columns else '',
                })
                .reset_index(drop=True)
            )
        else:
            agreg = quadro.copy()
            if 'Conta' not in agreg.columns:
                agreg['Conta'] = ''
            if 'Liquido' not in agreg.columns:
                agreg['Liquido'] = 0.0
            if 'Bruto' not in agreg.columns:
                agreg['Bruto'] = agreg['Liquido']
            if 'Imposto' not in agreg.columns:
                agreg['Imposto'] = 0.0
            if 'Saldo Antes' not in agreg.columns:
                agreg['Saldo Antes'] = None
            if 'Saldo Remanescente' not in agreg.columns:
                agreg['Saldo Remanescente'] = None
            if 'Lote' not in agreg.columns:
                agreg['Lote'] = ''
        agreg = agreg.sort_values('Data', ascending=False, kind='stable').head(limite)
        for _, row in agreg.iterrows():
            data = row.get('Data')
            pagamentos_realizados.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else data,
                'Descrição': row.get('Conta') or '',
                'Valor': round(float(row.get('Liquido') or 0.0), 2),
                'Lotes usados': row.get('Lote') or '',
                'Saldo Antes': round(float(row.get('Saldo Antes') or 0.0), 2) if row.get('Saldo Antes') is not None else None,
                'Bruto': round(float(row.get('Bruto') or 0.0), 2),
                'Imposto': round(float(row.get('Imposto') or 0.0), 2),
                'Líquido': round(float(row.get('Liquido') or 0.0), 2),
                'Saldo Remanescente': (0.0 if round(float(row.get('Saldo Remanescente') or 0.0), 2) <= obter_limiar_residuo_resolvido(contexto_baseline.pacote_config.conteudo) else round(float(row.get('Saldo Remanescente') or 0.0), 2)) if row.get('Saldo Remanescente') is not None else None,
            })

    quadro_futuro = None
    motor = getattr(contexto_baseline, 'motor_recomendacao_pagamentos_switching_v1', None)
    if motor is not None and hasattr(motor, 'quadro_recomendacoes'):
        quadro_futuro = motor.quadro_recomendacoes.copy()
        if len(quadro_futuro):
            quadro_futuro = quadro_futuro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable')
    if quadro_futuro is None or not len(quadro_futuro):
        quadro_futuro = getattr(decisao_local_v1, 'quadro_decisao_local_v1', None)
        if isinstance(quadro_futuro, pd.DataFrame) and len(quadro_futuro):
            quadro_futuro = quadro_futuro.sort_values(['data_pagamento', 'pagamento_id'], kind='stable')

    mapa_resumos_futuros = _mapa_resumos_futuros_operacionais(contexto_baseline, quadro_futuro) if isinstance(quadro_futuro, pd.DataFrame) else {}
    if isinstance(quadro_futuro, pd.DataFrame) and len(quadro_futuro):
        for _, row in quadro_futuro.head(limite).iterrows():
            data = row.get('data_pagamento')
            valor = round(float(row.get('valor_pagamento') or 0.0), 2)
            pagamento_id = row.get('pagamento_id')
            resumo = _resumo_financeiro_futuro_console(contexto_baseline, pagamento_id, row, mapa_resumos=mapa_resumos_futuros)
            pagamentos_proximos.append({
                'Data': data.isoformat() if hasattr(data, 'isoformat') else data,
                'Descrição': row.get('descricao_pagamento') or '',
                'Valor': valor,
                'Lote sugerido': resumo.get('Lote sugerido') or '',
                'Saldo Antes': resumo.get('Saldo Antes', ''),
                'Bruto': resumo.get('Bruto', ''),
                'Imposto': resumo.get('Imposto', ''),
                'Líquido': resumo.get('Líquido', ''),
                'Saldo Remanescente': resumo.get('Saldo Remanescente', ''),
            })

    return pagamentos_realizados, pagamentos_proximos


def _render_secao_ranking_oficial(contexto_baseline):
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
    ])
    destinos = ranking.quadro_destinos_switch.copy()
    linhas = []
    for _, row in destinos.head(10).iterrows():
        linhas.append({
            'Rank': row.get('rank_destino'),
            'Produto': row.get('nome'),
            'Score': row.get('score_final'),
            'Proxy terminal': row.get('proxy_terminal_destino'),
            'Liquidez': row.get('liquidez_dias'),
            'Carência': row.get('carencia_dias'),
            'Ticket mín.': row.get('aplicacao_minima'),
            'Status': 'elegível' if str(row.get('Status_Confirmação') or '').strip() in {'', 'Confirmado', 'confirmado'} else str(row.get('Status_Confirmação') or ''),
        })
    print('- amostra do ranking relevante do dia:')
    _imprimir_tabela(['Rank', 'Produto', 'Score', 'Proxy terminal', 'Liquidez', 'Carência', 'Ticket mín.', 'Status'], linhas, limite=10)


def _render_secao_switchings_oficiais(contexto_baseline):
    ranking = getattr(contexto_baseline, 'ranking_carteira', None)
    destino_top1 = ranking.auditoria.get('destino_top1') if ranking is not None else None
    linhas = _montar_switchings_oficiais(contexto_baseline, limite=10)
    _imprimir_titulo('SWITCHINGS CANDIDATOS / CLASSIFICADOS')
    _imprimir_pares([
        ('lotes avaliados para switching', len(linhas)),
        ('destinos elegíveis de switching', len(ranking.quadro_destinos_switch) if ranking is not None and isinstance(getattr(ranking, 'quadro_destinos_switch', None), pd.DataFrame) else 0),
        ('switchings promovidos/executados', len(linhas)),
        ('destino top 1 do ranking', destino_top1),
    ])
    print('- amostra de switchings reais da janela (independente de pagamentos):')
    _imprimir_tabela(['Data', 'Lote origem', 'Produto origem', 'Destino', 'Ganho estimado', 'Status'], linhas, limite=10)


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

    pagamentos_realizados_console, pagamentos_proximos_console = _preparar_amostras_pagamentos_console(dados_operacionais, replay_passado, contexto_baseline.decisao_local_v1, contexto_baseline, limite=5)
    render_secao_amostras_pagamentos(
        pagamentos_realizados=pagamentos_realizados_console,
        pagamentos_proximos=pagamentos_proximos_console,
    )
    _render_secao_ranking_oficial(contexto_baseline)
    _render_secao_switchings_oficiais(contexto_baseline)

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


if __name__ == '__main__':
    main()
