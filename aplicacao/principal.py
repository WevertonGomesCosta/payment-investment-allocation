"""Ponto de entrada mínimo da baseline reconstruída."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
import re
import pandas as pd
from typing import Iterable, Sequence

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.ambiente import bootstrap_ambiente
from nucleo.calendario_financeiro import construir_calendario_financeiro, contar_dias_rendimento, eh_dia_util_bancario, extrair_metadata_serie_cdi
from nucleo.carregador_config import carregar_config
from nucleo.cache_cdi_bcb import carregar_cache_cdi_diario
from nucleo.carteira_canonica import carregar_carteira_canonica
from nucleo.dados_operacionais_canonicos import carregar_dados_operacionais_canonicos
from nucleo.switching_shadow_reconciliacao import carregar_switching_shadow_reconciliacao
from nucleo.triagem_motor import carregar_triagem_motor
from nucleo.leitor_planilha import carregar_planilha, construir_resumo_planilha
from nucleo.nucleo_financeiro_minimo import carregar_nucleo_financeiro_minimo, construir_faixas_ir, construir_tabela_iof
from nucleo.replay_passado_controlado import carregar_replay_passado_controlado


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
        return 'ERRO'
    if avisos_norm or not condicao_ok:
        return 'AVISO'
    return 'OK'


def _imprimir_linha_status(rotulo: str, severidade: str, detalhe: str = '') -> None:
    sufixo = f" — {detalhe}" if detalhe else ''
    print(f"[{severidade}] {rotulo}{sufixo}")


def _imprimir_itens_severidade(rotulo: str, itens: Iterable[object] | None, severidade: str) -> None:
    itens_norm = _normalizar_lista(itens)
    if not itens_norm:
        return
    print(f"- {rotulo}:")
    for item in itens_norm:
        print(f"  [{severidade}] {item}")


def _formatar_valor_tabela(valor: object) -> str:
    if valor is None:
        return ''
    if isinstance(valor, float):
        return f"{valor:.2f}"
    return str(valor)


def _imprimir_tabela(colunas: Sequence[str], linhas: Sequence[dict[str, object]], *, limite: int | None = None) -> None:
    linhas_use = list(linhas[:limite] if limite is not None else linhas)
    if not linhas_use:
        print('  [OK] sem linhas para exibir')
        return
    larguras = {}
    for col in colunas:
        larguras[col] = len(col)
        for linha in linhas_use:
            larguras[col] = max(larguras[col], len(_formatar_valor_tabela(linha.get(col))))
    cab = ' | '.join(col.ljust(larguras[col]) for col in colunas)
    sep = '-+-'.join('-' * larguras[col] for col in colunas)
    print(cab)
    print(sep)
    for linha in linhas_use:
        print(' | '.join(_formatar_valor_tabela(linha.get(col)).ljust(larguras[col]) for col in colunas))


def _extrair_data_auditoria_item(item, data_padrao):
    valor = item.get('data_referencia_app') or item.get('data_app') or item.get('data_observacao')
    if valor:
        try:
            return pd.to_datetime(valor, dayfirst=True).date()
        except Exception:
            pass
    obs = str(item.get('observacao') or '')
    match = re.search(r'(\d{2}/\d{2}/\d{4})', obs)
    if match:
        try:
            return pd.to_datetime(match.group(1), dayfirst=True).date()
        except Exception:
            pass
    return data_padrao


def _preparar_auditoria_lotes_vs_app(replay_passado, calendario_financeiro, config, data_referencia, serie_cdi=None):
    refs = (((config.get('auditoria') or {}).get('referencias_app_lotes')) or [])
    if not refs:
        return []
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    lotes_por_id = {l.id: l for l in replay_passado.lotes_apos_replay}
    linhas = []
    for item in refs:
        lote_id = str(item.get('lote_id') or '').strip()
        lote = lotes_por_id.get(lote_id)
        if lote is None:
            linhas.append({
                'Lote': lote_id,
                'Bruto modelo': None,
                'Bruto app': item.get('saldo_bruto_app'),
                'Δ bruto': None,
                'Líquido modelo': None,
                'Líquido app': item.get('saldo_liquido_app'),
                'Δ líquido': None,
                'Dias úteis': None,
                'Obs.': 'lote não encontrado no replay',
            })
            continue
        data_auditoria = _extrair_data_auditoria_item(item, data_referencia)
        bruto = round(float(lote.saldo_bruto or 0.0), 2) if data_auditoria == data_referencia else round(float(lote.valor_bruto_em_data(data_auditoria, calendario_financeiro, serie_cdi=serie_cdi, data_base_referencia=data_referencia)), 2)
        liquido = round(float(lote.valor_liquido_em_data(data_auditoria, calendario_financeiro, tabela_iof=tabela_iof, faixas_ir=faixas_ir, serie_cdi=serie_cdi, data_base_referencia=data_referencia)), 2)
        bruto_app = float(item.get('saldo_bruto_app') or 0.0)
        liquido_app = float(item.get('saldo_liquido_app') or 0.0)
        linhas.append({
            'Lote': lote.id,
            'Bruto modelo': bruto,
            'Bruto app': bruto_app,
            'Δ bruto': round(bruto - bruto_app, 2),
            'Líquido modelo': liquido,
            'Líquido app': liquido_app,
            'Δ líquido': round(liquido - liquido_app, 2),
            'Dias úteis': contar_dias_rendimento(
                lote.data_base_fiscal,
                data_auditoria,
                calendario_financeiro,
                serie_cdi=serie_cdi,
                data_fechamento_referencia=data_auditoria,
            ) if data_auditoria >= lote.data_aplicacao else 0,
            'Obs.': item.get('observacao') or data_auditoria.isoformat(),
        })
    return linhas


def _preparar_resumo_delta_lotes(auditoria_lotes_vs_app):
    if not auditoria_lotes_vs_app:
        return []
    deltas_brutos = [abs(float(item.get('Δ bruto') or 0.0)) for item in auditoria_lotes_vs_app if item.get('Δ bruto') is not None]
    deltas_liquidos = [abs(float(item.get('Δ líquido') or 0.0)) for item in auditoria_lotes_vs_app if item.get('Δ líquido') is not None]
    return [
        ('lotes críticos auditados', len(auditoria_lotes_vs_app)),
        ('maior |Δ bruto|', round(max(deltas_brutos or [0.0]), 2)),
        ('maior |Δ líquido|', round(max(deltas_liquidos or [0.0]), 2)),
        ('soma |Δ bruto|', round(sum(deltas_brutos), 2)),
        ('soma |Δ líquido|', round(sum(deltas_liquidos), 2)),
    ]


def _obter_limiar_residuo_resolvido(config):
    auditoria_cfg = config.get('auditoria', {}) if isinstance(config.get('auditoria'), dict) else {}
    replay_cfg = config.get('replay', {}) if isinstance(config.get('replay'), dict) else {}
    valor = auditoria_cfg.get('limiar_residuo_resolvido')
    if valor is None:
        valor = replay_cfg.get('valor_minimo_lote_ativo', 0.01)
    try:
        return round(float(valor), 2)
    except Exception:
        return 0.01


def _classificar_status_residuo(valor, limiar):
    return 'resolvido por limiar' if float(valor or 0.0) <= float(limiar or 0.0) else 'pendente para validação'


def _preparar_auditoria_lotes_residuais(replay_passado, config):
    linhas = []
    limiar = _obter_limiar_residuo_resolvido(config)
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
    limiar = _obter_limiar_residuo_resolvido(config)
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


def _comparar_auditoria_lotes(auditoria_atual, auditoria_menos_1_dia, replay_passado=None, data_referencia=None):
    por_lote_menos_1 = {item.get('Lote'): item for item in auditoria_menos_1_dia or []}
    lotes_com_movimento_na_ref = set()
    if replay_passado is not None and data_referencia is not None and hasattr(replay_passado, 'log_passado'):
        try:
            log = replay_passado.log_passado
            if len(log):
                lotes_com_movimento_na_ref = set(log[log['Data'] == data_referencia]['Lote'].dropna().astype(str).tolist())
        except Exception:
            lotes_com_movimento_na_ref = set()
    linhas = []
    for item in auditoria_atual or []:
        lote = item.get('Lote')
        base = por_lote_menos_1.get(lote) or {}
        bruto_atual = item.get('Bruto modelo')
        liquido_atual = item.get('Líquido modelo')
        bruto_menos_1 = base.get('Bruto modelo')
        liquido_menos_1 = base.get('Líquido modelo')
        contaminado = lote in lotes_com_movimento_na_ref
        linhas.append({
            'Lote': lote,
            'Bruto ref': bruto_atual,
            'Bruto ref-1d': bruto_menos_1,
            'Δ 1d bruto': None if contaminado or bruto_atual is None or bruto_menos_1 is None else round(float(bruto_atual) - float(bruto_menos_1), 2),
            'Líquido ref': liquido_atual,
            'Líquido ref-1d': liquido_menos_1,
            'Δ 1d líquido': None if contaminado or liquido_atual is None or liquido_menos_1 is None else round(float(liquido_atual) - float(liquido_menos_1), 2),
            'Obs.': 'houve saque na data de referência; teste -1d não isola só rendimento' if contaminado else '',
        })
    return linhas


def _valor_liquido_disponivel_conservador_lote(
    lote,
    data_alvo,
    calendario_financeiro,
    *,
    tabela_iof=None,
    faixas_ir=None,
    serie_cdi=None,
    data_base_referencia=None,
):
    if lote.esgotado:
        return 0.0
    if data_alvo < lote.data_recebimento:
        return 0.0
    if lote.carencia_ate and data_alvo > lote.data_aplicacao and data_alvo < lote.carencia_ate:
        return 0.0
    return round(float(lote.valor_liquido_em_data(
        min(data_alvo, data_base_referencia or data_alvo),
        calendario_financeiro,
        tabela_iof=tabela_iof,
        faixas_ir=faixas_ir,
        serie_cdi=serie_cdi,
        data_base_referencia=data_base_referencia,
    ) or 0.0), 2)


def _preparar_painel_cobertura_futura(dados_operacionais, replay_passado, calendario_financeiro, config, data_referencia, *, serie_cdi=None):
    gastos = dados_operacionais.gastos_canonicos.copy()
    if len(gastos) == 0:
        return []
    futuros = gastos[gastos['futuro_ou_pendente_na_data_referencia'] == True].copy()
    if len(futuros) == 0:
        return []
    futuros = futuros.sort_values(by=['data', 'despesa_id'], kind='stable')
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    liquidez_atual_total = round(sum(
        _valor_liquido_disponivel_conservador_lote(
            lote,
            data_referencia,
            calendario_financeiro,
            tabela_iof=tabela_iof,
            faixas_ir=faixas_ir,
            serie_cdi=serie_cdi,
            data_base_referencia=data_referencia,
        )
        for lote in replay_passado.lotes_apos_replay
    ), 2)
    acumulado = 0.0
    linhas = []
    for item in futuros.to_dict('records'):
        valor = round(float(item.get('valor') or 0.0), 2)
        acumulado = round(acumulado + valor, 2)
        folga = round(liquidez_atual_total - acumulado, 2)
        lotes = ' | '.join([str(x).strip() for x in [item.get('lote_usado_1'), item.get('lote_usado_2')] if str(x or '').strip()])
        linhas.append({
            'Data': item.get('data').isoformat() if hasattr(item.get('data'), 'isoformat') else str(item.get('data') or ''),
            'Despesa ID': item.get('despesa_id') or '',
            'Conta': item.get('descricao') or '',
            'Valor': valor,
            'Acumulado': acumulado,
            'Liquidez atual': liquidez_atual_total,
            'Folga': folga,
            'Status': 'cobertura conservadora suficiente' if folga >= 0.0 else 'atenção: déficit potencial',
            'Lotes informados': lotes,
        })
    return linhas


def _preparar_resumo_cobertura_futura(painel_cobertura_futura):
    if not painel_cobertura_futura:
        return [('despesas futuras mapeadas', 0)]
    liquidez = round(float(painel_cobertura_futura[0].get('Liquidez atual') or 0.0), 2)
    maior_acumulado = round(max(float(item.get('Acumulado') or 0.0) for item in painel_cobertura_futura), 2)
    menor_folga = round(min(float(item.get('Folga') or 0.0) for item in painel_cobertura_futura), 2)
    qtd_deficit = sum(1 for item in painel_cobertura_futura if float(item.get('Folga') or 0.0) < 0.0)
    return [
        ('despesas futuras mapeadas', len(painel_cobertura_futura)),
        ('liquidez atual pós-replay', liquidez),
        ('maior demanda acumulada futura', maior_acumulado),
        ('menor folga conservadora', menor_folga),
        ('eventos com déficit potencial', qtd_deficit),
    ]


def _resolver_data_economica_situacao_atual(data_referencia, calendario_financeiro, serie_cdi=None):
    data_fechamento = data_referencia - timedelta(days=1)
    while data_fechamento > date(1900, 1, 1) and not eh_dia_util_bancario(data_fechamento, calendario_financeiro):
        data_fechamento -= timedelta(days=1)
    metadata = extrair_metadata_serie_cdi(serie_cdi) if serie_cdi else None
    ultima_data_serie = getattr(metadata, 'data_final', None) if metadata is not None else None
    if ultima_data_serie is not None and ultima_data_serie >= data_fechamento:
        return data_fechamento
    return data_referencia


def _preparar_tabela_lotes_ativos(replay_passado, calendario_financeiro, config, data_referencia, *, serie_cdi=None):
    tabela_iof = construir_tabela_iof(config)
    faixas_ir = construir_faixas_ir(config)
    limiar = _obter_limiar_residuo_resolvido(config)
    linhas = []
    data_economica = _resolver_data_economica_situacao_atual(data_referencia, calendario_financeiro, serie_cdi=serie_cdi)
    for lote in sorted(replay_passado.lotes_apos_replay, key=lambda x: (x.data_recebimento, x.data_aplicacao, x.id)):
        saldo_bruto = round(float(lote.valor_bruto_em_data(
            data_economica,
            calendario_financeiro,
            serie_cdi=serie_cdi,
            data_base_referencia=data_referencia,
        ) or 0.0), 2)
        if lote.esgotado or saldo_bruto <= limiar:
            continue
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
        linhas.append({
            'Recebimento': lote.data_recebimento.isoformat() if hasattr(lote.data_recebimento, 'isoformat') else str(lote.data_recebimento),
            'Aplicação': lote.data_aplicacao.isoformat() if hasattr(lote.data_aplicacao, 'isoformat') else str(lote.data_aplicacao),
            'Produto': lote.investimento,
            'Valor original': round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0), 2),
            'Dias corridos': dias_corridos,
            'Dias úteis': dias_uteis,
            'Bruto': saldo_bruto,
            'Líquido': saldo_liquido,
            'Saldo rem': saldo_rem,
            'Lote': lote.id,
        })
    return linhas


def main() -> None:
    pacote_config = carregar_config(raiz_repositorio=RAIZ_REPOSITORIO)
    contexto = bootstrap_ambiente(pacote_config.conteudo, grupos_extras=['financeiro'], instalar_automaticamente=False)
    calendario_financeiro = construir_calendario_financeiro(pacote_config.conteudo, data_referencia=contexto.data_referencia)
    pacote_planilha = carregar_planilha(pacote_config.conteudo, raiz_repositorio=pacote_config.raiz_repositorio)
    carteira_canonica = carregar_carteira_canonica(pacote_planilha, pacote_config.conteudo)
    dados_operacionais = carregar_dados_operacionais_canonicos(
        pacote_planilha,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
        carteira_canonica=carteira_canonica,
    )
    cache_cdi = carregar_cache_cdi_diario(
        dados_operacionais,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
        raiz_repositorio=pacote_config.raiz_repositorio,
    )
    switching_shadow = carregar_switching_shadow_reconciliacao(dados_operacionais, carteira_canonica=carteira_canonica)
    triagem_motor = carregar_triagem_motor(
        carteira_canonica,
        dados_operacionais,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
    )
    nucleo_financeiro = carregar_nucleo_financeiro_minimo(
        dados_operacionais,
        carteira_canonica,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
        serie_cdi=cache_cdi.serie_cdi,
    )
    replay_passado = carregar_replay_passado_controlado(
        dados_operacionais,
        nucleo_financeiro,
        calendario_financeiro,
        pacote_config.conteudo,
        data_referencia=contexto.data_referencia,
        serie_cdi=cache_cdi.serie_cdi,
    )

    data_referencia_menos_1_dia = contexto.data_referencia - timedelta(days=1)
    calendario_financeiro_menos_1_dia = construir_calendario_financeiro(pacote_config.conteudo, data_referencia=data_referencia_menos_1_dia)
    dados_operacionais_menos_1_dia = carregar_dados_operacionais_canonicos(
        pacote_planilha,
        pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        carteira_canonica=carteira_canonica,
    )
    nucleo_financeiro_menos_1_dia = carregar_nucleo_financeiro_minimo(
        dados_operacionais_menos_1_dia,
        carteira_canonica,
        calendario_financeiro_menos_1_dia,
        pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        serie_cdi=cache_cdi.serie_cdi,
    )
    replay_passado_menos_1_dia = carregar_replay_passado_controlado(
        dados_operacionais_menos_1_dia,
        nucleo_financeiro_menos_1_dia,
        calendario_financeiro_menos_1_dia,
        pacote_config.conteudo,
        data_referencia=data_referencia_menos_1_dia,
        serie_cdi=cache_cdi.serie_cdi,
    )

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
    auditoria_lotes_vs_app = _preparar_auditoria_lotes_vs_app(replay_passado, calendario_financeiro, pacote_config.conteudo, contexto.data_referencia, serie_cdi=cache_cdi.serie_cdi)
    auditoria_lotes_vs_app_menos_1_dia = _preparar_auditoria_lotes_vs_app(replay_passado_menos_1_dia, calendario_financeiro_menos_1_dia, pacote_config.conteudo, data_referencia_menos_1_dia, serie_cdi=cache_cdi.serie_cdi)
    limiar_residuo_resolvido = _obter_limiar_residuo_resolvido(pacote_config.conteudo)
    auditoria_residual_lotes = _preparar_auditoria_lotes_residuais(replay_passado, pacote_config.conteudo)
    auditoria_detalhada_residuos = _preparar_auditoria_detalhada_residuos(replay_passado, pacote_config.conteudo, contexto.data_referencia)
    auditoria_recebimento_aplicacao = _preparar_auditoria_recebimento_vs_aplicacao(dados_operacionais, replay_passado)
    auditoria_residual_lotes_resolvidos = [item for item in auditoria_residual_lotes if item.get('Status') == 'resolvido por limiar']
    auditoria_residual_lotes_pendentes = [item for item in auditoria_residual_lotes if item.get('Status') != 'resolvido por limiar']
    auditoria_detalhada_residuos_pendentes = [item for item in auditoria_detalhada_residuos if item.get('Status') != 'resolvido por limiar']
    comparativo_menos_1_dia = _comparar_auditoria_lotes(auditoria_lotes_vs_app, auditoria_lotes_vs_app_menos_1_dia, replay_passado=replay_passado, data_referencia=contexto.data_referencia)
    painel_cobertura_futura = _preparar_painel_cobertura_futura(dados_operacionais, replay_passado, calendario_financeiro, pacote_config.conteudo, contexto.data_referencia, serie_cdi=cache_cdi.serie_cdi)

    resumo_deltas_lotes_vs_app = _preparar_resumo_delta_lotes(auditoria_lotes_vs_app)
    resumo_detalhado_residuos = _preparar_resumo_auditoria_detalhada_residuos(auditoria_detalhada_residuos, limiar_residuo_resolvido)
    resumo_cobertura_futura = _preparar_resumo_cobertura_futura(painel_cobertura_futura)

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

    _imprimir_titulo('BASELINE')
    _imprimir_pares([
        ('versão', 'V44'),
        ('raiz do repositório', pacote_config.raiz_repositorio),
        ('config carregado', pacote_config.caminho),
        ('planilha carregada', pacote_planilha.caminho),
    ])

    _imprimir_titulo('AMBIENTE')
    _imprimir_pares([
        ('timezone', contexto.timezone_nome),
        ('data de referência', contexto.data_referencia.isoformat()),
        ('colab', 'sim' if contexto.em_colab else 'não'),
        ('warnings de rede configurados', 'sim' if contexto.warnings_configurados else 'não'),
    ])

    _imprimir_titulo('DEPENDÊNCIAS')
    _imprimir_linha_status('Dependências essenciais da baseline', severidade_dependencias, 'baseline mínima e auditoria estrutural')
    _imprimir_pares([
        ('instaladas', ', '.join(contexto.relatorio_dependencias.get('instaladas', [])) or 'nenhuma'),
        ('ausentes', ', '.join(contexto.relatorio_dependencias.get('ausentes', [])) or 'nenhuma'),
    ])

    _imprimir_titulo('CALENDÁRIO FINANCEIRO E TAXAS BASE')
    _imprimir_linha_status('Camada neutra de calendário e taxas base', 'OK', 'sem fetch do BCB e sem aplicação econômica aos lotes')
    _imprimir_pares([
        ('CDI anual do modelo', f"{calendario_financeiro.cdi_anual_modelo:.6f}"),
        ('convenção dias/ano CDI', calendario_financeiro.convencao_dias_ano_cdi),
        ('taxa diária base', f"{calendario_financeiro.taxa_dia_base:.12f}"),
        ('anos dias sem rendimento', f"{calendario_financeiro.ano_inicio_dias_sem_rendimento}-{calendario_financeiro.ano_fim_dias_sem_rendimento}"),
        ('dias sem rendimento mapeados', len(calendario_financeiro.dias_sem_rendimento_bancario)),
        ('workalendar disponível', 'sim' if calendario_financeiro.workalendar_disponivel else 'não'),
        ('calendário Brasil disponível', 'sim' if calendario_financeiro.calendario_brasil_disponivel else 'não'),
        ('dias de rendimento no mês até a data de referência', dias_rendimento_mes),
    ])

    _imprimir_titulo('CACHE CDI DIÁRIO (BCB)')
    _imprimir_linha_status('Cache diário de CDI para auditoria e replay', severidade_cache_cdi, f"{auditoria_cache_cdi.get('qtd_datas_serie_cdi', 0)} datas")
    _imprimir_pares([
        ('data inicial da consulta', auditoria_cache_cdi.get('data_inicial_consulta')),
        ('data final da consulta', auditoria_cache_cdi.get('data_final_consulta')),
        ('última data com fator no cache', data_ultimo_fator_cdi),
        ('fonte da série', auditoria_cache_cdi.get('fonte_serie_cdi')),
        ('status do fetch', auditoria_cache_cdi.get('fetch_status')),
        ('caminho do cache', auditoria_cache_cdi.get('caminho_cache')),
    ])
    _imprimir_itens_severidade('avisos do cache CDI', validacao_cache_cdi.get('avisos'), 'AVISO')

    _imprimir_titulo('ABAS ENCONTRADAS')
    for indice, nome_aba in enumerate(pacote_planilha.nomes_abas, start=1):
        print(f"- [{indice}] {nome_aba}")

    _imprimir_titulo('RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS')
    for _, nome_aba in abas_primarias_reais:
        info = resumo_por_aba.get(nome_aba)
        if not info:
            _imprimir_linha_status(nome_aba, 'ERRO', 'aba ausente')
            continue
        _imprimir_linha_status(nome_aba, 'OK', f"{info['n_linhas']} linhas, {info['n_colunas']} colunas")
        colunas = info.get('colunas', [])
        if colunas:
            print(f"  colunas (primeiras 8): {', '.join(colunas[:8])}")

    _imprimir_titulo('ABAS PRIMÁRIAS DO CONTRATO')
    _imprimir_linha_status('Abas primárias do contrato', severidade_abas, f"{len(abas_primarias_reais)} blocos esperados")
    for chave, nome_aba in abas_primarias_reais:
        presente = nome_aba in pacote_planilha.nomes_abas
        info = resumo_por_aba.get(nome_aba)
        linhas = info['n_linhas'] if info else '-'
        colunas = info['n_colunas'] if info else '-'
        sev = 'OK' if presente else 'ERRO'
        _imprimir_linha_status(f'Bloco {chave}', sev, nome_aba)
        _imprimir_pares([('presente', 'sim' if presente else 'não'), ('linhas', linhas), ('colunas', colunas)])
        print('')

    if abas_auxiliares:
        _imprimir_titulo('ABAS AUXILIARES / NÃO OPERACIONAIS')
        _imprimir_linha_status('Abas auxiliares identificadas', 'OK', f"{len(abas_auxiliares)} abas fora do contrato operacional")
        for nome_aba in abas_auxiliares:
            info = resumo_por_aba.get(nome_aba)
            linhas = info['n_linhas'] if info else '-'
            colunas = info['n_colunas'] if info else '-'
            print(f"- {nome_aba}: {linhas} linhas, {colunas} colunas")

    _imprimir_titulo('RESUMO CONSOLIDADO DAS CAMADAS CANÔNICAS')
    _imprimir_linha_status('Carteira canônica', severidade_carteira, f"{len(carteira_canonica.quadro_canonico)} produtos")
    _imprimir_linha_status('Inventário canônico', severidade_inventario, f"{len(dados_operacionais.inventario_canonico)} lotes")
    _imprimir_linha_status('Gastos canônicos', severidade_gastos, f"{len(dados_operacionais.gastos_canonicos)} despesas")
    _imprimir_linha_status('Lotes shadow', severidade_lotes_shadow, f"{len(switching_shadow.lotes_shadow)} lotes técnicos")
    _imprimir_linha_status('Trilha técnica de eventos', severidade_eventos_shadow, f"{len(switching_shadow.eventos_financeiros_ordenados)} eventos ordenados")
    _imprimir_linha_status('Triagem programática do motor', severidade_triagem, f"{auditoria_triagem.get('qtd_candidatos_motor_v1', 0)} candidatos")
    _imprimir_linha_status('Núcleo financeiro mínimo', severidade_nucleo, f"{auditoria_nucleo.get('qtd_lotes_financeiros', 0)} lotes financeiros")

    _imprimir_titulo('CARTEIRA CANÔNICA')
    _imprimir_linha_status('Validação estrutural da carteira', severidade_carteira)
    _imprimir_pares([
        ('aba', carteira_canonica.nome_aba),
        ('produtos canônicos', len(carteira_canonica.quadro_canonico)),
        ('produto_key únicos', len(carteira_canonica.mapa_produtos.get('by_key', {}))),
        ('nomes normalizados únicos', len(carteira_canonica.mapa_produtos.get('by_nome_norm', {}))),
        ('famílias de produto', len(carteira_canonica.auditoria.get('resumo_familia_produto', {}))),
        ('regimes de taxa', len(carteira_canonica.auditoria.get('resumo_regime_taxa', {}))),
        ('papéis de produto', len(carteira_canonica.auditoria.get('resumo_papel_produto', {}))),
        ('linhas sem produto_id explícito', carteira_canonica.auditoria.get('sem_produto_id', 0)),
        ('erros de validação', len(_normalizar_lista(validacao_carteira.get('erros')))),
        ('avisos de validação', len(_normalizar_lista(validacao_carteira.get('avisos')))),
    ])
    print('- colunas resolvidas:')
    for chave, valor in carteira_canonica.auditoria.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    print('- observação estrutural: metadados derivados da carteira atuam como ponte transitória até maior estruturação explícita da planilha.')
    print(f"- campos estruturais ainda sem coluna resolvida: {carteira_canonica.auditoria.get('qtd_campos_estruturais_sem_coluna_resolvida', 0)}")
    if carteira_canonica.auditoria.get('campos_estruturais_sem_coluna_resolvida'):
        print(f"  [AVISO] pendentes na planilha: {', '.join(carteira_canonica.auditoria.get('campos_estruturais_sem_coluna_resolvida', []))}")
    print('- fontes dos metadados estruturais:')
    for campo, resumo in carteira_canonica.auditoria.get('resumo_fontes_metadados', {}).items():
        cobertura_planilha = carteira_canonica.auditoria.get('resumo_cobertura_metadados_planilha', {}).get(campo, 0)
        cobertura_derivada = carteira_canonica.auditoria.get('resumo_cobertura_metadados_derivados', {}).get(campo, 0)
        print(f"  [OK] {campo}: {resumo} | planilha={cobertura_planilha} | derivado={cobertura_derivada}")
    _imprimir_itens_severidade('erros de validação', validacao_carteira.get('erros'), 'ERRO')
    _imprimir_itens_severidade('avisos de validação', validacao_carteira.get('avisos'), 'AVISO')

    _imprimir_titulo('INVENTÁRIO CANÔNICO')
    _imprimir_linha_status('Validação estrutural do inventário', severidade_inventario)
    _imprimir_pares([
        ('aba', dados_operacionais.nome_aba_lotes),
        ('lotes canônicos', len(dados_operacionais.inventario_canonico)),
        ('aportados', resumo_inventario.get('aportados', 0)),
        ('não aportados disponíveis', resumo_inventario.get('nao_aportados_disponiveis', 0)),
        ('não aportados exauridos', resumo_inventario.get('nao_aportados_exauridos', 0)),
        ('recebidos futuros', resumo_inventario.get('recebidos_futuros', 0)),
        ('aportados com match', resumo_inventario.get('aportados_com_match', 0)),
        ('aportados sem match', resumo_inventario.get('aportados_sem_match', 0)),
        ('erros de validação', len(_normalizar_lista(validacao_inventario.get('erros')))),
        ('avisos de validação', len(_normalizar_lista(validacao_inventario.get('avisos')))),
    ])
    print('- colunas resolvidas:')
    for chave, valor in dados_operacionais.auditoria_inventario.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    _imprimir_itens_severidade('erros de validação', validacao_inventario.get('erros'), 'ERRO')
    _imprimir_itens_severidade('avisos de validação', validacao_inventario.get('avisos'), 'AVISO')

    _imprimir_titulo('GASTOS CANÔNICOS')
    _imprimir_linha_status('Validação estrutural dos gastos', severidade_gastos)
    _imprimir_pares([
        ('aba', dados_operacionais.nome_aba_despesas),
        ('despesas canônicas', len(dados_operacionais.gastos_canonicos)),
        ('pagas até data de referência', resumo_gastos.get('pagas_ate_data_referencia', 0)),
        ('futuras ou pendentes', resumo_gastos.get('futuras_ou_pendentes', 0)),
        ('com lote informado', resumo_gastos.get('com_lote_informado', 0)),
        ('erros de validação', len(_normalizar_lista(validacao_gastos.get('erros')))),
        ('avisos de validação', len(_normalizar_lista(validacao_gastos.get('avisos')))),
    ])
    print('- colunas resolvidas:')
    for chave, valor in dados_operacionais.auditoria_gastos.get('colunas_resolvidas', {}).items():
        if valor:
            print(f"  [OK] {chave}: {valor}")
    _imprimir_itens_severidade('erros de validação', validacao_gastos.get('erros'), 'ERRO')
    _imprimir_itens_severidade('avisos de validação', validacao_gastos.get('avisos'), 'AVISO')

    _imprimir_titulo('SWITCHING SHADOW E RECONCILIAÇÃO')
    _imprimir_linha_status('Normalização shadow dos lotes', severidade_lotes_shadow)
    _imprimir_pares([
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
    amostras_sem_match = resumo_lotes_shadow.get('amostras_produto_nao_reconhecido', [])
    if amostras_sem_match:
        print('- amostras de lotes shadow sem match canônico:')
        for item in amostras_sem_match[:5]:
            print(f"  [AVISO] lote={item.get('lote_id')} | investimento={item.get('investimento_bruto')} | match={item.get('tipo_match_produto')}")

    _imprimir_titulo('NÚCLEO FINANCEIRO MÍNIMO')
    _imprimir_linha_status('Primitivas financeiras irreduzíveis do lote', severidade_nucleo, 'sem solver, sem replay, sem switching econômico e sem relatório financeiro atual')
    _imprimir_pares([
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
        ('data final valuation ref. completa', auditoria_nucleo.get('data_final_valuation_referencia')),
        ('fechamentos da referência com fallback CDI', auditoria_nucleo.get('qtd_fechamentos_referencia_com_fallback_cdi', 0)),
        ('saldo bruto ref. sem replay', auditoria_nucleo.get('saldo_bruto_total_referencia_sem_replay', 0.0)),
        ('saldo líquido ref. sem replay', auditoria_nucleo.get('saldo_liquido_total_referencia_sem_replay', 0.0)),
    ])
    amostra_saque = auditoria_nucleo.get('amostra_movimento_saque') or {}
    if amostra_saque:
        print('- amostra de saque no núcleo mínimo (auditoria técnica):')
        print(f"  [OK] lote={amostra_saque.get('lote_id')} | bruto={amostra_saque.get('bruto')} | liquido={amostra_saque.get('liquido')} | imposto={amostra_saque.get('imposto')} | saldo_remanescente={amostra_saque.get('saldo_remanescente')}")
    amostra_fechamento_nucleo = auditoria_nucleo.get('amostra_fechamento_referencia') or {}
    if amostra_fechamento_nucleo:
        print('- amostra de fechamento da referência no núcleo mínimo:')
        print(f"  [OK] data_valuation={amostra_fechamento_nucleo.get('data_valuation')} | data_fator_utilizado={amostra_fechamento_nucleo.get('data_fator_utilizado')} | fonte={amostra_fechamento_nucleo.get('fonte')} | lotes_atualizados={amostra_fechamento_nucleo.get('qtd_lotes_atualizados')}")
    _imprimir_itens_severidade('erros de validação', validacao_nucleo.get('erros'), 'ERRO')
    _imprimir_itens_severidade('avisos de validação', validacao_nucleo.get('avisos'), 'AVISO')

    _imprimir_titulo('REPLAY CONTROLADO DO PASSADO')
    _imprimir_linha_status('Reconciliacao de pagamentos historicos com lotes informados', severidade_replay, 'consome o nucleo financeiro minimo sem abrir switching economico, score final, solver ou relatorio financeiro atual')
    _imprimir_pares([
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
        ('data final valuation ref. completa', auditoria_replay.get('data_final_valuation_referencia')),
        ('fechamentos da referência com fallback CDI', auditoria_replay.get('qtd_fechamentos_referencia_com_fallback_cdi', 0)),
        ('valor contas historicas', auditoria_replay.get('total_valor_contas_historicas', 0.0)),
        ('liquido coberto', auditoria_replay.get('total_liquido_coberto', 0.0)),
        ('saldo bruto pos replay', auditoria_replay.get('saldo_bruto_total_pos_replay', 0.0)),
        ('saldo liquido pos replay', auditoria_replay.get('saldo_liquido_total_pos_replay', 0.0)),
    ])
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
        _imprimir_tabela(colunas_inc, linhas_inc)
    _imprimir_itens_severidade('erros de validação', validacao_replay.get('erros'), 'ERRO')
    _imprimir_itens_severidade('avisos de validação', validacao_replay.get('avisos'), 'AVISO')

    _imprimir_titulo('PAINEL MÍNIMO DE COBERTURA FUTURA')
    _imprimir_linha_status('Confronto conservador entre despesas futuras e liquidez atual pós-replay', 'OK', 'sem consumir lotes, sem solver e sem projeção econômica adicional além da posição atual')
    _imprimir_pares(resumo_cobertura_futura)
    if painel_cobertura_futura:
        _imprimir_tabela(['Data', 'Despesa ID', 'Conta', 'Valor', 'Acumulado', 'Liquidez atual', 'Folga', 'Status', 'Lotes informados'], painel_cobertura_futura, limite=12)
    else:
        print('  [OK] sem despesas futuras ou pendentes nesta execução')

    _imprimir_titulo('TRIAGEM PRELIMINAR PROXY DO MOTOR — SCORE V1')
    _imprimir_linha_status('Seleção contextual preliminar de candidatos', severidade_triagem, 'proxy de triagem; nao e decisao final do motor, sem replay, sem nucleo financeiro e sem switching economico; calibracao conservadora nesta fase')
    _imprimir_pares([
        ('produtos totais no universo', auditoria_triagem.get('qtd_total_produtos', 0)),
        ('elegíveis brutos', auditoria_triagem.get('qtd_elegiveis_brutos', 0)),
        ('candidatos motor v1', auditoria_triagem.get('qtd_candidatos_motor_v1', 0)),
        ('top_k global', auditoria_triagem.get('top_k_global', 0)),
        ('top_k por família', auditoria_triagem.get('top_k_por_familia', 0)),
        ('score mínimo seleção', auditoria_triagem.get('score_minimo_selecao', 0.0)),
        ('modo de calibração', auditoria_triagem.get('modo_calibracao', 'nao informado')),
        ('fração elegíveis selecionados', auditoria_triagem.get('fracao_elegiveis_selecionados', 0.0)),
        ('elegíveis não selecionados', auditoria_triagem.get('qtd_elegiveis_nao_selecionados', 0)),
        ('recursos disponíveis para aporte', contexto_triagem.get('recursos_disponiveis_para_aporte', 0.0)),
        ('recursos aportados observados', contexto_triagem.get('recursos_aportados_observados', 0.0)),
        ('despesas futuras 30 dias', contexto_triagem.get('despesas_futuras_30_dias', 0.0)),
        ('cobertura caixa 30 dias', round(float(contexto_triagem.get('cobertura_caixa_30_dias', 0.0) or 0.0), 4)),
    ])
    if auditoria_triagem.get('resumo_familia_produto'):
        print('- famílias no universo único da carteira:')
        for chave, valor in auditoria_triagem.get('resumo_familia_produto', {}).items():
            print(f"  [OK] {chave}: {valor}")

    _imprimir_titulo('TOP PRODUTOS SELECIONADOS — SCORE V1')
    if auditoria_triagem.get('amostra_top_produtos'):
        linhas_top = []
        for idx, item in enumerate(auditoria_triagem.get('amostra_top_produtos', []), start=1):
            linhas_top.append({
                'Rank': idx,
                'Produto': item.get('nome'),
                'Score': round(float(item.get('score_final') or 0.0), 2),
                'Família': item.get('familia_produto'),
                'Regime': item.get('regime_taxa'),
            })
        _imprimir_tabela(['Rank', 'Produto', 'Score', 'Família', 'Regime'], linhas_top, limite=10)
    else:
        print('  [OK] sem produtos selecionados nesta execução')

    if bool(((pacote_config.conteudo.get('auditoria') or {}).get('mostrar_teste_menos_1_dia', False))):
        _imprimir_titulo('TESTE DE -1 DIA DE RENDIMENTO')
        _imprimir_linha_status('Comparação da posição crítica entre a referência completa e a referência menos 1 dia', 'OK', f"ref={contexto.data_referencia.isoformat()} vs ref-1d={data_referencia_menos_1_dia.isoformat()}")
        _imprimir_tabela(
            ['Lote', 'Bruto ref', 'Bruto ref-1d', 'Δ 1d bruto', 'Líquido ref', 'Líquido ref-1d', 'Δ 1d líquido', 'Obs.'],
            comparativo_menos_1_dia,
        )

    lotes_ativos = _preparar_tabela_lotes_ativos(replay_passado, calendario_financeiro, pacote_config.conteudo, contexto.data_referencia, serie_cdi=cache_cdi.serie_cdi)

    _imprimir_titulo('SITUAÇÃO ATUAL — LOTES ATIVOS')
    if lotes_ativos:
        _imprimir_tabela(['Lote', 'Recebimento', 'Aplicação', 'Produto', 'Valor original', 'Dias corridos', 'Dias úteis', 'Bruto', 'Líquido', 'Saldo rem'], lotes_ativos)
    else:
        print('  [OK] sem lotes ativos acima do limiar nesta execução')




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
            sub_inc = inconsistencias[inconsistencias['lotes_informados'].astype(str).str.contains(re.escape(lote_id), na=False)] if 'lotes_informados' in inconsistencias.columns else inconsistencias.iloc[0:0]
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
